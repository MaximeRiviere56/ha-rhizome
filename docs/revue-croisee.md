# Revue croisée du catalogue

Première passe : **30 octobre 2026**, sur les 215 fiches, par
`tools/revue_croisee.py`.

Ce document dit ce qui a été vérifié, contre quoi, ce qui a changé, et —
surtout — **ce qui ne peut pas l'être**. Il est écrit pour être relu dans un
an par quelqu'un qui se demandera jusqu'où va la confiance qu'on peut
accorder à une fiche.

## Ce qui a été vérifié

Deux champs : le **nom scientifique** et la **famille botanique**.

Ils ne sont pas choisis au hasard. Ce sont les deux seuls champs du catalogue
qui soient des faits tranchables par une autorité extérieure — et la famille
est le seul champ dont une erreur change un *comportement* et non un
affichage : `rotation.DELAIS` s'y indexe, donc une famille fausse produit un
mauvais conseil de rotation. Les autres champs sont des jugements horticoles
(voir plus bas).

### Les sources

Trois bases indépendantes, interrogées pour chaque fiche :

| Source | Ce qu'elle est |
|---|---|
| [GBIF](https://www.gbif.org) | le référentiel taxonomique agrégé qui sert d'ossature à la plupart des bases de biodiversité |
| [World Flora Online](https://www.worldfloraonline.org) | successeur de The Plant List, porté par un consortium d'herbiers |
| [Catalogue of Life](https://www.catalogueoflife.org) | la somme des bases taxonomiques mondiales, éditée par un consortium distinct |

[Wikidata](https://www.wikidata.org) sert de **quatrième avis**, consulté
uniquement quand les trois premiers ne suffisent pas à trancher. Il reconstruit
la famille en remontant la chaîne des taxons parents, donc par un chemin
différent des autres, ce qui en fait un bon arbitre — mais son service SPARQL
se met régulièrement à limiter à une requête par minute, et faire dépendre une
revue de 215 fiches d'un service dans cet état serait un mauvais calcul.

POWO (Kew) aurait été un choix naturel de plus. Son API est derrière une
protection anti-robot, et on ne la contourne pas ; elle a été consultée à la
main sur les cas litigieux.

### Le résultat

```
215 fiches revues
  207 confirmées
    8 divergences assumées, avec leur raison
    0 à vérifier
```

Couverture : **205 fiches croisées sur 3 sources**, 8 sur 4, et 2 sur 2
seulement — `oignon-rocambole` (*Allium × proliferum*, un hybride que World
Flora Online ne liste pas) et `pissenlit` (*Taraxacum officinale*, un agrégat
de plusieurs milliers de microespèces). Dans les deux cas GBIF et le Catalogue
of Life sont d'accord, et la famille n'a rien d'ambigu.

## Ce qui a été corrigé

| Fiche | Avant | Après | Pourquoi |
|---|---|---|---|
| `sureau-noir` | Adoxacées | **Viburnacées** | *Viburnaceae* est le nom conservé depuis 2016 ; *Adoxaceae* n'a pas la priorité. Les quatre sources sont d'accord. |
| `camomille-matricaire` | *Matricaria recutita* | ***Matricaria chamomilla*** | *M. recutita* est un synonyme ; *M. chamomilla* est le nom accepté. |
| `orchidee-phalaenopsis` | *Phalaenopsis hybride* | ***Phalaenopsis* × hybr.** | « hybride » n'est pas un épithète. Ce qu'on achète est un hybride horticole sans nom d'espèce, et l'écrire ainsi le dit. |

Aucune des trois n'avait de conséquence fonctionnelle : ni Adoxacées ni
Viburnacées ne figurent dans `rotation.DELAIS`.

## Les huit divergences assumées

Elles sont inscrites dans `DIVERGENCES_ASSUMEES`, au début de
`tools/revue_croisee.py`, avec leur raison — sans quoi l'outil signalerait
huit fiches à chaque passage, et **un audit qui échoue toujours est un audit
que plus personne ne relance**. L'outil signale aussi l'inverse : une
divergence inscrite que les sources ne rapportent plus est du poids mort, et
masquerait une vraie erreur sur cette fiche.

### Amaranthacées contre Chénopodiacées — 6 fiches

`arroche`, `betterave`, `blette`, `quinoa`, `epinard`, `epinard-perpetuel`.

APG IV absorbe les Chénopodiacées dans les Amaranthacées. GBIF et le Catalogue
of Life suivent APG IV, World Flora Online garde l'ancienne famille. **On suit
APG IV**, et c'est aussi ce que veut la rotation : ces cultures partagent
réellement les mêmes parasites telluriques, et `rotation.DELAIS` les groupe
sous « Amaranthacées » avec un délai de trois ans. Les séparer casserait un
regroupement juste au jardin pour suivre une classification abandonnée.

### Hydrophyllacées contre Boraginacées — `phacelie`

Le même débat, dans l'autre sens : APG IV absorbe les Hydrophyllacées dans les
Boraginacées, et les trois bases suivent ici le *Boraginales Working Group*,
qui les sépare. **On reste sur APG IV par cohérence** — suivre APG IV pour la
betterave et son contraire pour la phacélie serait le seul choix indéfendable
des trois. Aucune des deux familles n'est dans `rotation.DELAIS`, donc aucune
conséquence fonctionnelle.

### `dracaena-marginata`

Kew (POWO) et GBIF disent *Asparagaceae* ; l'*Asphodelaceae* du Catalogue of
Life est isolé, et le *Solanaceae* qu'avançait Wikidata était une erreur
d'homonymie. La fiche est juste.

*Dracaena marginata* est par ailleurs un **synonyme horticole** de *D. reflexa*
var. *angustifolia* (POWO). On garde le nom des jardineries, puisque c'est sous
celui-là que la plante s'achète.

## Les synonymes horticoles conservés

La revue a relevé neuf fiches dont le nom scientifique est, pour les
référentiels, un synonyme d'un nom accepté plus récent. **Elles n'ont pas été
changées**, et c'est un choix : Rhizome est un outil de jardin, pas un
herbier. Un utilisateur qui cherche « petit pois » ne doit pas tomber sur
*Lathyrus oleraceus*.

| Fiche | Nom de la fiche | Nom accepté aujourd'hui |
|---|---|---|
| `petit-pois`, `pois-mange-tout` | *Pisum sativum* | *Lathyrus oleraceus* |
| `lentille` | *Lens culinaris* | *Vicia lens* |
| `scorsonere` | *Scorzonera hispanica* | *Pseudopodospermum hispanicum* |
| `calathea` | *Calathea orbifolia* | *Goeppertia orbifolia* |
| `kiwi` | *Actinidia deliciosa* | *A. chinensis* var. *deliciosa* |
| `oeillet-inde` | *Tagetes patula* | *Tagetes erecta* |

Ces révisions sont récentes et moléculaires ; le commerce horticole et la
littérature de jardinage emploient toujours les anciens noms. Le jour où ils
basculeront, ces lignes seront à reprendre.

## Ce qui ne peut pas être vérifié, et ne le sera jamais

**L'espacement, la fréquence d'arrosage, les fenêtres de semis et surtout les
durées de cycle ne sont pas vérifiables par une revue croisée.** Trois sources
sérieuses donnent trois chiffres différents pour une carotte, parce que la
réponse dépend de la variété, du sol, de l'exposition et du climat. Ce ne sont
pas des faits avec une valeur vraie : ce sont des jugements horticoles.

Ce que le projet oppose à cela n'a pas changé, et reste ce qu'il y a de plus
solide :

- **le réel prime dès le premier semis noté** — l'estimation ne sert qu'à la
  première saison d'une culture donnée ;
- **l'utilisateur corrige n'importe quelle fiche**, y compris livrée ;
- **`tools/auditer_catalogue.py`** prouve qu'aucune fiche n'est *impossible*
  (huit règles de cohérence interne). Il ne prouvera jamais qu'elle est juste.

Une revue croisée sur ces champs produirait une fourchette plausible et la
liste des désaccords entre sources. Ce serait utile. Ce ne serait pas une
vérité, et il ne faut pas le présenter comme tel.

## Rejouer la revue

```bash
python3 tools/revue_croisee.py                    # les 215 fiches
python3 tools/revue_croisee.py --seulement tomate,ortie
python3 tools/revue_croisee.py --json revue.json  # le détail par fiche
```

Le script rend 0 quand tout concorde ou que les divergences sont celles qui
sont assumées, 1 dès qu'une fiche sort du lot. Comptez une dizaine de minutes
pour le catalogue entier : il se limite à trois requêtes par seconde, parce
qu'on est invité sur ces services et non client.
