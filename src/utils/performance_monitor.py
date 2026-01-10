"""
Módulo de monitoramento de performance e memória.
Fornece ferramentas para medir consumo de memória e gerar relatórios detalhados.
"""

import time
import tracemalloc
import psutil
import os
from typing import Dict, Optional, Callable, Any, Tuple
from functools import wraps
import signal


class TimeoutError(Exception):
    """Exceção lançada quando uma função excede o tempo limite."""
    pass


def timeout_handler(signum, frame):
    """Handler para timeout usando signal."""
    raise TimeoutError("Função excedeu o tempo limite")


def with_timeout(seconds: int):
    """
    Decorator para adicionar timeout a uma função.
    
    Args:
        seconds: tempo limite em segundos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Configurar signal alarm (apenas Linux/Unix)
            if os.name != 'nt':  # Não é Windows
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
                try:
                    result = func(*args, **kwargs)
                    signal.alarm(0)  # Cancelar alarme
                    return result
                except TimeoutError:
                    signal.alarm(0)
                    raise
                finally:
                    signal.signal(signal.SIGALRM, old_handler)
            else:
                # No Windows, executar sem timeout
                return func(*args, **kwargs)
        return wrapper
    return decorator


class MemoryMonitor:
    """Monitora consumo de memória de uma operação."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_memory = 0
        self.peak_memory = 0
        self.end_memory = 0
        
    def __enter__(self):
        """Inicia monitoramento ao entrar no contexto."""
        tracemalloc.start()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finaliza monitoramento ao sair do contexto."""
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = peak / 1024 / 1024  # MB
        
    def get_stats(self) -> Dict[str, float]:
        """
        Retorna estatísticas de memória.
        
        Returns:
            Dicionário com uso de memória (em MB)
        """
        return {
            'start_mb': self.start_memory,
            'end_mb': self.end_memory,
            'peak_mb': self.peak_memory,
            'delta_mb': self.end_memory - self.start_memory
        }


class PerformanceMonitor:
    """
    Monitor completo de performance incluindo tempo, memória e estatísticas.
    """
    
    def __init__(self, timeout_seconds: Optional[int] = None):
        """
        Args:
            timeout_seconds: tempo limite opcional para execução
        """
        self.timeout_seconds = timeout_seconds
        self.results = {}
        
    def measure_function(
        self, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Tuple[Any, Dict]:
        """
        Mede performance de uma função incluindo tempo e memória.
        
        Args:
            func: função a ser medida
            *args: argumentos posicionais
            **kwargs: argumentos nomeados
            
        Returns:
            Tupla (resultado, estatísticas)
        """
        stats = {
            'time_seconds': 0,
            'memory_mb': 0,
            'peak_memory_mb': 0,
            'success': False,
            'error': None,
            'timeout': False
        }
        
        result = None
        
        try:
            with MemoryMonitor() as mem:
                start_time = time.time()
                
                if self.timeout_seconds and os.name != 'nt':
                    # Usar timeout apenas em sistemas Unix
                    @with_timeout(self.timeout_seconds)
                    def timed_func():
                        return func(*args, **kwargs)
                    result = timed_func()
                else:
                    result = func(*args, **kwargs)
                
                end_time = time.time()
                
                stats['time_seconds'] = end_time - start_time
                mem_stats = mem.get_stats()
                stats['memory_mb'] = mem_stats['delta_mb']
                stats['peak_memory_mb'] = mem_stats['peak_mb']
                stats['success'] = True
                
        except TimeoutError:
            stats['timeout'] = True
            stats['error'] = 'Timeout'
        except Exception as e:
            stats['error'] = str(e)
            
        return result, stats
    
    def compare_algorithms(
        self,
        algo1: Callable,
        algo2: Callable,
        algo1_name: str = "Algoritmo 1",
        algo2_name: str = "Algoritmo 2",
        *args,
        **kwargs
    ) -> Dict:
        """
        Compara dois algoritmos medindo tempo e memória.
        
        Args:
            algo1: primeiro algoritmo
            algo2: segundo algoritmo
            algo1_name: nome do primeiro algoritmo
            algo2_name: nome do segundo algoritmo
            *args: argumentos para ambos algoritmos
            **kwargs: argumentos nomeados
            
        Returns:
            Dicionário com comparação detalhada
        """
        print(f"Medindo {algo1_name}...", flush=True)
        result1, stats1 = self.measure_function(algo1, *args, **kwargs)
        
        print(f"Medindo {algo2_name}...", flush=True)
        result2, stats2 = self.measure_function(algo2, *args, **kwargs)
        
        comparison = {
            algo1_name: {
                'result': result1,
                'stats': stats1
            },
            algo2_name: {
                'result': result2,
                'stats': stats2
            }
        }
        
        # Calcular speedup e eficiência de memória
        if stats1['success'] and stats2['success']:
            if stats2['time_seconds'] > 0:
                comparison['speedup'] = stats1['time_seconds'] / stats2['time_seconds']
            if stats2['memory_mb'] > 0:
                comparison['memory_ratio'] = stats1['memory_mb'] / stats2['memory_mb']
        
        return comparison
    
    @staticmethod
    def format_stats(stats: Dict) -> str:
        """
        Formata estatísticas para exibição.
        
        Args:
            stats: dicionário de estatísticas
            
        Returns:
            String formatada
        """
        if stats.get('timeout'):
            return "⏱️  TIMEOUT"
        
        if not stats.get('success'):
            return f"❌ ERRO: {stats.get('error', 'Desconhecido')}"
        
        time_str = f"⏱️  {stats['time_seconds']:.6f}s"
        mem_str = f"💾 {stats['memory_mb']:.2f} MB"
        peak_str = f"(pico: {stats['peak_memory_mb']:.2f} MB)"
        
        return f"{time_str}  |  {mem_str} {peak_str}"


def get_system_info() -> Dict[str, Any]:
    """
    Retorna informações do sistema para contexto de experimentos.
    
    Returns:
        Dicionário com informações do sistema
    """
    return {
        'cpu_count': psutil.cpu_count(),
        'cpu_freq_mhz': psutil.cpu_freq().current if psutil.cpu_freq() else None,
        'total_memory_gb': psutil.virtual_memory().total / 1024**3,
        'available_memory_gb': psutil.virtual_memory().available / 1024**3,
        'os': os.name,
        'platform': psutil.os.name if hasattr(psutil, 'os') else 'unknown'
    }


if __name__ == "__main__":
    # Exemplo de uso
    import random
    
    def algorithm_slow(n):
        """Algoritmo lento para teste."""
        result = []
        for i in range(n):
            result.append([j**2 for j in range(1000)])
        return len(result)
    
    def algorithm_fast(n):
        """Algoritmo rápido para teste."""
        return n * 1000
    
    monitor = PerformanceMonitor(timeout_seconds=5)
    
    print("Comparando algoritmos...")
    comparison = monitor.compare_algorithms(
        algorithm_slow,
        algorithm_fast,
        "Lento",
        "Rápido",
        100
    )
    
    print("\nResultados:")
    for name, data in comparison.items():
        if name not in ['speedup', 'memory_ratio']:
            print(f"\n{name}:")
            print(f"  {monitor.format_stats(data['stats'])}")
    
    if 'speedup' in comparison:
        print(f"\nSpeedup: {comparison['speedup']:.2f}x")
