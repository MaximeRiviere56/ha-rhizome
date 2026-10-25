"""Rotation des cultures et semis échelonnés."""

from __future__ import annotations

from datetime import date
import unittest

from _pure import lifecycle as lc
from _pure import phenology as ph
from _pure import rotation as rot
from fixtures import RADIS

GELEES = ph.Gelees(derniere="04-15", premiere="11-15")

CULTURES = {
    "tomate": {"id": "tomate", "nom": "Tomate", "famille": "Solanacées"},
    "aubergine": {"id": "aubergine", "nom": "Aubergine", "famille": "Solanacées"},
    "carotte": {"id": "carotte", "nom": "Carotte", "famille": "Apiacées"},
    "pommier": {
        "id": "pommier", "nom": "Pommier", "famille": "Rosacées", "perenne": True,
    },
    "fraisier": {"id": "fraisier", "nom": "Fraisier", "famille": "Rosacées"},
}


def plante(culture_id, zone="pleine-terre", annees=()):
    return {
        "uid": culture_id[:4],
        "culture_id": culture_id,
        "zone": zone,
        "evenements": [{"type": "plante", "date": f"{a}-05-01"} for a in annees],
    }


class TestRotation(unittest.TestCase):
    def test_meme_famille_recente_declenche_un_avertissement(self):
        avis = rot.verifier(
            CULTURES["tomate"], "pleine-terre",
            [plante("aubergine", annees=(2025,))], CULTURES, date(2026, 10, 22),
        )
        self.assertIsNotNone(avis)
        self.assertEqual(avis["famille"], "Solanacées")
        self.assertEqual(avis["delai_ans"], 4)
        self.assertIn("Aubergine", avis["message"])

    def test_famille_assez_ancienne_ne_declenche_rien(self):
        """Quatre ans pour les solanacées : 2021 est hors délai en 2026."""
        self.assertIsNone(
            rot.verifier(
                CULTURES["tomate"], "pleine-terre",
                [plante("aubergine", annees=(2021,))], CULTURES, date(2026, 10, 22),
            )
        )

    def test_autre_zone_ne_compte_pas(self):
        self.assertIsNone(
            rot.verifier(
                CULTURES["tomate"], "pleine-terre",
                [plante("aubergine", zone="serre", annees=(2026,))],
                CULTURES, date(2026, 10, 22),
            )
        )

    def test_autre_famille_ne_compte_pas(self):
        self.assertIsNone(
            rot.verifier(
                CULTURES["tomate"], "pleine-terre",
                [plante("carotte", annees=(2026,))], CULTURES, date(2026, 10, 22),
            )
        )

    def test_une_perenne_n_entre_pas_dans_la_rotation(self):
        """Un pommier occupe sa place vingt ans : il ne se tourne pas."""
        self.assertIsNone(
            rot.verifier(
                CULTURES["fraisier"], "pleine-terre",
                [plante("pommier", annees=(2026,))], CULTURES, date(2026, 10, 22),
            )
        )

    def test_delai_plus_court_pour_les_fabacees(self):
        self.assertEqual(rot.delai_pour("Fabacées"), 2)
        self.assertEqual(rot.delai_pour("Solanacées"), 4)
        self.assertEqual(rot.delai_pour("Famille inconnue"), 3)

    def test_plante_sans_journal_compte_sur_l_annee_en_cours(self):
        """Une plante seulement prévue occupe déjà la place dans les faits."""
        avis = rot.verifier(
            CULTURES["tomate"], "pleine-terre",
            [plante("aubergine")], CULTURES, date(2026, 10, 22),
        )
        self.assertIsNotNone(avis)
        self.assertEqual(avis["precedents"][0]["annee"], 2026)


class TestEchelonnement(unittest.TestCase):
    def _radis_seme(self, jour, intervalle):
        p = {
            "uid": "r1", "culture_id": "radis", "evenements": [],
            "echelonnement_jours": intervalle,
        }
        lc.ajouter_evenement(
            p, lc.construire_evenement(lc.EVT_SEME, jour, mode=lc.MODE_SEMIS_DIRECT)
        )
        return p

    def test_un_ressemis_est_propose_a_l_intervalle_demande(self):
        p = self._radis_seme("2026-05-01", 15)
        etapes = ph.prochaines_etapes(RADIS, p, GELEES, 0, date(2026, 5, 2))
        ressemis = [e for e in etapes if e.type == ph.ETAPE_RESSEMER]
        self.assertEqual(len(ressemis), 1)
        self.assertEqual(ressemis[0].debut, date(2026, 5, 16))

    def test_sans_echelonnement_aucun_ressemis(self):
        p = self._radis_seme("2026-05-01", None)
        etapes = ph.prochaines_etapes(RADIS, p, GELEES, 0, date(2026, 5, 2))
        self.assertEqual([e for e in etapes if e.type == ph.ETAPE_RESSEMER], [])

    def test_pas_de_ressemis_hors_de_la_fenetre_de_semis(self):
        """La fenêtre du radis se ferme mi-août : rien à ressemer en décembre."""
        p = self._radis_seme("2026-08-10", 15)
        etapes = ph.prochaines_etapes(RADIS, p, GELEES, 0, date(2026, 8, 11))
        self.assertEqual([e for e in etapes if e.type == ph.ETAPE_RESSEMER], [])

    def test_le_ressemis_est_marque_comme_reel(self):
        """Il découle d'une date du journal, pas d'une moyenne saisonnière."""
        p = self._radis_seme("2026-05-01", 15)
        etapes = ph.prochaines_etapes(RADIS, p, GELEES, 0, date(2026, 5, 2))
        ressemis = next(e for e in etapes if e.type == ph.ETAPE_RESSEMER)
        self.assertTrue(ressemis.reelle)
        self.assertEqual(ressemis.libelle, "Ressemer")


class TestRecolteDeSaison(unittest.TestCase):
    def test_seules_les_recoltes_de_l_annee_comptent(self):
        evenements = [
            {"type": "recolte", "date": "2025-07-14", "quantite_g": 900},
            {"type": "recolte", "date": "2026-07-14", "quantite_g": 320},
            {"type": "recolte", "date": "2026-08-02", "quantite_g": 450},
        ]
        self.assertEqual(lc.total_recolte_saison_g(evenements, 2026), 770)
        self.assertEqual(lc.total_recolte_saison_g(evenements, 2025), 900)
        self.assertEqual(lc.total_recolte_g(evenements), 1670)

    def test_une_saison_vide_vaut_zero(self):
        self.assertEqual(lc.total_recolte_saison_g([], 2026), 0)


if __name__ == "__main__":
    unittest.main()
