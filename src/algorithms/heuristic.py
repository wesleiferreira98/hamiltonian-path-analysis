def heuristic_path(n, edges):
    adj = {i: [] for i in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    for start in range(n):
        path = [start]
        visited = {start}

        current = start
        while len(path) < n:
            candidates = [
                v for v in adj[current]
                if v not in visited
            ]
            if not candidates:
                break

            next_v = min(candidates, key=lambda x: len(adj[x]))
            path.append(next_v)
            visited.add(next_v)
            current = next_v

        if len(path) == n:
            return path

    return None
