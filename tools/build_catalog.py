#!/usr/bin/env python3
"""Compile la table des cultures en data/catalog.json, apres validation.

Usage : python3 tools/build_catalog.py [--check]

--check valide sans reecrire le JSON : c'est la forme utilisee par les tests.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from catalogue_source import CULTURES
from catalogue_traductions import CONSEILS, EAU_NOTES, FAMILLES, NOMS, SOLS

RACINE = pathlib.Path(__file__).resolve().parent.parent
SORTIE = RACINE / "custom_components" / "rhizome" / "data" / "catalog.json"

CATEGORIES = {
    "legume-fruit",
    "legume-racine",
    "legume-gousse",
    "legume-bulbe",
    "legume-feuille",
    "aromatique",
    "petit-fruit",
    "fruitier",
    "fleur-compagne",
    "cereale",
    "medicinale",
    "plante-interieur",
}

# Les plantes d'interieur sont le seul cas ou le modele du potager ne
# s'applique pas : pas de semis cale sur les gelees, pas de recolte. Leur
# fiche ne porte que la lumiere, l'eau, le substrat et les conseils, et le
# validateur cesse donc d'exiger ce qui n'existe pas. Inventer une fenetre
# pour satisfaire le controle aurait affiche des etapes absurdes.
CATEGORIE_INTERIEUR = "plante-interieur"
EXPOSITIONS = {"plein-soleil", "mi-ombre", "ombre"}
BESOINS_EAU = {"faible", "moyen", "eleve"}
ANCRAGES = {"gelees_derniere", "gelees_premiere", "date_fixe"}
CHAMPS_REQUIS = (
    "id", "nom", "nom_scientifique", "famille", "categorie", "emoji",
    "difficulte", "exposition", "arrosage", "sol", "espacement_cm",
    "rusticite", "fenetres", "cycle", "associations", "conseils",
)


def valider(cultures: list[dict]) -> list[str]:
    """Renvoie la liste des problemes trouves. Vide = catalogue sain."""
    problemes: list[str] = []
    ids = [c["id"] for c in cultures]
    connus = set(ids)

    for doublon in {i for i in ids if ids.count(i) > 1}:
        problemes.append(f"id en double : {doublon}")

    for c in cultures:
        cid = c.get("id", "<sans id>")

        for champ in CHAMPS_REQUIS:
            if champ not in c:
                problemes.append(f"{cid} : champ requis absent '{champ}'")

        if c.get("categorie") not in CATEGORIES:
            problemes.append(f"{cid} : categorie inconnue {c.get('categorie')!r}")
        if c.get("exposition") not in EXPOSITIONS:
            problemes.append(f"{cid} : exposition inconnue {c.get('exposition')!r}")
        if c.get("arrosage", {}).get("besoin") not in BESOINS_EAU:
            problemes.append(f"{cid} : besoin en eau inconnu")
        if not 1 <= c.get("difficulte", 0) <= 3:
            problemes.append(f"{cid} : difficulte hors de 1-3")

        # `gel` commande le plafonnement de la recolte a la premiere gelee :
        # une fiche qui l'omet serait traitee comme rustique en silence, et
        # promettrait des courgettes en janvier.
        if not isinstance((c.get("rusticite") or {}).get("gel"), bool):
            problemes.append(f"{cid} : 'rusticite.gel' absent ou non booleen")

        for nom, ref in (("aime", "aime"), ("evite", "evite")):
            for autre in c.get("associations", {}).get(ref, []):
                if autre not in connus:
                    problemes.append(
                        f"{cid} : association '{nom}' vers une culture inconnue "
                        f"'{autre}'"
                    )

        interieur = c.get("categorie") == CATEGORIE_INTERIEUR
        fenetres = c.get("fenetres") or {}
        if not fenetres and not interieur:
            problemes.append(f"{cid} : aucune fenetre, la culture serait injouable")
        if fenetres and interieur:
            problemes.append(
                f"{cid} : plante d'interieur avec des fenetres — elles sont "
                f"calees sur les gelees, qu'elle ne connait pas"
            )
        for type_fenetre, fenetre in fenetres.items():
            ancrage = fenetre.get("ancrage")
            if ancrage not in ANCRAGES:
                problemes.append(f"{cid}/{type_fenetre} : ancrage {ancrage!r}")
            if ancrage == "date_fixe" and not fenetre.get("date"):
                problemes.append(f"{cid}/{type_fenetre} : 'date_fixe' sans date")
            if fenetre.get("duree_jours", 0) <= 0:
                problemes.append(f"{cid}/{type_fenetre} : duree nulle")

        problemes.extend(_valider_coherence(c, fenetres))

    return problemes


def _valider_coherence(c: dict, fenetres: dict) -> list[str]:
    """Verifie qu'on saura calculer une recolte pour cette culture."""
    cid = c["id"]
    cycle = c.get("cycle") or {}
    soucis: list[str] = []

    semis_int = "semis_interieur" in fenetres
    semis_dir = "semis_direct" in fenetres
    recolte_explicite = "recolte" in fenetres

    # Une plante d'interieur est perenne sans rien produire : lui demander une
    # recolte reviendrait a inventer une date.
    if c.get("categorie") == CATEGORIE_INTERIEUR:
        return soucis

    if c.get("perenne"):
        if not recolte_explicite:
            soucis.append(
                f"{cid} : perenne sans fenetre de recolte explicite — sa recolte "
                f"ne reviendrait jamais"
            )
        return soucis

    if not recolte_explicite:
        deductible = (
            ("plantation" in fenetres and cycle.get("jours_plantation_a_recolte"))
            or ((semis_dir or semis_int) and cycle.get("jours_semis_a_recolte"))
        )
        if not deductible:
            soucis.append(
                f"{cid} : aucune recolte calculable (ni fenetre explicite, ni "
                f"duree de cycle exploitable)"
            )

    if semis_int and not cycle.get("jours_semis_a_repiquage"):
        soucis.append(
            f"{cid} : semis a l'abri sans 'jours_semis_a_repiquage' — le "
            f"repiquage ne serait jamais propose"
        )

    return soucis


# --- Traductions --------------------------------------------------------------
#
# La langue de reference du catalogue est le francais ; l'anglais vit a cote,
# dans des champs suffixes. Le panneau et les entites choisissent lequel
# afficher (`catalog.localiser`), et les champs francais restent les cles :
# `rotation.DELAIS` s'indexe sur le nom francais de la famille.

SUFFIXE = "_en"


def traduire(cultures: list[dict]) -> list[str]:
    """Ajoute l'anglais a chaque fiche. Renvoie ce qui manque.

    Le defaut rattrape ici est precis : une culture ajoutee a la table sans sa
    traduction. Sans ce controle, elle s'afficherait en francais au milieu
    d'une interface anglaise, et personne ne s'en apercevrait avant de l'avoir
    sous les yeux.
    """
    manquants: list[str] = []

    for c in cultures:
        cid = c["id"]

        nom = NOMS.get(cid)
        if nom:
            c[f"nom{SUFFIXE}"] = nom
        else:
            manquants.append(f"{cid} : nom anglais absent de NOMS")

        famille = FAMILLES.get(c["famille"])
        if famille:
            c[f"famille{SUFFIXE}"] = famille
        else:
            manquants.append(f"{cid} : famille non traduite — {c['famille']!r}")

        sol = SOLS.get(c["sol"])
        if sol:
            c[f"sol{SUFFIXE}"] = sol
        else:
            manquants.append(f"{cid} : sol non traduit — {c['sol']!r}")

        notes = c["arrosage"].get("notes")
        if notes:
            traduite = EAU_NOTES.get(notes)
            if traduite:
                c["arrosage"][f"notes{SUFFIXE}"] = traduite
            else:
                manquants.append(
                    f"{cid} : note d'arrosage non traduite — {notes!r}"
                )

        conseils = []
        for conseil in c.get("conseils") or []:
            traduit = CONSEILS.get(conseil)
            if traduit:
                conseils.append(traduit)
            else:
                manquants.append(f"{cid} : conseil non traduit — {conseil!r}")
        if conseils:
            c[f"conseils{SUFFIXE}"] = conseils

    # Une traduction qui ne correspond plus a aucun texte du catalogue n'est pas
    # une erreur fatale, mais c'est du poids mort : on le dit.
    for table, nom_table, textes in (
        (NOMS, "NOMS", {c["id"] for c in cultures}),
        (FAMILLES, "FAMILLES", {c["famille"] for c in cultures}),
        (SOLS, "SOLS", {c["sol"] for c in cultures}),
        (
            EAU_NOTES,
            "EAU_NOTES",
            {c["arrosage"]["notes"] for c in cultures if c["arrosage"].get("notes")},
        ),
        (
            CONSEILS,
            "CONSEILS",
            {x for c in cultures for x in c.get("conseils") or []},
        ),
    ):
        for orpheline in sorted(set(table) - textes):
            manquants.append(
                f"{nom_table} : traduction orpheline, plus aucune fiche ne porte "
                f"{orpheline!r}"
            )

    return manquants


def main() -> int:
    problemes = valider(CULTURES) + traduire(CULTURES)
    if problemes:
        print(f"{len(problemes)} probleme(s) dans le catalogue :", file=sys.stderr)
        for p in problemes:
            print(f"  - {p}", file=sys.stderr)
        return 1

    if "--check" in sys.argv:
        print(f"Catalogue valide : {len(CULTURES)} cultures.")
        return 0

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    charge = {
        "version": 1,
        "licence": "CC BY-SA 4.0",
        "cultures": sorted(CULTURES, key=lambda c: c["nom"]),
    }
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"{len(CULTURES)} cultures ecrites dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
