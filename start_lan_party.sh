#!/bin/bash

# Script de inicialização para CS2 Analyzer - Modo LAN Party
# Este script inicia o servidor web com monitoramento automático de demos

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║         🎮  CS2 DEMO ANALYZER - LAN PARTY MODE  🎮        ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Diretório do projeto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}📁 Diretório do projeto: ${SCRIPT_DIR}${NC}\n"

# Verificar se o venv existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo -e "${YELLOW}Por favor, crie o ambiente virtual primeiro:${NC}"
    echo -e "   python3 -m venv venv"
    echo -e "   source venv/bin/activate"
    echo -e "   pip install -r requirements.txt"
    exit 1
fi

# Ativar ambiente virtual
echo -e "${YELLOW}🔧 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Verificar se as dependências estão instaladas
echo -e "${YELLOW}📦 Verificando dependências...${NC}"
python -c "import fastapi, demoparser2, pandas, rich" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Dependências faltando!${NC}"
    echo -e "${YELLOW}Instalando dependências...${NC}"
    pip install fastapi uvicorn demoparser2 pandas rich python-multipart jinja2
fi

# Criar pastas necessárias
echo -e "${YELLOW}📂 Criando diretórios...${NC}"
mkdir -p demos
mkdir -p demo_analysis

# Informações do sistema
echo -e "\n${GREEN}✅ Sistema configurado!${NC}\n"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}📋 CONFIGURAÇÕES DA LAN PARTY:${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📁 Pasta de Demos:${NC}      ${SCRIPT_DIR}/demos"
echo -e "${GREEN}💾 Pasta de Análises:${NC}   ${SCRIPT_DIR}/demo_analysis"
echo -e "${GREEN}🔍 Intervalo de Scan:${NC}   30 segundos"
echo -e "${GREEN}🌐 URL do Dashboard:${NC}    http://localhost:8000"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"

# Instruções para os jogadores
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}📝 INSTRUÇÕES PARA GRAVAR DEMOS NO CS2:${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e ""
echo -e "${GREEN}1.${NC} Abra o console no CS2 (tecla ${CYAN}~${NC} ou ${CYAN}\`${NC})"
echo -e ""
echo -e "${GREEN}2.${NC} Para INICIAR a gravação, digite:"
echo -e "   ${CYAN}demo record nome_da_partida${NC}"
echo -e ""
echo -e "${GREEN}3.${NC} Para PARAR a gravação, digite:"
echo -e "   ${CYAN}demo stop${NC}"
echo -e ""
echo -e "${GREEN}4.${NC} O arquivo .dem será salvo automaticamente em:"
echo -e "   ${CYAN}${SCRIPT_DIR}/demos/${NC}"
echo -e ""
echo -e "${GREEN}5.${NC} O sistema irá detectar e analisar automaticamente!"
echo -e ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Avisos importantes
echo -e "${RED}⚠️  IMPORTANTE:${NC}"
echo -e "${YELLOW}• Configure o CS2 para salvar demos na pasta: ${SCRIPT_DIR}/demos${NC}"
echo -e "${YELLOW}• Você pode fazer isso com o comando: ${CYAN}demo setdirectory \"${SCRIPT_DIR}/demos\"${NC}"
echo -e "${YELLOW}• O dashboard atualiza automaticamente a cada 10 segundos${NC}\n"

# Perguntar se quer abrir o navegador
read -p "$(echo -e ${GREEN}🌐 Abrir o navegador automaticamente? [S/n]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    OPEN_BROWSER="yes"
else
    OPEN_BROWSER="no"
fi

# Iniciar servidor
echo -e "\n${GREEN}🚀 Iniciando servidor...${NC}\n"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}Pressione ${RED}CTRL+C${MAGENTA} para parar o servidor${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"

# Abrir navegador após 2 segundos (se escolhido)
if [ "$OPEN_BROWSER" = "yes" ]; then
    (sleep 2 && xdg-open http://localhost:8000 2>/dev/null || open http://localhost:8000 2>/dev/null) &
fi

# Iniciar o servidor
cd web_app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Cleanup ao sair
echo -e "\n${YELLOW}👋 Encerrando servidor...${NC}"
echo -e "${GREEN}Obrigado por usar o CS2 Analyzer!${NC}\n"

