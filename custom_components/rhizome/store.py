"""Persistance du jardin : plantes, journal, zones.

Le journal est la seule source de verite sur l'etat d'une plante ; la phase
stockee n'est qu'un cache recalcule a chaque ecriture. Toute mutation passe
par ce module, qui valide via `lifecycle` avant d'ecrire.
"""

from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import Any
import uuid

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import (
    DECALAGE_ZONE_MAX,
    STORAGE_KEY,
    STORAGE_KEY_HERITAGE,
    STORAGE_VERSION,
    TRAITS_ZONES_CONNUES,
    ZONE_PLEINE_TERRE,
    ZONES_DEFAUT,
)
from .i18n import nom_zone_defaut
from .lifecycle import (
    EVT_SEME,
    MODE_SEMIS_DIRECT,
    PHASE_PREVU,
    ErreurJournal,
    ajouter_evenement,
    annuler_dernier_evenement,
    construire_evenement,
    mode_semis,
    phase_depuis_evenements,
)
from .watering import construire_arrosage, noter_arrosage

_LOGGER = logging.getLogger(__name__)


class PlanteInconnue(ErreurJournal):
    """Aucune plante du jardin ne porte cet identifiant."""


class JardinStore:
    """Enveloppe typee autour du Store de Home Assistant."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._donnees: dict[str, Any] = {
            "plantes": [],
            "zones": [],
            "cultures_perso": [],
        }

    # --- Cycle de vie du stockage --------------------------------------------

    async def async_charger(self, langue: str = "fr") -> None:
        """Lit le jardin, et cree les zones livrees s'il n'en a pas encore.

        `langue` ne sert qu'a nommer ces quatre zones initiales. Elles
        deviennent ensuite des donnees : changer de langue plus tard ne les
        renomme pas, et c'est voulu — l'utilisateur a pu les rebaptiser.
        """
        charge = await self._store.async_load()
        if charge is None:
            charge = await self._async_adopter_heritage()
        if charge:
            self._donnees = charge
        self._donnees.setdefault("plantes", [])
        self._donnees.setdefault("cultures_perso", [])
        if not self._donnees.get("zones"):
            self._donnees["zones"] = [
                {**z, "nom": nom_zone_defaut(langue, z["id"], z["nom"])}
                for z in ZONES_DEFAUT
            ]
        else:
            # Un stockage anterieur a l'arrosage ne porte pas encore les
            # caracteristiques de zone : on les deduit pour les zones
            # d'origine, sans toucher a celles que l'utilisateur a creees.
            for zone in self._donnees["zones"]:
                for cle, valeur in TRAITS_ZONES_CONNUES.get(zone["id"], {}).items():
                    zone.setdefault(cle, valeur)
        # Les phases sont recalculees au chargement : un journal edite a la main
        # ou une version anterieure du schema se remet ainsi d'aplomb.
        for plante in self._donnees["plantes"]:
            plante["phase"] = phase_depuis_evenements(plante.get("evenements") or [])
            plante.setdefault("arrosages", [])

    async def _async_adopter_heritage(self) -> dict[str, Any] | None:
        """Reprend le jardin ecrit sous l'ancien nom de l'integration.

        Le renommage en « rhizome » change la cle de stockage : sans cette
        reprise, une installation existante redemarrerait sur un jardin vide.
        L'ancien fichier est volontairement laisse en place — il ne coute que
        quelques kilo-octets et reste le seul filet si la reprise deraille.
        """
        ancien: Store[dict[str, Any]] = Store(
            self._hass, STORAGE_VERSION, STORAGE_KEY_HERITAGE
        )
        donnees = await ancien.async_load()
        if donnees is None:
            return None
        _LOGGER.warning(
            "Jardin repris depuis « %s » : l'integration s'appelle desormais "
            "« %s ». L'ancien stockage est conserve intact.",
            STORAGE_KEY_HERITAGE,
            STORAGE_KEY,
        )
        await self._store.async_save(donnees)
        return donnees

    def _sauvegarder(self) -> None:
        """Programme une ecriture au prochain tour de boucle.

        Delai zero, et non quelques secondes : le jardin pese quelques kilo-
        octets, il n'y a rien a gagner a differer, et une fenetre d'attente est
        une fenetre pendant laquelle un arret de Home Assistant perd des
        donnees. Les mutations utilisateur passent de toute facon par
        `async_sauvegarder_maintenant`, qui attend l'ecriture.
        """
        self._store.async_delay_save(lambda: self._donnees, 0)

    async def async_sauvegarder_maintenant(self) -> None:
        """Ecrit sur disque et attend que ce soit fait."""
        await self._store.async_save(self._donnees)

    # --- Lecture -------------------------------------------------------------

    @property
    def plantes(self) -> list[dict]:
        return self._donnees["plantes"]

    @property
    def zones(self) -> list[dict]:
        return self._donnees["zones"]

    def plante(self, uid: str) -> dict:
        for plante in self.plantes:
            if plante["uid"] == uid:
                return plante
        raise PlanteInconnue(
            f"Plante introuvable dans le jardin : {uid}",
            cle="err_plante_introuvable",
            uid=uid,
        )

    def zone(self, zone_id: str | None) -> dict:
        for zone in self.zones:
            if zone["id"] == zone_id:
                return zone
        return {"id": ZONE_PLEINE_TERRE, "nom": "Pleine terre", "decalage_jours": 0}

    def decalage_zone(self, zone_id: str | None) -> int:
        """Decalage d'une zone, borne au sens horticole.

        Le schema WebSocket borne deja l'ecriture. Cette seconde garde vise ce
        qui est deja dans `.storage` : une valeur posee par une version
        anterieure, ou un fichier edite a la main. Sans elle, un decalage
        demesure faisait deborder `date + timedelta(...)` a chaque cycle du
        coordinateur, et l'etat ne se reparait ni au rechargement ni au
        redemarrage puisque la valeur est persistee.
        """
        brute = self.zone(zone_id).get("decalage_jours", 0)
        try:
            decalage = int(brute)
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Decalage illisible (%r) pour la zone « %s » : 0 utilise.",
                brute,
                zone_id,
            )
            return 0
        if not -DECALAGE_ZONE_MAX <= decalage <= DECALAGE_ZONE_MAX:
            borne = max(-DECALAGE_ZONE_MAX, min(DECALAGE_ZONE_MAX, decalage))
            _LOGGER.warning(
                "Decalage hors limites (%s j) pour la zone « %s » : "
                "ramene a %s j.",
                decalage,
                zone_id,
                borne,
            )
            return borne
        return decalage

    # --- Ecriture : plantes --------------------------------------------------

    def ajouter_plante(
        self,
        culture_id: str,
        *,
        zone: str = ZONE_PLEINE_TERRE,
        surnom: str | None = None,
        notifs: bool = True,
        rappel_jours: int | None = None,
        echelonnement_jours: int | None = None,
    ) -> dict:
        """Une culture peut etre ajoutee plusieurs fois : deux semis echelonnes,
        ou le meme legume en serre et en pleine terre. D'ou l'uid."""
        plante: dict[str, Any] = {
            "uid": uuid.uuid4().hex[:8],
            "culture_id": culture_id,
            "zone": zone,
            "surnom": surnom or None,
            "phase": PHASE_PREVU,
            "notifs": notifs,
            "rappel_jours": rappel_jours,
            "echelonnement_jours": echelonnement_jours,
            "arrosage_actif": True,
            "arrosage_frequence_jours": None,
            "evenements": [],
            "arrosages": [],
        }
        self.plantes.append(plante)
        self._sauvegarder()
        return plante

    def retirer_plante(self, uid: str) -> dict:
        plante = self.plante(uid)
        self.plantes.remove(plante)
        self.purger_notifs(uid)
        self._sauvegarder()
        return plante

    def modifier_plante(self, uid: str, **champs: Any) -> dict:
        """Modifie les reglages d'une plante. Le journal n'est pas touchable ici."""
        plante = self.plante(uid)
        for cle in ("zone", "surnom", "notifs", "rappel_jours",
                    "echelonnement_jours", "arrosage_actif",
                    "arrosage_frequence_jours"):
            if cle in champs:
                plante[cle] = champs[cle]
        self._sauvegarder()
        return plante

    def ressemer(self, uid: str, jour: Any) -> dict:
        """Ouvre la serie suivante d'un semis echelonne.

        Un semis echelonne n'est pas un evenement de plus sur la meme plante :
        c'est un second lot, a un stade different, qui vit sa propre vie. On
        cree donc une nouvelle plante, et on coupe l'echelonnement du parent —
        sans quoi les deux reclameraient le meme ressemis indefiniment.
        """
        parent = self.plante(uid)
        intervalle = parent.get("echelonnement_jours")

        rang = sum(
            1
            for p in self.plantes
            if p["culture_id"] == parent["culture_id"]
            and p.get("zone") == parent.get("zone")
        ) + 1
        base = parent.get("surnom") or ""
        surnom = f"{base} · lot {rang}".strip(" ·") if base else f"lot {rang}"

        enfant = self.ajouter_plante(
            parent["culture_id"],
            zone=parent.get("zone", ZONE_PLEINE_TERRE),
            surnom=surnom,
            notifs=parent.get("notifs", True),
            rappel_jours=parent.get("rappel_jours"),
            echelonnement_jours=intervalle,
        )
        mode = mode_semis(parent.get("evenements") or []) or MODE_SEMIS_DIRECT
        ajouter_evenement(
            enfant, construire_evenement(EVT_SEME, jour, mode=mode)
        )

        parent["echelonnement_jours"] = None
        self._sauvegarder()
        return enfant

    def arroser(self, uid: str, jour: Any, note: str | None = None) -> dict:
        """Note un arrosage.

        Ce n'est pas un evenement du journal : l'arrosage ne fait pas avancer
        la plante dans son cycle, et il se repete bien trop souvent pour ne
        pas noyer l'historique de culture.
        """
        plante = self.plante(uid)
        entree = noter_arrosage(plante, construire_arrosage(jour, note))
        self._sauvegarder()
        return entree

    def familles_recentes(self, zone_id: str, depuis_annee: int) -> dict[str, list]:
        """Familles botaniques deja cultivees dans cette zone, par famille.

        Sert a la rotation des cultures. Les plantes terminees et perdues
        comptent : c'est precisement l'historique qui nous interesse.
        """
        trouve: dict[str, list] = {}
        for plante in self.plantes:
            if plante.get("zone") != zone_id:
                continue
            annees = {
                int(evt["date"][:4])
                for evt in plante.get("evenements") or []
            } or {depuis_annee}
            recentes = [a for a in annees if a >= depuis_annee]
            if recentes:
                trouve.setdefault(plante["culture_id"], []).extend(sorted(recentes))
        return trouve

    # --- Ecriture : journal --------------------------------------------------

    def noter(self, uid: str, type_evt: str, jour: Any, **details: Any) -> dict:
        """Ajoute un evenement au journal apres validation de la transition."""
        plante = self.plante(uid)
        evt = construire_evenement(type_evt, jour, **details)
        ajouter_evenement(plante, evt)
        self._sauvegarder()
        return plante

    def annuler(self, uid: str) -> dict | None:
        plante = self.plante(uid)
        retire = annuler_dernier_evenement(plante)
        if retire is not None:
            self._sauvegarder()
        return retire

    # --- Catalogue personnel -------------------------------------------------
    #
    # Les fiches saisies par l'utilisateur vivent ici, et non dans le fichier
    # livre avec l'integration : une mise a jour ne doit jamais les effacer.

    @property
    def cultures_perso(self) -> list[dict]:
        return self._donnees.setdefault("cultures_perso", [])

    def enregistrer_culture(self, fiche: dict) -> dict:
        """Cree ou remplace une fiche personnelle, selon son id."""
        cultures = self.cultures_perso
        for index, existante in enumerate(cultures):
            if existante["id"] == fiche["id"]:
                cultures[index] = fiche
                break
        else:
            cultures.append(fiche)
        self._sauvegarder()
        return fiche

    def supprimer_culture(self, culture_id: str, retablit: bool = False) -> None:
        """Refuse tant qu'une plante du jardin s'appuie sur cette fiche :
        sans elle, la plante deviendrait un orphelin silencieux.

        `retablit` leve ce refus : supprimer une surcharge rend sa fiche
        d'origine, donc aucune plante ne se retrouve sans reference.
        """
        utilisees = [] if retablit else [
            p for p in self.plantes if p["culture_id"] == culture_id
        ]
        if utilisees:
            noms = ", ".join(p.get("surnom") or p["culture_id"] for p in utilisees)
            raise ErreurJournal(
                f"Cette fiche est utilisée par {len(utilisees)} plante(s) du "
                f"jardin ({noms}). Retirez-les d'abord.",
                cle="err_fiche_utilisee",
                nombre=len(utilisees),
                plantes=noms,
            )
        self._donnees["cultures_perso"] = [
            c for c in self.cultures_perso if c["id"] != culture_id
        ]
        self._sauvegarder()

    # --- Etat des rappels ----------------------------------------------------
    #
    # Memoriser ce qui a deja ete envoye est ce qui separe un rappel utile d'un
    # harcelement quotidien : une fenetre de semis reste ouverte un mois.

    @property
    def etat_notifs(self) -> dict[str, Any]:
        return self._donnees.setdefault("notifs", {"envoyees": {}, "reports": {}})

    def notif_deja_envoyee(self, cle: str) -> bool:
        return cle in self.etat_notifs["envoyees"]

    def dernier_envoi(self, cle: str) -> str | None:
        """Date du dernier rappel envoye pour cette occurrence, ou None.

        La date, et non un simple booleen : une relance de recolte doit savoir
        depuis combien de jours le dernier message est parti.
        """
        return self.etat_notifs["envoyees"].get(cle)

    def marquer_notif_envoyee(self, cle: str, jour: str) -> None:
        self.etat_notifs["envoyees"][cle] = jour
        self._sauvegarder()

    def reporter(self, cle: str, jusqu_au: str) -> None:
        self.etat_notifs["reports"][cle] = jusqu_au
        self._sauvegarder()

    def report_en_cours(self, cle: str, aujourdhui: str) -> bool:
        jusqu_au = self.etat_notifs["reports"].get(cle)
        return bool(jusqu_au and jusqu_au > aujourdhui)

    def purger_notifs(self, uid: str) -> None:
        """Au retrait d'une plante, ne pas laisser son etat de rappel derriere."""
        for bloc in ("envoyees", "reports"):
            table = self.etat_notifs[bloc]
            for cle in [c for c in table if c.startswith(f"{uid}:")]:
                del table[cle]

    def purger_notifs_anciennes(
        self, aujourdhui: str, retentions: dict[str, int], defaut: int
    ) -> int:
        """Oublie les rappels assez vieux pour ne plus pouvoir se re-declencher.

        Sans cela le stockage ne faisait que grossir : la cle d'un rappel
        d'arrosage porte la date du jour, donc une entree s'ajoutait par plante
        et par jour, et rien ne les retirait jamais hormis le retrait de la
        plante elle-meme.

        `retentions` donne un nombre de jours par type d'etape. Une etape
        annuelle doit etre gardee plus d'un an : la reoublier avant que sa
        fenetre ne revienne ferait repartir le meme rappel.

        Renvoie le nombre d'entrees retirees.
        """
        limite = (date.fromisoformat(aujourdhui) - timedelta(days=1)).isoformat()
        etat = self.etat_notifs
        retires = 0

        for cle, envoye_le in list(etat["envoyees"].items()):
            morceaux = cle.split(":")
            jours = retentions.get(morceaux[1] if len(morceaux) > 1 else "", defaut)
            perime = (
                date.fromisoformat(aujourdhui) - timedelta(days=jours)
            ).isoformat()
            if str(envoye_le) < perime:
                del etat["envoyees"][cle]
                retires += 1

        for cle, jusqu_au in list(etat["reports"].items()):
            if str(jusqu_au) <= limite:
                del etat["reports"][cle]
                retires += 1

        if retires:
            self._sauvegarder()
        return retires

    # --- Ecriture : zones ----------------------------------------------------

    def definir_zones(self, zones: list[dict]) -> None:
        """Les plantes rattachees a une zone disparue retombent en pleine terre."""
        self._donnees["zones"] = zones
        connues = {zone["id"] for zone in zones}
        for plante in self.plantes:
            if plante.get("zone") not in connues:
                plante["zone"] = ZONE_PLEINE_TERRE
        self._sauvegarder()
