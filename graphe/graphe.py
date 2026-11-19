"""Classe Graphe : graphe orienté pondéré.

Structures de données choisies
------------------------------
- self._sommets : dict  identifiant -> Sommet
    Accès, test de présence et détection des doublons en O(1).
    Depuis Python 3.7, un dict conserve l'ordre d'insertion,
    ce qui donne un affichage stable.
- self._adjacence : dict  identifiant -> dict(identifiant_destination -> Arc)
    Liste d'adjacence. Le dict interne permet de savoir en O(1)
    si l'arc A -> B existe déjà (interdiction des doublons) et
    d'énumérer rapidement les successeurs (utile pour Dijkstra).
    Un sommet isolé a simplement un dict interne vide.

Aucune méthode de cette classe n'appelle input() ni print() :
elles retournent des valeurs ou lèvent des exceptions.
"""

from .arc import Arc
from .exceptions import (
    ArcExistantError,
    SommetExistantError,
    SommetInconnuError,
)
from .sommet import Sommet


class Graphe:
    """Graphe orienté pondéré G = (V, E)."""

    def __init__(self):
        self._sommets = {}
        self._adjacence = {}

    # ------------------------------------------------------------------
    # Ajout
    # ------------------------------------------------------------------
    def ajouter_sommet(self, identifiant):
        """Ajoute un sommet et le retourne.

        Lève IdentifiantInvalideError si l'identifiant est vide ou n'est pas
        une chaîne, SommetExistantError s'il est déjà présent.
        """
        sommet = Sommet(identifiant)  # valide l'identifiant
        if sommet.identifiant in self._sommets:
            raise SommetExistantError(
                f"Le sommet '{sommet.identifiant}' existe déjà dans le graphe."
            )
        self._sommets[sommet.identifiant] = sommet
        self._adjacence[sommet.identifiant] = {}
        return sommet

    def ajouter_arc(self, origine, destination, poids):
        """Ajoute l'arc origine -> destination et le retourne.

        Lève SommetInconnuError si une extrémité n'existe pas,
        PoidsInvalideError si le poids est invalide,
        ArcExistantError si l'arc origine -> destination existe déjà.
        """
        s_origine = self._obtenir_sommet(origine)
        s_destination = self._obtenir_sommet(destination)

        # On crée l'arc avant le test de doublon : le poids est donc validé
        # en premier, mais rien n'est ajouté tant que tout n'est pas vérifié.
        arc = Arc(s_origine, s_destination, poids)

        if s_destination.identifiant in self._adjacence[s_origine.identifiant]:
            raise ArcExistantError(
                f"L'arc {s_origine} -> {s_destination} existe déjà."
            )
        self._adjacence[s_origine.identifiant][s_destination.identifiant] = arc
        return arc

    # ------------------------------------------------------------------
    # Consultation
    # ------------------------------------------------------------------
    def sommets(self):
        """Liste des identifiants des sommets, dans l'ordre d'ajout."""
        return list(self._sommets)

    def arcs(self):
        """Liste de tous les arcs (objets Arc)."""
        return [arc for voisins in self._adjacence.values() for arc in voisins.values()]

    def arcs_en_triplets(self):
        """Liste des arcs sous forme de triplets (origine, destination, poids)."""
        return [arc.en_triplet() for arc in self.arcs()]

    def get_sommet(self, identifiant):
        """Retourne l'objet Sommet correspondant (SommetInconnuError sinon)."""
        return self._obtenir_sommet(identifiant)

    def get_arc(self, origine, destination):
        """Retourne l'arc origine -> destination, ou None s'il n'existe pas.

        Lève SommetInconnuError si l'une des extrémités est inconnue.
        """
        self._obtenir_sommet(origine)
        self._obtenir_sommet(destination)
        return self._adjacence[origine].get(destination)

    def contient_sommet(self, identifiant):
        return identifiant in self._sommets

    def contient_arc(self, origine, destination):
        return (
            origine in self._adjacence
            and destination in self._adjacence[origine]
        )

    def nombre_sommets(self):
        return len(self._sommets)

    def nombre_arcs(self):
        return sum(len(voisins) for voisins in self._adjacence.values())

    # Raccourcis Python : len(g) et "A" in g
    def __len__(self):
        return self.nombre_sommets()

    def __contains__(self, identifiant):
        return self.contient_sommet(identifiant)

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------
    def __repr__(self):
        return f"Graphe({self.nombre_sommets()} sommets, {self.nombre_arcs()} arcs)"

    def __str__(self):
        """Représentation lisible : un sommet par ligne avec ses successeurs."""
        if not self._sommets:
            return "Graphe vide"
        lignes = [repr(self)]
        for ident, voisins in self._adjacence.items():
            if voisins:
                details = ", ".join(f"{dest} ({arc.poids})" for dest, arc in voisins.items())
            else:
                details = "(aucun successeur)"
            lignes.append(f"  {ident} -> {details}")
        return "\n".join(lignes)

    # ------------------------------------------------------------------
    # Outil interne
    # ------------------------------------------------------------------
    def _obtenir_sommet(self, identifiant):
        try:
            return self._sommets[identifiant]
        except (KeyError, TypeError):
            # TypeError : identifiant non hachable (ex. une liste).
            raise SommetInconnuError(
                f"Le sommet '{identifiant}' n'existe pas dans le graphe."
            ) from None