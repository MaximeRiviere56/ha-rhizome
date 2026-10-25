"""Les entites apparaissent et disparaissent avec les plantes.

Particularite du projet : rien n'est connu au demarrage. Une plante ajoutee
depuis le panneau doit faire apparaitre ses entites sans rechargement, et une
plante retiree doit les faire disparaitre du registre — sinon le potager se
remplit de capteurs fantomes.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.todo import TodoItem, TodoItemStatus
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util


async def test_une_plante_ajoutee_cree_ses_entites(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    await ajouter(coordinateur, "tomate", surnom="Noire de Crimée")
    await hass.async_block_till_done()

    ids = hass.states.async_entity_ids()
    assert any("crimee" in i and i.startswith("sensor.") for i in ids)
    assert any("crimee" in i and i.startswith("switch.") for i in ids)


async def test_une_plante_retiree_quitte_le_registre(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "tomate", surnom="Noire de Crimée")
    await hass.async_block_till_done()

    registre = er.async_get(hass)
    avant = [e for e in registre.entities.values() if e.platform == "rhizome"]

    await coordinateur.async_appliquer(
        lambda: coordinateur.store.retirer_plante(plante["uid"])
    )
    await hass.async_block_till_done()

    apres = [e for e in registre.entities.values() if e.platform == "rhizome"]
    assert len(apres) == len(avant) - 2  # le capteur et l'interrupteur


async def test_l_interrupteur_de_rappels_ecrit_dans_le_jardin(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "tomate", surnom="Marmande")
    await hass.async_block_till_done()

    interrupteur = next(
        i for i in hass.states.async_entity_ids("switch") if "marmande" in i
    )
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": interrupteur}, blocking=True
    )

    assert coordinateur.store.plante(plante["uid"])["notifs"] is False
    assert hass.states.get(interrupteur).state == "off"


async def test_le_capteur_de_recolte_cumule_la_saison(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "tomate")
    annee = coordinateur.aujourdhui().year
    coordinateur.store.noter(plante["uid"], "seme", date(annee, 3, 1))
    for jour, grammes in ((5, 1200), (12, 800)):
        coordinateur.store.noter(
            plante["uid"],
            "recolte",
            date(annee, 7, jour),
            quantite_g=grammes,
        )
    await coordinateur.async_refresh()
    await hass.async_block_till_done()

    etat = hass.states.get("sensor.rhizome_recolte_de_la_saison")
    assert float(etat.state) == 2.0
    # Les attributs volatils ne vont pas au recorder, mais restent lisibles.
    assert etat.attributes["nb_recoltes"] == 2


async def test_cocher_une_tache_inscrit_au_journal(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    """Cocher n'est pas un geste decoratif : c'est enregistrer l'evenement."""
    coordinateur = await monter(entree, {"rappel_jours": 400})
    plante = await ajouter(coordinateur, "radis")
    await hass.async_block_till_done()

    liste = hass.data["entity_components"]["todo"].get_entity("todo.rhizome")
    taches = liste.todo_items
    assert taches, "aucune tache proposee"

    await liste.async_update_todo_item(
        TodoItem(
            uid=taches[0].uid,
            summary=taches[0].summary,
            status=TodoItemStatus.COMPLETED,
        )
    )
    assert coordinateur.store.plante(plante["uid"])["phase"] != "prevu"


async def test_le_calendrier_melange_previsions_et_journal(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    # Le radis se seme en place et se recolte 25 jours plus tard : sa chaine
    # entiere se deduit donc de la date du journal.
    plante = await ajouter(coordinateur, "radis")
    # Seme il y a dix jours : la recolte deduite (vingt-cinq jours) tombe
    # encore dans l'avenir, donc dans les etapes calculees.
    aujourdhui = coordinateur.aujourdhui()
    annee = aujourdhui.year
    coordinateur.store.noter(plante["uid"], "seme", aujourdhui - timedelta(days=10))
    await coordinateur.async_refresh()
    await hass.async_block_till_done()

    agenda = hass.data["entity_components"]["calendar"].get_entity("calendar.rhizome")
    evenements = await agenda.async_get_events(
        hass,
        dt_util.as_utc(datetime(annee, 1, 1)),
        dt_util.as_utc(datetime(annee, 12, 31)),
    )

    resumes = [e.summary for e in evenements]
    assert any("Semé" in r for r in resumes), resumes
    assert any("Récolter" in r for r in resumes), resumes


async def test_le_capteur_d_arrosage_compte_ce_qui_attend(
    hass: HomeAssistant, entree, monter, ajouter
) -> None:
    coordinateur = await monter(entree)
    plante = await ajouter(coordinateur, "tomate", zone="serre")
    coordinateur.store.noter(
        plante["uid"], "seme", coordinateur.aujourdhui() - timedelta(days=30)
    )
    await coordinateur.async_refresh()
    await hass.async_block_till_done()

    etat = hass.states.get("sensor.rhizome_a_arroser")
    assert int(etat.state) == 1
    assert etat.attributes["plantes"][0]["uid"] == plante["uid"]
