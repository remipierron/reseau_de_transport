"""Démonstration en ligne de commande des principales fonctionnalités du projet.

Le script charge les réseaux de data/, puis enchaîne des exemples pour
chaque partie du sujet : chargement, analyse des sommets, plus court chemin,
sommet interdit, intersection, cycles et ordre topologique, robustesse de la
lecture. Il se déroule tout seul (aucune saisie) et affiche chaque appel
suivi de son résultat.

Comme interface.py, il ne contient AUCUNE logique de graphe : il n'appelle
que les méthodes publiques de la classe Graphe et met en forme les résultats.
Seules les erreurs prévues (GrapheError et ses sous-classes) sont interceptées.

Lancement (depuis n'importe quel dossier) :
    python3 demo.py
Sortie enregistrée dans exemples_execution.txt :
    python3 demo.py > exemples_execution.txt
"""

import tempfile
from pathlib import Path

from graphe import FormatFichierError, Graphe, GrapheCycliqueError, GrapheError

# Chemins construits à partir de l'emplacement de ce fichier (aucun chemin en dur).
DOSSIER_PROJET = Path(__file__).resolve().parent
FICHIER_RESEAU = DOSSIER_PROJET / "data" / "reseau.txt"
FICHIER_RESEAU2 = DOSSIER_PROJET / "data" / "reseau2.txt"

# Fichiers invalides pour la section 7 : (description, nom du fichier, contenu).
FICHIERS_INVALIDES = [
    ("Ligne mal formée", "mal_formee.txt", "Sommets: A, B\nA;B\n"),
    ("Poids non numérique", "poids_texte.txt", "Sommets: A, B\nA;B;quatre\n"),
    ("Poids négatif", "poids_negatif.txt", "Sommets: A, B\nA;B;-3\n"),
    ("Arc vers un sommet inconnu", "sommet_inconnu.txt", "Sommets: A, B\nA;Z;2\n"),
]


# ----------------------------------------------------------------------
# Mise en forme
# ----------------------------------------------------------------------
def titre(numero, texte):
    """Affiche le titre d'une section."""
    ligne = f"{numero}. {texte}"
    print()
    print(ligne)
    print("=" * len(ligne))


def formater_liste(identifiants):
    """« A, B, C », ou « (aucun) » pour une liste vide."""
    return ", ".join(identifiants) if identifiants else "(aucun)"


def formater_chemin(resultat):
    """Met en forme le tuple (chemin, cout) renvoyé par shortest_path*."""
    chemin, cout = resultat
    if not chemin:
        return "aucun chemin"
    return f"{' → '.join(chemin)} (coût {cout})"


def afficher_erreur(erreur, dossier=None, alias=None):
    """Affiche le type et le message d'une GrapheError interceptée.

    Si `dossier` est donné, son chemin absolu est remplacé par `alias` dans
    le message : la sortie ne dépend pas de la machine ni du dossier temporaire.
    """
    message = str(erreur)
    if dossier is not None:
        message = message.replace(str(dossier), alias)
    print(f"    {type(erreur).__name__} : {message}")
    if isinstance(erreur, FormatFichierError) and erreur.numero_ligne is not None:
        cause = type(erreur.__cause__).__name__ if erreur.__cause__ else "-"
        print(f"    (ligne {erreur.numero_ligne}, cause : {cause})")


# ----------------------------------------------------------------------
# Sections de la démonstration
# ----------------------------------------------------------------------
def demo_chargement():
    """Section 1 : chargement de data/reseau.txt."""
    titre(1, "Chargement du réseau (data/reseau.txt)")
    g = Graphe.from_file(FICHIER_RESEAU)
    print(f"Graphe.from_file(\"data/reseau.txt\") -> {g.nombre_sommets()} sommets, "
          f"{g.nombre_arcs()} arcs")
    print()
    print(g)
    return g


def demo_analyse(g):
    """Section 2 : analyse de quelques sommets (partie C)."""
    titre(2, "Analyse des sommets (analyser_sommet)")
    for identifiant, remarque in (("H", " (sommet isolé)"), ("B", ""), ("D", "")):
        infos = g.analyser_sommet(identifiant)
        print(f"analyser_sommet(\"{identifiant}\"){remarque}")
        print(f"    degré entrant : {infos['degre_entrant']}, "
              f"degré sortant : {infos['degre_sortant']}, "
              f"degré total : {infos['degre_total']}")
        print(f"    prédécesseurs : {formater_liste(infos['predecesseurs'])}")
        print(f"    successeurs   : {formater_liste(infos['successeurs'])}")


def demo_plus_court_chemin(g):
    """Section 3 : plus court chemin (partie D)."""
    titre(3, "Plus court chemin (shortest_path)")
    cas = [
        ("A", "G", ""),
        ("A", "H", "H est isolé"),
        ("G", "A", "sens inverse"),
        ("A", "A", "départ = arrivée"),
    ]
    for depart, arrivee, remarque in cas:
        resultat = formater_chemin(g.shortest_path(depart, arrivee))
        suffixe = f"   [{remarque}]" if remarque else ""
        print(f"shortest_path(\"{depart}\", \"{arrivee}\") -> {resultat}{suffixe}")


def demo_sommet_interdit(g):
    """Section 4 : plus court chemin avec un sommet interdit (partie E)."""
    titre(4, "Sommet interdit (shortest_path_avoiding)")
    for interdit, remarque in (("C", ""), ("D", ""), ("F", ""),
                               ("G", "interdit = arrivée : impossible")):
        resultat = formater_chemin(g.shortest_path_avoiding("A", "G", interdit))
        suffixe = f"   [{remarque}]" if remarque else ""
        print(f"shortest_path_avoiding(\"A\", \"G\", \"{interdit}\") -> {resultat}{suffixe}")


def demo_intersection(g):
    """Section 5 : intersection de deux graphes (partie E)."""
    titre(5, "Intersection (reseau.txt ∩ reseau2.txt)")
    g2 = Graphe.from_file(FICHIER_RESEAU2)
    inter = g.intersection(g2)
    print("g.intersection(g2)")
    print(f"    sommets : {formater_liste(inter.sommets())}")
    arcs = [f"{o}→{d} ({p})" for o, d, p in inter.arcs_en_triplets()]
    print(f"    arcs    : {formater_liste(arcs)}")
    print("Graphes d'origine inchangés :")
    print(f"    g  : {g.nombre_sommets()} sommets, {g.nombre_arcs()} arcs")
    print(f"    g2 : {g2.nombre_sommets()} sommets, {g2.nombre_arcs()} arcs")
    return g2


def demo_cycles(g, g2):
    """Section 6 : détection de cycle et ordre topologique (partie F)."""
    titre(6, "Cycles et ordre topologique")
    print("Sur reseau.txt :")
    print(f"    has_cycle() -> {g.has_cycle()}")
    print(f"    topological_sort() -> {formater_liste(g.topological_sort())}")
    print("Sur reseau2.txt :")
    print(f"    has_cycle() -> {g2.has_cycle()}")
    print(f"    trouver_cycle() -> {' → '.join(g2.trouver_cycle())}")
    try:
        g2.topological_sort()
    except GrapheCycliqueError as erreur:
        print("    topological_sort() -> exception interceptée :")
        afficher_erreur(erreur)


def demo_robustesse():
    """Section 7 : erreurs de lecture de fichier (partie B)."""
    titre(7, "Robustesse de la lecture")
    print("Fichier inexistant :")
    print("    Graphe.from_file(\"data/inexistant.txt\")")
    try:
        Graphe.from_file(DOSSIER_PROJET / "data" / "inexistant.txt")
    except GrapheError as erreur:
        afficher_erreur(erreur, DOSSIER_PROJET, "<projet>")

    # Dossier temporaire : data/ reste propre, tout est supprimé à la fin.
    with tempfile.TemporaryDirectory() as dossier:
        for description, nom, contenu in FICHIERS_INVALIDES:
            chemin = Path(dossier) / nom
            chemin.write_text(contenu, encoding="utf-8")
            print(f"{description} :")
            print(f"    contenu : {contenu!r}")
            try:
                Graphe.from_file(chemin)
            except GrapheError as erreur:
                afficher_erreur(erreur, dossier, "<dossier temporaire>")
            else:
                print("    (aucune erreur : comportement inattendu)")


def main():
    print("Démonstration : réseau de transport (graphe orienté pondéré)")
    g = demo_chargement()
    demo_analyse(g)
    demo_plus_court_chemin(g)
    demo_sommet_interdit(g)
    g2 = demo_intersection(g)
    demo_cycles(g, g2)
    demo_robustesse()


if __name__ == "__main__":
    main()
