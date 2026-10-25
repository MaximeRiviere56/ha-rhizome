"""Arrosage : qui est concerné, quand, et ce qui compte comme un arrosage."""

from __future__ import annotations

from datetime import date
from typing import ClassVar
import unittest

from _pure import lifecycle as lc
from _pure import phenology as ph
from _pure import watering as wa
from fixtures import TOMATE

GELEES = ph.Gelees(derniere="04-15", premiere="11-15")

PLEINE_TERRE = {"id": "pleine-terre", "nom": "Pleine terre"}
SERRE = {"id": "serre", "nom": "Serre", "abritee": True}
BALCON = {"id": "balcon", "nom": "Balcon", "abritee": True}

ETE = date(2026, 7, 15)
HIVER = date(2026, 12, 20)


def plante(evenements=(), **kw):
    p = {"uid": "t1", "culture_id": "tomate", "evenements": [], "arrosages": []}
    p.update(kw)
    for type_evt, jour in evenements:
        lc.ajouter_evenement(p, lc.construire_evenement(type_evt, jour))
    return p


def arroser(p, jour, note=None):
    wa.noter_arrosage(p, wa.construire_arrosage(jour, note))
    return p


class TestQuiEstConcerne(unittest.TestCase):
    def test_une_plante_pas_encore_en_terre_ne_s_arrose_pas(self):
        e = wa.etat(TOMATE, plante(), PLEINE_TERRE, GELEES, ETE)
        self.assertFalse(e.concernee)
        self.assertIn("en terre", e.motif_exclusion)

    def test_une_plante_terminee_ne_s_arrose_plus(self):
        p = plante([("plante", "2026-05-02"), ("termine", "2026-09-30")])
        self.assertFalse(wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE).concernee)

    def test_une_plante_perdue_ne_s_arrose_plus(self):
        p = plante([("plante", "2026-05-02"), ("perdu", "2026-06-01")])
        self.assertFalse(wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE).concernee)

    def test_rappels_desactivables_plante_par_plante(self):
        p = plante([("plante", "2026-05-02")], arrosage_actif=False)
        e = wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE)
        self.assertFalse(e.concernee)
        self.assertIn("désactivés", e.motif_exclusion)

    def test_pas_de_rappel_en_pleine_terre_l_hiver(self):
        """De la première à la dernière gelée, personne n'arrose son jardin."""
        p = plante([("plante", "2026-05-02")])
        e = wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, HIVER)
        self.assertFalse(e.concernee)
        self.assertIn("nature s'en charge", e.motif_exclusion)

    def test_mais_les_zones_abritees_boivent_toute_l_annee(self):
        """Serre, châssis et pots sèchent, hiver compris."""
        p = plante([("plante", "2026-05-02")])
        self.assertTrue(wa.etat(TOMATE, p, BALCON, GELEES, HIVER).concernee)
        self.assertTrue(wa.etat(TOMATE, p, SERRE, GELEES, HIVER).concernee)


class TestQuand(unittest.TestCase):
    def test_prochain_arrosage_a_la_frequence_de_la_fiche(self):
        """La tomate boit tous les 2 jours."""
        p = arroser(plante([("plante", "2026-05-02")]), "2026-07-14")
        e = wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE)
        self.assertEqual(e.frequence_jours, 2)
        self.assertEqual(e.prochain, date(2026, 7, 16))
        self.assertEqual(e.jours_restants, 1)
        self.assertFalse(e.a_arroser)

    def test_le_compte_repart_du_dernier_arrosage_declare(self):
        """Rien n'observe le sol : c'est la déclaration qui fait foi."""
        p = plante([("plante", "2026-05-02")])
        arroser(p, "2026-07-01")
        self.assertTrue(wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE).en_retard)
        arroser(p, "2026-07-15")
        e = wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE)
        self.assertFalse(e.en_retard)
        self.assertEqual(e.prochain, date(2026, 7, 17))

    def test_en_retard_quand_la_date_est_passee(self):
        p = arroser(plante([("plante", "2026-05-02")]), "2026-07-10")
        e = wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE)
        self.assertTrue(e.en_retard)
        self.assertTrue(e.a_arroser)
        self.assertEqual(e.jours_restants, -3)

    def test_un_semis_boit_deux_fois_plus_souvent(self):
        """La graine est en surface et ne pardonne pas un dessèchement."""
        semee = arroser(plante([("seme", "2026-07-10")]), "2026-07-14")
        plantee = arroser(plante([("plante", "2026-05-02")]), "2026-07-14")
        self.assertEqual(wa.etat(TOMATE, semee, SERRE, GELEES, ETE).frequence_jours, 1)
        self.assertEqual(
            wa.etat(TOMATE, plantee, PLEINE_TERRE, GELEES, ETE).frequence_jours, 2
        )

    def test_jamais_arrosee_c_est_du_maintenant(self):
        """Compter depuis la plantation afficherait « depuis 692 jours » pour
        un arbre planté il y a deux ans : un retard qui ne veut rien dire."""
        p = plante([("plante", "2024-11-20")])
        e = wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE)
        self.assertIsNone(e.dernier)
        self.assertEqual(e.prochain, ETE)
        self.assertEqual(e.jours_restants, 0)
        self.assertTrue(e.a_arroser)
        self.assertFalse(e.en_retard)

    def test_la_frequence_de_la_plante_prime_sur_la_fiche(self):
        p = arroser(
            plante([("plante", "2026-05-02")], arrosage_frequence_jours=5), "2026-07-14"
        )
        e = wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE)
        self.assertEqual(e.frequence_jours, 5)
        self.assertEqual(e.prochain, date(2026, 7, 19))


class TestPerennesInstallees(unittest.TestCase):
    """Les fiches disent « aucun arrosage une fois établi » : le moteur
    doit les écouter."""

    SOBRE: ClassVar[dict] = {
        "perenne": True,
        "arrosage": {"besoin": "faible", "frequence_jours": 10},
    }
    GOURMANDE: ClassVar[dict] = {
        "perenne": True,
        "arrosage": {"besoin": "eleve", "frequence_jours": 3},
    }

    def test_une_perenne_sobre_installee_ne_reclame_rien(self):
        # Plantée en 2023 : plus de deux ans en terre à l'été 2026.
        p = plante([("plante", "2023-11-20")])
        e = wa.etat(self.SOBRE, p, PLEINE_TERRE, GELEES, ETE)
        self.assertFalse(e.concernee)
        self.assertIn("se débrouille seule", e.motif_exclusion)

    def test_mais_les_deux_premieres_annees_elle_compte(self):
        """Un arbre tout juste planté a besoin d'eau pour s'installer."""
        p = plante([("plante", "2025-04-20")])
        self.assertTrue(wa.etat(self.SOBRE, p, PLEINE_TERRE, GELEES, ETE).concernee)

    def test_une_perenne_gourmande_reste_concernee(self):
        """Un myrtillier installé a toujours soif."""
        p = plante([("plante", "2023-11-20")])
        self.assertTrue(
            wa.etat(self.GOURMANDE, p, PLEINE_TERRE, GELEES, ETE).concernee
        )

    def test_une_annuelle_n_est_jamais_concernee_par_cette_regle(self):
        p = plante([("plante", "2023-11-20")])
        self.assertTrue(wa.etat(TOMATE, p, PLEINE_TERRE, GELEES, ETE).concernee)


class TestHistorique(unittest.TestCase):
    def test_l_historique_reste_trie(self):
        p = plante()
        arroser(p, "2026-07-14")
        arroser(p, "2026-07-10")
        self.assertEqual([a["date"] for a in p["arrosages"]], ["2026-07-10", "2026-07-14"])

    def test_l_historique_est_borne(self):
        """Soixante entrées suffisent ; les garder toutes gonflerait le
        stockage saison après saison."""
        from datetime import timedelta

        p = plante()
        debut = date(2026, 1, 1)
        for n in range(70):
            wa.noter_arrosage(p, wa.construire_arrosage(debut + timedelta(days=n)))
        self.assertEqual(len(p["arrosages"]), 60)
        # Les dix plus anciennes ont été écartées.
        self.assertEqual(p["arrosages"][0]["date"], "2026-01-11")
        self.assertEqual(p["arrosages"][-1]["date"], "2026-03-11")

    def test_une_note_est_conservee(self):
        p = plante()
        arroser(p, "2026-07-14", "au goulot, il faisait 32°")
        self.assertEqual(p["arrosages"][0]["note"], "au goulot, il faisait 32°")


if __name__ == "__main__":
    unittest.main()
