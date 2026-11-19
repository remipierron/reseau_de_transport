# PROJET PYTHON NOTÉ

## Concevoir et analyser un réseau de transport

*POO • Théorie des graphes • Fichiers • Algorithmique • Tests*

---

- Le travail est **individuel**. Les échanges de méthodes ou de pistes sont possibles, mais le code et le rapport doivent être personnels.
- Les bibliothèques Python standard sont autorisées. Les bibliothèques spécialisées de graphes (NetworkX, igraph, etc.) **ne sont pas autorisées** pour implémenter les algorithmes demandés.
- Vous pouvez consulter la documentation officielle et des ressources pédagogiques. Toute ressource externe ou assistance par IA ayant contribué au code doit être signalée dans le README : outil ou source, usage effectué et parties concernées. Vous devez être capable d'expliquer et de modifier votre code.
- Les méthodes métier ne doivent pas appeler `input()` ni afficher directement les résultats. La saisie et l'affichage doivent être séparés des traitements.
- Un programme qui fonctionne uniquement sur le jeu de données fourni, sans gérer les cas limites demandés, ne pourra pas obtenir tous les points.

---

## 1. Contexte et objectif

Une collectivité souhaite étudier les déplacements entre plusieurs lieux de son territoire. Les lieux sont représentés par des sommets et les liaisons possibles par des arcs orientés et pondérés. Le poids représente un coût de déplacement (durée, distance ou coût financier).

Votre mission consiste à développer une petite application Python qui permet de créer un réseau, de le charger depuis un fichier, de l'analyser et de rechercher des itinéraires. Le projet doit être conçu en programmation orientée objet et accompagné de tests.

Le travail est à réaliser sur une semaine. Vous pouvez organiser votre travail librement, mais le code rendu doit être personnel, compréhensible et exécutable.

## 2. Modèle et règles de gestion

On modélise le réseau par un graphe orienté pondéré **G = (V, E)**. V est l'ensemble des sommets. Chaque arc est un triplet `(origine, destination, poids)`. Un arc A → B n'implique pas qu'un arc B → A existe.

- Chaque sommet possède un identifiant textuel unique et non vide.
- Le poids d'un arc est un nombre positif ou nul.
- Les deux extrémités d'un arc doivent être des sommets déjà présents dans le graphe.
- Dans le cadre de ce sujet, deux arcs ayant la même origine et la même destination sont interdits. Si vous souhaitez gérer plusieurs liaisons entre deux lieux, expliquez votre choix dans le rapport.
- Un sommet peut être isolé, c'est-à-dire ne posséder aucun arc entrant ni sortant.

## 3. Données de départ

Créez un fichier `reseau.txt` contenant les données suivantes :

```text
Sommets: A, B, C, D, E, F, G, H
A;B;4
A;C;2
C;B;1
B;D;5
C;D;8
C;E;10
D;E;2
D;F;6
E;F;3
F;G;1
B;G;15
```

**Format :** la première ligne commence par « `Sommets:` » et contient les identifiants séparés par des virgules. Chaque ligne suivante contient `origine;destination;poids`. Le sommet H est volontairement isolé. Vous devez également créer un second petit graphe de votre choix pour tester la comparaison.

## 4. Travail demandé

Les parties A à E et les tests constituent le travail obligatoire, noté sur **18 points**. La partie F est un bonus facultatif de **2 points** maximum, dans la limite de la note maximale de 20.

### A. Modélisation orientée objet – 3 points

Définissez une conception orientée objet comportant au minimum une classe `Graphe` et, selon votre choix, des classes `Sommet` et `Arc`. Vous pouvez proposer une autre conception si elle est cohérente et expliquée. La classe `Graphe` doit gérer les sommets et les arcs.

À réaliser :

- constructeur et représentation lisible du graphe ;
- `ajouter_sommet(...)` et `ajouter_arc(...)` ;
- vérification des doublons et des extrémités inexistantes ;
- méthodes de consultation des sommets et des arcs.

Dans le rapport, justifiez brièvement les structures de données choisies (liste, dictionnaire, ensemble, etc.).

### B. Lecture d'un fichier et robustesse – 2 points

Écrivez une méthode ou fonction `from_file(chemin)` qui construit un graphe à partir du fichier `reseau.txt`.

Le programme doit traiter au minimum les situations suivantes : fichier inexistant, ligne mal formée, poids non numérique ou négatif, arc faisant référence à un sommet inconnu. Utilisez des exceptions adaptées et des messages compréhensibles. Précisez si une erreur entraîne le rejet du fichier entier ou uniquement de la ligne concernée.

### C. Analyse du réseau – 2 points

Pour un sommet donné, calculez : son degré entrant, son degré sortant et son degré total. Retournez également ses prédécesseurs et ses successeurs. Testez notamment le sommet H, qui est isolé, ainsi que deux autres sommets. Les méthodes doivent retourner des résultats exploitables par le reste du programme.

### D. Recherche d'itinéraire – 4 points

Implémentez `shortest_path(depart, arrivee)`, qui retourne le chemin de coût minimal ainsi que son coût total. Les poids étant non négatifs, vous pouvez utiliser Dijkstra. Vous devez gérer le cas où aucun chemin n'existe et celui où le départ et l'arrivée sont identiques.

Dans le rapport, expliquez le principe de l'algorithme choisi et justifiez pourquoi il convient aux données du sujet. Indiquez le chemin et le coût obtenus entre A et G.

### E. Contraintes et comparaison – 3 points

1. Implémentez `shortest_path_avoiding(depart, arrivee, interdit)`, qui recherche un itinéraire optimal sans passer par le sommet interdit. Définissez clairement le comportement si le sommet interdit correspond au départ ou à l'arrivée.
2. Implémentez `intersection(autre_graphe)`, qui retourne un nouveau graphe composé des sommets communs et des arcs présents dans les deux graphes. Pour cet exercice, un arc est commun si son origine, sa destination et son poids sont identiques. Les graphes d'origine ne doivent pas être modifiés.

### F. Approfondissement algorithmique – bonus jusqu'à 2 points

Choisissez et implémentez au moins une des deux fonctionnalités suivantes :

- **Option 1 – Détection de cycle :** `has_cycle()` retourne `True` si le graphe orienté contient au moins un cycle, `False` sinon. Testez avec un graphe acyclique et un graphe dans lequel vous avez ajouté un cycle.
- **Option 2 – Ordonnancement :** `topological_sort()` retourne un ordre topologique si le graphe est acyclique et signale clairement qu'un tel ordre n'existe pas en présence d'un cycle.

Pour obtenir tous les points de cette partie, expliquez l'idée de l'algorithme et testez les cas positifs et négatifs. Les deux options peuvent être réalisées pour un travail particulièrement abouti.

## 5. Tests obligatoires

Fournissez au moins **huit tests automatisés**. Vous pouvez utiliser `unittest` ou `pytest` (ou des assertions Python simples). Les tests doivent contrôler les résultats attendus et pas seulement afficher des informations.

- ajout correct d'un sommet et refus d'un doublon ;
- refus d'un arc dont une extrémité est inconnue ;
- lecture correcte du fichier et réaction à une donnée invalide ;
- degrés d'un sommet isolé ;
- plus court chemin entre deux sommets connectés ;
- absence de chemin entre deux sommets ;
- itinéraire avec sommet interdit ;
- intersection de deux graphes sans modification des graphes initiaux.

## 6. Livrables à déposer

- Les fichiers source Python (`.py`), organisés proprement. Le code doit pouvoir être exécuté sans modification manuelle des chemins.
- Le fichier `reseau.txt` et le second graphe utilisé pour les tests.
- Un fichier `README.md` indiquant la version de Python, les instructions d'installation éventuelles et la commande pour lancer le programme et les tests.
- Un court rapport PDF (2 à 4 pages maximum) présentant le modèle choisi, les structures de données, l'algorithme de plus court chemin, les résultats de tests et les limites connues.
- Une courte démonstration ou quelques exemples d'exécution montrant les principales fonctionnalités.

---

<p align="center"><strong>Bon travail !</strong></p>