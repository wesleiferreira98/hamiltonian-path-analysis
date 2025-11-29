# src/heuristic.py
import random

def heuristic_hamiltonian_path(n, adj):
    """
    Heurística:
    - Vértice inicial aleatório.
    - Sempre segue para o vizinho ainda não visitado com menor grau.
    Retorna o caminho ou None.
    """

    order = list(range(n))
    random.shuffle(order)

    for start in order:
        visited = set([start])
        current = start
        path = [start]

        for _ in range(n - 1):
            candidates = [v for v in adj[current] if v not in visited]
            if not candidates:
                break

            # Escolhe vizinho com menor grau
            current = min(candidates, key=lambda x: len(adj[x]))
            visited.add(current)
            path.append(current)

        if len(visited) == n:
            return path

    return None


if __name__ == "__main__":
    from graph_io import load_graph
    n, adj = load_graph("instances/graph10.txt")

    path = heuristic_hamiltonian_path(n, adj)
    print("Heurística:", path if path else "Falhou")
