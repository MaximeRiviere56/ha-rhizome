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
import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import i18n, rotation, watering
from .catalog import Catalogue, nom_localise
from .const import (
    CONF_ARROSAGE_ACTIF,
    CONF_GELEES_DERNIERE,
    CONF_GELEES_PREMIERE,
    CONF_LANGUE,
    CONF_MASQUER_TERMINEES,
    CONF_NOTIFY_ARROSAGE,
    CONF_NOTIFY_ETAPES,
    CONF_NOTIFY_RECOLTE_RECURRENCE,
    CONF_NOTIFY_RESUME,
    CONF_RAPPEL_JOURS,
    DEFAUT_ARROSAGE_ACTIF,
    DEFAUT_GELEES_DERNIERE,
    DEFAUT_GELEES_PREMIERE,
    DEFAUT_LANGUE,
    DEFAUT_MASQUER_TERMINEES,
    DEFAUT_NOTIFY_ARROSAGE,
    DEFAUT_NOTIFY_RECOLTE_RECURRENCE,
    DEFAUT_NOTIFY_RESUME,
    DEFAUT_RAPPEL_JOURS,
    DOMAIN,
    ETAPES_NOTIFIABLES,
)
from .lifecycle import (
    resume as resume_journal,
)
from .lifecycle import (
    total_recolte_saison_g,
)
from .phenology import Gelees, prochaines_etapes
from .store import JardinStore

_LOGGER = logging.getLogger(__name__)

INTERVALLE = timedelta(hours=1)

_MOTIF_JOUR_MOIS = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")


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

    def _entier(self, cle: str, defaut: int) -> int:
        """Lit une option entiere sans jamais faire echouer le calcul.

        Une valeur illisible dans `entry.options` est persistee : si elle
        remontait en ValueError depuis `_calculer`, l'integration resterait en
        panne a chaque cycle, y compris apres redemarrage. Le defaut, lui, est
        toujours un etat exploitable.
        """
        brute = self.entry.options.get(cle, defaut)
        try:
            return int(brute)
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Reglage « %s » illisible (%r) : valeur par defaut %s utilisee. "
                "Corrigez-le depuis le panneau ou la page de l'integration.",
                cle,
                brute,
                defaut,
            )
            return defaut

    @property
    def langue(self) -> str:
        """La langue des textes que le serveur produit lui-meme.

        Elle vaut pour les noms d'entites, les rappels, le calendrier et la
        liste de taches — tout ce que le panneau ne rend pas. Le panneau, lui,
        suit la langue de qui le regarde : c'est `hass.language`, qui est propre
        a l'utilisateur, alors que `hass.config.language` est celle de
        l'instance. Les deux coincident dans la quasi-totalite des cas, et
        quand elles divergent, c'est la bonne reponse de chaque cote.
        """
        return i18n.resoudre(
            self.entry.options.get(CONF_LANGUE, DEFAUT_LANGUE),
            getattr(self.hass.config, "language", None),
        )

    @property
    def gelees(self) -> Gelees:
        options = self.entry.options
        derniere = options.get(CONF_GELEES_DERNIERE, DEFAUT_GELEES_DERNIERE)
        premiere = options.get(CONF_GELEES_PREMIERE, DEFAUT_GELEES_PREMIERE)
        if not _MOTIF_JOUR_MOIS.match(str(derniere)):
            _LOGGER.warning("Gelée de printemps illisible (%r).", derniere)
            derniere = DEFAUT_GELEES_DERNIERE
        if not _MOTIF_JOUR_MOIS.match(str(premiere)):
            _LOGGER.warning("Gelée d'automne illisible (%r).", premiere)
            premiere = DEFAUT_GELEES_PREMIERE
        return Gelees(derniere=derniere, premiere=premiere)

    @property
    def rappel_jours(self) -> int:
        return self._entier(CONF_RAPPEL_JOURS, DEFAUT_RAPPEL_JOURS)

    @property
    def etapes_notifiables(self) -> list[str]:
        """Types d'etapes pour lesquels un rappel part. Tout, par defaut :
        mieux vaut desactiver ce qui derange que decouvrir en juillet qu'un
        rappel n'est jamais parti."""
        choix = self.entry.options.get(CONF_NOTIFY_ETAPES)
        if not isinstance(choix, (list, tuple)):
            return list(ETAPES_NOTIFIABLES)
        return [etape for etape in choix if etape in ETAPES_NOTIFIABLES]

    @property
    def notify_resume(self) -> bool:
        return bool(self.entry.options.get(CONF_NOTIFY_RESUME, DEFAUT_NOTIFY_RESUME))

    @property
    def recolte_recurrence(self) -> int:
        """Relance pendant la fenetre de recolte, en jours. 0 = une seule fois."""
        return self._entier(
            CONF_NOTIFY_RECOLTE_RECURRENCE, DEFAUT_NOTIFY_RECOLTE_RECURRENCE
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
        if propre is None:
            return self.rappel_jours
        try:
            return int(propre)
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Delai de rappel illisible (%r) pour une plante : "
                "le reglage global prend le relais.",
                propre,
            )
            return self.rappel_jours

    # --- Calcul --------------------------------------------------------------

    @staticmethod
    def aujourdhui() -> date:
        """Le jour tel que Home Assistant le voit.

        `date.today()` suit le fuseau de la machine, qui se regle
        independamment de celui de l'instance : un jardin pouvait basculer de
        jour a une heure qui n'est pas celle de son jardinier.
        """
        return dt_util.now().date()

    async def _async_update_data(self) -> dict[str, Any]:
        # Dans la boucle, et non dans un executeur. Le calcul est pur et local :
        # moins d'une milliseconde pour cinquante plantes, mesure sur le
        # catalogue complet — moins que le cout du saut de thread. L'executeur,
        # lui, lisait des structures que la boucle peut muter au meme instant.
        return self._calculer()

    def _calculer(self) -> dict[str, Any]:
        aujourdhui = self.aujourdhui()
        gelees = self.gelees
        langue = self.langue
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
            try:
                etapes = prochaines_etapes(
                    fiche, brute, gelees, decalage, aujourdhui
                )
                infos = resume_journal(brute)
            # Une plante abimee ne doit pas coucher le jardin entier.
            #
            # Les schemas bornent desormais tout ce qui entre, et le stockage
            # borne ce qu'il relit. Reste ce qu'aucune garde ne peut prevoir :
            # une date du journal posee par une version anterieure, un fichier
            # `.storage` edite a la main. Sans ce filet, l'exception remontait
            # a `_async_update_data`, donc a chaque cycle — et comme la donnee
            # est persistee, ni le rechargement ni le redemarrage n'y
            # changeaient rien. Ignorer la plante laisse les autres vivre, et
            # le journal dit laquelle regarder.
            except (OverflowError, ValueError, TypeError, KeyError):
                _LOGGER.exception(
                    "Plante ignoree ce cycle, son enregistrement est "
                    "incalculable (uid %s, culture %s). Les autres plantes "
                    "ne sont pas affectees.",
                    uid,
                    brute.get("culture_id"),
                )
                continue
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
                "nom_affiche": nom_affiche(brute, fiche, langue),
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
                # Meme filet que plus haut : un historique d'arrosage abime
                # prive cette plante de son echeance d'eau, pas le jardin de
                # son calcul.
                try:
                    etat = watering.etat(
                        entree["culture"],
                        entree["plante"],
                        entree["zone"],
                        gelees,
                        aujourdhui,
                    )
                except (OverflowError, ValueError, TypeError, KeyError):
                    _LOGGER.exception(
                        "Arrosage incalculable pour la plante %s : ignore.", uid
                    )
                    entree["arrosage"] = None
                    continue
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
        avis = rotation.verifier(
            fiche,
            zone_id,
            self.store.plantes,
            {c["id"]: c for c in self._catalogue.toutes()},
            self.aujourdhui(),
        )
        return self._rotation_traduite(avis, fiche)

    def _rotation_traduite(self, avis: dict | None, fiche: dict) -> dict | None:
        """Reecrit l'avis de rotation dans la langue de l'interface.

        `rotation` est un module pur : il rend son message en francais, langue
        de reference du projet, et y cite des noms de cultures qu'il a lus dans
        le catalogue francais. On le reconstruit donc ici, ou le catalogue et
        la langue sont connus.

        La famille se lit sur la fiche qu'on vient de verifier, et non sur une
        des antecedentes : `rotation.verifier` ne retient que les plantes de la
        meme famille, c'est donc la meme — et elle est sous la main.
        """
        langue = self.langue
        if avis is None or langue == "fr":
            return avis

        noms = ", ".join(
            f"{self._nom_culture(p.get('culture_id'), p['nom'])} ({p['annee']})"
            for p in sorted(avis["precedents"], key=lambda p: -p["annee"])[:3]
        )
        return {
            **avis,
            "precedents_libelle": noms,
            "message": i18n.t(
                langue,
                "rotation_message",
                famille=fiche.get(f"famille_{langue}") or avis["famille"],
                precedents=noms,
                delai=avis["delai_ans"],
            ),
        }

    def _nom_culture(self, culture_id: str | None, defaut: str) -> str:
        """Le nom traduit de cette culture, ou le nom francais si elle a
        disparu du catalogue entre-temps."""
        fiche = self._catalogue.culture(culture_id or "")
        return nom_localise(fiche, self.langue) if fiche else defaut

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


def nom_affiche(plante: dict, fiche: dict, langue: str = "fr") -> str:
    """Le nom sous lequel cette plante apparait partout : entites, rappels,
    calendrier, panneau.

    Le surnom est une donnee de l'utilisateur et n'est jamais traduit ; le nom
    de la culture, lui, suit la langue de l'interface.
    """
    nom = nom_localise(fiche, langue)
    surnom = plante.get("surnom")
    return f"{nom} ({surnom})" if surnom else nom


def etape_en_dict(etape, langue: str = "fr") -> dict | None:
    """Serialise une etape pour le panneau et les attributs d'entite.

    `libelle` est traduit ici et non cote panneau : les attributs d'entite
    passent par le meme chemin, et la carte Lovelace les lit tels quels.
    """
    if etape is None:
        return None
    donnees = asdict(etape)
    donnees["debut"] = etape.debut.isoformat()
    donnees["fin"] = etape.fin.isoformat()
    donnees["libelle"] = i18n.libelle_etape(langue, etape.type)
    donnees["reelle"] = etape.reelle
    return donnees


def libelle_phase(phase: str, langue: str = "fr") -> str:
    return i18n.libelle_phase(langue, phase)
