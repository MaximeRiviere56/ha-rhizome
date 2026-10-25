"""Qui a le droit d'ecrire dans le jardin.

Une commande WebSocket personnalisee n'herite d'aucun controle d'acces :
toute session authentifiee l'atteint. Seule `rhizome/reglages/definir`
etait gardee, parce qu'elle ecrit dans l'entree de configuration ; le reste
ne l'etait pas. Un jeton en lecture seule pouvait donc ajouter, modifier,
noter, redefinir les zones et surtout **retirer** une plante — donc effacer
le journal, la seule donnee de ce projet que rien ne reconstitue.

Le critere retenu est celui de Home Assistant pour decider si quelqu'un peut
agir : le droit de controler les entites. Il laisse la maisonnee jardiner et
arrete les comptes en lecture seule.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
import pytest

# Les commandes qui ecrivent, et de quoi les appeler sur un jardin d'un pied.
ECRITURES = [
    ("rhizome/ajouter", {"culture_id": "radis"}),
    ("rhizome/modifier", {"uid": "@uid", "surnom": "pirate"}),
    ("rhizome/noter", {"uid": "@uid", "evenement": "seme"}),
    ("rhizome/annuler", {"uid": "@uid"}),
    ("rhizome/arroser", {"uid": "@uid"}),
    ("rhizome/ressemer", {"uid": "@uid"}),
    (
        "rhizome/zones",
        {"zones": [{"id": "z", "nom": "Z", "decalage_jours": 0}]},
    ),
    ("rhizome/culture_perso/definir", {"fiche": {"nom": "Faux légume"}}),
    ("rhizome/culture_perso/supprimer", {"culture_id": "perso-x"}),
    ("rhizome/culture_perso/retablir", {"culture_id": "tomate"}),
    ("rhizome/retirer", {"uid": "@uid"}),
]


def _resoudre(charge: dict, uid: str) -> dict:
    return {cle: (uid if val == "@uid" else val) for cle, val in charge.items()}


@pytest.mark.parametrize(("commande", "charge"), ECRITURES)
async def test_la_lecture_seule_ne_peut_rien_ecrire(
    hass: HomeAssistant,
    entree,
    monter,
    ajouter,
    hass_ws_client,
    hass_read_only_access_token,
    commande,
    charge,
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur)
    client = await hass_ws_client(hass, hass_read_only_access_token)

    await client.send_json(
        {"id": 1, "type": commande, **_resoudre(charge, plante["uid"])}
    )
    reponse = await client.receive_json()

    assert reponse["success"] is False
    assert reponse["error"]["code"] == "unauthorized"
    # Et rien n'a bouge : c'est le point du test, pas le code d'erreur.
    assert [p["uid"] for p in coordinateur.store.plantes] == [plante["uid"]]
    assert coordinateur.store.plante(plante["uid"])["surnom"] is None
    assert coordinateur.store.plante(plante["uid"])["evenements"] == []


async def test_la_lecture_seule_peut_toujours_consulter(
    hass: HomeAssistant,
    entree,
    monter,
    ajouter,
    hass_ws_client,
    hass_read_only_access_token,
) -> None:
    """La garde porte sur l'ecriture seule : un ecran mural reste utile."""
    coordinateur = await monter(entree)
    await ajouter(coordinateur)
    client = await hass_ws_client(hass, hass_read_only_access_token)

    for identifiant, commande in enumerate(
        ("rhizome/jardin", "rhizome/catalogue", "rhizome/calendrier",
         "rhizome/reglages", "rhizome/cultures_perso"),
        start=1,
    ):
        await client.send_json({"id": identifiant, "type": commande})
        reponse = await client.receive_json()
        assert reponse["success"] is True, commande


async def test_un_compte_ordinaire_peut_jardiner(
    hass: HomeAssistant, entree, monter, hass_ws_client, hass_access_token
) -> None:
    """Le panneau est fait pour la maisonnee, pas pour le seul administrateur.

    `require_admin` aurait ete plus simple et aurait casse cet usage : ce
    test est la pour que personne ne fasse ce raccourci plus tard.
    """
    jeton = hass.auth.async_validate_access_token(hass_access_token)
    utilisateur = jeton.user
    # Un compte ordinaire : ni administrateur, ni lecture seule.
    groupe = await hass.auth.async_get_group("system-users")
    await hass.auth.async_update_user(utilisateur, group_ids=[groupe.id])
    assert not utilisateur.is_admin

    coordinateur = await monter(entree)
    client = await hass_ws_client(hass, hass_access_token)

    await client.send_json(
        {"id": 1, "type": "rhizome/ajouter", "culture_id": "tomate"}
    )
    reponse = await client.receive_json()

    assert reponse["success"] is True
    assert len(coordinateur.store.plantes) == 1
