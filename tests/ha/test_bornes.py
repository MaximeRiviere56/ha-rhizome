"""Rien de ce qui entre par WebSocket ne doit pouvoir paralyser le calcul.

Ces valeurs finissent dans `.storage/rhizome.jardin`, puis dans un
`date + timedelta(...)`. Un entier demesure y levait une `OverflowError`
depuis `_calculer`, donc a chaque cycle du coordinateur. Et comme la valeur
etait persistee, l'integration ne se reparait ni au rechargement ni au
redemarrage : seule une edition manuelle du stockage la remettait d'aplomb.

C'est exactement la panne que la validation des reglages avait corrigee pour
`entry.options` ; le stockage du jardin, lui, n'avait aucune garde. Trois
chemins y menaient : le decalage d'une zone, la frequence d'arrosage d'une
plante, et une date du journal en l'an 9999.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
import pytest


async def _envoyer(client, identifiant, **message):
    await client.send_json({"id": identifiant, **message})
    return await client.receive_json()


# --- Ce qui entre est borne ---------------------------------------------------


@pytest.mark.parametrize(
    ("champ", "valeur"),
    [
        ("echelonnement_jours", 10**12),
        ("echelonnement_jours", -1),
        ("arrosage_frequence_jours", 10**12),
        ("arrosage_frequence_jours", 0),
        ("rappel_jours", 10**9),
    ],
)
async def test_un_entier_demesure_est_refuse(
    hass: HomeAssistant, entree, monter, ajouter, hass_ws_client, champ, valeur
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur)
    client = await hass_ws_client(hass)

    reponse = await _envoyer(
        client, 1, type="rhizome/modifier", uid=plante["uid"], **{champ: valeur}
    )

    assert reponse["success"] is False
    assert coordinateur.store.plante(plante["uid"])[champ] is None


async def test_un_decalage_de_zone_demesure_est_refuse(
    hass: HomeAssistant, entree, monter, ajouter, hass_ws_client
) -> None:
    coordinateur = await monter(entree)
    await ajouter(coordinateur, zone="potager")
    client = await hass_ws_client(hass)

    reponse = await _envoyer(
        client,
        1,
        type="rhizome/zones",
        zones=[{"id": "potager", "nom": "Potager", "decalage_jours": 10**9}],
    )

    assert reponse["success"] is False
    await coordinateur.async_refresh()
    assert coordinateur.last_update_success is True


async def test_une_date_hors_des_annees_credibles_est_refusee(
    hass: HomeAssistant, entree, monter, ajouter, hass_ws_client
) -> None:
    """« 9999-12-31 » passait le schema et se rangeait au journal."""
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur)
    client = await hass_ws_client(hass)

    reponse = await _envoyer(
        client,
        1,
        type="rhizome/noter",
        uid=plante["uid"],
        evenement="seme",
        date="9999-12-31",
    )

    assert reponse["success"] is False
    assert coordinateur.store.plante(plante["uid"])["evenements"] == []
    await coordinateur.async_refresh()
    assert coordinateur.last_update_success is True


async def test_un_mode_de_semis_invente_est_refuse(
    hass: HomeAssistant, entree, monter, ajouter, hass_ws_client
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur)
    client = await hass_ws_client(hass)

    reponse = await _envoyer(
        client,
        1,
        type="rhizome/noter",
        uid=plante["uid"],
        evenement="seme",
        mode="n_importe_quoi",
    )

    assert reponse["success"] is False


@pytest.mark.parametrize(
    ("commande", "champ"),
    [("rhizome/ajouter", "surnom"), ("rhizome/modifier", "surnom")],
)
async def test_un_texte_libre_demesure_est_refuse(
    hass: HomeAssistant, entree, monter, ajouter, hass_ws_client, commande, champ
) -> None:
    """Le surnom devient le nom de l'entite, donc son `entity_id`.

    Sans borne, un surnom de cent mille caracteres produisait un identifiant
    d'entite de cent mille caracteres dans le registre.
    """
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur)
    client = await hass_ws_client(hass)

    cible = (
        {"culture_id": "tomate"}
        if commande == "rhizome/ajouter"
        else {"uid": plante["uid"]}
    )
    reponse = await _envoyer(client, 1, type=commande, **cible, **{champ: "x" * 5000})

    assert reponse["success"] is False


async def test_une_date_et_un_surnom_normaux_passent_toujours(
    hass: HomeAssistant, entree, monter, ajouter, hass_ws_client
) -> None:
    """Les bornes ne doivent rien casser de l'usage ordinaire."""
    coordinateur = await monter(entree)
    client = await hass_ws_client(hass)

    ajout = await _envoyer(
        client,
        1,
        type="rhizome/ajouter",
        culture_id="tomate",
        surnom="Cœur de bœuf, serre",
        echelonnement_jours=14,
    )
    assert ajout["success"] is True
    uid = ajout["result"]["uid"]

    note = await _envoyer(
        client,
        2,
        type="rhizome/noter",
        uid=uid,
        evenement="seme",
        date="2026-03-07",
        mode="interieur",
        note="semis en godet",
    )
    assert note["success"] is True

    zones = await _envoyer(
        client,
        3,
        type="rhizome/zones",
        zones=[{"id": "serre", "nom": "Serre", "decalage_jours": -21,
                "abritee": True}],
    )
    assert zones["success"] is True

    modif = await _envoyer(
        client, 4, type="rhizome/modifier", uid=uid, arrosage_frequence_jours=3
    )
    assert modif["success"] is True

    await coordinateur.async_refresh()
    assert coordinateur.last_update_success is True
    assert coordinateur.store.plante(uid)["surnom"] == "Cœur de bœuf, serre"


# --- Ce qui est deja dans le stockage reste calculable ------------------------
#
# Les schemas ci-dessus ferment la porte. Ces trois tests visent les jardins
# deja empoisonnes par une version anterieure, ou un `.storage` edite a la
# main : la ou aucun schema ne passe plus.


async def test_un_decalage_deja_stocke_est_borne_a_la_lecture(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    await ajouter(coordinateur, zone="potager")
    coordinateur.store.zones.append(
        {"id": "potager", "nom": "Potager", "decalage_jours": 10**9}
    )

    assert coordinateur.store.decalage_zone("potager") == 120
    await coordinateur.async_refresh()
    assert coordinateur.last_update_success is True


async def test_une_frequence_deja_stockee_est_bornee_a_la_lecture(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, zone="serre")
    await coordinateur.async_appliquer(
        lambda: coordinateur.store.noter(plante["uid"], "seme", "2026-06-01")
    )
    await coordinateur.async_appliquer(
        lambda: coordinateur.store.arroser(plante["uid"], "2026-06-02")
    )
    coordinateur.store.plante(plante["uid"])["arrosage_frequence_jours"] = 10**12

    await coordinateur.async_refresh()
    assert coordinateur.last_update_success is True


async def test_une_plante_incalculable_n_emporte_pas_les_autres(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    """Le dernier filet : ce qu'aucune borne ne pouvait prevoir."""
    coordinateur = await monter(entree)
    saine = await ajouter(coordinateur, culture_id="tomate")
    abimee = await ajouter(coordinateur, culture_id="radis")
    # Une date que plus aucun schema n'accepte, telle qu'une version
    # anterieure aurait pu la ranger.
    coordinateur.store.plante(abimee["uid"])["evenements"] = [
        {"type": "seme", "date": "9999-12-31"}
    ]

    await coordinateur.async_refresh()

    assert coordinateur.last_update_success is True
    assert saine["uid"] in coordinateur.data["plantes"]
    assert abimee["uid"] not in coordinateur.data["plantes"]
