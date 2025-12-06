@echo off
REM Script de entrada rápido para Windows
REM Funciona sem instalação de dependências GUI

setlocal enabledelayedexpansion

REM Detectar Python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON=python
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON=python3
    ) else (
        echo Erro: Python nao encontrado no sistema
        exit /b 1
    )
)

REM Se não houver argumentos, mostrar ajuda
if "%~1"=="" (
    %PYTHON% main.py --help
    exit /b 0
)

REM Executar main.py com os argumentos
%PYTHON% main.py %*
