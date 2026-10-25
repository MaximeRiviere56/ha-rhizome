"""Socle commun des entites et gestion de leur apparition dynamique.

Particularite de cette integration : ses entites ne sont pas connues au
demarrage. Une plante ajoutee depuis le panneau doit faire apparaitre ses
entites sans rechargement, et une plante retiree doit les faire disparaitre du
registre — sinon le potager se remplirait de capteurs fantomes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PANEL_TITLE
from .coordinator import RhizomeCoordinator

# Convention d'identifiant unique, ecrite ici une seule fois.
#
# Elle etait auparavant construite dans ce fichier et relue dans `__init__.py`,
# a deux cents lignes de distance, par un `split("_")` qui exigeait exactement
# trois morceaux. Cela ne tient que parce qu'un `entry_id` est un ULID sans
# tiret bas et qu'aucun suffixe actuel n'en contient — rien ne le garantissait.
SEPARATEUR_UID = "_"


def unique_id_plante(entry_id: str, uid: str, suffixe: str) -> str:
    return SEPARATEUR_UID.join((entry_id, uid, suffixe))


def uid_depuis_unique_id(entry_id: str, unique_id: str) -> str | None:
    """Rend l'uid de la plante porte par cet identifiant, ou None.

    None pour une entite globale du potager (le calendrier, les totaux), qui
    ne designe aucune plante en particulier.
    """
    prefixe = f"{entry_id}{SEPARATEUR_UID}"
    if not unique_id.startswith(prefixe):
        return None
    reste = unique_id[len(prefixe) :]
    uid, separateur, _suffixe = reste.rpartition(SEPARATEUR_UID)
    return uid if separateur else None


def info_appareil(entry: ConfigEntry) -> DeviceInfo:
    """Un seul appareil regroupe tout : le potager lui-meme.

    Un appareil par plante donnerait une page par legume, mais ferait churner
    le registre a chaque ajout ou retrait.
    """
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=PANEL_TITLE,
        manufacturer="Rhizome",
        entry_type=DeviceEntryType.SERVICE,
    )


class RhizomeEntity(CoordinatorEntity[RhizomeCoordinator]):
    """Base des entites globales du potager."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: RhizomeCoordinator, cle: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{cle}"
        self._attr_device_info = info_appareil(coordinator.entry)


class RhizomePlanteEntity(RhizomeEntity):
    """Base des entites rattachees a une plante du jardin."""

    def __init__(self, coordinator: RhizomeCoordinator, uid: str, suffixe: str) -> None:
        super().__init__(coordinator, SEPARATEUR_UID.join((uid, suffixe)))
        self._uid = uid

    @property
    def entree(self) -> dict | None:
        """La plante telle que calculee, ou None si elle a ete retiree."""
        return self.coordinator.data["plantes"].get(self._uid)

    @property
    def available(self) -> bool:
        return super().available and self.entree is not None

    @property
    def name(self) -> str | None:
        entree = self.entree
        return entree["nom_affiche"] if entree else None


@callback
def suivre_les_plantes(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: RhizomeCoordinator,
    async_add_entities: AddEntitiesCallback,
    fabrique: Callable[[RhizomeCoordinator, str], Iterable],
    plateforme: str,
    suffixe: str,
) -> None:
    """Cree les entites des nouvelles plantes, nettoie celles des disparues."""
    connus: set[str] = set()

    @callback
    def _synchroniser() -> None:
        presents = set(coordinator.data["plantes"])

        nouveaux = presents - connus
        if nouveaux:
            connus.update(nouveaux)
            entites = [
                entite
                for uid in sorted(nouveaux)
                for entite in fabrique(coordinator, uid)
            ]
            if entites:
                async_add_entities(entites)

        for uid in connus - presents:
            connus.discard(uid)
            _retirer_du_registre(hass, entry, uid, plateforme, suffixe)

    _synchroniser()
    entry.async_on_unload(coordinator.async_add_listener(_synchroniser))


@callback
def _retirer_du_registre(
    hass: HomeAssistant,
    entry: ConfigEntry,
    uid: str,
    plateforme: str,
    suffixe: str,
) -> None:
    registre = er.async_get(hass)
    entity_id = registre.async_get_entity_id(
        plateforme, DOMAIN, unique_id_plante(entry.entry_id, uid, suffixe)
    )
    if entity_id:
        registre.async_remove(entity_id)
