"""Alerte gel : qui souffrira cette nuit, d'apres la temperature annoncee.

Module volontairement pur : aucun import Home Assistant. Il ne lit pas la
meteo, on la lui donne — c'est ce qui le rend verifiable sans instance.

Le catalogue porte deja tout ce qu'il faut. Chaque fiche declare `rusticite.gel`
— la plante craint-elle le gel — et `rusticite.temp_min_c`, la temperature en
dessous de laquelle elle souffre. Ces deux champs ne servaient jusqu'ici qu'a
l'affichage.

**Le seuil est celui de la plante, pas zero degre.** C'est tout l'interet
d'avoir 215 fiches : un aloe vera souffre a 10 °C et un pommier tient -20 °C,
donc une alerte unique « il gele cette nuit » serait a la fois tardive pour
l'un et inutile pour l'autre. Les 22 plantes d'interieur ont rendu la question
concrete : sorties l'ete, elles se rentrent bien avant la premiere gelee.

Trois garde-fous, pour la meme raison que l'arrosage : un rappel qu'on ignore
discredite tous les autres.

Une plante qui n'est pas en terre ne risque rien — au stade « prevu », elle est
encore un sachet de graines.

Une plante en zone abritee n'est pas concernee. Serre, chassis, veranda : c'est
le sens meme du reglage, et l'alerte le respecte comme l'arrosage le respecte.

Une plante rustique au-dela de la temperature annoncee ne declenche rien, meme
s'il gele. Un poireau a -15 °C n'a pas besoin qu'on le lui dise.
"""

from __future__ import annotations

from .lifecycle import (
    PHASE_EN_RECOLTE,
    PHASE_PLANTE,
    PHASE_SEME,
    phase_depuis_evenements,
)

# Phases pendant lesquelles la plante est dehors et exposee. Identiques a
# celles de l'arrosage, et pour la meme raison : avant, elle n'est pas en
# terre ; apres, il n'y a plus rien a sauver.
PHASES_EXPOSEES = frozenset({PHASE_SEME, PHASE_PLANTE, PHASE_EN_RECOLTE})

# Seuil retenu pour une plante gelive qui ne declare pas sa temperature
# minimale. Zero est le choix prudent : c'est la ou le gel commence.
SEUIL_GELIVE_DEFAUT = 0.0


def seuil_pour(culture: dict) -> float | None:
    """Temperature en dessous de laquelle cette culture souffre, ou None.

    None veut dire « rien a dire » : la fiche se declare rustique sans borne,
    donc aucune temperature annoncee ne justifie une alerte.
    """
    rusticite = culture.get("rusticite") or {}
    minimum = rusticite.get("temp_min_c")
    if minimum is not None:
        try:
            return float(minimum)
        except (TypeError, ValueError):
            return None
    # Pas de minimum declare : seule une fiche gelive a quelque chose a dire,
    # et son seuil est le gel lui-meme.
    return SEUIL_GELIVE_DEFAUT if rusticite.get("gel") is False else None


def menacee(culture: dict, plante: dict, zone: dict, mini_prevu: float) -> bool:
    """Cette plante souffrira-t-elle de la temperature annoncee ?"""
    if zone.get("abritee"):
        return False
    if phase_depuis_evenements(plante.get("evenements") or []) not in PHASES_EXPOSEES:
        return False
    seuil = seuil_pour(culture)
    return seuil is not None and mini_prevu <= seuil


def menacees(entrees, mini_prevu: float) -> list[dict]:
    """Les plantes menacees, de la plus fragile a la plus resistante.

    `entrees` est la vue calculee du coordinateur. L'ordre compte : la
    notification ne cite que les premieres, et ce sont les plus fragiles
    qu'il faut rentrer en premier.
    """
    if mini_prevu is None:
        return []

    retenues = []
    for entree in entrees:
        culture = entree["culture"]
        if not menacee(culture, entree["plante"], entree["zone"], mini_prevu):
            continue
        retenues.append(
            {
                "uid": entree["uid"],
                "nom": entree["nom_affiche"],
                "emoji": culture.get("emoji", "🌱"),
                "zone": entree["zone"].get("nom"),
                "seuil_c": seuil_pour(culture),
                # Une plante d'interieur se rentre ; une tomate se voile. Le
                # geste n'est pas le meme, et la notification le dit.
                "interieur": culture.get("categorie") == "plante-interieur",
            }
        )

    return sorted(retenues, key=lambda p: -p["seuil_c"])
