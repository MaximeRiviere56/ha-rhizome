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

Mis à jour au fil de la phase 2. Voir le rapport final pour les commits.

| # | Sévérité | Statut |
|---|---|---|
| C1 | Critique | à faire |
| C2 | Critique | à faire |
| É1 | Élevé | à faire |
| É2 | Élevé | à faire |
| É3 | Élevé | à faire |
| É4 | Élevé | à faire |
| É5 | Élevé | à faire |
| É6 | Élevé | à faire |
| M1 | Moyen | à faire |
| M2 | Moyen | à faire |
| M3 | Moyen | à faire |
| M4 | Moyen | à faire |
| M5 | Moyen | à faire |
| M6 | Moyen | à faire |
| M7 | Moyen | à faire |
| M8 | Moyen | à faire |
| M9 | Moyen | à faire |
| M10 | Moyen | à faire |
| M11 | Moyen | à faire |
| M12 | Moyen | à faire |
| F1–F11 | Faible | à faire |

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
