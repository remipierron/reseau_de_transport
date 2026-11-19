"""Tests de la partie A : modélisation orientée objet.

Lancer depuis la racine du projet :
    python -m unittest discover -s tests -v
"""

import unittest

from graphe import (
    ArcExistantError,
    Graphe,
    IdentifiantInvalideError,
    PoidsInvalideError,
    SommetExistantError,
    SommetInconnuError,
)


class TestSommets(unittest.TestCase):
    def setUp(self):
        self.g = Graphe()

    def test_ajout_sommet_correct(self):
        self.g.ajouter_sommet("A")
        self.assertIn("A", self.g)
        self.assertEqual(self.g.sommets(), ["A"])
        self.assertEqual(self.g.nombre_sommets(), 1)

    def test_refus_doublon_sommet(self):
        self.g.ajouter_sommet("A")
        with self.assertRaises(SommetExistantError):
            self.g.ajouter_sommet("A")
        self.assertEqual(self.g.nombre_sommets(), 1)  # le graphe n'a pas changé

    def test_refus_identifiant_vide(self):
        for invalide in ("", "   "):
            with self.assertRaises(IdentifiantInvalideError):
                self.g.ajouter_sommet(invalide)

    def test_refus_identifiant_non_chaine(self):
        with self.assertRaises(IdentifiantInvalideError):
            self.g.ajouter_sommet(42)

    def test_sommet_isole_sans_arc(self):
        self.g.ajouter_sommet("H")
        self.assertEqual(self.g.nombre_arcs(), 0)


class TestArcs(unittest.TestCase):
    def setUp(self):
        self.g = Graphe()
        for s in ("A", "B", "C"):
            self.g.ajouter_sommet(s)

    def test_ajout_arc_correct(self):
        self.g.ajouter_arc("A", "B", 4)
        self.assertTrue(self.g.contient_arc("A", "B"))
        self.assertEqual(self.g.get_arc("A", "B").poids, 4)
        self.assertEqual(self.g.arcs_en_triplets(), [("A", "B", 4)])

    def test_arc_oriente(self):
        self.g.ajouter_arc("A", "B", 4)
        self.assertFalse(self.g.contient_arc("B", "A"))  # A -> B n'implique pas B -> A

    def test_arc_inverse_autorise(self):
        self.g.ajouter_arc("A", "B", 4)
        self.g.ajouter_arc("B", "A", 7)
        self.assertEqual(self.g.nombre_arcs(), 2)

    def test_poids_nul_autorise(self):
        self.g.ajouter_arc("A", "B", 0)
        self.assertEqual(self.g.get_arc("A", "B").poids, 0)

    def test_refus_arc_origine_inconnue(self):
        with self.assertRaises(SommetInconnuError):
            self.g.ajouter_arc("Z", "A", 1)
        self.assertEqual(self.g.nombre_arcs(), 0)

    def test_refus_arc_destination_inconnue(self):
        with self.assertRaises(SommetInconnuError):
            self.g.ajouter_arc("A", "Z", 1)
        self.assertEqual(self.g.nombre_arcs(), 0)

    def test_refus_doublon_arc(self):
        self.g.ajouter_arc("A", "B", 4)
        with self.assertRaises(ArcExistantError):
            self.g.ajouter_arc("A", "B", 9)  # même origine/destination, poids différent
        self.assertEqual(self.g.get_arc("A", "B").poids, 4)  # l'arc d'origine est conservé

    def test_refus_poids_negatif(self):
        with self.assertRaises(PoidsInvalideError):
            self.g.ajouter_arc("A", "B", -1)

    def test_refus_poids_non_numerique(self):
        for invalide in ("4", None, True, float("nan"), float("inf")):
            with self.assertRaises(PoidsInvalideError):
                self.g.ajouter_arc("A", "B", invalide)
        self.assertEqual(self.g.nombre_arcs(), 0)

    def test_get_arc_absent_retourne_none(self):
        self.assertIsNone(self.g.get_arc("A", "C"))


class TestRepresentation(unittest.TestCase):
    def test_graphe_vide(self):
        self.assertEqual(str(Graphe()), "Graphe vide")

    def test_representation_lisible(self):
        g = Graphe()
        for s in ("A", "B", "H"):
            g.ajouter_sommet(s)
        g.ajouter_arc("A", "B", 4)
        texte = str(g)
        self.assertIn("3 sommets, 1 arcs", texte)
        self.assertIn("A -> B (4)", texte)
        self.assertIn("H -> (aucun successeur)", texte)


if __name__ == "__main__":
    unittest.main()