"""Rhizome : catalogue, jardin virtuel, calendrier et rappels."""

from __future__ import annotations

from contextlib import contextmanager
import logging
from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_FINAL_WRITE, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from . import catalog, websocket
from .const import (
    DOMAIN,
    PANEL_ICON,
    PANEL_PATH,
    PANEL_TITLE,
    PANEL_URL,
    SERVICE_AJOUTER_PLANTE,
    SERVICE_ANNULER,
    SERVICE_ARROSER,
    SERVICE_MARQUER_PERDU,
    SERVICE_MARQUER_RECOLTE,
    SERVICE_MARQUER_REPIQUE,
    SERVICE_MARQUER_SEME,
    SERVICE_MARQUER_TERMINE,
    SERVICE_RAFRAICHIR,
    SERVICE_RESSEMER,
    SERVICE_RETIRER_PLANTE,
    ZONE_PLEINE_TERRE,
)
from .coordinator import RhizomeCoordinator
from .lifecycle import (
    EVT_PERDU,
    EVT_RECOLTE,
    EVT_REPIQUE,
    EVT_SEME,
    EVT_TERMINE,
    MODE_SEMIS_DIRECT,
    MODE_SEMIS_INTERIEUR,
    ErreurJournal,
)
from .notifier import RhizomeNotifier
from .store import JardinStore

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.CALENDAR, Platform.TODO]

# Alias ecrit en affectation simple, et non avec le mot-cle `type` de PEP 695 :
# cela reste parsable par un Python 3.9, donc verifiable en local avant
# d'atterrir sur l'instance.
RhizomeEntry = ConfigEntry[RhizomeCoordinator]

# --- Schemas des services -----------------------------------------------------

# Une plante se designe par son `uid` (visible dans les attributs de son
# capteur) ou, plus simplement, par l'entite elle-meme : c'est la facon
# naturelle de cibler quelque chose dans Home Assistant.
SCHEMA_UID = vol.Schema(
    vol.All(
        {
            vol.Optional("uid"): cv.string,
            vol.Optional("entity_id"): cv.entity_id,
        },
        cv.has_at_least_one_key("uid", "entity_id"),
    )
)

SCHEMA_AJOUTER = vol.Schema(
    {
        vol.Required("culture_id"): cv.string,
        vol.Optional("zone", default=ZONE_PLEINE_TERRE): cv.string,
        vol.Optional("surnom"): cv.string,
        vol.Optional("notifs", default=True): cv.boolean,
        vol.Optional("echelonnement_jours"): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=90)
        ),
    }
)

SCHEMA_CIBLE = vol.Schema(
    {
        vol.Optional("uid"): cv.string,
        vol.Optional("entity_id"): cv.entity_id,
    }
)

SCHEMA_SEMIS = SCHEMA_CIBLE.extend(
    {
        vol.Optional("date"): cv.date,
        vol.Optional("mode", default=MODE_SEMIS_DIRECT): vol.In(
            [MODE_SEMIS_DIRECT, MODE_SEMIS_INTERIEUR]
        ),
        vol.Optional("note"): cv.string,
    }
)

SCHEMA_DATE = SCHEMA_CIBLE.extend(
    {vol.Optional("date"): cv.date, vol.Optional("note"): cv.string}
)

SCHEMA_RECOLTE = SCHEMA_DATE.extend(
    {vol.Optional("quantite_g"): vol.All(vol.Coerce(int), vol.Range(min=0))}
)

SCHEMA_PERDU = SCHEMA_DATE.extend({vol.Optional("cause"): cv.string})


def _resoudre_uid(hass: HomeAssistant, call: ServiceCall) -> str:
    """Rend l'uid de la plante visee, qu'on l'ait designee par uid ou entite."""
    uid = call.data.get("uid")
    if uid:
        return uid

    entity_id = call.data.get("entity_id")
    if not entity_id:
        raise ServiceValidationError(
            "Indiquez la plante : son `uid` (attribut de son capteur) ou son "
            "`entity_id`."
        )

    entree = er.async_get(hass).async_get(entity_id)
    if entree is None or entree.platform != DOMAIN:
        raise ServiceValidationError(
            f"{entity_id} n'est pas une entite de Rhizome."
        )

    # unique_id = <entry_id>_<uid>_<suffixe>
    morceaux = entree.unique_id.split("_")
    if len(morceaux) != 3:
        raise ServiceValidationError(
            f"{entity_id} ne designe pas une plante du jardin."
        )
    return morceaux[1]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Enregistre ce qui ne doit l'etre qu'une fois, quel que soit le nombre
    d'entrees : les commandes WebSocket du panneau."""
    websocket.async_enregistrer(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: RhizomeEntry) -> bool:
    # Lecture du catalogue hors boucle d'evenements : c'est de l'I/O fichier.
    await hass.async_add_executor_job(catalog.charger)

    store = JardinStore(hass)
    await store.async_charger()

    coordinator = RhizomeCoordinator(hass, entry, store)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await _async_enregistrer_panneau(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    notifier = RhizomeNotifier(hass, coordinator)
    entry.async_on_unload(notifier.async_demarrer())

    _async_enregistrer_services(hass)
    entry.async_on_unload(entry.add_update_listener(_async_options_modifiees))

    # Filet de securite : Home Assistant n'appelle pas toujours
    # `async_unload_entry` quand il s'arrete. Cet evenement, lui, est le
    # dernier moment garanti pour ecrire sur disque.
    async def _ecrire_a_l_arret(_event) -> None:
        await store.async_sauvegarder_maintenant()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_FINAL_WRITE, _ecrire_a_l_arret)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RhizomeEntry) -> bool:
    decharge = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if decharge:
        await entry.runtime_data.store.async_sauvegarder_maintenant()
    return decharge


async def _async_options_modifiees(hass: HomeAssistant, entry: RhizomeEntry) -> None:
    """Changer les dates de gelees ou les zones redessine tout le calendrier."""
    await entry.runtime_data.async_refresh()


# --- Panneau ------------------------------------------------------------------


async def _async_enregistrer_panneau(hass: HomeAssistant) -> None:
    """Sert le bundle du panneau et l'ajoute a la barre laterale.

    Garde explicite contre un second enregistrement : avec plusieurs entrees,
    ou apres un rechargement, HA leverait sinon une erreur de panneau existant.
    """
    if DOMAIN in hass.data.setdefault(f"{DOMAIN}_panneau", {}):
        return

    dossier = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_URL, str(dossier), cache_headers=False)]
    )

    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_PATH,
        webcomponent_name="rhizome-panel",
        module_url=f"{PANEL_URL}/rhizome-panel.js",
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=False,
        embed_iframe=False,
    )
    hass.data[f"{DOMAIN}_panneau"][DOMAIN] = True


# --- Services -----------------------------------------------------------------


@contextmanager
def _refus_lisible():
    """Transforme un refus du journal en erreur de validation.

    Sans cela, une transition impossible ou une plante disparue remonte en
    HTTP 500 « Server got itself in trouble » : l'utilisateur n'apprend rien,
    et le vrai motif reste dans les logs.
    """
    try:
        yield
    except ErreurJournal as err:
        raise ServiceValidationError(str(err)) from err


def _async_enregistrer_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_AJOUTER_PLANTE):
        return

    def _coordinateur() -> RhizomeCoordinator:
        entrees = hass.config_entries.async_loaded_entries(DOMAIN)
        if not entrees:
            raise RuntimeError("Rhizome n'est pas charge.")
        return entrees[0].runtime_data

    async def ajouter(call: ServiceCall) -> None:
        coord = _coordinateur()
        if coord.catalogue.culture(call.data["culture_id"]) is None:
            raise ServiceValidationError(
                f"Culture inconnue : {call.data['culture_id']}. "
                f"Les identifiants sont ceux du catalogue, par exemple « tomate »."
            )
        await coord.async_appliquer(
            lambda: coord.store.ajouter_plante(
                call.data["culture_id"],
                zone=call.data["zone"],
                surnom=call.data.get("surnom"),
                notifs=call.data["notifs"],
                echelonnement_jours=call.data.get("echelonnement_jours"),
            )
        )

    async def retirer(call: ServiceCall) -> None:
        coord = _coordinateur()
        uid = _resoudre_uid(hass, call)
        with _refus_lisible():
            await coord.async_appliquer(lambda: coord.store.retirer_plante(uid))

    def _noteur(type_evt: str, *champs: str):
        async def noter(call: ServiceCall) -> None:
            coord = _coordinateur()
            uid = _resoudre_uid(hass, call)
            jour = call.data.get("date") or coord.data["calcule_le"]
            details = {
                champ: call.data[champ] for champ in champs if champ in call.data
            }
            with _refus_lisible():
                await coord.async_appliquer(
                    lambda: coord.store.noter(uid, type_evt, jour, **details)
                )

        return noter

    async def arroser(call: ServiceCall) -> None:
        coord = _coordinateur()
        uid = _resoudre_uid(hass, call)
        jour = call.data.get("date") or coord.data["calcule_le"]
        note = call.data.get("note")
        with _refus_lisible():
            await coord.async_appliquer(
                lambda: coord.store.arroser(uid, jour, note)
            )

    async def ressemer(call: ServiceCall) -> None:
        coord = _coordinateur()
        uid = _resoudre_uid(hass, call)
        jour = call.data.get("date") or coord.data["calcule_le"]
        with _refus_lisible():
            await coord.async_appliquer(lambda: coord.store.ressemer(uid, jour))

    async def annuler(call: ServiceCall) -> None:
        coord = _coordinateur()
        uid = _resoudre_uid(hass, call)
        with _refus_lisible():
            await coord.async_appliquer(lambda: coord.store.annuler(uid))

    async def rafraichir(_: ServiceCall) -> None:
        await _coordinateur().async_refresh()

    inscriptions = (
        (SERVICE_AJOUTER_PLANTE, ajouter, SCHEMA_AJOUTER),
        (SERVICE_RETIRER_PLANTE, retirer, SCHEMA_UID),
        (SERVICE_MARQUER_SEME, _noteur(EVT_SEME, "mode", "note"), SCHEMA_SEMIS),
        (SERVICE_MARQUER_REPIQUE, _noteur(EVT_REPIQUE, "note"), SCHEMA_DATE),
        (
            SERVICE_MARQUER_RECOLTE,
            _noteur(EVT_RECOLTE, "quantite_g", "note"),
            SCHEMA_RECOLTE,
        ),
        (SERVICE_MARQUER_PERDU, _noteur(EVT_PERDU, "cause", "note"), SCHEMA_PERDU),
        (SERVICE_MARQUER_TERMINE, _noteur(EVT_TERMINE, "note"), SCHEMA_DATE),
        (SERVICE_ARROSER, arroser, SCHEMA_DATE),
        (SERVICE_RESSEMER, ressemer, SCHEMA_DATE),
        (SERVICE_ANNULER, annuler, SCHEMA_UID),
        (SERVICE_RAFRAICHIR, rafraichir, vol.Schema({})),
    )
    for nom, fonction, schema in inscriptions:
        hass.services.async_register(DOMAIN, nom, fonction, schema=schema)
