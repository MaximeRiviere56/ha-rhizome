/**
 * Panneau « Rhizome ».
 *
 * Ecrit en web components natifs, sans bundler ni dependance : le fichier que
 * Home Assistant sert est celui qu'on lit ici. C'est ce qui garde l'install
 * HACS sans etape de build et le projet modifiable dans un an.
 *
 * Toutes les couleurs viennent des variables CSS de Home Assistant : le
 * panneau suit le theme de l'utilisateur, mode sombre compris, sans code.
 *
 * Les textes vivent dans la table `TEXTES`, en francais et en anglais. La
 * langue n'est pas devinee ici : elle est resolue par le serveur, qui applique
 * le reglage de l'integration (« auto » suivant Home Assistant) et s'en sert
 * lui-meme pour les rappels, le calendrier et les noms d'entites. Le panneau
 * la recoit dans `rhizome/jardin` et `rhizome/reglages`, ce qui garantit que
 * les deux cotes parlent la meme langue — un panneau qui deciderait seul
 * afficherait des libelles anglais sur des noms de cultures francais.
 */

const LANGUE_DEFAUT = "fr";

/** Langue courante, au niveau du module.
 *
 *  Une variable de module et non un champ de l'instance : les fonctions
 *  utilitaires d'en dessous (`fmtCourt`, `quand`, `kg`) sont appelees depuis
 *  les gabarits sans `this`, et il n'y a de toute facon qu'un panneau par
 *  page et qu'une langue par installation. */
let LANGUE = LANGUE_DEFAUT;

/** Texte localise. Une cle inconnue se rend elle-meme : visible au
 *  developpement, jamais une exception a l'affichage. */
function T(cle, params) {
  const table = TEXTES[LANGUE] || TEXTES[LANGUE_DEFAUT];
  let texte = table[cle] ?? TEXTES[LANGUE_DEFAUT][cle];
  if (texte == null) return cle;
  if (params) {
    for (const [nom, valeur] of Object.entries(params)) {
      texte = texte.replaceAll(`{${nom}}`, String(valeur));
    }
  }
  return texte;
}

/** Pose la langue resolue par le serveur. Vrai si elle a change, pour que
 *  l'appelant sache qu'il doit refaire son rendu. */
function definirLangue(langue) {
  const retenue = TEXTES[langue] ? langue : LANGUE_DEFAUT;
  if (retenue === LANGUE) return false;
  LANGUE = retenue;
  return true;
}

const TEXTES = {
  fr: {
    // Barre de navigation.
    vueAujourdhui: "Aujourd'hui",
    vuePotager: "Mon potager",
    vueCatalogue: "Catalogue",
    vueCalendrier: "Calendrier",
    vueJournal: "Journal",
    vueReglages: "Réglages",
    enteteAFaire: "{nombre} à faire",
    chargement: "Chargement du potager…",
    chargementReglages: "Chargement des réglages…",
    injoignable: "Impossible de joindre Rhizome.",
    actionRefusee: "Action refusée.",
    ficheIndisponible: "Fiche indisponible.",

    // Categories du catalogue.
    "cat_legume-fruit": "Légumes-fruits",
    "cat_legume-racine": "Racines",
    "cat_legume-gousse": "Gousses",
    "cat_legume-bulbe": "Bulbes",
    "cat_legume-feuille": "Feuilles",
    cat_aromatique: "Aromatiques",
    "cat_petit-fruit": "Petits fruits",
    cat_fruitier: "Fruitiers",
    "cat_fleur-compagne": "Fleurs compagnes",
    cat_cereale: "Céréales et graines",
    cat_medicinale: "Médicinales",
    "cat_plante-interieur": "Plantes d'intérieur",

    // Exposition et besoin en eau.
    "expo_plein-soleil": "Plein soleil",
    "expo_mi-ombre": "Mi-ombre",
    expo_ombre: "Ombre",
    eau_faible: "Peu d'eau",
    eau_moyen: "Arrosage modéré",
    eau_eleve: "Beaucoup d'eau",

    // Evenements du journal, pour les filtres.
    evt_seme: "Semé",
    evt_repique: "Repiqué",
    evt_plante: "Planté",
    evt_recolte: "Récolté",
    evt_termine: "Terminé",
    evt_perdu: "Perdu",
    // L'arrosage n'est pas un evenement du journal (invariant 6) mais il
    // s'affiche dedans : c'est un fait date, et le cacher laissait l'utilisateur
    // sans trace de ce qu'il venait de noter.
    evt_arrosage: "Arrosé",

    // Etapes culturales, pour les formulaires qui les listent.
    etape_semis_interieur: "Semer à l'abri",
    etape_semis_direct: "Semer en place",
    etape_repiquage: "Repiquer",
    etape_plantation: "Planter",
    etape_recolte: "Récolter",

    // Echeances.
    quandMaintenant: "C'est le moment",
    quandAujourdhui: "Aujourd'hui",
    quandDemain: "Demain",
    quandDans: "Dans {jours} jours",
    quandDepuisHier: "Depuis hier",
    quandDepuis: "Depuis {jours} jours",

    // Vue « Aujourd'hui ».
    videPotagerTitre: "Votre potager est vide.",
    videPotagerSuite:
      "Choisissez vos premiers légumes dans le catalogue&nbsp;: {total} cultures vous attendent.",
    ouvrirCatalogue: "Ouvrir le catalogue",
    videRienAFaire: "Rien à faire au potager aujourd'hui.",
    videRienAFaireSuite:
      "{nombre} plante{s} suivie{s}, prochaine échéance plus tard.",
    voirPotager: "Voir mon potager",
    sectionMaintenant: "C'est le moment",
    sectionAPreparer: "À préparer",
    sectionAArroser: "À arroser · {nombre}",
    eauTousLesNJours: "tous les {jours} j",
    eauDernierLe: "Dernier arrosage le {date}",
    eauJamais: "Jamais arrosée depuis sa mise en terre",
    // L'etat se lit dans la pastille, au passe quand c'est un fait ; le bouton
    // ne porte que le geste, a l'imperatif.
    eauChipRetard: "À arroser · {jours} j de retard",
    eauChipAujourdhui: "À arroser aujourd'hui",
    eauChipOk: "Arrosé · prochain dans {jours} j",
    eauChipFait: "Arrosé · noté au journal",
    boutonArroser: "Arroser",
    boutonToutArroser: "Tout arroser ({nombre})",
    fenetreJusquAu: "Fenêtre jusqu'au {date}",
    dApresVotreJournal: "d'après votre journal",
    enregistrerAuJournal: "Enregistrer au journal",
    boutonFait: "Fait",
    boutonSeme: "Semé",

    // Vue « Mon potager ».
    videAucunePlante: "Aucune plante pour l'instant.",
    ajouterDesLegumes: "Ajouter des légumes",
    recoltesSuffixe: "{poids} récoltés",
    rienDePrevu: "Rien de prévu",
    noterUnArrosage: "Noter un arrosage",

    // Vue « Catalogue ».
    chercherPlaceholder: "Chercher un légume, un fruit, une famille…",
    filtreSemable: "🌱 Semable maintenant",
    filtreFacile: "★ Facile",
    filtreVivace: "🔁 Vivace",
    filtreContinue: "♾️ Récolte toute l'année",
    filtreAnnuelle: "↻ Annuelle",
    compteCultures: "{nombre} culture{s} sur {total}",
    aucuneCorrespondance: "Aucune culture ne correspond.",
    badgeAuPotager: "{nombre} au potager",
    badgeSemableMaintenant: "🌱 maintenant",
    marqueurPerpetuelle: " · ♾️ perpétuelle",
    marqueurVivace: " · 🔁 vivace",
    plantationPerenne: "Plantation pérenne",
    cultureInterieur: "En pot, toute l'année",

    // Vue « Calendrier ».
    videCalendrier:
      "Le calendrier se remplira dès que vous aurez ajouté des cultures.",
    calPrevu: "(prévu)",
    calReel: "(d'après votre journal)",
    calNoteLe: "{evenement} le {date}",
    legendeSemis: "Semis",
    legendePlantation: "Plantation, repiquage",
    legendeRecolte: "Récolte",
    legendeJournal: "Noté au journal",
    legendeTrame:
      "Trame claire&nbsp;: prévu · Plein&nbsp;: calculé d'après votre journal",

    // Vue « Journal ».
    videJournalTitre: "Votre journal est vide.",
    videJournalSuite:
      "Dès que vous noterez un semis — depuis «&nbsp;Aujourd'hui&nbsp;», une notification ou la liste de tâches — il s'écrira ici tout seul.",
    bilanRecoltes: "récoltés cette saison",
    bilanNbRecoltes: "récolte{s} notée{s}",
    bilanPlantes: "plantes suivies",
    bilanPertes: "perte{s}",
    bilanArrosages: "arrosage{s}",
    journalNPlantes: "{nombre} plantes",
    filtreTout: "Tout",
    etiquetteCause: "Cause : {cause}",

    // Fiche d'une plante.
    blocProchaineEtape: "Prochaine étape",
    duAuLong: "Du {debut} au {fin}",
    calculeeDepuisJournal:
      "Calculée depuis votre journal, et non depuis une moyenne saisonnière.",
    noterUneRecolte: "Noter une récolte",
    cestFaitEtape: "C'est fait : {etape}",
    plusRienDePrevu: "Plus rien de prévu pour cette plante.",
    grammesPlaceholder: "grammes",
    boutonEnregistrer: "Enregistrer",
    quantiteFacultative: "La quantité est facultative.",
    dejaNotees: "{nombre} récolte{s} déjà notée{s}, {poids} au total.",
    blocReglages: "Réglages",
    champZone: "Zone",
    champSurnom: "Surnom",
    surnomPlaceholder: "variété, emplacement…",
    champRappelsPlante: "Rappels pour cette plante",
    champPrevenirAvance: "Prévenir à l'avance",
    champRessemerTous: "Ressemer tous les",
    uniteJours: "jours",
    aideEchelonnement:
      "Pour les semis échelonnés&nbsp;: radis, laitue, haricot. À chaque intervalle, un rappel propose d'ouvrir le lot suivant — qui devient une plante à part, avec son propre journal. 0 pour désactiver.",
    blocCorriger: "Corriger",
    boutonAnnulerEvt: "Annuler «&nbsp;{evenement}&nbsp;»",
    boutonRetirerPlante: "Retirer du potager",
    confirmRetirerPlante: "Retirer cette plante et son journal ?",

    // Arrosage, dans la fiche.
    blocArrosage: "Arrosage",
    eauProchainLe: "Prochain arrosage le {date}",
    eauTousLesJours: "Tous les {jours} jours",
    eauDernierLeLong: "dernier le {date}",
    eauJamaisCourt: "jamais arrosée depuis sa mise en terre",
    boutonJeViensDArroser: "Je viens d'arroser",
    eauSuiviInactif: "Suivi d'arrosage inactif.",
    champRappelsEau: "Rappels d'arrosage",
    champArroserTous: "Arroser tous les",
    aideFrequenceEau:
      "0 pour suivre la fréquence de la fiche{precision}. Un semis boit deux fois plus souvent qu'un plant installé, l'écart est appliqué automatiquement.",
    aideFrequenceEauPrecision: " ({jours} j)",

    // Frise du journal.
    blocJournal: "Journal",
    friseArrosages: "{nombre} arrosages",
    frisePeriode: "du {debut} au {fin}",
    videFrise:
      "Rien de noté pour l'instant. Le premier «&nbsp;C'est fait&nbsp;» démarrera la frise, et les dates suivantes se calculeront depuis lui.",

    // Fiche d'une culture.
    chargementCourt: "Chargement…",
    blocAjouter: "Ajouter à mon potager",
    dejaAuPotager:
      "Déjà {nombre} au potager ({zones}). En ajouter un autre permet d'échelonner les semis.",
    boutonAjouter: "Ajouter",
    blocCetteFiche: "Cette fiche",
    ficheCorrigee:
      "Vous avez corrigé cette fiche livrée. Vos valeurs remplacent les miennes.",
    ficheCreee: "Fiche que vous avez créée.",
    ficheEstimations:
      "Les durées de cette fiche sont des estimations, pas des mesures. Si votre jardin dit autre chose, corrigez-les : vos valeurs feront foi.",
    boutonCorrigerFiche: "Corriger cette fiche",
    boutonRetablirFiche: "Rétablir l'originale",
    confirmRetablirFiche: "Rétablir la fiche d'origine et perdre vos corrections ?",
    blocCalendrierType: "Calendrier type, chez vous",
    aideCalendrierType:
      "Calculé depuis vos dates de gelées ({derniere} et {premiere}), pas depuis une moyenne nationale.",
    blocLaCulture: "La culture",
    cleExposition: "Exposition",
    cleArrosage: "Arrosage",
    valeurArrosage: "{besoin}, tous les {jours} j",
    cleEspacement: "Espacement",
    cleFamille: "Famille",
    cleDifficulte: "Difficulté",
    cleCycle: "Cycle",
    cycleContinue: "Perpétuelle — récolte quasi continue",
    cycleVivace: "Vivace — elle revient chaque année",
    cycleInterieur: "Plante d'intérieur — elle ne connaît pas de saison",
    cycleAnnuelle: "Annuelle — à ressemer chaque année",
    cleGel: "Gel",
    gelSupporte: "Supporte",
    gelSupporteJusqua: "Supporte jusqu'à {temperature} °C",
    gelCraint: "Craint le gel",
    gelInterieurMini: "Jamais en dessous de {temperature} °C",
    cleSol: "Sol",
    cleConseils: "Conseils",
    blocVoisinage: "Voisinage",
    bonsVoisins: "Bons voisins",
    aEloigner: "À éloigner",

    // Vue « Réglages ».
    titreSaison: "Saison et gelées",
    aideSaison:
      "Ces deux dates calent <strong>tout</strong> le calendrier. Aucune date du catalogue n'est écrite en dur&nbsp;: chaque période est un décalage en jours par rapport à elles. Les modifier redessine immédiatement les {total} fiches.",
    champClimat: "Climat",
    presetOceanique: "Ouest océanique (Bretagne, Loire)",
    presetNordEst: "Nord et Est continental",
    presetMidi: "Midi méditerranéen",
    presetMontagne: "Montagne",
    presetPersonnalise: "Dates personnalisées",
    champGeleePrintemps: "Dernière gelée de printemps",
    champGeleeAutomne: "Première gelée d'automne",
    aideGelees:
      "Si vous tenez un relevé, vos propres dates valent mieux que n'importe quelle moyenne.",

    titreLangue: "Langue",
    champLangue: "Langue de l'interface",
    langueAuto: "Automatique (langue de Home Assistant)",
    langueFr: "Français",
    langueEn: "English",
    aideLangue:
      "Ce réglage vaut pour tout&nbsp;: le panneau, le catalogue, les rappels, le calendrier et les noms affichés des entités. Les <code>entity_id</code>, eux, sont figés à la création et ne changent pas — vos automatisations survivent au changement de langue.",
    aideLangueEtat:
      "Les capteurs de phase passent eux aussi dans la nouvelle langue&nbsp;: leur historique garde donc les anciens libellés avant le changement.",

    titreRappels: "Rappels",
    sousTitreAQui: "À qui",
    aideAQui:
      "Seules les applications mobiles portent les boutons «&nbsp;C'est fait&nbsp;»&nbsp;; c'est par eux que votre journal se remplit sans effort. Sans destinataire coché, aucun rappel ne part.",
    aucuneAppMobile: "Aucune application mobile connectée à Home Assistant.",
    sansBoutonAction: " — sans bouton d'action",
    sousTitreQuoi: "Quoi",
    etapeArroser: "Arroser",
    aideQuoi:
      "Tout est activé au départ&nbsp;: mieux vaut décocher ce qui dérange que découvrir en juillet qu'un rappel n'est jamais parti.",
    aideQuoiEau:
      "Décocher «&nbsp;Arroser&nbsp;» tait les rappels d'eau sans arrêter le suivi&nbsp;: les échéances restent visibles et le bouton «&nbsp;Arrosé&nbsp;» reste à portée.",
    sousTitreQuand: "Quand",
    champHeure: "Heure de la vérification",
    champRelancer: "Relancer pendant la récolte",
    aideRelancer:
      "Une courgette se cueille tous les deux jours&nbsp;: prévenir une seule fois ne sert à rien. Mettez 0 pour un unique rappel par récolte.",
    sousTitreComment: "Comment",
    champResume:
      "Un seul message groupé quand plusieurs choses tombent le même jour",
    aideResume:
      "Au printemps, cinq rappels le même matin sont cinq rappels qu'on balaie sans lire. Le revers&nbsp;: un message groupé ne peut pas porter de bouton «&nbsp;C'est fait&nbsp;», puisqu'il faudrait deviner de quelle plante il s'agit.",
    aideResumePlante:
      "Le réglage par plante reste prioritaire&nbsp;: chaque plante a son interrupteur de rappels et peut avoir son propre délai, dans sa fiche.",

    titreArrosage: "Arrosage",
    champSuivreArrosage: "Suivre l'arrosage",
    aideArrosageCoupe:
      "Décoché, l'eau disparaît entièrement de l'application. Pour garder le suivi mais sans notification, laissez coché ici et décochez «&nbsp;Arroser&nbsp;» dans <strong>Rappels&nbsp;· Quoi</strong>.",
    aideArrosageTheorique:
      "Le calcul est théorique et assumé comme tel&nbsp;: il part de la fréquence indiquée sur la fiche, et le compte à rebours repart quand <strong>vous</strong> déclarez avoir arrosé. Rien n'observe le sol ni la météo.",
    aideArrosageGardeFous:
      "Deux garde-fous évitent les rappels absurdes&nbsp;: une plante pas encore en terre ne réclame rien, et les zones non abritées se taisent entre la première et la dernière gelée.",

    titreZones: "Zones",
    aideZones:
      "Le décalage avance ou retarde tout le calendrier des plantes de la zone. Il ne s'applique <strong>jamais</strong> à une date de votre journal&nbsp;: un fait n'est pas une prévision.",
    zoneNomPlaceholder: "Nom de la zone",
    uniteJourCourt: "j",
    zoneAbritee: "abritée",
    zoneAbriteeAide:
      "Serre, châssis ou pots : l'arrosage y est rappelé toute l'année",
    boutonSupprimer: "Supprimer",
    boutonAjouterZone: "Ajouter une zone",
    boutonEnregistrerZones: "Enregistrer les zones",
    erreurGarderUneZone: "Gardez au moins une zone.",

    titreMesFiches: "Mes fiches",
    aideMesFiches:
      "Ajoutez les légumes qui manquent au catalogue. Vos fiches sont conservées dans votre jardin&nbsp;: une mise à jour de l'intégration ne les efface pas.",
    marqueurFicheCorrigee: " · fiche livrée corrigée",
    marqueurFicheInedite: " · fiche inédite",
    aucuneFichePerso: "Aucune fiche personnelle pour l'instant.",
    boutonAjouterFiche: "Ajouter une fiche",
    boutonModifier: "Modifier",
    confirmSupprimerFiche: "Supprimer cette fiche ?",

    titreAffichage: "Affichage",
    champMasquerTerminees:
      "Masquer les plantes terminées ou perdues dans «&nbsp;Mon potager&nbsp;»",
    aideMasquerTerminees:
      "Elles restent dans le journal et dans le calendrier&nbsp;: c'est l'historique de votre potager, il ne s'efface pas.",

    // Formulaire d'une fiche personnelle.
    titreModifierFiche: "Modifier la fiche",
    titreNouvelleFiche: "Nouvelle fiche",
    blocIdentite: "Identité",
    champNomFiche: "Nom *",
    exempleNomFiche: "Chou-rave",
    champEmoji: "Emoji",
    champCategorie: "Catégorie *",
    champFamilleFiche: "Famille",
    exempleFamille: "Brassicacées",
    blocConditions: "Conditions",
    champExposition: "Exposition *",
    champBesoinEau: "Besoin en eau *",
    champDifficulte: "Difficulté",
    difficulteFacile: "★ Facile",
    difficulteMoyenne: "★★ Moyenne",
    difficulteExigeante: "★★★ Exigeante",
    champResisteGel: "Résiste au gel",
    aideGelFiche:
      "Décochez pour une culture gélive&nbsp;: sa récolte sera alors automatiquement plafonnée à votre première gelée d'automne.",
    champPerenne: "Pérenne (ne se replante pas chaque année)",
    blocPeriodes: "Périodes",
    aidePeriodesLivree:
      "Les périodes de cette fiche sont calées sur <strong>vos dates de gelées</strong>, et non sur des mois fixes&nbsp;: c'est ce qui les rend justes chez vous. Elles sont conservées telles quelles.",
    aidePeriodesMois: "En mois, comme sur un sachet de graines.",
    aidePeriodesPerenne:
      "Pour une pérenne, seule «&nbsp;Récolter&nbsp;» compte vraiment&nbsp;: sa récolte revient chaque année.",
    separateurPeriode: "à",
    blocDurees: "Durées du cycle",
    champSemisRecolte: "Du semis à la récolte",
    champSemisRepiquage: "Du semis au repiquage",
    champPlantationRecolte: "De la plantation à la récolte",
    champDureeRecolte: "La récolte dure",
    aideDurees:
      "Ce sont ces durées qui permettent de recalculer votre récolte à partir de la date où vous avez réellement semé. Laissez vide ce que vous ne savez pas, mais il en faut au moins une.",
    blocNotes: "Notes",
    champConseilArrosage: "Conseil d'arrosage",
    champSolFiche: "Sol",
    exempleSol: "riche et frais",
    champConseils: "Conseils (un par ligne)",
    boutonEnregistrerFiche: "Enregistrer la fiche",
    boutonAnnuler: "Annuler",
    ficheIncomplete: "Fiche incomplète.",

    moisInitiales: "J,F,M,A,M,J,J,A,S,O,N,D",
    moisLongs:
      "janvier,février,mars,avril,mai,juin,juillet,août,septembre,octobre,novembre,décembre",
    localeDate: "fr-FR",
  },
  en: {
    vueAujourdhui: "Today",
    vuePotager: "My garden",
    vueCatalogue: "Catalogue",
    vueCalendrier: "Calendar",
    vueJournal: "Journal",
    vueReglages: "Settings",
    enteteAFaire: "{nombre} to do",
    chargement: "Loading the garden…",
    chargementReglages: "Loading settings…",
    injoignable: "Cannot reach Rhizome.",
    actionRefusee: "Action refused.",
    ficheIndisponible: "Crop entry unavailable.",

    "cat_legume-fruit": "Fruiting vegetables",
    "cat_legume-racine": "Roots",
    "cat_legume-gousse": "Pods",
    "cat_legume-bulbe": "Bulbs",
    "cat_legume-feuille": "Leaves",
    cat_aromatique: "Herbs",
    "cat_petit-fruit": "Soft fruit",
    cat_fruitier: "Fruit trees",
    "cat_fleur-compagne": "Companion flowers",
    cat_cereale: "Cereals and seeds",
    cat_medicinale: "Medicinal",
    "cat_plante-interieur": "Houseplants",

    "expo_plein-soleil": "Full sun",
    "expo_mi-ombre": "Partial shade",
    expo_ombre: "Shade",
    eau_faible: "Little water",
    eau_moyen: "Moderate watering",
    eau_eleve: "Plenty of water",

    evt_seme: "Sown",
    evt_repique: "Transplanted",
    evt_plante: "Planted",
    evt_recolte: "Harvested",
    evt_termine: "Finished",
    evt_perdu: "Lost",
    evt_arrosage: "Watered",

    etape_semis_interieur: "Sow under cover",
    etape_semis_direct: "Sow in place",
    etape_repiquage: "Transplant",
    etape_plantation: "Plant out",
    etape_recolte: "Harvest",

    quandMaintenant: "Now is the time",
    quandAujourdhui: "Today",
    quandDemain: "Tomorrow",
    quandDans: "In {jours} days",
    quandDepuisHier: "Since yesterday",
    quandDepuis: "{jours} days ago",

    videPotagerTitre: "Your garden is empty.",
    videPotagerSuite:
      "Pick your first vegetables from the catalogue&nbsp;: {total} crops are waiting.",
    ouvrirCatalogue: "Open the catalogue",
    videRienAFaire: "Nothing to do in the garden today.",
    videRienAFaireSuite: "{nombre} plant{s} tracked, nothing due just yet.",
    voirPotager: "See my garden",
    sectionMaintenant: "Now is the time",
    sectionAPreparer: "Coming up",
    sectionAArroser: "Needs watering · {nombre}",
    eauTousLesNJours: "every {jours} d",
    eauDernierLe: "Last watered {date}",
    eauJamais: "Never watered since it went in the ground",
    eauChipRetard: "Needs water · {jours} d overdue",
    eauChipAujourdhui: "Needs water today",
    eauChipOk: "Watered · next in {jours} d",
    eauChipFait: "Watered · recorded in the journal",
    boutonArroser: "Water",
    boutonToutArroser: "Water all ({nombre})",
    fenetreJusquAu: "Window until {date}",
    dApresVotreJournal: "from your journal",
    enregistrerAuJournal: "Record in the journal",
    boutonFait: "Done",
    boutonSeme: "Sown",

    videAucunePlante: "No plants yet.",
    ajouterDesLegumes: "Add some vegetables",
    recoltesSuffixe: "{poids} harvested",
    rienDePrevu: "Nothing planned",
    noterUnArrosage: "Record a watering",

    chercherPlaceholder: "Search a vegetable, a fruit, a family…",
    filtreSemable: "🌱 Sowable now",
    filtreFacile: "★ Easy",
    filtreVivace: "🔁 Perennial",
    filtreContinue: "♾️ Harvest all year",
    filtreAnnuelle: "↻ Annual",
    compteCultures: "{nombre} crop{s} of {total}",
    aucuneCorrespondance: "No crop matches.",
    badgeAuPotager: "{nombre} in the garden",
    badgeSemableMaintenant: "🌱 now",
    marqueurPerpetuelle: " · ♾️ everbearing",
    marqueurVivace: " · 🔁 perennial",
    plantationPerenne: "Perennial planting",
    cultureInterieur: "In a pot, all year round",

    videCalendrier: "The calendar fills up as soon as you add a crop.",
    calPrevu: "(forecast)",
    calReel: "(from your journal)",
    calNoteLe: "{evenement} on {date}",
    legendeSemis: "Sowing",
    legendePlantation: "Planting, transplanting",
    legendeRecolte: "Harvest",
    legendeJournal: "Recorded in the journal",
    legendeTrame:
      "Hatched&nbsp;: forecast · Solid&nbsp;: computed from your journal",

    videJournalTitre: "Your journal is empty.",
    videJournalSuite:
      "As soon as you record a sowing — from «&nbsp;Today&nbsp;», a notification or the to-do list — it writes itself here.",
    bilanRecoltes: "harvested this season",
    bilanNbRecoltes: "harvest{s} recorded",
    bilanPlantes: "plants tracked",
    bilanPertes: "loss{s}",
    bilanArrosages: "watering{s}",
    journalNPlantes: "{nombre} plants",
    filtreTout: "All",
    etiquetteCause: "Cause: {cause}",

    blocProchaineEtape: "Next step",
    duAuLong: "From {debut} to {fin}",
    calculeeDepuisJournal:
      "Computed from your journal, not from a seasonal average.",
    noterUneRecolte: "Record a harvest",
    cestFaitEtape: "Done: {etape}",
    plusRienDePrevu: "Nothing left planned for this plant.",
    grammesPlaceholder: "grams",
    boutonEnregistrer: "Save",
    quantiteFacultative: "The quantity is optional.",
    dejaNotees: "{nombre} harvest{s} already recorded, {poids} in total.",
    blocReglages: "Settings",
    champZone: "Zone",
    champSurnom: "Nickname",
    surnomPlaceholder: "variety, spot…",
    champRappelsPlante: "Reminders for this plant",
    champPrevenirAvance: "Warn in advance",
    champRessemerTous: "Sow again every",
    uniteJours: "days",
    aideEchelonnement:
      "For successional sowing&nbsp;: radish, lettuce, beans. At each interval a reminder offers to open the next batch — which becomes a plant of its own, with its own journal. 0 to switch it off.",
    blocCorriger: "Fix a mistake",
    boutonAnnulerEvt: "Undo «&nbsp;{evenement}&nbsp;»",
    boutonRetirerPlante: "Remove from the garden",
    confirmRetirerPlante: "Remove this plant and its journal?",

    blocArrosage: "Watering",
    eauProchainLe: "Next watering on {date}",
    eauTousLesJours: "Every {jours} days",
    eauDernierLeLong: "last on {date}",
    eauJamaisCourt: "never watered since it went in the ground",
    boutonJeViensDArroser: "I have just watered",
    eauSuiviInactif: "Watering tracking is off.",
    champRappelsEau: "Watering reminders",
    champArroserTous: "Water every",
    aideFrequenceEau:
      "0 to follow the frequency on the crop entry{precision}. A seedling drinks twice as often as an established plant, and that difference is applied for you.",
    aideFrequenceEauPrecision: " ({jours} d)",

    blocJournal: "Journal",
    friseArrosages: "{nombre} waterings",
    frisePeriode: "from {debut} to {fin}",
    videFrise:
      "Nothing recorded yet. The first «&nbsp;Done&nbsp;» starts the timeline, and the dates that follow are computed from it.",

    chargementCourt: "Loading…",
    blocAjouter: "Add to my garden",
    dejaAuPotager:
      "Already {nombre} in the garden ({zones}). Adding another lets you stagger the sowings.",
    boutonAjouter: "Add",
    blocCetteFiche: "This crop entry",
    ficheCorrigee:
      "You have corrected this shipped entry. Your values replace mine.",
    ficheCreee: "An entry you created.",
    ficheEstimations:
      "The durations in this entry are estimates, not measurements. If your garden says otherwise, correct them: your values win.",
    boutonCorrigerFiche: "Correct this entry",
    boutonRetablirFiche: "Restore the original",
    confirmRetablirFiche: "Restore the original entry and lose your corrections?",
    blocCalendrierType: "Typical calendar, where you are",
    aideCalendrierType:
      "Computed from your frost dates ({derniere} and {premiere}), not from a national average.",
    blocLaCulture: "The crop",
    cleExposition: "Exposure",
    cleArrosage: "Watering",
    valeurArrosage: "{besoin}, every {jours} d",
    cleEspacement: "Spacing",
    cleFamille: "Family",
    cleDifficulte: "Difficulty",
    cleCycle: "Cycle",
    cycleContinue: "Everbearing — almost continuous harvest",
    cycleVivace: "Perennial — it comes back every year",
    cycleInterieur: "Houseplant — it has no seasons",
    cycleAnnuelle: "Annual — to be sown again each year",
    cleGel: "Frost",
    gelSupporte: "Hardy",
    gelSupporteJusqua: "Hardy down to {temperature} °C",
    gelCraint: "Frost-tender",
    gelInterieurMini: "Never below {temperature} °C",
    cleSol: "Soil",
    cleConseils: "Tips",
    blocVoisinage: "Neighbours",
    bonsVoisins: "Good neighbours",
    aEloigner: "Keep apart",

    titreSaison: "Season and frosts",
    aideSaison:
      "These two dates anchor <strong>the whole</strong> calendar. No date in the catalogue is hard-coded&nbsp;: every period is an offset in days from them. Changing them redraws all {total} entries at once.",
    champClimat: "Climate",
    presetOceanique: "Oceanic west (Brittany, Loire)",
    presetNordEst: "Continental north and east",
    presetMidi: "Mediterranean south",
    presetMontagne: "Mountain",
    presetPersonnalise: "Custom dates",
    champGeleePrintemps: "Last spring frost",
    champGeleeAutomne: "First autumn frost",
    aideGelees:
      "If you keep records of your own, your dates beat any average.",

    titreLangue: "Language",
    champLangue: "Interface language",
    langueAuto: "Automatic (Home Assistant language)",
    langueFr: "Français",
    langueEn: "English",
    aideLangue:
      "This setting covers everything&nbsp;: the panel, the catalogue, reminders, the calendar and the displayed names of entities. The <code>entity_id</code>s are fixed when an entity is created and do not change — your automations survive a language switch.",
    aideLangueEtat:
      "Phase sensors switch language too&nbsp;: their history therefore keeps the old labels from before the change.",

    titreRappels: "Reminders",
    sousTitreAQui: "Who",
    aideAQui:
      "Only mobile apps carry the «&nbsp;Done&nbsp;» buttons&nbsp;; they are how your journal fills itself in. With no recipient ticked, no reminder is sent.",
    aucuneAppMobile: "No mobile app connected to Home Assistant.",
    sansBoutonAction: " — no action button",
    sousTitreQuoi: "What",
    etapeArroser: "Water",
    aideQuoi:
      "Everything is on to begin with&nbsp;: better to untick what bothers you than to find out in July that a reminder never went out.",
    aideQuoiEau:
      "Unticking «&nbsp;Water&nbsp;» silences the watering reminders without stopping the tracking&nbsp;: the due dates stay visible and the «&nbsp;Watered&nbsp;» button stays within reach.",
    sousTitreQuand: "When",
    champHeure: "Time of the daily check",
    champRelancer: "Repeat during the harvest",
    aideRelancer:
      "A courgette is picked every other day&nbsp;: telling you once is no use. Set 0 for a single reminder per harvest.",
    sousTitreComment: "How",
    champResume: "A single grouped message when several things fall on the same day",
    aideResume:
      "In spring, five reminders on the same morning are five reminders you swipe away unread. The downside&nbsp;: a grouped message cannot carry a «&nbsp;Done&nbsp;» button, since it would have to guess which plant you mean.",
    aideResumePlante:
      "The per-plant setting still wins&nbsp;: each plant has its own reminder switch and can have its own lead time, on its card.",

    titreArrosage: "Watering",
    champSuivreArrosage: "Track watering",
    aideArrosageCoupe:
      "Unticked, water disappears from the application entirely. To keep the tracking without notifications, leave this ticked and untick «&nbsp;Water&nbsp;» under <strong>Reminders&nbsp;· What</strong>.",
    aideArrosageTheorique:
      "The calculation is theoretical and openly so&nbsp;: it starts from the frequency on the crop entry, and the countdown restarts when <strong>you</strong> say you have watered. Nothing watches the soil or the weather.",
    aideArrosageGardeFous:
      "Two safeguards avoid absurd reminders&nbsp;: a plant not yet in the ground asks for nothing, and unsheltered zones stay silent between the first and the last frost.",

    titreZones: "Zones",
    aideZones:
      "The offset moves the whole calendar of the zone's plants forward or back. It <strong>never</strong> applies to a date from your journal&nbsp;: a fact is not a forecast.",
    zoneNomPlaceholder: "Zone name",
    uniteJourCourt: "d",
    zoneAbritee: "sheltered",
    zoneAbriteeAide:
      "Greenhouse, cold frame or pots: watering is reminded there all year round",
    boutonSupprimer: "Delete",
    boutonAjouterZone: "Add a zone",
    boutonEnregistrerZones: "Save the zones",
    erreurGarderUneZone: "Keep at least one zone.",

    titreMesFiches: "My entries",
    aideMesFiches:
      "Add the vegetables the catalogue is missing. Your entries live in your garden&nbsp;: an update of the integration does not erase them.",
    marqueurFicheCorrigee: " · shipped entry, corrected",
    marqueurFicheInedite: " · entry of your own",
    aucuneFichePerso: "No entries of your own yet.",
    boutonAjouterFiche: "Add an entry",
    boutonModifier: "Edit",
    confirmSupprimerFiche: "Delete this entry?",

    titreAffichage: "Display",
    champMasquerTerminees:
      "Hide finished or lost plants in «&nbsp;My garden&nbsp;»",
    aideMasquerTerminees:
      "They stay in the journal and in the calendar&nbsp;: that is your garden's history, and it is not erased.",

    titreModifierFiche: "Edit the entry",
    titreNouvelleFiche: "New entry",
    blocIdentite: "Identity",
    champNomFiche: "Name *",
    exempleNomFiche: "Kohlrabi",
    champEmoji: "Emoji",
    champCategorie: "Category *",
    champFamilleFiche: "Family",
    exempleFamille: "Brassicaceae",
    blocConditions: "Conditions",
    champExposition: "Exposure *",
    champBesoinEau: "Water need *",
    champDifficulte: "Difficulty",
    difficulteFacile: "★ Easy",
    difficulteMoyenne: "★★ Moderate",
    difficulteExigeante: "★★★ Demanding",
    champResisteGel: "Frost hardy",
    aideGelFiche:
      "Untick for a frost-tender crop&nbsp;: its harvest is then capped automatically at your first autumn frost.",
    champPerenne: "Perennial (not replanted every year)",
    blocPeriodes: "Periods",
    aidePeriodesLivree:
      "The periods in this entry are anchored to <strong>your frost dates</strong>, not to fixed months&nbsp;: that is what makes them right where you are. They are kept as they are.",
    aidePeriodesMois: "In months, as on a seed packet.",
    aidePeriodesPerenne:
      "For a perennial, only «&nbsp;Harvest&nbsp;» really counts&nbsp;: its harvest comes back every year.",
    separateurPeriode: "to",
    blocDurees: "Cycle durations",
    champSemisRecolte: "Sowing to harvest",
    champSemisRepiquage: "Sowing to transplanting",
    champPlantationRecolte: "Planting out to harvest",
    champDureeRecolte: "The harvest lasts",
    aideDurees:
      "These durations are what let the harvest be recomputed from the date you actually sowed. Leave blank whatever you do not know, but at least one is needed.",
    blocNotes: "Notes",
    champConseilArrosage: "Watering tip",
    champSolFiche: "Soil",
    exempleSol: "rich and moist",
    champConseils: "Tips (one per line)",
    boutonEnregistrerFiche: "Save the entry",
    boutonAnnuler: "Cancel",
    ficheIncomplete: "Incomplete entry.",

    moisInitiales: "J,F,M,A,M,J,J,A,S,O,N,D",
    moisLongs:
      "January,February,March,April,May,June,July,August,September,October,November,December",
    localeDate: "en-GB",
  },
};

/** Les six vues, dans l'ordre de la barre de navigation. */
const VUES = [
  { id: "aujourdhui", cle: "vueAujourdhui", icone: "mdi:white-balance-sunny" },
  { id: "potager", cle: "vuePotager", icone: "mdi:sprout" },
  { id: "catalogue", cle: "vueCatalogue", icone: "mdi:book-open-variant" },
  { id: "calendrier", cle: "vueCalendrier", icone: "mdi:calendar-month" },
  { id: "journal", cle: "vueJournal", icone: "mdi:notebook-outline" },
  { id: "reglages", cle: "vueReglages", icone: "mdi:cog-outline" },
];

const CATEGORIES_IDS = [
  "legume-fruit", "legume-racine", "legume-gousse", "legume-bulbe",
  "legume-feuille", "aromatique", "petit-fruit", "fruitier", "fleur-compagne",
  "cereale", "medicinale", "plante-interieur",
];

const libelleCategorie = (id) => (id ? T(`cat_${id}`) : "");

const ICONES_EXPOSITION = {
  "plein-soleil": "mdi:weather-sunny",
  "mi-ombre": "mdi:weather-partly-cloudy",
  ombre: "mdi:weather-cloudy",
};

const libelleExposition = (id) => (id ? T(`expo_${id}`) : "");
const libelleEau = (id) => (id ? T(`eau_${id}`) : "");

const COULEURS_ETAPE = {
  semis_interieur: "var(--rhizome-semis)",
  semis_direct: "var(--rhizome-semis)",
  repiquage: "var(--rhizome-plantation)",
  plantation: "var(--rhizome-plantation)",
  recolte: "var(--rhizome-recolte)",
};

/** Miroir cote client de JOURNAL_POUR_ETAPE (notifier.py) : ce qu'un
 *  « C'est fait » inscrit au journal selon l'etape concernee. */
const EVT_POUR_ETAPE = {
  semis_interieur: { evenement: "seme", mode: "interieur" },
  semis_direct: { evenement: "seme", mode: "direct" },
  repiquage: { evenement: "repique" },
  plantation: { evenement: "plante" },
  recolte: { evenement: "recolte" },
  // Le ressemis ne note rien : il ouvre un nouveau lot, donc une nouvelle
  // plante. D'ou une commande distincte.
  ressemer: { commande: "rhizome/ressemer" },
};

const libelleEvenement = (type) => (type ? T(`evt_${type}`) : "");

/** Les trois etats d'arrosage, chacun avec son icone et son fond.
 *
 *  Un bouton bleu « Arrosé » posait la mauvaise question : etait-ce un constat
 *  ou une commande ? L'etat vit desormais dans une pastille — au passe quand
 *  c'est un fait, a l'impératif sur le bouton d'a cote — et l'icone suffit a
 *  trancher sans lire : alerte, arrosoir, ou coche. */
const NIVEAUX_EAU = {
  retard: { icone: "mdi:water-alert", cle: "eauChipRetard" },
  jour: { icone: "mdi:watering-can", cle: "eauChipAujourdhui" },
  ok: { icone: "mdi:water-check", cle: "eauChipOk" },
  fait: { icone: "mdi:check-circle", cle: "eauChipFait" },
};

const niveauEau = (eau) =>
  eau.jours_restants < 0 ? "retard" : eau.jours_restants === 0 ? "jour" : "ok";

/** La pastille d'etat. `confirme` la remplace quelques secondes par la
 *  confirmation du clic : le compte a rebours repart de lui-meme, mais rien ne
 *  disait que *ce* geste avait ete pris, ni ou il etait parti. */
function pastilleEau(eau, confirme = false) {
  const niveau = confirme ? "fait" : niveauEau(eau);
  const { icone, cle } = NIVEAUX_EAU[niveau];
  const jours = Math.abs(eau.jours_restants);
  return `<span class="chip-eau" data-niveau="${niveau}">
      <ha-icon icon="${icone}" style="--mdc-icon-size:15px"></ha-icon>
      ${T(cle, { jours })}
    </span>`;
}

/** Vrai quand l'eau n'est pas due : le bouton se fait discret, pour que la
 *  couleur pleine reste le signal de ce qui attend un geste. */
const eauAJour = (eau, confirme) => confirme || eau.jours_restants > 0;

// Au-delà de ce seuil, la récolte couvre l'essentiel de l'année : c'est ce
// qui sépare le poireau perpétuel, qu'on coupe en janvier comme en juillet,
// de l'asperge, qui ne donne que six semaines.
const RECOLTE_CONTINUE_JOURS = 240;

// Les mois sont des listes dans la table des textes, et non des tableaux
// separes : une langue de plus se traduit alors en un seul endroit.
const mois = () => T("moisInitiales").split(",");
const moisLongs = () => T("moisLongs").split(",");

const jour = (iso) => new Date(`${iso}T12:00:00`);
// `toLocaleDateString` avec la locale de la langue affichee, et non celle du
// navigateur : le reglage de Rhizome doit l'emporter, sinon un panneau mis en
// anglais garderait des dates au format francais.
const fmtCourt = (iso) =>
  jour(iso).toLocaleDateString(T("localeDate"), {
    day: "numeric",
    month: "short",
  });
const fmtLong = (iso) =>
  jour(iso).toLocaleDateString(T("localeDate"), {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
const kg = (grammes) =>
  grammes >= 1000 ? `${(grammes / 1000).toFixed(grammes % 1000 ? 2 : 0)} kg` : `${grammes} g`;

/** Identifiant stable derive d'un nom saisi, pour les zones. */
function slugifier(texte) {
  return (
    texte
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "zone"
  );
}

/** Refait le chemin inverse du serveur : une fiche stockee redevient les
 *  champs du formulaire, pour pouvoir la modifier. */
function _versFormulaire(fiche) {
  const periodes = {};
  for (const [cle, f] of Object.entries(fiche.fenetres || {})) {
    if (!f.date) continue;
    const debut = Number(f.date.slice(0, 2));
    const mois = Math.max(1, Math.round((f.duree_jours || 30) / 30));
    periodes[cle] = { debut, fin: ((debut - 1 + mois - 1) % 12) + 1 };
  }
  const cycle = fiche.cycle || {};
  return {
    id: fiche.id,
    nom: fiche.nom,
    emoji: fiche.emoji,
    categorie: fiche.categorie,
    famille: fiche.famille,
    exposition: fiche.exposition,
    arrosage: fiche.arrosage,
    sol: fiche.sol,
    espacement_cm: fiche.espacement_cm,
    difficulte: fiche.difficulte,
    gel: (fiche.rusticite || {}).gel !== false,
    perenne: !!fiche.perenne,
    periodes,
    jours_semis_a_recolte: cycle.jours_semis_a_recolte,
    jours_semis_a_repiquage: cycle.jours_semis_a_repiquage,
    jours_plantation_a_recolte: cycle.jours_plantation_a_recolte,
    duree_recolte_jours: cycle.duree_recolte_jours,
    conseils: fiche.conseils || [],
    // Une fiche livree garde ses fenetres ancrees aux gelees : le formulaire
    // ne les propose pas en mois, qui les figeraient sur le calendrier.
    livree: !fiche.perso || !!fiche.surcharge,
    fenetres_origine: fiche.fenetres || {},
  };
}

// Les guillemets comptent autant que les chevrons.
//
// La version precedente passait par `textContent` puis relisait `innerHTML`.
// Le serialiseur HTML n'echappe alors que `&`, `<` et `>` : les guillemets
// traversent intacts, parce qu'ils sont inoffensifs dans un noeud de texte.
// Or `echappe()` est aussi employe a l'interieur d'attributs — le surnom d'une
// plante dans `value="..."`, le nom d'une zone dans `title="..."`. Un surnom
// contenant un guillemet y fermait l'attribut et ouvrait les suivants : un
// `onmouseover` suffisait alors a executer du code dans l'origine de Home
// Assistant, avec la session de qui regarde le panneau.
//
// On echappe donc explicitement les cinq caracteres, sans dependre du
// serialiseur ni du contexte d'insertion.
const ENTITES = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

function echappe(texte) {
  return texte == null
    ? ""
    : String(texte).replace(/[&<>"']/g, (c) => ENTITES[c]);
}

/** Jours entre aujourd'hui et une date ISO. Negatif si elle est passee. */
function joursJusqu(iso) {
  const aujourdhui = new Date();
  aujourdhui.setHours(12, 0, 0, 0);
  return Math.round((jour(iso) - aujourdhui) / 86400000);
}

const estDansFenetre = (etape) =>
  joursJusqu(etape.debut) <= 0 && joursJusqu(etape.fin) >= 0;

/** « C'est le moment », « Demain », « Dans 5 jours », « Depuis 3 jours ». */
function quand(joursRestants, enCours) {
  if (enCours) return T("quandMaintenant");
  if (joursRestants === 0) return T("quandAujourdhui");
  if (joursRestants === 1) return T("quandDemain");
  if (joursRestants > 1) return T("quandDans", { jours: joursRestants });
  if (joursRestants === -1) return T("quandDepuisHier");
  return T("quandDepuis", { jours: Math.abs(joursRestants) });
}

/** Pluriel anglais et francais a la fois : les deux prennent un « s ».
 *  Les cles qui en ont besoin portent un `{s}` que l'on remplit ici. */
const pluriel = (nombre) => (Math.abs(nombre) > 1 ? "s" : "");

const STYLES = `
  :host {
    --rhizome-semis: #7cb342;
    --rhizome-plantation: #00897b;
    --rhizome-recolte: #ef6c00;
    --rhizome-eau: #29b6f6;
    --rhizome-rayon: var(--ha-card-border-radius, 12px);
    display: block;
    height: 100%;
    overflow: hidden;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif);
  }
  * { box-sizing: border-box; }

  .enveloppe { display: flex; flex-direction: column; height: 100%; }

  header {
    background: var(--app-header-background-color, var(--primary-color));
    color: var(--app-header-text-color, #fff);
    flex: 0 0 auto;
  }
  .barre-titre {
    display: flex; align-items: center; gap: 12px;
    padding: 0 16px; height: var(--header-height, 56px);
  }
  .barre-titre h1 { font-size: 20px; font-weight: 400; margin: 0; flex: 1; }
  .compteur-entete {
    background: rgba(255,255,255,.2); border-radius: 999px;
    padding: 3px 10px; font-size: 13px; font-weight: 500;
  }
  nav { display: flex; overflow-x: auto; scrollbar-width: none; }
  nav::-webkit-scrollbar { display: none; }
  nav button {
    flex: 1 0 auto; display: flex; align-items: center; justify-content: center; gap: 6px;
    min-width: 64px; padding: 10px 14px; border: 0; cursor: pointer;
    background: none; color: inherit; opacity: .7;
    border-bottom: 3px solid transparent; font-size: 13px; font-weight: 500;
    font-family: inherit; white-space: nowrap;
  }
  nav button[aria-selected="true"] { opacity: 1; border-bottom-color: currentColor; }
  nav button:hover { opacity: 1; background: rgba(255,255,255,.08); }

  main { flex: 1 1 auto; overflow-y: auto; padding: 16px; }
  .contenu { max-width: 1100px; margin: 0 auto; }

  h2 { font-size: 15px; font-weight: 500; margin: 24px 0 10px;
       color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: .5px; }
  h2:first-child { margin-top: 0; }

  .carte {
    background: var(--card-background-color, #fff);
    border-radius: var(--rhizome-rayon);
    box-shadow: var(--ha-card-box-shadow, 0 1px 3px rgba(0,0,0,.12));
    border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, transparent);
  }

  .grille { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
  .grille-large { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }

  /* --- Cartes d'action --------------------------------------------------- */
  .action { display: flex; align-items: center; gap: 14px; padding: 14px; }
  .action .emoji { font-size: 32px; line-height: 1; flex: 0 0 auto; }
  .action .corps { flex: 1 1 auto; min-width: 0; }
  .action .titre { font-size: 16px; font-weight: 500; }
  .action .detail { font-size: 13px; color: var(--secondary-text-color); margin-top: 2px; }
  .action .verbe { font-weight: 500; }
  .urgent .verbe { color: var(--rhizome-recolte); }

  /* --- Cartes de plante ------------------------------------------------- */
  .plante { padding: 14px; cursor: pointer; transition: box-shadow .15s, transform .15s; }
  .plante:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.16); }
  .plante-tete { display: flex; align-items: flex-start; gap: 12px; }
  .plante-tete .emoji { font-size: 30px; line-height: 1; }
  .plante-nom { font-size: 16px; font-weight: 500; }
  .plante-zone { font-size: 12px; color: var(--secondary-text-color); }
  .progression { height: 5px; border-radius: 3px; background: var(--divider-color); margin-top: 12px; overflow: hidden; }
  .progression > div { height: 100%; border-radius: 3px; }

  .pied-eau {
    display: flex; align-items: center; justify-content: space-between;
    gap: 8px; flex-wrap: wrap; margin-top: 10px; padding-top: 10px;
    border-top: 1px solid var(--divider-color);
    font-size: 12px; color: var(--secondary-text-color);
  }
  button.bouton.mini { padding: 5px 12px; font-size: 12px; }

  /* --- Pastille d'arrosage ----------------------------------------------
     L'etat d'arrosage tient dans une pastille, pas dans le libelle d'un
     bouton : trois fonds, trois icones, pour que « c'est fait » et « c'est a
     faire » ne se ressemblent pas. Le texte reste en couleur de premier plan,
     comme les badges de phase — un texte teinte sur un fond teinte de la meme
     teinte passe mal en theme sombre. */
  .chip-eau {
    display: inline-flex; align-items: center; gap: 5px; max-width: 100%;
    font-size: 12px; font-weight: 500; padding: 4px 10px; border-radius: 999px;
    background: color-mix(in srgb, var(--secondary-text-color) 14%, transparent);
    color: var(--primary-text-color); line-height: 1.35;
  }
  .chip-eau ha-icon { color: var(--secondary-text-color); flex: 0 0 auto; }
  .chip-eau[data-niveau="retard"] {
    background: color-mix(in srgb, var(--rhizome-recolte) 26%, transparent);
  }
  .chip-eau[data-niveau="retard"] ha-icon { color: var(--rhizome-recolte); }
  .chip-eau[data-niveau="jour"] {
    background: color-mix(in srgb, var(--rhizome-eau) 24%, transparent);
  }
  .chip-eau[data-niveau="jour"] ha-icon { color: var(--rhizome-eau); }
  .chip-eau[data-niveau="ok"] ha-icon { color: var(--rhizome-eau); }
  .chip-eau[data-niveau="fait"] {
    background: color-mix(in srgb, var(--rhizome-semis) 30%, transparent);
  }
  .chip-eau[data-niveau="fait"] ha-icon { color: var(--rhizome-semis); }

  .badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 999px;
    background: var(--divider-color); color: var(--primary-text-color); white-space: nowrap;
  }
  .badge.prevu { background: color-mix(in srgb, var(--secondary-text-color) 18%, transparent); }
  .badge.seme { background: color-mix(in srgb, var(--rhizome-semis) 25%, transparent); }
  .badge.plante { background: color-mix(in srgb, var(--rhizome-plantation) 25%, transparent); }
  .badge.en_recolte { background: color-mix(in srgb, var(--rhizome-recolte) 28%, transparent); }
  .badge.termine, .badge.perdu { background: color-mix(in srgb, var(--error-color) 20%, transparent); }

  /* --- Boutons ----------------------------------------------------------- */
  button.bouton {
    display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    border: 0; border-radius: 999px; padding: 9px 16px; cursor: pointer;
    font-size: 14px; font-weight: 500; font-family: inherit;
    background: var(--primary-color); color: var(--text-primary-color, #fff);
  }
  button.bouton:hover { filter: brightness(1.08); }
  button.bouton.discret { background: var(--divider-color); color: var(--primary-text-color); }
  button.bouton.danger { background: var(--error-color); color: #fff; }
  button.bouton:disabled { opacity: .5; cursor: default; }
  button.icone {
    border: 0; background: none; cursor: pointer; color: var(--secondary-text-color);
    padding: 8px; border-radius: 50%; display: inline-flex;
  }
  button.icone:hover { background: var(--divider-color); color: var(--primary-text-color); }

  /* --- Recherche et filtres --------------------------------------------- */
  .recherche { display: flex; align-items: center; gap: 10px; padding: 10px 14px; margin-bottom: 12px; }
  .recherche input {
    flex: 1; border: 0; background: none; outline: none; font-size: 16px;
    color: var(--primary-text-color); font-family: inherit; min-width: 0;
  }
  .puces { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 10px; scrollbar-width: none; }
  .puces::-webkit-scrollbar { display: none; }
  .puce {
    flex: 0 0 auto; border: 1px solid var(--divider-color); background: var(--card-background-color);
    color: var(--primary-text-color); border-radius: 999px; padding: 7px 14px;
    font-size: 13px; cursor: pointer; font-family: inherit; white-space: nowrap;
  }
  .puce[aria-pressed="true"] { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }

  /* --- Etat vide --------------------------------------------------------- */
  .vide { text-align: center; padding: 48px 20px; color: var(--secondary-text-color); }
  .vide .gros { font-size: 52px; margin-bottom: 12px; }
  .vide p { margin: 0 0 18px; line-height: 1.5; }

  /* --- Calendrier ------------------------------------------------------- */
  .cal-defilement { overflow-x: auto; padding: 4px; }
  .cal { min-width: 680px; }
  .cal-ligne { display: grid; grid-template-columns: 150px 1fr; align-items: center; gap: 10px; padding: 5px 0; }
  .cal-nom { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .cal-piste { position: relative; height: 24px; background: var(--divider-color); border-radius: 4px; }
  .cal-bande { position: absolute; top: 3px; height: 18px; border-radius: 4px; min-width: 3px; }
  .cal-bande.prevue { opacity: .4; background-image: repeating-linear-gradient(45deg, rgba(255,255,255,.5) 0 3px, transparent 3px 6px); }
  .cal-entete { display: grid; grid-template-columns: 150px 1fr; gap: 10px; padding-bottom: 6px; }
  .cal-mois { display: grid; grid-template-columns: repeat(12, 1fr); font-size: 11px; color: var(--secondary-text-color); text-align: center; }
  .cal-aujourdhui { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--error-color); z-index: 2; }
  .legende { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; font-size: 12px; color: var(--secondary-text-color); }
  .legende span { display: inline-flex; align-items: center; gap: 6px; }
  .pastille { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }

  /* --- Journal ---------------------------------------------------------- */
  .journal-ligne { display: flex; gap: 14px; padding: 12px 14px; align-items: flex-start; }
  .journal-date { flex: 0 0 72px; font-size: 12px; color: var(--secondary-text-color); padding-top: 2px; }
  .journal-corps { flex: 1; min-width: 0; }
  .journal-note { font-size: 13px; color: var(--secondary-text-color); margin-top: 2px; font-style: italic; }
  .bilan { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin-bottom: 20px; }
  .bilan .tuile { padding: 16px; text-align: center; }
  .bilan .chiffre { font-size: 26px; font-weight: 500; }
  .bilan .etiquette { font-size: 12px; color: var(--secondary-text-color); margin-top: 2px; }

  /* --- Fiche (panneau lateral) ------------------------------------------ */
  .voile {
    position: fixed; inset: 0; background: rgba(0,0,0,.45);
    display: flex; justify-content: flex-end; z-index: 10;
  }
  .fiche {
    width: min(560px, 100%); height: 100%; overflow-y: auto;
    background: var(--primary-background-color);
    box-shadow: -4px 0 24px rgba(0,0,0,.25);
    animation: glisse .18s ease-out;
  }
  @keyframes glisse { from { transform: translateX(24px); opacity: .6; } }
  .fiche-tete {
    position: sticky; top: 0; z-index: 1; display: flex; align-items: center; gap: 12px;
    padding: 14px 16px; background: var(--card-background-color);
    border-bottom: 1px solid var(--divider-color);
  }
  .fiche-tete .emoji { font-size: 30px; }
  .fiche-tete h3 { margin: 0; font-size: 18px; font-weight: 500; flex: 1; }
  .fiche-corps { padding: 16px; display: flex; flex-direction: column; gap: 16px; }
  .bloc { padding: 14px; }
  .bloc h4 { margin: 0 0 10px; font-size: 13px; text-transform: uppercase;
             letter-spacing: .5px; color: var(--secondary-text-color); font-weight: 500; }
  .faits { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
  .fait { font-size: 13px; }
  .fait .cle { color: var(--secondary-text-color); font-size: 11px; text-transform: uppercase; }
  .fait .valeur { margin-top: 2px; }
  ul.conseils { margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.6; }
  .compagnes { display: flex; flex-wrap: wrap; gap: 6px; }
  .compagne { font-size: 12px; padding: 4px 10px; border-radius: 999px; background: var(--divider-color); }
  .frise { display: flex; flex-direction: column; gap: 0; }
  .frise-etape { display: flex; gap: 12px; }
  .frise-trait { flex: 0 0 12px; display: flex; flex-direction: column; align-items: center; }
  .frise-point { width: 10px; height: 10px; border-radius: 50%; background: var(--primary-color); margin-top: 5px; }
  /* Creux et bleu : un arrosage se lit dans le journal sans se confondre avec
     une etape du cycle, qu'il ne fait pas avancer (invariant 6). */
  .frise-point.eau {
    background: var(--card-background-color, #fff);
    border: 2px solid var(--rhizome-eau);
  }
  /* Largeur figee : la goutte tient la meme colonne que l'emoji des autres
     lignes, sinon le journal part en escalier. */
  .journal-ligne .goutte { flex: 0 0 20px; color: var(--rhizome-eau); --mdc-icon-size: 20px; }
  .frise-barre { flex: 1; width: 2px; background: var(--divider-color); min-height: 14px; }
  .frise-texte { flex: 1; padding-bottom: 14px; font-size: 14px; }
  .frise-texte .date { font-size: 12px; color: var(--secondary-text-color); }
  .reglage { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 9px 0; }
  .reglage label { font-size: 14px; }
  .reglage select, .reglage input {
    border: 1px solid var(--divider-color); border-radius: 8px; padding: 7px 10px;
    background: var(--card-background-color); color: var(--primary-text-color);
    font-family: inherit; font-size: 14px; max-width: 58%;
  }
  .actions-fiche { display: flex; flex-wrap: wrap; gap: 8px; }

  .aide {
    font-size: 13px; line-height: 1.5; color: var(--secondary-text-color);
    margin: 10px 0 0;
  }
  .bloc > .aide:first-child { margin-top: 0; margin-bottom: 12px; }
  label.case {
    display: flex; align-items: flex-start; gap: 10px; padding: 7px 0;
    font-size: 14px; cursor: pointer;
  }
  label.case input { width: 18px; height: 18px; flex: 0 0 auto; margin-top: 1px; }
  .ligne-zone {
    display: flex; align-items: center; gap: 8px; padding: 6px 0;
    border-bottom: 1px solid var(--divider-color);
  }
  .ligne-zone:last-child { border-bottom: 0; }
  .ligne-zone .zone-nom { flex: 1; min-width: 0; }
  .ligne-zone input, .ligne-zone select, .reglage textarea {
    border: 1px solid var(--divider-color); border-radius: 8px; padding: 7px 10px;
    background: var(--card-background-color); color: var(--primary-text-color);
    font-family: inherit; font-size: 14px;
  }
  .reglage > span { display: flex; align-items: center; gap: 6px; font-size: 14px;
                    color: var(--secondary-text-color); }

  .avertissement {
    display: flex; align-items: flex-start; gap: 8px; margin-top: 12px;
    background: color-mix(in srgb, var(--warning-color, #ef6c00) 16%, transparent);
    color: var(--primary-text-color); padding: 10px 12px;
    border-radius: var(--rhizome-rayon); font-size: 13px; line-height: 1.5;
  }

  .erreur {
    background: color-mix(in srgb, var(--error-color) 15%, transparent);
    color: var(--error-color); padding: 12px 14px; border-radius: var(--rhizome-rayon);
    margin-bottom: 14px; font-size: 14px;
  }
  .chargement { text-align: center; padding: 48px; color: var(--secondary-text-color); }

  @media (max-width: 600px) {
    main { padding: 12px; }
    nav button span.etiquette { display: none; }
    nav button { min-width: 0; }
    .fiche { width: 100%; }
  }
`;

class RhizomePanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._vue = "aujourdhui";
    this._jardin = null;
    this._catalogue = null;
    this._fiche = null;
    this._erreur = null;
    this._chargement = true;
    this._recherche = "";
    this._filtreCategorie = null;
    this._filtreDifficulte = null;
    this._filtreVie = null;
    this._filtreJournal = null;
    this._anneeCal = new Date().getFullYear();
    this._signature = null;
    this._rendu = false;
    this._reglages = null;
    this._cataloguePerso = null;
    this._calendrier = null;
  }

  /** Home Assistant pousse un nouvel objet `hass` a chaque changement d'etat.
   *  On s'en sert comme signal de rafraichissement : si le capteur d'actions a
   *  bouge, le jardin a change, y compris depuis un autre appareil. */
  set hass(hass) {
    const premier = !this._hass;
    this._hass = hass;
    if (premier) {
      this._rendreCoquille();
      this._charger();
      return;
    }
    const signature = this._signatureEtat();
    if (signature !== this._signature) {
      this._signature = signature;
      this._charger({ discret: true });
    }
  }

  _signatureEtat() {
    // Le prefixe suit le nom de l'appareil, donc celui de l'integration. Il a
    // longtemps valu « sensor.potager » alors que les entites s'appelaient
    // « sensor.mon_potager_… » : le filtre ne matchait rien et le panneau ne
    // voyait aucun changement d'etat venu d'ailleurs. Garder les deux bouts
    // d'accord, ou renoncer au prefixe.
    const etats = this._hass?.states || {};
    return Object.keys(etats)
      .filter((id) => id.startsWith("sensor.rhizome") || id.startsWith("switch.rhizome"))
      .map((id) => `${id}:${etats[id].state}:${etats[id].last_updated}`)
      .join(",");
  }

  connectedCallback() {
    if (this._hass && !this._rendu) {
      this._rendreCoquille();
      this._charger();
    }
  }

  // --- Donnees -------------------------------------------------------------

  async _charger({ discret = false } = {}) {
    if (!discret) this._chargement = true;
    try {
      const [jardin, catalogue, reglages, perso, calendrier] = await Promise.all([
        this._hass.callWS({ type: "rhizome/jardin" }),
        this._hass.callWS({ type: "rhizome/catalogue" }),
        this._hass.callWS({ type: "rhizome/reglages" }),
        this._hass.callWS({ type: "rhizome/cultures_perso" }),
        this._hass.callWS({ type: "rhizome/calendrier", annee: this._anneeCal }),
      ]);
      // La langue vient du serveur, qui a resolu « auto » et s'en sert deja
      // pour les noms de cultures que ces reponses transportent. La poser
      // avant d'affecter les donnees evite un premier rendu dans l'autre
      // langue, et refaire la coquille remet la barre de navigation d'aplomb.
      const changee = definirLangue(reglages?.langue || jardin?.langue);
      this._jardin = jardin;
      this._catalogue = catalogue;
      this._reglages = reglages;
      this._cataloguePerso = perso.cultures;
      this._calendrier = calendrier;
      this._erreur = null;
      this._signature = this._signatureEtat();
      if (changee) this._rendreCoquille();
    } catch (err) {
      this._erreur = err?.message || T("injoignable");
    } finally {
      this._chargement = false;
      this._rendreVue();
    }
  }

  async _appeler(message) {
    try {
      const reponse = await this._hass.callWS(message);
      await this._charger({ discret: true });
      return reponse;
    } catch (err) {
      this._erreur = err?.message || T("actionRefusee");
      this._rendreVue();
      return null;
    }
  }

  /** Note un arrosage, et retient quelques secondes que ce clic a ete pris.
   *
   *  Sans ca, le seul retour visible est un compte a rebours qui repart : rien
   *  ne dit que *ce* geste a ete enregistre, ni ou il est parti. La pastille le
   *  dit, et nomme le journal. */
  async _arroser(uids) {
    const reponse = await this._appeler({ type: "rhizome/arroser", uid: uids });
    if (!reponse) return;
    this._eauConfirmee = new Set(uids);
    clearTimeout(this._minuteurEau);
    this._minuteurEau = setTimeout(() => {
      this._eauConfirmee = null;
      this._rendreVue();
    }, 4000);
    this._rendreVue();
  }

  _noter(uid, evenement, extra = {}) {
    return this._appeler({ type: "rhizome/noter", uid, evenement, ...extra });
  }

  // --- Coquille ------------------------------------------------------------

  _rendreCoquille() {
    this._rendu = true;
    this.shadowRoot.innerHTML = `
      <style>${STYLES}</style>
      <div class="enveloppe">
        <header>
          <div class="barre-titre">
            <ha-icon icon="mdi:sprout"></ha-icon>
            <h1>Rhizome</h1>
            <span class="compteur-entete" id="compteur" hidden></span>
          </div>
          <nav id="nav"></nav>
        </header>
        <main><div class="contenu" id="vue"></div></main>
      </div>
      <div id="fiche"></div>
    `;

    const nav = this.shadowRoot.getElementById("nav");
    nav.innerHTML = VUES.map(
      (v) => `<button data-vue="${v.id}" aria-selected="${v.id === this._vue}">
          <ha-icon icon="${v.icone}"></ha-icon><span class="etiquette">${T(v.cle)}</span>
        </button>`
    ).join("");
    nav.addEventListener("click", (ev) => {
      const bouton = ev.target.closest("button[data-vue]");
      if (!bouton) return;
      this._vue = bouton.dataset.vue;
      nav.querySelectorAll("button").forEach((b) =>
        b.setAttribute("aria-selected", String(b.dataset.vue === this._vue))
      );
      this._rendreVue();
      this.shadowRoot.querySelector("main").scrollTop = 0;
    });
  }

  _rendreVue() {
    const hote = this.shadowRoot?.getElementById("vue");
    if (!hote) return;

    const compteur = this.shadowRoot.getElementById("compteur");
    const nbActions = this._jardin?.actions?.length || 0;
    if (nbActions > 0) {
      compteur.textContent = T("enteteAFaire", { nombre: nbActions });
      compteur.hidden = false;
    } else {
      compteur.hidden = true;
    }

    if (this._chargement && !this._jardin) {
      hote.innerHTML = `<div class="chargement">${T("chargement")}</div>`;
      return;
    }

    const banniere = this._erreur
      ? `<div class="erreur">${echappe(this._erreur)}</div>`
      : "";

    const vues = {
      aujourdhui: () => this._vueAujourdhui(),
      potager: () => this._vuePotager(),
      catalogue: () => this._vueCatalogue(),
      calendrier: () => this._vueCalendrier(),
      journal: () => this._vueJournal(),
      reglages: () => this._vueReglages(),
    };
    hote.innerHTML = banniere + (vues[this._vue] || vues.aujourdhui)();
    this._brancherVue(hote);
    this._rendreFiche();
  }

  // --- Vue : Aujourd'hui ---------------------------------------------------

  _vueAujourdhui() {
    const actions = this._jardin?.actions || [];
    const plantes = this._jardin?.plantes || [];

    if (!plantes.length) {
      return `<div class="vide">
          <div class="gros">🌱</div>
          <p>${T("videPotagerTitre")}<br>
             ${T("videPotagerSuite", { total: this._catalogue?.total || 172 })}</p>
          <button class="bouton" data-aller="catalogue">
            <ha-icon icon="mdi:book-open-variant"></ha-icon> ${T("ouvrirCatalogue")}
          </button>
        </div>`;
    }

    if (!actions.length && !(this._jardin?.arrosages || []).length) {
      return `<div class="vide">
          <div class="gros">☕</div>
          <p>${T("videRienAFaire")}<br>
             ${T("videRienAFaireSuite", {
               nombre: plantes.length,
               s: pluriel(plantes.length),
             })}</p>
          <button class="bouton discret" data-aller="potager">
            <ha-icon icon="mdi:sprout"></ha-icon> ${T("voirPotager")}
          </button>
        </div>`;
    }

    const maintenant = actions.filter((a) => a.en_cours);
    const bientot = actions.filter((a) => !a.en_cours);
    const arrosage = this._blocArrosage();

    return `
      ${arrosage}
      ${
        maintenant.length
          ? `<h2>${T("sectionMaintenant")}</h2>
             <div class="grille grille-large">${maintenant
               .map((a) => this._carteAction(a, true))
               .join("")}</div>`
          : ""
      }
      ${
        bientot.length
          ? `<h2>${T("sectionAPreparer")}</h2>
             <div class="grille grille-large">${bientot
               .map((a) => this._carteAction(a, false))
               .join("")}</div>`
          : ""
      }`;
  }

  /** Ce qui attend de l'eau, avec de quoi le noter d'un clic.
   *
   *  Le compte a rebours est theorique : il part de la frequence de la fiche
   *  et repart quand vous declarez avoir arrose. Rien n'observe le sol. */
  _blocArrosage() {
    const besoins = this._jardin?.arrosages || [];
    if (!this._jardin?.arrosage_actif || !besoins.length) return "";

    return `<h2>${T("sectionAArroser", { nombre: besoins.length })}</h2>
      <div class="grille grille-large">${besoins
        .map((b) => {
          const confirme = this._eauConfirmee?.has(b.uid);
          return `<div class="carte action ${
            b.etat.jours_restants < -1 && !confirme ? "urgent" : ""
          }">
            <div class="emoji">${echappe(b.emoji)}</div>
            <div class="corps">
              <div class="titre">${echappe(b.nom)}</div>
              <div class="detail" style="margin-top:4px">
                ${pastilleEau(b.etat, confirme)}
              </div>
              <div class="detail">
                ${echappe(b.zone)} ·
                ${T("eauTousLesNJours", { jours: b.etat.frequence_jours })} ·
                ${
                  b.etat.dernier
                    ? T("eauDernierLe", { date: fmtCourt(b.etat.dernier) })
                    : T("eauJamais")
                }
              </div>
            </div>
            <button class="bouton ${eauAJour(b.etat, confirme) ? "discret" : ""}"
                    data-arroser="${b.uid}">
              <ha-icon icon="mdi:watering-can"></ha-icon> ${T("boutonArroser")}
            </button>
          </div>`;
        })
        .join("")}
      </div>
      ${
        besoins.length > 1
          ? `<div class="actions-fiche" style="margin-top:12px">
               <button class="bouton discret" data-arroser-tout="${besoins
                 .map((b) => b.uid)
                 .join(",")}">
                 <ha-icon icon="mdi:watering-can"></ha-icon>
                 ${T("boutonToutArroser", { nombre: besoins.length })}
               </button>
             </div>`
          : ""
      }`;
  }

  _carteAction(action, urgent) {
    const etape = action.etape;
    const correspondance = EVT_POUR_ETAPE[etape.type];
    const largeur = action.en_cours ? this._avancementFenetre(etape) : 0;
    return `
      <div class="carte action ${urgent ? "urgent" : ""}">
        <div class="emoji">${echappe(action.emoji)}</div>
        <div class="corps">
          <div class="titre">${echappe(action.nom)}</div>
          <div class="detail">
            <span class="verbe">${echappe(etape.libelle)}</span> ·
            ${quand(action.jours_restants, action.en_cours)} ·
            ${echappe(action.zone)}
          </div>
          <div class="detail">${T("fenetreJusquAu", {
            date: fmtCourt(etape.fin),
          })}${etape.reelle ? ` · ${T("dApresVotreJournal")}` : ""}</div>
          ${
            largeur
              ? `<div class="progression"><div style="width:${largeur}%;background:${
                  COULEURS_ETAPE[etape.type]
                }"></div></div>`
              : ""
          }
        </div>
        ${
          correspondance
            ? `<button class="bouton" data-fait="${action.uid}"
                 data-etape="${etape.type}" title="${T("enregistrerAuJournal")}">
                 <ha-icon icon="mdi:check"></ha-icon> ${
                   etape.type === "ressemer" ? T("boutonSeme") : T("boutonFait")
                 }
               </button>`
            : ""
        }
      </div>`;
  }

  _avancementFenetre(etape) {
    const debut = jour(etape.debut).getTime();
    const fin = jour(etape.fin).getTime();
    if (fin <= debut) return 100;
    const part = ((Date.now() - debut) / (fin - debut)) * 100;
    return Math.min(100, Math.max(4, Math.round(part)));
  }

  // --- Vue : Mon potager ---------------------------------------------------

  _vuePotager() {
    const toutes = this._jardin?.plantes || [];
    const plantes = this._reglages?.options?.masquer_terminees
      ? toutes.filter((p) => !["termine", "perdu"].includes(p.phase))
      : toutes;
    if (!plantes.length) {
      return `<div class="vide">
          <div class="gros">🪴</div>
          <p>${T("videAucunePlante")}</p>
          <button class="bouton" data-aller="catalogue">
            <ha-icon icon="mdi:plus"></ha-icon> ${T("ajouterDesLegumes")}
          </button>
        </div>`;
    }

    const parZone = new Map();
    for (const plante of plantes) {
      const cle = plante.zone.nom;
      if (!parZone.has(cle)) parZone.set(cle, []);
      parZone.get(cle).push(plante);
    }

    return [...parZone.entries()]
      .map(
        ([zone, liste]) => `
          <h2>${echappe(zone)} · ${liste.length}</h2>
          <div class="grille">${liste.map((p) => this._cartePlante(p)).join("")}</div>`
      )
      .join("");
  }

  _cartePlante(plante) {
    const prochaine = plante.prochaine;
    const largeur = prochaine ? this._avancementFenetre(prochaine) : 0;
    return `
      <div class="carte plante" data-fiche="${plante.uid}">
        <div class="plante-tete">
          <div class="emoji">${echappe(plante.emoji)}</div>
          <div style="flex:1;min-width:0">
            <div class="plante-nom">${echappe(plante.nom)}</div>
            <div class="plante-zone">${echappe(plante.zone.nom)}${
      plante.total_recolte_g
        ? ` · ${T("recoltesSuffixe", { poids: kg(plante.total_recolte_g) })}`
        : ""
    }</div>
          </div>
          <span class="badge ${plante.phase}">${echappe(plante.phase_libelle)}</span>
        </div>
        <div class="detail" style="margin-top:10px;font-size:13px;color:var(--secondary-text-color)">
          ${
            prochaine
              ? `${echappe(prochaine.libelle)} · ${quand(
                  joursJusqu(prochaine.debut),
                  estDansFenetre(prochaine)
                )}`
              : T("rienDePrevu")
          }
        </div>
        ${
          prochaine
            ? `<div class="progression"><div style="width:${largeur || 3}%;background:${
                COULEURS_ETAPE[prochaine.type]
              }"></div></div>`
            : ""
        }
        ${this._pieDArrosage(plante)}
      </div>`;
  }

  /** Ligne d'arrosage d'une carte de plante : l'état, et le bouton qui le
   *  note sans avoir à ouvrir la fiche. C'est le geste le plus fréquent du
   *  potager, il doit coûter un clic. */
  _pieDArrosage(plante) {
    const eau = plante.arrosage;
    if (!this._jardin?.arrosage_actif || !eau || !eau.concernee) return "";
    const confirme = this._eauConfirmee?.has(plante.uid);

    return `<div class="pied-eau">
        ${pastilleEau(eau, confirme)}
        <button class="bouton mini ${eauAJour(eau, confirme) ? "discret" : ""}"
                data-arroser="${plante.uid}"
                aria-label="${T("noterUnArrosage")}"
                title="${T("noterUnArrosage")}">
          ${T("boutonArroser")}
        </button>
      </div>`;
  }

  // --- Vue : Catalogue -----------------------------------------------------

  _vueCatalogue() {
    const cultures = this._cataloguFiltre();
    const categories = this._catalogue?.categories || [];

    return `
      <div class="carte recherche">
        <ha-icon icon="mdi:magnify"></ha-icon>
        <input id="champ-recherche" type="search"
               placeholder="${T("chercherPlaceholder")}"
               value="${echappe(this._recherche)}" autocomplete="off">
        ${
          this._recherche
            ? `<button class="icone" data-vider="1"><ha-icon icon="mdi:close"></ha-icon></button>`
            : ""
        }
      </div>

      <div class="puces">
        <button class="puce" data-filtre-semable="1"
                aria-pressed="${this._filtreDifficulte === "semable"}">
          ${T("filtreSemable")}
        </button>
        <button class="puce" data-filtre-facile="1"
                aria-pressed="${this._filtreDifficulte === "facile"}">
          ${T("filtreFacile")}
        </button>
        <button class="puce" data-filtre-vie="vivace"
                aria-pressed="${this._filtreVie === "vivace"}">
          ${T("filtreVivace")}
        </button>
        <button class="puce" data-filtre-vie="continue"
                aria-pressed="${this._filtreVie === "continue"}">
          ${T("filtreContinue")}
        </button>
        <button class="puce" data-filtre-vie="annuelle"
                aria-pressed="${this._filtreVie === "annuelle"}">
          ${T("filtreAnnuelle")}
        </button>
        ${categories
          .map(
            (c) => `<button class="puce" data-filtre-cat="${c}"
                 aria-pressed="${this._filtreCategorie === c}">${
              libelleCategorie(c) || c
            }</button>`
          )
          .join("")}
      </div>

      <div class="detail" style="margin:4px 0 12px;font-size:13px;color:var(--secondary-text-color)">
        ${T("compteCultures", {
          nombre: cultures.length,
          s: pluriel(cultures.length),
          total: this._catalogue?.total || 0,
        })}
      </div>

      ${
        cultures.length
          ? `<div class="grille">${cultures.map((c) => this._carteCulture(c)).join("")}</div>`
          : `<div class="vide"><div class="gros">🔍</div><p>${T(
              "aucuneCorrespondance"
            )}</p></div>`
      }`;
  }

  _cataloguFiltre() {
    let cultures = this._catalogue?.cultures || [];
    if (this._filtreCategorie) {
      cultures = cultures.filter((c) => c.categorie === this._filtreCategorie);
    }
    if (this._filtreDifficulte === "facile") {
      cultures = cultures.filter((c) => c.difficulte === 1);
    }
    if (this._filtreDifficulte === "semable") {
      cultures = cultures.filter((c) => c.semable_maintenant);
    }
    if (this._filtreVie === "vivace") {
      cultures = cultures.filter((c) => c.perenne);
    }
    if (this._filtreVie === "annuelle") {
      cultures = cultures.filter((c) => !c.perenne);
    }
    if (this._filtreVie === "continue") {
      cultures = cultures.filter(
        (c) => c.perenne && (c.duree_recolte_jours || 0) >= RECOLTE_CONTINUE_JOURS
      );
    }
    if (this._recherche) {
      const terme = this._recherche
        .toLowerCase()
        .normalize("NFD")
        .replace(/[̀-ͯ]/g, "");
      cultures = cultures.filter((c) =>
        `${c.nom} ${c.famille}`
          .toLowerCase()
          .normalize("NFD")
          .replace(/[̀-ͯ]/g, "")
          .includes(terme)
      );
    }
    return cultures;
  }

  _carteCulture(culture) {
    const dejaAu = (this._jardin?.plantes || []).filter(
      (p) => p.culture_id === culture.id
    ).length;

    return `
      <div class="carte plante" data-culture="${culture.id}">
        <div class="plante-tete">
          <div class="emoji">${echappe(culture.emoji)}</div>
          <div style="flex:1;min-width:0">
            <div class="plante-nom">${echappe(culture.nom)}</div>
            <div class="plante-zone">${libelleCategorie(
              culture.categorie
            )} · ${"★".repeat(culture.difficulte)}${
      culture.perenne
        ? (culture.duree_recolte_jours || 0) >= RECOLTE_CONTINUE_JOURS
          ? T("marqueurPerpetuelle")
          : T("marqueurVivace")
        : ""
    }</div>
          </div>
          ${
            dejaAu
              ? `<span class="badge plante">${T("badgeAuPotager", {
                  nombre: dejaAu,
                })}</span>`
              : culture.semable_maintenant
              ? `<span class="badge seme">${T("badgeSemableMaintenant")}</span>`
              : ""
          }
          ${culture.perso ? `<span class="badge prevu">✎</span>` : ""}
        </div>
        <div class="detail" style="margin-top:10px;font-size:13px;color:var(--secondary-text-color)">
          <ha-icon icon="${
            ICONES_EXPOSITION[culture.exposition] || "mdi:weather-sunny"
          }" style="--mdc-icon-size:16px"></ha-icon>
          ${libelleExposition(culture.exposition)} · ${libelleEau(
      culture.arrosage.besoin
    )}
        </div>
        <div class="detail" style="margin-top:4px;font-size:13px;color:var(--secondary-text-color)">
          ${
            culture.prochain_depart
              ? `${echappe(culture.prochain_depart.libelle)} : ${fmtCourt(
                  culture.prochain_depart.debut
                )} → ${fmtCourt(culture.prochain_depart.fin)}`
              : culture.categorie === "plante-interieur"
              ? T("cultureInterieur")
              : culture.perenne
              ? T("plantationPerenne")
              : ""
          }
        </div>
      </div>`;
  }

  // --- Vue : Calendrier ----------------------------------------------------

  _vueCalendrier() {
    const lignes = this._calendrier?.lignes || [];
    if (!lignes.length) {
      return `<div class="vide"><div class="gros">📅</div>
        <p>${T("videCalendrier")}</p></div>`;
    }

    const annee = this._calendrier.annee;
    const debutAnnee = new Date(annee, 0, 1).getTime();
    const finAnnee = new Date(annee + 1, 0, 1).getTime();
    const duree = finAnnee - debutAnnee;
    const position = (iso) =>
      Math.max(0, Math.min(100, ((jour(iso).getTime() - debutAnnee) / duree) * 100));

    const maintenant = Date.now();
    const repere =
      maintenant >= debutAnnee && maintenant < finAnnee
        ? `<div class="cal-aujourdhui" style="left:${
            ((maintenant - debutAnnee) / duree) * 100
          }%"></div>`
        : "";

    const bande = (e, reelle) => {
      const gauche = position(e.debut);
      const largeur = Math.max(1.2, position(e.fin) - gauche);
      return `<div class="cal-bande ${reelle ? "" : "prevue"}"
        style="left:${gauche}%;width:${largeur}%;background:${
        COULEURS_ETAPE[e.type] || "var(--primary-color)"
      }"
        title="${echappe(e.libelle)} : ${fmtCourt(e.debut)} → ${fmtCourt(e.fin)} ${
        reelle ? T("calReel") : T("calPrevu")
      }"></div>`;
    };

    const corps = lignes
      .map((ligne) => {
        // Le réel recouvre le prévu : une étape notée au journal remplace la
        // moyenne saisonnière, elle ne s'y ajoute pas.
        const typesReels = new Set((ligne.reelles || []).map((e) => e.type));
        const prevues = (ligne.prevues || [])
          .filter((e) => !typesReels.has(e.type))
          .map((e) => bande(e, false))
          .join("");
        const reelles = (ligne.reelles || [])
          .filter(
            (e) =>
              jour(e.fin).getTime() >= debutAnnee &&
              jour(e.debut).getTime() < finAnnee
          )
          .map((e) => bande(e, true))
          .join("");
        const faits = (ligne.evenements || [])
          .map(
            (evt) => `<div class="cal-bande"
              style="left:${position(evt.date)}%;width:1.2%;
                     background:var(--primary-text-color)"
              title="${echappe(
                T("calNoteLe", {
                  evenement: libelleEvenement(evt.type),
                  date: fmtCourt(evt.date),
                })
              )}"></div>`
          )
          .join("");

        return `<div class="cal-ligne">
            <div class="cal-nom" title="${echappe(ligne.nom)}">${echappe(ligne.emoji)} ${echappe(
          ligne.nom
        )}</div>
            <div class="cal-piste">${prevues}${reelles}${faits}${repere}</div>
          </div>`;
      })
      .join("");

    return `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <button class="icone" data-annee="${annee - 1}"><ha-icon icon="mdi:chevron-left"></ha-icon></button>
        <strong style="font-size:17px">${annee}</strong>
        <button class="icone" data-annee="${annee + 1}"><ha-icon icon="mdi:chevron-right"></ha-icon></button>
      </div>

      <div class="carte cal-defilement">
        <div class="cal">
          <div class="cal-entete">
            <div></div>
            <div class="cal-mois">${mois()
              .map((m) => `<span>${m}</span>`)
              .join("")}</div>
          </div>
          ${corps}
        </div>
      </div>

      <div class="legende">
        <span><i class="pastille" style="background:var(--rhizome-semis)"></i> ${T(
          "legendeSemis"
        )}</span>
        <span><i class="pastille" style="background:var(--rhizome-plantation)"></i> ${T(
          "legendePlantation"
        )}</span>
        <span><i class="pastille" style="background:var(--rhizome-recolte)"></i> ${T(
          "legendeRecolte"
        )}</span>
        <span><i class="pastille" style="background:var(--primary-text-color)"></i> ${T(
          "legendeJournal"
        )}</span>
        <span>${T("legendeTrame")}</span>
      </div>`;
  }

  // --- Vue : Journal -------------------------------------------------------

  _vueJournal() {
    const plantes = this._jardin?.plantes || [];
    const entrees = [];
    for (const plante of plantes) {
      for (const evt of plante.evenements || []) {
        entrees.push({ ...evt, plante });
      }
    }

    // L'arrosage ne fait pas avancer le cycle (invariant 6), mais c'est un
    // fait date : il a sa place au journal. Groupe par jour et non par plante,
    // sinon un ete d'arrosages enterrerait les semis et les recoltes sous des
    // centaines de lignes identiques.
    const parJour = new Map();
    for (const plante of plantes) {
      for (const arrosage of plante.arrosages || []) {
        if (!parJour.has(arrosage.date)) parJour.set(arrosage.date, []);
        parJour.get(arrosage.date).push(plante);
      }
    }
    let nbArrosages = 0;
    for (const [date, concernees] of parJour) {
      nbArrosages += concernees.length;
      entrees.push({ type: "arrosage", eau: true, date, concernees });
    }

    entrees.sort((a, b) => (a.date < b.date ? 1 : -1));

    if (!entrees.length) {
      return `<div class="vide"><div class="gros">📖</div>
        <p>${T("videJournalTitre")}<br>
           ${T("videJournalSuite")}</p></div>`;
    }

    const total = this._jardin.total_recolte_g || 0;
    const pertes = entrees.filter((e) => e.type === "perdu");
    const recoltes = entrees.filter((e) => e.type === "recolte");
    const filtrees = this._filtreJournal
      ? entrees.filter((e) => e.type === this._filtreJournal)
      : entrees;

    const typesPresents = [...new Set(entrees.map((e) => e.type))];

    return `
      <div class="bilan">
        <div class="carte tuile">
          <div class="chiffre">${kg(total)}</div>
          <div class="etiquette">${T("bilanRecoltes")}</div>
        </div>
        <div class="carte tuile">
          <div class="chiffre">${recoltes.length}</div>
          <div class="etiquette">${T("bilanNbRecoltes", {
            s: pluriel(recoltes.length),
          })}</div>
        </div>
        <div class="carte tuile">
          <div class="chiffre">${plantes.length}</div>
          <div class="etiquette">${T("bilanPlantes")}</div>
        </div>
        ${
          nbArrosages
            ? `<div class="carte tuile">
                 <div class="chiffre">${nbArrosages}</div>
                 <div class="etiquette">${T("bilanArrosages", {
                   s: pluriel(nbArrosages),
                 })}</div>
               </div>`
            : ""
        }
        ${
          pertes.length
            ? `<div class="carte tuile">
                 <div class="chiffre">${pertes.length}</div>
                 <div class="etiquette">${T("bilanPertes", {
                   s: pluriel(pertes.length),
                 })}</div>
               </div>`
            : ""
        }
      </div>

      <div class="puces">
        <button class="puce" data-filtre-journal=""
                aria-pressed="${!this._filtreJournal}">${T("filtreTout")}</button>
        ${typesPresents
          .map(
            (t) => `<button class="puce" data-filtre-journal="${t}"
              aria-pressed="${this._filtreJournal === t}">${
              libelleEvenement(t) || t
            }</button>`
          )
          .join("")}
      </div>

      <div class="carte" style="padding:4px 0">
        ${filtrees
          .map((e) => (e.eau ? this._ligneJournalEau(e) : this._ligneJournal(e)))
          .join("")}
      </div>`;
  }

  _ligneJournal(e) {
    return `<div class="journal-ligne">
        <div class="journal-date">${fmtCourt(e.date)}</div>
        <div style="font-size:20px">${echappe(e.plante.emoji)}</div>
        <div class="journal-corps">
          <div><strong>${echappe(e.libelle)}</strong> · ${echappe(
      e.plante.nom
    )} <span class="badge">${echappe(e.plante.zone.nom)}</span></div>
          ${
            e.quantite_g
              ? `<div class="journal-note">${kg(e.quantite_g)}</div>`
              : ""
          }
          ${
            e.cause
              ? `<div class="journal-note">${T("etiquetteCause", {
                  cause: echappe(e.cause),
                })}</div>`
              : ""
          }
          ${e.note ? `<div class="journal-note">${echappe(e.note)}</div>` : ""}
        </div>
      </div>`;
  }

  /** Une journee d'arrosage. L'arrosoir remplace l'emoji de la plante : d'un
   *  coup d'oeil, la ligne se distingue d'une etape du cycle. */
  _ligneJournalEau(e) {
    const seule = e.concernees.length === 1 ? e.concernees[0] : null;
    return `<div class="journal-ligne">
        <div class="journal-date">${fmtCourt(e.date)}</div>
        <ha-icon class="goutte" icon="mdi:watering-can"></ha-icon>
        <div class="journal-corps">
          <div><strong>${T("evt_arrosage")}</strong> · ${
      seule
        ? `${echappe(seule.nom)} <span class="badge">${echappe(
            seule.zone.nom
          )}</span>`
        : T("journalNPlantes", { nombre: e.concernees.length })
    }</div>
          ${
            seule
              ? ""
              : `<div class="journal-note">${e.concernees
                  .map((plante) => echappe(plante.nom))
                  .join(" · ")}</div>`
          }
        </div>
      </div>`;
  }

  // --- Branchement des interactions ---------------------------------------

  _brancherVue(hote) {
    hote.querySelectorAll("[data-aller]").forEach((el) =>
      el.addEventListener("click", () => {
        this._vue = el.dataset.aller;
        this.shadowRoot
          .getElementById("nav")
          .querySelectorAll("button")
          .forEach((b) => b.setAttribute("aria-selected", String(b.dataset.vue === this._vue)));
        this._rendreVue();
      })
    );

    hote.querySelectorAll("[data-fait]").forEach((el) =>
      el.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        el.disabled = true;
        const corr = EVT_POUR_ETAPE[el.dataset.etape];
        if (!corr) return;
        if (corr.commande) {
          await this._appeler({ type: corr.commande, uid: el.dataset.fait });
          return;
        }
        if (corr.evenement === "recolte") {
          this._demanderRecolte(el.dataset.fait);
          el.disabled = false;
          return;
        }
        await this._noter(el.dataset.fait, corr.evenement,
          corr.mode ? { mode: corr.mode } : {});
      })
    );

    hote.querySelectorAll("[data-arroser]").forEach((el) =>
      el.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        el.disabled = true;
        await this._arroser([el.dataset.arroser]);
      })
    );

    hote.querySelectorAll("[data-arroser-tout]").forEach((el) =>
      el.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        el.disabled = true;
        await this._arroser(el.dataset.arroserTout.split(","));
      })
    );

    hote.querySelectorAll("[data-fiche]").forEach((el) =>
      el.addEventListener("click", () => {
        this._ouvrirFichePlante(el.dataset.fiche);
      })
    );

    hote.querySelectorAll("[data-culture]").forEach((el) =>
      el.addEventListener("click", () => {
        this._fiche = { type: "culture", id: el.dataset.culture };
        this._ouvrirFicheCulture(el.dataset.culture);
      })
    );

    const champ = hote.querySelector("#champ-recherche");
    if (champ) {
      champ.addEventListener("input", () => {
        this._recherche = champ.value;
        clearTimeout(this._tempo);
        this._tempo = setTimeout(() => {
          const position = champ.selectionStart;
          this._rendreVue();
          const nouveau = this.shadowRoot.querySelector("#champ-recherche");
          if (nouveau) {
            nouveau.focus();
            nouveau.setSelectionRange(position, position);
          }
        }, 180);
      });
    }

    const vider = hote.querySelector("[data-vider]");
    if (vider) {
      vider.addEventListener("click", () => {
        this._recherche = "";
        this._rendreVue();
      });
    }

    hote.querySelectorAll("[data-filtre-cat]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreCategorie =
          this._filtreCategorie === el.dataset.filtreCat ? null : el.dataset.filtreCat;
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-filtre-facile]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreDifficulte = this._filtreDifficulte === "facile" ? null : "facile";
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-filtre-vie]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreVie =
          this._filtreVie === el.dataset.filtreVie ? null : el.dataset.filtreVie;
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-filtre-semable]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreDifficulte = this._filtreDifficulte === "semable" ? null : "semable";
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-filtre-journal]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreJournal = el.dataset.filtreJournal || null;
        this._rendreVue();
      })
    );
    if (this._vue === "reglages") this._brancherReglages(hote);

    hote.querySelectorAll("[data-annee]").forEach((el) =>
      el.addEventListener("click", async () => {
        this._anneeCal = Number(el.dataset.annee);
        this._calendrier = await this._hass.callWS({
          type: "rhizome/calendrier",
          annee: this._anneeCal,
        });
        this._rendreVue();
      })
    );
  }

  // --- Fiche detaillee -----------------------------------------------------

  async _ouvrirFicheCulture(cultureId) {
    this._ficheDetail = null;
    this._rendreFiche();
    try {
      this._ficheDetail = await this._hass.callWS({
        type: "rhizome/culture",
        culture_id: cultureId,
      });
    } catch (err) {
      this._erreur = err?.message || T("ficheIndisponible");
    }
    this._rendreFiche();
  }

  async _ouvrirFichePlante(uid) {
    const plante = (this._jardin?.plantes || []).find((p) => p.uid === uid);
    this._fiche = { type: "plante", uid };
    this._ficheDetail = null;
    this._rendreFiche();
    if (plante) {
      try {
        this._ficheDetail = await this._hass.callWS({
          type: "rhizome/culture",
          culture_id: plante.culture_id,
        });
      } catch (err) {
        /* la fiche reste utilisable sans ses compagnes */
      }
      this._rendreFiche();
    }
  }

  _fermerFiche() {
    this._fiche = null;
    this._ficheDetail = null;
    this._rendreFiche();
  }

  _rendreFiche() {
    const hote = this.shadowRoot?.getElementById("fiche");
    if (!hote) return;

    if (!this._fiche) {
      hote.innerHTML = "";
      return;
    }

    const contenu =
      this._fiche.type === "plante"
        ? this._fichePlante()
        : this._fiche.type === "perso"
        ? this._fichePerso()
        : this._ficheCulture();
    if (contenu === null) {
      hote.innerHTML = "";
      this._fiche = null;
      return;
    }

    hote.innerHTML = `<div class="voile" id="voile"><div class="fiche">${contenu}</div></div>`;
    this._brancherFiche(hote);
  }

  _fichePlante() {
    const plante = (this._jardin?.plantes || []).find(
      (p) => p.uid === this._fiche.uid
    );
    if (!plante) return null;

    const culture = this._ficheDetail?.culture;
    const prochaine = plante.prochaine;
    const corr = prochaine ? EVT_POUR_ETAPE[prochaine.type] : null;
    const zones = this._jardin?.zones || [];

    return `
      <div class="fiche-tete">
        <div class="emoji">${echappe(plante.emoji)}</div>
        <h3>${echappe(plante.nom)}</h3>
        <span class="badge ${plante.phase}">${echappe(plante.phase_libelle)}</span>
        <button class="icone" data-fermer="1"><ha-icon icon="mdi:close"></ha-icon></button>
      </div>

      <div class="fiche-corps">
        ${
          prochaine
            ? `<div class="carte bloc">
                 <h4>${T("blocProchaineEtape")}</h4>
                 <div style="font-size:17px;font-weight:500">${echappe(
                   prochaine.libelle
                 )}</div>
                 <div style="font-size:13px;color:var(--secondary-text-color);margin:4px 0 12px">
                   ${T("duAuLong", {
                     debut: fmtLong(prochaine.debut),
                     fin: fmtLong(prochaine.fin),
                   })}
                   ${
                     prochaine.reelle
                       ? `<br>${T("calculeeDepuisJournal")}`
                       : ""
                   }
                 </div>
                 ${
                   corr
                     ? `<button class="bouton" data-fait-fiche="${plante.uid}"
                          data-etape="${prochaine.type}">
                          <ha-icon icon="mdi:check"></ha-icon>
                          ${
                            corr.evenement === "recolte"
                              ? T("noterUneRecolte")
                              : T("cestFaitEtape", {
                                  etape: prochaine.libelle.toLowerCase(),
                                })
                          }
                        </button>`
                     : ""
                 }
               </div>`
            : `<div class="carte bloc"><h4>${T("blocProchaineEtape")}</h4>
                 <div style="color:var(--secondary-text-color)">${T(
                   "plusRienDePrevu"
                 )}</div></div>`
        }

        ${
          ["seme", "plante", "en_recolte"].includes(plante.phase)
            ? `<div class="carte bloc">
                 <h4>${T("noterUneRecolte")}</h4>
                 <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                   <input id="qte-recolte" type="number" min="0" step="10"
                          placeholder="${T("grammesPlaceholder")}"
                          style="border:1px solid var(--divider-color);border-radius:8px;padding:8px 10px;
                                 background:var(--card-background-color);color:var(--primary-text-color);
                                 font-family:inherit;width:120px">
                   <button class="bouton" data-recolter="${plante.uid}">
                     <ha-icon icon="mdi:basket"></ha-icon> ${T("boutonEnregistrer")}
                   </button>
                 </div>
                 <div style="font-size:12px;color:var(--secondary-text-color);margin-top:8px">
                   ${T("quantiteFacultative")} ${
                     plante.nb_recoltes
                       ? T("dejaNotees", {
                           nombre: plante.nb_recoltes,
                           s: pluriel(plante.nb_recoltes),
                           poids: kg(plante.total_recolte_g),
                         })
                       : ""
                   }
                 </div>
               </div>`
            : ""
        }

        ${this._blocEauFiche(plante)}
        ${this._blocFrise(plante)}

        <div class="carte bloc">
          <h4>${T("blocReglages")}</h4>
          <div class="reglage">
            <label for="sel-zone">${T("champZone")}</label>
            <select id="sel-zone" data-uid="${plante.uid}">
              ${zones
                .map(
                  (z) => `<option value="${echappe(z.id)}" ${
                    z.id === plante.zone.id ? "selected" : ""
                  }>${echappe(z.nom)}${
                    z.decalage_jours
                      ? ` (${z.decalage_jours > 0 ? "+" : ""}${
                          z.decalage_jours
                        } ${T("uniteJourCourt")})`
                      : ""
                  }</option>`
                )
                .join("")}
            </select>
          </div>
          <div class="reglage">
            <label for="champ-surnom">${T("champSurnom")}</label>
            <input id="champ-surnom" type="text" data-uid="${plante.uid}"
                   value="${echappe(plante.surnom || "")}"
                   placeholder="${T("surnomPlaceholder")}">
          </div>
          <div class="reglage">
            <label for="bascule-notifs">${T("champRappelsPlante")}</label>
            <input id="bascule-notifs" type="checkbox" data-uid="${plante.uid}"
                   ${plante.notifs ? "checked" : ""} style="width:20px;height:20px">
          </div>
          <div class="reglage">
            <label for="champ-rappel">${T("champPrevenirAvance")}</label>
            <input id="champ-rappel" type="number" min="0" max="30" data-uid="${plante.uid}"
                   value="${
                     plante.rappel_jours ?? this._jardin?.rappel_jours ?? 3
                   }" style="width:90px">
          </div>
          <div class="reglage">
            <label for="champ-echelon">${T("champRessemerTous")}</label>
            <span><input id="champ-echelon" type="number" min="0" max="90"
                         data-uid="${plante.uid}"
                         value="${plante.echelonnement_jours || 0}"
                         style="width:90px"> ${T("uniteJours")}</span>
          </div>
          <p class="aide">${T("aideEchelonnement")}</p>
        </div>

        ${culture ? this._blocCulture(culture) : ""}
        ${this._ficheDetail ? this._blocCompagnes(this._ficheDetail.compagnes) : ""}

        <div class="carte bloc">
          <h4>${T("blocCorriger")}</h4>
          <div class="actions-fiche">
            ${
              plante.evenements.length
                ? `<button class="bouton discret" data-annuler="${plante.uid}">
                     <ha-icon icon="mdi:undo"></ha-icon>
                     ${T("boutonAnnulerEvt", {
                       evenement: echappe(
                         plante.evenements[plante.evenements.length - 1].libelle
                       ),
                     })}
                   </button>`
                : ""
            }
            <button class="bouton danger" data-retirer="${plante.uid}">
              <ha-icon icon="mdi:delete-outline"></ha-icon> ${T(
                "boutonRetirerPlante"
              )}
            </button>
          </div>
        </div>
      </div>`;
  }

  _blocEauFiche(plante) {
    if (!this._jardin?.arrosage_actif) return "";
    const eau = plante.arrosage;
    const confirme = this._eauConfirmee?.has(plante.uid);

    return `<div class="carte bloc">
        <h4>${T("blocArrosage")}</h4>
        ${
          eau && eau.concernee
            ? `<div>${pastilleEau(eau, confirme)}</div>
               <div style="font-size:13px;color:var(--secondary-text-color);margin-top:8px">
                 ${T("eauTousLesJours", { jours: eau.frequence_jours })} · ${
                 eau.dernier
                   ? T("eauDernierLeLong", { date: fmtLong(eau.dernier) })
                   : T("eauJamaisCourt")
               }${
                 eau.prochain && !eau.a_arroser
                   ? ` · ${T("eauProchainLe", { date: fmtLong(eau.prochain) })}`
                   : ""
               }
               </div>
               <button class="bouton ${
                 eauAJour(eau, confirme) ? "discret" : ""
               }" data-arroser="${plante.uid}" style="margin-top:12px">
                 <ha-icon icon="mdi:watering-can"></ha-icon> ${T(
                   "boutonJeViensDArroser"
                 )}
               </button>`
            : `<p class="aide" style="margin-top:0">${echappe(
                eau?.motif_exclusion || T("eauSuiviInactif")
              )}</p>`
        }

        <div class="reglage" style="margin-top:14px">
          <label for="bascule-eau">${T("champRappelsEau")}</label>
          <input id="bascule-eau" type="checkbox" data-uid="${plante.uid}"
                 ${plante.arrosage_actif !== false ? "checked" : ""}
                 style="width:20px;height:20px">
        </div>
        <div class="reglage">
          <label for="champ-eau-freq">${T("champArroserTous")}</label>
          <span><input id="champ-eau-freq" type="number" min="0" max="60"
                       data-uid="${plante.uid}"
                       value="${plante.arrosage_frequence_jours || 0}"
                       style="width:90px"> ${T("uniteJours")}</span>
        </div>
        <p class="aide">${T("aideFrequenceEau", {
          precision: eau?.frequence_jours
            ? T("aideFrequenceEauPrecision", { jours: eau.frequence_jours })
            : "",
        })}</p>
      </div>`;
  }

  /** Le journal de la plante : le cycle et les arrosages, meles par date.
   *
   *  Les arrosages arrivent groupes par series consecutives. Une tomate
   *  arrosee tous les deux jours pendant un ete noierait sinon ses cinq
   *  etapes de cycle sous trente lignes identiques ; une serie tient en une
   *  ligne, qui porte toutes ses dates. */
  _entreesFrise(plante) {
    const brut = [
      ...(plante.evenements || []).map((evt) => ({ ...evt, eau: false })),
      ...(plante.arrosages || []).map((a) => ({ ...a, eau: true })),
    ].sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));

    const entrees = [];
    for (const item of brut) {
      const precedent = entrees[entrees.length - 1];
      if (item.eau && precedent?.eau) {
        precedent.dates.push(item.date);
      } else if (item.eau) {
        entrees.push({ eau: true, date: item.date, dates: [item.date] });
      } else {
        entrees.push(item);
      }
    }
    return entrees;
  }

  _friseEau(serie) {
    const nombre = serie.dates.length;
    const tete = `<strong>
        <ha-icon icon="mdi:watering-can"
                 style="--mdc-icon-size:16px;color:var(--rhizome-eau)"></ha-icon>
        ${nombre === 1 ? T("evt_arrosage") : T("friseArrosages", { nombre })}
      </strong>`;
    if (nombre === 1)
      return `${tete}<div class="date">${fmtLong(serie.dates[0])}</div>`;
    return `${tete}
      <div class="date">${T("frisePeriode", {
        debut: fmtCourt(serie.dates[0]),
        fin: fmtCourt(serie.dates[nombre - 1]),
      })}</div>
      <div class="compagnes" style="margin-top:6px">${serie.dates
        .map((d) => `<span class="compagne">${fmtCourt(d)}</span>`)
        .join("")}</div>`;
  }

  _blocFrise(plante) {
    const entrees = this._entreesFrise(plante);
    if (!entrees.length) {
      return `<div class="carte bloc"><h4>${T("blocJournal")}</h4>
        <div style="color:var(--secondary-text-color);font-size:14px">
          ${T("videFrise")}
        </div></div>`;
    }

    const etapes = entrees
      .map(
        (evt, index) => `
          <div class="frise-etape">
            <div class="frise-trait">
              <div class="frise-point ${evt.eau ? "eau" : ""}"></div>
              ${
                index < entrees.length - 1
                  ? `<div class="frise-barre"></div>`
                  : ""
              }
            </div>
            <div class="frise-texte">
              ${
                evt.eau
                  ? this._friseEau(evt)
                  : `<strong>${echappe(evt.libelle)}</strong>
              ${evt.quantite_g ? ` · ${kg(evt.quantite_g)}` : ""}
              <div class="date">${fmtLong(evt.date)}${
                      evt.cause ? ` · ${echappe(evt.cause)}` : ""
                    }</div>
              ${
                evt.note
                  ? `<div class="journal-note">${echappe(evt.note)}</div>`
                  : ""
              }`
              }
            </div>
          </div>`
      )
      .join("");

    return `<div class="carte bloc"><h4>${T(
      "blocJournal"
    )}</h4><div class="frise">${etapes}</div></div>`;
  }

  _ficheCulture() {
    const detail = this._ficheDetail;
    if (!detail) {
      return `<div class="fiche-tete">
          <h3>${T("chargementCourt")}</h3>
          <button class="icone" data-fermer="1"><ha-icon icon="mdi:close"></ha-icon></button>
        </div>`;
    }

    const culture = detail.culture;
    const zones = this._jardin?.zones || [];
    const dejaAu = (this._jardin?.plantes || []).filter(
      (p) => p.culture_id === culture.id
    );

    return `
      <div class="fiche-tete">
        <div class="emoji">${echappe(culture.emoji)}</div>
        <h3>${echappe(culture.nom)}</h3>
        <button class="icone" data-fermer="1"><ha-icon icon="mdi:close"></ha-icon></button>
      </div>

      <div class="fiche-corps">
        <div class="carte bloc">
          <h4>${T("blocAjouter")}</h4>
          ${
            dejaAu.length
              ? `<div style="font-size:13px;color:var(--secondary-text-color);margin-bottom:10px">
                   ${T("dejaAuPotager", {
                     nombre: dejaAu.length,
                     zones: dejaAu.map((p) => echappe(p.zone.nom)).join(", "),
                   })}
                 </div>`
              : ""
          }
          <div class="reglage">
            <label for="sel-zone-ajout">${T("champZone")}</label>
            <select id="sel-zone-ajout">
              ${zones
                .map(
                  (z) => `<option value="${echappe(z.id)}">${echappe(z.nom)}${
                    z.decalage_jours
                      ? ` (${z.decalage_jours > 0 ? "+" : ""}${
                          z.decalage_jours
                        } ${T("uniteJourCourt")})`
                      : ""
                  }</option>`
                )
                .join("")}
            </select>
          </div>
          <div class="reglage">
            <label for="champ-surnom-ajout">${T("champSurnom")}</label>
            <input id="champ-surnom-ajout" type="text"
                   placeholder="${T("surnomPlaceholder")}">
          </div>
          <div class="reglage">
            <label for="champ-echelon-ajout">${T("champRessemerTous")}</label>
            <span><input id="champ-echelon-ajout" type="number" min="0" max="90"
                         value="0" style="width:90px"> ${T("uniteJours")}</span>
          </div>
          <div id="avis-rotation" class="avertissement" hidden></div>
          <button class="bouton" data-ajouter="${culture.id}" style="margin-top:8px">
            <ha-icon icon="mdi:plus"></ha-icon> ${T("boutonAjouter")}
          </button>
        </div>

        <div class="carte bloc">
          <h4>${T("blocCetteFiche")}</h4>
          ${
            culture.perso
              ? `<p class="aide">${
                  culture.surcharge ? T("ficheCorrigee") : T("ficheCreee")
                }</p>`
              : `<p class="aide">${T("ficheEstimations")}</p>`
          }
          <div class="actions-fiche">
            <button class="bouton discret" data-corriger="${culture.id}">
              <ha-icon icon="mdi:pencil"></ha-icon> ${T("boutonCorrigerFiche")}
            </button>
            ${
              culture.surcharge
                ? `<button class="bouton discret" data-retablir="${culture.id}">
                     <ha-icon icon="mdi:restore"></ha-icon> ${T(
                       "boutonRetablirFiche"
                     )}
                   </button>`
                : ""
            }
          </div>
        </div>

        ${this._blocFenetres(detail.fenetres)}
        ${this._blocCulture(culture)}
        ${this._blocCompagnes(detail.compagnes)}
      </div>`;
  }

  _blocFenetres(fenetres) {
    if (!fenetres?.length) return "";
    return `<div class="carte bloc">
        <h4>${T("blocCalendrierType")}</h4>
        ${fenetres
          .map(
            (f) => `<div style="display:flex;justify-content:space-between;gap:12px;
                        padding:7px 0;border-bottom:1px solid var(--divider-color)">
              <span style="display:inline-flex;align-items:center;gap:8px">
                <i class="pastille" style="background:${
                  COULEURS_ETAPE[f.type] || "var(--primary-color)"
                }"></i>
                ${echappe(f.libelle)}
              </span>
              <span style="color:var(--secondary-text-color);font-size:13px;text-align:right">
                ${fmtCourt(f.debut)} → ${fmtCourt(f.fin)}
              </span>
            </div>`
          )
          .join("")}
        <div style="font-size:12px;color:var(--secondary-text-color);margin-top:10px">
          ${T("aideCalendrierType", {
            derniere: this._jardin?.gelees?.derniere || "?",
            premiere: this._jardin?.gelees?.premiere || "?",
          })}
        </div>
      </div>`;
  }

  _blocCulture(culture) {
    return `
      <div class="carte bloc">
        <h4>${T("blocLaCulture")}</h4>
        <div class="faits">
          <div class="fait"><div class="cle">${T("cleExposition")}</div>
            <div class="valeur">${
              libelleExposition(culture.exposition) || culture.exposition
            }</div></div>
          <div class="fait"><div class="cle">${T("cleArrosage")}</div>
            <div class="valeur">${T("valeurArrosage", {
              besoin: libelleEau(culture.arrosage.besoin),
              jours: culture.arrosage.frequence_jours,
            })}</div></div>
          <div class="fait"><div class="cle">${T("cleEspacement")}</div>
            <div class="valeur">${culture.espacement_cm} cm</div></div>
          <div class="fait"><div class="cle">${T("cleFamille")}</div>
            <div class="valeur">${echappe(culture.famille)}</div></div>
          <div class="fait"><div class="cle">${T("cleDifficulte")}</div>
            <div class="valeur">${"★".repeat(culture.difficulte)}${"☆".repeat(
      3 - culture.difficulte
    )}</div></div>
          <div class="fait"><div class="cle">${T("cleCycle")}</div>
            <div class="valeur">${
              culture.categorie === "plante-interieur"
                ? T("cycleInterieur")
                : culture.perenne
                ? ((culture.cycle || {}).duree_recolte_jours || 0) >=
                  RECOLTE_CONTINUE_JOURS
                  ? T("cycleContinue")
                  : T("cycleVivace")
                : T("cycleAnnuelle")
            }</div></div>
          <div class="fait"><div class="cle">${T("cleGel")}</div>
            <div class="valeur">${
              culture.categorie === "plante-interieur" &&
              culture.rusticite.temp_min_c != null
                ? T("gelInterieurMini", {
                    temperature: culture.rusticite.temp_min_c,
                  })
                : culture.rusticite.gel
                ? culture.rusticite.temp_min_c != null
                  ? T("gelSupporteJusqua", {
                      temperature: culture.rusticite.temp_min_c,
                    })
                  : T("gelSupporte")
                : T("gelCraint")
            }</div></div>
        </div>
        <div style="margin-top:12px;font-size:14px">
          <div style="color:var(--secondary-text-color);font-size:11px;text-transform:uppercase">${T(
            "cleSol"
          )}</div>
          ${echappe(culture.sol)}
        </div>
        ${
          culture.arrosage.notes
            ? `<div style="margin-top:10px;font-size:14px;line-height:1.5">
                 💧 ${echappe(culture.arrosage.notes)}</div>`
            : ""
        }
        ${
          culture.conseils?.length
            ? `<div style="margin-top:12px">
                 <div style="color:var(--secondary-text-color);font-size:11px;
                             text-transform:uppercase;margin-bottom:6px">${T(
                               "cleConseils"
                             )}</div>
                 <ul class="conseils">${culture.conseils
                   .map((c) => `<li>${echappe(c)}</li>`)
                   .join("")}</ul>
               </div>`
            : ""
        }
      </div>`;
  }

  _blocCompagnes(compagnes) {
    if (!compagnes) return "";
    const aime = compagnes.aime || [];
    const evite = compagnes.evite || [];
    if (!aime.length && !evite.length) return "";
    return `
      <div class="carte bloc">
        <h4>${T("blocVoisinage")}</h4>
        ${
          aime.length
            ? `<div style="font-size:13px;margin-bottom:4px">${T(
                "bonsVoisins"
              )}</div>
               <div class="compagnes" style="margin-bottom:12px">${aime
                 .map((c) => `<span class="compagne">${echappe(c.emoji)} ${echappe(c.nom)}</span>`)
                 .join("")}</div>`
            : ""
        }
        ${
          evite.length
            ? `<div style="font-size:13px;margin-bottom:4px">${T(
                "aEloigner"
              )}</div>
               <div class="compagnes">${evite
                 .map((c) => `<span class="compagne">${echappe(c.emoji)} ${echappe(c.nom)}</span>`)
                 .join("")}</div>`
            : ""
        }
      </div>`;
  }

  _demanderRecolte(uid) {
    this._ouvrirFichePlante(uid);
  }

  _brancherFiche(hote) {
    const voile = hote.querySelector("#voile");
    if (voile) {
      voile.addEventListener("click", (ev) => {
        if (ev.target === voile) this._fermerFiche();
      });
    }
    hote.querySelectorAll("[data-fermer]").forEach((el) =>
      el.addEventListener("click", () => this._fermerFiche())
    );

    // « Je viens d'arroser » n'avait jamais rien fait : la fiche se rend dans
    // son propre hote, et seul `_brancherVue` ecoutait `[data-arroser]`. Le
    // clic partait dans le vide, sans erreur ni retour — exactement ce qui
    // rendait l'arrosage illisible depuis la fiche.
    hote.querySelectorAll("[data-arroser]").forEach((el) =>
      el.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        el.disabled = true;
        await this._arroser([el.dataset.arroser]);
      })
    );

    hote.querySelectorAll("[data-fait-fiche]").forEach((el) =>
      el.addEventListener("click", async () => {
        const corr = EVT_POUR_ETAPE[el.dataset.etape];
        if (!corr) return;
        if (corr.evenement === "recolte") {
          const champ = hote.querySelector("#qte-recolte");
          champ?.focus();
          return;
        }
        el.disabled = true;
        await this._noter(el.dataset.faitFiche, corr.evenement,
          corr.mode ? { mode: corr.mode } : {});
      })
    );

    hote.querySelectorAll("[data-recolter]").forEach((el) =>
      el.addEventListener("click", async () => {
        const champ = hote.querySelector("#qte-recolte");
        const brut = champ?.value?.trim();
        el.disabled = true;
        await this._noter(el.dataset.recolter, "recolte",
          brut ? { quantite_g: Number(brut) } : {});
      })
    );

    const zoneAjout = hote.querySelector("#sel-zone-ajout");
    const avis = hote.querySelector("#avis-rotation");
    if (zoneAjout && avis && this._fiche?.type === "culture") {
      const verifier = async () => {
        try {
          const r = await this._hass.callWS({
            type: "rhizome/rotation",
            culture_id: this._fiche.id,
            zone: zoneAjout.value,
          });
          if (r?.avertissement) {
            avis.innerHTML = `<ha-icon icon="mdi:alert-outline"></ha-icon> ${echappe(
              r.avertissement.message
            )}`;
            avis.hidden = false;
          } else {
            avis.hidden = true;
          }
        } catch (err) {
          avis.hidden = true;
        }
      };
      zoneAjout.addEventListener("change", verifier);
      verifier();
    }

    hote.querySelectorAll("[data-corriger]").forEach((el) =>
      el.addEventListener("click", () => {
        const fiche = this._ficheDetail?.culture;
        this._fiche = {
          type: "perso",
          fiche: fiche ? _versFormulaire(fiche) : null,
        };
        this._rendreFiche();
      })
    );

    hote.querySelectorAll("[data-retablir]").forEach((el) =>
      el.addEventListener("click", async () => {
        if (!confirm(T("confirmRetablirFiche"))) return;
        el.disabled = true;
        await this._appeler({
          type: "rhizome/culture_perso/retablir",
          culture_id: el.dataset.retablir,
        });
        this._fermerFiche();
      })
    );

    hote.querySelectorAll("[data-ajouter]").forEach((el) =>
      el.addEventListener("click", async () => {
        el.disabled = true;
        const zone = hote.querySelector("#sel-zone-ajout")?.value;
        const surnom = hote.querySelector("#champ-surnom-ajout")?.value?.trim();
        const echelon = Number(
          hote.querySelector("#champ-echelon-ajout")?.value || 0
        );
        const reponse = await this._appeler({
          type: "rhizome/ajouter",
          culture_id: el.dataset.ajouter,
          zone: zone || "pleine-terre",
          surnom: surnom || null,
          echelonnement_jours: echelon || null,
        });
        if (reponse?.uid) {
          this._vue = "potager";
          this.shadowRoot
            .getElementById("nav")
            .querySelectorAll("button")
            .forEach((b) =>
              b.setAttribute("aria-selected", String(b.dataset.vue === "potager"))
            );
          this._fermerFiche();
          this._rendreVue();
        }
      })
    );

    hote.querySelectorAll("[data-annuler]").forEach((el) =>
      el.addEventListener("click", async () => {
        el.disabled = true;
        await this._appeler({ type: "rhizome/annuler", uid: el.dataset.annuler });
      })
    );

    hote.querySelectorAll("[data-retirer]").forEach((el) =>
      el.addEventListener("click", async () => {
        if (!confirm(T("confirmRetirerPlante"))) return;
        el.disabled = true;
        await this._appeler({ type: "rhizome/retirer", uid: el.dataset.retirer });
        this._fermerFiche();
      })
    );

    hote.querySelector("#pf-enregistrer")?.addEventListener("click", async (ev) => {
      const zoneErreur = hote.querySelector("#pf-erreur");
      zoneErreur.hidden = true;
      ev.target.disabled = true;
      try {
        await this._hass.callWS({
          type: "rhizome/culture_perso/definir",
          fiche: this._lireFichePerso(),
        });
        await this._charger({ discret: true });
        this._fermerFiche();
      } catch (err) {
        // L'erreur s'affiche dans le formulaire, à côté du champ fautif :
        // la renvoyer en bandeau ferait perdre la saisie de vue.
        zoneErreur.textContent = err?.message || T("ficheIncomplete");
        zoneErreur.hidden = false;
        ev.target.disabled = false;
      }
    });

    const modifier = (champs) =>
      this._appeler({ type: "rhizome/modifier", ...champs });

    const zone = hote.querySelector("#sel-zone");
    if (zone) {
      zone.addEventListener("change", () =>
        modifier({ uid: zone.dataset.uid, zone: zone.value })
      );
    }
    const surnom = hote.querySelector("#champ-surnom");
    if (surnom) {
      surnom.addEventListener("change", () =>
        modifier({ uid: surnom.dataset.uid, surnom: surnom.value.trim() || null })
      );
    }
    const notifs = hote.querySelector("#bascule-notifs");
    if (notifs) {
      notifs.addEventListener("change", () =>
        modifier({ uid: notifs.dataset.uid, notifs: notifs.checked })
      );
    }
    const rappel = hote.querySelector("#champ-rappel");
    if (rappel) {
      rappel.addEventListener("change", () =>
        modifier({ uid: rappel.dataset.uid, rappel_jours: Number(rappel.value) })
      );
    }
    const basculeEau = hote.querySelector("#bascule-eau");
    if (basculeEau) {
      basculeEau.addEventListener("change", () =>
        modifier({
          uid: basculeEau.dataset.uid,
          arrosage_actif: basculeEau.checked,
        })
      );
    }
    const freqEau = hote.querySelector("#champ-eau-freq");
    if (freqEau) {
      freqEau.addEventListener("change", () =>
        modifier({
          uid: freqEau.dataset.uid,
          arrosage_frequence_jours: Number(freqEau.value) || null,
        })
      );
    }

    const echelon = hote.querySelector("#champ-echelon");
    if (echelon) {
      echelon.addEventListener("change", () =>
        modifier({
          uid: echelon.dataset.uid,
          echelonnement_jours: Number(echelon.value) || null,
        })
      );
    }
  }

  // --- Vue : Réglages ------------------------------------------------------

  _vueReglages() {
    if (!this._reglages) {
      return `<div class="chargement">${T("chargementReglages")}</div>`;
    }
    const o = this._reglages.options;
    return `
      ${this._blocSaison(o)}
      ${this._blocLangue(o)}
      ${this._blocNotifs(o)}
      ${this._blocEauReglages(o)}
      ${this._blocZones()}
      ${this._blocCataloguePerso()}
      ${this._blocAffichage(o)}`;
  }

  _blocSaison(o) {
    const presets = [
      ["oceanique", T("presetOceanique")],
      ["nord_est", T("presetNordEst")],
      ["midi", T("presetMidi")],
      ["montagne", T("presetMontagne")],
      ["personnalise", T("presetPersonnalise")],
    ];
    return `
      <h2>${T("titreSaison")}</h2>
      <div class="carte bloc">
        <p class="aide">${T("aideSaison", {
          total: this._catalogue?.total || 172,
        })}</p>
        <div class="reglage">
          <label for="preset">${T("champClimat")}</label>
          <select id="preset">
            ${presets
              .map(
                ([v, l]) =>
                  `<option value="${v}" ${
                    o.preset_climat === v ? "selected" : ""
                  }>${l}</option>`
              )
              .join("")}
          </select>
        </div>
        ${this._champDate(T("champGeleePrintemps"), "gelee-der", o.gelees_derniere)}
        ${this._champDate(T("champGeleeAutomne"), "gelee-pre", o.gelees_premiere)}
        <p class="aide">${T("aideGelees")}</p>
      </div>`;
  }

  /** Le selecteur de langue.
   *
   *  Il vit dans le panneau et pas seulement dans « Configurer » parce que
   *  c'est ici que l'utilisateur passe son temps — et parce que le reglage
   *  touche tout ce qu'il a sous les yeux. Le changer recharge l'entree cote
   *  serveur (noms d'entites, rappels, calendrier), et le panneau se redessine
   *  tout seul a la reponse. */
  _blocLangue(o) {
    const choix = [
      ["auto", T("langueAuto")],
      ["fr", T("langueFr")],
      ["en", T("langueEn")],
    ];
    const courante = o.langue || "auto";
    return `
      <h2>${T("titreLangue")}</h2>
      <div class="carte bloc">
        <div class="reglage">
          <label for="langue">${T("champLangue")}</label>
          <select id="langue">
            ${choix
              .map(
                ([v, l]) =>
                  `<option value="${v}" ${
                    courante === v ? "selected" : ""
                  }>${l}</option>`
              )
              .join("")}
          </select>
        </div>
        <p class="aide">${T("aideLangue")}</p>
        <p class="aide">${T("aideLangueEtat")}</p>
      </div>`;
  }

  _champDate(libelle, id, valeur) {
    // `numeroMois` et non `mois` : `mois()` est la fonction qui rend les
    // initiales des mois, et l'ombrer ici rendait le calendrier muet.
    const [numeroMois, jour] = (valeur || "01-01").split("-").map(Number);
    return `
      <div class="reglage">
        <label>${libelle}</label>
        <span style="display:flex;gap:6px">
          <select id="${id}-mois">
            ${moisLongs()
              .map(
                (m, i) =>
                  `<option value="${i + 1}" ${
                    numeroMois === i + 1 ? "selected" : ""
                  }>${m}</option>`
              )
              .join("")}
          </select>
          <input id="${id}-jour" type="number" min="1" max="31" value="${jour}"
                 style="width:64px">
        </span>
      </div>`;
  }

  _blocNotifs(o) {
    const cibles = this._reglages.cibles_possibles || [];
    const choisies = o.notify_targets || [];
    const etapes = o.notify_etapes || [];
    // Les memes cles que le serveur, qui les tient dans `i18n.py` : une etape
    // ajoutee la se traduit ici sans retoucher cette liste.
    const etapesNotifiables = (
      this._reglages.etapes_notifiables || [
        "semis_interieur", "semis_direct", "repiquage", "plantation", "recolte",
      ]
    ).map((cle) => [cle, T(`etape_${cle}`)]);

    return `
      <h2>${T("titreRappels")}</h2>
      <div class="carte bloc">
        <h4>${T("sousTitreAQui")}</h4>
        ${
          cibles.length
            ? cibles
                .map(
                  (c) => `
            <label class="case">
              <input type="checkbox" data-cible="${c.value}"
                     ${choisies.includes(c.value) ? "checked" : ""}>
              <span>${echappe(c.label)}${
                    c.mobile ? "" : T("sansBoutonAction")
                  }</span>
            </label>`
                )
                .join("")
            : `<p class="aide">${T("aucuneAppMobile")}</p>`
        }
        <p class="aide">${T("aideAQui")}</p>
      </div>

      <div class="carte bloc">
        <h4>${T("sousTitreQuoi")}</h4>
        ${etapesNotifiables
          .map(
            ([cle, lib]) => `
          <label class="case">
            <input type="checkbox" data-etape-notif="${cle}"
                   ${etapes.includes(cle) ? "checked" : ""}>
            <span>${lib}</span>
          </label>`
          )
          .join("")}
        <label class="case">
          <input type="checkbox" id="notify-arrosage"
                 ${o.notify_arrosage !== false ? "checked" : ""}>
          <span>${T("etapeArroser")}</span>
        </label>
        <p class="aide">${T("aideQuoi")}</p>
        <p class="aide">${T("aideQuoiEau")}</p>
      </div>

      <div class="carte bloc">
        <h4>${T("sousTitreQuand")}</h4>
        <div class="reglage">
          <label for="heure">${T("champHeure")}</label>
          <input id="heure" type="time" value="${(o.notify_heure || "08:00:00").slice(0, 5)}">
        </div>
        <div class="reglage">
          <label for="rappel">${T("champPrevenirAvance")}</label>
          <span><input id="rappel" type="number" min="0" max="30"
                       value="${o.rappel_jours}" style="width:72px"> ${T(
      "uniteJours"
    )}</span>
        </div>
        <div class="reglage">
          <label for="recurrence">${T("champRelancer")}</label>
          <span><input id="recurrence" type="number" min="0" max="30"
                       value="${o.notify_recolte_recurrence}"
                       style="width:72px"> ${T("uniteJours")}</span>
        </div>
        <p class="aide">${T("aideRelancer")}</p>
      </div>

      <div class="carte bloc">
        <h4>${T("sousTitreComment")}</h4>
        <label class="case">
          <input type="checkbox" id="resume" ${o.notify_resume ? "checked" : ""}>
          <span>${T("champResume")}</span>
        </label>
        <p class="aide">${T("aideResume")}</p>
        <p class="aide">${T("aideResumePlante")}</p>
      </div>`;
  }

  _blocEauReglages(o) {
    return `
      <h2>${T("titreArrosage")}</h2>
      <div class="carte bloc">
        <label class="case">
          <input type="checkbox" id="arrosage-actif"
                 ${o.arrosage_actif !== false ? "checked" : ""}>
          <span>${T("champSuivreArrosage")}</span>
        </label>
        <p class="aide">${T("aideArrosageCoupe")}</p>
        <p class="aide">${T("aideArrosageTheorique")}</p>
        <p class="aide">${T("aideArrosageGardeFous")}</p>
      </div>`;
  }

  _blocZones() {
    const zones = this._jardin?.zones || [];
    return `
      <h2>${T("titreZones")}</h2>
      <div class="carte bloc">
        <p class="aide">${T("aideZones")}</p>
        <div id="zones-liste">
          ${zones
            .map(
              (z, i) => `
            <div class="ligne-zone" data-zone-index="${i}">
              <input class="zone-nom" type="text" value="${echappe(z.nom)}"
                     placeholder="${T("zoneNomPlaceholder")}">
              <span style="display:flex;align-items:center;gap:6px">
                <input class="zone-decalage" type="number" min="-120" max="120"
                       value="${z.decalage_jours}" style="width:76px">
                <span class="aide" style="margin:0">${T("uniteJourCourt")}</span>
              </span>
              <label class="case" style="padding:0;white-space:nowrap"
                     title="${T("zoneAbriteeAide")}">
                <input class="zone-abritee" type="checkbox" ${
                  z.abritee ? "checked" : ""
                }>
                <span class="aide" style="margin:0">${T("zoneAbritee")}</span>
              </label>
              <button class="icone" data-zone-suppr="${i}"
                      title="${T("boutonSupprimer")}">
                <ha-icon icon="mdi:close"></ha-icon>
              </button>
            </div>`
            )
            .join("")}
        </div>
        <div class="actions-fiche" style="margin-top:12px">
          <button class="bouton discret" id="zone-ajouter">
            <ha-icon icon="mdi:plus"></ha-icon> ${T("boutonAjouterZone")}
          </button>
          <button class="bouton" id="zones-enregistrer">
            <ha-icon icon="mdi:content-save"></ha-icon> ${T(
              "boutonEnregistrerZones"
            )}
          </button>
        </div>
      </div>`;
  }

  _blocCataloguePerso() {
    const perso = this._cataloguePerso || [];
    return `
      <h2>${T("titreMesFiches")}</h2>
      <div class="carte bloc">
        <p class="aide">${T("aideMesFiches")}</p>
        ${
          perso.length
            ? perso
                .map(
                  (c) => `
            <div class="ligne-zone">
              <span style="flex:1">${echappe(c.emoji)} ${echappe(c.nom)}
                <span class="aide" style="margin:0">· ${
                  libelleCategorie(c.categorie) || c.categorie
                }${
                  c.surcharge
                    ? T("marqueurFicheCorrigee")
                    : T("marqueurFicheInedite")
                }</span>
              </span>
              <button class="icone" data-perso-editer="${c.id}"
                      title="${T("boutonModifier")}">
                <ha-icon icon="mdi:pencil"></ha-icon>
              </button>
              <button class="icone" data-perso-suppr="${c.id}"
                      title="${T("boutonSupprimer")}">
                <ha-icon icon="mdi:delete-outline"></ha-icon>
              </button>
            </div>`
                )
                .join("")
            : `<p class="aide">${T("aucuneFichePerso")}</p>`
        }
        <div class="actions-fiche" style="margin-top:12px">
          <button class="bouton" id="perso-nouvelle">
            <ha-icon icon="mdi:plus"></ha-icon> ${T("boutonAjouterFiche")}
          </button>
        </div>
      </div>`;
  }

  _blocAffichage(o) {
    return `
      <h2>${T("titreAffichage")}</h2>
      <div class="carte bloc">
        <label class="case">
          <input type="checkbox" id="masquer-terminees"
                 ${o.masquer_terminees ? "checked" : ""}>
          <span>${T("champMasquerTerminees")}</span>
        </label>
        <p class="aide">${T("aideMasquerTerminees")}</p>
      </div>`;
  }

  // --- Formulaire de fiche personnelle -------------------------------------

  _fichePerso() {
    const f = this._fiche.fiche || {};
    const p = f.periodes || {};
    const selMois = (id, valeur) =>
      `<select id="${id}">
         <option value="">—</option>
         ${moisLongs()
           .map(
             (m, i) =>
               `<option value="${i + 1}" ${
                 Number(valeur) === i + 1 ? "selected" : ""
               }>${m}</option>`
           )
           .join("")}
       </select>`;

    const periode = (cle, libelle) => `
      <div class="reglage">
        <label>${libelle}</label>
        <span style="display:flex;gap:6px;align-items:center">
          ${selMois(`per-${cle}-debut`, (p[cle] || {}).debut)}
          <span class="aide" style="margin:0">${T("separateurPeriode")}</span>
          ${selMois(`per-${cle}-fin`, (p[cle] || {}).fin)}
        </span>
      </div>`;

    const choix = (id, valeur, options) =>
      `<select id="${id}">${options
        .map(
          ([v, l]) =>
            `<option value="${v}" ${valeur === v ? "selected" : ""}>${l}</option>`
        )
        .join("")}</select>`;

    return `
      <div class="fiche-tete">
        <div class="emoji">${echappe(f.emoji || "🌱")}</div>
        <h3>${f.id ? T("titreModifierFiche") : T("titreNouvelleFiche")}</h3>
        <button class="icone" data-fermer="1"><ha-icon icon="mdi:close"></ha-icon></button>
      </div>

      <div class="fiche-corps">
        <div class="carte bloc">
          <h4>${T("blocIdentite")}</h4>
          <div class="reglage">
            <label for="pf-nom">${T("champNomFiche")}</label>
            <input id="pf-nom" type="text" value="${echappe(f.nom || "")}"
                   placeholder="${T("exempleNomFiche")}">
          </div>
          <div class="reglage">
            <label for="pf-emoji">${T("champEmoji")}</label>
            <input id="pf-emoji" type="text" value="${echappe(f.emoji || "")}"
                   placeholder="🥬" style="width:80px">
          </div>
          <div class="reglage">
            <label for="pf-categorie">${T("champCategorie")}</label>
            ${choix(
              "pf-categorie",
              f.categorie,
              CATEGORIES_IDS.map((id) => [id, libelleCategorie(id)])
            )}
          </div>
          <div class="reglage">
            <label for="pf-famille">${T("champFamilleFiche")}</label>
            <input id="pf-famille" type="text" value="${echappe(f.famille || "")}"
                   placeholder="${T("exempleFamille")}">
          </div>
        </div>

        <div class="carte bloc">
          <h4>${T("blocConditions")}</h4>
          <div class="reglage">
            <label for="pf-expo">${T("champExposition")}</label>
            ${choix(
              "pf-expo",
              f.exposition || "plein-soleil",
              Object.keys(ICONES_EXPOSITION).map((id) => [
                id,
                libelleExposition(id),
              ])
            )}
          </div>
          <div class="reglage">
            <label for="pf-eau">${T("champBesoinEau")}</label>
            ${choix(
              "pf-eau",
              (f.arrosage || {}).besoin || "moyen",
              ["faible", "moyen", "eleve"].map((id) => [id, libelleEau(id)])
            )}
          </div>
          <div class="reglage">
            <label for="pf-freq">${T("champArroserTous")}</label>
            <span><input id="pf-freq" type="number" min="1" max="30"
                         value="${(f.arrosage || {}).frequence_jours || 4}"
                         style="width:72px"> ${T("uniteJours")}</span>
          </div>
          <div class="reglage">
            <label for="pf-espacement">${T("cleEspacement")}</label>
            <span><input id="pf-espacement" type="number" min="1" max="1000"
                         value="${f.espacement_cm || 30}" style="width:72px"> cm</span>
          </div>
          <div class="reglage">
            <label for="pf-difficulte">${T("champDifficulte")}</label>
            ${choix("pf-difficulte", String(f.difficulte || 1), [
              ["1", T("difficulteFacile")],
              ["2", T("difficulteMoyenne")],
              ["3", T("difficulteExigeante")],
            ])}
          </div>
          <label class="case">
            <input type="checkbox" id="pf-gel" ${
              f.gel === false ? "" : "checked"
            }>
            <span>${T("champResisteGel")}</span>
          </label>
          <p class="aide">${T("aideGelFiche")}</p>
          <label class="case">
            <input type="checkbox" id="pf-perenne" ${f.perenne ? "checked" : ""}>
            <span>${T("champPerenne")}</span>
          </label>
        </div>

        <div class="carte bloc">
          <h4>${T("blocPeriodes")}</h4>
          ${
            f.livree
              ? `<p class="aide">${T("aidePeriodesLivree")}</p>
                 ${(this._ficheDetail?.fenetres || [])
                   .map(
                     (w) => `<div class="reglage">
                       <label>${echappe(w.libelle)}</label>
                       <span>${fmtCourt(w.debut)} → ${fmtCourt(w.fin)}</span>
                     </div>`
                   )
                   .join("")}`
              : `<p class="aide">${T("aidePeriodesMois")}</p>
                 ${periode("semis_interieur", T("etape_semis_interieur"))}
                 ${periode("semis_direct", T("etape_semis_direct"))}
                 ${periode("plantation", T("etape_plantation"))}
                 ${periode("recolte", T("etape_recolte"))}
                 <p class="aide">${T("aidePeriodesPerenne")}</p>`
          }
        </div>

        <div class="carte bloc">
          <h4>${T("blocDurees")}</h4>
          <div class="reglage">
            <label for="pf-semis-recolte">${T("champSemisRecolte")}</label>
            <span><input id="pf-semis-recolte" type="number" min="0" max="900"
                         value="${f.jours_semis_a_recolte || ""}"
                         style="width:84px"> ${T("uniteJours")}</span>
          </div>
          <div class="reglage">
            <label for="pf-semis-repiquage">${T("champSemisRepiquage")}</label>
            <span><input id="pf-semis-repiquage" type="number" min="0" max="365"
                         value="${f.jours_semis_a_repiquage || ""}"
                         style="width:84px"> ${T("uniteJours")}</span>
          </div>
          <div class="reglage">
            <label for="pf-plantation-recolte">${T(
              "champPlantationRecolte"
            )}</label>
            <span><input id="pf-plantation-recolte" type="number" min="0" max="900"
                         value="${f.jours_plantation_a_recolte || ""}"
                         style="width:84px"> ${T("uniteJours")}</span>
          </div>
          <div class="reglage">
            <label for="pf-duree-recolte">${T("champDureeRecolte")}</label>
            <span><input id="pf-duree-recolte" type="number" min="1" max="365"
                         value="${f.duree_recolte_jours || 30}"
                         style="width:84px"> ${T("uniteJours")}</span>
          </div>
          <p class="aide">${T("aideDurees")}</p>
        </div>

        <div class="carte bloc">
          <h4>${T("blocNotes")}</h4>
          <div class="reglage">
            <label for="pf-arrosage-notes">${T("champConseilArrosage")}</label>
            <input id="pf-arrosage-notes" type="text"
                   value="${echappe((f.arrosage || {}).notes || "")}">
          </div>
          <div class="reglage">
            <label for="pf-sol">${T("champSolFiche")}</label>
            <input id="pf-sol" type="text" value="${echappe(f.sol || "")}"
                   placeholder="${T("exempleSol")}">
          </div>
          <div class="reglage">
            <label for="pf-conseils">${T("champConseils")}</label>
          </div>
          <textarea id="pf-conseils" rows="3" style="width:100%;border:1px solid
                    var(--divider-color);border-radius:8px;padding:8px;
                    background:var(--card-background-color);
                    color:var(--primary-text-color);font-family:inherit"
          >${echappe((f.conseils || []).join("\n"))}</textarea>
        </div>

        <div class="carte bloc">
          <div class="actions-fiche">
            <button class="bouton" id="pf-enregistrer">
              <ha-icon icon="mdi:content-save"></ha-icon> ${T(
                "boutonEnregistrerFiche"
              )}
            </button>
            <button class="bouton discret" data-fermer="1">${T(
              "boutonAnnuler"
            )}</button>
          </div>
          <div id="pf-erreur" class="erreur" hidden style="margin-top:12px"></div>
        </div>
      </div>`;
  }

  _lireFichePerso() {
    const sr = this.shadowRoot.getElementById("fiche");
    const v = (id) => sr.querySelector(`#${id}`)?.value?.trim() || "";
    const n = (id) => {
      const brut = v(id);
      return brut === "" ? null : Number(brut);
    };
    const periode = (cle) => {
      const debut = n(`per-${cle}-debut`);
      return debut ? { debut, fin: n(`per-${cle}-fin`) || debut } : null;
    };

    return {
      id: this._fiche.fiche?.id || null,
      nom: v("pf-nom"),
      emoji: v("pf-emoji") || "🌱",
      categorie: v("pf-categorie"),
      famille: v("pf-famille"),
      exposition: v("pf-expo"),
      arrosage: {
        besoin: v("pf-eau"),
        frequence_jours: n("pf-freq") || 4,
        notes: v("pf-arrosage-notes"),
      },
      sol: v("pf-sol"),
      espacement_cm: n("pf-espacement") || 30,
      difficulte: n("pf-difficulte") || 1,
      gel: sr.querySelector("#pf-gel")?.checked ?? true,
      perenne: sr.querySelector("#pf-perenne")?.checked || false,
      // Une fiche livree ne renvoie aucune periode : le serveur conserve
      // alors ses fenetres d'origine.
      periodes: this._fiche.fiche?.livree
        ? {}
        : {
            semis_interieur: periode("semis_interieur"),
            semis_direct: periode("semis_direct"),
            plantation: periode("plantation"),
            recolte: periode("recolte"),
          },
      jours_semis_a_recolte: n("pf-semis-recolte"),
      jours_semis_a_repiquage: n("pf-semis-repiquage"),
      jours_plantation_a_recolte: n("pf-plantation-recolte"),
      duree_recolte_jours: n("pf-duree-recolte") || 30,
      conseils: (sr.querySelector("#pf-conseils")?.value || "")
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean),
    };
  }

  // --- Câblage des réglages ------------------------------------------------

  async _enregistrerReglages(partiel) {
    const reponse = await this._appeler({
      type: "rhizome/reglages/definir",
      options: partiel,
    });
    if (reponse?.options) {
      this._reglages.options = reponse.options;
    }
    return reponse;
  }

  /** Change la langue, puis attend que l'entree soit remontee.
   *
   *  Ecrire ce reglage fait recharger l'entree de configuration cote serveur,
   *  parce que les noms d'entites sont poses a leur creation : sans
   *  rechargement, « Actions à mener » resterait en francais jusqu'au
   *  redemarrage. Le temps de ce rechargement, les commandes WebSocket
   *  repondent « pas chargé ». On ne montre donc pas ce refus transitoire :
   *  on reessaie, et on n'affiche une erreur que si ca ne revient pas.
   */
  async _changerLangue(valeur) {
    try {
      await this._hass.callWS({
        type: "rhizome/reglages/definir",
        options: { langue: valeur },
      });
    } catch (err) {
      this._erreur = err?.message || T("actionRefusee");
      this._rendreVue();
      return;
    }
    for (const attente of [150, 400, 1000]) {
      await new Promise((suite) => setTimeout(suite, attente));
      try {
        await this._charger({ discret: true });
        if (!this._erreur) return;
      } catch (err) {
        /* on retente */
      }
    }
    await this._charger({ discret: true });
  }

  _brancherReglages(hote) {
    const jourMois = (id) => {
      const mois = Number(hote.querySelector(`#${id}-mois`)?.value || 1);
      const jour = Number(hote.querySelector(`#${id}-jour`)?.value || 1);
      return `${String(mois).padStart(2, "0")}-${String(jour).padStart(2, "0")}`;
    };

    const langue = hote.querySelector("#langue");
    langue?.addEventListener("change", () => this._changerLangue(langue.value));

    const preset = hote.querySelector("#preset");
    preset?.addEventListener("change", () =>
      this._enregistrerReglages({ preset_climat: preset.value })
    );

    ["gelee-der", "gelee-pre"].forEach((id) =>
      ["mois", "jour"].forEach((suffixe) =>
        hote.querySelector(`#${id}-${suffixe}`)?.addEventListener("change", () =>
          this._enregistrerReglages({
            preset_climat: "personnalise",
            gelees_derniere: jourMois("gelee-der"),
            gelees_premiere: jourMois("gelee-pre"),
          })
        )
      )
    );

    const cibles = () =>
      [...hote.querySelectorAll("[data-cible]")]
        .filter((c) => c.checked)
        .map((c) => c.dataset.cible);
    hote.querySelectorAll("[data-cible]").forEach((c) =>
      c.addEventListener("change", () =>
        this._enregistrerReglages({ notify_targets: cibles() })
      )
    );

    const etapes = () =>
      [...hote.querySelectorAll("[data-etape-notif]")]
        .filter((c) => c.checked)
        .map((c) => c.dataset.etapeNotif);
    hote.querySelectorAll("[data-etape-notif]").forEach((c) =>
      c.addEventListener("change", () =>
        this._enregistrerReglages({ notify_etapes: etapes() })
      )
    );

    const notifEau = hote.querySelector("#notify-arrosage");
    notifEau?.addEventListener("change", () =>
      this._enregistrerReglages({ notify_arrosage: notifEau.checked })
    );

    const heure = hote.querySelector("#heure");
    heure?.addEventListener("change", () =>
      this._enregistrerReglages({ notify_heure: `${heure.value}:00` })
    );
    const rappel = hote.querySelector("#rappel");
    rappel?.addEventListener("change", () =>
      this._enregistrerReglages({ rappel_jours: Number(rappel.value) })
    );
    const recurrence = hote.querySelector("#recurrence");
    recurrence?.addEventListener("change", () =>
      this._enregistrerReglages({
        notify_recolte_recurrence: Number(recurrence.value),
      })
    );
    const resume = hote.querySelector("#resume");
    resume?.addEventListener("change", () =>
      this._enregistrerReglages({ notify_resume: resume.checked })
    );
    const arrosageActif = hote.querySelector("#arrosage-actif");
    arrosageActif?.addEventListener("change", () =>
      this._enregistrerReglages({ arrosage_actif: arrosageActif.checked })
    );
    const masquer = hote.querySelector("#masquer-terminees");
    masquer?.addEventListener("change", () =>
      this._enregistrerReglages({ masquer_terminees: masquer.checked })
    );

    // --- Zones
    hote.querySelector("#zone-ajouter")?.addEventListener("click", () => {
      const liste = hote.querySelector("#zones-liste");
      const index = liste.querySelectorAll(".ligne-zone").length;
      const ligne = document.createElement("div");
      ligne.className = "ligne-zone";
      ligne.dataset.zoneIndex = String(index);
      ligne.innerHTML = `
        <input class="zone-nom" type="text" value=""
               placeholder="${T("zoneNomPlaceholder")}">
        <span style="display:flex;align-items:center;gap:6px">
          <input class="zone-decalage" type="number" min="-120" max="120" value="0"
                 style="width:76px">
          <span class="aide" style="margin:0">${T("uniteJourCourt")}</span>
        </span>
        <label class="case" style="padding:0;white-space:nowrap">
          <input class="zone-abritee" type="checkbox">
          <span class="aide" style="margin:0">${T("zoneAbritee")}</span>
        </label>
        <button class="icone" data-zone-suppr="${index}">
          <ha-icon icon="mdi:close"></ha-icon>
        </button>`;
      liste.appendChild(ligne);
      ligne
        .querySelector("[data-zone-suppr]")
        .addEventListener("click", () => ligne.remove());
      ligne.querySelector(".zone-nom").focus();
    });

    hote.querySelectorAll("[data-zone-suppr]").forEach((b) =>
      b.addEventListener("click", () => b.closest(".ligne-zone")?.remove())
    );

    hote.querySelector("#zones-enregistrer")?.addEventListener("click", async (ev) => {
      const zones = [...hote.querySelectorAll(".ligne-zone")]
        .map((ligne) => {
          const nom = ligne.querySelector(".zone-nom").value.trim();
          if (!nom) return null;
          return {
            id: slugifier(nom),
            nom,
            decalage_jours: Number(ligne.querySelector(".zone-decalage").value || 0),
            abritee: ligne.querySelector(".zone-abritee")?.checked || false,
          };
        })
        .filter(Boolean);
      if (!zones.length) {
        this._erreur = T("erreurGarderUneZone");
        this._rendreVue();
        return;
      }
      ev.target.disabled = true;
      await this._appeler({ type: "rhizome/zones", zones });
    });

    // --- Catalogue personnel
    hote.querySelector("#perso-nouvelle")?.addEventListener("click", () => {
      this._fiche = { type: "perso", fiche: null };
      this._rendreFiche();
    });
    hote.querySelectorAll("[data-perso-editer]").forEach((b) =>
      b.addEventListener("click", () => {
        const fiche = (this._cataloguePerso || []).find(
          (c) => c.id === b.dataset.persoEditer
        );
        this._fiche = { type: "perso", fiche: fiche ? _versFormulaire(fiche) : null };
        this._rendreFiche();
      })
    );
    hote.querySelectorAll("[data-perso-suppr]").forEach((b) =>
      b.addEventListener("click", async () => {
        if (!confirm(T("confirmSupprimerFiche"))) return;
        b.disabled = true;
        await this._appeler({
          type: "rhizome/culture_perso/supprimer",
          culture_id: b.dataset.persoSuppr,
        });
      })
    );
  }
}

customElements.define("rhizome-panel", RhizomePanel);
