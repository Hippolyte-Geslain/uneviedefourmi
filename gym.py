from collections import deque
import networkx as nx 
import matplotlib.pyplot as plt

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
    pos_f = {f: "Sv" for f in range(nb_fourmis)}
    print(pos_f)
    etape = 0
    while not all(
        pos_f =="Sd"
        for pos_f in pos_f.values()
    ):
        etape += 1
        occ = set()
        for f, salle in pos_f.items():
            if salle == "Sd":
                continue
            for v in G.neighbors(salle):
                if v == "Sd" or v not in occ:
                    pos_f[f] = v
                    if v != "Sd":
                        occ.add(v)
                    break
    return etape


def parse_ant_numbers(line):
    """Parse a line such as 'f=50'."""
    if not line.startswith("f="):
        return None

    value = line.split("=", 1)[1].strip()
    return int(value)


def parse_node_capacity(line):
    """Parse a line such as 'S1 { 5 }'."""
    if "{" not in line or "}" not in line:
        return None

    node, capacity = line.split("{", 1)
    capacity = capacity.split("}", 1)[0].strip()
    return node.strip(), int(capacity)


def parse_edge(line):
    """Parse a line such as 'S1 - S2'."""
    if "-" not in line:
        return None

    start, end = line.split("-", 1)
    return start.strip(), end.strip()


def extract_data(filepath):
    ants_nb = None
    nodes_capacity = {}
    edges = []

    with open(filepath, encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line:
                continue

            ant_count = parse_ant_count(line)
            if ant_count is not None:
                ants_nb = ant_count
                continue

            node_data = parse_node_capacity(line)
            if node_data is not None:
                node, capacity = node_data
                nodes_capacity[node] = capacity
                continue

            edge = parse_edge(line)
            if edge is not None:
                edges.append(edge)
                continue

            raise ValueError(f"Ligne non reconnue : {line}")

    if ants_nb is None:
        raise ValueError("Le nombre de fourmis est absent")

    return ants_nb, nodes_capacity, edges


ants_nb, nodes_capacity, edges = extract_data(
    "fourmilieres/fourmiliere_3D.txt"
)
G = nx.Graph()
G.add_edges_from(edges)
nx.set_node_attributes(G, nodes_capacity, "capacity")
print(list(G.nodes))
print(f"Nombre de fourmis : {ants_nb}")
print(f"Capacites : {nodes_capacity}")
print(bfs(G,"Sv"))

pos = nx.spring_layout(G, seed=42)

nx.draw_networkx_edges(G, pos, edge_color="gray", width=2)
nx.draw_networkx_nodes(
    G,
    pos,
    node_color=[
        "seagreen" if node == "Sv" else
        "crimson" if node == "Sd" else
        "skyblue"
        for node in G.nodes
    ],
    node_size=1400,
)
nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold")

plt.title("Graphe des salles")
plt.axis("off")
plt.show()


distances, noeuds_visites = bfs(G,"Sv")

chemin_trouve = chemin(
    noeuds_visites,
    "Sv",
    "Sd"
)

print(chemin_trouve)