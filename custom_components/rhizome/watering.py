"""Arrosage : à quelle fréquence, et depuis quand.

Module volontairement pur : aucun import Home Assistant.

Le modèle est théorique et assumé comme tel. La fiche donne une fréquence,
et le compte à rebours repart du moment où vous dites avoir arrosé. Rien
n'observe le sol, la pluie ni la température : si vous décidez de ne pas
arroser, c'est votre affaire, l'application se contente de rappeler.

Trois règles bornent les rappels, pour qu'ils restent crédibles.

Une plante qui n'est pas en terre ne s'arrose pas — tant qu'elle est au stade
« prévu », ou une fois terminée, elle ne réclame rien.

Une pérenne sobre et installée se débrouille seule. Un pommier en place depuis
deux ans n'a plus besoin qu'on l'arrose, et les fiches le disent elles-mêmes :
« aucun arrosage une fois établi ».

Un semis boit deux fois plus souvent qu'un plant installé : la graine est en
surface et ne pardonne pas un dessèchement.

En pleine terre l'hiver, on n'arrose pas. Entre la première et la dernière
gelée, aucun rappel pour les zones découvertes. Les zones abritées — serre,
châssis, pots — continuent, elles sèchent toute l'année.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .lifecycle import (
    EVT_SEME,
    PHASE_EN_RECOLTE,
    PHASE_PLANTE,
    PHASE_SEME,
    date_evenement,
    date_mise_en_place,
    parse_date,
    phase_depuis_evenements,
)

# Phases pendant lesquelles la plante occupe le terrain et boit.
PHASES_ARROSABLES = frozenset({PHASE_SEME, PHASE_PLANTE, PHASE_EN_RECOLTE})

# Un semis boit deux fois plus souvent qu'un plant installé.
FACTEUR_SEMIS = 0.5

# Soixante entrées suffisent à l'affichage et au calcul ; les garder toutes
# gonflerait le stockage saison après saison.
HISTORIQUE_MAX = 60

# Au-delà, une pérenne à faible besoin en eau est considérée comme installée :
# ses racines vont chercher seules, et les fiches le disent explicitement.
JOURS_PERENNE_INSTALLEE = 730


@dataclass(frozen=True)
class EtatArrosage:
    """Ce qu'il faut savoir de l'arrosage d'une plante, à une date donnée."""

    concernee: bool
    dernier: date | None
    prochain: date | None
    frequence_jours: int | None
    jours_restants: int | None
    motif_exclusion: str | None = None
    # Cle de traduction du motif ci-dessus. Le module reste pur : il ne sait
    # pas dans quelle langue l'interface parle, mais il sait de quel motif il
    # s'agit. La couche de presentation traduit depuis cette cle, et retombe
    # sur le texte francais quand elle est absente.
    motif_cle: str | None = None

    @property
    def en_retard(self) -> bool:
        return self.jours_restants is not None and self.jours_restants < 0

    @property
    def a_arroser(self) -> bool:
        return self.jours_restants is not None and self.jours_restants <= 0


# Un arrosage s'espace de quelques jours à une saison. Au-delà, la valeur ne
# décrit plus un besoin en eau : elle vient d'une saisie aberrante ou d'un
# stockage édité à la main, et `date + timedelta(jours)` y déborde — ce qui
# mettait le coordinateur en panne à chaque cycle, de façon persistante.
FREQUENCE_MAX_JOURS = 365


def frequence_pour(culture: dict, plante: dict) -> int:
    """Nombre de jours entre deux arrosages. Le réglage de la plante prime."""
    propre = plante.get("arrosage_frequence_jours")
    if propre:
        return _borner(propre)
    base = (culture.get("arrosage") or {}).get("frequence_jours") or 4
    return _borner(base)


def _borner(valeur) -> int:
    """Ramène une fréquence dans l'intervalle où elle a un sens."""
    try:
        jours = int(valeur)
    except (TypeError, ValueError):
        return 4
    return max(1, min(FREQUENCE_MAX_JOURS, jours))


def dernier_arrosage(plante: dict) -> dict | None:
    liste = plante.get("arrosages") or []
    return max(liste, key=lambda a: a["date"]) if liste else None


def _jour_mois(repere: str, annee: int) -> date:
    mois, jour = (int(part) for part in repere.split("-", 1))
    while jour > 1:
        try:
            return date(annee, mois, jour)
        except ValueError:
            jour -= 1
    return date(annee, mois, 1)


def _dans_la_periode_de_gel(jour: date, gelees) -> bool:
    """Vrai entre la première gelée d'automne et la dernière de printemps."""
    return (
        jour >= _jour_mois(gelees.premiere, jour.year)
        or jour <= _jour_mois(gelees.derniere, jour.year)
    )


def _perenne_installee(culture: dict, evenements: list, aujourdhui: date) -> bool:
    """Une pérenne sobre, en place depuis plus de deux ans, n'attend rien."""
    if not culture.get("perenne"):
        return False
    if (culture.get("arrosage") or {}).get("besoin") != "faible":
        return False
    depuis = date_mise_en_place(evenements) or date_evenement(evenements, EVT_SEME)
    if depuis is None:
        return False
    return (aujourdhui - depuis).days >= JOURS_PERENNE_INSTALLEE


def etat(
    culture: dict,
    plante: dict,
    zone: dict,
    gelees,
    aujourdhui: date | None = None,
) -> EtatArrosage:
    """Où en est l'arrosage de cette plante."""
    aujourdhui = aujourdhui or date.today()
    evenements = plante.get("evenements") or []
    phase = phase_depuis_evenements(evenements)
    dernier = dernier_arrosage(plante)

    def exclue(motif: str, cle: str) -> EtatArrosage:
        return EtatArrosage(
            concernee=False,
            dernier=parse_date(dernier["date"]) if dernier else None,
            prochain=None,
            frequence_jours=None,
            jours_restants=None,
            motif_exclusion=motif,
            motif_cle=cle,
        )

    if not plante.get("arrosage_actif", True):
        return exclue(
            "Rappels d'arrosage désactivés pour cette plante.",
            "eau_exclu_desactive",
        )
    if phase not in PHASES_ARROSABLES:
        return exclue(
            "Pas encore en terre, ou culture terminée.", "eau_exclu_pas_en_terre"
        )
    if not zone.get("abritee") and _dans_la_periode_de_gel(aujourdhui, gelees):
        return exclue(
            "En pleine terre l'hiver, la nature s'en charge.", "eau_exclu_hiver"
        )

    if _perenne_installee(culture, evenements, aujourdhui):
        return exclue(
            "Pérenne installée et peu gourmande : elle se débrouille seule.",
            "eau_exclu_perenne",
        )

    frequence = frequence_pour(culture, plante)
    if phase == PHASE_SEME:
        frequence = max(1, round(frequence * FACTEUR_SEMIS))

    if dernier is not None:
        prochain = parse_date(dernier["date"]) + timedelta(days=frequence)
    else:
        # Jamais arrosée : on ne sait rien, donc c'est dû maintenant. Compter
        # depuis la mise en terre afficherait un retard de plusieurs centaines
        # de jours pour un arbre planté il y a deux ans, ce qui ne veut rien
        # dire et décrédibilise la liste entière.
        prochain = aujourdhui
    return EtatArrosage(
        concernee=True,
        dernier=parse_date(dernier["date"]) if dernier else None,
        prochain=prochain,
        frequence_jours=frequence,
        jours_restants=(prochain - aujourdhui).days,
    )


def construire_arrosage(jour, note: str | None = None) -> dict:
    entree = {"date": parse_date(jour).isoformat()}
    if note:
        entree["note"] = note
    return entree


def noter_arrosage(plante: dict, entree: dict) -> dict:
    """Ajoute un arrosage, en bornant l'historique."""
    liste = plante.setdefault("arrosages", [])
    liste.append(entree)
    liste.sort(key=lambda a: a["date"])
    if len(liste) > HISTORIQUE_MAX:
        del liste[: len(liste) - HISTORIQUE_MAX]
    return entree
