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
    "achillee": "Yarrow",
    "ail-blanc": "White garlic",
    "ail-ours": "Wild garlic",
    "ail-rose": "Pink garlic",
    "aloe-vera": "Aloe vera",
    "amandier": "Almond tree",
    "amarante": "Amaranth",
    "aneth": "Dill",
    "angelique": "Angelica",
    "argousier": "Sea buckthorn",
    "armoise-absinthe": "Wormwood",
    "arroche": "Orache",
    "artichaut": "Globe artichoke",
    "asperge": "Asparagus",
    "aspidistra": "Cast-iron plant",
    "aubepine": "Common hawthorn",
    "aubergine": "Aubergine",
    "avoine": "Oats (green manure)",
    "bardane": "Greater burdock",
    "basilic": "Basil",
    "betterave": "Beetroot",
    "blette": "Chard",
    "bouillon-blanc": "Great mullein",
    "bourrache": "Borage",
    "brocoli": "Broccoli",
    "calathea": "Calathea",
    "camerisier": "Honeyberry",
    "camomille": "Roman chamomile",
    "camomille-matricaire": "German chamomile",
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
    "chlorophytum": "Spider plant",
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
    "crassula": "Jade plant",
    "cresson-alenois": "Garden cress",
    "cresson-fontaine": "Watercress",
    "crosne": "Chinese artichoke",
    "daikon": "Daikon radish",
    "dieffenbachia": "Dumb cane",
    "dracaena-marginata": "Madagascar dragon tree",
    "echalote": "Shallot",
    "echinacee": "Purple coneflower",
    "edamame": "Edamame soybean",
    "eglantier": "Dog rose",
    "endive": "Belgian endive",
    "epinard": "Spinach",
    "epinard-perpetuel": "Perpetual spinach (Good-King-Henry)",
    "estragon": "Tarragon",
    "fenouil-aromatique": "Herb fennel",
    "fenouil-bulbeux": "Florence fennel",
    "feve": "Broad bean",
    "ficus-elastica": "Rubber plant",
    "ficus-lyrata": "Fiddle-leaf fig",
    "figuier": "Fig tree",
    "fougere-nid": "Bird's nest fern",
    "fraisier": "Strawberry",
    "fraisier-remontant": "Everbearing strawberry",
    "framboisier": "Raspberry",
    "framboisier-remontant": "Autumn raspberry",
    "goji": "Goji berry",
    "gombo": "Okra",
    "groseillier": "Redcurrant",
    "groseillier-maquereau": "Gooseberry",
    "guimauve": "Marshmallow",
    "haricot-a-rames": "Climbing French bean",
    "haricot-espagne": "Runner bean",
    "haricot-nain": "Dwarf French bean",
    "haricot-sec": "Drying bean",
    "houblon": "Hop",
    "hoya": "Wax plant",
    "hysope": "Hyssop",
    "kaki": "Persimmon",
    "kentia": "Kentia palm",
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
    "maranta": "Prayer plant",
    "marjolaine": "Marjoram",
    "mauve": "Common mallow",
    "melisse": "Lemon balm",
    "melon": "Melon",
    "menthe": "Mint",
    "menthe-poivree": "Peppermint",
    "millepertuis": "St John's wort",
    "mizuna": "Mizuna",
    "monstera": "Swiss cheese plant",
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
    "onagre": "Evening primrose",
    "orchidee-phalaenopsis": "Moth orchid",
    "origan": "Oregano",
    "ortie": "Stinging nettle",
    "oseille": "Sorrel",
    "pain-de-sucre": "Sugarloaf chicory",
    "panais": "Parsnip",
    "passiflore": "Purple passionflower",
    "pasteque": "Watermelon",
    "patate-douce": "Sweet potato",
    "patisson": "Pattypan squash",
    "pecher": "Peach tree",
    "peperomia": "Baby rubber plant",
    "persil": "Parsley",
    "persil-tubereux": "Turnip-rooted parsley",
    "petit-pois": "Garden pea",
    "phacelie": "Phacelia",
    "philodendron": "Heartleaf philodendron",
    "physalis": "Cape gooseberry",
    "pilea": "Chinese money plant",
    "piment": "Chilli pepper",
    "pissenlit": "Dandelion",
    "plantain-lanceole": "Ribwort plantain",
    "poireau": "Leek",
    "poireau-perpetuel": "Perennial leek",
    "poirier": "Pear tree",
    "pois-chiche": "Chickpea",
    "pois-mange-tout": "Mangetout pea",
    "poivron": "Sweet pepper",
    "pomme-de-terre": "Potato",
    "pommier": "Apple tree",
    "pothos": "Golden pothos",
    "potimarron": "Red kuri squash",
    "pourpier": "Summer purslane",
    "prele": "Field horsetail",
    "prunier": "Plum tree",
    "quinoa": "Quinoa",
    "radis": "Radish",
    "radis-noir": "Black winter radish",
    "raifort": "Horseradish",
    "reine-des-pres": "Meadowsweet",
    "rhubarbe": "Rhubarb",
    "romarin": "Rosemary",
    "roquette": "Rocket",
    "roquette-vivace": "Perennial wall rocket",
    "rutabaga": "Swede",
    "salsifis": "Salsify",
    "sansevieria": "Snake plant",
    "sarrasin": "Buckwheat (green manure)",
    "sarriette": "Summer savory",
    "sauge": "Sage",
    "scarole": "Escarole",
    "scorsonere": "Scorzonera",
    "seigle": "Rye (green manure)",
    "shiso": "Shiso",
    "souci": "Pot marigold",
    "spathiphyllum": "Peace lily",
    "sureau-noir": "Black elder",
    "tanaisie": "Tansy",
    "tetragone": "New Zealand spinach",
    "thym": "Thyme",
    "tilleul": "Small-leaved lime",
    "tomate": "Tomato",
    "tomate-cerise": "Cherry tomato",
    "tomatille": "Tomatillo",
    "topinambour": "Jerusalem artichoke",
    "tournesol": "Sunflower",
    "trefle-incarnat": "Crimson clover (green manure)",
    "trevise": "Radicchio",
    "valeriane": "Valerian",
    "verveine-citronnelle": "Lemon verbena",
    "vesce": "Winter vetch (green manure)",
    "vigne-table": "Grapevine (table grapes)",
    "zamioculcas": "ZZ plant",
}


# --- Familles botaniques ------------------------------------------------------
#
# Le nom francais reste la cle du catalogue : `rotation.DELAIS` s'indexe dessus
# pour decider du delai de retour d'une famille sur la meme parcelle. Ne jamais
# traduire ces cles, seulement leurs valeurs.

FAMILLES = {
    "Actinidiacées": "Actinidiaceae",
    "Aizoacées": "Aizoaceae",
    "Amaranthacées": "Amaranthaceae",
    "Amaryllidacées": "Amaryllidaceae",
    "Apiacées": "Apiaceae",
    "Apocynacées": "Apocynaceae",
    "Aracées": "Araceae",
    "Arécacées": "Arecaceae",
    "Asparagacées": "Asparagaceae",
    "Asphodélacées": "Asphodelaceae",
    "Aspléniacées": "Aspleniaceae",
    "Astéracées": "Asteraceae",
    "Boraginacées": "Boraginaceae",
    "Brassicacées": "Brassicaceae",
    "Bétulacées": "Betulaceae",
    "Cannabacées": "Cannabaceae",
    "Caprifoliacées": "Caprifoliaceae",
    "Convolvulacées": "Convolvulaceae",
    "Crassulacées": "Crassulaceae",
    "Cucurbitacées": "Cucurbitaceae",
    "Fabacées": "Fabaceae",
    "Fagacées": "Fagaceae",
    "Grossulariacées": "Grossulariaceae",
    "Hypéricacées": "Hypericaceae",
    "Juglandacées": "Juglandaceae",
    "Lamiacées": "Lamiaceae",
    "Lauracées": "Lauraceae",
    "Malvacées": "Malvaceae",
    "Marantacées": "Marantaceae",
    "Montiacées": "Montiaceae",
    "Moracées": "Moraceae",
    "Onagracées": "Onagraceae",
    "Orchidacées": "Orchidaceae",
    "Oxalidacées": "Oxalidaceae",
    "Passifloracées": "Passifloraceae",
    "Pipéracées": "Piperaceae",
    "Plantaginacées": "Plantaginaceae",
    "Poacées": "Poaceae",
    "Polygonacées": "Polygonaceae",
    "Portulacacées": "Portulacaceae",
    "Rosacées": "Rosaceae",
    "Scrofulariacées": "Scrophulariaceae",
    "Solanacées": "Solanaceae",
    "Tropaeolacées": "Tropaeolaceae",
    "Urticacées": "Urticaceae",
    "Verbénacées": "Verbenaceae",
    "Viburnacées": "Viburnaceae",
    "Vitacées": "Vitaceae",
    "Ébénacées": "Ebenaceae",
    "Éléagnacées": "Elaeagnaceae",
    "Équisétacées": "Equisetaceae",
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
    "caillouteux, drainé, même pauvre": "stony, free draining, poor is fine",    "frais, lourd, qui ne sèche jamais": "moist, heavy, never drying out",
    "terreau de plantes vertes, drainant": "houseplant compost, free draining",
    "terreau très aéré, écorce et perlite": "very open compost, bark and perlite",
    "substrat à cactées, sableux et très drainant": "cactus compost, sandy and very free draining",
    "écorce de pin seule, sans terreau": "pine bark only, no compost",

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
    "Très sobre : elle pousse dans les talus que personne n'arrose.": (
        "Very frugal: it grows on banks nobody waters."
    ),
    "Sobre ; il supporte même le piétinement et la sécheresse.": (
        "Frugal; it even takes trampling and drought."
    ),
    "Aime les sols riches en azote et frais ; elle marque les anciens fumiers.": (
        "Likes soil rich in nitrogen and moist; it marks out old manure heaps."
    ),
    "Sobre : trop d'eau le fait pourrir au collet.": (
        "Frugal: too much water rots it at the collar."
    ),
    "Aucun arrosage une fois établie : c'est un arbuste de haie.": (
        "No watering once established: it is a hedgerow shrub."
    ),
    "Jamais à sec : c'est une plante de fossé et de prairie humide.": (
        "Never dry: this is a plant of ditches and wet meadows."
    ),
    "Aime avoir le pied frais tout l'été.": "Likes its feet cool all summer.",
    "Sobre une fois installée ; craint l'humidité stagnante de l'hiver.": (
        "Frugal once settled; dislikes standing winter wet."
    ),
    "Sol frais en permanence ; elle pousse naturellement au bord des ruisseaux.": (
        "Permanently moist soil; it grows naturally along streams."
    ),
    "Sobre : sa racine pivot va chercher l'eau en profondeur.": (
        "Frugal: its taproot goes down for water."
    ),
    "Régulier la première année, le temps que la racine descende.": (
        "Regular the first year, while the root goes down."
    ),
    "Aucun arrosage : il colonise les gravières et les talus secs.": (
        "No watering: it colonises gravel pits and dry banks."
    ),
    "Sol humide en permanence ; elle signale les terrains mal drainés.": (
        "Permanently wet soil; it marks out badly drained ground."
    ),
    "Très sobre, à la limite de l'indestructible.": (
        "Very frugal, close to indestructible."
    ),
    "Jamais à sec : elle flétrit en une journée de canicule.": (
        "Never dry: it wilts in a single day of heatwave."
    ),
    "Aucun arrosage une fois établi ; le soutenir les deux premiers étés.": (
        "No watering once established; see it through its first two summers."
    ),
    "Aucun arrosage une fois établi : c'est la ronce des haies.": (
        "No watering once established: it is the bramble of the hedgerows."
    ),
    "Très sobre : elle pousse dans les sables et les remblais.": (
        "Very frugal: it grows in sand and on spoil."
    ),
    "Régulier en été ; très réduit l'hiver, quand elle disparaît.": (
        "Regular in summer; very sparing in winter, when it disappears."
    ),
    "Sobre ; elle n'aime pas les sols lourds et détrempés.": (
        "Frugal; it dislikes heavy, waterlogged soil."
    ),
    "Laisser sécher les trois premiers centimètres entre deux arrosages.": (
        "Let the top three centimetres dry out between waterings."
    ),
    "Attendre que le terreau soit sec sur la moitié du pot.": (
        "Wait until the compost is dry halfway down the pot."
    ),
    "Garder le terreau juste humide, jamais détrempé.": (
        "Keep the compost just moist, never sodden."
    ),
    "Elle signale elle-même la soif en s'affaissant, et se relève en deux heures.": (
        "It announces thirst by drooping, and recovers within two hours."
    ),
    "Un arrosage toutes les trois semaines suffit, moitié moins l'hiver.": (
        "One watering every three weeks is enough, half that in winter."
    ),
    "Terreau frais en permanence, mais jamais d'eau dans la soucoupe.": (
        "Compost moist at all times, but never water left in the saucer."
    ),
    "Toutes les trois semaines l'été, une fois par mois l'hiver.": (
        "Every three weeks in summer, once a month in winter."
    ),
    "Laisser sécher la moitié du pot ; elle craint l'eau stagnante.": (
        "Let the pot dry halfway down; it dislikes standing water."
    ),
    "Très sobre, et elle pardonne l'oubli mieux que l'excès.": (
        "Very frugal, and it forgives neglect better than excess."
    ),
    "Terreau frais l'été, plus sec l'hiver ; ses racines charnues stockent l'eau.": (
        "Compost moist in summer, drier in winter; its fleshy roots store water."
    ),
    "Jamais à sec, et à l'eau non calcaire : eau de pluie ou eau filtrée.": (
        "Never dry, and with lime-free water: rainwater or filtered water."
    ),
    "Terreau frais en permanence, à l'eau non calcaire.": (
        "Compost moist at all times, with lime-free water."
    ),
    "Laisser sécher la surface entre deux arrosages ; elle flétrit vite et se remet vite.": (
        "Let the surface dry between waterings; it wilts fast and recovers fast."
    ),
    "Ses feuilles épaisses stockent l'eau : laisser bien sécher entre deux arrosages.": (
        "Its thick leaves store water: let it dry well between waterings."
    ),
    "Laisser sécher complètement entre deux arrosages, surtout l'hiver.": (
        "Let it dry out completely between waterings, especially in winter."
    ),
    "Terreau constamment humide ; arroser sur le bord, jamais dans le cœur.": (
        "Compost constantly moist; water at the edge, never into the crown."
    ),
    "Terreau frais l'été, nettement plus sec l'hiver.": (
        "Compost moist in summer, distinctly drier in winter."
    ),
    "Tremper le pot un quart d'heure puis l'égoutter entièrement ; jamais d'eau résiduelle.": (
        "Soak the pot for a quarter of an hour then drain it fully; never leave water behind."
    ),
    "Arroser abondamment, puis laisser le pot sécher complètement.": (
        "Water generously, then let the pot dry out completely."
    ),
    "Laisser sécher complètement ; presque rien de novembre à mars.": (
        "Let it dry out completely; almost nothing from November to March."
    ),
    "Laisser sécher la moitié du pot entre deux arrosages.": (
        "Let the pot dry halfway down between waterings."
    ),
    "Régulier et modéré : il perd ses feuilles basses à la moindre irrégularité.": (
        "Regular and moderate: it drops its lower leaves at the least irregularity."
    ),
}


# --- Conseils de culture ------------------------------------------------------
#
# Indexes par le conseil francais, comme les notes d'arrosage : le meme conseil
# sert parfois a deux fiches voisines.

CONSEILS = {
    "Usage externe seulement : ses alcaloïdes pyrrolizidiniques sont toxiques pour le foie par voie interne": (
        "External use only: its pyrrolizidine alkaloids are toxic to the liver "
        "if taken internally"
    ),
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
    "Déconseillée aux femmes enceintes, et allergisante comme toutes les astéracées": (
        "Not advised during pregnancy, and an allergen like all daisy-family plants"
    ),
    "Ne jamais la cueillir jeune en mélange : ses feuilles ressemblent à celles de la ciguë, mortelle": (
        "Never gather it young in a mixed handful: its leaves resemble those of hemlock, which is lethal"
    ),
    "Couper les sommités fleuries par temps sec, en pleine floraison": (
        "Cut the flowering tops in dry weather, in full flower"
    ),
    "Une bordure d'achillée attire les syrphes, qui mangent les pucerons": (
        "An edging of yarrow draws in hoverflies, which eat aphids"
    ),
    "Aucune confusion dangereuse connue, ce qui en fait une bonne première plante à apprendre": (
        "No dangerous look-alike known, which makes it a good first plant to learn"
    ),
    "Jeunes feuilles comestibles en salade ; les vieilles sont filandreuses": (
        "Young leaves edible in salad; the old ones are stringy"
    ),
    "Pousse spontanément dans toutes les pelouses de France — inutile de l'acheter": (
        "Grows wild in every lawn in France — no need to buy it"
    ),
    "Se ressème seul : supprimer les épis si on ne veut pas qu'il s'étende": (
        "It self-seeds: remove the spikes if you do not want it spreading"
    ),
    "Cueillir avec des gants : les poils urticants tiennent jusqu'à la cuisson": (
        "Pick it with gloves: the stinging hairs hold until cooking"
    ),
    "Ne récolter que les quatre feuilles du sommet, avant la floraison": (
        "Take only the top four leaves, before it flowers"
    ),
    "Elle envahit par ses rhizomes : la cantonner dans un carré, ou en pot": (
        "It invades by rhizomes: confine it to one bed, or to a pot"
    ),
    "Son purin est un engrais azoté ; celui de consoude apporte la potasse": (
        "Its liquid feed supplies nitrogen; comfrey's supplies potash"
    ),
    "Interagit avec beaucoup de médicaments — pilule, anticoagulants, antirétroviraux — en accélérant leur élimination": (
        "Interacts with many medicines — the pill, anticoagulants, antiretrovirals — by speeding up their elimination"
    ),
    "Photosensibilisant : il rend la peau plus sensible au soleil": (
        "Photosensitising: it makes the skin more sensitive to sun"
    ),
    "Reconnaissable aux points translucides de ses feuilles, vues à contre-jour": (
        "Recognisable by the translucent dots in its leaves, seen against the light"
    ),
    "Récolter les sommités fleuries autour du solstice, c'est là qu'elles sont les plus riches": (
        "Gather the flowering tops around the solstice, when they are at their richest"
    ),
    "Ses épines sont longues et cassent sous la peau : tailler gants et manches longues": (
        "Its thorns are long and snap off under the skin: prune in gloves and long sleeves"
    ),
    "Plantation réglementée par endroits : hôte du feu bactérien, se renseigner en pépinière": (
        "Planting is restricted in some areas: it hosts fireblight, so ask at the nursery"
    ),
    "Récolter les fleurs à peine ouvertes, les cynorhodons rouges en automne": (
        "Gather the flowers barely open, and the red hips in autumn"
    ),
    "Une haie d'aubépine abrite les oiseaux insectivores tout l'hiver": (
        "A hawthorn hedge shelters insect-eating birds all winter"
    ),
    "Contient des dérivés salicylés : à éviter en cas d'allergie à l'aspirine": (
        "Contains salicylates: avoid it if you are allergic to aspirin"
    ),
    "Elle meurt de sécheresse avant de mourir de froid : ne la planter qu'en sol frais": (
        "It dies of drought long before it dies of cold: plant it only in moist soil"
    ),
    "Récolter les fleurs blanches en plein épanouissement, elles sentent l'amande": (
        "Gather the white flowers in full bloom, when they smell of almond"
    ),
    "Fleurs, feuilles et racines sont comestibles ; aucune toxicité connue": (
        "Flowers, leaves and roots are all edible; no known toxicity"
    ),
    "Ne récolter les racines qu'à l'automne de la deuxième année": (
        "Lift the roots only in the autumn of the second year"
    ),
    "Sa levée est lente et irrégulière : passer par un plant est plus sûr": (
        "Germination is slow and uneven: starting from a plant is safer"
    ),
    "Allergisante comme toutes les astéracées ; déconseillée en cas de maladie auto-immune": (
        "An allergen like all daisy-family plants; not advised with an auto-immune condition"
    ),
    "Ne rien prélever les deux premières années, le temps que la touffe se fasse": (
        "Take nothing for the first two years, while the clump builds up"
    ),
    "Laisser les capitules secs en place l'hiver : les chardonnerets les vident": (
        "Leave the dry seed heads standing through winter: goldfinches empty them"
    ),
    "Déconseillée avant la conduite : elle agit sur la vigilance": (
        "Not advised before driving: it acts on alertness"
    ),
    "Ses racines sentent fort une fois sèches, et les chats s'y roulent": (
        "Its roots smell strongly once dried, and cats roll in them"
    ),
    "Déterrer les racines à l'automne de la deuxième année, pas avant": (
        "Dig the roots in the autumn of the second year, not before"
    ),
    "Entièrement comestible, sans confusion dangereuse connue en France": (
        "Entirely edible, with no dangerous look-alike known in France"
    ),
    "Ne jamais cueillir au bord d'une route ni sur une pelouse traitée": (
        "Never pick it by a roadside or on a treated lawn"
    ),
    "Blanchir les cœurs sous un pot retourné quinze jours : l'amertume tombe": (
        "Blanch the hearts under an upturned pot for a fortnight: the bitterness goes"
    ),
    "Il remonte le calcium et le potassium des couches profondes du sol": (
        "It lifts calcium and potassium from the deeper layers of the soil"
    ),
    "Allergisante comme les astéracées ; ses capitules s'accrochent aux vêtements et aux animaux": (
        "An allergen like the daisy family; its burrs catch on clothes and on animals"
    ),
    "Racine comestible, récoltée à l'automne de la première année — c'est le gobō japonais": (
        "Edible root, lifted in the autumn of the first year — this is Japanese gobō"
    ),
    "Semer en sol profond et meuble : la racine descend à cinquante centimètres": (
        "Sow in deep, loose soil: the root goes down fifty centimetres"
    ),
    "Supprimer les fleurs de la deuxième année, sinon elle se ressème partout": (
        "Remove the second-year flowers, or it seeds itself everywhere"
    ),
    "Filtrer soigneusement toute infusion : les poils des feuilles irritent la gorge": (
        "Strain any infusion carefully: the leaf hairs irritate the throat"
    ),
    "Bisannuel — rosette la première année, hampe de deux mètres la seconde": (
        "Biennial — a rosette the first year, a two-metre spike the second"
    ),
    "Semer en surface sans recouvrir, la graine a besoin de lumière pour lever": (
        "Sow on the surface without covering; the seed needs light to germinate"
    ),
    "Récolter les fleurs jaunes au fur et à mesure, elles s'ouvrent de bas en haut": (
        "Gather the yellow flowers as they come, opening from the bottom up"
    ),
    "Ne pas la confondre avec la prêle des marais, Equisetum palustre, toxique : chez la prêle des champs, le premier entre-nœud d'un rameau est aussi long ou plus long que la gaine de la tige d'où il part": (
        "Do not confuse it with marsh horsetail, Equisetum palustre, which is toxic: in field horsetail the first internode of a branch is as long as or longer than the stem sheath it springs from"
    ),
    "Ses rhizomes descendent à un mètre et la rendent impossible à éradiquer : la planter en bac": (
        "Its rhizomes go down a metre and make it impossible to eradicate: plant it in a container"
    ),
    "Récolter les tiges stériles vertes de l'été, pas les épis bruns du printemps": (
        "Gather the green sterile stems of summer, not the brown spring cones"
    ),
    "Sa décoction, riche en silice, sert de traitement préventif contre les maladies cryptogamiques": (
        "Its silica-rich decoction is used as a preventive against fungal disease"
    ),
    "Toxique par ingestion à cause de sa thuyone, et interdite aux femmes enceintes : on la cultive pour le jardin, pas pour la tisane": (
        "Toxic if swallowed, because of its thujone, and barred during pregnancy: it is grown for the garden, not for the teapot"
    ),
    "Son purin répulsif est son véritable usage, contre pucerons et altises": (
        "Its repellent liquid feed is its real use, against aphids and flea beetles"
    ),
    "Elle s'étend par rhizomes et prend la place : la diviser tous les trois ans": (
        "It spreads by rhizomes and takes over: divide it every three years"
    ),
    "Neurotoxique à forte dose par sa thuyone, et interdite aux femmes enceintes": (
        "Neurotoxic in quantity through its thujone, and barred during pregnancy"
    ),
    "Elle inhibe la germination de ses voisines : la planter en bout de planche, jamais au milieu": (
        "It inhibits its neighbours' germination: plant it at the end of a bed, never in the middle"
    ),
    "Son purin éloigne les pucerons, les limaces et la piéride du chou": (
        "Its liquid feed keeps off aphids, slugs and cabbage white caterpillars"
    ),
    "Déconseillée aux nourrissons et aux jeunes enfants, par voie interne comme en inhalation": (
        "Not advised for infants and young children, internally or as an inhalation"
    ),
    "Hybride stérile : elle ne se ressème pas, mais ses stolons envahissent tout — la planter en pot enterré": (
        "A sterile hybrid: it does not self-seed, but its runners take over — plant it in a sunken pot"
    ),
    "Rabattre toute la touffe avant la floraison, l'arôme y est au maximum": (
        "Cut the whole clump back before it flowers, when the aroma is at its peak"
    ),
    "Plus poivrée et plus riche en menthol que la menthe verte": (
        "More peppery and richer in menthol than garden mint"
    ),
    "Aucune toxicité connue, ce qui en fait une tisane de tous les âges": (
        "No known toxicity, which makes it a tea for any age"
    ),
    "Arbre de vingt mètres : à ne planter que si la place existe vraiment": (
        "A twenty-metre tree: plant it only if the room genuinely exists"
    ),
    "La fenêtre de récolte des bractées dure dix jours, pas plus": (
        "The window for gathering the bracts lasts ten days, no more"
    ),
    "Récolter en hauteur et jamais en bord de route : ses fleurs captent les poussières": (
        "Gather high up and never by a road: its flowers catch the dust"
    ),
    "Les poils qui entourent les graines du cynorhodon sont irritants : les retirer avant toute préparation": (
        "The hairs around the seeds inside the hip are irritant: remove them before any preparation"
    ),
    "Attendre les premières gelées pour cueillir, le fruit devient blet et sucré": (
        "Wait for the first frosts to pick: the fruit goes soft and sweet"
    ),
    "Son cynorhodon est l'un des fruits les plus riches en vitamine C de la flore française": (
        "Its hip is one of the richest sources of vitamin C in the French flora"
    ),
    "Il sert de porte-greffe aux rosiers de jardin": (
        "It serves as rootstock for garden roses"
    ),
    "Aucune toxicité connue ; sa racine de première année se mange comme un salsifis": (
        "No known toxicity; its first-year root eats like a salsify"
    ),
    "Bisannuelle — rosette la première année, hampe fleurie la seconde": (
        "Biennial — a rosette the first year, a flowering spike the second"
    ),
    "Ses fleurs s'ouvrent au crépuscule en quelques minutes et nourrissent les sphinx": (
        "Its flowers open at dusk in a matter of minutes and feed the hawkmoths"
    ),
    "Elle se ressème abondamment : garder deux ou trois pieds, arracher le reste": (
        "It self-seeds freely: keep two or three plants, pull the rest"
    ),
    "Déconseillée avant la conduite ; ne pas la confondre avec Passiflora caerulea, la passiflore bleue ornementale, dont les fruits ne se consomment pas": (
        "Not advised before driving; do not confuse it with Passiflora caerulea, the ornamental blue passionflower, whose fruit is not for eating"
    ),
    "Elle disparaît complètement l'hiver et repart de souche en mai : ne pas croire qu'elle est morte": (
        "It vanishes completely in winter and comes back from the crown in May: do not assume it is dead"
    ),
    "Ne pas espérer de fruit au nord de la Loire — c'est la partie aérienne qui est récoltée": (
        "Do not expect fruit north of the Loire — it is the top growth that is gathered"
    ),
    "Lui donner un mur au sud et un paillis épais pour passer l'hiver": (
        "Give it a south-facing wall and a thick mulch to get through winter"
    ),
    "Allergisante chez les personnes sensibles aux astéracées": (
        "An allergen in people sensitive to the daisy family"
    ),
    "Annuelle, à ne pas confondre avec la camomille romaine, vivace : son réceptacle est creux quand on le coupe en deux": (
        "Annual, not to be confused with the perennial Roman chamomile: its receptacle is hollow when you cut one in half"
    ),
    "Semer en surface sans recouvrir, la graine est minuscule": (
        "Sow on the surface without covering; the seed is tiny"
    ),
    "Cueillir les capitules un à un, au plus chaud d'une journée sèche": (
        "Pick the flower heads one by one, at the hottest point of a dry day"
    ),
    "Irritante pour la bouche de l'homme et de l'animal : à mettre hors de portée d'un chat ou d'un petit enfant": (
        "Irritant to the mouth, human or animal: keep it out of reach of a cat or a small child"
    ),
    "Ses découpes n'apparaissent qu'avec l'âge et la lumière : une jeune feuille pleine est normale": (
        "Its splits only appear with age and light: a solid young leaf is normal"
    ),
    "Lui donner un tuteur-mousse, ses racines aériennes s'y accrochent": (
        "Give it a moss pole; its aerial roots take hold on it"
    ),
    "Dépoussiérer les feuilles : c'est par elles qu'elle respire": (
        "Dust the leaves: they are how it breathes"
    ),
    "Irritante par ses oxalates : la suspendre hors d'atteinte si un animal grignote": (
        "Irritant through its oxalates: hang it out of reach if an animal nibbles"
    ),
    "La plante la plus indulgente du rayon : elle survit à l'oubli et au fond d'une pièce": (
        "The most forgiving plant on the shelf: it survives neglect and the back of a room"
    ),
    "Une tige coupée sous un nœud racine en deux semaines dans un verre d'eau": (
        "A stem cut below a node roots within a fortnight in a glass of water"
    ),
    "Ses panachures pâlissent dans l'ombre : la rapprocher d'une fenêtre pour les garder": (
        "Its variegation fades in shade: move it nearer a window to keep it"
    ),
    "Irritante par ses oxalates, pour l'homme comme pour l'animal": (
        "Irritant through its oxalates, for people as much as for animals"
    ),
    "Pincer les tiges régulièrement, sans quoi elle file en lianes nues": (
        "Pinch the stems regularly, or it runs away into bare vines"
    ),
    "Le pot doit pouvoir s'égoutter : l'eau stagnante lui pourrit les racines": (
        "The pot must be able to drain: standing water rots its roots"
    ),
    "Irritante par ses oxalates : c'est la plante d'intérieur la plus souvent signalée aux centres antipoison vétérinaires": (
        "Irritant through its oxalates: it is the houseplant most often reported to veterinary poison centres"
    ),
    "Fleurit peu dans l'ombre profonde : lumière vive indirecte, sans soleil direct": (
        "It flowers little in deep shade: bright indirect light, no direct sun"
    ),
    "Ne pas se fier à l'affaissement comme méthode d'arrosage : répété, il abîme les racines": (
        "Do not use the drooping as a watering method: repeated, it damages the roots"
    ),
    "Irritante par ses oxalates et ses saponines, concentrées dans les tiges et les rhizomes": (
        "Irritant through its oxalates and saponins, concentrated in the stems and rhizomes"
    ),
    "Elle meurt bien plus souvent d'excès d'eau que de sécheresse : en cas de doute, ne pas arroser": (
        "It dies of too much water far more often than of drought: when in doubt, do not water"
    ),
    "Ses rhizomes stockent l'eau : elle encaisse un mois d'absence sans broncher": (
        "Its rhizomes store water: it takes a month's absence without flinching"
    ),
    "La plus toxique du rayon : sa sève provoque une douleur buccale intense et un gonflement qui peut gêner la parole — à écarter d'un foyer avec enfant en bas âge ou animal": (
        "The most toxic on the shelf: its sap causes intense mouth pain and a swelling that can impede speech — keep it out of a home with a toddler or an animal"
    ),
    "Porter des gants pour la bouturer, et se laver les mains après": (
        "Wear gloves to take cuttings, and wash your hands afterwards"
    ),
    "Ses feuilles brûlent au soleil direct : lumière tamisée uniquement": (
        "Its leaves scorch in direct sun: filtered light only"
    ),
    "Ses saponines provoquent vomissements et diarrhée chez le chien et le chat ; sans gravité chez l'adulte": (
        "Its saponins cause vomiting and diarrhoea in dogs and cats; harmless in an adult"
    ),
    "Elle supporte tout sauf l'excès d'eau : c'est la seule faute qui la tue": (
        "It takes anything but too much water: that is the one mistake that kills it"
    ),
    "Elle se contente du fond d'une pièce, mais pousse trois fois plus vite près d'une fenêtre": (
        "It makes do with the back of a room, but grows three times faster near a window"
    ),
    "Une feuille coupée en tronçons et plantée dans du sable donne un nouveau pied": (
        "A leaf cut into sections and set in sand gives a new plant"
    ),
    "Ses saponines rendent le chat malade ; les extrémités de feuilles tentent les chats, les mettre en hauteur": (
        "Its saponins make a cat ill; the leaf tips tempt cats, so put it up high"
    ),
    "Les pointes brunes signalent presque toujours un excès de fluor ou de chlore : laisser l'eau reposer une nuit": (
        "Brown tips nearly always mean too much fluoride or chlorine: let the water stand overnight"
    ),
    "Une tige dégarnie peut être étêtée : elle repart en deux ou trois têtes": (
        "A bare stem can be topped: it comes back as two or three heads"
    ),
    "Aucune toxicité connue pour le chien ni le chat": (
        "No known toxicity to dogs or cats"
    ),
    "Surnommée la plante du fer forgé : elle vit dans les coins que rien d'autre ne supporte": (
        "Nicknamed the cast-iron plant: it lives in corners nothing else will take"
    ),
    "Elle tient 5 °C : c'est la seule du rayon qui passe l'hiver dans une cage d'escalier non chauffée": (
        "It takes 5 °C: the only one here that winters in an unheated stairwell"
    ),
    "Sa croissance est très lente — deux ou trois feuilles par an, c'est normal": (
        "Its growth is very slow — two or three leaves a year is normal"
    ),
    "Non toxique pour le chien et le chat selon l'ASPCA — mais les chats s'y intéressent et peuvent vomir d'en avoir trop mangé": (
        "Non-toxic to dogs and cats per the ASPCA — but cats take an interest and may be sick from eating too much"
    ),
    "Ses stolons portent des plantules qui racinent dans un verre d'eau": (
        "Its runners carry plantlets that root in a glass of water"
    ),
    "Les pointes brunes viennent du calcaire de l'eau du robinet": (
        "Brown tips come from the lime in tap water"
    ),
    "Non toxique pour le chien et le chat selon l'ASPCA": (
        "Non-toxic to dogs and cats per the ASPCA"
    ),
    "La plus difficile de cette liste : elle veut 60 % d'humidité et brunit sèchement en appartement chauffé": (
        "The hardest on this list: it wants 60% humidity and browns off dryly in a heated flat"
    ),
    "Le calcaire de l'eau du robinet lui brûle le bord des feuilles : c'est la cause la plus fréquente d'échec": (
        "The lime in tap water scorches its leaf edges: this is the commonest cause of failure"
    ),
    "La poser sur un lit de billes d'argile humides, jamais les pieds dans l'eau": (
        "Stand it on a bed of damp clay pebbles, never with its feet in water"
    ),
    "Elle replie ses feuilles la nuit : c'est son fonctionnement normal, pas un signe de soif": (
        "It folds its leaves up at night: that is how it works, not a sign of thirst"
    ),
    "Plus indulgente que la calathea, pour un feuillage presque aussi beau": (
        "More forgiving than the calathea, for foliage nearly as good"
    ),
    "La tourner d'un quart de tour chaque semaine, sinon elle penche vers la fenêtre": (
        "Turn it a quarter turn each week, or it leans towards the window"
    ),
    "Elle produit des rejets au pied : les détacher avec un peu de racine et les rempoter": (
        "It makes offsets at the base: detach them with a little root and pot them on"
    ),
    "Petite et lente : idéale sur un bureau, elle ne dépassera pas trente centimètres": (
        "Small and slow: ideal on a desk, it will not pass thirty centimetres"
    ),
    "Une feuille piquée dans du terreau humide donne un nouveau pied": (
        "A leaf pushed into damp compost gives a new plant"
    ),
    "Ne jamais couper le pédoncule après la floraison : elle refleurit dessus l'année suivante": (
        "Never cut the flower stalk after flowering: it blooms again on the same one next year"
    ),
    "Elle ne fleurit qu'une fois à l'étroit dans son pot : ne pas la rempoter trop vite": (
        "It flowers only once snug in its pot: do not pot it on too soon"
    ),
    "Il lui faut quelques heures de soleil filtré pour fleurir": (
        "It needs a few hours of filtered sun to flower"
    ),
    "L'eau versée au centre de la rosette la fait pourrir : c'est la faute classique": (
        "Water poured into the centre of the rosette rots it: that is the classic mistake"
    ),
    "Une salle de bains éclairée est son meilleur emplacement en appartement": (
        "A lit bathroom is its best spot in a flat"
    ),
    "Ne jamais lustrer ses frondes : les produits lustrants les brûlent": (
        "Never polish its fronds: leaf-shine products scorch them"
    ),
    "Non toxique pour le chien et le chat selon l'ASPCA : c'est le grand sujet de foyer avec animaux": (
        "Non-toxic to dogs and cats per the ASPCA: that is the whole question in a home with animals"
    ),
    "Croissance très lente : une ou deux palmes par an, et un grand sujet coûte cher pour cette raison": (
        "Very slow growing: one or two fronds a year, which is why a large specimen costs what it does"
    ),
    "Ne jamais couper le sommet d'un stipe : un palmier n'a qu'un bourgeon et ne repartira pas": (
        "Never cut the top off a stem: a palm has one bud and will not come back"
    ),
    "Les araignées rouges l'attaquent en air sec : doucher le feuillage une fois par mois": (
        "Red spider mite attacks it in dry air: shower the foliage once a month"
    ),
    "Jamais de terreau : ses racines sont aériennes et étouffent dedans": (
        "Never compost: its roots are aerial and suffocate in it"
    ),
    "Des racines vertes après arrosage et argentées ensuite indiquent un rythme juste": (
        "Roots green after watering and silvery afterwards mean the rhythm is right"
    ),
    "Après la floraison, couper la hampe un centimètre au-dessus du deuxième œil": (
        "After flowering, cut the stem a centimetre above the second node"
    ),
    "Le latex jaune sous la peau de la feuille est purgatif et rend chiens et chats malades : non toxique ne vaut que pour le gel transparent du cœur": (
        "The yellow latex under the leaf skin is a purgative and makes dogs and cats ill: non-toxic applies only to the clear gel at the centre"
    ),
    "L'erreur fatale est l'arrosage d'hiver : la plante est au repos et pourrit": (
        "The fatal mistake is watering in winter: the plant is dormant and rots"
    ),
    "Il lui faut le rebord de fenêtre le plus ensoleillé de la maison": (
        "It wants the sunniest windowsill in the house"
    ),
    "Elle peut passer l'été dehors, rentrée avant que les nuits descendent sous 10 °C": (
        "It can spend the summer outdoors, brought in before nights drop below 10 °C"
    ),
    "Toxique pour le chien et le chat, qui vomissent et deviennent apathiques": (
        "Toxic to dogs and cats, which vomit and turn listless"
    ),
    "Ses feuilles qui se rident disent la soif mieux que n'importe quel calendrier": (
        "Its leaves wrinkling tell you it is thirsty better than any calendar"
    ),
    "Un pot étroit et lourd l'empêche de verser quand elle grossit": (
        "A narrow, heavy pot stops it tipping over as it fills out"
    ),
    "Elle vit cinquante ans et se transmet : c'est la plante grasse des maisons de famille": (
        "It lives fifty years and gets handed down: this is the succulent of family houses"
    ),
    "Son latex blanc irrite la peau et la bouche, de l'homme comme de l'animal : couper avec des gants": (
        "Its white latex irritates skin and mouth, human and animal alike: cut it wearing gloves"
    ),
    "Il n'aime pas qu'on le déplace : trouver sa place et ne plus y toucher": (
        "It dislikes being moved: find its place and leave it there"
    ),
    "Dépoussiérer les feuilles à l'éponge humide, elles captent beaucoup": (
        "Dust the leaves with a damp sponge; they catch a great deal"
    ),
    "Étêter un sujet trop haut le fait ramifier": (
        "Topping a specimen that has grown too tall makes it branch"
    ),
    "Son latex blanc irrite la peau et la bouche, comme chez tous les ficus": (
        "Its white latex irritates skin and mouth, as in every ficus"
    ),
    "Le plus capricieux des ficus : courant d'air, déplacement ou arrosage irrégulier lui font perdre ses feuilles": (
        "The most temperamental of the figs: a draught, a move or uneven watering all make it drop leaves"
    ),
    "Il veut beaucoup de lumière indirecte, à moins d'un mètre d'une grande fenêtre": (
        "It wants plenty of indirect light, within a metre of a large window"
    ),
    "Les feuilles perdues en bas ne repoussent jamais au même endroit": (
        "Leaves lost at the bottom never grow back in the same place"
    ),
}
