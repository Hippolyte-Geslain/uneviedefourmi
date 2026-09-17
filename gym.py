from collections import deque
import networkx as nx
edges = [
    ("Sv","S1"),
    ("S1","S2"),
    ("S1","Sd"),
    ("Sv","S3"),
    ("S3","Sd"),
    ("S2","Sv"),
    ("S2","Sd")
]

adj = [
    [0,1,1,1,0],
    [1,0,1,0,1],
    [1,1,0,0,1],
    [1,0,0,0,1],
    [0,1,1,1,0]
]

def voisins(adj, i):
    return [j for j in range(len(adj))
            if adj[i][j] == 1]


def bfs(G, Sv):
    distances = {Sv:0}
    queue = deque([Sv])
    noeuds_visites = {Sv: None}
    print(queue)
    while queue:
        salle = queue.popleft()
        for voisin in G.neighbors(salle):
            if voisin not in distances:
                distances[voisin] = distances[salle] +1
                noeuds_visites[voisin] = salle
                queue.append(voisin)
                print(queue)
    return distances, noeuds_visites

def chemin(noeuds_visites, Sv, Sd):
    chemin = []
    noeud = Sd

    while noeud is not None:
        chemin.append(noeud)
        noeud = noeuds_visites.get(noeud)
    chemin.reverse()

    if chemin[0] != Sv:
        return []

    return chemin


    
def simuler(G, nb_fourmis):
    pos = {f: "Sv" for f in range(nb_fourmis)}
    print(pos)
    etape = 0
    while not all(
        pos =="Sd"
        for pos in pos.values()
    ):
        etape += 1
        occ = set()
        for f, salle in pos.items():
            if salle == "Sd":
                continue
            for v in G.neighbors(salle):
                if v == "Sd" or v not in occ:
                    pos[f] = v
                    if v != "Sd":
                        occ.add(v)
                    break
    return etape


G = nx.Graph()
G.add_edges_from(edges)
print(list(G.nodes))
print(bfs(G,"Sv"))

distances, noeuds_visites = bfs(G,"Sv")

chemin_trouve = chemin(
    noeuds_visites,
    "Sv",
    "Sd"
)

print(chemin_trouve)