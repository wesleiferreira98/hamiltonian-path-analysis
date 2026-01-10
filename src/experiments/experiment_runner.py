# src/experiments/experiment_runner.py
"""
Módulo para execução de experimentos sistemáticos.
Mede tempo, passos, taxas de sucesso, memória para diferentes configurações.
"""

import time
import csv
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import sys
import os
import warnings

# Adicionar o diretório raiz ao path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.algorithms.backtracking import find_hamiltonian_path_bt
from src.algorithms.heuristic import heuristic_path
from src.utils.performance_monitor import PerformanceMonitor, TimeoutError


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
    
    def __init__(self, timeout_seconds: int = 60, measure_memory: bool = True):
        """
        Args:
            timeout_seconds: tempo limite por experimento individual (padrão: 60s)
            measure_memory: se deve medir consumo de memória
        """
        self.results: List[Dict] = []
        self.timeout_seconds = timeout_seconds
        self.measure_memory = measure_memory
        self.monitor = PerformanceMonitor(timeout_seconds=timeout_seconds)
        
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
            
            # --- Backtracking com monitoramento ---
            bt_result, bt_perf = self.monitor.measure_function(
                find_hamiltonian_path_bt, n, edges, collect_stats=True
            )
            
            if bt_perf['success']:
                path_bt, stats_bt = bt_result if bt_result else (None, {"steps": 0})
            else:
                path_bt, stats_bt = None, {"steps": 0}
                if bt_perf.get('timeout'):
                    warnings.warn(f"Backtracking TIMEOUT em n={n}, run={run_id}")

            # --- Heurística com monitoramento ---
            h_result, h_perf = self.monitor.measure_function(
                heuristic_path, n, edges
            )
            path_h = h_result if h_perf['success'] else None

            run_data = {
                "run_id": run_id,
                "num_edges": len(edges),
                "bt_time": bt_perf['time_seconds'],
                "bt_success": path_bt is not None and not bt_perf.get('timeout'),
                "bt_steps": stats_bt.get("steps", 0) if stats_bt else 0,
                "bt_path": path_bt,
                "bt_timeout": bt_perf.get('timeout', False),
                "bt_memory_mb": bt_perf.get('memory_mb', 0),
                "bt_peak_memory_mb": bt_perf.get('peak_memory_mb', 0),
                "h_time": h_perf['time_seconds'],
                "h_success": path_h is not None,
                "h_path": path_h,
                "h_memory_mb": h_perf.get('memory_mb', 0),
                "h_peak_memory_mb": h_perf.get('peak_memory_mb', 0),
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
        bt_times = [r["bt_time"] for r in runs if not r.get("bt_timeout")]
        h_times = [r["h_time"] for r in runs]
        bt_steps = [r["bt_steps"] for r in runs]
        bt_memory = [r.get("bt_memory_mb", 0) for r in runs]
        h_memory = [r.get("h_memory_mb", 0) for r in runs]
        
        bt_success_count = sum(1 for r in runs if r["bt_success"])
        h_success_count = sum(1 for r in runs if r["h_success"])
        bt_timeout_count = sum(1 for r in runs if r.get("bt_timeout", False))
        
        total = len(runs)
        
        return {
            "bt_avg_time": sum(bt_times) / len(bt_times) if bt_times else 0,
            "bt_min_time": min(bt_times) if bt_times else 0,
            "bt_max_time": max(bt_times) if bt_times else 0,
            "bt_success_rate": bt_success_count / total if total > 0 else 0,
            "bt_timeout_count": bt_timeout_count,
            "bt_avg_steps": sum(bt_steps) / total if total > 0 else 0,
            "bt_min_steps": min(bt_steps) if bt_steps else 0,
            "bt_max_steps": max(bt_steps) if bt_steps else 0,
            "bt_avg_memory": sum(bt_memory) / total if total > 0 else 0,
            
            "h_avg_time": sum(h_times) / total if total > 0 else 0,
            "h_min_time": min(h_times) if h_times else 0,
            "h_max_time": max(h_times) if h_times else 0,
            "h_success_rate": h_success_count / total if total > 0 else 0,
            "h_avg_memory": sum(h_memory) / total if total > 0 else 0,
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
                'bt_tempo', 'bt_sucesso', 'bt_timeout', 'bt_passos', 'bt_memoria_mb',
                'h_tempo', 'h_sucesso', 'h_memoria_mb'
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
                        1 if run.get('bt_timeout', False) else 0,
                        run['bt_steps'],
                        f"{run.get('bt_memory_mb', 0):.4f}",
                        f"{run['h_time']:.6f}",
                        1 if run['h_success'] else 0,
                        f"{run.get('h_memory_mb', 0):.4f}"
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
    
    def generate_plots(self, output_dir: str = "results/plots"):
        """Gera gráficos dos resultados."""
        try:
            from src.utils.plot_generator import PlotGenerator
            
            # Adicionar estatísticas de memória aos resultados
            for result in self.results:
                if 'statistics' in result:
                    if 'memory_stats' not in result:
                        result['memory_stats'] = {
                            'bt_avg_memory': result['statistics'].get('bt_avg_memory', 0),
                            'h_avg_memory': result['statistics'].get('h_avg_memory', 0)
                        }
            
            generator = PlotGenerator(output_dir)
            return generator.generate_all_plots(self.results)
        except ImportError as e:
            warnings.warn(f"Erro ao gerar gráficos: {e}. Instale matplotlib: pip install matplotlib")
            return []

