"""Lecture d'un graphe depuis un fichier texte (partie B).

Format attendu
--------------
    Sommets: A, B, C, D
    A;B;4
    C;D;2.5

- La première ligne utile commence par « Sommets: » et liste les
  identifiants séparés par des virgules.
- Chaque ligne suivante décrit un arc : origine;destination;poids.
- Les lignes vides et les lignes commençant par « # » sont ignorées.
- Les espaces autour des identifiants et des poids sont tolérés.

Politique d'erreur
------------------
Le fichier est REJETÉ EN ENTIER à la première erreur : la fonction lève
une exception et ne retourne aucun graphe. Un réseau chargé à moitié
pourrait en effet produire de faux itinéraires sans que l'utilisateur
s'en rende compte. Le message d'erreur indique le numéro et le contenu
de la ligne fautive pour qu'on puisse corriger le fichier.
"""

from pathlib import Path

from .exceptions import (
    FichierGrapheError,
    FichierIntrouvableError,
    FormatFichierError,
    GrapheError,
    LigneMalFormeeError,
    PoidsInvalideError,
)
from .graphe import Graphe


def lire_graphe(chemin):
    """Construit et retourne un Graphe à partir du fichier `chemin`.

    `chemin` peut être une chaîne ou un objet pathlib.Path.

    Lève :
    - FichierIntrouvableError si le fichier n'existe pas ;
    - FichierGrapheError si le fichier ne peut pas être ouvert (dossier, droits) ;
    - FormatFichierError si le contenu est invalide (avec numéro de ligne).
    """
    chemin = Path(chemin)
    lignes = _lire_lignes(chemin)

    graphe = Graphe()
    entete_lue = False

    for numero, brute in enumerate(lignes, start=1):
        ligne = brute.strip()
        if ligne == "" or ligne.startswith("#"):
            continue
        try:
            if not entete_lue:
                _lire_entete(graphe, ligne)
                entete_lue = True
            else:
                _lire_arc(graphe, ligne)
        except GrapheError as erreur:
            # On ajoute le contexte (fichier, ligne) et on garde la cause précise.
            raise FormatFichierError(str(erreur), chemin, numero, brute) from erreur

    if not entete_lue:
        raise FormatFichierError(
            "le fichier est vide : la ligne 'Sommets:' est absente.", chemin
        )
    return graphe


# ----------------------------------------------------------------------
# Fonctions internes
# ----------------------------------------------------------------------
def _lire_lignes(chemin):
    """Retourne la liste des lignes du fichier, ou lève une erreur adaptée."""
    try:
        with chemin.open(encoding="utf-8") as fichier:
            return fichier.read().splitlines()
    except FileNotFoundError:
        raise FichierIntrouvableError(
            f"Le fichier '{chemin}' est introuvable."
        ) from None
    except UnicodeDecodeError:
        raise FormatFichierError(
            "le fichier n'est pas un fichier texte UTF-8 valide.", chemin
        ) from None
    except OSError as erreur:
        # Dossier à la place d'un fichier, droits insuffisants, etc.
        raise FichierGrapheError(
            f"Impossible de lire '{chemin}' : {erreur.strerror}."
        ) from erreur


def _lire_entete(graphe, ligne):
    """Traite la ligne « Sommets: A, B, C » et ajoute les sommets au graphe."""
    cle, separateur, reste = ligne.partition(":")
    if separateur == "" or cle.strip().lower() != "sommets":
        raise LigneMalFormeeError(
            "la première ligne doit commencer par 'Sommets:'."
        )
    if reste.strip() == "":
        return  # graphe sans sommet : autorisé
    for identifiant in reste.split(","):
        # Identifiant vide -> IdentifiantInvalideError ; doublon -> SommetExistantError
        graphe.ajouter_sommet(identifiant)


def _lire_arc(graphe, ligne):
    """Traite une ligne « origine;destination;poids » et ajoute l'arc au graphe."""
    morceaux = [morceau.strip() for morceau in ligne.split(";")]
    if len(morceaux) != 3:
        raise LigneMalFormeeError(
            f"un arc doit avoir 3 champs 'origine;destination;poids', "
            f"{len(morceaux)} trouvé(s)."
        )
    origine, destination, texte_poids = morceaux
    if origine == "" or destination == "":
        raise LigneMalFormeeError(
            "l'origine et la destination d'un arc ne peuvent pas être vides."
        )
    poids = _convertir_poids(texte_poids)
    # Sommet inconnu, poids négatif ou arc en double : erreurs levées par Graphe.
    graphe.ajouter_arc(origine, destination, poids)


def _convertir_poids(texte):
    """Convertit le texte en int si possible, sinon en float."""
    try:
        return int(texte)
    except ValueError:
        pass
    try:
        return float(texte)
    except ValueError:
        raise PoidsInvalideError(
            f"le poids '{texte}' n'est pas un nombre."
        ) from None