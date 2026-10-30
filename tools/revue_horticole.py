#!/usr/bin/env python3
"""Revue croisee des donnees de culture, contre des relevés sourcés.

Pourquoi ce fichier contient des donnees et non du reseau, contrairement a
`revue_croisee.py` : **aucune API ne sert de calendriers de culture.** OpenFarm
est mort, Permapeople demande une cle, practicalplants ne repond plus, et les
bases taxonomiques ignorent l'horticulture. La verification se fait donc a la
main, source par source — et ce qu'elle produit doit alors etre *conserve*,
sinon chaque relecture repart de zero et le travail n'est vrai qu'au jour ou
il est fait.

Chaque entree de `RELEVES` est un fait releve dans une source nommee, avec son
URL. Le script ne les croit pas : il les compare a la fiche et dit ou ca
diverge, et de combien.

**Ce qui est verifiable, et ce qui ne l'est pas.** Une revue croisee ne rend
pas ces champs « vrais » — l'espacement, l'eau et les durees de cycle
dependent de la variete, du sol et du climat, et trois sources serieuses
donnent trois chiffres. Ce qu'elle etablit est plus modeste et plus utile :
une **fourchette plausible**, et le constat qu'une valeur de fiche en sort.
C'est une alerte, pas un verdict. Ne presente jamais ce fichier comme une
preuve d'exactitude.

Les offsets sont exprimes en jours par rapport a la derniere gelee, comme dans
le catalogue : une source qui dit « fin avril » pour une derniere gelee au
15 avril vaut +15.

Usage : python3 tools/revue_horticole.py [--tout]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
CATALOGUE = RACINE / "custom_components" / "rhizome" / "data" / "catalog.json"

SOURCES = {
    "rhs": ("Royal Horticultural Society", "https://www.rhs.org.uk"),
    "almanac": ("The Old Farmer's Almanac", "https://www.almanac.com"),
    "aujardin": ("Au Jardin", "https://www.aujardin.info"),
    "gerbeaud": ("Gerbeaud", "https://www.gerbeaud.com"),
    "anses": ("Anses — toxicovigilance", "https://www.anses.fr"),
    "ema": ("Agence europeenne du medicament, monographies HMPC",
            "https://www.ema.europa.eu"),
    "aspca": ("ASPCA — plantes toxiques", "https://www.aspca.org"),
}

# Les champs relevables, et ce que chacun signifie ici.
#   espacement_cm        : distance entre plants, en centimetres
#   profondeur_cm        : profondeur de semis, en centimetres
#   offset_plantation    : jours apres la derniere gelee pour la mise en place
#   offset_semis_direct  : idem pour un semis en place
#   offset_semis_abri    : jours avant la derniere gelee pour un semis a l'abri
#   jours_plant_recolte  : plantation -> recolte, en jours
#   jours_semis_recolte  : semis -> recolte, en jours
#
# Piege a connaitre avant de relever un « days to maturity » anglo-saxon : il
# se compte **depuis le repiquage** pour une culture que l'on repique (tomate,
# poivron, aubergine) et **depuis le semis** pour une culture semee en place
# (carotte, radis, haricot). Le lire comme « semis -> recolte » dans le premier
# cas fait apparaitre un ecart de cinquante jours qui n'existe pas.
#   besoin_eau           : faible | moyen | eleve
#   temp_min_c           : temperature en dessous de laquelle la plante souffre
#
# Une valeur peut etre un nombre ou un couple (mini, maxi) quand la source
# donne une fourchette — et elle en donne presque toujours une.

RELEVES: dict[str, dict[str, dict]] = {
    "tomate": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/tomatoes/grow-your-own",
            "espacement_cm": (45, 60),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/tomatoes",
            "espacement_cm": (60, 90),
            "profondeur_cm": 1.3,
            "offset_semis_abri": -42,
            "offset_plantation": 14,
            "jours_plant_recolte": (60, 100),
            "besoin_eau": "eleve",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/tomate.php",
            "espacement_cm": 50,
            "profondeur_cm": 0.3,
            "offset_semis_abri": -60,
            "offset_plantation": (15, 20),
            "besoin_eau": "eleve",
        },
    },
    "courgette": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/courgettes/grow-your-own",
            "espacement_cm": 90,
            "profondeur_cm": (1.3, 2.5),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/zucchini",
            "espacement_cm": (60, 90),
            "profondeur_cm": 2.5,
            "jours_plant_recolte": 60,
            "besoin_eau": "eleve",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/courgette.php",
            "espacement_cm": 100,
            "offset_plantation": 15,  # « dès que tout risque de gel est écarté »
            "besoin_eau": "eleve",
        },
    },
    "carotte": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/carrots/grow-your-own",
            "espacement_cm": (5, 7.5),
            "profondeur_cm": 1,
            "jours_semis_recolte": (84, 112),
            "besoin_eau": "faible",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/carrots",
            "espacement_cm": (3, 4),
            "profondeur_cm": 0.6,
            "offset_semis_direct": -21,
            "jours_semis_recolte": 60,
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/carotte.php",
            "espacement_cm": (6, 7),
            "jours_semis_recolte": (90, 150),
            "besoin_eau": "moyen",
        },
    },
    "poivron": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/peppers/grow-your-own",
            "espacement_cm": (30, 45),
            "temp_min_c": 12,
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/bell-peppers",
            "espacement_cm": (30, 45),
            "profondeur_cm": 0.6,
            "offset_semis_abri": (-70, -56),
            "offset_plantation": (14, 21),
            "jours_plant_recolte": (60, 90),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/poivron.php",
            "espacement_cm": 60,
            "offset_plantation": 30,
            "temp_min_c": 15,
        },
    },
    "radis": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/radishes/grow-your-own",
            "espacement_cm": (2.5, 5),
            "profondeur_cm": (1, 2),
            "jours_semis_recolte": (28, 42),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/radishes",
            "espacement_cm": (2.5, 5),
            "profondeur_cm": 1.3,
            "offset_semis_direct": -42,
            "jours_semis_recolte": (21, 28),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/radis.php",
            "espacement_cm": 3,
            "profondeur_cm": (1, 2),
            "jours_semis_recolte": (28, 35),
            "besoin_eau": "eleve",
        },
    },
    "laitue": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/lettuce/grow-your-own",
            "espacement_cm": (15, 30),
            "profondeur_cm": 1,
            "jours_semis_recolte": (28, 98),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/lettuce",
            "espacement_cm": (10, 40),
            "profondeur_cm": (0.3, 0.6),
            "offset_semis_abri": (-56, -42),
            "offset_semis_direct": (-28, -14),
            "besoin_eau": "eleve",
            "temp_min_c": -2,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/laitue.php",
            "jours_semis_recolte": 42,
            "besoin_eau": "eleve",
        },
    },
    "haricot-nain": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/french-beans/grow-your-own",
            "espacement_cm": 15,
            "profondeur_cm": 5,
            "jours_semis_recolte": (56, 70),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/beans",
            "espacement_cm": 5,
            "profondeur_cm": 2.5,
            "jours_semis_recolte": (50, 55),
            "temp_min_c": 12,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/haricot.php",
            "espacement_cm": 40,
            "profondeur_cm": 3,
            "offset_semis_direct": 28,  # « mai dans le nord »
            "jours_semis_recolte": 90,
        },
    },
    "petit-pois": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/peas/grow-your-own",
            "espacement_cm": 7.5,
            "profondeur_cm": 5,
            "jours_semis_recolte": (84, 112),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/peas",
            "espacement_cm": 5,
            "profondeur_cm": 2.5,
            "offset_semis_direct": (-42, -28),
            "jours_semis_recolte": (60, 70),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/pois.php",
            "espacement_cm": (2, 3),
            "profondeur_cm": (5, 8),
            "jours_semis_recolte": (70, 80),
            "besoin_eau": "faible",
        },
    },
    "concombre": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/cucumbers/grow-your-own",
            "espacement_cm": 30,
            "profondeur_cm": (1, 2),
            "temp_min_c": 12,
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/cucumbers",
            "espacement_cm": (30, 45),
            "profondeur_cm": 2.5,
            "offset_semis_abri": -21,
            "offset_plantation": 14,
            "jours_semis_recolte": (50, 70),
            "besoin_eau": "eleve",
            "temp_min_c": 10,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/concombre.php",
            "espacement_cm": 60,
            "offset_plantation": (45, 75),
            "temp_min_c": 10,
            "besoin_eau": "eleve",
        },
    },
    "aubergine": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/aubergines/grow-your-own",
            "espacement_cm": 60,
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/eggplants",
            "espacement_cm": (60, 75),
            "profondeur_cm": 0.6,
            "offset_semis_abri": (-56, -42),
            "jours_semis_recolte": (100, 120),
            "jours_plant_recolte": (65, 80),
            "besoin_eau": "eleve",
            "temp_min_c": 13,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/aubergine.php",
            "offset_plantation": 28,  # « mai, après la dernière gelée »
            "temp_min_c": 12,
            "besoin_eau": "eleve",
        },
    },
    "poireau": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/leeks/grow-your-own",
            "espacement_cm": (15, 20),
            "profondeur_cm": 1.5,
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/leeks",
            "profondeur_cm": 0.6,
            "offset_semis_abri": (-70, -56),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/poireau.php",
            "espacement_cm": 15,
            "offset_plantation": 30,
            "besoin_eau": "moyen",
        },
    },
    "cosmos": {
        "almanac": {
            "url": "https://www.almanac.com/plant/cosmos",
            "espacement_cm": (30, 45),
            "profondeur_cm": 0.6,
            "offset_semis_direct": 15,  # « once the danger of frost has passed »
            "besoin_eau": "faible",
        },
    },
    "tournesol": {
        "almanac": {
            "url": "https://www.almanac.com/plant/sunflowers",
            "espacement_cm": 15,
            "profondeur_cm": (2.5, 4),
            "offset_semis_direct": 15,  # « after the danger of frost has passed »
        },
    },
}


# Tolerance avant de crier a l'ecart. Sans elle, une profondeur de semis de
# 0,5 cm « diverge » d'une source qui dit 0,6 : un millimetre, sur un geste
# qui se fait au doigt. On veut attraper l'erreur d'ordre de grandeur, pas la
# decimale — c'est la meme logique que les plages larges de l'audit.
TOLERANCE_RELATIVE = 0.25
TOLERANCE_ABSOLUE = {"profondeur_cm": 0.5, "temp_min_c": 2.0}
# Une tolerance relative sur une temperature ne veut rien dire : 25 % de 12 °C
# n'est pas une grandeur horticole. Ces champs n'ont qu'une marge absolue.
SANS_TOLERANCE_RELATIVE = {"temp_min_c"}


# Les ecarts assumes, par (identifiant, champ), avec leur raison. Meme logique
# que `DIVERGENCES_ASSUMEES` dans `revue_croisee.py` : sans cette table,
# l'outil signalerait a chaque passage des choix deliberes, et un audit qui
# echoue toujours est un audit que plus personne ne relance.
#
# Le gros du lot vient d'une seule decision : les cultures gelives sortent
# apres les saints de glace, soit vingt-huit jours apres une derniere gelee
# moyenne au 15 avril. Les sources anglo-saxonnes disent « apres la derniere
# gelee » sans marge, ce qui est vrai ailleurs et imprudent ici.
ECARTS_ASSUMES = {
    ("tomate", "offset_plantation"): "saints de glace — 13 mai, non +14 j",
    ("courgette", "offset_plantation"): "saints de glace",
    ("cosmos", "offset_semis_direct"): "saints de glace",
    ("tournesol", "offset_semis_direct"): "saints de glace",
    ("aubergine", "offset_semis_abri"): (
        "semis avance de 13 j avec la plantation, pour garder le delai en godet"
    ),
    # Pratiques francaises, ou la source anglo-saxonne decrit un autre usage.
    ("carotte", "offset_semis_direct"): (
        "semis des mars sous chassis en France ; RHS dit fevrier-juillet"
    ),
    ("petit-pois", "offset_semis_direct"): (
        "semis de fevrier en France (Au Jardin), plus tot qu'aux Etats-Unis"
    ),
    ("radis", "offset_semis_direct"): "la fiche seme plus tard que l'Almanac, pas plus tot",
    ("tournesol", "espacement_cm"): (
        "l'Almanac decrit un semis dense de rang a 15 cm ; 50 cm est l'usage "
        "francais pour un tournesol de pied"
    ),
}


def _fourchette(valeur) -> tuple[float, float]:
    if isinstance(valeur, (list, tuple)):
        return float(valeur[0]), float(valeur[1])
    return float(valeur), float(valeur)


def _valeur_fiche(fiche: dict, champ: str):
    fenetres = fiche.get("fenetres") or {}
    cycle = fiche.get("cycle") or {}
    if champ == "espacement_cm":
        return fiche.get("espacement_cm")
    if champ == "profondeur_cm":
        return fiche.get("profondeur_semis_cm")
    if champ == "besoin_eau":
        return (fiche.get("arrosage") or {}).get("besoin")
    if champ == "temp_min_c":
        return (fiche.get("rusticite") or {}).get("temp_min_c")
    if champ == "jours_plant_recolte":
        return cycle.get("jours_plantation_a_recolte")
    if champ == "jours_semis_recolte":
        return cycle.get("jours_semis_a_recolte")
    correspondance = {
        "offset_plantation": "plantation",
        "offset_semis_direct": "semis_direct",
        "offset_semis_abri": "semis_interieur",
    }
    fenetre = fenetres.get(correspondance.get(champ, ""))
    return fenetre.get("offset_jours") if fenetre else None


def comparer(fiches: dict) -> list[dict]:
    """Confronte chaque relevé à sa fiche. Renvoie les écarts constatés."""
    ecarts = []
    for cid, par_source in sorted(RELEVES.items()):
        fiche = fiches.get(cid)
        if fiche is None:
            ecarts.append({"id": cid, "champ": "—", "probleme": "fiche absente"})
            continue

        champs = {c for releve in par_source.values() for c in releve if c != "url"}
        for champ in sorted(champs):
            valeurs = {
                src: releve[champ]
                for src, releve in par_source.items()
                if champ in releve
            }
            nôtre = _valeur_fiche(fiche, champ)
            if nôtre is None:
                continue

            if champ == "besoin_eau":
                accord = set(valeurs.values())
                if len(accord) == 1 and nôtre not in accord:
                    ecarts.append({
                        "id": cid, "champ": champ, "fiche": nôtre,
                        "sources": valeurs, "n": len(valeurs),
                    })
                continue

            # L'enveloppe de toutes les sources : une valeur de fiche qui en
            # sort est hors de ce que *personne* n'avance.
            bas = min(_fourchette(v)[0] for v in valeurs.values())
            haut = max(_fourchette(v)[1] for v in valeurs.values())
            # Une seule source qui diverge est une piste, pas un constat :
            # Almanac donne 15 cm entre tournesols (semis dense de rang), la
            # pratique francaise 50. Croire la premiere source venue
            # remplacerait une valeur discutable par une autre.
            if champ in SANS_TOLERANCE_RELATIVE:
                marge = TOLERANCE_ABSOLUE.get(champ, 0.0)
            else:
                marge = max(
                    abs(haut - bas) * TOLERANCE_RELATIVE,
                    abs(haut) * TOLERANCE_RELATIVE,
                    TOLERANCE_ABSOLUE.get(champ, 0.0),
                )
            if not (bas - marge) <= float(nôtre) <= (haut + marge):
                ecarts.append({
                    "id": cid, "champ": champ, "fiche": nôtre,
                    "enveloppe": (bas, haut), "sources": valeurs,
                    "n": len(valeurs),
                })
    return ecarts


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument(
        "--tout", action="store_true", help="liste aussi les fiches sans relevé"
    )
    args = parseur.parse_args()

    fiches = {
        c["id"]: c
        for c in json.loads(CATALOGUE.read_text(encoding="utf-8"))["cultures"]
    }
    ecarts = comparer(fiches)

    croisees = [c for c in RELEVES if len(RELEVES[c]) >= 3]
    print(f"{len(RELEVES)} fiches relevées sur {len(fiches)} "
          f"({len(croisees)} sur trois sources ou plus).")
    assumes = [e for e in ecarts if (e["id"], e["champ"]) in ECARTS_ASSUMES]
    ecarts = [e for e in ecarts if (e["id"], e["champ"]) not in ECARTS_ASSUMES]
    fermes = [e for e in ecarts if e.get("n", 0) >= 2]
    print(f"{len(assumes)} écart(s) assumé(s), avec leur raison.")
    print(f"{len(ecarts)} écart(s) restant(s), dont {len(fermes)} où au moins deux sources "
          f"convergent contre la fiche.")
    print("  ! = deux sources ou plus   ~ = une seule, piste à creuser\n")

    for e in ecarts:
        sources = ", ".join(f"{s}={v}" for s, v in e.get("sources", {}).items())
        enveloppe = e.get("enveloppe")
        etendue = (
            f" — hors de {enveloppe[0]:g}…{enveloppe[1]:g}, tolérance comprise"
            if enveloppe else ""
        )
        poids = "!" if e.get("n", 0) >= 2 else "~"
        print(f"{poids} {e['id']:20} {e['champ']:20} fiche={e['fiche']}{etendue}")
        print(f"  {'':20} {'':20} {sources}")

    for e in assumes:
        print(f"~ {e['id']:20} {e['champ']:20} "
              f"{ECARTS_ASSUMES[(e['id'], e['champ'])]}")

    # Un écart assumé que les sources ne rapportent plus masquerait une vraie
    # divergence sur cette fiche : on le dit.
    vus = {(e["id"], e["champ"]) for e in assumes}
    for cle in sorted(set(ECARTS_ASSUMES) - vus):
        if cle[0] in RELEVES:
            print(f"! {cle[0]} / {cle[1]} : écart assumé devenu sans objet, à retirer")

    if args.tout:
        manquantes = sorted(set(fiches) - set(RELEVES))
        print(f"\n{len(manquantes)} fiches sans relevé :")
        for debut in range(0, len(manquantes), 6):
            print("  " + "  ".join(f"{m:22}" for m in manquantes[debut : debut + 6]))

    # Seuls les ecarts ou au moins deux sources convergent contre la fiche
    # font echouer : en dessous, c'est une piste a creuser, pas un constat.
    fermes = [e for e in ecarts if e.get("n", 0) >= 2]
    return 1 if fermes else 0


if __name__ == "__main__":
    sys.exit(main())
