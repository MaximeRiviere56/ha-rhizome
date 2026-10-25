"""Harnais des tests qui ont besoin d'une vraie instance Home Assistant.

Les tests de `tests/` restent purs et tournent sous `unittest` avec le Python
du systeme. Ceux de ce dossier demandent `pytest-homeassistant-custom-component`
et un Python 3.14 : ils sont separes pour que la decouverte `unittest` ne les
voie pas.
"""

from __future__ import annotations

import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[2]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import pytest  # noqa: E402
from pytest_homeassistant_custom_component.common import MockConfigEntry  # noqa: E402

# `pytest-homeassistant-custom-component` livre son propre paquet
# `custom_components`, qui gagne la resolution d'import. Le loader de Home
# Assistant lit `custom_components.__path__` : on y ajoute le notre, sans quoi
# l'integration reste introuvable.
import custom_components  # noqa: E402

_NOTRE_CHEMIN = str(RACINE / "custom_components")
if _NOTRE_CHEMIN not in custom_components.__path__:
    custom_components.__path__.append(_NOTRE_CHEMIN)

@pytest.fixture(autouse=True)
def _integrations_personnalisees(enable_custom_integrations):
    """Toutes les suites de ce dossier chargent l'integration locale."""
    return


@pytest.fixture
def entree() -> MockConfigEntry:
    return MockConfigEntry(domain="rhizome", title="Rhizome", data={}, options={})


@pytest.fixture
def monter(hass):
    """Monte l'integration et rend son coordinateur."""
    from homeassistant.setup import async_setup_component

    async def _monter(entree, options=None):
        assert await async_setup_component(hass, "rhizome", {})
        entree.add_to_hass(hass)
        if options:
            hass.config_entries.async_update_entry(entree, options=dict(options))
        assert await hass.config_entries.async_setup(entree.entry_id)
        await hass.async_block_till_done()
        return entree.runtime_data

    return _monter


@pytest.fixture
def ajouter():
    """Ajoute une plante au jardin et rend son dictionnaire."""

    async def _ajouter(coordinateur, culture_id="tomate", **kwargs):
        return await coordinateur.async_appliquer(
            lambda: coordinateur.store.ajouter_plante(culture_id, **kwargs)
        )

    return _ajouter
