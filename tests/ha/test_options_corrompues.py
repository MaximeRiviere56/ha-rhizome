"""Une option illisible ne doit jamais paralyser le calcul.

Les options sont persistees : une ValueError remontee depuis `_calculer`
laissait le coordinateur en echec a chaque cycle, redemarrage compris. Le
schema WebSocket empeche desormais d'en poser une, mais un fichier `.storage`
edite a la main, ou herite d'une version anterieure, reste possible.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant


async def test_rappel_jours_illisible_ne_casse_pas_le_calcul(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    await ajouter(coordinateur)

    hass.config_entries.async_update_entry(
        entree, options={**entree.options, "rappel_jours": "abc"}
    )
    await hass.async_block_till_done()
    await coordinateur.async_refresh()

    assert coordinateur.last_update_success is True
    assert coordinateur.rappel_jours == 3


async def test_gelees_illisibles_retombent_sur_le_defaut(
    hass: HomeAssistant, entree, monter
) -> None:
    coordinateur = await monter(entree, {"gelees_derniere": "pas une date"})
    assert coordinateur.gelees.derniere == "04-15"
    assert coordinateur.last_update_success is True


async def test_rappel_par_plante_illisible_retombe_sur_le_global(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree, {"rappel_jours": 5})
    plante = await ajouter(coordinateur)
    plante["rappel_jours"] = "beaucoup"

    assert coordinateur.rappel_pour(plante) == 5


async def test_etapes_notifiables_corrompues_sont_filtrees(
    hass: HomeAssistant, entree, monter
) -> None:
    coordinateur = await monter(
        entree, {"notify_etapes": ["recolte", "etape_inventee"]}
    )
    assert coordinateur.etapes_notifiables == ["recolte"]

    hass.config_entries.async_update_entry(
        entree, options={**entree.options, "notify_etapes": "pas une liste"}
    )
    assert "recolte" in coordinateur.etapes_notifiables
