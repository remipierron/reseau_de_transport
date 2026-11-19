"""Exceptions propres au module graphe.

Toutes héritent de GrapheError : un appelant peut donc intercepter
une erreur précise (ex. SommetInconnuError) ou toutes les erreurs
du graphe d'un coup avec `except GrapheError`.
"""


class GrapheError(Exception):
    """Classe de base de toutes les erreurs liées au graphe."""


class IdentifiantInvalideError(GrapheError, ValueError):
    """L'identifiant d'un sommet est vide ou n'est pas une chaîne."""


class SommetExistantError(GrapheError):
    """On tente d'ajouter un sommet déjà présent dans le graphe."""


class SommetInconnuError(GrapheError, KeyError):
    """Un sommet référencé n'existe pas dans le graphe."""

    def __str__(self):
        # KeyError entoure le message de guillemets : on garde un affichage lisible.
        return str(self.args[0]) if self.args else ""


class ArcExistantError(GrapheError):
    """Un arc de même origine et même destination existe déjà."""


class PoidsInvalideError(GrapheError, ValueError):
    """Le poids d'un arc n'est pas un nombre positif ou nul."""