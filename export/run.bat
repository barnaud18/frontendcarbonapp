@echo off
REM Execute a Calculadora de Pegada de Carbono

REM Verifica se o ambiente virtual existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Ambiente virtual nao encontrado. Executando setup.py primeiro...
    python setup.py
    call venv\Scripts\activate.bat
)

REM Executa a aplicacao
python main.py