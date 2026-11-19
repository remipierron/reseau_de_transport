"""Tests de la partie D : recherche du plus court chemin (Dijkstra)."""

import math
import unittest
from pathlib import Path

from graphe import Graphe, SommetInconnuError

DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"


def cout_du_chemin(graphe, chemin):
    """Somme des poids le long du chemin (échoue si un arc n'existe pas)."""
    return sum(graphe.get_arc(a, b).poids for a, b in zip(chemin, chemin[1:]))


def plus_petit_cout_force_brute(graphe, depart, arrivee):
    """Énumère tous les chemins élémentaires : référence indépendante de Dijkstra."""
    if depart == arrivee:
        return 0
    meilleur = math.inf
    pile = [(depart, 0, {depart})]
    while pile:
        sommet, cout, vus = pile.pop()
        for voisin in graphe.successeurs(sommet):
            if voisin in vus:
                continue
            nouveau = cout + graphe.get_arc(sommet, voisin).poids
            if voisin == arrivee:
                meilleur = min(meilleur, nouveau)
            else:
                pile.append((voisin, nouveau, vus | {voisin}))
    return meilleur


class TestPlusCourtCheminReseau(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Graphe.from_file(DOSSIER_DATA / "reseau.txt")

    def test_chemin_A_G(self):
        # Résultat demandé dans le sujet : A -> C -> B -> D -> E -> F -> G, coût 14
        # (2 + 1 + 5 + 2 + 3 + 1). L'arc direct B -> G (15) est plus cher.
        chemin, cout = self.g.shortest_path("A", "G")
        self.assertEqual(chemin, ["A", "C", "B", "D", "E", "F", "G"])
        self.assertEqual(cout, 14)

    def test_detour_moins_cher_que_arc_direct(self):
        # A -> B direct coûte 4, mais A -> C -> B coûte 2 + 1 = 3.
        self.assertEqual(self.g.shortest_path("A", "B"), (["A", "C", "B"], 3))

    def test_arc_direct_optimal(self):
        self.assertEqual(self.g.shortest_path("F", "G"), (["F", "G"], 1))

    def test_depart_egal_arrivee(self):
        self.assertEqual(self.g.shortest_path("A", "A"), (["A"], 0))
        # Vrai aussi pour un sommet isolé.
        self.assertEqual(self.g.shortest_path("H", "H"), (["H"], 0))

    def test_aucun_chemin_vers_sommet_isole(self):
        self.assertEqual(self.g.shortest_path("A", "H"), ([], math.inf))
        self.assertEqual(self.g.shortest_path("H", "A"), ([], math.inf))

    def test_aucun_chemin_sens_inverse(self):
        # A -> G existe, mais le graphe est orienté et G n'a aucun successeur.
        chemin, cout = self.g.shortest_path("G", "A")
        self.assertEqual(chemin, [])
        self.assertTrue(math.isinf(cout))

    def test_sommet_inconnu(self):
        for depart, arrivee in (("Z", "A"), ("A", "Z"), ("Z", "Z")):
            with self.assertRaises(SommetInconnuError):
                self.g.shortest_path(depart, arrivee)

    def test_graphe_non_modifie(self):
        avant = self.g.arcs_en_triplets()
        self.g.shortest_path("A", "G")
        self.assertEqual(self.g.arcs_en_triplets(), avant)

    def test_coherence_chemin_et_cout(self):
        # Pour chaque couple relié : le chemin commence et finit au bon endroit,
        # n'emprunte que des arcs existants et son coût est bien la somme des poids.
        for depart in self.g.sommets():
            for arrivee in self.g.sommets():
                chemin, cout = self.g.shortest_path(depart, arrivee)
                if not chemin:
                    continue
                self.assertEqual(chemin[0], depart)
                self.assertEqual(chemin[-1], arrivee)
                self.assertEqual(len(chemin), len(set(chemin)))  # pas de boucle
                self.assertEqual(cout_du_chemin(self.g, chemin), cout)


class TestPlusCourtCheminForceBrute(unittest.TestCase):
    def test_tous_les_couples_des_deux_fichiers(self):
        for nom in ("reseau.txt", "reseau2.txt"):
            g = Graphe.from_file(DOSSIER_DATA / nom)
            for depart in g.sommets():
                for arrivee in g.sommets():
                    with self.subTest(fichier=nom, depart=depart, arrivee=arrivee):
                        _, cout = g.shortest_path(depart, arrivee)
                        attendu = plus_petit_cout_force_brute(g, depart, arrivee)
                        self.assertEqual(cout, attendu)


class TestPlusCourtCheminCasParticuliers(unittest.TestCase):
    def test_graphe_avec_cycle(self):
        # reseau2 contient le cycle A -> B -> D -> X -> A : Dijkstra ne doit pas boucler.
        g = Graphe.from_file(DOSSIER_DATA / "reseau2.txt")
        self.assertEqual(g.shortest_path("D", "C"), (["D", "X", "A", "C"], 6))

    def test_poids_nuls(self):
        g = Graphe()
        for s in "ABC":
            g.ajouter_sommet(s)
        g.ajouter_arc("A", "B", 0)
        g.ajouter_arc("B", "C", 0)
        g.ajouter_arc("A", "C", 1)
        self.assertEqual(g.shortest_path("A", "C"), (["A", "B", "C"], 0))

    def test_poids_decimaux(self):
        g = Graphe()
        for s in "ABC":
            g.ajouter_sommet(s)
        g.ajouter_arc("A", "B", 1.5)
        g.ajouter_arc("B", "C", 2.25)
        g.ajouter_arc("A", "C", 4)
        chemin, cout = g.shortest_path("A", "C")
        self.assertEqual(chemin, ["A", "B", "C"])
        self.assertAlmostEqual(cout, 3.75)

    def test_premier_arc_bon_marche_mais_suite_chere(self):
        # Piège pour un algorithme glouton : A -> B (1) semble attirant,
        # mais B -> D coûte 100 ; le bon chemin passe par C.
        g = Graphe()
        for s in "ABCD":
            g.ajouter_sommet(s)
        g.ajouter_arc("A", "B", 1)
        g.ajouter_arc("B", "D", 100)
        g.ajouter_arc("A", "C", 5)
        g.ajouter_arc("C", "D", 5)
        self.assertEqual(g.shortest_path("A", "D"), (["A", "C", "D"], 10))

    def test_graphe_a_un_seul_sommet(self):
        g = Graphe()
        g.ajouter_sommet("A")
        self.assertEqual(g.shortest_path("A", "A"), (["A"], 0))


if __name__ == "__main__":
    unittest.main()