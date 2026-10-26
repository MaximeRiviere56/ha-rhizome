# Journal des versions

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Versions sous [SemVer](https://semver.org/lang/fr/). Rhizome est en `0.x` :
l'intérieur peut encore bouger, mais pas vos données.

## [0.10.0] — 2026-10-25

Rhizome parle anglais. Interface, catalogue, rappels, calendrier, liste de
tâches et noms d'entités : tout ce que l'application affiche existe désormais
dans les deux langues, avec un réglage pour choisir.

Rien à migrer. Une installation existante ne change pas de langue : son Home
Assistant est en français, et le réglage vaut « Automatique » par défaut.

### Ajouté

- **Un réglage de langue**, dans *Réglages · Langue* du panneau et dans le flux
  de configuration : **Automatique** (défaut, suit Home Assistant), **Français**
  ou **English**.
- **Le catalogue en anglais** : les 172 noms de cultures, 36 familles, 13
  descriptions de sol, 148 notes d'arrosage et 318 conseils. Le français reste
  la version de référence — c'est lui qui sert de clé, notamment pour le délai
  de rotation d'une famille. `tools/build_catalog.py` **refuse de compiler** si
  une fiche arrive sans sa traduction : une culture ajoutée sans son anglais
  est rattrapée à la construction, pas chez l'utilisateur.
- **La recherche du catalogue interroge les deux langues**, quelle que soit
  celle affichée : « courgette » trouve la courgette sur une interface
  anglaise, « leek » trouve le poireau sur une interface française.
- **Le banc d'essai se monte dans les deux langues** :
  `python3 tools/banc_fixture.py en`. C'est le seul moyen rapide de voir un
  libellé resté en français — il ne se remarque pas en relisant la table.
- `custom_components/rhizome/i18n.py`, module pur : résolution de la langue,
  table des textes du serveur, formats de date. Ses tests vérifient ce qui est
  vérifiable mécaniquement — que les deux tables portent les mêmes clés, que
  les modèles attendent les mêmes variables, et qu'« auto » retombe toujours
  sur une langue connue.

### Modifié

- **Les noms affichés des entités suivent la langue** : « Actions à mener »
  devient « Tasks due », « Rappels Tomate » devient « Tomato reminders ». Les
  `entity_id`, eux, sont figés à la création de l'entité et **ne bougent
  pas** : vos automatisations survivent au changement de langue. Une
  installation créée en anglais les nomme en anglais dès le départ.
- **Le capteur de phase d'une plante traduit son état** (`Semé` → `Sown`)
  **et ses `options`** — traduire l'un sans l'autre rend une entité `enum`
  invalide à chaque changement d'état. Conséquence assumée : l'historique
  garde les anciens libellés avant le changement, et une automatisation qui
  compare cet état à un texte demande à être relue.
- **Les refus du moteur sont traduits.** Les modules purs ne connaissent aucun
  réglage : ils portent désormais leur message français *et* une clé, que la
  couche Home Assistant rend dans la langue de l'interface. Les deux
  sous-libellés d'un refus de transition (l'événement et la phase) sont
  traduits avec lui, sinon un refus anglais citerait « Semé ».
- **Les quatre zones livrées naissent dans la langue de l'installation.**
  Elles deviennent ensuite des données : changer de langue plus tard ne les
  renomme pas — ce serait effacer les noms que vous leur avez donnés.
- **Les dates suivent la langue** : « 15/04 » devient « Apr 15 ». « 15/04 » se
  lit « le 4 du quinzième mois » pour un anglophone.
- `catalog.valider_fiche` renvoie des clés de traduction et non des phrases :
  ces messages s'affichent dans le formulaire du panneau, donc dans la langue
  de l'interface.

### Corrigé

- **Les préréglages climatiques n'étaient jamais traduits.** Le flux de
  configuration posait un `label=` explicite sur chaque option, ce qui écrase
  la traduction : le bloc `selector.preset_climat` de `translations/en.json`
  existait depuis des versions sans que rien ne l'appelle, et le formulaire
  anglais affichait « Ouest océanique (Bretagne, Loire) ». Les options passent
  désormais par `translation_key`. Un test vérifie les deux sens — aucune clé
  employée sans traduction, aucune traduction orpheline.
- **La carte Lovelace trouvait son capteur par le nom de l'entité.** Elle
  cherchait le suffixe `_actions_a_mener`, ce qui ne tenait que tant que
  l'intégration était francophone : une installation créée en anglais nomme la
  même entité `sensor.rhizome_tasks_due`, et la carte restait vide sans rien
  signaler. La détection porte maintenant sur les attributs.

### Non traduit, délibérément

Vos propres textes : surnoms, noms de zones, fiches personnelles, notes du
journal. Ce sont des données, pas des libellés — et rien ne pourrait les
traduire. La traduction anglaise du catalogue, elle, **n'est pas plus sourcée
que l'original** et ne lui ajoute aucune autorité.

## [0.9.0] — 2026-10-25

Issu de deux passes d'audit de sécurité, de conformité Home Assistant et de
qualité menées le 25 octobre 2026 (voir `AUDIT.md`), sur Home Assistant
2026.10.4. Aucun changement cassant : rien à migrer, rien à reconfigurer.

### Sécurité — seconde passe

- **Le panneau échappe enfin les guillemets.** `echappe()` passait par le
  sérialiseur HTML, qui ne couvre que `&`, `<` et `>` : sans danger dans un
  nœud de texte, mais la fonction sert aussi à l'intérieur d'attributs — le
  surnom d'une plante, le nom d'une zone, le titre de la carte. Un surnom
  contenant un guillemet y fermait l'attribut et en ouvrait d'autres, ce qui
  permettait d'exécuter du code dans l'origine de Home Assistant, avec la
  session de qui regarde le panneau. Vérifié dans un navigateur.
- **Modifier le jardin demande désormais le droit d'écrire.** Onze commandes
  WebSocket — dont `retirer`, qui efface le journal d'une plante — étaient
  ouvertes à toute session authentifiée, y compris un jeton en lecture seule.
  Un compte ordinaire jardine, un compte en lecture seule consulte, et les
  commandes de lecture restent ouvertes à tous.
- **Rien d'illimité n'entre plus dans le stockage du jardin.** Un décalage de
  zone, une fréquence d'arrosage ou une date du journal démesurés étaient
  acceptés, persistés, et faisaient déborder le calcul de date à chaque cycle
  du coordinateur — une panne dont ni le rechargement ni le redémarrage ne
  sortaient. Même défaut que celui corrigé pour les réglages, par un autre
  chemin. Les bornes sont désormais posées à l'écriture, à la lecture, et une
  plante abîmée n'emporte plus les autres.
- **Le mode de semis et les textes libres sont bornés.** Le service le faisait
  déjà, la commande du panneau non : un surnom de cent mille caractères
  produisait un identifiant d'entité de cent mille caractères.

### Performance — seconde passe

- **La plage demandée au calendrier est bornée à dix années.** Elle venait du
  client sans limite, et chaque année de prévision se recalcule pour chaque
  plante dans la boucle d'événements : près d'une seconde de boucle bloquée
  pour cinq siècles et dix plantes.

### Sécurité — première passe

- **`rhizome/reglages/definir` exige désormais le rôle administrateur.** La
  commande écrit dans l'entrée de configuration sans l'avoir jamais réclamé :
  un client WebSocket muni d'un jeton **en lecture seule** pouvait rediriger
  les destinataires des rappels, ou poser une valeur qui paralyse le calcul.
- **Chaque réglage est typé avant d'être écrit.** `vol.Required("options"):
  dict` acceptait n'importe quoi ; seules les deux dates de gelées étaient
  vérifiées. Les destinataires de notification sont en plus confrontés à la
  liste réellement proposée.
- **L'identifiant de zone est contraint côté serveur.** Le panneau le dérivait
  d'un `slugifier()`, le serveur l'acceptait tel quel, et l'interpolait sans
  échappement dans un attribut HTML : injection possible par commande forgée.
- **Les fiches personnelles passent par un schéma**, avec des longueurs bornées.
  Rien ne limitait ce qui pouvait finir dans le stockage du jardin.

### Corrigé

- **Une option illisible ne met plus l'intégration hors service.** Un
  `rappel_jours` non numérique faisait remonter une `ValueError` brute depuis
  le calcul : le coordinateur échouait à chaque cycle, et l'option étant
  persistée, le redémarrage n'y changeait rien. Les lectures d'option
  retombent sur leur valeur par défaut, avec un avertissement.
- **Régler l'heure des rappels a enfin un effet.** Elle n'était lue qu'au
  démarrage, pour armer le minuteur ; la changer ne faisait rien jusqu'au
  redémarrage suivant, sans aucun signe.
- **Le bouton « Semé » d'un rappel de ressemis ne lève plus d'erreur.** La
  branche correspondante journalisait une variable qui n'y existe pas : une
  erreur attendue devenait une `UnboundLocalError` levée depuis le
  gestionnaire d'exception lui-même.
- **Retirer l'intégration retire son panneau.** L'entrée restait dans la barre
  latérale jusqu'au redémarrage et menait vers un panneau mort. Les onze
  actions `rhizome.*`, qui survivaient aussi, sont désormais enregistrées au
  démarrage de Home Assistant : l'éditeur d'automatisation les voit même quand
  l'intégration n'est pas chargée, et elles expliquent pourquoi au lieu de
  remonter une erreur 500 muette.
- **Un rappel n'est plus perdu quand son destinataire est injoignable.** Il
  était marqué « envoyé » avant de l'être.
- **Le stockage ne grossit plus indéfiniment.** La clé d'un rappel d'arrosage
  porte la date du jour : une entrée s'ajoutait par plante et par jour, et rien
  ne les retirait jamais. Vingt plantes produisaient de l'ordre de 7 000 clés
  par an. Elles sont maintenant oubliées dès qu'elles ne peuvent plus
  re-déclencher quoi que ce soit.
- **Les dates suivent le fuseau de Home Assistant**, et non celui de la machine
  qui l'héberge.

### Ajouté

- **Diagnostics** téléchargeables depuis la page de l'intégration. Ils
  décrivent la forme du jardin — plantes, phases, zones, réglages — sans vos
  surnoms, vos notes, vos causes de perte ni le nom de vos appareils.
- **Intégration continue** : `hassfest`, validation HACS, ruff, mypy et pytest
  à chaque poussée, plus une exécution hebdomadaire — une version de Home
  Assistant peut invalider un manifest sans qu'une ligne ait bougé. Actions
  épinglées par SHA, permissions minimales, dependabot.
- **`scripts/verifier.sh`**, qui monte l'environnement au besoin et enchaîne
  toute la batterie.
- **Tests de la couche Home Assistant** : montage, déchargement,
  rechargement, commandes WebSocket, rappels, diagnostics. Couverture passée
  de 61 % à 75 %.
- `SECURITY.md`, `CONTRIBUTING.md`, ce `CHANGELOG.md`, et des gabarits d'issue
  et de pull request.
- `icons.json` : les onze actions ont enfin une icône dans l'interface.

### Modifié

- **Les interrupteurs de rappel passent en catégorie « Configuration ».** Ils
  apparaissent désormais dans la section Configuration de l'appareil plutôt
  qu'au milieu des entités principales. **Leur `entity_id` ne change pas** et
  vos automatisations continuent de fonctionner.
- `manifest.json` déclare `single_config_entry` et `quality_scale: bronze`.
- Les attributs volatils ne sont plus archivés par le `recorder` : la liste des
  actions, celle des plantes à arroser, et la fiche de culture de chaque
  plante. Seule la phase est historisée — c'est elle qui raconte la saison.
- Le calcul tourne dans la boucle d'événements plutôt que dans un exécuteur.
  Mesuré à 0,84 ms pour cinquante plantes, soit moins que le coût du saut de
  thread, et la lecture concurrente disparaît.

### Aucun changement cassant

Aucune donnée n'est touchée, aucun `entity_id` ne change, aucune action n'est
renommée. Rien à migrer.

## [0.8.0] — 2026-10-24

L'arrosage par plante refonctionne, et son rappel se règle à part.

- `_plante_en_dict` définissait **deux fois** la clé `arrosage` : l'état
  calculé, puis les besoins de la culture, qui l'écrasaient. Le panneau n'avait
  jamais affiché d'échéance d'arrosage sur une plante.
- Le schéma de `rhizome/modifier` ne déclarait ni `arrosage_actif` ni
  `arrosage_frequence_jours`, que le panneau envoyait pourtant : les deux
  réglages d'eau par plante étaient morts.
- Nouveau réglage `notify_arrosage` : voir où en est l'eau sans recevoir une
  notification de plus chaque matin d'été.

## [0.7.0] — 2026-10-23

« Mon Potager » devient **Rhizome**, pour que le projet puisse un jour accueillir
les plantes d'intérieur à côté du jardin.

- Le domaine passe de `potager` à `rhizome`. Le jardin écrit sous l'ancienne
  clé de stockage est repris automatiquement au premier chargement, et l'ancien
  fichier est laissé intact.
- **Cassant** : les `entity_id`, les actions, la carte Lovelace et l'URL du
  panneau changent de préfixe. Voir la table de correspondance dans le README.

## [0.6.0] — 2026-10-23

Suivi de l'arrosage : fréquence par fiche, échéance par plante, bouton
« Arrosé », et quatre garde-fous pour que les rappels restent crédibles.

## [0.5.0] — 2026-10-22

Céréales, légumes perpétuels, et filtre annuelle / vivace.

## [0.4.0] — 2026-10-22

Le catalogue passe de 108 à 162 cultures.

## [0.3.0] — 2026-10-22

Semis échelonnés, avertissement de rotation des cultures, correction des fiches
livrées depuis le panneau.

## [0.2.1] — 2026-10-22

L'intégration embarque son logo.

## [0.2.0] — 2026-10-19

Onglet Réglages, catalogue extensible, calendrier réparé.

## [0.1.2] — 2026-10-19

La sauvegarde différée perdait le jardin au redémarrage. Toute mutation attend
désormais l'écriture sur disque.

## [0.1.1] — 2026-10-19

Premiers correctifs après mise en service.

## [0.1.0] — 2026-10-19

Première version : catalogue, jardin virtuel, panneau latéral, rappels.

[Non publié]: https://github.com/MaximeRiviere56/ha-rhizome/compare/v0.10.0...HEAD
[0.10.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.10.0
[0.9.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.9.0
[0.8.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.8.0
[0.7.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.7.0
[0.6.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.6.0
[0.5.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.5.0
[0.4.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.4.0
[0.3.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.3.0
[0.2.1]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.2.1
[0.2.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.2.0
[0.1.2]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.1.2
[0.1.1]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.1.1
[0.1.0]: https://github.com/MaximeRiviere56/ha-rhizome/releases/tag/v0.1.0
