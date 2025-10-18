#!/bin/bash
# ==============================================================
# 🚀 INICIADOR DA APLICAÇÃO WEB CS2 DEMO ANALYZER
# ==============================================================

echo "=============================================================="
echo "🎮 INICIANDO CS2 DEMO ANALYZER WEB APP"
echo "=============================================================="

# Navegar para o diretório do projeto
cd ~/cs2analyzer

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
. venv/bin/activate

# Verificar se as dependências estão instaladas
echo "🔍 Verificando dependências..."
python -c "import fastapi, uvicorn, jinja2; print('✅ Todas as dependências estão instaladas!')" || {
    echo "❌ Instalando dependências faltantes..."
    pip install fastapi uvicorn jinja2 python-multipart
}

# Iniciar o servidor
echo "🌐 Iniciando servidor web..."
echo "📍 Acesse: http://localhost:8000"
echo "📍 Para parar: Ctrl+C"
echo "=============================================================="

uvicorn web_app.main:app --reload --host 0.0.0.0 --port 8000
