# Audit de Rhizome — 25 octobre 2026

Audit de sécurité, de conformité Home Assistant, de performance et de qualité,
mené sur `main` à la v0.8.0 (commit `6bbafb4`).

## Conditions de l'audit

Contrairement à ce que décrit `CLAUDE.md`, le poste dispose de `uv` : un
environnement réel a donc pu être monté, et **les constats ci-dessous sont
vérifiés en exécution**, pas déduits de la lecture.

| Outil | Version | Rôle |
|---|---|---|
| Python | 3.14.8 (via `uv`) | exigé par HA 2026.10 |
| `homeassistant` | 2026.10.4 | version du jour, celle de l'instance |
| `pytest-homeassistant-custom-component` | 0.13.375 | harnais apparié à 2026.10.4 |
| `ruff` | 0.17.2 | lint |
| `mypy` | 2.4.0 | typage |
| `script.hassfest` | extrait du tag `2026.10.4` de `home-assistant/core` | validation officielle |

### État de référence (avant correction)

| Vérification | Résultat |
|---|---|
| `python3 -m unittest` (modules purs) | **95 tests OK** |
| `pytest` (mêmes tests, avec `asyncio_mode=auto`) | 95 OK, 1 204 sous-tests |
| `pytest` sur la couche HA | **aucun test n'existe** |
| `hassfest` 2026.10.4 | **0 intégration invalide** |
| `ruff check` | **39 écarts** |
| `mypy --ignore-missing-imports` | **66 erreurs** |
| `mypy --strict` | **277 erreurs** |
| Validation HACS (`hacs/action`) | **non exécutable** : aucun workflow, non lançable hors CI |
| Couverture | **non mesurée** (aucune configuration) |

### Ce qui n'a pas pu être vérifié

- La **validation HACS officielle** (`hacs/action`) ne tourne que dans GitHub
  Actions. Les exigences structurelles ont été vérifiées à la main contre
  [la documentation HACS](https://www.hacs.xyz/docs/publish/integration/).
- Le **frontend** (3 130 lignes de JS) n'a ni linter ni test ici : pas de Node
  sur le poste. L'analyse est une relecture ciblée sur l'échappement.
- L'**exactitude agronomique** des 172 fiches reste hors de portée, comme le
  dit déjà le README. Rien dans cet audit ne la met en cause ni ne la valide.

---

## Constats

Sévérité : **C**ritique · **É**levé · **M**oyen · **F**aible.
« Vérifié » signale un constat reproduit en exécution sur HA 2026.10.4.

### Critique

#### C1 — Un utilisateur non-admin peut écrire n'importe quoi dans la configuration
`custom_components/rhizome/websocket.py:565-601` (`definir_reglages`)

La commande `rhizome/reglages/definir` appelle
`hass.config_entries.async_update_entry(...)`. Elle n'est protégée ni par
`@websocket_api.require_admin`, ni par un schéma : `vol.Required("options"): dict`
accepte n'importe quelle valeur, et seules les deux dates de gelées sont
validées. Toute modification d'une entrée de configuration est pourtant une
opération d'administration dans Home Assistant.

**Vérifié** : un client WebSocket authentifié avec un jeton **en lecture seule**
obtient `success: true` et persiste `rappel_jours: "abc"` dans `entry.options`.

**Impact** — deux escalades distinctes :
1. combiné à C2, mise hors service persistante de l'intégration ;
2. réécriture de `notify_targets`, donc redirection des notifications du jardin
   vers un service `notify.*` choisi par l'attaquant.

**Correctif prévu** : `require_admin` sur la commande, et un schéma voluptuous
typé par option plutôt qu'un `dict` libre.

#### C2 — Une option non numérique casse le coordinateur définitivement
`custom_components/rhizome/coordinator.py:93-94, 109-115, 118-121, 130-132, 135-138`

`rappel_jours`, `notify_recolte_recurrence` et les booléens sont lus par
`int(...)` / `bool(...)` sans garde. `_calculer` tourne dans un exécuteur et la
`ValueError` remonte brute à `_async_update_data`.

**Vérifié** : avec une plante au jardin et `rappel_jours: "abc"`,
`coordinator.last_update_success` passe à `False` et chaque cycle journalise
« Unexpected error fetching rhizome data ». L'option étant persistée dans
`.storage`, **l'état ne se répare pas tout seul** — ni au redémarrage, ni au
rechargement. Seule une édition manuelle du fichier de configuration le remet
d'aplomb.

**Correctif prévu** : une lecture d'option tolérante (repli sur le défaut +
log) et un schéma strict en entrée (C1), de sorte qu'une valeur invalide ne
puisse ni entrer ni paralyser le calcul.

### Élevé

#### É1 — `UnboundLocalError` dans le gestionnaire de bouton de notification
`custom_components/rhizome/notifier.py:325-342`

Dans la branche `ressemer`, `type_evt` n'est jamais lié ; le bloc
`except Exception` l'utilise pourtant dans son message de log. Une erreur
attendue (plante retirée, journal déjà avancé) se transforme donc en exception
levée **depuis le gestionnaire d'exception**, dans un écouteur du bus.

**Vérifié** : `UnboundLocalError` remontée sur un événement
`mobile_app_notification_action` de type `ressemer`.

**Correctif prévu** : journaliser le type d'étape, qui est toujours défini.

#### É2 — Le panneau, le chemin statique et les services survivent au déchargement
`custom_components/rhizome/__init__.py:188-192, 203-227, 247-339`

`async_unload_entry` décharge les plateformes et sauvegarde, mais ne retire ni
le panneau (`frontend.async_remove_panel`), ni les 11 services.

**Vérifié** : après `async_unload`, `rhizome` reste dans `hass.data[DATA_PANELS]`
et les 11 services `rhizome.*` répondent encore. Appelés, ils lèvent
`RuntimeError("Rhizome n'est pas charge.")`, soit une erreur 500 côté client.

**Correctif prévu** : retirer le panneau et les services au déchargement de la
dernière entrée ; passer l'enregistrement des services dans `async_setup` (voir
M3).

#### É3 — Changer l'heure des rappels n'a aucun effet
`custom_components/rhizome/__init__.py:195-197` · `notifier.py:92-102`

`RhizomeNotifier.async_demarrer` lit `CONF_NOTIFY_HEURE` une seule fois, au
démarrage, pour armer `async_track_time_change`. L'écouteur d'options
(`_async_options_modifiees`) se contente d'un `async_refresh()` : le minuteur
n'est jamais réarmé. L'utilisateur règle 21 h, les rappels continuent de partir
à 8 h jusqu'au prochain redémarrage, sans aucun signe.

**Correctif prévu** : `hass.config_entries.async_reload(entry.entry_id)` sur
changement d'options.

#### É4 — Croissance sans borne du stockage des rappels
`custom_components/rhizome/store.py:327-359` · `notifier.py:166`

La clé d'un rappel d'arrosage contient la date du jour :
`f"{uid}:arrosage:{aujourdhui_iso}"`. Une entrée s'ajoute donc **par plante et
par jour**, et `purger_notifs` ne s'exécute qu'au retrait d'une plante. Vingt
plantes suivies produisent de l'ordre de 7 000 clés par an, conservées
indéfiniment dans `.storage/rhizome.jardin`.

Les clés d'étape (`uid:type:debut`) s'accumulent aussi, saison après saison.

**Correctif prévu** : purge des entrées antérieures à une fenêtre de rétention
à chaque vérification quotidienne.

#### É5 — Aucune intégration continue
Racine du dépôt

Il n'existe pas de `.github/` : ni `hassfest`, ni validation HACS, ni ruff,
ni mypy, ni pytest, ni dependabot, ni templates d'issue/PR, ni `SECURITY.md`,
`CONTRIBUTING.md` ou `CHANGELOG.md`. Rien n'empêche aujourd'hui de publier une
release qui casse l'instance de l'utilisateur — ce qui s'est produit en v0.6.0,
comme le raconte `CLAUDE.md`.

**Correctif prévu** : workflows `hassfest` + `hacs/action` + qualité (ruff,
mypy, pytest), actions épinglées par SHA, permissions minimales, dependabot,
et les fichiers de publication manquants.

#### É6 — Aucun test de la couche Home Assistant
`tests/`

Les 95 tests portent exclusivement sur les quatre modules purs. Rien ne couvre
`config_flow`, `coordinator`, `store`, `websocket`, `notifier` ni les entités —
c'est-à-dire exactement la zone où vivent C1, C2, É1, É2 et É3. La règle Bronze
`config-flow-test-coverage` exige 100 % sur le config flow.

**Correctif prévu** : harnais `pytest-homeassistant-custom-component` et tests
de non-régression pour chaque correctif.

### Moyen

#### M1 — XSS stockée par l'identifiant de zone
`custom_components/rhizome/websocket.py:480-499` · `frontend/rhizome-panel.js:1475, 1681`

Le schéma de `rhizome/zones` accepte `vol.Required("id"): str`, sans contrainte.
Le panneau interpole ensuite cet identifiant **non échappé** dans un attribut :
`<option value="${z.id}" ...>`.

**Vérifié côté serveur** : `rhizome/zones` accepte et persiste
`id = '"><img src=x onerror=alert(1)>'`. Seule l'interface se protège, en
passant par `slugifier()` — le serveur, non.

**Correctif prévu** : contraindre l'identifiant côté serveur (motif
`[a-z0-9-]`), et échapper quand même côté panneau.

#### M2 — Destinataire de notification non vérifié
`custom_components/rhizome/notifier.py:216, 252, 286`

`cible.split(".", 1)[-1]` est passé tel quel comme nom de service `notify`,
sans vérifier qu'il existe ni qu'il figure dans la liste proposée. Le domaine
restant `notify`, la portée est bornée — mais couplé à C1, n'importe quel
service de notification devient atteignable.

#### M3 — Services enregistrés dans `async_setup_entry`
`custom_components/rhizome/__init__.py:173, 247`

La règle Bronze
[`action-setup`](https://contributors.home-assistant.io/core/quality-scale/rules/action-setup)
impose l'enregistrement dans `async_setup`, pour que les actions soient
connues même quand l'entrée n'est pas chargée.

#### M4 — `RuntimeError` au lieu d'une exception Home Assistant
`custom_components/rhizome/__init__.py:252-255`

`_coordinateur()` lève `RuntimeError` quand aucune entrée n'est chargée : le
client reçoit une 500 sans explication. Silver
[`action-exceptions`](https://contributors.home-assistant.io/core/quality-scale/rules/action-exceptions)
attend `ServiceValidationError` ou `HomeAssistantError`.

#### M5 — Fiche personnelle acceptée sans schéma
`custom_components/rhizome/websocket.py:605-625` · `websocket.py:744-822`

`vol.Required("fiche"): dict` laisse passer n'importe quelle structure.
`_normaliser_fiche` fait ensuite `int(brute.get("difficulte") or 1)` et
`c.strip()` sur chaque conseil : une chaîne non numérique ou un entier dans
`conseils` lève `ValueError` / `AttributeError`, que `_avec_coordinateur` ne
rattrape pas (il ne connaît qu'`ErreurJournal`) — erreur 500. Aucune borne de
longueur n'existe non plus sur `nom`, `conseils`, `sol` : le stockage peut
grossir sans limite.

#### M6 — `date.today()` au lieu du fuseau de Home Assistant
`coordinator.py:151` · `notifier.py:123, 311, 319, 327, 333` ·
`watering.py:130` · `rotation.py:61`

`date.today()` suit le fuseau de l'hôte. Home Assistant a le sien, réglable
indépendamment ; `homeassistant.util.dt.now().date()` est la forme attendue.
Sans incidence sur l'instance actuelle, mais faux pour qui décale son fuseau.

#### M7 — Pression inutile sur le recorder
`custom_components/rhizome/sensor.py:61-81, 146-163, 195-271`

Aucun `_unrecorded_attributes`. `ActionsSensor.actions`,
`ArrosageSensor.plantes` et la vingtaine d'attributs de chaque `PlanteSensor`
contiennent des valeurs qui changent chaque jour (`jours_restants`,
`arrosage_jours_restants`, `prochaine_date`…) ; tous sont écrits en base à
chaque changement d'état, pour un intérêt historique nul.

#### M8 — Entités et exceptions non traduites, pas d'`icons.json`
`sensor.py:48, 88, 133` · `switch.py:48-50` · `strings.json:…"entity": {}`

Noms d'entités codés en dur en français, aucun `translation_key`, bloc `entity`
vide dans `strings.json`, icônes posées par `_attr_icon` plutôt que par
`icons.json`. Trois règles Gold manquées : `entity-translations`,
`exception-translations`, `icon-translations`.

#### M9 — `manifest.json` incomplet au regard des usages actuels
`custom_components/rhizome/manifest.json`

Ni `quality_scale`, ni `single_config_entry: true` — ce dernier existe depuis
HA 2024.11 et remplacerait avantageusement la garde manuelle
`_async_current_entries()` de `config_flow.py:147`.

#### M10 — `voluptuous` : le shim de compatibilité n'est pas éternel
Tous les fichiers important `voluptuous as vol`

Depuis HA 2026.9, la validation tourne sur **probatio** ;
`homeassistant/__init__.py:11` appelle `probatio.compat.install_as_voluptuous()`
et le commentaire du code nomme explicitement les intégrations personnalisées
comme motif. Le runtime est donc correct aujourd'hui — **vérifié** :
`import voluptuous` rend `probatio._vol_shim`. Mais mypy, lui, voit le vrai
`voluptuous` : d'où 48 des 66 erreurs de typage, toutes sur les schémas.

#### M11 — Ni diagnostics, ni repairs
Fichiers absents

Deux règles Gold (`diagnostics`, `repair-issues`). Les diagnostics sont ici
particulièrement utiles : le journal du jardin est la seule donnée non
reconstituable du projet.

#### M12 — Convention fragile sur `unique_id`
`custom_components/rhizome/__init__.py:140-146`

`_resoudre_uid` décompose `entree.unique_id.split("_")` et exige exactement
trois morceaux. La convention `<entry_id>_<uid>_<suffixe>` tient parce que
`entry_id` est un ULID sans tiret bas et que les suffixes actuels (`etat`,
`notifs`) n'en contiennent pas. Rien ne le garantit ni ne le teste.

### Faible

| # | Fichier | Constat |
|---|---|---|
| F1 | 7 fichiers | `ruff` : 39 écarts — imports non triés (×6), `noqa` inutiles (×11), `RUF012`, imports morts dans `tests/test_rotation.py:11`, `B023` dans `tools/auditer_catalogue.py:89` |
| F2 | racine | Pas de `pyproject.toml` : aucune configuration de ruff, mypy ou pytest, donc aucune vérification reproductible |
| F3 | `translations/en.json` | `options.step.init.data_description` manquant ; `strings.json` déclare `selector.preset_climat`, que `config_flow.py:74-78` n'utilise pas (libellés codés en dur) |
| F4 | `README.md` | Un seul badge ; pas de section vie privée, dépannage, FAQ, contribution ni changelog ; « 94 tests » (95) et « cinq vues » (six) obsolètes |
| F5 | `hacs.json` | `homeassistant: "2025.10.0"` sous-estime le vrai minimum (`entry.runtime_data`, `async_register_static_paths`, `OptionsFlow` sans `config_entry`) |
| F6 | dépôt GitHub | Aucun topic déclaré : découvrabilité nulle dans HACS |
| F7 | `coordinator.py:148` | `_calculer` tourne dans un exécuteur et lit des structures mutées depuis la boucle : course possible, pour un calcul pur et rapide qui n'a rien à y gagner |
| F8 | `notifier.py:159` | `marquer_notif_envoyee` est appelé **avant** l'envoi : un échec perd le rappel définitivement |
| F9 | `CLAUDE.md:177`, `tools/banc_fixture.py:256`, `const.py:63` | Données personnelles mineures dans un dépôt public : commune de résidence, modèle de téléphone |
| F10 | `notifier.py:43` | Indentation cassée dans le bloc d'import |
| F11 | plateformes | Aucun `PARALLEL_UPDATES` (Silver `parallel-updates`) |

### Non-constats (vérifiés, rien à signaler)

- **Aucun secret** dans le dépôt (balayage clés/jetons/mots de passe).
- **Aucun appel réseau** : le projet est strictement local, sans `requirements`,
  sans client HTTP. SSRF, TLS et session partagée sont sans objet.
- **Aucune I/O bloquante** dans la boucle : `catalog.charger()` passe par
  `async_add_executor_job` et est mis en cache (`lru_cache`).
- **Échappement du frontend** : `echappe()` est appliqué à 53 endroits et couvre
  tous les textes libres (noms, surnoms, notes, causes, conseils, sols, noms de
  zone). Les seules interpolations nues portent sur des valeurs contraintes —
  identifiants de culture slugifiés, emojis tronqués à 4 caractères, uid
  hexadécimaux — sauf l'identifiant de zone (M1).
- **`hassfest` 2026.10.4 passe** sans aucun écart.
- **Pas de `requests`, pas de `time.sleep`, pas de désérialisation non sûre.**
- **`async_on_unload`** est correctement utilisé pour le notifier, l'écouteur
  d'options et l'écouteur `EVENT_HOMEASSISTANT_FINAL_WRITE`.

---

## Suivi des correctifs

Branche `audit/hardening-20261025`. Relire avec `git log main..` et
`git diff main...`.

| # | Sévérité | Statut | Commit |
|---|---|---|---|
| C1 | Critique | corrigé | `a04ea98` |
| C2 | Critique | corrigé | `a04ea98` |
| É1 | Élevé | corrigé | `5ccfa44` |
| É2 | Élevé | corrigé | `5ccfa44` |
| É3 | Élevé | corrigé | `5ccfa44` |
| É4 | Élevé | corrigé | `5ccfa44` |
| É5 | Élevé | corrigé | `8bbe769` |
| É6 | Élevé | corrigé | `86ad864`, `1fa12b0` |
| M1 | Moyen | corrigé | `a04ea98` |
| M2 | Moyen | corrigé | `a04ea98` |
| M3 | Moyen | corrigé | `5ccfa44` |
| M4 | Moyen | corrigé | `5ccfa44` |
| M5 | Moyen | corrigé | `253f30e` |
| M6 | Moyen | corrigé | `5ccfa44`, `253f30e`, `1c07ed6` |
| M7 | Moyen | corrigé | `2e93dd7` |
| M8 | Moyen | **partiel — décision requise** | `2e93dd7` |
| M9 | Moyen | corrigé | `2e93dd7` |
| M10 | Moyen | **contourné — décision requise** | `8bbe769` |
| M11 | Moyen | corrigé | `2e93dd7` |
| M12 | Moyen | corrigé | `1fa12b0` |
| F1 | Faible | corrigé | `86ad864` |
| F2 | Faible | corrigé | `86ad864` |
| F3 | Faible | corrigé | `2e93dd7` |
| F4 | Faible | corrigé | `8c6d703` |
| F5 | Faible | corrigé | `8bbe769` |
| F6 | Faible | corrigé — topics posés sur le dépôt (hors commit) |
| F7 | Faible | corrigé | `253f30e` |
| F8 | Faible | corrigé | `5ccfa44` |
| F9 | Faible | **non corrigé** — donnée du propriétaire, pas un défaut |
| F10 | Faible | corrigé | `86ad864` |
| F11 | Faible | corrigé | `2e93dd7` |

### Ce qui reste à décider

**M8 — traduction des entités (Gold `entity-translations`).** Essayée puis
retirée. Home Assistant construit l'`entity_id` à partir du nom **anglais** :
avec une `translation_key`, une nouvelle installation obtient
`sensor.rhizome_tasks_due` au lieu de `sensor.rhizome_actions_a_mener`. Les
installations existantes gardent leur identifiant, mais le README documente
ceux-là, et le projet est francophone. Le choix est entre la règle Gold et des
identifiants français : il appartient au propriétaire.

**M10 — `voluptuous` ou `probatio`.** Depuis 2026.9, Home Assistant valide
avec probatio et installe un shim qui répond aux `import voluptuous` des
intégrations personnalisées : **le code tourne juste aujourd'hui**, vérifié en
exécution. Les 60 erreurs mypy correspondantes sont tues par module, avec la
note expliquant quoi faire. Passer à `import probatio as vol` relèverait le
minimum à 2026.9 : c'est une décision de compatibilité.

**F6 — topics du dépôt.** Posés le 25/10/2026 : `home-assistant`, `hacs`,
`home-assistant-custom`, `gardening`, `garden`, `potager`, `plants`, `python`.
C'est une métadonnée GitHub, pas un fichier du dépôt : `hacs/action` la vérifie
et refusait la validation sans elle.

**Clé `categories` du manifest.** `hacs/action` la réclame en avertissement, et
`garden_plants` conviendrait exactement. Elle a été ajoutée puis retirée : le
`hassfest` de 2026.10.4 — la version qui tourne sur l'instance — ne connaît pas
encore cette clé et refuse le manifest. À reprendre quand le minimum supporté
aura dépassé la version qui l'introduit. Optionnelle pour une intégration
personnalisée.

**F9 — données personnelles.** La commune de résidence et le modèle de
téléphone sont dans `CLAUDE.md`, `tools/banc_fixture.py` et un commentaire de
`const.py`. Ce sont les données du propriétaire dans son propre dépôt public :
à lui de juger. Aucun secret n'a été trouvé, donc aucune rotation à prévoir.

---

# Seconde passe — 25 octobre 2026

Menée sur `main` après fusion de la première passe (commit `60b50b1`), sur la
même instance : HA 2026.10.4, Python 3.14.8, `pytest-homeassistant-custom-
component`, ruff, mypy, et `script.hassfest` extrait du tag `2026.10.4`.

Branche `audit/hardening-20261025-2`.

### Lancer `hassfest` en local

`CLAUDE.md` renvoyait ici sans donner la marche à suivre. Deux pièges :
`script/hassfest` importe `script.translations`, donc il faut **tout
`script/`** et non le seul sous-dossier ; et il ne faut surtout **pas**
récupérer `homeassistant/`, dont la copie partielle masquerait le paquet
installé (`ModuleNotFoundError: homeassistant.generated`).

```bash
git clone --depth 1 --branch 2026.10.4 --filter=blob:none --sparse \
  https://github.com/home-assistant/core.git /tmp/core
git -C /tmp/core sparse-checkout set script
PYTHONPATH=/tmp/core .venv/bin/python -m script.hassfest \
  --integration-path custom_components/rhizome
```

## État de référence (après la première passe)

| Vérification | Résultat |
|---|---|
| `ruff check` | **0 écart** |
| `mypy` | **0 erreur** (18 fichiers) |
| `pytest` | **181 tests OK**, 1 204 sous-tests, **couverture 91 %** |
| `hassfest` 2026.10.4 | **0 intégration invalide** |
| Validation HACS | non exécutable hors CI (inchangé) |

La première passe tient : rien de ce qu'elle déclare corrigé ne s'est révélé
faux. Les constats ci-dessous sont des défauts qu'elle **n'avait pas vus** —
trois d'entre eux dans des zones qu'elle avait explicitement déclarées saines.

## Constats

### Critique

#### C3 — XSS stockée dans le panneau : `echappe()` n'échappe pas les guillemets
`frontend/rhizome-panel.js:140-144` (fonction) · points d'injection
`rhizome-panel.js:1027, 1054, 1059, 1489, 2297, 2431, 2436, 2445, 2563, 2567`
et `rhizome-card.js:143, 202`

`echappe()` posait le texte dans un nœud puis relisait `innerHTML`. Le
sérialiseur HTML n'échappe alors que `&`, `<` et `>` : le guillemet passe
intact, parce qu'il est sans danger **dans un nœud de texte**. Or `echappe()`
est aussi employé **à l'intérieur d'attributs**, à une douzaine d'endroits :
`value="${echappe(plante.surnom)}"`, `title="${echappe(ligne.nom)}"`,
`header="${echappe(this._config.titre)}"`.

**Vérifié dans un navigateur** : la charge `" onmouseover="…" x="` posée comme
nom de zone produit un véritable attribut `onmouseover` sur l'élément, et le
code s'exécute. Le shadow DOM n'y change rien.

**Impact** — exécution de JavaScript arbitraire dans l'origine de Home
Assistant, avec la session de qui regarde le panneau. La charge se pose par
`rhizome/modifier` (surnom) ou `rhizome/zones` (nom), c'est-à-dire par
n'importe quel compte authentifié — y compris en lecture seule avant É7 — et
se déclenche chez l'administrateur. C'est une prise de contrôle de l'instance.

La première passe concluait, en « non-constats » : « `echappe()` est appliqué
à 53 endroits et couvre tous les textes libres ». Le comptage était juste, le
contexte d'insertion n'avait pas été examiné.

**Corrigé** — table d'entités couvrant les cinq caractères, indépendante du
contexte. Identifiant de zone et emojis, jusqu'ici interpolés nus parce que
contraints côté serveur, passent aussi par `echappe()` : la sûreté ne repose
plus sur une troncature à quatre caractères lue ailleurs.

#### C4 — Un entier non borné écrit dans le stockage paralyse le coordinateur
`websocket.py:426, 458-464, 501, 542, 825` → `phenology.py:150` ·
`watering.py:155` · `lifecycle` (dates du journal)

Même panne que C2, par un autre chemin. Ces valeurs finissent dans
`.storage/rhizome.jardin`, puis dans un `date + timedelta(...)` : un entier
démesuré y lève une `OverflowError` depuis `_calculer`, donc à chaque cycle.
La valeur étant **persistée**, ni le rechargement ni le redémarrage n'y
changent rien.

C2 avait fermé ce chemin pour `entry.options` ; le stockage du jardin, lui,
n'avait aucune garde — ni à l'écriture, ni à la lecture.

**Vérifié en exécution**, trois chemins, tous avec `success: true` côté client
et `last_update_success: false` juste après :

| Commande | Valeur acceptée |
|---|---|
| `rhizome/zones` | `decalage_jours: 10**9` |
| `rhizome/modifier` | `arrosage_frequence_jours: 10**12` |
| `rhizome/noter` | `date: "9999-12-31"`, rangée au journal |

Le service `rhizome.ajouter_plante` bornait pourtant déjà `echelonnement_jours`
entre 0 et 90 (`__init__.py:86`) : c'est le schéma WebSocket qui avait été
écrit plus lâche — et le panneau est le seul chemin que l'utilisateur emprunte.

**Corrigé** — trois niveaux : les schémas bornent ce qui entre, `store` et
`watering` bornent ce qu'ils relisent (pour les jardins déjà empoisonnés),
et `_calculer` isole chaque plante.

### Élevé

#### É7 — Les commandes d'écriture du jardin n'exigent aucune autorisation
`websocket.py:378-415` (`_avec_coordinateur`) et les onze commandes qu'il
enveloppe

Une commande WebSocket personnalisée n'hérite d'aucun contrôle d'accès : toute
session authentifiée l'atteint. La première passe avait gardé
`rhizome/reglages/definir` avec `require_admin`, parce qu'elle écrit dans
l'entrée de configuration. Les onze autres, non.

**Vérifié** avec un jeton en lecture seule : `ajouter`, `modifier`, `noter`,
`annuler`, `arroser`, `ressemer`, `zones` et **`retirer`** renvoient toutes
`success: true`.

**Impact** — `retirer` efface le journal d'une plante, c'est-à-dire la seule
donnée du projet que rien ne reconstitue : ni le catalogue, ni le calcul, ni
une sauvegarde de configuration. L'audit précédent le dit lui-même en
justifiant les diagnostics.

**Corrigé** — garde unique dans `_avec_coordinateur`, sur le droit de contrôler
les entités : un compte ordinaire jardine, un compte en lecture seule consulte.

### Moyen

#### M13 — Textes libres non bornés
`websocket.py:424, 457, 505-507, 541`

`surnom`, `note`, `cause` et le nom d'une zone n'avaient aucune borne de
longueur — contrairement aux fiches personnelles, bornées par M5.
**Vérifié** : un surnom de 100 000 caractères est accepté, persisté, et devient
le nom de l'entité donc son `entity_id` — un identifiant de 100 000 caractères
apparaît dans le registre. **Corrigé** avec C4.

#### M14 — Le mode de semis n'était contraint que côté service
`websocket.py:502`

`vol.Optional("mode"): str` acceptait n'importe quelle chaîne, rangée au
journal et ressortie telle quelle, là où `SCHEMA_SEMIS` (`__init__.py:103`)
borne à deux valeurs. **Vérifié**. **Corrigé** avec C4.

#### M16 — La plage demandée au calendrier bloque la boucle d'événements
`calendar.py:60-96`

`async_get_events` reçoit ses dates du client et recalcule les prévisions année
par année, pour chaque plante, dans la boucle. L'API calendrier de Home
Assistant n'impose aucune borne.

**Mesuré** : 0,91 s de boucle bloquée pour 500 ans et 10 plantes, coût
linéaire ensuite. Toute session authentifiée pouvait figer l'instance sans
rien écrire. **Corrigé** : dix années par requête, plage tronquée et non
refusée.

### Faible

| # | Fichier | Constat | Statut |
|---|---|---|---|
| F12 | `rhizome-panel.js:1475, 1681` | L'identifiant de zone restait interpolé nu, alors que la première passe annonçait « échapper quand même côté panneau ». Sans danger (motif `[a-z0-9-]` imposé par M1), mais la ceinture manquait. | corrigé (C3) |
| F13 | `rhizome-panel.js` ×13 | Emojis interpolés nus. Sûrs par une troncature à 4 caractères dans `_normaliser_fiche`, lue à deux cents lignes de là. | corrigé (C3) |
| F14 | `websocket.py:826` | La liste d'uid de `rhizome/arroser` n'avait pas de borne de taille. | corrigé (C4) |

### Non-constats de cette passe (vérifiés)

- **`DeviceInfo` devient une dataclass en 2026.11** (4 nov. 2026, sans période
  de dépréciation). `entity.py:56` la construit par mots-clés et n'en fait
  aucun usage de dictionnaire — pas de `copy()`, `|`, `get()`, `len()`.
  **Rien à changer**, vérifié par relecture de la seule occurrence du dépôt.
- **`RestoreStateData.last_states`, retiré en 2026.11** : non utilisé.
- **`step_id` obligatoire dans les résultats de flux** (dépréciation annoncée
  pour 2027.5) : `config_flow.py` le passe déjà dans ses deux `async_show_form`.
- **Exposition et catégorie des fiches personnelles**, interpolées nues en
  repli dans `rhizome-panel.js:1796` : validées côté serveur contre une liste
  blanche (`catalog.valider_fiche:176-179`). Pas de vecteur.
- **`c.nom`/`c.famille` de `rhizome-panel.js:958`** : concaténation pour la
  recherche, pas du HTML. Faux positif de l'analyse statique, écarté.
- **Première passe** : aucun de ses correctifs ne s'est révélé incomplet ou
  faux, hors les deux cas notés F12 et F13 ci-dessus.

## Suivi des correctifs — seconde passe

| # | Sévérité | Statut | Commit |
|---|---|---|---|
| C3 | Critique | corrigé | `fc34282` |
| C4 | Critique | corrigé | `0a42cc9` |
| É7 | Élevé | corrigé | `0fd7e80` |
| M13 | Moyen | corrigé | `0a42cc9` |
| M14 | Moyen | corrigé | `0a42cc9` |
| M16 | Moyen | corrigé | `607f94c` |
| F12 | Faible | corrigé | `fc34282` |
| F13 | Faible | corrigé | `fc34282` |
| F14 | Faible | corrigé | `0a42cc9` |

### Ce qui n'a pas pu être vérifié

- La **validation HACS officielle**, toujours non exécutable hors CI.
- Le **frontend** n'a toujours ni linter ni test unitaire : pas de Node sur le
  poste. Les correctifs de C3 ont été vérifiés **dans un vrai navigateur** —
  exécution de la charge avant, absence d'exécution après — puis les cinq vues
  du panneau ont été rendues au banc d'essai, sans erreur console ni entité
  HTML visible dans le texte. Les trois garde-fous de `tests/test_source.py`
  lisent le source, faute de pouvoir l'exécuter ; chacun a été vérifié en
  réintroduisant la faute.
- L'**exactitude agronomique** des 172 fiches, inchangée et hors de portée.

### Décisions qui restent au propriétaire

Les deux de la première passe (M8 traduction des entités, M10 `voluptuous` ou
`probatio`) sont inchangées. Sur M10, la source est désormais explicite :
« Your integration can keep the old import for as long as you like »
([Probatio is our validation engine](https://contributors.home-assistant.io/blog/2026/09/30/probatio-validation-engine/)).
Aucune échéance n'est annoncée — la décision peut attendre.

Une nouvelle, mineure : **É7 fixe une politique d'accès**. Le choix retenu est
le droit de contrôler les entités, ce qui laisse jardiner un compte ordinaire
et arrête un compte en lecture seule. Si vous préférez réserver l'écriture aux
administrateurs, c'est `require_admin` sur `_avec_coordinateur` et un test à
retourner.

## Sources

- [Integration Quality Scale — toutes les règles](https://contributors.home-assistant.io/core/quality-scale/rules/)
  (`developers.home-assistant.io/docs/core/integration-quality-scale/rules/`
  redirige désormais vers `contributors.home-assistant.io`)
- [Publier une intégration sur HACS](https://www.hacs.xyz/docs/publish/integration/)
- [Config entry functions now return None (23 oct. 2026)](https://contributors.home-assistant.io/blog/2026/10/23/config-entry-methods-return-none/)
  — sans effet ici : les intégrations personnalisées peuvent continuer à
  renvoyer un booléen.
- `homeassistant/__init__.py` 2026.10.4, appel à
  `probatio.compat.install_as_voluptuous()`.
- [DeviceInfo is now a dataclass (13 oct. 2026)](https://contributors.home-assistant.io/blog/2026/10/13/device-info-class/)
  — 2026.11, sans période de dépréciation ; sans effet ici.
- [Probatio is our validation engine (30 sept. 2026)](https://contributors.home-assistant.io/blog/2026/09/30/probatio-validation-engine/)
- [Always pass a step_id to flow results (23 oct. 2026)](https://contributors.home-assistant.io/blog/2026/10/23/flow-results-require-step-id/)
  — déjà respecté.
- [Integrations have categories now (20 oct. 2026)](https://contributors.home-assistant.io/blog/2026/10/20/integration-categories/)
  — `categories` reste **optionnelle** pour une intégration personnalisée :
  `hacs/action` se contente d'un avertissement. Confirme la note ci-dessus.
- HACS devient **Marketplace**, intégré au cœur à partir de 2026.11
  ([hacs.xyz](https://www.hacs.xyz/docs/publish/integration/)). Les exigences
  structurelles sont inchangées, et le dépôt les satisfait déjà :
  `hacs.json`, `README.md`, `custom_components/rhizome/`, les six clés de
  manifest, et `brand/icon.png`.
