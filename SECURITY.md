# Politique de sécurité

## Versions suivies

Seule la dernière version publiée reçoit des correctifs. Rhizome n'a pas de
branche de maintenance.

## Signaler une faille

**N'ouvrez pas d'issue publique.** Utilisez
[l'avis de sécurité privé GitHub](https://github.com/MaximeRiviere56/ha-rhizome/security/advisories/new).

Donnez la version de Rhizome, celle de Home Assistant, et de quoi reproduire.
Réponse sous une semaine ; correctif publié dès qu'il est prêt et testé, avec
mention dans `CHANGELOG.md`.

## Ce que Rhizome touche, et ce qu'il ne touche pas

Le périmètre, pour situer ce qui compte :

- **Aucun appel réseau.** `manifest.json` ne déclare aucune dépendance et le
  code n'embarque pas de client HTTP. Tout est calculé localement.
- **Aucun secret.** Rhizome ne manipule ni jeton, ni clé, ni mot de passe.
- **Données stockées** : le jardin (plantes, journal, arrosages, fiches
  personnelles) dans `.storage/rhizome.jardin`, et les réglages dans l'entrée
  de configuration. Rien n'en sort, sauf le contenu des rappels envoyés aux
  services `notify` que vous avez choisis.
- **Données personnelles** : les surnoms et les notes du journal sont du texte
  libre. Ils sont masqués dans les diagnostics ; ils apparaissent en revanche
  dans une sauvegarde Home Assistant, comme le reste de `.storage`.

## Surface exposée

- **Commandes WebSocket** `rhizome/*`, accessibles à tout utilisateur
  authentifié de Home Assistant. `rhizome/reglages/definir`, qui écrit dans
  l'entrée de configuration, exige en plus le rôle administrateur.
- **Actions** `rhizome.*`, soumises au modèle de permissions de Home Assistant.
- **Un chemin statique** `/rhizome-frontend`, qui ne sert que le JavaScript du
  panneau et de la carte.
- **Le panneau latéral**, délibérément accessible aux non-administrateurs :
  un jardin se tient à plusieurs.

Les textes saisis par l'utilisateur sont échappés avant affichage dans le
panneau, et les identifiants (zone, culture) sont contraints côté serveur.
