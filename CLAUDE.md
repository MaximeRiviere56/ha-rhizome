# Rhizome — passation

Tu reprends une intégration Home Assistant personnalisée, `rhizome`, écrite de
zéro et déployée en production chez son unique utilisateur. Ce document te
donne ce qui ne se devine pas en lisant le code.

## Le produit

Un suivi de plantes dans Home Assistant : un catalogue de 215 cultures — dont
21 médicinales et 22 plantes d'intérieur —, un jardin virtuel, un panneau
latéral, des rappels, et un suivi d'arrosage.

**L'idée centrale, qui gouverne tout le reste : le calendrier est piloté par ce
qui s'est vraiment passé, pas par une moyenne saisonnière.** Dès qu'une date
réelle entre au journal, les étapes suivantes s'enchaînent depuis elle. Semer
trois semaines en retard décale la récolte d'autant, et une plante déjà semée
ne réclame plus jamais de la semer. Toute évolution doit préserver ça.

## Où

- Source : `~/Documents/apps/ha-rhizome`
- Dépôt : `https://github.com/MaximeRiviere56/ha-rhizome` (public)
- Déploiement : HACS en dépôt personnalisé → `/config/custom_components/rhizome/`
  sur l'instance. **Modifier les sources ne change rien chez l'utilisateur**
  tant qu'une release n'est pas publiée et téléchargée par HACS.

## Architecture

### Modules purs — aucun import Home Assistant, donc testables hors instance

| Module | Rôle |
|---|---|
| `lifecycle.py` | journal d'une plante, machine à états, transitions |
| `phenology.py` | calcul des étapes culturales, théoriques et recalculées |
| `rotation.py` | avertissement de rotation des cultures |
| `watering.py` | arrosage : fréquence, échéance, exclusions |
| `i18n.py` | langue de l'interface : résolution, textes du serveur, dates |
| `gel.py` | alerte gel : qui souffrira d'une température annoncée |
| `serialisation.py` | ce que le panneau reçoit : la vue calculée, mise en dictionnaires |

**C'est la convention la plus importante du projet.** Toute logique métier non
triviale va dans un module pur et arrive avec ses tests. Home Assistant ne peut
pas être exécuté sur le poste de développement : ces modules sont le seul filet.

### Couche Home Assistant

`__init__.py` (setup, panneau, services) · `config_flow.py` · `coordinator.py`
(`DataUpdateCoordinator`, vue calculée partagée) · `store.py` (persistance) ·
`catalog.py` (catalogue livré + fiches personnelles fusionnées) ·
`websocket.py` (API du panneau) · `notifier.py` · `sensor.py` `switch.py`
`calendar.py` `todo.py` · `frontend/rhizome-panel.js` et `rhizome-card.js`.

### Frontend

Web components natifs, **zéro étape de build**, zéro dépendance. Le fichier
servi est celui qu'on lit. Ne pas introduire de bundler.

## Invariants à ne pas casser

1. **Un fait du journal gagne toujours sur une fenêtre saisonnière.**
2. **Le décalage de zone ne s'applique jamais à une date réelle.** Une prévision
   se décale, un fait non.
3. **Aucune date en dur dans le catalogue.** Chaque fenêtre est un décalage en
   jours par rapport aux gelées locales de l'utilisateur. Seules les pérennes
   déclarent une récolte à date fixe.
4. **Semis à l'abri et plantation se déplacent ensemble.** Décaler l'un sans
   l'autre allonge silencieusement l'attente du plant en godet, et un plant
   qui attend file. C'est arrivé en décalant les gélives après les saints de
   glace : la tomate est passée de 75 à 88 jours entre semis et plantation
   avant que ce ne soit rattrapé. `auditer_catalogue.py` le rappelle, mais sa
   borne est large : elle attrape le grossier, pas la dérive.
5. **La phase se déduit toujours du journal par repli**, jamais stockée comme
   fait indépendant. C'est ce qui rend l'annulation fiable.
6. **Toute mutation passe par `coordinator.async_appliquer`**, qui écrit sur
   disque *et attend* avant de rendre la main. Une sauvegarde différée a déjà
   coûté un jardin entier au redémarrage.
7. **L'arrosage n'est pas un événement du journal.** Il ne fait pas avancer le
   cycle et se répète trop souvent : liste séparée `arrosages`.
8. **Un rappel qu'on ignore discrédite tous les autres.** Chaque garde-fou
   existant (plante pas en terre, hiver en pleine terre, pérenne installée)
   est là pour ça.

## Outillage — lis ceci avant de proposer quoi que ce soit

Le Mac a **Python 3.9.6 en système**, pas de Node, pas de pip utilisable —
mais **`uv` est installé**, ce qui change tout : un environnement réel se monte
en une minute, avec Python 3.14, Home Assistant et son harnais de test.

```bash
./scripts/verifier.sh          # tout, en montant l'environnement au besoin
./scripts/verifier.sh rapide   # seulement les modules purs, instantané
```

- **Modules purs** : `PYTHONPATH=tests python3 -m unittest discover -s tests
  -p 'test_*.py'`. 117 tests, zéro dépendance, Python du système.
- **Couche Home Assistant** : `tests/ha/`, sous `pytest` avec
  `pytest-homeassistant-custom-component`. Dossier séparé exprès, pour que la
  découverte `unittest` ne le voie pas.
- **Éviter la syntaxe Python 3.12+** dans les modules purs (`type X = ...`
  notamment) : c'est ce qui les garde vérifiables sans environnement, et la CI
  les exécute sur 3.9 **et** 3.14 pour que la promesse ne s'effrite pas.
- `hassfest` tourne en CI. En local il faut extraire `script/` du dépôt
  `home-assistant/core` au tag correspondant ; le détail est dans `AUDIT.md`.
- Le JavaScript se vérifie dans un navigateur ou au banc d'essai, pas par un
  linter.
- Git passe par HTTPS avec le jeton `gh` (aucune clé SSH sur ce poste).

## La langue

Le réglage `CONF_LANGUE` vaut `auto` (défaut), `fr` ou `en`. **Une seule langue
par installation**, résolue côté serveur par `coordinator.langue` : « auto »
suit `hass.config.language`. Le panneau ne décide rien — il reçoit la langue
résolue dans `rhizome/jardin` et `rhizome/reglages`. C'est ce qui empêche
l'incohérence la plus visible : des libellés anglais sur des noms de cultures
français.

Quatre endroits à tenir d'accord, et c'est tout :

| Où | Quoi |
|---|---|
| `i18n.py` | tout ce que le **serveur** produit : noms d'entités, rappels, calendrier, tâches, refus |
| `frontend/rhizome-panel.js`, table `TEXTES` | les libellés du **panneau** |
| `frontend/rhizome-card.js`, table `TEXTES` | les libellés de la **carte** |
| `tools/catalogue_traductions.py` | les **215 fiches** : noms, familles, sols, notes d'eau, conseils |

Trois règles qui ne se devinent pas :

1. **Le français est la clé, pas seulement une traduction.** `rotation.DELAIS`
   s'indexe sur le nom français de la famille botanique ; `catalog.localiser`
   substitue l'anglais à l'affichage et laisse l'original en place. Ne jamais
   traduire une clé.
2. **Les modules purs ne connaissent aucun réglage.** Ils rendent leur message
   en français *et* portent une clé (`ErreurJournal.cle`,
   `EtatArrosage.motif_cle`, `valider_fiche`) ; la couche Home Assistant
   traduit. C'est ce qui garde ces modules testables sans instance.
3. **Les `entity_id` ne changent jamais.** Les noms d'entités sont posés à
   l'instanciation (`_attr_name` dans `__init__`), pas par `translation_key` :
   Home Assistant dériverait sinon l'identifiant du nom traduit. Le nom
   affiché suit la langue, l'identifiant est figé à la création. C'est ce qui
   rend le réglage sans danger pour les automatisations — et c'est la réponse
   à la question laissée ouverte par l'audit du 25/10.

Ce qui n'est **jamais** traduit, et ne doit pas l'être : les surnoms, les noms
de zones après la première installation, les fiches personnelles, les notes du
journal. Ce sont des données.

Les garde-fous, dans l'ordre d'utilité :

- `tools/build_catalog.py` échoue si une fiche n'a pas sa traduction, et
  signale les traductions orphelines ;
- `tests/test_i18n.py` vérifie que les deux tables portent les mêmes clés et
  les mêmes variables ;
- `tests/ha/test_langue.py` monte une installation anglophone de bout en bout ;
- `python3 tools/banc_fixture.py en` monte le banc en anglais — **le seul
  moyen rapide de voir un libellé resté en français**, qui ne se remarque pas
  en relisant la table.

Les tests de `tests/ha/` forcent `hass.config.language = "fr"` : le harnais de
Home Assistant monte sinon une instance anglaise, et les suites qui vérifient
un libellé vérifieraient la traduction au lieu du comportement.

## Vérification

```bash
./scripts/verifier.sh                   # unittest, catalogue, ruff, mypy, pytest
python3 tools/build_catalog.py          # régénère data/catalog.json
python3 tools/banc_fixture.py && python3 -m http.server 8777
#   http://localhost:8777/tools/banc.html        — le panneau, six vues
#   http://localhost:8777/tools/banc-carte.html  — la carte Lovelace
```

Le **banc d'essai** monte le frontend hors de Home Assistant, avec un `hass`
factice alimenté par le vrai moteur et le vrai catalogue. Il a attrapé la
plupart des défauts réels du projet : libellés sans accents, récolte annoncée
en janvier pour une courgette, calendrier vide, « depuis 692 jours » sur un
pommier, lecture d'`entity_id` sur un objet qui ne le porte pas. **Utilise-le
systématiquement avant de publier.**

Le catalogue se modifie dans `tools/catalogue_source.py` (table compacte), pas
dans le JSON généré — **et sa traduction dans `tools/catalogue_traductions.py`**,
sans quoi `build_catalog.py` refuse de compiler.

## Honnêteté sur les données

Le catalogue a **deux régimes de confiance**, et la distinction se perd vite
si personne ne la tient. Vérifie à quelle moitié tu touches avant d'affirmer
quoi que ce soit sur une fiche.

**172 fiches n'ont été confrontées à aucune base de référence** — potagères,
aromatiques, fruitiers, fleurs compagnes, céréales — et leur traduction
anglaise pas davantage : c'est le même contenu dans une autre langue, pas une
seconde source. Les API du domaine ne fournissent pas de calendriers de semis
— OpenFarm est mort, Growstuff n'a pas d'API officielle, Permapeople ne couvre
pas les semis. Elles ont été écrites de mémoire horticole. **Ne présente
jamais ces données comme sourcées.**

**43 fiches sont sourcées** : les 21 médicinales et les 22 plantes
d'intérieur. Monographies HMPC de l'Agence européenne du médicament, bulletins
de toxicovigilance de l'Anses, fiches de culture de la RHS, base ASPCA pour la
toxicité envers les animaux. Les sources sont en tête de chaque section de
`tools/catalogue_source.py`, et leur détail dans la PR #8.

Pourquoi cette asymétrie est assumée plutôt que corrigée : sourcer les
médicinales était une nécessité de sûreté, pas un gain de qualité. Une fiche
muette sur une interaction médicamenteuse ou sur une confusion mortelle à la
cueillette peut nuire ; une durée de cycle approximative coûte au pire une
saison, et le réel la corrige dès le premier semis noté. Sourcer les 172
autres serait un travail utile, pas un travail urgent — et tant qu'il n'est
pas fait, ne laisse pas le sourçage des 43 déteindre sur elles dans un texte
destiné à l'utilisateur.

Deux règles non négociables sur les médicinales, tenues fiche par fiche :
**aucune posologie, aucune indication thérapeutique** — Rhizome dit comment
faire pousser une plante, jamais quoi en faire pour se soigner — et **le
risque dit en clair, toujours en premier conseil**. `tests/test_catalogue.py`
vérifie que chaque plante d'intérieur dit quelque chose de sa toxicité ; aucun
test ne peut vérifier que la réponse est juste, seulement que la question est
posée.

**La nomenclature est vérifiée, depuis la revue du 30/10/2026.** Le nom
scientifique et la famille des 215 fiches ont été croisés sur GBIF, World
Flora Online et le Catalogue of Life par `tools/revue_croisee.py` : 207
confirmées, 8 divergences assumées et justifiées dans le script lui-même, 0 à
vérifier. Trois fiches ont été corrigées. `docs/revue-croisee.md` porte le
raisonnement complet, y compris les synonymes horticoles délibérément
conservés — un utilisateur qui cherche « petit pois » ne doit pas tomber sur
*Lathyrus oleraceus*.

Deux choses à ne pas défaire là-dessus :

- **La table `DIVERGENCES_ASSUMEES` n'est pas une liste d'exceptions à
  nettoyer.** Chaque entrée est une décision prise, avec sa raison. La rouvrir
  demande de refaire le raisonnement, pas de supprimer la ligne. Sans elle
  l'outil signalerait huit fiches à chaque passage, et un audit qui échoue
  toujours est un audit que plus personne ne relance.
- **Les données de culture ont leur propre revue**, `tools/revue_horticole.py`,
  et elle est **partielle : 6 fiches sur 215**. Elle conserve des relevés
  sourcés à la main, faute d'API — OpenFarm est mort, Permapeople demande une
  clé, practicalplants ne répond plus, et je l'ai revérifié. `--tout` liste ce
  qui reste à voir. Ne présente jamais cette passe comme terminée.
- **Ne promets pas la même chose aux autres champs.** L'espacement, l'eau, les
  fenêtres et les durées de cycle ne sont pas vérifiables par une revue
  croisée : trois sources donnent trois chiffres pour une carotte, parce que
  la réponse dépend de la variété, du sol et du climat. Une revue y produirait
  une fourchette et la liste des désaccords, pas une vérité.

Trois atténuations valent pour tout le catalogue : le réel prime dès le
premier semis noté ; l'utilisateur peut corriger n'importe quelle fiche, y
compris livrée ; et `tools/auditer_catalogue.py` prouve qu'aucune fiche n'est
*impossible* (huit règles de cohérence interne). Les durées de cycle restent
hors de portée de toute vérification automatique.

## Les plantes d'intérieur

Elles sont le seul endroit où le modèle du potager ne s'applique pas, et la
tentation de les y ramener reviendra. Trois faits à ne pas défaire :

1. **Elles ne portent aucune fenêtre**, et `build_catalog.py` leur interdit
   d'en porter. Toutes les fenêtres du catalogue sont des décalages par
   rapport aux gelées locales (invariant 3) ; une plante qui vit à vingt
   degrés n'en connaît pas. Leur inventer une plantation et une récolte pour
   satisfaire le validateur annoncerait la récolte d'un monstera au 5 juillet.
2. **Elles échappent à deux exclusions d'arrosage** — l'hiver en zone
   découverte, et la pérenne installée depuis deux ans. Le signal est la
   catégorie de la fiche, jamais la case « zone abritée » : faire dépendre la
   survie de la plante d'un réglage coché par l'utilisateur était le mauvais
   choix. `watering.py` l'explique en tête, et quatre tests le verrouillent,
   dont un contre-exemple sur un pommier. Les deux symptômes sont silencieux
   et différés — plus aucun rappel, visible seulement en décembre ou deux ans
   après l'achat.
3. **`exposition` et `espacement_cm` changent de sens** : lumière vive
   indirecte plutôt que mi-ombre, encombrement adulte plutôt que distance de
   plantation. Documenté en tête de section, et non résolu par de nouvelles
   valeurs — qui auraient demandé de toucher les filtres du panneau et les
   deux tables de libellés pour un gain de vocabulaire seulement.

## Conventions

- Tout en français : code, commentaires, commits, documentation.
- **L'interface, elle, est bilingue depuis la v0.10.0** — et le français en
  reste la version de référence. Un texte affiché ne s'écrit plus en dur : il
  passe par `i18n.py` côté serveur, par la table `TEXTES` de chaque fichier du
  frontend, et par `tools/catalogue_traductions.py` pour le catalogue. Le
  détail est plus bas.
- Les commentaires disent **pourquoi**, pas quoi. Ceux qui expliquent un choix
  contre-intuitif ont de la valeur ; les autres non.
- Messages de commit : ce qui change, et le raisonnement derrière. Les défauts
  trouvés y sont consignés avec leur cause.
- Versionner à chaque livraison : bump `manifest.json`, tag, release GitHub avec
  des notes rédigées, puis `ha_manage_hacs` (update_information + download).

## Ce que tu ne fais pas sans accord explicite

`main` est protégée : pull request obligatoire, cinq contrôles verts
(`Modules purs (3.9)` et `(3.14)`, `ruff, mypy, pytest`, `hassfest`, `HACS`),
branche à jour avant fusion, ni force-push ni suppression. La règle s'applique
**aussi aux administrateurs**, donc à toi.

Mais la protection ne te distingue pas du propriétaire : tu agis avec son jeton
`gh`, et GitHub ne voit qu'un seul compte. Aucun réglage de permission ne peut
poser cette frontière — c'est cette convention qui la pose, et elle seule.

**Tu ouvres, tu surveilles, tu ne conclus pas :**

| Tu peux, sans demander | Tu demandes d'abord |
|---|---|
| pousser une branche de travail | **fusionner une PR dans `main`** |
| ouvrir une pull request, la rédiger | **taguer une version** |
| surveiller la CI et corriger ce qui casse | **publier une release GitHub** |
| lire l'instance (états, diagnostics, logs) | **déployer par HACS**, et *a fortiori* **redémarrer Home Assistant** |

Approuver une PR est **hors de ta portée, et doit le rester** : c'est le geste
par lequel le propriétaire dit qu'il a lu. Ne le contourne pas, ne propose pas
de le contourner, et ne désactive jamais la protection pour « débloquer » quoi
que ce soit — si une règle gêne, dis-le et laisse-le trancher.

Une sonde qui écrit n'est pas une sonde. `git push --dry-run` est purement
local et ne consulte aucune règle du serveur : pour vérifier une protection, on
relit son état par l'API, on ne pousse pas pour voir.

## Audits du 25 octobre 2026

Deux passes, toutes deux sur HA 2026.10.4, toutes deux **non publiées** : rien
n'est parti en release, donc rien n'a encore atteint l'instance.

**Première passe**, branche `audit/hardening-20261025`, **fusionnée dans
`main`** (commit `60b50b1`). Deux critiques reproduits en exécution :
`rhizome/reglages/definir` écrivait dans l'entrée de configuration sans exiger
d'administrateur ni typer ses entrées, et une option non numérique mettait le
coordinateur en panne de façon persistante. Couverture de 61 % à 91 %, mypy de
66 erreurs à zéro, CI mise en place.

**Seconde passe**, branche `audit/hardening-20261025-2`, **non fusionnée**.
Elle a trouvé ce que la première avait manqué, dans des zones qu'elle déclarait
saines :

- une **XSS stockée** dans le panneau — `echappe()` n'échappait pas les
  guillemets, et sert à l'intérieur d'attributs ;
- les **onze commandes d'écriture** du jardin n'exigeaient aucune autorisation,
  `retirer` compris ;
- la panne persistante du coordinateur **existait aussi par le stockage du
  jardin**, pas seulement par les réglages.

Les constats et leur suivi sont dans `AUDIT.md`, le détail des correctifs dans
`CHANGELOG.md`.

**Leçon pour la suite** : les deux passes ont trouvé la même classe de défaut
en trois endroits — une valeur non contrainte qui finit dans un calcul de date
et fige le coordinateur jusqu'à édition manuelle du stockage. Avant d'ajouter
un champ, demande-toi où il atterrit et ce qu'il devient dans
`date + timedelta(...)`.

Des deux décisions laissées au propriétaire en fin d'`AUDIT.md`, une est
tranchée : **les entités sont traduites depuis la v0.10.0**, mais par leur nom
affiché et non par une `translation_key`. Les `entity_id` d'une installation
existante ne bougent donc pas ; seule une installation créée en anglais les
nomme en anglais. Reste le passage de `voluptuous` à `probatio`, qui relèverait
le minimum à HA 2026.9 — et sur ce point Home Assistant a depuis écrit noir sur
blanc qu'une intégration peut garder l'ancien import aussi longtemps qu'elle
veut : rien ne presse.

## État au 26 octobre 2026

**v0.10.0 (bilingue) publiée, fusionnée dans `main`, et téléchargée par HACS
sur l'instance — mais pas encore active** : le propriétaire redémarrera Home
Assistant quand la maison sera calme. Jusque-là l'instance exécute la v0.9.0,
et le prochain redémarrage chargera la v0.10.0 tout seul. Si tu reprends après
ce redémarrage, c'est bien la v0.10.0 qui tourne.

La CI est verte sur la PR #3 — `hassfest`, validation HACS, et les modules purs
sur Python 3.9 **et** 3.14.

Avant : v0.9.0 (deux passes d'audit), puis v0.8.0. L'intégration s'appelait `potager` /
« Mon Potager » jusqu'à la v0.6.0 ; elle s'appelle `rhizome` / « Rhizome »
depuis la v0.7.0. Le nom a changé pour que le projet puisse accueillir les
plantes d'intérieur à côté du jardin — **et cette extension est faite depuis
la PR #8** : 22 fiches d'intérieur, dans une catégorie `plante-interieur` qui
ne porte aucune fenêtre.

Ce que le renommage a impliqué, et qu'il ne faut pas défaire :

- `STORAGE_KEY` vaut `rhizome.jardin`, et `store.py` adopte au premier
  chargement le `potager.jardin` écrit par les versions antérieures. L'ancien
  fichier est laissé intact. Cette reprise pourra disparaître le jour où plus
  aucune installation ne vient de « Mon Potager ».
- Le mot « potager » reste partout où il est un **nom commun** : la vue
  « Mon potager », les fiches du catalogue, les commentaires. Ne passe jamais
  un rechercher-remplacer global sur ce mot.

### Trois défauts de la v0.6.0, corrigés en v0.8.0

Ils datent tous de l'ajout de l'arrosage, et aucun n'était visible depuis le
poste de développement. À lire avant de toucher à cette zone :

- `_plante_en_dict` définissait **deux fois** la clé `arrosage` : l'état
  calculé, puis les besoins de la culture, qui l'écrasaient. Le panneau n'a
  jamais affiché d'échéance d'arrosage sur une plante. `tests/test_source.py`
  interdit désormais les clés dupliquées dans tout le paquet.
- Le schéma de `rhizome/modifier` ne déclarait ni `arrosage_actif` ni
  `arrosage_frequence_jours`, que le panneau envoyait pourtant. Les deux
  réglages d'eau par plante étaient morts, avec une erreur WebSocket.
- Rappeler l'arrosage n'avait pas de réglage propre : seul `arrosage_actif`
  existait, et il coupait le suivi entier. D'où `CONF_NOTIFY_ARROSAGE`,
  volontairement **hors** de `ETAPES_NOTIFIABLES` — l'arrosage n'est pas une
  étape du cycle (invariant 7), et une liste enregistrée avant ce réglage ne
  l'aurait pas contenu, taisant les rappels sans rien dire.

### L'angle mort du banc, comblé

`tools/banc_fixture.py` **réimplémentait à la main** la sérialisation que fait
`websocket.py`, parce que ce dernier importe Home Assistant. Le banc a donc
montré un arrosage par plante qui fonctionnait alors qu'il était cassé en
production, et sa copie avait déjà pris du retard : elle n'envoyait pas
`echelonnement_jours`.

C'est réparé. `serialisation.py` est un module pur, et le banc l'appelle au
lieu de le recopier — le panneau voit donc littéralement ce que l'instance lui
enverra. Le gain secondaire est que cette sérialisation devient testable par
le harnais rapide : `tests/test_serialisation.py`, dix tests, sans instance.

**Ne refais pas cette copie.** Si une donnée manque au banc, elle manque à
`serialisation.plante_en_dict`, et c'est là qu'il faut l'ajouter.

Deux réponses du banc étaient par ailleurs **uniques** là où l'instance les
calcule par culture : `rhizome/culture` servait la fiche de la tomate quelle
que soit la carte cliquée — toute la vue détail échappait donc au banc — et
`rhizome/rotation` annonçait des solanacées devant n'importe quelle fiche, un
peperomia compris. Les deux sont désormais indexées, et l'avertissement de
rotation sort du vrai module face au vrai jardin du banc. C'est pour cela
qu'une aubergine terminée y occupe la pleine terre : sans antécédent réel,
l'avertissement ne se déclencherait plus du tout et la vue perdrait sa
couverture.

Depuis l'audit du 25/10/2026, `tests/ha/test_websocket.py` tape sur les vraies
commandes et rejoue les trois défauts de la v0.6.0. Le banc garde sa valeur
pour l'œil, plus pour la preuve.

Son instance : HA 2026.10.2, Bouguenais (44), zone 9a, gelées 15/04 et 15/11,
notifications vers `notify.mobile_app_fairphone_6`. Une vue « Rhizome » a été
ajoutée à son tableau de bord `lovelace`, avec deux cartes `custom:rhizome-card`
et quatre tuiles de plantes **figées** (elles ne suivent pas les ajouts).

Pistes restantes, par ordre de valeur : arrosage réellement journalisé par
zone ; export du journal. Le propriétaire a écarté les deux pour l'instant.

L'**alerte gel est faite**. `gel.py` décide, le coordinateur lit la météo par
`weather.get_forecasts`, le notifieur envoie à 18 h. Trois choses à ne pas
défaire :

- **Le seuil est celui de la fiche, jamais zéro.** C'est ce qui justifie
  d'avoir 215 fiches : une alerte unique « il gèle » serait tardive pour un
  aloe vera (10 °C) et inutile pour un pommier (−20 °C).
- **Le second passage du soir est la raison d'être du réglage d'heure.**
  L'alerte gel est la seule notification qui porte sur une échéance de
  quelques heures ; la replier sur le passage de 8 h la rendrait inutile.
- **Une météo absente ou illisible rend `None`, et le notifieur se tait.**
  Inventer une valeur de repli ferait soit une alerte fausse, soit un silence
  qui coûte une plante — le mutisme est le seul comportement honnête.
