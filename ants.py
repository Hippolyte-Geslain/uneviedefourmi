"""Résolution du problème « Une vie de fourmi ».

Représentation d'une fourmilière
--------------------------------
Une fourmilière est un dictionnaire :

    {
        "nom": "fourmiliere_un",
        "fourmis": 5,                         # nombre de fourmis (F)
        "salles": ["Sv", "S1", "S2", "Sd"],   # nom de chaque salle (l'indice
                                              # sert de numéro de salle)
        "capacites": [5, 1, 1, 5],            # capacité de chaque salle
        "matrice": [[0, 1, 0, 0],             # matrice d'adjacence :
                    [1, 0, 1, 0],             # matrice[i][j] vaut 1 s'il y a
                    [0, 1, 0, 1],             # un tunnel entre i et j
                    [0, 0, 1, 0]],
    }

Règles du jeu (résumé)
----------------------
* ``Sv`` est le vestibule (tout le monde y commence), ``Sd`` le dortoir.
* Une salle ordinaire contient 1 fourmi, ou ``k`` si le fichier la note
  ``Si { k }`` ; le vestibule et le dortoir contiennent toute la colonie.
* Une étape : chaque fourmi reste sur place ou traverse un tunnel vers une
  salle voisine. On ne peut pas entrer dans une salle dont la capacité serait
  dépassée à la fin de l'étape (salle vide, place libre, ou occupant qui part).

Algorithme (glouton, étape par étape)
-------------------------------------
À chaque étape, on regarde les fourmis en commençant par celles qui sont le
plus près du dortoir. Chacune avance vers une salle voisine plus proche du
dortoir si la place est libre à la fin de l'étape ; sinon elle attend.

Ordre de lecture conseillé des fonctions :
    lire_fourmiliere → indice → voisins → distances → plus_court_chemin
    → place_libre → choisir_destination → resoudre → verifier_planning
    → format_planning
"""

from __future__ import annotations

import re
from collections import Counter, deque
from pathlib import Path

import networkx as nx

# Noms des deux salles particulières.
VESTIBULE = "Sv"
DORTOIR = "Sd"

# Valeur renvoyée par `distances` pour une salle injoignable.
INJOIGNABLE = -1


class ErreurFourmiliere(ValueError):
    """Fourmilière illisible ou planning incohérent."""


# ---------------------------------------------------------------------------
# 1. Lecture du fichier
# ---------------------------------------------------------------------------

_RE_FOURMIS = re.compile(r"^[fF]\s*=\s*(\d+)$")
_RE_CAPACITE = re.compile(r"^(\S+)\s*\{\s*(\d+)\s*\}$")
_RE_TUNNEL = re.compile(r"^(\S+)\s+-\s+(\S+)$")
_RE_SALLE = re.compile(r"^(\S+)$")


def lire_fourmiliere(chemin: str | Path) -> dict:
    """Lit le fichier texte décrivant une fourmilière.

    Format reconnu, une information par ligne :

    * ``f = 5`` (ou ``F = 5``) : le nombre de fourmis ;
    * ``S1`` : une salle de capacité 1 ;
    * ``S1 { 2 }`` : une salle de capacité 2 ;
    * ``Sv - S1`` : un tunnel entre deux salles.

    Les lignes vides et les lignes commençant par ``#`` sont ignorées.
    À la fin, on construit la matrice d'adjacence à partir des tunnels.
    """

    chemin = Path(chemin)
    nb_fourmis = None
    noms: list[str] = []
    capacites: dict[str, int] = {}
    tunnels: list[tuple[str, str]] = []

    for numero, brute in enumerate(chemin.read_text(encoding="utf-8").splitlines(), start=1):
        ligne = brute.strip()
        if not ligne or ligne.startswith("#"):
            continue

        correspondance = _RE_FOURMIS.match(ligne)
        if correspondance:
            nb_fourmis = int(correspondance.group(1))
            continue

        correspondance = _RE_CAPACITE.match(ligne)
        if correspondance:
            nom = correspondance.group(1)
            if nom not in noms:
                noms.append(nom)
            capacites[nom] = int(correspondance.group(2))
            continue

        correspondance = _RE_TUNNEL.match(ligne)
        if correspondance:
            depart = correspondance.group(1)
            arrivee = correspondance.group(2)
            if depart == arrivee:
                raise ErreurFourmiliere(
                    f"{chemin.name}, ligne {numero} : tunnel {depart} - {arrivee} sans intérêt"
                )
            for nom in (depart, arrivee):
                if nom not in noms:
                    noms.append(nom)
                capacites.setdefault(nom, 1)
            tunnels.append((depart, arrivee))
            continue

        correspondance = _RE_SALLE.match(ligne)
        if correspondance:
            nom = correspondance.group(1)
            if nom not in noms:
                noms.append(nom)
            capacites.setdefault(nom, 1)
            continue

        raise ErreurFourmiliere(f"{chemin.name}, ligne {numero} : ligne incomprise {ligne!r}")

    if nb_fourmis is None:
        raise ErreurFourmiliere(f"{chemin.name} : la ligne « f = ... » est absente")
    for extremite in (VESTIBULE, DORTOIR):
        if extremite not in capacites:
            raise ErreurFourmiliere(f"{chemin.name} : la salle {extremite} n'existe pas")

    # Le vestibule et le dortoir sont les deux plus vastes salles de la
    # fourmilière : ils accueillent toute la colonie.
    capacites[VESTIBULE] = max(nb_fourmis, 1)
    capacites[DORTOIR] = max(nb_fourmis, 1)

    # Matrice d'adjacence : 1 dans la case (i, j) s'il y a un tunnel i - j.
    taille = len(noms)
    matrice = [[0] * taille for _ in range(taille)]
    for depart, arrivee in tunnels:
        i = noms.index(depart)
        j = noms.index(arrivee)
        matrice[i][j] = 1
        matrice[j][i] = 1

    return {
        "nom": chemin.stem,
        "fourmis": nb_fourmis,
        "salles": noms,
        "capacites": [capacites[nom] for nom in noms],
        "matrice": matrice,
    }


def exemple_du_sujet() -> dict:
    """Le « cas simple » de l'énoncé : 3 fourmis, Sv-S1-Sd et Sv-S2-Sd.

    Salles :      0 = Sv, 1 = S1, 2 = S2, 3 = Sd
    """

    return {
        "nom": "cas_simple",
        "fourmis": 3,
        "salles": ["Sv", "S1", "S2", "Sd"],
        "capacites": [3, 1, 1, 3],
        "matrice": [
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [0, 1, 1, 0],
        ],
    }


# ---------------------------------------------------------------------------
# 2. Outils sur la matrice d'adjacence
# ---------------------------------------------------------------------------


def indice(fourmiliere: dict, nom: str) -> int:
    """Numéro (indice) d'une salle à partir de son nom."""

    return fourmiliere["salles"].index(nom)


def voisins(fourmiliere: dict, salle: int) -> list[int]:
    """Numéros des salles reliées à ``salle`` (une ligne de la matrice)."""

    ligne = fourmiliere["matrice"][salle]
    return [autre for autre in range(len(ligne)) if ligne[autre] == 1]


def distances(fourmiliere: dict, depart: int) -> list[int]:
    """Distance (en tunnels) du départ à chaque salle.

    Parcours en largeur sur la matrice d'adjacence. Une salle injoignable
    garde la valeur ``INJOIGNABLE`` (-1).
    """

    distance = [INJOIGNABLE] * len(fourmiliere["salles"])
    distance[depart] = 0
    file = deque([depart])
    while file:
        salle = file.popleft()
        for voisine in voisins(fourmiliere, salle):
            if distance[voisine] == INJOIGNABLE:
                distance[voisine] = distance[salle] + 1
                file.append(voisine)
    return distance


def plus_court_chemin(fourmiliere: dict, depart: int, arrivee: int) -> list[int]:
    """Plus court chemin (liste de numéros de salles) de ``depart`` à ``arrivee``.

    Parcours en largeur : on mémorise le prédécesseur de chaque salle, puis on
    remonte depuis l'arrivée. Lève une :class:`ErreurFourmiliere` si le dortoir
    est injoignable.
    """

    precedent = {depart: None}
    file = deque([depart])
    while file:
        salle = file.popleft()
        if salle == arrivee:
            break
        for voisine in voisins(fourmiliere, salle):
            if voisine not in precedent:
                precedent[voisine] = salle
                file.append(voisine)

    if arrivee not in precedent:
        raise ErreurFourmiliere(
            f"{fourmiliere['nom']} : aucun chemin entre "
            f"{fourmiliere['salles'][depart]} et {fourmiliere['salles'][arrivee]}"
        )

    chemin = []
    salle = arrivee
    while salle is not None:
        chemin.append(salle)
        salle = precedent[salle]
    return chemin[::-1]


def construire_graphe(fourmiliere: dict) -> nx.Graph:
    """Construit le graphe networkx correspondant (utile pour l'affichage)."""

    graphe = nx.Graph()
    graphe.add_nodes_from(fourmiliere["salles"])
    taille = len(fourmiliere["salles"])
    for i in range(taille):
        for j in range(i + 1, taille):
            if fourmiliere["matrice"][i][j] == 1:
                graphe.add_edge(fourmiliere["salles"][i], fourmiliere["salles"][j])
    return graphe


# ---------------------------------------------------------------------------
# 3. Algorithme glouton
# ---------------------------------------------------------------------------


def place_libre(fourmiliere: dict, salle: int, occupes: list[int], departs: list[int], arrivees: list[int]) -> int:
    """Places libres dans une salle à la fin de l'étape en cours.

    ``occupes`` est le nombre de fourmis présentes dans la salle au début de
    l'étape ; ``departs`` et ``arrivees`` comptent les mouvements déjà décidés
    pendant cette même étape (les partants libèrent leur place tout de suite).
    """

    if salle == indice(fourmiliere, DORTOIR):
        return fourmiliere["fourmis"]  # le dortoir est sans limite
    dedans = occupes[salle] - departs[salle] + arrivees[salle]
    return fourmiliere["capacites"][salle] - dedans


def choisir_destination(
    fourmiliere: dict,
    distance_dortoir: list[int],
    occupes: list[int],
    departs: list[int],
    arrivees: list[int],
    salle: int,
) -> int | None:
    """Meilleure salle voisine où avancer, ou ``None`` si aucune ne convient.

    On ne regarde que les salles strictement plus proches du dortoir, et on
    préfère la plus proche ; à égalité, celle qui a le plus de places libres
    (pour répartir les fourmis sur plusieurs voies parallèles).
    """

    meilleure = None
    meilleur_score = None

    for voisine in voisins(fourmiliere, salle):
        if distance_dortoir[voisine] == INJOIGNABLE:
            continue  # cette salle ne mène pas au dortoir
        if distance_dortoir[voisine] >= distance_dortoir[salle]:
            continue  # ce n'est pas un progrès vers le dortoir
        libre = place_libre(fourmiliere, voisine, occupes, departs, arrivees)
        if libre <= 0:
            continue  # il n'y aura plus de place à la fin de l'étape

        score = (distance_dortoir[voisine], -libre)
        if meilleur_score is None or score < meilleur_score:
            meilleure = voisine
            meilleur_score = score

    return meilleure


def resoudre_glouton(fourmiliere: dict) -> dict:
    """Déplace toute la colonie au dortoir (algorithme glouton).

    À chaque étape :

    1. on compte les fourmis présentes dans chaque salle ;
    2. on examine les fourmis en commençant par celles qui sont le plus près du
       dortoir (elles libèrent la place pour celles qui suivent) ;
    3. chacune avance vers une salle voisine plus proche du dortoir s'il reste
       de la place à la fin de l'étape, sinon elle attend ;
    4. on applique tous les mouvements en même temps.

    Renvoie un dictionnaire ``{"duree", "etapes", "etats"}`` :

    * ``etapes[k]`` : liste des mouvements ``(fourmi, salle de départ, salle
      d'arrivée)`` de l'étape ``k + 1`` (les numéros de salles) ;
    * ``etats[k]`` : position de chaque fourmi avant l'étape ``k + 1``.
    """

    taille = len(fourmiliere["salles"])
    dortoir = indice(fourmiliere, DORTOIR)
    vestibule = indice(fourmiliere, VESTIBULE)
    distance_dortoir = distances(fourmiliere, dortoir)

    position = [vestibule] * fourmiliere["fourmis"]
    etats = [list(position)]
    etapes = []

    while any(salle != dortoir for salle in position):
        # 1. Où sont les fourmis au début de l'étape ?
        occupes = [0] * taille
        for salle in position:
            occupes[salle] += 1

        departs = [0] * taille
        arrivees = [0] * taille
        mouvements = []

        # 2. Les fourmis les plus proches du dortoir passent en premier.
        ordre = sorted(range(len(position)), key=lambda fourmi: distance_dortoir[position[fourmi]])

        # 3. Chacune essaie d'avancer d'une salle.
        for fourmi in ordre:
            ici = position[fourmi]
            if ici == dortoir:
                continue
            destination = choisir_destination(
                fourmiliere, distance_dortoir, occupes, departs, arrivees, ici
            )
            if destination is None:
                continue  # pas de place devant : la fourmi attend
            mouvements.append((fourmi + 1, ici, destination))
            departs[ici] += 1
            arrivees[destination] += 1

        if not mouvements:
            raise ErreurFourmiliere(
                f"{fourmiliere['nom']} : plus aucune fourmi ne peut avancer"
            )

        # 4. Tous les mouvements ont lieu en même temps.
        for fourmi, _, destination in mouvements:
            position[fourmi - 1] = destination

        etapes.append(mouvements)
        etats.append(list(position))

    return {"duree": len(etapes), "etapes": etapes, "etats": etats}


def occupation(fourmiliere: dict, position: list[int]) -> dict[str, list[int]]:
    """Quelles fourmis sont dans quelle salle (pour l'affichage) ?"""

    contenu = {nom: [] for nom in fourmiliere["salles"]}
    for numero, salle in enumerate(position, start=1):
        contenu[fourmiliere["salles"][salle]].append(numero)
    return contenu


# ---------------------------------------------------------------------------
# 4. Méthode exacte : flot maximum dans le réseau dilaté dans le temps
# ---------------------------------------------------------------------------

ENTREE = "entree"
SORTIE = "sortie"
SOURCE = "SOURCE"
PUITS = "PUITS"


def reseau_dilate(fourmiliere: dict, duree: int) -> dict:
    """Recopie la fourmilière à chaque pas de temps, de 0 à ``duree``.

    Pour chaque salle et chaque pas ``t``, deux nœuds sont créés :
    ``(ENTREE, salle, t)`` (on peut y arriver au pas t) et
    ``(SORTIE, salle, t)`` (on peut en partir au pas t). Les arcs sont :

    * ``(ENTREE, s, t) → (SORTIE, s, t)`` : occuper une place dans la salle
      pendant le pas t (capacité = capacité de la salle) ;
    * ``(SORTIE, s, t) → (ENTREE, s, t+1)`` : attendre un pas de plus ;
    * ``(SORTIE, u, t) → (ENTREE, v, t+1)`` : traverser un tunnel, l'arrivée
      étant limitée par la capacité de la salle d'arrivée.

    Deux arcs inutiles sont omis : sortir du dortoir et rentrer dans le
    vestibule (le dortoir est sans limite, le vestibule ne sert qu'au départ).

    Renvoie un dictionnaire de capacités : ``{nœud: {voisin: capacité}}``.
    """

    capacites: dict = {}
    dortoir = indice(fourmiliere, DORTOIR)
    vestibule = indice(fourmiliere, VESTIBULE)
    places = fourmiliere["capacites"]
    taille = len(fourmiliere["salles"])

    def ajouter(depart, arrivee, capacite):
        """Ajoute un arc orienté et fait exister ses deux extrémités."""
        capacites.setdefault(depart, {})[arrivee] = capacite
        capacites.setdefault(arrivee, {})

    for salle in range(taille):
        for pas in range(duree + 1):
            ajouter((ENTREE, salle, pas), (SORTIE, salle, pas), places[salle])
            if pas < duree:
                ajouter((SORTIE, salle, pas), (ENTREE, salle, pas + 1), places[salle])

    for depart in range(taille):
        for arrivee in voisins(fourmiliere, depart):
            if depart == dortoir or arrivee == vestibule:
                continue
            for pas in range(duree):
                ajouter((SORTIE, depart, pas), (ENTREE, arrivee, pas + 1), places[arrivee])

    # Toutes les fourmis sont dans le vestibule au temps 0…
    ajouter(SOURCE, (ENTREE, vestibule, 0), fourmiliere["fourmis"])
    # … et ont jusqu'au pas « duree » pour atteindre le dortoir.
    for pas in range(duree + 1):
        ajouter((SORTIE, dortoir, pas), PUITS, fourmiliere["fourmis"])

    return capacites


def chemin_augmentant(residuel: dict, source, puits):
    """Plus court chemin de ``source`` à ``puits`` où il reste de la place.

    Parcours en largeur sur les capacités restantes ; on garde le prédécesseur
    de chaque nœud pour reconstruire le chemin. Renvoie ``None`` s'il n'existe
    plus aucun chemin (le flot est alors maximum).
    """

    precedent = {source: None}
    file = deque([source])
    while file:
        noeud = file.popleft()
        if noeud == puits:
            break
        for voisin, reste in residuel[noeud].items():
            if reste > 0 and voisin not in precedent:
                precedent[voisin] = noeud
                file.append(voisin)

    if puits not in precedent:
        return None

    chemin = []
    noeud = puits
    while noeud != source:
        chemin.append((precedent[noeud], noeud))
        noeud = precedent[noeud]
    return chemin[::-1]


def flot_maximum(capacites: dict, source, puits, limite: int | None = None):
    """Flot maximum par la méthode d'Edmonds-Karp.

    Principe : tant qu'il existe un chemin de ``source`` à ``puits`` dont tous
    les arcs ont encore de la place, on fait passer le long de ce chemin le
    "goulot d'étranglement" (la plus petite capacité restante du chemin). On
    met ensuite à jour les capacités restantes ; pour chaque arc utilisé, on
    autorise aussi l'arc inverse, ce qui permet d'annuler un mauvais choix.

    ``limite`` arrête le calcul dès qu'on a atteint ce nombre d'unités (utile
    pour la question « les F fourmis passent-elles toutes ? »).

    Renvoie ``(valeur, flot)`` : le nombre d'unités arrivées à ``puits`` et le
    flot de chaque arc (``flot[noeud][voisin]``).
    """

    # Capacités restantes : les capacités du réseau, plus un arc arrière
    # de capacité nulle pour chaque arc existant.
    residuel: dict = {}
    for noeud, sorties in capacites.items():
        residuel[noeud] = dict(sorties)
    for noeud, sorties in capacites.items():
        for voisin in sorties:
            residuel[voisin].setdefault(noeud, 0)

    valeur = 0
    while limite is None or valeur < limite:
        chemin = chemin_augmentant(residuel, source, puits)
        if chemin is None:
            break  # plus aucun chemin : le flot est maximum

        marge = min(residuel[depart][arrivee] for depart, arrivee in chemin)
        if limite is not None:
            marge = min(marge, limite - valeur)

        for depart, arrivee in chemin:
            residuel[depart][arrivee] -= marge
            residuel[arrivee][depart] += marge
        valeur += marge

    flot: dict = {}
    for noeud, sorties in capacites.items():
        flot[noeud] = {}
        for voisin, capacite in sorties.items():
            flot[noeud][voisin] = capacite - residuel[noeud][voisin]

    return valeur, flot


def plan_possible(fourmiliere: dict, duree: int) -> bool:
    """Les F fourmis peuvent-elles toutes être au dortoir en ``duree`` étapes ?

    C'est la question à laquelle répond le flot maximum du réseau dilaté :
    si le flot vaut F, un plan existe.
    """

    reseau = reseau_dilate(fourmiliere, duree)
    valeur, _ = flot_maximum(reseau, SOURCE, PUITS, limite=fourmiliere["fourmis"])
    return valeur >= fourmiliere["fourmis"]


def temps_minimal(fourmiliere: dict) -> int:
    """Plus petit nombre d'étapes possible (recherche par dichotomie).

    * borne basse : la distance Sv → Sd (aucune fourmi ne peut arriver plus tôt) ;
    * borne haute : ``distance + F``, toujours réalisable en « pipeline » sur
      un plus court chemin (chaque fourmi part une étape après la précédente).
    """

    if fourmiliere["fourmis"] <= 0:
        return 0

    depart = indice(fourmiliere, VESTIBULE)
    arrivee = indice(fourmiliere, DORTOIR)
    borne_basse = distances(fourmiliere, depart)[arrivee]
    borne_haute = borne_basse + fourmiliere["fourmis"]

    while borne_basse < borne_haute:
        milieu = (borne_basse + borne_haute) // 2
        if plan_possible(fourmiliere, milieu):
            borne_haute = milieu
        else:
            borne_basse = milieu + 1
    return borne_basse


def resoudre_optimal(fourmiliere: dict) -> dict:
    """Planning optimal (durée minimale), par flot maximum.

    Renvoie le même genre de dictionnaire que ``resoudre_glouton`` :
    ``{"duree", "etapes", "etats"}``.
    """

    duree = temps_minimal(fourmiliere)
    vestibule = indice(fourmiliere, VESTIBULE)
    depart = vestibule
    etats = [[depart] * fourmiliere["fourmis"]]
    if duree == 0:
        return {"duree": 0, "etapes": [], "etats": etats}

    reseau = reseau_dilate(fourmiliere, duree)
    valeur, flot = flot_maximum(reseau, SOURCE, PUITS)
    if valeur < fourmiliere["fourmis"]:
        raise ErreurFourmiliere(f"{fourmiliere['nom']} : aucune solution en {duree} étapes")

    # Combien de fourmis traversent chaque tunnel à chaque pas ?
    passages = {}
    for noeud, sorties in flot.items():
        if not isinstance(noeud, tuple) or noeud[0] != SORTIE:
            continue  # nœud SOURCE ou PUITS
        _, salle, pas = noeud
        for arrivee, quantite in sorties.items():
            if quantite > 0 and arrivee[0] == ENTREE and arrivee[1] != salle:
                passages[(pas, salle, arrivee[1])] = quantite

    etapes, etats = derouler(fourmiliere, duree, passages)
    return {"duree": duree, "etapes": etapes, "etats": etats}


def derouler(fourmiliere: dict, duree: int, passages: dict):
    """Transforme le flot en mouvements de fourmis numérotées.

    À chaque pas, chaque tunnel reçoit un certain nombre de fourmis (donné par
    le flot) ; comme les fourmis sont interchangeables, on choisit lesquelles
    des fourmis présentes dans la salle traversent le tunnel, les autres
    attendent sur place.
    """

    taille = len(fourmiliere["salles"])
    vestibule = indice(fourmiliere, VESTIBULE)
    position = [vestibule] * fourmiliere["fourmis"]
    etats = [list(position)]
    etapes = []

    for pas in range(duree):
        debut_etape = list(position)
        mouvements = []

        for salle in range(taille):
            destinations = []
            for voisine in range(taille):
                destinations += [voisine] * passages.get((pas, salle, voisine), 0)

            presentes = [i for i, pos in enumerate(debut_etape) if pos == salle]
            if len(destinations) > len(presentes):
                raise ErreurFourmiliere(
                    f"{fourmiliere['nom']} : incohérence du flot au pas {pas + 1}"
                )

            for fourmi, arrivee in zip(presentes, destinations):
                mouvements.append((fourmi, salle, arrivee))

        # Tous les mouvements de l'étape ont lieu en même temps.
        for fourmi, _, arrivee in mouvements:
            position[fourmi] = arrivee

        for salle in range(taille):
            dedans = sum(1 for pos in position if pos == salle)
            if dedans > fourmiliere["capacites"][salle]:
                raise ErreurFourmiliere(
                    f"{fourmiliere['nom']} : capacité de "
                    f"{fourmiliere['salles'][salle]} dépassée au pas {pas + 1}"
                )

        etapes.append(sorted((fourmi + 1, depart, arrivee) for fourmi, depart, arrivee in mouvements))
        etats.append(list(position))

    dortoir = indice(fourmiliere, DORTOIR)
    if any(pos != dortoir for pos in position):
        raise ErreurFourmiliere(
            f"{fourmiliere['nom']} : toutes les fourmis n'ont pas atteint le dortoir"
        )
    return etapes, etats


# ---------------------------------------------------------------------------
# 5. Vérification et mise en forme
# ---------------------------------------------------------------------------


def verifier_planning(fourmiliere: dict, etapes: list[list[tuple]]) -> int:
    """Rejoue le planning et vérifie les règles une par une.

    * chaque fourmi est numérotée entre 1 et F ;
    * une fourmi ne se déplace qu'une fois par étape ;
    * elle part bien de la salle où elle se trouve ;
    * le tunnel emprunté existe bien dans la matrice d'adjacence ;
    * aucune capacité n'est dépassée à la fin d'une étape ;
    * à la fin, toute la colonie est au dortoir.

    Renvoie le nombre d'étapes si tout est correct, lève une
    :class:`ErreurFourmiliere` sinon.
    """

    dortoir = indice(fourmiliere, DORTOIR)
    vestibule = indice(fourmiliere, VESTIBULE)
    position = {fourmi: vestibule for fourmi in range(1, fourmiliere["fourmis"] + 1)}

    for numero, etape in enumerate(etapes, start=1):
        deja_deplacees = set()
        deplacements = {}

        for fourmi, depart, arrivee in etape:
            if not 1 <= fourmi <= fourmiliere["fourmis"]:
                raise ErreurFourmiliere(f"étape {numero} : fourmi inconnue f{fourmi}")
            if fourmi in deja_deplacees:
                raise ErreurFourmiliere(f"étape {numero} : f{fourmi} se déplace deux fois")
            deja_deplacees.add(fourmi)
            if position[fourmi] != depart:
                raise ErreurFourmiliere(
                    f"étape {numero} : f{fourmi} est en "
                    f"{fourmiliere['salles'][position[fourmi]]}, pas en "
                    f"{fourmiliere['salles'][depart]}"
                )
            if fourmiliere["matrice"][depart][arrivee] != 1:
                raise ErreurFourmiliere(
                    f"étape {numero} : pas de tunnel entre "
                    f"{fourmiliere['salles'][depart]} et {fourmiliere['salles'][arrivee]}"
                )
            deplacements[fourmi] = arrivee

        for fourmi, arrivee in deplacements.items():
            position[fourmi] = arrivee

        for salle, nombre in Counter(position.values()).items():
            if nombre > fourmiliere["capacites"][salle]:
                raise ErreurFourmiliere(
                    f"étape {numero} : {fourmiliere['salles'][salle]} accueille {nombre} fourmis "
                    f"(capacité {fourmiliere['capacites'][salle]})"
                )

    for fourmi, salle in position.items():
        if salle != dortoir:
            raise ErreurFourmiliere(f"f{fourmi} n'est pas au dortoir à la fin du planning")
    return len(etapes)


def format_planning(fourmiliere: dict, etapes: list[list[tuple]]) -> str:
    """Planning au format papier : ``+++ E1 +++`` puis ``f1 - Sv - S1``."""

    salles = fourmiliere["salles"]
    lignes = []
    for numero, etape in enumerate(etapes, start=1):
        lignes.append(f"+++ E{numero} +++")
        for fourmi, depart, arrivee in etape:
            lignes.append(f"f{fourmi} - {salles[depart]} - {salles[arrivee]}")
    return "\n".join(lignes)


def lire_planning(fourmiliere: dict, texte: str) -> list[list[tuple]]:
    """Relit un planning écrit au format « +++ E1 +++ » et « f1 - Sv - S1 ».

    Les noms de salles sont retraduits en numéros grâce à la fourmilière.
    Sert à re-vérifier un planning déjà enregistré dans ``solutions/``.
    """

    etapes = []
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        if ligne.startswith("+++"):
            etapes.append([])
            continue
        if not etapes:
            continue  # ligne d'en-tête du fichier (résumé de la fourmilière)

        morceaux = [morceau.strip() for morceau in ligne.split("-")]
        if len(morceaux) != 3:
            raise ErreurFourmiliere(f"ligne de planning incomprise : {ligne!r}")
        fourmi, depart, arrivee = morceaux
        if not fourmi.startswith("f") or not fourmi[1:].isdigit():
            raise ErreurFourmiliere(f"ligne de planning incomprise : {ligne!r}")
        etapes[-1].append((int(fourmi[1:]), indice(fourmiliere, depart), indice(fourmiliere, arrivee)))
    return etapes
