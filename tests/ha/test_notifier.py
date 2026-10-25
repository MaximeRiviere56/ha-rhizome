"""Rappels : ce qui part, ce qui ne part pas, et ce qu'on en garde."""

from __future__ import annotations

from datetime import date, timedelta

from homeassistant.core import HomeAssistant
import pytest

from custom_components.rhizome.notifier import RETENTION_DEFAUT


@pytest.fixture
def recus(hass):
    """Intercepte les appels a notify.test, qui remplace un telephone."""
    messages: list[dict] = []

    async def _notifier(call):
        messages.append(dict(call.data))

    hass.services.async_register("notify", "test", _notifier)
    return messages


async def test_le_bouton_ressemer_ne_leve_plus_d_unbound_local(
    hass: HomeAssistant, entree, monter, caplog
) -> None:
    """La branche « ressemer » du gestionnaire d'action utilisait `type_evt`,
    qui n'y est jamais defini : l'erreur attendue devenait une
    UnboundLocalError levee depuis le gestionnaire d'exception lui-meme."""
    await monter(entree)

    hass.bus.async_fire(
        "mobile_app_notification_action",
        {"action": "RHIZOME|fait|plante-inexistante|ressemer"},
    )
    await hass.async_block_till_done()

    assert not [r for r in caplog.records if r.exc_info]


async def test_le_bouton_c_est_fait_inscrit_au_journal(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "radis")

    hass.bus.async_fire(
        "mobile_app_notification_action",
        {"action": f"RHIZOME|fait|{plante['uid']}|semis_direct"},
    )
    await hass.async_block_till_done()

    assert coordinateur.store.plante(plante["uid"])["phase"] == "seme"


async def test_un_destinataire_absent_ne_consomme_pas_le_rappel(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    """Le rappel etait marque « envoye » avant l'envoi : un service
    injoignable le perdait definitivement."""
    coordinateur = await monter(
        entree, {"notify_targets": ["notify.telephone_disparu"]}
    )
    plante = await ajouter(coordinateur, "radis")
    coordinateur.store.noter(plante["uid"], "seme", date(2026, 1, 1))
    await coordinateur.async_refresh()

    notifier_ = _notifier_de(hass, coordinateur)
    await notifier_._async_verifier()

    assert coordinateur.store.etat_notifs["envoyees"] == {}


async def test_les_rappels_perimes_sont_oublies(
    hass: HomeAssistant, entree, monter, recus
) -> None:
    """La cle d'un rappel d'arrosage porte la date du jour : une entree
    s'ajoutait par plante et par jour, et rien ne les retirait jamais."""
    coordinateur = await monter(entree, {"notify_targets": ["notify.test"]})
    store = coordinateur.store

    vieux = (date.today() - timedelta(days=RETENTION_DEFAUT + 10)).isoformat()
    hier = (date.today() - timedelta(days=30)).isoformat()
    store.marquer_notif_envoyee("abc:recolte:2020-06-01", vieux)
    store.marquer_notif_envoyee("abc:arrosage:2026-09-01", hier)
    store.marquer_notif_envoyee("abc:recolte:2026-06-01", hier)
    store.reporter("abc:recolte", vieux)

    notifier_ = _notifier_de(hass, coordinateur)
    await notifier_._async_verifier()

    restantes = store.etat_notifs["envoyees"]
    assert "abc:recolte:2020-06-01" not in restantes  # au-dela de la retention
    assert "abc:arrosage:2026-09-01" not in restantes  # arrosage : 7 jours
    assert "abc:recolte:2026-06-01" in restantes  # etape de la saison en cours
    assert store.etat_notifs["reports"] == {}


def _notifier_de(hass, coordinateur):
    from custom_components.rhizome.notifier import RhizomeNotifier

    return RhizomeNotifier(hass, coordinateur)
