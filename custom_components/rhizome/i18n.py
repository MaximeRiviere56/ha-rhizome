"""Textes de l'interface, en francais et en anglais.

Module pur : aucun import Home Assistant, donc verifiable sans instance.

Pourquoi une table ici plutot que `translations/*.json` : Home Assistant ne
localise que ce qui passe par ses propres mecanismes — titres du flux de
configuration, descriptions d'actions, messages d'exception a cle. Tout le
reste de ce projet est produit par du code : le resume d'une notification, la
description d'un evenement de calendrier, le libelle d'une phase, le nom d'un
capteur. Ces textes n'ont pas de place dans le fichier de traductions de HA, et
les laisser en dur rendait l'integration inutilisable hors du francais.

Trois regles tenues ici :

1. **Le francais reste la langue de reference.** Une cle absente de `en` retombe
   sur `fr` plutot que de rendre sa propre cle : un libelle francais au milieu
   d'une interface anglaise est desagreable, un `notif_eau_titre` nu est casse.
2. **Aucune donnee utilisateur dans une cle.** Les textes prennent leurs
   variables par `format()`, et l'echappement reste a la charge de l'appelant —
   le panneau echappe au moment de construire son HTML.
3. **Les cles de phase, d'etape et d'evenement sont celles du moteur.** Elles ne
   sont pas recopiees : `libelle_phase`, `libelle_etape` et `libelle_evenement`
   prennent le type tel que `lifecycle` et `phenology` l'ecrivent, ce qui rend
   une divergence impossible a introduire en silence.
"""

from __future__ import annotations

LANGUE_DEFAUT = "fr"
LANGUE_AUTO = "auto"
LANGUES = ("fr", "en")


def resoudre(option: str | None, langue_hass: str | None = None) -> str:
    """La langue a employer, a partir du reglage et de celle de Home Assistant.

    Tout ce qui n'est pas reconnu retombe sur le francais : une option illisible
    dans `entry.options` ne doit pas priver l'utilisateur de son interface. Les
    etiquettes regionales sont tolerees (`en-GB`, `fr_CA`), parce que
    `hass.config.language` et `hass.language` n'ont pas le meme format selon les
    versions.
    """
    if option in LANGUES:
        return str(option)
    base = (langue_hass or "").replace("_", "-").split("-", 1)[0].lower()
    return base if base in LANGUES else LANGUE_DEFAUT


def t(langue: str, cle: str, **params: object) -> str:
    """Le texte de cette cle, dans cette langue, variables substituees.

    Une cle inconnue rend la cle elle-meme : visible en developpement, et
    jamais une exception en production — un libelle manquant ne doit pas
    empecher un rappel de partir.
    """
    table = TEXTES.get(langue) or TEXTES[LANGUE_DEFAUT]
    modele = table.get(cle) or TEXTES[LANGUE_DEFAUT].get(cle)
    if modele is None:
        return cle
    if not params:
        return modele
    try:
        return modele.format(**params)
    # Un modele traduit a la main peut porter une variable qui n'existe plus.
    # Rendre le modele brut reste plus utile qu'une KeyError dans un rappel.
    except (KeyError, IndexError, ValueError):
        return modele


def libelle_phase(langue: str, phase: str) -> str:
    return t(langue, f"phase_{phase}") if f"phase_{phase}" in TEXTES["fr"] else phase


def libelle_etape(langue: str, type_etape: str) -> str:
    cle = f"etape_{type_etape}"
    return t(langue, cle) if cle in TEXTES["fr"] else type_etape


def libelle_evenement(langue: str, type_evt: str) -> str:
    cle = f"evt_{type_evt}"
    return t(langue, cle) if cle in TEXTES["fr"] else type_evt


def traduire_erreur(langue: str, err: Exception) -> str:
    """Le refus porte par cette exception, dans la langue demandee.

    Les exceptions du moteur viennent de modules purs, qui ne connaissent
    aucun reglage : elles transportent donc une cle et ses variables, pas un
    texte traduit. Sans cle — une exception d'une autre origine — on rend son
    message tel quel.

    Deux variables sont elles-memes des cles plutot que du texte : le type
    d'evenement et la phase. Les laisser en clair ferait citer « Semé » et
    « En récolte » au milieu d'un refus anglais.
    """
    cle = getattr(err, "cle", None)
    if not cle:
        return str(err)
    params = dict(getattr(err, "params", None) or {})
    if "evenement" in params:
        params["evenement"] = libelle_evenement(langue, str(params["evenement"]))
    if "phase" in params:
        params["phase"] = libelle_phase(langue, str(params["phase"]))
    return t(langue, str(cle), **params)


def phases_libellees(langue: str) -> list[str]:
    """Les phases dans l'ordre du cycle, pour les options d'un capteur `enum`."""
    return [libelle_phase(langue, phase) for phase in ORDRE_PHASES]


ORDRE_PHASES = ("prevu", "seme", "plante", "en_recolte", "termine", "perdu")


# --- Dates --------------------------------------------------------------------
#
# Les formats de date sont des textes comme les autres : « 15/04 » est illisible
# pour un anglophone, qui y lit le 4 du quinzieme mois. On passe donc par
# `strftime` avec un motif par langue, et non par un format en dur.

FORMATS_DATE = {
    "fr": {"court": "%d/%m", "long": "%d/%m/%Y"},
    "en": {"court": "%b %-d", "long": "%b %-d, %Y"},
}


def date_courte(langue: str, jour) -> str:
    """« 15/04 » ou « Apr 15 », selon la langue."""
    return _formater(langue, "court", jour)


def date_longue(langue: str, jour) -> str:
    """« 15/04/2026 » ou « Apr 15, 2026 », selon la langue."""
    return _formater(langue, "long", jour)


def _formater(langue: str, forme: str, jour) -> str:
    motif = (FORMATS_DATE.get(langue) or FORMATS_DATE[LANGUE_DEFAUT])[forme]
    try:
        return jour.strftime(motif)
    # `%-d` n'existe pas partout (Windows notamment) : le repli garde un jour
    # sur deux chiffres plutot que de lever au moment d'envoyer un rappel.
    except ValueError:
        return jour.strftime(motif.replace("%-d", "%d"))


# --- Zones livrees ------------------------------------------------------------
#
# Les quatre zones d'origine sont creees une seule fois, au premier chargement,
# puis deviennent des donnees que l'utilisateur renomme a sa guise. Les traduire
# ici ne les renomme donc jamais apres coup : cela evite seulement qu'une
# installation anglophone naisse avec « Pleine terre » et « Chassis / tunnel ».
NOMS_ZONES_DEFAUT = {
    "fr": {
        "pleine-terre": "Pleine terre",
        "serre": "Serre",
        "chassis": "Chassis / tunnel",
        "balcon": "Balcon / pots",
    },
    "en": {
        "pleine-terre": "Open ground",
        "serre": "Greenhouse",
        "chassis": "Cold frame / tunnel",
        "balcon": "Balcony / pots",
    },
}


def nom_zone_defaut(langue: str, zone_id: str, defaut: str) -> str:
    table = NOMS_ZONES_DEFAUT.get(langue) or {}
    return table.get(zone_id, defaut)


# --- Table des textes ---------------------------------------------------------

TEXTES: dict[str, dict[str, str]] = {
    "fr": {
        # Phases du cycle d'une plante.
        "phase_prevu": "Prévu",
        "phase_seme": "Semé",
        "phase_plante": "Planté",
        "phase_en_recolte": "En récolte",
        "phase_termine": "Terminé",
        "phase_perdu": "Perdu",
        # Etapes culturales : ce sont des ordres, d'ou l'infinitif.
        "etape_semis_interieur": "Semer à l'abri",
        "etape_semis_direct": "Semer en place",
        "etape_repiquage": "Repiquer",
        "etape_plantation": "Planter",
        "etape_recolte": "Récolter",
        "etape_ressemer": "Ressemer",
        # Evenements du journal : ce sont des faits, d'ou le participe.
        "evt_seme": "Semé",
        "evt_repique": "Repiqué",
        "evt_plante": "Planté",
        "evt_recolte": "Récolté",
        "evt_termine": "Terminé",
        "evt_perdu": "Perdu",
        # Noms d'entites.
        "entite_actions": "Actions à mener",
        "entite_recolte": "Récolte de la saison",
        "entite_arrosage": "À arroser",
        "entite_rappels": "Rappels {plante}",
        # Rappels : etapes du cycle.
        "notif_titre": "{emoji} {verbe} : {plante}",
        "notif_message": "{quand} — {zone}. Fenêtre jusqu'au {fin}.",
        "notif_quand_moment": "C'est le moment",
        "notif_quand_demain": "Demain",
        "notif_quand_dans": "Dans {jours} jours",
        "notif_bouton_fait": "C'est fait",
        "notif_bouton_seme": "Semé",
        "notif_bouton_report": "Rappeler dans {jours} j",
        "notif_resume_titre": "🌱 {nombre} choses à faire au potager",
        "notif_resume_ligne": "{emoji} {verbe} : {plante} ({zone})",
        # Rappels : arrosage.
        "notif_eau_titre": "💧 Arroser : {plante}",
        "notif_eau_message": "{quand} — {zone}. {dernier}.",
        "notif_eau_quand_jour": "C'est le jour",
        "notif_eau_quand_hier": "Depuis hier",
        "notif_eau_quand_depuis": "Depuis {jours} jours",
        "notif_eau_dernier": "Dernier arrosage le {date}",
        "notif_eau_jamais": "Jamais arrosée depuis sa mise en terre",
        "notif_bouton_arrose": "Arrosé",
        # Calendrier.
        "cal_resume_etape": "{verbe} : {plante}",
        "cal_resume_journal": "{emoji} {evenement} : {plante}",
        "cal_fenetre_prevue": "Fenêtre prévue, du {debut} au {fin}.",
        "cal_fenetre_reelle": "Fenêtre d'après votre journal, du {debut} au {fin}.",
        "cal_cause": "cause : {cause}",
        "cal_note_defaut": "Noté au journal du potager.",
        # Liste de taches.
        "todo_resume": "{emoji} {verbe} : {plante}",
        "todo_description": "{zone} — fenêtre jusqu'au {fin}.",
        # Arrosage : pourquoi une plante n'a pas d'echeance d'eau.
        "eau_exclu_desactive": "Rappels d'arrosage désactivés pour cette plante.",
        "eau_exclu_pas_en_terre": "Pas encore en terre, ou culture terminée.",
        "eau_exclu_hiver": "En pleine terre l'hiver, la nature s'en charge.",
        "eau_exclu_perenne": (
            "Pérenne installée et peu gourmande : elle se débrouille seule."
        ),
        "eau_suivi_inactif": "Suivi d'arrosage inactif.",
        # Rotation des cultures.
        "rotation_message": (
            "{famille} déjà cultivées ici : {precedents}. Cette famille demande "
            "{delai} ans avant de revenir au même endroit."
        ),
        # Refus et erreurs d'usage.
        "err_non_charge": "Rhizome n'est pas chargé",
        "err_lecture_seule": (
            "Un compte en lecture seule ne peut pas modifier le jardin."
        ),
        "err_saisie_invalide": "Saisie invalide : {detail}",
        "err_reglage_invalide": "Réglage invalide : {detail}",
        "err_fiche_invalide": "Fiche invalide : {detail}",
        "err_culture_inconnue": "Culture inconnue : {culture_id}",
        "err_culture_inconnue_service": (
            "Culture inconnue : {culture_id}. Les identifiants sont ceux du "
            "catalogue, par exemple « tomate »."
        ),
        "err_plante_introuvable": "Plante introuvable dans le jardin : {uid}",
        "err_fiche_utilisee": (
            "Cette fiche est utilisée par {nombre} plante(s) du jardin "
            "({plantes}). Retirez-les d'abord."
        ),
        "err_transition": (
            "Impossible d'enregistrer '{evenement}' depuis la phase '{phase}'."
        ),
        "err_type_evenement": "Type d'événement inconnu : {type}",
        "err_date_invalide": "Date invalide : {valeur}",
        "err_quantite_negative": "Une quantité récoltée ne peut pas être négative.",
        "err_cible_notif": "Destinataire de notification inconnu : {cibles}.",
        "err_rien_a_retablir": (
            "Cette fiche n'existe pas dans le catalogue livré : il n'y a rien à "
            "rétablir. Supprimez-la plutôt."
        ),
        "err_plante_a_designer": (
            "Indiquez la plante : son `uid` (attribut de son capteur) ou son "
            "`entity_id`."
        ),
        "err_pas_une_entite": "{entity_id} n'est pas une entité de Rhizome.",
        "err_pas_une_plante": (
            "{entity_id} ne désigne pas une plante du jardin : visez le capteur "
            "d'une plante."
        ),
        # Validation d'une fiche personnelle.
        "fiche_nom_requis": "Le nom est obligatoire.",
        "fiche_categorie": "Catégorie inconnue.",
        "fiche_exposition": "Exposition inconnue.",
        "fiche_eau": "Besoin en eau inconnu.",
        "fiche_gel": "Indiquez si la culture craint le gel.",
        "fiche_aucune_periode": (
            "Indiquez au moins une période de semis ou de plantation."
        ),
        "fiche_recolte_incalculable": (
            "Impossible de calculer une récolte : indiquez une période de "
            "récolte, ou le nombre de jours entre la mise en terre et la récolte."
        ),
        # Destinataire de rappel sans bouton d'action.
        "cible_persistante": "Notification dans Home Assistant",
        # Famille botanique d'une fiche personnelle laissee vide.
        "famille_inconnue": "Non précisée",
    },
    "en": {
        "phase_prevu": "Planned",
        "phase_seme": "Sown",
        "phase_plante": "Planted",
        "phase_en_recolte": "Harvesting",
        "phase_termine": "Finished",
        "phase_perdu": "Lost",
        "etape_semis_interieur": "Sow under cover",
        "etape_semis_direct": "Sow in place",
        "etape_repiquage": "Transplant",
        "etape_plantation": "Plant out",
        "etape_recolte": "Harvest",
        "etape_ressemer": "Sow next batch",
        "evt_seme": "Sown",
        "evt_repique": "Transplanted",
        "evt_plante": "Planted",
        "evt_recolte": "Harvested",
        "evt_termine": "Finished",
        "evt_perdu": "Lost",
        "entite_actions": "Tasks due",
        "entite_recolte": "Harvest this season",
        "entite_arrosage": "Needs watering",
        "entite_rappels": "{plante} reminders",
        "notif_titre": "{emoji} {verbe}: {plante}",
        "notif_message": "{quand} — {zone}. Window until {fin}.",
        "notif_quand_moment": "Now is the time",
        "notif_quand_demain": "Tomorrow",
        "notif_quand_dans": "In {jours} days",
        "notif_bouton_fait": "Done",
        "notif_bouton_seme": "Sown",
        "notif_bouton_report": "Remind in {jours} d",
        "notif_resume_titre": "🌱 {nombre} things to do in the garden",
        "notif_resume_ligne": "{emoji} {verbe}: {plante} ({zone})",
        "notif_eau_titre": "💧 Water: {plante}",
        "notif_eau_message": "{quand} — {zone}. {dernier}.",
        "notif_eau_quand_jour": "Due today",
        "notif_eau_quand_hier": "Due since yesterday",
        "notif_eau_quand_depuis": "{jours} days overdue",
        "notif_eau_dernier": "Last watered {date}",
        "notif_eau_jamais": "Never watered since it went in the ground",
        "notif_bouton_arrose": "Watered",
        "cal_resume_etape": "{verbe}: {plante}",
        "cal_resume_journal": "{emoji} {evenement}: {plante}",
        "cal_fenetre_prevue": "Forecast window, {debut} to {fin}.",
        "cal_fenetre_reelle": "Window from your journal, {debut} to {fin}.",
        "cal_cause": "cause: {cause}",
        "cal_note_defaut": "Recorded in the garden journal.",
        "todo_resume": "{emoji} {verbe}: {plante}",
        "todo_description": "{zone} — window until {fin}.",
        "eau_exclu_desactive": "Watering reminders are off for this plant.",
        "eau_exclu_pas_en_terre": "Not in the ground yet, or the crop is over.",
        "eau_exclu_hiver": "Outdoors in winter, nature takes care of it.",
        "eau_exclu_perenne": (
            "An established perennial with low water needs: it manages on its own."
        ),
        "eau_suivi_inactif": "Watering tracking is off.",
        "rotation_message": (
            "{famille} already grown here: {precedents}. This family needs "
            "{delai} years before it comes back to the same spot."
        ),
        "err_non_charge": "Rhizome is not loaded",
        "err_lecture_seule": "A read-only account cannot change the garden.",
        "err_saisie_invalide": "Invalid input: {detail}",
        "err_reglage_invalide": "Invalid setting: {detail}",
        "err_fiche_invalide": "Invalid crop entry: {detail}",
        "err_culture_inconnue": "Unknown crop: {culture_id}",
        "err_culture_inconnue_service": (
            "Unknown crop: {culture_id}. Ids are the catalogue ones, for example "
            "“tomate”."
        ),
        "err_plante_introuvable": "No such plant in the garden: {uid}",
        "err_fiche_utilisee": (
            "This entry is used by {nombre} plant(s) in the garden ({plantes}). "
            "Remove them first."
        ),
        "err_transition": "Cannot record '{evenement}' from phase '{phase}'.",
        "err_type_evenement": "Unknown event type: {type}",
        "err_date_invalide": "Invalid date: {valeur}",
        "err_quantite_negative": "A harvested quantity cannot be negative.",
        "err_cible_notif": "Unknown reminder recipient: {cibles}.",
        "err_rien_a_retablir": (
            "This entry does not exist in the shipped catalogue, so there is "
            "nothing to restore. Delete it instead."
        ),
        "err_plante_a_designer": (
            "Name the plant: its `uid` (an attribute of its sensor) or its "
            "`entity_id`."
        ),
        "err_pas_une_entite": "{entity_id} is not a Rhizome entity.",
        "err_pas_une_plante": (
            "{entity_id} does not point at a plant: aim at a plant's sensor."
        ),
        "fiche_nom_requis": "A name is required.",
        "fiche_categorie": "Unknown category.",
        "fiche_exposition": "Unknown exposure.",
        "fiche_eau": "Unknown water need.",
        "fiche_gel": "Say whether the crop is frost-tender.",
        "fiche_aucune_periode": "Give at least one sowing or planting period.",
        "fiche_recolte_incalculable": (
            "No harvest can be computed: give a harvest period, or the number of "
            "days from going in the ground to harvest."
        ),
        "cible_persistante": "Notification inside Home Assistant",
        "famille_inconnue": "Unspecified",
    },
}
