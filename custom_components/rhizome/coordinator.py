"""Coordinateur : agrege jardin, catalogue et moteur en une vue unique.

Il n'y a rien a interroger sur le reseau : tout est calcule localement. Le
DataUpdateCoordinator sert ici pour sa plomberie (abonnement des entites,
rafraichissement sur demande) et pour un recalcul horaire, qui suffit a faire
basculer les etapes au passage de minuit.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import rotation, watering
from .catalog import Catalogue
from .const import (
    CONF_ARROSAGE_ACTIF,
    CONF_GELEES_DERNIERE,
    CONF_GELEES_PREMIERE,
    CONF_MASQUER_TERMINEES,
    CONF_NOTIFY_ARROSAGE,
    CONF_NOTIFY_ETAPES,
    CONF_NOTIFY_RECOLTE_RECURRENCE,
    CONF_NOTIFY_RESUME,
    CONF_RAPPEL_JOURS,
    DEFAUT_ARROSAGE_ACTIF,
    DEFAUT_GELEES_DERNIERE,
    DEFAUT_GELEES_PREMIERE,
    DEFAUT_MASQUER_TERMINEES,
    DEFAUT_NOTIFY_ARROSAGE,
    DEFAUT_NOTIFY_RECOLTE_RECURRENCE,
    DEFAUT_NOTIFY_RESUME,
    DEFAUT_RAPPEL_JOURS,
    DOMAIN,
    ETAPES_NOTIFIABLES,
)
from .lifecycle import (
    PHASES_LIBELLES,
    total_recolte_saison_g,
)
from .lifecycle import (
    resume as resume_journal,
)
from .phenology import Gelees, prochaines_etapes
from .store import JardinStore

_LOGGER = logging.getLogger(__name__)

INTERVALLE = timedelta(hours=1)


class RhizomeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Vue calculee du potager, partagee par toutes les entites."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, store: JardinStore
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=INTERVALLE,
            config_entry=entry,
        )
        self.entry = entry
        self.store = store
        self._catalogue = Catalogue(store.cultures_perso)

    @property
    def catalogue(self) -> Catalogue:
        """Fiches livrees et fiches personnelles, vues comme un seul catalogue."""
        return self._catalogue

    def recharger_catalogue(self) -> None:
        """A appeler apres toute modification des fiches personnelles."""
        self._catalogue = Catalogue(self.store.cultures_perso)

    # --- Options -------------------------------------------------------------

    @property
    def gelees(self) -> Gelees:
        options = self.entry.options
        return Gelees(
            derniere=options.get(CONF_GELEES_DERNIERE, DEFAUT_GELEES_DERNIERE),
            premiere=options.get(CONF_GELEES_PREMIERE, DEFAUT_GELEES_PREMIERE),
        )

    @property
    def rappel_jours(self) -> int:
        return int(self.entry.options.get(CONF_RAPPEL_JOURS, DEFAUT_RAPPEL_JOURS))

    @property
    def etapes_notifiables(self) -> list[str]:
        """Types d'etapes pour lesquels un rappel part. Tout, par defaut :
        mieux vaut desactiver ce qui derange que decouvrir en juillet qu'un
        rappel n'est jamais parti."""
        choix = self.entry.options.get(CONF_NOTIFY_ETAPES)
        return list(choix) if choix is not None else list(ETAPES_NOTIFIABLES)

    @property
    def notify_resume(self) -> bool:
        return bool(self.entry.options.get(CONF_NOTIFY_RESUME, DEFAUT_NOTIFY_RESUME))

    @property
    def recolte_recurrence(self) -> int:
        """Relance pendant la fenetre de recolte, en jours. 0 = une seule fois."""
        return int(
            self.entry.options.get(
                CONF_NOTIFY_RECOLTE_RECURRENCE, DEFAUT_NOTIFY_RECOLTE_RECURRENCE
            )
        )

    @property
    def arrosage_actif(self) -> bool:
        return bool(
            self.entry.options.get(CONF_ARROSAGE_ACTIF, DEFAUT_ARROSAGE_ACTIF)
        )

    @property
    def notify_arrosage(self) -> bool:
        """Rappeler les arrosages dus, ou seulement les suivre.

        Distinct de `arrosage_actif` : couper les rappels ne doit pas faire
        disparaitre les echeances ni le bouton « Arrosé ».
        """
        return bool(
            self.entry.options.get(CONF_NOTIFY_ARROSAGE, DEFAUT_NOTIFY_ARROSAGE)
        )

    @property
    def masquer_terminees(self) -> bool:
        return bool(
            self.entry.options.get(CONF_MASQUER_TERMINEES, DEFAUT_MASQUER_TERMINEES)
        )

    def rappel_pour(self, plante: dict) -> int:
        """Le reglage de la plante prime sur le reglage global."""
        propre = plante.get("rappel_jours")
        return int(propre) if propre is not None else self.rappel_jours

    # --- Calcul --------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        return await self.hass.async_add_executor_job(self._calculer)

    def _calculer(self) -> dict[str, Any]:
        aujourdhui = date.today()
        gelees = self.gelees
        plantes: dict[str, dict] = {}
        actions: list[dict] = []
        total_recolte = 0
        total_saison = 0

        for brute in self.store.plantes:
            uid = brute["uid"]
            fiche = self._catalogue.culture(brute["culture_id"])
            if fiche is None:
                _LOGGER.warning(
                    "Culture absente du catalogue, plante ignoree : %s",
                    brute["culture_id"],
                )
                continue

            decalage = self.store.decalage_zone(brute.get("zone"))
            etapes = prochaines_etapes(fiche, brute, gelees, decalage, aujourdhui)
            infos = resume_journal(brute)
            total_recolte += infos["total_recolte_g"]
            # Le total « de la saison » doit se remettre a zero chaque annee,
            # sinon son nom ment des la deuxieme. L'annee civile tranche la
            # saison de maniere comprehensible, et rend les annees comparables.
            saison = total_recolte_saison_g(
                brute.get("evenements") or [], aujourdhui.year
            )
            infos["recolte_saison_g"] = saison
            total_saison += saison

            entree = {
                "uid": uid,
                "plante": brute,
                "culture": fiche,
                "zone": self.store.zone(brute.get("zone")),
                "etapes": etapes,
                "prochaine": etapes[0] if etapes else None,
                "resume": infos,
                "nom_affiche": nom_affiche(brute, fiche),
            }
            plantes[uid] = entree

            prochaine = entree["prochaine"]
            if prochaine is not None:
                restants = prochaine.jours_restants(aujourdhui)
                if restants <= self.rappel_pour(brute):
                    actions.append(
                        {
                            "uid": uid,
                            "nom": entree["nom_affiche"],
                            "emoji": fiche["emoji"],
                            "zone": entree["zone"]["nom"],
                            "etape": prochaine,
                            "jours_restants": restants,
                            "en_cours": prochaine.contient(aujourdhui),
                        }
                    )

        arrosages: list[dict] = []
        if self.arrosage_actif:
            for uid, entree in plantes.items():
                etat = watering.etat(
                    entree["culture"],
                    entree["plante"],
                    entree["zone"],
                    gelees,
                    aujourdhui,
                )
                entree["arrosage"] = etat
                if etat.a_arroser:
                    arrosages.append(
                        {
                            "uid": uid,
                            "nom": entree["nom_affiche"],
                            "emoji": entree["culture"]["emoji"],
                            "zone": entree["zone"]["nom"],
                            "etat": etat,
                        }
                    )
        else:
            for entree in plantes.values():
                entree["arrosage"] = None

        arrosages.sort(key=lambda a: (a["etat"].jours_restants, a["nom"]))
        actions.sort(key=lambda a: (a["etape"].debut, a["nom"]))

        return {
            "plantes": plantes,
            "zones": list(self.store.zones),
            "actions": actions,
            "arrosages": arrosages,
            "total_recolte_g": total_saison,
            "total_toutes_saisons_g": total_recolte,
            "saison": aujourdhui.year,
            "calcule_le": aujourdhui,
        }

    # --- Rotation des cultures -----------------------------------------------

    def verifier_rotation(self, culture_id: str, zone_id: str) -> dict | None:
        """Avertit si la meme famille a deja occupe cette zone recemment."""
        fiche = self._catalogue.culture(culture_id)
        if fiche is None:
            return None
        return rotation.verifier(
            fiche,
            zone_id,
            self.store.plantes,
            {c["id"]: c for c in self._catalogue.toutes()},
            date.today(),
        )

    # --- Ecriture : toute mutation passe par un rafraichissement -------------

    async def async_appliquer(self, mutation) -> Any:
        """Execute une mutation du store puis recalcule la vue.

        Point de passage unique : aucun appelant n'a a se souvenir de
        rafraichir, donc entites et panneau ne peuvent pas rester en retard.
        """
        resultat = mutation()

        # Ecriture immediate et attendue. Une sauvegarde differee a deja coute
        # un jardin entier : les plantes ajoutees avaient disparu au
        # redemarrage suivant. Quelques kilo-octets par geste de jardinage ne
        # justifient aucun differe.
        await self.store.async_sauvegarder_maintenant()

        # `async_refresh` et non `async_request_refresh` : ce dernier est
        # debounce, et le panneau qui rappelle `rhizome/jardin` juste apres
        # recevrait l'etat d'avant la mutation. Le calcul etant pur et local,
        # il n'y a rien a economiser en le differant.
        await self.async_refresh()
        return resultat


def nom_affiche(plante: dict, fiche: dict) -> str:
    surnom = plante.get("surnom")
    return f"{fiche['nom']} ({surnom})" if surnom else fiche["nom"]


def etape_en_dict(etape) -> dict | None:
    """Serialise une etape pour le panneau et les attributs d'entite."""
    if etape is None:
        return None
    donnees = asdict(etape)
    donnees["debut"] = etape.debut.isoformat()
    donnees["fin"] = etape.fin.isoformat()
    donnees["libelle"] = etape.libelle
    donnees["reelle"] = etape.reelle
    return donnees


def libelle_phase(phase: str) -> str:
    return PHASES_LIBELLES.get(phase, phase)
