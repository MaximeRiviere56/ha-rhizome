#!/usr/bin/env python3
"""Revue croisee de la nomenclature du catalogue, sur trois sources.

Pourquoi ce script existe plutot qu'une relecture a la main : 215 fiches ne se
revoient pas une fois, elles se revoient a chaque ajout. Une relecture
manuelle n'est vraie qu'au jour ou elle est faite.

**Ce qu'il verifie, et c'est volontairement etroit** : le nom scientifique et
la famille botanique. Ce sont les deux seuls champs du catalogue qui soient
des faits tranchables par une autorite — et la famille est le seul champ dont
une erreur change un *comportement* : `rotation.DELAIS` s'y indexe, donc une
famille fausse produit un mauvais conseil de rotation, pas une coquille.

**Ce qu'il ne verifie pas, et ne pourra jamais verifier** : l'espacement, la
frequence d'arrosage, les durees de cycle, les fenetres de semis. Trois
sources serieuses donnent trois chiffres differents pour une carotte, parce
que la reponse depend de la variete, du sol et du climat. `auditer_catalogue.py`
montre qu'elles ne sont pas *impossibles* ; aucun outil ne montrera qu'elles
sont *vraies*. Ne pretends pas le contraire dans la documentation.

Les trois sources sont independantes l'une de l'autre, ce qui est tout
l'interet :

- **GBIF** — le referentiel taxonomique agrege qui sert d'ossature a la
  plupart des bases de biodiversite ;
- **World Flora Online** — le successeur de The Plant List, porte par un
  consortium d'herbiers ;
- **Catalogue of Life** — la somme des bases taxonomiques mondiales, editee
  par un consortium distinct des deux premiers.

Wikidata sert de quatrieme avis, consulte seulement quand les trois premiers
ne suffisent pas a trancher : son service SPARQL se met regulierement a
limiter a une requete par minute, et faire dependre une revue de 215 fiches
d'un service dans cet etat serait un mauvais calcul. Il reconstruit la famille
en remontant la chaine des taxons parents, donc par un chemin different des
autres, ce qui en fait un bon arbitre.

POWO (Kew) aurait ete un choix naturel de plus, mais son API est derriere une
protection anti-robot : on ne la contourne pas.

Usage : python3 tools/revue_croisee.py [--json SORTIE] [--seulement ID,ID]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "tools"))

from catalogue_traductions import FAMILLES  # noqa: E402

CATALOGUE = RACINE / "custom_components" / "rhizome" / "data" / "catalog.json"

# Les divergences que l'on assume, avec leur raison. Sans cette table, l'outil
# signalerait huit fiches a chaque passage, et un audit qui echoue toujours est
# un audit que plus personne ne relance : le bruit finirait par couvrir la
# vraie erreur du jour ou elle arrivera.
#
# Chaque entree est une decision prise, pas un oubli. La reouvrir demande de
# refaire le raisonnement, pas de supprimer la ligne.
DIVERGENCES_ASSUMEES = {
    # APG IV absorbe les Chenopodiacees dans les Amaranthacees. GBIF et le
    # Catalogue of Life suivent APG IV, World Flora Online garde l'ancienne
    # famille. On suit APG IV — et c'est aussi ce que la rotation veut : ces
    # cinq cultures partagent reellement les memes parasites telluriques, et
    # `rotation.DELAIS` les groupe sous « Amaranthacees ».
    "arroche": "Chenopodiaceae chez WFO — APG IV les absorbe dans Amaranthaceae",
    "betterave": "Chenopodiaceae chez WFO — APG IV les absorbe dans Amaranthaceae",
    "blette": "Chenopodiaceae chez WFO — APG IV les absorbe dans Amaranthaceae",
    "quinoa": "Chenopodiaceae chez WFO — APG IV les absorbe dans Amaranthaceae",
    "epinard": "Chenopodiaceae chez WFO — APG IV les absorbe dans Amaranthaceae",
    "epinard-perpetuel": "Chenopodiaceae chez WFO — APG IV les absorbe dans Amaranthaceae",
    # Meme debat, dans l'autre sens : APG IV absorbe les Hydrophyllacees dans
    # les Boraginacees, les trois bases suivent ici le Boraginales Working
    # Group qui les separe. On reste sur APG IV par coherence avec la decision
    # precedente — suivre APG IV pour la betterave et son contraire pour la
    # phacelie serait le seul choix indefendable.
    "phacelie": "Hydrophyllaceae dans les trois bases — APG IV la place en Boraginaceae",
    # Kew (POWO) et GBIF disent Asparagaceae ; l'Asphodelaceae du Catalogue of
    # Life est isole, et le Solanaceae qu'avancait Wikidata etait une erreur
    # d'homonymie. `Dracaena marginata` est par ailleurs un synonyme horticole
    # de `D. reflexa var. angustifolia` : on garde le nom des jardineries,
    # puisque c'est sous celui-la que la plante s'achete.
    "dracaena-marginata": "Asphodelaceae chez COL — Kew et GBIF disent Asparagaceae",
}
AGENT = "rhizome-catalogue-audit/1.0 (github.com/MaximeRiviere56/ha-rhizome)"
PAUSE = 0.34  # Trois requetes par seconde au plus : on est invite, pas client.


def _lire(url: str, entetes: dict | None = None) -> dict | None:
    requete = urllib.request.Request(url, headers={"User-Agent": AGENT, **(entetes or {})})
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except Exception as err:  # noqa: BLE001 - une source muette n'invalide pas
        # les autres : c'est tout l'interet d'en interroger trois.
        print(f"    ! {url.split('?')[0]} : {err}", file=sys.stderr)
        return None


# --- Les trois sources --------------------------------------------------------


def gbif(nom: str) -> dict:
    url = "https://api.gbif.org/v1/species/match?" + urllib.parse.urlencode(
        {"name": nom, "kingdom": "Plantae"}
    )
    donnees = _lire(url) or {}
    if donnees.get("matchType") in (None, "NONE"):
        return {}
    return {
        "famille": donnees.get("family"),
        "nom_accepte": donnees.get("species") or donnees.get("canonicalName"),
        "statut": donnees.get("status"),
        "confiance": donnees.get("confidence"),
    }


def wfo(nom: str) -> dict:
    url = "https://list.worldfloraonline.org/matching_rest.php?" + urllib.parse.urlencode(
        {"input_string": nom}
    )
    donnees = _lire(url) or {}
    match = donnees.get("match") or {}
    placement = match.get("placement") or ""

    # Sans correspondance unique, WFO rend des candidats : c'est le cas des
    # homonymes, « Prunus armeniaca L. » contre quatre autres auteurs. Les
    # ignorer coutait 64 fiches sur 215, soit presque un tiers de la revue
    # reduite a deux sources sans que rien ne le signale. Un seul candidat
    # porte une classification — les homonymes posterieurs n'en ont pas — et
    # c'est celui-la qui repond.
    if not placement:
        for candidat in donnees.get("candidates") or []:
            if candidat.get("placement"):
                match = candidat
                placement = candidat["placement"]
                break
    # « Code/Plantae/.../Alismatales/Araceae/Monstera/deliciosa » : la famille
    # est le segment en « aceae ». Le lire par suffixe plutot que par position
    # evite de dependre de la profondeur de la classification, qui varie.
    famille = next(
        (seg for seg in placement.split("/") if seg.endswith("aceae")), None
    )
    return {
        "famille": famille,
        "nom_accepte": (match.get("full_name_plain") or "").rsplit(" ", 1)[0] or None,
        "wfo_id": match.get("wfo_id"),
    }


def catalogue_of_life(nom: str) -> dict:
    """Le dataset 3LR est la derniere version annuelle publiee du COL."""
    url = "https://api.checklistbank.org/dataset/3LR/nameusage/search?" + urllib.parse.urlencode(
        {"q": nom, "limit": 1, "content": "SCIENTIFIC_NAME"}
    )
    donnees = _lire(url) or {}
    resultats = donnees.get("result") or []
    if not resultats:
        return {}
    premier = resultats[0]
    classification = premier.get("classification") or []
    famille = next(
        (c.get("name") for c in classification if c.get("rank") == "family"), None
    )
    return {
        "famille": famille,
        "nom_accepte": (premier.get("usage") or {}).get("label"),
    }


REQUETE_WIKIDATA = """
SELECT ?nom ?familleNom WHERE {
  VALUES ?nom { %s }
  ?taxon wdt:P225 ?nom .
  ?taxon wdt:P171* ?fam .
  ?fam wdt:P105 wd:Q35409 ; wdt:P225 ?familleNom .
}
"""


def wikidata(noms: list[str]) -> dict[str, str]:
    """Les familles de Wikidata, en une requete pour tout un lot.

    Groupee a dessein : 215 requetes separees seraient impolies et lentes, et
    le service SPARQL accepte tres bien une liste de valeurs.
    """
    familles: dict[str, str] = {}
    for depart in range(0, len(noms), 60):
        lot = noms[depart : depart + 60]
        valeurs = " ".join(f'"{n}"' for n in lot)
        url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode(
            {"query": REQUETE_WIKIDATA % valeurs, "format": "json"}
        )
        donnees = _lire(url, {"Accept": "application/sparql-results+json"}) or {}
        for ligne in (donnees.get("results") or {}).get("bindings", []):
            familles[ligne["nom"]["value"]] = ligne["familleNom"]["value"]
        time.sleep(PAUSE)
    return familles


# --- Comparaison --------------------------------------------------------------


def _nom_interrogeable(nom_scientifique: str) -> str:
    """Le binome, sans l'infraspecifique ni l'auteur.

    « Solanum lycopersicum var. cerasiforme » s'interroge comme l'espece :
    les referentiels rangent la variete sous elle, et c'est la famille qui
    nous interesse.
    """
    mots = (nom_scientifique or "").replace("×", " ").split()
    # Le « x » d'un hybride horticole — « Fragaria x ananassa » — est un signe,
    # pas un epithete : le garder decalait le binome et faisait interroger
    # « Fragaria x », d'ou un repli sur le genre qui ressemblait a une erreur
    # de fiche alors que c'en etait une de l'outil.
    mots = [m for m in mots if m and m.lower() != "x" and not m.endswith(".")]
    return " ".join(mots[:2])


def revoir(fiches: list[dict]) -> list[dict]:
    # Wikidata n'est consulte qu'en arbitrage, et son service limite
    # severement : on ne lui demande que les noms sur lesquels les trois
    # premieres sources ne se sont pas mises d'accord. Premier passage donc
    # sans lui, second passage pour les seuls litiges.
    familles_wd: dict[str, str] = {}

    resultats = []
    for n, fiche in enumerate(fiches, 1):
        nom = _nom_interrogeable(fiche["nom_scientifique"])
        print(f"[{n}/{len(fiches)}] {fiche['id']}", file=sys.stderr)

        g = gbif(nom)
        time.sleep(PAUSE)
        w = wfo(nom)
        time.sleep(PAUSE)
        c = catalogue_of_life(nom)
        time.sleep(PAUSE)

        attendue = FAMILLES.get(fiche["famille"])
        trouvees = {
            "gbif": g.get("famille"),
            "wfo": w.get("famille"),
            "col": c.get("famille"),
        }
        repondu = {s: f for s, f in trouvees.items() if f}
        accord = set(repondu.values())

        resultats.append(
            {
                "id": fiche["id"],
                "nom": fiche["nom"],
                "nom_scientifique": fiche["nom_scientifique"],
                "nom_interroge": nom,
                "famille_fiche": fiche["famille"],
                "famille_fiche_latin": attendue,
                "familles_sources": trouvees,
                "sources_repondues": len(repondu),
                "sources_d_accord_entre_elles": len(accord) <= 1,
                "accord_avec_la_fiche": bool(attendue) and accord == {attendue},
                "nom_accepte_gbif": g.get("nom_accepte"),
                "nom_accepte_col": c.get("nom_accepte"),
                "statut_gbif": g.get("statut"),
                "famille_inconnue_du_projet": attendue is None,
            }
        )

    # Arbitrage : Wikidata n'est appele que sur les fiches qui posent
    # question, et son silence ne les condamne pas.
    litiges = [
        r for r in resultats
        if not r["accord_avec_la_fiche"] or not r["sources_d_accord_entre_elles"]
    ]
    if litiges:
        print(f"Wikidata : arbitrage sur {len(litiges)} fiches…", file=sys.stderr)
        familles_wd = wikidata(sorted({r["nom_interroge"] for r in litiges}))
        for r in litiges:
            r["familles_sources"]["wikidata"] = familles_wd.get(r["nom_interroge"])
            repondu = set(filter(None, r["familles_sources"].values()))
            r["sources_repondues"] = len(
                [f for f in r["familles_sources"].values() if f]
            )
            r["sources_d_accord_entre_elles"] = len(repondu) <= 1
            r["accord_avec_la_fiche"] = (
                bool(r["famille_fiche_latin"]) and repondu == {r["famille_fiche_latin"]}
            )

    return resultats


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--json", type=pathlib.Path)
    parseur.add_argument("--seulement", help="liste d'identifiants separes par des virgules")
    args = parseur.parse_args()

    fiches = json.loads(CATALOGUE.read_text(encoding="utf-8"))["cultures"]
    if args.seulement:
        garder = set(args.seulement.split(","))
        fiches = [f for f in fiches if f["id"] in garder]

    resultats = revoir(fiches)

    desaccords = [
        r for r in resultats
        if not r["accord_avec_la_fiche"] and r["id"] not in DIVERGENCES_ASSUMEES
    ]
    assumees = [
        r for r in resultats
        if not r["accord_avec_la_fiche"] and r["id"] in DIVERGENCES_ASSUMEES
    ]
    # Une fiche confirmee par une seule source n'est pas croisee : on la
    # distingue, sans quoi « confirmee » voudrait dire deux choses.
    faiblement = [
        r for r in resultats
        if r["accord_avec_la_fiche"] and r["sources_repondues"] < 2
    ]
    muettes = [r for r in resultats if r["sources_repondues"] == 0]
    divergentes = [r for r in resultats if not r["sources_d_accord_entre_elles"]]

    print(f"\n{len(resultats)} fiches revues sur trois sources.")
    print(f"  {len(resultats) - len(desaccords) - len(assumees)} confirmees")
    print(f"  {len(assumees)} divergences assumees, avec leur raison")
    print(f"  {len(desaccords)} a verifier")
    print(f"  {len(divergentes)} ou les sources se contredisent entre elles")
    print(f"  {len(muettes)} qu'aucune source ne connait")
    if faiblement:
        print(f"  {len(faiblement)} confirmees par une seule source — non croisees :")
        for r in faiblement:
            print(f"      {r['id']}")

    for r in desaccords:
        sources = ", ".join(
            f"{s}={f or '—'}" for s, f in r["familles_sources"].items()
        )
        print(f"\n  {r['id']:24} fiche : {r['famille_fiche_latin'] or r['famille_fiche']}")
        print(f"  {'':24} {sources}")
        if r["nom_accepte_gbif"] and r["nom_accepte_gbif"] != r["nom_interroge"]:
            print(f"  {'':24} GBIF accepte plutot : {r['nom_accepte_gbif']}")

    for r in assumees:
        print(f"\n  ~ {r['id']:22} {DIVERGENCES_ASSUMEES[r['id']]}")

    # Une divergence inscrite dans la table mais que les sources ne signalent
    # plus est du poids mort, et pire : elle masquerait une vraie erreur sur
    # cette fiche le jour ou elle apparaitrait.
    for cid in sorted(set(DIVERGENCES_ASSUMEES) - {r["id"] for r in assumees}):
        if any(r["id"] == cid for r in resultats):
            print(f"\n  ! {cid} : divergence assumee devenue sans objet, a retirer")

    if args.json:
        args.json.write_text(
            json.dumps(resultats, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"\nDetail complet : {args.json}")

    return 1 if desaccords else 0


if __name__ == "__main__":
    sys.exit(main())
