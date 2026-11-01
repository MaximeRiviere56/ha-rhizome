"""Ce que le panneau recoit : un seul chemin, pour l'instance et pour le banc.

Ces tests n'existaient pas avant, et ne pouvaient pas exister : la
serialisation vivait dans `websocket.py`, qui importe Home Assistant, absent
de ce poste. Elle n'etait donc verifiee que par `tests/ha/`, sous pytest. En
la sortant dans un module pur, elle devient verifiable par le harnais le plus
rapide du projet — et le banc d'essai cesse de la reimplementer.
"""

from __future__ import annotations

from datetime import date
import unittest

from _pure import lifecycle as lc
from _pure import phenology as ph
from _pure import serialisation as ser
from _pure import watering as wa
from fixtures import TOMATE

GELEES = ph.Gelees(derniere="04-15", premiere="11-15")
AUJ = date(2026, 7, 15)
ZONE = {"id": "pleine-terre", "nom": "Pleine terre", "decalage_jours": 0}


def entree(**surcharges):
    """Une entree de la vue calculee, comme le coordinateur la construit."""
    plante = {
        "uid": "t1",
        "culture_id": "tomate",
        "evenements": [],
        "arrosages": [],
        "zone": "pleine-terre",
    }
    plante.update(surcharges.pop("plante", {}))
    etapes = ph.prochaines_etapes(TOMATE, plante, GELEES, 0, AUJ)
    base = {
        "uid": plante["uid"],
        "plante": plante,
        "culture": {**TOMATE, "emoji": "🍅", "categorie": "legume-fruit",
                    "exposition": "plein-soleil"},
        "zone": ZONE,
        "etapes": etapes,
        "prochaine": etapes[0] if etapes else None,
        "resume": lc.resume(plante),
        "nom_affiche": "Tomate",
        "arrosage": wa.etat(TOMATE, plante, ZONE, GELEES, AUJ),
    }
    base.update(surcharges)
    return base


class TestPlanteEnDict(unittest.TestCase):
    def test_les_cles_attendues_par_le_panneau(self):
        d = ser.plante_en_dict(entree())
        for cle in (
            "uid", "culture_id", "nom", "emoji", "categorie", "zone", "phase",
            "phase_libelle", "perenne", "prochaine", "etapes", "evenements",
            "arrosage", "arrosages", "arrosage_actif",
            "arrosage_frequence_jours", "echelonnement_jours", "exposition",
        ):
            self.assertIn(cle, d)

    def test_arrosage_porte_l_etat_et_non_les_besoins(self):
        """Le defaut de la v0.6.0, rejoue ici.

        `arrosage` etait defini deux fois dans ce dictionnaire : l'etat
        calcule, puis les besoins theoriques de la culture, qui l'ecrasaient.
        Le panneau n'a jamais affiche d'echeance d'arrosage sur une plante.
        """
        p = {"evenements": [], "arrosages": []}
        lc.ajouter_evenement(p, lc.construire_evenement(lc.EVT_PLANTE, "2026-05-02"))
        d = ser.plante_en_dict(entree(plante=p))
        self.assertIn("concernee", d["arrosage"])
        self.assertNotIn("besoin", d["arrosage"])

    def test_les_dates_sortent_en_chaines(self):
        """Le panneau lit du JSON : un objet `date` n'y survivrait pas."""
        p = {"evenements": [], "arrosages": []}
        lc.ajouter_evenement(p, lc.construire_evenement(lc.EVT_SEME, "2026-04-01"))
        d = ser.plante_en_dict(entree(plante=p))
        self.assertEqual(d["date_semis"], "2026-04-01")
        for etape in d["etapes"]:
            self.assertIsInstance(etape["debut"], str)
            self.assertIsInstance(etape["fin"], str)

    def test_les_arrosages_sortent_du_plus_recent_au_plus_ancien(self):
        p = {"evenements": [], "arrosages": []}
        lc.ajouter_evenement(p, lc.construire_evenement(lc.EVT_PLANTE, "2026-05-02"))
        for jour in ("2026-07-01", "2026-07-08"):
            wa.noter_arrosage(p, wa.construire_arrosage(jour))
        d = ser.plante_en_dict(entree(plante=p))
        self.assertEqual([a["date"] for a in d["arrosages"]],
                         ["2026-07-08", "2026-07-01"])

    def test_une_plante_sans_etape_ne_casse_pas(self):
        """Le cas des plantes d'interieur : aucune fenetre, aucune etape."""
        interieur = {
            **TOMATE, "id": "monstera", "nom": "Monstera", "emoji": "🪴",
            "categorie": "plante-interieur", "exposition": "mi-ombre",
            "fenetres": {}, "perenne": True,
        }
        d = ser.plante_en_dict(entree(culture=interieur, etapes=[], prochaine=None))
        self.assertIsNone(d["prochaine"])
        self.assertEqual(d["etapes"], [])
        self.assertTrue(d["perenne"])

    def test_la_langue_traverse_jusqu_aux_libelles(self):
        p = {"evenements": [], "arrosages": []}
        lc.ajouter_evenement(p, lc.construire_evenement(lc.EVT_SEME, "2026-04-01"))
        fr = ser.plante_en_dict(entree(plante=p), "fr")
        en = ser.plante_en_dict(entree(plante=p), "en")
        self.assertEqual(fr["phase_libelle"], "Semé")
        self.assertEqual(en["phase_libelle"], "Sown")
        self.assertEqual(en["evenements"][0]["libelle"], "Sown")


class TestEtapeEnDict(unittest.TestCase):
    def test_none_reste_none(self):
        self.assertIsNone(ser.etape_en_dict(None))

    def test_le_libelle_suit_la_langue(self):
        etapes = ph.fenetres_theoriques(TOMATE, GELEES, 0, 2026)
        d = ser.etape_en_dict(etapes[0], "en")
        self.assertEqual(d["libelle"], "Sow under cover")


class TestArrosageEnDict(unittest.TestCase):
    def test_none_reste_none(self):
        self.assertIsNone(ser.arrosage_en_dict(None))

    def test_le_motif_d_exclusion_est_traduit(self):
        """Les modules purs rendent leur message en francais et portent une
        cle ; c'est ici que la cle devient la langue de l'utilisateur."""
        etat = wa.etat(TOMATE, {"evenements": [], "arrosages": []}, ZONE, GELEES, AUJ)
        self.assertFalse(etat.concernee)
        fr = ser.arrosage_en_dict(etat, "fr")["motif_exclusion"]
        en = ser.arrosage_en_dict(etat, "en")["motif_exclusion"]
        self.assertNotEqual(fr, en)
        self.assertTrue(en)


if __name__ == "__main__":
    unittest.main()
