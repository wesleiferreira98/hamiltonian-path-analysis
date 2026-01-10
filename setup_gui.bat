@echo off
REM Script para configurar ambiente virtual e instalar dependencias da GUI no Windows

echo ==========================================
echo Configuracao do Ambiente Virtual para GUI
echo ==========================================
echo.

echo Sistema detectado: Windows
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado. Tentando instalar via winget...
    echo.
    
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo ERRO: winget nao encontrado.
        echo.
        echo Por favor, instale Python manualmente:
        echo   1. Baixe de https://www.python.org/downloads/
        echo   2. Durante instalacao, marque "Add Python to PATH"
        echo   3. Execute este script novamente
        echo.
        echo Ou instale o winget (Windows 10/11):
        echo   Microsoft Store ^> App Installer
        pause
        exit /b 1
    )
    
    echo Instalando Python via winget...
    winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    
    if errorlevel 1 (
        echo.
        echo ERRO: Falha na instalacao automatica.
        echo Por favor, instale Python manualmente de https://www.python.org/
        pause
        exit /b 1
    )
    
    echo.
    echo Python instalado com sucesso!
    echo IMPORTANTE: Feche e reabra este terminal, depois execute este script novamente.
    pause
    exit /b 0
) else (
    python --version
    echo Python encontrado!
)

echo.
echo Criando ambiente virtual...
if exist venv (
    echo AVISO: Diretorio venv ja existe. Removendo...
    rmdir /s /q venv
)

python -m venv venv

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Atualizando pip...
python -m pip install --upgrade pip

echo.
echo Instalando dependencias da GUI...
pip install -r requirements-gui.txt

echo.
echo ==========================================
echo Configuracao concluida com sucesso!
echo ==========================================
echo.
echo Para usar a GUI, execute:
echo   venv\Scripts\activate
echo   python main.py gui
echo.
echo Para desativar o ambiente virtual:
echo   deactivate
echo.

pause
