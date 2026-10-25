"""La plage demandee au calendrier vient du client, sans borne.

`async_get_events` recalcule les previsions annee par annee, pour chaque
plante, dans la boucle d'evenements. Mesure avant correction : 0,9 s de
boucle bloquee pour cinq siecles et dix plantes, et le cout est lineaire.
N'importe quelle session authentifiee pouvait donc figer l'instance.
"""

from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.core import HomeAssistant

from custom_components.rhizome.calendar import ANNEES_MAX


def _calendrier(hass: HomeAssistant):
    return next(iter(hass.data["entity_components"]["calendar"].entities))


async def _evenements(hass, cal, premiere_annee, derniere_annee):
    return await cal.async_get_events(
        hass,
        datetime(premiere_annee, 1, 1, tzinfo=UTC),
        datetime(derniere_annee, 12, 31, tzinfo=UTC),
    )


async def test_une_plage_demesuree_est_ramenee_a_la_borne(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    await ajouter(coordinateur, culture_id="tomate")
    cal = _calendrier(hass)

    bornee = await _evenements(hass, cal, 2026, 2026 + ANNEES_MAX)
    demesuree = await _evenements(hass, cal, 2026, 2526)

    # Au-dela de la borne, la requete ne coute plus rien de plus.
    assert len(demesuree) == len(bornee)


async def test_une_plage_ordinaire_rend_toujours_ses_evenements(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    """La borne ne doit pas amputer un usage reel."""
    coordinateur = await monter(entree)
    await ajouter(coordinateur, culture_id="tomate")
    cal = _calendrier(hass)

    une_annee = await _evenements(hass, cal, 2026, 2026)
    trois_annees = await _evenements(hass, cal, 2026, 2028)

    assert une_annee, "une année de prévisions doit produire des événements"
    assert len(trois_annees) > len(une_annee)
