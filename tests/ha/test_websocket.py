"""L'API du panneau, bout a bout.

Le panneau ne passe pas par l'etat des entites : il parle a ces commandes. Les
trois defauts de la v0.6.0 vivaient tous ici, et aucun n'etait visible depuis
le banc d'essai, qui reimplemente la serialisation a la main.
"""

from __future__ import annotations

from datetime import date

import pytest


@pytest.fixture
async def client(hass, entree, monter, hass_ws_client):
    coordinateur = await monter(entree)
    connexion = await hass_ws_client(hass)
    compteur = {"n": 0}

    async def _appeler(**message):
        compteur["n"] += 1
        await connexion.send_json({"id": compteur["n"], **message})
        return await connexion.receive_json()

    _appeler.coordinateur = coordinateur
    return _appeler


# --- Lecture -----------------------------------------------------------------


async def test_catalogue(client) -> None:
    rep = await client(type="rhizome/catalogue", requete="tomate")
    assert rep["success"]
    assert rep["result"]["total"] > 100
    assert any(c["id"] == "tomate" for c in rep["result"]["cultures"])
    assert "semable_maintenant" in rep["result"]["cultures"][0]


async def test_catalogue_filtre_par_categorie(client) -> None:
    rep = await client(type="rhizome/catalogue", categorie="aromatique")
    assert rep["success"]
    assert {c["categorie"] for c in rep["result"]["cultures"]} == {"aromatique"}


async def test_fiche_de_culture(client) -> None:
    rep = await client(type="rhizome/culture", culture_id="tomate")
    assert rep["success"]
    assert rep["result"]["culture"]["nom"]
    assert "aime" in rep["result"]["compagnes"]
    assert rep["result"]["fenetres"]


async def test_fiche_inconnue(client) -> None:
    rep = await client(type="rhizome/culture", culture_id="dragonnier-de-mars")
    assert rep["success"] is False
    assert rep["error"]["code"] == "introuvable"


async def test_jardin_vide(client) -> None:
    rep = await client(type="rhizome/jardin")
    assert rep["success"]
    assert rep["result"]["plantes"] == []
    assert rep["result"]["gelees"]["derniere"] == "04-15"


async def test_calendrier(client) -> None:
    await client(type="rhizome/ajouter", culture_id="tomate")
    rep = await client(type="rhizome/calendrier", annee=2026)
    assert rep["success"]
    assert rep["result"]["annee"] == 2026
    assert len(rep["result"]["lignes"]) == 1
    assert rep["result"]["lignes"][0]["prevues"]


async def test_reglages(client) -> None:
    rep = await client(type="rhizome/reglages")
    assert rep["success"]
    assert rep["result"]["options"]["gelees_derniere"] == "04-15"
    assert any(
        c["value"] == "persistent_notification"
        for c in rep["result"]["cibles_possibles"]
    )


# --- Ecriture ----------------------------------------------------------------


async def test_ajouter_puis_retirer(client) -> None:
    rep = await client(type="rhizome/ajouter", culture_id="tomate", zone="serre")
    assert rep["success"]
    uid = rep["result"]["uid"]

    jardin = await client(type="rhizome/jardin")
    assert [p["uid"] for p in jardin["result"]["plantes"]] == [uid]
    assert jardin["result"]["plantes"][0]["zone"]["id"] == "serre"

    rep = await client(type="rhizome/retirer", uid=uid)
    assert rep["success"]
    jardin = await client(type="rhizome/jardin")
    assert jardin["result"]["plantes"] == []


async def test_ajouter_une_culture_inconnue(client) -> None:
    rep = await client(type="rhizome/ajouter", culture_id="dragonnier-de-mars")
    assert rep["success"] is False
    assert rep["error"]["code"] == "refuse"


async def test_les_deux_reglages_d_eau_par_plante_passent(client) -> None:
    """Le schema de `modifier` ne les declarait pas : le panneau les envoyait,
    et les deux commandes etaient mortes avec une erreur WebSocket."""
    rep = await client(type="rhizome/ajouter", culture_id="tomate")
    uid = rep["result"]["uid"]

    rep = await client(
        type="rhizome/modifier",
        uid=uid,
        arrosage_actif=False,
        arrosage_frequence_jours=9,
    )
    assert rep["success"], rep

    plante = client.coordinateur.store.plante(uid)
    assert plante["arrosage_actif"] is False
    assert plante["arrosage_frequence_jours"] == 9


async def test_la_plante_porte_son_echeance_d_arrosage(client) -> None:
    """La cle `arrosage` etait ecrite deux fois dans le meme dictionnaire :
    les besoins de la culture ecrasaient l'etat calcule de la plante, et le
    panneau n'a jamais affiche d'echeance."""
    rep = await client(type="rhizome/ajouter", culture_id="tomate", zone="serre")
    uid = rep["result"]["uid"]
    await client(type="rhizome/noter", uid=uid, evenement="seme")

    jardin = await client(type="rhizome/jardin")
    plante = jardin["result"]["plantes"][0]

    assert plante["uid"] == uid
    assert plante["arrosage"] is not None
    assert "jours_restants" in plante["arrosage"]
    assert "frequence_jours" in plante["arrosage"]


async def test_noter_puis_annuler(client) -> None:
    rep = await client(type="rhizome/ajouter", culture_id="radis")
    uid = rep["result"]["uid"]

    rep = await client(
        type="rhizome/noter", uid=uid, evenement="seme", date="2026-04-01"
    )
    assert rep["result"]["phase"] == "seme"

    rep = await client(type="rhizome/annuler", uid=uid)
    assert rep["success"]
    assert client.coordinateur.store.plante(uid)["phase"] == "prevu"


async def test_une_transition_impossible_est_refusee(client) -> None:
    rep = await client(type="rhizome/ajouter", culture_id="radis")
    uid = rep["result"]["uid"]
    await client(type="rhizome/noter", uid=uid, evenement="seme")

    rep = await client(type="rhizome/noter", uid=uid, evenement="seme")
    assert rep["success"] is False
    assert rep["error"]["code"] == "refuse"


async def test_une_plante_inconnue_est_refusee(client) -> None:
    rep = await client(type="rhizome/noter", uid="jamais-vue", evenement="seme")
    assert rep["success"] is False
    assert rep["error"]["code"] == "refuse"


async def test_arroser_plusieurs_plantes_d_un_coup(client) -> None:
    """« Tout arroser » est un geste reel : le faire repeter dix fois serait
    absurde."""
    uids = []
    for culture in ("tomate", "courgette"):
        rep = await client(type="rhizome/ajouter", culture_id=culture)
        uids.append(rep["result"]["uid"])
        await client(type="rhizome/noter", uid=uids[-1], evenement="seme")

    rep = await client(type="rhizome/arroser", uid=uids, date="2026-07-01")
    assert rep["success"]
    assert rep["result"]["arrosees"] == 2
    for uid in uids:
        assert client.coordinateur.store.plante(uid)["arrosages"]


async def test_ressemer_ouvre_un_lot(client) -> None:
    rep = await client(
        type="rhizome/ajouter", culture_id="radis", echelonnement_jours=15
    )
    parent = rep["result"]["uid"]
    await client(type="rhizome/noter", uid=parent, evenement="seme")

    rep = await client(type="rhizome/ressemer", uid=parent)
    assert rep["success"]
    assert rep["result"]["uid"] != parent
    # Le parent cesse de reclamer un ressemis : sinon les deux le feraient
    # indefiniment.
    assert client.coordinateur.store.plante(parent)["echelonnement_jours"] is None


async def test_rotation_avertit_sur_la_meme_famille(client) -> None:
    rep = await client(type="rhizome/ajouter", culture_id="tomate")
    await client(
        type="rhizome/noter", uid=rep["result"]["uid"], evenement="seme",
        date=date.today().isoformat(),
    )

    rep = await client(
        type="rhizome/rotation", culture_id="pomme-de-terre", zone="pleine-terre"
    )
    assert rep["success"]
    avertissement = rep["result"]["avertissement"]
    assert avertissement is not None
    assert avertissement["famille"] == "Solanacées"


# --- Catalogue personnel ------------------------------------------------------


async def test_corriger_une_fiche_livree_puis_la_retablir(client) -> None:
    """Corriger conserve l'id : la fiche personnelle remplace la livree au lieu
    de la doubler, et les plantes deja au jardin suivent la correction."""
    rep = await client(
        type="rhizome/culture_perso/definir",
        fiche={
            "id": "tomate",
            "nom": "Tomate",
            "categorie": "legume-fruit",
            "exposition": "plein-soleil",
            "arrosage": {"besoin": "eleve", "frequence_jours": 2},
            "gel": False,
            "jours_semis_a_recolte": 200,
        },
    )
    assert rep["success"], rep
    assert rep["result"]["id"] == "tomate"

    perso = await client(type="rhizome/cultures_perso")
    assert [c["id"] for c in perso["result"]["cultures"]] == ["tomate"]

    rep = await client(type="rhizome/culture_perso/retablir", culture_id="tomate")
    assert rep["success"]
    perso = await client(type="rhizome/cultures_perso")
    assert perso["result"]["cultures"] == []


async def test_retablir_une_fiche_inedite_est_refuse(client) -> None:
    rep = await client(
        type="rhizome/culture_perso/retablir", culture_id="perso-inventee"
    )
    assert rep["success"] is False


async def test_supprimer_une_fiche_utilisee_est_refuse(client) -> None:
    """Sans sa fiche, la plante deviendrait un orphelin silencieux."""
    await client(
        type="rhizome/culture_perso/definir",
        fiche={
            "nom": "Cardon sauvage",
            "categorie": "legume-feuille",
            "exposition": "plein-soleil",
            "arrosage": {"besoin": "moyen", "frequence_jours": 5},
            "gel": True,
            "periodes": {"semis_direct": {"debut": 4, "fin": 5}},
            "jours_semis_a_recolte": 150,
        },
    )
    await client(type="rhizome/ajouter", culture_id="perso-cardon-sauvage")

    rep = await client(
        type="rhizome/culture_perso/supprimer", culture_id="perso-cardon-sauvage"
    )
    assert rep["success"] is False
    assert "plante" in rep["error"]["message"]


# --- Zones --------------------------------------------------------------------


async def test_une_plante_dont_la_zone_disparait_retombe_en_pleine_terre(
    client,
) -> None:
    rep = await client(type="rhizome/ajouter", culture_id="tomate", zone="serre")
    uid = rep["result"]["uid"]

    rep = await client(
        type="rhizome/zones",
        zones=[{"id": "pleine-terre", "nom": "Pleine terre", "decalage_jours": 0}],
    )
    assert rep["success"]
    assert client.coordinateur.store.plante(uid)["zone"] == "pleine-terre"
