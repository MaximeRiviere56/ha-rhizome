"""Table compacte des cultures, compilee en data/catalog.json.

Pourquoi une table et pas du JSON ecrit a la main : 100 cultures x 25 champs
tiennent ici en une ligne chacune, les valeurs par defaut sont appliquees une
seule fois, et ajouter une culture reste une ligne a ecrire.

Les fenetres ne contiennent JAMAIS de mois en dur : chaque offset est un nombre
de jours par rapport a la derniere gelee de printemps ("derniere") ou a la
premiere gelee d'automne ("premiere"). Le calendrier devient ainsi juste partout.
Seules les perennes declarent une recolte a date fixe, puisqu'elle ne depend
plus d'un semis.

cycle = (jours_semis_a_repiquage, jours_semis_a_recolte,
         jours_plantation_a_recolte, duree_recolte_jours)
"""

from __future__ import annotations

CULTURES: list[dict] = []


def C(
    cid, nom, sci, famille, cat, emoji, *,
    expo="plein-soleil", eau="moyen", freq=4, sol="ordinaire, bien drainé",
    espacement=30, prof=None, diff=2, gel=True, tmin=None, perenne=False,
    semis_int=None, semis_dir=None, plantation=None, recolte=None,
    anchor_si="derniere", anchor_sd="derniere", anchor_pl="derniere",
    cycle=(None, None, None, 30),
    eau_notes="", aime=(), evite=(), conseils=(),
):
    ancrages = {"derniere": "gelees_derniere", "premiere": "gelees_premiere"}

    def fen(valeur, ancrage):
        offset, duree = valeur
        return {
            "ancrage": ancrages[ancrage],
            "offset_jours": offset,
            "duree_jours": duree,
        }

    fenetres: dict[str, dict] = {}
    if semis_int:
        fenetres["semis_interieur"] = fen(semis_int, anchor_si)
    if semis_dir:
        fenetres["semis_direct"] = fen(semis_dir, anchor_sd)
    if plantation:
        fenetres["plantation"] = fen(plantation, anchor_pl)
    if recolte:
        jour, duree = recolte
        fenetres["recolte"] = {
            "ancrage": "date_fixe",
            "date": jour,
            "duree_jours": duree,
        }

    repiquage, semis_recolte, plant_recolte, duree_recolte = cycle
    bloc_cycle: dict[str, int] = {"duree_recolte_jours": duree_recolte}
    if repiquage:
        bloc_cycle["jours_semis_a_repiquage"] = repiquage
    if semis_recolte:
        bloc_cycle["jours_semis_a_recolte"] = semis_recolte
    if plant_recolte:
        bloc_cycle["jours_plantation_a_recolte"] = plant_recolte

    fiche = {
        "id": cid,
        "nom": nom,
        "nom_scientifique": sci,
        "famille": famille,
        "categorie": cat,
        "emoji": emoji,
        "difficulte": diff,
        "exposition": expo,
        "arrosage": {"besoin": eau, "frequence_jours": freq, "notes": eau_notes},
        "sol": sol,
        "espacement_cm": espacement,
        "rusticite": {"gel": gel, "temp_min_c": tmin},
        "fenetres": fenetres,
        "cycle": bloc_cycle,
        "associations": {"aime": list(aime), "evite": list(evite)},
        "conseils": list(conseils),
    }
    if prof is not None:
        fiche["profondeur_semis_cm"] = prof
    if perenne:
        fiche["perenne"] = True
    CULTURES.append(fiche)
    return fiche


SOL_RICHE = "riche en humus, frais et bien drainé"
SOL_LEGER = "léger, meuble, sans cailloux"
SOL_ORDINAIRE = "ordinaire, bien drainé"

# =============================================================================
# Légumes-fruits
# =============================================================================

C("tomate", "Tomate", "Solanum lycopersicum", "Solanacées", "legume-fruit", "🍅",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=60, prof=0.5, diff=2, gel=False, tmin=5,
  semis_int=(-60, 30), plantation=(28, 30), cycle=(45, 110, 75, 90),
  eau_notes="Au pied, jamais sur le feuillage : c'est ainsi qu'arrive le mildiou.",
  aime=["basilic", "oeillet-inde", "carotte", "persil"],
  evite=["pomme-de-terre", "fenouil-bulbeux", "chou-cabus"],
  conseils=["Tailler les gourmands une fois par semaine",
            "Tuteurer dès la plantation, pas après",
            "Pailler dès juin pour stabiliser l'humidité"])

C("tomate-cerise", "Tomate cerise", "Solanum lycopersicum var. cerasiforme", "Solanacées",
  "legume-fruit", "🍅", eau="eleve", freq=2, sol=SOL_RICHE, espacement=50, prof=0.5,
  diff=1, gel=False, tmin=5, semis_int=(-60, 30), plantation=(28, 30), cycle=(45, 100, 70, 100),
  eau_notes="Plus tolérante que la grosse tomate, mais garder le sol frais.",
  aime=["basilic", "oeillet-inde"], evite=["pomme-de-terre", "fenouil-bulbeux"],
  conseils=["Se passe de taille si elle est bien tuteurée", "Idéale en pot sur un balcon"])

C("poivron", "Poivron", "Capsicum annuum", "Solanacées", "legume-fruit", "🫑",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=50, prof=0.5, diff=3, gel=False, tmin=12,
  semis_int=(-75, 30), plantation=(28, 25), cycle=(55, 130, 90, 70),
  eau_notes="Régulier et sans excès ; craint l'eau stagnante.",
  aime=["basilic", "carotte", "oignon-jaune"], evite=["haricot-nain", "fenouil-bulbeux"],
  conseils=["Chaleur indispensable : attendre un sol à 15 °C",
            "Pincer la première fleur pour renforcer le plant"])

C("piment", "Piment", "Capsicum annuum", "Solanacées", "legume-fruit", "🌶️",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=45, prof=0.5, diff=3, gel=False, tmin=10,
  semis_int=(-80, 30), plantation=(31, 25), cycle=(55, 135, 95, 80),
  eau_notes="Laisser sécher légèrement entre deux arrosages : le piment gagne en force.",
  aime=["basilic", "tomate"], evite=["fenouil-bulbeux"],
  conseils=["Semis très précoce indispensable sous nos latitudes",
            "Se cultive très bien en pot à rentrer l'hiver"])

C("aubergine", "Aubergine", "Solanum melongena", "Solanacées", "legume-fruit", "🍆",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=60, prof=0.5, diff=3, gel=False, tmin=12,
  semis_int=(-80, 30), plantation=(31, 25), cycle=(55, 140, 95, 70),
  eau_notes="Gourmande en eau dès la formation des fruits.",
  aime=["haricot-nain", "thym", "oeillet-inde"], evite=["pomme-de-terre"],
  conseils=["Tuteurer : les fruits sont lourds", "Limiter à 4-5 fruits par plant"])

C("courgette", "Courgette", "Cucurbita pepo", "Cucurbitacées", "legume-fruit", "🥒",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=100, prof=2, diff=1, gel=False, tmin=10,
  semis_int=(-30, 20), semis_dir=(28, 45), plantation=(28, 30), cycle=(28, 60, 50, 90),
  eau_notes="Beaucoup d'eau, au pied, sans mouiller les feuilles.",
  aime=["haricot-nain", "mais-doux", "capucine"], evite=["pomme-de-terre", "concombre"],
  conseils=["Récolter jeune et souvent : un plant freine dès qu'un fruit grossit",
            "Deux plants suffisent pour une famille"])

C("concombre", "Concombre", "Cucumis sativus", "Cucurbitacées", "legume-fruit", "🥒",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=80, prof=2, diff=2, gel=False, tmin=12,
  semis_int=(-30, 20), plantation=(28, 30), cycle=(28, 65, 55, 70),
  eau_notes="Un manque d'eau rend les fruits amers.",
  aime=["haricot-a-rames", "laitue", "aneth"], evite=["pomme-de-terre", "courgette"],
  conseils=["Palisser à la verticale : fruits plus droits, moins de maladies"])

C("cornichon", "Cornichon", "Cucumis sativus", "Cucurbitacées", "legume-fruit", "🥒",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=70, prof=2, diff=2, gel=False, tmin=12,
  semis_int=(-25, 20), semis_dir=(28, 40), cycle=(25, 60, 50, 60),
  eau_notes="Arrosage régulier, sinon les fruits avortent.",
  aime=["aneth", "haricot-nain"], evite=["pomme-de-terre"],
  conseils=["Cueillir tous les deux jours au plus fort de la production"])

C("courge-butternut", "Courge butternut", "Cucurbita moschata", "Cucurbitacées",
  "legume-fruit", "🎃", eau="moyen", freq=4, sol=SOL_RICHE, espacement=120, prof=3,
  diff=1, gel=False, tmin=10, semis_int=(-30, 20), plantation=(28, 30), cycle=(28, 120, 100, 45),
  eau_notes="Arrosages copieux mais espacés ; couper l'eau à l'approche de la récolte.",
  aime=["mais-doux", "haricot-a-rames", "capucine"], evite=["pomme-de-terre"],
  conseils=["Récolter quand le pédoncule est sec et liégeux",
            "Laisser ressuyer une semaine au soleil avant de stocker"])

C("potimarron", "Potimarron", "Cucurbita maxima", "Cucurbitacées", "legume-fruit", "🎃",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=120, prof=3, diff=1, gel=False, tmin=10,
  semis_int=(-30, 20), plantation=(28, 30), cycle=(28, 110, 95, 45),
  eau_notes="Comme la butternut : copieux et espacés.",
  aime=["mais-doux", "haricot-a-rames"], evite=["pomme-de-terre"],
  conseils=["Se conserve tout l'hiver dans une pièce fraîche et sèche"])

C("citrouille", "Citrouille", "Cucurbita maxima", "Cucurbitacées", "legume-fruit", "🎃",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=150, prof=3, diff=1, gel=False, tmin=10,
  semis_int=(-30, 20), plantation=(28, 30), cycle=(28, 115, 100, 45),
  eau_notes="Volume d'eau important, surtout pendant le grossissement.",
  aime=["mais-doux", "capucine"], evite=["pomme-de-terre"],
  conseils=["Glisser une planchette sous le fruit pour éviter qu'il pourrisse"])

C("melon", "Melon", "Cucumis melo", "Cucurbitacées", "legume-fruit", "🍈",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=100, prof=2, diff=3, gel=False, tmin=14,
  semis_int=(-45, 25), plantation=(33, 25), cycle=(35, 115, 90, 40),
  eau_notes="Réduire fortement l'eau dix jours avant la récolte : c'est ce qui fait le sucre.",
  aime=["mais-doux", "capucine"], evite=["concombre", "pomme-de-terre"],
  conseils=["Pailler avec une bâche ou de l'ardoise pour accumuler la chaleur",
            "Récolter quand le pédoncule se craquelle et que le parfum monte"])

C("pasteque", "Pastèque", "Citrullus lanatus", "Cucurbitacées", "legume-fruit", "🍉",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=140, prof=2, diff=3, gel=False, tmin=15,
  semis_int=(-45, 25), plantation=(35, 25), cycle=(35, 125, 100, 35),
  eau_notes="Comme le melon : couper l'eau en fin de cycle.",
  aime=["mais-doux"], evite=["pomme-de-terre"],
  conseils=["Exige un été chaud : réserver la place la plus abritée du jardin"])

C("mais-doux", "Maïs doux", "Zea mays", "Poacées", "legume-fruit", "🌽",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=40, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(28, 45), cycle=(None, 90, None, 25),
  eau_notes="Très assoiffé à la floraison : ne jamais laisser sécher à ce stade.",
  aime=["courgette", "haricot-a-rames", "potimarron"], evite=["betterave", "celeri-branche"],
  conseils=["Semer en bloc carré, jamais en ligne unique : la pollinisation en dépend",
            "Récolter quand les soies brunissent"])

C("physalis", "Physalis", "Physalis peruviana", "Solanacées", "legume-fruit", "🏮",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=80, prof=0.5, diff=2, gel=False, tmin=8,
  semis_int=(-60, 30), plantation=(28, 25), cycle=(45, 130, 95, 60),
  eau_notes="Supporte bien un léger stress hydrique.",
  aime=["tomate", "basilic"], evite=[],
  conseils=["Les fruits sont mûrs quand le calice est sec et qu'ils tombent seuls"])

# =============================================================================
# Légumes-gousses
# =============================================================================

C("haricot-nain", "Haricot vert nain", "Phaseolus vulgaris", "Fabacées", "legume-gousse", "🫘",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=10, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(28, 90), cycle=(None, 55, None, 40),
  eau_notes="Ne pas arroser avant la levée, puis régulièrement à la floraison.",
  aime=["carotte", "laitue", "courgette", "fraisier"], evite=["ail-blanc", "oignon-jaune", "echalote", "poireau"],
  conseils=["Semer tous les 15 jours jusqu'en juillet pour étaler la récolte",
            "Récolter tous les deux jours : un haricot oublié stoppe le plant"])

C("haricot-a-rames", "Haricot à rames", "Phaseolus vulgaris", "Fabacées", "legume-gousse", "🫘",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=15, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(33, 75), cycle=(None, 65, None, 60),
  eau_notes="Régulier dès la floraison.",
  aime=["mais-doux", "courgette", "laitue"], evite=["ail-blanc", "oignon-jaune", "poireau", "betterave"],
  conseils=["Installer les tuteurs avant de semer", "Produit plus longtemps que le nain"])

C("haricot-sec", "Haricot sec", "Phaseolus vulgaris", "Fabacées", "legume-gousse", "🫘",
  eau="faible", freq=6, sol=SOL_ORDINAIRE, espacement=12, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(33, 60), cycle=(None, 95, None, 25),
  eau_notes="Sobre ; arrêter l'arrosage dès que les gousses jaunissent.",
  aime=["carotte", "mais-doux"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Arracher les plants entiers et les faire sécher tête en bas"])

C("petit-pois", "Petit pois", "Pisum sativum", "Fabacées", "legume-gousse", "🫛",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=5, prof=3, diff=1, gel=True, tmin=-5,
  semis_dir=(-60, 60), cycle=(None, 90, None, 30),
  eau_notes="Craint la sécheresse à la floraison.",
  aime=["carotte", "radis", "navet", "laitue"], evite=["ail-blanc", "oignon-jaune", "echalote"],
  conseils=["Supporte le froid : un semis de février donne la première récolte",
            "Ramer dès 15 cm de hauteur"])

C("pois-mange-tout", "Pois mange-tout", "Pisum sativum", "Fabacées", "legume-gousse", "🫛",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=5, prof=3, diff=1, gel=True, tmin=-5,
  semis_dir=(-55, 60), cycle=(None, 80, None, 35),
  eau_notes="Comme le petit pois.",
  aime=["carotte", "radis", "laitue"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Récolter les gousses bien plates, avant que les grains ne se forment"])

C("feve", "Fève", "Vicia faba", "Fabacées", "legume-gousse", "🫘",
  eau="moyen", freq=5, sol=SOL_ORDINAIRE, espacement=20, prof=5, diff=1, gel=True, tmin=-8,
  semis_dir=(-15, 45), anchor_sd="premiere", cycle=(None, 180, None, 30),
  eau_notes="Peu exigeante, l'hiver s'en charge.",
  aime=["pomme-de-terre", "laitue", "epinard"], evite=["ail-blanc", "oignon-jaune", "betterave"],
  conseils=["Semée en novembre, elle passe l'hiver et devance les pucerons noirs",
            "Pincer les têtes dès l'apparition des premiers pucerons"])

C("pois-chiche", "Pois chiche", "Cicer arietinum", "Fabacées", "legume-gousse", "🫘",
  eau="faible", freq=8, sol="léger, calcaire, très drainé", espacement=15, prof=4,
  diff=2, gel=True, tmin=-4, semis_dir=(0, 30), cycle=(None, 120, None, 20),
  eau_notes="Résiste très bien au sec : ne pas arroser hors période de semis.",
  aime=["carotte", "sarriette"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Redoute l'excès d'eau plus que la sécheresse"])

# =============================================================================
# Légumes-racines et tubercules
# =============================================================================

C("carotte", "Carotte", "Daucus carota", "Apiacées", "legume-racine", "🥕",
  eau="moyen", freq=4, sol=SOL_LEGER, espacement=5, prof=0.5, diff=2, gel=True, tmin=-5,
  semis_dir=(-45, 150), cycle=(None, 100, None, 60),
  eau_notes="Humidité constante jusqu'à la levée, qui est lente (15 à 20 jours).",
  aime=["poireau", "oignon-jaune", "radis", "laitue", "petit-pois"], evite=["aneth", "betterave"],
  conseils=["Semer clair et éclaircir sans pitié : une carotte serrée reste un fil",
            "Le poireau voisin éloigne la mouche de la carotte"])

C("radis", "Radis", "Raphanus sativus", "Brassicacées", "legume-racine", "🥗",
  eau="eleve", freq=2, sol=SOL_LEGER, espacement=4, prof=1, diff=1, gel=True, tmin=-4,
  semis_dir=(-30, 150), cycle=(None, 25, None, 14),
  eau_notes="Jamais sec : un radis qui a soif devient piquant et creux.",
  aime=["carotte", "laitue", "petit-pois", "epinard"], evite=["concombre", "chou-cabus"],
  conseils=["Le plus rapide du potager : parfait pour débuter",
            "Semer une petite ligne tous les 10 jours plutôt qu'une grande d'un coup"])

C("radis-noir", "Radis noir d'hiver", "Raphanus sativus", "Brassicacées", "legume-racine", "🥗",
  eau="moyen", freq=3, sol=SOL_LEGER, espacement=15, prof=2, diff=1, gel=True, tmin=-8,
  semis_dir=(-90, 45), anchor_sd="premiere", cycle=(None, 70, None, 60),
  eau_notes="Régulier, sinon la racine se fend.",
  aime=["carotte", "laitue"], evite=["chou-cabus"],
  conseils=["Semé en août, il se récolte tout l'automne et se garde en cave"])

C("navet", "Navet", "Brassica rapa", "Brassicacées", "legume-racine", "🥗",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=12, prof=1, diff=1, gel=True, tmin=-6,
  semis_dir=(-20, 120), cycle=(None, 60, None, 30),
  eau_notes="Un arrosage irrégulier le rend fibreux.",
  aime=["petit-pois", "laitue"], evite=["chou-cabus", "radis"],
  conseils=["Récolter jeune, à la taille d'une balle de golf"])

C("betterave", "Betterave rouge", "Beta vulgaris", "Amaranthacées", "legume-racine", "🥗",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=12, prof=2, diff=1, gel=True, tmin=-4,
  semis_dir=(-15, 100), cycle=(None, 90, None, 45),
  eau_notes="Modéré et régulier.",
  aime=["laitue", "oignon-jaune", "chou-cabus"], evite=["haricot-a-rames", "mais-doux"],
  conseils=["Chaque graine donne plusieurs plants : éclaircir à 10 cm"])

C("panais", "Panais", "Pastinaca sativa", "Apiacées", "legume-racine", "🥕",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=15, prof=1, diff=2, gel=True, tmin=-15,
  semis_dir=(-30, 60), cycle=(None, 150, None, 90),
  eau_notes="Peu d'arrosage une fois installé, la racine va chercher loin.",
  aime=["radis", "laitue"], evite=["carotte", "celeri-rave"],
  conseils=["Le gel améliore son goût : le laisser en terre et récolter au besoin",
            "Graines à renouveler chaque année, elles perdent vite leur pouvoir germinatif"])

C("celeri-rave", "Céleri-rave", "Apium graveolens var. rapaceum", "Apiacées", "legume-racine", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=35, prof=0.2, diff=3, gel=True, tmin=-5,
  semis_int=(-75, 30), plantation=(20, 30), cycle=(60, None, 120, 45),
  eau_notes="Jamais à sec : c'est la culture la plus assoiffée du potager.",
  aime=["poireau", "tomate", "haricot-nain"], evite=["carotte", "panais", "persil"],
  conseils=["Dégager la base de la boule en fin d'été pour qu'elle grossisse"])

C("salsifis", "Salsifis", "Tragopogon porrifolius", "Astéracées", "legume-racine", "🥕",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=10, prof=2, diff=2, gel=True, tmin=-12,
  semis_dir=(-15, 60), cycle=(None, 160, None, 60),
  eau_notes="Sobre après la levée.",
  aime=["carotte", "oignon-jaune"], evite=[],
  conseils=["Se récolte de novembre à mars, au fur et à mesure des besoins"])

C("pomme-de-terre", "Pomme de terre", "Solanum tuberosum", "Solanacées", "legume-racine", "🥔",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=35, prof=10, diff=1, gel=False, tmin=2,
  plantation=(-30, 45), cycle=(None, None, 100, 45),
  eau_notes="Régulier à la floraison, moment où les tubercules se forment.",
  aime=["haricot-nain", "chou-cabus", "feve", "epinard"],
  evite=["tomate", "aubergine", "courgette", "potimarron"],
  conseils=["Butter dès que les plants atteignent 20 cm",
            "Ne jamais replanter au même endroit avant 4 ans"])

C("patate-douce", "Patate douce", "Ipomoea batatas", "Convolvulacées", "legume-racine", "🍠",
  eau="moyen", freq=4, sol=SOL_LEGER, espacement=80, diff=2, gel=False, tmin=12,
  plantation=(33, 30), cycle=(None, None, 130, 30),
  eau_notes="Supporte le sec une fois installée.",
  aime=["haricot-nain"], evite=["pomme-de-terre"],
  conseils=["Planter les boutures quand le sol atteint 15 °C",
            "Récolter avant les premières gelées, le feuillage est très sensible"])

C("rutabaga", "Rutabaga", "Brassica napobrassica", "Brassicacées", "legume-racine", "🥗",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=25, prof=2, diff=1, gel=True, tmin=-10,
  semis_dir=(30, 45), cycle=(None, 100, None, 60),
  eau_notes="Régulier, il n'aime pas les à-coups.",
  aime=["petit-pois", "laitue"], evite=["chou-cabus", "navet"],
  conseils=["Se garde en terre tout l'hiver sous un paillage"])

C("topinambour", "Topinambour", "Helianthus tuberosus", "Astéracées", "legume-racine", "🥔",
  eau="faible", freq=8, sol=SOL_ORDINAIRE, espacement=60, prof=10, diff=1, gel=True, tmin=-20,
  perenne=True, plantation=(-45, 45), recolte=("10-15", 150),
  cycle=(None, None, None, 150),
  eau_notes="Se débrouille seul, même en sol pauvre.",
  aime=[], evite=["pomme-de-terre"],
  conseils=["Très envahissant : lui réserver un coin dont il ne sortira pas",
            "Récolter au fur et à mesure, il ne se conserve pas hors de terre"])

C("crosne", "Crosne du Japon", "Stachys affinis", "Lamiacées", "legume-racine", "🥔",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=40, prof=8, diff=2, gel=True, tmin=-15,
  perenne=True, plantation=(-30, 30), recolte=("11-01", 120),
  cycle=(None, None, None, 120),
  eau_notes="Arroser en été pour grossir les tubercules.",
  aime=[], evite=[],
  conseils=["Récolter après les premières gelées et ne pas chercher à les conserver"])

C("raifort", "Raifort", "Armoracia rusticana", "Brassicacées", "legume-racine", "🌿",
  eau="faible", freq=7, sol=SOL_LEGER, espacement=50, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-45, 45), recolte=("10-15", 120), cycle=(None, None, None, 120),
  eau_notes="Rustique et sobre.",
  aime=["pomme-de-terre"], evite=[],
  conseils=["Aussi envahissant que le topinambour : le cantonner dans un bac"])

# =============================================================================
# Légumes-bulbes
# =============================================================================

C("oignon-jaune", "Oignon jaune", "Allium cepa", "Amaryllidacées", "legume-bulbe", "🧅",
  eau="faible", freq=7, sol=SOL_LEGER, espacement=12, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-60, 45), cycle=(None, 150, None, 30),
  eau_notes="Très peu d'eau : l'excès fait pourrir le bulbe.",
  aime=["carotte", "betterave", "laitue", "fraisier"], evite=["haricot-nain", "petit-pois", "feve"],
  conseils=["Coucher le feuillage en fin de cycle pour hâter la maturité",
            "Faire sécher au soleil une semaine avant de stocker"])

C("oignon-blanc", "Oignon blanc", "Allium cepa", "Amaryllidacées", "legume-bulbe", "🧅",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=10, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-60, 30), anchor_sd="premiere", cycle=(None, 210, None, 45),
  eau_notes="Comme le jaune : sobre.",
  aime=["carotte", "laitue"], evite=["haricot-nain", "petit-pois"],
  conseils=["Semé en août, il se consomme frais au printemps suivant"])

C("echalote", "Échalote", "Allium cepa var. aggregatum", "Amaryllidacées", "legume-bulbe", "🧅",
  eau="faible", freq=7, sol=SOL_LEGER, espacement=15, prof=3, diff=1, gel=True, tmin=-10,
  plantation=(-75, 60), cycle=(None, None, 120, 21),
  eau_notes="Presque aucun arrosage.",
  aime=["carotte", "betterave", "fraisier"], evite=["haricot-nain", "petit-pois", "feve"],
  conseils=["Dicton fiable : plantée en février, récoltée en juillet",
            "Ne pas enterrer la pointe, elle doit affleurer"])

C("ail-blanc", "Ail blanc", "Allium sativum", "Amaryllidacées", "legume-bulbe", "🧄",
  eau="faible", freq=10, sol=SOL_LEGER, espacement=12, prof=3, diff=1, gel=True, tmin=-15,
  plantation=(-30, 45), anchor_pl="premiere", cycle=(None, None, 240, 21),
  eau_notes="Ne jamais arroser : l'ail déteste l'humidité.",
  aime=["carotte", "betterave", "fraisier", "tomate"], evite=["haricot-nain", "petit-pois", "chou-cabus"],
  conseils=["Planté en octobre-novembre, il profite du froid pour se diviser",
            "Couper les fleurs pour que le bulbe grossisse"])

C("ail-rose", "Ail rose", "Allium sativum", "Amaryllidacées", "legume-bulbe", "🧄",
  eau="faible", freq=10, sol=SOL_LEGER, espacement=12, prof=3, diff=1, gel=True, tmin=-12,
  plantation=(-75, 40), cycle=(None, None, 150, 21),
  eau_notes="Aucun arrosage.",
  aime=["carotte", "fraisier", "tomate"], evite=["haricot-nain", "petit-pois"],
  conseils=["Se plante en février, contrairement à l'ail blanc"])

C("poireau", "Poireau", "Allium ampeloprasum", "Amaryllidacées", "legume-bulbe", "🥬",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=15, prof=1, diff=2, gel=True, tmin=-15,
  semis_int=(-75, 45), plantation=(30, 60), cycle=(70, None, 120, 120),
  eau_notes="Régulier, surtout après la plantation.",
  aime=["carotte", "celeri-rave", "fraisier", "tomate"], evite=["haricot-nain", "petit-pois"],
  conseils=["Raccourcir racines et feuilles de moitié avant de planter",
            "Butter progressivement pour allonger le blanc"])

C("ciboule", "Ciboule", "Allium fistulosum", "Amaryllidacées", "legume-bulbe", "🌿",
  eau="moyen", freq=5, sol=SOL_ORDINAIRE, espacement=10, prof=1, diff=1, gel=True, tmin=-12,
  semis_dir=(-30, 90), cycle=(None, 90, None, 150),
  eau_notes="Modéré.",
  aime=["carotte", "fraisier"], evite=["haricot-nain", "petit-pois"],
  conseils=["Se coupe comme de la ciboulette et repousse toute la saison"])

# =============================================================================
# Légumes-feuilles
# =============================================================================

C("laitue", "Laitue", "Lactuca sativa", "Astéracées", "legume-feuille", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=25, prof=0.5, diff=1, gel=True, tmin=-4,
  semis_int=(-60, 30), semis_dir=(-15, 150), cycle=(30, 60, 45, 30),
  eau_notes="Le matin, au pied : l'eau sur les feuilles au soleil les brûle.",
  aime=["carotte", "radis", "fraisier", "haricot-nain"], evite=["persil", "celeri-branche"],
  conseils=["Semer 6 à 8 pieds tous les 15 jours plutôt qu'une planche entière",
            "Ne pas enterrer la graine : elle a besoin de lumière pour germer"])

C("laitue-hiver", "Laitue d'hiver", "Lactuca sativa", "Astéracées", "legume-feuille", "🥬",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=25, prof=0.5, diff=2, gel=True, tmin=-10,
  semis_dir=(-75, 40), anchor_sd="premiere", cycle=(None, 150, None, 45),
  eau_notes="Modéré, l'hiver fournit l'essentiel.",
  aime=["mache", "epinard"], evite=["persil"],
  conseils=["Variétés 'Merveille d'hiver' ou 'Rougette' : les seules à passer le froid"])

C("mache", "Mâche", "Valerianella locusta", "Caprifoliacées", "legume-feuille", "🥬",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=10, prof=0.5, diff=1, gel=True, tmin=-15,
  semis_dir=(-75, 60), anchor_sd="premiere", cycle=(None, 90, None, 60),
  eau_notes="Garder frais jusqu'à la levée, puis l'oublier.",
  aime=["laitue-hiver", "epinard", "radis"], evite=[],
  conseils=["Semer sur sol tassé, surtout pas labouré : elle aime la terre ferme",
            "Plombez le semis en tapotant avec le dos du râteau"])

C("epinard", "Épinard", "Spinacia oleracea", "Amaranthacées", "legume-feuille", "🥬",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=15, prof=2, diff=1, gel=True, tmin=-12,
  semis_dir=(-75, 45), anchor_sd="premiere", cycle=(None, 60, None, 60),
  eau_notes="Généreux : la sécheresse le fait monter en graines aussitôt.",
  aime=["fraisier", "chou-cabus", "radis"], evite=["betterave"],
  conseils=["Culture d'automne et de printemps : l'été le fait monter",
            "Couper les feuilles extérieures, le pied continue de produire"])

C("blette", "Blette (poirée)", "Beta vulgaris var. cicla", "Amaranthacées", "legume-feuille", "🥬",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=35, prof=2, diff=1, gel=True, tmin=-8,
  semis_dir=(-15, 90), cycle=(None, 60, None, 150),
  eau_notes="Régulier ; très tolérante par ailleurs.",
  aime=["carotte", "laitue", "chou-cabus"], evite=["betterave", "epinard"],
  conseils=["Un seul semis nourrit du printemps aux gelées",
            "Récolter feuille à feuille, jamais le pied entier"])

C("roquette", "Roquette", "Eruca vesicaria", "Brassicacées", "legume-feuille", "🥬",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=10, prof=0.5, diff=1, gel=True, tmin=-6,
  semis_dir=(-30, 150), cycle=(None, 40, None, 30),
  eau_notes="Régulier, sinon elle devient très piquante et monte.",
  aime=["laitue", "carotte"], evite=["chou-cabus"],
  conseils=["Pousse si vite qu'un semis de printemps et un d'automne suffisent"])

C("chou-cabus", "Chou pommé", "Brassica oleracea var. capitata", "Brassicacées", "legume-feuille", "🥬",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=50, prof=1, diff=2, gel=True, tmin=-8,
  semis_int=(-45, 30), plantation=(30, 45), cycle=(40, None, 90, 45),
  eau_notes="Soutenu pendant la formation de la pomme.",
  aime=["betterave", "laitue", "epinard", "aneth"], evite=["tomate", "fraisier", "ail-blanc"],
  conseils=["Poser une collerette en carton au pied contre la mouche du chou",
            "Un filet anti-insectes règle le problème des piérides une fois pour toutes"])

C("chou-rouge", "Chou rouge", "Brassica oleracea var. capitata f. rubra", "Brassicacées",
  "legume-feuille", "🥬", eau="eleve", freq=3, sol=SOL_RICHE, espacement=50, prof=1,
  diff=2, gel=True, tmin=-8, semis_int=(-45, 30), plantation=(30, 45), cycle=(40, None, 100, 45),
  eau_notes="Comme le chou pommé.",
  aime=["betterave", "laitue", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Se conserve plusieurs mois en cave"])

C("chou-fleur", "Chou-fleur", "Brassica oleracea var. botrytis", "Brassicacées", "legume-feuille", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=60, prof=1, diff=3, gel=True, tmin=-6,
  semis_int=(-30, 45), plantation=(45, 45), cycle=(40, None, 100, 30),
  eau_notes="Le plus exigeant des choux : un coup de sec et la pomme avorte.",
  aime=["betterave", "celeri-branche", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Casser une feuille sur la pomme pour la garder blanche",
            "Récolter avant que les grains ne s'écartent"])

C("brocoli", "Brocoli", "Brassica oleracea var. italica", "Brassicacées", "legume-feuille", "🥦",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=50, prof=1, diff=2, gel=True, tmin=-8,
  semis_int=(-30, 45), plantation=(40, 45), cycle=(35, None, 85, 60),
  eau_notes="Régulier et généreux.",
  aime=["betterave", "laitue", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Couper la tête centrale incite les rejets latéraux à se développer"])

C("chou-bruxelles", "Chou de Bruxelles", "Brassica oleracea var. gemmifera", "Brassicacées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_RICHE, espacement=60, prof=1,
  diff=2, gel=True, tmin=-12, semis_int=(-30, 30), plantation=(45, 30), cycle=(40, None, 150, 90),
  eau_notes="Modéré ; le froid fait le reste.",
  aime=["betterave", "laitue"], evite=["tomate", "fraisier"],
  conseils=["Pincer la tête en septembre pour grossir les choux du bas",
            "Meilleur après une gelée"])

C("chou-kale", "Chou frisé (kale)", "Brassica oleracea var. sabellica", "Brassicacées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_RICHE, espacement=45, prof=1,
  diff=1, gel=True, tmin=-15, semis_int=(-15, 45), plantation=(45, 45), cycle=(35, None, 80, 180),
  eau_notes="Peu exigeant, très résistant.",
  aime=["betterave", "laitue", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Le plus facile et le plus rustique des choux : il produit tout l'hiver",
            "Cueillir les feuilles du bas, le pied continue de monter"])

C("chou-milan", "Chou de Milan", "Brassica oleracea var. sabauda", "Brassicacées",
  "legume-feuille", "🥬", eau="eleve", freq=3, sol=SOL_RICHE, espacement=55, prof=1,
  diff=2, gel=True, tmin=-12, semis_int=(-30, 40), plantation=(40, 50), cycle=(40, None, 110, 60),
  eau_notes="Soutenu à la formation de la pomme.",
  aime=["betterave", "laitue"], evite=["tomate", "fraisier"],
  conseils=["Variété d'hiver : se récolte de novembre à mars"])

C("chou-chinois", "Chou chinois (pak choï)", "Brassica rapa var. chinensis", "Brassicacées",
  "legume-feuille", "🥬", eau="eleve", freq=2, sol=SOL_RICHE, espacement=30, prof=1,
  diff=2, gel=True, tmin=-5, semis_dir=(-90, 40), anchor_sd="premiere", cycle=(None, 70, None, 30),
  eau_notes="Jamais sec, sinon il monte immédiatement.",
  aime=["laitue", "radis"], evite=["chou-cabus"],
  conseils=["Culture d'arrière-saison : semé en juillet-août, il ne monte pas"])

C("endive", "Endive (chicon)", "Cichorium intybus", "Astéracées", "legume-feuille", "🥬",
  eau="moyen", freq=4, sol=SOL_LEGER, espacement=12, prof=1, diff=3, gel=True, tmin=-8,
  semis_dir=(30, 30), cycle=(None, 160, None, 90),
  eau_notes="Régulier pendant la formation de la racine.",
  aime=["carotte", "oignon-jaune"], evite=[],
  conseils=["Deux temps : la racine au jardin l'été, le forçage à l'obscurité l'hiver",
            "Arracher les racines en novembre et les forcer en cave par lots"])

C("scarole", "Scarole", "Cichorium endivia", "Astéracées", "legume-feuille", "🥬",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=35, prof=0.5, diff=2, gel=True, tmin=-6,
  semis_dir=(45, 60), cycle=(None, 85, None, 45),
  eau_notes="Régulier ; au pied uniquement.",
  aime=["carotte", "radis"], evite=["persil"],
  conseils=["Lier les feuilles ou poser une assiette dessus pour blanchir le cœur"])

C("cresson-alenois", "Cresson alénois", "Lepidium sativum", "Brassicacées", "legume-feuille", "🌿",
  eau="eleve", freq=2, sol=SOL_ORDINAIRE, espacement=5, prof=0.5, diff=1, gel=True, tmin=-5,
  semis_dir=(-30, 150), cycle=(None, 30, None, 20),
  eau_notes="Toujours humide.",
  aime=["radis", "laitue"], evite=[],
  conseils=["Prêt en trois semaines : le plus rapide après le radis"])

C("pourpier", "Pourpier d'été", "Portulaca oleracea", "Portulacacées", "legume-feuille", "🌿",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=15, prof=0.5, diff=1, gel=False, tmin=8,
  semis_dir=(28, 90), cycle=(None, 50, None, 60),
  eau_notes="Supporte très bien la sécheresse : c'est une plante grasse.",
  aime=["carotte", "tomate"], evite=[],
  conseils=["Pousse là où rien ne pousse, en plein cagnard"])

C("tetragone", "Tétragone (épinard d'été)", "Tetragonia tetragonoides", "Aizoacées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=50, prof=2,
  diff=1, gel=False, tmin=8, semis_dir=(28, 45), cycle=(None, 60, None, 120),
  eau_notes="Modéré, bien plus tolérante que l'épinard.",
  aime=["tomate", "haricot-nain"], evite=[],
  conseils=["La solution à l'épinard qui monte en été : elle ne monte pas"])

C("celeri-branche", "Céleri branche", "Apium graveolens var. dulce", "Apiacées", "legume-feuille", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=30, prof=0.2, diff=3, gel=True, tmin=-4,
  semis_int=(-75, 30), plantation=(25, 30), cycle=(60, None, 100, 60),
  eau_notes="Jamais sec, jamais : c'est une plante de marais.",
  aime=["poireau", "chou-fleur", "tomate"], evite=["carotte", "persil", "mais-doux"],
  conseils=["Butter ou lier en fin de culture pour blanchir les côtes"])

C("fenouil-bulbeux", "Fenouil bulbeux", "Foeniculum vulgare var. azoricum", "Apiacées",
  "legume-feuille", "🥬", eau="moyen", freq=3, sol=SOL_RICHE, espacement=25, prof=1,
  diff=2, gel=True, tmin=-5, semis_dir=(30, 60), cycle=(None, 100, None, 30),
  eau_notes="Régulier, sinon il monte sans faire de bulbe.",
  aime=["laitue", "concombre"], evite=["tomate", "haricot-nain", "carotte", "coriandre"],
  conseils=["Semer après le solstice : semé trop tôt, il monte systématiquement",
            "Mauvais voisin pour presque tout : lui donner un coin à part"])

C("artichaut", "Artichaut", "Cynara scolymus", "Astéracées", "legume-feuille", "🌿",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=100, diff=2, gel=True, tmin=-8, perenne=True,
  plantation=(-30, 45), recolte=("06-01", 75), cycle=(None, None, None, 75),
  eau_notes="Généreux en été, surtout la première année.",
  aime=["feve", "laitue"], evite=[],
  conseils=["Pailler le pied l'hiver : c'est le gel qui tue les artichauts",
            "Productif 4 à 5 ans, puis diviser les œilletons"])

C("asperge", "Asperge", "Asparagus officinalis", "Asparagacées", "legume-feuille", "🌿",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=50, diff=3, gel=True, tmin=-15, perenne=True,
  plantation=(-60, 45), recolte=("04-15", 45), cycle=(None, None, None, 45),
  eau_notes="Modéré ; craint l'eau stagnante en hiver.",
  aime=["tomate", "persil"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Patience : aucune récolte les deux premières années, puis 15 ans de production",
            "Butter la griffe au printemps pour obtenir des asperges blanches"])

C("rhubarbe", "Rhubarbe", "Rheum rhabarbarum", "Polygonacées", "legume-feuille", "🌿",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=100, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 60), anchor_pl="premiere", recolte=("04-20", 75), cycle=(None, None, None, 75),
  eau_notes="Aime les sols frais ; arroser en été.",
  aime=[], evite=[],
  conseils=["Ne rien récolter la première année",
            "Tirer les pétioles, ne pas les couper ; les feuilles sont toxiques"])

C("cardon", "Cardon", "Cynara cardunculus", "Astéracées", "legume-feuille", "🌿",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=90, prof=2, diff=2, gel=True, tmin=-5,
  semis_dir=(30, 30), cycle=(None, 150, None, 60),
  eau_notes="Soutenu : c'est un gros buveur.",
  aime=["feve"], evite=[],
  conseils=["Lier et emballer les côtes un mois avant la récolte pour les blanchir"])

# =============================================================================
# Aromatiques
# =============================================================================

C("basilic", "Basilic", "Ocimum basilicum", "Lamiacées", "aromatique", "🌿",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=25, prof=0.5, diff=1, gel=False, tmin=12,
  semis_int=(-45, 30), plantation=(33, 40), cycle=(35, 70, 45, 120),
  eau_notes="Le matin, au pied ; jamais le soir, l'humidité nocturne le fait noircir.",
  aime=["tomate", "poivron", "courgette"], evite=["concombre"],
  conseils=["Pincer les fleurs dès qu'elles apparaissent : elles arrêtent la production de feuilles",
            "Craint le froid plus que tout : attendre la mi-mai dehors"])

C("persil", "Persil", "Petroselinum crispum", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=15, prof=1, diff=2, gel=True, tmin=-10,
  semis_dir=(-30, 120), cycle=(None, 80, None, 240),
  eau_notes="Régulier ; il jaunit s'il a soif.",
  aime=["tomate", "carotte", "radis"], evite=["laitue", "celeri-rave"],
  conseils=["Germination très lente (3 semaines) : tremper les graines une nuit",
            "Bisannuel : il monte en graines la deuxième année, mieux vaut le ressemer"])

C("coriandre", "Coriandre", "Coriandrum sativum", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=15, prof=1, diff=1, gel=True, tmin=-5,
  semis_dir=(-15, 120), cycle=(None, 50, None, 45),
  eau_notes="Régulier ; le sec la fait monter aussitôt.",
  aime=["tomate"], evite=["fenouil-bulbeux"],
  conseils=["Monte très vite en été : semer peu et souvent, ou à l'ombre légère"])

C("aneth", "Aneth", "Anethum graveolens", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=20, prof=1, diff=1, gel=True, tmin=-5,
  semis_dir=(-15, 120), cycle=(None, 60, None, 60),
  eau_notes="Modéré.",
  aime=["chou-cabus", "concombre", "cornichon", "laitue"], evite=["carotte", "fenouil-bulbeux"],
  conseils=["Se ressème seul année après année si on le laisse fleurir"])

C("cerfeuil", "Cerfeuil", "Anthriscus cerefolium", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=15, prof=0.5, diff=1, gel=True, tmin=-8,
  semis_dir=(-30, 120), cycle=(None, 50, None, 60),
  eau_notes="Garder frais ; il aime la mi-ombre.",
  aime=["radis", "laitue"], evite=[],
  conseils=["Préfère la mi-ombre : parfait au pied des plus grands"])

C("sarriette", "Sarriette", "Satureja hortensis", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=20, prof=0.5, diff=1, gel=False, tmin=5,
  semis_dir=(28, 45), cycle=(None, 60, None, 90),
  eau_notes="Sobre, comme toutes les méditerranéennes.",
  aime=["haricot-nain", "oignon-jaune", "pois-chiche"], evite=[],
  conseils=["Plantée près des haricots, elle éloigne les pucerons noirs"])

C("ciboulette", "Ciboulette", "Allium schoenoprasum", "Amaryllidacées", "aromatique", "🌿",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=20, prof=1, diff=1, gel=True, tmin=-20, perenne=True,
  semis_dir=(-30, 60), recolte=("04-01", 210), cycle=(None, None, None, 210),
  eau_notes="Régulier, elle aime la fraîcheur.",
  aime=["carotte", "tomate", "fraisier"], evite=["haricot-nain", "petit-pois"],
  conseils=["Couper à 3 cm du sol, elle repousse trois à quatre fois par saison",
            "Diviser la touffe tous les 3 ans"])

C("thym", "Thym", "Thymus vulgaris", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=10, sol="pauvre, caillouteux, très drainé", espacement=30,
  diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 60), recolte=("03-01", 270), cycle=(None, None, None, 270),
  eau_notes="Ne jamais arroser en pleine terre : il meurt d'excès d'eau, pas de sécheresse.",
  aime=["chou-cabus", "aubergine", "fraisier"], evite=[],
  conseils=["Le pire ennemi du thym est l'arrosoir",
            "Tailler après la floraison pour éviter qu'il se dégarnisse"])

C("romarin", "Romarin", "Salvia rosmarinus", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=12, sol="pauvre, caillouteux, très drainé", espacement=80,
  diff=1, gel=True, tmin=-12, perenne=True,
  plantation=(-15, 60), recolte=("01-01", 364), cycle=(None, None, None, 364),
  eau_notes="Aucun arrosage une fois installé.",
  aime=["chou-cabus", "carotte"], evite=[],
  conseils=["Se récolte toute l'année, même sous la neige",
            "Bouture très facilement : une branche dans un verre d'eau"])

C("sauge", "Sauge officinale", "Salvia officinalis", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=8, sol=SOL_LEGER, espacement=50, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 60), recolte=("04-01", 210), cycle=(None, None, None, 210),
  eau_notes="Sobre ; craint l'humidité hivernale.",
  aime=["chou-cabus", "carotte", "fraisier"], evite=["concombre"],
  conseils=["Rabattre d'un tiers au printemps pour la garder compacte"])

C("menthe", "Menthe", "Mentha spicata", "Lamiacées", "aromatique", "🌿",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=40, diff=1, gel=True, tmin=-18, perenne=True,
  plantation=(-30, 60), recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Aime avoir les pieds au frais, presque humides.",
  aime=["chou-cabus", "tomate"], evite=["persil", "camomille"],
  conseils=["À cultiver en pot, sans exception : en pleine terre elle colonise tout",
            "Rabattre au sol en fin d'été pour une repousse tendre"])

C("origan", "Origan", "Origanum vulgare", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=8, sol=SOL_LEGER, espacement=35, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 60), recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Sobre.",
  aime=["tomate", "poivron", "courgette"], evite=[],
  conseils=["Le plus parfumé juste avant la floraison : c'est le moment de le sécher"])

C("estragon", "Estragon", "Artemisia dracunculus", "Astéracées", "aromatique", "🌿",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=50, diff=2, gel=True, tmin=-10, perenne=True,
  plantation=(-15, 45), recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Modéré ; redoute l'humidité stagnante l'hiver.",
  aime=["tomate", "aubergine"], evite=[],
  conseils=["Protéger le pied l'hiver par un paillage sec",
            "Diviser tous les 3 ans, il s'épuise"])

C("laurier-sauce", "Laurier-sauce", "Laurus nobilis", "Lauracées", "aromatique", "🌿",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=150, diff=1, gel=True, tmin=-12, perenne=True,
  plantation=(-30, 90), anchor_pl="premiere", recolte=("01-01", 364), cycle=(None, None, None, 364),
  eau_notes="Aucun arrosage une fois établi.",
  aime=[], evite=[],
  conseils=["Devient un arbre : prévoir la place ou le tailler en boule",
            "Se cueille toute l'année"])

C("liveche", "Livèche (ache des montagnes)", "Levisticum officinale", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=80, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-30, 60), recolte=("04-15", 180), cycle=(None, None, None, 180),
  eau_notes="Aime la fraîcheur.",
  aime=[], evite=[],
  conseils=["Goût de céleri en plus puissant : quelques feuilles suffisent",
            "Monte à 2 m : à placer au fond du jardin"])

# =============================================================================
# Petits fruits
# =============================================================================

C("fraisier", "Fraisier", "Fragaria x ananassa", "Rosacées", "petit-fruit", "🍓",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=35, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-60, 60), anchor_pl="premiere", recolte=("05-15", 45), cycle=(None, None, None, 45),
  eau_notes="Régulier, au pied : l'eau sur les fruits les fait pourrir.",
  aime=["ail-blanc", "echalote", "oignon-jaune", "epinard", "ciboulette"], evite=["chou-cabus"],
  conseils=["Planter en septembre pour récolter dès le printemps suivant",
            "Pailler pour garder les fruits propres et hors du sol",
            "Remplacer les pieds tous les 3 ans, le rendement s'effondre après"])

C("fraisier-remontant", "Fraisier remontant", "Fragaria x ananassa", "Rosacées", "petit-fruit", "🍓",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=35, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-60, 60), anchor_pl="premiere", recolte=("06-01", 135), cycle=(None, None, None, 135),
  eau_notes="Comme le fraisier classique, mais sur une période bien plus longue.",
  aime=["ail-blanc", "echalote", "ciboulette"], evite=["chou-cabus"],
  conseils=["Produit par vagues de juin aux gelées", "Supprimer les stolons pour favoriser les fruits"])

C("framboisier", "Framboisier", "Rubus idaeus", "Rosacées", "petit-fruit", "🫐",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=50, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("06-20", 45), cycle=(None, None, None, 45),
  eau_notes="Aime les sols frais ; pailler plutôt qu'arroser beaucoup.",
  aime=["ail-blanc", "oeillet-inde"], evite=["pomme-de-terre"],
  conseils=["Palisser sur deux fils : sans cela c'est un roncier",
            "Non remontant : couper au sol les cannes qui ont fructifié"])

C("framboisier-remontant", "Framboisier remontant", "Rubus idaeus", "Rosacées", "petit-fruit", "🫐",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=50, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("08-15", 60), cycle=(None, None, None, 60),
  eau_notes="Comme le non remontant.",
  aime=["ail-blanc"], evite=["pomme-de-terre"],
  conseils=["Taille simple : tout rabattre au sol en février"])

C("groseillier", "Groseillier", "Ribes rubrum", "Grossulariacées", "petit-fruit", "🫐",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=120, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("06-25", 30), cycle=(None, None, None, 30),
  eau_notes="Modéré ; supporte la mi-ombre.",
  aime=["ciboulette"], evite=[],
  conseils=["Tolère très bien la mi-ombre : utile pour les coins ingrats",
            "Supprimer le bois de plus de 4 ans en hiver"])

C("cassissier", "Cassissier", "Ribes nigrum", "Grossulariacées", "petit-fruit", "🫐",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=130, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("07-01", 25), cycle=(None, None, None, 25),
  eau_notes="Aime la fraîcheur, plus exigeant que le groseillier.",
  aime=["ciboulette"], evite=[],
  conseils=["Fructifie sur le bois de l'année : tailler sévèrement les vieilles branches"])

C("murier", "Mûrier (ronce)", "Rubus fruticosus", "Rosacées", "petit-fruit", "🫐",
  eau="faible", freq=6, sol=SOL_ORDINAIRE, espacement=200, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("08-01", 45), cycle=(None, None, None, 45),
  eau_notes="Très sobre une fois installé.",
  aime=[], evite=[],
  conseils=["Choisir une variété sans épines, la cueillette change de nature",
            "Palisser sur un grillage et rabattre chaque hiver"])

C("myrtillier", "Myrtillier", "Vaccinium corymbosum", "Éricacées", "petit-fruit", "🫐",
  eau="eleve", freq=2, sol="acide (pH 4-5), terre de bruyère", espacement=120,
  diff=2, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("07-10", 40), cycle=(None, None, None, 40),
  eau_notes="Eau non calcaire impérative : eau de pluie si possible.",
  aime=[], evite=[],
  conseils=["Sol acide obligatoire : en pot avec de la terre de bruyère si le jardin est calcaire",
            "Planter deux variétés différentes pour une bonne pollinisation"])

C("vigne-table", "Vigne (raisin de table)", "Vitis vinifera", "Vitacées", "petit-fruit", "🍇",
  eau="faible", freq=10, sol="caillouteux, drainé, même pauvre", espacement=150,
  diff=2, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("09-01", 40), cycle=(None, None, None, 40),
  eau_notes="Ne pas arroser : la vigne cherche l'eau en profondeur et gagne en sucre au sec.",
  aime=[], evite=["chou-cabus"],
  conseils=["Taille d'hiver indispensable : 2 yeux par coursonne",
            "Plein sud contre un mur : c'est la chaleur restituée qui fait le raisin"])

C("kiwi", "Kiwi (actinidia)", "Actinidia deliciosa", "Actinidiacées", "petit-fruit", "🥝",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=400, diff=2, gel=True, tmin=-12, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("10-25", 30), cycle=(None, None, None, 30),
  eau_notes="Gros besoins en été ; le feuillage flétrit vite s'il manque d'eau.",
  aime=[], evite=[],
  conseils=["Un pied mâle pour cinq femelles, sauf variété autofertile",
            "Prévoir une pergola solide : il devient très lourd",
            "Récolter avant les gelées et laisser mûrir en cagette"])

# =============================================================================
# Arbres fruitiers
# =============================================================================

C("pommier", "Pommier", "Malus domestica", "Rosacées", "fruitier", "🍎",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-10", 40), cycle=(None, None, None, 40),
  eau_notes="Aucun arrosage une fois établi, sauf été de canicule les 3 premières années.",
  aime=["capucine", "ciboulette"], evite=[],
  conseils=["À la Sainte-Catherine (25 novembre), tout bois prend racine",
            "Deux variétés différentes pour la pollinisation",
            "Éclaircir les fruits en juin : moins de pommes, mais plus belles"])

C("poirier", "Poirier", "Pyrus communis", "Rosacées", "fruitier", "🍐",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=2, gel=True, tmin=-20, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-01", 35), cycle=(None, None, None, 35),
  eau_notes="Sobre une fois installé.",
  aime=["capucine"], evite=[],
  conseils=["Fleurit tôt : éviter les fonds de vallée gélifs",
            "Cueillir légèrement avant maturité et finir en fruitier"])

C("cerisier", "Cerisier", "Prunus avium", "Rosacées", "fruitier", "🍒",
  eau="faible", freq=12, sol=SOL_ORDINAIRE, espacement=500, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("06-05", 25), cycle=(None, None, None, 25),
  eau_notes="Ne pas arroser en période de fruits : les cerises éclatent.",
  aime=["ciboulette"], evite=[],
  conseils=["Tailler le moins possible, et seulement après la récolte : il gomme",
            "Un filet est la seule défense réaliste contre les oiseaux"])

C("prunier", "Prunier", "Prunus domestica", "Rosacées", "fruitier", "🫐",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=450, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("08-05", 30), cycle=(None, None, None, 30),
  eau_notes="Sobre.",
  aime=[], evite=[],
  conseils=["Le plus facile des fruitiers à noyau sous climat océanique",
            "Étayer les branches chargées, elles cassent"])

C("pecher", "Pêcher", "Prunus persica", "Rosacées", "fruitier", "🍑",
  eau="moyen", freq=6, sol=SOL_LEGER, espacement=400, diff=3, gel=True, tmin=-18, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("07-20", 30), cycle=(None, None, None, 30),
  eau_notes="Arroser en été, mais jamais le feuillage.",
  aime=["ail-blanc", "capucine"], evite=[],
  conseils=["La cloque est la difficulté principale : décoction de prêle dès le débourrement",
            "Planter de l'ail au pied, vieux remède de jardinier contre la cloque"])

C("abricotier", "Abricotier", "Prunus armeniaca", "Rosacées", "fruitier", "🍑",
  eau="faible", freq=10, sol=SOL_LEGER, espacement=450, diff=3, gel=True, tmin=-20, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("07-05", 20), cycle=(None, None, None, 20),
  eau_notes="Sobre ; redoute l'humidité.",
  aime=[], evite=[],
  conseils=["Floraison très précoce : une gelée de mars supprime la récolte",
            "Lui donner l'emplacement le plus abrité et le plus tardif à se réchauffer"])

C("figuier", "Figuier", "Ficus carica", "Moracées", "fruitier", "🫒",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("08-15", 45), cycle=(None, None, None, 45),
  eau_notes="Très sobre ; trop d'eau dilue le goût des figues.",
  aime=[], evite=[],
  conseils=["Se plaît contre un mur au sud, racines contenues",
            "Parfaitement adapté au climat de la Loire-Atlantique"])

C("noisetier", "Noisetier", "Corylus avellana", "Bétulacées", "fruitier", "🌰",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-15", 30), cycle=(None, None, None, 30),
  eau_notes="Aucun arrosage une fois installé.",
  aime=[], evite=[],
  conseils=["Deux variétés différentes pour la pollinisation",
            "Le balanin perce les noisettes : ramasser et détruire les fruits tombés"])

C("noyer", "Noyer", "Juglans regia", "Juglandacées", "fruitier", "🌰",
  eau="faible", freq=12, sol=SOL_RICHE, espacement=1000, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-25", 30), cycle=(None, None, None, 30),
  eau_notes="Aucun arrosage une fois établi.",
  aime=[], evite=["pomme-de-terre", "tomate"],
  conseils=["Rien ne pousse sous un noyer : la juglone inhibe les voisins",
            "Prévoir 10 m de dégagement, c'est un arbre de 20 m"])

# =============================================================================
# Fleurs compagnes — elles se sèment au potager et y jouent un rôle
# =============================================================================

C("oeillet-inde", "Œillet d'Inde", "Tagetes patula", "Astéracées", "fleur-compagne", "🌼",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=25, prof=0.5, diff=1, gel=False, tmin=5,
  semis_int=(-45, 30), semis_dir=(28, 60), cycle=(30, 70, 55, 150),
  eau_notes="Modéré ; très tolérant.",
  aime=["tomate", "aubergine", "framboisier", "pomme-de-terre"], evite=[],
  conseils=["Ses racines assainissent le sol des nématodes : le compagnon numéro un de la tomate",
            "Supprimer les fleurs fanées pour prolonger la floraison jusqu'aux gelées"])

C("capucine", "Capucine", "Tropaeolum majus", "Tropaeolacées", "fleur-compagne", "🌼",
  eau="faible", freq=5, sol="pauvre, sinon elle fait des feuilles et pas de fleurs",
  espacement=40, prof=2, diff=1, gel=False, tmin=5,
  semis_dir=(28, 60), cycle=(None, 55, None, 150),
  eau_notes="Sobre ; trop d'eau et d'engrais la font monter en feuilles.",
  aime=["courgette", "citrouille", "pommier", "poirier", "pecher", "haricot-a-rames"], evite=[],
  conseils=["Plante-piège à pucerons : ils s'y installent plutôt que sur vos légumes",
            "Fleurs et jeunes feuilles se mangent, goût poivré"])

C("bourrache", "Bourrache", "Borago officinalis", "Boraginacées", "fleur-compagne", "🌼",
  eau="faible", freq=6, sol=SOL_ORDINAIRE, espacement=40, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-15, 90), cycle=(None, 60, None, 120),
  eau_notes="Très sobre.",
  aime=["tomate", "courgette", "fraisier", "chou-cabus"], evite=[],
  conseils=["Aimant à bourdons : elle fait grimper la pollinisation des courgettes",
            "Se ressème seule indéfiniment"])

C("souci", "Souci (calendula)", "Calendula officinalis", "Astéracées", "fleur-compagne", "🌼",
  eau="faible", freq=5, sol=SOL_ORDINAIRE, espacement=30, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-30, 120), cycle=(None, 60, None, 180),
  eau_notes="Sobre.",
  aime=["tomate", "laitue", "chou-cabus", "pomme-de-terre"], evite=[],
  conseils=["Attire les syrphes, dont les larves dévorent les pucerons",
            "Fleurit du printemps aux gelées et se ressème seul"])

C("phacelie", "Phacélie", "Phacelia tanacetifolia", "Boraginacées", "fleur-compagne", "🌼",
  eau="faible", freq=7, sol=SOL_ORDINAIRE, espacement=15, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-30, 150), cycle=(None, 60, None, 60),
  eau_notes="Aucun arrosage.",
  aime=[], evite=[],
  conseils=["Engrais vert et pompe à pollinisateurs : à semer sur toute planche vide",
            "Faucher avant la montée en graines et laisser sur place"])

C("camomille", "Camomille romaine", "Chamaemelum nobile", "Astéracées", "aromatique", "🌼",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=30, prof=0.5, diff=1, gel=True, tmin=-15,
  perenne=True, plantation=(-15, 60), recolte=("06-01", 90), cycle=(None, None, None, 90),
  eau_notes="Sobre une fois installée.",
  aime=["chou-cabus", "oignon-jaune"], evite=["menthe"],
  conseils=["Se récolte en fleurs, à sécher à l'ombre"])

# =============================================================================
# Légumes-fruits — compléments
# =============================================================================

C("courge-spaghetti", "Courge spaghetti", "Cucurbita pepo", "Cucurbitacées",
  "legume-fruit", "🎃", eau="moyen", freq=4, sol=SOL_RICHE, espacement=110, prof=3,
  diff=1, gel=False, tmin=10, semis_int=(-30, 20), plantation=(28, 30),
  cycle=(28, 110, 95, 45),
  eau_notes="Copieux mais espacés ; couper l'eau à l'approche de la récolte.",
  aime=["mais-doux", "capucine", "bourrache"], evite=["pomme-de-terre"],
  conseils=["Sa chair se défait en filaments à la cuisson, d'où son nom",
            "Récolter quand l'écorce résiste à l'ongle, vers la mi-septembre"])

C("patisson", "Pâtisson", "Cucurbita pepo", "Cucurbitacées", "legume-fruit", "🎃",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=90, prof=3, diff=1, gel=False, tmin=10,
  semis_int=(-30, 20), semis_dir=(28, 40), plantation=(28, 30), cycle=(28, 70, 55, 75),
  eau_notes="Comme la courgette : beaucoup d'eau au pied.",
  aime=["mais-doux", "haricot-nain", "capucine"], evite=["pomme-de-terre"],
  conseils=["Se cueille jeune, à la taille d'une soucoupe",
            "Plus il grossit, plus il devient cotonneux"])

C("courge-muscade", "Courge muscade de Provence", "Cucurbita moschata",
  "Cucurbitacées", "legume-fruit", "🎃", eau="moyen", freq=4, sol=SOL_RICHE,
  espacement=150, prof=3, diff=2, gel=False, tmin=12, semis_int=(-30, 20),
  plantation=(31, 30), cycle=(28, 125, 110, 45),
  eau_notes="Gros buveur en été, à sevrer en fin de cycle.",
  aime=["mais-doux", "bourrache"], evite=["pomme-de-terre", "courgette"],
  conseils=["Exige une longue saison chaude : à réserver aux étés francs",
            "Un seul fruit nourrit une famille pendant des semaines"])

C("tomatille", "Tomatille", "Physalis philadelphica", "Solanacées", "legume-fruit", "🫒",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=80, prof=0.5, diff=2,
  gel=False, tmin=8, semis_int=(-60, 30), plantation=(28, 25), cycle=(45, 120, 80, 70),
  eau_notes="Supporte le sec mieux que la tomate.",
  aime=["basilic", "oeillet-inde", "capucine"], evite=["pomme-de-terre"],
  conseils=["Deux pieds minimum : elle ne se féconde pas elle-même",
            "Mûre quand le fruit fait éclater son calice"])

C("gombo", "Gombo (okra)", "Abelmoschus esculentus", "Malvacées", "legume-fruit", "🫑",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=50, prof=2, diff=3, gel=False, tmin=15,
  semis_int=(-45, 25), plantation=(38, 25), cycle=(40, 110, 70, 60),
  eau_notes="Régulier, mais il déteste les pieds mouillés.",
  aime=["basilic", "poivron"], evite=[],
  conseils=["Demande une vraie chaleur : serre ou mur plein sud sous climat océanique",
            "Cueillir les gousses à 7-8 cm, elles deviennent filandreuses ensuite"])

C("chayotte", "Chayotte (christophine)", "Sechium edule", "Cucurbitacées",
  "legume-fruit", "🥒", eau="eleve", freq=3, sol=SOL_RICHE, espacement=200,
  diff=3, gel=False, tmin=10, perenne=True, plantation=(33, 30),
  recolte=("09-20", 50), cycle=(None, None, None, 50),
  eau_notes="Très gourmande en eau pendant toute la végétation.",
  aime=[], evite=[],
  conseils=["Se plante en enterrant le fruit entier, germe vers le haut",
            "Prévoir une treille solide : une liane de 8 m en une saison",
            "Pailler lourdement la souche pour la faire repartir l'an prochain"])

# =============================================================================
# Légumes-racines — compléments
# =============================================================================

C("scorsonere", "Scorsonère", "Scorzonera hispanica", "Astéracées", "legume-racine", "🥕",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=10, prof=2, diff=2, gel=True, tmin=-15,
  semis_dir=(-15, 60), cycle=(None, 170, None, 90),
  eau_notes="Sobre une fois levée.",
  aime=["carotte", "oignon-jaune"], evite=[],
  conseils=["Racine noire, chair plus fine que le salsifis",
            "Se laisse en terre tout l'hiver et s'arrache au besoin"])

C("daikon", "Daikon (radis blanc)", "Raphanus sativus var. longipinnatus",
  "Brassicacées", "legume-racine", "🥗", eau="moyen", freq=3, sol=SOL_LEGER,
  espacement=20, prof=2, diff=1, gel=True, tmin=-5,
  semis_dir=(-80, 50), anchor_sd="premiere", cycle=(None, 70, None, 60),
  eau_notes="Régulier, sinon la racine devient piquante et creuse.",
  aime=["carotte", "laitue"], evite=["chou-cabus"],
  conseils=["Semé fin août, il se récolte d'octobre aux gelées",
            "Sa racine descend profond : ameublir sur 30 cm"])

C("chervis", "Chervis", "Sium sisarum", "Apiacées", "legume-racine", "🥕",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=30, prof=1, diff=2, gel=True,
  tmin=-20, perenne=True, plantation=(-30, 45), recolte=("10-15", 120),
  cycle=(None, None, None, 120),
  eau_notes="Aime la fraîcheur, comme toutes les apiacées.",
  aime=["carotte"], evite=["panais", "celeri-rave"],
  conseils=["Légume oublié, très sucré, à la mode avant la pomme de terre",
            "Se multiplie par éclat de souche au printemps"])

C("persil-tubereux", "Persil tubéreux", "Petroselinum crispum var. tuberosum",
  "Apiacées", "legume-racine", "🥕", eau="moyen", freq=4, sol=SOL_LEGER,
  espacement=15, prof=1, diff=2, gel=True, tmin=-15,
  semis_dir=(-30, 60), cycle=(None, 160, None, 90),
  eau_notes="Régulier au départ, la levée est lente.",
  aime=["radis", "laitue"], evite=["carotte", "celeri-rave"],
  conseils=["Racine au goût de persil et de panais, feuillage utilisable aussi",
            "Comme le panais, le gel l'adoucit"])

C("oca-perou", "Oca du Pérou", "Oxalis tuberosa", "Oxalidacées", "legume-racine", "🥔",
  eau="moyen", freq=4, sol=SOL_LEGER, espacement=40, prof=6, diff=2, gel=False, tmin=2,
  plantation=(28, 40), cycle=(None, None, 210, 45),
  eau_notes="Modéré ; elle grossit surtout à l'automne.",
  aime=["pomme-de-terre"], evite=[],
  conseils=["Les tubercules ne se forment qu'aux jours courts, en octobre",
            "Récolter après le premier gel du feuillage, pas avant"])

# =============================================================================
# Légumes-gousses — compléments
# =============================================================================

C("haricot-espagne", "Haricot d'Espagne", "Phaseolus coccineus", "Fabacées",
  "legume-gousse", "🫘", eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=20,
  prof=4, diff=1, gel=False, tmin=8, semis_dir=(28, 60), cycle=(None, 80, None, 70),
  eau_notes="Régulier à la floraison.",
  aime=["mais-doux", "courgette"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Fleurs rouges très décoratives, et comestibles",
            "Plus rustique que le haricot vert : il supporte les étés frais"])

C("lentille", "Lentille", "Lens culinaris", "Fabacées", "legume-gousse", "🫘",
  eau="faible", freq=10, sol="pauvre, caillouteux, très drainé", espacement=5,
  prof=3, diff=2, gel=True, tmin=-6, semis_dir=(-45, 40), cycle=(None, 110, None, 20),
  eau_notes="Ne jamais arroser : l'excès d'eau la fait verser.",
  aime=["sarriette"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Réussit en sol pauvre, là où rien d'autre ne donne",
            "Arracher les plants entiers quand les gousses du bas brunissent"])

C("edamame", "Soja edamame", "Glycine max", "Fabacées", "legume-gousse", "🫛",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=15, prof=3, diff=2,
  gel=False, tmin=10, semis_dir=(33, 45), cycle=(None, 95, None, 25),
  eau_notes="Soutenu à la formation des gousses.",
  aime=["mais-doux", "concombre"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Se récolte vert, quand les gousses sont pleines mais encore tendres",
            "Blanchir 5 minutes dans l'eau salée, puis déguster à la main"])

# =============================================================================
# Légumes-bulbes — compléments
# =============================================================================

C("oignon-rouge", "Oignon rouge", "Allium cepa", "Amaryllidacées", "legume-bulbe", "🧅",
  eau="faible", freq=7, sol=SOL_LEGER, espacement=12, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-60, 45), cycle=(None, 150, None, 30),
  eau_notes="Très peu d'eau, comme tous les oignons.",
  aime=["carotte", "betterave", "fraisier"], evite=["haricot-nain", "petit-pois"],
  conseils=["Se conserve moins longtemps que le jaune : à consommer en premier"])

C("ail-ours", "Ail des ours", "Allium ursinum", "Amaryllidacées", "aromatique", "🌿",
  expo="ombre", eau="moyen", freq=5, sol=SOL_RICHE, espacement=20, diff=1,
  gel=True, tmin=-20, perenne=True, plantation=(-15, 60), anchor_pl="premiere",
  recolte=("03-15", 60), cycle=(None, None, None, 60),
  eau_notes="Aime les sols frais et ombragés de sous-bois.",
  aime=[], evite=[],
  conseils=["La seule allium qui préfère l'ombre : idéale sous un arbre",
            "Se récolte en feuilles avant la floraison, de mars à mai",
            "Ne jamais le confondre avec le muguet : froisser et sentir l'ail"])

C("oignon-rocambole", "Oignon rocambole", "Allium × proliferum", "Amaryllidacées",
  "legume-bulbe", "🧅", eau="faible", freq=8, sol=SOL_ORDINAIRE, espacement=25,
  prof=3, diff=1, gel=True, tmin=-20, perenne=True, plantation=(-30, 60),
  anchor_pl="premiere", recolte=("07-01", 60), cycle=(None, None, None, 60),
  eau_notes="Rustique et sobre.",
  aime=["carotte", "fraisier"], evite=["haricot-nain", "petit-pois"],
  conseils=["Il produit ses bulbilles en haut de la tige, qui se replantent seules",
            "Une fois installé, il revient indéfiniment sans qu'on s'en occupe"])

# =============================================================================
# Légumes-feuilles — compléments
# =============================================================================

C("chou-rave", "Chou-rave", "Brassica oleracea var. gongylodes", "Brassicacées",
  "legume-feuille", "🥬", eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=25,
  prof=1, diff=1, gel=True, tmin=-6, semis_dir=(-15, 120), cycle=(None, 70, None, 30),
  eau_notes="Régulier : un à-coup le rend ligneux.",
  aime=["betterave", "laitue", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Récolter à la taille d'une balle de tennis, pas plus gros",
            "La boule pousse au-dessus du sol : ne jamais la butter"])

C("chicoree-frisee", "Chicorée frisée", "Cichorium endivia var. crispum",
  "Astéracées", "legume-feuille", "🥬", eau="moyen", freq=3, sol=SOL_RICHE,
  espacement=30, prof=0.5, diff=2, gel=True, tmin=-5,
  semis_dir=(40, 60), cycle=(None, 80, None, 45),
  eau_notes="Au pied uniquement : le cœur mouillé pourrit.",
  aime=["carotte", "radis"], evite=["persil"],
  conseils=["Lier les feuilles deux semaines avant pour blanchir le cœur"])

C("pain-de-sucre", "Chicorée pain de sucre", "Cichorium intybus", "Astéracées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=30,
  prof=1, diff=1, gel=True, tmin=-10, semis_dir=(90, 45), cycle=(None, 100, None, 75),
  eau_notes="Modéré.",
  aime=["carotte", "poireau"], evite=[],
  conseils=["La salade d'hiver la plus facile : semée en juillet, récoltée en décembre",
            "Son cœur serré se conserve des semaines en cave"])

C("trevise", "Trévise (radicchio)", "Cichorium intybus var. foliosum", "Astéracées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=30,
  prof=1, diff=2, gel=True, tmin=-8, semis_dir=(90, 40), cycle=(None, 100, None, 60),
  eau_notes="Modéré.",
  aime=["carotte", "poireau"], evite=[],
  conseils=["C'est le froid qui fait rougir les feuilles : ne pas récolter trop tôt"])

C("oseille", "Oseille", "Rumex acetosa", "Polygonacées", "legume-feuille", "🌿",
  expo="mi-ombre", eau="moyen", freq=4, sol=SOL_RICHE, espacement=30, prof=1,
  diff=1, gel=True, tmin=-20, perenne=True, semis_dir=(-30, 90),
  recolte=("04-01", 180), cycle=(None, None, None, 180),
  eau_notes="Aime les sols frais ; elle monte si elle a soif.",
  aime=[], evite=[],
  conseils=["Une touffe suffit pour des années",
            "Couper les hampes florales dès qu'elles montent, pour garder les feuilles tendres"])

C("arroche", "Arroche", "Atriplex hortensis", "Amaranthacées", "legume-feuille", "🥬",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=40, prof=1, diff=1,
  gel=True, tmin=-5, semis_dir=(-15, 90), cycle=(None, 55, None, 90),
  eau_notes="Modéré ; bien plus tolérante que l'épinard.",
  aime=["laitue", "radis"], evite=[],
  conseils=["L'épinard des étés secs : elle monte beaucoup moins vite",
            "Se ressème seule d'année en année"])

C("claytone", "Claytone de Cuba", "Claytonia perfoliata", "Montiacées",
  "legume-feuille", "🥬", expo="mi-ombre", eau="moyen", freq=4, sol=SOL_ORDINAIRE,
  espacement=15, prof=0.5, diff=1, gel=True, tmin=-15,
  semis_dir=(-75, 45), anchor_sd="premiere", cycle=(None, 60, None, 90),
  eau_notes="Garder frais ; elle apprécie la mi-ombre.",
  aime=["mache", "epinard"], evite=[],
  conseils=["Salade d'hiver increvable, elle pousse sous la neige",
            "Se ressème toute seule une fois installée"])

C("cresson-fontaine", "Cresson de fontaine", "Nasturtium officinale",
  "Brassicacées", "legume-feuille", "🌿", expo="mi-ombre", eau="eleve", freq=1,
  sol="toujours détrempé, au bord de l'eau", espacement=20, prof=0.5, diff=3,
  gel=True, tmin=-8, perenne=True, semis_dir=(-15, 90), recolte=("04-01", 210),
  cycle=(None, None, None, 210),
  eau_notes="Les pieds littéralement dans l'eau : bac, mare ou ruisseau.",
  aime=[], evite=[],
  conseils=["Impossible en pleine terre ordinaire : il lui faut l'eau courante ou un bac",
            "Ne jamais récolter de cresson sauvage : risque de douve du foie"])

C("mizuna", "Mizuna (moutarde japonaise)", "Brassica rapa var. nipposinica",
  "Brassicacées", "legume-feuille", "🥬", eau="moyen", freq=3, sol=SOL_ORDINAIRE,
  espacement=20, prof=0.5, diff=1, gel=True, tmin=-10,
  semis_dir=(-75, 90), anchor_sd="premiere", cycle=(None, 45, None, 90),
  eau_notes="Régulier ; le sec la rend très piquante.",
  aime=["laitue", "mache"], evite=["chou-cabus"],
  conseils=["Se coupe et repousse trois ou quatre fois",
            "Résiste au froid bien mieux que la roquette"])

C("celeri-couper", "Céleri à couper", "Apium graveolens var. secalinum",
  "Apiacées", "legume-feuille", "🌿", eau="eleve", freq=3, sol=SOL_RICHE,
  espacement=20, prof=0.2, diff=1, gel=True, tmin=-10,
  semis_dir=(-15, 90), cycle=(None, 90, None, 180),
  eau_notes="Jamais sec, comme tous les céleris.",
  aime=["poireau", "tomate", "chou-cabus"], evite=["carotte", "persil"],
  conseils=["Bien plus facile que le céleri branche, et aussi parfumé",
            "Se coupe au fur et à mesure pendant des mois"])

C("chou-daubenton", "Chou Daubenton", "Brassica oleracea var. ramosa",
  "Brassicacées", "legume-feuille", "🥬", eau="moyen", freq=5, sol=SOL_ORDINAIRE,
  espacement=100, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-30, 90), recolte=("01-01", 364), cycle=(None, None, None, 364),
  eau_notes="Sobre une fois installé.",
  aime=["betterave", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Un chou vivace qui donne des feuilles toute l'année, pendant 5 à 6 ans",
            "Se bouture en plantant simplement un rameau en terre",
            "Le meilleur rapport effort/récolte du potager"])

# =============================================================================
# Aromatiques — compléments
# =============================================================================

C("melisse", "Mélisse citronnelle", "Melissa officinalis", "Lamiacées", "aromatique", "🌿",
  expo="mi-ombre", eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=40, diff=1,
  gel=True, tmin=-20, perenne=True, plantation=(-30, 60), recolte=("05-01", 150),
  cycle=(None, None, None, 150),
  eau_notes="Aime la fraîcheur et la mi-ombre.",
  aime=["tomate", "chou-cabus"], evite=[],
  conseils=["Envahissante par semis spontané : couper les fleurs avant qu'elles montent",
            "Rabattre en juillet pour une repousse tendre"])

C("hysope", "Hysope", "Hyssopus officinalis", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=8, sol=SOL_LEGER, espacement=40, diff=1, gel=True, tmin=-15,
  perenne=True, plantation=(-15, 60), recolte=("06-01", 120),
  cycle=(None, None, None, 120),
  eau_notes="Sobre : une méditerranéenne de plus.",
  aime=["chou-cabus", "vigne-table"], evite=["radis"],
  conseils=["Ses fleurs bleues attirent les abeilles tout l'été",
            "Plantée près des choux, elle détourne la piéride"])

C("marjolaine", "Marjolaine", "Origanum majorana", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=25, prof=0.5, diff=1,
  gel=False, tmin=3, semis_int=(-45, 30), plantation=(28, 40), cycle=(35, 90, 60, 120),
  eau_notes="Sobre.",
  aime=["tomate", "courgette"], evite=[],
  conseils=["Plus douce et plus fine que l'origan, mais gélive : à rentrer ou ressemer",
            "Se cultive très bien en pot"])

C("verveine-citronnelle", "Verveine citronnelle", "Aloysia citrodora", "Verbénacées",
  "aromatique", "🌿", eau="moyen", freq=5, sol=SOL_LEGER, espacement=100, diff=2,
  gel=True, tmin=-8, perenne=True, plantation=(0, 60), recolte=("06-01", 120),
  cycle=(None, None, None, 120),
  eau_notes="Modéré ; elle craint surtout l'humidité hivernale.",
  aime=[], evite=[],
  conseils=["Pailler le pied généreusement l'hiver, elle gèle facilement",
            "Elle perd toutes ses feuilles l'hiver et repart tard : ne pas l'arracher trop vite"])

C("lavande", "Lavande", "Lavandula angustifolia", "Lamiacées", "aromatique", "💜",
  eau="faible", freq=12, sol="pauvre, caillouteux, très drainé", espacement=60,
  diff=1, gel=True, tmin=-15, perenne=True, plantation=(-15, 60),
  recolte=("06-20", 45), cycle=(None, None, None, 45),
  eau_notes="Aucun arrosage : elle meurt d'excès d'eau, jamais de sécheresse.",
  aime=["chou-cabus", "carotte"], evite=[],
  conseils=["Tailler en boule après la floraison, sans jamais couper dans le vieux bois",
            "Une bordure de lavande éloigne les pucerons et nourrit les abeilles"])

C("fenouil-aromatique", "Fenouil aromatique", "Foeniculum vulgare", "Apiacées",
  "aromatique", "🌿", eau="faible", freq=7, sol=SOL_ORDINAIRE, espacement=60,
  prof=1, diff=1, gel=True, tmin=-12, perenne=True, semis_dir=(-15, 90),
  recolte=("06-01", 150), cycle=(None, None, None, 150),
  eau_notes="Très sobre une fois installé.",
  aime=["concombre"], evite=["tomate", "haricot-nain", "carotte", "coriandre"],
  conseils=["Mauvais voisin notoire : lui réserver un coin à l'écart",
            "Ses ombelles jaunes attirent quantité d'insectes auxiliaires"])

C("shiso", "Shiso (périlla)", "Perilla frutescens", "Lamiacées", "aromatique", "🌿",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=35, prof=0.5, diff=1,
  gel=False, tmin=8, semis_int=(-45, 30), plantation=(28, 40), cycle=(35, 85, 55, 120),
  eau_notes="Régulier ; il flétrit vite au sec.",
  aime=["tomate", "concombre"], evite=[],
  conseils=["Goût entre la menthe et le cumin : la feuille des sushis",
            "Se ressème seul si on le laisse fleurir"])

C("angelique", "Angélique", "Angelica archangelica", "Apiacées", "aromatique", "🌿",
  expo="mi-ombre", eau="eleve", freq=3, sol=SOL_RICHE, espacement=100, prof=0.5,
  diff=2, gel=True, tmin=-20, perenne=True, semis_dir=(-60, 45), anchor_sd="premiere",
  recolte=("05-01", 90), cycle=(None, None, None, 90),
  eau_notes="Aime les sols humides et frais, au bord de l'eau si possible.",
  aime=[], evite=[],
  conseils=["Bisannuelle : elle fleurit et meurt la deuxième année, mais se ressème",
            "Monte à 2 m : à placer au fond, elle ferait de l'ombre à tout"])

# =============================================================================
# Petits fruits — compléments
# =============================================================================

C("groseillier-maquereau", "Groseillier à maquereau", "Ribes uva-crispa",
  "Grossulariacées", "petit-fruit", "🫐", expo="mi-ombre", eau="moyen", freq=4,
  sol=SOL_RICHE, espacement=120, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("06-20", 35),
  cycle=(None, None, None, 35),
  eau_notes="Modéré ; il supporte bien la mi-ombre.",
  aime=["ciboulette"], evite=[],
  conseils=["Épineux : tailler en gobelet pour pouvoir cueillir",
            "Se récolte vert pour les tartes, mûr pour le frais"])

C("sureau-noir", "Sureau noir", "Sambucus nigra", "Viburnacées", "petit-fruit", "🫐",
  eau="faible", freq=8, sol=SOL_RICHE, espacement=300, diff=1, gel=True, tmin=-25,
  perenne=True, plantation=(-15, 90), anchor_pl="premiere", recolte=("08-20", 30),
  cycle=(None, None, None, 30),
  eau_notes="Aucun arrosage une fois établi.",
  aime=[], evite=[],
  conseils=["Deux récoltes : les fleurs en juin pour le sirop, les baies en août",
            "Les baies crues sont indigestes : toujours les cuire",
            "Pousse vite et partout, y compris en haie"])

C("camerisier", "Camerisier (baie de mai)", "Lonicera caerulea", "Caprifoliacées",
  "petit-fruit", "🫐", expo="mi-ombre", eau="moyen", freq=4, sol=SOL_RICHE,
  espacement=150, diff=1, gel=True, tmin=-40, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("05-20", 25),
  cycle=(None, None, None, 25),
  eau_notes="Aime la fraîcheur, redoute la sécheresse estivale.",
  aime=[], evite=[],
  conseils=["Le tout premier fruit de l'année, avant même les fraises",
            "Deux variétés différentes sont indispensables pour fructifier"])

C("argousier", "Argousier", "Hippophae rhamnoides", "Éléagnacées", "petit-fruit", "🫐",
  eau="faible", freq=12, sol="pauvre, sableux, très drainé", espacement=250,
  diff=2, gel=True, tmin=-30, perenne=True, plantation=(-15, 90),
  anchor_pl="premiere", recolte=("09-10", 40), cycle=(None, None, None, 40),
  eau_notes="Aucun arrosage : il pousse dans les dunes.",
  aime=[], evite=[],
  conseils=["Un pied mâle pour cinq femelles, sans quoi aucun fruit",
            "Très épineux : cueillir en coupant les rameaux entiers",
            "Drageonne beaucoup : poser une barrière anti-rhizome"])

C("goji", "Goji (lyciet)", "Lycium barbarum", "Solanacées", "petit-fruit", "🫐",
  eau="faible", freq=8, sol=SOL_LEGER, espacement=180, diff=1, gel=True, tmin=-25,
  perenne=True, plantation=(-15, 90), anchor_pl="premiere", recolte=("08-01", 75),
  cycle=(None, None, None, 75),
  eau_notes="Très sobre, il préfère le sec.",
  aime=[], evite=["pomme-de-terre", "tomate"],
  conseils=["Palisser : laissé libre, il devient un buisson retombant ingérable",
            "Ne fructifie vraiment qu'à partir de la troisième année"])

# =============================================================================
# Arbres fruitiers — compléments
# =============================================================================

C("cognassier", "Cognassier", "Cydonia oblonga", "Rosacées", "fruitier", "🍐",
  eau="faible", freq=10, sol=SOL_RICHE, espacement=400, diff=1, gel=True, tmin=-20,
  perenne=True, plantation=(15, 75), anchor_pl="premiere", recolte=("10-05", 30),
  cycle=(None, None, None, 30),
  eau_notes="Aime les sols frais, mais ne demande aucun arrosage une fois pris.",
  aime=["capucine"], evite=[],
  conseils=["Autofertile : un seul arbre suffit",
            "Cueillir quand le duvet s'efface et que le parfum embaume"])

C("neflier", "Néflier", "Mespilus germanica", "Rosacées", "fruitier", "🍐",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=350, diff=1, gel=True,
  tmin=-25, perenne=True, plantation=(15, 75), anchor_pl="premiere",
  recolte=("11-05", 30), cycle=(None, None, None, 30),
  eau_notes="Aucun arrosage une fois établi.",
  aime=[], evite=[],
  conseils=["Les nèfles ne se mangent que blettes, après les premières gelées",
            "Petit arbre très rustique, et un des derniers fruits de l'année"])

C("kaki", "Kaki (plaqueminier)", "Diospyros kaki", "Ébénacées", "fruitier", "🍊",
  eau="moyen", freq=8, sol=SOL_RICHE, espacement=450, diff=2, gel=True, tmin=-15,
  perenne=True, plantation=(15, 75), anchor_pl="premiere", recolte=("10-25", 35),
  cycle=(None, None, None, 35),
  eau_notes="Arroser les trois premières années, puis plus rien.",
  aime=[], evite=[],
  conseils=["Se récolte après la chute des feuilles, quand le fruit est translucide",
            "Choisir une variété non astringente si l'on veut croquer le fruit ferme"])

C("chataignier", "Châtaignier", "Castanea sativa", "Fagacées", "fruitier", "🌰",
  eau="faible", freq=12, sol="acide, drainé, sans calcaire", espacement=1000,
  diff=1, gel=True, tmin=-25, perenne=True, plantation=(15, 75),
  anchor_pl="premiere", recolte=("10-01", 35), cycle=(None, None, None, 35),
  eau_notes="Aucun arrosage une fois installé.",
  aime=[], evite=[],
  conseils=["Refuse absolument le calcaire : inutile d'insister en sol crayeux",
            "Deux variétés pour la pollinisation, et vingt mètres de dégagement"])

C("amandier", "Amandier", "Prunus dulcis", "Rosacées", "fruitier", "🌰",
  eau="faible", freq=12, sol=SOL_LEGER, espacement=450, diff=3, gel=True, tmin=-18,
  perenne=True, plantation=(15, 75), anchor_pl="premiere", recolte=("09-01", 30),
  cycle=(None, None, None, 30),
  eau_notes="Très sobre ; il redoute l'humidité bien plus que la sécheresse.",
  aime=[], evite=[],
  conseils=["Floraison en février : une gelée tardive suffit à supprimer la récolte",
            "Sous climat océanique, la cloque est son ennemie principale"])

C("nashi", "Nashi (poirier asiatique)", "Pyrus pyrifolia", "Rosacées", "fruitier", "🍐",
  eau="moyen", freq=8, sol=SOL_RICHE, espacement=400, diff=2, gel=True, tmin=-20,
  perenne=True, plantation=(15, 75), anchor_pl="premiere", recolte=("09-05", 30),
  cycle=(None, None, None, 30),
  eau_notes="Un peu plus exigeant en eau que le poirier européen.",
  aime=["capucine"], evite=[],
  conseils=["Croquant comme une pomme, juteux comme une poire",
            "Éclaircir sévèrement : il met trop de fruits et les fait tous petits"])

# =============================================================================
# Fleurs compagnes et engrais verts — compléments
# =============================================================================

C("consoude", "Consoude officinale", "Symphytum officinale", "Boraginacées",
  "fleur-compagne", "🌼", expo="mi-ombre", eau="moyen", freq=5, sol=SOL_RICHE,
  espacement=80, diff=1, gel=True, tmin=-25, perenne=True, plantation=(-30, 60),
  recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Aime les sols riches et frais.",
  aime=["tomate", "pomme-de-terre"], evite=[],
  conseils=["Usage externe seulement : ses alcaloïdes pyrrolizidiniques sont toxiques pour le foie par voie interne",
            "Trois à quatre coupes par an pour le purin, riche en potasse",
            "Choisir la variété Bocking 14, stérile : les autres envahissent tout",
            "Ses racines descendent à deux mètres et remontent les minéraux"])

C("moutarde-blanche", "Moutarde blanche (engrais vert)", "Sinapis alba",
  "Brassicacées", "fleur-compagne", "🌼", eau="faible", freq=8, sol=SOL_ORDINAIRE,
  espacement=10, prof=2, diff=1, gel=True, tmin=-5,
  semis_dir=(-60, 150), cycle=(None, 50, None, 30),
  eau_notes="Aucun arrosage.",
  aime=[], evite=["chou-cabus", "chou-fleur", "radis"],
  conseils=["Pousse en six semaines sur toute planche vide",
            "Faucher avant la floraison et laisser sur place",
            "Jamais avant ni après un chou : même famille, mêmes maladies"])

C("sarrasin", "Sarrasin (engrais vert)", "Fagopyrum esculentum", "Polygonacées",
  "fleur-compagne", "🌼", eau="faible", freq=8, sol="pauvre, même ingrat",
  espacement=10, prof=3, diff=1, gel=False, tmin=2, semis_dir=(28, 90),
  cycle=(None, 45, None, 30),
  eau_notes="Aucun arrosage.",
  aime=[], evite=[],
  conseils=["Étouffe les adventices mieux que tout autre engrais vert",
            "Gèle au premier froid, ce qui évite d'avoir à le faucher"])

C("trefle-incarnat", "Trèfle incarnat (engrais vert)", "Trifolium incarnatum",
  "Fabacées", "fleur-compagne", "🌼", eau="faible", freq=8, sol=SOL_ORDINAIRE,
  espacement=8, prof=1, diff=1, gel=True, tmin=-12,
  semis_dir=(-60, 45), anchor_sd="premiere", cycle=(None, 210, None, 40),
  eau_notes="Aucun arrosage.",
  aime=[], evite=[],
  conseils=["Semé en septembre, il couvre le sol tout l'hiver et fixe l'azote",
            "Ses fleurs rouges en mai sont un festin pour les abeilles"])

C("vesce", "Vesce d'hiver (engrais vert)", "Vicia villosa", "Fabacées",
  "fleur-compagne", "🌼", eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=8,
  prof=3, diff=1, gel=True, tmin=-15, semis_dir=(-60, 45), anchor_sd="premiere",
  cycle=(None, 200, None, 40),
  eau_notes="Aucun arrosage.",
  aime=[], evite=[],
  conseils=["Se sème avec du seigle, qui lui sert de tuteur",
            "L'engrais vert d'hiver le plus riche en azote"])

C("cosmos", "Cosmos", "Cosmos bipinnatus", "Astéracées", "fleur-compagne", "🌼",
  eau="faible", freq=6, sol="pauvre : trop riche, il ne fait que des feuilles",
  espacement=40, prof=1, diff=1, gel=False, tmin=4,
  semis_dir=(28, 75), cycle=(None, 70, None, 120),
  eau_notes="Sobre.",
  aime=["tomate", "courgette"], evite=[],
  conseils=["Aimant à syrphes et à chrysopes, dont les larves mangent les pucerons",
            "Fleurit jusqu'aux gelées et se ressème seul"])

C("mauve", "Mauve sylvestre", "Malva sylvestris", "Malvacées", "fleur-compagne", "🌼",
  eau="faible", freq=7, sol=SOL_ORDINAIRE, espacement=50, prof=1, diff=1,
  gel=True, tmin=-15, perenne=True, semis_dir=(-30, 75), recolte=("06-01", 120),
  cycle=(None, None, None, 120),
  eau_notes="Très sobre.",
  aime=[], evite=[],
  conseils=["Fleurs et jeunes feuilles comestibles, en salade ou en tisane",
            "Se ressème abondamment : arracher les surnuméraires au printemps"])

# =============================================================================
# Céréales et graines — on les cultive pour leurs graines, pas pour leurs
# feuilles ni leurs fruits. Les ranger ailleurs les rendrait introuvables.
# =============================================================================

C("tournesol", "Tournesol", "Helianthus annuus", "Astéracées", "cereale", "🌻",
  eau="moyen", freq=5, sol=SOL_ORDINAIRE, espacement=50, prof=3, diff=1,
  gel=False, tmin=6, semis_dir=(28, 60), cycle=(None, 110, None, 30),
  eau_notes="Modéré ; ses racines descendent chercher loin.",
  aime=["concombre", "courgette", "mais-doux"], evite=["pomme-de-terre", "haricot-a-rames"],
  conseils=["Récolter quand le dos du capitule jaunit et que les graines se détachent",
            "Laisser une tête sur pied : les mésanges s'en chargeront tout l'hiver",
            "Il assèche et épuise le sol : ne pas le mettre à côté d'un gourmand"])

C("mais-popcorn", "Maïs à pop-corn", "Zea mays var. everta", "Poacées", "cereale", "🌽",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=35, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(28, 45), cycle=(None, 115, None, 30),
  eau_notes="Assoiffé à la floraison, comme le maïs doux.",
  aime=["courgette", "haricot-a-rames"], evite=["betterave", "mais-doux"],
  conseils=["Se récolte sec, à l'inverse du maïs doux : attendre que les tiges brunissent",
            "Jamais près du maïs doux : ils se croisent et gâchent les deux",
            "Faire sécher les épis deux mois avant de tenter le premier pop"])

C("quinoa", "Quinoa", "Chenopodium quinoa", "Amaranthacées", "cereale", "🌾",
  eau="faible", freq=7, sol=SOL_ORDINAIRE, espacement=30, prof=1, diff=2,
  gel=True, tmin=-4, semis_dir=(-15, 45), cycle=(None, 130, None, 30),
  eau_notes="Très sobre : il vient de l'Altiplano.",
  aime=["mais-doux"], evite=["betterave", "epinard"],
  conseils=["Les graines portent une saponine amère : les rincer longuement",
            "Les jeunes feuilles se mangent comme des épinards",
            "Récolter quand les feuilles tombent et que la graine résiste à l'ongle"])

C("amarante", "Amarante", "Amaranthus caudatus", "Amaranthacées", "cereale", "🌾",
  eau="faible", freq=6, sol=SOL_ORDINAIRE, espacement=40, prof=0.5, diff=1,
  gel=False, tmin=6, semis_dir=(28, 60), cycle=(None, 110, None, 40),
  eau_notes="Supporte très bien la sécheresse.",
  aime=["mais-doux", "tournesol"], evite=["betterave"],
  conseils=["Double usage : feuilles en épinard tout l'été, graines à l'automne",
            "Se ressème très abondamment : couper les épis avant qu'ils ne lâchent"])

C("houblon", "Houblon", "Humulus lupulus", "Cannabacées", "aromatique", "🌿",
  expo="mi-ombre", eau="moyen", freq=4, sol=SOL_RICHE, espacement=150, diff=2,
  gel=True, tmin=-25, perenne=True, plantation=(-30, 60), recolte=("08-25", 35),
  cycle=(None, None, None, 35),
  eau_notes="Aime les sols frais et profonds.",
  aime=[], evite=[],
  conseils=["Six mètres en une saison : il lui faut un fil solide jusqu'au toit",
            "Seuls les pieds femelles donnent des cônes",
            "Les jeunes pousses de printemps se mangent comme des asperges"])

# --- Engrais verts céréaliers ------------------------------------------------

C("seigle", "Seigle (engrais vert)", "Secale cereale", "Poacées", "fleur-compagne", "🌾",
  eau="faible", freq=10, sol="pauvre, même ingrat", espacement=8, prof=3,
  diff=1, gel=True, tmin=-25, semis_dir=(-60, 50), anchor_sd="premiere",
  cycle=(None, 200, None, 40),
  eau_notes="Aucun arrosage.",
  aime=["vesce", "trefle-incarnat"], evite=[],
  conseils=["Le plus rustique des engrais verts : il lève encore à 3 °C",
            "Se sème avec la vesce, à qui il sert de tuteur",
            "Ses racines décompactent les sols tassés en profondeur"])

C("avoine", "Avoine (engrais vert)", "Avena sativa", "Poacées", "fleur-compagne", "🌾",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=8, prof=3, diff=1,
  gel=True, tmin=-12, semis_dir=(-60, 60), anchor_sd="premiere",
  cycle=(None, 120, None, 40),
  eau_notes="Aucun arrosage.",
  aime=["vesce", "trefle-incarnat"], evite=[],
  conseils=["Gèle vers -12 °C et forme alors un paillage naturel : rien à faucher",
            "Idéale avant une culture exigeante au printemps suivant"])

# =============================================================================
# Légumes perpétuels — plantés une fois, récoltés des années durant
# =============================================================================

C("poireau-perpetuel", "Poireau perpétuel", "Allium ampeloprasum var. sectivum",
  "Amaryllidacées", "legume-bulbe", "🥬", eau="faible", freq=8, sol=SOL_ORDINAIRE,
  espacement=20, prof=3, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-30, 60), anchor_pl="premiere", recolte=("01-01", 364),
  cycle=(None, None, None, 364),
  eau_notes="Sobre une fois installé ; il se débrouille seul.",
  aime=["carotte", "fraisier", "celeri-rave"], evite=["haricot-nain", "petit-pois"],
  conseils=["Planté une fois, il se récolte toute l'année pendant des années",
            "Couper le fût au ras du sol : il repousse depuis la souche",
            "Il se multiplie seul par bulbilles — diviser la touffe tous les 3 ans"])

C("epinard-perpetuel", "Épinard perpétuel (Bon-Henri)", "Blitum bonus-henricus",
  "Amaranthacées", "legume-feuille", "🥬", expo="mi-ombre", eau="moyen", freq=5,
  sol=SOL_RICHE, espacement=40, prof=1, diff=1, gel=True, tmin=-20, perenne=True,
  semis_dir=(-30, 60), recolte=("04-01", 180), cycle=(None, None, None, 180),
  eau_notes="Aime la fraîcheur et la mi-ombre.",
  aime=["oseille"], evite=["betterave", "epinard"],
  conseils=["Une touffe donne des feuilles d'avril à octobre, pendant dix ans",
            "Ne rien récolter la première année, le temps qu'il s'installe",
            "Les jeunes pousses se préparent comme des asperges"])

C("roquette-vivace", "Roquette vivace", "Diplotaxis tenuifolia", "Brassicacées",
  "legume-feuille", "🥬", eau="faible", freq=6, sol=SOL_LEGER, espacement=25,
  prof=0.5, diff=1, gel=True, tmin=-15, perenne=True, semis_dir=(-30, 90),
  recolte=("03-15", 240), cycle=(None, None, None, 240),
  eau_notes="Très sobre, bien plus que la roquette annuelle.",
  aime=["laitue", "carotte"], evite=["chou-cabus"],
  conseils=["Plus piquante et bien plus rustique que la roquette cultivée",
            "Se coupe et repousse sans fin, de mars à novembre",
            "Supprimer les fleurs jaunes pour garder des feuilles tendres"])

# =============================================================================
# Médicinales et comestibles sauvages
#
# Cette section est la seule du catalogue à avoir été écrite en consultant des
# sources extérieures, et non de mémoire horticole : les monographies de
# plantes du HMPC de l'Agence européenne du médicament pour les usages et les
# contre-indications, les bulletins de toxicovigilance de l'Anses et des
# Centres antipoison pour les confusions de cueillette. Les sources exactes
# sont listées dans le message de la pull request qui les introduit.
#
# Deux règles tenues pour chaque fiche, et elles ne sont pas négociables :
#
# 1. **Aucune posologie, aucune indication thérapeutique.** Rhizome dit
#    comment faire pousser une plante, jamais quoi en faire pour se soigner.
#    Une fiche qui conseillerait une dose sortirait de son rôle et prendrait
#    une responsabilité qu'un suivi de jardin ne peut pas porter.
# 2. **Le risque est dit en clair, dans les conseils.** Toxicité, confusion
#    mortelle à la cueillette, interaction médicamenteuse connue : c'est le
#    seul endroit du catalogue où une fiche muette peut nuire. Le conseil de
#    prudence est toujours le premier de la liste, pour qu'il soit lu.
# =============================================================================

SOL_FRAIS_LOURD = "frais, lourd, qui ne sèche jamais"

C("achillee", "Achillée millefeuille", "Achillea millefolium", "Astéracées",
  "medicinale", "🌿", eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=40,
  prof=0.5, diff=1, gel=True, tmin=-25, perenne=True, plantation=(-30, 75),
  recolte=("06-01", 105), cycle=(None, None, None, 105),
  eau_notes="Très sobre : elle pousse dans les talus que personne n'arrose.",
  aime=["aubepine"], evite=[],
  conseils=["Déconseillée aux femmes enceintes, et allergisante comme toutes les astéracées",
            "Ne jamais la cueillir jeune en mélange : ses feuilles ressemblent à celles de la ciguë, mortelle",
            "Couper les sommités fleuries par temps sec, en pleine floraison",
            "Une bordure d'achillée attire les syrphes, qui mangent les pucerons"])

C("plantain-lanceole", "Plantain lancéolé", "Plantago lanceolata", "Plantaginacées",
  "medicinale", "🌿", eau="faible", freq=8, sol=SOL_ORDINAIRE, espacement=25,
  prof=0.5, diff=1, gel=True, tmin=-25, perenne=True, semis_dir=(-15, 90),
  recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Sobre ; il supporte même le piétinement et la sécheresse.",
  aime=[], evite=[],
  conseils=["Aucune confusion dangereuse connue, ce qui en fait une bonne première plante à apprendre",
            "Jeunes feuilles comestibles en salade ; les vieilles sont filandreuses",
            "Pousse spontanément dans toutes les pelouses de France — inutile de l'acheter",
            "Se ressème seul : supprimer les épis si on ne veut pas qu'il s'étende"])

C("ortie", "Ortie dioïque", "Urtica dioica", "Urticacées",
  "medicinale", "🌿", expo="mi-ombre", eau="moyen", freq=5, sol=SOL_RICHE,
  espacement=50, diff=1, gel=True, tmin=-25, perenne=True, plantation=(-30, 75),
  recolte=("04-01", 120), cycle=(None, None, None, 120),
  eau_notes="Aime les sols riches en azote et frais ; elle marque les anciens fumiers.",
  aime=["tomate", "menthe-poivree"], evite=[],
  conseils=["Cueillir avec des gants : les poils urticants tiennent jusqu'à la cuisson",
            "Ne récolter que les quatre feuilles du sommet, avant la floraison",
            "Elle envahit par ses rhizomes : la cantonner dans un carré, ou en pot",
            "Son purin est un engrais azoté ; celui de consoude apporte la potasse"])

C("millepertuis", "Millepertuis perforé", "Hypericum perforatum", "Hypéricacées",
  "medicinale", "🌼", eau="faible", freq=10, sol="pauvre, caillouteux, très drainé",
  espacement=40, diff=1, gel=True, tmin=-20, perenne=True, plantation=(-30, 60),
  recolte=("06-21", 60), cycle=(None, None, None, 60),
  eau_notes="Sobre : trop d'eau le fait pourrir au collet.",
  aime=[], evite=[],
  conseils=["Interagit avec beaucoup de médicaments — pilule, anticoagulants, antirétroviraux — en accélérant leur élimination",
            "Photosensibilisant : il rend la peau plus sensible au soleil",
            "Reconnaissable aux points translucides de ses feuilles, vues à contre-jour",
            "Récolter les sommités fleuries autour du solstice, c'est là qu'elles sont les plus riches"])

C("aubepine", "Aubépine monogyne", "Crataegus monogyna", "Rosacées",
  "medicinale", "🌸", eau="faible", freq=12, sol=SOL_ORDINAIRE, espacement=200,
  diff=1, gel=True, tmin=-30, perenne=True, plantation=(-15, 75), anchor_pl="premiere",
  recolte=("05-01", 30), cycle=(None, None, None, 30),
  eau_notes="Aucun arrosage une fois établie : c'est un arbuste de haie.",
  aime=["achillee"], evite=[],
  conseils=["Ses épines sont longues et cassent sous la peau : tailler gants et manches longues",
            "Plantation réglementée par endroits : hôte du feu bactérien, se renseigner en pépinière",
            "Récolter les fleurs à peine ouvertes, les cynorhodons rouges en automne",
            "Une haie d'aubépine abrite les oiseaux insectivores tout l'hiver"])

C("reine-des-pres", "Reine-des-prés", "Filipendula ulmaria", "Rosacées",
  "medicinale", "🌼", expo="mi-ombre", eau="eleve", freq=3, sol=SOL_FRAIS_LOURD,
  espacement=60, diff=1, gel=True, tmin=-25, perenne=True, plantation=(-30, 75),
  recolte=("06-15", 60), cycle=(None, None, None, 60),
  eau_notes="Jamais à sec : c'est une plante de fossé et de prairie humide.",
  aime=[], evite=[],
  conseils=["Contient des dérivés salicylés : à éviter en cas d'allergie à l'aspirine",
            "Elle meurt de sécheresse avant de mourir de froid : ne la planter qu'en sol frais",
            "Récolter les fleurs blanches en plein épanouissement, elles sentent l'amande"])

C("guimauve", "Guimauve officinale", "Althaea officinalis", "Malvacées",
  "medicinale", "🌸", eau="moyen", freq=5, sol=SOL_FRAIS_LOURD, espacement=60,
  prof=1, diff=2, gel=True, tmin=-20, perenne=True, plantation=(-15, 60),
  recolte=("07-01", 75), cycle=(None, None, None, 75),
  eau_notes="Aime avoir le pied frais tout l'été.",
  aime=["mauve"], evite=[],
  conseils=["Fleurs, feuilles et racines sont comestibles ; aucune toxicité connue",
            "Ne récolter les racines qu'à l'automne de la deuxième année",
            "Sa levée est lente et irrégulière : passer par un plant est plus sûr"])

C("echinacee", "Échinacée pourpre", "Echinacea purpurea", "Astéracées",
  "medicinale", "🌸", eau="faible", freq=8, sol=SOL_ORDINAIRE, espacement=45,
  prof=0.5, diff=2, gel=True, tmin=-25, perenne=True, plantation=(0, 60),
  recolte=("07-15", 75), cycle=(None, None, None, 75),
  eau_notes="Sobre une fois installée ; craint l'humidité stagnante de l'hiver.",
  aime=["tournesol"], evite=[],
  conseils=["Allergisante comme toutes les astéracées ; déconseillée en cas de maladie auto-immune",
            "Ne rien prélever les deux premières années, le temps que la touffe se fasse",
            "Laisser les capitules secs en place l'hiver : les chardonnerets les vident"])

C("valeriane", "Valériane officinale", "Valeriana officinalis", "Caprifoliacées",
  "medicinale", "🌼", expo="mi-ombre", eau="moyen", freq=4, sol=SOL_FRAIS_LOURD,
  espacement=50, prof=0.5, diff=2, gel=True, tmin=-25, perenne=True,
  plantation=(-15, 60), recolte=("10-01", 45), cycle=(None, None, None, 45),
  eau_notes="Sol frais en permanence ; elle pousse naturellement au bord des ruisseaux.",
  aime=[], evite=[],
  conseils=["Déconseillée avant la conduite : elle agit sur la vigilance",
            "Ses racines sentent fort une fois sèches, et les chats s'y roulent",
            "Déterrer les racines à l'automne de la deuxième année, pas avant"])

C("pissenlit", "Pissenlit", "Taraxacum officinale", "Astéracées",
  "medicinale", "🌼", eau="faible", freq=8, sol=SOL_ORDINAIRE, espacement=30,
  prof=0.5, diff=1, gel=True, tmin=-25, perenne=True, semis_dir=(-30, 90),
  recolte=("03-01", 180), cycle=(None, None, None, 180),
  eau_notes="Sobre : sa racine pivot va chercher l'eau en profondeur.",
  aime=[], evite=[],
  conseils=["Entièrement comestible, sans confusion dangereuse connue en France",
            "Ne jamais cueillir au bord d'une route ni sur une pelouse traitée",
            "Blanchir les cœurs sous un pot retourné quinze jours : l'amertume tombe",
            "Il remonte le calcium et le potassium des couches profondes du sol"])

C("bardane", "Grande bardane", "Arctium lappa", "Astéracées",
  "medicinale", "🌿", eau="moyen", freq=6, sol=SOL_LEGER, espacement=70,
  prof=2, diff=2, gel=True, tmin=-20, semis_dir=(-15, 60), cycle=(None, 150, None, 60),
  eau_notes="Régulier la première année, le temps que la racine descende.",
  aime=[], evite=[],
  conseils=["Allergisante comme les astéracées ; ses capitules s'accrochent aux vêtements et aux animaux",
            "Racine comestible, récoltée à l'automne de la première année — c'est le gobō japonais",
            "Semer en sol profond et meuble : la racine descend à cinquante centimètres",
            "Supprimer les fleurs de la deuxième année, sinon elle se ressème partout"])

C("bouillon-blanc", "Bouillon-blanc", "Verbascum thapsus", "Scrofulariacées",
  "medicinale", "🌼", eau="faible", freq=12, sol="pauvre, caillouteux, très drainé",
  espacement=60, prof=0.2, diff=1, gel=True, tmin=-25, semis_dir=(-15, 90),
  cycle=(None, 150, None, 75),
  eau_notes="Aucun arrosage : il colonise les gravières et les talus secs.",
  aime=[], evite=[],
  conseils=["Filtrer soigneusement toute infusion : les poils des feuilles irritent la gorge",
            "Bisannuel — rosette la première année, hampe de deux mètres la seconde",
            "Semer en surface sans recouvrir, la graine a besoin de lumière pour lever",
            "Récolter les fleurs jaunes au fur et à mesure, elles s'ouvrent de bas en haut"])

C("prele", "Prêle des champs", "Equisetum arvense", "Équisétacées",
  "medicinale", "🌿", expo="mi-ombre", eau="eleve", freq=4, sol=SOL_FRAIS_LOURD,
  espacement=40, diff=2, gel=True, tmin=-25, perenne=True, plantation=(-30, 75),
  recolte=("06-01", 90), cycle=(None, None, None, 90),
  eau_notes="Sol humide en permanence ; elle signale les terrains mal drainés.",
  aime=["pommier", "tomate"], evite=[],
  conseils=["Ne pas la confondre avec la prêle des marais, Equisetum palustre, toxique : chez la prêle des champs, le premier entre-nœud d'un rameau est aussi long ou plus long que la gaine de la tige d'où il part",
            "Ses rhizomes descendent à un mètre et la rendent impossible à éradiquer : la planter en bac",
            "Récolter les tiges stériles vertes de l'été, pas les épis bruns du printemps",
            "Sa décoction, riche en silice, sert de traitement préventif contre les maladies cryptogamiques"])

C("tanaisie", "Tanaisie commune", "Tanacetum vulgare", "Astéracées",
  "medicinale", "🌼", eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=60,
  diff=1, gel=True, tmin=-25, perenne=True, plantation=(-30, 75),
  recolte=("07-01", 75), cycle=(None, None, None, 75),
  eau_notes="Très sobre, à la limite de l'indestructible.",
  aime=["chou-cabus", "pomme-de-terre"], evite=[],
  conseils=["Toxique par ingestion à cause de sa thuyone, et interdite aux femmes enceintes : on la cultive pour le jardin, pas pour la tisane",
            "Son purin répulsif est son véritable usage, contre pucerons et altises",
            "Elle s'étend par rhizomes et prend la place : la diviser tous les trois ans"])

C("armoise-absinthe", "Absinthe", "Artemisia absinthium", "Astéracées",
  "medicinale", "🌿", eau="faible", freq=12, sol="pauvre, caillouteux, très drainé",
  espacement=60, diff=1, gel=True, tmin=-25, perenne=True, plantation=(-15, 60),
  recolte=("07-15", 60), cycle=(None, None, None, 60),
  eau_notes="Aucun arrosage : elle meurt d'excès d'eau, jamais de sécheresse.",
  aime=["chou-cabus", "carotte"], evite=["aneth", "coriandre", "fenouil-aromatique"],
  conseils=["Neurotoxique à forte dose par sa thuyone, et interdite aux femmes enceintes",
            "Elle inhibe la germination de ses voisines : la planter en bout de planche, jamais au milieu",
            "Son purin éloigne les pucerons, les limaces et la piéride du chou"])

C("menthe-poivree", "Menthe poivrée", "Mentha × piperita", "Lamiacées",
  "medicinale", "🌿", expo="mi-ombre", eau="eleve", freq=3, sol=SOL_RICHE,
  espacement=40, diff=1, gel=True, tmin=-20, perenne=True, plantation=(-15, 90),
  recolte=("06-01", 120), cycle=(None, None, None, 120),
  eau_notes="Jamais à sec : elle flétrit en une journée de canicule.",
  aime=["chou-cabus", "tomate"], evite=["camomille", "persil"],
  conseils=["Déconseillée aux nourrissons et aux jeunes enfants, par voie interne comme en inhalation",
            "Hybride stérile : elle ne se ressème pas, mais ses stolons envahissent tout — la planter en pot enterré",
            "Rabattre toute la touffe avant la floraison, l'arôme y est au maximum",
            "Plus poivrée et plus riche en menthol que la menthe verte"])

C("tilleul", "Tilleul à petites feuilles", "Tilia cordata", "Malvacées",
  "medicinale", "🌳", eau="faible", freq=14, sol=SOL_ORDINAIRE, espacement=800,
  diff=1, gel=True, tmin=-30, perenne=True, plantation=(-15, 75), anchor_pl="premiere",
  recolte=("06-10", 20), cycle=(None, None, None, 20),
  eau_notes="Aucun arrosage une fois établi ; le soutenir les deux premiers étés.",
  aime=[], evite=[],
  conseils=["Aucune toxicité connue, ce qui en fait une tisane de tous les âges",
            "Arbre de vingt mètres : à ne planter que si la place existe vraiment",
            "La fenêtre de récolte des bractées dure dix jours, pas plus",
            "Récolter en hauteur et jamais en bord de route : ses fleurs captent les poussières"])

C("eglantier", "Églantier", "Rosa canina", "Rosacées",
  "medicinale", "🌹", eau="faible", freq=12, sol=SOL_ORDINAIRE, espacement=180,
  diff=1, gel=True, tmin=-30, perenne=True, plantation=(-15, 75), anchor_pl="premiere",
  recolte=("10-01", 60), cycle=(None, None, None, 60),
  eau_notes="Aucun arrosage une fois établi : c'est la ronce des haies.",
  aime=["aubepine"], evite=[],
  conseils=["Les poils qui entourent les graines du cynorhodon sont irritants : les retirer avant toute préparation",
            "Attendre les premières gelées pour cueillir, le fruit devient blet et sucré",
            "Son cynorhodon est l'un des fruits les plus riches en vitamine C de la flore française",
            "Il sert de porte-greffe aux rosiers de jardin"])

C("onagre", "Onagre bisannuelle", "Oenothera biennis", "Onagracées",
  "medicinale", "🌼", eau="faible", freq=10, sol="pauvre, sableux, très drainé",
  espacement=50, prof=0.5, diff=1, gel=True, tmin=-25, semis_dir=(-15, 90),
  cycle=(None, 150, None, 60),
  eau_notes="Très sobre : elle pousse dans les sables et les remblais.",
  aime=[], evite=[],
  conseils=["Aucune toxicité connue ; sa racine de première année se mange comme un salsifis",
            "Bisannuelle — rosette la première année, hampe fleurie la seconde",
            "Ses fleurs s'ouvrent au crépuscule en quelques minutes et nourrissent les sphinx",
            "Elle se ressème abondamment : garder deux ou trois pieds, arracher le reste"])

C("passiflore", "Passiflore officinale", "Passiflora incarnata", "Passifloracées",
  "medicinale", "🌸", eau="moyen", freq=5, sol=SOL_ORDINAIRE, espacement=120,
  diff=3, gel=True, tmin=-15, perenne=True, plantation=(15, 45),
  recolte=("07-01", 75), cycle=(None, None, None, 75),
  eau_notes="Régulier en été ; très réduit l'hiver, quand elle disparaît.",
  aime=[], evite=[],
  conseils=["Déconseillée avant la conduite ; ne pas la confondre avec Passiflora caerulea, la passiflore bleue ornementale, dont les fruits ne se consomment pas",
            "Elle disparaît complètement l'hiver et repart de souche en mai : ne pas croire qu'elle est morte",
            "Ne pas espérer de fruit au nord de la Loire — c'est la partie aérienne qui est récoltée",
            "Lui donner un mur au sud et un paillis épais pour passer l'hiver"])

C("camomille-matricaire", "Camomille matricaire", "Matricaria chamomilla", "Astéracées",
  "medicinale", "🌼", eau="faible", freq=8, sol=SOL_LEGER, espacement=20,
  prof=0.2, diff=1, gel=True, tmin=-15, semis_dir=(-30, 90), cycle=(None, 75, None, 60),
  eau_notes="Sobre ; elle n'aime pas les sols lourds et détrempés.",
  aime=["chou-cabus", "oignon-jaune"], evite=["menthe-poivree"],
  conseils=["Allergisante chez les personnes sensibles aux astéracées",
            "Annuelle, à ne pas confondre avec la camomille romaine, vivace : son réceptacle est creux quand on le coupe en deux",
            "Semer en surface sans recouvrir, la graine est minuscule",
            "Cueillir les capitules un à un, au plus chaud d'une journée sèche"])

# =============================================================================
# Plantes d'intérieur
#
# Elles ne portent aucune fenêtre, et c'est volontaire : toutes les fenêtres du
# catalogue sont des décalages par rapport aux gelées locales, et une plante qui
# vit à vingt degrés toute l'année ne connaît pas de gelées. Lui inventer une
# plantation et une récolte pour satisfaire le validateur aurait affiché des
# étapes culturales absurdes — « récolte du monstera le 5 juillet ». La fiche ne
# porte donc que ce qui est vrai d'elle : la lumière, l'eau, le substrat,
# l'encombrement adulte et les conseils. L'arrosage, lui, fonctionne — c'est
# justement le seul mécanisme de Rhizome qui ne dépende pas des saisons.
#
# `exposition` change de sens ici, et il faut le savoir pour lire ces fiches :
# « plein-soleil » veut dire plein sud derrière une vitre, « mi-ombre » la
# lumière vive mais indirecte dont la plupart de ces plantes vivent, et
# « ombre » le fond d'une pièce. Ajouter des valeurs propres à l'intérieur
# aurait demandé de toucher les filtres du panneau et les deux tables de
# libellés pour un gain de vocabulaire seulement.
#
# `espacement_cm` est l'encombrement adulte — ce que la plante prendra sur le
# meuble — et non une distance de plantation.
#
# `temp_min_c` est la température en dessous de laquelle la plante souffre,
# pas celle d'une gelée : c'est le chiffre qui dit si elle peut passer l'été
# dehors ou hiverner dans une véranda non chauffée.
#
# Sources : les fiches de culture de la Royal Horticultural Society pour la
# lumière, l'eau et le rempotage ; la base des plantes toxiques de l'ASPCA
# pour la toxicité envers chiens et chats, qui est la question que pose
# vraiment un foyer avec un animal. Détail dans la pull request.
# =============================================================================

SOL_TERREAU = "terreau de plantes vertes, drainant"
SOL_TERREAU_AERE = "terreau très aéré, écorce et perlite"
SOL_CACTEE = "substrat à cactées, sableux et très drainant"
SOL_ORCHIDEE = "écorce de pin seule, sans terreau"


def INT(cid, nom, sci, famille, emoji, **kw):
    """Une plante d'intérieur : perenne, gélive, et sans aucune fenêtre.

    Le raccourci existe pour que ces trois faits ne puissent pas être oubliés
    sur une fiche — une plante d'intérieur déclarée non gélive passerait le
    validateur et promettrait un hivernage dehors.
    """
    kw.setdefault("gel", False)
    kw.setdefault("sol", SOL_TERREAU)
    return C(cid, nom, sci, famille, "plante-interieur", emoji,
             perenne=True, cycle=(None, None, None, 0), **kw)


# --- Aracées : le gros du rayon, et toutes irritantes ------------------------
#
# Toutes contiennent des oxalates de calcium en aiguilles : la bouche brûle
# immédiatement, ce qui limite heureusement la quantité avalée. C'est le motif
# de toxicité le plus répandu du rayon plantes vertes, et il est dit sur
# chaque fiche plutôt que renvoyé à une note générale que personne ne lirait.

INT("monstera", "Monstera", "Monstera deliciosa", "Aracées", "🪴",
  expo="mi-ombre", eau="moyen", freq=8, sol=SOL_TERREAU_AERE, espacement=150,
  diff=1, tmin=13,
  eau_notes="Laisser sécher les trois premiers centimètres entre deux arrosages.",
  conseils=["Irritante pour la bouche de l'homme et de l'animal : à mettre hors de portée d'un chat ou d'un petit enfant",
            "Ses découpes n'apparaissent qu'avec l'âge et la lumière : une jeune feuille pleine est normale",
            "Lui donner un tuteur-mousse, ses racines aériennes s'y accrochent",
            "Dépoussiérer les feuilles : c'est par elles qu'elle respire"])

INT("pothos", "Pothos", "Epipremnum aureum", "Aracées", "🌿",
  expo="mi-ombre", eau="moyen", freq=9, espacement=60, diff=1, tmin=13,
  eau_notes="Attendre que le terreau soit sec sur la moitié du pot.",
  conseils=["Irritante par ses oxalates : la suspendre hors d'atteinte si un animal grignote",
            "La plante la plus indulgente du rayon : elle survit à l'oubli et au fond d'une pièce",
            "Une tige coupée sous un nœud racine en deux semaines dans un verre d'eau",
            "Ses panachures pâlissent dans l'ombre : la rapprocher d'une fenêtre pour les garder"])

INT("philodendron", "Philodendron grimpant", "Philodendron hederaceum", "Aracées", "🌿",
  expo="mi-ombre", eau="moyen", freq=8, sol=SOL_TERREAU_AERE, espacement=80,
  diff=1, tmin=15,
  eau_notes="Garder le terreau juste humide, jamais détrempé.",
  conseils=["Irritante par ses oxalates, pour l'homme comme pour l'animal",
            "Pincer les tiges régulièrement, sans quoi elle file en lianes nues",
            "Le pot doit pouvoir s'égoutter : l'eau stagnante lui pourrit les racines"])

INT("spathiphyllum", "Fleur de lune", "Spathiphyllum wallisii", "Aracées", "🤍",
  expo="mi-ombre", eau="eleve", freq=5, espacement=50, diff=1, tmin=15,
  eau_notes="Elle signale elle-même la soif en s'affaissant, et se relève en deux heures.",
  conseils=["Irritante par ses oxalates : c'est la plante d'intérieur la plus souvent signalée aux centres antipoison vétérinaires",
            "Fleurit peu dans l'ombre profonde : lumière vive indirecte, sans soleil direct",
            "Ne pas se fier à l'affaissement comme méthode d'arrosage : répété, il abîme les racines"])

INT("zamioculcas", "Zamioculcas", "Zamioculcas zamiifolia", "Aracées", "🪴",
  expo="mi-ombre", eau="faible", freq=21, sol=SOL_CACTEE, espacement=70,
  diff=1, tmin=15,
  eau_notes="Un arrosage toutes les trois semaines suffit, moitié moins l'hiver.",
  conseils=["Irritante par ses oxalates et ses saponines, concentrées dans les tiges et les rhizomes",
            "Elle meurt bien plus souvent d'excès d'eau que de sécheresse : en cas de doute, ne pas arroser",
            "Ses rhizomes stockent l'eau : elle encaisse un mois d'absence sans broncher"])

INT("dieffenbachia", "Dieffenbachia", "Dieffenbachia seguine", "Aracées", "🪴",
  expo="mi-ombre", eau="moyen", freq=7, espacement=70, diff=2, tmin=16,
  eau_notes="Terreau frais en permanence, mais jamais d'eau dans la soucoupe.",
  conseils=["La plus toxique du rayon : sa sève provoque une douleur buccale intense et un gonflement qui peut gêner la parole — à écarter d'un foyer avec enfant en bas âge ou animal",
            "Porter des gants pour la bouturer, et se laver les mains après",
            "Ses feuilles brûlent au soleil direct : lumière tamisée uniquement"])

# --- Asparagacées : robustes, et seulement la nausée en cas d'ingestion ------

INT("sansevieria", "Sansevieria", "Dracaena trifasciata", "Asparagacées", "🌵",
  expo="mi-ombre", eau="faible", freq=21, sol=SOL_CACTEE, espacement=40,
  diff=1, tmin=12,
  eau_notes="Toutes les trois semaines l'été, une fois par mois l'hiver.",
  conseils=["Ses saponines provoquent vomissements et diarrhée chez le chien et le chat ; sans gravité chez l'adulte",
            "Elle supporte tout sauf l'excès d'eau : c'est la seule faute qui la tue",
            "Elle se contente du fond d'une pièce, mais pousse trois fois plus vite près d'une fenêtre",
            "Une feuille coupée en tronçons et plantée dans du sable donne un nouveau pied"])

INT("dracaena-marginata", "Dragonnier de Madagascar", "Dracaena marginata",
  "Asparagacées", "🌴", expo="mi-ombre", eau="faible", freq=12, espacement=80,
  diff=1, tmin=15,
  eau_notes="Laisser sécher la moitié du pot ; elle craint l'eau stagnante.",
  conseils=["Ses saponines rendent le chat malade ; les extrémités de feuilles tentent les chats, les mettre en hauteur",
            "Les pointes brunes signalent presque toujours un excès de fluor ou de chlore : laisser l'eau reposer une nuit",
            "Une tige dégarnie peut être étêtée : elle repart en deux ou trois têtes"])

INT("aspidistra", "Aspidistra", "Aspidistra elatior", "Asparagacées", "🌿",
  expo="ombre", eau="faible", freq=14, espacement=60, diff=1, tmin=5,
  eau_notes="Très sobre, et elle pardonne l'oubli mieux que l'excès.",
  conseils=["Aucune toxicité connue pour le chien ni le chat",
            "Surnommée la plante du fer forgé : elle vit dans les coins que rien d'autre ne supporte",
            "Elle tient 5 °C : c'est la seule du rayon qui passe l'hiver dans une cage d'escalier non chauffée",
            "Sa croissance est très lente — deux ou trois feuilles par an, c'est normal"])

INT("chlorophytum", "Phalangère", "Chlorophytum comosum", "Asparagacées", "🌱",
  expo="mi-ombre", eau="moyen", freq=7, espacement=45, diff=1, tmin=10,
  eau_notes="Terreau frais l'été, plus sec l'hiver ; ses racines charnues stockent l'eau.",
  conseils=["Non toxique pour le chien et le chat selon l'ASPCA — mais les chats s'y intéressent et peuvent vomir d'en avoir trop mangé",
            "Ses stolons portent des plantules qui racinent dans un verre d'eau",
            "Les pointes brunes viennent du calcaire de l'eau du robinet"])

# --- Marantacées : non toxiques, mais exigeantes en humidité ------------------

INT("calathea", "Calathea", "Calathea orbifolia", "Marantacées", "🍃",
  expo="mi-ombre", eau="eleve", freq=4, sol=SOL_TERREAU_AERE, espacement=60,
  diff=3, tmin=18,
  eau_notes="Jamais à sec, et à l'eau non calcaire : eau de pluie ou eau filtrée.",
  conseils=["Non toxique pour le chien et le chat selon l'ASPCA",
            "La plus difficile de cette liste : elle veut 60 % d'humidité et brunit sèchement en appartement chauffé",
            "Le calcaire de l'eau du robinet lui brûle le bord des feuilles : c'est la cause la plus fréquente d'échec",
            "La poser sur un lit de billes d'argile humides, jamais les pieds dans l'eau"])

INT("maranta", "Maranta", "Maranta leuconeura", "Marantacées", "🍃",
  expo="mi-ombre", eau="eleve", freq=4, sol=SOL_TERREAU_AERE, espacement=40,
  diff=2, tmin=16,
  eau_notes="Terreau frais en permanence, à l'eau non calcaire.",
  conseils=["Non toxique pour le chien et le chat selon l'ASPCA",
            "Elle replie ses feuilles la nuit : c'est son fonctionnement normal, pas un signe de soif",
            "Plus indulgente que la calathea, pour un feuillage presque aussi beau"])

# --- Les faciles, non toxiques ------------------------------------------------

INT("pilea", "Plante à monnaie chinoise", "Pilea peperomioides", "Urticacées", "🪙",
  expo="mi-ombre", eau="moyen", freq=8, espacement=35, diff=1, tmin=13,
  eau_notes="Laisser sécher la surface entre deux arrosages ; elle flétrit vite et se remet vite.",
  conseils=["Aucune toxicité connue pour le chien ni le chat",
            "La tourner d'un quart de tour chaque semaine, sinon elle penche vers la fenêtre",
            "Elle produit des rejets au pied : les détacher avec un peu de racine et les rempoter"])

INT("peperomia", "Peperomia", "Peperomia obtusifolia", "Pipéracées", "🌿",
  expo="mi-ombre", eau="faible", freq=12, sol=SOL_TERREAU_AERE, espacement=30,
  diff=1, tmin=15,
  eau_notes="Ses feuilles épaisses stockent l'eau : laisser bien sécher entre deux arrosages.",
  conseils=["Non toxique pour le chien et le chat selon l'ASPCA",
            "Petite et lente : idéale sur un bureau, elle ne dépassera pas trente centimètres",
            "Une feuille piquée dans du terreau humide donne un nouveau pied"])

INT("hoya", "Fleur de porcelaine", "Hoya carnosa", "Apocynacées", "🌸",
  expo="plein-soleil", eau="faible", freq=14, sol=SOL_TERREAU_AERE, espacement=100,
  diff=2, tmin=12,
  eau_notes="Laisser sécher complètement entre deux arrosages, surtout l'hiver.",
  conseils=["Aucune toxicité connue pour le chien ni le chat",
            "Ne jamais couper le pédoncule après la floraison : elle refleurit dessus l'année suivante",
            "Elle ne fleurit qu'une fois à l'étroit dans son pot : ne pas la rempoter trop vite",
            "Il lui faut quelques heures de soleil filtré pour fleurir"])

INT("fougere-nid", "Fougère nid d'oiseau", "Asplenium nidus", "Aspléniacées", "🌿",
  expo="ombre", eau="eleve", freq=4, sol=SOL_TERREAU_AERE, espacement=70,
  diff=2, tmin=16,
  eau_notes="Terreau constamment humide ; arroser sur le bord, jamais dans le cœur.",
  conseils=["Non toxique pour le chien et le chat selon l'ASPCA",
            "L'eau versée au centre de la rosette la fait pourrir : c'est la faute classique",
            "Une salle de bains éclairée est son meilleur emplacement en appartement",
            "Ne jamais lustrer ses frondes : les produits lustrants les brûlent"])

INT("kentia", "Kentia", "Howea forsteriana", "Arécacées", "🌴",
  expo="mi-ombre", eau="moyen", freq=8, espacement=150, diff=2, tmin=12,
  eau_notes="Terreau frais l'été, nettement plus sec l'hiver.",
  conseils=["Non toxique pour le chien et le chat selon l'ASPCA : c'est le grand sujet de foyer avec animaux",
            "Croissance très lente : une ou deux palmes par an, et un grand sujet coûte cher pour cette raison",
            "Ne jamais couper le sommet d'un stipe : un palmier n'a qu'un bourgeon et ne repartira pas",
            "Les araignées rouges l'attaquent en air sec : doucher le feuillage une fois par mois"])

INT("orchidee-phalaenopsis", "Orchidée papillon", "Phalaenopsis × hybr.",
  "Orchidacées", "🌺", expo="mi-ombre", eau="moyen", freq=7, sol=SOL_ORCHIDEE,
  espacement=40, diff=2, tmin=16,
  eau_notes="Tremper le pot un quart d'heure puis l'égoutter entièrement ; jamais d'eau résiduelle.",
  conseils=["Non toxique pour le chien et le chat selon l'ASPCA",
            "Jamais de terreau : ses racines sont aériennes et étouffent dedans",
            "Des racines vertes après arrosage et argentées ensuite indiquent un rythme juste",
            "Après la floraison, couper la hampe un centimètre au-dessus du deuxième œil"])

# --- Succulentes et ficus ----------------------------------------------------

INT("aloe-vera", "Aloe vera", "Aloe vera", "Asphodélacées", "🌵",
  expo="plein-soleil", eau="faible", freq=21, sol=SOL_CACTEE, espacement=50,
  diff=1, tmin=10,
  eau_notes="Arroser abondamment, puis laisser le pot sécher complètement.",
  conseils=["Le latex jaune sous la peau de la feuille est purgatif et rend chiens et chats malades : non toxique ne vaut que pour le gel transparent du cœur",
            "L'erreur fatale est l'arrosage d'hiver : la plante est au repos et pourrit",
            "Il lui faut le rebord de fenêtre le plus ensoleillé de la maison",
            "Elle peut passer l'été dehors, rentrée avant que les nuits descendent sous 10 °C"])

INT("crassula", "Arbre de jade", "Crassula ovata", "Crassulacées", "🪴",
  expo="plein-soleil", eau="faible", freq=18, sol=SOL_CACTEE, espacement=60,
  diff=1, tmin=7,
  eau_notes="Laisser sécher complètement ; presque rien de novembre à mars.",
  conseils=["Toxique pour le chien et le chat, qui vomissent et deviennent apathiques",
            "Ses feuilles qui se rident disent la soif mieux que n'importe quel calendrier",
            "Un pot étroit et lourd l'empêche de verser quand elle grossit",
            "Elle vit cinquante ans et se transmet : c'est la plante grasse des maisons de famille"])

INT("ficus-elastica", "Caoutchouc", "Ficus elastica", "Moracées", "🌳",
  expo="mi-ombre", eau="moyen", freq=10, espacement=120, diff=1, tmin=13,
  eau_notes="Laisser sécher la moitié du pot entre deux arrosages.",
  conseils=["Son latex blanc irrite la peau et la bouche, de l'homme comme de l'animal : couper avec des gants",
            "Il n'aime pas qu'on le déplace : trouver sa place et ne plus y toucher",
            "Dépoussiérer les feuilles à l'éponge humide, elles captent beaucoup",
            "Étêter un sujet trop haut le fait ramifier"])

INT("ficus-lyrata", "Figuier lyre", "Ficus lyrata", "Moracées", "🌳",
  expo="mi-ombre", eau="moyen", freq=9, sol=SOL_TERREAU_AERE, espacement=120,
  diff=3, tmin=15,
  eau_notes="Régulier et modéré : il perd ses feuilles basses à la moindre irrégularité.",
  conseils=["Son latex blanc irrite la peau et la bouche, comme chez tous les ficus",
            "Le plus capricieux des ficus : courant d'air, déplacement ou arrosage irrégulier lui font perdre ses feuilles",
            "Il veut beaucoup de lumière indirecte, à moins d'un mètre d'une grande fenêtre",
            "Les feuilles perdues en bas ne repoussent jamais au même endroit"])
