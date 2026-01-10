"""
Gerador de gráficos para análise de performance de algoritmos.
Cria visualizações comparativas de tempo e memória.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sem GUI para gerar arquivos
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import csv


class PlotGenerator:
    """Gera gráficos de análise de performance."""
    
    def __init__(self, output_dir: str = "results/plots"):
        """
        Args:
            output_dir: diretório para salvar os gráficos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
        
    def plot_time_comparison(
        self,
        results: List[Dict],
        save_name: str = "time_comparison.png"
    ):
        """
        Gera gráfico comparando tempos de execução.
        
        Args:
            results: lista de resultados de experimentos
            save_name: nome do arquivo de saída
        """
        # Organizar dados por densidade
        densities = ['sparse', 'medium', 'dense']
        data_by_density = {d: {'n': [], 'bt': [], 'h': []} for d in densities}
        
        for result in results:
            density = result['density']
            n = result['n']
            stats = result['statistics']
            
            data_by_density[density]['n'].append(n)
            data_by_density[density]['bt'].append(stats['bt_avg_time'])
            data_by_density[density]['h'].append(stats['h_avg_time'])
        
        # Criar subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle('Comparação de Tempo de Execução', fontsize=16, fontweight='bold')
        
        colors = {'bt': '#FF6B6B', 'h': '#4ECDC4'}
        
        for idx, density in enumerate(densities):
            ax = axes[idx]
            data = data_by_density[density]
            
            if data['n']:  # Se há dados
                ax.plot(data['n'], data['bt'], 'o-', 
                       label='Backtracking', color=colors['bt'], linewidth=2, markersize=8)
                ax.plot(data['n'], data['h'], 's-', 
                       label='Heurística', color=colors['h'], linewidth=2, markersize=8)
                
                ax.set_xlabel('Número de Vértices (n)', fontsize=12)
                ax.set_ylabel('Tempo (segundos)', fontsize=12)
                ax.set_title(f'Densidade: {density.capitalize()}', fontsize=14, fontweight='bold')
                ax.legend(fontsize=10)
                ax.grid(True, alpha=0.3)
                ax.set_yscale('log')
        
        plt.tight_layout()
        output_path = self.output_dir / save_name
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Gráfico salvo: {output_path}")
        return str(output_path)
    
    def plot_memory_comparison(
        self,
        results: List[Dict],
        save_name: str = "memory_comparison.png"
    ):
        """
        Gera gráfico comparando uso de memória.
        
        Args:
            results: lista de resultados de experimentos
            save_name: nome do arquivo de saída
        """
        # Organizar dados
        densities = ['sparse', 'medium', 'dense']
        data_by_density = {d: {'n': [], 'bt': [], 'h': []} for d in densities}
        
        for result in results:
            if 'memory_stats' in result:
                density = result['density']
                n = result['n']
                mem = result['memory_stats']
                
                data_by_density[density]['n'].append(n)
                data_by_density[density]['bt'].append(mem.get('bt_avg_memory', 0))
                data_by_density[density]['h'].append(mem.get('h_avg_memory', 0))
        
        # Criar subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle('Comparação de Uso de Memória', fontsize=16, fontweight='bold')
        
        colors = {'bt': '#FF6B6B', 'h': '#4ECDC4'}
        
        for idx, density in enumerate(densities):
            ax = axes[idx]
            data = data_by_density[density]
            
            if data['n']:  # Se há dados
                ax.bar(np.array(data['n']) - 0.2, data['bt'], 
                      width=0.4, label='Backtracking', color=colors['bt'], alpha=0.8)
                ax.bar(np.array(data['n']) + 0.2, data['h'], 
                      width=0.4, label='Heurística', color=colors['h'], alpha=0.8)
                
                ax.set_xlabel('Número de Vértices (n)', fontsize=12)
                ax.set_ylabel('Memória (MB)', fontsize=12)
                ax.set_title(f'Densidade: {density.capitalize()}', fontsize=14, fontweight='bold')
                ax.legend(fontsize=10)
                ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.output_dir / save_name
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Gráfico salvo: {output_path}")
        return str(output_path)
    
    def plot_speedup(
        self,
        results: List[Dict],
        save_name: str = "speedup.png"
    ):
        """
        Gera gráfico de speedup (BT/Heurística).
        
        Args:
            results: lista de resultados de experimentos
            save_name: nome do arquivo de saída
        """
        # Organizar dados
        densities = ['sparse', 'medium', 'dense']
        data_by_density = {d: {'n': [], 'speedup': []} for d in densities}
        
        for result in results:
            density = result['density']
            n = result['n']
            stats = result['statistics']
            
            if stats['h_avg_time'] > 0:
                speedup = stats['bt_avg_time'] / stats['h_avg_time']
                data_by_density[density]['n'].append(n)
                data_by_density[density]['speedup'].append(speedup)
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle('Speedup: Backtracking / Heurística', fontsize=16, fontweight='bold')
        
        colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
        markers = ['o', 's', '^']
        
        for idx, density in enumerate(densities):
            data = data_by_density[density]
            if data['n']:
                ax.plot(data['n'], data['speedup'], 
                       marker=markers[idx], label=density.capitalize(),
                       color=colors[idx], linewidth=2, markersize=10)
        
        ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, label='Sem diferença')
        ax.set_xlabel('Número de Vértices (n)', fontsize=12)
        ax.set_ylabel('Speedup (x vezes)', fontsize=12)
        ax.set_title('Quanto maior, mais rápida é a Heurística', fontsize=11, style='italic')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        plt.tight_layout()
        output_path = self.output_dir / save_name
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Gráfico salvo: {output_path}")
        return str(output_path)
    
    def plot_success_rate(
        self,
        results: List[Dict],
        save_name: str = "success_rate.png"
    ):
        """
        Gera gráfico de taxa de sucesso dos algoritmos.
        
        Args:
            results: lista de resultados de experimentos
            save_name: nome do arquivo de saída
        """
        # Organizar dados
        n_values = sorted(set(r['n'] for r in results))
        densities = ['sparse', 'medium', 'dense']
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Taxa de Sucesso dos Algoritmos', fontsize=16, fontweight='bold')
        
        colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
        
        # Backtracking
        ax = axes[0]
        for idx, density in enumerate(densities):
            data = {'n': [], 'rate': []}
            for result in results:
                if result['density'] == density:
                    data['n'].append(result['n'])
                    data['rate'].append(result['statistics']['bt_success_rate'] * 100)
            
            if data['n']:
                ax.plot(data['n'], data['rate'], 'o-', 
                       label=density.capitalize(), color=colors[idx], 
                       linewidth=2, markersize=8)
        
        ax.set_xlabel('Número de Vértices (n)', fontsize=12)
        ax.set_ylabel('Taxa de Sucesso (%)', fontsize=12)
        ax.set_title('Backtracking', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 105])
        
        # Heurística
        ax = axes[1]
        for idx, density in enumerate(densities):
            data = {'n': [], 'rate': []}
            for result in results:
                if result['density'] == density:
                    data['n'].append(result['n'])
                    data['rate'].append(result['statistics']['h_success_rate'] * 100)
            
            if data['n']:
                ax.plot(data['n'], data['rate'], 's-', 
                       label=density.capitalize(), color=colors[idx], 
                       linewidth=2, markersize=8)
        
        ax.set_xlabel('Número de Vértices (n)', fontsize=12)
        ax.set_ylabel('Taxa de Sucesso (%)', fontsize=12)
        ax.set_title('Heurística', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 105])
        
        plt.tight_layout()
        output_path = self.output_dir / save_name
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Gráfico salvo: {output_path}")
        return str(output_path)
    
    def generate_all_plots(self, results: List[Dict]) -> List[str]:
        """
        Gera todos os gráficos de uma vez.
        
        Args:
            results: lista de resultados de experimentos
            
        Returns:
            Lista de caminhos dos gráficos gerados
        """
        print("\nGerando gráficos...")
        
        plots = []
        plots.append(self.plot_time_comparison(results))
        plots.append(self.plot_speedup(results))
        plots.append(self.plot_success_rate(results))
        
        # Apenas se houver dados de memória
        if any('memory_stats' in r for r in results):
            plots.append(self.plot_memory_comparison(results))
        
        print(f"\n✓ {len(plots)} gráficos gerados em: {self.output_dir}")
        return plots


def load_results_from_csv(csv_path: str) -> List[Dict]:
    """
    Carrega resultados de um arquivo CSV para gerar gráficos.
    
    Args:
        csv_path: caminho do arquivo CSV
        
    Returns:
        Lista de dicionários com resultados agregados
    """
    results = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            key = (int(row['n']), row['densidade'])
            
            if key not in results:
                results[key] = {
                    'n': int(row['n']),
                    'density': row['densidade'],
                    'runs': []
                }
            
            results[key]['runs'].append({
                'bt_time': float(row['bt_tempo']),
                'bt_success': bool(int(row['bt_sucesso'])),
                'bt_steps': int(row['bt_passos']),
                'h_time': float(row['h_tempo']),
                'h_success': bool(int(row['h_sucesso']))
            })
    
    # Calcular estatísticas
    result_list = []
    for (n, density), data in results.items():
        runs = data['runs']
        
        bt_times = [r['bt_time'] for r in runs]
        h_times = [r['h_time'] for r in runs]
        bt_steps = [r['bt_steps'] for r in runs]
        
        data['statistics'] = {
            'bt_avg_time': np.mean(bt_times),
            'bt_success_rate': sum(r['bt_success'] for r in runs) / len(runs),
            'bt_avg_steps': np.mean(bt_steps),
            'h_avg_time': np.mean(h_times),
            'h_success_rate': sum(r['h_success'] for r in runs) / len(runs),
        }
        
        result_list.append(data)
    
    return result_list


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        print(f"Carregando dados de: {csv_file}")
        
        results = load_results_from_csv(csv_file)
        generator = PlotGenerator()
        generator.generate_all_plots(results)
    else:
        print("Uso: python plot_generator.py <arquivo.csv>")
