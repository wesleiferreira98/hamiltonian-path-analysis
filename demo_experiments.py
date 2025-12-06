#!/usr/bin/env python3
"""
Script de demonstração do módulo de experimentos.
Executa um batch de experimentos e exporta os resultados.
"""

import sys
import os

# Adicionar o diretório raiz ao path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.experiments.experiment_runner import ExperimentRunner


def main():
    print("=" * 80)
    print("DEMO: Módulo de Experimentos - Análise de Caminhos Hamiltonianos")
    print("=" * 80)
    print()
    
    # Criar runner
    runner = ExperimentRunner()
    
    # Configurações
    sizes = [10, 15, 20]
    densities = ['sparse', 'medium', 'dense']
    repetitions = 3
    
    print(f"Configuração:")
    print(f"  Tamanhos: {sizes}")
    print(f"  Densidades: {densities}")
    print(f"  Repetições por configuração: {repetitions}")
    print()
    
    # Executar batch
    print("Executando experimentos...")
    print("-" * 80)
    
    total = len(sizes) * len(densities)
    current = 0
    
    for n in sizes:
        for density in densities:
            current += 1
            print(f"[{current}/{total}] n={n}, densidade={density}...", end=" ")
            result = runner.run_single_experiment(n, density, repetitions)
            stats = result['statistics']
            print(f"✓ (BT: {stats['bt_avg_time']:.4f}s, H: {stats['h_avg_time']:.4f}s)")
    
    print()
    print("-" * 80)
    print("Experimentos concluídos!")
    print()
    
    # Mostrar sumário
    print(runner.get_summary_table())
    print()
    
    # Exportar para CSV
    output_file = os.path.join(PROJECT_ROOT, "results", "demo_experiments.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    runner.export_to_csv(output_file)
    print(f"Resultados exportados para: {output_file}")
    print()
    
    # Estatísticas detalhadas
    print("=" * 80)
    print("ANÁLISE DETALHADA")
    print("=" * 80)
    
    for result in runner.results:
        stats = result['statistics']
        print(f"\nn={result['n']}, densidade={result['density']}:")
        print(f"  Backtracking:")
        print(f"    Tempo médio: {stats['bt_avg_time']:.6f}s (min: {stats['bt_min_time']:.6f}s, max: {stats['bt_max_time']:.6f}s)")
        print(f"    Taxa de sucesso: {stats['bt_success_rate']:.1%}")
        print(f"    Passos médios: {stats['bt_avg_steps']:.0f} (min: {stats['bt_min_steps']}, max: {stats['bt_max_steps']})")
        print(f"  Heurística:")
        print(f"    Tempo médio: {stats['h_avg_time']:.6f}s (min: {stats['h_min_time']:.6f}s, max: {stats['h_max_time']:.6f}s)")
        print(f"    Taxa de sucesso: {stats['h_success_rate']:.1%}")
        
        # Speedup
        if stats['h_avg_time'] > 0:
            speedup = stats['bt_avg_time'] / stats['h_avg_time']
            print(f"  Speedup (BT/H): {speedup:.2f}x")
    
    print()
    print("=" * 80)
    print("Demo concluída!")
    print("=" * 80)


if __name__ == "__main__":
    main()
