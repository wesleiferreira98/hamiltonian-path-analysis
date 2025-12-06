#!/bin/bash
# Script de entrada rápido para Hamiltonian Path Analysis
# Funciona sem instalação de dependências GUI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "Erro: Python não encontrado no sistema"
    exit 1
fi

# Verificar versão do Python (mínimo 3.6)
PYTHON_VERSION=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$($PYTHON -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$($PYTHON -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
    echo "Erro: Python 3.6+ é necessário (encontrado: $PYTHON_VERSION)"
    exit 1
fi

# Se não houver argumentos, mostrar ajuda
if [ $# -eq 0 ]; then
    $PYTHON main.py --help
    exit 0
fi

# Executar main.py com os argumentos
exec $PYTHON main.py "$@"
