# Contribuer à Rhizome

Merci de l'intérêt. Quelques repères avant d'écrire du code — le projet a des
conventions fermes, et elles ont toutes une raison.

## La règle qui gouverne le reste

**Le calendrier est piloté par ce qui s'est vraiment passé, pas par une
moyenne saisonnière.** Dès qu'une date réelle entre au journal, les étapes
suivantes s'enchaînent depuis elle. Semer trois semaines en retard décale la
récolte d'autant, et une plante déjà semée ne réclame plus jamais de la semer.
Toute évolution doit préserver ça.

## Invariants

1. Un fait du journal gagne toujours sur une fenêtre saisonnière.
2. Le décalage de zone ne s'applique jamais à une date réelle. Une prévision se
   décale, un fait non.
3. Aucune date en dur dans le catalogue : chaque fenêtre est un décalage en
   jours par rapport aux gelées locales. Seules les pérennes déclarent une
   récolte à date fixe.
4. La phase se déduit toujours du journal par repli, jamais stockée comme fait
   indépendant. C'est ce qui rend l'annulation fiable.
5. Toute mutation passe par `coordinator.async_appliquer`, qui écrit sur disque
   *et attend*. Une sauvegarde différée a déjà coûté un jardin entier.
6. L'arrosage n'est pas un événement du journal : il ne fait pas avancer le
   cycle et se répète trop souvent. Liste séparée.
7. Un rappel qu'on ignore discrédite tous les autres. Chaque garde-fou existant
   est là pour ça.

## Architecture

Quatre modules **purs**, sans aucun import Home Assistant, donc testables hors
instance : `lifecycle.py` (le journal), `phenology.py` (le calcul des étapes),
`rotation.py`, `watering.py`.

**Toute logique métier non triviale va dans un module pur et arrive avec ses
tests.** C'est la convention la plus importante du projet.

Le reste est la couche Home Assistant : `__init__.py`, `config_flow.py`,
`coordinator.py`, `store.py`, `catalog.py`, `websocket.py`, `notifier.py`,
`diagnostics.py` et les quatre plateformes d'entités.

Le frontend est en web components natifs : **zéro étape de build, zéro
dépendance.** Le fichier servi est celui qu'on lit. N'introduisez pas de
bundler.

## Vérifier

```bash
./scripts/verifier.sh
```

Le script monte l'environnement au besoin (il lui faut
[uv](https://docs.astral.sh/uv/)) et enchaîne :

| Étape | Ce qu'elle couvre |
|---|---|
| `unittest` | les quatre modules purs, sans aucune dépendance |
| `tools/auditer_catalogue.py` | cohérence interne des 215 fiches |
| `ruff check` | lint et tri des imports |
| `mypy` | typage de l'intégration |
| `pytest` | la couche Home Assistant, avec couverture |

Les modules purs tournent aussi sur le Python du système, sans rien installer :

```bash
PYTHONPATH=tests python3 -m unittest discover -s tests -p 'test_*.py'
```

**Évitez la syntaxe Python 3.12+** dans les modules purs : c'est ce qui les
garde vérifiables sur un poste sans environnement.

### Le banc d'essai

Le panneau et la carte se vérifient hors de Home Assistant, avec un `hass`
factice alimenté par le vrai moteur et le vrai catalogue :

```bash
python3 tools/banc_fixture.py && python3 -m http.server 8777
# http://localhost:8777/tools/banc.html        — le panneau
# http://localhost:8777/tools/banc-carte.html  — la carte Lovelace
```

Il a attrapé la plupart des défauts réels du projet. Utilisez-le avant de
proposer un changement d'interface.

**Son angle mort** : `tools/banc_fixture.py` réimplémente à la main la
sérialisation de `websocket.py`. Si les deux divergent, le banc ment.

## Le catalogue

Les fiches se modifient dans `tools/catalogue_source.py` (table compacte), pas
dans le JSON généré :

```bash
$EDITOR tools/catalogue_source.py       # la fiche
$EDITOR tools/catalogue_traductions.py  # son anglais
python3 tools/build_catalog.py          # valide puis régénère data/catalog.json
```

Les deux vont ensemble : `build_catalog.py` **échoue** si une fiche arrive sans
son nom anglais, sa famille, son sol, sa note d'arrosage ou ses conseils
traduits. C'est délibéré — une fiche à moitié traduite ne se remarque qu'une
fois sous les yeux d'un utilisateur anglophone.

**172 des 215 fiches n'ont été confrontées à aucune base de référence** —
potagères, aromatiques, fruitiers, fleurs compagnes : elles sont écrites de
mémoire horticole, ne les présentez jamais comme sourcées. Les 43 autres — 21
médicinales, 22 plantes d'intérieur — le sont, et leurs sources figurent en
tête de section dans `tools/catalogue_source.py`. Une correction de fiche est
la bienvenue dans les deux cas ; dites d'où vient votre valeur.

Si vous ajoutez une médicinale, deux règles sans exception : **aucune
posologie ni indication thérapeutique**, et **le risque en premier conseil** —
toxicité, confusion dangereuse à la cueillette, interaction médicamenteuse
connue. C'est le seul endroit du catalogue où une fiche muette peut nuire.

## Conventions

- **Tout en français** : code, commentaires, commits, documentation.
- **L'interface, elle, est bilingue** (français et anglais), et le français en
  reste la version de référence. Un texte affiché ne s'écrit jamais en dur : il
  passe par `i18n.py` côté serveur, par la table `TEXTES` du fichier concerné
  côté frontend, et par `tools/catalogue_traductions.py` pour le catalogue —
  où `build_catalog.py` refuse de compiler une fiche sans sa traduction. Les
  textes de l'utilisateur (surnoms, noms de zones, fiches personnelles, notes)
  ne sont jamais traduits : ce sont des données.
- Les commentaires disent **pourquoi**, pas quoi. Ceux qui expliquent un choix
  contre-intuitif ont de la valeur ; les autres non.
- Messages de commit : ce qui change, et le raisonnement derrière. Les défauts
  trouvés y sont consignés avec leur cause.
- Le mot « potager » reste partout où c'est un **nom commun**. Pas de
  rechercher-remplacer global dessus.

## Avant d'ouvrir une pull request

- `./scripts/verifier.sh` passe.
- Tout correctif de bug ou de sécurité arrive avec son test de non-régression.
- Un changement cassant est décrit dans `CHANGELOG.md`, avec sa migration.
- Pas de changement de `domain` ni d'`unique_id` sans `async_migrate_entry`
  testé.
