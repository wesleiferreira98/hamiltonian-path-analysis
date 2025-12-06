# Módulo de Experimentos - Documentação

## Visão Geral

O módulo de experimentos foi implementado para realizar análises sistemáticas e comparativas dos algoritmos de busca de caminhos hamiltonianos (backtracking exato vs heurística).

## Componentes Implementados

### 1. ExperimentRunner (`src/experiments/experiment_runner.py`)

Classe principal para gerenciar e executar experimentos.

#### Funcionalidades:

- **Experimentos individuais**: Executa múltiplas repetições para um tamanho e densidade específicos
- **Batch de experimentos**: Executa experimentos para múltiplos tamanhos e densidades automaticamente
- **Métricas coletadas**:
  - Tempo de execução (backtracking e heurística)
  - Número de passos do backtracking
  - Taxa de sucesso/falha
  - Número de arestas geradas
- **Estatísticas agregadas**:
  - Tempo médio, mínimo e máximo
  - Taxa de sucesso
  - Passos médios, mínimo e máximo
- **Exportação**: Gera arquivo CSV com todos os resultados

#### Exemplo de uso:

```python
from src.experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner()

# Experimento individual
result = runner.run_single_experiment(n=20, density='medium', repetitions=5)

# Batch de experimentos
results = runner.run_batch_experiments(
    sizes=[10, 20, 30, 40, 50],
    densities=['sparse', 'medium', 'dense'],
    repetitions=5
)

# Exportar resultados
runner.export_to_csv('results.csv')

# Ver sumário
print(runner.get_summary_table())
```

### 2. ExperimentsTab (`src/gui/experiments_tab.py`)

Aba completa integrada à GUI com todas as funcionalidades de visualização.

#### Características:

- **Interface dividida em dois painéis**:
  - **Painel de controles** (esquerdo):
    - Configuração de experimentos individuais (n, densidade, repetições)
    - Execução de batch automático (tamanhos padrão: 10, 20, 30, 40, 50)
    - Botões de exportar CSV e limpar resultados
    - Log de execução em tempo real
  
  - **Painel de visualização** (direito) com 3 abas:
    - **Visualização do Grafo**: Reutiliza `GraphCanvas` com todas as funcionalidades (zoom, pan, drag, etc.)
    - **Tabela de Resultados**: Mostra estatísticas agregadas de forma tabular
    - **Sumário**: Exibe relatório formatado em texto

- **Execução assíncrona**: Usa `QThread` para não travar a GUI durante experimentos longos
- **Barra de progresso**: Mostra progresso visual durante batch de experimentos
- **Integração completa**: Mantém todas as funcionalidades de visualização de grafos da aba principal

### 3. Integração no MainWindow

A aba de experimentos foi integrada ao `MainWindow` usando `QTabWidget`:

- **Aba 1**: "Análise de Grafo" - Interface original (análise individual)
- **Aba 2**: "Experimentos" - Nova aba de experimentos sistemáticos

## Métricas e Análises

### Métricas coletadas:

1. **Tempo de execução**:
   - Backtracking exato (em segundos)
   - Heurística (em segundos)

2. **Número de passos**:
   - Contagem total de chamadas recursivas do backtracking

3. **Taxa de sucesso**:
   - Percentual de execuções que encontraram caminho hamiltoniano

4. **Características do grafo**:
   - Número de vértices (n)
   - Densidade (sparse/medium/dense)
   - Número de arestas geradas

### Análises suportadas:

- **Comparação de desempenho**: Tempo backtracking vs heurística
- **Escalabilidade**: Comportamento com diferentes tamanhos (10 a 50 vértices)
- **Impacto da densidade**: Grafos esparsos (p=0.2) vs médios (p=0.5) vs densos (p=0.8)
- **Complexidade prática**: Número de passos do backtracking
- **Eficácia**: Taxas de sucesso dos algoritmos

## Como Usar

### Via GUI:

1. Execute: `python -m src.gui.main_window`
2. Clique na aba "Experimentos"
3. Configure os parâmetros ou use os padrões
4. Clique em "Executar Experimento" ou "Executar Batch"
5. Veja os resultados nas sub-abas (Grafo, Tabela, Sumário)
6. Exporte para CSV se necessário

### Via Script:

Execute o script de demonstração:
```bash
python demo_experiments.py
```

Este script:
- Executa batch de experimentos
- Exibe sumário formatado no terminal
- Exporta resultados para `results/demo_experiments.csv`
- Mostra análise detalhada com speedups

## Formato do CSV

O arquivo CSV exportado contém as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| n | Número de vértices |
| densidade | sparse/medium/dense |
| probabilidade | Valor de p usado (0.2/0.5/0.8) |
| run_id | ID da repetição (0 a N-1) |
| num_arestas | Número de arestas do grafo |
| bt_tempo | Tempo do backtracking (segundos) |
| bt_sucesso | 1 se encontrou caminho, 0 caso contrário |
| bt_passos | Número de passos do backtracking |
| h_tempo | Tempo da heurística (segundos) |
| h_sucesso | 1 se encontrou caminho, 0 caso contrário |

## Configurações Padrão

### Tamanhos padrão:
- 10, 20, 30, 40, 50 vértices

### Densidades:
- **sparse** (esparso): p = 0.2
- **medium** (médio): p = 0.5
- **dense** (denso): p = 0.8

### Repetições:
- Padrão: 5 repetições por configuração
- Configurável: 1 a 100 repetições

## Observações Importantes

1. **Threads**: Experimentos rodam em thread separada para não travar a GUI
2. **Memória**: Todos os resultados ficam em memória até serem exportados ou limpos
3. **Performance**: Experimentos com n > 50 podem ser muito lentos devido à complexidade exponencial do backtracking
4. **Visualização**: O grafo mostrado é da última execução (ainda pode ser melhorado para mostrar grafos específicos)

## Próximas Melhorias Possíveis

- [ ] Gráficos matplotlib integrados (tempo vs n, taxa de sucesso vs densidade, etc.)
- [ ] Salvar/carregar sessões de experimentos
- [ ] Comparação visual lado a lado de múltiplos resultados
- [ ] Filtros e busca na tabela de resultados
- [ ] Exportação em outros formatos (JSON, Excel)
- [ ] Análise estatística avançada (desvio padrão, intervalos de confiança)
- [ ] Cancelamento de experimentos em andamento
- [ ] Histórico de experimentos executados
