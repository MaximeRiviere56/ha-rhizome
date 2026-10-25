"""Les diagnostics doivent renseigner sans livrer le jardin."""

from __future__ import annotations

from datetime import date

from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant

from custom_components.rhizome.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_les_diagnostics_decrivent_le_jardin(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree, {"rappel_jours": 4})
    plante = await ajouter(coordinateur, "tomate", surnom="Cœur de bœuf")
    coordinateur.store.noter(
        plante["uid"], "seme", date(2026, 3, 1), note="semis sous châssis"
    )
    await coordinateur.async_refresh()

    rapport = await async_get_config_entry_diagnostics(hass, entree)

    assert rapport["options"]["rappel_jours"] == 4
    assert rapport["catalogue"]["total"] > 100
    assert len(rapport["plantes"]) == 1
    assert rapport["plantes"][0]["culture_id"] == "tomate"
    assert rapport["plantes"][0]["phase"] == "seme"
    assert rapport["plantes"][0]["nb_evenements"] == 1


async def test_les_textes_libres_ne_sortent_pas(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(
        entree, {"notify_targets": ["persistent_notification"]}
    )
    plante = await ajouter(coordinateur, "tomate", surnom="Cœur de bœuf")
    coordinateur.store.noter(
        plante["uid"], "seme", date(2026, 3, 1), note="derrière chez moi"
    )
    await coordinateur.async_refresh()

    rapport = await async_get_config_entry_diagnostics(hass, entree)
    texte = repr(rapport)

    assert "Cœur de bœuf" not in texte
    assert "derrière chez moi" not in texte
    assert rapport["options"]["notify_targets"] == REDACTED
