"""Constantes de l'integration Rhizome."""

from __future__ import annotations

DOMAIN = "rhizome"

STORAGE_KEY = "rhizome.jardin"
STORAGE_VERSION = 1

# L'integration s'est appelee « potager » jusqu'a la v0.7.0, et le jardin de
# toute installation anterieure vit encore sous cette cle. On l'adopte au
# premier chargement : le journal est la seule donnee du projet qu'aucun calcul
# ne peut reconstituer.
STORAGE_KEY_HERITAGE = "potager.jardin"

PANEL_URL = "/rhizome-frontend"
PANEL_PATH = "rhizome"
PANEL_TITLE = "Rhizome"
PANEL_ICON = "mdi:sprout"

# --- Options de configuration -------------------------------------------------

CONF_GELEES_DERNIERE = "gelees_derniere"
CONF_GELEES_PREMIERE = "gelees_premiere"
CONF_ZONES = "zones"
CONF_NOTIFY_TARGETS = "notify_targets"
CONF_NOTIFY_HEURE = "notify_heure"
CONF_PRESET_CLIMAT = "preset_climat"
CONF_RAPPEL_JOURS = "rappel_jours"

# Langue de l'interface. « auto » suit la langue de Home Assistant ; les deux
# autres valeurs la forcent. Ce reglage n'est pas cosmetique : il decide aussi
# de la langue des rappels, du calendrier et des noms d'entites, qui sont
# produits par le serveur et non par le panneau.
CONF_LANGUE = "langue"

# --- Granularite des rappels --------------------------------------------------

# Quelles etapes meritent un rappel. Tout le monde ne veut pas etre prevenu
# d'un semis a l'abri, mais presque personne ne veut rater une recolte.
CONF_NOTIFY_ETAPES = "notify_etapes"

# Un seul message groupe, plutot qu'une notification par plante : au printemps,
# cinq rappels le meme matin, c'est cinq rappels qu'on balaie sans lire.
CONF_NOTIFY_RESUME = "notify_resume"

# Relance pendant la fenetre de recolte, en jours (0 = une seule fois). Une
# courgette se cueille tous les deux jours : prevenir une fois ne sert a rien.
CONF_NOTIFY_RECOLTE_RECURRENCE = "notify_recolte_recurrence"

# Masquer les plantes terminees ou perdues dans « Mon potager ».
CONF_MASQUER_TERMINEES = "masquer_terminees"

# --- Alerte gel ---------------------------------------------------------------
#
# L'entite meteo a consulter. Vide = alerte desactivee, et c'est le defaut :
# aucune integration ne doit se mettre a lire une entite que l'utilisateur ne
# lui a pas designee.
CONF_METEO_ENTITE = "meteo_entite"

# Un second passage, en soiree, distinct du rappel quotidien. L'alerte gel est
# la seule notification de Rhizome qui porte sur une echeance de quelques
# heures : envoyee avec les autres a 8 h, elle arriverait apres la nuit
# qu'elle devait prevenir.
CONF_NOTIFY_GEL = "notify_gel"
CONF_NOTIFY_GEL_HEURE = "notify_gel_heure"

# --- Arrosage -----------------------------------------------------------------

# Le suivi d'arrosage s'active globalement. Un potager entierement en pleine
# terre, sous climat humide, n'en a pas forcement l'usage.
CONF_ARROSAGE_ACTIF = "arrosage_actif"

# Rappeler les arrosages dus, ou se contenter de les suivre. Deux reglages et
# non un seul : on peut vouloir voir ou en est l'eau, et presser « Arrosé »,
# sans recevoir une notification de plus chaque matin d'ete.
#
# Volontairement en dehors de `ETAPES_NOTIFIABLES` : l'arrosage n'est pas une
# etape du cycle (invariant 6), et une liste enregistree avant ce reglage ne le
# contiendrait pas — les rappels d'eau se seraient tus sans rien dire.
CONF_NOTIFY_ARROSAGE = "notify_arrosage"

# Bouguenais (44), zone USDA 9a, climat oceanique.
DEFAUT_GELEES_DERNIERE = "04-15"
DEFAUT_GELEES_PREMIERE = "11-15"
DEFAUT_NOTIFY_HEURE = "08:00:00"
DEFAUT_RAPPEL_JOURS = 3
DEFAUT_NOTIFY_RECOLTE_RECURRENCE = 0
DEFAUT_NOTIFY_RESUME = False
DEFAUT_MASQUER_TERMINEES = False
DEFAUT_ARROSAGE_ACTIF = True
DEFAUT_NOTIFY_ARROSAGE = True
DEFAUT_METEO_ENTITE = ""
DEFAUT_NOTIFY_GEL = True
# 18 h : assez tot pour rentrer des pots avant la nuit, assez tard pour que la
# prevision du soir ait remplace celle du matin.
DEFAUT_NOTIFY_GEL_HEURE = "18:00:00"

# « auto » plutot que « fr » : une installation anglophone n'a aucune raison
# d'afficher du francais, et une installation existante ne change pas de langue
# puisque son Home Assistant est en francais.
DEFAUT_LANGUE = "auto"
LANGUE_AUTO = "auto"
LANGUES = ("fr", "en")

# Par defaut on notifie tout : mieux vaut desactiver ce qui derange que
# decouvrir en juillet qu'un rappel n'est jamais parti.
ETAPES_NOTIFIABLES = (
    "semis_interieur",
    "semis_direct",
    "repiquage",
    "plantation",
    "recolte",
)

ZONE_PLEINE_TERRE = "pleine-terre"

# Un decalage de zone s'exprime en semaines : une serre prend trois semaines
# d'avance, pas trois siecles. La borne protege le calcul de date, ou un
# entier demesure leve une OverflowError a chaque cycle du coordinateur.
DECALAGE_ZONE_MAX = 120

# `abritee` : serre, chassis, pots. Ces zones sechent toute l'annee, donc
# l'arrosage y est rappele meme en hiver. En pleine terre, aucun rappel entre
# la premiere et la derniere gelee : personne n'arrose son jardin en decembre.
ZONES_DEFAUT: list[dict] = [
    {"id": ZONE_PLEINE_TERRE, "nom": "Pleine terre", "decalage_jours": 0},
    {"id": "serre", "nom": "Serre", "decalage_jours": -21, "abritee": True},
    {"id": "chassis", "nom": "Chassis / tunnel", "decalage_jours": -10,
     "abritee": True},
    {"id": "balcon", "nom": "Balcon / pots", "decalage_jours": 0, "abritee": True},
]

# Caracteristique deduite pour les zones d'origine, quand un stockage anterieur
# a l'arrosage ne la porte pas encore.
TRAITS_ZONES_CONNUES = {
    "serre": {"abritee": True},
    "chassis": {"abritee": True},
    "balcon": {"abritee": True},
}

# --- Services -----------------------------------------------------------------

SERVICE_AJOUTER_PLANTE = "ajouter_plante"
SERVICE_RETIRER_PLANTE = "retirer_plante"
SERVICE_MARQUER_SEME = "marquer_seme"
SERVICE_MARQUER_REPIQUE = "marquer_repique"
SERVICE_MARQUER_RECOLTE = "marquer_recolte"
SERVICE_MARQUER_PERDU = "marquer_perdu"
SERVICE_MARQUER_TERMINE = "marquer_termine"
SERVICE_ARROSER = "marquer_arrose"
SERVICE_RESSEMER = "ressemer"
SERVICE_ANNULER = "annuler_dernier_evenement"
SERVICE_RAFRAICHIR = "rafraichir"

# --- Evenements du bus -------------------------------------------------------

EVENT_JARDIN_MAJ = f"{DOMAIN}_jardin_maj"

# --- Catalogue personnel ------------------------------------------------------

# Prefixe des fiches ajoutees par l'utilisateur, pour ne jamais les confondre
# avec les 108 fiches livrees ni risquer d'ecraser l'une d'elles.
PREFIXE_PERSO = "perso-"

# Preselections climatiques : eviter de demander a froid une date de gelee.
PRESETS_CLIMAT: dict[str, dict[str, str]] = {
    "oceanique": {"derniere": "04-15", "premiere": "11-15"},
    "nord_est": {"derniere": "05-05", "premiere": "10-20"},
    "midi": {"derniere": "03-20", "premiere": "12-05"},
    "montagne": {"derniere": "05-25", "premiere": "10-01"},
}
PRESET_PERSONNALISE = "personnalise"
