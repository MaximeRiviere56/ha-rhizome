#!/usr/bin/env python3
"""Genere tools/fixture.js pour le banc d'essai du panneau.

Les reponses simulees sortent du vrai catalogue et du vrai moteur : le banc
verifie donc le panneau face aux donnees qu'il recevra reellement, et non face
a un jeu d'essai ecrit a la main qui finirait par mentir.

Usage : python3 tools/banc_fixture.py [fr|en]

La langue est un argument et non une devinette : le serveur resout « auto » et
l'annonce au panneau, donc le banc doit pouvoir faire les deux. Monter le banc
en anglais est la seule facon de voir d'un coup d'oeil ce qui serait reste en
francais — un libelle oublie ne se remarque pas en relisant la table.
"""

from __future__ import annotations

from datetime import date, timedelta
import importlib.util
import json
import pathlib
import sys
import types

RACINE = pathlib.Path(__file__).resolve().parent.parent
SRC = RACINE / "custom_components" / "rhizome"

_pkg = types.ModuleType("rhizome_banc")
_pkg.__path__ = [str(SRC)]
sys.modules["rhizome_banc"] = _pkg


def _charger(nom: str):
    spec = importlib.util.spec_from_file_location(f"rhizome_banc.{nom}", SRC / f"{nom}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"rhizome_banc.{nom}"] = module
    spec.loader.exec_module(module)
    return module


i18n = _charger("i18n")
lc = _charger("lifecycle")
ph = _charger("phenology")
cat = _charger("catalog")
wa = _charger("watering")

GELEES = ph.Gelees("04-15", "11-15")
AUJ = date.today()
DEPARTS = ("semis_interieur", "semis_direct", "plantation")

LANGUE = i18n.resoudre(sys.argv[1] if len(sys.argv) > 1 else None, None)

ZONES = [
    {
        "id": z["id"],
        "nom": i18n.nom_zone_defaut(LANGUE, z["id"], z["nom"]),
        "decalage_jours": z["decalage_jours"],
        **({"abritee": True} if z.get("abritee") else {}),
    }
    for z in [
        {"id": "pleine-terre", "nom": "Pleine terre", "decalage_jours": 0},
        {"id": "serre", "nom": "Serre", "decalage_jours": -21, "abritee": True},
        {"id": "chassis", "nom": "Chassis / tunnel", "decalage_jours": -10,
         "abritee": True},
        {"id": "balcon", "nom": "Balcon / pots", "decalage_jours": 0,
         "abritee": True},
    ]
]


def fiche_localisee(culture_id: str) -> dict:
    """La fiche telle que `websocket.py` la servira, dans la langue du banc."""
    return cat.localiser(cat.culture(culture_id), LANGUE)


def etape_dict(etape) -> dict:
    return {
        "type": etape.type,
        "debut": etape.debut.isoformat(),
        "fin": etape.fin.isoformat(),
        "source": etape.source,
        "libelle": i18n.libelle_etape(LANGUE, etape.type),
        "reelle": etape.reelle,
    }


def arrosage_dict(etat) -> dict | None:
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
            i18n.t(LANGUE, etat.motif_cle)
            if etat.motif_cle
            else etat.motif_exclusion
        ),
    }


def construire(culture_id, zone_id, evenements, surnom=None, arrose_il_y_a=None) -> dict:
    fiche = fiche_localisee(culture_id)
    zone = next(z for z in ZONES if z["id"] == zone_id)
    plante = {
        "uid": culture_id[:6],
        "culture_id": culture_id,
        "evenements": [],
        "surnom": surnom,
        "notifs": True,
        "rappel_jours": None,
        "zone": zone_id,
    }
    for type_evt, jour, extra in evenements:
        lc.ajouter_evenement(plante, lc.construire_evenement(type_evt, jour, **extra))

    if arrose_il_y_a is not None:
        wa.noter_arrosage(
            plante,
            wa.construire_arrosage(AUJ - timedelta(days=arrose_il_y_a)),
        )

    etapes = ph.prochaines_etapes(fiche, plante, GELEES, zone["decalage_jours"], AUJ)
    infos = lc.resume(plante)
    etat_eau = wa.etat(fiche, plante, zone, GELEES, AUJ)
    return {
        "uid": plante["uid"],
        "culture_id": culture_id,
        "nom": f"{fiche['nom']} ({surnom})" if surnom else fiche["nom"],
        "emoji": fiche["emoji"],
        "categorie": fiche["categorie"],
        "surnom": surnom,
        "zone": zone,
        "notifs": True,
        "rappel_jours": None,
        "phase": infos["phase"],
        "phase_libelle": i18n.libelle_phase(LANGUE, infos["phase"]),
        "perenne": bool(fiche.get("perenne")),
        "prochaine": etape_dict(etapes[0]) if etapes else None,
        "etapes": [etape_dict(e) for e in etapes],
        "date_semis": infos["date_semis"].isoformat() if infos["date_semis"] else None,
        "date_mise_en_place": (
            infos["date_mise_en_place"].isoformat() if infos["date_mise_en_place"] else None
        ),
        "nb_recoltes": infos["nb_recoltes"],
        "total_recolte_g": infos["total_recolte_g"],
        "evenements": [
            {**e, "libelle": i18n.libelle_evenement(LANGUE, e["type"])}
            for e in plante["evenements"]
        ],
        "arrosage_actif": True,
        "arrosage_frequence_jours": None,
        "arrosage": arrosage_dict(etat_eau),
        "arrosages": list(reversed(plante.get("arrosages") or []))[:20],
        "exposition": fiche["exposition"],
    }


def depart(fiche) -> dict:
    candidates = [
        e
        for annee in (AUJ.year, AUJ.year + 1)
        for e in ph.fenetres_theoriques(fiche, GELEES, 0, annee)
        if e.type in DEPARTS and e.fin >= AUJ
    ]
    if not candidates:
        return {"semable_maintenant": False, "prochain_depart": None}
    candidates.sort(key=lambda e: e.debut)
    ouverte = next((e for e in candidates if e.contient(AUJ)), None)
    return {
        "semable_maintenant": ouverte is not None,
        "prochain_depart": etape_dict(ouverte or candidates[0]),
    }


def main() -> None:
    il_y_a = lambda n: (AUJ - timedelta(days=n)).isoformat()  # noqa: E731

    # Un echantillon qui couvre les cinq phases : c'est la seule facon de voir
    # si une vue se casse sur un cas de bord.
    plantes = [
        construire("tomate", "serre", [("seme", il_y_a(40), {"mode": "interieur"})],
                   "Cœur de bœuf", arrose_il_y_a=3),
        construire("radis", "pleine-terre", []),
        construire(
            "courgette",
            "pleine-terre",
            [
                ("plante", il_y_a(70), {}),
                ("recolte", il_y_a(9), {"quantite_g": 620}),
                ("recolte", il_y_a(2), {"quantite_g": 840, "note": "trois belles"}),
            ],
            arrose_il_y_a=1,
        ),
        construire("pommier", "pleine-terre", [("plante", "2024-11-20", {})]),
        construire(
            "laitue",
            "balcon",
            [("seme", il_y_a(60), {"mode": "direct"}), ("perdu", il_y_a(30), {"cause": "limaces"})],
        ),
    ]

    actions = []
    for plante in plantes:
        prochaine = plante["prochaine"]
        if not prochaine:
            continue
        debut = date.fromisoformat(prochaine["debut"])
        fin = date.fromisoformat(prochaine["fin"])
        restants = (debut - AUJ).days
        if restants <= 3:
            actions.append(
                {
                    "uid": plante["uid"],
                    "nom": plante["nom"],
                    "emoji": plante["emoji"],
                    "zone": plante["zone"]["nom"],
                    "etape": prochaine,
                    "jours_restants": restants,
                    "en_cours": debut <= AUJ <= fin,
                }
            )

    besoins_eau = []
    for plante in plantes:
        eau = plante["arrosage"]
        if eau and eau["a_arroser"]:
            besoins_eau.append(
                {
                    "uid": plante["uid"],
                    "nom": plante["nom"],
                    "emoji": plante["emoji"],
                    "zone": plante["zone"]["nom"],
                    "etat": eau,
                }
            )
    besoins_eau.sort(key=lambda b: b["etat"]["jours_restants"])

    jardin = {
        "plantes": plantes,
        "arrosages": besoins_eau,
        "arrosage_actif": True,
        "zones": ZONES,
        "actions": actions,
        "total_recolte_g": sum(p["total_recolte_g"] for p in plantes),
        "gelees": {"derniere": GELEES.derniere, "premiere": GELEES.premiere},
        "rappel_jours": 3,
        "langue": LANGUE,
    }
    # Une fiche marquee « corrigee », pour voir le badge et le libelle.
    catalogue = {
        "cultures": [
            {
                **cat.info_minimale(cat.localiser(c, LANGUE)),
                **depart(c),
                "perso": c["id"] == "carotte",
                "surcharge": c["id"] == "carotte",
            }
            for c in cat.toutes(LANGUE)
        ],
        "categories": cat.categories(),
        "total": len(cat.toutes()),
    }

    # Un avertissement de rotation realiste : la tomate apres l'aubergine.
    aubergine = fiche_localisee("aubergine")
    rotation = {
        "avertissement": {
            "famille": aubergine["famille"],
            "delai_ans": 4,
            "precedents": [
                {
                    "nom": aubergine["nom"],
                    "annee": AUJ.year,
                    "culture_id": "aubergine",
                }
            ],
            "message": i18n.t(
                LANGUE,
                "rotation_message",
                famille=aubergine["famille"],
                precedents=f"{aubergine['nom']} ({AUJ.year})",
                delai=4,
            ),
        }
    }
    reglages = {
        "options": {
            "preset_climat": "oceanique",
            "gelees_derniere": GELEES.derniere,
            "gelees_premiere": GELEES.premiere,
            "notify_targets": ["notify.mobile_app_fairphone_6"],
            "notify_heure": "08:00:00",
            "rappel_jours": 3,
            "notify_etapes": [
                "semis_interieur", "semis_direct", "repiquage", "plantation", "recolte",
            ],
            "notify_resume": False,
            "notify_recolte_recurrence": 2,
            "masquer_terminees": False,
            "arrosage_actif": True,
            "langue": LANGUE,
        },
        "cibles_possibles": [
            {"value": "notify.mobile_app_fairphone_6", "label": "Fairphone 6", "mobile": True},
            {"value": "notify.mobile_app_maxime", "label": "Maxime", "mobile": True},
            {"value": "persistent_notification",
             "label": i18n.t(LANGUE, "cible_persistante"), "mobile": False},
        ],
        "presets": {},
        "etapes_notifiables": [
            "semis_interieur", "semis_direct", "repiquage", "plantation", "recolte",
        ],
        "langue": LANGUE,
        "langues": list(i18n.LANGUES),
    }

    cultures_perso = {
        "cultures": [
            {
                "id": "perso-chou-rave", "nom": "Chou-rave", "emoji": "🥬",
                "categorie": "legume-feuille", "famille": "Brassicacées",
                "difficulte": 1, "exposition": "plein-soleil",
                "arrosage": {"besoin": "moyen", "frequence_jours": 3, "notes": ""},
                "sol": "ordinaire", "espacement_cm": 25,
                "rusticite": {"gel": True, "temp_min_c": None}, "perso": True,
                "fenetres": {
                    "semis_direct": {"ancrage": "date_fixe", "date": "03-01",
                                     "duree_jours": 120}
                },
                "cycle": {"jours_semis_a_recolte": 70, "duree_recolte_jours": 30},
                "associations": {"aime": [], "evite": []}, "conseils": [],
            }
        ]
    }

    # Le calendrier : fenetres theoriques de l'annee, et etapes reelles.
    lignes = []
    for plante in plantes:
        zone = next(z for z in ZONES if z["id"] == plante["zone"]["id"])
        fiche_culture = fiche_localisee(plante["culture_id"])
        lignes.append(
            {
                "uid": plante["uid"],
                "nom": plante["nom"],
                "emoji": plante["emoji"],
                "zone": plante["zone"]["nom"],
                "prevues": [
                    etape_dict(e)
                    for e in ph.fenetres_theoriques(
                        fiche_culture, GELEES, zone["decalage_jours"], AUJ.year
                    )
                ],
                "reelles": [e for e in plante["etapes"] if e["reelle"]],
                "evenements": [
                    evt for evt in plante["evenements"]
                    if evt["date"][:4] == str(AUJ.year)
                ],
            }
        )
    calendrier = {"annee": AUJ.year, "lignes": lignes}

    tomate = fiche_localisee("tomate")
    fiche = {
        "culture": tomate,
        "compagnes": {
            cle: [cat.info_minimale(cat.localiser(x, LANGUE)) for x in valeur]
            for cle, valeur in cat.compagnes("tomate").items()
        },
        "fenetres": [etape_dict(e) for e in ph.fenetres_theoriques(tomate, GELEES)],
    }

    sortie = RACINE / "tools" / "fixture.js"
    sortie.write_text(
        "// Genere par tools/banc_fixture.py — ne pas editer a la main.\n"
        "window.__hassFactice = {\n  states: {},\n  callWS: async (msg) => {\n"
        "    const reponses = {\n"
        f'      "rhizome/jardin": {json.dumps(jardin, ensure_ascii=False)},\n'
        f'      "rhizome/catalogue": {json.dumps(catalogue, ensure_ascii=False)},\n'
        f'      "rhizome/culture": {json.dumps(fiche, ensure_ascii=False)},\n'
        f'      "rhizome/reglages": {json.dumps(reglages, ensure_ascii=False)},\n'
        f'      "rhizome/cultures_perso": {json.dumps(cultures_perso, ensure_ascii=False)},\n'
        f'      "rhizome/calendrier": {json.dumps(calendrier, ensure_ascii=False)},\n'
        f'      "rhizome/rotation": {json.dumps(rotation, ensure_ascii=False)},\n'
        "    };\n"
        "    if (msg.type in reponses) return reponses[msg.type];\n"
        "    // Les commandes d'ecriture n'ont rien a simuler : le banc verifie\n"
        "    // que l'interface les emet, pas qu'elles aboutissent.\n"
        '    if (/\\/(ajouter|modifier|retirer|noter|annuler|zones|ressemer|arroser|definir|supprimer|retablir)/.test(msg.type)) {\n'
        '      console.log("ECRITURE", JSON.stringify(msg));\n'
        "      return { ok: true, uid: \"simule\" };\n"
        "    }\n"
        '    throw new Error("commande non simulee : " + msg.type);\n'
        "  },\n};\n",
        encoding="utf-8",
    )
    print(
        f"{sortie.relative_to(RACINE)} : {len(plantes)} plantes, "
        f"{len(actions)} actions, langue « {LANGUE} »"
    )
    for plante in plantes:
        prochaine = plante["prochaine"] or {}
        eau = plante["arrosage"] or {}
        soif = (
            "à arroser" if eau.get("a_arroser")
            else f"eau dans {eau['jours_restants']} j" if eau.get("concernee")
            else "—"
        )
        print(
            f"  {plante['nom']:28} {plante['phase_libelle']:11} "
            f"{prochaine.get('libelle', '—'):16} {soif}"
        )


if __name__ == "__main__":
    main()
