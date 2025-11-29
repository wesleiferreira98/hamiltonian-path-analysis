# src/backtracking.py

def hamiltonian_path_backtracking(n, adj):
    """
    Versão simples: retorna um caminho Hamiltoniano como lista de vértices
    ou None se não existir.
    (Mantemos esta função para uso em experimentos sem animação.)
    """
    visited = [False] * n
    path = []

    def backtrack(v, depth):
        visited[v] = True
        path.append(v)

        if depth == n:
            return True

        for u in adj[v]:
            if not visited[u]:
                if backtrack(u, depth + 1):
                    return True

        visited[v] = False
        path.pop()
        return False

    for start in range(n):
        if backtrack(start, 1):
            return path.copy()

    return None


def hamiltonian_path_backtracking_steps(n, adj):
    """
    Generator que produz passos do backtracking.
    Yield: (estado, caminho_atual)
      estado ∈ {"start", "visit", "backtrack", "solution", "fail"}
      caminho_atual é uma lista de vértices (parcial ou completa).
    """

    visited = [False] * n
    path = []
    found = False

    def backtrack(v, depth):
        nonlocal found

        visited[v] = True
        path.append(v)
        # descendo na recursão
        yield ("visit", list(path))

        if depth == n:
            found = True
            # solução encontrada
            yield ("solution", list(path))
            return

        for u in adj[v]:
            if found:
                break
            if not visited[u]:
                # explorar vizinho
                yield from backtrack(u, depth + 1)

        # se ainda não achou, faz backtrack
        visited[v] = False
        path.pop()
        yield ("backtrack", list(path))

    # tentar cada vértice como início
    for start in range(n):
        if found:
            break

        # reinicia estruturas a cada nova raiz
        for i in range(n):
            visited[i] = False
        path.clear()

        # começando nova raiz
        yield ("start", [start])
        yield from backtrack(start, 1)

    if not found:
        yield ("fail", [])
