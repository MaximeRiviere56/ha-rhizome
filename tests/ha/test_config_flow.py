"""Config flow et flux d'options.

Regle Bronze config-flow-test-coverage : ce chemin doit etre couvert
entierement. C'est aussi le seul endroit ou un utilisateur saisit des dates
a la main.
"""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

SAISIE = {
    "preset_climat": "oceanique",
    "gelees_derniere": "04-15",
    "gelees_premiere": "11-15",
    "notify_targets": [],
    "notify_heure": "08:00:00",
    "arrosage_actif": True,
    "rappel_jours": 3,
}


async def test_le_formulaire_s_ouvre(hass: HomeAssistant) -> None:
    flux = await hass.config_entries.flow.async_init(
        "rhizome", context={"source": config_entries.SOURCE_USER}
    )
    assert flux["type"] is FlowResultType.FORM
    assert flux["step_id"] == "user"


async def test_creation_avec_un_preset(hass: HomeAssistant) -> None:
    flux = await hass.config_entries.flow.async_init(
        "rhizome", context={"source": config_entries.SOURCE_USER}
    )
    resultat = await hass.config_entries.flow.async_configure(
        flux["flow_id"], {**SAISIE, "preset_climat": "montagne"}
    )

    assert resultat["type"] is FlowResultType.CREATE_ENTRY
    # Le preset prime sur les dates saisies : sinon le choix ne voudrait rien
    # dire pour qui ne connait pas ses gelees.
    assert resultat["options"]["gelees_derniere"] == "05-25"
    assert resultat["options"]["gelees_premiere"] == "10-01"


async def test_les_dates_personnalisees_sont_conservees(
    hass: HomeAssistant,
) -> None:
    flux = await hass.config_entries.flow.async_init(
        "rhizome", context={"source": config_entries.SOURCE_USER}
    )
    resultat = await hass.config_entries.flow.async_configure(
        flux["flow_id"],
        {**SAISIE, "preset_climat": "personnalise", "gelees_derniere": "03-10"},
    )

    assert resultat["options"]["gelees_derniere"] == "03-10"


async def test_une_date_malformee_est_refusee(hass: HomeAssistant) -> None:
    """Home Assistant rejette la saisie au schema et reaffiche le formulaire
    avec le message ; c'est une `InvalidData`, pas un resultat de flux."""
    flux = await hass.config_entries.flow.async_init(
        "rhizome", context={"source": config_entries.SOURCE_USER}
    )

    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(
            flux["flow_id"],
            {**SAISIE, "preset_climat": "personnalise", "gelees_derniere": "15/04"},
        )


async def test_une_seule_entree_possible(hass: HomeAssistant, entree) -> None:
    """Un seul potager par instance : tout se gere ensuite dans le panneau."""
    entree.add_to_hass(hass)

    flux = await hass.config_entries.flow.async_init(
        "rhizome", context={"source": config_entries.SOURCE_USER}
    )

    assert flux["type"] is FlowResultType.ABORT
    assert flux["reason"] == "single_instance_allowed"


async def test_le_flux_d_options_fusionne_sans_effacer(
    hass: HomeAssistant, monter
) -> None:
    """Le formulaire ne connait que les reglages d'origine. Le panneau en gere
    d'autres, qu'un passage par « Configurer » effacerait s'il ecrivait
    seulement ses propres champs."""
    entree = MockConfigEntry(
        domain="rhizome",
        title="Rhizome",
        data={},
        options={**SAISIE, "notify_resume": True, "masquer_terminees": True},
    )
    await monter(entree)

    flux = await hass.config_entries.options.async_init(entree.entry_id)
    assert flux["type"] is FlowResultType.FORM

    resultat = await hass.config_entries.options.async_configure(
        flux["flow_id"], {**SAISIE, "rappel_jours": 10}
    )
    await hass.async_block_till_done()

    assert resultat["data"]["rappel_jours"] == 10
    assert resultat["data"]["notify_resume"] is True
    assert resultat["data"]["masquer_terminees"] is True
