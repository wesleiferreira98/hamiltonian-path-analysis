#!/usr/bin/env python3
"""
Hamiltonian Path Analysis - Interface de Linha de Comando
==========================================================

Script principal para análise de caminhos hamiltonianos via terminal.
Não requer dependências de GUI.

Uso:
    python main.py analyze <arquivo_grafo> [--algorithm bt|heur|both]
    python main.py generate <n> <densidade> [--output arquivo]
    python main.py experiment <n> <densidade> [--repetitions N]
    python main.py batch [--sizes N1,N2,...] [--densities sparse,medium,dense]
    python main.py gui (requer PyQt6)
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Adicionar diretório raiz ao path
PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.backtracking import find_hamiltonian_path_bt
from src.algorithms.heuristic import heuristic_path
from src.graph_io import load_graph, save_graph
from src.utils.graph_generator import generate_random_graph
from src.experiments.experiment_runner import ExperimentRunner


# ============================================================================
# CORES PARA TERMINAL (ANSI)
# ============================================================================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


# ============================================================================
# COMANDOS
# ============================================================================

def cmd_analyze(args):
    """Analisa um grafo de arquivo."""
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}ANÁLISE DE CAMINHO HAMILTONIANO{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    # Carregar grafo
    print(f"Carregando grafo: {args.file}")
    try:
        n, adj = load_graph(args.file)
        # Converter adjacência para lista de arestas
        edges = [(u, v) for u in range(n) for v in adj[u] if u < v]
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Grafo carregado: {n} vértices, {len(edges)} arestas\n")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Erro ao carregar grafo: {e}{Colors.ENDC}")
        return 1
    
    # Executar algoritmos
    algorithms = []
    if args.algorithm in ['bt', 'both']:
        algorithms.append(('Backtracking', 'bt'))
    if args.algorithm in ['heur', 'both']:
        algorithms.append(('Heurística', 'heur'))
    
    results = {}
    
    for name, alg in algorithms:
        print(f"{Colors.OKCYAN}Executando {name}...{Colors.ENDC}")
        
        t_start = time.time()
        
        if alg == 'bt':
            path, stats = find_hamiltonian_path_bt(n, edges, collect_stats=True)
            elapsed = time.time() - t_start
            results[name] = {
                'path': path,
                'time': elapsed,
                'steps': stats['steps']
            }
        else:  # heur
            path = heuristic_path(n, edges)
            elapsed = time.time() - t_start
            results[name] = {
                'path': path,
                'time': elapsed,
                'steps': None
            }
        
        if path:
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Caminho encontrado em {elapsed:.6f}s")
            if alg == 'bt':
                print(f"  Passos: {stats['steps']}")
            if args.verbose:
                print(f"  Caminho: {path}")
        else:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Nenhum caminho encontrado ({elapsed:.6f}s)")
        print()
    
    # Resumo comparativo
    if len(results) > 1:
        print(f"{Colors.HEADER}{'-'*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}COMPARAÇÃO{Colors.ENDC}\n")
        
        for name, result in results.items():
            status = "✓ Sucesso" if result['path'] else "✗ Falhou"
            color = Colors.OKGREEN if result['path'] else Colors.FAIL
            print(f"{name:15} {color}{status}{Colors.ENDC}  Tempo: {result['time']:.6f}s", end="")
            if result['steps']:
                print(f"  Passos: {result['steps']}")
            else:
                print()
        
        # Speedup
        if 'Backtracking' in results and 'Heurística' in results:
            bt_time = results['Backtracking']['time']
            h_time = results['Heurística']['time']
            if h_time > 0:
                speedup = bt_time / h_time
                print(f"\nSpeedup (BT/H): {Colors.BOLD}{speedup:.2f}x{Colors.ENDC}")
    
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    return 0


def cmd_generate(args):
    """Gera um grafo aleatório."""
    print(f"{Colors.HEADER}GERAÇÃO DE GRAFO ALEATÓRIO{Colors.ENDC}\n")
    
    n = args.n
    density_map = {'sparse': 0.2, 'medium': 0.5, 'dense': 0.8}
    p = density_map.get(args.density, 0.5)
    
    print(f"Parâmetros:")
    print(f"  Vértices: {n}")
    print(f"  Densidade: {args.density} (p={p})")
    
    edges = generate_random_graph(n, p)
    
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} Grafo gerado: {len(edges)} arestas\n")
    
    if args.output:
        # Converter para formato de adjacência
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        save_graph(args.output, n, adj)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Salvo em: {args.output}")
    else:
        print("Grafo (arestas):")
        for u, v in edges:
            print(f"  {u} -- {v}")
    
    return 0


def cmd_experiment(args):
    """Executa experimento individual."""
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}EXPERIMENTO INDIVIDUAL{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    runner = ExperimentRunner()
    
    print(f"Configuração:")
    print(f"  n = {args.n}")
    print(f"  densidade = {args.density}")
    print(f"  repetições = {args.repetitions}")
    print()
    
    print(f"{Colors.OKCYAN}Executando experimento...{Colors.ENDC}\n")
    
    result = runner.run_single_experiment(args.n, args.density, args.repetitions)
    stats = result['statistics']
    
    print(f"{Colors.OKGREEN}✓ Experimento concluído!{Colors.ENDC}\n")
    print(f"{Colors.BOLD}Resultados:{Colors.ENDC}")
    print(f"\n{Colors.UNDERLINE}Backtracking:{Colors.ENDC}")
    print(f"  Tempo médio:     {stats['bt_avg_time']:.6f}s")
    print(f"  Tempo min/max:   {stats['bt_min_time']:.6f}s / {stats['bt_max_time']:.6f}s")
    print(f"  Taxa de sucesso: {stats['bt_success_rate']:.1%}")
    print(f"  Passos médios:   {stats['bt_avg_steps']:.0f}")
    print(f"  Passos min/max:  {stats['bt_min_steps']:.0f} / {stats['bt_max_steps']:.0f}")
    
    print(f"\n{Colors.UNDERLINE}Heurística:{Colors.ENDC}")
    print(f"  Tempo médio:     {stats['h_avg_time']:.6f}s")
    print(f"  Tempo min/max:   {stats['h_min_time']:.6f}s / {stats['h_max_time']:.6f}s")
    print(f"  Taxa de sucesso: {stats['h_success_rate']:.1%}")
    
    if stats['h_avg_time'] > 0:
        speedup = stats['bt_avg_time'] / stats['h_avg_time']
        print(f"\n{Colors.BOLD}Speedup (BT/H): {speedup:.2f}x{Colors.ENDC}")
    
    if args.output:
        runner.export_to_csv(args.output)
        print(f"\n{Colors.OKGREEN}✓{Colors.ENDC} Resultados exportados para: {args.output}")
    
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    return 0


def cmd_batch(args):
    """Executa batch de experimentos."""
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}BATCH DE EXPERIMENTOS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    runner = ExperimentRunner()
    
    # Parse tamanhos
    if args.sizes:
        sizes = [int(x.strip()) for x in args.sizes.split(',')]
    else:
        sizes = [10, 20, 30, 40, 50]
    
    # Parse densidades
    if args.densities:
        densities = [x.strip() for x in args.densities.split(',')]
    else:
        densities = ['sparse', 'medium', 'dense']
    
    print(f"Configuração:")
    print(f"  Tamanhos: {sizes}")
    print(f"  Densidades: {densities}")
    print(f"  Repetições: {args.repetitions}")
    print(f"  Total de experimentos: {len(sizes) * len(densities)}")
    print()
    
    total = len(sizes) * len(densities)
    current = 0
    
    for n in sizes:
        for density in densities:
            current += 1
            print(f"{Colors.OKCYAN}[{current}/{total}]{Colors.ENDC} n={n}, densidade={density}...", end=" ", flush=True)
            
            result = runner.run_single_experiment(n, density, args.repetitions)
            stats = result['statistics']
            
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} (BT: {stats['bt_avg_time']:.4f}s, H: {stats['h_avg_time']:.4f}s)")
    
    print(f"\n{Colors.OKGREEN}✓ Batch concluído!{Colors.ENDC}\n")
    
    # Mostrar sumário
    print(runner.get_summary_table())
    
    # Exportar
    if args.output:
        runner.export_to_csv(args.output)
        print(f"\n{Colors.OKGREEN}✓{Colors.ENDC} Resultados exportados para: {args.output}")
    
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    return 0


def cmd_gui(args):
    """Inicia interface gráfica."""
    try:
        from src.gui.main_window import main as gui_main
        print(f"{Colors.OKCYAN}Iniciando interface gráfica...{Colors.ENDC}")
        return gui_main()
    except ImportError as e:
        print(f"{Colors.FAIL}✗ Erro: Dependências de GUI não instaladas.{Colors.ENDC}\n")
        print("Para usar a interface gráfica, instale as dependências:")
        print(f"  {Colors.BOLD}pip install -r requirements-gui.txt{Colors.ENDC}\n")
        print("Ou use a interface de linha de comando (veja 'python main.py --help')")
        return 1


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Hamiltonian Path Analysis - Análise de caminhos hamiltonianos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Analisar grafo de arquivo
  python main.py analyze instances/auto_n10_p05.txt
  python main.py analyze instances/auto_n10_p05.txt --algorithm both -v
  
  # Gerar grafo aleatório
  python main.py generate 20 medium --output meu_grafo.txt
  
  # Executar experimento
  python main.py experiment 30 sparse --repetitions 10 --output results.csv
  
  # Executar batch
  python main.py batch --sizes 10,20,30 --densities sparse,dense --output batch.csv
  
  # Interface gráfica (requer PyQt6)
  python main.py gui
        """
    )
    
    parser.add_argument('--no-color', action='store_true', help='Desabilitar cores no terminal')
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Comando: analyze
    parser_analyze = subparsers.add_parser('analyze', help='Analisar grafo de arquivo')
    parser_analyze.add_argument('file', help='Arquivo do grafo')
    parser_analyze.add_argument('-a', '--algorithm', choices=['bt', 'heur', 'both'], 
                                default='both', help='Algoritmo a usar (padrão: both)')
    parser_analyze.add_argument('-v', '--verbose', action='store_true', 
                                help='Mostrar caminho completo')
    
    # Comando: generate
    parser_generate = subparsers.add_parser('generate', help='Gerar grafo aleatório')
    parser_generate.add_argument('n', type=int, help='Número de vértices')
    parser_generate.add_argument('density', choices=['sparse', 'medium', 'dense'], 
                                 help='Densidade do grafo')
    parser_generate.add_argument('-o', '--output', help='Arquivo de saída')
    
    # Comando: experiment
    parser_exp = subparsers.add_parser('experiment', help='Executar experimento individual')
    parser_exp.add_argument('n', type=int, help='Número de vértices')
    parser_exp.add_argument('density', choices=['sparse', 'medium', 'dense'], 
                            help='Densidade do grafo')
    parser_exp.add_argument('-r', '--repetitions', type=int, default=5, 
                            help='Número de repetições (padrão: 5)')
    parser_exp.add_argument('-o', '--output', help='Arquivo CSV de saída')
    
    # Comando: batch
    parser_batch = subparsers.add_parser('batch', help='Executar batch de experimentos')
    parser_batch.add_argument('-s', '--sizes', help='Tamanhos separados por vírgula (padrão: 10,20,30,40,50)')
    parser_batch.add_argument('-d', '--densities', help='Densidades separadas por vírgula (padrão: sparse,medium,dense)')
    parser_batch.add_argument('-r', '--repetitions', type=int, default=5, 
                              help='Número de repetições (padrão: 5)')
    parser_batch.add_argument('-o', '--output', help='Arquivo CSV de saída')
    
    # Comando: gui
    parser_gui = subparsers.add_parser('gui', help='Iniciar interface gráfica (requer PyQt6)')
    
    args = parser.parse_args()
    
    # Desabilitar cores se solicitado
    if args.no_color:
        Colors.disable()
    
    # Executar comando
    if args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'generate':
        return cmd_generate(args)
    elif args.command == 'experiment':
        return cmd_experiment(args)
    elif args.command == 'batch':
        return cmd_batch(args)
    elif args.command == 'gui':
        return cmd_gui(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
