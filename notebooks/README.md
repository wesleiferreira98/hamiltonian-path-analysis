# Jupyter Notebooks - Hamiltonian Path Analysis

Este diretório contém notebooks Jupyter interativos para facilitar a compreensão, revisão e experimentação com os algoritmos de caminhos hamiltonianos.

---

## Notebooks Disponíveis

### 1. `hamiltonian_path_complete_demo.ipynb` 

**Notebook principal completo** com todas as funcionalidades essenciais do projeto.

**Conteúdo:**

- Implementação completa dos algoritmos (Backtracking + Heurística)
- Gerador de grafos aleatórios
- Monitoramento de performance (tempo + memória)
- Experimentos sistemáticos
- Visualizações interativas
- Análise estatística completa
- Exemplos práticos e didáticos

**Ideal para:**

- Revisores do projeto
- Apresentações
- Aprendizado interativo
- Experimentação rápida

---

## Como Usar

### Opção 1: Google Colab (Recomendado!)

**Sem instalação, roda no navegador!**

#### Passo 1: Abrir no Colab

Clique no botão abaixo para abrir diretamente no Google Colab:

[![https://colab.research.google.com/drive/1mrX705rGVzLQyid573LU9VsN3XYVwueH?usp=sharing](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/wesleiferreira98/hamiltonian-path-analysis/blob/main/notebooks/hamiltonian_path_complete_demo.ipynb)

**Ou manualmente:**

1. Acesse [Google Colab](https://colab.research.google.com/)
2. Vá em `Arquivo` → `Abrir notebook`
3. Selecione a aba `GitHub`
4. Cole a URL: `https://github.com/wesleiferreira98/hamiltonian-path-analysis`
5. Selecione o notebook: `notebooks/hamiltonian_path_complete_demo.ipynb`

#### Passo 2: Executar

1. Execute a primeira célula para instalar dependências (leva ~30 segundos)
2. Execute as demais células sequencialmente
3. Experimente modificar os parâmetros!

**Dica:** Use `Runtime` → `Run all` para executar tudo de uma vez.

---

### Opção 2: Jupyter Notebook Local

#### Requisitos

- Python 3.7+
- Jupyter Notebook ou JupyterLab

#### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/wesleiferreira98/hamiltonian-path-analysis.git
cd hamiltonian-path-analysis

# 2. Instale as dependências
pip install jupyter matplotlib numpy pandas psutil

# 3. Inicie o Jupyter
jupyter notebook notebooks/

# 4. Abra o notebook no navegador
```

---

### Opção 3: VS Code

#### Requisitos

- Visual Studio Code
- Extensão "Jupyter" da Microsoft

#### Como Usar

1. Abra o VS Code
2. Instale a extensão Jupyter (se ainda não tiver)
3. Abra o arquivo `hamiltonian_path_complete_demo.ipynb`
4. Selecione o kernel Python
5. Execute as células!

---

## O Que Você Vai Ver

### Seção 1: Configuração

- Instalação automática de dependências
- Importações e configuração

### Seção 2: Algoritmos

- **Backtracking**: Implementação do algoritmo exato
- **Heurística**: Implementação da abordagem gulosa
- Gerador de grafos aleatórios

### Seção 3: Exemplos Práticos

- Exemplo simples com grafo pequeno
- Comparação entre densidades
- Visualização passo a passo

### Seção 4: Experimentos

- Experimentos sistemáticos variando tamanho
- Análise estatística completa
- Comparação de performance

### Seção 5: Visualizações

- Gráfico de tempo de execução
- Gráfico de speedup
- Gráfico de taxa de sucesso
- Visualização de grafos e caminhos

### Seção 6: Conclusões

- Resumo dos resultados
- Explicação técnica
- Recomendações de uso

---

## Execução Rápida (5 minutos)

Para uma demonstração rápida:

1. Execute as células da **Seção 1** (Configuração)
2. Execute as células da **Seção 2** (Algoritmos)
3. Execute a célula **3.1** (Exemplo Simples)
4. Pule para a **Seção 5** (Visualizações)

Isso dará uma visão geral sem rodar experimentos longos.

---

## Exemplos de Saída

### Exemplo de Comparação

```
EXEMPLO 1: Grafo Pequeno (n=5, denso)
======================================================================

Grafo gerado:
  Vértices: 5
  Arestas: 8 de 10 possíveis
  Densidade: 80.0%

Backtracking:
   Caminho encontrado: [0, 1, 3, 2, 4]
    Tempo: 0.000123s
    Memória: 0.0234 MB
    Passos: 12
    Backtracks: 3

 Heurística:
   Caminho encontrado: [0, 1, 3, 2, 4]
     Tempo: 0.000001s
   Memória: 0.0012 MB

   Speedup (BT/H): 123.0x
   → Heurística foi 123.0x mais rápida!
```

### Exemplo de Visualização

O notebook gera gráficos interativos mostrando:

- O grafo com todas as arestas
- O caminho hamiltoniano destacado em azul
- Vértice inicial em verde, final em vermelho
- Setas indicando a direção do caminho

---

## Dicas de Uso

### Para Revisores

1. **Leia a introdução** (primeira seção) para entender o problema
2. **Execute os exemplos simples** (seção 3) para ver os algoritmos em ação
3. **Veja as visualizações** (seção 5) para insights visuais
4. **Leia as conclusões** (seção 6) para o resumo técnico

### Para Experimentação

**Modificar tamanhos:**

```python
sizes = [5, 10, 15, 20, 25]  # Adicionar mais tamanhos
```

**Modificar densidades:**

```python
DENSITY_MAP = {
    'very_sparse': 0.1,
    'sparse': 0.2,
    'medium': 0.5,
    'dense': 0.8,
    'very_dense': 0.95
}
```

**Mudar repetições:**

```python
repetitions = 10  # Mais repetições = resultados mais confiáveis
```

---

## Dependências

O notebook instalará automaticamente:

```bash
matplotlib>=3.5.0    # Gráficos
numpy>=1.21.0        # Cálculos numéricos
pandas>=1.3.0        # Análise de dados
psutil>=5.9.0        # Monitoramento de memória
```

**Total:** ~50 MB de download

---

## Limitações e Cuidados

### Tempo de Execução

- **n ≤ 15**: Execução rápida (segundos)
- **n = 20**: Pode demorar alguns minutos
- **n ≥ 25**: Pode demorar muito (especialmente sparse)

**Recomendação:** Para grafos grandes (n > 20), reduza o número de repetições ou use apenas a heurística.

### Memória

O notebook usa relativamente pouca memória:

- **Uso típico**: 50-100 MB
- **Pico máximo**: ~500 MB (experimentos grandes)

Funciona bem até no Colab gratuito!

### Google Colab

**Vantagens:**

- Não precisa instalar nada
- GPU/TPU disponível (não usado neste projeto)
- Compartilhamento fácil

**Limitações:**

- Timeout de 12 horas de execução
- Arquivos são temporários (baixe os resultados!)
- Requer internet

---

## Solução de Problemas

### "Módulo não encontrado"

Execute a primeira célula para instalar dependências:

```python
!pip install matplotlib numpy pandas psutil -q
```

### "Kernel morreu"

Possíveis causas:

- Grafo muito grande (reduza `n`)
- Memória insuficiente (feche outras abas)
- Timeout (reduza repetições)

### Gráficos não aparecem

No Colab, certifique-se de ter:

```python
%matplotlib inline
```

No Jupyter local, instale:

```bash
pip install ipykernel
```

---

## Material Complementar

### Documentação do Projeto

- [README.md](../README.md) - Documentação principal
- [PERFORMANCE_ANALYSIS.md](../PERFORMANCE_ANALYSIS.md) - Análise técnica detalhada

### Código Fonte

- [src/algorithms/](../src/algorithms/) - Implementações dos algoritmos
- [src/utils/](../src/utils/) - Ferramentas auxiliares


---

## Licença

Este projeto está sob a licença especificada no arquivo [LICENSE](../LICENSE).

---

## Agradecimentos

Notebooks criados para facilitar a revisão e compreensão do projeto **Hamiltonian Path Analysis**.

**Autor:** Weslei Ferreira
**Versão:** 2.0
**Data:** Janeiro 2026

---

## Sobre Python e Jupyter

- [Jupyter Documentation](https://jupyter.org/documentation)
- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
