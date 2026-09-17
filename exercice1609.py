edge = [
    ("Sv", "S1"),
    ("Sv", "S2"),
    ("Sv", "S3"),
    ("S1", "S2"),
    ("S2", "Sd"),
    ("S3", "Sd"),]

import networkx as nx
G = nx.Graph()
G.add_edges_from(edge)

print("Nodes of graph: ")
print(G.nodes())

adj = [
    [0, 1, 1, 1, 0],#Sv
    [1, 0, 1, 0, 1],#S1
    [1, 1, 0, 0, 1],#S2
    [1, 0, 0, 0, 1],#S3
    [0, 1, 1, 1, 1],#Sd
    ]

#Trouver les voisins d'une salle

def voisins(adj, i):
    return[j for j in range(len(adj))
           if adj[i][j] ==1]
#Exemple : voisin de S2(index 2)
print(voisins(adj, 2))
# [0, 1, 4] (Sv, S1, Sd )

#BFS: parcours en largeur (plus court chemin)
from collections import deque

def bfs(G, depart):
    """Retourne la distance (en nombre d'aretes) entre depart et chaque salle."""
    distance = {depart: 0}
    queue = deque([depart])
    while queue:
        salle = queue.popleft()
        for voisin in G.neighbors(salle):
            if voisin not in distance:
                distance[voisin] = distance[salle] + 1
                queue.append(voisin)
    return distance

distances = bfs(G, "Sv")
print("Distances depuis Sv :", distances)
print("Distance Sv -> Sd :", distances["Sd"])

def plus_court_chemin(G, depart, arrivee):
    """Retourne la liste des salles du plus court chemin, ou None si aucun chemin."""
    precedent = {depart: None}
    queue = deque([depart])
    while queue:
        salle = queue.popleft()
        if salle == arrivee:
            break
        for voisin in G.neighbors(salle):
            if voisin not in precedent:
                precedent[voisin] = salle
                queue.append(voisin)
    if arrivee not in precedent:
        return None
    # On remonte les predecesseurs depuis l'arrivee jusqu'au depart
    chemin = []
    salle = arrivee
    while salle is not None:
        chemin.append(salle)
        salle = precedent[salle]
    return chemin[::-1]

chemin = plus_court_chemin(G, "Sv", "Sd")
print("Plus court chemin de Sv a Sd :", chemin)

def simuler(G, nb_fourmis):
    pos = {f: "Sv" for f in range (nb_fourmis)}
    


