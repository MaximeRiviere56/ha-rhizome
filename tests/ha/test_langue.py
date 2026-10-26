"""Une installation anglophone, de bout en bout.

`tests/test_i18n.py` verifie la table des textes ; ici on verifie que la langue
atteint vraiment tout ce qu'elle doit atteindre. C'est la seule facon de voir
ce qui aurait ete oublie : un libelle laisse en dur dans un capteur ne se
remarque pas en relisant la table.

Les deux defauts que ces tests rejouent :

- une installation en anglais recevait les noms de cultures du catalogue
  francais, parce que la localisation s'appliquait au panneau mais pas aux
  entites ;
- le capteur de phase traduisait son etat sans traduire ses `options`, ce qui
  rend une entite `enum` invalide a chaque changement d'etat.
"""

from __future__ import annotations

import pytest

from custom_components.rhizome.const import CONF_LANGUE


@pytest.fixture
def anglais(monter, entree):
    """Une installation dont la langue est forcee a l'anglais."""

    async def _monter(**options):
        return await monter(entree, {CONF_LANGUE: "en", **options})

    return _monter


@pytest.fixture
def appeler(hass, hass_ws_client):
    """Une commande WebSocket, numerotee comme dans `test_websocket.py`."""
    compteur = {"n": 0}

    async def _appeler(**message):
        connexion = compteur.get("connexion")
        if connexion is None:
            connexion = await hass_ws_client(hass)
            compteur["connexion"] = connexion
        compteur["n"] += 1
        await connexion.send_json({"id": compteur["n"], **message})
        return await connexion.receive_json()

    return _appeler


async def test_auto_suit_la_langue_de_l_instance(hass, monter, entree):
    """« auto » est le defaut : une instance anglophone n'a aucune raison
    d'afficher du francais, et une instance francophone ne change pas."""
    hass.config.language = "en"
    coordinateur = await monter(entree)
    assert coordinateur.langue == "en"

    hass.config.language = "fr"
    await hass.config_entries.async_reload(entree.entry_id)
    await hass.async_block_till_done()
    assert entree.runtime_data.langue == "fr"


async def test_un_choix_explicite_ignore_l_instance(hass, anglais):
    hass.config.language = "fr"
    coordinateur = await anglais()
    assert coordinateur.langue == "en"


async def test_une_option_illisible_ne_met_pas_en_panne(monter, entree):
    """Meme garde que pour les autres reglages : une valeur persistee qui ne
    veut rien dire doit laisser l'integration utilisable."""
    coordinateur = await monter(entree, {CONF_LANGUE: "klingon"})
    assert coordinateur.langue == "fr"
    assert coordinateur.data is not None


async def test_les_noms_des_entites_globales_sont_traduits(hass, anglais):
    await anglais()
    noms = {
        etat.attributes.get("friendly_name")
        for etat in hass.states.async_all("sensor")
    }
    assert "Rhizome Tasks due" in noms
    assert "Rhizome Harvest this season" in noms


async def test_le_nom_d_une_plante_vient_du_catalogue_traduit(
    hass, anglais, ajouter
):
    """Le defaut qui a motive ce test : le panneau parlait anglais et les
    entites annonçaient « Tomate »."""
    coordinateur = await anglais()
    await ajouter(coordinateur, "tomate")
    await hass.async_block_till_done()

    capteur = next(
        etat
        for etat in hass.states.async_all("sensor")
        if etat.attributes.get("uid")
    )
    assert capteur.attributes["culture"] == "Tomato"
    assert capteur.attributes["famille"] == "Solanaceae"
    assert capteur.attributes["friendly_name"].endswith("Tomato")


async def test_la_phase_et_ses_options_sont_traduites_ensemble(
    hass, anglais, ajouter
):
    """Traduire l'etat sans traduire `options` rend l'entite `enum` invalide."""
    coordinateur = await anglais()
    await ajouter(coordinateur, "tomate")
    await hass.async_block_till_done()

    capteur = next(
        etat
        for etat in hass.states.async_all("sensor")
        if etat.attributes.get("uid")
    )
    assert capteur.state == "Planned"
    assert capteur.state in capteur.attributes["options"]


async def test_le_surnom_n_est_jamais_traduit(hass, anglais, ajouter):
    """C'est une donnee de l'utilisateur, pas un libelle."""
    coordinateur = await anglais()
    await ajouter(coordinateur, "tomate", surnom="Coeur de boeuf")
    await hass.async_block_till_done()

    capteur = next(
        etat
        for etat in hass.states.async_all("sensor")
        if etat.attributes.get("uid")
    )
    assert "Coeur de boeuf" in capteur.attributes["friendly_name"]


async def test_les_zones_livrees_naissent_dans_la_bonne_langue(anglais):
    coordinateur = await anglais()
    noms = {zone["nom"] for zone in coordinateur.store.zones}
    assert "Open ground" in noms
    assert "Greenhouse" in noms
    # Les identifiants, eux, ne bougent pas : ils servent de cle partout.
    assert {"pleine-terre", "serre"} <= {z["id"] for z in coordinateur.store.zones}


async def test_le_catalogue_du_panneau_est_traduit(anglais, appeler):
    await anglais()
    reponse = await appeler(type="rhizome/catalogue", requete="tomato")

    assert reponse["success"], reponse
    assert "Tomato" in [c["nom"] for c in reponse["result"]["cultures"]]


async def test_la_recherche_trouve_dans_les_deux_langues(anglais, appeler):
    """« courgette » doit trouver la courgette meme sur une interface anglaise :
    l'utilisateur peut connaitre le nom francais d'une plante francaise."""
    await anglais()
    for terme, attendu in (("courgette", "Courgette"), ("leek", "Leek")):
        reponse = await appeler(type="rhizome/catalogue", requete=terme)
        assert attendu in [c["nom"] for c in reponse["result"]["cultures"]], terme


async def test_la_fiche_ne_transporte_pas_les_deux_langues(anglais, appeler):
    """Servir `nom_en` a cote de `nom` doublerait le catalogue sur le fil pour
    une donnee que le panneau ne lit pas."""
    await anglais()
    reponse = await appeler(type="rhizome/culture", culture_id="tomate")

    culture = reponse["result"]["culture"]
    assert culture["nom"] == "Tomato"
    assert culture["sol"].startswith("rich in humus")
    assert culture["conseils"][0] == "Pinch out the side shoots once a week"
    assert not [cle for cle in culture if cle.endswith("_en")]
    assert "notes_en" not in culture["arrosage"]


async def test_le_panneau_recoit_la_langue_resolue(anglais, appeler):
    """Le panneau rend ses propres libelles : sans cette valeur il devinerait,
    et afficherait des libelles anglais sur des noms francais."""
    await anglais()
    reponse = await appeler(type="rhizome/reglages")

    assert reponse["result"]["langue"] == "en"
    assert reponse["result"]["options"][CONF_LANGUE] == "en"


async def test_un_refus_du_journal_est_traduit(anglais, ajouter, appeler):
    coordinateur = await anglais()
    plante = await ajouter(coordinateur, "tomate")
    # Repiquer une plante jamais semee : transition refusee.
    reponse = await appeler(
        type="rhizome/noter", uid=plante["uid"], evenement="repique"
    )

    assert not reponse["success"]
    message = reponse["error"]["message"]
    assert "Cannot record" in message
    assert "Transplanted" in message


async def test_la_liste_de_taches_est_traduite(hass, anglais, ajouter):
    coordinateur = await anglais()
    await ajouter(coordinateur, "radis")
    await hass.async_block_till_done()

    entite = hass.data["entity_components"]["todo"].get_entity("todo.rhizome")
    resumes = [element.summary for element in entite.todo_items]
    # Le radis se seme en place ; selon la date du jour la tache peut ne pas
    # etre ouverte, d'ou la tolerance a une liste vide.
    for resume in resumes:
        assert "Semer" not in resume
        assert "Récolter" not in resume


async def test_un_reglage_de_langue_invalide_est_refuse(anglais, appeler):
    """La valeur atterrit dans `entry.options` et decide des noms d'entites :
    elle est bornee au schema, pas acceptee puis ignoree."""
    await anglais()
    reponse = await appeler(
        type="rhizome/reglages/definir", options={CONF_LANGUE: "klingon"}
    )
    assert not reponse["success"]


async def test_l_avis_de_rotation_est_traduit(anglais, ajouter, appeler):
    """L'avertissement vient d'un module pur, donc en francais : il est
    reconstruit la ou le catalogue et la langue sont connus, noms des cultures
    precedentes compris."""
    coordinateur = await anglais()
    plante = await ajouter(coordinateur, "aubergine", zone="pleine-terre")
    await coordinateur.async_appliquer(
        lambda: coordinateur.store.noter(
            plante["uid"], "seme", coordinateur.data["calcule_le"]
        )
    )

    reponse = await appeler(
        type="rhizome/rotation", culture_id="tomate", zone="pleine-terre"
    )
    avis = reponse["result"]["avertissement"]
    assert avis is not None
    assert "Solanaceae already grown here" in avis["message"]
    assert "Aubergine" in avis["message"]
    assert "déjà cultivées" not in avis["message"]
