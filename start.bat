@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === PsycoManager ===
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    echo Instale Python 3 e tente novamente.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [1/5] Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o venv.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Ambiente virtual ja existe.
)

set "PY=venv\Scripts\python.exe"

echo [2/5] Instalando dependencias...
"%PY%" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo [3/5] Aplicando migracoes...
"%PY%" manage.py migrate
if errorlevel 1 (
    echo [ERRO] Falha ao migrar a base de dados.
    pause
    exit /b 1
)

echo [4/5] Carregando dados demo (se a base estiver vazia)...
"%PY%" manage.py carregar_demo

echo [5/5] A iniciar o servidor...
echo.
echo UI:    http://127.0.0.1:8000/pacientes/
echo Admin: http://127.0.0.1:8000/admin/  (admin / admin123)
echo.
echo Ctrl+C para parar.
echo.

"%PY%" manage.py runserver
pause
