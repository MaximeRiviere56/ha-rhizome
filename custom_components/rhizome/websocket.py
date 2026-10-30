"""Commandes WebSocket du panneau.

Le catalogue (108 fiches) et le journal ne passent pas par l'etat des entites :
un etat Home Assistant n'est pas fait pour transporter cela, et le ferait payer
a chaque client connecte. Le panneau interroge donc directement ces commandes.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.auth.permissions.const import POLICY_CONTROL
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from . import catalog, i18n
from .const import (
    CONF_ARROSAGE_ACTIF,
    CONF_GELEES_DERNIERE,
    CONF_GELEES_PREMIERE,
    CONF_LANGUE,
    CONF_MASQUER_TERMINEES,
    CONF_METEO_ENTITE,
    CONF_NOTIFY_ARROSAGE,
    CONF_NOTIFY_ETAPES,
    CONF_NOTIFY_GEL,
    CONF_NOTIFY_GEL_HEURE,
    CONF_NOTIFY_HEURE,
    CONF_NOTIFY_RECOLTE_RECURRENCE,
    CONF_NOTIFY_RESUME,
    CONF_NOTIFY_TARGETS,
    CONF_PRESET_CLIMAT,
    CONF_RAPPEL_JOURS,
    DEFAUT_LANGUE,
    DEFAUT_NOTIFY_GEL_HEURE,
    DEFAUT_NOTIFY_HEURE,
    DOMAIN,
    ETAPES_NOTIFIABLES,
    LANGUE_AUTO,
    LANGUES,
    PREFIXE_PERSO,
    PRESET_PERSONNALISE,
    PRESETS_CLIMAT,
    ZONE_PLEINE_TERRE,
)
from .coordinator import RhizomeCoordinator
from .lifecycle import (
    MODE_SEMIS_DIRECT,
    MODE_SEMIS_INTERIEUR,
    TYPES_EVENEMENTS,
    ErreurJournal,
)
from .phenology import (
    ETAPE_PLANTATION,
    ETAPE_SEMIS_DIRECT,
    ETAPE_SEMIS_INTERIEUR,
    Gelees,
    fenetres_theoriques,
)
from .serialisation import (
    arrosage_en_dict,
    etape_en_dict,
    plante_en_dict,
)

_LOGGER = logging.getLogger(__name__)

_MOTIF_JOUR_MOIS = r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
_MOTIF_HEURE = r"^([01][0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$"
# Un identifiant de zone finit dans un attribut HTML du panneau : on ne laisse
# passer que ce que `slugifier()` cote interface produit deja.
_MOTIF_ID_ZONE = r"^[a-z0-9]+(-[a-z0-9]+)*$"

# Les quatre fenetres qu'un formulaire de fiche sait exprimer en mois.
FENETRES_SAISIES = ("semis_interieur", "semis_direct", "plantation", "recolte")

_JOUR_MOIS = vol.Match(_MOTIF_JOUR_MOIS, msg="Format attendu : MM-JJ.")
_HEURE = vol.Match(_MOTIF_HEURE, msg="Format attendu : HH:MM ou HH:MM:SS.")
_ID_ZONE = vol.Match(
    _MOTIF_ID_ZONE, msg="Identifiant de zone : minuscules, chiffres et tirets."
)

# --- Bornes des valeurs qui finissent dans un calcul de date ------------------
#
# Tout ce qui est ci-dessous atterrit dans le stockage du jardin, puis dans un
# `date + timedelta(...)`. Un entier demesure y leve une `OverflowError` depuis
# `_calculer`, donc a chaque cycle du coordinateur — et comme la valeur est
# persistee, l'integration ne se repare ni au rechargement ni au redemarrage.
# C'est exactement ce que la validation des reglages a corrige pour
# `entry.options` ; le stockage du jardin, lui, n'avait aucune garde.
#
# Les bornes sont celles du sens horticole, pas celles de `timedelta` : un
# decalage de serre se compte en semaines, pas en siecles.
_DECALAGE_ZONE = vol.All(vol.Coerce(int), vol.Range(min=-120, max=120))
_RAPPEL_JOURS = vol.Any(vol.All(vol.Coerce(int), vol.Range(min=0, max=30)), None)
_ECHELONNEMENT = vol.Any(vol.All(vol.Coerce(int), vol.Range(min=0, max=90)), None)
_FREQUENCE_EAU = vol.Any(vol.All(vol.Coerce(int), vol.Range(min=1, max=365)), None)
_QUANTITE_G = vol.Any(
    vol.All(vol.Coerce(int), vol.Range(min=0, max=10_000_000)), None
)

# Une date du journal reste dans les annees ou un potager existe. « 9999-12-31 »
# passait le schema, se rangeait au journal, et faisait deborder le calcul de
# la recolte suivante : meme panne persistante, par un autre chemin.
_MOTIF_DATE = r"^(19|20|21)[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
_DATE = vol.Any(
    vol.Match(_MOTIF_DATE, msg="Date attendue au format AAAA-MM-JJ."), None
)

# Les textes libres finissent dans `.storage/rhizome.jardin`, et le surnom
# devient le nom d'une entite, donc son `entity_id`. Sans borne, un surnom de
# cent mille caracteres produisait un identifiant d'entite de cent mille
# caracteres dans le registre.
_SURNOM = vol.Any(vol.All(cv.string, vol.Length(max=120)), None)
_NOTE = vol.All(cv.string, vol.Length(max=1000))
_NOM_ZONE = vol.All(cv.string, vol.Length(max=80))


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
            "label": i18n.t(_langue(hass), "cible_persistante"),
            "mobile": False,
        }
    )
    return cibles


def _meteo_possibles(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Entites meteo proposables, et seules acceptables.

    Memes raisons que pour les destinataires de rappel : cette valeur devient
    une entite interrogee chaque soir, et accepter une chaine libre reviendrait
    a appeler un service sur n'importe quoi.
    """
    return [
        {
            "value": etat.entity_id,
            "label": etat.name or etat.entity_id,
        }
        for etat in sorted(
            hass.states.async_all("weather"), key=lambda e: e.entity_id
        )
    ]


def _coordinateur(hass: HomeAssistant) -> RhizomeCoordinator | None:
    entrees = hass.config_entries.async_loaded_entries(DOMAIN)
    return entrees[0].runtime_data if entrees else None


def _langue(hass: HomeAssistant) -> str:
    """La langue de l'interface, y compris quand l'entree n'est pas chargee.

    Les commandes de lecture repondent « Rhizome n'est pas chargé » avant
    d'avoir un coordinateur : ce refus doit lui aussi etre dans la bonne
    langue, donc se lire depuis les options de l'entree, chargee ou non.
    """
    entrees = hass.config_entries.async_entries(DOMAIN)
    option = entrees[0].options.get(CONF_LANGUE, DEFAUT_LANGUE) if entrees else None
    return i18n.resoudre(option, getattr(hass.config, "language", None))


def _refus_non_charge(hass: HomeAssistant, connection, msg) -> None:
    connection.send_error(
        msg["id"], "non_charge", i18n.t(_langue(hass), "err_non_charge")
    )


def _peut_ecrire(connection) -> bool:
    """Ce compte a-t-il le droit de modifier le jardin ?

    Une commande WebSocket personnalisee n'herite d'aucun controle : toute
    session authentifiee l'atteint, y compris celle d'un compte en lecture
    seule. Seule `rhizome/reglages/definir` etait gardee, parce qu'elle ecrit
    dans l'entree de configuration. Le reste ne l'etait pas : un jeton en
    lecture seule pouvait ajouter, modifier, noter et surtout **retirer** une
    plante — donc effacer le journal, la seule donnee de ce projet que rien
    ne reconstitue.

    Le critere retenu est celui de Home Assistant lui-meme pour decider si
    quelqu'un peut agir sur l'instance : le droit de controler les entites.
    Administrateurs et comptes ordinaires l'ont ; les comptes en lecture
    seule, non. Jardiner a plusieurs reste donc possible — c'etait le point —
    sans que « lecture seule » cesse de vouloir dire quelque chose.

    `require_admin` aurait ete plus simple et plus faux : le panneau est fait
    pour etre utilise par la maisonnee, pas par le seul administrateur.
    """
    utilisateur = getattr(connection, "user", None)
    if utilisateur is None:
        return False
    return utilisateur.permissions.access_all_entities(POLICY_CONTROL)


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
        _refus_non_charge(hass, connection, msg)
        return

    langue = coordinator.langue
    fiches = coordinator.catalogue
    resultats = fiches.rechercher(
        msg.get("requete", ""),
        langue=langue,
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
                    **catalog.info_minimale(catalog.localiser(c, langue)),
                    "perso": bool(c.get("perso")),
                    **_semis(c, gelees, aujourdhui, langue),
                }
                for c in resultats
            ],
            "categories": fiches.categories(),
            "total": len(fiches.toutes()),
        },
    )


ETAPES_DE_DEPART = (ETAPE_SEMIS_INTERIEUR, ETAPE_SEMIS_DIRECT, ETAPE_PLANTATION)


def _semis(
    fiche: dict, gelees: Gelees, aujourdhui, langue: str = "fr"
) -> dict[str, Any]:
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
        "prochain_depart": etape_en_dict(retenue, langue),
    }


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/culture", vol.Required("culture_id"): str}
)
@callback
def fiche_culture(hass, connection, msg) -> None:
    coordinator = _coordinateur(hass)
    if coordinator is None:
        _refus_non_charge(hass, connection, msg)
        return

    fiche = coordinator.catalogue.culture(msg["culture_id"])
    if fiche is None:
        connection.send_error(msg["id"], "introuvable", "Culture inconnue")
        return

    langue = coordinator.langue
    connection.send_result(
        msg["id"],
        {
            "culture": catalog.localiser(fiche, langue),
            "compagnes": {
                cle: [
                    catalog.info_minimale(catalog.localiser(c, langue))
                    for c in fiches
                ]
                for cle, fiches in coordinator.catalogue.compagnes(
                    msg["culture_id"]
                ).items()
            },
            "fenetres": [
                etape_en_dict(e, langue)
                for e in fenetres_theoriques(
                    fiche, coordinator.gelees, 0, coordinator.data["calcule_le"].year
                )
            ],
        },
    )


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/jardin"})
@callback
def jardin(hass, connection, msg) -> None:
    coordinator = _coordinateur(hass)
    if coordinator is None:
        _refus_non_charge(hass, connection, msg)
        return

    donnees = coordinator.data
    langue = coordinator.langue
    connection.send_result(
        msg["id"],
        {
            "plantes": [
                plante_en_dict(entree, coordinator.langue)
                for entree in donnees["plantes"].values()
            ],
            "zones": donnees["zones"],
            "actions": [
                {
                    "uid": a["uid"],
                    "nom": a["nom"],
                    "emoji": a["emoji"],
                    "zone": a["zone"],
                    "etape": etape_en_dict(a["etape"], langue),
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
                    "etat": arrosage_en_dict(a["etat"], langue),
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
            # Le panneau rend ses propres libelles : il a besoin de savoir dans
            # quelle langue le serveur lui parle, pour ne pas melanger les deux.
            "langue": langue,
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
        _refus_non_charge(hass, connection, msg)
        return

    annee = msg.get("annee") or coordinator.data["calcule_le"].year
    langue = coordinator.langue
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
                    etape_en_dict(e, langue)
                    for e in fenetres_theoriques(
                        entree["culture"], coordinator.gelees, decalage, annee
                    )
                ],
                "reelles": [
                    etape_en_dict(e, langue) for e in entree["etapes"] if e.reelle
                ],
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
    """Resout le coordinateur, verifie le droit d'ecrire, et remonte
    proprement les refus du journal.

    Toutes les commandes d'ecriture passent par ici : c'est le seul endroit
    ou poser la garde, et le seul ou l'oublier serait invisible.
    """

    async def enveloppe(hass, connection, msg) -> None:
        if not _peut_ecrire(connection):
            connection.send_error(
                msg["id"],
                websocket_api.const.ERR_UNAUTHORIZED,
                i18n.t(_langue(hass), "err_lecture_seule"),
            )
            return

        coordinator = _coordinateur(hass)
        if coordinator is None:
            _refus_non_charge(hass, connection, msg)
            return
        try:
            resultat = await fonction(coordinator, msg)
        except ErreurJournal as err:
            # Transition refusee ou plante disparue : c'est une erreur d'usage,
            # elle a sa place dans l'interface, pas dans les logs. Le moteur
            # l'a levee en francais avec sa cle : on la rend ici dans la langue
            # de l'interface.
            connection.send_error(
                msg["id"], "refuse", i18n.traduire_erreur(coordinator.langue, err)
            )
            return
        except (TypeError, ValueError, KeyError) as err:
            # Une saisie mal formee (une difficulte non numerique, un conseil
            # qui n'est pas une chaine) partait en erreur 500 : le panneau
            # n'affichait rien et le motif restait dans les logs.
            _LOGGER.debug("Commande %s refusee : %s", msg.get("type"), err)
            connection.send_error(
                msg["id"],
                "saisie_invalide",
                i18n.t(coordinator.langue, "err_saisie_invalide", detail=err),
            )
            return
        connection.send_result(msg["id"], resultat or {"ok": True})

    enveloppe.__name__ = fonction.__name__
    return enveloppe


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/ajouter",
        vol.Required("culture_id"): str,
        vol.Optional("zone", default=ZONE_PLEINE_TERRE): _ID_ZONE,
        vol.Optional("surnom"): _SURNOM,
        vol.Optional("notifs", default=True): bool,
        vol.Optional("echelonnement_jours"): _ECHELONNEMENT,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def ajouter(coordinator, msg) -> dict:
    if coordinator.catalogue.culture(msg["culture_id"]) is None:
        raise ErreurJournal(
            f"Culture inconnue : {msg['culture_id']}",
            cle="err_culture_inconnue",
            culture_id=msg["culture_id"],
        )

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
        vol.Optional("zone"): _ID_ZONE,
        vol.Optional("surnom"): _SURNOM,
        vol.Optional("notifs"): bool,
        vol.Optional("rappel_jours"): _RAPPEL_JOURS,
        vol.Optional("echelonnement_jours"): _ECHELONNEMENT,
        # Les deux reglages d'eau d'une plante. Oublies ici lors de l'ajout de
        # l'arrosage : le panneau les envoyait, le schema les refusait, et les
        # deux commandes etaient donc mortes sans que rien ne le signale.
        vol.Optional("arrosage_actif"): bool,
        vol.Optional("arrosage_frequence_jours"): _FREQUENCE_EAU,
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
        vol.Optional("date"): _DATE,
        # Les deux seuls modes de semis, comme le service le fait deja. Le
        # schema acceptait n'importe quelle chaine, qui se rangeait au
        # journal et ressortait telle quelle dans le panneau.
        vol.Optional("mode"): vol.In([MODE_SEMIS_DIRECT, MODE_SEMIS_INTERIEUR]),
        vol.Optional("quantite_g"): _QUANTITE_G,
        vol.Optional("cause"): _NOTE,
        vol.Optional("note"): _NOTE,
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
                vol.Required("nom"): _NOM_ZONE,
                vol.Required("decalage_jours"): _DECALAGE_ZONE,
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
        _refus_non_charge(hass, connection, msg)
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
                # Le reglage brut, qui peut valoir « auto » : le selecteur du
                # panneau doit montrer ce qui a ete choisi, pas seulement ce
                # qui en a ete deduit.
                CONF_LANGUE: options.get(CONF_LANGUE, DEFAUT_LANGUE),
                CONF_METEO_ENTITE: coordinator.meteo_entite,
                CONF_NOTIFY_GEL: coordinator.notify_gel,
                CONF_NOTIFY_GEL_HEURE: options.get(
                    CONF_NOTIFY_GEL_HEURE, DEFAUT_NOTIFY_GEL_HEURE
                ),
            },
            "cibles_possibles": cibles,
            "meteo_possibles": _meteo_possibles(hass),
            "presets": PRESETS_CLIMAT,
            "etapes_notifiables": list(ETAPES_NOTIFIABLES),
            # La langue reellement appliquee, « auto » resolu. C'est elle que le
            # panneau emploie pour ses propres libelles.
            "langue": coordinator.langue,
            "langues": list(LANGUES),
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
        # Une chaine vide est une valeur legitime : c'est ainsi qu'on coupe
        # l'alerte gel sans avoir a decocher autre chose.
        vol.Optional(CONF_METEO_ENTITE): vol.Any("", str),
        vol.Optional(CONF_NOTIFY_GEL): bool,
        vol.Optional(CONF_NOTIFY_GEL_HEURE): _HEURE,
        # Borne stricte : cette valeur decide de la langue des noms d'entites,
        # relus a chaque montage. Une chaine libre y produirait une interface
        # a moitie francaise sans rien signaler.
        vol.Optional(CONF_LANGUE): vol.In([LANGUE_AUTO, *LANGUES]),
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
        raise ErreurJournal(
            f"Réglage invalide : {err}", cle="err_reglage_invalide", detail=err
        ) from err

    # Les destinataires ne sont pas de simples chaines : ils deviennent un nom
    # de service appele chaque matin. On n'accepte que ceux que le panneau
    # propose vraiment.
    if CONF_NOTIFY_TARGETS in propose:
        connues = {c["value"] for c in _cibles_possibles(coordinator.hass)}
        refusees = [c for c in propose[CONF_NOTIFY_TARGETS] if c not in connues]
        if refusees:
            raise ErreurJournal(
                f"Destinataire de notification inconnu : {', '.join(refusees)}.",
                cle="err_cible_notif",
                cibles=", ".join(refusees),
            )

    # Meme garde que pour les destinataires : cette entite sera interrogee
    # par un appel de service, elle ne peut pas etre une chaine quelconque.
    if propose.get(CONF_METEO_ENTITE):
        connues = {m["value"] for m in _meteo_possibles(coordinator.hass)}
        if propose[CONF_METEO_ENTITE] not in connues:
            raise ErreurJournal(
                f"Entité météo inconnue : {propose[CONF_METEO_ENTITE]}.",
                cle="err_meteo_inconnue",
                entite=propose[CONF_METEO_ENTITE],
            )

    fusion = {**coordinator.entry.options, **propose}
    coordinator.hass.config_entries.async_update_entry(
        coordinator.entry, options=fusion
    )
    return {"options": fusion}


# --- Catalogue personnel ------------------------------------------------------


# Une fiche personnelle va dans le stockage du jardin, et son texte s'affiche
# dans le panneau : on borne les longueurs et on type les nombres, plutot que
# d'accepter n'importe quel dictionnaire.
_TEXTE = vol.All(cv.string, vol.Length(max=200))
_TEXTE_LONG = vol.All(cv.string, vol.Length(max=1000))
_MOIS = vol.All(vol.Coerce(int), vol.Range(min=1, max=12))
_PERIODE = vol.Schema(
    {vol.Optional("debut"): vol.Any(_MOIS, None), vol.Optional("fin"): vol.Any(_MOIS, None)}
)

SCHEMA_FICHE = vol.Schema(
    {
        vol.Optional("id"): vol.Any(vol.All(cv.string, vol.Length(max=120)), None),
        # Pas de longueur minimale : un nom vide a droit au message de
        # `valider_fiche`, plus parlant qu'un refus de schema.
        vol.Required("nom"): vol.All(cv.string, vol.Length(max=120)),
        vol.Optional("nom_scientifique"): _TEXTE,
        vol.Optional("famille"): _TEXTE,
        vol.Optional("categorie"): vol.Any(cv.string, None),
        vol.Optional("emoji"): vol.All(cv.string, vol.Length(max=8)),
        vol.Optional("difficulte"): vol.Any(vol.Coerce(int), None),
        vol.Optional("exposition"): vol.Any(cv.string, None),
        vol.Optional("arrosage"): vol.Schema(
            {
                vol.Optional("besoin"): vol.Any(cv.string, None),
                vol.Optional("frequence_jours"): vol.Any(vol.Coerce(int), None),
                vol.Optional("notes"): _TEXTE_LONG,
            }
        ),
        vol.Optional("sol"): _TEXTE,
        vol.Optional("espacement_cm"): vol.Any(
            vol.All(vol.Coerce(int), vol.Range(min=1, max=2000)), None
        ),
        vol.Optional("gel"): bool,
        vol.Optional("temp_min_c"): vol.Any(vol.Coerce(float), None),
        vol.Optional("perenne"): bool,
        vol.Optional("periodes"): {vol.In(FENETRES_SAISIES): vol.Any(_PERIODE, None)},
        vol.Optional("duree_recolte_jours"): vol.Any(
            vol.All(vol.Coerce(int), vol.Range(min=1, max=365)), None
        ),
        vol.Optional("jours_semis_a_repiquage"): vol.Any(
            vol.All(vol.Coerce(int), vol.Range(min=0, max=400)), None
        ),
        vol.Optional("jours_semis_a_recolte"): vol.Any(
            vol.All(vol.Coerce(int), vol.Range(min=0, max=2000)), None
        ),
        vol.Optional("jours_plantation_a_recolte"): vol.Any(
            vol.All(vol.Coerce(int), vol.Range(min=0, max=2000)), None
        ),
        vol.Optional("conseils"): vol.All([_TEXTE_LONG], vol.Length(max=20)),
    },
    extra=vol.REMOVE_EXTRA,
)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/culture_perso/definir",
        vol.Required("fiche"): dict,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def definir_culture_perso(coordinator, msg) -> dict:
    try:
        brute = SCHEMA_FICHE(msg["fiche"])
    except vol.Invalid as err:
        raise ErreurJournal(
            f"Fiche invalide : {err}", cle="err_fiche_invalide", detail=err
        ) from err
    fiche = _normaliser_fiche(brute, coordinator)
    # `valider_fiche` rend des cles : ces messages s'affichent dans le
    # formulaire du panneau, donc dans la langue de l'interface.
    soucis = catalog.valider_fiche(fiche)
    if soucis:
        # Rendu ici, et non porte comme cle : on est deja dans la couche qui
        # connait la langue, et il y a plusieurs messages a joindre.
        raise ErreurJournal(
            " ".join(i18n.t(coordinator.langue, cle) for cle in soucis)
        )

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
            "à rétablir. Supprimez-la plutôt.",
            cle="err_rien_a_retablir",
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
        _refus_non_charge(hass, connection, msg)
        return
    connection.send_result(
        msg["id"],
        {"avertissement": coordinator.verifier_rotation(msg["culture_id"], msg["zone"])},
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/arroser",
        # Borne le lot : « tout arroser » vise le jardin, pas dix mille uid.
        vol.Required("uid"): vol.Any(str, vol.All([str], vol.Length(max=500))),
        vol.Optional("date"): _DATE,
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
        _refus_non_charge(hass, connection, msg)
        return
    langue = coordinator.langue
    connection.send_result(
        msg["id"],
        {
            "cultures": [
                catalog.localiser(c, langue)
                for c in coordinator.catalogue.perso(langue)
            ]
        },
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
    for cle in FENETRES_SAISIES:
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
        "famille": (
            brute.get("famille") or i18n.t(coordinator.langue, "famille_inconnue")
        ).strip(),
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
        "sol": (
            brute.get("sol") or i18n.t(coordinator.langue, "sol_defaut")
        ).strip(),
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
