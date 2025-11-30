import time
from .graph_generator import generate_graph
from algorithms.backtracking import find_hamiltonian_path_bt
from algorithms.heuristic import heuristic_path

def run_experiment(n, density, repetitions=5):
    results = {
        "n": n,
        "density": density,
        "runs": [],
    }

    for _ in range(repetitions):
        edges = generate_graph(n, density)

        # --- Backtracking ---
        bt_start = time.time()
        path_bt, stats_bt = find_hamiltonian_path_bt(edges, n, collect_stats=True)
        bt_time = time.time() - bt_start

        # --- Heurística ---
        h_start = time.time()
        path_h = heuristic_path(edges, n)
        h_time = time.time() - h_start

        results["runs"].append({
            "edges": len(edges),
            "bt_time": bt_time,
            "bt_success": path_bt is not None,
            "bt_steps": stats_bt["steps"],

            "h_time": h_time,
            "h_success": path_h is not None,
        })

    return results
