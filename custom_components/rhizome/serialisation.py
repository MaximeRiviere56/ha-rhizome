"""Ce que le panneau recoit : la vue calculee, mise en dictionnaires.

Module volontairement pur : aucun import Home Assistant. C'est tout l'interet
de son existence.

Ces fonctions vivaient dans `websocket.py` et `coordinator.py`, qui importent
tous deux Home Assistant, absent du poste de developpement. Le banc d'essai —
`tools/banc_fixture.py`, qui monte le frontend hors d'une instance — ne
pouvait donc pas les appeler, et les **reimplementait a la main**.

Ce que cette copie a coute, et qui justifie le module : le banc a montre un
arrosage par plante qui fonctionnait alors qu'il etait casse en production. Sa
promesse — « le panneau face a ce qu'il recevra reellement » — ne tient que
tant que les deux ne divergent pas, et rien ne les empechait de diverger. Le
banc appelle desormais le meme code que l'instance.

La traduction se fait ici, et non cote panneau, parce que les attributs
d'entite passent par le meme chemin : la carte Lovelace les lit tels quels, et
les sondes les exposent a des automatisations.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from . import i18n


def etape_en_dict(etape, langue: str = "fr") -> dict | None:
    """Serialise une etape pour le panneau et les attributs d'entite."""
    if etape is None:
        return None
    donnees = asdict(etape)
    donnees["debut"] = etape.debut.isoformat()
    donnees["fin"] = etape.fin.isoformat()
    donnees["libelle"] = i18n.libelle_etape(langue, etape.type)
    donnees["reelle"] = etape.reelle
    return donnees


def libelle_phase(phase: str, langue: str = "fr") -> str:
    return i18n.libelle_phase(langue, phase)


def arrosage_en_dict(etat, langue: str = "fr") -> dict | None:
    """Serialise l'etat d'arrosage d'une plante."""
    if etat is None:
        return None
    return {
        "concernee": etat.concernee,
        "dernier": etat.dernier.isoformat() if etat.dernier else None,
        "prochain": etat.prochain.isoformat() if etat.prochain else None,
        "frequence_jours": etat.frequence_jours,
        "jours_restants": etat.jours_restants,
        "a_arroser": etat.a_arroser,
        "en_retard": etat.en_retard,
        "motif_exclusion": (
            i18n.t(langue, etat.motif_cle)
            if etat.motif_cle
            else etat.motif_exclusion
        ),
    }


def plante_en_dict(entree: dict, langue: str = "fr") -> dict[str, Any]:
    """Une plante du jardin, telle que le panneau la recoit.

    `entree` est une entree de la vue calculee du coordinateur : les cles
    `uid`, `plante`, `culture`, `zone`, `etapes`, `prochaine`, `resume`,
    `nom_affiche`, et `arrosage` quand le suivi d'eau est actif.
    """
    plante = entree["plante"]
    fiche = entree["culture"]
    infos = entree["resume"]
    return {
        "uid": entree["uid"],
        "culture_id": fiche["id"],
        "nom": entree["nom_affiche"],
        "emoji": fiche["emoji"],
        "categorie": fiche["categorie"],
        "surnom": plante.get("surnom"),
        "zone": entree["zone"],
        "notifs": plante.get("notifs", True),
        "rappel_jours": plante.get("rappel_jours"),
        "echelonnement_jours": plante.get("echelonnement_jours"),
        "arrosage_actif": plante.get("arrosage_actif", True),
        "arrosage_frequence_jours": plante.get("arrosage_frequence_jours"),
        "arrosage": arrosage_en_dict(entree.get("arrosage"), langue),
        # Tout l'historique conserve, et non les vingt derniers : le journal
        # les affiche desormais a leur date, et une liste tronquee y ferait un
        # trou sans le dire. Le stockage en borne deja le nombre
        # (`watering.HISTORIQUE_MAX`).
        "arrosages": list(reversed(plante.get("arrosages") or [])),
        "phase": infos["phase"],
        "phase_libelle": libelle_phase(infos["phase"], langue),
        "perenne": bool(fiche.get("perenne")),
        "prochaine": etape_en_dict(entree["prochaine"], langue),
        "etapes": [etape_en_dict(e, langue) for e in entree["etapes"]],
        "date_semis": infos["date_semis"].isoformat() if infos["date_semis"] else None,
        "date_mise_en_place": (
            infos["date_mise_en_place"].isoformat()
            if infos["date_mise_en_place"]
            else None
        ),
        "nb_recoltes": infos["nb_recoltes"],
        "total_recolte_g": infos["total_recolte_g"],
        "evenements": [
            {**evt, "libelle": i18n.libelle_evenement(langue, evt["type"])}
            for evt in plante.get("evenements") or []
        ],
        # Pas de `fiche["arrosage"]` ici : la cle porte l'etat calcule de la
        # plante (plus haut), pas les besoins theoriques de la culture. Les
        # deux ont coexiste dans ce meme dictionnaire, et la seconde ecrasait
        # silencieusement la premiere — le panneau n'a jamais vu d'echeance
        # d'arrosage sur une plante. Les besoins de la culture arrivent par
        # `rhizome/culture`, sous `culture.arrosage`.
        "exposition": fiche["exposition"],
    }
