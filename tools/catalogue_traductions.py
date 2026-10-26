"""Traductions anglaises du catalogue, compilees dans data/catalog.json.

Pourquoi ici et pas dans `catalogue_source.py` : la table des cultures tient
une ligne par fiche, et y ajouter cinq champs anglais la rendrait illisible.
Pourquoi pas dans `translations/en.json` : Home Assistant ne sert ce fichier
qu'a ses propres mecanismes — un flux de configuration, une action, une
exception a cle — pas a 172 fiches de catalogue lues par le panneau.

Les textes libres sont indexes par leur version francaise, et non par
l'identifiant de la culture. C'est voulu :

- les repetitions se traduisent une fois (148 notes d'arrosage pour 172 fiches,
  et treize descriptions de sol pour tout le catalogue) ;
- `build_catalog.py` refuse de compiler s'il manque une traduction, donc une
  fiche ajoutee sans son anglais est rattrapee a la construction et non chez
  l'utilisateur.

**Ces traductions ne sont pas plus sourcees que l'original.** Le catalogue
francais a ete ecrit de memoire horticole (voir CLAUDE.md) ; le traduire ne lui
ajoute aucune autorite. Les noms communs retenus sont ceux qu'emploie le
jardinage anglophone — « courgette » plutot que « zucchini » serait un choix
britannique, « zucchini » un choix americain : on garde le terme le plus
largement compris, et le nom latin reste dans la fiche pour trancher.
"""

from __future__ import annotations

# --- Noms des cultures, par identifiant ---------------------------------------

NOMS = {
    "abricotier": "Apricot tree",
    "ail-blanc": "White garlic",
    "ail-ours": "Wild garlic",
    "ail-rose": "Pink garlic",
    "amandier": "Almond tree",
    "amarante": "Amaranth",
    "aneth": "Dill",
    "angelique": "Angelica",
    "argousier": "Sea buckthorn",
    "arroche": "Orache",
    "artichaut": "Globe artichoke",
    "asperge": "Asparagus",
    "aubergine": "Aubergine",
    "avoine": "Oats (green manure)",
    "basilic": "Basil",
    "betterave": "Beetroot",
    "blette": "Chard",
    "bourrache": "Borage",
    "brocoli": "Broccoli",
    "camerisier": "Honeyberry",
    "camomille": "Roman chamomile",
    "capucine": "Nasturtium",
    "cardon": "Cardoon",
    "carotte": "Carrot",
    "cassissier": "Blackcurrant",
    "celeri-branche": "Celery",
    "celeri-couper": "Leaf celery",
    "celeri-rave": "Celeriac",
    "cerfeuil": "Chervil",
    "cerisier": "Cherry tree",
    "chataignier": "Sweet chestnut",
    "chayotte": "Chayote",
    "chervis": "Skirret",
    "chicoree-frisee": "Curly endive",
    "chou-bruxelles": "Brussels sprouts",
    "chou-cabus": "White cabbage",
    "chou-chinois": "Pak choi",
    "chou-daubenton": "Daubenton perennial kale",
    "chou-fleur": "Cauliflower",
    "chou-kale": "Kale",
    "chou-milan": "Savoy cabbage",
    "chou-rave": "Kohlrabi",
    "chou-rouge": "Red cabbage",
    "ciboule": "Welsh onion",
    "ciboulette": "Chives",
    "citrouille": "Pumpkin",
    "claytone": "Miner's lettuce",
    "cognassier": "Quince tree",
    "concombre": "Cucumber",
    "consoude": "Comfrey",
    "coriandre": "Coriander",
    "cornichon": "Gherkin",
    "cosmos": "Cosmos",
    "courge-butternut": "Butternut squash",
    "courge-muscade": "Musquée de Provence squash",
    "courge-spaghetti": "Spaghetti squash",
    "courgette": "Courgette",
    "cresson-alenois": "Garden cress",
    "cresson-fontaine": "Watercress",
    "crosne": "Chinese artichoke",
    "daikon": "Daikon radish",
    "echalote": "Shallot",
    "edamame": "Edamame soybean",
    "endive": "Belgian endive",
    "epinard": "Spinach",
    "epinard-perpetuel": "Perpetual spinach (Good-King-Henry)",
    "estragon": "Tarragon",
    "fenouil-aromatique": "Herb fennel",
    "fenouil-bulbeux": "Florence fennel",
    "feve": "Broad bean",
    "figuier": "Fig tree",
    "fraisier": "Strawberry",
    "fraisier-remontant": "Everbearing strawberry",
    "framboisier": "Raspberry",
    "framboisier-remontant": "Autumn raspberry",
    "goji": "Goji berry",
    "gombo": "Okra",
    "groseillier": "Redcurrant",
    "groseillier-maquereau": "Gooseberry",
    "haricot-a-rames": "Climbing French bean",
    "haricot-espagne": "Runner bean",
    "haricot-nain": "Dwarf French bean",
    "haricot-sec": "Drying bean",
    "houblon": "Hop",
    "hysope": "Hyssop",
    "kaki": "Persimmon",
    "kiwi": "Kiwi",
    "laitue": "Lettuce",
    "laitue-hiver": "Winter lettuce",
    "laurier-sauce": "Bay laurel",
    "lavande": "Lavender",
    "lentille": "Lentil",
    "liveche": "Lovage",
    "mache": "Lamb's lettuce",
    "mais-doux": "Sweetcorn",
    "mais-popcorn": "Popcorn maize",
    "marjolaine": "Marjoram",
    "mauve": "Common mallow",
    "melisse": "Lemon balm",
    "melon": "Melon",
    "menthe": "Mint",
    "mizuna": "Mizuna",
    "moutarde-blanche": "White mustard (green manure)",
    "murier": "Blackberry",
    "myrtillier": "Blueberry",
    "nashi": "Nashi pear",
    "navet": "Turnip",
    "neflier": "Medlar",
    "noisetier": "Hazel",
    "noyer": "Walnut tree",
    "oca-perou": "Oca",
    "oeillet-inde": "French marigold",
    "oignon-blanc": "Spring onion",
    "oignon-jaune": "Yellow onion",
    "oignon-rocambole": "Walking onion",
    "oignon-rouge": "Red onion",
    "origan": "Oregano",
    "oseille": "Sorrel",
    "pain-de-sucre": "Sugarloaf chicory",
    "panais": "Parsnip",
    "pasteque": "Watermelon",
    "patate-douce": "Sweet potato",
    "patisson": "Pattypan squash",
    "pecher": "Peach tree",
    "persil": "Parsley",
    "persil-tubereux": "Turnip-rooted parsley",
    "petit-pois": "Garden pea",
    "phacelie": "Phacelia",
    "physalis": "Cape gooseberry",
    "piment": "Chilli pepper",
    "poireau": "Leek",
    "poireau-perpetuel": "Perennial leek",
    "poirier": "Pear tree",
    "pois-chiche": "Chickpea",
    "pois-mange-tout": "Mangetout pea",
    "poivron": "Sweet pepper",
    "pomme-de-terre": "Potato",
    "pommier": "Apple tree",
    "potimarron": "Red kuri squash",
    "pourpier": "Summer purslane",
    "prunier": "Plum tree",
    "quinoa": "Quinoa",
    "radis": "Radish",
    "radis-noir": "Black winter radish",
    "raifort": "Horseradish",
    "rhubarbe": "Rhubarb",
    "romarin": "Rosemary",
    "roquette": "Rocket",
    "roquette-vivace": "Perennial wall rocket",
    "rutabaga": "Swede",
    "salsifis": "Salsify",
    "sarrasin": "Buckwheat (green manure)",
    "sarriette": "Summer savory",
    "sauge": "Sage",
    "scarole": "Escarole",
    "scorsonere": "Scorzonera",
    "seigle": "Rye (green manure)",
    "shiso": "Shiso",
    "souci": "Pot marigold",
    "sureau-noir": "Black elder",
    "tetragone": "New Zealand spinach",
    "thym": "Thyme",
    "tomate": "Tomato",
    "tomate-cerise": "Cherry tomato",
    "tomatille": "Tomatillo",
    "topinambour": "Jerusalem artichoke",
    "tournesol": "Sunflower",
    "trefle-incarnat": "Crimson clover (green manure)",
    "trevise": "Radicchio",
    "verveine-citronnelle": "Lemon verbena",
    "vesce": "Winter vetch (green manure)",
    "vigne-table": "Grapevine (table grapes)",
}


# --- Familles botaniques ------------------------------------------------------
#
# Le nom francais reste la cle du catalogue : `rotation.DELAIS` s'indexe dessus
# pour decider du delai de retour d'une famille sur la meme parcelle. Ne jamais
# traduire ces cles, seulement leurs valeurs.

FAMILLES = {
    "Actinidiacées": "Actinidiaceae",
    "Adoxacées": "Adoxaceae",
    "Aizoacées": "Aizoaceae",
    "Amaranthacées": "Amaranthaceae",
    "Amaryllidacées": "Amaryllidaceae",
    "Apiacées": "Apiaceae",
    "Asparagacées": "Asparagaceae",
    "Astéracées": "Asteraceae",
    "Boraginacées": "Boraginaceae",
    "Brassicacées": "Brassicaceae",
    "Bétulacées": "Betulaceae",
    "Cannabacées": "Cannabaceae",
    "Caprifoliacées": "Caprifoliaceae",
    "Convolvulacées": "Convolvulaceae",
    "Cucurbitacées": "Cucurbitaceae",
    "Fabacées": "Fabaceae",
    "Fagacées": "Fagaceae",
    "Grossulariacées": "Grossulariaceae",
    "Juglandacées": "Juglandaceae",
    "Lamiacées": "Lamiaceae",
    "Lauracées": "Lauraceae",
    "Malvacées": "Malvaceae",
    "Montiacées": "Montiaceae",
    "Moracées": "Moraceae",
    "Oxalidacées": "Oxalidaceae",
    "Poacées": "Poaceae",
    "Polygonacées": "Polygonaceae",
    "Portulacacées": "Portulacaceae",
    "Rosacées": "Rosaceae",
    "Solanacées": "Solanaceae",
    "Tropaeolacées": "Tropaeolaceae",
    "Verbénacées": "Verbenaceae",
    "Vitacées": "Vitaceae",
    "Ébénacées": "Ebenaceae",
    "Éléagnacées": "Elaeagnaceae",
    "Éricacées": "Ericaceae",
}


# --- Descriptions de sol ------------------------------------------------------

SOLS = {
    "riche en humus, frais et bien drainé": (
        "rich in humus, moist and well drained"
    ),
    "ordinaire, bien drainé": "ordinary, well drained",
    "léger, meuble, sans cailloux": "light, loose, free of stones",
    "pauvre, caillouteux, très drainé": "poor, stony, very free draining",
    "pauvre, même ingrat": "poor, even downright unpromising",
    "pauvre, sableux, très drainé": "poor, sandy, very free draining",
    "pauvre, sinon elle fait des feuilles et pas de fleurs": (
        "poor, or it makes leaves instead of flowers"
    ),
    "acide, drainé, sans calcaire": "acid, free draining, lime-free",
    "pauvre : trop riche, il ne fait que des feuilles": (
        "poor: too rich and it makes nothing but leaves"
    ),
    "toujours détrempé, au bord de l'eau": "permanently wet, at the water's edge",
    "acide (pH 4-5), terre de bruyère": "acid (pH 4-5), ericaceous compost",
    "léger, calcaire, très drainé": "light, chalky, very free draining",
    "caillouteux, drainé, même pauvre": "stony, free draining, poor is fine",
}


# --- Notes d'arrosage ---------------------------------------------------------
#
# Indexees par la note francaise : plusieurs fiches partagent la meme, et une
# note repetee ne se traduit qu'une fois.

EAU_NOTES = {
    "Aime avoir les pieds au frais, presque humides.": (
        "Likes its feet cool, almost damp."
    ),
    "Aime la fraîcheur et la mi-ombre.": "Likes cool soil and partial shade.",
    "Aime la fraîcheur, comme toutes les apiacées.": (
        "Likes cool soil, like every apiaceae."
    ),
    "Aime la fraîcheur, plus exigeant que le groseillier.": (
        "Likes cool soil, thirstier than the redcurrant."
    ),
    "Aime la fraîcheur, redoute la sécheresse estivale.": (
        "Likes cool soil, suffers in summer drought."
    ),
    "Aime la fraîcheur.": "Likes cool soil.",
    "Aime les sols frais ; arroser en été.": (
        "Likes moist soil; water through the summer."
    ),
    "Aime les sols frais ; elle monte si elle a soif.": (
        "Likes moist soil; it bolts when thirsty."
    ),
    "Aime les sols frais ; pailler plutôt qu'arroser beaucoup.": (
        "Likes moist soil; mulch rather than water heavily."
    ),
    "Aime les sols frais et ombragés de sous-bois.": (
        "Likes the cool, shaded soil of woodland."
    ),
    "Aime les sols frais et profonds.": "Likes deep, moist soil.",
    "Aime les sols frais, mais ne demande aucun arrosage une fois pris.": (
        "Likes moist soil, but asks for nothing once established."
    ),
    "Aime les sols humides et frais, au bord de l'eau si possible.": (
        "Likes wet, cool soil, by water if you can."
    ),
    "Aime les sols riches et frais.": "Likes rich, moist soil.",
    "Arrosage régulier, sinon les fruits avortent.": (
        "Water regularly, or the fruit aborts."
    ),
    "Arrosages copieux mais espacés ; couper l'eau à l'approche de la récolte.": (
        "Generous but infrequent watering; cut the water off as harvest nears."
    ),
    "Arroser en été pour grossir les tubercules.": (
        "Water in summer to swell the tubers."
    ),
    "Arroser en été, mais jamais le feuillage.": (
        "Water in summer, but never the foliage."
    ),
    "Arroser les trois premières années, puis plus rien.": (
        "Water for the first three years, then nothing."
    ),
    "Assoiffé à la floraison, comme le maïs doux.": (
        "Thirsty at flowering, like sweetcorn."
    ),
    "Au pied uniquement : le cœur mouillé pourrit.": (
        "At the base only: a wet crown rots."
    ),
    "Au pied, jamais sur le feuillage : c'est ainsi qu'arrive le mildiou.": (
        "At the base, never on the foliage: that is how blight arrives."
    ),
    "Aucun arrosage : elle meurt d'excès d'eau, jamais de sécheresse.": (
        "No watering: it dies of too much water, never of drought."
    ),
    "Aucun arrosage : il pousse dans les dunes.": (
        "No watering: it grows in sand dunes."
    ),
    "Aucun arrosage une fois installé.": "No watering once established.",
    "Aucun arrosage une fois établi, sauf été de canicule les 3 premières années.": (
        "No watering once established, apart from heatwave summers in the first "
        "three years."
    ),
    "Aucun arrosage une fois établi.": "No watering once established.",
    "Aucun arrosage.": "No watering.",
    "Beaucoup d'eau, au pied, sans mouiller les feuilles.": (
        "Plenty of water, at the base, without wetting the leaves."
    ),
    "Comme la butternut : copieux et espacés.": (
        "Like butternut: generous and infrequent."
    ),
    "Comme la courgette : beaucoup d'eau au pied.": (
        "Like courgette: plenty of water at the base."
    ),
    "Comme le chou pommé.": "Same as white cabbage.",
    "Comme le fraisier classique, mais sur une période bien plus longue.": (
        "Like an ordinary strawberry, but over a far longer season."
    ),
    "Comme le jaune : sobre.": "Like the yellow one: frugal.",
    "Comme le melon : couper l'eau en fin de cycle.": (
        "Like melon: cut the water off at the end of the cycle."
    ),
    "Comme le non remontant.": "Same as the summer-fruiting kind.",
    "Comme le petit pois.": "Same as the garden pea.",
    "Copieux mais espacés ; couper l'eau à l'approche de la récolte.": (
        "Generous but infrequent; cut the water off as harvest nears."
    ),
    "Craint la sécheresse à la floraison.": "Suffers from drought at flowering.",
    "Eau non calcaire impérative : eau de pluie si possible.": (
        "Lime-free water is essential: rainwater if you can."
    ),
    "Garder frais ; elle apprécie la mi-ombre.": (
        "Keep it moist; it appreciates partial shade."
    ),
    "Garder frais ; il aime la mi-ombre.": (
        "Keep it moist; it likes partial shade."
    ),
    "Garder frais jusqu'à la levée, puis l'oublier.": (
        "Keep moist until it germinates, then forget it."
    ),
    "Gourmande en eau dès la formation des fruits.": (
        "Thirsty from the moment the fruit sets."
    ),
    "Gros besoins en été ; le feuillage flétrit vite s'il manque d'eau.": (
        "Thirsty in summer; the foliage wilts quickly when water runs short."
    ),
    "Gros buveur en été, à sevrer en fin de cycle.": (
        "A heavy drinker in summer, to be weaned off at the end of the cycle."
    ),
    "Généreux : la sécheresse le fait monter en graines aussitôt.": (
        "Generous: drought sends it straight to seed."
    ),
    "Généreux en été, surtout la première année.": (
        "Generous in summer, especially in the first year."
    ),
    "Humidité constante jusqu'à la levée, qui est lente (15 à 20 jours).": (
        "Constant moisture until it germinates, which is slow (15 to 20 days)."
    ),
    "Jamais sec : un radis qui a soif devient piquant et creux.": (
        "Never dry: a thirsty radish turns hot and hollow."
    ),
    "Jamais sec, comme tous les céleris.": "Never dry, like every celery.",
    "Jamais sec, jamais : c'est une plante de marais.": (
        "Never dry, ever: this is a marsh plant."
    ),
    "Jamais sec, sinon il monte immédiatement.": (
        "Never dry, or it bolts straight away."
    ),
    "Jamais à sec : c'est la culture la plus assoiffée du potager.": (
        "Never dry: this is the thirstiest crop in the garden."
    ),
    "Laisser sécher légèrement entre deux arrosages : le piment gagne en force.": (
        "Let it dry out a little between waterings: the chilli gets hotter."
    ),
    "Le matin, au pied : l'eau sur les feuilles au soleil les brûle.": (
        "In the morning, at the base: water on the leaves in full sun scorches "
        "them."
    ),
    "Le matin, au pied ; jamais le soir, l'humidité nocturne le fait noircir.": (
        "In the morning, at the base; never in the evening, night damp turns it "
        "black."
    ),
    "Le plus exigeant des choux : un coup de sec et la pomme avorte.": (
        "The thirstiest of the cabbages: one dry spell and the head aborts."
    ),
    "Les pieds littéralement dans l'eau : bac, mare ou ruisseau.": (
        "Feet literally in water: a tub, a pond or a stream."
    ),
    "Modéré ; bien plus tolérante que l'épinard.": (
        "Moderate; far more forgiving than spinach."
    ),
    "Modéré ; craint l'eau stagnante en hiver.": (
        "Moderate; dislikes standing water in winter."
    ),
    "Modéré ; elle craint surtout l'humidité hivernale.": (
        "Moderate; what it really fears is winter damp."
    ),
    "Modéré ; elle grossit surtout à l'automne.": (
        "Moderate; it mostly bulks up in autumn."
    ),
    "Modéré ; il supporte bien la mi-ombre.": (
        "Moderate; it copes well with partial shade."
    ),
    "Modéré ; le froid fait le reste.": "Moderate; the cold does the rest.",
    "Modéré ; redoute l'humidité stagnante l'hiver.": (
        "Moderate; fears standing damp in winter."
    ),
    "Modéré ; ses racines descendent chercher loin.": (
        "Moderate; its roots go down a long way to find water."
    ),
    "Modéré ; supporte la mi-ombre.": "Moderate; tolerates partial shade.",
    "Modéré ; très tolérant.": "Moderate; very forgiving.",
    "Modéré et régulier.": "Moderate and regular.",
    "Modéré, bien plus tolérante que l'épinard.": (
        "Moderate, far more forgiving than spinach."
    ),
    "Modéré, l'hiver fournit l'essentiel.": (
        "Moderate, winter supplies most of it."
    ),
    "Modéré.": "Moderate.",
    "Ne jamais arroser : l'ail déteste l'humidité.": (
        "Never water: garlic hates damp."
    ),
    "Ne jamais arroser : l'excès d'eau la fait verser.": (
        "Never water: too much and it flops over."
    ),
    "Ne jamais arroser en pleine terre : il meurt d'excès d'eau, pas de sécheresse.": (
        "Never water it in open ground: it dies of too much water, not of drought."
    ),
    "Ne pas arroser : la vigne cherche l'eau en profondeur et gagne en sucre au sec.": (
        "Do not water: the vine finds water deep down and sweetens when kept dry."
    ),
    "Ne pas arroser avant la levée, puis régulièrement à la floraison.": (
        "Do not water before germination, then regularly at flowering."
    ),
    "Ne pas arroser en période de fruits : les cerises éclatent.": (
        "Do not water while it is in fruit: the cherries split."
    ),
    "Peu d'arrosage une fois installé, la racine va chercher loin.": (
        "Little watering once established, the root reaches a long way."
    ),
    "Peu exigeant, très résistant.": "Undemanding, very tough.",
    "Peu exigeante, l'hiver s'en charge.": "Undemanding, winter sees to it.",
    "Plus tolérante que la grosse tomate, mais garder le sol frais.": (
        "More forgiving than a large tomato, but keep the soil moist."
    ),
    "Presque aucun arrosage.": "Almost no watering at all.",
    "Rustique et sobre.": "Hardy and frugal.",
    "Réduire fortement l'eau dix jours avant la récolte : c'est ce qui fait le sucre.": (
        "Cut the water right back ten days before harvest: that is what makes "
        "the sugar."
    ),
    "Régulier : un à-coup le rend ligneux.": (
        "Regular: an interruption turns it woody."
    ),
    "Régulier ; au pied uniquement.": "Regular; at the base only.",
    "Régulier ; il flétrit vite au sec.": "Regular; it wilts quickly when dry.",
    "Régulier ; il jaunit s'il a soif.": "Regular; it yellows when thirsty.",
    "Régulier ; le sec la fait monter aussitôt.": (
        "Regular; dryness sends it to seed at once."
    ),
    "Régulier ; le sec la rend très piquante.": (
        "Regular; dryness makes it very hot."
    ),
    "Régulier ; très tolérante par ailleurs.": (
        "Regular; otherwise very forgiving."
    ),
    "Régulier au départ, la levée est lente.": (
        "Regular at the start, germination is slow."
    ),
    "Régulier dès la floraison.": "Regular from flowering onwards.",
    "Régulier et généreux.": "Regular and generous.",
    "Régulier et sans excès ; craint l'eau stagnante.": (
        "Regular and never excessive; dislikes standing water."
    ),
    "Régulier pendant la formation de la racine.": (
        "Regular while the root is forming."
    ),
    "Régulier à la floraison, moment où les tubercules se forment.": (
        "Regular at flowering, which is when the tubers form."
    ),
    "Régulier à la floraison.": "Regular at flowering.",
    "Régulier, au pied : l'eau sur les fruits les fait pourrir.": (
        "Regular, at the base: water on the fruit makes it rot."
    ),
    "Régulier, elle aime la fraîcheur.": "Regular, it likes cool soil.",
    "Régulier, il n'aime pas les à-coups.": (
        "Regular, it does not like interruptions."
    ),
    "Régulier, mais il déteste les pieds mouillés.": (
        "Regular, but it hates wet feet."
    ),
    "Régulier, sinon elle devient très piquante et monte.": (
        "Regular, or it turns very hot and bolts."
    ),
    "Régulier, sinon il monte sans faire de bulbe.": (
        "Regular, or it bolts without making a bulb."
    ),
    "Régulier, sinon la racine devient piquante et creuse.": (
        "Regular, or the root turns hot and hollow."
    ),
    "Régulier, sinon la racine se fend.": "Regular, or the root splits.",
    "Régulier, surtout après la plantation.": (
        "Regular, especially after planting out."
    ),
    "Résiste très bien au sec : ne pas arroser hors période de semis.": (
        "Stands drought very well: do not water outside the sowing period."
    ),
    "Se débrouille seul, même en sol pauvre.": (
        "Manages on its own, even in poor soil."
    ),
    "Sobre : une méditerranéenne de plus.": (
        "Frugal: one more Mediterranean plant."
    ),
    "Sobre ; arrêter l'arrosage dès que les gousses jaunissent.": (
        "Frugal; stop watering as soon as the pods turn yellow."
    ),
    "Sobre ; craint l'humidité hivernale.": "Frugal; fears winter damp.",
    "Sobre ; redoute l'humidité.": "Frugal; dislikes damp.",
    "Sobre ; trop d'eau et d'engrais la font monter en feuilles.": (
        "Frugal; too much water and feed send it to leaf."
    ),
    "Sobre après la levée.": "Frugal once it has germinated.",
    "Sobre une fois installé ; il se débrouille seul.": (
        "Frugal once established; it manages on its own."
    ),
    "Sobre une fois installé.": "Frugal once established.",
    "Sobre une fois installée.": "Frugal once established.",
    "Sobre une fois levée.": "Frugal once it has germinated.",
    "Sobre, comme toutes les méditerranéennes.": (
        "Frugal, like every Mediterranean plant."
    ),
    "Sobre.": "Frugal.",
    "Soutenu : c'est un gros buveur.": "Sustained: this one drinks heavily.",
    "Soutenu pendant la formation de la pomme.": (
        "Sustained while the head is forming."
    ),
    "Soutenu à la formation de la pomme.": (
        "Sustained as the head forms."
    ),
    "Soutenu à la formation des gousses.": "Sustained as the pods form.",
    "Supporte bien un léger stress hydrique.": (
        "Copes well with a little water stress."
    ),
    "Supporte le sec mieux que la tomate.": (
        "Stands dry conditions better than a tomato."
    ),
    "Supporte le sec une fois installée.": (
        "Stands dry conditions once established."
    ),
    "Supporte très bien la sécheresse : c'est une plante grasse.": (
        "Stands drought very well: it is a succulent."
    ),
    "Supporte très bien la sécheresse.": "Stands drought very well.",
    "Toujours humide.": "Always damp.",
    "Très assoiffé à la floraison : ne jamais laisser sécher à ce stade.": (
        "Very thirsty at flowering: never let it dry out at that stage."
    ),
    "Très gourmande en eau pendant toute la végétation.": (
        "Very thirsty throughout its growing season."
    ),
    "Très peu d'eau : l'excès fait pourrir le bulbe.": (
        "Very little water: too much rots the bulb."
    ),
    "Très peu d'eau, comme tous les oignons.": (
        "Very little water, like every onion."
    ),
    "Très sobre : il vient de l'Altiplano.": (
        "Very frugal: it comes from the Altiplano."
    ),
    "Très sobre ; il redoute l'humidité bien plus que la sécheresse.": (
        "Very frugal; it fears damp far more than drought."
    ),
    "Très sobre ; trop d'eau dilue le goût des figues.": (
        "Very frugal; too much water waters down the figs."
    ),
    "Très sobre une fois installé.": "Very frugal once established.",
    "Très sobre, bien plus que la roquette annuelle.": (
        "Very frugal, far more so than annual rocket."
    ),
    "Très sobre, il préfère le sec.": "Very frugal, it prefers dry conditions.",
    "Très sobre.": "Very frugal.",
    "Un arrosage irrégulier le rend fibreux.": (
        "Irregular watering turns it stringy."
    ),
    "Un manque d'eau rend les fruits amers.": (
        "A shortage of water makes the fruit bitter."
    ),
    "Un peu plus exigeant en eau que le poirier européen.": (
        "A little thirstier than a European pear."
    ),
    "Volume d'eau important, surtout pendant le grossissement.": (
        "Large volumes of water, especially while it is bulking up."
    ),
}


# --- Conseils de culture ------------------------------------------------------
#
# Indexes par le conseil francais, comme les notes d'arrosage : le meme conseil
# sert parfois a deux fiches voisines.

CONSEILS = {
    "Aimant à bourdons : elle fait grimper la pollinisation des courgettes": (
        "A bumblebee magnet: it lifts courgette pollination sharply"
    ),
    "Aimant à syrphes et à chrysopes, dont les larves mangent les pucerons": (
        "A magnet for hoverflies and lacewings, whose larvae eat aphids"
    ),
    "Arracher les plants entiers et les faire sécher tête en bas": (
        "Pull whole plants and hang them upside down to dry"
    ),
    "Arracher les plants entiers quand les gousses du bas brunissent": (
        "Pull whole plants once the lower pods turn brown"
    ),
    "Arracher les racines en novembre et les forcer en cave par lots": (
        "Lift the roots in November and force them in batches in the cellar"
    ),
    "Attire les syrphes, dont les larves dévorent les pucerons": (
        "Draws hoverflies, whose larvae devour aphids"
    ),
    "Aussi envahissant que le topinambour : le cantonner dans un bac": (
        "As invasive as a Jerusalem artichoke: confine it to a container"
    ),
    "Autofertile : un seul arbre suffit": "Self-fertile: one tree is enough",
    "Bien plus facile que le céleri branche, et aussi parfumé": (
        "Far easier than celery, and just as fragrant"
    ),
    "Bisannuel : il monte en graines la deuxième année, mieux vaut le ressemer": (
        "Biennial: it goes to seed in the second year, better to sow again"
    ),
    "Bisannuelle : elle fleurit et meurt la deuxième année, mais se ressème": (
        "Biennial: it flowers and dies in the second year, but self-seeds"
    ),
    "Blanchir 5 minutes dans l'eau salée, puis déguster à la main": (
        "Blanch five minutes in salted water, then eat with your fingers"
    ),
    "Bouture très facilement : une branche dans un verre d'eau": (
        "Strikes very easily: a sprig in a glass of water"
    ),
    "Butter dès que les plants atteignent 20 cm": (
        "Earth up as soon as the plants reach 20 cm"
    ),
    "Butter la griffe au printemps pour obtenir des asperges blanches": (
        "Earth up the crown in spring to get white spears"
    ),
    "Butter ou lier en fin de culture pour blanchir les côtes": (
        "Earth up or tie late in the season to blanch the stalks"
    ),
    "Butter progressivement pour allonger le blanc": (
        "Earth up gradually to lengthen the white shank"
    ),
    "C'est le froid qui fait rougir les feuilles : ne pas récolter trop tôt": (
        "Cold is what reddens the leaves: do not harvest too early"
    ),
    "Casser une feuille sur la pomme pour la garder blanche": (
        "Snap a leaf over the head to keep it white"
    ),
    "Chaleur indispensable : attendre un sol à 15 °C": (
        "Warmth is essential: wait for the soil to reach 15 °C"
    ),
    "Chaque graine donne plusieurs plants : éclaircir à 10 cm": (
        "Each seed gives several plants: thin to 10 cm"
    ),
    "Choisir la variété Bocking 14, stérile : les autres envahissent tout": (
        "Choose the sterile Bocking 14: the others take over everything"
    ),
    "Choisir une variété non astringente si l'on veut croquer le fruit ferme": (
        "Choose a non-astringent variety if you want to eat the fruit firm"
    ),
    "Choisir une variété sans épines, la cueillette change de nature": (
        "Choose a thornless variety, picking becomes another matter entirely"
    ),
    "Comme le panais, le gel l'adoucit": "Like parsnip, frost sweetens it",
    "Coucher le feuillage en fin de cycle pour hâter la maturité": (
        "Bend the foliage over at the end of the cycle to hasten ripening"
    ),
    "Couper la tête centrale incite les rejets latéraux à se développer": (
        "Cutting the central head pushes the side shoots to develop"
    ),
    "Couper le fût au ras du sol : il repousse depuis la souche": (
        "Cut the stem at ground level: it regrows from the stool"
    ),
    "Couper les feuilles extérieures, le pied continue de produire": (
        "Pick the outer leaves and the plant keeps producing"
    ),
    "Couper les fleurs pour que le bulbe grossisse": (
        "Cut the flowers off so the bulb swells"
    ),
    "Couper les hampes florales dès qu'elles montent, pour garder les feuilles tendres": (
        "Cut the flower stems as soon as they rise, to keep the leaves tender"
    ),
    "Couper à 3 cm du sol, elle repousse trois à quatre fois par saison": (
        "Cut 3 cm above the ground, it regrows three or four times a season"
    ),
    "Craint le froid plus que tout : attendre la mi-mai dehors": (
        "Fears cold above all: wait until mid-May outdoors"
    ),
    "Croquant comme une pomme, juteux comme une poire": (
        "Crisp as an apple, juicy as a pear"
    ),
    "Cueillir les feuilles du bas, le pied continue de monter": (
        "Pick the bottom leaves, the plant keeps growing upward"
    ),
    "Cueillir les gousses à 7-8 cm, elles deviennent filandreuses ensuite": (
        "Pick the pods at 7-8 cm, they turn stringy after that"
    ),
    "Cueillir légèrement avant maturité et finir en fruitier": (
        "Pick slightly before ripeness and finish them indoors"
    ),
    "Cueillir quand le duvet s'efface et que le parfum embaume": (
        "Pick when the down fades and the scent fills the air"
    ),
    "Cueillir tous les deux jours au plus fort de la production": (
        "Pick every other day at the height of production"
    ),
    "Culture d'arrière-saison : semé en juillet-août, il ne monte pas": (
        "A late-season crop: sown in July or August, it does not bolt"
    ),
    "Culture d'automne et de printemps : l'été le fait monter": (
        "An autumn and spring crop: summer makes it bolt"
    ),
    "Demande une vraie chaleur : serre ou mur plein sud sous climat océanique": (
        "Needs real heat: a greenhouse or a south wall in a maritime climate"
    ),
    "Deux pieds minimum : elle ne se féconde pas elle-même": (
        "Two plants at least: it does not fertilise itself"
    ),
    "Deux plants suffisent pour une famille": (
        "Two plants are enough for a family"
    ),
    "Deux récoltes : les fleurs en juin pour le sirop, les baies en août": (
        "Two harvests: the flowers in June for cordial, the berries in August"
    ),
    "Deux temps : la racine au jardin l'été, le forçage à l'obscurité l'hiver": (
        "Two stages: the root in the garden in summer, forcing in the dark in "
        "winter"
    ),
    "Deux variétés différentes pour la pollinisation": (
        "Two different varieties for pollination"
    ),
    "Deux variétés différentes sont indispensables pour fructifier": (
        "Two different varieties are essential for it to set fruit"
    ),
    "Deux variétés pour la pollinisation, et vingt mètres de dégagement": (
        "Two varieties for pollination, and twenty metres of clearance"
    ),
    "Devient un arbre : prévoir la place ou le tailler en boule": (
        "It becomes a tree: allow the space or keep it clipped to a ball"
    ),
    "Dicton fiable : plantée en février, récoltée en juillet": (
        "A reliable saying: planted in February, harvested in July"
    ),
    "Diviser la touffe tous les 3 ans": "Divide the clump every three years",
    "Diviser tous les 3 ans, il s'épuise": (
        "Divide every three years, it exhausts itself"
    ),
    "Double usage : feuilles en épinard tout l'été, graines à l'automne": (
        "Dual purpose: leaves as spinach all summer, seed in autumn"
    ),
    "Drageonne beaucoup : poser une barrière anti-rhizome": (
        "Suckers freely: put in a root barrier"
    ),
    "Dégager la base de la boule en fin d'été pour qu'elle grossisse": (
        "Clear soil from the base of the bulb in late summer so it swells"
    ),
    "Elle perd toutes ses feuilles l'hiver et repart tard : ne pas l'arracher trop vite": (
        "It drops every leaf in winter and starts late: do not pull it up too soon"
    ),
    "Engrais vert et pompe à pollinisateurs : à semer sur toute planche vide": (
        "Green manure and a pollinator pump: sow it on any empty bed"
    ),
    "Envahissante par semis spontané : couper les fleurs avant qu'elles montent": (
        "Invasive by self-seeding: cut the flowers before they run to seed"
    ),
    "Exige un été chaud : réserver la place la plus abritée du jardin": (
        "Demands a hot summer: give it the most sheltered spot in the garden"
    ),
    "Exige une longue saison chaude : à réserver aux étés francs": (
        "Demands a long warm season: keep it for proper summers"
    ),
    "Faire sécher au soleil une semaine avant de stocker": (
        "Dry in the sun for a week before storing"
    ),
    "Faire sécher les épis deux mois avant de tenter le premier pop": (
        "Dry the cobs for two months before trying your first pop"
    ),
    "Faucher avant la floraison et laisser sur place": (
        "Cut before flowering and leave it where it falls"
    ),
    "Faucher avant la montée en graines et laisser sur place": (
        "Cut before it runs to seed and leave it where it falls"
    ),
    "Fleurit du printemps aux gelées et se ressème seul": (
        "Flowers from spring to the frosts and self-seeds"
    ),
    "Fleurit jusqu'aux gelées et se ressème seul": (
        "Flowers until the frosts and self-seeds"
    ),
    "Fleurit tôt : éviter les fonds de vallée gélifs": (
        "Flowers early: avoid frost-prone valley bottoms"
    ),
    "Fleurs et jeunes feuilles comestibles, en salade ou en tisane": (
        "Flowers and young leaves are edible, in salad or as a tea"
    ),
    "Fleurs et jeunes feuilles se mangent, goût poivré": (
        "Flowers and young leaves are edible, peppery"
    ),
    "Fleurs rouges très décoratives, et comestibles": (
        "Very decorative red flowers, and edible"
    ),
    "Floraison en février : une gelée tardive suffit à supprimer la récolte": (
        "Flowers in February: one late frost is enough to wipe out the crop"
    ),
    "Floraison très précoce : une gelée de mars supprime la récolte": (
        "Flowers very early: a March frost wipes out the crop"
    ),
    "Fructifie sur le bois de l'année : tailler sévèrement les vieilles branches": (
        "Fruits on the current year's wood: prune the old branches hard"
    ),
    "Germination très lente (3 semaines) : tremper les graines une nuit": (
        "Very slow to germinate (three weeks): soak the seed overnight"
    ),
    "Glisser une planchette sous le fruit pour éviter qu'il pourrisse": (
        "Slide a board under the fruit to stop it rotting"
    ),
    "Goût de céleri en plus puissant : quelques feuilles suffisent": (
        "Celery flavour, only stronger: a few leaves are plenty"
    ),
    "Goût entre la menthe et le cumin : la feuille des sushis": (
        "Somewhere between mint and cumin: the sushi leaf"
    ),
    "Graines à renouveler chaque année, elles perdent vite leur pouvoir germinatif": (
        "Buy fresh seed each year, it loses viability quickly"
    ),
    "Gèle au premier froid, ce qui évite d'avoir à le faucher": (
        "Killed by the first cold, which saves you cutting it"
    ),
    "Gèle vers -12 °C et forme alors un paillage naturel : rien à faucher": (
        "Killed around -12 °C and then forms its own mulch: nothing to cut"
    ),
    "Idéale avant une culture exigeante au printemps suivant": (
        "Ideal ahead of a hungry crop the following spring"
    ),
    "Idéale en pot sur un balcon": "Ideal in a pot on a balcony",
    "Il assèche et épuise le sol : ne pas le mettre à côté d'un gourmand": (
        "It dries and exhausts the soil: do not put it next to a hungry crop"
    ),
    "Il produit ses bulbilles en haut de la tige, qui se replantent seules": (
        "It makes its bulbils at the top of the stem, which replant themselves"
    ),
    "Il se multiplie seul par bulbilles — diviser la touffe tous les 3 ans": (
        "It multiplies itself by bulbils — divide the clump every three years"
    ),
    "Impossible en pleine terre ordinaire : il lui faut l'eau courante ou un bac": (
        "Impossible in ordinary ground: it needs running water or a tub"
    ),
    "Installer les tuteurs avant de semer": "Put the supports in before sowing",
    "Jamais avant ni après un chou : même famille, mêmes maladies": (
        "Never before or after a brassica: same family, same diseases"
    ),
    "Jamais près du maïs doux : ils se croisent et gâchent les deux": (
        "Never near sweetcorn: they cross and spoil both"
    ),
    "L'engrais vert d'hiver le plus riche en azote": (
        "The winter green manure richest in nitrogen"
    ),
    "L'épinard des étés secs : elle monte beaucoup moins vite": (
        "The spinach for dry summers: it bolts far more slowly"
    ),
    "La boule pousse au-dessus du sol : ne jamais la butter": (
        "The bulb grows above ground: never earth it up"
    ),
    "La cloque est la difficulté principale : décoction de prêle dès le débourrement": (
        "Peach leaf curl is the main difficulty: horsetail decoction from bud "
        "break"
    ),
    "La salade d'hiver la plus facile : semée en juillet, récoltée en décembre": (
        "The easiest winter salad: sown in July, harvested in December"
    ),
    "La seule allium qui préfère l'ombre : idéale sous un arbre": (
        "The one allium that prefers shade: ideal under a tree"
    ),
    "La solution à l'épinard qui monte en été : elle ne monte pas": (
        "The answer to spinach bolting in summer: this one does not bolt"
    ),
    "Laisser ressuyer une semaine au soleil avant de stocker": (
        "Leave to dry off in the sun for a week before storing"
    ),
    "Laisser une tête sur pied : les mésanges s'en chargeront tout l'hiver": (
        "Leave one head standing: the tits will see to it all winter"
    ),
    "Le balanin perce les noisettes : ramasser et détruire les fruits tombés": (
        "The nut weevil bores into hazelnuts: gather and destroy the fallen nuts"
    ),
    "Le gel améliore son goût : le laisser en terre et récolter au besoin": (
        "Frost improves the flavour: leave it in the ground and lift as needed"
    ),
    "Le meilleur rapport effort/récolte du potager": (
        "The best effort-to-harvest ratio in the garden"
    ),
    "Le pire ennemi du thym est l'arrosoir": (
        "Thyme's worst enemy is the watering can"
    ),
    "Le plus facile des fruitiers à noyau sous climat océanique": (
        "The easiest stone fruit in a maritime climate"
    ),
    "Le plus facile et le plus rustique des choux : il produit tout l'hiver": (
        "The easiest and hardiest of the brassicas: it crops all winter"
    ),
    "Le plus parfumé juste avant la floraison : c'est le moment de le sécher": (
        "At its most fragrant just before flowering: that is the moment to dry it"
    ),
    "Le plus rapide du potager : parfait pour débuter": (
        "The fastest crop in the garden: perfect for a beginner"
    ),
    "Le plus rustique des engrais verts : il lève encore à 3 °C": (
        "The hardiest green manure: it still germinates at 3 °C"
    ),
    "Le poireau voisin éloigne la mouche de la carotte": (
        "A leek alongside keeps the carrot fly away"
    ),
    "Le tout premier fruit de l'année, avant même les fraises": (
        "The very first fruit of the year, even before strawberries"
    ),
    "Les baies crues sont indigestes : toujours les cuire": (
        "The raw berries are indigestible: always cook them"
    ),
    "Les fruits sont mûrs quand le calice est sec et qu'ils tombent seuls": (
        "The fruit is ripe when the husk is dry and it drops by itself"
    ),
    "Les graines portent une saponine amère : les rincer longuement": (
        "The seed carries a bitter saponin: rinse it thoroughly"
    ),
    "Les jeunes feuilles se mangent comme des épinards": (
        "The young leaves eat like spinach"
    ),
    "Les jeunes pousses de printemps se mangent comme des asperges": (
        "The young spring shoots eat like asparagus"
    ),
    "Les jeunes pousses se préparent comme des asperges": (
        "The young shoots are cooked like asparagus"
    ),
    "Les nèfles ne se mangent que blettes, après les premières gelées": (
        "Medlars are only edible bletted, after the first frosts"
    ),
    "Les tubercules ne se forment qu'aux jours courts, en octobre": (
        "The tubers only form in short days, in October"
    ),
    "Lier et emballer les côtes un mois avant la récolte pour les blanchir": (
        "Tie and wrap the stalks a month before harvest to blanch them"
    ),
    "Lier les feuilles deux semaines avant pour blanchir le cœur": (
        "Tie the leaves up two weeks beforehand to blanch the heart"
    ),
    "Lier les feuilles ou poser une assiette dessus pour blanchir le cœur": (
        "Tie the leaves up or lay a plate on top to blanch the heart"
    ),
    "Limiter à 4-5 fruits par plant": "Limit it to four or five fruits per plant",
    "Lui donner l'emplacement le plus abrité et le plus tardif à se réchauffer": (
        "Give it the most sheltered spot, and the last one to warm up"
    ),
    "Légume oublié, très sucré, à la mode avant la pomme de terre": (
        "A forgotten vegetable, very sweet, fashionable before the potato"
    ),
    "Mauvais voisin notoire : lui réserver un coin à l'écart": (
        "A notoriously bad neighbour: keep it in a corner of its own"
    ),
    "Mauvais voisin pour presque tout : lui donner un coin à part": (
        "A bad neighbour for almost everything: give it a corner of its own"
    ),
    "Meilleur après une gelée": "Better after a frost",
    "Monte très vite en été : semer peu et souvent, ou à l'ombre légère": (
        "Bolts very fast in summer: sow a little and often, or in light shade"
    ),
    "Monte à 2 m : à placer au fond du jardin": (
        "Reaches 2 m: put it at the back of the garden"
    ),
    "Monte à 2 m : à placer au fond, elle ferait de l'ombre à tout": (
        "Reaches 2 m: put it at the back, it would shade everything else"
    ),
    "Mûre quand le fruit fait éclater son calice": (
        "Ripe when the fruit bursts its husk"
    ),
    "Ne fructifie vraiment qu'à partir de la troisième année": (
        "It does not really fruit before the third year"
    ),
    "Ne jamais le confondre avec le muguet : froisser et sentir l'ail": (
        "Never confuse it with lily of the valley: crush a leaf and smell garlic"
    ),
    "Ne jamais replanter au même endroit avant 4 ans": (
        "Never replant in the same spot for four years"
    ),
    "Ne jamais récolter de cresson sauvage : risque de douve du foie": (
        "Never gather wild watercress: risk of liver fluke"
    ),
    "Ne pas enterrer la graine : elle a besoin de lumière pour germer": (
        "Do not bury the seed: it needs light to germinate"
    ),
    "Ne pas enterrer la pointe, elle doit affleurer": (
        "Do not bury the tip, it must sit at the surface"
    ),
    "Ne rien récolter la première année": "Harvest nothing in the first year",
    "Ne rien récolter la première année, le temps qu'il s'installe": (
        "Harvest nothing in the first year, while it settles in"
    ),
    "Non remontant : couper au sol les cannes qui ont fructifié": (
        "Summer-fruiting: cut the canes that have fruited to the ground"
    ),
    "Pailler avec une bâche ou de l'ardoise pour accumuler la chaleur": (
        "Mulch with sheeting or slate to store up heat"
    ),
    "Pailler dès juin pour stabiliser l'humidité": (
        "Mulch from June to even out the moisture"
    ),
    "Pailler le pied généreusement l'hiver, elle gèle facilement": (
        "Mulch the crown generously in winter, it frosts easily"
    ),
    "Pailler le pied l'hiver : c'est le gel qui tue les artichauts": (
        "Mulch the crown in winter: frost is what kills artichokes"
    ),
    "Pailler lourdement la souche pour la faire repartir l'an prochain": (
        "Mulch the stool heavily so it comes back next year"
    ),
    "Pailler pour garder les fruits propres et hors du sol": (
        "Mulch to keep the fruit clean and off the soil"
    ),
    "Palisser : laissé libre, il devient un buisson retombant ingérable": (
        "Train it: left alone it becomes an unmanageable sprawling bush"
    ),
    "Palisser sur deux fils : sans cela c'est un roncier": (
        "Train it on two wires: without that it is a bramble thicket"
    ),
    "Palisser sur un grillage et rabattre chaque hiver": (
        "Train it on a wire mesh and cut it back each winter"
    ),
    "Palisser à la verticale : fruits plus droits, moins de maladies": (
        "Train it vertically: straighter fruit, less disease"
    ),
    "Parfaitement adapté au climat de la Loire-Atlantique": (
        "Perfectly suited to the Loire-Atlantique climate"
    ),
    "Patience : aucune récolte les deux premières années, puis 15 ans de production": (
        "Patience: nothing for the first two years, then fifteen years of crops"
    ),
    "Petit arbre très rustique, et un des derniers fruits de l'année": (
        "A small, very hardy tree, and one of the last fruits of the year"
    ),
    "Pincer la première fleur pour renforcer le plant": (
        "Pinch out the first flower to strengthen the plant"
    ),
    "Pincer la tête en septembre pour grossir les choux du bas": (
        "Pinch out the top in September to swell the lower sprouts"
    ),
    "Pincer les fleurs dès qu'elles apparaissent : elles arrêtent la production de feuilles": (
        "Pinch out the flowers as they appear: they stop leaf production"
    ),
    "Pincer les têtes dès l'apparition des premiers pucerons": (
        "Pinch out the tips as soon as the first aphids show"
    ),
    "Plante-piège à pucerons : ils s'y installent plutôt que sur vos légumes": (
        "An aphid trap plant: they settle on it rather than on your vegetables"
    ),
    "Planter de l'ail au pied, vieux remède de jardinier contre la cloque": (
        "Plant garlic at its foot, an old gardener's remedy against leaf curl"
    ),
    "Planter deux variétés différentes pour une bonne pollinisation": (
        "Plant two different varieties for good pollination"
    ),
    "Planter en septembre pour récolter dès le printemps suivant": (
        "Plant in September to harvest the following spring"
    ),
    "Planter les boutures quand le sol atteint 15 °C": (
        "Plant the slips when the soil reaches 15 °C"
    ),
    "Planté en octobre-novembre, il profite du froid pour se diviser": (
        "Planted in October or November, it uses the cold to split"
    ),
    "Planté une fois, il se récolte toute l'année pendant des années": (
        "Planted once, it is harvested all year round for years"
    ),
    "Plantée près des choux, elle détourne la piéride": (
        "Planted near brassicas, it draws the cabbage white away"
    ),
    "Plantée près des haricots, elle éloigne les pucerons noirs": (
        "Planted near beans, it keeps blackfly away"
    ),
    "Plein sud contre un mur : c'est la chaleur restituée qui fait le raisin": (
        "Due south against a wall: the stored heat is what makes the grapes"
    ),
    "Plombez le semis en tapotant avec le dos du râteau": (
        "Firm the seedbed down with the back of the rake"
    ),
    "Plus douce et plus fine que l'origan, mais gélive : à rentrer ou ressemer": (
        "Milder and finer than oregano, but frost-tender: bring it in or sow again"
    ),
    "Plus il grossit, plus il devient cotonneux": (
        "The bigger it gets, the woollier it becomes"
    ),
    "Plus piquante et bien plus rustique que la roquette cultivée": (
        "Hotter and far hardier than cultivated rocket"
    ),
    "Plus rustique que le haricot vert : il supporte les étés frais": (
        "Hardier than a French bean: it copes with cool summers"
    ),
    "Poser une collerette en carton au pied contre la mouche du chou": (
        "Fit a cardboard collar at the base against cabbage root fly"
    ),
    "Pousse en six semaines sur toute planche vide": (
        "Grows in six weeks on any empty bed"
    ),
    "Pousse là où rien ne pousse, en plein cagnard": (
        "Grows where nothing else will, in full baking sun"
    ),
    "Pousse si vite qu'un semis de printemps et un d'automne suffisent": (
        "Grows so fast that one spring and one autumn sowing are enough"
    ),
    "Pousse vite et partout, y compris en haie": (
        "Grows fast and anywhere, hedges included"
    ),
    "Productif 4 à 5 ans, puis diviser les œilletons": (
        "Productive for four or five years, then split the offsets"
    ),
    "Produit par vagues de juin aux gelées": (
        "Crops in flushes from June to the frosts"
    ),
    "Produit plus longtemps que le nain": (
        "Crops over a longer period than the dwarf kind"
    ),
    "Protéger le pied l'hiver par un paillage sec": (
        "Protect the crown in winter with a dry mulch"
    ),
    "Préfère la mi-ombre : parfait au pied des plus grands": (
        "Prefers partial shade: perfect at the foot of taller plants"
    ),
    "Prévoir 10 m de dégagement, c'est un arbre de 20 m": (
        "Allow 10 m of clearance, this is a 20 m tree"
    ),
    "Prévoir une pergola solide : il devient très lourd": (
        "Allow for a sturdy pergola: it gets very heavy"
    ),
    "Prévoir une treille solide : une liane de 8 m en une saison": (
        "Allow for a sturdy trellis: an 8 m vine in one season"
    ),
    "Prêt en trois semaines : le plus rapide après le radis": (
        "Ready in three weeks: the fastest after radish"
    ),
    "Rabattre au sol en fin d'été pour une repousse tendre": (
        "Cut to the ground in late summer for tender regrowth"
    ),
    "Rabattre d'un tiers au printemps pour la garder compacte": (
        "Cut back by a third in spring to keep it compact"
    ),
    "Rabattre en juillet pour une repousse tendre": (
        "Cut back in July for tender regrowth"
    ),
    "Raccourcir racines et feuilles de moitié avant de planter": (
        "Trim roots and leaves back by half before planting"
    ),
    "Racine au goût de persil et de panais, feuillage utilisable aussi": (
        "A root tasting of parsley and parsnip, and the leaves are usable too"
    ),
    "Racine noire, chair plus fine que le salsifis": (
        "Black root, finer flesh than salsify"
    ),
    "Ramer dès 15 cm de hauteur": "Give it supports from 15 cm tall",
    "Redoute l'excès d'eau plus que la sécheresse": (
        "Fears too much water more than drought"
    ),
    "Refuse absolument le calcaire : inutile d'insister en sol crayeux": (
        "Flatly refuses lime: no point persisting on chalk"
    ),
    "Remplacer les pieds tous les 3 ans, le rendement s'effondre après": (
        "Replace the plants every three years, yield collapses after that"
    ),
    "Rien ne pousse sous un noyer : la juglone inhibe les voisins": (
        "Nothing grows under a walnut: juglone holds back the neighbours"
    ),
    "Récolter après le premier gel du feuillage, pas avant": (
        "Harvest after the foliage has been frosted, not before"
    ),
    "Récolter après les premières gelées et ne pas chercher à les conserver": (
        "Harvest after the first frosts and do not try to store them"
    ),
    "Récolter au fur et à mesure, il ne se conserve pas hors de terre": (
        "Lift as you need it, it does not keep out of the ground"
    ),
    "Récolter avant les gelées et laisser mûrir en cagette": (
        "Harvest before the frosts and let them ripen in a crate"
    ),
    "Récolter avant les premières gelées, le feuillage est très sensible": (
        "Harvest before the first frosts, the foliage is very tender"
    ),
    "Récolter avant que les grains ne s'écartent": (
        "Harvest before the beads start to separate"
    ),
    "Récolter feuille à feuille, jamais le pied entier": (
        "Harvest leaf by leaf, never the whole plant"
    ),
    "Récolter jeune et souvent : un plant freine dès qu'un fruit grossit": (
        "Harvest young and often: a plant slows down as soon as one fruit swells"
    ),
    "Récolter jeune, à la taille d'une balle de golf": (
        "Harvest young, at golf-ball size"
    ),
    "Récolter les gousses bien plates, avant que les grains ne se forment": (
        "Harvest the pods while flat, before the peas form"
    ),
    "Récolter quand l'écorce résiste à l'ongle, vers la mi-septembre": (
        "Harvest when the skin resists a fingernail, around mid-September"
    ),
    "Récolter quand le dos du capitule jaunit et que les graines se détachent": (
        "Harvest when the back of the head yellows and the seeds come loose"
    ),
    "Récolter quand le pédoncule est sec et liégeux": (
        "Harvest when the stalk is dry and corky"
    ),
    "Récolter quand le pédoncule se craquelle et que le parfum monte": (
        "Harvest when the stalk cracks and the scent rises"
    ),
    "Récolter quand les feuilles tombent et que la graine résiste à l'ongle": (
        "Harvest when the leaves drop and the seed resists a fingernail"
    ),
    "Récolter quand les soies brunissent": "Harvest when the silks turn brown",
    "Récolter tous les deux jours : un haricot oublié stoppe le plant": (
        "Harvest every other day: one forgotten bean stops the plant"
    ),
    "Récolter à la taille d'une balle de tennis, pas plus gros": (
        "Harvest at tennis-ball size, no bigger"
    ),
    "Résiste au froid bien mieux que la roquette": (
        "Stands cold far better than rocket"
    ),
    "Réussit en sol pauvre, là où rien d'autre ne donne": (
        "Succeeds in poor soil, where nothing else will crop"
    ),
    "Sa chair se défait en filaments à la cuisson, d'où son nom": (
        "The flesh falls apart into strands when cooked, hence the name"
    ),
    "Sa racine descend profond : ameublir sur 30 cm": (
        "Its root goes deep: loosen the soil to 30 cm"
    ),
    "Salade d'hiver increvable, elle pousse sous la neige": (
        "An indestructible winter salad, it grows under snow"
    ),
    "Se bouture en plantant simplement un rameau en terre": (
        "Strikes from a sprig simply pushed into the ground"
    ),
    "Se conserve moins longtemps que le jaune : à consommer en premier": (
        "Keeps less well than the yellow one: eat it first"
    ),
    "Se conserve plusieurs mois en cave": "Keeps for months in a cellar",
    "Se conserve tout l'hiver dans une pièce fraîche et sèche": (
        "Keeps all winter in a cool, dry room"
    ),
    "Se coupe au fur et à mesure pendant des mois": (
        "Cut as you need it, for months"
    ),
    "Se coupe comme de la ciboulette et repousse toute la saison": (
        "Cut like chives and it regrows all season"
    ),
    "Se coupe et repousse sans fin, de mars à novembre": (
        "Cut and come again endlessly, from March to November"
    ),
    "Se coupe et repousse trois ou quatre fois": (
        "Cut and come again three or four times"
    ),
    "Se cueille jeune, à la taille d'une soucoupe": (
        "Pick young, at saucer size"
    ),
    "Se cueille toute l'année": "Picked all year round",
    "Se cultive très bien en pot": "Grows very well in a pot",
    "Se cultive très bien en pot à rentrer l'hiver": (
        "Grows very well in a pot to bring in over winter"
    ),
    "Se garde en terre tout l'hiver sous un paillage": (
        "Keeps in the ground all winter under a mulch"
    ),
    "Se laisse en terre tout l'hiver et s'arrache au besoin": (
        "Left in the ground all winter and lifted as needed"
    ),
    "Se multiplie par éclat de souche au printemps": (
        "Propagated by splitting the crown in spring"
    ),
    "Se passe de taille si elle est bien tuteurée": (
        "Needs no pruning if it is well staked"
    ),
    "Se plante en enterrant le fruit entier, germe vers le haut": (
        "Planted by burying the whole fruit, sprout upward"
    ),
    "Se plante en février, contrairement à l'ail blanc": (
        "Planted in February, unlike white garlic"
    ),
    "Se plaît contre un mur au sud, racines contenues": (
        "Happy against a south wall, with its roots confined"
    ),
    "Se ressème abondamment : arracher les surnuméraires au printemps": (
        "Self-seeds freely: pull out the surplus in spring"
    ),
    "Se ressème seul année après année si on le laisse fleurir": (
        "Self-seeds year after year if you let it flower"
    ),
    "Se ressème seul si on le laisse fleurir": (
        "Self-seeds if you let it flower"
    ),
    "Se ressème seule d'année en année": "Self-seeds from year to year",
    "Se ressème seule indéfiniment": "Self-seeds indefinitely",
    "Se ressème toute seule une fois installée": (
        "Self-seeds on its own once established"
    ),
    "Se ressème très abondamment : couper les épis avant qu'ils ne lâchent": (
        "Self-seeds very freely: cut the heads before they shed"
    ),
    "Se récolte après la chute des feuilles, quand le fruit est translucide": (
        "Harvested after leaf fall, when the fruit turns translucent"
    ),
    "Se récolte de novembre à mars, au fur et à mesure des besoins": (
        "Harvested from November to March, as you need it"
    ),
    "Se récolte en feuilles avant la floraison, de mars à mai": (
        "Harvested as leaves before flowering, from March to May"
    ),
    "Se récolte en fleurs, à sécher à l'ombre": (
        "Harvested in flower, to be dried in the shade"
    ),
    "Se récolte sec, à l'inverse du maïs doux : attendre que les tiges brunissent": (
        "Harvested dry, unlike sweetcorn: wait for the stems to brown"
    ),
    "Se récolte toute l'année, même sous la neige": (
        "Harvested all year round, even under snow"
    ),
    "Se récolte vert pour les tartes, mûr pour le frais": (
        "Picked green for tarts, ripe for eating fresh"
    ),
    "Se récolte vert, quand les gousses sont pleines mais encore tendres": (
        "Harvested green, when the pods are full but still tender"
    ),
    "Se sème avec du seigle, qui lui sert de tuteur": (
        "Sown with rye, which holds it up"
    ),
    "Se sème avec la vesce, à qui il sert de tuteur": (
        "Sown with vetch, which it holds up"
    ),
    "Semer 6 à 8 pieds tous les 15 jours plutôt qu'une planche entière": (
        "Sow six to eight plants every fortnight rather than a whole bed"
    ),
    "Semer après le solstice : semé trop tôt, il monte systématiquement": (
        "Sow after the solstice: sown too early, it bolts every time"
    ),
    "Semer clair et éclaircir sans pitié : une carotte serrée reste un fil": (
        "Sow thinly and thin ruthlessly: a crowded carrot stays a thread"
    ),
    "Semer en bloc carré, jamais en ligne unique : la pollinisation en dépend": (
        "Sow in a square block, never a single row: pollination depends on it"
    ),
    "Semer sur sol tassé, surtout pas labouré : elle aime la terre ferme": (
        "Sow on firm ground, certainly not dug over: it likes solid soil"
    ),
    "Semer tous les 15 jours jusqu'en juillet pour étaler la récolte": (
        "Sow every fortnight until July to spread the harvest"
    ),
    "Semer une petite ligne tous les 10 jours plutôt qu'une grande d'un coup": (
        "Sow a short row every ten days rather than one long row at once"
    ),
    "Semis très précoce indispensable sous nos latitudes": (
        "A very early sowing is essential at our latitudes"
    ),
    "Semé en août, il se consomme frais au printemps suivant": (
        "Sown in August, eaten fresh the following spring"
    ),
    "Semé en août, il se récolte tout l'automne et se garde en cave": (
        "Sown in August, harvested all autumn and kept in the cellar"
    ),
    "Semé en septembre, il couvre le sol tout l'hiver et fixe l'azote": (
        "Sown in September, it covers the soil all winter and fixes nitrogen"
    ),
    "Semé fin août, il se récolte d'octobre aux gelées": (
        "Sown in late August, harvested from October to the frosts"
    ),
    "Semée en novembre, elle passe l'hiver et devance les pucerons noirs": (
        "Sown in November, it overwinters and gets ahead of the blackfly"
    ),
    "Ses fleurs bleues attirent les abeilles tout l'été": (
        "Its blue flowers draw bees all summer"
    ),
    "Ses fleurs rouges en mai sont un festin pour les abeilles": (
        "Its red May flowers are a feast for bees"
    ),
    "Ses ombelles jaunes attirent quantité d'insectes auxiliaires": (
        "Its yellow umbels draw a great many beneficial insects"
    ),
    "Ses racines assainissent le sol des nématodes : le compagnon numéro un de la tomate": (
        "Its roots clear the soil of nematodes: the tomato's number one companion"
    ),
    "Ses racines descendent à deux mètres et remontent les minéraux": (
        "Its roots go down two metres and bring minerals back up"
    ),
    "Ses racines décompactent les sols tassés en profondeur": (
        "Its roots break up compacted soil at depth"
    ),
    "Seuls les pieds femelles donnent des cônes": (
        "Only the female plants bear cones"
    ),
    "Six mètres en une saison : il lui faut un fil solide jusqu'au toit": (
        "Six metres in one season: it needs a strong wire up to the roof"
    ),
    "Sol acide obligatoire : en pot avec de la terre de bruyère si le jardin est calcaire": (
        "Acid soil is mandatory: in a pot of ericaceous compost if the garden is "
        "chalky"
    ),
    "Son cœur serré se conserve des semaines en cave": (
        "Its tight heart keeps for weeks in a cellar"
    ),
    "Sous climat océanique, la cloque est son ennemie principale": (
        "In a maritime climate, leaf curl is its main enemy"
    ),
    "Supporte le froid : un semis de février donne la première récolte": (
        "Stands the cold: a February sowing gives the first crop"
    ),
    "Supprimer le bois de plus de 4 ans en hiver": (
        "Take out wood more than four years old in winter"
    ),
    "Supprimer les fleurs fanées pour prolonger la floraison jusqu'aux gelées": (
        "Deadhead to keep it flowering until the frosts"
    ),
    "Supprimer les fleurs jaunes pour garder des feuilles tendres": (
        "Remove the yellow flowers to keep the leaves tender"
    ),
    "Supprimer les stolons pour favoriser les fruits": (
        "Remove the runners to favour the fruit"
    ),
    "Taille d'hiver indispensable : 2 yeux par coursonne": (
        "Winter pruning is essential: two buds per spur"
    ),
    "Taille simple : tout rabattre au sol en février": (
        "Simple pruning: cut everything to the ground in February"
    ),
    "Tailler après la floraison pour éviter qu'il se dégarnisse": (
        "Prune after flowering to stop it going bare"
    ),
    "Tailler en boule après la floraison, sans jamais couper dans le vieux bois": (
        "Clip to a ball after flowering, never cutting into old wood"
    ),
    "Tailler le moins possible, et seulement après la récolte : il gomme": (
        "Prune as little as possible, and only after harvest: it bleeds gum"
    ),
    "Tailler les gourmands une fois par semaine": (
        "Pinch out the side shoots once a week"
    ),
    "Tirer les pétioles, ne pas les couper ; les feuilles sont toxiques": (
        "Pull the stalks, do not cut them; the leaves are poisonous"
    ),
    "Tolère très bien la mi-ombre : utile pour les coins ingrats": (
        "Very tolerant of partial shade: useful for awkward corners"
    ),
    "Trois à quatre coupes par an pour le purin, riche en potasse": (
        "Three or four cuts a year for liquid feed, rich in potash"
    ),
    "Très envahissant : lui réserver un coin dont il ne sortira pas": (
        "Very invasive: give it a corner it cannot escape from"
    ),
    "Très épineux : cueillir en coupant les rameaux entiers": (
        "Very thorny: pick by cutting whole shoots"
    ),
    "Tuteurer : les fruits sont lourds": "Stake it: the fruit is heavy",
    "Tuteurer dès la plantation, pas après": (
        "Stake at planting time, not afterwards"
    ),
    "Un chou vivace qui donne des feuilles toute l'année, pendant 5 à 6 ans": (
        "A perennial kale giving leaves all year, for five or six years"
    ),
    "Un filet anti-insectes règle le problème des piérides une fois pour toutes": (
        "Insect mesh settles the cabbage white problem once and for all"
    ),
    "Un filet est la seule défense réaliste contre les oiseaux": (
        "Netting is the only realistic defence against birds"
    ),
    "Un pied mâle pour cinq femelles, sans quoi aucun fruit": (
        "One male plant per five females, or no fruit at all"
    ),
    "Un pied mâle pour cinq femelles, sauf variété autofertile": (
        "One male plant per five females, unless the variety is self-fertile"
    ),
    "Un seul fruit nourrit une famille pendant des semaines": (
        "A single fruit feeds a family for weeks"
    ),
    "Un seul semis nourrit du printemps aux gelées": (
        "One sowing feeds you from spring to the frosts"
    ),
    "Une bordure de lavande éloigne les pucerons et nourrit les abeilles": (
        "A lavender edging keeps aphids off and feeds the bees"
    ),
    "Une fois installé, il revient indéfiniment sans qu'on s'en occupe": (
        "Once established it comes back indefinitely with no attention"
    ),
    "Une touffe donne des feuilles d'avril à octobre, pendant dix ans": (
        "One clump gives leaves from April to October, for ten years"
    ),
    "Une touffe suffit pour des années": "One clump is enough for years",
    "Variété d'hiver : se récolte de novembre à mars": (
        "A winter variety: harvested from November to March"
    ),
    "Variétés 'Merveille d'hiver' ou 'Rougette' : les seules à passer le froid": (
        "'Merveille d'hiver' or 'Rougette': the only ones that come through the "
        "cold"
    ),
    "À cultiver en pot, sans exception : en pleine terre elle colonise tout": (
        "Grow it in a pot, no exceptions: in open ground it colonises everything"
    ),
    "À la Sainte-Catherine (25 novembre), tout bois prend racine": (
        "On St Catherine's day (25 November), any wood takes root"
    ),
    "Éclaircir les fruits en juin : moins de pommes, mais plus belles": (
        "Thin the fruit in June: fewer apples, but better ones"
    ),
    "Éclaircir sévèrement : il met trop de fruits et les fait tous petits": (
        "Thin hard: it sets too much fruit and makes it all small"
    ),
    "Épineux : tailler en gobelet pour pouvoir cueillir": (
        "Thorny: prune to an open goblet so you can pick"
    ),
    "Étayer les branches chargées, elles cassent": (
        "Prop up the laden branches, they break"
    ),
    "Étouffe les adventices mieux que tout autre engrais vert": (
        "Smothers weeds better than any other green manure"
    ),
}
