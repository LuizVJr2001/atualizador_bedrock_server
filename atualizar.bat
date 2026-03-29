@echo off
echo ==========================================
echo   Atualizador do Servidor Minecraft Bedrock
echo ==========================================
echo.

:: 1. Verifica se o Python ja esta instalado (procura por python ou py)
set "PYTHON_CMD="
python --version >nul 2>&1
if %errorlevel% equ 0 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
    py --version >nul 2>&1
    if %errorlevel% equ 0 set "PYTHON_CMD=py"
)

:: 2. A MAGICA: Se nao achou, baixa e instala sozinho!
if not defined PYTHON_CMD (
    echo [INFO] Python nao encontrado no computador.
    echo [INFO] Baixando o instalador oficial do Python 3.12...
    
    :: O curl baixa o arquivo do site oficial e salva na pasta atual
    curl -# -L -o python_installer.exe https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    
    if exist python_installer.exe (
        echo [INFO] Instalando o Python em modo silencioso (isso pode levar uns 2 minutos)...
        
        :: Inicia a instalação invisivel com o PATH ativado
        start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        
        echo [INFO] Instalacao concluida! Apagando arquivo de instalacao...
        del python_installer.exe
        
        :: Como o terminal atual nao "enxerga" o PATH novo imediatamente, apontamos direto pro caminho recem-instalado
        set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        
        if not exist "!PYTHON_CMD!" (
            :: Caso ele instale em outro lugar (raro), forçamos o uso basico
            set "PYTHON_CMD=python"
        )
    ) else (
        echo [ERRO] Ocorreu um problema ao baixar o Python. Verifique a internet.
        pause
        exit /b
    )
)

:: 3. Continua o fluxo normalmente criando a VENV
if not exist "venv" (
    echo [INFO] Criando ambiente virtual isolado...
    "%PYTHON_CMD%" -m venv venv
)

:: 4. Ativa a VENV e roda o pip
echo [INFO] Instalando dependencias do projeto...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

:: 5. Chama o script Python
echo [INFO] Iniciando comunicacao com o servidor...
echo.
python update_bedrock.py
echo.

pause