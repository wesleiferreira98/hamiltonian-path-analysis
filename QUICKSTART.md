# Quick Start Guide - Hamiltonian Path Analysis

## Início Rápido (2 minutos)

### 1. Clone o Repositório

```bash
git clone https://github.com/wesleiferreira98/hamiltonian-path-analysis.git
cd hamiltonian-path-analysis
```

### 2. Pronto! Você já pode usar

**Não precisa instalar nada!** O projeto roda com Python padrão (3.6+).

```bash
# Linux/Mac
./run.sh --help

# Windows
run.bat --help

# Ou diretamente
python main.py --help
```

---

## Comandos Essenciais

### Analisar um Grafo

```bash
# Gerar um grafo de teste
python main.py generate 10 medium --output grafo.txt

# Analisar o grafo
python main.py analyze grafo.txt

# Análise detalhada com ambos algoritmos
python main.py analyze grafo.txt --algorithm both -v
```

**Saída:**

```
================================================================================
ANÁLISE DE CAMINHO HAMILTONIANO
================================================================================

Carregando grafo: grafo.txt
✓ Grafo carregado: 10 vértices, 28 arestas

Executando Backtracking...
✓ Caminho encontrado em 0.000013s
  Passos: 14
  Caminho: [0, 1, 2, 3, 4, 5, 7, 6, 9, 8]

Executando Heurística...
✓ Caminho encontrado em 0.000017s
  Caminho: [0, 1, 6, 7, 2, 4, 3, 9, 8, 5]

--------------------------------------------------------------------------------
COMPARAÇÃO

Backtracking    ✓ Sucesso  Tempo: 0.000013s  Passos: 14
Heurística      ✓ Sucesso  Tempo: 0.000017s

Speedup (BT/H): 0.73x
================================================================================
```

### Executar Experimento

```bash
# Experimento com 20 vértices, densidade média, 10 repetições
python main.py experiment 20 medium --repetitions 10 --output resultado.csv
```

**Saída:**

```
================================================================================
EXPERIMENTO INDIVIDUAL
================================================================================

Configuração:
  n = 20
  densidade = medium
  repetições = 10

Executando experimento...

✓ Experimento concluído!

Resultados:

Backtracking:
  Tempo médio:     0.003456s
  Tempo min/max:   0.001234s / 0.005678s
  Taxa de sucesso: 80.0%
  Passos médios:   456

Heurística:
  Tempo médio:     0.000123s
  Tempo min/max:   0.000098s / 0.000156s
  Taxa de sucesso: 60.0%

Speedup (BT/H): 28.10x

✓ Resultados exportados para: resultado.csv
================================================================================
```

### Batch de Experimentos

```bash
# Batch completo com tamanhos e densidades padrão
python main.py batch --output resultados_completos.csv

# Batch customizado
python main.py batch \
  --sizes 10,15,20,25,30 \
  --densities sparse,medium,dense \
  --repetitions 10 \
  --output experimentos.csv
```

**Saída:**

```
================================================================================
BATCH DE EXPERIMENTOS
================================================================================

Configuração:
  Tamanhos: [10, 20, 30, 40, 50]
  Densidades: ['sparse', 'medium', 'dense']
  Repetições: 5
  Total de experimentos: 15

[1/15] n=10, densidade=sparse... ✓ (BT: 0.0001s, H: 0.0000s)
[2/15] n=10, densidade=medium... ✓ (BT: 0.0002s, H: 0.0000s)
[3/15] n=10, densidade=dense... ✓ (BT: 0.0003s, H: 0.0000s)
...

✓ Batch concluído!

====================================================================================================
n     Dens     BT Tempo     BT Taxa    BT Passos    H Tempo      H Taxa  
====================================================================================================
10    sparse   0.000123     100.00%    45.2         0.000012     100.00%   
10    medium   0.000234     100.00%    67.3         0.000015     100.00%   
10    dense    0.000289     100.00%    78.5         0.000018     100.00%   
...
====================================================================================================

✓ Resultados exportados para: resultados_completos.csv
```

---

## Interface Gráfica (Opcional)

Se você quiser usar a interface gráfica:

```bash
# Instalar dependências GUI (PyQt6, matplotlib, networkx)
pip install -r requirements-gui.txt

# Iniciar GUI
python main.py gui
```

---

## Formato do CSV Gerado

O CSV pode ser importado em Excel, Google Sheets, R, Python pandas, etc:

```csv
n,densidade,probabilidade,run_id,num_arestas,bt_tempo,bt_sucesso,bt_passos,h_tempo,h_sucesso
10,sparse,0.2,0,9,0.000123,1,45,0.000012,1
10,sparse,0.2,1,11,0.000145,1,52,0.000014,1
10,sparse,0.2,2,8,0.000098,1,38,0.000011,1
...
```

---

## Dicas

### 1. Sem Cores no Terminal

```bash
python main.py analyze grafo.txt --no-color
```

### 2. Redirecionamento de Saída

```bash
# Salvar output completo
python main.py batch --output data.csv > relatorio.txt 2>&1
```

### 3. Tamanhos Maiores (Cuidado!)

Para n > 30, o backtracking pode ser **muito lento**:

```bash
# Use apenas heurística para grafos grandes
python main.py analyze grafo_grande.txt --algorithm heur
```

### 4. Densidades

- **sparse** (p=0.2): ~20% das arestas possíveis
- **medium** (p=0.5): ~50% das arestas possíveis
- **dense** (p=0.8): ~80% das arestas possíveis

---

## Comandos de Ajuda

```bash
# Ajuda geral
python main.py --help

# Ajuda de comando específico
python main.py analyze --help
python main.py experiment --help
python main.py batch --help
```

---

## Workflow

```bash
# 1. Gerar dados experimentais
python main.py batch --output dados_tcc.csv

# 2. Analisar casos específicos interessantes
python main.py generate 25 sparse --output caso_interessante.txt
python main.py analyze caso_interessante.txt -v

# 3. Usar GUI para visualizar (opcional)
python main.py gui
```

---

## Problemas Comuns

### "Python não encontrado"

```bash
# Use python3 explicitamente
python3 main.py --help
```

### "ModuleNotFoundError: src..."

```bash
# Execute sempre do diretório raiz do projeto
cd hamiltonian-path-analysis
python main.py --help
```

### "ImportError: PyQt6"

```bash
# Você tentou usar 'python main.py gui' sem instalar dependências
# Solução 1: Instalar GUI
pip install -r requirements-gui.txt

# Solução 2: Usar apenas CLI (não precisa instalar nada)
python main.py batch --output results.csv
```

---

**Pronto para começar!**

Execute:

```bash
python main.py analyze test_graph.txt
```
