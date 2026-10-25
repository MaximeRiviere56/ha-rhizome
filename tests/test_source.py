"""Garde-fous sur la source elle-meme, sans executer Home Assistant.

La couche HA n'est pas testable sur le poste de developpement : ces verifications
lisent le code plutot que de l'appeler. Elles ne remplacent pas un test, mais
elles attrapent une classe de defaut que rien d'autre ne voit ici.
"""

import ast
import pathlib
import re
import unittest

SRC = pathlib.Path(__file__).resolve().parent.parent / "custom_components" / "rhizome"


class ClesDupliquees(unittest.TestCase):
    """Une cle ecrite deux fois dans le meme dictionnaire litteral.

    Python l'accepte sans broncher et garde la derniere. C'est ainsi que
    `_plante_en_dict` a renvoye les besoins theoriques de la culture sous la
    cle « arrosage » au lieu de l'etat calcule de la plante : le panneau n'a
    jamais affiche d'echeance d'arrosage, et aucune erreur n'est apparue.
    """

    def test_aucun_dictionnaire_ne_repete_une_cle(self):
        fautes = []
        for fichier in sorted(SRC.rglob("*.py")):
            arbre = ast.parse(fichier.read_text(encoding="utf-8"), str(fichier))
            for noeud in ast.walk(arbre):
                if not isinstance(noeud, ast.Dict):
                    continue
                vues = set()
                for cle in noeud.keys:
                    # `**autre` donne une cle None : rien a comparer.
                    if not isinstance(cle, ast.Constant):
                        continue
                    if cle.value in vues:
                        fautes.append(
                            f"{fichier.relative_to(SRC.parent.parent)}:"
                            f"{cle.lineno} — clé « {cle.value} » répétée"
                        )
                    vues.add(cle.value)

        self.assertEqual(fautes, [], "Clés dupliquées :\n  " + "\n  ".join(fautes))


class EchappementDuFrontend(unittest.TestCase):
    """`echappe()` doit couvrir les guillemets, pas seulement les chevrons.

    Il n'y a pas de Node sur ce poste : ces verifications lisent le source au
    lieu de l'executer. Elles existent parce que la faute qu'elles attrapent
    etait invisible — `textContent` puis `innerHTML` echappe `&`, `<` et `>`
    mais laisse passer `"`, ce qui est sans danger dans un noeud de texte et
    ouvre une XSS stockee des que le resultat atterrit dans un attribut. Or
    `echappe()` est employe dans des attributs a une dizaine d'endroits :
    `value="${echappe(plante.surnom)}"`, `title="${echappe(ligne.nom)}"`.
    """

    FRONTEND = SRC / "frontend"
    #  Les cinq caracteres qu'un echappement HTML doit couvrir pour etre sur
    #  dans un attribut comme dans un noeud de texte.
    ENTITES = ('"&": "&amp;"', '"<": "&lt;"', '">": "&gt;"',
               '\'"\': "&quot;"', '"\'": "&#39;"')

    def _sources(self):
        fichiers = sorted(self.FRONTEND.glob("*.js"))
        self.assertTrue(fichiers, "aucun fichier frontend trouvé")
        return [(f, f.read_text(encoding="utf-8")) for f in fichiers]

    def test_echappe_couvre_les_cinq_caracteres(self):
        for fichier, source in self._sources():
            if "function echappe" not in source and "const echappe" not in source:
                continue
            for entite in self.ENTITES:
                self.assertIn(
                    entite,
                    source,
                    f"{fichier.name} : la table d'échappement ne couvre pas "
                    f"{entite}",
                )

    def test_echappe_ne_passe_plus_par_le_serialiseur_html(self):
        """`div.textContent = …; return div.innerHTML` n'échappe pas `"`."""
        for fichier, source in self._sources():
            self.assertNotIn(
                "div.innerHTML",
                source,
                f"{fichier.name} : échappement via le sérialiseur HTML, qui "
                f"laisse passer les guillemets",
            )

    # Les champs que l'utilisateur remplit librement, et qui reviennent du
    # stockage tels qu'il les a ecrits. Tout le reste de ce qui traverse le
    # panneau est soit une constante du source, soit une valeur contrainte par
    # un schema (uid hexadecimal, entier borne, identifiant slugifie).
    TEXTES_LIBRES = (
        "surnom", "nom", "note", "cause", "sol", "notes", "famille", "emoji",
    )
    # Ce qui porte un de ces noms sans venir du stockage : les vues du
    # panneau et les libelles de fenetres sont des constantes de ce fichier.
    CONSTANTES_DU_SOURCE = ("v.nom", "etape.libelle", "prochaine.libelle")

    def test_aucun_texte_libre_interpole_sans_echappement(self):
        """Un champ saisi par l'utilisateur passe toujours par `echappe()`.

        Peu importe le contexte : un `${plante.surnom}` nu est une XSS dans un
        noeud de texte, et l'etait aussi dans un attribut tant que `echappe()`
        laissait passer les guillemets.
        """
        champs = "|".join(self.TEXTES_LIBRES)
        motif = re.compile(r"\$\{([^{}]*\.(?:" + champs + r")\b[^{}]*)\}")
        fautes = []
        for fichier, source in self._sources():
            for numero, ligne in enumerate(source.splitlines(), 1):
                # Un gabarit sans balise ni attribut ne construit pas de
                # HTML : la recherche du catalogue concatene `nom` et
                # `famille` pour comparer des chaines, pas pour les afficher.
                # On teste aussi `="`, car un attribut occupe souvent sa
                # propre ligne, loin du chevron qui ouvre la balise.
                if not any(marque in ligne for marque in ("<", ">", '="')):
                    continue
                for expression in motif.findall(ligne):
                    if "echappe(" in expression:
                        continue
                    if any(c in expression for c in self.CONSTANTES_DU_SOURCE):
                        continue
                    fautes.append(
                        f"{fichier.name}:{numero} — ${{{expression.strip()}}}"
                    )
        self.assertEqual(
            fautes,
            [],
            "Textes libres interpolés sans échappement :\n  "
            + "\n  ".join(fautes),
        )


if __name__ == "__main__":
    unittest.main()
