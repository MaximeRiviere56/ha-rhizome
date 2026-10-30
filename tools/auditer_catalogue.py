#!/usr/bin/env python3
"""Audit de cohérence du catalogue.

Ce script ne peut pas dire qu'une fiche est *juste* — il n'a aucune source de
vérité. Il dit qu'une fiche est *impossible*, ce qui est déjà beaucoup :
une courgette semée en novembre, une récolte qui précède son semis, un arbre
espacé de trente centimètres. Chaque anomalie est un fait vérifiable sans
connaissance extérieure, par simple confrontation des champs entre eux.

Les durées de cycle restent hors de portée : seul un relevé au jardin peut
dire si la carotte met 100 ou 120 jours chez vous.

Usage : python3 tools/auditer_catalogue.py
"""

from __future__ import annotations

from datetime import date, timedelta
import importlib.util
import pathlib
import sys
import types

RACINE = pathlib.Path(__file__).resolve().parent.parent
SRC = RACINE / "custom_components" / "rhizome"

_pkg = types.ModuleType("rhizome_audit")
_pkg.__path__ = [str(SRC)]
sys.modules["rhizome_audit"] = _pkg


def _charger(nom: str):
    spec = importlib.util.spec_from_file_location(f"rhizome_audit.{nom}", SRC / f"{nom}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"rhizome_audit.{nom}"] = module
    spec.loader.exec_module(module)
    return module


ph = _charger("phenology")
cat = _charger("catalog")

GELEES = ph.Gelees("04-15", "11-15")
ANNEE = 2026
DERNIERE_GELEE = date(ANNEE, 4, 15)
PREMIERE_GELEE = date(ANNEE, 11, 15)

# Marge minimale entre la dernière gelée et la mise dehors d'une gélive. La
# « dernière gelée » est une moyenne : une année sur dix elle tombe après le
# 13 mai en plaine. Quinze jours est le minimum que s'applique déjà le
# catalogue, pas une valeur inventée ici.
MARGE_GELEE_MINI_JOURS = 15

# Bandes de fréquence d'arrosage plausibles par besoin, en jours. Elles ne
# disent pas quelle est la bonne fréquence — personne ne le sait sans relevé —
# mais interdisent qu'un « besoin élevé » soit arrosé moins souvent qu'un
# « besoin faible », ce qui rendrait les trois niveaux inutiles.
FREQUENCES = {
    "eleve": (1, 5),
    "moyen": (3, 10),
    "faible": (5, 25),
}

# Espacements plausibles par catégorie, en centimètres. Larges à dessein :
# on cherche l'aberration, pas le désaccord d'école.
ESPACEMENTS = {
    "aromatique": (5, 200),
    "legume-feuille": (4, 120),
    "legume-fruit": (10, 200),
    "legume-gousse": (3, 60),
    "legume-bulbe": (5, 40),
    "legume-racine": (3, 90),
    "fleur-compagne": (5, 80),
    "petit-fruit": (30, 500),
    "fruitier": (200, 1200),
    "cereale": (5, 120),
    # La plage est très large, et c'est le défaut assumé de la catégorie :
    # « médicinale » décrit un usage, pas un port. Elle contient une camomille
    # de vingt centimètres et un tilleul de vingt mètres, donc la règle n'y
    # attrape plus qu'une faute de frappe d'un ordre de grandeur.
    "medicinale": (10, 1000),
    # Pour une plante d'interieur, l'espacement n'est pas une distance de
    # plantation : c'est l'encombrement adulte, ce qu'elle prendra sur le
    # meuble. La plage va du pilea au ficus lyrata.
    "plante-interieur": (15, 300),
}

# Catégories plausibles pour une famille botanique donnée. Le but est
# d'attraper une faute de frappe — « Solanacées » sur un cerisier — pas de
# trancher des débats de classification. Les ensembles couvrent donc les
# usages réels : le goji est bien une solanacée et bien un petit fruit, et
# trèfle et vesce sont des fabacées que l'on sème comme engrais verts.
FAMILLES_ATTENDUES = {
    "Solanacées": {"legume-fruit", "legume-racine", "petit-fruit"},
    "Cucurbitacées": {"legume-fruit"},
    "Fabacées": {"legume-gousse", "fleur-compagne"},
    "Amaryllidacées": {"legume-bulbe", "aromatique"},
    # L'aubépine, l'églantier et la reine-des-prés sont des rosacées qu'on
    # cultive pour la fleur ou la feuille, pas pour le fruit.
    "Rosacées": {"fruitier", "petit-fruit", "medicinale"},
}


def auditer() -> list[tuple[str, str, str]]:
    """Renvoie (gravité, id, description) pour chaque anomalie."""
    anomalies: list[tuple[str, str, str]] = []
    index = cat.charger()

    for cid, c in sorted(index.items()):
        fenetres = c.get("fenetres") or {}
        cycle = c.get("cycle") or {}
        gelive = (c.get("rusticite") or {}).get("gel") is False
        perenne = bool(c.get("perenne"))

        # `fenetres` est lie par defaut : sans cela la fermeture lirait la
        # derniere fiche de la boucle, pas celle en cours.
        def borne(nom, fenetres=fenetres):
            f = fenetres.get(nom)
            if not f:
                return None
            return ph.resoudre_fenetre(f, GELEES, ANNEE, 0)

        semis_direct = borne("semis_direct")
        plantation = borne("plantation")
        recolte = borne("recolte")

        # 1. Une culture gélive mise dehors avant la dernière gelée gèlera.
        #
        #    Exception : ce qu'on enterre profond n'est pas exposé. La pomme de
        #    terre se plante mi-mars, bien avant la dernière gelée, parce que
        #    c'est un tubercule à 10 cm qui entre en terre ; le feuillage,
        #    lui, sortira plus tard. Le seuil de 8 cm distingue ces cultures
        #    des semis et plants de surface.
        enterre = (c.get("profondeur_semis_cm") or 0) >= 8

        for nom, bornes in (("semis en place", semis_direct), ("plantation", plantation)):
            if gelive and not enterre and bornes and bornes[0] < DERNIERE_GELEE:
                anomalies.append((
                    "GRAVE", cid,
                    f"gélive, mais {nom} commence le {bornes[0]:%d/%m}, "
                    f"avant la dernière gelée du {DERNIERE_GELEE:%d/%m}",
                ))

        # 1 bis. Une gélive mise dehors trop près de la dernière gelée.
        #
        #    La règle 1 ne regarde que l'antériorité, et laisse donc passer une
        #    tomate plantée le lendemain de la dernière gelée. Or la « dernière
        #    gelée » est une moyenne, pas une garantie : une année sur dix, en
        #    plaine, la dernière gelée tombe après le 13 mai, et c'est tout le
        #    sens des saints de glace. Ouvrir la fenêtre à la date moyenne,
        #    c'est annoncer « c'est le moment » une fois sur deux trop tôt.
        #
        #    Quinze jours est le seuil retenu, et c'est le minimum : c'est la
        #    valeur que le catalogue emploie déjà pour l'écrasante majorité de
        #    ses cultures gélives. Voir docs/revue-croisee.md pour la question
        #    restée ouverte — faut-il aller jusqu'aux saints de glace, soit
        #    près de quatre semaines.
        for nom, bornes in (("semis en place", semis_direct), ("plantation", plantation)):
            if gelive and not enterre and bornes:
                marge = (bornes[0] - DERNIERE_GELEE).days
                if 0 <= marge < MARGE_GELEE_MINI_JOURS:
                    anomalies.append((
                        "DOUTE", cid,
                        f"gélive, {nom} ouvert {marge} j après la dernière gelée — "
                        f"moins que les {MARGE_GELEE_MINI_JOURS} j de marge usuels",
                    ))

        # 2. Semer dehors une gélive après la première gelée n'a aucun sens.
        if gelive and semis_direct and semis_direct[0] > PREMIERE_GELEE:
            anomalies.append((
                "GRAVE", cid,
                f"gélive semée en place le {semis_direct[0]:%d/%m}, après la "
                f"première gelée",
            ))

        # 3. Récolte annoncée après la première gelée pour une gélive non
        #    plafonnée (le plafond ne joue que sur les fenêtres déduites).
        if gelive and recolte and recolte[0] > PREMIERE_GELEE and not perenne:
            anomalies.append((
                "GRAVE", cid,
                f"gélive dont la récolte démarre le {recolte[0]:%d/%m}, après "
                f"la première gelée",
            ))

        # 4. Durées incohérentes entre elles.
        semis_recolte = cycle.get("jours_semis_a_recolte")
        plant_recolte = cycle.get("jours_plantation_a_recolte")
        repiquage = cycle.get("jours_semis_a_repiquage")

        if semis_recolte and plant_recolte and semis_recolte <= plant_recolte:
            anomalies.append((
                "GRAVE", cid,
                f"semis→récolte ({semis_recolte} j) n'est pas plus long que "
                f"plantation→récolte ({plant_recolte} j) : le semis précède "
                f"pourtant la mise en place",
            ))
        if semis_recolte and repiquage and semis_recolte <= repiquage:
            anomalies.append((
                "GRAVE", cid,
                f"semis→récolte ({semis_recolte} j) n'est pas plus long que "
                f"semis→repiquage ({repiquage} j)",
            ))
        if repiquage and plant_recolte and semis_recolte:
            attendu = repiquage + plant_recolte
            ecart = abs(attendu - semis_recolte)
            if ecart > 45:
                anomalies.append((
                    "DOUTE", cid,
                    f"semis→récolte vaut {semis_recolte} j, mais repiquage "
                    f"({repiquage}) + plantation→récolte ({plant_recolte}) "
                    f"donne {attendu} j — {ecart} j d'écart",
                ))

        # 5. Une récolte déduite qui tombe loin de la récolte déclarée.
        if recolte and plantation and plant_recolte:
            deduite = plantation[0] + timedelta(days=plant_recolte)
            ecart = abs((deduite - recolte[0]).days)
            if ecart > 45:
                anomalies.append((
                    "DOUTE", cid,
                    f"récolte déclarée au {recolte[0]:%d/%m}, mais plantation "
                    f"+ {plant_recolte} j donne le {deduite:%d/%m} — {ecart} j "
                    f"d'écart",
                ))

        # 6. Espacement hors de toute plausibilité pour la catégorie.
        mini, maxi = ESPACEMENTS.get(c["categorie"], (1, 2000))
        if not mini <= c["espacement_cm"] <= maxi:
            anomalies.append((
                "DOUTE", cid,
                f"espacement de {c['espacement_cm']} cm hors de la plage "
                f"{mini}–{maxi} attendue pour « {c['categorie']} »",
            ))

        # 6 bis. Fréquence d'arrosage incohérente avec le besoin annoncé.
        eau = c.get("arrosage") or {}
        bornes_eau = FREQUENCES.get(eau.get("besoin"))
        if bornes_eau and not bornes_eau[0] <= eau.get("frequence_jours", 0) <= bornes_eau[1]:
            anomalies.append((
                "DOUTE", cid,
                f"besoin en eau « {eau.get('besoin')} » mais arrosage tous les "
                f"{eau.get('frequence_jours')} j, hors de la plage "
                f"{bornes_eau[0]}–{bornes_eau[1]} j",
            ))

        # 7. Famille botanique incompatible avec la catégorie annoncée.
        attendues = FAMILLES_ATTENDUES.get(c["famille"])
        if attendues and c["categorie"] not in attendues:
            anomalies.append((
                "DOUTE", cid,
                f"{c['famille']} classée « {c['categorie']} », là où on "
                f"attendrait {' ou '.join(sorted(attendues))}",
            ))

        # 8. Une pérenne qui déclare un cycle de semis se contredit.
        if perenne and (semis_recolte or repiquage):
            anomalies.append((
                "DOUTE", cid,
                "pérenne, mais déclare des durées de semis : elle ne se "
                "ressème pas chaque année",
            ))

    return anomalies


def main() -> int:
    anomalies = auditer()
    graves = [a for a in anomalies if a[0] == "GRAVE"]
    doutes = [a for a in anomalies if a[0] == "DOUTE"]
    total = len(cat.charger())

    for titre, lot in (("Impossibles", graves), ("À vérifier", doutes)):
        print(f"\n{titre} — {len(lot)}")
        print("-" * 72)
        for _, cid, texte in lot:
            print(f"  {cid:22} {texte}")

    print(
        f"\n{total} fiches auditées : {len(graves)} impossibles, "
        f"{len(doutes)} douteuses."
    )
    return 1 if graves else 0


if __name__ == "__main__":
    sys.exit(main())
