# src/graph_io.py

def load_graph(path):
    """
    Lê um grafo a partir de um arquivo no formato:
    n m
    u v
    u v
    ...
    Retorna:
        n (int): número de vértices
        adj (list[list[int]]): lista de adjacência
    """
    with open(path, "r") as f:
        first_line = f.readline().strip().split()
        n, m = map(int, first_line)

        adj = [[] for _ in range(n)]

        for line in f:
            u, v = map(int, line.strip().split())
            adj[u].append(v)
            adj[v].append(u)  # grafo não-direcionado

    return n, adj
