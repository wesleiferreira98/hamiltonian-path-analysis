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


def save_graph(path, n, adj):
    """
    Salva um grafo em arquivo no formato:
    n m
    u v
    u v
    ...
    Args:
        path (str): caminho do arquivo
        n (int): número de vértices
        adj (list[list[int]]): lista de adjacência
    """
    # Contar arestas (cada aresta aparece 2x na lista de adjacência)
    edges = set()
    for u in range(n):
        for v in adj[u]:
            if u < v:  # evitar duplicatas
                edges.add((u, v))
    
    m = len(edges)
    
    with open(path, "w") as f:
        f.write(f"{n} {m}\n")
        for u, v in sorted(edges):
            f.write(f"{u} {v}\n")

