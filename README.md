# Une vie de fourmi

> 📘 Pour tout comprendre en détail (modèle, fonctions, questions/réponses de
> soutenance), voir le guide **`EXPLICATIONS.md`**.

## Contexte du projet
Une colonie de F fourmis doit rejoindre le dortoir (`Sd`) depuis le vestibule
(`Sv`) en un minimum d'étapes.

Une fourmilière est un graphe : les salles sont les sommets et les tunnels les
arêtes (traversés instantanément). Une salle ordinaire accueille 1 fourmi, ou
`k` fourmis quand le fichier la note `Si { k }` ; le vestibule et le dortoir
accueillent toute la colonie.

À chaque étape, toutes les fourmis se déplacent en même temps : chacune reste
sur place ou rejoint une salle voisine. Une fourmi ne peut entrer dans une
salle que si sa capacité n'est pas dépassée à la fin de l'étape : salle vide,
place libre, ou occupant en train de partir.

Les fourmilières à traiter sont dans `fourmilieres/`.

## La problématique
Trouver, pour chaque fourmilière, le nombre **minimal** d'étapes pour mettre
les F fourmis au dortoir, puis décrire le déplacement de chaque fourmi à chaque
étape (format `+++ E1 +++` puis `f1 - Sv - S1`).

## Solutions apportées
Le problème est modélisé comme un **flot entier dans un réseau dilaté dans le
temps** (voir `ants.py`) :

1. **Lecture** — `lire_fourmiliere` : salles, capacités et tunnels du fichier,
   rangés dans une **matrice d'adjacence**.
2. **Distances** — `distances` et `plus_court_chemin` (parcours en largeur sur
   la matrice) donnent la distance Sv → Sd, borne inférieure du temps de trajet.
3. **Glouton** — `resoudre_glouton` fait avancer les fourmis, étape par étape,
   vers une salle plus proche du dortoir dès qu'une place se libère. C'est la
   méthode simple du cours : rapide et optimale sur 7 fourmilières sur 9, mais
   aveugle aux goulets (jusqu'à 83 étapes perdues sur `salle_d_at-ant`).
4. **Méthode exacte** — `plan_possible(f, T)` recopie la fourmilière à chaque
   pas de temps (réseau dilaté) : un arc signifie « attendre » ou « traverser un
   tunnel ». Un flot de F unités de `Sv` (temps 0) vers `Sd` (temps T) existe si
   et seulement s'il existe un plan valide en T étapes.
5. **Temps minimal** — `temps_minimal` : dichotomie entre la distance Sv → Sd et
   `distance + F`. Le flot maximum est calculé par l'algorithme d'Edmonds-Karp
   écrit à la main (`flot_maximum`).
6. **Planning** — `resoudre_optimal` relit le flot arc par arc, puis `derouler`
   répartit les fourmis dans les tunnels utilisés à chaque pas.
7. **Contrôle** — `verifier_planning` rejoue le planning et vérifie chaque
   règle : un seul déplacement par fourmi et par étape, tunnel existant,
   capacités respectées, toute la colonie au dortoir à la fin.
8. **Affichage** — `graphes.py` dessine la fourmilière (salles en colonnes
   selon leur distance au vestibule, fourmis posées sur les salles occupées)
   et anime le déroulement étape par étape.

### Utilisation

```bash
pip install -r requirements.txt
python main.py                        # résout toutes les fourmilières
python main.py fourmiliere_un -d      # affiche le détail des étapes
python main.py fourmiliere_un -g      # affiche le graphe et l'animation
python main.py fourmiliere_un -i      # enregistre les images dans images/
python main.py --verifier             # rejoue les plannings enregistrés
python main.py --test                 # vérifie le cas simple de l'énoncé
```

Les plannings calculés sont écrits dans `solutions/`.

### Conformité aux règles de l'énoncé

| Règle | Où elle est garantie |
|---|---|
| Même vitesse pour toutes : au plus un tunnel par étape | les arcs du réseau dilaté vont toujours du pas `t` au pas `t + 1` ; `verifier_planning` refuse deux déplacements d'une même fourmi dans la même étape |
| Une salle = 1 fourmi, ou `k` si `Si { k }` ; vestibule et dortoir illimités | capacité portée par l'arc `(ENTREE, salle, t) → (SORTIE, salle, t)`, vérifiée après chaque étape |
| On n'entre dans une salle que si elle est vide, a une place libre, ou si l'occupant part | équivaut à « capacité non dépassée à la fin de l'étape » : les fourmis qui partent libèrent la place dans la même étape |
| Tunnels traversés instantanément | ni temps ni capacité sur les tunnels : un tunnel = une étape, plusieurs fourmis peuvent l'emprunter au même pas si la destination a la place |
| Toute la colonie au dortoir en un minimum d'étapes | flot de F unités + recherche du plus petit T par dichotomie |
| Notation `f1 - Sv - S1`, `+++ E1 +++`, attente non notée | `format_planning` |

`python main.py --verifier` relit les plannings de `solutions/` et les rejoue règle
par règle : les 9 plannings sont valides et optimaux.

### Résultats

| fourmilière | fourmis | plus court trajet | glouton | **minimum** |
|---|---|---|---|---|
| `fourmiliere_zero` | 2 | 2 tunnels | 2 | **2** |
| `fourmiliere_un` | 5 | 3 tunnels | 7 | **7** |
| `fourmiliere_deux` | 5 | 1 tunnel | 1 | **1** |
| `fourmiliere_trois` | 5 | 3 tunnels | 7 | **7** |
| `fourmiliere_quatre` | 10 | 5 tunnels | 9 | **9** |
| `fourmiliere_cinq` | 50 | 5 tunnels | 17 | **11** |
| `fourmiliere_3D` | 50 | 4 tunnels | 28 | **14** |
| `La_hormiguera_de_la_muerte` | 30 | 4 tunnels | 9 | **9** |
| `salle_d_at-ant` | 100 | 6 tunnels | 98 | **15** |

## Conclusion
Le flot dans un réseau dilaté dans le temps donne le nombre minimal d'étapes de
façon exacte, y compris pour les fourmilières à fortes capacités (jusqu'à 100
fourmis). Chaque planning produit est rejoué et vérifié règle par règle, et
l'affichage graphique permet de suivre les fourmis étape par étape.
