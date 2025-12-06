# src/experiments/experiment_runner.py
"""
Módulo para execução de experimentos sistemáticos.
Mede tempo, passos, taxas de sucesso para diferentes configurações.
"""

import time
import csv
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import sys
import os

# Adicionar o diretório raiz ao path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.algorithms.backtracking import find_hamiltonian_path_bt
from src.algorithms.heuristic import heuristic_path


def generate_graph(n: int, p: float) -> List[Tuple[int, int]]:
    """Gera grafo aleatório com n vértices e probabilidade p."""
    import random
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < p:
                edges.append((u, v))
    return edges


class ExperimentRunner:
    """Gerencia e executa experimentos com grafos hamiltonianos."""
    
    def __init__(self):
        self.results: List[Dict] = []
        
    def run_single_experiment(
        self, 
        n: int, 
        density: str, 
        repetitions: int = 5
    ) -> Dict:
        """
        Executa experimento para um tamanho n e densidade específica.
        
        Args:
            n: número de vértices
            density: 'sparse' (0.2), 'medium' (0.5) ou 'dense' (0.8)
            repetitions: número de repetições
            
        Returns:
            Dicionário com estatísticas agregadas
        """
        density_map = {
            'sparse': 0.2,
            'medium': 0.5,
            'dense': 0.8
        }
        p = density_map.get(density, 0.5)
        
        result = {
            "n": n,
            "density": density,
            "probability": p,
            "repetitions": repetitions,
            "runs": [],
            "timestamp": datetime.now().isoformat()
        }

        for run_id in range(repetitions):
            edges = generate_graph(n, p)
            
            # --- Backtracking ---
            bt_start = time.time()
            path_bt, stats_bt = find_hamiltonian_path_bt(n, edges, collect_stats=True)
            bt_time = time.time() - bt_start

            # --- Heurística ---
            h_start = time.time()
            path_h = heuristic_path(n, edges)
            h_time = time.time() - h_start

            run_data = {
                "run_id": run_id,
                "num_edges": len(edges),
                "bt_time": bt_time,
                "bt_success": path_bt is not None,
                "bt_steps": stats_bt["steps"],
                "bt_path": path_bt,
                "h_time": h_time,
                "h_success": path_h is not None,
                "h_path": path_h,
            }
            
            result["runs"].append(run_data)
        
        # Calcular estatísticas agregadas
        result["statistics"] = self._compute_statistics(result["runs"])
        self.results.append(result)
        
        return result
    
    def run_batch_experiments(
        self,
        sizes: List[int] = [10, 20, 30, 40, 50],
        densities: List[str] = ['sparse', 'medium', 'dense'],
        repetitions: int = 5
    ) -> List[Dict]:
        """
        Executa batch de experimentos para múltiplos tamanhos e densidades.
        
        Args:
            sizes: lista de tamanhos de grafos
            densities: lista de densidades
            repetitions: repetições por configuração
            
        Returns:
            Lista de resultados
        """
        batch_results = []
        
        for n in sizes:
            for density in densities:
                result = self.run_single_experiment(n, density, repetitions)
                batch_results.append(result)
                
        return batch_results
    
    def _compute_statistics(self, runs: List[Dict]) -> Dict:
        """Computa estatísticas agregadas de múltiplas execuções."""
        bt_times = [r["bt_time"] for r in runs]
        h_times = [r["h_time"] for r in runs]
        bt_steps = [r["bt_steps"] for r in runs]
        
        bt_success_count = sum(1 for r in runs if r["bt_success"])
        h_success_count = sum(1 for r in runs if r["h_success"])
        
        total = len(runs)
        
        return {
            "bt_avg_time": sum(bt_times) / total if total > 0 else 0,
            "bt_min_time": min(bt_times) if bt_times else 0,
            "bt_max_time": max(bt_times) if bt_times else 0,
            "bt_success_rate": bt_success_count / total if total > 0 else 0,
            "bt_avg_steps": sum(bt_steps) / total if total > 0 else 0,
            "bt_min_steps": min(bt_steps) if bt_steps else 0,
            "bt_max_steps": max(bt_steps) if bt_steps else 0,
            
            "h_avg_time": sum(h_times) / total if total > 0 else 0,
            "h_min_time": min(h_times) if h_times else 0,
            "h_max_time": max(h_times) if h_times else 0,
            "h_success_rate": h_success_count / total if total > 0 else 0,
        }
    
    def export_to_csv(self, filepath: str):
        """
        Exporta resultados para arquivo CSV.
        
        Args:
            filepath: caminho do arquivo de saída
        """
        if not self.results:
            raise ValueError("Nenhum resultado para exportar")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            writer.writerow([
                'n', 'densidade', 'probabilidade', 'run_id', 
                'num_arestas',
                'bt_tempo', 'bt_sucesso', 'bt_passos',
                'h_tempo', 'h_sucesso'
            ])
            
            # Dados
            for result in self.results:
                n = result['n']
                density = result['density']
                prob = result['probability']
                
                for run in result['runs']:
                    writer.writerow([
                        n, density, prob, run['run_id'],
                        run['num_edges'],
                        f"{run['bt_time']:.6f}", 
                        1 if run['bt_success'] else 0,
                        run['bt_steps'],
                        f"{run['h_time']:.6f}",
                        1 if run['h_success'] else 0
                    ])
    
    def get_summary_table(self) -> str:
        """Retorna tabela formatada com resumo dos resultados."""
        if not self.results:
            return "Nenhum resultado disponível."
        
        lines = []
        lines.append("=" * 100)
        lines.append(f"{'n':<5} {'Dens':<8} {'BT Tempo':<12} {'BT Taxa':<10} {'BT Passos':<12} {'H Tempo':<12} {'H Taxa':<10}")
        lines.append("=" * 100)
        
        for result in self.results:
            stats = result['statistics']
            lines.append(
                f"{result['n']:<5} "
                f"{result['density']:<8} "
                f"{stats['bt_avg_time']:<12.6f} "
                f"{stats['bt_success_rate']:<10.2%} "
                f"{stats['bt_avg_steps']:<12.1f} "
                f"{stats['h_avg_time']:<12.6f} "
                f"{stats['h_success_rate']:<10.2%}"
            )
        
        lines.append("=" * 100)
        return "\n".join(lines)
