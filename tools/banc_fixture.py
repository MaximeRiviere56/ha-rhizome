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
rot = _charger("rotation")
ser = _charger("serialisation")

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

    # Une liste donne une serie, et c'est le seul moyen de voir si le journal
    # groupe ses arrosages au lieu de noyer les etapes du cycle sous eux.
    if arrose_il_y_a is not None:
        jours = (
            [arrose_il_y_a] if isinstance(arrose_il_y_a, int) else list(arrose_il_y_a)
        )
        for ecart in sorted(jours, reverse=True):
            wa.noter_arrosage(
                plante,
                wa.construire_arrosage(AUJ - timedelta(days=ecart)),
            )

    etapes = ph.prochaines_etapes(fiche, plante, GELEES, zone["decalage_jours"], AUJ)
    infos = lc.resume(plante)
    etat_eau = wa.etat(fiche, plante, zone, GELEES, AUJ)
    # La vue calculee du coordinateur, telle que `coordinator.py` la construit.
    # Le banc la fabrique, mais ne serialise plus lui-meme : c'est
    # `serialisation.plante_en_dict` qui s'en charge, le meme code que
    # l'instance. Cette copie manuelle avait deja montre un arrosage par
    # plante qui fonctionnait au banc alors qu'il etait casse en production.
    entree = {
        "uid": plante["uid"],
        "plante": plante,
        "culture": fiche,
        "zone": zone,
        "etapes": etapes,
        "prochaine": etapes[0] if etapes else None,
        "resume": infos,
        "nom_affiche": f"{fiche['nom']} ({surnom})" if surnom else fiche["nom"],
        "arrosage": etat_eau,
    }
    return ser.plante_en_dict(entree, LANGUE)


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
        "prochain_depart": ser.etape_en_dict(ouverte or candidates[0], LANGUE),
    }


def main() -> None:
    il_y_a = lambda n: (AUJ - timedelta(days=n)).isoformat()  # noqa: E731

    # Un echantillon qui couvre les cinq phases : c'est la seule facon de voir
    # si une vue se casse sur un cas de bord.
    plantes = [
        construire("tomate", "serre", [("seme", il_y_a(40), {"mode": "interieur"})],
                   "Cœur de bœuf", arrose_il_y_a=[3, 6, 9, 12, 15, 18, 21, 24]),
        construire("radis", "pleine-terre", []),
        construire(
            "courgette",
            "pleine-terre",
            [
                ("plante", il_y_a(70), {}),
                ("recolte", il_y_a(9), {"quantite_g": 620}),
                ("recolte", il_y_a(2), {"quantite_g": 840, "note": "trois belles"}),
            ],
            arrose_il_y_a=[1, 4, 11],
        ),
        construire("pommier", "pleine-terre", [("plante", "2024-11-20", {})]),
        # Terminee, mais elle a occupe la pleine terre cette annee : c'est
        # elle qui declenche pour de vrai l'avertissement de rotation sur
        # toute solanacee, au lieu qu'il soit ecrit a la main.
        construire(
            "aubergine",
            "pleine-terre",
            [("plante", il_y_a(150), {}), ("termine", il_y_a(20), {})],
        ),
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

    # L'avertissement de rotation, calcule pour de vrai et par culture. Le
    # banc en servait un seul, ecrit a la main : il annoncait des solanacees
    # devant n'importe quelle fiche, un peperomia compris. Tant que la vue
    # detail servait elle aussi une reponse unique, cela ne se voyait pas.
    index_cultures = {cid: cat.localiser(f, LANGUE) for cid, f in cat.charger().items()}
    plantes_brutes = [
        {"culture_id": p["culture_id"], "zone": p["zone"]["id"],
         "evenements": p["evenements"]}
        for p in plantes
    ]
    rotations = {}
    for cid, fiche in index_cultures.items():
        for zone in ZONES:
            avis = rot.verifier(fiche, zone["id"], plantes_brutes, index_cultures, AUJ)
            if avis is None:
                continue
            avis = {
                **avis,
                "message": i18n.t(
                    LANGUE,
                    "rotation_message",
                    famille=fiche["famille"],
                    precedents=avis["precedents_libelle"],
                    delai=avis["delai_ans"],
                ),
            }
            rotations[f"{cid}|{zone['id']}"] = {"avertissement": avis}

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
                    ser.etape_en_dict(e, LANGUE)
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

    # Une fiche de detail par culture, et non la seule tomate. Le banc servait
    # la meme reponse quelle que soit la carte cliquee : toute la vue detail
    # lui echappait donc, y compris ce qu'elle montre d'une plante d'interieur
    # — qui n'a aucune fenetre et ne doit afficher aucun calendrier. Les 429 Ko
    # que cela ajoute a `fixture.js` ne coutent rien : le fichier est local,
    # genere, et jamais versionne.
    fiches = {
        cid: {
            "culture": fiche,
            "compagnes": {
                cle: [cat.info_minimale(cat.localiser(x, LANGUE)) for x in valeur]
                for cle, valeur in cat.compagnes(cid).items()
            },
            "fenetres": [
                ser.etape_en_dict(e, LANGUE)
                for e in ph.fenetres_theoriques(fiche, GELEES)
            ],
        }
        for cid, fiche in (
            (cid, fiche_localisee(cid)) for cid in sorted(cat.charger())
        )
    }

    sortie = RACINE / "tools" / "fixture.js"
    sortie.write_text(
        "// Genere par tools/banc_fixture.py — ne pas editer a la main.\n"
        "window.__hassFactice = {\n  states: {},\n  callWS: async (msg) => {\n"
        "    const reponses = {\n"
        f'      "rhizome/jardin": {json.dumps(jardin, ensure_ascii=False)},\n'
        f'      "rhizome/catalogue": {json.dumps(catalogue, ensure_ascii=False)},\n'
        f'      "rhizome/reglages": {json.dumps(reglages, ensure_ascii=False)},\n'
        f'      "rhizome/cultures_perso": {json.dumps(cultures_perso, ensure_ascii=False)},\n'
        f'      "rhizome/calendrier": {json.dumps(calendrier, ensure_ascii=False)},\n'
        "    };\n"
        f'    const fiches = {json.dumps(fiches, ensure_ascii=False)};\n'
        f'    const rotations = {json.dumps(rotations, ensure_ascii=False)};\n'
        '    if (msg.type === "rhizome/rotation") {\n'
        '      return rotations[msg.culture_id + "|" + msg.zone] || { avertissement: null };\n'
        '    }\n'
        '    if (msg.type === "rhizome/culture") {\n'
        '      const fiche = fiches[msg.culture_id];\n'
        '      if (!fiche) throw new Error("fiche inconnue : " + msg.culture_id);\n'
        '      return fiche;\n'
        '    }\n'
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
