# Projet Python : concevoir et analyser un réseau de transport

Projet individuel noté (POO, théorie des graphes, fichiers, algorithmique, tests).
Un réseau de lieux est modélisé par un **graphe orienté pondéré** G = (V, E) ; l'application
permet de le construire, de le charger depuis un fichier, de l'analyser et de chercher des itinéraires.
Le sujet complet est dans [`sujet/projet.md`](sujet/projet.md).

## Environnement

- **Python** : 3.15 (testé ; tout Python ≥ 3.7 convient, l'ordre d'insertion des `dict` étant utilisé).
- **Installation** : aucune. Seule la bibliothèque standard est utilisée (aucune bibliothèque de graphes).
- **Lancer les tests** (depuis la racine du projet) :

```bash
python3 -m unittest
```

- **Lancer le programme** : le point d'entrée (démonstration) sera ajouté avec les parties suivantes.

## Structure du projet

```
graphe/             paquet principal
  sommet.py         classe Sommet (identifiant textuel unique, non vide)
  arc.py            classe Arc (origine, destination, poids >= 0)
  graphe.py         classe Graphe (sommets + liste d'adjacence)
  exceptions.py     hiérarchie d'exceptions personnalisées
data/reseau.txt     réseau du sujet (8 sommets, 11 arcs, H isolé)
tests/              tests unittest
documentation/      notes de travail
sujet/              énoncé
```

## Avancement

| Partie | Contenu | Points | État |
|---|---|---|---|
| A | Modélisation orientée objet | 3 | ✅ Terminée |
| B | Lecture de fichier (`from_file`) et robustesse | 2 | ⏳ À faire (le fichier `reseau.txt` est déjà créé) |
| C | Analyse : degrés, prédécesseurs, successeurs | 2 | ⏳ À faire |
| D | Plus court chemin (`shortest_path`, Dijkstra) | 4 | ⏳ À faire |
| E | Sommet interdit et intersection de graphes | 3 | ⏳ À faire |
| F | Bonus : détection de cycle / tri topologique | +2 | ⏳ Optionnel, à faire |
| Tests | 8 tests minimum | – | 🔶 17 tests écrits pour la partie A ; ceux des parties B à E restent à écrire |
| Livrables | Rapport PDF (2 à 4 pages), exemples d'exécution, second graphe de test | – | ⏳ À faire |

### Partie A (réalisée)

- **Classes** : `Graphe` (gère sommets et arcs), `Sommet` et `Arc` (objets valeurs),
  plus des exceptions dérivées de `GrapheError` : `IdentifiantInvalideError`,
  `SommetExistantError`, `SommetInconnuError`, `ArcExistantError`, `PoidsInvalideError`.
- **Méthodes** : `ajouter_sommet`, `ajouter_arc`, `sommets`, `arcs`, `arcs_en_triplets`,
  `get_sommet`, `get_arc`, `contient_sommet`, `contient_arc`, `nombre_sommets`, `nombre_arcs`,
  `len(g)`, `"A" in g`, `repr` et `str` (affichage lisible, un sommet par ligne avec ses successeurs).
- **Règles de gestion appliquées** :
  - identifiant de sommet textuel, non vide et unique ;
  - poids numérique et ≥ 0 (nécessaire pour Dijkstra) ;
  - extrémités d'un arc déjà présentes dans le graphe ;
  - arcs multiples interdits : le doublon se juge sur le couple (origine, destination), quel que soit le poids ;
  - `A → B` n'implique pas `B → A` ;
  - un sommet isolé est valide.
- **Séparation traitements / affichage** : aucune méthode n'appelle `input()` ni `print()` ;
  elles retournent des valeurs ou lèvent des exceptions.

### Structures de données choisies

- `_sommets` : `dict` identifiant → `Sommet`. Test de présence et détection des doublons en O(1),
  ordre d'insertion conservé (affichage stable).
- `_adjacence` : `dict` identifiant → `dict` (destination → `Arc`). Liste d'adjacence : savoir si
  l'arc A → B existe est en O(1) et l'énumération des successeurs est directe, ce qui servira à Dijkstra.
  Un sommet isolé a simplement un dictionnaire interne vide.

### Tests

`tests/test_graphe.py` contient 17 tests `unittest`, tous passants :
ajout d'un sommet et refus d'un doublon ou d'un identifiant vide ; refus d'un arc dont l'origine ou
la destination est inconnue ; poids négatif ou non numérique refusé, poids nul accepté ;
arc en double refusé même avec un autre poids ; non-symétrie des arcs ; sommet isolé.

## Choix et décisions à reprendre dans le rapport

- Arcs multiples interdits (choix du sujet).
- Exceptions personnalisées, avec héritage de `ValueError` / `KeyError` quand c'est pertinent.
- Poids non négatifs, donc Dijkstra est applicable.
- Pour la partie B, il reste à décider et à documenter si une erreur rejette tout le fichier ou seulement la ligne fautive.

## Ressources externes et assistance par IA

Conformément au sujet, voici l'assistance utilisée :

- **Outil** : Claude Code (Opus 5.5, Sonnet 5.5).