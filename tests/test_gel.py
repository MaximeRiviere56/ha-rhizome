"""Alerte gel : qui souffrira cette nuit, et qui n'a rien à craindre.

Le risque que ces tests couvrent est le même que pour l'arrosage : une alerte
de trop discrédite toutes les autres, et une alerte manquante coûte la plante.
Chaque garde-fou a donc son contre-exemple.
"""

from __future__ import annotations

import unittest

from _pure import gel
from _pure import lifecycle as lc

PLEINE_TERRE = {"id": "pleine-terre", "nom": "Pleine terre"}
SERRE = {"id": "serre", "nom": "Serre", "abritee": True}

TOMATE = {
    "id": "tomate", "nom": "Tomate", "emoji": "🍅", "categorie": "legume-fruit",
    "rusticite": {"gel": False, "temp_min_c": 5},
}
POIREAU = {
    "id": "poireau", "nom": "Poireau", "emoji": "🥬", "categorie": "legume-bulbe",
    "rusticite": {"gel": True, "temp_min_c": -20},
}
RUSTIQUE_SANS_BORNE = {
    "id": "oseille", "nom": "Oseille", "emoji": "🌿", "categorie": "legume-feuille",
    "rusticite": {"gel": True, "temp_min_c": None},
}
GELIVE_SANS_BORNE = {
    "id": "basilic", "nom": "Basilic", "emoji": "🌿", "categorie": "aromatique",
    "rusticite": {"gel": False, "temp_min_c": None},
}
ALOE = {
    "id": "aloe-vera", "nom": "Aloe vera", "emoji": "🌵",
    "categorie": "plante-interieur", "rusticite": {"gel": False, "temp_min_c": 10},
}


def plante(evenements=()):
    p = {"uid": "x", "culture_id": "x", "evenements": []}
    for type_evt, jour in evenements:
        lc.ajouter_evenement(p, lc.construire_evenement(type_evt, jour))
    return p


EN_TERRE = (("plante", "2026-05-02"),)


class TestSeuil(unittest.TestCase):
    def test_le_seuil_est_celui_de_la_fiche(self):
        self.assertEqual(gel.seuil_pour(TOMATE), 5)
        self.assertEqual(gel.seuil_pour(ALOE), 10)
        self.assertEqual(gel.seuil_pour(POIREAU), -20)

    def test_une_gelive_sans_borne_retombe_sur_zero(self):
        self.assertEqual(gel.seuil_pour(GELIVE_SANS_BORNE), gel.SEUIL_GELIVE_DEFAUT)

    def test_une_rustique_sans_borne_n_a_rien_a_dire(self):
        """None, et non zéro : elle ne doit déclencher aucune alerte."""
        self.assertIsNone(gel.seuil_pour(RUSTIQUE_SANS_BORNE))

    def test_un_minimum_illisible_ne_fait_pas_tomber_le_calcul(self):
        """Une fiche personnelle peut porter n'importe quoi.

        Le défaut récurrent du projet est une valeur non contrainte qui finit
        dans un calcul et fige tout : ici elle doit seulement se taire.
        """
        abimee = {**TOMATE, "rusticite": {"gel": False, "temp_min_c": "froid"}}
        self.assertIsNone(gel.seuil_pour(abimee))


class TestMenacee(unittest.TestCase):
    def test_une_gelive_dehors_sous_son_seuil(self):
        self.assertTrue(gel.menacee(TOMATE, plante(EN_TERRE), PLEINE_TERRE, 3))

    def test_au_seuil_exact_l_alerte_part(self):
        """Le seuil est la température à laquelle elle souffre déjà."""
        self.assertTrue(gel.menacee(TOMATE, plante(EN_TERRE), PLEINE_TERRE, 5))

    def test_au_dessus_du_seuil_rien(self):
        self.assertFalse(gel.menacee(TOMATE, plante(EN_TERRE), PLEINE_TERRE, 6))

    def test_une_rustique_ne_s_alarme_pas_d_une_gelee(self):
        """Un poireau à -15 °C n'a pas besoin qu'on le lui dise."""
        self.assertFalse(gel.menacee(POIREAU, plante(EN_TERRE), PLEINE_TERRE, -15))

    def test_mais_une_rustique_sous_son_propre_minimum_oui(self):
        self.assertTrue(gel.menacee(POIREAU, plante(EN_TERRE), PLEINE_TERRE, -22))

    def test_la_serre_protege(self):
        self.assertFalse(gel.menacee(TOMATE, plante(EN_TERRE), SERRE, -5))

    def test_une_plante_pas_encore_en_terre_ne_risque_rien(self):
        self.assertFalse(gel.menacee(TOMATE, plante(), PLEINE_TERRE, -5))

    def test_une_plante_terminee_non_plus(self):
        finie = plante((("plante", "2026-05-02"), ("termine", "2026-09-30")))
        self.assertFalse(gel.menacee(TOMATE, finie, PLEINE_TERRE, -5))

    def test_une_plante_d_interieur_sortie_pour_l_ete(self):
        """Le cas qui a motivé la fonctionnalité : « rentre l'aloe »."""
        self.assertTrue(gel.menacee(ALOE, plante(EN_TERRE), PLEINE_TERRE, 8))
        self.assertFalse(gel.menacee(ALOE, plante(EN_TERRE), PLEINE_TERRE, 12))


class TestListe(unittest.TestCase):
    def entrees(self):
        return [
            {"uid": "a", "nom_affiche": "Aloe", "culture": ALOE,
             "plante": plante(EN_TERRE), "zone": PLEINE_TERRE},
            {"uid": "t", "nom_affiche": "Tomate", "culture": TOMATE,
             "plante": plante(EN_TERRE), "zone": PLEINE_TERRE},
            {"uid": "p", "nom_affiche": "Poireau", "culture": POIREAU,
             "plante": plante(EN_TERRE), "zone": PLEINE_TERRE},
            {"uid": "s", "nom_affiche": "Tomate sous serre", "culture": TOMATE,
             "plante": plante(EN_TERRE), "zone": SERRE},
        ]

    def test_la_plus_fragile_en_tete(self):
        """La notification ne cite que les premières : ce doit être celles
        qu'il faut rentrer en premier."""
        menacees = gel.menacees(self.entrees(), 2)
        self.assertEqual([p["uid"] for p in menacees], ["a", "t"])

    def test_le_poireau_n_entre_que_sous_son_minimum(self):
        self.assertEqual([p["uid"] for p in gel.menacees(self.entrees(), -25)],
                         ["a", "t", "p"])

    def test_sans_prevision_aucune_alerte(self):
        """Une météo absente ou illisible ne doit pas inventer une alerte."""
        self.assertEqual(gel.menacees(self.entrees(), None), [])

    def test_une_nuit_douce_ne_dit_rien(self):
        self.assertEqual(gel.menacees(self.entrees(), 14), [])

    def test_le_geste_attendu_est_porte_par_la_fiche(self):
        """Une plante d'intérieur se rentre, une tomate se voile."""
        par_uid = {p["uid"]: p for p in gel.menacees(self.entrees(), 2)}
        self.assertTrue(par_uid["a"]["interieur"])
        self.assertFalse(par_uid["t"]["interieur"])


if __name__ == "__main__":
    unittest.main()
