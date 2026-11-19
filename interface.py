"""Interface graphique Tkinter de démonstration du réseau de transport.

Lancement (depuis la racine du projet) : python3 interface.py

L'interface ne contient AUCUNE logique de graphe : elle se contente
d'appeler les méthodes publiques de la classe Graphe (from_file, sommets,
arcs_en_triplets, analyser_sommet, shortest_path, shortest_path_avoiding,
trouver_cycle, topological_sort)
et d'afficher les résultats.
Les erreurs (GrapheError) sont montrées dans une boîte de dialogue.
"""

import math
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from graphe import Graphe, GrapheCycliqueError, GrapheError

# Chemins construits à partir de l'emplacement de ce fichier (aucun chemin en dur).
DOSSIER_PROJET = Path(__file__).resolve().parent
FICHIER_PAR_DEFAUT = DOSSIER_PROJET / "data" / "reseau.txt"

# Constantes d'affichage
LARGEUR, HAUTEUR = 560, 500   # taille du dessin
RAYON_SOMMET = 20             # rayon d'un cercle représentant un sommet
DECALAGE = 6                  # écart entre deux arcs opposés (A -> B et B -> A)
COULEUR_NORMALE = "#4a6fa5"
COULEUR_CHEMIN = "#d9534f"
AUCUN = "(aucun)"            # choix « pas de sommet interdit »


class InterfaceGraphe:
    """Fenêtre principale : dessin du graphe + panneau d'analyse et d'itinéraire."""

    def __init__(self, racine):
        self.racine = racine
        self.racine.title("Réseau de transport")
        self.graphe = Graphe()   # graphe vide tant qu'aucun fichier n'est chargé
        self.positions = {}      # identifiant -> (x, y) du sommet sur le dessin
        self._construire_fenetre()
        self.charger(FICHIER_PAR_DEFAUT)

    # ------------------------------------------------------------------
    # Construction des widgets
    # ------------------------------------------------------------------
    def _construire_fenetre(self):
        # Barre du haut : bouton d'ouverture et nom du fichier chargé
        haut = ttk.Frame(self.racine, padding=6)
        haut.pack(fill="x")
        ttk.Button(haut, text="Ouvrir un fichier…", command=self.ouvrir_fichier).pack(side="left")
        self.etiquette_fichier = ttk.Label(haut, text="Aucun fichier chargé")
        self.etiquette_fichier.pack(side="left", padx=10)

        # Zone de dessin à gauche ; un clic sur un sommet l'analyse
        self.canevas = tk.Canvas(self.racine, width=LARGEUR, height=HAUTEUR, bg="white")
        self.canevas.pack(side="left", padx=6, pady=6)
        self.canevas.tag_bind("sommet", "<Button-1>", self._clic_sommet)

        # Panneau de droite
        panneau = ttk.Frame(self.racine, padding=6)
        panneau.pack(side="left", fill="both", expand=True)

        # Analyse d'un sommet (partie C)
        cadre_analyse = ttk.LabelFrame(panneau, text="Analyse d'un sommet", padding=6)
        cadre_analyse.pack(fill="x")
        self.choix_sommet = ttk.Combobox(cadre_analyse, state="readonly", width=12)
        self.choix_sommet.pack(side="left")
        ttk.Button(cadre_analyse, text="Analyser", command=self.analyser).pack(side="left", padx=6)

        # Recherche d'itinéraire (parties D et E)
        cadre_chemin = ttk.LabelFrame(panneau, text="Plus court chemin", padding=6)
        cadre_chemin.pack(fill="x", pady=8)
        ttk.Label(cadre_chemin, text="Départ :").grid(row=0, column=0, sticky="w")
        self.choix_depart = ttk.Combobox(cadre_chemin, state="readonly", width=12)
        self.choix_depart.grid(row=0, column=1, pady=2)
        ttk.Label(cadre_chemin, text="Arrivée :").grid(row=1, column=0, sticky="w")
        self.choix_arrivee = ttk.Combobox(cadre_chemin, state="readonly", width=12)
        self.choix_arrivee.grid(row=1, column=1, pady=2)
        ttk.Label(cadre_chemin, text="Interdit :").grid(row=2, column=0, sticky="w")
        self.choix_interdit = ttk.Combobox(cadre_chemin, state="readonly", width=12)
        self.choix_interdit.grid(row=2, column=1, pady=2)
        ttk.Button(cadre_chemin, text="Calculer", command=self.calculer_chemin).grid(
            row=3, column=0, columnspan=2, pady=4)

        # Structure du graphe (partie F) : cycle ou ordre topologique
        cadre_structure = ttk.LabelFrame(panneau, text="Structure du graphe", padding=6)
        cadre_structure.pack(fill="x", pady=(0, 8))
        ttk.Button(cadre_structure, text="Cycle / ordre topologique",
                   command=self.analyser_structure).pack()

        # Zone de texte où s'affichent les résultats
        self.resultat = tk.Text(panneau, width=34, height=14, state="disabled", wrap="word")
        self.resultat.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Chargement d'un fichier
    # ------------------------------------------------------------------
    def ouvrir_fichier(self):
        """Demande un fichier à l'utilisateur puis le charge."""
        chemin = filedialog.askopenfilename(
            initialdir=DOSSIER_PROJET / "data",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*")],
        )
        if chemin:  # chaîne vide si l'utilisateur annule
            self.charger(Path(chemin))

    def charger(self, chemin):
        """Charge le graphe ; en cas d'erreur, l'ancien graphe est conservé."""
        try:
            self.graphe = Graphe.from_file(chemin)
        except GrapheError as erreur:
            messagebox.showerror("Erreur de chargement", str(erreur))
            return
        self.etiquette_fichier.config(text=f"{chemin.name} : {self.graphe!r}")

        # Les listes déroulantes proposent les sommets du nouveau graphe
        sommets = self.graphe.sommets()
        for liste in (self.choix_sommet, self.choix_depart, self.choix_arrivee):
            liste["values"] = sommets
            liste.set(sommets[0] if sommets else "")
        self.choix_interdit["values"] = [AUCUN] + sommets
        self.choix_interdit.set(AUCUN)
        self.afficher("Graphe chargé.\nCliquez sur un sommet pour l'analyser.")
        self.dessiner()

    # ------------------------------------------------------------------
    # Dessin du graphe
    # ------------------------------------------------------------------
    def dessiner(self, chemin=()):
        """Dessine le graphe ; les sommets et arcs de `chemin` sont mis en rouge."""
        self.canevas.delete("all")
        sommets = self.graphe.sommets()

        # Sommets placés régulièrement sur un cercle (angle de 2π/n entre deux sommets)
        cx, cy = LARGEUR / 2, HAUTEUR / 2
        rayon = min(cx, cy) - 2 * RAYON_SOMMET
        self.positions = {}
        for i, ident in enumerate(sommets):
            angle = 2 * math.pi * i / len(sommets) - math.pi / 2  # premier sommet en haut
            self.positions[ident] = (cx + rayon * math.cos(angle), cy + rayon * math.sin(angle))

        # Arcs du chemin sous forme de couples (origine, destination)
        arcs_chemin = set(zip(chemin, chemin[1:]))
        for origine, destination, poids in self.graphe.arcs_en_triplets():
            couleur = COULEUR_CHEMIN if (origine, destination) in arcs_chemin else "gray"
            self._dessiner_arc(origine, destination, poids, couleur)

        for ident, (x, y) in self.positions.items():
            couleur = COULEUR_CHEMIN if ident in chemin else COULEUR_NORMALE
            r = RAYON_SOMMET
            # Le tag « sommet » rend le cercle cliquable ; le tag ident permet de le retrouver
            self.canevas.create_oval(x - r, y - r, x + r, y + r, fill=couleur,
                                     outline="black", tags=("sommet", ident))
            self.canevas.create_text(x, y, text=ident, fill="white",
                                     font=("Helvetica", 12, "bold"), tags=("sommet", ident))

    def _dessiner_arc(self, origine, destination, poids, couleur):
        """Flèche de `origine` vers `destination`, arrêtée au bord des cercles."""
        x1, y1 = self.positions[origine]
        x2, y2 = self.positions[destination]
        longueur = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / longueur, (y2 - y1) / longueur  # vecteur unitaire
        # Léger décalage perpendiculaire : A -> B et B -> A ne se superposent pas
        px, py = -uy * DECALAGE, ux * DECALAGE
        debut = (x1 + ux * RAYON_SOMMET + px, y1 + uy * RAYON_SOMMET + py)
        fin = (x2 - ux * RAYON_SOMMET + px, y2 - uy * RAYON_SOMMET + py)
        largeur = 3 if couleur == COULEUR_CHEMIN else 1.5
        self.canevas.create_line(*debut, *fin, arrow=tk.LAST, fill=couleur, width=largeur)
        # Poids écrit au milieu de l'arc, un peu à côté du trait
        mx, my = (debut[0] + fin[0]) / 2 + 2 * px, (debut[1] + fin[1]) / 2 + 2 * py
        self.canevas.create_text(mx, my, text=f"{poids:g}", fill=couleur)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _clic_sommet(self, evenement):
        """Clic sur le canevas : retrouve le sommet cliqué grâce à ses tags."""
        element = self.canevas.find_withtag("current")
        tags = self.canevas.gettags(element)
        ident = next(tag for tag in tags if tag not in ("sommet", "current"))
        self.choix_sommet.set(ident)
        self.analyser()

    def analyser(self):
        """Affiche les degrés, prédécesseurs et successeurs du sommet choisi."""
        try:
            infos = self.graphe.analyser_sommet(self.choix_sommet.get())
        except GrapheError as erreur:
            messagebox.showerror("Erreur", str(erreur))
            return
        self.afficher(
            f"Sommet {infos['sommet']}\n"
            f"  degré entrant : {infos['degre_entrant']}\n"
            f"  degré sortant : {infos['degre_sortant']}\n"
            f"  degré total   : {infos['degre_total']}\n"
            f"  prédécesseurs : {', '.join(infos['predecesseurs']) or 'aucun'}\n"
            f"  successeurs   : {', '.join(infos['successeurs']) or 'aucun'}"
        )

    def calculer_chemin(self):
        """Appelle shortest_path (ou shortest_path_avoiding si un sommet est
        interdit) et met le chemin trouvé en évidence sur le dessin."""
        depart, arrivee = self.choix_depart.get(), self.choix_arrivee.get()
        interdit = self.choix_interdit.get()
        try:
            if interdit == AUCUN:
                chemin, cout = self.graphe.shortest_path(depart, arrivee)
            else:
                chemin, cout = self.graphe.shortest_path_avoiding(depart, arrivee, interdit)
        except GrapheError as erreur:
            messagebox.showerror("Erreur", str(erreur))
            return
        sans = "" if interdit == AUCUN else f" sans passer par {interdit}"
        if chemin:
            self.afficher(f"Chemin de {depart} à {arrivee}{sans} :\n"
                          f"  {' -> '.join(chemin)}\nCoût total : {cout:g}")
        else:  # ([], inf) quand aucun chemin n'existe
            self.afficher(f"Aucun chemin de {depart} à {arrivee}{sans}.")
        self.dessiner(chemin)

    def analyser_structure(self):
        """Affiche un ordre topologique, ou le cycle qui l'empêche (mis en rouge)."""
        try:
            ordre = self.graphe.topological_sort()
        except GrapheCycliqueError as erreur:
            self.afficher("Le graphe contient un cycle :\n"
                          f"  {' -> '.join(erreur.cycle)}\n"
                          "Aucun ordre topologique n'existe.")
            self.dessiner(erreur.cycle)  # le cycle est fermé : ses arcs sont colorés
            return
        if ordre:
            self.afficher("Le graphe est acyclique.\nOrdre topologique :\n"
                          f"  {', '.join(ordre)}")
        else:
            self.afficher("Le graphe est vide.")
        self.dessiner()

    def afficher(self, texte):
        """Remplace le contenu de la zone de résultats (en lecture seule)."""
        self.resultat.config(state="normal")
        self.resultat.delete("1.0", "end")
        self.resultat.insert("1.0", texte)
        self.resultat.config(state="disabled")


if __name__ == "__main__":
    fenetre = tk.Tk()
    InterfaceGraphe(fenetre)
    fenetre.mainloop()