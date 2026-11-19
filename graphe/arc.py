"""Classe Arc : une liaison orientée et pondérée entre deux sommets."""

import math

from .exceptions import PoidsInvalideError


def valider_poids(poids):
    """Vérifie qu'un poids est un nombre réel positif ou nul et le retourne.

    Les booléens sont refusés (en Python, True est un int qui vaut 1),
    ainsi que NaN et l'infini, qui fausseraient les calculs de chemin.
    """
    if isinstance(poids, bool) or not isinstance(poids, (int, float)):
        raise PoidsInvalideError(
            f"Le poids doit être un nombre, reçu : {poids!r}."
        )
    if math.isnan(poids) or math.isinf(poids):
        raise PoidsInvalideError(f"Le poids doit être un nombre fini, reçu : {poids!r}.")
    if poids < 0:
        raise PoidsInvalideError(
            f"Le poids doit être positif ou nul, reçu : {poids!r}."
        )
    return poids


class Arc:
    """Arc orienté origine -> destination, de poids positif ou nul.

    L'arc ne vérifie pas que ses extrémités existent : c'est le rôle
    du Graphe, seul à connaître la liste des sommets.
    """

    def __init__(self, origine, destination, poids):
        self._origine = origine          # objet Sommet
        self._destination = destination  # objet Sommet
        self._poids = valider_poids(poids)

    @property
    def origine(self):
        return self._origine

    @property
    def destination(self):
        return self._destination

    @property
    def poids(self):
        return self._poids

    def en_triplet(self):
        """Retourne l'arc sous la forme (origine, destination, poids) avec les identifiants."""
        return (self._origine.identifiant, self._destination.identifiant, self._poids)

    # Égalité complète (origine, destination ET poids) : utile pour l'intersection (partie E).
    def __eq__(self, autre):
        if not isinstance(autre, Arc):
            return NotImplemented
        return self.en_triplet() == autre.en_triplet()

    def __hash__(self):
        return hash(self.en_triplet())

    def __str__(self):
        return f"{self._origine} -> {self._destination} ({self._poids})"

    def __repr__(self):
        return f"Arc({self._origine.identifiant!r}, {self._destination.identifiant!r}, {self._poids!r})"