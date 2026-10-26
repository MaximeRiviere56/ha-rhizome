"""Chargement et interrogation du catalogue de cultures."""

from __future__ import annotations

from functools import lru_cache
import json
import logging
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

CHEMIN_CATALOGUE = Path(__file__).parent / "data" / "catalog.json"


@lru_cache(maxsize=1)
def charger() -> dict[str, dict]:
    """Catalogue indexe par id. Lu une seule fois, le fichier est fige."""
    try:
        charge = json.loads(CHEMIN_CATALOGUE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _LOGGER.exception("Catalogue illisible : %s", CHEMIN_CATALOGUE)
        return {}
    return {culture["id"]: culture for culture in charge.get("cultures", [])}


# Champs du catalogue qui s'affichent et se traduisent donc. Les autres sont
# soit des nombres, soit des identifiants, soit du latin.
#
# Les valeurs d'origine sont celles du catalogue francais et le restent : la
# famille commande le delai de rotation (`rotation.DELAIS` s'indexe dessus), et
# un nom francais est l'identite d'une fiche aux yeux de l'utilisateur qui l'a
# corrigee. La traduction vit a cote, suffixee par la langue.
CHAMPS_TRADUITS = ("nom", "famille", "sol", "conseils")

# Les suffixes de traduction reconnus, pour pouvoir les retirer des fiches
# servies au panneau : un `conseils_en` de plus par fiche doublerait la taille
# du catalogue sur le fil pour une donnee que personne ne lit la.
SUFFIXES_TRADUCTION = ("_en",)


def localiser(fiche: dict, langue: str) -> dict:
    """La fiche telle qu'elle doit s'afficher dans cette langue.

    Une fiche personnelle n'a pas de traduction : elle s'affiche telle que son
    auteur l'a ecrite, quelle que soit la langue de l'interface. C'est le bon
    comportement — personne n'attend que « Chou-rave de ma grand-mere » soit
    traduit — et c'est le seul possible : rien ne peut la traduire.
    """
    suffixe = f"_{langue}"
    traduit = dict(fiche)
    if langue != "fr":
        for champ in CHAMPS_TRADUITS:
            valeur = fiche.get(f"{champ}{suffixe}")
            if valeur:
                traduit[champ] = valeur
        arrosage = fiche.get("arrosage") or {}
        notes = arrosage.get(f"notes{suffixe}")
        if notes:
            traduit["arrosage"] = {**arrosage, "notes": notes}

    for cle in list(traduit):
        if cle.endswith(SUFFIXES_TRADUCTION):
            del traduit[cle]
    arrosage = traduit.get("arrosage")
    if isinstance(arrosage, dict) and any(
        cle.endswith(SUFFIXES_TRADUCTION) for cle in arrosage
    ):
        traduit["arrosage"] = {
            cle: valeur
            for cle, valeur in arrosage.items()
            if not cle.endswith(SUFFIXES_TRADUCTION)
        }
    return traduit


def nom_localise(fiche: dict, langue: str) -> str:
    """Le nom d'affichage, sans recopier toute la fiche."""
    if langue == "fr":
        return str(fiche["nom"])
    return str(fiche.get(f"nom_{langue}") or fiche["nom"])


def culture(culture_id: str) -> dict | None:
    return charger().get(culture_id)


def toutes(langue: str = "fr") -> list[dict]:
    """Toutes les fiches, triees par le nom tel qu'il s'affichera.

    Trier sur le nom francais quand l'interface est anglaise donnerait un
    catalogue dans un ordre apparemment aleatoire : « Leek » entre « Poireau »
    et « Poirée ».
    """
    return sorted(charger().values(), key=lambda c: nom_localise(c, langue))


def categories() -> list[str]:
    return sorted({c["categorie"] for c in charger().values()})


def familles() -> list[str]:
    return sorted({c["famille"] for c in charger().values()})


def _sans_accents(texte: str) -> str:
    """Pour que 'poireau' trouve 'Poirée' et que 'oeillet' trouve 'Œillet'."""
    remplacements = str.maketrans(
        "àâäéèêëîïôöùûüÿçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇ", "aaaeeeeiioouuuycAAAEEEEIIOOUUUYC"
    )
    return texte.translate(remplacements).replace("œ", "oe").replace("Œ", "OE").lower()


def rechercher(
    requete: str = "",
    *,
    categorie: str | None = None,
    exposition: str | None = None,
    difficulte_max: int | None = None,
    perenne: bool | None = None,
) -> list[dict]:
    """Recherche texte libre et filtres, cumulables."""
    resultats = toutes()

    if requete:
        terme = _sans_accents(requete.strip())
        resultats = [c for c in resultats if _correspond(c, terme)]
    if categorie:
        resultats = [c for c in resultats if c["categorie"] == categorie]
    if exposition:
        resultats = [c for c in resultats if c["exposition"] == exposition]
    if difficulte_max is not None:
        resultats = [c for c in resultats if c["difficulte"] <= difficulte_max]
    if perenne is not None:
        resultats = [c for c in resultats if bool(c.get("perenne")) is perenne]

    return resultats


def _correspond(fiche: dict, terme: str) -> bool:
    """Le terme cherche apparait-il dans un des noms de cette fiche ?

    On cherche dans les deux langues sans se demander laquelle est affichee :
    « courgette » doit trouver la courgette meme sur une interface anglaise,
    et « zucchini » doit la trouver sur une interface francaise. Le nom latin
    sert de pont pour qui le connait.
    """
    champs = [
        fiche.get("nom"),
        fiche.get("nom_scientifique"),
        fiche.get("famille"),
        *(fiche.get(f"nom{suffixe}") for suffixe in SUFFIXES_TRADUCTION),
        *(fiche.get(f"famille{suffixe}") for suffixe in SUFFIXES_TRADUCTION),
    ]
    return any(champ and terme in _sans_accents(champ) for champ in champs)


def compagnes(culture_id: str) -> dict[str, list[dict]]:
    """Fiches completes des compagnes, pour l'affichage de la fiche."""
    fiche = culture(culture_id)
    if not fiche:
        return {"aime": [], "evite": []}
    index = charger()
    return {
        cle: [index[autre] for autre in fiche["associations"][cle] if autre in index]
        for cle in ("aime", "evite")
    }


def info_minimale(fiche: dict) -> dict[str, Any]:
    """Version allegee d'une fiche, pour les listes du panneau.

    La fiche recue est deja passee par `localiser()` : il n'y a qu'un endroit
    ou la langue est appliquee, et c'est celui-la.
    """
    return {
        "id": fiche["id"],
        "nom": fiche["nom"],
        "emoji": fiche["emoji"],
        "categorie": fiche["categorie"],
        "famille": fiche["famille"],
        "difficulte": fiche["difficulte"],
        "exposition": fiche["exposition"],
        "perenne": bool(fiche.get("perenne")),
        # Sert a distinguer une vivace saisonniere (pommier, asperge) d'une
        # vivace que l'on cueille presque sans interruption (poireau
        # perpetuel, chou Daubenton, romarin).
        "duree_recolte_jours": (fiche.get("cycle") or {}).get(
            "duree_recolte_jours", 0
        ),
        "arrosage": fiche["arrosage"],
    }


# --- Catalogue personnel ------------------------------------------------------
#
# Les fiches ajoutees par l'utilisateur vivent dans le stockage du jardin, pas
# dans le fichier livre : une mise a jour de l'integration ne doit jamais les
# effacer. Elles sont fusionnees au chargement, et leur id porte un prefixe
# pour qu'elles ne puissent pas masquer une fiche d'origine.

CATEGORIES_VALIDES = {
    "legume-fruit", "legume-racine", "legume-gousse", "legume-bulbe",
    "legume-feuille", "aromatique", "petit-fruit", "fruitier", "fleur-compagne",
    "cereale",
}
EXPOSITIONS_VALIDES = {"plein-soleil", "mi-ombre", "ombre"}
BESOINS_EAU_VALIDES = {"faible", "moyen", "eleve"}


def slug(texte: str) -> str:
    """Identifiant stable derive du nom, sans accent ni espace."""
    base = _sans_accents(texte).strip().lower()
    garde = [c if c.isalnum() else "-" for c in base]
    morceaux = "".join(garde).split("-")
    return "-".join(m for m in morceaux if m) or "culture"


def fenetre_par_mois(mois_debut: int, mois_fin: int) -> dict:
    """Transforme « de mars à juillet » en fenetre exploitable par le moteur.

    Les fiches livrees sont ancrees aux gelees locales, ce qui les rend justes
    partout. Demander cela a quelqu'un qui saisit une fiche a la main serait
    absurde : on prend des mois, donc un ancrage a date fixe. C'est moins
    savant, mais c'est ce que les sachets de graines indiquent.
    """
    mois_debut = max(1, min(12, int(mois_debut)))
    mois_fin = max(1, min(12, int(mois_fin)))
    duree = (mois_fin - mois_debut) % 12
    # Un mois unique couvre tout de meme le mois entier.
    jours = (duree + 1) * 30 if duree or mois_debut == mois_fin else 30
    return {
        "ancrage": "date_fixe",
        "date": f"{mois_debut:02d}-01",
        "duree_jours": jours,
    }


def valider_fiche(fiche: dict) -> list[str]:
    """Problemes empechant une fiche personnelle de fonctionner.

    Volontairement plus souple que la validation du catalogue livre : on
    verifie ce sans quoi le moteur ne saurait rien calculer, pas la qualite
    agronomique de la saisie.

    Renvoie des cles de traduction et non des phrases : ces messages
    s'affichent dans le formulaire du panneau, donc dans la langue de
    l'interface. Ce module reste pur et ne la connait pas.
    """
    soucis: list[str] = []

    if not (fiche.get("nom") or "").strip():
        soucis.append("fiche_nom_requis")
    if fiche.get("categorie") not in CATEGORIES_VALIDES:
        soucis.append("fiche_categorie")
    if fiche.get("exposition") not in EXPOSITIONS_VALIDES:
        soucis.append("fiche_exposition")
    if (fiche.get("arrosage") or {}).get("besoin") not in BESOINS_EAU_VALIDES:
        soucis.append("fiche_eau")
    if not isinstance((fiche.get("rusticite") or {}).get("gel"), bool):
        soucis.append("fiche_gel")

    fenetres = fiche.get("fenetres") or {}
    if not fenetres:
        soucis.append("fiche_aucune_periode")

    cycle = fiche.get("cycle") or {}
    recolte_calculable = (
        "recolte" in fenetres
        or ("plantation" in fenetres and cycle.get("jours_plantation_a_recolte"))
        or (
            ("semis_direct" in fenetres or "semis_interieur" in fenetres)
            and cycle.get("jours_semis_a_recolte")
        )
    )
    if not recolte_calculable:
        soucis.append("fiche_recolte_incalculable")

    return soucis


class Catalogue:
    """Vue fusionnee des fiches livrees et des fiches personnelles."""

    def __init__(self, perso: list[dict] | None = None) -> None:
        livrees = charger()
        self._index = dict(livrees)
        for fiche in perso or []:
            # Une fiche personnelle portant l'id d'une fiche livree ne la
            # double pas : elle la remplace. C'est ainsi qu'on corrige une
            # duree de cycle qui ne correspond pas a son propre jardin.
            fiche = {**fiche, "surcharge": fiche["id"] in livrees}
            self._index[fiche["id"]] = fiche

    def culture(self, culture_id: str) -> dict | None:
        return self._index.get(culture_id)

    def toutes(self, langue: str = "fr") -> list[dict]:
        return sorted(self._index.values(), key=lambda c: nom_localise(c, langue))

    def categories(self) -> list[str]:
        return sorted({c["categorie"] for c in self._index.values()})

    def perso(self, langue: str = "fr") -> list[dict]:
        """Fiches inedites et fiches livrees corrigees, les secondes marquees."""
        return sorted(
            (c for c in self._index.values() if c.get("perso")),
            key=lambda c: nom_localise(c, langue),
        )

    def est_livree(self, culture_id: str) -> bool:
        """Vrai si cet id existe dans le catalogue d'origine."""
        return culture_id in charger()

    def rechercher(
        self, requete: str = "", *, langue: str = "fr", **filtres
    ) -> list[dict]:
        resultats = self.toutes(langue)
        if requete:
            terme = _sans_accents(requete.strip())
            resultats = [c for c in resultats if _correspond(c, terme)]
        if filtres.get("categorie"):
            resultats = [c for c in resultats if c["categorie"] == filtres["categorie"]]
        if filtres.get("exposition"):
            resultats = [
                c for c in resultats if c["exposition"] == filtres["exposition"]
            ]
        if filtres.get("difficulte_max") is not None:
            resultats = [
                c for c in resultats if c["difficulte"] <= filtres["difficulte_max"]
            ]
        return resultats

    def compagnes(self, culture_id: str) -> dict[str, list[dict]]:
        fiche = self.culture(culture_id)
        if not fiche:
            return {"aime": [], "evite": []}
        return {
            cle: [
                self._index[autre]
                for autre in (fiche.get("associations") or {}).get(cle, [])
                if autre in self._index
            ]
            for cle in ("aime", "evite")
        }
