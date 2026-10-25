"""Montage, dechargement et rechargement de l'integration."""

from __future__ import annotations

from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.setup import async_setup_component
import pytest

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


async def test_le_dechargement_retire_le_panneau(
    hass: HomeAssistant, entree, monter
) -> None:
    """Sinon l'entree restait dans la barre laterale apres suppression de
    l'integration, menant vers un panneau mort."""
    await monter(entree)
    assert "rhizome" in hass.data[frontend.DATA_PANELS]

    assert await hass.config_entries.async_unload(entree.entry_id)
    await hass.async_block_till_done()

    assert "rhizome" not in hass.data[frontend.DATA_PANELS]


async def test_le_panneau_revient_au_rechargement(
    hass: HomeAssistant, entree, monter
) -> None:
    await monter(entree)
    await hass.config_entries.async_reload(entree.entry_id)
    await hass.async_block_till_done()
    assert "rhizome" in hass.data[frontend.DATA_PANELS]


async def test_les_actions_existent_sans_entree_chargee(
    hass: HomeAssistant,
) -> None:
    """Regle Bronze action-setup : l'editeur d'automatisation doit les voir."""
    assert await async_setup_component(hass, "rhizome", {})
    assert "marquer_seme" in hass.services.async_services().get("rhizome", {})


async def test_une_action_sans_entree_chargee_dit_pourquoi(
    hass: HomeAssistant,
) -> None:
    """Et non une RuntimeError, qui remontait en erreur 500 muette."""
    assert await async_setup_component(hass, "rhizome", {})
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "rhizome", "rafraichir", {}, blocking=True
        )


async def test_changer_l_heure_des_rappels_recharge_l_entree(
    hass: HomeAssistant, entree, monter
) -> None:
    """L'heure est lue une seule fois, pour armer le minuteur : sans
    rechargement, la regler n'avait aucun effet jusqu'au redemarrage."""
    coordinateur = await monter(entree, {"notify_heure": "08:00:00"})

    hass.config_entries.async_update_entry(
        entree, options={**entree.options, "notify_heure": "21:00:00"}
    )
    await hass.async_block_till_done()

    assert entree.state is ConfigEntryState.LOADED
    # Un rechargement construit un nouveau coordinateur.
    assert entree.runtime_data is not coordinateur
    assert entree.runtime_data.entry.options["notify_heure"] == "21:00:00"
