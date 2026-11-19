"""Classe Sommet : un lieu du réseau."""

from .exceptions import IdentifiantInvalideError


class Sommet:
    """Un sommet identifié par une chaîne unique et non vide.

    L'identifiant est en lecture seule : il sert de clé dans les
    dictionnaires du graphe, le modifier casserait leur cohérence.
    """

    def __init__(self, identifiant):
        if not isinstance(identifiant, str):
            raise IdentifiantInvalideError(
                f"L'identifiant d'un sommet doit être une chaîne, "
                f"reçu : {type(identifiant).__name__}."
            )
        identifiant = identifiant.strip()
        if identifiant == "":
            raise IdentifiantInvalideError(
                "L'identifiant d'un sommet ne peut pas être vide."
            )
        self._identifiant = identifiant

    @property
    def identifiant(self):
        return self._identifiant

    # Deux sommets de même identifiant sont considérés comme égaux.
    def __eq__(self, autre):
        if not isinstance(autre, Sommet):
            return NotImplemented
        return self._identifiant == autre._identifiant

    def __hash__(self):
        return hash(self._identifiant)

    def __str__(self):
        return self._identifiant

    def __repr__(self):
        return f"Sommet({self._identifiant!r})"