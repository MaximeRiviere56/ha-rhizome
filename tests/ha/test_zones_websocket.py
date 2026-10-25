"""L'identifiant de zone finit dans un attribut HTML du panneau.

Le panneau le derive d'un `slugifier()`, mais rien ne contraignait le serveur :
une commande WebSocket forgee pouvait y poser du balisage, stocke tel quel puis
reinjecte dans `<option value="...">`.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant


async def _definir(client, zones, identifiant=1):
    await client.send_json(
        {"id": identifiant, "type": "rhizome/zones", "zones": zones}
    )
    return await client.receive_json()


async def test_un_identifiant_de_zone_avec_du_balisage_est_refuse(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    coordinateur = await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(
        client,
        [
            {
                "id": '"><img src=x onerror=alert(1)>',
                "nom": "Piégée",
                "decalage_jours": 0,
            }
        ],
    )

    assert reponse["success"] is False
    assert all(z["id"] != '"><img src=x onerror=alert(1)>' for z in coordinateur.store.zones)


async def test_un_identifiant_slugifie_passe(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    coordinateur = await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(
        client,
        [{"id": "carre-nord-2", "nom": "Carré nord", "decalage_jours": -7}],
    )

    assert reponse["success"] is True
    assert [z["id"] for z in coordinateur.store.zones] == ["carre-nord-2"]


async def test_le_nom_de_zone_reste_libre(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    """Seul l'identifiant est contraint : le nom s'affiche echappe."""
    coordinateur = await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(
        client, [{"id": "serre", "nom": "Serre « sud » & co", "decalage_jours": -21}]
    )

    assert reponse["success"] is True
    assert coordinateur.store.zones[0]["nom"] == "Serre « sud » & co"
