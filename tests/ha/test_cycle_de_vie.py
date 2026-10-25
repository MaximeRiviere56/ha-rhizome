"""Montage, dechargement et rechargement de l'integration."""

from __future__ import annotations

from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

ENTITES_GLOBALES = {
    "sensor.rhizome_actions_a_mener",
    "sensor.rhizome_a_arroser",
    "sensor.rhizome_recolte_de_la_saison",
    "calendar.rhizome",
    "todo.rhizome",
}


async def test_montage_cree_les_entites_globales(hass: HomeAssistant, entree, monter) -> None:
    await monter(entree)
    assert set(hass.states.async_entity_ids()) >= ENTITES_GLOBALES
    assert entree.state is ConfigEntryState.LOADED


async def test_montage_enregistre_les_services(hass: HomeAssistant, entree, monter) -> None:
    await monter(entree)
    services = hass.services.async_services().get("rhizome", {})
    assert "ajouter_plante" in services
    assert "marquer_seme" in services


async def test_montage_pose_le_panneau(hass: HomeAssistant, entree, monter) -> None:
    await monter(entree)
    assert "rhizome" in hass.data[frontend.DATA_PANELS]


async def test_rechargement(hass: HomeAssistant, entree, monter) -> None:
    await monter(entree)
    await hass.config_entries.async_reload(entree.entry_id)
    await hass.async_block_till_done()
    assert entree.state is ConfigEntryState.LOADED
    assert set(hass.states.async_entity_ids()) >= ENTITES_GLOBALES
