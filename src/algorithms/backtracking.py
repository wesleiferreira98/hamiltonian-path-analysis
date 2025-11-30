def find_hamiltonian_path_bt(n, edges, collect_stats=False):
    adj = {i: [] for i in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    visited = [False] * n
    path = []
    stats = {"steps": 0}

    def backtrack(u):
        stats["steps"] += 1
        path.append(u)
        visited[u] = True

        if len(path) == n:
            return True

        for v in adj[u]:
            if not visited[v]:
                if backtrack(v):
                    return True

        visited[u] = False
        path.pop()
        return False

    for start in range(n):
        visited = [False] * n
        path = []
        if backtrack(start):
            return path, stats if collect_stats else path

    return None, stats if collect_stats else None
