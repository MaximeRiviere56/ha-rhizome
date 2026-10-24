# Rhizome

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

## Développement

```bash
python3 -m unittest discover -s tests -p 'test_*.py'   # 94 tests, sans dépendance
```

`lifecycle.py` (le journal), `phenology.py` (le calcul des étapes),
`rotation.py` et `watering.py` n'importent rien de Home Assistant : ils sont testables hors
instance.

Le panneau et la carte se vérifient sans instance :

```bash
python3 tools/banc_fixture.py && python3 -m http.server 8777
# http://localhost:8777/tools/banc.html        — le panneau, cinq vues
# http://localhost:8777/tools/banc-carte.html  — la carte Lovelace
```

Les données du banc sortent du vrai catalogue et du vrai moteur : il montre donc
le panneau face à ce qu'il recevra réellement.

## Licence

MIT.
