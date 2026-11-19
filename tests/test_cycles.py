"""Tests de la partie F (bonus) : détection de cycle et tri topologique."""

import itertools
import random
import unittest
from pathlib import Path

from graphe import Graphe, GrapheCycliqueError, GrapheError

DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"


def construire(sommets, arcs):
    """Petit graphe de test : arcs donnés en couples (origine, destination), poids 1."""
    g = Graphe()
    for s in sommets:
        g.ajouter_sommet(s)
    for origine, destination in arcs:
        g.ajouter_arc(origine, destination, 1)
    return g


def etat(graphe):
    """Photographie d'un graphe (sommets + arcs) pour vérifier qu'il n'a pas changé."""
    return graphe.sommets(), graphe.arcs_en_triplets()


def a_un_cycle_par_force_brute(graphe):
    """Référence indépendante : un graphe est acyclique si et seulement si
    au moins une permutation de ses sommets respecte tous les arcs.
    Réservé aux très petits graphes (n! permutations)."""
    arcs = [(o, d) for o, d, _ in graphe.arcs_en_triplets()]
    for permutation in itertools.permutations(graphe.sommets()):
        rang = {s: i for i, s in enumerate(permutation)}
        if all(rang[o] < rang[d] for o, d in arcs):
            return False
    return True


class OutilsVerification:
    """Assertions communes aux deux classes de tests."""

    def assertCycleValide(self, graphe, cycle):
        """Le cycle est fermé, ses arcs existent et il ne repasse pas par un sommet."""
        self.assertGreaterEqual(len(cycle), 2)
        self.assertEqual(cycle[0], cycle[-1], "le cycle doit être fermé")
        self.assertEqual(len(set(cycle[:-1])), len(cycle) - 1, "cycle non élémentaire")
        for origine, destination in zip(cycle, cycle[1:]):
            self.assertTrue(graphe.contient_arc(origine, destination),
                            f"l'arc {origine} -> {destination} n'existe pas")

    def assertOrdreTopologique(self, graphe, ordre):
        """Chaque sommet apparaît une fois et chaque arc va vers l'avant."""
        self.assertCountEqual(ordre, graphe.sommets())
        rang = {s: i for i, s in enumerate(ordre)}
        for origine, destination, _ in graphe.arcs_en_triplets():
            self.assertLess(rang[origine], rang[destination],
                            f"{origine} doit précéder {destination}")


class TestDetectionCycle(OutilsVerification, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reseau = Graphe.from_file(DOSSIER_DATA / "reseau.txt")
        cls.reseau2 = Graphe.from_file(DOSSIER_DATA / "reseau2.txt")

    # Cas négatifs : graphes acycliques
    def test_reseau_du_sujet_est_acyclique(self):
        self.assertFalse(self.reseau.has_cycle())
        self.assertEqual(self.reseau.trouver_cycle(), [])

    def test_graphe_vide_est_acyclique(self):
        self.assertFalse(Graphe().has_cycle())

    def test_sommets_isoles_seuls_sont_acycliques(self):
        self.assertFalse(construire("ABC", []).has_cycle())

    def test_losange_n_est_pas_un_cycle(self):
        # Deux chemins A -> B -> D et A -> C -> D se rejoignent : pas de cycle.
        # Un DFS qui confondrait « déjà visité » et « en cours » se tromperait ici.
        g = construire("ABCD", [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
        self.assertFalse(g.has_cycle())

    def test_arcs_opposes_vers_un_sommet_termine(self):
        # D est terminé (NOIR) quand on l'atteint depuis C : ce n'est pas un cycle.
        g = construire("ABCD", [("A", "D"), ("B", "C"), ("C", "D")])
        self.assertFalse(g.has_cycle())

    # Cas positifs : graphes avec cycle
    def test_reseau2_contient_un_cycle(self):
        # A -> B -> D -> X -> A
        self.assertTrue(self.reseau2.has_cycle())
        cycle = self.reseau2.trouver_cycle()
        self.assertEqual(cycle, ["A", "B", "D", "X", "A"])
        self.assertCycleValide(self.reseau2, cycle)

    def test_ajout_d_un_cycle_au_reseau_du_sujet(self):
        # Copie de reseau.txt à laquelle on ajoute G -> A : A -> ... -> G -> A.
        g = Graphe.from_file(DOSSIER_DATA / "reseau.txt")
        self.assertFalse(g.has_cycle())
        g.ajouter_arc("G", "A", 1)
        self.assertTrue(g.has_cycle())
        self.assertCycleValide(g, g.trouver_cycle())

    def test_cycle_de_deux_sommets(self):
        g = construire("AB", [("A", "B"), ("B", "A")])
        self.assertTrue(g.has_cycle())
        self.assertEqual(g.trouver_cycle(), ["A", "B", "A"])

    def test_boucle_sur_un_sommet(self):
        g = construire("AB", [("A", "B"), ("B", "B")])
        self.assertTrue(g.has_cycle())
        self.assertEqual(g.trouver_cycle(), ["B", "B"])

    def test_cycle_dans_une_partie_non_accessible_depuis_le_premier_sommet(self):
        # A -> B est acyclique ; le cycle C -> D -> E -> C n'est pas atteint depuis A.
        g = construire("ABCDE", [("A", "B"), ("C", "D"), ("D", "E"), ("E", "C")])
        self.assertTrue(g.has_cycle())
        self.assertEqual(g.trouver_cycle(), ["C", "D", "E", "C"])

    def test_cycle_atteint_apres_une_branche_sans_cycle(self):
        # Depuis A, la branche A -> B est explorée en premier et ne contient
        # pas de cycle ; le cycle C -> D -> C n'est trouvé qu'ensuite.
        g = construire("ABCD", [("A", "B"), ("A", "C"), ("C", "D"), ("D", "C")])
        self.assertEqual(g.trouver_cycle(), ["C", "D", "C"])

    # Robustesse
    def test_long_graphe_sans_recursion_error(self):
        # Chaîne de 5000 sommets : une version récursive dépasserait la limite de Python.
        n = 5000
        g = construire([f"S{i}" for i in range(n)],
                       [(f"S{i}", f"S{i + 1}") for i in range(n - 1)])
        self.assertFalse(g.has_cycle())
        g.ajouter_arc(f"S{n - 1}", "S0", 1)
        self.assertTrue(g.has_cycle())
        self.assertEqual(len(g.trouver_cycle()), n + 1)

    def test_graphe_non_modifie(self):
        avant = etat(self.reseau2)
        self.reseau2.has_cycle()
        self.reseau2.trouver_cycle()
        self.assertEqual(etat(self.reseau2), avant)

    def test_comparaison_avec_force_brute_sur_graphes_aleatoires(self):
        hasard = random.Random(2026)  # graine fixe : test reproductible
        for _ in range(300):
            n = hasard.randint(1, 6)
            sommets = [chr(ord("A") + i) for i in range(n)]
            arcs = [(o, d) for o in sommets for d in sommets if hasard.random() < 0.25]
            g = construire(sommets, arcs)
            attendu = a_un_cycle_par_force_brute(g)
            with self.subTest(arcs=arcs):
                self.assertEqual(g.has_cycle(), attendu)
                if attendu:
                    self.assertCycleValide(g, g.trouver_cycle())


class TestTriTopologique(OutilsVerification, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reseau = Graphe.from_file(DOSSIER_DATA / "reseau.txt")
        cls.reseau2 = Graphe.from_file(DOSSIER_DATA / "reseau2.txt")

    # Cas positifs : un ordre existe
    def test_ordre_du_reseau_du_sujet(self):
        # Kahn avec file FIFO : A et H (degré entrant 0) d'abord, puis C, B, D, E, F, G.
        ordre = self.reseau.topological_sort()
        self.assertEqual(ordre, ["A", "H", "C", "B", "D", "E", "F", "G"])
        self.assertOrdreTopologique(self.reseau, ordre)

    def test_sommet_isole_present_dans_l_ordre(self):
        self.assertIn("H", self.reseau.topological_sort())

    def test_graphe_vide(self):
        self.assertEqual(Graphe().topological_sort(), [])

    def test_sommets_isoles_dans_l_ordre_d_ajout(self):
        self.assertEqual(construire("CAB", []).topological_sort(), ["C", "A", "B"])

    def test_chaine_dans_le_sens_inverse_de_l_ajout(self):
        # Sommets ajoutés A, B, C mais arcs C -> B -> A : l'ordre doit être C, B, A.
        g = construire("ABC", [("C", "B"), ("B", "A")])
        self.assertEqual(g.topological_sort(), ["C", "B", "A"])

    def test_losange(self):
        g = construire("ABCD", [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
        ordre = g.topological_sort()
        self.assertEqual(ordre[0], "A")
        self.assertEqual(ordre[-1], "D")
        self.assertOrdreTopologique(g, ordre)

    def test_resultat_modifiable_sans_effet_sur_le_graphe(self):
        avant = etat(self.reseau)
        ordre = self.reseau.topological_sort()
        ordre.clear()
        self.assertEqual(etat(self.reseau), avant)
        self.assertEqual(len(self.reseau.topological_sort()), 8)

    # Cas négatifs : aucun ordre n'existe
    def test_reseau2_avec_cycle_leve_une_exception(self):
        with self.assertRaises(GrapheCycliqueError) as contexte:
            self.reseau2.topological_sort()
        erreur = contexte.exception
        self.assertEqual(erreur.cycle, ["A", "B", "D", "X", "A"])
        self.assertIn("A -> B -> D -> X -> A", str(erreur))

    def test_exception_rattachee_a_la_hierarchie_du_projet(self):
        # Interceptable avec `except GrapheError` comme les autres erreurs, ou en ValueError.
        for type_attendu in (GrapheError, ValueError):
            with self.assertRaises(type_attendu):
                self.reseau2.topological_sort()

    def test_boucle_sur_un_sommet(self):
        g = construire("AB", [("A", "B"), ("B", "B")])
        with self.assertRaises(GrapheCycliqueError) as contexte:
            g.topological_sort()
        self.assertEqual(contexte.exception.cycle, ["B", "B"])

    def test_cycle_qui_ne_contient_pas_tous_les_sommets_bloques(self):
        # E dépend du cycle B <-> C sans en faire partie : le cycle signalé est bien B, C.
        g = construire("ABCDE", [("A", "B"), ("B", "C"), ("C", "B"), ("C", "E"), ("A", "D")])
        with self.assertRaises(GrapheCycliqueError) as contexte:
            g.topological_sort()
        self.assertCycleValide(g, contexte.exception.cycle)
        self.assertNotIn("E", contexte.exception.cycle)

    def test_ajout_d_un_cycle_rend_le_tri_impossible(self):
        g = Graphe.from_file(DOSSIER_DATA / "reseau.txt")
        g.topological_sort()  # possible avant l'ajout
        g.ajouter_arc("E", "C", 1)  # C -> E -> C
        with self.assertRaises(GrapheCycliqueError):
            g.topological_sort()

    def test_graphe_non_modifie_meme_en_cas_d_echec(self):
        avant = etat(self.reseau2)
        with self.assertRaises(GrapheCycliqueError):
            self.reseau2.topological_sort()
        self.assertEqual(etat(self.reseau2), avant)

    def test_coherence_avec_has_cycle_sur_graphes_aleatoires(self):
        hasard = random.Random(1789)
        for _ in range(300):
            n = hasard.randint(0, 7)
            sommets = [chr(ord("A") + i) for i in range(n)]
            arcs = [(o, d) for o in sommets for d in sommets if hasard.random() < 0.2]
            g = construire(sommets, arcs)
            with self.subTest(arcs=arcs):
                if g.has_cycle():
                    with self.assertRaises(GrapheCycliqueError):
                        g.topological_sort()
                else:
                    self.assertOrdreTopologique(g, g.topological_sort())


if __name__ == "__main__":
    unittest.main()