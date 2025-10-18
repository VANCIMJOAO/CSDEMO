#!/bin/bash

# Script de Teste Rápido do Sistema LAN Party

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🧪 TESTE DO SISTEMA LAN PARTY  🧪   ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}\n"

# 1. Verificar arquivos necessários
echo -e "${YELLOW}1. Verificando arquivos...${NC}"
files=("monitor.py" "web_app/main.py" "web_app/templates/matches.html" "start_lan_party.sh")
all_ok=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✓${NC} $file"
    else
        echo -e "   ${RED}✗${NC} $file ${RED}FALTANDO!${NC}"
        all_ok=false
    fi
done

if [ "$all_ok" = false ]; then
    echo -e "\n${RED}❌ Arquivos faltando! Sistema incompleto.${NC}"
    exit 1
fi

# 2. Verificar ambiente virtual
echo -e "\n${YELLOW}2. Verificando ambiente virtual...${NC}"
if [ -d "venv" ]; then
    echo -e "   ${GREEN}✓${NC} venv encontrado"
    source venv/bin/activate
    
    # Verificar dependências
    python -c "import fastapi, demoparser2, pandas, rich" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✓${NC} Dependências instaladas"
    else
        echo -e "   ${YELLOW}⚠${NC} Instalando dependências..."
        pip install -q fastapi uvicorn demoparser2 pandas rich python-multipart jinja2
    fi
else
    echo -e "   ${RED}✗${NC} venv não encontrado!"
    echo -e "   ${YELLOW}Criando ambiente virtual...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q fastapi uvicorn demoparser2 pandas rich python-multipart jinja2
fi

# 3. Verificar pastas
echo -e "\n${YELLOW}3. Verificando estrutura de pastas...${NC}"
mkdir -p demos demo_analysis

if [ -d "demos" ] && [ -d "demo_analysis" ]; then
    echo -e "   ${GREEN}✓${NC} Pastas criadas"
else
    echo -e "   ${RED}✗${NC} Erro ao criar pastas"
    exit 1
fi

# 4. Testar importação do monitor
echo -e "\n${YELLOW}4. Testando módulo monitor...${NC}"
python -c "from monitor import DemoMonitor; print('   ✓ Monitor importado com sucesso')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "   ${RED}✗${NC} Erro ao importar monitor"
    exit 1
fi

# 5. Verificar demos de exemplo
echo -e "\n${YELLOW}5. Verificando demos de exemplo...${NC}"
demo_count=$(ls demos/*.dem 2>/dev/null | wc -l)
if [ $demo_count -gt 0 ]; then
    echo -e "   ${GREEN}✓${NC} $demo_count demo(s) encontrado(s)"
else
    echo -e "   ${YELLOW}⚠${NC} Nenhuma demo de exemplo encontrada"
    echo -e "   ${CYAN}ℹ${NC} Coloque arquivos .dem na pasta demos/ para testar"
fi

# 6. Teste de permissões
echo -e "\n${YELLOW}6. Verificando permissões...${NC}"
if [ -x "start_lan_party.sh" ]; then
    echo -e "   ${GREEN}✓${NC} start_lan_party.sh é executável"
else
    echo -e "   ${YELLOW}⚠${NC} Ajustando permissões..."
    chmod +x start_lan_party.sh
fi

# 7. Verificar porta 8000
echo -e "\n${YELLOW}7. Verificando porta 8000...${NC}"
if lsof -i :8000 >/dev/null 2>&1; then
    echo -e "   ${YELLOW}⚠${NC} Porta 8000 em uso"
    echo -e "   ${CYAN}ℹ${NC} Você precisará parar o processo ou usar outra porta"
else
    echo -e "   ${GREEN}✓${NC} Porta 8000 disponível"
fi

# Resumo final
echo -e "\n${CYAN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SISTEMA PRONTO PARA USO!${NC}"
echo -e "${CYAN}════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}📋 Próximos passos:${NC}\n"
echo -e "   1. Iniciar o servidor:"
echo -e "      ${CYAN}./start_lan_party.sh${NC}\n"
echo -e "   2. Acessar o dashboard:"
echo -e "      ${CYAN}http://localhost:8000${NC}\n"
echo -e "   3. Testar com demo existente:"
echo -e "      ${CYAN}cp demos/*.dem demos/teste_\$(date +%s).dem${NC}\n"

echo -e "${GREEN}Documentação completa:${NC}"
echo -e "   → README_LAN_PARTY.md"
echo -e "   → TESTE_RAPIDO.md"
echo -e "   → RESUMO_LAN_PARTY.txt\n"

echo -e "${CYAN}Boa LAN Party! 🎮${NC}\n"

