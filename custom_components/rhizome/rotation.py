"""Rotation des cultures : la même famille ne doit pas revenir trop vite.

Module volontairement pur : aucun import Home Assistant.

La donnée nécessaire existe déjà — la famille botanique dans chaque fiche, la
zone et le journal dans le jardin. L'erreur qu'elle évite est coûteuse et
silencieuse : une solanacée qui revient au même endroit au bout de deux ans
ramène le mildiou avec elle, et le jardinier n'en saura rien avant juillet.

L'avertissement ne bloque jamais. C'est un rappel, pas une règle.
"""

from __future__ import annotations

from datetime import date

# Délai avant de revenir sur la même famille, en années. Les solanacées et les
# brassicacées sont les plus exigeantes : mildiou et hernie du chou survivent
# longtemps dans le sol. Les fabacées, elles, enrichissent et se replacent vite.
DELAIS = {
    "Solanacées": 4,
    "Brassicacées": 4,
    "Apiacées": 3,
    "Cucurbitacées": 3,
    "Amaryllidacées": 3,
    "Amaranthacées": 3,
    "Astéracées": 2,
    "Fabacées": 2,
}
DELAI_DEFAUT = 3


def delai_pour(famille: str | None) -> int:
    return DELAIS.get(famille or "", DELAI_DEFAUT)


def annee_occupation(plante: dict, defaut: int) -> int:
    """Année où cette plante a réellement occupé le terrain.

    Le dernier événement du journal fait foi. Sans journal, la plante est
    seulement prévue : on la compte sur l'année en cours.
    """
    annees = sorted(
        {int(evt["date"][:4]) for evt in plante.get("evenements") or [] if evt.get("date")}
    )
    return annees[-1] if annees else defaut


def verifier(
    fiche: dict,
    zone_id: str,
    plantes: list[dict],
    index_cultures: dict[str, dict],
    aujourdhui: date | None = None,
) -> dict | None:
    """Antécédents de la même famille dans cette zone, ou None.

    Les pérennes sont écartées : un pommier n'entre pas dans une rotation, il
    occupe sa place pour vingt ans.
    """
    aujourdhui = aujourdhui or date.today()
    famille = fiche.get("famille")
    if not famille:
        return None

    delai = delai_pour(famille)
    limite = aujourdhui.year - delai + 1

    precedents = []
    for plante in plantes:
        if plante.get("zone") != zone_id:
            continue
        autre = index_cultures.get(plante.get("culture_id") or "")
        if autre is None or autre.get("famille") != famille or autre.get("perenne"):
            continue
        annee = annee_occupation(plante, aujourdhui.year)
        if annee >= limite:
            # `culture_id` en plus du nom : c'est lui qui permet de retrouver
            # le nom traduit de la culture au moment d'afficher l'avis, le nom
            # stocke ici etant celui du catalogue francais.
            precedents.append(
                {"nom": autre["nom"], "annee": annee, "culture_id": autre["id"]}
            )

    if not precedents:
        return None

    noms = ", ".join(
        f"{p['nom']} ({p['annee']})"
        for p in sorted(precedents, key=lambda p: -p["annee"])[:3]
    )
    # Le message francais est rendu ici parce que ce module est pur et que le
    # francais est la langue de reference. `precedents_libelle` est la meme
    # enumeration, exposee a part : la couche de presentation la reutilise
    # pour reconstruire le message dans une autre langue, sans avoir a
    # retrier ni retronquer la liste.
    return {
        "famille": famille,
        "delai_ans": delai,
        "precedents": precedents,
        "precedents_libelle": noms,
        "message": (
            f"{famille} déjà cultivées ici : {noms}. Cette famille demande "
            f"{delai} ans avant de revenir au même endroit."
        ),
    }
