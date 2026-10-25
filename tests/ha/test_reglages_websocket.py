"""Garde-fous sur la commande qui ecrit dans l'entree de configuration.

Deux defauts tenaient ensemble : la commande n'exigeait pas d'administrateur,
et n'imposait aucun type. Un jeton en lecture seule suffisait donc a poser un
`rappel_jours` non numerique, ce qui paralysait le coordinateur a chaque cycle
— definitivement, puisque l'option est persistee.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant


async def _envoyer(client, options, identifiant=1):
    await client.send_json(
        {
            "id": identifiant,
            "type": "rhizome/reglages/definir",
            "options": options,
        }
    )
    return await client.receive_json()


async def test_un_non_admin_ne_peut_pas_ecrire_les_reglages(
    hass: HomeAssistant, entree, monter, hass_ws_client, hass_read_only_access_token
) -> None:
    await monter(entree)
    client = await hass_ws_client(hass, hass_read_only_access_token)
    reponse = await _envoyer(client, {"rappel_jours": 7})

    assert reponse["success"] is False
    assert reponse["error"]["code"] == "unauthorized"
    assert "rappel_jours" not in entree.options


async def test_un_admin_peut_ecrire_un_reglage_valide(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    await monter(entree)
    client = await hass_ws_client(hass)
    reponse = await _envoyer(client, {"rappel_jours": 7, "gelees_derniere": "03-20"})

    assert reponse["success"] is True
    assert entree.options["rappel_jours"] == 7
    assert entree.options["gelees_derniere"] == "03-20"


async def test_un_reglage_non_numerique_est_refuse(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    await monter(entree)
    client = await hass_ws_client(hass)
    reponse = await _envoyer(client, {"rappel_jours": "abc"})

    assert reponse["success"] is False
    assert "rappel_jours" not in entree.options


async def test_une_date_de_gelee_malformee_est_refusee(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    await monter(entree)
    client = await hass_ws_client(hass)
    reponse = await _envoyer(client, {"gelees_derniere": "32-99"})

    assert reponse["success"] is False
    assert "gelees_derniere" not in entree.options


async def test_un_destinataire_inconnu_est_refuse(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    """Un destinataire devient un nom de service appele chaque matin."""
    await monter(entree)
    client = await hass_ws_client(hass)
    reponse = await _envoyer(client, {"notify_targets": ["notify.inexistant"]})

    assert reponse["success"] is False
    assert "notify_targets" not in entree.options


async def test_persistent_notification_reste_acceptable(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    await monter(entree)
    client = await hass_ws_client(hass)
    reponse = await _envoyer(client, {"notify_targets": ["persistent_notification"]})

    assert reponse["success"] is True
    assert entree.options["notify_targets"] == ["persistent_notification"]


async def test_une_etape_de_rappel_inconnue_est_refusee(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    await monter(entree)
    client = await hass_ws_client(hass)
    reponse = await _envoyer(client, {"notify_etapes": ["recolte", "n_importe_quoi"]})

    assert reponse["success"] is False


async def test_une_cle_inconnue_est_ignoree_sans_echouer(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    """Un panneau plus recent que l'integration ne doit pas tout bloquer."""
    await monter(entree)
    client = await hass_ws_client(hass)
    reponse = await _envoyer(client, {"rappel_jours": 5, "reglage_du_futur": True})

    assert reponse["success"] is True
    assert entree.options["rappel_jours"] == 5
    assert "reglage_du_futur" not in entree.options
