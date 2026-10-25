"""Rappels du potager : quoi semer, repiquer ou recolter, et quand.

Deux partis pris.

Le moteur vit dans l'integration, pas dans des automatisations YAML : il n'y a
rien a cabler cote utilisateur, et la logique « ne pas reclamer un semis deja
fait » reste au meme endroit que la phase qui la porte.

Les rappels passent par les services `notify.mobile_app_*` et non par
`notify.send_message`, parce que seuls les premiers transportent des boutons
d'action. C'est ce bouton « C'est fait » qui remplit le journal ; sans lui, le
suivi reel reposerait sur la bonne volonte de rouvrir l'application.
"""

from __future__ import annotations

from datetime import date, timedelta
import functools
import logging
from typing import Any

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    CONF_NOTIFY_HEURE,
    CONF_NOTIFY_TARGETS,
    DEFAUT_NOTIFY_HEURE,
    DOMAIN,
)
from .coordinator import RhizomeCoordinator
from .lifecycle import (
    EVT_PLANTE,
    EVT_RECOLTE,
    EVT_REPIQUE,
    EVT_SEME,
    MODE_SEMIS_DIRECT,
    MODE_SEMIS_INTERIEUR,
    ErreurJournal,
)
from .phenology import (
    ETAPE_PLANTATION,
    ETAPE_RECOLTE,
    ETAPE_REPIQUAGE,
    ETAPE_RESSEMER,
    ETAPE_SEMIS_DIRECT,
    ETAPE_SEMIS_INTERIEUR,
)

_LOGGER = logging.getLogger(__name__)

EVENT_ACTION_MOBILE = "mobile_app_notification_action"
PREFIXE = "RHIZOME"
# L'arrosage n'est pas une etape du cycle : il a son propre type d'action.
ETAPE_ARROSAGE = "arrosage"
SEPARATEUR = "|"
JOURS_REPORT = 3

# Combien de temps garder la trace d'un rappel envoye. Une etape annuelle doit
# l'etre plus d'un an : l'oublier avant que sa fenetre ne revienne ferait
# repartir le meme rappel. L'arrosage, lui, ne sert qu'a ne pas prevenir deux
# fois le meme jour.
RETENTION_JOURS = {"arrosage": 7}
RETENTION_DEFAUT = 400

# Ce qu'il faut inscrire au journal quand l'utilisateur repond « C'est fait ».
JOURNAL_POUR_ETAPE: dict[str, tuple[str, dict[str, Any]]] = {
    ETAPE_SEMIS_INTERIEUR: (EVT_SEME, {"mode": MODE_SEMIS_INTERIEUR}),
    ETAPE_SEMIS_DIRECT: (EVT_SEME, {"mode": MODE_SEMIS_DIRECT}),
    ETAPE_REPIQUAGE: (EVT_REPIQUE, {}),
    ETAPE_PLANTATION: (EVT_PLANTE, {}),
    ETAPE_RECOLTE: (EVT_RECOLTE, {}),
}

VERBES = {
    ETAPE_SEMIS_INTERIEUR: "Semer à l'abri",
    ETAPE_SEMIS_DIRECT: "Semer en place",
    ETAPE_REPIQUAGE: "Repiquer",
    ETAPE_PLANTATION: "Planter",
    ETAPE_RECOLTE: "Récolter",
    ETAPE_RESSEMER: "Ressemer",
}


class RhizomeNotifier:
    """Verifie une fois par jour ce qui merite un rappel."""

    def __init__(self, hass: HomeAssistant, coordinator: RhizomeCoordinator) -> None:
        self.hass = hass
        self.coordinator = coordinator

    # --- Branchement ---------------------------------------------------------

    @callback
    def async_demarrer(self):
        """Arme la verification quotidienne et l'ecoute des boutons.

        Renvoie la fonction de desabonnement, a confier a `entry.async_on_unload`.
        """
        heure = dt_util.parse_time(
            self.coordinator.entry.options.get(CONF_NOTIFY_HEURE, DEFAUT_NOTIFY_HEURE)
        ) or dt_util.parse_time(DEFAUT_NOTIFY_HEURE)

        annuler_horaire = async_track_time_change(
            self.hass,
            self._async_verifier,
            hour=heure.hour,
            minute=heure.minute,
            second=0,
        )
        annuler_actions = self.hass.bus.async_listen(
            EVENT_ACTION_MOBILE, self._async_action_recue
        )

        @callback
        def _desabonner() -> None:
            annuler_horaire()
            annuler_actions()

        return _desabonner

    @staticmethod
    def _aujourdhui() -> date:
        """Le jour tel que Home Assistant le voit, pas tel que l'hote le voit.

        Le fuseau de l'instance se regle independamment de celui de la machine.
        """
        return dt_util.now().date()

    # --- Verification quotidienne -------------------------------------------

    async def _async_verifier(self, _now=None) -> None:
        cibles = self.coordinator.entry.options.get(CONF_NOTIFY_TARGETS) or []
        if not cibles:
            return

        # Rafraichissement certain avant de decider des envois du jour.
        await self.coordinator.async_refresh()
        aujourdhui = self._aujourdhui()
        aujourdhui_iso = aujourdhui.isoformat()
        etapes_voulues = set(self.coordinator.etapes_notifiables)
        recurrence = self.coordinator.recolte_recurrence

        a_envoyer: list[dict] = []

        for action in self.coordinator.data["actions"]:
            entree = self.coordinator.data["plantes"].get(action["uid"])
            if entree is None or not entree["plante"].get("notifs", True):
                continue

            etape = action["etape"]
            if etape.type not in etapes_voulues:
                continue

            cle_report = f"{action['uid']}:{etape.type}"
            if self.coordinator.store.report_en_cours(cle_report, aujourdhui_iso):
                continue

            cle = f"{action['uid']}:{etape.type}:{etape.debut.isoformat()}"
            dernier = self.coordinator.store.dernier_envoi(cle)

            # Une recolte se relance : une courgette se cueille tous les deux
            # jours, prevenir une seule fois ne sert a rien. Les autres etapes
            # ne se repetent pas.
            if dernier is not None and not (
                recurrence
                and etape.type == ETAPE_RECOLTE
                and action["en_cours"]
                and (aujourdhui - date.fromisoformat(dernier)).days >= recurrence
            ):
                continue

            a_envoyer.append((cle, action))

        # Les arrosages dus, une entree par plante et par jour. Suivre l'eau et
        # se la faire rappeler sont deux choix separes : le compte a rebours
        # reste visible meme quand le rappel se tait.
        if self.coordinator.arrosage_actif and self.coordinator.notify_arrosage:
            for besoin in self.coordinator.data["arrosages"]:
                cle = f"{besoin['uid']}:arrosage:{aujourdhui_iso}"
                if self.coordinator.store.notif_deja_envoyee(cle):
                    continue
                entree = self.coordinator.data["plantes"].get(besoin["uid"])
                if entree is None or not entree["plante"].get("notifs", True):
                    continue
                if await self._async_envoyer_arrosage(cibles, besoin):
                    self.coordinator.store.marquer_notif_envoyee(cle, aujourdhui_iso)

        if a_envoyer:
            actions = [action for _, action in a_envoyer]
            if self.coordinator.notify_resume and len(actions) > 1:
                if await self._async_envoyer_resume(cibles, actions):
                    for cle, _ in a_envoyer:
                        self.coordinator.store.marquer_notif_envoyee(
                            cle, aujourdhui_iso
                        )
            else:
                for cle, action in a_envoyer:
                    # Marque apres l'envoi, et non avant : un destinataire
                    # injoignable faisait perdre le rappel definitivement.
                    if await self._async_envoyer(cibles, action):
                        self.coordinator.store.marquer_notif_envoyee(
                            cle, aujourdhui_iso
                        )

        retires = self.coordinator.store.purger_notifs_anciennes(
            aujourdhui_iso, RETENTION_JOURS, RETENTION_DEFAUT
        )
        if retires:
            _LOGGER.debug("%s rappels perimes oublies.", retires)

    async def _async_envoyer_arrosage(self, cibles: list[str], besoin: dict) -> bool:
        """Un rappel d'arrosage, avec un bouton qui le note d'un geste.

        Renvoie vrai des qu'un destinataire a recu le message.
        """
        etat = besoin["etat"]
        retard = -etat.jours_restants
        if retard <= 0:
            quand = "C'est le jour"
        elif retard == 1:
            quand = "Depuis hier"
        else:
            quand = f"Depuis {retard} jours"

        dernier = (
            f"Dernier arrosage le {etat.dernier:%d/%m}"
            if etat.dernier
            else "Jamais arrosée depuis sa mise en terre"
        )

        charge: dict[str, Any] = {
            "title": f"💧 Arroser : {besoin['nom']}",
            "message": f"{quand} — {besoin['zone']}. {dernier}.",
        }
        actions_notif = [
            {
                "action": _encoder("fait", besoin["uid"], ETAPE_ARROSAGE),
                "title": "Arrosé",
            },
            {
                "action": _encoder("report", besoin["uid"], ETAPE_ARROSAGE),
                "title": f"Rappeler dans {JOURS_REPORT} j",
            },
        ]
        envoye = False
        for cible in cibles:
            service = cible.split(".", 1)[-1]
            donnees = dict(charge)
            if service != "persistent_notification":
                donnees["data"] = {
                    "actions": actions_notif,
                    "tag": f"{DOMAIN}_{besoin['uid']}_arrosage",
                    "group": f"{DOMAIN}_arrosage",
                }
            envoye = await self._async_appeler(service, donnees) or envoye
        return envoye

    async def _async_envoyer_resume(
        self, cibles: list[str], actions: list[dict]
    ) -> bool:
        """Un seul message pour toute la journee.

        Au printemps, cinq rappels le meme matin sont cinq rappels qu'on
        balaie sans lire. Le resume n'a pas de bouton d'action : il y a
        plusieurs plantes, et deviner laquelle serait pire que rien.
        """
        lignes = [
            f"{a['emoji']} {VERBES.get(a['etape'].type, a['etape'].libelle)} : "
            f"{a['nom']} ({a['zone']})"
            for a in actions
        ]
        charge: dict[str, Any] = {
            "title": f"🌱 {len(actions)} choses à faire au potager",
            "message": "\n".join(lignes),
        }
        envoye = False
        for cible in cibles:
            service = cible.split(".", 1)[-1]
            donnees = dict(charge)
            if service != "persistent_notification":
                donnees["data"] = {"tag": f"{DOMAIN}_resume", "group": DOMAIN}
            envoye = await self._async_appeler(service, donnees) or envoye
        return envoye

    async def _async_envoyer(self, cibles: list[str], action: dict) -> bool:
        etape = action["etape"]
        verbe = VERBES.get(etape.type, etape.libelle)
        titre = f"{action['emoji']} {verbe} : {action['nom']}"

        if action["en_cours"]:
            quand = "C'est le moment"
        elif action["jours_restants"] == 1:
            quand = "Demain"
        else:
            quand = f"Dans {action['jours_restants']} jours"
        message = f"{quand} — {action['zone']}. Fenêtre jusqu'au {etape.fin:%d/%m}."

        actions_notif = [
            {
                "action": _encoder("fait", action["uid"], etape.type),
                "title": "Semé" if etape.type == ETAPE_RESSEMER else "C'est fait",
            },
            {
                "action": _encoder("report", action["uid"], etape.type),
                "title": f"Rappeler dans {JOURS_REPORT} j",
            },
        ]

        envoye = False
        for cible in cibles:
            service = cible.split(".", 1)[-1]
            charge: dict[str, Any] = {"title": titre, "message": message}
            if service != "persistent_notification":
                charge["data"] = {
                    "actions": actions_notif,
                    "tag": f"{DOMAIN}_{action['uid']}_{etape.type}",
                    "group": DOMAIN,
                }
            envoye = await self._async_appeler(service, charge) or envoye
        return envoye

    async def _async_appeler(self, service: str, charge: dict[str, Any]) -> bool:
        """Appelle un service `notify`. Un destinataire absent ne doit pas
        empecher les autres de recevoir leur rappel.

        `blocking=True`, contrairement a avant : sans attendre, un service
        defaillant echouait apres coup et le rappel passait quand meme pour
        envoye, donc etait perdu.
        """
        if not self.hass.services.has_service("notify", service):
            _LOGGER.warning(
                "Destinataire de rappel introuvable : notify.%s. "
                "Verifiez les reglages de Rhizome.",
                service,
            )
            return False
        try:
            await self.hass.services.async_call(
                "notify", service, charge, blocking=True
            )
        # Un service de notification tiers peut lever a peu pres n'importe
        # quoi : on l'absorbe pour ne pas perdre les autres destinataires.
        except Exception:
            _LOGGER.exception("Echec de l'envoi du rappel vers notify.%s", service)
            return False
        return True

    # --- Reponses aux boutons ------------------------------------------------

    async def _async_action_recue(self, event: Event) -> None:
        decode = _decoder(event.data.get("action", ""))
        if decode is None:
            return
        quoi, uid, type_etape = decode

        if quoi == "report":
            jusqu_au = (self._aujourdhui() + timedelta(days=JOURS_REPORT)).isoformat()
            self.coordinator.store.reporter(f"{uid}:{type_etape}", jusqu_au)
            return

        store = self.coordinator.store
        jour = self._aujourdhui()

        if type_etape == ETAPE_ARROSAGE:
            mutation = functools.partial(store.arroser, uid, jour)
        elif type_etape == ETAPE_RESSEMER:
            # Un ressemis n'est pas un evenement de plus sur la meme plante :
            # c'est un nouveau lot. D'ou un chemin distinct.
            mutation = functools.partial(store.ressemer, uid, jour)
        else:
            inscription = JOURNAL_POUR_ETAPE.get(type_etape)
            if inscription is None:
                return
            type_evt, details = inscription
            mutation = functools.partial(store.noter, uid, type_evt, jour, **details)

        try:
            await self.coordinator.async_appliquer(mutation)
        except ErreurJournal as err:
            # Journal deja avance, ou plante retiree entre l'envoi du rappel et
            # la reponse : sans interet a remonter.
            #
            # On journalise `type_etape`, et non le type d'evenement : ce
            # dernier n'existe pas sur le chemin du ressemis, et la variable
            # non liee faisait lever une UnboundLocalError depuis le
            # gestionnaire d'exception lui-meme.
            _LOGGER.debug(
                "Action « %s » ignoree pour %s : %s", type_etape, uid, err
            )


def _encoder(quoi: str, uid: str, type_etape: str) -> str:
    return SEPARATEUR.join((PREFIXE, quoi, uid, type_etape))


def _decoder(action: str) -> tuple[str, str, str] | None:
    morceaux = action.split(SEPARATEUR)
    if len(morceaux) != 4 or morceaux[0] != PREFIXE:
        return None
    return morceaux[1], morceaux[2], morceaux[3]
