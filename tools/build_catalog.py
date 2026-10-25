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
}
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

        fenetres = c.get("fenetres") or {}
        if not fenetres:
            problemes.append(f"{cid} : aucune fenetre, la culture serait injouable")
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


def main() -> int:
    problemes = valider(CULTURES)
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
