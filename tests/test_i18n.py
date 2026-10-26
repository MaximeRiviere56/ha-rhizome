"""La table des textes et la resolution de la langue.

Module pur, donc testable avec le Python du systeme. Ce que ces tests
protegent n'est pas l'orthographe des traductions — rien ne peut la verifier —
mais trois promesses mecaniques :

- une cle presente en francais existe aussi en anglais, sinon l'interface se
  panache ;
- les variables d'un modele sont les memes dans les deux langues, sinon un
  rappel anglais part avec un « {zone} » en clair ;
- « auto » retombe toujours sur une langue connue, quelle que soit l'etiquette
  que Home Assistant presente.
"""

from __future__ import annotations

from datetime import date
import json
import pathlib
import re
import unittest

from _pure import i18n

VARIABLES = re.compile(r"\{(\w+)\}")


class TableDesTextes(unittest.TestCase):
    def test_les_deux_langues_portent_les_memes_cles(self):
        """Une cle manquante en anglais donne un libelle francais isole au
        milieu de l'interface : repli correct, resultat desagreable."""
        self.assertEqual(
            sorted(i18n.TEXTES["fr"]),
            sorted(i18n.TEXTES["en"]),
            "les tables fr et en ont divergé",
        )

    def test_les_modeles_attendent_les_memes_variables(self):
        """`{zone}` oublie dans la traduction sortirait tel quel dans un rappel."""
        ecarts = []
        for cle, modele_fr in i18n.TEXTES["fr"].items():
            attendues = set(VARIABLES.findall(modele_fr))
            trouvees = set(VARIABLES.findall(i18n.TEXTES["en"][cle]))
            if attendues != trouvees:
                ecarts.append(f"{cle} : fr={sorted(attendues)} en={sorted(trouvees)}")
        self.assertEqual(ecarts, [], "variables divergentes :\n  " + "\n  ".join(ecarts))

    def test_toutes_les_langues_annoncees_ont_une_table(self):
        for langue in i18n.LANGUES:
            self.assertIn(langue, i18n.TEXTES)
            self.assertIn(langue, i18n.FORMATS_DATE)
            self.assertIn(langue, i18n.NOMS_ZONES_DEFAUT)

    def test_les_zones_livrees_sont_traduites_a_l_identique(self):
        """Les quatre zones d'origine, et seulement elles."""
        self.assertEqual(
            sorted(i18n.NOMS_ZONES_DEFAUT["fr"]),
            sorted(i18n.NOMS_ZONES_DEFAUT["en"]),
        )


class ResolutionDeLaLangue(unittest.TestCase):
    def test_un_choix_explicite_gagne_sur_home_assistant(self):
        self.assertEqual(i18n.resoudre("fr", "en"), "fr")
        self.assertEqual(i18n.resoudre("en", "fr"), "en")

    def test_auto_suit_home_assistant(self):
        self.assertEqual(i18n.resoudre("auto", "en"), "en")
        self.assertEqual(i18n.resoudre("auto", "fr"), "fr")

    def test_les_etiquettes_regionales_sont_tolerees(self):
        """`hass.config.language` et `hass.language` n'ont pas le meme format
        selon les versions : « en-GB », « fr_CA », « en »."""
        self.assertEqual(i18n.resoudre("auto", "en-GB"), "en")
        self.assertEqual(i18n.resoudre("auto", "fr_CA"), "fr")
        self.assertEqual(i18n.resoudre("auto", "EN"), "en")

    def test_une_langue_inconnue_retombe_sur_le_francais(self):
        """Repli et non erreur : une option illisible dans `entry.options` ne
        doit pas priver l'utilisateur de son interface."""
        self.assertEqual(i18n.resoudre("auto", "de"), "fr")
        self.assertEqual(i18n.resoudre("klingon", None), "fr")
        self.assertEqual(i18n.resoudre(None, None), "fr")


class RenduDesTextes(unittest.TestCase):
    def test_les_variables_sont_substituees(self):
        self.assertEqual(
            i18n.t("fr", "notif_quand_dans", jours=5), "Dans 5 jours"
        )
        self.assertEqual(i18n.t("en", "notif_quand_dans", jours=5), "In 5 days")

    def test_une_cle_inconnue_se_rend_elle_meme(self):
        """Visible au developpement, jamais une exception en production."""
        self.assertEqual(i18n.t("fr", "cle_qui_n_existe_pas"), "cle_qui_n_existe_pas")

    def test_une_variable_manquante_ne_leve_pas(self):
        """Un modele retouche a la main ne doit pas faire echouer un rappel."""
        self.assertIn("{jours}", i18n.t("fr", "notif_quand_dans"))

    def test_une_langue_inconnue_rend_du_francais(self):
        self.assertEqual(i18n.t("de", "phase_seme"), "Semé")

    def test_les_libelles_du_moteur_passent_par_leur_type(self):
        self.assertEqual(i18n.libelle_phase("en", "en_recolte"), "Harvesting")
        self.assertEqual(i18n.libelle_etape("en", "semis_direct"), "Sow in place")
        self.assertEqual(i18n.libelle_evenement("en", "repique"), "Transplanted")

    def test_un_type_inconnu_se_rend_tel_quel(self):
        """Une phase posee par une version future ne doit pas afficher
        « phase_quelque_chose » a l'utilisateur."""
        self.assertEqual(i18n.libelle_phase("fr", "hibernation"), "hibernation")
        self.assertEqual(i18n.libelle_etape("fr", "greffage"), "greffage")

    def test_les_phases_libellees_couvrent_le_cycle(self):
        """Les options d'un capteur `enum` doivent contenir tous ses etats."""
        self.assertEqual(len(i18n.phases_libellees("fr")), 6)
        self.assertIn("Harvesting", i18n.phases_libellees("en"))


class FormatsDeDate(unittest.TestCase):
    def test_le_format_suit_la_langue(self):
        """« 15/04 » se lit « le 4 du quinzieme mois » pour un anglophone."""
        jour = date(2026, 4, 15)
        self.assertEqual(i18n.date_courte("fr", jour), "15/04")
        self.assertEqual(i18n.date_longue("fr", jour), "15/04/2026")
        self.assertIn("Apr", i18n.date_courte("en", jour))
        self.assertIn("2026", i18n.date_longue("en", jour))

    def test_une_langue_inconnue_prend_le_format_francais(self):
        self.assertEqual(i18n.date_courte("de", date(2026, 4, 15)), "15/04")


class TraductionDesRefus(unittest.TestCase):
    def test_un_refus_a_cle_est_traduit(self):
        from _pure import lifecycle

        err = lifecycle.TransitionInvalide(
            "message francais", cle="err_transition", evenement="seme", phase="seme"
        )
        rendu = i18n.traduire_erreur("en", err)
        # Les deux sous-libelles sont traduits avec le message qui les porte :
        # un refus anglais ne doit pas citer « Semé ».
        self.assertIn("Sown", rendu)
        self.assertNotIn("Semé", rendu)

    def test_un_refus_sans_cle_garde_son_message(self):
        self.assertEqual(
            i18n.traduire_erreur("en", ValueError("quelque chose")), "quelque chose"
        )


class ClesDeTraductionDeHomeAssistant(unittest.TestCase):
    """Les `translation_key` du code et les fichiers de traduction doivent se
    repondre, dans les deux sens.

    Le defaut que ces tests rattrapent etait invisible et ancien : le flux de
    configuration posait un `label=` explicite sur chaque preselection
    climatique, ce qui ecrase la traduction. Le bloc `selector.preset_climat`
    de `translations/en.json` existait donc sans que rien ne l'appelle, et le
    formulaire anglais affichait « Ouest océanique (Bretagne, Loire) ».
    """

    SRC = (
        pathlib.Path(__file__).resolve().parent.parent
        / "custom_components"
        / "rhizome"
    )
    # Les deux sections de `strings.json` indexees par cle depuis le code.
    SECTIONS = ("selector", "exceptions")
    MOTIF_CLE = re.compile(r"""translation_key=["'](\w+)["']""")

    def _fichiers_de_traduction(self):
        chemins = [self.SRC / "strings.json"]
        chemins += sorted((self.SRC / "translations").glob("*.json"))
        return [
            (c.name, json.loads(c.read_text(encoding="utf-8"))) for c in chemins
        ]

    @staticmethod
    def _declarees(contenu):
        declarees = set()
        for section in ClesDeTraductionDeHomeAssistant.SECTIONS:
            declarees |= set(contenu.get(section, {}))
        return declarees

    def _employees(self):
        cles = set()
        for f in self.SRC.glob("*.py"):
            cles |= set(self.MOTIF_CLE.findall(f.read_text(encoding="utf-8")))
        return cles

    def test_chaque_cle_employee_existe_dans_chaque_langue(self):
        employees = self._employees()
        self.assertTrue(employees, "aucun translation_key trouvé — motif obsolète ?")
        for nom, contenu in self._fichiers_de_traduction():
            manquantes = employees - self._declarees(contenu)
            self.assertEqual(manquantes, set(), f"{nom} : clés absentes")

    def test_aucune_cle_orpheline(self):
        """Une cle que plus rien n'appelle est du texte mort, qui donne
        l'illusion d'une traduction."""
        employees = self._employees()
        for nom, contenu in self._fichiers_de_traduction():
            orphelines = self._declarees(contenu) - employees
            self.assertEqual(orphelines, set(), f"{nom} : clés orphelines")

    def test_le_flux_de_configuration_ne_pose_pas_de_libelle_en_dur(self):
        """Un `label=` explicite ecrase la traduction, en silence.

        La seule exception toleree est la liste des destinataires de rappel :
        ses autres options sont des noms d'appareils, donc des donnees qu'il
        ne faut surtout pas traduire. Son libelle fixe passe par `i18n.t`.
        """
        source = (self.SRC / "config_flow.py").read_text(encoding="utf-8")
        en_dur = [
            ligne.strip()
            for ligne in source.splitlines()
            if "label=" in ligne
            and "i18n.t(" not in ligne
            and "removeprefix" not in ligne
        ]
        self.assertEqual(
            en_dur, [], "libellés en dur dans le flux de configuration"
        )


if __name__ == "__main__":
    unittest.main()
