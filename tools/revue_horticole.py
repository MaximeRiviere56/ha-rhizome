#!/usr/bin/env python3
"""Revue croisee des donnees de culture, contre des relevés sourcés.

Pourquoi ce fichier contient des donnees et non du reseau, contrairement a
`revue_croisee.py` : **aucune API ne sert de calendriers de culture.** OpenFarm
est mort, Permapeople demande une cle, practicalplants ne repond plus, et les
bases taxonomiques ignorent l'horticulture. La verification se fait donc a la
main, source par source — et ce qu'elle produit doit alors etre *conserve*,
sinon chaque relecture repart de zero et le travail n'est vrai qu'au jour ou
il est fait.

Chaque entree de `RELEVES` est un fait releve dans une source nommee, avec son
URL. Le script ne les croit pas : il les compare a la fiche et dit ou ca
diverge, et de combien.

**Ce qui est verifiable, et ce qui ne l'est pas.** Une revue croisee ne rend
pas ces champs « vrais » — l'espacement, l'eau et les durees de cycle
dependent de la variete, du sol et du climat, et trois sources serieuses
donnent trois chiffres. Ce qu'elle etablit est plus modeste et plus utile :
une **fourchette plausible**, et le constat qu'une valeur de fiche en sort.
C'est une alerte, pas un verdict. Ne presente jamais ce fichier comme une
preuve d'exactitude.

Les offsets sont exprimes en jours par rapport a la derniere gelee, comme dans
le catalogue : une source qui dit « fin avril » pour une derniere gelee au
15 avril vaut +15.

**Verifie toujours que la page recuperee parle bien de la plante.** Le piege
s'est presente trois fois sur une vingtaine de fiches, et il est silencieux :
une URL construite par analogie rend une page de garde, ou pire, une autre
plante. Gerbeaud a servi la fiche de l'agerate pour une demande sur la tomate,
et la page « groseillier » d'Au Jardin decrit un groseillier a fleurs — elle
dit le fruit « sans interet », ce qui ne laisse aucun doute. Une source qui se
trompe de plante est pire qu'une source absente : elle vote.

Usage : python3 tools/revue_horticole.py [--tout]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
CATALOGUE = RACINE / "custom_components" / "rhizome" / "data" / "catalog.json"

SOURCES = {
    "rhs": ("Royal Horticultural Society", "https://www.rhs.org.uk"),
    "almanac": ("The Old Farmer's Almanac", "https://www.almanac.com"),
    "aujardin": ("Au Jardin", "https://www.aujardin.info"),
    "gerbeaud": ("Gerbeaud", "https://www.gerbeaud.com"),
    "anses": ("Anses — toxicovigilance", "https://www.anses.fr"),
    "ema": ("Agence europeenne du medicament, monographies HMPC",
            "https://www.ema.europa.eu"),
    "aspca": ("ASPCA — plantes toxiques", "https://www.aspca.org"),
    "plandejardin": ("Plan de jardin — jardin biologique",
                     "https://plandejardin-jardinbiologique.com"),
    # Pour les fruitiers, les tables de pepinieristes valent mieux qu'une
    # fiche par espece : elles donnent la distance *par porte-greffe et par
    # forme*, qui est la seule facon honnete de repondre — un pommier sur M7
    # et un pommier sur franc ne se plantent pas a la meme distance.
    "pepins": ("Pépins & Cie, pépiniériste", "https://pepinsetcie.fr"),
    "willemse": ("Willemse France", "https://conseils-jardin.willemsefrance.fr"),
    "monjardin": ("Mon Jardin Paysager", "https://monjardinpaysager.fr"),
    "biogarten": ("Biogarten", "https://www.biogarten.ch"),
    "senura": ("Senura, station de recherche sur la noix", "https://senura.com"),
}

# Les champs relevables, et ce que chacun signifie ici.
#   espacement_cm        : distance entre plants, en centimetres
#   profondeur_cm        : profondeur de semis, en centimetres
#   offset_plantation    : jours apres la derniere gelee pour la mise en place
#   offset_semis_direct  : idem pour un semis en place
#   offset_semis_abri    : jours avant la derniere gelee pour un semis a l'abri
#   jours_plant_recolte  : plantation -> recolte, en jours
#   jours_semis_recolte  : semis -> recolte, en jours
#
# Piege a connaitre avant de relever un « days to maturity » anglo-saxon : il
# se compte **depuis le repiquage** pour une culture que l'on repique (tomate,
# poivron, aubergine) et **depuis le semis** pour une culture semee en place
# (carotte, radis, haricot). Le lire comme « semis -> recolte » dans le premier
# cas fait apparaitre un ecart de cinquante jours qui n'existe pas.
#   besoin_eau           : faible | moyen | eleve
#   temp_min_c           : temperature en dessous de laquelle la plante souffre
#
# Une valeur peut etre un nombre ou un couple (mini, maxi) quand la source
# donne une fourchette — et elle en donne presque toujours une.

# Deux tables francaises d'ecartement au potager, qui couvrent a elles seules
# une trentaine de legumes. Memes raisons que les tables de pepinieristes pour
# les fruitiers : interroger trente fiches une a une aurait coute trente fois
# plus pour la meme donnee, et une table est plus coherente avec elle-meme
# qu'une collection de pages ecrites separement.
PLAN = "https://plandejardin-jardinbiologique.com/distance-pantation-legume-au-potager.html"
GERB = "https://www.gerbeaud.com/jardin/fiches/bonne-distance-plantation,1308.html"

# Pour les plantes d'interieur, la cote de rusticite RHS est le seul chiffre
# comparable qui existe : H1a au-dessus de 15 °C, H1b de 10 a 15, H1c de 5 a
# 10, H2 de 1 a 5. Les fiches RHS donnent aussi l'exposition, l'eau et
# l'envergure adulte, ce qui couvre tout ce que la fiche affirme d'elles —
# elles n'ont ni fenetre, ni cycle, ni profondeur de semis.
# Les medicinales sont des sauvages de France, et Au Jardin les indexe par
# leur nom latin — `plantago-lanceolata` et non `plantain`. C'est ce qui les
# rendait introuvables : l'URL devinee depuis le nom francais rend une page
# d'accueil, sans le dire.
AJ = "https://www.aujardin.info/plantes"
R = "https://www.rhs.org.uk/herbs"
V = "https://www.rhs.org.uk/vegetables"

# Les engrais verts se sement a la volee : la RHS ne donne ni ecartement ni
# besoin en eau pour eux, seulement des periodes de semis. Et ces periodes
# s'etendent sur cinq a six mois, ce qui ne falsifie pas grand-chose — une
# fenetre aussi large accepte presque n'importe quelle valeur de fiche. Le
# releve est donc honnete mais faible, et il vaut d'etre dit : confirmer une
# date dans un intervalle de six mois n'est pas la confirmer.
GM = "https://www.rhs.org.uk/soil-composts-mulches/green-manures"

RELEVES: dict[str, dict[str, dict]] = {
    "celeri-branche": {
        "rhs": {"url": f"{V}/celery/grow-your-own",
                "espacement_cm": 23, "besoin_eau": "eleve",
                "jours_plant_recolte": (70, 112)},
        "aujardin": {"url": f"{AJ}/celeri-branche.php", "besoin_eau": "eleve"},
    },
    "cresson-fontaine": {
        "aujardin": {"url": f"{AJ}/cresson-fontaine.php", "besoin_eau": "eleve"},
    },
    "ail-ours": {
        "aujardin": {"url": f"{AJ}/ail-des-ours.php",
                     "besoin_eau": "moyen", "temp_min_c": -34},
    },
    "houblon": {
        "aujardin": {"url": f"{AJ}/houblon.php", "besoin_eau": "moyen"},
    },
    # Memes especes que `tomate` et `mais-doux` : la tomate cerise est
    # Solanum lycopersicum var. cerasiforme, le mais a eclater un Zea mays
    # comme le mais doux. Les sources de l'espece valent pour la variete,
    # et les recopier plutot que les reutiliser creerait deux verites.
    "tomate-cerise": {
        "rhs": {"url": "https://www.rhs.org.uk/vegetables/tomatoes/grow-your-own",
                "espacement_cm": (45, 60), "besoin_eau": "eleve"},
        "aujardin": {"url": f"{AJ}/tomate.php",
                     "espacement_cm": 50, "besoin_eau": "eleve"},
    },
    "mais-popcorn": {
        "rhs": {"url": f"{V}/sweetcorn/grow-your-own",
                "espacement_cm": (34, 45), "profondeur_cm": 2.5,
                "temp_min_c": 10},
    },
    "radis-noir": {
        "rhs": {"url": f"{V}/radishes/grow-your-own",
                # « 15-20cm for winter/oriental types »
                "espacement_cm": (15, 20), "profondeur_cm": 2,
                "besoin_eau": "moyen"},
    },
    "argousier": {
        "aujardin": {"url": f"{AJ}/hippophae-rhamnoides.php",
                     "besoin_eau": "moyen", "temp_min_c": -40},
    },
    "goji": {
        "aujardin": {"url": f"{AJ}/lycium-barbarum.php",
                     "besoin_eau": "faible", "temp_min_c": -22},
    },
    "sureau-noir": {
        "aujardin": {"url": f"{AJ}/sambucus-nigra.php", "besoin_eau": "faible"},
    },
    "physalis": {
        "aujardin": {"url": f"{AJ}/physalis-peruviana.php",
                     "besoin_eau": "moyen", "espacement_cm": 100},
    },
    "bourrache": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/borage",
                "besoin_eau": "faible"},
    },
    "capucine": {
        "aujardin": {"url": f"{AJ}/capucine.php",
                     "espacement_cm": (40, 50), "besoin_eau": "moyen",
                     "temp_min_c": 0},
    },
    "souci": {
        "aujardin": {"url": f"{AJ}/souci.php",
                     "espacement_cm": (10, 15), "besoin_eau": "faible"},
    },
    "moutarde-blanche": {
        "rhs": {"url": GM, "offset_semis_direct": (-45, 168)},
    },
    "phacelie": {
        "rhs": {"url": GM, "offset_semis_direct": (-14, 138)},
    },
    "vesce": {
        "rhs": {"url": GM, "offset_semis_direct": (-45, 168)},
    },
    "trefle-incarnat": {
        "rhs": {"url": GM, "offset_semis_direct": (-45, 138)},
    },
    "seigle": {
        "rhs": {"url": GM, "offset_semis_direct": (108, 229)},
    },
    "sarrasin": {
        "rhs": {"url": GM, "offset_semis_direct": (-14, 138)},
    },
    "celeri-rave": {
        "rhs": {"url": f"{V}/celeriac/grow-your-own", "espacement_cm": 30, "besoin_eau": "eleve", "jours_plant_recolte": (120, 180)},
    },
    "feve": {
        "rhs": {"url": f"{V}/broad-beans/grow-your-own", "espacement_cm": (15, 23), "profondeur_cm": 5, "besoin_eau": "moyen"},
    },
    "haricot-espagne": {
        "rhs": {"url": f"{V}/runner-beans/grow-your-own", "espacement_cm": 30, "profondeur_cm": 5, "besoin_eau": "eleve"},
    },
    "chou-rave": {
        "rhs": {"url": f"{V}/kohl-rabi/grow-your-own", "espacement_cm": 15, "profondeur_cm": 1.5, "besoin_eau": "moyen", "jours_semis_recolte": (42, 84)},
        "plandejardin": {"url": PLAN, "espacement_cm": 15},
        "gerbeaud": {"url": GERB, "espacement_cm": 70},
    },
    "patate-douce": {
        "rhs": {"url": f"{V}/sweet-potatoes/grow-your-own", "espacement_cm": 30, "besoin_eau": "eleve", "jours_plant_recolte": (120, 150)},
    },
    "chou-kale": {
        "rhs": {"url": f"{V}/kale/grow-your-own", "espacement_cm": (30, 60), "profondeur_cm": 1, "besoin_eau": "moyen"},
        "plandejardin": {"url": PLAN, "espacement_cm": (50, 60)},
        "gerbeaud": {"url": GERB, "espacement_cm": 70},
    },
    "chou-bruxelles": {
        "rhs": {"url": f"{V}/brussels-sprouts/grow-your-own", "espacement_cm": 60, "profondeur_cm": 2, "besoin_eau": "moyen"},
        "plandejardin": {"url": PLAN, "espacement_cm": (40, 60)},
        "gerbeaud": {"url": GERB, "espacement_cm": 70},
    },
    "blette": {
        "rhs": {"url": f"{V}/chard/grow-your-own", "espacement_cm": 30, "profondeur_cm": 2.5, "besoin_eau": "moyen"},
        "plandejardin": {"url": PLAN, "espacement_cm": 15},
        "gerbeaud": {"url": GERB, "espacement_cm": 40},
    },
    "roquette": {
        "rhs": {"url": f"{V}/rocket/grow-your-own", "espacement_cm": 15, "profondeur_cm": 1, "besoin_eau": "moyen", "jours_semis_recolte": (28, 42)},
    },
    "fenouil-bulbeux": {
        "rhs": {"url": f"{V}/florence-fennel/grow-your-own", "espacement_cm": (10, 30), "profondeur_cm": 1.5, "besoin_eau": "eleve", "jours_semis_recolte": (90, 120)},
    },
    "navet": {
        "rhs": {"url": f"{V}/turnips/grow-your-own", "espacement_cm": (15, 23), "profondeur_cm": 1, "besoin_eau": "moyen", "jours_semis_recolte": (42, 70)},
        "plandejardin": {"url": PLAN, "espacement_cm": (5, 15)},
        "gerbeaud": {"url": GERB, "espacement_cm": 10},
    },
    "aneth": {
        "rhs": {"url": f"{R}/dill/grow-your-own", "espacement_cm": 20, "profondeur_cm": 1, "besoin_eau": "moyen"},
    },
    "coriandre": {
        "rhs": {"url": f"{R}/coriander/grow-your-own", "espacement_cm": (5, 20), "besoin_eau": "moyen"},
    },
    "cerfeuil": {
        "rhs": {"url": f"{R}/chervil/grow-your-own", "espacement_cm": 15, "profondeur_cm": 1, "besoin_eau": "moyen"},
    },
    "estragon": {
        "rhs": {"url": f"{R}/tarragon/grow-your-own", "espacement_cm": (20, 30), "besoin_eau": "faible"},
    },
    "laurier-sauce": {
        "rhs": {"url": f"{R}/bay/grow-your-own", "besoin_eau": "faible"},
    },
    "marjolaine": {
        "rhs": {"url": f"{R}/marjoram/grow-your-own", "espacement_cm": (20, 50), "besoin_eau": "faible"},
    },
    "melisse": {
        "rhs": {"url": f"{R}/lemon-balm/grow-your-own", "besoin_eau": "faible"},
    },
    "sarriette": {
        "rhs": {"url": f"{R}/savory/grow-your-own", "espacement_cm": (20, 30), "besoin_eau": "faible"},
    },
    "liveche": {
        "rhs": {"url": f"{R}/lovage/grow-your-own", "espacement_cm": (30, 100), "besoin_eau": "moyen"},
    },
    "groseillier-maquereau": {
        "rhs": {"url": "https://www.rhs.org.uk/fruit/gooseberries/grow-your-own",
                "espacement_cm": (120, 150), "besoin_eau": "faible"},
    },
    "vigne-table": {
        "rhs": {"url": "https://www.rhs.org.uk/fruit/grapes/grow-your-own",
                "espacement_cm": (120, 150), "besoin_eau": "faible"},
    },
    "camerisier": {
        "rhs": {"url": "https://www.rhs.org.uk/fruit/honeyberry/grow-your-own",
                "temp_min_c": -40},
    },
    "framboisier-remontant": {
        "rhs": {"url": "https://www.rhs.org.uk/fruit/raspberries/grow-your-own",
                "espacement_cm": (40, 60), "besoin_eau": "moyen"},
        "almanac": {"url": "https://www.almanac.com/plant/raspberries",
                    "espacement_cm": 45, "besoin_eau": "moyen"},
    },
    "fraisier-remontant": {
        "rhs": {"url": "https://www.rhs.org.uk/fruit/strawberries/grow-your-own",
                "espacement_cm": (35, 40), "besoin_eau": "eleve"},
        "aujardin": {"url": "https://www.aujardin.info/plantes/fraisier.php",
                     "besoin_eau": "eleve"},
        "gerbeaud": {"url": GERB, "espacement_cm": 30},
    },
    "artichaut": {
        "aujardin": {"url": f"{AJ}/artichaut.php",
                     "besoin_eau": "moyen", "temp_min_c": (-12, -10)},
        "gerbeaud": {"url": GERB, "espacement_cm": 80},
    },
    "asperge": {
        "aujardin": {"url": f"{AJ}/asperge.php",
                     "besoin_eau": "moyen", "espacement_cm": 60},
    },
    "rhubarbe": {
        "aujardin": {"url": f"{AJ}/rhubarbe.php",
                     "besoin_eau": "eleve", "espacement_cm": (100, 150)},
    },
    "oseille": {
        "aujardin": {"url": f"{AJ}/oseille.php",
                     "besoin_eau": "moyen", "espacement_cm": 20},
    },
    "topinambour": {
        "aujardin": {"url": f"{AJ}/topinambour.php",
                     "besoin_eau": "moyen", "espacement_cm": 40,
                     "profondeur_cm": 10},
    },
    "mache": {
        "aujardin": {"url": f"{AJ}/mache.php", "besoin_eau": "moyen"},
    },
    "ortie": {
        # 120 cm est la hauteur, pas l'ecartement : la source ne donne pas
        # de distance de plantation, et la confondre avec la hauteur etait
        # mon erreur, pas celle de la fiche.
        "aujardin": {"url": f"{AJ}/ortie.php", "besoin_eau": "moyen"},
    },
    "millepertuis": {
        "aujardin": {"url": f"{AJ}/millepertuis.php", "besoin_eau": "faible"},
    },
    "pissenlit": {
        "aujardin": {"url": f"{AJ}/pissenlit.php",
                     "besoin_eau": "moyen", "espacement_cm": (10, 15)},
    },
    "eglantier": {
        # 1 a 3 m est la hauteur de l'arbuste, pas sa distance de plantation.
        "aujardin": {"url": f"{AJ}/eglantier.php", "besoin_eau": "moyen"},
    },
    "achillee": {
        "aujardin": {"url": f"{AJ}/achillea-millefolium.php",
                     "besoin_eau": "faible", "temp_min_c": -29, "espacement_cm": (40, 50)},
    },
    "plantain-lanceole": {
        "aujardin": {"url": f"{AJ}/plantago-lanceolata.php",
                     "besoin_eau": "faible"},
    },
    "aubepine": {
        "aujardin": {"url": f"{AJ}/crataegus-monogyna.php",
                     "besoin_eau": "faible", "temp_min_c": -29},
    },
    "reine-des-pres": {
        "aujardin": {"url": f"{AJ}/filipendula-ulmaria.php",
                     "besoin_eau": "eleve", "temp_min_c": -25, "espacement_cm": 40},
    },
    "guimauve": {
        "aujardin": {"url": f"{AJ}/althaea-officinalis.php",
                     "besoin_eau": "moyen", "temp_min_c": -24},
    },
    "bardane": {
        "aujardin": {"url": f"{AJ}/arctium-lappa.php",
                     "besoin_eau": "moyen", "temp_min_c": -34, "espacement_cm": 20},
    },
    "bouillon-blanc": {
        "aujardin": {"url": f"{AJ}/verbascum-thapsus.php",
                     "besoin_eau": "faible", "temp_min_c": -24, "espacement_cm": 50},
    },
    "tanaisie": {
        "aujardin": {"url": f"{AJ}/tanacetum-vulgare.php",
                     "besoin_eau": "faible", "temp_min_c": -22},
    },
    "armoise-absinthe": {
        "aujardin": {"url": f"{AJ}/artemisia-absinthium.php",
                     "besoin_eau": "moyen", "espacement_cm": 100},
    },
    "tilleul": {
        "aujardin": {"url": f"{AJ}/tilia-cordata.php",
                     "besoin_eau": "moyen", "temp_min_c": -24},
    },
    "onagre": {
        "aujardin": {"url": f"{AJ}/oenothera-biennis.php",
                     "besoin_eau": "faible", "temp_min_c": -24},
    },
    "passiflore": {
        "aujardin": {"url": f"{AJ}/passiflora-incarnata.php",
                     "besoin_eau": "moyen", "temp_min_c": -20},
    },
    "aspidistra": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/1715/aspidistra-elatior/details",  # cote H3
                "temp_min_c": (-5, 1), "besoin_eau": "moyen", "espacement_cm": (10, 50)},
    },
    "crassula": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/4739/crassula-ovata/details",  # cote H2
                "temp_min_c": (1, 5), "besoin_eau": "faible", "espacement_cm": (100, 150)},
    },
    "dieffenbachia": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/31781/dieffenbachia-seguine/details",  # cote H1a
                "temp_min_c": (15, 20), "besoin_eau": "moyen", "espacement_cm": (100, 100)},
    },
    "ficus-elastica": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/95720/ficus-elastica/details",  # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "moyen", "espacement_cm": (100, 150)},
    },
    "spathiphyllum": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/17623/spathiphyllum-wallisii/details",  # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "eleve", "espacement_cm": (10, 50)},
    },
    "aloe-vera": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/981/aloe-vera/details",  # cote H1c
                "temp_min_c": (5, 10), "besoin_eau": "faible", "espacement_cm": (50, 100)},
    },
    "ficus-lyrata": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/7207/ficus-lyrata/details",  # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "moyen", "espacement_cm": (100, 150)},
    },
    "calathea": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/calathea",
                "espacement_cm": (10, 250)},
    },
    "chlorophytum": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/spider-plants",
                "espacement_cm": (10, 50)},
    },
    "dracaena-marginata": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/dracaena",
                "espacement_cm": (100, 150)},
    },
    "sansevieria": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/sansevieria",
                # « toujours les garder au-dessus de 10 °C »
                "temp_min_c": 10, "besoin_eau": "faible",
                "espacement_cm": (10, 50)},
    },
    "orchidee-phalaenopsis": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/pdfs/rhs-recommended-award-of-garden-merit-orchids.pdf",
                # cote H1a
                "temp_min_c": (15, 20)},
    },
    "monstera": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/11192/monstera-deliciosa-f/details",
                # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "moyen",
                "espacement_cm": (150, 250)},
    },
    "pothos": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/91403/epipremnum-aureum/details",
                # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "moyen",
                "espacement_cm": (100, 150)},
    },
    "zamioculcas": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/19185/zamioculcas-zamiifolia/details",
                # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "faible",
                "espacement_cm": (50, 100)},
    },
    "philodendron": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/514461/philodendron-hederaceum/details",
                # cote H1a
                "temp_min_c": (15, 20), "besoin_eau": "moyen",
                "espacement_cm": (50, 100)},
    },
    "maranta": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/119598/maranta-leuconeura/details",
                # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "moyen",
                "espacement_cm": (10, 50)},
    },
    "pilea": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/13015/i-pilea-peperomioides-i/details",
                # cote H1c
                "temp_min_c": (5, 10), "besoin_eau": "faible",
                "espacement_cm": (10, 50)},
    },
    "peperomia": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/106212/peperomia-obtusifolia/details",
                # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "faible",
                "espacement_cm": (10, 50)},
    },
    "hoya": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/8852/hoya-carnosa/details",
                # cote H2
                "temp_min_c": (1, 5), "besoin_eau": "faible",
                "espacement_cm": (100, 150)},
    },
    "fougere-nid": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/1728/asplenium-nidus/details",
                # cote H1b
                "temp_min_c": (10, 15), "besoin_eau": "moyen",
                "espacement_cm": (50, 100)},
    },
    "kentia": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/8845/howea-forsteriana/details",
                # cote H1a
                "temp_min_c": (15, 20), "besoin_eau": "moyen"},
    },
    "ail-blanc": {
        "plandejardin": {"url": PLAN, "espacement_cm": (12, 15)},
        "gerbeaud": {"url": GERB, "espacement_cm": 15},
    },
    "ail-rose": {
        "plandejardin": {"url": PLAN, "espacement_cm": (12, 15)},
        "gerbeaud": {"url": GERB, "espacement_cm": 15},
    },
    "chicoree-frisee": {
        "plandejardin": {"url": PLAN, "espacement_cm": 30},
    },
    "chou-chinois": {
        "plandejardin": {"url": PLAN, "espacement_cm": (30, 45)},
        "gerbeaud": {"url": GERB, "espacement_cm": 70},
    },
    "chou-milan": {
        "plandejardin": {"url": PLAN, "espacement_cm": (30, 45)},
        "gerbeaud": {"url": GERB, "espacement_cm": 70},
    },
    "chou-rouge": {
        "plandejardin": {"url": PLAN, "espacement_cm": (30, 45)},
        "gerbeaud": {"url": GERB, "espacement_cm": 70},
    },
    "citrouille": {
        "plandejardin": {"url": PLAN, "espacement_cm": (90, 150)},
        "gerbeaud": {"url": GERB, "espacement_cm": 100},
    },
    "cornichon": {
        "plandejardin": {"url": PLAN, "espacement_cm": (40, 50)},
        "gerbeaud": {"url": GERB, "espacement_cm": 60},
    },
    "courge-butternut": {
        "plandejardin": {"url": PLAN, "espacement_cm": (90, 150)},
        "gerbeaud": {"url": GERB, "espacement_cm": 100},
    },
    "courge-muscade": {
        "plandejardin": {"url": PLAN, "espacement_cm": (90, 150)},
        "gerbeaud": {"url": GERB, "espacement_cm": 100},
    },
    "courge-spaghetti": {
        "plandejardin": {"url": PLAN, "espacement_cm": (90, 150)},
        "gerbeaud": {"url": GERB, "espacement_cm": 100},
    },
    "echalote": {
        "plandejardin": {"url": PLAN, "espacement_cm": (5, 10)},
        "gerbeaud": {"url": GERB, "espacement_cm": 15},
    },
    "endive": {
        "plandejardin": {"url": PLAN, "espacement_cm": (25, 30)},
        "rhs": {"url": "https://www.rhs.org.uk/vegetables/chicory/grow-your-own",
                "espacement_cm": 15, "profondeur_cm": 1, "besoin_eau": "moyen"},
    },
    "haricot-a-rames": {
        "plandejardin": {"url": PLAN, "espacement_cm": 10},
        "gerbeaud": {"url": GERB, "espacement_cm": 40},
    },
    "haricot-sec": {
        "plandejardin": {"url": PLAN, "espacement_cm": (15, 20)},
        "gerbeaud": {"url": GERB, "espacement_cm": 40},
    },
    "laitue-hiver": {
        "plandejardin": {"url": PLAN, "espacement_cm": (25, 30)},
        "gerbeaud": {"url": GERB, "espacement_cm": (30, 40)},
    },
    "mais-doux": {
        "plandejardin": {"url": PLAN, "espacement_cm": (20, 30)},
        "rhs": {"url": "https://www.rhs.org.uk/vegetables/sweetcorn/grow-your-own",
                "espacement_cm": (34, 45), "profondeur_cm": 2.5,
                "temp_min_c": 10},
    },
    "melon": {
        "plandejardin": {"url": PLAN, "espacement_cm": (30, 40)},
        "gerbeaud": {"url": GERB, "espacement_cm": 100},
    },
    "oignon-blanc": {
        "plandejardin": {"url": PLAN, "espacement_cm": (5, 10)},
        "gerbeaud": {"url": GERB, "espacement_cm": 15},
    },
    "oignon-jaune": {
        "plandejardin": {"url": PLAN, "espacement_cm": (5, 10)},
        "gerbeaud": {"url": GERB, "espacement_cm": 15},
    },
    "oignon-rouge": {
        "plandejardin": {"url": PLAN, "espacement_cm": (5, 10)},
        "gerbeaud": {"url": GERB, "espacement_cm": 15},
    },
    "panais": {
        "plandejardin": {"url": PLAN, "espacement_cm": 25},
        "rhs": {"url": "https://www.rhs.org.uk/vegetables/parsnips/grow-your-own",
                "espacement_cm": 15, "profondeur_cm": 1, "besoin_eau": "moyen"},
    },
    "pasteque": {
        "plandejardin": {"url": PLAN, "espacement_cm": (150, 200)},
    },
    "patisson": {
        "plandejardin": {"url": PLAN, "espacement_cm": (60, 100)},
    },
    "piment": {
        "plandejardin": {"url": PLAN, "espacement_cm": (30, 60)},
    },
    "pois-mange-tout": {
        "plandejardin": {"url": PLAN, "espacement_cm": (5, 10)},
        "gerbeaud": {"url": GERB, "espacement_cm": 3},
    },
    "pomme-de-terre": {
        "plandejardin": {"url": PLAN, "espacement_cm": (20, 30)},
        "gerbeaud": {"url": GERB, "espacement_cm": 40},
    },
    "potimarron": {
        "plandejardin": {"url": PLAN, "espacement_cm": (90, 150)},
        "gerbeaud": {"url": GERB, "espacement_cm": 100},
    },
    "salsifis": {
        "plandejardin": {"url": PLAN, "espacement_cm": 10},
    },
    "scarole": {
        "plandejardin": {"url": PLAN, "espacement_cm": 30},
    },
    "tomate": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/tomatoes/grow-your-own",
            "espacement_cm": (45, 60),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/tomatoes",
            "espacement_cm": (60, 90),
            "profondeur_cm": 1.3,
            "offset_semis_abri": -42,
            "offset_plantation": 14,
            "jours_plant_recolte": (60, 100),
            "besoin_eau": "eleve",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/tomate.php",
            "espacement_cm": 50,
            "profondeur_cm": 0.3,
            "offset_semis_abri": -60,
            "offset_plantation": (15, 20),
            "besoin_eau": "eleve",
        },
    },
    "courgette": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/courgettes/grow-your-own",
            "espacement_cm": 90,
            "profondeur_cm": (1.3, 2.5),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/zucchini",
            "espacement_cm": (60, 90),
            "profondeur_cm": 2.5,
            "jours_plant_recolte": 60,
            "besoin_eau": "eleve",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/courgette.php",
            "espacement_cm": 100,
            "offset_plantation": 15,  # « dès que tout risque de gel est écarté »
            "besoin_eau": "eleve",
        },
    },
    "carotte": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/carrots/grow-your-own",
            "espacement_cm": (5, 7.5),
            "profondeur_cm": 1,
            "jours_semis_recolte": (84, 112),
            "besoin_eau": "faible",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/carrots",
            "espacement_cm": (3, 4),
            "profondeur_cm": 0.6,
            "offset_semis_direct": -21,
            "jours_semis_recolte": 60,
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/carotte.php",
            "espacement_cm": (6, 7),
            "jours_semis_recolte": (90, 150),
            "besoin_eau": "moyen",
        },
    },
    "poivron": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/peppers/grow-your-own",
            "espacement_cm": (30, 45),
            "temp_min_c": 12,
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/bell-peppers",
            "espacement_cm": (30, 45),
            "profondeur_cm": 0.6,
            "offset_semis_abri": (-70, -56),
            "offset_plantation": (14, 21),
            "jours_plant_recolte": (60, 90),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/poivron.php",
            "espacement_cm": 60,
            "offset_plantation": 30,
            "temp_min_c": 15,
        },
    },
    "radis": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/radishes/grow-your-own",
            "espacement_cm": (2.5, 5),
            "profondeur_cm": (1, 2),
            "jours_semis_recolte": (28, 42),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/radishes",
            "espacement_cm": (2.5, 5),
            "profondeur_cm": 1.3,
            "offset_semis_direct": -42,
            "jours_semis_recolte": (21, 28),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/radis.php",
            "espacement_cm": 3,
            "profondeur_cm": (1, 2),
            "jours_semis_recolte": (28, 35),
            "besoin_eau": "eleve",
        },
    },
    "laitue": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/lettuce/grow-your-own",
            "espacement_cm": (15, 30),
            "profondeur_cm": 1,
            "jours_semis_recolte": (28, 98),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/lettuce",
            "espacement_cm": (10, 40),
            "profondeur_cm": (0.3, 0.6),
            "offset_semis_abri": (-56, -42),
            "offset_semis_direct": (-28, -14),
            "besoin_eau": "eleve",
            "temp_min_c": -2,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/laitue.php",
            "jours_semis_recolte": 42,
            "besoin_eau": "eleve",
        },
    },
    "haricot-nain": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/french-beans/grow-your-own",
            "espacement_cm": 15,
            "profondeur_cm": 5,
            "jours_semis_recolte": (56, 70),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/beans",
            "espacement_cm": 5,
            "profondeur_cm": 2.5,
            "jours_semis_recolte": (50, 55),
            "temp_min_c": 12,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/haricot.php",
            "espacement_cm": 40,
            "profondeur_cm": 3,
            "offset_semis_direct": 28,  # « mai dans le nord »
            "jours_semis_recolte": 90,
        },
    },
    "petit-pois": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/peas/grow-your-own",
            "espacement_cm": 7.5,
            "profondeur_cm": 5,
            "jours_semis_recolte": (84, 112),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/peas",
            "espacement_cm": 5,
            "profondeur_cm": 2.5,
            "offset_semis_direct": (-42, -28),
            "jours_semis_recolte": (60, 70),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/pois.php",
            "espacement_cm": (2, 3),
            "profondeur_cm": (5, 8),
            "jours_semis_recolte": (70, 80),
            "besoin_eau": "faible",
        },
    },
    "concombre": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/cucumbers/grow-your-own",
            "espacement_cm": 30,
            "profondeur_cm": (1, 2),
            "temp_min_c": 12,
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/cucumbers",
            "espacement_cm": (30, 45),
            "profondeur_cm": 2.5,
            "offset_semis_abri": -21,
            "offset_plantation": 14,
            "jours_semis_recolte": (50, 70),
            "besoin_eau": "eleve",
            "temp_min_c": 10,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/concombre.php",
            "espacement_cm": 60,
            "offset_plantation": (45, 75),
            "temp_min_c": 10,
            "besoin_eau": "eleve",
        },
    },
    "aubergine": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/aubergines/grow-your-own",
            "espacement_cm": 60,
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/eggplants",
            "espacement_cm": (60, 75),
            "profondeur_cm": 0.6,
            "offset_semis_abri": (-56, -42),
            "jours_semis_recolte": (100, 120),
            "jours_plant_recolte": (65, 80),
            "besoin_eau": "eleve",
            "temp_min_c": 13,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/aubergine.php",
            "offset_plantation": 28,  # « mai, après la dernière gelée »
            "temp_min_c": 12,
            "besoin_eau": "eleve",
        },
    },
    "poireau": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/leeks/grow-your-own",
            "espacement_cm": (15, 20),
            "profondeur_cm": 1.5,
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/leeks",
            "profondeur_cm": 0.6,
            "offset_semis_abri": (-70, -56),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/poireau.php",
            "espacement_cm": 15,
            "offset_plantation": 30,
            "besoin_eau": "moyen",
        },
    },
    "framboisier": {
        "rhs": {
            "url": "https://www.rhs.org.uk/fruit/raspberries/grow-your-own",
            "espacement_cm": (40, 60),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/raspberries",
            "espacement_cm": 45,
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/framboisier.php",
            "espacement_cm": 100,
            "besoin_eau": "moyen",
        },
    },
    "cassissier": {
        "rhs": {
            "url": "https://www.rhs.org.uk/fruit/blackcurrants/grow-your-own",
            "espacement_cm": (150, 180),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/currants",
            "espacement_cm": (90, 150),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/cassissier.php",
            "espacement_cm": 100,
            "besoin_eau": "moyen",
        },
    },
    "groseillier": {
        "rhs": {
            "url": "https://www.rhs.org.uk/fruit/redcurrants/grow-your-own",
            "espacement_cm": (120, 150),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/currants",
            "espacement_cm": (90, 150),
            "besoin_eau": "moyen",
        },
    },
    "myrtillier": {
        "rhs": {
            "url": "https://www.rhs.org.uk/fruit/blueberries/grow-your-own",
            "espacement_cm": (100, 200),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/blueberries",
            "espacement_cm": (120, 150),
            "besoin_eau": "eleve",
        },
    },
    "fraisier": {
        "rhs": {
            "url": "https://www.rhs.org.uk/fruit/strawberries/grow-your-own",
            "espacement_cm": (35, 40),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/strawberries",
            "espacement_cm": 45,
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/fraisier.php",
            "besoin_eau": "eleve",
        },
    },
    "menthe": {
        "rhs": {
            "url": "https://www.rhs.org.uk/herbs/mint/grow-your-own",
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/mint",
            "espacement_cm": 60,
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/menthe.php",
            "besoin_eau": "moyen",
        },
    },
    "romarin": {
        "rhs": {
            "url": "https://www.rhs.org.uk/herbs/rosemary/grow-your-own",
            "espacement_cm": 45,
            "besoin_eau": "faible",
            "temp_min_c": -8,
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/rosemary",
            "espacement_cm": (60, 90),
            "besoin_eau": "faible",
            "temp_min_c": (-10, -5),
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/romarin.php",
            "espacement_cm": 100,
            "besoin_eau": "faible",
        },
    },
    "thym": {
        "rhs": {
            "url": "https://www.rhs.org.uk/herbs/thyme/grow-your-own",
            "espacement_cm": (20, 30),
            "besoin_eau": "faible",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/thyme",
            "espacement_cm": (12, 24),
            "besoin_eau": "faible",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/thym.php",
            "espacement_cm": (20, 40),
            "besoin_eau": "faible",
        },
    },
    "sauge": {
        "rhs": {
            "url": "https://www.rhs.org.uk/herbs/sage/grow-your-own",
            "espacement_cm": 30,
            "besoin_eau": "faible",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/sage",
            "espacement_cm": 60,
            "besoin_eau": "moyen",
        },
    },
    "origan": {
        "rhs": {
            "url": "https://www.rhs.org.uk/herbs/oregano/grow-your-own",
            "espacement_cm": (20, 30),
            "besoin_eau": "faible",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/oregano",
            "espacement_cm": (20, 25),
            "besoin_eau": "faible",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/origan.php",
            "besoin_eau": "faible",
            "temp_min_c": -28,
        },
    },
    "chou-cabus": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/cabbages/grow-your-own",
            "espacement_cm": (30, 45),
            "profondeur_cm": 2,
            "jours_plant_recolte": (120, 180),  # « quatre à six mois »
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/cabbage",
            "espacement_cm": (18, 30),
            "profondeur_cm": 0.6,
            "offset_semis_abri": (-56, -42),
            "jours_plant_recolte": 70,
            "besoin_eau": "eleve",
            "temp_min_c": -8,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/chou-pomme.php",
            "espacement_cm": 50,
            "besoin_eau": "eleve",
        },
    },
    "chou-fleur": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/cauliflower/grow-your-own",
            "espacement_cm": (45, 70),
            "profondeur_cm": 1.5,
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/cauliflower",
            "espacement_cm": (46, 61),
            "profondeur_cm": 1.3,
            "offset_semis_abri": (-35, -28),
            "jours_plant_recolte": (50, 100),
            "besoin_eau": "eleve",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/chou-fleur.php",
            "espacement_cm": 70,
            "profondeur_cm": 2,
            "besoin_eau": "eleve",
        },
    },
    "brocoli": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/calabrese/grow-your-own",
            "espacement_cm": (30, 45),
            "profondeur_cm": 2,
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/broccoli",
            "espacement_cm": (30, 51),
            "offset_semis_abri": (-56, -42),
            "besoin_eau": "eleve",
        },
    },
    "epinard": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/spinach/grow-your-own",
            "espacement_cm": 15,
            "profondeur_cm": 2.5,
            "jours_semis_recolte": (30, 60),
            "besoin_eau": "eleve",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/spinach",
            "espacement_cm": (7, 10),
            "profondeur_cm": 1.25,
            "besoin_eau": "eleve",
            "temp_min_c": -9,
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/epinard.php",
            "espacement_cm": 15,
            "jours_semis_recolte": (45, 60),
            "besoin_eau": "eleve",
        },
    },
    "betterave": {
        "rhs": {
            "url": "https://www.rhs.org.uk/vegetables/beetroot/grow-your-own",
            "espacement_cm": (10, 15),
            "profondeur_cm": 2.5,
            "jours_semis_recolte": (40, 60),
            "besoin_eau": "moyen",
        },
        "almanac": {
            "url": "https://www.almanac.com/plant/beets",
            "espacement_cm": (7.5, 10),
            "profondeur_cm": 1.3,
            "jours_semis_recolte": (55, 70),
            "besoin_eau": "moyen",
        },
        "aujardin": {
            "url": "https://www.aujardin.info/plantes/betterave.php",
            "espacement_cm": 10,
            "profondeur_cm": 5,
            "jours_semis_recolte": 75,
            "besoin_eau": "moyen",
            "temp_min_c": -10,
        },
    },
    "pommier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (250, 1000)},
        "monjardin": {"url": "https://monjardinpaysager.fr/distance-plantation-arbres-fruitiers/",
                      "espacement_cm": (200, 1000)},
        "almanac": {"url": "https://www.almanac.com/plant/apples",
                    "espacement_cm": (120, 550), "besoin_eau": "moyen"},
        "rhs": {"url": "https://www.rhs.org.uk/fruit/apples/grow-your-own",
                "besoin_eau": "faible"},
    },
    "poirier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (200, 1000)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (100, 800)},
    },
    "cerisier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (500, 800)},
        "monjardin": {"url": "https://monjardinpaysager.fr/distance-plantation-arbres-fruitiers/",
                      "espacement_cm": (400, 1000)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (600, 1200)},
    },
    "prunier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (400, 500)},
        "monjardin": {"url": "https://monjardinpaysager.fr/distance-plantation-arbres-fruitiers/",
                      "espacement_cm": (300, 500)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (700, 1000)},
    },
    "pecher": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": 400},
        "monjardin": {"url": "https://monjardinpaysager.fr/distance-plantation-arbres-fruitiers/",
                      "espacement_cm": (300, 400)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (300, 500)},
    },
    "abricotier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": 500},
        "monjardin": {"url": "https://monjardinpaysager.fr/distance-plantation-arbres-fruitiers/",
                      "espacement_cm": (400, 600)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (500, 700)},
    },
    "amandier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (500, 700)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (400, 700)},
    },
    "cognassier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (400, 600)},
    },
    "figuier": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (600, 700)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (500, 800)},
        "rhs": {"url": "https://www.rhs.org.uk/fruit/figs/grow-your-own",
                "espacement_cm": 350, "besoin_eau": "moyen"},
        "aujardin": {"url": "https://www.aujardin.info/plantes/figuier.php",
                     "besoin_eau": "moyen", "temp_min_c": -15},
    },
    "kaki": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (500, 700)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (400, 600)},
    },
    "nashi": {
        "pepins": {"url": "https://pepinsetcie.fr/quelle-distance-de-plantation-pour-les-arbres-fruitiers/",
                   "espacement_cm": (200, 500)},
    },
    "noyer": {
        "senura": {"url": "https://senura.com/le-noyer/itineraire-technique",
                   "espacement_cm": (600, 1400)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (700, 1000)},
    },
    "chataignier": {
        "biogarten": {"url": "https://www.biogarten.ch/fr-ch/conseils/service/instructions-de-plantation-et-soins/fruits/instruction-soins-chataigniers-noisetiers",
                      "espacement_cm": (700, 800)},
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (700, 1000)},
    },
    "neflier": {
        "willemse": {"url": "https://conseils-jardin.willemsefrance.fr/quelles-distances-de-plantation-entre-les-arbres-fruitiers/",
                     "espacement_cm": (500, 600)},
    },
    "noisetier": {
        "biogarten": {"url": "https://www.biogarten.ch/fr-ch/conseils/service/instructions-de-plantation-et-soins/fruits/instruction-soins-chataigniers-noisetiers",
                      "espacement_cm": (150, 200)},
    },
    "basilic": {
        "rhs": {"url": "https://www.rhs.org.uk/herbs/basil/grow-your-own",
                "espacement_cm": (10, 20), "besoin_eau": "eleve",
                "temp_min_c": 10},
        "almanac": {"url": "https://www.almanac.com/plant/basil",
                    "espacement_cm": (25, 30), "profondeur_cm": 0.6,
                    "offset_semis_abri": (-56, -42), "besoin_eau": "moyen",
                    "temp_min_c": 10},
        "aujardin": {"url": "https://www.aujardin.info/plantes/basilic.php",
                     "espacement_cm": 25, "offset_plantation": (15, 45),
                     "besoin_eau": "eleve", "temp_min_c": 15},
    },
    "persil": {
        "rhs": {"url": "https://www.rhs.org.uk/herbs/parsley/grow-your-own",
                "espacement_cm": (15, 30), "profondeur_cm": 1,
                "besoin_eau": "moyen"},
        "almanac": {"url": "https://www.almanac.com/plant/parsley",
                    "espacement_cm": (6, 10), "profondeur_cm": 0.6,
                    "offset_semis_direct": (-28, -21),
                    "jours_semis_recolte": (70, 90), "besoin_eau": "moyen"},
        "aujardin": {"url": "https://www.aujardin.info/plantes/persil.php",
                     "espacement_cm": 20, "profondeur_cm": 1,
                     "besoin_eau": "moyen"},
    },
    "lavande": {
        "rhs": {"url": "https://www.rhs.org.uk/plants/lavender/growing-guide",
                "espacement_cm": (30, 90), "besoin_eau": "faible"},
        "aujardin": {"url": "https://www.aujardin.info/plantes/lavande.php",
                     "espacement_cm": (40, 50), "besoin_eau": "faible",
                     "temp_min_c": -15},
    },
    "ciboulette": {
        "rhs": {"url": "https://www.rhs.org.uk/herbs/chives/grow-your-own",
                "espacement_cm": 15, "profondeur_cm": (0.5, 1),
                "besoin_eau": "moyen"},
        "almanac": {"url": "https://www.almanac.com/plant/chives",
                    "espacement_cm": (10, 15), "profondeur_cm": 0.6,
                    "besoin_eau": "moyen"},
    },
    "cosmos": {
        "almanac": {
            "url": "https://www.almanac.com/plant/cosmos",
            "espacement_cm": (30, 45),
            "profondeur_cm": 0.6,
            "offset_semis_direct": 15,  # « once the danger of frost has passed »
            "besoin_eau": "faible",
        },
    },
    "tournesol": {
        "almanac": {
            "url": "https://www.almanac.com/plant/sunflowers",
            "espacement_cm": 15,
            "profondeur_cm": (2.5, 4),
            "offset_semis_direct": 15,  # « after the danger of frost has passed »
        },
    },
    # Memes especes que `framboisier` et `fraisier`, dont les sources traitent
    # explicitement les varietes remontantes : la RHS decrit les
    # « autumn-fruiting raspberries » dans la meme page, et Au Jardin les
    # fraisiers remontants dans la sienne. On reutilise donc les memes relevés
    # plutot que d'en inventer.
    # Page de genre : Au Jardin traite les trois cents especes d'Hypericum
    # ensemble, pas H. perforatum en particulier. On n'en retient donc que ce
    # qui vaut pour le genre — l'eau — et surtout pas une valeur chiffree.

    # Deux sources seulement : la page « groseillier » d'Au Jardin decrit un
    # groseillier a fleurs, dont elle dit le fruit « sans interet ». Ce n'est
    # pas la meme plante, et on ne la compte pas.
    # Deux sources : Au Jardin n'a pas de fiche myrtillier.
    # Deux sources : Au Jardin n'expose pas de fiche sous ce nom.
    # Deux sources : Au Jardin n'expose pas de fiche brocoli.
    # --- Fruitiers ------------------------------------------------------------
    #
    # Releves depuis trois tables de pepinieristes francais plutot que fiche
    # par fiche : elles couvrent tout le verger d'un coup, et surtout elles
    # distinguent le porte-greffe et la forme, ce qu'une fiche generique ne
    # fait pas. Les fourchettes sont donc larges a dessein — un pommier va de
    # 2 m en palisse a 10 m en plein vent, et le catalogue vise la demi-tige
    # de jardin.
    # Deux sources : la RHS classe la lavande en ornementale, pas en aromatique.
    # Deux sources : Au Jardin n'expose pas de fiche ciboulette.
}


# Tolerance avant de crier a l'ecart. Sans elle, une profondeur de semis de
# 0,5 cm « diverge » d'une source qui dit 0,6 : un millimetre, sur un geste
# qui se fait au doigt. On veut attraper l'erreur d'ordre de grandeur, pas la
# decimale — c'est la meme logique que les plages larges de l'audit.
TOLERANCE_RELATIVE = 0.25
TOLERANCE_ABSOLUE = {"profondeur_cm": 0.5, "temp_min_c": 2.0}
# Une tolerance relative sur une temperature ne veut rien dire : 25 % de 12 °C
# n'est pas une grandeur horticole. Ces champs n'ont qu'une marge absolue.
SANS_TOLERANCE_RELATIVE = {"temp_min_c"}


# Les ecarts assumes, par (identifiant, champ), avec leur raison. Meme logique
# que `DIVERGENCES_ASSUMEES` dans `revue_croisee.py` : sans cette table,
# l'outil signalerait a chaque passage des choix deliberes, et un audit qui
# echoue toujours est un audit que plus personne ne relance.
#
# Le gros du lot vient d'une seule decision : les cultures gelives sortent
# apres les saints de glace, soit vingt-huit jours apres une derniere gelee
# moyenne au 15 avril. Les sources anglo-saxonnes disent « apres la derniere
# gelee » sans marge, ce qui est vrai ailleurs et imprudent ici.
ECARTS_ASSUMES = {
    ("tomate", "offset_plantation"): "saints de glace — 13 mai, non +14 j",
    ("courgette", "offset_plantation"): "saints de glace",
    ("cosmos", "offset_semis_direct"): "saints de glace",
    ("tournesol", "offset_semis_direct"): "saints de glace",
    ("aubergine", "offset_semis_abri"): (
        "semis avance de 13 j avec la plantation, pour garder le delai en godet"
    ),
    # Pratiques francaises, ou la source anglo-saxonne decrit un autre usage.
    ("carotte", "offset_semis_direct"): (
        "semis des mars sous chassis en France ; RHS dit fevrier-juillet"
    ),
    ("petit-pois", "offset_semis_direct"): (
        "semis de fevrier en France (Au Jardin), plus tot qu'aux Etats-Unis"
    ),
    ("radis", "offset_semis_direct"): "la fiche seme plus tard que l'Almanac, pas plus tot",
    # Sur `temp_min_c`, se tromper vers le haut est sans danger et se tromper
    # vers le bas coute la plante : c'est ce champ qui declenche l'alerte gel,
    # donc une fiche plus frileuse que la source avertit plus tot. On ne
    # « corrige » pas une prudence dans le bon sens.
    # Le releve ne sait pas exprimer un plancher : « at least 15cm » devient
    # 15, donc un plafond. Les 20 cm de la fiche respectent la RHS ; seul
    # l'Almanac diverge vraiment, et c'est une source.
    # Sur `temp_min_c`, la fiche plus frileuse que la source avance l'alerte
    # gel : c'est le bon sens de l'erreur, on ne la corrige pas. Voir origan.
    # Quatre medicinales dont la fiche se declare moins rustique que la
    # source. Meme regle qu'ailleurs : sur ce champ, la fiche la plus
    # frileuse avance l'alerte gel au lieu de la retarder.
    ("achillee", "temp_min_c"): "Au Jardin dit -29 °C, la fiche -25 : alerte plus tôt",
    ("bardane", "temp_min_c"): "Au Jardin dit -34 °C, la fiche -20 : alerte plus tôt",
    ("guimauve", "temp_min_c"): "Au Jardin dit -24 °C, la fiche -20 : alerte plus tôt",
    ("passiflore", "temp_min_c"): "Au Jardin dit -20 °C, la fiche -15 : alerte plus tôt",
    # L'espacement de la bardane : la source donne 20 cm, mais dans le
    # paragraphe consacre a la production de racines, recoltees en 90 jours
    # avant qu'elles ne durcissent. La fiche decrit la plante entiere, qui
    # monte a deux metres. Les deux chiffres sont dans la meme page.
    ("bardane", "espacement_cm"): (
        "20 cm est la densité pour produire des racines (gobō) ; la fiche "
        "espace une plante de deux mètres"
    ),
    ("hoya", "temp_min_c"): (
        "la RHS la classe H2 (1-5 °C) ; la fiche s'arrête à 12, donc elle "
        "alerte plus tôt"
    ),
    ("pilea", "temp_min_c"): (
        "la RHS la classe H1c (5-10 °C) ; la fiche s'arrête à 13, donc elle "
        "alerte plus tôt"
    ),
    # L'eau : trois fiches arrosent plus souvent que la RHS ne le demande. La
    # RHS decrit un sujet sous verre, en atmosphere humide et sans chauffage
    # central ; un appartement francais chauffe seche plus vite. Arroser trop
    # souvent reste un defaut — mais le corriger a l'aveugle sur une source
    # qui ne decrit pas le meme milieu serait pire.
    ("fougere-nid", "besoin_eau"): "la RHS décrit un sujet sous verre, pas en appartement chauffé",
    ("maranta", "besoin_eau"): "la RHS décrit un sujet sous verre, pas en appartement chauffé",
    ("pilea", "besoin_eau"): "la RHS décrit un sujet sous verre, pas en appartement chauffé",
    # L'envergure RHS est celle d'un sujet mature sous verre ; la fiche donne
    # l'encombrement d'un pot d'appartement, qui est la facon dont ces plantes
    # se cultivent reellement. L'ecart est systematique et non une erreur.
    ("crassula", "espacement_cm"): "envergure RHS d'un sujet mature ; la fiche donne un pot",
    ("dieffenbachia", "espacement_cm"): "envergure RHS d'un sujet mature ; la fiche donne un pot",
    ("aspidistra", "temp_min_c"): (
        "la RHS la classe H3 (-5 à 1 °C) ; la fiche s'arrête à 5, donc elle "
        "alerte plus tôt"
    ),
    ("aspidistra", "besoin_eau"): (
        "surnommée « cast iron plant » pour sa résistance ; la fiche la dit "
        "sobre, ce que la RHS confirme en texte sans le dire dans son champ"
    ),
    ("pothos", "espacement_cm"): (
        "la RHS donne l'envergure d'un sujet grimpant mature ; la fiche donne "
        "l'encombrement d'une suspension, qui est la façon dont il se cultive"
    ),
    ("ciboulette", "espacement_cm"): (
        "la RHS dit « at least 15cm apart » — un plancher que 20 cm respecte, "
        "pas un plafond ; l'Almanac seul donne 10-15"
    ),
    ("figuier", "besoin_eau"): (
        "les deux sources parlent d'un figuier jeune ou aux racines contraintes — "
        "Au Jardin precise « attention a la secheresse pendant les premieres "
        "annees », et la RHS decrit un sujet palisse dont elle conseille "
        "elle-meme de restreindre les racines. Un figuier etabli en pleine "
        "terre est sobre, et la fiche le dit : trop d'eau dilue le gout."
    ),
    ("brocoli", "offset_semis_abri"): (
        "la fiche seme plus tard que l'Almanac, et suit la RHS : mars-avril "
        "a l'abri"
    ),
    ("brocoli", "profondeur_cm"): "1 cm contre 2 a la RHS, une seule source",
    ("epinard", "temp_min_c"): (
        "l'Almanac donne -9 °C, mais la fiche seme des fin janvier et compte "
        "donc sur un hivernage : les varietes d'hiver tiennent plus bas, et "
        "abaisser le seuil contredirait sa propre fenetre de semis"
    ),
    ("betterave", "temp_min_c"): (
        "Au Jardin la donne a -10 °C, la fiche s'arrete a -4 : prudence dans "
        "le bon sens, l'alerte gel part plus tot"
    ),
    ("origan", "temp_min_c"): (
        "Au Jardin le donne rustique a -28 °C ; la fiche s'arrete a -15, "
        "ce qui avance l'alerte gel au lieu de la retarder"
    ),
    ("menthe", "besoin_eau"): (
        "les trois sources disent d'elever la menthe en pot, pour la contenir ; "
        "un pot seche en deux jours l'ete, d'ou « eleve » et non « moyen »"
    ),
    ("menthe", "espacement_cm"): "une seule source, et la menthe se cultive en pot",
    ("tournesol", "espacement_cm"): (
        "l'Almanac decrit un semis dense de rang a 15 cm ; 50 cm est l'usage "
        "francais pour un tournesol de pied"
    ),
}


def _fourchette(valeur) -> tuple[float, float]:
    if isinstance(valeur, (list, tuple)):
        return float(valeur[0]), float(valeur[1])
    return float(valeur), float(valeur)


def _valeur_fiche(fiche: dict, champ: str):
    fenetres = fiche.get("fenetres") or {}
    cycle = fiche.get("cycle") or {}
    if champ == "espacement_cm":
        return fiche.get("espacement_cm")
    if champ == "profondeur_cm":
        return fiche.get("profondeur_semis_cm")
    if champ == "besoin_eau":
        return (fiche.get("arrosage") or {}).get("besoin")
    if champ == "temp_min_c":
        return (fiche.get("rusticite") or {}).get("temp_min_c")
    if champ == "jours_plant_recolte":
        return cycle.get("jours_plantation_a_recolte")
    if champ == "jours_semis_recolte":
        return cycle.get("jours_semis_a_recolte")
    correspondance = {
        "offset_plantation": "plantation",
        "offset_semis_direct": "semis_direct",
        "offset_semis_abri": "semis_interieur",
    }
    fenetre = fenetres.get(correspondance.get(champ, ""))
    return fenetre.get("offset_jours") if fenetre else None


def comparer(fiches: dict) -> list[dict]:
    """Confronte chaque relevé à sa fiche. Renvoie les écarts constatés."""
    ecarts = []
    for cid, par_source in sorted(RELEVES.items()):
        fiche = fiches.get(cid)
        if fiche is None:
            ecarts.append({"id": cid, "champ": "—", "probleme": "fiche absente"})
            continue

        champs = {c for releve in par_source.values() for c in releve if c != "url"}
        for champ in sorted(champs):
            valeurs = {
                src: releve[champ]
                for src, releve in par_source.items()
                if champ in releve
            }
            nôtre = _valeur_fiche(fiche, champ)
            if nôtre is None:
                continue

            if champ == "besoin_eau":
                accord = set(valeurs.values())
                if len(accord) == 1 and nôtre not in accord:
                    ecarts.append({
                        "id": cid, "champ": champ, "fiche": nôtre,
                        "sources": valeurs, "n": len(valeurs),
                    })
                continue

            # L'enveloppe de toutes les sources : une valeur de fiche qui en
            # sort est hors de ce que *personne* n'avance.
            bas = min(_fourchette(v)[0] for v in valeurs.values())
            haut = max(_fourchette(v)[1] for v in valeurs.values())
            # Une seule source qui diverge est une piste, pas un constat :
            # Almanac donne 15 cm entre tournesols (semis dense de rang), la
            # pratique francaise 50. Croire la premiere source venue
            # remplacerait une valeur discutable par une autre.
            if champ in SANS_TOLERANCE_RELATIVE:
                marge = TOLERANCE_ABSOLUE.get(champ, 0.0)
            else:
                marge = max(
                    abs(haut - bas) * TOLERANCE_RELATIVE,
                    abs(haut) * TOLERANCE_RELATIVE,
                    TOLERANCE_ABSOLUE.get(champ, 0.0),
                )
            if not (bas - marge) <= float(nôtre) <= (haut + marge):
                ecarts.append({
                    "id": cid, "champ": champ, "fiche": nôtre,
                    "enveloppe": (bas, haut), "sources": valeurs,
                    "n": len(valeurs),
                })
    return ecarts


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument(
        "--tout", action="store_true", help="liste aussi les fiches sans relevé"
    )
    args = parseur.parse_args()

    fiches = {
        c["id"]: c
        for c in json.loads(CATALOGUE.read_text(encoding="utf-8"))["cultures"]
    }
    ecarts = comparer(fiches)

    croisees = [c for c in RELEVES if len(RELEVES[c]) >= 3]
    print(f"{len(RELEVES)} fiches relevées sur {len(fiches)} "
          f"({len(croisees)} sur trois sources ou plus).")
    assumes = [e for e in ecarts if (e["id"], e["champ"]) in ECARTS_ASSUMES]
    ecarts = [e for e in ecarts if (e["id"], e["champ"]) not in ECARTS_ASSUMES]
    fermes = [e for e in ecarts if e.get("n", 0) >= 2]
    print(f"{len(assumes)} écart(s) assumé(s), avec leur raison.")
    print(f"{len(ecarts)} écart(s) restant(s), dont {len(fermes)} où au moins deux sources "
          f"convergent contre la fiche.")
    print("  ! = deux sources ou plus   ~ = une seule, piste à creuser\n")

    for e in ecarts:
        sources = ", ".join(f"{s}={v}" for s, v in e.get("sources", {}).items())
        enveloppe = e.get("enveloppe")
        etendue = (
            f" — hors de {enveloppe[0]:g}…{enveloppe[1]:g}, tolérance comprise"
            if enveloppe else ""
        )
        poids = "!" if e.get("n", 0) >= 2 else "~"
        print(f"{poids} {e['id']:20} {e['champ']:20} fiche={e['fiche']}{etendue}")
        print(f"  {'':20} {'':20} {sources}")

    for e in assumes:
        print(f"~ {e['id']:20} {e['champ']:20} "
              f"{ECARTS_ASSUMES[(e['id'], e['champ'])]}")

    # Un écart assumé que les sources ne rapportent plus masquerait une vraie
    # divergence sur cette fiche : on le dit.
    vus = {(e["id"], e["champ"]) for e in assumes}
    for cle in sorted(set(ECARTS_ASSUMES) - vus):
        if cle[0] in RELEVES:
            print(f"! {cle[0]} / {cle[1]} : écart assumé devenu sans objet, à retirer")

    if args.tout:
        manquantes = sorted(set(fiches) - set(RELEVES))
        print(f"\n{len(manquantes)} fiches sans relevé :")
        for debut in range(0, len(manquantes), 6):
            print("  " + "  ".join(f"{m:22}" for m in manquantes[debut : debut + 6]))

    # Seuls les ecarts ou au moins deux sources convergent contre la fiche
    # font echouer : en dessous, c'est une piste a creuser, pas un constat.
    fermes = [e for e in ecarts if e.get("n", 0) >= 2]
    return 1 if fermes else 0


if __name__ == "__main__":
    sys.exit(main())
