"""Calcul des etapes culturales : fenetres theoriques et dates recalculees.

Module volontairement pur : aucun import Home Assistant.

Deux regles gouvernent tout ce fichier.

1. Un fait gagne toujours sur une moyenne. Des qu'une date reelle est au
   journal, les etapes suivantes s'enchainent depuis elle, en jours, et la
   fenetre saisonniere theorique est ignoree. Semer trois semaines en retard
   decale la recolte d'autant.
2. Une date reelle ne subit jamais le decalage de zone. Le decalage de zone
   (une serre prend trois semaines d'avance) est une prevision ; il n'a aucun
   sens applique a ce qui s'est deja produit.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta

from .lifecycle import (
    EVT_SEME,
    MODE_SEMIS_INTERIEUR,
    PHASE_EN_RECOLTE,
    PHASE_PLANTE,
    PHASE_PREVU,
    PHASE_SEME,
    PHASES_FINALES,
    date_evenement,
    date_mise_en_place,
    mode_semis,
    parse_date,
    phase_depuis_evenements,
    recoltes,
)

# --- Types d'etapes -----------------------------------------------------------

ETAPE_SEMIS_INTERIEUR = "semis_interieur"
ETAPE_SEMIS_DIRECT = "semis_direct"
ETAPE_REPIQUAGE = "repiquage"
ETAPE_PLANTATION = "plantation"
ETAPE_RECOLTE = "recolte"
ETAPE_RESSEMER = "ressemer"

LIBELLES_ETAPES = {
    ETAPE_SEMIS_INTERIEUR: "Semer à l'abri",
    ETAPE_SEMIS_DIRECT: "Semer en place",
    ETAPE_REPIQUAGE: "Repiquer",
    ETAPE_PLANTATION: "Planter",
    ETAPE_RECOLTE: "Récolter",
    ETAPE_RESSEMER: "Ressemer",
}

# Ordre canonique d'affichage quand deux etapes tombent le meme jour.
ORDRE_ETAPES = [
    ETAPE_SEMIS_INTERIEUR,
    ETAPE_SEMIS_DIRECT,
    ETAPE_REPIQUAGE,
    ETAPE_PLANTATION,
    ETAPE_RESSEMER,
    ETAPE_RECOLTE,
]

SOURCE_REELLE = "reel"
SOURCE_PREVUE = "prevu"

ANCRAGE_GELEES_DERNIERE = "gelees_derniere"
ANCRAGE_GELEES_PREMIERE = "gelees_premiere"
ANCRAGE_DATE_FIXE = "date_fixe"

# Largeur par defaut d'une fenetre deduite d'un enchainement en jours.
DUREE_FENETRE_DEFAUT = 14


@dataclass(frozen=True)
class Gelees:
    """Reperes climatiques locaux, au format 'MM-JJ'."""

    derniere: str = "04-15"
    premiere: str = "11-15"


@dataclass(frozen=True)
class Etape:
    """Une action a mener, sur une fenetre de temps."""

    type: str
    debut: date
    fin: date
    source: str = SOURCE_PREVUE

    @property
    def libelle(self) -> str:
        return LIBELLES_ETAPES.get(self.type, self.type)

    @property
    def reelle(self) -> bool:
        return self.source == SOURCE_REELLE

    def contient(self, jour: date) -> bool:
        return self.debut <= jour <= self.fin

    def jours_restants(self, jour: date) -> int:
        """Negatif si la fenetre est deja ouverte, 0 le jour d'ouverture."""
        return (self.debut - jour).days


class CatalogueInvalide(ValueError):
    """La fiche de culture ne permet pas de calculer ses etapes."""


# --- Resolution des fenetres theoriques ---------------------------------------


def _jour_mois(repere: str, annee: int) -> date:
    """'MM-JJ' + annee -> date, en tolerant le 29 fevrier des annees communes."""
    try:
        mois, jour = (int(part) for part in repere.split("-", 1))
    except (ValueError, AttributeError) as err:
        raise CatalogueInvalide(f"Repere de date invalide : {repere!r}") from err
    while jour > 1:
        try:
            return date(annee, mois, jour)
        except ValueError:
            jour -= 1
    return date(annee, mois, 1)


def resoudre_fenetre(
    fenetre: dict,
    gelees: Gelees,
    annee: int,
    decalage_zone: int = 0,
) -> tuple[date, date]:
    """Transforme une fenetre du catalogue en dates concretes."""
    ancrage = fenetre.get("ancrage", ANCRAGE_DATE_FIXE)
    if ancrage == ANCRAGE_GELEES_DERNIERE:
        pivot = _jour_mois(gelees.derniere, annee)
    elif ancrage == ANCRAGE_GELEES_PREMIERE:
        pivot = _jour_mois(gelees.premiere, annee)
    elif ancrage == ANCRAGE_DATE_FIXE:
        repere = fenetre.get("date")
        if not repere:
            raise CatalogueInvalide("Une fenetre 'date_fixe' doit porter une 'date'.")
        pivot = _jour_mois(repere, annee)
    else:
        raise CatalogueInvalide(f"Ancrage inconnu : {ancrage!r}")

    debut = pivot + timedelta(days=int(fenetre.get("offset_jours", 0)) + decalage_zone)
    duree = int(fenetre.get("duree_jours", DUREE_FENETRE_DEFAUT))
    return debut, debut + timedelta(days=max(duree, 0))


def _cycle(culture: dict) -> dict:
    return culture.get("cycle") or {}


def premier_gel_apres(reference: date, gelees: Gelees) -> date:
    """Premiere gelee d'automne a survenir a partir de `reference`.

    Le repere doit etre la saison de culture, jamais l'annee civile de la
    fenetre calculee : une recolte qui deborde sur janvier appartient encore a
    la saison precedente, et c'est la gelee de CETTE saison qui tuera le plant.
    """
    gel = _jour_mois(gelees.premiere, reference.year)
    if gel < reference:
        gel = _jour_mois(gelees.premiere, reference.year + 1)
    return gel


def caper_au_gel(
    etape: Etape, culture: dict, gelees: Gelees, reference: date | None = None
) -> Etape | None:
    """Raccourcit une fenetre de recolte a la premiere gelee, si besoin.

    Une courgette ne se recolte pas en janvier : elle a gele en novembre. Sans
    ce plafond, une duree de recolte de 90 jours comptee depuis une plantation
    tardive promet des legumes bien apres la mort du plant — et declencherait
    un rappel absurde en plein hiver.

    `reference` est le moment ou la plante occupe le terrain (semis ou mise en
    place). Il determine quelle gelee compte. Sans lui on retomberait sur
    l'annee de la fenetre, ce qui choisit une gelee d'un an trop tard des que
    la recolte franchit le 1er janvier.

    Renvoie None quand la fenetre entiere tombe apres la gelee : la culture
    n'aura pas le temps, et promettre une recolte serait un mensonge.

    Seules les cultures declarees gelives sont concernees ; poireaux, choux et
    arbres fruitiers traversent l'hiver sans y prendre garde.
    """
    if etape.type != ETAPE_RECOLTE:
        return etape
    if (culture.get("rusticite") or {}).get("gel", True):
        return etape

    gel = premier_gel_apres(reference or etape.debut, gelees)
    if etape.fin <= gel:
        return etape
    if etape.debut >= gel:
        return None
    return replace(etape, fin=gel)


def fenetres_theoriques(
    culture: dict,
    gelees: Gelees,
    decalage_zone: int = 0,
    annee: int | None = None,
) -> list[Etape]:
    """Fenetres saisonnieres d'une culture pour une annee donnee.

    La fenetre de recolte est deduite de la plantation quand le catalogue ne la
    declare pas explicitement. Les perennes (arbres, petits fruits) la declarent
    toujours : chez elles la recolte revient chaque annee sans nouveau semis.
    """
    annee = annee or date.today().year
    fenetres = culture.get("fenetres") or {}
    cycle = _cycle(culture)
    etapes: list[Etape] = []

    for type_etape in (
        ETAPE_SEMIS_INTERIEUR,
        ETAPE_SEMIS_DIRECT,
        ETAPE_PLANTATION,
    ):
        brute = fenetres.get(type_etape)
        if brute:
            debut, fin = resoudre_fenetre(brute, gelees, annee, decalage_zone)
            etapes.append(Etape(type_etape, debut, fin, SOURCE_PREVUE))

    # La reference du plafond de gel : le moment ou la plante occupe le
    # terrain, et non l'annee civile de la recolte.
    reference = _debut_occupation(etapes)

    recolte_brute = fenetres.get(ETAPE_RECOLTE)
    if recolte_brute:
        debut, fin = resoudre_fenetre(recolte_brute, gelees, annee, decalage_zone)
        brute = Etape(ETAPE_RECOLTE, debut, fin, SOURCE_PREVUE)
    else:
        brute = _recolte_deduite(etapes, cycle)

    if brute is not None:
        capee = caper_au_gel(brute, culture, gelees, reference)
        if capee is not None:
            etapes.append(capee)

    return trier(etapes)


def _debut_occupation(etapes: list[Etape]) -> date | None:
    """Date a laquelle la plante prend sa place au jardin."""
    par_type = {etape.type: etape for etape in etapes}
    for type_etape in (ETAPE_PLANTATION, ETAPE_SEMIS_DIRECT, ETAPE_SEMIS_INTERIEUR):
        etape = par_type.get(type_etape)
        if etape is not None:
            return etape.debut
    return None


def _recolte_deduite(etapes: list[Etape], cycle: dict) -> Etape | None:
    """Recolte calculee depuis la plantation, a defaut depuis le semis direct."""
    duree = int(cycle.get("duree_recolte_jours", DUREE_FENETRE_DEFAUT))
    par_type = {etape.type: etape for etape in etapes}

    plantation = par_type.get(ETAPE_PLANTATION)
    jours_plantation = cycle.get("jours_plantation_a_recolte")
    if plantation is not None and jours_plantation:
        debut = plantation.debut + timedelta(days=int(jours_plantation))
        return Etape(ETAPE_RECOLTE, debut, debut + timedelta(days=duree), SOURCE_PREVUE)

    semis = par_type.get(ETAPE_SEMIS_DIRECT) or par_type.get(ETAPE_SEMIS_INTERIEUR)
    jours_semis = cycle.get("jours_semis_a_recolte")
    if semis is not None and jours_semis:
        debut = semis.debut + timedelta(days=int(jours_semis))
        return Etape(ETAPE_RECOLTE, debut, debut + timedelta(days=duree), SOURCE_PREVUE)

    return None


# --- Etapes recalculees depuis le journal -------------------------------------


def _chaine_depuis_semis(
    culture: dict, jour_semis: date, direct: bool, gelees: Gelees
) -> list[Etape]:
    cycle = _cycle(culture)
    duree_recolte = int(cycle.get("duree_recolte_jours", DUREE_FENETRE_DEFAUT))
    etapes: list[Etape] = []

    jours_repiquage = cycle.get("jours_semis_a_repiquage")
    if not direct and jours_repiquage:
        debut_repiquage = jour_semis + timedelta(days=int(jours_repiquage))
        etapes.append(
            Etape(
                ETAPE_REPIQUAGE,
                debut_repiquage,
                debut_repiquage + timedelta(days=DUREE_FENETRE_DEFAUT),
                SOURCE_REELLE,
            )
        )
        jours_recolte = cycle.get("jours_plantation_a_recolte")
        if jours_recolte:
            debut_recolte = debut_repiquage + timedelta(days=int(jours_recolte))
            capee = caper_au_gel(
                Etape(
                    ETAPE_RECOLTE,
                    debut_recolte,
                    debut_recolte + timedelta(days=duree_recolte),
                    SOURCE_REELLE,
                ),
                culture,
                gelees,
                jour_semis,
            )
            if capee is not None:
                etapes.append(capee)
        return etapes

    # Semis en place : on va du semis a la recolte sans repiquage.
    jours_recolte = cycle.get("jours_semis_a_recolte") or cycle.get(
        "jours_plantation_a_recolte"
    )
    if jours_recolte:
        debut_recolte = jour_semis + timedelta(days=int(jours_recolte))
        capee = caper_au_gel(
            Etape(
                ETAPE_RECOLTE,
                debut_recolte,
                debut_recolte + timedelta(days=duree_recolte),
                SOURCE_REELLE,
            ),
            culture,
            gelees,
            jour_semis,
        )
        if capee is not None:
            etapes.append(capee)
    return etapes


def _chaine_depuis_mise_en_place(
    culture: dict, jour: date, gelees: Gelees
) -> list[Etape]:
    cycle = _cycle(culture)
    jours_recolte = cycle.get("jours_plantation_a_recolte")
    if not jours_recolte:
        return []
    duree = int(cycle.get("duree_recolte_jours", DUREE_FENETRE_DEFAUT))
    debut = jour + timedelta(days=int(jours_recolte))
    capee = caper_au_gel(
        Etape(ETAPE_RECOLTE, debut, debut + timedelta(days=duree), SOURCE_REELLE),
        culture,
        gelees,
        jour,
    )
    return [capee] if capee is not None else []


def prochaines_etapes(
    culture: dict,
    plante: dict,
    gelees: Gelees,
    decalage_zone: int = 0,
    aujourdhui: date | None = None,
) -> list[Etape]:
    """Etapes a venir ou en cours, triees, la plus urgente d'abord.

    Les fenetres deja fermees sont ecartees. Pour une plante encore au stade
    'prevu' on produit l'annee en cours et la suivante : sans cela un potager
    consulte en decembre n'afficherait plus rien.
    """
    aujourdhui = aujourdhui or date.today()
    evenements = plante.get("evenements") or []
    phase = phase_depuis_evenements(evenements)

    if phase in PHASES_FINALES:
        return []

    perenne = bool(culture.get("perenne"))

    if phase == PHASE_PREVU:
        etapes = fenetres_theoriques(
            culture, gelees, decalage_zone, aujourdhui.year
        ) + fenetres_theoriques(culture, gelees, decalage_zone, aujourdhui.year + 1)
        return _a_venir(etapes, aujourdhui)

    if perenne:
        # Un pommier plante ne se resseme pas : sa recolte revient chaque annee
        # sur sa fenetre saisonniere, et seule la recolte nous interesse encore.
        etapes = [
            etape
            for annee in (aujourdhui.year, aujourdhui.year + 1)
            for etape in fenetres_theoriques(culture, gelees, decalage_zone, annee)
            if etape.type == ETAPE_RECOLTE
        ]
        return _a_venir(etapes, aujourdhui)

    if phase == PHASE_SEME:
        jour_semis = date_evenement(evenements, EVT_SEME)
        if jour_semis is None:
            # La phase se deduit du journal : « seme » implique un evenement
            # de semis. Garde defensive, pour un journal edite a la main.
            return []
        direct = mode_semis(evenements) != MODE_SEMIS_INTERIEUR
        etapes = _chaine_depuis_semis(culture, jour_semis, direct, gelees)
        etapes += _etape_echelonnement(
            culture, plante, jour_semis, gelees, decalage_zone
        )
        return _a_venir(etapes, aujourdhui)

    if phase == PHASE_PLANTE:
        jour = date_mise_en_place(evenements)
        if jour is None:
            return []
        return _a_venir(
            _chaine_depuis_mise_en_place(culture, jour, gelees), aujourdhui
        )

    if phase == PHASE_EN_RECOLTE:
        # La recolte a commence : la fenetre court depuis la premiere recolte
        # reelle, et c'est elle qu'on continue d'afficher.
        premiere = parse_date(recoltes(evenements)[0]["date"])
        duree = int(_cycle(culture).get("duree_recolte_jours", DUREE_FENETRE_DEFAUT))
        en_cours = caper_au_gel(
            Etape(
                ETAPE_RECOLTE,
                premiere,
                premiere + timedelta(days=duree),
                SOURCE_REELLE,
            ),
            culture,
            gelees,
            premiere,
        )
        if en_cours is None or en_cours.fin < aujourdhui:
            return []
        return [en_cours]

    return []


def _etape_echelonnement(
    culture: dict,
    plante: dict,
    jour_semis: date,
    gelees: Gelees,
    decalage_zone: int,
) -> list[Etape]:
    """Le prochain semis d'une serie echelonnee.

    Semer des radis tous les quinze jours est le geste le plus repetitif d'un
    potager, et celui qu'on oublie le plus surement. L'etape n'est proposee
    que tant que la fenetre de semis reste ouverte : rien ne sert de reclamer
    un semis de radis en decembre.
    """
    intervalle = plante.get("echelonnement_jours")
    if not intervalle:
        return []

    prochain = jour_semis + timedelta(days=int(intervalle))

    # La fenetre de semis de l'annee concernee borne la serie.
    fenetres = [
        etape
        for etape in fenetres_theoriques(
            culture, gelees, decalage_zone, prochain.year
        )
        if etape.type in (ETAPE_SEMIS_DIRECT, ETAPE_SEMIS_INTERIEUR)
    ]
    if not fenetres or prochain > max(f.fin for f in fenetres):
        return []

    return [
        Etape(
            ETAPE_RESSEMER,
            prochain,
            prochain + timedelta(days=DUREE_FENETRE_DEFAUT),
            SOURCE_REELLE,
        )
    ]


def prochaine_etape(
    culture: dict,
    plante: dict,
    gelees: Gelees,
    decalage_zone: int = 0,
    aujourdhui: date | None = None,
) -> Etape | None:
    etapes = prochaines_etapes(culture, plante, gelees, decalage_zone, aujourdhui)
    return etapes[0] if etapes else None


def etapes_reelles(plante: dict) -> list[tuple[str, date]]:
    """Les faits du journal, pour l'historique du calendrier."""
    faits: list[tuple[str, date]] = []
    for evt in plante.get("evenements") or []:
        type_evt = evt.get("type")
        if type_evt:
            faits.append((type_evt, parse_date(evt["date"])))
    return faits


# --- Tri et filtrage ----------------------------------------------------------


def trier(etapes: list[Etape]) -> list[Etape]:
    ordre = {type_etape: rang for rang, type_etape in enumerate(ORDRE_ETAPES)}
    return sorted(etapes, key=lambda e: (e.debut, ordre.get(e.type, 99)))


def _a_venir(etapes: list[Etape], aujourdhui: date) -> list[Etape]:
    return trier([etape for etape in etapes if etape.fin >= aujourdhui])
