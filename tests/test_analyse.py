"""Tests de la partie C : analyse du réseau (degrés, prédécesseurs, successeurs)."""

import unittest
from pathlib import Path

from graphe import Graphe, SommetInconnuError

DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"


class TestAnalyse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Le graphe n'est pas modifié par ces tests : on le charge une seule fois.
        cls.g = Graphe.from_file(DOSSIER_DATA / "reseau.txt")

    def test_sommet_isole_H(self):
        self.assertEqual(self.g.degre_entrant("H"), 0)
        self.assertEqual(self.g.degre_sortant("H"), 0)
        self.assertEqual(self.g.degre_total("H"), 0)
        self.assertEqual(self.g.predecesseurs("H"), [])
        self.assertEqual(self.g.successeurs("H"), [])
        self.assertTrue(self.g.est_isole("H"))

    def test_sommet_B(self):
        # Arcs entrants : A->B, C->B ; arcs sortants : B->D, B->G
        self.assertEqual(self.g.degre_entrant("B"), 2)
        self.assertEqual(self.g.degre_sortant("B"), 2)
        self.assertEqual(self.g.degre_total("B"), 4)
        self.assertEqual(sorted(self.g.predecesseurs("B")), ["A", "C"])
        self.assertEqual(sorted(self.g.successeurs("B")), ["D", "G"])

    def test_sommet_C(self):
        # Arc entrant : A->C ; arcs sortants : C->B, C->D, C->E
        self.assertEqual(self.g.degre_entrant("C"), 1)
        self.assertEqual(self.g.degre_sortant("C"), 3)
        self.assertEqual(self.g.degre_total("C"), 4)
        self.assertEqual(self.g.predecesseurs("C"), ["A"])
        self.assertEqual(sorted(self.g.successeurs("C")), ["B", "D", "E"])

    def test_sommet_G_sans_successeur(self):
        self.assertEqual(self.g.degre_sortant("G"), 0)
        self.assertEqual(sorted(self.g.predecesseurs("G")), ["B", "F"])
        self.assertFalse(self.g.est_isole("G"))

    def test_sommet_A_sans_predecesseur(self):
        self.assertEqual(self.g.degre_entrant("A"), 0)
        self.assertEqual(sorted(self.g.successeurs("A")), ["B", "C"])

    def test_analyser_sommet(self):
        infos = self.g.analyser_sommet("D")
        self.assertEqual(infos["degre_entrant"], 2)
        self.assertEqual(infos["degre_sortant"], 2)
        self.assertEqual(infos["degre_total"], 4)
        self.assertEqual(sorted(infos["predecesseurs"]), ["B", "C"])
        self.assertEqual(sorted(infos["successeurs"]), ["E", "F"])

    def test_sommet_inconnu(self):
        for methode in (self.g.degre_entrant, self.g.degre_sortant, self.g.degre_total,
                        self.g.predecesseurs, self.g.successeurs):
            with self.assertRaises(SommetInconnuError):
                methode("Z")

    def test_resultat_modifiable_sans_effet_sur_le_graphe(self):
        succ = self.g.successeurs("A")
        succ.append("Z")
        self.assertEqual(sorted(self.g.successeurs("A")), ["B", "C"])

    def test_somme_des_degres(self):
        # Propriété des graphes orientés : somme des degrés entrants
        # = somme des degrés sortants = nombre d'arcs.
        total_entrant = sum(self.g.degre_entrant(s) for s in self.g.sommets())
        total_sortant = sum(self.g.degre_sortant(s) for s in self.g.sommets())
        self.assertEqual(total_entrant, self.g.nombre_arcs())
        self.assertEqual(total_sortant, self.g.nombre_arcs())


if __name__ == "__main__":
    unittest.main()