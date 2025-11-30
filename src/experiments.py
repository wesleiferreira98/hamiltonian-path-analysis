# src/experiments.py

import time
from src.graph_io import load_graph
from src.backtracking import hamiltonian_path_backtracking
from src.heuristic import heuristic_hamiltonian_path

def run_experiment(path):
    n, adj = load_graph(path)

    print(f"Executando instância: {path} | n={n}")

    # método exato
    t0 = time.time()
    result_exact = hamiltonian_path_backtracking(n, adj)
    t1 = time.time()

    # heurística
    t2 = time.time()
    result_heur = heuristic_hamiltonian_path(n, adj)
    t3 = time.time()

    print("\nResultados:")
    print(f"Backtracking: {'SIM' if result_exact else 'NÃO'} | Tempo: {t1 - t0:.4f}s")
    print(f"Heurística:   {'SIM' if result_heur else 'NÃO'} | Tempo: {t3 - t2:.4f}s")

    return {
        "exact_time": t1 - t0,
        "heur_time": t3 - t2,
        "exact_result": result_exact,
        "heur_result": result_heur
    }
