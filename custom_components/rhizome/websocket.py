"""Commandes WebSocket du panneau.

Le catalogue (108 fiches) et le journal ne passent pas par l'etat des entites :
un etat Home Assistant n'est pas fait pour transporter cela, et le ferait payer
a chaque client connecte. Le panneau interroge donc directement ces commandes.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
import voluptuous as vol

from . import catalog
from .const import (
    CONF_ARROSAGE_ACTIF,
    CONF_GELEES_DERNIERE,
    CONF_GELEES_PREMIERE,
    CONF_MASQUER_TERMINEES,
    CONF_NOTIFY_ARROSAGE,
    CONF_NOTIFY_ETAPES,
    CONF_NOTIFY_HEURE,
    CONF_NOTIFY_RECOLTE_RECURRENCE,
    CONF_NOTIFY_RESUME,
    CONF_NOTIFY_TARGETS,
    CONF_PRESET_CLIMAT,
    CONF_RAPPEL_JOURS,
    DEFAUT_NOTIFY_HEURE,
    DOMAIN,
    ETAPES_NOTIFIABLES,
    PREFIXE_PERSO,
    PRESET_PERSONNALISE,
    PRESETS_CLIMAT,
    ZONE_PLEINE_TERRE,
)
from .coordinator import RhizomeCoordinator, etape_en_dict, libelle_phase
from .lifecycle import LIBELLES_EVENEMENTS, TYPES_EVENEMENTS, ErreurJournal
from .phenology import (
    ETAPE_PLANTATION,
    ETAPE_SEMIS_DIRECT,
    ETAPE_SEMIS_INTERIEUR,
    Gelees,
    fenetres_theoriques,
)

_MOTIF_JOUR_MOIS = r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
_MOTIF_HEURE = r"^([01][0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$"
# Un identifiant de zone finit dans un attribut HTML du panneau : on ne laisse
# passer que ce que `slugifier()` cote interface produit deja.
_MOTIF_ID_ZONE = r"^[a-z0-9]+(-[a-z0-9]+)*$"

_JOUR_MOIS = vol.Match(_MOTIF_JOUR_MOIS, msg="Format attendu : MM-JJ.")
_HEURE = vol.Match(_MOTIF_HEURE, msg="Format attendu : HH:MM ou HH:MM:SS.")
_ID_ZONE = vol.Match(
    _MOTIF_ID_ZONE, msg="Identifiant de zone : minuscules, chiffres et tirets."
)


def _cibles_possibles(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Destinataires de rappel proposables, et seuls acceptables.

    Les services `notify.mobile_app_*` sont les seuls a transporter des boutons
    d'action ; `persistent_notification` sert de repli sans telephone.
    """
    services = hass.services.async_services().get("notify", {})
    cibles: list[dict[str, Any]] = [
        {
            "value": f"notify.{nom}",
            "label": nom.removeprefix("mobile_app_").replace("_", " ").title(),
            "mobile": True,
        }
        for nom in sorted(services)
        if nom.startswith("mobile_app_")
    ]
    cibles.append(
        {
            "value": "persistent_notification",
            "label": "Notification dans Home Assistant",
            "mobile": False,
        }
    )
    return cibles


def _coordinateur(hass: HomeAssistant) -> RhizomeCoordinator | None:
    entrees = hass.config_entries.async_loaded_entries(DOMAIN)
    return entrees[0].runtime_data if entrees else None


def _arrosage_en_dict(etat) -> dict | None:
    """Serialise l'etat d'arrosage pour le panneau."""
    if etat is None:
        return None
    return {
        "concernee": etat.concernee,
        "dernier": etat.dernier.isoformat() if etat.dernier else None,
        "prochain": etat.prochain.isoformat() if etat.prochain else None,
        "frequence_jours": etat.frequence_jours,
        "jours_restants": etat.jours_restants,
        "a_arroser": etat.a_arroser,
        "en_retard": etat.en_retard,
        "motif_exclusion": etat.motif_exclusion,
    }


def _plante_en_dict(entree: dict, coordinator: RhizomeCoordinator) -> dict[str, Any]:
    plante = entree["plante"]
    fiche = entree["culture"]
    infos = entree["resume"]
    return {
        "uid": entree["uid"],
        "culture_id": fiche["id"],
        "nom": entree["nom_affiche"],
        "emoji": fiche["emoji"],
        "categorie": fiche["categorie"],
        "surnom": plante.get("surnom"),
        "zone": entree["zone"],
        "notifs": plante.get("notifs", True),
        "rappel_jours": plante.get("rappel_jours"),
        "echelonnement_jours": plante.get("echelonnement_jours"),
        "arrosage_actif": plante.get("arrosage_actif", True),
        "arrosage_frequence_jours": plante.get("arrosage_frequence_jours"),
        "arrosage": _arrosage_en_dict(entree.get("arrosage")),
        "arrosages": list(reversed(plante.get("arrosages") or []))[:20],
        "phase": infos["phase"],
        "phase_libelle": libelle_phase(infos["phase"]),
        "perenne": bool(fiche.get("perenne")),
        "prochaine": etape_en_dict(entree["prochaine"]),
        "etapes": [etape_en_dict(e) for e in entree["etapes"]],
        "date_semis": infos["date_semis"].isoformat() if infos["date_semis"] else None,
        "date_mise_en_place": (
            infos["date_mise_en_place"].isoformat()
            if infos["date_mise_en_place"]
            else None
        ),
        "nb_recoltes": infos["nb_recoltes"],
        "total_recolte_g": infos["total_recolte_g"],
        "evenements": [
            {**evt, "libelle": LIBELLES_EVENEMENTS.get(evt["type"], evt["type"])}
            for evt in plante.get("evenements") or []
        ],
        # Pas de `fiche["arrosage"]` ici : la cle porte l'etat calcule de la
        # plante (plus haut), pas les besoins theoriques de la culture. Les
        # deux ont coexiste dans ce meme dictionnaire, et la seconde ecrasait
        # silencieusement la premiere — le panneau n'a jamais vu d'echeance
        # d'arrosage sur une plante. Les besoins de la culture arrivent par
        # `rhizome/culture`, sous `culture.arrosage`.
        "exposition": fiche["exposition"],
    }


@callback
def async_enregistrer(hass: HomeAssistant) -> None:
    for commande in (
        arroser,
        retablir_culture,
        rotation,
        ressemer,
        reglages,
        definir_reglages,
        definir_culture_perso,
        supprimer_culture_perso,
        cultures_perso,
        catalogue,
        fiche_culture,
        jardin,
        ajouter,
        modifier,
        retirer,
        noter,
        annuler,
        definir_zones,
        calendrier,
    ):
        websocket_api.async_register_command(hass, commande)


# --- Lecture ------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/catalogue",
        vol.Optional("requete"): str,
        vol.Optional("categorie"): str,
        vol.Optional("exposition"): str,
        vol.Optional("difficulte_max"): int,
    }
)
@callback
def catalogue(hass, connection, msg) -> None:
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Rhizome n'est pas chargé")
        return

    fiches = coordinator.catalogue
    resultats = fiches.rechercher(
        msg.get("requete", ""),
        categorie=msg.get("categorie"),
        exposition=msg.get("exposition"),
        difficulte_max=msg.get("difficulte_max"),
    )
    gelees = coordinator.gelees
    aujourdhui = coordinator.data["calcule_le"]

    connection.send_result(
        msg["id"],
        {
            "cultures": [
                {
                    **catalog.info_minimale(c),
                    "perso": bool(c.get("perso")),
                    **_semis(c, gelees, aujourdhui),
                }
                for c in resultats
            ],
            "categories": fiches.categories(),
            "total": len(fiches.toutes()),
        },
    )


ETAPES_DE_DEPART = (ETAPE_SEMIS_INTERIEUR, ETAPE_SEMIS_DIRECT, ETAPE_PLANTATION)


def _semis(fiche: dict, gelees: Gelees, aujourdhui) -> dict[str, Any]:
    """Quand cette culture se met-elle en terre, et est-ce le moment ?

    « Qu'est-ce que je peux semer ce week-end ? » est la question la plus utile
    face a un catalogue de cent fiches : elle merite d'etre calculee ici, ou
    les dates de gelees sont connues.
    """
    candidates = [
        etape
        for annee in (aujourdhui.year, aujourdhui.year + 1)
        for etape in fenetres_theoriques(fiche, gelees, 0, annee)
        if etape.type in ETAPES_DE_DEPART and etape.fin >= aujourdhui
    ]
    if not candidates:
        return {"semable_maintenant": False, "prochain_depart": None}

    candidates.sort(key=lambda e: e.debut)
    ouverte = next((e for e in candidates if e.contient(aujourdhui)), None)
    retenue = ouverte or candidates[0]
    return {
        "semable_maintenant": ouverte is not None,
        "prochain_depart": etape_en_dict(retenue),
    }


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/culture", vol.Required("culture_id"): str}
)
@callback
def fiche_culture(hass, connection, msg) -> None:
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Rhizome n'est pas chargé")
        return

    fiche = coordinator.catalogue.culture(msg["culture_id"])
    if fiche is None:
        connection.send_error(msg["id"], "introuvable", "Culture inconnue")
        return

    connection.send_result(
        msg["id"],
        {
            "culture": fiche,
            "compagnes": {
                cle: [catalog.info_minimale(c) for c in fiches]
                for cle, fiches in coordinator.catalogue.compagnes(
                    msg["culture_id"]
                ).items()
            },
            "fenetres": [
                etape_en_dict(e)
                for e in fenetres_theoriques(fiche, coordinator.gelees)
            ],
        },
    )


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/jardin"})
@callback
def jardin(hass, connection, msg) -> None:
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Rhizome n'est pas chargé")
        return

    donnees = coordinator.data
    connection.send_result(
        msg["id"],
        {
            "plantes": [
                _plante_en_dict(entree, coordinator)
                for entree in donnees["plantes"].values()
            ],
            "zones": donnees["zones"],
            "actions": [
                {
                    "uid": a["uid"],
                    "nom": a["nom"],
                    "emoji": a["emoji"],
                    "zone": a["zone"],
                    "etape": etape_en_dict(a["etape"]),
                    "jours_restants": a["jours_restants"],
                    "en_cours": a["en_cours"],
                }
                for a in donnees["actions"]
            ],
            "arrosages": [
                {
                    "uid": a["uid"],
                    "nom": a["nom"],
                    "emoji": a["emoji"],
                    "zone": a["zone"],
                    "etat": _arrosage_en_dict(a["etat"]),
                }
                for a in donnees.get("arrosages", [])
            ],
            "arrosage_actif": coordinator.arrosage_actif,
            "total_recolte_g": donnees["total_recolte_g"],
            "gelees": {
                "derniere": coordinator.gelees.derniere,
                "premiere": coordinator.gelees.premiere,
            },
            "rappel_jours": coordinator.rappel_jours,
        },
    )


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/calendrier", vol.Optional("annee"): int}
)
@callback
def calendrier(hass, connection, msg) -> None:
    """Bandes annuelles par plante, prevues et reelles, pour la vue calendrier."""
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Rhizome n'est pas chargé")
        return

    annee = msg.get("annee") or coordinator.data["calcule_le"].year
    lignes = []
    for entree in coordinator.data["plantes"].values():
        decalage = coordinator.store.decalage_zone(entree["plante"].get("zone"))
        lignes.append(
            {
                "uid": entree["uid"],
                "nom": entree["nom_affiche"],
                "emoji": entree["culture"]["emoji"],
                "zone": entree["zone"]["nom"],
                "prevues": [
                    etape_en_dict(e)
                    for e in fenetres_theoriques(
                        entree["culture"], coordinator.gelees, decalage, annee
                    )
                ],
                "reelles": [etape_en_dict(e) for e in entree["etapes"] if e.reelle],
                "evenements": [
                    evt
                    for evt in entree["plante"].get("evenements") or []
                    if evt["date"][:4] == str(annee)
                ],
            }
        )
    connection.send_result(msg["id"], {"annee": annee, "lignes": lignes})


# --- Ecriture -----------------------------------------------------------------


def _avec_coordinateur(fonction):
    """Resout le coordinateur, remonte proprement les refus du journal."""

    async def enveloppe(hass, connection, msg) -> None:
        coordinator = _coordinateur(hass)
        if coordinator is None:
            connection.send_error(
                msg["id"], "non_charge", "Rhizome n'est pas chargé"
            )
            return
        try:
            resultat = await fonction(coordinator, msg)
        except ErreurJournal as err:
            # Transition refusee ou plante disparue : c'est une erreur d'usage,
            # elle a sa place dans l'interface, pas dans les logs.
            connection.send_error(msg["id"], "refuse", str(err))
            return
        connection.send_result(msg["id"], resultat or {"ok": True})

    enveloppe.__name__ = fonction.__name__
    return enveloppe


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/ajouter",
        vol.Required("culture_id"): str,
        vol.Optional("zone", default=ZONE_PLEINE_TERRE): str,
        vol.Optional("surnom"): vol.Any(str, None),
        vol.Optional("notifs", default=True): bool,
        vol.Optional("echelonnement_jours"): vol.Any(int, None),
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def ajouter(coordinator, msg) -> dict:
    if coordinator.catalogue.culture(msg["culture_id"]) is None:
        raise ErreurJournal(f"Culture inconnue : {msg['culture_id']}")

    # Calcule avant l'ajout : sinon la plante qu'on vient de poser compterait
    # comme son propre antecedent.
    avertissement = coordinator.verifier_rotation(msg["culture_id"], msg["zone"])

    plante = await coordinator.async_appliquer(
        lambda: coordinator.store.ajouter_plante(
            msg["culture_id"],
            zone=msg["zone"],
            surnom=msg.get("surnom"),
            notifs=msg["notifs"],
            echelonnement_jours=msg.get("echelonnement_jours"),
        )
    )
    return {"uid": plante["uid"], "rotation": avertissement}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/modifier",
        vol.Required("uid"): str,
        vol.Optional("zone"): str,
        vol.Optional("surnom"): vol.Any(str, None),
        vol.Optional("notifs"): bool,
        vol.Optional("rappel_jours"): vol.Any(int, None),
        vol.Optional("echelonnement_jours"): vol.Any(int, None),
        # Les deux reglages d'eau d'une plante. Oublies ici lors de l'ajout de
        # l'arrosage : le panneau les envoyait, le schema les refusait, et les
        # deux commandes etaient donc mortes sans que rien ne le signale.
        vol.Optional("arrosage_actif"): bool,
        vol.Optional("arrosage_frequence_jours"): vol.Any(int, None),
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def modifier(coordinator, msg) -> dict:
    champs = {
        cle: msg[cle]
        for cle in (
            "zone", "surnom", "notifs", "rappel_jours", "echelonnement_jours",
            "arrosage_actif", "arrosage_frequence_jours",
        )
        if cle in msg
    }
    await coordinator.async_appliquer(
        lambda: coordinator.store.modifier_plante(msg["uid"], **champs)
    )
    return {"ok": True}


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/retirer", vol.Required("uid"): str}
)
@websocket_api.async_response
@_avec_coordinateur
async def retirer(coordinator, msg) -> dict:
    await coordinator.async_appliquer(
        lambda: coordinator.store.retirer_plante(msg["uid"])
    )
    return {"ok": True}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/noter",
        vol.Required("uid"): str,
        vol.Required("evenement"): vol.In(sorted(TYPES_EVENEMENTS)),
        vol.Optional("date"): vol.Any(str, None),
        vol.Optional("mode"): str,
        vol.Optional("quantite_g"): vol.Any(int, None),
        vol.Optional("cause"): str,
        vol.Optional("note"): str,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def noter(coordinator, msg) -> dict:
    jour = msg.get("date") or coordinator.data["calcule_le"]
    details = {
        cle: msg[cle]
        for cle in ("mode", "quantite_g", "cause", "note")
        if msg.get(cle) is not None
    }
    plante = await coordinator.async_appliquer(
        lambda: coordinator.store.noter(msg["uid"], msg["evenement"], jour, **details)
    )
    return {"phase": plante["phase"]}


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/annuler", vol.Required("uid"): str}
)
@websocket_api.async_response
@_avec_coordinateur
async def annuler(coordinator, msg) -> dict:
    retire = await coordinator.async_appliquer(
        lambda: coordinator.store.annuler(msg["uid"])
    )
    return {"retire": retire}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/zones",
        vol.Required("zones"): [
            {
                vol.Required("id"): _ID_ZONE,
                vol.Required("nom"): str,
                vol.Required("decalage_jours"): int,
                vol.Optional("abritee", default=False): bool,
            }
        ],
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def definir_zones(coordinator, msg) -> dict:
    await coordinator.async_appliquer(
        lambda: coordinator.store.definir_zones(msg["zones"])
    )
    return {"ok": True}


# --- Reglages -----------------------------------------------------------------


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/reglages"})
@callback
def reglages(hass, connection, msg) -> None:
    """Reglages courants, et le choix de destinataires possibles.

    La liste des services de notification est calculee ici plutot que devinee
    cote panneau : elle change quand un telephone est ajoute ou retire.
    """
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Rhizome n'est pas chargé")
        return

    options = dict(coordinator.entry.options)
    cibles = _cibles_possibles(hass)

    connection.send_result(
        msg["id"],
        {
            "options": {
                CONF_PRESET_CLIMAT: options.get(CONF_PRESET_CLIMAT, "oceanique"),
                CONF_GELEES_DERNIERE: coordinator.gelees.derniere,
                CONF_GELEES_PREMIERE: coordinator.gelees.premiere,
                CONF_NOTIFY_TARGETS: options.get(CONF_NOTIFY_TARGETS, []),
                CONF_NOTIFY_HEURE: options.get(
                    CONF_NOTIFY_HEURE, DEFAUT_NOTIFY_HEURE
                ),
                CONF_RAPPEL_JOURS: coordinator.rappel_jours,
                CONF_NOTIFY_ETAPES: coordinator.etapes_notifiables,
                CONF_NOTIFY_RESUME: coordinator.notify_resume,
                CONF_NOTIFY_RECOLTE_RECURRENCE: coordinator.recolte_recurrence,
                CONF_MASQUER_TERMINEES: coordinator.masquer_terminees,
                CONF_ARROSAGE_ACTIF: coordinator.arrosage_actif,
            },
            "cibles_possibles": cibles,
            "presets": PRESETS_CLIMAT,
            "etapes_notifiables": list(ETAPES_NOTIFIABLES),
        },
    )


# Chaque reglage est type ici, et non simplement filtre par son nom. Un
# `rappel_jours` non numerique accepte se retrouvait dans `entry.options`, d'ou
# une ValueError a chaque recalcul : l'integration restait en panne meme apres
# redemarrage, puisque la valeur etait persistee.
SCHEMA_REGLAGES = vol.Schema(
    {
        vol.Optional(CONF_PRESET_CLIMAT): vol.In(
            [*PRESETS_CLIMAT, PRESET_PERSONNALISE]
        ),
        vol.Optional(CONF_GELEES_DERNIERE): _JOUR_MOIS,
        vol.Optional(CONF_GELEES_PREMIERE): _JOUR_MOIS,
        vol.Optional(CONF_NOTIFY_TARGETS): [str],
        vol.Optional(CONF_NOTIFY_HEURE): _HEURE,
        vol.Optional(CONF_RAPPEL_JOURS): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=30)
        ),
        vol.Optional(CONF_NOTIFY_ETAPES): [vol.In(ETAPES_NOTIFIABLES)],
        vol.Optional(CONF_NOTIFY_RESUME): bool,
        vol.Optional(CONF_NOTIFY_RECOLTE_RECURRENCE): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=90)
        ),
        vol.Optional(CONF_MASQUER_TERMINEES): bool,
        vol.Optional(CONF_ARROSAGE_ACTIF): bool,
        vol.Optional(CONF_NOTIFY_ARROSAGE): bool,
    }
)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/reglages/definir",
        vol.Required("options"): dict,
    }
)
# Ecrire dans une entree de configuration est une operation d'administration.
# Sans cette garde, un simple jeton en lecture seule suffisait a rediriger les
# notifications du jardin, ou a y poser une valeur qui paralyse le calcul.
@websocket_api.require_admin
@websocket_api.async_response
@_avec_coordinateur
async def definir_reglages(coordinator, msg) -> dict:
    """Ecrit les reglages dans l'entree de configuration.

    Les reglages globaux restent dans `entry.options` et non dans le stockage
    du jardin : ils restent ainsi modifiables depuis la page d'integration de
    Home Assistant, et le panneau n'est qu'une facon plus agreable d'y acceder.
    """
    inconnues = set(msg["options"]) - set(SCHEMA_REGLAGES.schema)
    propose = {
        cle: val for cle, val in msg["options"].items() if cle not in inconnues
    }
    try:
        propose = SCHEMA_REGLAGES(propose)
    except vol.Invalid as err:
        raise ErreurJournal(f"Réglage invalide : {err}") from err

    # Les destinataires ne sont pas de simples chaines : ils deviennent un nom
    # de service appele chaque matin. On n'accepte que ceux que le panneau
    # propose vraiment.
    if CONF_NOTIFY_TARGETS in propose:
        connues = {c["value"] for c in _cibles_possibles(coordinator.hass)}
        refusees = [c for c in propose[CONF_NOTIFY_TARGETS] if c not in connues]
        if refusees:
            raise ErreurJournal(
                f"Destinataire de notification inconnu : {', '.join(refusees)}."
            )

    fusion = {**coordinator.entry.options, **propose}
    coordinator.hass.config_entries.async_update_entry(
        coordinator.entry, options=fusion
    )
    return {"options": fusion}


# --- Catalogue personnel ------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/culture_perso/definir",
        vol.Required("fiche"): dict,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def definir_culture_perso(coordinator, msg) -> dict:
    fiche = _normaliser_fiche(msg["fiche"], coordinator)
    soucis = catalog.valider_fiche(fiche)
    if soucis:
        raise ErreurJournal(" ".join(soucis))

    def _ecrire() -> dict:
        resultat = coordinator.store.enregistrer_culture(fiche)
        coordinator.recharger_catalogue()
        return resultat

    await coordinator.async_appliquer(_ecrire)
    return {"id": fiche["id"]}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/culture_perso/supprimer",
        vol.Required("culture_id"): str,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def supprimer_culture_perso(coordinator, msg) -> dict:
    def _effacer() -> None:
        coordinator.store.supprimer_culture(msg["culture_id"])
        coordinator.recharger_catalogue()

    await coordinator.async_appliquer(_effacer)
    return {"ok": True}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/culture_perso/retablir",
        vol.Required("culture_id"): str,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def retablir_culture(coordinator, msg) -> dict:
    """Annule une correction et rend la fiche livree."""
    if not coordinator.catalogue.est_livree(msg["culture_id"]):
        raise ErreurJournal(
            "Cette fiche n'existe pas dans le catalogue livré : il n'y a rien "
            "à rétablir. Supprimez-la plutôt."
        )

    def _effacer() -> None:
        coordinator.store.supprimer_culture(msg["culture_id"], retablit=True)
        coordinator.recharger_catalogue()

    await coordinator.async_appliquer(_effacer)
    return {"ok": True}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/rotation",
        vol.Required("culture_id"): str,
        vol.Required("zone"): str,
    }
)
@callback
def rotation(hass, connection, msg) -> None:
    """Avertissement de rotation, avant d'ajouter une plante a une zone."""
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Rhizome n'est pas chargé")
        return
    connection.send_result(
        msg["id"],
        {"avertissement": coordinator.verifier_rotation(msg["culture_id"], msg["zone"])},
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/arroser",
        vol.Required("uid"): vol.Any(str, [str]),
        vol.Optional("date"): vol.Any(str, None),
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def arroser(coordinator, msg) -> dict:
    """Note un arrosage. Accepte plusieurs plantes : « tout arroser » est un
    geste reel, qu'il serait absurde de faire repeter dix fois."""
    uids = msg["uid"] if isinstance(msg["uid"], list) else [msg["uid"]]
    jour = msg.get("date") or coordinator.data["calcule_le"]

    def _noter() -> int:
        for uid in uids:
            coordinator.store.arroser(uid, jour)
        return len(uids)

    nombre = await coordinator.async_appliquer(_noter)
    return {"arrosees": nombre}


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/ressemer", vol.Required("uid"): str}
)
@websocket_api.async_response
@_avec_coordinateur
async def ressemer(coordinator, msg) -> dict:
    """Ouvre le lot suivant d'un semis echelonne."""
    jour = coordinator.data["calcule_le"]
    enfant = await coordinator.async_appliquer(
        lambda: coordinator.store.ressemer(msg["uid"], jour)
    )
    return {"uid": enfant["uid"], "nom": enfant.get("surnom")}


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/cultures_perso"})
@callback
def cultures_perso(hass, connection, msg) -> None:
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Rhizome n'est pas chargé")
        return
    connection.send_result(
        msg["id"], {"cultures": coordinator.catalogue.perso()}
    )


def _normaliser_fiche(brute: dict, coordinator) -> dict:
    """Construit une fiche complete a partir du formulaire du panneau.

    Le formulaire parle en mois ; le moteur parle en fenetres. La conversion
    se fait ici, une seule fois, pour que le reste du code ne connaisse qu'une
    seule forme de fiche.
    """
    nom = (brute.get("nom") or "").strip()
    identifiant = brute.get("id")
    # Corriger une fiche livree conserve son id : la fiche personnelle la
    # remplace alors au lieu de la doubler, et les plantes deja au jardin
    # suivent la correction. Toute autre saisie recoit le prefixe.
    if not identifiant or not (
        identifiant.startswith(PREFIXE_PERSO)
        or coordinator.catalogue.est_livree(identifiant)
    ):
        identifiant = f"{PREFIXE_PERSO}{catalog.slug(nom)}"

    fenetres: dict[str, dict] = {}
    for cle in ("semis_interieur", "semis_direct", "plantation", "recolte"):
        periode = (brute.get("periodes") or {}).get(cle)
        if periode and periode.get("debut"):
            fenetres[cle] = catalog.fenetre_par_mois(
                periode["debut"], periode.get("fin") or periode["debut"]
            )

    # Corriger une fiche livree sans toucher a ses periodes conserve ses
    # fenetres d'origine, ancrees aux gelees. Les convertir en mois les
    # figerait sur le calendrier et leur ferait perdre ce qui les rend justes
    # d'un jardin a l'autre — pour un gain nul, puisque ce qu'on vient
    # corriger est presque toujours une duree de cycle.
    if not fenetres:
        origine = catalog.culture(identifiant)
        if origine:
            fenetres = origine["fenetres"]

    cycle: dict[str, int] = {
        "duree_recolte_jours": int(brute.get("duree_recolte_jours") or 30)
    }
    for cle, source in (
        ("jours_semis_a_repiquage", "jours_semis_a_repiquage"),
        ("jours_semis_a_recolte", "jours_semis_a_recolte"),
        ("jours_plantation_a_recolte", "jours_plantation_a_recolte"),
    ):
        valeur = brute.get(source)
        if valeur:
            cycle[cle] = int(valeur)

    return {
        "id": identifiant,
        "nom": nom,
        "nom_scientifique": (brute.get("nom_scientifique") or "").strip(),
        "famille": (brute.get("famille") or "Non précisée").strip(),
        "categorie": brute.get("categorie"),
        "emoji": (brute.get("emoji") or "🌱")[:4],
        "difficulte": max(1, min(3, int(brute.get("difficulte") or 1))),
        "exposition": brute.get("exposition"),
        "arrosage": {
            "besoin": (brute.get("arrosage") or {}).get("besoin"),
            "frequence_jours": int(
                (brute.get("arrosage") or {}).get("frequence_jours") or 4
            ),
            "notes": ((brute.get("arrosage") or {}).get("notes") or "").strip(),
        },
        "sol": (brute.get("sol") or "ordinaire, bien drainé").strip(),
        "espacement_cm": int(brute.get("espacement_cm") or 30),
        "rusticite": {
            "gel": bool(brute.get("gel", True)),
            "temp_min_c": brute.get("temp_min_c"),
        },
        "perenne": bool(brute.get("perenne")),
        "fenetres": fenetres,
        "cycle": cycle,
        "associations": {"aime": [], "evite": []},
        "conseils": [c for c in (brute.get("conseils") or []) if c.strip()],
        "perso": True,
    }
