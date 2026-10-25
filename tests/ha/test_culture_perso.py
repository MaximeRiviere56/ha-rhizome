"""Fiches personnelles : ce que le panneau envoie, et ce qu'on refuse.

La commande acceptait `fiche: dict` sans schema. Une difficulte non numerique
ou un conseil qui n'est pas une chaine partait en erreur 500, et rien ne
bornait la taille de ce qui finissait dans le stockage du jardin.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant

# Exactement ce que construit `_lireFichePerso()` dans le panneau.
FICHE_DU_PANNEAU = {
    "id": None,
    "nom": "Panais de Guernesey",
    "emoji": "🥕",
    "categorie": "legume-racine",
    "famille": "Apiacées",
    "exposition": "plein-soleil",
    "arrosage": {"besoin": "moyen", "frequence_jours": 5, "notes": ""},
    "sol": "profond, meuble",
    "espacement_cm": 20,
    "difficulte": 2,
    "gel": False,
    "perenne": False,
    "periodes": {
        "semis_interieur": None,
        "semis_direct": {"debut": 3, "fin": 5},
        "plantation": None,
        "recolte": {"debut": 10, "fin": 12},
    },
    "jours_semis_a_recolte": 180,
    "jours_semis_a_repiquage": None,
    "jours_plantation_a_recolte": None,
    "duree_recolte_jours": 60,
    "conseils": ["Semer clair.", "Éclaircir à 15 cm."],
}


async def _definir(client, fiche, identifiant=1):
    await client.send_json(
        {
            "id": identifiant,
            "type": "rhizome/culture_perso/definir",
            "fiche": fiche,
        }
    )
    return await client.receive_json()


async def test_la_charge_reelle_du_panneau_passe(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    coordinateur = await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(client, dict(FICHE_DU_PANNEAU))

    assert reponse["success"] is True, reponse
    assert reponse["result"]["id"] == "perso-panais-de-guernesey"
    assert coordinateur.catalogue.culture("perso-panais-de-guernesey") is not None


async def test_une_difficulte_non_numerique_est_refusee_proprement(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    """Avant, int() levait une ValueError que le wrapper ne rattrapait pas."""
    await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(
        client, {**FICHE_DU_PANNEAU, "difficulte": "très dure"}
    )

    assert reponse["success"] is False
    assert reponse["error"]["code"] in ("refuse", "saisie_invalide")


async def test_un_conseil_qui_n_est_pas_du_texte_est_refuse(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    """Un nombre se laisse convertir en texte, une structure non : c'est elle
    qui faisait lever `.strip()` dans `_normaliser_fiche`."""
    await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(
        client, {**FICHE_DU_PANNEAU, "conseils": [{"texte": "semer clair"}]}
    )

    assert reponse["success"] is False


async def test_un_texte_demesure_est_refuse(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    """Rien ne bornait ce qui finissait dans le stockage du jardin."""
    await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(
        client, {**FICHE_DU_PANNEAU, "sol": "a" * 5000}
    )

    assert reponse["success"] is False


async def test_un_nom_vide_recoit_le_message_metier(
    hass: HomeAssistant, entree, monter, hass_ws_client
) -> None:
    await monter(entree)
    client = await hass_ws_client(hass)

    reponse = await _definir(client, {**FICHE_DU_PANNEAU, "nom": ""})

    assert reponse["success"] is False
    assert "nom" in reponse["error"]["message"].lower()
