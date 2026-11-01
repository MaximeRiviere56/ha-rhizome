"""Alerte gel : la lecture de la météo, et ce qui part le soir.

Le module pur `gel.py` décide qui est menacé ; ces tests vérifient ce que la
couche Home Assistant met autour — lire une prévision sans se laisser abattre
par une entité absente, et n'envoyer qu'une alerte par nuit.
"""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
import pytest


@pytest.fixture
def recus(hass):
    """Intercepte les appels a notify.test, qui remplace un telephone."""
    messages: list[dict] = []

    async def _notifier(call):
        messages.append(dict(call.data))

    hass.services.async_register("notify", "test", _notifier)
    return messages


@pytest.fixture
def meteo(hass):
    """Déclare une entité météo et le service qui sert ses prévisions."""

    def _meteo(previsions, *, genre="hourly", entite="weather.banc"):
        hass.states.async_set(entite, "cloudy", {"friendly_name": "Banc"})

        async def _previsions(call):
            if call.data.get("type") != genre:
                return {entite: {"forecast": []}}
            return {entite: {"forecast": previsions}}

        hass.services.async_register(
            "weather",
            "get_forecasts",
            _previsions,
            supports_response="only",
        )
        return entite

    return _meteo


async def _notifieur(hass, coordinateur):
    """Le notifieur, construit comme `__init__.py` le construit.

    On ne passe pas par le minuteur : c'est `async_track_time_change` qui le
    declenche a 18 h, et le tester reviendrait a tester Home Assistant.
    """
    from custom_components.rhizome.notifier import RhizomeNotifier

    return RhizomeNotifier(hass, coordinateur)


async def _en_terre(coordinateur, plante):
    """Met la plante en terre aujourd'hui : sans quoi rien ne la menace."""
    coordinateur.store.noter(
        plante["uid"], "plante", coordinateur.aujourdhui()
    )
    await coordinateur.async_refresh()


def dans(heures: int) -> str:
    return (dt_util.now() + timedelta(hours=heures)).isoformat()


OPTIONS = {
    "notify_targets": ["notify.test"],
    "meteo_entite": "weather.banc",
}


async def test_le_minimum_sort_des_previsions_horaires(
    hass: HomeAssistant, entree, monter, meteo
) -> None:
    meteo([
        {"datetime": dans(2), "temperature": 9},
        {"datetime": dans(8), "temperature": 2},
        {"datetime": dans(14), "temperature": 11},
    ])
    coordinateur = await monter(entree, OPTIONS)

    assert await coordinateur.async_minimum_cette_nuit() == 2


async def test_repli_sur_les_previsions_quotidiennes(
    hass: HomeAssistant, entree, monter, meteo
) -> None:
    """Toutes les entités météo ne servent pas l'horaire."""
    meteo(
        [{"datetime": dans(6), "temperature": 12, "templow": -1}],
        genre="daily",
    )
    coordinateur = await monter(entree, OPTIONS)

    assert await coordinateur.async_minimum_cette_nuit() == -1


async def test_sans_entite_designee_on_ne_lit_rien(
    hass: HomeAssistant, entree, monter
) -> None:
    """Aucune intégration ne doit lire une entité qu'on ne lui a pas donnée."""
    coordinateur = await monter(entree, {"notify_targets": ["notify.test"]})

    assert await coordinateur.async_minimum_cette_nuit() is None


async def test_une_meteo_en_panne_ne_fait_pas_tomber_le_reste(
    hass: HomeAssistant, entree, monter
) -> None:
    """Le service n'existe pas : on se tait, on ne lève pas."""
    hass.states.async_set("weather.banc", "cloudy", {})
    coordinateur = await monter(entree, OPTIONS)

    assert await coordinateur.async_minimum_cette_nuit() is None


async def test_une_prevision_illisible_ne_fait_pas_tomber_le_reste(
    hass: HomeAssistant, entree, monter, meteo
) -> None:
    """Le défaut récurrent du projet : une valeur non contrainte dans un calcul."""
    meteo([
        {"datetime": "pas une date", "temperature": -5},
        {"datetime": dans(6), "temperature": "froid"},
        {"datetime": dans(7), "temperature": 1},
    ])
    coordinateur = await monter(entree, OPTIONS)

    assert await coordinateur.async_minimum_cette_nuit() == 1


async def test_l_alerte_part_et_nomme_la_plante(
    hass: HomeAssistant, entree, monter, ajouter, meteo, recus
) -> None:
    meteo([{"datetime": dans(8), "temperature": -2}])
    coordinateur = await monter(entree, OPTIONS)
    plante = await ajouter(coordinateur, "tomate", zone="pleine-terre")
    await _en_terre(coordinateur, plante)

    notifieur = await _notifieur(hass, coordinateur)
    await notifieur._async_verifier_gel()
    await hass.async_block_till_done()

    assert recus, "aucune alerte envoyée"
    assert "-2" in recus[0]["title"]
    assert "Tomate" in recus[0]["message"]


async def test_une_seule_alerte_par_nuit(
    hass: HomeAssistant, entree, monter, ajouter, meteo, recus
) -> None:
    """Déplacer l'heure du réglage ou redémarrer à 18 h repasserait ici."""
    meteo([{"datetime": dans(8), "temperature": -2}])
    coordinateur = await monter(entree, OPTIONS)
    plante = await ajouter(coordinateur, "tomate", zone="pleine-terre")
    await _en_terre(coordinateur, plante)

    notifieur = await _notifieur(hass, coordinateur)
    await notifieur._async_verifier_gel()
    await notifieur._async_verifier_gel()
    await hass.async_block_till_done()

    assert len(recus) == 1


async def test_une_nuit_douce_ne_dit_rien(
    hass: HomeAssistant, entree, monter, ajouter, meteo, recus
) -> None:
    meteo([{"datetime": dans(8), "temperature": 14}])
    coordinateur = await monter(entree, OPTIONS)
    plante = await ajouter(coordinateur, "tomate", zone="pleine-terre")
    await _en_terre(coordinateur, plante)

    notifieur = await _notifieur(hass, coordinateur)
    await notifieur._async_verifier_gel()
    await hass.async_block_till_done()

    assert recus == []


async def test_le_reglage_coupe_l_alerte(
    hass: HomeAssistant, entree, monter, ajouter, meteo, recus
) -> None:
    meteo([{"datetime": dans(8), "temperature": -5}])
    coordinateur = await monter(entree, {**OPTIONS, "notify_gel": False})
    plante = await ajouter(coordinateur, "tomate", zone="pleine-terre")
    await _en_terre(coordinateur, plante)

    notifieur = await _notifieur(hass, coordinateur)
    await notifieur._async_verifier_gel()
    await hass.async_block_till_done()

    assert recus == []
