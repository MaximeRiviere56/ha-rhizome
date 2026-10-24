"""Garde-fous sur la source elle-meme, sans executer Home Assistant.

La couche HA n'est pas testable sur le poste de developpement : ces verifications
lisent le code plutot que de l'appeler. Elles ne remplacent pas un test, mais
elles attrapent une classe de defaut que rien d'autre ne voit ici.
"""

import ast
import pathlib
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


if __name__ == "__main__":
    unittest.main()
