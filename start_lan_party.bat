@echo off
chcp 65001 >nul
color 0B
cls

REM ════════════════════════════════════════════════════════════════
REM CS2 DEMO ANALYZER - Script de Instalação e Inicialização (Windows)
REM Este script verifica dependências, instala se necessário e inicia o servidor
REM ════════════════════════════════════════════════════════════════

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         🎮  CS2 DEMO ANALYZER - LAN PARTY MODE  🎮        ║
echo ║                    INSTALADOR AUTOMÁTICO                   ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Ir para o diretório do script
cd /d "%~dp0"
set "SCRIPT_DIR=%CD%"

echo 📁 Diretório do projeto: %SCRIPT_DIR%
echo.
echo ════════════════════════════════════════════════════════════
echo 🔍 VERIFICANDO DEPENDÊNCIAS DO SISTEMA
echo ════════════════════════════════════════════════════════════
echo.

REM ════════════════════════════════════════════════════════════
REM VERIFICAR PYTHON
REM ════════════════════════════════════════════════════════════
echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ Python NÃO está instalado!
    echo.
    color 0E
    echo 📥 INSTALE O PYTHON AGORA:
    echo.
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe a versão mais recente do Python 3 (3.9 ou superior)
    echo 3. IMPORTANTE: Marque a opção "Add Python to PATH" durante a instalação
    echo 4. Após instalar, feche e abra este script novamente
    echo.
    color 0C
    echo Pressione qualquer tecla para abrir o site do Python...
    pause >nul
    start https://www.python.org/downloads/
    echo.
    echo Execute este script novamente após instalar o Python.
    pause
    exit /b 1
) else (
    color 0A
    python --version 2>&1 | findstr /C:"Python"
    echo ✅ Python está instalado!
    echo.
)

REM ════════════════════════════════════════════════════════════
REM VERIFICAR PIP
REM ════════════════════════════════════════════════════════════
color 0B
echo [2/3] Verificando pip (gerenciador de pacotes Python)...
pip --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ pip NÃO está instalado!
    echo.
    echo Instalando pip...
    python -m ensurepip --default-pip
    python -m pip install --upgrade pip
    echo.
) else (
    color 0A
    echo ✅ pip está instalado!
    echo.
)

REM ════════════════════════════════════════════════════════════
REM CRIAR AMBIENTE VIRTUAL
REM ════════════════════════════════════════════════════════════
color 0B
echo [3/3] Verificando ambiente virtual...
if not exist "venv\" (
    color 0E
    echo 📦 Criando ambiente virtual Python...
    echo.
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo ❌ Erro ao criar ambiente virtual!
        echo.
        pause
        exit /b 1
    )
    color 0A
    echo ✅ Ambiente virtual criado!
    echo.
) else (
    color 0A
    echo ✅ Ambiente virtual já existe!
    echo.
)

REM ════════════════════════════════════════════════════════════
REM ATIVAR AMBIENTE VIRTUAL
REM ════════════════════════════════════════════════════════════
color 0B
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    color 0C
    echo ❌ Erro ao ativar ambiente virtual!
    pause
    exit /b 1
)
color 0A
echo ✅ Ambiente virtual ativado!
echo.

REM ════════════════════════════════════════════════════════════
REM VERIFICAR/CRIAR REQUIREMENTS.TXT
REM ════════════════════════════════════════════════════════════
color 0B
if not exist "requirements.txt" (
    echo 📝 Criando requirements.txt...
    (
        echo fastapi==0.104.1
        echo uvicorn[standard]==0.24.0
        echo demoparser2==0.20.0
        echo pandas==2.1.3
        echo rich==13.7.0
        echo python-multipart==0.0.6
        echo jinja2==3.1.2
    ) > requirements.txt
    echo ✅ requirements.txt criado!
    echo.
)

REM ════════════════════════════════════════════════════════════
REM INSTALAR DEPENDÊNCIAS PYTHON
REM ════════════════════════════════════════════════════════════
echo ════════════════════════════════════════════════════════════
echo 📦 INSTALANDO DEPENDÊNCIAS PYTHON
echo ════════════════════════════════════════════════════════════
echo.
echo Verificando se as bibliotecas necessárias estão instaladas...
python -c "import fastapi, demoparser2, pandas, rich" 2>nul
if errorlevel 1 (
    color 0E
    echo 📥 Instalando dependências do requirements.txt...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo.
        echo ❌ Erro ao instalar dependências!
        echo.
        echo Tente instalar manualmente:
        echo    pip install fastapi uvicorn demoparser2 pandas rich python-multipart jinja2
        echo.
        pause
        exit /b 1
    )
    color 0A
    echo.
    echo ✅ Todas as dependências foram instaladas!
    echo.
) else (
    color 0A
    echo ✅ Todas as dependências já estão instaladas!
    echo.
)

REM ════════════════════════════════════════════════════════════
REM CRIAR ESTRUTURA DE PASTAS
REM ════════════════════════════════════════════════════════════
color 0B
echo ════════════════════════════════════════════════════════════
echo 📂 CRIANDO ESTRUTURA DE PASTAS
echo ════════════════════════════════════════════════════════════
echo.

if not exist "demos" (
    mkdir demos
    echo ✅ Pasta 'demos' criada
) else (
    echo ✅ Pasta 'demos' já existe
)

if not exist "demo_analysis" (
    mkdir demo_analysis
    echo ✅ Pasta 'demo_analysis' criada
) else (
    echo ✅ Pasta 'demo_analysis' já existe
)

if not exist "web_app" (
    color 0C
    echo.
    echo ❌ ERRO: Pasta 'web_app' não encontrada!
    echo.
    echo Certifique-se de que está executando este script na pasta raiz do projeto.
    pause
    exit /b 1
)

REM ════════════════════════════════════════════════════════════
REM INFORMAÇÕES DO SISTEMA
REM ════════════════════════════════════════════════════════════
echo.
color 0A
echo ════════════════════════════════════════════════════════════
echo ✅ INSTALAÇÃO COMPLETA - SISTEMA PRONTO!
echo ════════════════════════════════════════════════════════════
echo.
color 0B
echo ════════════════════════════════════════════════════════════
echo 📋 CONFIGURAÇÕES DA LAN PARTY:
echo ════════════════════════════════════════════════════════════
echo.
echo 📁 Pasta de Demos:      %SCRIPT_DIR%\demos
echo 💾 Pasta de Análises:   %SCRIPT_DIR%\demo_analysis
echo 🔍 Intervalo de Scan:   30 segundos
echo 🌐 URL do Dashboard:    http://localhost:8000
echo 🌐 Rede Local:          http://SEU_IP:8000
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM ════════════════════════════════════════════════════════════
REM INSTRUÇÕES PARA OS JOGADORES
REM ════════════════════════════════════════════════════════════
color 0E
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📝 INSTRUÇÕES PARA GRAVAR DEMOS NO CS2:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 1. Abra o console no CS2 (tecla ~ ou `)
echo.
echo 2. Configure o diretório de demos (APENAS UMA VEZ):
echo    demo setdirectory "%SCRIPT_DIR%\demos"
echo.
echo 3. Para INICIAR a gravação:
echo    demo record nome_da_partida
echo.
echo 4. Para PARAR a gravação:
echo    demo stop
echo.
echo 5. O sistema detectará e analisará automaticamente!
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM ════════════════════════════════════════════════════════════
REM AVISOS IMPORTANTES
REM ════════════════════════════════════════════════════════════
color 0C
echo ⚠️  IMPORTANTE:
color 0E
echo.
echo • O dashboard atualiza automaticamente a cada 10 segundos
echo • Compartilhe http://SEU_IP:8000 com outros PCs na LAN
echo • Para descobrir seu IP, digite: ipconfig
echo.

REM ════════════════════════════════════════════════════════════
REM PERGUNTAR SE QUER ABRIR O NAVEGADOR
REM ════════════════════════════════════════════════════════════
color 0A
set /p "OPEN_BROWSER=🌐 Abrir o navegador automaticamente? [S/n]: "
if /i "%OPEN_BROWSER%"=="n" (
    set "OPEN_BROWSER=no"
) else (
    set "OPEN_BROWSER=yes"
)

REM ════════════════════════════════════════════════════════════
REM INICIAR SERVIDOR
REM ════════════════════════════════════════════════════════════
echo.
color 0B
echo ════════════════════════════════════════════════════════════
echo 🚀 INICIANDO SERVIDOR CS2 ANALYZER
echo ════════════════════════════════════════════════════════════
echo.
color 0C
echo Pressione CTRL+C para parar o servidor
color 0B
echo ════════════════════════════════════════════════════════════
echo.

REM Abrir navegador após 2 segundos (se escolhido)
if "%OPEN_BROWSER%"=="yes" (
    start "" cmd /c "timeout /t 2 >nul && start http://localhost:8000"
)

REM Iniciar o servidor
cd web_app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

REM ════════════════════════════════════════════════════════════
REM CLEANUP AO SAIR
REM ════════════════════════════════════════════════════════════
echo.
color 0E
echo 👋 Encerrando servidor...
color 0A
echo.
echo Obrigado por usar o CS2 Analyzer!
echo.
color 07
pause
