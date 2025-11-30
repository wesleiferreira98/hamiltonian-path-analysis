import time
from typing import Dict, Any

from .graph_generator import generate_graph
from src.backtracking import hamiltonian_path_backtracking
from src.heuristic import heuristic_hamiltonian_path


def run_experiments(
    n: int,
    density: str,
    repetitions: int = 5
) -> Dict[str, Any]:
    """
    Executa múltiplos experimentos e retorna métricas.
    Não imprime nada – sua GUI decide como registrar.
    """

    results = {
        "n": n,
        "density": density,
        "repetitions": repetitions,
        "runs": [],
    }

    for _ in range(repetitions):

        # ------------------------------
        # Gerar grafo
        # ------------------------------
        edges = generate_graph(n, density)

        # Construir adjacência compatível com seu backtracking
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        # ------------------------------
        # Executar Backtracking (EXATO)
        # ------------------------------
        start_bt = time.perf_counter()
        path_bt = hamiltonian_path_backtracking(n, adj)
        end_bt = time.perf_counter()

        # ------------------------------
        # Executar Heurística
        # ------------------------------
        start_h = time.perf_counter()
        path_h = heuristic_hamiltonian_path(n, adj)
        end_h = time.perf_counter()

        # ------------------------------
        # Registrar resultados
        # ------------------------------
        results["runs"].append({
            "edges": len(edges),

            "bt_time": end_bt - start_bt,
            "bt_success": path_bt is not None,

            "h_time": end_h - start_h,
            "h_success": path_h is not None,
        })

    return results
