# src/utils/graph_generator.py
import random

def generate_random_graph(n, p):
    """
    Gera grafo aleatório de n vértices com probabilidade p de existir aresta.
    p baixo → esparso
    p alto → denso
    """
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < p:
                edges.append((i, j))
    return edges


def save_graph(path, n, edges):
    with open(path, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")
