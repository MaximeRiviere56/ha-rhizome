"""Cycle de vie d'une plante du jardin et journal de ses evenements.

Module volontairement pur : aucun import Home Assistant, pour rester testable
hors instance. Le journal est la source de verite ; la phase s'en deduit
toujours par repli (fold), jamais stockee comme un fait independant. C'est ce
qui rend `annuler_dernier_evenement` fiable.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from typing import Any

# --- Phases -------------------------------------------------------------------

PHASE_PREVU = "prevu"
PHASE_SEME = "seme"
PHASE_PLANTE = "plante"
PHASE_EN_RECOLTE = "en_recolte"
PHASE_TERMINE = "termine"
PHASE_PERDU = "perdu"

PHASES_LIBELLES = {
    PHASE_PREVU: "Prévu",
    PHASE_SEME: "Semé",
    PHASE_PLANTE: "Planté",
    PHASE_EN_RECOLTE: "En récolte",
    PHASE_TERMINE: "Terminé",
    PHASE_PERDU: "Perdu",
}

PHASES_FINALES = frozenset({PHASE_TERMINE, PHASE_PERDU})

# --- Evenements ---------------------------------------------------------------

EVT_SEME = "seme"
EVT_REPIQUE = "repique"
EVT_PLANTE = "plante"
EVT_RECOLTE = "recolte"
EVT_TERMINE = "termine"
EVT_PERDU = "perdu"

TYPES_EVENEMENTS = frozenset(
    {EVT_SEME, EVT_REPIQUE, EVT_PLANTE, EVT_RECOLTE, EVT_TERMINE, EVT_PERDU}
)

MODE_SEMIS_DIRECT = "direct"
MODE_SEMIS_INTERIEUR = "interieur"

# Phases depuis lesquelles chaque evenement est acceptable.
#
# `recolte` est volontairement autorise depuis `seme` : un radis seme en place
# n'est jamais repique, il passe directement du semis a la recolte. Oublier ce
# cas rendrait la moitie du catalogue injournalisable.
TRANSITIONS: dict[str, frozenset[str]] = {
    EVT_SEME: frozenset({PHASE_PREVU}),
    EVT_REPIQUE: frozenset({PHASE_SEME}),
    EVT_PLANTE: frozenset({PHASE_PREVU, PHASE_SEME}),
    EVT_RECOLTE: frozenset({PHASE_SEME, PHASE_PLANTE, PHASE_EN_RECOLTE}),
    EVT_TERMINE: frozenset({PHASE_SEME, PHASE_PLANTE, PHASE_EN_RECOLTE}),
    EVT_PERDU: frozenset({PHASE_SEME, PHASE_PLANTE, PHASE_EN_RECOLTE}),
}

PHASE_APRES: dict[str, str] = {
    EVT_SEME: PHASE_SEME,
    EVT_REPIQUE: PHASE_PLANTE,
    EVT_PLANTE: PHASE_PLANTE,
    EVT_RECOLTE: PHASE_EN_RECOLTE,
    EVT_TERMINE: PHASE_TERMINE,
    EVT_PERDU: PHASE_PERDU,
}

LIBELLES_EVENEMENTS = {
    EVT_SEME: "Semé",
    EVT_REPIQUE: "Repiqué",
    EVT_PLANTE: "Planté",
    EVT_RECOLTE: "Récolté",
    EVT_TERMINE: "Terminé",
    EVT_PERDU: "Perdu",
}


class ErreurJournal(ValueError):
    """Operation refusee sur le journal d'une plante.

    Elle porte toujours son message francais — c'est la langue de reference du
    projet, et ce module reste pur, donc sans acces aux reglages. Elle porte en
    plus, quand il en existe une, la cle de traduction qui permet a la couche
    Home Assistant de rendre le meme refus dans la langue de l'interface. Sans
    cle, le message francais passe tel quel : un refus comprehensible dans la
    mauvaise langue vaut mieux qu'un refus muet.
    """

    def __init__(self, message: str, *, cle: str | None = None, **params: Any) -> None:
        super().__init__(message)
        self.cle = cle
        self.params = params


class TransitionInvalide(ErreurJournal):
    """L'evenement n'a pas de sens depuis la phase courante."""


# --- Utilitaires de date ------------------------------------------------------


def parse_date(valeur: Any) -> date:
    """Accepte une date, un datetime ou une chaine ISO 'AAAA-MM-JJ'."""
    if isinstance(valeur, datetime):
        return valeur.date()
    if isinstance(valeur, date):
        return valeur
    if isinstance(valeur, str):
        try:
            return date.fromisoformat(valeur[:10])
        except ValueError as err:
            raise ErreurJournal(
            f"Date invalide : {valeur!r}", cle="err_date_invalide", valeur=repr(valeur)
        ) from err
    raise ErreurJournal(
        f"Date invalide : {valeur!r}", cle="err_date_invalide", valeur=repr(valeur)
    )


def fmt_date(valeur: date) -> str:
    return valeur.isoformat()


# --- Lecture du journal -------------------------------------------------------


def phase_depuis_evenements(evenements: Iterable[dict]) -> str:
    """Replie le journal en une phase. L'ordre d'insertion fait foi."""
    phase = PHASE_PREVU
    for evt in evenements:
        suivante = PHASE_APRES.get(evt.get("type") or "")
        if suivante is not None:
            phase = suivante
    return phase


def dernier_evenement(evenements: Iterable[dict], type_evt: str) -> dict | None:
    """Dernier evenement du type demande, ou None."""
    trouve = None
    for evt in evenements:
        if evt.get("type") == type_evt:
            trouve = evt
    return trouve


def date_evenement(evenements: Iterable[dict], type_evt: str) -> date | None:
    evt = dernier_evenement(evenements, type_evt)
    if evt is None:
        return None
    return parse_date(evt["date"])


def date_mise_en_place(evenements: Iterable[dict]) -> date | None:
    """Date a laquelle la plante a rejoint sa place definitive.

    Un repiquage ou une plantation, selon ce qui s'est produit. Sert de point
    de depart au calcul de la recolte.
    """
    evenements = list(evenements)
    for type_evt in (EVT_REPIQUE, EVT_PLANTE):
        trouvee = date_evenement(evenements, type_evt)
        if trouvee is not None:
            return trouvee
    return None


def mode_semis(evenements: Iterable[dict]) -> str | None:
    """'direct' ou 'interieur' tel qu'enregistre lors du semis."""
    evt = dernier_evenement(evenements, EVT_SEME)
    if evt is None:
        return None
    return evt.get("mode") or MODE_SEMIS_DIRECT


def recoltes(evenements: Iterable[dict]) -> list[dict]:
    return [evt for evt in evenements if evt.get("type") == EVT_RECOLTE]


def total_recolte_saison_g(evenements: Iterable[dict], annee: int) -> int:
    """Recoltes de l'annee demandee, en grammes.

    Un total cumule depuis toujours ne dit plus rien des la deuxieme saison,
    et empeche de comparer une annee a la precedente.
    """
    return sum(
        int(evt.get("quantite_g") or 0)
        for evt in recoltes(evenements)
        if str(evt.get("date", ""))[:4] == str(annee)
    )


def total_recolte_g(evenements: Iterable[dict]) -> int:
    """Somme des quantites recoltees, en grammes. Les recoltes non pesees
    comptent pour zero mais restent au journal."""
    total = 0
    for evt in recoltes(evenements):
        quantite = evt.get("quantite_g")
        if isinstance(quantite, (int, float)):
            total += int(quantite)
    return total


# --- Ecriture du journal ------------------------------------------------------


def valider_transition(phase: str, type_evt: str) -> None:
    if type_evt not in TYPES_EVENEMENTS:
        raise ErreurJournal(
            f"Type d'événement inconnu : {type_evt!r}",
            cle="err_type_evenement",
            type=repr(type_evt),
        )
    autorisees = TRANSITIONS[type_evt]
    if phase not in autorisees:
        # Les deux libelles partent en cles et non en texte : le rendu les
        # traduit avec le reste du message, sinon un refus anglais citerait
        # « Semé » et « En récolte » en plein milieu.
        raise TransitionInvalide(
            f"Impossible d'enregistrer '{LIBELLES_EVENEMENTS[type_evt]}' "
            f"depuis la phase '{PHASES_LIBELLES.get(phase, phase)}'.",
            cle="err_transition",
            evenement=type_evt,
            phase=phase,
        )


def construire_evenement(
    type_evt: str,
    jour: Any,
    *,
    quantite_g: int | None = None,
    cause: str | None = None,
    note: str | None = None,
    mode: str | None = None,
) -> dict:
    evt: dict[str, Any] = {"type": type_evt, "date": fmt_date(parse_date(jour))}
    if type_evt == EVT_SEME:
        evt["mode"] = mode or MODE_SEMIS_DIRECT
    if quantite_g is not None:
        quantite = int(quantite_g)
        if quantite < 0:
            raise ErreurJournal(
                "Une quantité récoltée ne peut pas être négative.",
                cle="err_quantite_negative",
            )
        evt["quantite_g"] = quantite
    if cause:
        evt["cause"] = cause
    if note:
        evt["note"] = note
    return evt


def ajouter_evenement(plante: dict, evt: dict) -> dict:
    """Ajoute un evenement au journal apres validation. Mute `plante`."""
    evenements = plante.setdefault("evenements", [])
    phase = phase_depuis_evenements(evenements)
    valider_transition(phase, evt["type"])
    evenements.append(evt)
    plante["phase"] = phase_depuis_evenements(evenements)
    return plante


def annuler_dernier_evenement(plante: dict) -> dict | None:
    """Retire le dernier evenement et recalcule la phase.

    Renvoie l'evenement retire, ou None si le journal etait vide.
    """
    evenements = plante.get("evenements") or []
    if not evenements:
        return None
    retire = evenements.pop()
    plante["phase"] = phase_depuis_evenements(evenements)
    return retire


def resume(plante: dict) -> dict:
    """Vue agregee du journal, pour les attributs d'entite et le panneau."""
    evenements = plante.get("evenements") or []
    liste_recoltes = recoltes(evenements)
    return {
        "phase": phase_depuis_evenements(evenements),
        "date_semis": date_evenement(evenements, EVT_SEME),
        "date_mise_en_place": date_mise_en_place(evenements),
        "mode_semis": mode_semis(evenements),
        "nb_recoltes": len(liste_recoltes),
        "total_recolte_g": total_recolte_g(evenements),
        "derniere_recolte": (
            parse_date(liste_recoltes[-1]["date"]) if liste_recoltes else None
        ),
        "nb_evenements": len(evenements),
    }
