"""Tests de la partie E : sommet interdit et intersection de deux graphes."""

import math
import unittest
from pathlib import Path

from graphe import Graphe, SommetInconnuError

DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"


def plus_petit_cout_en_evitant(graphe, depart, arrivee, interdit):
    """Référence indépendante de Dijkstra : énumère tous les chemins élémentaires."""
    if interdit in (depart, arrivee):
        return math.inf
    if depart == arrivee:
        return 0
    meilleur = math.inf
    pile = [(depart, 0, {depart})]
    while pile:
        sommet, cout, vus = pile.pop()
        for voisin in graphe.successeurs(sommet):
            if voisin in vus or voisin == interdit:
                continue
            nouveau = cout + graphe.get_arc(sommet, voisin).poids
            if voisin == arrivee:
                meilleur = min(meilleur, nouveau)
            else:
                pile.append((voisin, nouveau, vus | {voisin}))
    return meilleur


def etat(graphe):
    """Photographie d'un graphe (sommets + arcs) pour vérifier qu'il n'a pas changé."""
    return graphe.sommets(), graphe.arcs_en_triplets()


class TestCheminAvecSommetInterdit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Graphe.from_file(DOSSIER_DATA / "reseau.txt")

    def test_eviter_C_entre_A_et_G(self):
        # Sans C : A -> B -> D -> E -> F -> G = 4 + 5 + 2 + 3 + 1
        self.assertEqual(
            self.g.shortest_path_avoiding("A", "G", "C"),
            (["A", "B", "D", "E", "F", "G"], 15),
        )

    def test_eviter_D_entre_A_et_G(self):
        # Sans D : A -> C -> E -> F -> G (16) bat A -> C -> B -> G (18)
        self.assertEqual(
            self.g.shortest_path_avoiding("A", "G", "D"),
            (["A", "C", "E", "F", "G"], 16),
        )

    def test_eviter_F_force_l_arc_direct_B_G(self):
        self.assertEqual(
            self.g.shortest_path_avoiding("A", "G", "F"),
            (["A", "C", "B", "G"], 18),
        )

    def test_sommet_interdit_hors_du_chemin_optimal(self):
        # H n'est sur aucun chemin : même résultat que shortest_path.
        self.assertEqual(
            self.g.shortest_path_avoiding("A", "G", "H"),
            self.g.shortest_path("A", "G"),
        )

    def test_interdit_rend_l_arrivee_inaccessible(self):
        # Y est un passage obligé de X vers Z : l'interdire supprime tout chemin.
        g = Graphe()
        for s in "XYZ":
            g.ajouter_sommet(s)
        g.ajouter_arc("X", "Y", 1)
        g.ajouter_arc("Y", "Z", 1)
        self.assertEqual(g.shortest_path_avoiding("X", "Z", "Y"), ([], math.inf))

    def test_interdit_egal_depart(self):
        self.assertEqual(self.g.shortest_path_avoiding("A", "G", "A"), ([], math.inf))

    def test_interdit_egal_arrivee(self):
        self.assertEqual(self.g.shortest_path_avoiding("A", "G", "G"), ([], math.inf))

    def test_depart_egal_arrivee(self):
        self.assertEqual(self.g.shortest_path_avoiding("A", "A", "C"), (["A"], 0))
        self.assertEqual(self.g.shortest_path_avoiding("A", "A", "A"), ([], math.inf))

    def test_sommets_inconnus(self):
        with self.assertRaises(SommetInconnuError):
            self.g.shortest_path_avoiding("A", "G", "Z")
        with self.assertRaises(SommetInconnuError):
            self.g.shortest_path_avoiding("Z", "G", "C")
        with self.assertRaises(SommetInconnuError):
            self.g.shortest_path_avoiding("A", "Z", "C")

    def test_graphe_non_modifie(self):
        avant = etat(self.g)
        self.g.shortest_path_avoiding("A", "G", "C")
        self.assertEqual(etat(self.g), avant)
        # Le sommet interdit reste utilisable ensuite.
        self.assertIn("C", self.g.shortest_path("A", "G")[0])

    def test_tous_les_triplets_des_deux_fichiers(self):
        for nom in ("reseau.txt", "reseau2.txt"):
            g = Graphe.from_file(DOSSIER_DATA / nom)
            for depart in g.sommets():
                for arrivee in g.sommets():
                    for interdit in g.sommets():
                        with self.subTest(fichier=nom, depart=depart,
                                          arrivee=arrivee, interdit=interdit):
                            chemin, cout = g.shortest_path_avoiding(depart, arrivee, interdit)
                            self.assertEqual(
                                cout, plus_petit_cout_en_evitant(g, depart, arrivee, interdit)
                            )
                            self.assertNotIn(interdit, chemin)


class TestIntersection(unittest.TestCase):
    def setUp(self):
        self.g1 = Graphe.from_file(DOSSIER_DATA / "reseau.txt")
        self.g2 = Graphe.from_file(DOSSIER_DATA / "reseau2.txt")

    def test_intersection_des_deux_fichiers(self):
        inter = self.g1.intersection(self.g2)
        self.assertEqual(inter.sommets(), ["A", "B", "C", "D"])
        # A;C a un poids différent (2 contre 3) : il n'est pas commun.
        self.assertEqual(
            set(inter.arcs_en_triplets()),
            {("A", "B", 4), ("C", "B", 1), ("B", "D", 5)},
        )

    def test_graphes_initiaux_non_modifies(self):
        avant1, avant2 = etat(self.g1), etat(self.g2)
        inter = self.g1.intersection(self.g2)
        self.assertEqual(etat(self.g1), avant1)
        self.assertEqual(etat(self.g2), avant2)
        # Modifier le résultat ne touche pas non plus les originaux.
        inter.ajouter_sommet("Nouveau")
        inter.ajouter_arc("D", "A", 7)
        self.assertEqual(etat(self.g1), avant1)
        self.assertEqual(etat(self.g2), avant2)

    def test_resultat_est_un_nouveau_graphe(self):
        inter = self.g1.intersection(self.g1)
        self.assertIsInstance(inter, Graphe)
        self.assertIsNot(inter, self.g1)
        self.assertIsNot(inter.get_sommet("A"), self.g1.get_sommet("A"))

    def test_intersection_avec_soi_meme(self):
        inter = self.g1.intersection(self.g1)
        self.assertEqual(etat(inter), etat(self.g1))

    def test_commutativite_des_ensembles(self):
        a, b = self.g1.intersection(self.g2), self.g2.intersection(self.g1)
        self.assertEqual(set(a.sommets()), set(b.sommets()))
        self.assertEqual(set(a.arcs_en_triplets()), set(b.arcs_en_triplets()))

    def test_arc_de_sens_oppose_non_commun(self):
        g1, g2 = Graphe(), Graphe()
        for g in (g1, g2):
            g.ajouter_sommet("P")
            g.ajouter_sommet("Q")
        g1.ajouter_arc("P", "Q", 1)
        g2.ajouter_arc("Q", "P", 1)
        inter = g1.intersection(g2)
        self.assertEqual(inter.sommets(), ["P", "Q"])
        self.assertEqual(inter.nombre_arcs(), 0)

    def test_poids_entier_et_decimal_egaux(self):
        g1, g2 = Graphe(), Graphe()
        for g in (g1, g2):
            g.ajouter_sommet("P")
            g.ajouter_sommet("Q")
        g1.ajouter_arc("P", "Q", 2)
        g2.ajouter_arc("P", "Q", 2.0)
        self.assertEqual(g1.intersection(g2).nombre_arcs(), 1)

    def test_aucun_sommet_commun(self):
        autre = Graphe()
        autre.ajouter_sommet("Z")
        inter = self.g1.intersection(autre)
        self.assertEqual(inter.nombre_sommets(), 0)
        self.assertEqual(inter.nombre_arcs(), 0)

    def test_avec_graphe_vide(self):
        self.assertEqual(len(self.g1.intersection(Graphe())), 0)
        self.assertEqual(len(Graphe().intersection(self.g1)), 0)

    def test_sommet_isole_commun_conserve(self):
        autre = Graphe()
        autre.ajouter_sommet("H")
        self.assertEqual(self.g1.intersection(autre).sommets(), ["H"])

    def test_argument_invalide(self):
        with self.assertRaises(TypeError):
            self.g1.intersection("pas un graphe")


if __name__ == "__main__":
    unittest.main()