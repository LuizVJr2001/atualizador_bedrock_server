@echo off
echo ==========================================
echo   Atualizador do Servidor Minecraft Bedrock
echo ==========================================
echo.

:: 1. Tenta descobrir qual comando chama o Python globalmente
set GLOBAL_PYTHON=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    set GLOBAL_PYTHON=py
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERRO] O Windows nao encontrou o Python instalado.
        echo Por favor, instale o Python e lembre-se de marcar a caixa:
        echo "Add python.exe to PATH" na primeira tela do instalador.
        echo.
        pause
        exit /b
    )
)

:: 2. Cria a venv usando o comando global que funcionou
if not exist "venv" (
    echo [INFO] Criando ambiente virtual isolado...
    %GLOBAL_PYTHON% -m venv venv
)

:: 3. Ativa a venv (a partir daqui, o comando 'python' e 'pip' sempre funcionam)
echo [INFO] Preparando as bibliotecas...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

:: 4. Roda o seu script principal
echo [INFO] Iniciando o processo de atualizacao...
echo.
python update_bedrock.py
echo.

pause