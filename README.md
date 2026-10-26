# Rhizome

[![Version](https://img.shields.io/github/v/release/MaximeRiviere56/ha-rhizome?label=version&sort=semver)](https://github.com/MaximeRiviere56/ha-rhizome/releases)
[![Validation](https://github.com/MaximeRiviere56/ha-rhizome/actions/workflows/validation.yml/badge.svg)](https://github.com/MaximeRiviere56/ha-rhizome/actions/workflows/validation.yml)
[![Qualité](https://github.com/MaximeRiviere56/ha-rhizome/actions/workflows/qualite.yml/badge.svg)](https://github.com/MaximeRiviere56/ha-rhizome/actions/workflows/qualite.yml)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.10%2B-41BDF5?logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![Licence MIT](https://img.shields.io/github/license/MaximeRiviere56/ha-rhizome)](LICENSE)
[![Local first](https://img.shields.io/badge/local-100%25-brightgreen)](#vie-privée)

[![Ajouter le dépôt à HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MaximeRiviere56&repository=ha-rhizome&category=integration)

Une intégration Home Assistant pour gérer un potager : choisir ses légumes dans
un catalogue de 172 cultures, les suivre dans un jardin virtuel, et recevoir au
bon moment un rappel pour semer, repiquer ou récolter.

> **L'idée centrale.** Le calendrier n'est pas une fiche théorique figée : il
> est piloté par ce qui s'est vraiment passé. Vous semez vos tomates trois
> semaines en retard ? La date de récolte se décale de trois semaines. Et la
> plante déjà semée ne vous réclamera plus jamais de la semer.

> **Rhizome s'appelait « Mon Potager » jusqu'à la v0.6.0.** Le nom a changé
> parce que le projet ne veut plus se limiter au jardin. Si vous venez de cette
> version, lisez [Migration depuis Mon Potager](#migration-depuis-mon-potager)
> avant de mettre à jour : votre journal est repris automatiquement, mais vos
> entités changent de nom.

## Ce que ça donne

**Un panneau « Rhizome » dans la barre latérale**, avec six vues :
Aujourd'hui, Mon potager, Catalogue, Calendrier, Journal et Réglages.

L'ensemble existe **en français et en anglais** — panneau, carte, catalogue,
rappels, calendrier et noms d'entités. Par défaut la langue suit celle de Home
Assistant ; elle se force depuis *Réglages · Langue*.

![Le jardin, par zone](docs/mon-potager.png)

Chaque plante montre sa phase, sa zone et son échéance suivante. La barre de
progression se remplit pendant la fenêtre en cours.

![Le catalogue](docs/catalogue.png)

Les 172 fiches, filtrables. Le filtre **Semable maintenant** répond à la seule
question qui compte devant un catalogue de cette taille : qu'est-ce que je peux
mettre en terre ce week-end ? Les dates affichées sont calculées depuis vos
propres gelées, pas depuis une moyenne nationale.

![Rien à faire aujourd'hui](docs/aujourdhui.png)

Et quand il n'y a rien à faire, l'application le dit. Un potager n'a pas besoin
d'attention tous les jours, et inventer des tâches pour meubler serait le plus
sûr moyen de faire ignorer les vraies.

**Des entités** pour vos tableaux de bord et vos automatisations :

| Entité | Rôle |
|---|---|
| `sensor.rhizome_actions_a_mener` | Nombre d'actions du jour, détail en attributs |
| `sensor.rhizome_a_arroser` | Nombre de plantes qui attendent de l'eau, détail en attributs |
| `sensor.rhizome_recolte_de_la_saison` | Récolte de l'année en cours en kg (`state_class: total`) ; le cumul de toutes les saisons reste en attribut |
| `sensor.<plante>` | Phase de la plante, et toute sa fiche en attributs |
| `switch.rappels_<plante>` | Rappels de cette plante — automatisable (« coupe tout pendant les vacances ») |
| `calendar.rhizome` | Étapes prévues **et** journal passé |
| `todo.rhizome` | Tâches en cours — **cocher enregistre l'événement** |

**Une carte Lovelace** `custom:rhizome-card` pour votre tableau de bord principal.

> **Les `entity_id` ci-dessus sont ceux d'une installation en français.** Ils
> sont dérivés du nom de l'entité **au moment où elle est créée**, et ne
> bougent plus ensuite : changer de langue renomme ce qui s'affiche, jamais un
> identifiant, donc vos automatisations survivent. Une installation créée en
> anglais, elle, les nomme dès le départ `sensor.rhizome_tasks_due`,
> `sensor.rhizome_needs_watering` et `sensor.rhizome_harvest_this_season`.

## Le suivi réel, sans formulaire

Un journal qu'on doit tenir à la main ne se tient pas. Il y a donc trois chemins
pour enregistrer un geste, et aucun ne demande de saisir une date :

1. le bouton **« C'est fait »** sur la notification ;
2. la **case à cocher** de `todo.rhizome` ;
3. le bouton **« Fait »** sur la carte Lovelace ou dans le panneau.

Chacun inscrit l'événement au journal à la date du jour, ce qui recalcule
immédiatement la suite du cycle.

```
prévu ──semé le──▶ semé ──repiqué le──▶ planté ──1ʳᵉ récolte──▶ en récolte ──▶ terminé
                     │                     │
                     └─ repiquage prévu    └─ récolte prévue
                        = cette date + jours_semis_a_repiquage
```

Les récoltes se cumulent : un plant de tomates se récolte vingt fois, et vous
obtenez un total par culture et par saison. `rhizome.annuler_dernier_evenement`
défait la dernière entrée — on se trompe toujours une fois.

## Installation

### En un clic

[![Ajouter le dépôt à HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MaximeRiviere56&repository=ha-rhizome&category=integration)

Ce bouton ouvre HACS sur votre propre instance avec le dépôt déjà renseigné :
il ne reste qu'à télécharger, redémarrer, puis ajouter l'intégration.

> Il s'appuie sur [My Home Assistant](https://my.home-assistant.io/). Au premier
> usage, votre navigateur vous demandera l'adresse de votre instance ; elle
> reste stockée dans ce navigateur et n'est transmise à personne.

### À la main, dans HACS

1. HACS → menu ⋮ → **Dépôts personnalisés**
2. URL `https://github.com/MaximeRiviere56/ha-rhizome`, catégorie **Integration**
3. Installer **Rhizome**, puis redémarrer Home Assistant
4. **Paramètres → Appareils et services → Ajouter une intégration → Rhizome**

### Sans HACS

Copier `custom_components/rhizome/` dans le dossier `config/` de Home
Assistant, redémarrer, puis ajouter l'intégration.

### Désinstaller

1. **Paramètres → Appareils et services → Rhizome → menu ⋮ → Supprimer.** Les
   entités, le panneau latéral et les actions disparaissent immédiatement, sans
   redémarrage.
2. Dans HACS, **Rhizome → menu ⋮ → Supprimer**, puis redémarrer Home Assistant.
3. Retirer la ressource `/rhizome-frontend/rhizome-card.js` de **Paramètres →
   Tableaux de bord → Ressources**, et les cartes `custom:rhizome-card` de vos
   tableaux de bord.

**Votre jardin n'est pas effacé.** Le journal vit dans
`.storage/rhizome.jardin`, que l'intégration ne touche pas en partant :
réinstaller le retrouve intact. Pour l'effacer vraiment, supprimez ce fichier
à la main, Home Assistant arrêté.

### Migration depuis Mon Potager

Le renommage change le domaine de l'intégration, et Home Assistant ne sait pas
déplacer une entrée de configuration d'un domaine à l'autre. La bascule se fait
donc à la main, une seule fois :

1. **Paramètres → Appareils et services → Mon Potager → Supprimer.** Cela
   n'efface pas votre jardin : le journal vit dans un fichier de stockage que
   l'intégration ne touche pas en partant.
2. Dans HACS, supprimer **Mon Potager**, puis ajouter le dépôt
   `https://github.com/MaximeRiviere56/ha-rhizome` et télécharger **Rhizome**.
3. Redémarrer Home Assistant, puis ajouter l'intégration **Rhizome**.

Au premier démarrage, Rhizome reprend le jardin écrit par Mon Potager —
plantes, journal, arrosages, fiches personnelles et zones. L'ancien fichier est
laissé intact : il reste votre filet.

Ce qui change, en revanche :

| Avant | Après |
|---|---|
| `sensor.mon_potager_actions_a_mener` | `sensor.rhizome_actions_a_mener` |
| `calendar.mon_potager`, `todo.mon_potager` | `calendar.rhizome`, `todo.rhizome` |
| `potager.marquer_seme` et les autres services | `rhizome.marquer_seme` |
| `custom:potager-card` | `custom:rhizome-card` |
| `/potager-frontend/potager-card.js` | `/rhizome-frontend/rhizome-card.js` |
| Panneau sur `/potager` | Panneau sur `/rhizome` |

Vos tableaux de bord et automatisations qui nomment ces entités sont à
reprendre. Les réglages — gelées, destinataires des rappels, zones — sont à
ressaisir une fois, puisqu'ils vivent dans l'entrée de configuration supprimée.

### La carte Lovelace

Le fichier est servi par l'intégration. L'ajouter dans **Paramètres →
Tableaux de bord → Ressources** :

- URL : `/rhizome-frontend/rhizome-card.js`
- Type : **Module JavaScript**

```yaml
type: custom:rhizome-card
titre: Au potager
vue: tout        # tout (défaut) · actions · arrosage
max: 8
```

La carte liste ce qu'il y a à faire et les plantes à arroser, chacune avec son
bouton. En `vue: arrosage`, elle ne montre que l'eau.

## Réglages

Tout se règle depuis l'onglet **Réglages** du panneau, sans passer par les
pages de configuration de Home Assistant.

### Saison et gelées

Les deux dates qui calent **tout** le calendrier. Un préréglage climatique
(Ouest océanique, Nord et Est, Midi, Montagne) les remplit, ou vous saisissez
les vôtres. Les modifier redessine immédiatement les 172 fiches.

### Langue

**Automatique**, **Français** ou **English**. « Automatique » est le défaut et
suit la langue de Home Assistant.

Le réglage ne touche pas que le panneau. Il décide aussi de la langue des
rappels, des événements du calendrier, de la liste de tâches, du catalogue
(les 172 fiches sont traduites : noms, familles, sols, conseils) et des **noms
affichés** des entités.

Trois conséquences, qu'il vaut mieux connaître avant de changer :

- les `entity_id` ne bougent pas. Ils sont figés à la création de l'entité :
  une installation française garde `sensor.rhizome_actions_a_mener` même
  passée en anglais, et vos automatisations continuent de fonctionner ;
- le capteur de phase d'une plante change d'état (`Semé` devient `Sown`). Son
  historique garde donc les anciens libellés avant le changement, et une
  automatisation qui compare cet état au texte demande à être relue ;
- les noms de vos zones ne sont pas traduits. Les quatre zones livrées sont
  nommées dans votre langue **à la première installation**, puis deviennent
  des données que vous pouvez renommer — les retraduire après coup effacerait
  vos propres noms.

Vos fiches personnelles ne sont pas traduites non plus, pour la même raison :
elles s'affichent telles que vous les avez écrites.

### Rappels

Quatre niveaux de granularité, du plus large au plus fin :

| Niveau | Réglage |
|---|---|
| **À qui** | les applications mobiles qui reçoivent les rappels, et/ou une notification interne à Home Assistant |
| **Quoi** | ce qui mérite un rappel — semis à l'abri, semis en place, repiquage, plantation, récolte, arrosage |
| **Quand** | l'heure de la vérification, le délai d'anticipation, et la relance pendant la récolte |
| **Comment** | un message par plante, ou un seul message groupé |

Deux réglages méritent un mot.

**La relance de récolte.** Une courgette se cueille tous les deux jours :
prévenir une seule fois ne sert à rien. Mettez 2 et le rappel revient tant que
la fenêtre est ouverte. À 0, un unique rappel par récolte.

**Le message groupé.** Au printemps, cinq rappels le même matin sont cinq
rappels qu'on balaie sans lire. Le revers : un message groupé ne peut pas
porter de bouton « C'est fait », puisqu'il faudrait deviner de quelle plante
il s'agit.

Au-dessous, chaque plante garde son propre interrupteur de rappels et peut
avoir son propre délai, dans sa fiche.

### Zones

Pleine terre, serre, châssis, balcon — ajoutez, renommez, supprimez. Chacune
porte un décalage en jours qui avance ou retarde tout le calendrier de ses
plantes. Il ne s'applique **jamais** à une date de votre journal : un fait
n'est pas une prévision.

### Arrosage

Deux réglages, et non un seul : **Suivre l'arrosage** fait exister l'eau dans
l'application, **Arroser** dans *Rappels · Quoi* décide si elle vous notifie. On
peut donc garder les échéances sous les yeux sans recevoir un message chaque
matin d'été.

Un bouton **Arrosé** sur chaque plante — dans « Aujourd'hui », sur sa carte, dans
sa fiche, et sur la carte Lovelace. C'est le geste le plus fréquent du potager :
il doit coûter un clic, jamais un formulaire. Quand plusieurs plantes attendent,
un bouton **Tout arroser** règle la tournée d'un coup.

Le calcul est **théorique, et assumé comme tel**. Il part de la fréquence
indiquée sur la fiche, et le compte à rebours repart quand *vous* déclarez avoir
arrosé. Rien n'observe le sol ni la météo : si vous décidez de ne pas arroser,
c'est votre affaire.

Quatre garde-fous évitent les rappels absurdes, parce qu'un rappel qu'on ignore
discrédite tous les autres :

| Règle | Pourquoi |
|---|---|
| Une plante pas encore en terre, terminée ou perdue ne réclame rien | Elle ne boit pas |
| Un semis boit deux fois plus souvent qu'un plant installé | La graine est en surface et ne pardonne pas un dessèchement |
| Pas de rappel en zone non abritée entre la première et la dernière gelée | Personne n'arrose son jardin en décembre |
| Une pérenne sobre en terre depuis plus de deux ans se tait | Les fiches le disent elles-mêmes : « aucun arrosage une fois établi » |

Une zone cochée **abritée** — serre, châssis, pots — sèche toute l'année : les
rappels y continuent l'hiver. La fréquence se règle plante par plante, et le
suivi s'éteint globalement depuis les réglages.

### Semis échelonnés

Semer des radis tous les quinze jours est le geste le plus répétitif d'un
potager, et celui qu'on oublie le plus sûrement. Réglez un intervalle sur une
plante et, à chaque échéance, un rappel propose d'ouvrir le lot suivant.

Ce lot devient une **plante à part entière**, avec son propre journal : deux
semis à trois semaines d'écart sont à deux stades différents, et les confondre
n'aurait aucun sens. Le parent cesse alors de réclamer, pour que la série ne se
dédouble pas. Les ressemis s'arrêtent d'eux-mêmes à la fermeture de la fenêtre
de semis — personne ne veut qu'on lui réclame des radis en décembre.

### Rotation des cultures

Au moment d'ajouter une plante, si la même famille botanique a occupé cette
zone récemment, un avertissement le signale — avec quoi, et en quelle année.

| Famille | Délai |
|---|---|
| Solanacées, Brassicacées | 4 ans |
| Apiacées, Cucurbitacées, Amaryllidacées, Amaranthacées | 3 ans |
| Astéracées, Fabacées | 2 ans |

L'avertissement ne bloque rien : c'est au jardinier de trancher. Les pérennes
sont écartées — un pommier n'entre pas dans une rotation, il occupe sa place
pour vingt ans.

### Mes fiches

Le catalogue livré ne contiendra jamais votre variété locale. Ajoutez-la :
nom, catégorie, exposition, eau, périodes **en mois** (comme sur un sachet de
graines) et durées du cycle. Ce sont ces durées qui permettent ensuite de
recalculer la récolte depuis votre date réelle de semis.

Vos fiches sont conservées dans le stockage de votre jardin, pas dans le
fichier livré : **une mise à jour de l'intégration ne les efface pas.** Elles
apparaissent dans le catalogue au milieu des autres, et une fiche utilisée par
une plante du jardin ne peut pas être supprimée par mégarde.

### Affichage

Masquer ou non les plantes terminées et perdues dans « Mon potager ». Elles
restent dans le journal et le calendrier : c'est l'historique du potager, il
ne s'efface pas.

## Configuration initiale

Deux réglages comptent vraiment.

**Vos dates de gelées.** Elles calent tout le calendrier. Le formulaire propose
des préselections climatiques (Ouest océanique, Nord et Est, Midi, Montagne) ;
vous pouvez aussi saisir vos dates au format `MM-JJ`. Aucune date n'est écrite
en dur dans le catalogue : tout est un décalage en jours par rapport à la
dernière gelée de printemps ou à la première gelée d'automne. C'est ce qui rend
le calendrier juste chez vous, et pas seulement en moyenne nationale.

**Les destinataires des rappels.** Choisissez vos applications mobiles : seuls
les services `notify.mobile_app_*` transportent des boutons d'action, et c'est
le bouton « C'est fait » qui remplit votre journal sans effort.

Tout cela se modifie ensuite depuis l'onglet **Réglages** du panneau.

## Le catalogue

172 cultures. Chaque fiche porte l'exposition, les besoins en eau, le sol,
l'espacement, la rusticité, les bons et mauvais voisins, des conseils, et ses
fenêtres culturales.

| Famille | Nombre |
|---|---|
| Feuilles | 38 |
| Aromatiques | 26 |
| Légumes-fruits | 21 |
| Racines et tubercules | 19 |
| Fruitiers | 15 |
| Petits fruits | 15 |
| Fleurs compagnes et engrais verts | 14 |
| Bulbes | 10 |
| Gousses | 10 |
| Céréales et graines | 4 |

**65 sont vivaces** : plantées une fois, elles reviennent seules. Six d'entre
elles se récoltent quasiment toute l'année — poireau perpétuel, chou
Daubenton, roquette vivace, thym, romarin, laurier. Le catalogue se filtre sur
ce critère : `🔁 Vivace`, `♾️ Récolte toute l'année`, `↻ Annuelle`.

Le parti pris : une fiche par culture ayant **son propre calendrier**, et non
par variété. La tomate cerise est là parce qu'elle mûrit nettement plus tôt
qu'une cœur de bœuf ; une « carotte de Colmar » n'apporterait rien qu'une
correction de fiche ne règle mieux.

Le catalogue est **embarqué** : aucune API, aucun compte, aucun service externe
susceptible de disparaître. Il est extensible depuis le panneau (voir
[Mes fiches](#mes-fiches)). Les API publiques du domaine ont d'ailleurs mal
vieilli — OpenFarm est mort, Growstuff n'a jamais eu d'API officielle, et
Permapeople ne fournit pas de calendrier de semis.

Une culture gélive voit sa fenêtre de récolte plafonnée à la première gelée :
une courgette ne se récolte pas en janvier.

Le catalogue existe **dans les deux langues** : les 172 noms, les 36 familles,
les descriptions de sol, les notes d'arrosage et les 318 conseils sont
traduits. Le français reste la version de référence — c'est lui qui sert de
clé, notamment pour le délai de rotation d'une famille — et la construction du
catalogue échoue si une fiche arrive sans sa traduction, plutôt que de la
laisser passer en français au milieu d'une interface anglaise.

La recherche, elle, interroge les deux langues quelle que soit celle affichée :
« courgette » trouve la courgette sur une interface anglaise, « leek » trouve
le poireau sur une interface française.

### Peut-on s'y fier ?

Autant le dire franchement : **ces 172 fiches n'ont été confrontées à aucune
base de référence.** Les API du domaine n'offrent pas ce qu'il faudrait —
OpenFarm est mort, Growstuff n'a pas d'API officielle, et Permapeople ne
fournit pas de calendriers de semis. Le catalogue a donc été écrit de mémoire
horticole.

Trois garde-fous compensent, par ordre d'efficacité.

**Le réel prime, toujours.** Dès que vous notez un semis, l'estimation ne sert
plus : la récolte se calcule depuis votre date. Mes chiffres ne pilotent que la
première saison d'une culture donnée — ensuite c'est votre jardin qui parle.
C'est la raison d'être du suivi réel.

**Vous pouvez corriger n'importe quelle fiche**, y compris livrée, depuis le
catalogue. Vos valeurs remplacent les miennes et les plantes déjà au jardin
suivent la correction.

**Un audit de cohérence** passe les 172 fiches au crible :

```bash
python3 tools/auditer_catalogue.py
```

Il ne peut pas dire qu'une fiche est *juste* — il n'a aucune source de vérité.
Il dit qu'elle est *impossible*, ce qui est déjà beaucoup : une gélive semée
après les gelées, une récolte qui précède son semis, un arbre espacé de trente
centimètres, des durées de cycle qui se contredisent. Huit règles, toutes
vérifiables sans connaissance extérieure. **Au dernier passage : 0 impossible,
0 douteuse.**

**La traduction anglaise n'est pas plus sourcée que l'original**, et ne lui
ajoute aucune autorité : c'est le même contenu, dans une autre langue. Le nom
latin reste sur chaque fiche pour trancher quand le nom commun est ambigu.

Ce qui reste hors de portée, ce sont les durées de cycle — elles varient de
plusieurs semaines selon la variété, et seul un relevé au jardin peut trancher.
C'est précisément ce que la correction de fiche permet de rattraper.

### Ajouter une culture

Les fiches vivent dans une table compacte, une ligne par culture :

```bash
$EDITOR tools/catalogue_source.py
python3 tools/build_catalog.py     # valide puis régénère data/catalog.json
```

La validation refuse une fiche dont la récolte ne serait pas calculable, dont un
compagnon n'existe pas, ou à qui il manque `rusticite.gel`.

## Services

| Service | Effet |
|---|---|
| `rhizome.ajouter_plante` | Ajoute une culture au jardin |
| `rhizome.retirer_plante` | La retire, avec son journal |
| `rhizome.marquer_seme` | Semis à sa date réelle (`mode` : `direct` ou `interieur`) |
| `rhizome.marquer_repique` | Mise en place |
| `rhizome.marquer_recolte` | Récolte, avec `quantite_g` facultatif |
| `rhizome.marquer_perdu` | Perte, avec sa `cause` |
| `rhizome.marquer_termine` | Clôt la culture |
| `rhizome.marquer_arrose` | Note un arrosage ; le compte à rebours repart de là |
| `rhizome.ressemer` | Ouvre le lot suivant d'un semis échelonné |
| `rhizome.annuler_dernier_evenement` | Défait la dernière entrée du journal |
| `rhizome.rafraichir` | Recalcule tout de suite |

## Exemples d'automatisation

Syntaxe moderne (`triggers:` / `conditions:` / `actions:`).

**Couper tous les rappels pendant les vacances** — chaque plante a son
interrupteur :

```yaml
alias: Potager en vacances
triggers:
  - trigger: calendar
    entity_id: calendar.vacances
    event: start
actions:
  - action: switch.turn_off
    target:
      entity_id: >
        {{ states.switch
           | selectattr('entity_id', 'search', '^switch.rhizome_rappels_')
           | map(attribute='entity_id') | list }}
```

**Annoncer la tournée du matin sur une enceinte**, seulement s'il y a quelque
chose à faire :

```yaml
alias: Le potager du matin
triggers:
  - trigger: time
    at: "07:30:00"
conditions:
  - condition: numeric_state
    entity_id: sensor.rhizome_actions_a_mener
    above: 0
actions:
  - action: tts.speak
    target:
      entity_id: tts.piper
    data:
      media_player_entity_id: media_player.cuisine
      message: >
        {{ states('sensor.rhizome_actions_a_mener') }} choses au potager :
        {{ state_attr('sensor.rhizome_actions_a_mener', 'actions')
           | map(attribute='plante') | join(', ') }}.
```

**Noter l'arrosage depuis une vanne connectée** — l'uid est dans les attributs
du capteur de la plante :

```yaml
alias: La vanne du potager note son arrosage
triggers:
  - trigger: state
    entity_id: switch.vanne_potager
    to: "off"
actions:
  - action: rhizome.marquer_arrose
    data:
      entity_id: sensor.rhizome_tomate
      note: arrosage automatique
```

**Alerter quand une récolte s'ouvre**, sans attendre le rappel quotidien :

```yaml
alias: Une récolte commence
triggers:
  - trigger: state
    entity_id: sensor.rhizome_tomate
    to: En récolte
actions:
  - action: notify.persistent_notification
    data:
      title: 🍅 Première tomate
      message: >
        Semée le {{ state_attr('sensor.rhizome_tomate', 'date_semis') }}.
```

Une carte minimale qui liste ce qu'il y a à faire, sans la carte dédiée :

```yaml
type: markdown
content: >
  {% for a in state_attr('sensor.rhizome_actions_a_mener', 'actions') %}
  - {{ a.emoji }} **{{ a.action }}** : {{ a.plante }} ({{ a.zone }}) —
    {{ 'maintenant' if a.en_cours else 'dans ' ~ a.jours_restants ~ ' j' }}
  {% else %}
  Rien à faire aujourd'hui.
  {% endfor %}
```

## Développement

Toute la batterie, en une commande. Le script monte l'environnement au besoin
(il lui faut [uv](https://docs.astral.sh/uv/)) :

```bash
./scripts/verifier.sh
```

Elle enchaîne `unittest` sur les modules purs, l'audit du catalogue, `ruff`,
`mypy`, et `pytest` sur la couche Home Assistant avec la couverture.

Les quatre modules purs — `lifecycle.py` (le journal), `phenology.py` (le
calcul des étapes), `rotation.py` et `watering.py` — n'importent rien de Home
Assistant. Ils se vérifient donc sur n'importe quel poste, sans rien
installer :

```bash
PYTHONPATH=tests python3 -m unittest discover -s tests -p 'test_*.py'
```

Les tests de la couche Home Assistant vivent à part, dans `tests/ha/`, et
demandent Python 3.14 et `pytest-homeassistant-custom-component`.

Le panneau et la carte se vérifient sans instance :

```bash
python3 tools/banc_fixture.py && python3 -m http.server 8777
# http://localhost:8777/tools/banc.html        — le panneau, six vues
# http://localhost:8777/tools/banc-carte.html  — la carte Lovelace
```

Les données du banc sortent du vrai catalogue et du vrai moteur : il montre donc
le panneau face à ce qu'il recevra réellement.

Le banc se monte dans l'une ou l'autre langue, et c'est le seul moyen rapide de
voir un libellé resté en français — il ne se remarque pas en relisant la table
des textes :

```bash
python3 tools/banc_fixture.py en   # puis recharger le banc
python3 tools/banc_fixture.py      # retour au français
```

> **Son angle mort.** `tools/banc_fixture.py` réimplémente à la main la
> sérialisation que fait `websocket.py`. Sa promesse ne tient que tant que les
> deux ne divergent pas — c'est ce qui lui avait fait montrer un arrosage par
> plante qui fonctionnait alors qu'il était cassé en production. Les tests de
> `tests/ha/test_websocket.py` tapent, eux, sur les vraies commandes.

`CONTRIBUTING.md` détaille les conventions et les sept invariants à ne pas
casser.

## Vie privée

Rhizome est **local de bout en bout**. Ce n'est pas une intention, c'est une
propriété vérifiable :

- `manifest.json` ne déclare **aucune dépendance** (`"requirements": []`) ;
- le code n'embarque aucun client HTTP et ne fait aucun appel sortant ;
- le catalogue des 172 cultures est **livré avec l'intégration** : aucune API à
  interroger, aucun compte, aucun service susceptible de disparaître ;
- rien ne demande votre position. Les gelées se saisissent, ou se choisissent
  dans une préselection climatique.

**Ce qui est stocké chez vous** : le jardin — plantes, journal, arrosages,
fiches personnelles, zones — dans `.storage/rhizome.jardin`, et les réglages
dans l'entrée de configuration. Comme tout `.storage`, cela entre dans vos
sauvegardes Home Assistant.

**Ce qui sort** : uniquement le contenu des rappels, vers les services `notify`
que vous avez choisis — donc vers votre propre application Home Assistant.

**Les diagnostics** téléchargeables depuis la page de l'intégration décrivent la
forme du jardin, pas son contenu : surnoms, notes du journal, causes de perte et
noms d'appareils en sont retirés. Vous pouvez les joindre à une issue sans les
relire.

Pour le périmètre de sécurité et le signalement d'une faille, voir
[`SECURITY.md`](SECURITY.md).

## Dépannage

**Activer les logs de débogage** — `configuration.yaml`, puis redémarrer :

```yaml
logger:
  default: warning
  logs:
    custom_components.rhizome: debug
```

Ou, sans redémarrer, depuis **Paramètres → Appareils et services → Rhizome →
menu ⋮ → Activer la journalisation de débogage**.

| Symptôme | Piste |
|---|---|
| **Le panneau n'apparaît pas dans la barre latérale** | Videz le cache du navigateur (Ctrl-Maj-R). Le bundle est servi sans cache, mais le service worker de Home Assistant, lui, en garde un. |
| **La carte affiche « Capteur du potager introuvable »** | L'intégration n'est pas chargée, ou la ressource Lovelace pointe encore vers `/potager-frontend/`. Voir [La carte Lovelace](#la-carte-lovelace). |
| **Aucun rappel ne part** | Trois causes, dans l'ordre : aucun destinataire coché dans *Réglages · Rappels · À qui* ; l'étape concernée décochée dans *Quoi* ; ou l'interrupteur de rappels de la plante sur `off`. La vérification n'a lieu qu'une fois par jour, à l'heure réglée. |
| **Les rappels partent à la mauvaise heure** | Vérifiez le fuseau de Home Assistant dans *Paramètres → Système → Général*. Rhizome suit celui-là, pas celui de la machine. |
| **Les dates du calendrier sont fausses de plusieurs semaines** | Ce sont vos gelées. Un préréglage trop large décale tout le calendrier ; saisissez vos dates réelles. |
| **Une plante réclame un semis déjà fait** | Son journal est vide. Notez le semis — par le bouton d'un rappel, la case de `todo.rhizome`, ou le bouton « Fait » — et la suite du cycle se recalcule. |
| **Une récolte est annoncée en plein hiver** | Si la culture n'est pas gélive, c'est normal. Sinon, c'est une durée de cycle de la fiche qui ne correspond pas à votre jardin : corrigez-la depuis le catalogue. |
| **Après un `git pull`, rien n'a changé sur l'instance** | HACS installe des *releases*, pas la branche. Il faut publier une version. |

Si rien de tout cela ne colle, ouvrez une
[anomalie](https://github.com/MaximeRiviere56/ha-rhizome/issues/new/choose) avec
les logs et les diagnostics.

## Questions fréquentes

**Faut-il un compte, une clé d'API, une connexion ?**
Non. Voir [Vie privée](#vie-privée).

**Ça marche hors de France ?**
Oui. Rien n'est calé sur un calendrier national : tout part de vos deux dates
de gelées. Les quatre préréglages climatiques sont français, mais les dates se
saisissent à la main, et l'interface comme le catalogue existent en anglais
(voir [Langue](#langue)).

**Changer de langue casse-t-il mes automatisations ?**
Non pour celles qui visent une entité : les `entity_id` sont figés à la
création et ne bougent pas. Oui, potentiellement, pour celles qui comparent
l'**état** d'un capteur de plante à un texte (`Semé`, `En récolte`) : cet état
suit la langue. L'historique garde les anciens libellés avant le changement.

**Puis-je avoir plusieurs jardins ?**
Non, une seule entrée par instance. Les **zones** jouent ce rôle : chacune
porte son propre décalage de calendrier.

**Une mise à jour efface-t-elle mes fiches personnelles ?**
Non. Elles vivent dans le stockage du jardin, pas dans le fichier livré.

**Peut-on corriger une fiche livrée ?**
Oui, depuis le catalogue. Votre version remplace la mienne, et les plantes déjà
au jardin suivent la correction. Un bouton **Rétablir** rend l'originale.

**Que se passe-t-il si je supprime l'intégration ?**
Le jardin reste sur disque. Le réinstaller le retrouve. Supprimer une plante
depuis le panneau, en revanche, supprime son journal.

**Pourquoi l'arrosage ne regarde-t-il pas la météo ?**
Parce que le modèle serait faux sans capteur d'humidité du sol, et qu'un
rappel faux discrédite tous les autres. Le compte à rebours repart quand
*vous* dites avoir arrosé. Brancher l'alerte gel sur l'entité météo est en
revanche une piste ouverte.

## Limites connues

Dites franchement, pour qu'elles ne soient pas découvertes en juillet.

- **Les 172 fiches ne sont sourcées nulle part** — voir
  [Peut-on s'y fier ?](#peut-on-sy-fier). Les durées de cycle sont ce qu'il y
  a de plus approximatif, et ce que la correction de fiche rattrape le mieux.
- **Un seul jardin par instance.**
- **Aucune plante d'intérieur**, malgré le nom. Il anticipe, il ne décrit pas.
- **Les quantités récoltées se saisissent à la main**, en grammes, et rien
  n'oblige à les peser.
- **L'arrosage est théorique** : rien n'observe le sol, la pluie ni la
  température.
- **Pas de capteur de gel.** L'entité météo n'est pas lue, alors que chaque
  fiche porte sa rusticité.
- **Aucun export du journal** pour l'instant.
- **Deux langues, et pas une de plus.** Français et anglais. En ajouter une
  demande de remplir `i18n.py`, les deux tables du frontend et
  `tools/catalogue_traductions.py` — le catalogue est le gros du travail.
- **Vos propres textes ne sont jamais traduits** : surnoms, noms de zones,
  fiches personnelles, notes du journal. C'est délibéré, ce sont des données.
- **Minimum Home Assistant 2026.10.** Rien n'est testé en dessous.

## Contribuer

Les conventions, les sept invariants à ne pas casser et la façon de vérifier
sont dans [`CONTRIBUTING.md`](CONTRIBUTING.md). Une correction de fiche du
catalogue est particulièrement bienvenue : il y a un
[gabarit d'issue](https://github.com/MaximeRiviere56/ha-rhizome/issues/new/choose)
pour ça.

## Changelog

Chaque version est décrite dans [`CHANGELOG.md`](CHANGELOG.md) et publiée en
[release GitHub](https://github.com/MaximeRiviere56/ha-rhizome/releases).

## Licence

MIT — voir [`LICENSE`](LICENSE).

