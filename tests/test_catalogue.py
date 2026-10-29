"""Integrite du catalogue, et son passage dans le moteur.

Le test croise est le plus utile du lot : il fait passer les 108 fiches dans
`prochaines_etapes` a plusieurs dates de l'annee. Une fiche mal remplie ne
casse pas a l'ecriture, elle casse six mois plus tard chez l'utilisateur.
"""

from __future__ import annotations

from datetime import date
import json
import pathlib
import sys
import unittest

from _pure import lifecycle as lc
from _pure import phenology as ph

RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "tools"))

from build_catalog import valider  # noqa: E402
from catalogue_source import CULTURES  # noqa: E402

CATALOG_JSON = RACINE / "custom_components" / "rhizome" / "data" / "catalog.json"
GELEES = ph.Gelees(derniere="04-15", premiere="11-15")

# Quelques dates reparties sur l'annee, dont les deux pieges : le creux de
# l'hiver et la fin decembre, ou il faut deja voir la saison suivante.
DATES_SONDE = [
    date(2026, 1, 15),
    date(2026, 3, 1),
    date(2026, 5, 20),
    date(2026, 8, 10),
    date(2026, 10, 5),
    date(2026, 12, 28),
]


class TestIntegrite(unittest.TestCase):
    def test_catalogue_sans_probleme(self):
        problemes = valider(CULTURES)
        self.assertEqual(problemes, [], "\n".join(problemes))

    def test_json_a_jour(self):
        """Le JSON livre doit correspondre a la table source."""
        self.assertTrue(CATALOG_JSON.exists(), "lancer tools/build_catalog.py")
        charge = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        self.assertEqual(len(charge["cultures"]), len(CULTURES))
        self.assertEqual(
            {c["id"] for c in charge["cultures"]}, {c["id"] for c in CULTURES}
        )

    def test_taille_annoncee(self):
        self.assertGreaterEqual(len(CULTURES), 100)

    def test_associations_symetriques_quand_elles_existent(self):
        """Si A evite B, B ne doit pas aimer A : ce serait un conseil contradictoire."""
        par_id = {c["id"]: c for c in CULTURES}
        for c in CULTURES:
            for evite in c["associations"]["evite"]:
                autre = par_id[evite]
                self.assertNotIn(
                    c["id"],
                    autre["associations"]["aime"],
                    f"{c['id']} evite {evite}, mais {evite} aime {c['id']}",
                )


# Les plantes d'interieur sont hors de ce test par construction : elles ne
# portent aucune fenetre, puisque toutes les fenetres du catalogue sont des
# decalages par rapport aux gelees. Elles ont leur propre test, plus bas, qui
# verifie justement qu'elles ne proposent rien.
CATEGORIE_INTERIEUR = "plante-interieur"
PLEIN_AIR = [c for c in CULTURES if c["categorie"] != CATEGORIE_INTERIEUR]
INTERIEUR = [c for c in CULTURES if c["categorie"] == CATEGORIE_INTERIEUR]


class TestCatalogueDansLeMoteur(unittest.TestCase):
    def test_toute_culture_produit_des_etapes_toute_l_annee(self):
        for culture in PLEIN_AIR:
            plante = {"uid": "x", "culture_id": culture["id"], "evenements": []}
            for jour in DATES_SONDE:
                with self.subTest(culture=culture["id"], jour=jour):
                    etapes = ph.prochaines_etapes(culture, plante, GELEES, 0, jour)
                    self.assertTrue(
                        etapes,
                        f"{culture['id']} n'a aucune etape a venir au {jour}",
                    )

    def test_toute_culture_sait_mener_un_cycle_complet(self):
        """Semer, puis mettre en place, doit rester calculable partout."""
        for culture in PLEIN_AIR:
            if culture.get("perenne"):
                continue
            fenetres = culture["fenetres"]
            interieur = "semis_interieur" in fenetres
            plante = {"uid": "x", "culture_id": culture["id"], "evenements": []}
            with self.subTest(culture=culture["id"]):
                if interieur or "semis_direct" in fenetres:
                    lc.ajouter_evenement(
                        plante,
                        lc.construire_evenement(
                            lc.EVT_SEME,
                            "2026-04-01",
                            mode=lc.MODE_SEMIS_INTERIEUR if interieur else lc.MODE_SEMIS_DIRECT,
                        ),
                    )
                else:
                    lc.ajouter_evenement(
                        plante, lc.construire_evenement(lc.EVT_PLANTE, "2026-04-01")
                    )
                etapes = ph.prochaines_etapes(
                    culture, plante, GELEES, 0, date(2026, 4, 2)
                )
                self.assertTrue(etapes, f"{culture['id']} : chaine interrompue")
                self.assertTrue(
                    any(e.type == ph.ETAPE_RECOLTE for e in etapes),
                    f"{culture['id']} : aucune recolte calculee apres mise en place",
                )

    def test_les_perennes_ne_demandent_jamais_de_semis(self):
        for culture in PLEIN_AIR:
            if not culture.get("perenne"):
                continue
            plante = {"uid": "x", "culture_id": culture["id"], "evenements": []}
            lc.ajouter_evenement(
                plante, lc.construire_evenement(lc.EVT_PLANTE, "2025-11-20")
            )
            etapes = ph.prochaines_etapes(culture, plante, GELEES, 0, date(2026, 3, 1))
            with self.subTest(culture=culture["id"]):
                self.assertEqual({e.type for e in etapes}, {ph.ETAPE_RECOLTE})


if __name__ == "__main__":
    unittest.main()


class TestCataloguePersonnel(unittest.TestCase):
    """Les fiches saisies à la main : conversion, validation, fusion."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        import types

        src = RACINE / "custom_components" / "rhizome"
        if "rhizome_cat" not in sys.modules:
            pkg = types.ModuleType("rhizome_cat")
            pkg.__path__ = [str(src)]
            sys.modules["rhizome_cat"] = pkg
            spec = importlib.util.spec_from_file_location(
                "rhizome_cat.catalog", src / "catalog.py"
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules["rhizome_cat.catalog"] = module
            spec.loader.exec_module(module)
        cls.cat = sys.modules["rhizome_cat.catalog"]

    def test_slug_sans_accent_ni_espace(self):
        self.assertEqual(self.cat.slug("Chou-rave de Vienne"), "chou-rave-de-vienne")
        self.assertEqual(self.cat.slug("Œillet d'Inde"), "oeillet-d-inde")
        self.assertEqual(self.cat.slug("   "), "culture")

    def test_une_periode_en_mois_devient_une_fenetre(self):
        f = self.cat.fenetre_par_mois(3, 7)
        self.assertEqual(f["ancrage"], "date_fixe")
        self.assertEqual(f["date"], "03-01")
        self.assertEqual(f["duree_jours"], 150)

    def test_une_periode_qui_franchit_l_annee(self):
        """D'octobre à février : cinq mois, pas moins huit."""
        self.assertEqual(self.cat.fenetre_par_mois(10, 2)["duree_jours"], 150)

    def test_un_mois_unique_couvre_le_mois(self):
        self.assertEqual(self.cat.fenetre_par_mois(5, 5)["duree_jours"], 30)

    def test_fiche_sans_recolte_calculable_refusee(self):
        """Sans durée de cycle ni période de récolte, le moteur ne saurait
        rien annoncer : mieux vaut refuser à la saisie."""
        fiche = {
            "nom": "Test", "categorie": "legume-feuille", "exposition": "plein-soleil",
            "arrosage": {"besoin": "moyen"}, "rusticite": {"gel": True},
            "fenetres": {"semis_direct": {"ancrage": "date_fixe", "date": "03-01"}},
            "cycle": {},
        }
        soucis = self.cat.valider_fiche(fiche)
        # `valider_fiche` rend des cles de traduction, pas des phrases : la
        # couche Home Assistant les rend dans la langue de l'interface.
        self.assertIn("fiche_recolte_incalculable", soucis)

    def test_fiche_complete_acceptee(self):
        fiche = {
            "nom": "Chou-rave", "categorie": "legume-feuille",
            "exposition": "plein-soleil", "arrosage": {"besoin": "moyen"},
            "rusticite": {"gel": True},
            "fenetres": {"semis_direct": {"ancrage": "date_fixe", "date": "03-01"}},
            "cycle": {"jours_semis_a_recolte": 70},
        }
        self.assertEqual(self.cat.valider_fiche(fiche), [])

    def test_fusion_sans_ecraser_les_fiches_livrees(self):
        perso = {
            "id": "perso-chou-rave", "nom": "Chou-rave", "categorie": "legume-feuille",
            "emoji": "🥬", "difficulte": 1, "exposition": "plein-soleil",
            "famille": "Brassicacées", "nom_scientifique": "",
            "arrosage": {"besoin": "moyen", "frequence_jours": 3, "notes": ""},
            "perso": True,
        }
        fusionne = self.cat.Catalogue([perso])
        self.assertEqual(len(fusionne.toutes()), len(CULTURES) + 1)
        self.assertEqual([f["nom"] for f in fusionne.perso()], ["Chou-rave"])
        self.assertEqual(fusionne.culture("tomate")["nom"], "Tomate")

    def test_une_fiche_perso_ne_peut_pas_masquer_une_fiche_livree(self):
        """Le préfixe garantit qu'aucune saisie ne remplace « tomate »."""
        self.assertTrue(
            all(not c["id"].startswith("perso-") for c in CULTURES),
            "le catalogue livré ne doit pas utiliser le préfixe perso-",
        )


class TestPlantesInterieur(unittest.TestCase):
    """Ce que le catalogue promet des plantes d'interieur, et rien de plus.

    Le risque qu'on couvre ici n'est pas qu'elles cassent : c'est qu'une
    evolution leur redonne un calendrier par inadvertance, et que le panneau
    annonce la recolte d'un monstera.
    """

    def test_il_y_en_a(self):
        self.assertGreaterEqual(len(INTERIEUR), 20)

    def test_aucune_fenetre_ni_etape(self):
        for culture in INTERIEUR:
            with self.subTest(culture=culture["id"]):
                self.assertEqual(culture["fenetres"], {})
                plante = {"uid": "x", "culture_id": culture["id"], "evenements": []}
                for jour in DATES_SONDE:
                    self.assertEqual(
                        ph.prochaines_etapes(culture, plante, GELEES, 0, jour), []
                    )

    def test_toutes_perennes_et_gelives(self):
        """Une plante d'interieur declaree rustique promettrait un hivernage dehors."""
        for culture in INTERIEUR:
            with self.subTest(culture=culture["id"]):
                self.assertTrue(culture["perenne"])
                self.assertIs(culture["rusticite"]["gel"], False)
                self.assertIsNotNone(culture["rusticite"]["temp_min_c"])

    def test_chacune_dit_sa_toxicite(self):
        """La question que pose un foyer avec un animal ou un enfant.

        On ne verifie pas la justesse de la reponse — aucun test ne peut le
        faire — mais qu'elle soit posee : une fiche muette sur ce point est le
        seul endroit du catalogue ou le silence peut nuire.
        """
        marqueurs = ("toxi", "irritant", "latex", "saponine", "oxalate", "purgatif")
        for culture in INTERIEUR:
            with self.subTest(culture=culture["id"]):
                conseils = " ".join(culture["conseils"]).lower()
                self.assertTrue(
                    any(m in conseils for m in marqueurs),
                    f"{culture['id']} ne dit rien de sa toxicite",
                )
