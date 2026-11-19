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


class GrapheCycliqueError(GrapheError, ValueError):
    """Le graphe contient un cycle : aucun ordre topologique n'existe (partie F).

    L'attribut `cycle` contient un cycle trouvé, sous la forme d'une liste
    d'identifiants dont le premier et le dernier sont identiques
    (ex. ["A", "B", "D", "X", "A"]), pour que l'appelant puisse l'exploiter
    (affichage, mise en évidence, correction des données...).
    """

    def __init__(self, message, cycle=None):
        self.cycle = list(cycle) if cycle else []
        super().__init__(message)


# ----------------------------------------------------------------------
# Erreurs de lecture de fichier (partie B)
# ----------------------------------------------------------------------
class LigneMalFormeeError(GrapheError, ValueError):
    """Une ligne du fichier ne respecte pas le format attendu."""


class FichierGrapheError(GrapheError):
    """Classe de base des erreurs liées à la lecture d'un fichier de graphe."""


class FichierIntrouvableError(FichierGrapheError, FileNotFoundError):
    """Le fichier demandé n'existe pas."""


class FormatFichierError(FichierGrapheError):
    """Le contenu du fichier est invalide.

    Attributs utiles pour l'appelant :
    - chemin        : fichier concerné
    - numero_ligne  : numéro de la ligne fautive (None si l'erreur est globale)
    - ligne         : contenu brut de la ligne fautive
    La cause précise (poids invalide, sommet inconnu, ...) est
    disponible dans __cause__.
    """

    def __init__(self, message, chemin=None, numero_ligne=None, ligne=None):
        self.message = message
        self.chemin = chemin
        self.numero_ligne = numero_ligne
        self.ligne = ligne
        super().__init__(self._construire_message())

    def _construire_message(self):
        lieu = str(self.chemin) if self.chemin is not None else "fichier"
        if self.numero_ligne is not None:
            lieu += f", ligne {self.numero_ligne}"
        texte = f"{lieu} : {self.message}"
        if self.ligne is not None:
            texte += f" (ligne lue : {self.ligne!r})"
        return texte