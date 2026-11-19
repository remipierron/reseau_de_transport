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
  graphe.py         classe Graphe (sommets + liste d'adjacence, analyse d'un sommet)
  lecture.py        lecture d'un graphe depuis un fichier texte (`Graphe.from_file`)
  exceptions.py     hiérarchie d'exceptions personnalisées
data/reseau.txt     réseau du sujet (8 sommets, 11 arcs, H isolé)
data/reseau2.txt    second graphe de test (5 sommets, 6 arcs)
tests/              tests unittest
documentation/      notes de travail
sujet/              énoncé
```

## Avancement

| Partie | Contenu | Points | État |
|---|---|---|---|
| A | Modélisation orientée objet | 3 | ✅ Terminée |
| B | Lecture de fichier (`from_file`) et robustesse | 2 | ✅ Terminée |
| C | Analyse : degrés, prédécesseurs, successeurs | 2 | ✅ Terminée |
| D | Plus court chemin (`shortest_path`, Dijkstra) | 4 | ⏳ À faire |
| E | Sommet interdit et intersection de graphes | 3 | ⏳ À faire |
| F | Bonus : détection de cycle / tri topologique | +2 | ⏳ Optionnel, à faire |
| Tests | 8 tests minimum | – | 🔶 44 tests écrits pour les parties A à C ; ceux des parties D et E restent à écrire |
| Livrables | Rapport PDF (2 à 4 pages), exemples d'exécution, second graphe de test | – | 🔶 Second graphe (`data/reseau2.txt`) fait ; rapport et exemples d'exécution à faire |

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

### Partie B (réalisée)

- **Méthode** : `Graphe.from_file(chemin)` (chemin en `str` ou `Path`), qui s'appuie sur
  `lire_graphe` dans `graphe/lecture.py`.
- **Format** : première ligne utile `Sommets: A, B, C`, puis une ligne par arc `origine;destination;poids`.
  Les lignes vides et celles commençant par `#` sont ignorées ; les espaces autour des valeurs sont tolérés.
- **Politique d'erreur** : le fichier est **rejeté en entier** à la première erreur, car un réseau
  chargé à moitié pourrait donner de faux itinéraires. L'exception porte le numéro et le contenu de la ligne fautive.
- **Exceptions** : `FichierIntrouvableError` (fichier absent, hérite aussi de `FileNotFoundError`),
  `FichierGrapheError` (fichier illisible : dossier, droits), `FormatFichierError` (contenu invalide,
  avec `numero_ligne` et la cause d'origine en `__cause__`), `LigneMalFormeeError` (ligne mal structurée),
  en plus des erreurs de la partie A (doublon, sommet inconnu, poids invalide) qui sont réutilisées.

### Partie C (réalisée)

- **Méthodes de `Graphe`** : `successeurs`, `predecesseurs`, `degre_entrant`, `degre_sortant`,
  `degre_total`, `est_isole`, `analyser_sommet` (dictionnaire regroupant toutes ces informations).
- Un sommet inconnu lève `SommetInconnuError`.
- Les listes retournées sont des copies : les modifier ne modifie pas le graphe.

### Structures de données choisies

- `_sommets` : `dict` identifiant → `Sommet`. Test de présence et détection des doublons en O(1),
  ordre d'insertion conservé (affichage stable).
- `_adjacence` : `dict` identifiant → `dict` (destination → `Arc`). Liste d'adjacence : savoir si
  l'arc A → B existe est en O(1) et l'énumération des successeurs est directe, ce qui servira à Dijkstra.
  Un sommet isolé a simplement un dictionnaire interne vide.
- `_entrants` : pour chaque sommet, ses prédécesseurs, afin de calculer `predecesseurs` et
  `degre_entrant` sans parcourir tout le graphe.

### Tests

44 tests `unittest`, tous passants :

- `tests/test_graphe.py` (17, partie A) : ajout d'un sommet et refus d'un doublon ou d'un identifiant vide ;
  refus d'un arc dont l'origine ou la destination est inconnue ; poids négatif ou non numérique refusé,
  poids nul accepté ; arc en double refusé même avec un autre poids ; non-symétrie des arcs ; sommet isolé.
- `tests/test_lecture.py` (18, partie B) : lecture des deux fichiers fournis ; fichiers invalides
  (numéro de ligne et cause vérifiés), créés dans un dossier temporaire pour garder `data/` propre.
- `tests/test_analyse.py` (9, partie C) : degrés, prédécesseurs et successeurs de plusieurs sommets,
  sommet isolé, sans prédécesseur ou sans successeur, sommet inconnu, somme des degrés,
  résultat modifiable sans effet sur le graphe.

## Choix et décisions à reprendre dans le rapport

- Arcs multiples interdits (choix du sujet).
- Exceptions personnalisées, avec héritage de `ValueError` / `KeyError` quand c'est pertinent.
- Poids non négatifs, donc Dijkstra est applicable.
- Partie B : une erreur rejette tout le fichier (aucun graphe partiel), avec le numéro de ligne dans l'exception.

## Ressources externes et assistance par IA

Conformément au sujet, voici l'assistance utilisée :

- **Outil** : Claude Code (Opus 5.5, Sonnet 5.5).