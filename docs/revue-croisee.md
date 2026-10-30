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

---

# Seconde passe : les données de culture

**30 octobre 2026.** Là où la première passe portait sur la nomenclature, qui
se tranche, celle-ci porte sur l'arrosage, les espacements et les périodes —
qui ne se tranchent pas.

## Pourquoi ce n'est pas le même travail

Aucune API ne sert de calendriers de culture. Je l'ai revérifié plutôt que de
le supposer : **OpenFarm** redirige dans le vide, **Permapeople** demande une
clé, **practicalplants** ne répond plus, et les bases taxonomiques ignorent
l'horticulture. La vérification se fait donc page par page, à la main.

Et surtout : **ces champs n'ont pas de valeur vraie.** Trois sources sérieuses
donnent trois espacements différents pour une carotte — la RHS 5–7,5 cm,
l'Almanac 3–4 cm, Au Jardin 6–7 cm — parce que la réponse dépend de la
variété, du sol et de la densité voulue. Ce qu'une revue croisée établit est
plus modeste : une **enveloppe plausible**, et le constat qu'une valeur de
fiche en sort. C'est une alerte, pas un verdict.

`tools/revue_horticole.py` conserve les relevés avec leurs sources et fait
cette comparaison. Il distingue deux poids : `!` quand au moins deux sources
convergent contre la fiche, `~` quand une seule diverge — l'Almanac donne
15 cm entre tournesols, qui est un semis dense de rang, là où la pratique
française est 50. Croire la première source venue remplacerait une valeur
discutable par une autre.

## Ce qui a été trouvé, et corrigé

### Des fenêtres ouvertes trop près de la dernière gelée — 7 fiches

C'est le constat le plus important de cette passe, et il est **systématique,
pas anecdotique**.

La « dernière gelée » du réglage est une moyenne, pas une garantie :
**une année sur dix, en plaine, la dernière gelée tombe après le 13 mai**, et
c'est tout le sens des saints de glace. Ouvrir la fenêtre d'une culture gélive
à la date moyenne, c'est annoncer « c'est le moment » une fois sur deux trop
tôt — et une tomate perdue ne se rattrape pas dans la saison.

Sept fiches ouvraient leur fenêtre de mise en terre entre 0 et 10 jours après
la dernière gelée. Elles passent à 15 jours, qui est la valeur que le
catalogue applique déjà à l'écrasante majorité de ses cultures gélives :

| Fiche | Avant | Après | Source |
|---|---|---|---|
| `tomate`, `tomate-cerise` | +7 j | **+15 j** | Au Jardin « fin avril, début mai » ; Almanac « 2 semaines après » |
| `cosmos` | +0 j | **+15 j** | Almanac « once the danger of frost has passed » |
| `tournesol` | +0 j | **+15 j** | Almanac « after the danger of spring frost has passed », sol ≥ 10 °C |
| `amarante` | +5 j | **+15 j** | gélive semée en surface, même principe |
| `capucine` | +10 j | **+15 j** | idem |
| `oca-perou` | +0 j | **+15 j** | tubercule à 6 cm, sous le seuil d'enfouissement protecteur |

### `poivron` : minimum thermique à 12 °C et non 10 °C

La RHS donne 12 °C comme minimum, Au Jardin 15 °C pour la mise en place. Ce
n'est pas cosmétique : `temp_min_c` **pilote l'alerte gel** depuis qu'elle
existe, donc une valeur trop basse retarde l'avertissement. Le poivron était
par ailleurs le seul des solanacées de saison chaude à 10 °C, aubergine et
basilic étant déjà à 12.

## Deux règles d'audit, qui couvrent les 215 fiches

Les corrections ci-dessus sont ponctuelles ; les règles, elles, valent pour
tout le catalogue et pour tout ce qu'on y ajoutera.

1. **Une gélive mise dehors moins de 15 jours après la dernière gelée** est
   signalée. La règle existante ne regardait que l'antériorité, et laissait
   donc passer une tomate plantée le lendemain de la dernière gelée.
2. **Une fréquence d'arrosage incohérente avec le besoin annoncé** est
   signalée — un « besoin élevé » arrosé moins souvent qu'un « besoin faible »
   rendrait les trois niveaux inutiles. Le catalogue est déjà sain sur ce
   point (élevé 1–5 j, moyen 3–10 j, faible 5–21 j, sans chevauchement) ; la
   règle verrouille cet état.

Les deux ont été vérifiées en les faisant échouer volontairement : une règle
qui ne se déclenche jamais ne prouve rien.

## Les saints de glace, tranchés

La question était ouverte à la rédaction de cette section : fallait-il se
contenter de quinze jours, ou aller jusqu'aux saints de glace ? **Le
propriétaire a tranché pour les saints de glace** — le jardin est en France,
et c'est la règle que le jardinage français applique réellement.

Les 43 fenêtres de mise en terre des cultures gélives ont donc été décalées de
**treize jours**, uniformément. Un décalage uniforme plutôt qu'un plancher,
pour une raison précise : le catalogue gradue déjà ses décalages selon la
frilosité de chaque culture — +15 pour la tomate, +25 pour le gombo — et un
plancher aurait écrasé cette gradation en alignant tout le monde sur la même
date. Le décalage la conserve, et place la plus précoce exactement au bon
jour.

Ce que ça donne, pour une dernière gelée au 15 avril :

| Culture | Mise en terre |
|---|---|
| tomate, courgette, haricot, maïs, poivron, concombre… | **13 mai** — Saint Servais, dernier des saints de glace |
| aubergine, piment, courge musquée | 16 mai |
| basilic, melon, patate douce, haricot à rames | 18 mai |
| pastèque | 20 mai |
| gombo | **23 mai** — Saint Didier, la date des anciens pour les plus frileuses |

La pomme de terre ne bouge pas : elle est plantée à dix centimètres, et ce qui
est enterré n'est pas exposé. C'est l'exception que l'audit connaissait déjà.

`MARGE_GELEE_MINI_JOURS` passe de 15 à 28 dans `auditer_catalogue.py` : une
dernière gelée moyenne au 15 avril plus vingt-huit jours tombe le 13 mai. Le
seuil n'est pas un arrondi prudent, il est calé sur une date.

### L'effet de bord, et l'invariant qu'il a révélé

Décaler les plantations sans toucher aux semis à l'abri allongeait d'autant
l'attente du plant en godet : la tomate passait de 75 à 88 jours entre son
semis et l'ouverture de sa plantation, et un plant qui attend file et
s'enracine dans son godet. **Les 23 semis à l'abri des mêmes cultures ont donc
été décalés de treize jours eux aussi**, ce qui rétablit exactement les délais
d'origine — tomate semée le 27 février, aubergine le 7 février, courgette le
29 mars.

L'invariant qui n'était écrit nulle part, et qui l'est maintenant : **semis à
l'abri et plantation se déplacent ensemble.** `auditer_catalogue.py` porte une
règle qui le rappelle, en signalant un plant qui resterait plus de soixante
jours en godet après son repiquage. La borne est large à dessein — l'aubergine
et le piment y passent réellement six semaines — et cette règle attrape une
incohérence grossière, pas une dérive de quelques jours. Elle vaut surtout
comme rappel.

## Couverture, dite franchement

**6 fiches sur 215 ont été relevées**, dont 4 sur trois sources ou plus :
`tomate`, `courgette`, `carotte`, `poivron`, plus `cosmos` et `tournesol` sur
une source.

Ce n'est pas la revue complète, et il ne faut pas la présenter comme telle.
Une passe complète représente de l'ordre de **630 consultations de pages** —
215 fiches × 3 sources — faites à la main faute d'API. Ce qui est livré ici
est la **méthode, l'outillage et la première série** : le registre des relevés
est dans le dépôt avec ses sources, `--tout` liste les fiches qui n'ont pas
encore été vues, et la revue se reprend par lots sans rien refaire.

Ce qui couvre déjà les 215 fiches, en revanche, ce sont les deux règles
d'audit et les huit règles de cohérence qui existaient : elles ne disent pas
qu'une fiche est juste, elles disent qu'elle n'est pas absurde.
