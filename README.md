# Hamiltonian Path Analysis

Ferramenta completa para análise de algoritmos de busca de caminhos hamiltonianos em grafos. Compara o desempenho de **backtracking exato** vs **heurística** com monitoramento de memória e geração automática de gráficos.

## Novidades (v2.0)

- **Timeout configurável** - Evita que experimentos travem indefinidamente
- **Monitoramento de memória** - Mede consumo real de RAM de cada algoritmo
- **Gráficos automáticos** - Visualizações comparativas de performance
- **Análise detalhada** - Entenda por que grafos sparse demoram mais
- **Jupyter Notebooks** - Demonstração interativa completa para revisores

Veja [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) para detalhes técnicos.

---

## Início Rápido para Revisores

### Opção 1: Jupyter Notebook (Recomendado!)

**Execute o projeto completo no navegador, sem instalar nada!**

[![https://colab.research.google.com/drive/1mrX705rGVzLQyid573LU9VsN3XYVwueH?usp=sharing](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/wesleiferreira98/hamiltonian-path-analysis/blob/main/notebooks/hamiltonian_path_complete_demo.ipynb)

**Conteúdo do notebook:**

- Implementação completa dos algoritmos
- Exemplos práticos interativos
- Experimentos com visualizações
- Análise de performance
- Explicações detalhadas

Veja [notebooks/README.md](notebooks/README.md) para mais opções.

### Opção 2: Linha de Comando

---

## Uso Rápido (Sem Instalação de GUI)

O projeto funciona **completamente via linha de comando**, sem necessidade de instalar dependências pesadas de interface gráfica.

### Análise de Grafo

```bash
# Analisar grafo de arquivo
./run.sh analyze instances/auto_n10_p05.txt

# Comparar ambos algoritmos com saída detalhada
./run.sh analyze instances/auto_n10_p05.txt --algorithm both -v
```

### Gerar Grafo Aleatório

```bash
# Gerar e salvar
./run.sh generate 20 medium --output meu_grafo.txt

# Gerar e exibir na tela
./run.sh generate 15 sparse
```

### Executar Experimentos

```bash
# Experimento individual com timeout
./run.sh experiment 30 sparse --repetitions 10 --timeout 60 --output results.csv

# Batch com gráficos automáticos 📊
./run.sh batch --sizes 10,20,30 --densities sparse,dense --output batch.csv --plots

# Batch padrão com timeout customizado
./run.sh batch --timeout 120 --output resultados.csv --plots
```

### Demonstração Rápida

```bash
# Executar demo com grafos pequenos (n=10,15,20)
python demo_performance.py

# Demo de monitoramento de memória
python demo_performance.py memory
```

### Ajuda

```bash
# Ver todos os comandos disponíveis
./run.sh --help

# Ajuda específica de um comando
./run.sh analyze --help
./run.sh experiment --help
```

---

## Instalação

### Uso Básico (CLI apenas)

**Python 3.6+ padrão** é suficiente para funcionalidade básica.

```bash
git clone https://github.com/wesleiferreira98/hamiltonian-path-analysis.git
cd hamiltonian-path-analysis
./run.sh --help
```

### Monitoramento de Memória e Gráficos (Recomendado)

Para funcionalidades avançadas (monitoramento de memória e gráficos):

```bash
pip install -r requirements-full.txt
```

Ou apenas o essencial:

```bash
pip install psutil matplotlib
```

### Uso com Interface Gráfica (Opcional)

Se você deseja usar a interface gráfica:

```bash
pip install -r requirements-gui.txt
./run.sh gui
```

Ou diretamente:

```bash
python -m src.gui.main_window
```

---

## Estrutura do Projeto

```
hamiltonian-path-analysis/
├── main.py                    # CLI principal
├── run.sh / run.bat           # Scripts de entrada (Linux/Windows)
├── requirements.txt           # Sem dependências (Python puro)
├── requirements-gui.txt       # Dependências opcionais (PyQt6, matplotlib)
│
├── src/
│   ├── algorithms/            # Algoritmos principais (independentes)
│   │   ├── backtracking.py    # Backtracking exato
│   │   └── heuristic.py       # Heurística gulosa
│   │
│   ├── experiments/           # Módulo de experimentos
│   │   ├── experiment_runner.py
│   │   └── graph_generator.py
│   │
│   ├── gui/                   # Interface gráfica (opcional)
│   │   ├── main_window.py
│   │   ├── experiments_tab.py
│   │   └── ...
│   │
│   ├── utils/                 # Utilitários
│   │   └── graph_generator.py
│   │
│   ├── graph_io.py            # I/O de grafos
│   ├── backtracking.py        # Versão legacy (com animação)
│   └── heuristic.py           # Versão legacy
│
├── instances/                 # Grafos de exemplo
├── results/                   # Resultados de experimentos
└── demo_experiments.py        # Script de demonstração
```

---

## Funcionalidades

### Algoritmos Implementados

1. **Backtracking Exato**

   - Busca exaustiva
   - Garantia de encontrar caminho se existir
   - Coleta estatísticas (número de passos)
   - Complexidade O(n!)
2. **Heurística Gulosa**

   - Escolhe sempre o vértice vizinho com menor grau
   - Rápida mas não garante encontrar solução
   - Complexidade O(n²)

### Métricas Coletadas

- **Tempo de execução** (precisão de microssegundos)
- **Número de passos** do backtracking
- **Taxa de sucesso/falha**
- **Comportamento com diferentes densidades** (sparse/medium/dense)
- **Escalabilidade** (tamanhos de 10 a 50+ vértices)

### Formatos de Saída

- **Terminal**: Saída colorida e formatada
- **CSV**: Dados tabulares para análise
- **Tabelas**: Sumário estatístico
- **GUI**: Visualização gráfica interativa (opcional)

---

## Exemplos de Uso

### 1. Análise Simples

```bash
$ ./run.sh analyze instances/auto_n10_p05.txt

================================================================================
ANÁLISE DE CAMINHO HAMILTONIANO
================================================================================

Carregando grafo: instances/auto_n10_p05.txt
✓ Grafo carregado: 10 vértices, 23 arestas

Executando Backtracking...
✓ Caminho encontrado em 0.000142s
  Passos: 67

Executando Heurística...
✓ Caminho encontrado em 0.000008s

--------------------------------------------------------------------------------
COMPARAÇÃO

Backtracking    ✓ Sucesso  Tempo: 0.000142s  Passos: 67
Heurística      ✓ Sucesso  Tempo: 0.000008s

Speedup (BT/H): 17.75x
================================================================================
```

### 2. Experimento Individual

```bash
$ ./run.sh experiment 20 medium --repetitions 5

================================================================================
EXPERIMENTO INDIVIDUAL
================================================================================

Configuração:
  n = 20
  densidade = medium
  repetições = 5

Executando experimento...

✓ Experimento concluído!

Resultados:

Backtracking:
  Tempo médio:     0.001234s
  Tempo min/max:   0.000987s / 0.001456s
  Taxa de sucesso: 80.0%
  Passos médios:   234
  Passos min/max:  198 / 289

Heurística:
  Tempo médio:     0.000045s
  Tempo min/max:   0.000032s / 0.000056s
  Taxa de sucesso: 60.0%

Speedup (BT/H): 27.42x
================================================================================
```

### 3. Batch de Experimentos

```bash
$ ./run.sh batch --sizes 10,15,20 --densities sparse,dense --repetitions 3

================================================================================
BATCH DE EXPERIMENTOS
================================================================================

Configuração:
  Tamanhos: [10, 15, 20]
  Densidades: ['sparse', 'dense']
  Total de experimentos: 6

[1/6] n=10, densidade=sparse... ✓ (BT: 0.0001s, H: 0.0000s)
[2/6] n=10, densidade=dense... ✓ (BT: 0.0003s, H: 0.0000s)
[3/6] n=15, densidade=sparse... ✓ (BT: 0.0012s, H: 0.0001s)
[4/6] n=15, densidade=dense... ✓ (BT: 0.0034s, H: 0.0001s)
[5/6] n=20, densidade=sparse... ✓ (BT: 0.0089s, H: 0.0002s)
[6/6] n=20, densidade=dense... ✓ (BT: 0.0234s, H: 0.0003s)

✓ Batch concluído!

====================================================================================================
n     Dens     BT Tempo     BT Taxa    BT Passos    H Tempo      H Taxa  
====================================================================================================
10    sparse   0.000123     100.00%    45.2         0.000012     100.00%   
10    dense    0.000289     100.00%    78.5         0.000015     100.00%   
15    sparse   0.001234     80.00%     234.5        0.000045     60.00%  
15    dense    0.003456     100.00%    456.7        0.000067     80.00%  
20    sparse   0.008923     60.00%     1234.5       0.000123     40.00%  
20    dense    0.023456     80.00%     2345.6       0.000234     60.00%  
====================================================================================================

✓ Resultados exportados para: batch.csv
================================================================================
```

---

## Interface Gráfica (Opcional)

Se você instalou as dependências GUI (`pip install -r requirements-gui.txt`), pode usar a interface gráfica:

```bash
./run.sh gui
```

### Funcionalidades da GUI:

- **Aba "Análise de Grafo"**:

  - Carregar/gerar grafos
  - Visualização interativa (zoom, pan, drag)
  - Executar algoritmos com animação
  - Comparação visual lado a lado
- **Aba "Experimentos"**:

  - Configurar e executar experimentos
  - Visualizar resultados em tabelas
  - Gráficos e sumários estatísticos
  - Exportar CSV

---

## Formato dos Arquivos

### Arquivo de Grafo (.txt)

```
10          # número de vértices
0 1 2       # vizinhos do vértice 0
1 0 3 4     # vizinhos do vértice 1
2 0 5       # vizinhos do vértice 2
...
```

### CSV de Resultados

```csv
n,densidade,probabilidade,run_id,num_arestas,bt_tempo,bt_sucesso,bt_passos,h_tempo,h_sucesso
10,sparse,0.2,0,9,0.000123,1,45,0.000012,1
10,sparse,0.2,1,11,0.000145,1,52,0.000014,1
...
```

---

## Testes

```bash
# Rodar testes unitários (se implementados)
python -m pytest tests/

# Executar demo completo
python demo_experiments.py
```

---

## Referências

- Problema do Caminho Hamiltoniano (NP-completo)
- Backtracking para problemas de otimização
- Heurísticas gulosas para grafos

---

## Licença

 Apache License Version 2.0

---

## Autor

Weslei Ferreira (@wesleiferreira98)
