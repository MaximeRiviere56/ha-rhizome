"""Les actions `rhizome.*`, et la facon de designer une plante.

Une plante se vise par son `uid` ou, plus simplement, par l'entite de son
capteur. La seconde forme relisait l'identifiant unique a la main, a deux
cents lignes du code qui le construit.
"""

from __future__ import annotations

from datetime import date

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
import pytest


async def test_viser_une_plante_par_son_uid(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "radis")

    await hass.services.async_call(
        "rhizome",
        "marquer_seme",
        {"uid": plante["uid"], "date": date(2026, 4, 1)},
        blocking=True,
    )

    assert coordinateur.store.plante(plante["uid"])["phase"] == "seme"


async def test_viser_une_plante_par_son_entite(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "radis", surnom="rond écarlate")
    await hass.async_block_till_done()

    entity_id = next(
        i for i in hass.states.async_entity_ids("sensor") if "ecarlate" in i
    )
    await hass.services.async_call(
        "rhizome",
        "marquer_seme",
        {"entity_id": entity_id, "date": date(2026, 4, 1)},
        blocking=True,
    )

    assert coordinateur.store.plante(plante["uid"])["phase"] == "seme"


async def test_viser_une_entite_globale_est_refuse(
    hass: HomeAssistant, entree, monter
) -> None:
    """Le calendrier du potager ne designe aucune plante en particulier."""
    await monter(entree)

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "rhizome",
            "marquer_seme",
            {"entity_id": "sensor.rhizome_actions_a_mener"},
            blocking=True,
        )


async def test_viser_une_entite_etrangere_est_refuse(
    hass: HomeAssistant, entree, monter
) -> None:
    await monter(entree)
    hass.states.async_set("sensor.ailleurs", "42")

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "rhizome", "marquer_seme", {"entity_id": "sensor.ailleurs"}, blocking=True
        )


async def test_une_transition_impossible_est_expliquee(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "radis")
    coordinateur.store.noter(plante["uid"], "seme", date(2026, 4, 1))

    with pytest.raises(ServiceValidationError, match="Semé"):
        await hass.services.async_call(
            "rhizome", "marquer_seme", {"uid": plante["uid"]}, blocking=True
        )


async def test_une_culture_inconnue_est_expliquee(
    hass: HomeAssistant, entree, monter
) -> None:
    await monter(entree)

    with pytest.raises(ServiceValidationError, match="Culture inconnue"):
        await hass.services.async_call(
            "rhizome", "ajouter_plante", {"culture_id": "dragonnier-de-mars"},
            blocking=True,
        )
