# Journal des versions

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Versions sous [SemVer](https://semver.org/lang/fr/). Rhizome est en `0.x` :
l'intérieur peut encore bouger, mais pas vos données.

## Non publié

Rhizome tient enfin ce que son nom promettait : des plantes d'intérieur à côté
du potager. Et l'arrosage, qui se lisait mal — un bouton bleu « Arrosé » qui ne
disait pas s'il constatait ou commandait, et des arrosages notés nulle part de
visible.

### Ajouté

- **43 fiches, et le catalogue passe de 172 à 215 cultures.** 21 médicinales
  et comestibles sauvages — achillée, plantain, ortie, millepertuis, aubépine,
  reine-des-prés, guimauve, échinacée, valériane, pissenlit, bardane,
  bouillon-blanc, prêle, tanaisie, absinthe, menthe poivrée, tilleul,
  églantier, onagre, passiflore, camomille matricaire — et 22 plantes
  d'intérieur : monstera, pothos, philodendron, spathiphyllum, zamioculcas,
  dieffenbachia, sansevieria, dragonnier, aspidistra, phalangère, calathea,
  maranta, pilea, peperomia, hoya, fougère nid d'oiseau, kentia, phalaenopsis,
  aloe vera, crassula, ficus elastica, ficus lyrata. Deux catégories nouvelles
  dans le panneau, `Médicinales` et `Plantes d'intérieur`, filtrables comme
  les autres.
- **Les plantes d'intérieur n'ont pas de calendrier, et c'est voulu.** Toutes
  les fenêtres du catalogue sont des décalages par rapport à vos gelées ; une
  plante qui vit à vingt degrés toute l'année n'en connaît pas. Leur inventer
  une plantation et une récolte aurait annoncé la récolte d'un monstera au
  5 juillet. Leur fiche porte la lumière, l'eau, le substrat, l'encombrement
  adulte, la toxicité et les conseils — et l'arrosage, qui est le seul
  mécanisme de Rhizome à ne pas dépendre des saisons.
- **Chaque fiche médicinale dit son risque en premier conseil** : toxicité,
  confusion dangereuse à la cueillette, interaction médicamenteuse connue.
  Aucune ne porte de posologie ni d'indication thérapeutique — Rhizome dit
  comment faire pousser une plante, jamais quoi en faire pour se soigner.
- **Ces 43 fiches sont les seules du catalogue à être sourcées** :
  monographies du HMPC de l'Agence européenne du médicament, bulletins de
  toxicovigilance de l'Anses, fiches de culture de la Royal Horticultural
  Society, base de l'ASPCA pour la toxicité envers chiens et chats. Les 172
  autres restent écrites de mémoire horticole, et la nuance est dite dans le
  README.
- **Les arrosages apparaissent au journal**, de la plante et du potager. Dans
  la fiche d'une plante, ils se mêlent aux étapes du cycle à leur date, sur un
  point bleu creux qui les distingue d'un semis ou d'une récolte — l'arrosage
  reste hors du cycle, il ne le fait pas avancer. Une série d'arrosages
  consécutifs tient en une ligne qui porte toutes ses dates, sinon un été
  d'arrosages noierait les cinq étapes de la plante. Dans la vue *Journal*,
  ils sont groupés par jour, filtrables comme les autres événements, et
  comptés dans le bilan.
- **Une pastille d'état d'arrosage**, à trois niveaux et trois icônes : en
  retard (alerte, orangé), dû aujourd'hui (arrosoir, bleu), à jour (coche,
  neutre). Elle remplace le texte libre dans le panneau comme dans la carte
  Lovelace.
- **Une confirmation après le clic** : la pastille passe au vert et dit
  « Arrosé · noté au journal » pendant quelques secondes. Le seul retour
  visible était jusqu'ici un compte à rebours qui repart, que personne ne
  remarque.

- **Une alerte gel, le soir, d'après votre météo.** Désignez une entité météo
  dans *Réglages · Alerte gel*, et Rhizome vous prévient à 18 h quand la nuit
  qui vient menace une plante. **Le seuil est celui de chaque fiche, pas zéro
  degré** : un aloe vera souffre à 10 °C quand un pommier tient −20 °C, donc
  une alerte unique « il gèle cette nuit » serait tardive pour l'un et inutile
  pour l'autre. Seules les plantes en terre et en zone non abritée sont
  concernées — une serre protège, et l'alerte le sait — et le message dit le
  geste : rentrer ce qui est en pot, voiler ce qui est en terre. Un seul
  message pour tout le jardin, une seule fois par nuit.
- **L'heure de l'alerte gel est un réglage à part**, à 18 h par défaut, et
  c'est délibéré : c'est la seule notification de Rhizome qui porte sur une
  échéance de quelques heures. Envoyée à 8 h avec les autres rappels, elle
  arriverait après la nuit qu'elle devait prévenir.

### Modifié

- **Une plante d'intérieur n'est plus privée de rappels d'arrosage l'hiver,
  ni passé deux ans.** Deux règles existaient pour que les rappels restent
  crédibles : rien en pleine terre entre les gelées, et rien pour une pérenne
  sobre installée depuis deux ans. Appliquées à une plante de salon, la
  première coupait les rappels de novembre à avril — la saison où elle sèche
  le plus vite, le chauffage abaissant l'humidité de l'air pendant qu'elle
  continue — et la seconde les coupait définitivement sur un sansevieria,
  dont les racines sont pourtant enfermées dans un litre de terreau. Les deux
  sont levées pour cette catégorie, d'après la fiche et non d'après la case
  « zone abritée » : la survie de la plante ne doit pas dépendre d'un réglage
  coché. Les règles restent entières pour le jardin.
- **Le bouton d'arrosage dit « Arroser », et non plus « Arrosé »** : un bouton
  porte le geste qu'il déclenche, l'état vit dans la pastille d'à côté. Il
  reste plein tant que l'eau est due et se fait discret une fois la plante à
  jour, pour que la couleur pleine ne signale que ce qui attend un geste.
- **Le panneau reçoit tout l'historique d'arrosage** d'une plante, et non plus
  ses vingt dernières entrées : le journal les affiche désormais à leur date,
  et une liste tronquée y ferait un trou sans le dire. Le stockage en borne
  déjà le nombre.

### Interne

- **La sérialisation envoyée au panneau vit dans un module pur**,
  `serialisation.py`. Elle était écrite dans `websocket.py`, qui importe Home
  Assistant : le banc d'essai, qui monte le frontend hors d'une instance, la
  réimplémentait donc à la main. Cette copie avait déjà montré un arrosage par
  plante qui fonctionnait au banc alors qu'il était cassé en production, et
  elle avait pris du retard sur un champ. Le banc appelle désormais le même
  code que l'instance, et cette sérialisation gagne dix tests qui n'étaient
  pas possibles auparavant.
- **Le banc d'essai sert une fiche de détail par culture**, et non plus
  toujours la même : toute la vue détail lui échappait. Son avertissement de
  rotation est de même calculé par le vrai module face à son propre jardin,
  au lieu d'annoncer des solanacées devant n'importe quelle fiche.

- **Le nom scientifique et la famille des 215 fiches sont croisés sur trois
  bases taxonomiques** — GBIF, World Flora Online et le Catalogue of Life — par
  `tools/revue_croisee.py`, rejouable à tout moment. La famille n'est pas un
  détail d'affichage : c'est elle qui pilote le délai de rotation, donc une
  famille fausse donne un mauvais conseil. 207 fiches confirmées, 8 divergences
  assumées et justifiées, 0 à vérifier. Le raisonnement complet est dans
  `docs/revue-croisee.md`.

- **Deux règles d'audit de plus sur les 215 fiches** : une culture gélive dont
  la mise en terre s'ouvre moins de quinze jours après la dernière gelée est
  signalée — la dernière gelée est une moyenne, et une année sur dix elle
  tombe après le 13 mai —, et une fréquence d'arrosage incohérente avec le
  besoin annoncé l'est aussi.

### Corrigé

- **Sept cultures gélives sortaient trop tôt.** Tomate et tomate cerise
  ouvraient leur plantation sept jours après la dernière gelée, cosmos,
  tournesol et oca le jour même. Toutes passent à quinze jours, la valeur que
  le catalogue appliquait déjà au reste de ses gélives. Annoncer « c'est le
  moment » à la date moyenne de dernière gelée, c'est se tromper une fois sur
  deux, et une tomate perdue ne se rattrape pas dans la saison.
- **Le poivron souffrait à 12 °C, pas à 10.** Ce n'est pas cosmétique depuis
  que l'alerte gel existe : `temp_min_c` la pilote, donc une valeur trop basse
  retardait l'avertissement. Il était par ailleurs le seul des solanacées de
  saison chaude sous les 12 °C.
- **Le sureau noir était rangé en Adoxacées.** *Viburnaceae* est le nom
  conservé depuis 2016 ; *Adoxaceae* n'a pas la priorité, et les quatre
  sources consultées sont d'accord.
- **La camomille matricaire portait un synonyme** : *Matricaria recutita* au
  lieu du nom accepté *Matricaria chamomilla*.
- **L'orchidée papillon portait « Phalaenopsis hybride »**, qui n'est pas un
  épithète. Ce qu'on achète est un hybride horticole sans nom d'espèce, et
  *Phalaenopsis* × hybr. le dit.
- **La fiche consoude ne disait rien de l'usage interne.** Livrée depuis la
  v0.6.0, elle est rangée en fleur compagne pour le purin, mais rien
  n'empêchait d'en faire une tisane : l'Agence européenne du médicament écarte
  l'usage interne, ses alcaloïdes pyrrolizidiniques étant toxiques pour le
  foie. La mise en garde y figure désormais.
- **Le panneau annonçait « Vivace — elle revient chaque année » sur une plante
  qui ne part jamais**, et « Craint le gel » là où le chiffre utile est le
  minimum thermique — c'est lui qui dit si la plante peut passer l'été dehors,
  et quand la rentrer.
- **« Je viens d'arroser », dans la fiche d'une plante, ne faisait rien.** La
  fiche se rend dans son propre hôte et seul le branchement de la vue écoutait
  le bouton : le clic partait dans le vide, sans erreur ni retour. Le défaut
  datait de l'ajout de l'arrosage et n'était visible que depuis la fiche.

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
