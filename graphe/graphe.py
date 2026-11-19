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
- self._entrants : dict  identifiant -> dict(identifiant_origine -> Arc)
    Liste d'adjacence inverse (ajoutée pour la partie C). Elle donne
    les prédécesseurs et le degré entrant en O(1), au lieu de parcourir
    tous les arcs du graphe. Coût : chaque arc est référencé deux fois
    (mais l'objet Arc n'existe qu'une fois en mémoire).

Aucune méthode de cette classe n'appelle input() ni print() :
elles retournent des valeurs ou lèvent des exceptions.
"""

import heapq
import math

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
        self._entrants = {}

    @classmethod
    def from_file(cls, chemin):
        """Construit un graphe à partir d'un fichier texte (voir graphe/lecture.py).

        Le fichier est rejeté en entier à la première erreur.
        """
        # Import local : lecture.py importe déjà Graphe, un import en haut
        # de ce fichier créerait un import circulaire.
        from .lecture import lire_graphe
        return lire_graphe(chemin)

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
        self._entrants[sommet.identifiant] = {}
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
        self._entrants[s_destination.identifiant][s_origine.identifiant] = arc
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

    # ------------------------------------------------------------------
    # Analyse d'un sommet (partie C)
    # Toutes ces méthodes lèvent SommetInconnuError si le sommet n'existe pas.
    # Elles retournent de nouvelles listes : les modifier ne modifie pas le graphe.
    # ------------------------------------------------------------------
    def successeurs(self, identifiant):
        """Identifiants des sommets atteints par un arc partant de `identifiant`."""
        self._obtenir_sommet(identifiant)
        return list(self._adjacence[identifiant])

    def predecesseurs(self, identifiant):
        """Identifiants des sommets ayant un arc vers `identifiant`."""
        self._obtenir_sommet(identifiant)
        return list(self._entrants[identifiant])

    def degre_sortant(self, identifiant):
        self._obtenir_sommet(identifiant)
        return len(self._adjacence[identifiant])

    def degre_entrant(self, identifiant):
        self._obtenir_sommet(identifiant)
        return len(self._entrants[identifiant])

    def degre_total(self, identifiant):
        return self.degre_entrant(identifiant) + self.degre_sortant(identifiant)

    def est_isole(self, identifiant):
        return self.degre_total(identifiant) == 0

    def analyser_sommet(self, identifiant):
        """Regroupe toutes les informations d'un sommet dans un dictionnaire."""
        return {
            "sommet": identifiant,
            "degre_entrant": self.degre_entrant(identifiant),
            "degre_sortant": self.degre_sortant(identifiant),
            "degre_total": self.degre_total(identifiant),
            "predecesseurs": self.predecesseurs(identifiant),
            "successeurs": self.successeurs(identifiant),
        }

    # ------------------------------------------------------------------
    # Recherche d'itinéraire (partie D)
    # ------------------------------------------------------------------
    def shortest_path(self, depart, arrivee):
        """Plus court chemin de `depart` à `arrivee` (algorithme de Dijkstra).

        Retourne un tuple (chemin, cout) :
        - chemin : liste des identifiants, de `depart` à `arrivee` inclus ;
        - cout   : somme des poids des arcs empruntés.

        Cas particuliers :
        - départ = arrivée : (["A"], 0), chemin trivial de coût nul ;
        - aucun chemin     : ([], math.inf). Ce n'est pas une erreur mais un
          résultat normal (ex. vers le sommet isolé H), d'où l'absence
          d'exception. Le tuple se déballe toujours de la même façon
          (`chemin, cout = g.shortest_path(...)`) et `if not chemin` suffit
          pour tester l'absence de chemin.

        Lève SommetInconnuError si `depart` ou `arrivee` n'existe pas.
        """
        return self._dijkstra(depart, arrivee)

    # ------------------------------------------------------------------
    # Contraintes et comparaison (partie E)
    # ------------------------------------------------------------------
    def shortest_path_avoiding(self, depart, arrivee, interdit):
        """Plus court chemin de `depart` à `arrivee` sans passer par `interdit`.

        Retourne (chemin, cout), comme shortest_path.

        Comportement choisi :
        - `interdit` est le départ ou l'arrivée : ([], math.inf). Un chemin
          contient toujours ses deux extrémités ; aucun chemin ne peut donc
          éviter ce sommet. C'est cohérent avec shortest_path : « aucun
          itinéraire possible » est un résultat normal, pas une exception.
          Cela vaut aussi quand départ = arrivée = interdit.
        - `interdit` inconnu : SommetInconnuError (sans doute une faute de
          frappe, qu'il vaut mieux signaler que d'ignorer).
        - départ ou arrivée inconnu : SommetInconnuError, comme shortest_path.

        Le graphe n'est pas modifié : le sommet interdit est simplement
        ignoré pendant le parcours de Dijkstra.
        """
        self._obtenir_sommet(depart)
        self._obtenir_sommet(arrivee)
        self._obtenir_sommet(interdit)
        if interdit in (depart, arrivee):
            return [], math.inf
        return self._dijkstra(depart, arrivee, exclus=frozenset([interdit]))

    def intersection(self, autre_graphe):
        """Nouveau graphe formé des sommets communs et des arcs communs.

        - Sommet commun : identifiant présent dans les deux graphes.
        - Arc commun : même origine, même destination ET même poids dans
          les deux graphes (les deux extrémités sont alors forcément communes).
        - L'ordre des sommets et des arcs suit celui de `self`.
        - Les deux graphes d'origine ne sont pas modifiés : le résultat est
          construit avec ses propres objets Sommet et Arc.

        Lève TypeError si `autre_graphe` n'est pas un Graphe.
        Complexité : O(|V| + |E|) grâce aux dictionnaires (tests en O(1)).
        """
        if not isinstance(autre_graphe, Graphe):
            raise TypeError(
                f"intersection attend un Graphe, reçu : {type(autre_graphe).__name__}."
            )
        resultat = Graphe()
        for identifiant in self._sommets:
            if autre_graphe.contient_sommet(identifiant):
                resultat.ajouter_sommet(identifiant)

        for origine, destination, poids in self.arcs_en_triplets():
            if (autre_graphe.contient_arc(origine, destination)
                    and autre_graphe.get_arc(origine, destination).poids == poids):
                resultat.ajouter_arc(origine, destination, poids)
        return resultat

    def _dijkstra(self, depart, arrivee, exclus=frozenset()):
        """Dijkstra avec file de priorité (heapq), arrêt dès que `arrivee` est fixée.

        `exclus` : sommets que le chemin n'a pas le droit de traverser
        (utilisé par shortest_path_avoiding, partie E). Le départ et l'arrivée
        ne sont jamais filtrés ici : c'est l'appelant qui décide du
        comportement si l'un d'eux est interdit.

        Validité : les poids sont >= 0 (garanti par valider_poids). Quand un
        sommet sort de la file avec le plus petit coût provisoire, aucun
        détour ne peut donc plus le rendre moins cher : son coût est définitif.

        Complexité : O((|V| + |E|) log |V|).
        """
        self._obtenir_sommet(depart)
        self._obtenir_sommet(arrivee)

        couts = {depart: 0}        # meilleur coût connu depuis le départ
        precedent = {depart: None}  # pour reconstruire le chemin
        definitifs = set()          # sommets dont le coût est définitif
        # Entrées (cout, ordre, sommet) : `ordre` départage les égalités de coût
        # (résultat déterministe) et évite de comparer des identifiants.
        file = [(0, 0, depart)]
        ordre = 1

        while file:
            cout, _, sommet = heapq.heappop(file)
            if sommet in definitifs:
                continue  # entrée périmée : un meilleur coût a déjà été traité
            definitifs.add(sommet)
            if sommet == arrivee:
                return self._reconstruire_chemin(precedent, arrivee), cout

            for voisin, arc in self._adjacence[sommet].items():
                if voisin in definitifs or (voisin in exclus and voisin != arrivee):
                    continue
                nouveau = cout + arc.poids
                if voisin not in couts or nouveau < couts[voisin]:
                    couts[voisin] = nouveau
                    precedent[voisin] = sommet
                    heapq.heappush(file, (nouveau, ordre, voisin))
                    ordre += 1

        return [], math.inf  # file vide sans atteindre l'arrivée

    @staticmethod
    def _reconstruire_chemin(precedent, arrivee):
        """Remonte les prédécesseurs depuis l'arrivée jusqu'au départ."""
        chemin = []
        sommet = arrivee
        while sommet is not None:
            chemin.append(sommet)
            sommet = precedent[sommet]
        chemin.reverse()
        return chemin

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