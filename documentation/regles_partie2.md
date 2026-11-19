# Aide-mémoire – Partie 2 : Modèle et règles de gestion

> Note personnelle de travail. À fusionner dans le README ou à retirer avant le rendu.

## Le modèle

- Graphe **orienté** et **pondéré** : G = (V, E)
- **V** = ensemble des sommets (les lieux), identifiés par une chaîne de caractères
- **E** = ensemble des arcs, chaque arc est un triplet `(origine, destination, poids)`
- **Orienté** : `A → B` n'implique **pas** `B → A`
- **Pondéré** : le poids = coût du déplacement (durée, distance, prix)

---

## Les 5 règles et leur traduction dans le code

### Règle 1 – Identifiant de sommet unique et non vide

| Vérification | Où | Exception suggérée |
|---|---|---|
| L'identifiant est une chaîne | `ajouter_sommet` | `TypeError` |
| L'identifiant n'est pas vide (penser à `strip()`) | `ajouter_sommet` | `ValueError` |
| Le sommet n'existe pas déjà | `ajouter_sommet` | `ValueError` / exception perso |

### Règle 2 – Poids positif ou nul

| Vérification | Où | Exception suggérée |
|---|---|---|
| Le poids est un nombre (`int` ou `float`) | `ajouter_arc`, `from_file` | `TypeError` / `ValueError` |
| Le poids est `>= 0` (0 est accepté) | `ajouter_arc`, `from_file` | `ValueError` |

**Pourquoi c'est important :** c'est ce qui permet d'utiliser **Dijkstra** (partie D), qui ne fonctionne pas avec des poids négatifs. À mentionner dans le rapport.

### Règle 3 – Les extrémités d'un arc doivent exister

| Vérification | Où | Exception suggérée |
|---|---|---|
| L'origine est un sommet du graphe | `ajouter_arc` | `KeyError` / exception perso |
| La destination est un sommet du graphe | `ajouter_arc` | `KeyError` / exception perso |

**Conséquence :** il faut ajouter les sommets **avant** les arcs (d'où la ligne `Sommets:` en tête du fichier).

### Règle 4 – Pas d'arc en double

| Vérification | Où | Exception suggérée |
|---|---|---|
| Aucun arc `origine → destination` n'existe déjà | `ajouter_arc` | `ValueError` / exception perso |

- Le doublon se juge sur le couple **(origine, destination)**, **pas** sur le poids.
- `A → B` (4) puis `A → B` (7) : **refusé**.
- `A → B` puis `B → A` : **autorisé** (sens différent).
- Si je choisis d'autoriser les arcs multiples : **le justifier dans le rapport**.

### Règle 5 – Un sommet peut être isolé

- Un sommet sans aucun arc est **valide** (ex. : H).
- Il doit fonctionner partout sans planter :
  - degré entrant = degré sortant = degré total = 0
  - prédécesseurs = successeurs = liste vide
  - `shortest_path` vers ou depuis H : « aucun chemin », pas une erreur imprévue

---

## Idée : exceptions personnalisées

Créer une hiérarchie d'exceptions rend les messages plus clairs et valorise la POO :

- `GrapheError` (classe de base, hérite de `Exception`)
  - `SommetExistantError`
  - `SommetInconnuError`
  - `ArcExistantError`
  - `PoidsInvalideError`

---

## Tests à écrire en lien avec ces règles

- [ ] Ajout correct d'un sommet
- [ ] Refus d'un sommet en doublon
- [ ] Refus d'un identifiant vide
- [ ] Refus d'un arc dont l'origine est inconnue
- [ ] Refus d'un arc dont la destination est inconnue
- [ ] Refus d'un poids négatif
- [ ] Refus d'un poids non numérique
- [ ] Acceptation d'un poids égal à 0
- [ ] Refus d'un arc en double (même avec un poids différent)
- [ ] `A → B` ajouté n'implique pas `B → A`
- [ ] Le sommet H existe et n'a aucun arc

---

## Choix à faire et à justifier dans le rapport

- [ ] Structure de données choisie (ex. : dictionnaire d'adjacence `{origine: {destination: poids}}`) et pourquoi
- [ ] Arcs multiples interdits (choix par défaut du sujet) ou autorisés (à justifier)
- [ ] Type d'exceptions utilisées
- [ ] Lien entre poids non négatifs et choix de Dijkstra

---

## Points de vigilance

- Les méthodes ne doivent **ni** appeler `input()` **ni** faire de `print()` : elles **retournent** des valeurs ou **lèvent** des exceptions.
- Mettre les règles dans les **docstrings** de `ajouter_sommet` et `ajouter_arc`.
- Si une aide IA a été utilisée (y compris pour ce fichier), le signaler dans le README.
