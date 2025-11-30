import random

def generate_graph(n: int, density: str):
    edges = []

    if density == "sparse":
        p = 1.5 / n      # baixa densidade
    elif density == "dense":
        p = 0.30         # mais denso
    else:
        p = random.uniform(0.05, 0.25)

    for u in range(n):
        for v in range(u+1, n):
            if random.random() < p:
                edges.append((u, v))

    return edges
