#!/bin/bash

# Script para configurar ambiente virtual e instalar dependencias da GUI
# Compativel com Ubuntu, Fedora, Arch Linux e macOS

set -e

echo "=========================================="
echo "Configuracao do Ambiente Virtual para GUI"
echo "=========================================="
echo ""

# Detectar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Detectar distribuicao Linux
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    else
        DISTRO="unknown"
    fi
    
    echo "Sistema detectado: Linux ($DISTRO)"
    
    # Verificar se Python3 esta instalado
    if ! command -v python3 &> /dev/null; then
        echo ""
        echo "Python3 nao encontrado. Instalando..."
        
        case $DISTRO in
            ubuntu|debian)
                echo "Usando apt para instalar Python3..."
                sudo apt update
                sudo apt install -y python3 python3-venv python3-pip
                ;;
            fedora|rhel|centos)
                echo "Usando dnf para instalar Python3..."
                sudo dnf install -y python3 python3-virtualenv python3-pip
                ;;
            arch|manjaro)
                echo "Usando pacman para instalar Python..."
                sudo pacman -S --noconfirm python python-virtualenv python-pip
                ;;
            *)
                echo "ERRO: Distribuicao nao reconhecida."
                echo "Por favor, instale Python3 manualmente e execute este script novamente."
                exit 1
                ;;
        esac
    else
        echo "Python3 encontrado: $(python3 --version)"
    fi
    
    # Verificar se python3-venv esta instalado
    if ! python3 -m venv --help &> /dev/null; then
        echo ""
        echo "Python venv nao encontrado. Instalando..."
        
        case $DISTRO in
            ubuntu|debian)
                echo "Usando apt para instalar python3-venv..."
                sudo apt update
                sudo apt install -y python3-venv python3-pip
                ;;
            fedora|rhel|centos)
                echo "Usando dnf para instalar python3-virtualenv..."
                sudo dnf install -y python3-virtualenv python3-pip
                ;;
            arch|manjaro)
                echo "Usando pacman para instalar python-virtualenv..."
                sudo pacman -S --noconfirm python-virtualenv python-pip
                ;;
            *)
                echo "AVISO: Distribuicao nao reconhecida. Tente instalar python3-venv manualmente."
                echo "Continuando mesmo assim..."
                ;;
        esac
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Sistema detectado: macOS"
    
    # Verificar se Python3 esta instalado
    if ! command -v python3 &> /dev/null; then
        echo ""
        echo "Python3 nao encontrado. Verificando Homebrew..."
        
        if command -v brew &> /dev/null; then
            echo "Usando Homebrew para instalar Python3..."
            brew install python3
        else
            echo "ERRO: Homebrew nao encontrado."
            echo "Por favor, instale Python3 manualmente:"
            echo "  1. Instale Homebrew: https://brew.sh"
            echo "  2. Execute: brew install python3"
            echo "Ou baixe Python de: https://www.python.org/downloads/"
            exit 1
        fi
    else
        echo "Python3 encontrado: $(python3 --version)"
    fi
else
    echo "Sistema nao reconhecido: $OSTYPE"
    echo "Verificando Python3..."
    
    if ! command -v python3 &> /dev/null; then
        echo "ERRO: Python3 nao encontrado."
        echo "Por favor, instale Python3 manualmente e execute este script novamente."
        exit 1
    else
        echo "Python3 encontrado: $(python3 --version)"
    fi
fi

echo ""
echo "Criando ambiente virtual..."
if [ -d "venv" ]; then
    echo "AVISO: Diretorio venv ja existe. Removendo..."
    rm -rf venv
fi

python3 -m venv venv

echo ""
echo "Ativando ambiente virtual..."
source venv/bin/activate

echo ""
echo "Atualizando pip..."
pip install --upgrade pip

echo ""
echo "Instalando dependencias da GUI..."
pip install -r requirements-gui.txt

echo ""
echo "=========================================="
echo "Configuracao concluida com sucesso!"
echo "=========================================="
echo ""
echo "Para usar a GUI, execute:"
echo "  source venv/bin/activate"
echo "  ./run.sh gui"
echo ""
echo "Para desativar o ambiente virtual:"
echo "  deactivate"
echo ""
