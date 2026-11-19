"""Tests de la partie B : lecture d'un fichier et robustesse.

Les fichiers invalides sont créés dans un dossier temporaire, supprimé
automatiquement après chaque test : le dossier data/ reste propre.
"""

import tempfile
import unittest
from pathlib import Path

from graphe import (
    ArcExistantError,
    FichierIntrouvableError,
    FormatFichierError,
    Graphe,
    IdentifiantInvalideError,
    LigneMalFormeeError,
    PoidsInvalideError,
    SommetExistantError,
    SommetInconnuError,
)

# Chemin construit à partir de l'emplacement de ce fichier :
# fonctionne quel que soit le dossier depuis lequel on lance les tests.
DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"
ENTETE = "Sommets: A, B, C\n"


class TestLectureFichiersFournis(unittest.TestCase):
    def test_lecture_reseau(self):
        g = Graphe.from_file(DOSSIER_DATA / "reseau.txt")
        self.assertEqual(g.sommets(), ["A", "B", "C", "D", "E", "F", "G", "H"])
        self.assertEqual(g.nombre_arcs(), 11)
        self.assertEqual(g.get_arc("A", "B").poids, 4)
        self.assertEqual(g.get_arc("B", "G").poids, 15)
        self.assertIn("H", g)  # sommet isolé bien chargé

    def test_lecture_second_graphe(self):
        g = Graphe.from_file(DOSSIER_DATA / "reseau2.txt")
        self.assertEqual(g.nombre_sommets(), 5)
        self.assertEqual(g.nombre_arcs(), 6)

    def test_chemin_en_chaine_accepte(self):
        g = Graphe.from_file(str(DOSSIER_DATA / "reseau.txt"))
        self.assertEqual(g.nombre_sommets(), 8)


class TestLectureFichiersInvalides(unittest.TestCase):
    def setUp(self):
        self._dossier = tempfile.TemporaryDirectory()
        self.dossier = Path(self._dossier.name)

    def tearDown(self):
        self._dossier.cleanup()

    def ecrire(self, contenu):
        """Écrit `contenu` dans un fichier temporaire et retourne son chemin."""
        chemin = self.dossier / "test.txt"
        chemin.write_text(contenu, encoding="utf-8")
        return chemin

    def verifier_erreur(self, contenu, numero_ligne, cause):
        """Vérifie que la lecture échoue à la bonne ligne pour la bonne raison."""
        with self.assertRaises(FormatFichierError) as ctx:
            Graphe.from_file(self.ecrire(contenu))
        self.assertEqual(ctx.exception.numero_ligne, numero_ligne)
        self.assertIsInstance(ctx.exception.__cause__, cause)
        return ctx.exception

    # --- Cas demandés par le sujet ------------------------------------
    def test_fichier_inexistant(self):
        with self.assertRaises(FichierIntrouvableError):
            Graphe.from_file(self.dossier / "absent.txt")

    def test_fichier_inexistant_est_aussi_un_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Graphe.from_file(self.dossier / "absent.txt")

    def test_ligne_mal_formee(self):
        erreur = self.verifier_erreur(ENTETE + "A;B;4\nA;C\n", 3, LigneMalFormeeError)
        self.assertIn("ligne 3", str(erreur))  # message compréhensible

    def test_trop_de_champs(self):
        self.verifier_erreur(ENTETE + "A;B;4;7\n", 2, LigneMalFormeeError)

    def test_poids_non_numerique(self):
        self.verifier_erreur(ENTETE + "A;B;abc\n", 2, PoidsInvalideError)

    def test_poids_negatif(self):
        self.verifier_erreur(ENTETE + "A;B;-3\n", 2, PoidsInvalideError)

    def test_sommet_inconnu(self):
        self.verifier_erreur(ENTETE + "A;Z;3\n", 2, SommetInconnuError)

    # --- Autres cas limites -------------------------------------------
    def test_fichier_vide(self):
        with self.assertRaises(FormatFichierError):
            Graphe.from_file(self.ecrire(""))

    def test_entete_absente(self):
        self.verifier_erreur("A;B;4\n", 1, LigneMalFormeeError)

    def test_arc_en_double(self):
        self.verifier_erreur(ENTETE + "A;B;4\nA;B;5\n", 3, ArcExistantError)

    def test_sommet_en_double_dans_entete(self):
        self.verifier_erreur("Sommets: A, B, A\n", 1, SommetExistantError)

    def test_identifiant_vide_dans_entete(self):
        self.verifier_erreur("Sommets: A,,B\n", 1, IdentifiantInvalideError)

    def test_extremite_vide(self):
        self.verifier_erreur(ENTETE + ";B;4\n", 2, LigneMalFormeeError)

    def test_tout_le_fichier_est_rejete(self):
        # Une seule ligne fausse suffit : aucun graphe n'est retourné.
        with self.assertRaises(FormatFichierError):
            Graphe.from_file(self.ecrire(ENTETE + "A;B;4\nA;C;2\nB;C;x\n"))

    # --- Souplesse du format ------------------------------------------
    def test_lignes_vides_commentaires_et_espaces(self):
        contenu = (
            "# Mon réseau\n"
            "\n"
            "Sommets :  A ,B,  C\n"
            "  A ; B ; 4  \n"
            "\n"
            "# arc décimal\n"
            "B;C;2.5\n"
        )
        g = Graphe.from_file(self.ecrire(contenu))
        self.assertEqual(g.sommets(), ["A", "B", "C"])
        self.assertEqual(g.get_arc("A", "B").poids, 4)
        self.assertEqual(g.get_arc("B", "C").poids, 2.5)


if __name__ == "__main__":
    unittest.main()