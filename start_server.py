#!/usr/bin/env python3
"""
🚀 CS2 Demo Analyzer Web App - Iniciador
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Navegar para o diretório do projeto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("==============================================================")
    print("🎮 INICIANDO CS2 DEMO ANALYZER WEB APP")
    print("==============================================================")
    
    # Verificar se o ambiente virtual existe
    venv_dir = project_dir / "venv"
    if not venv_dir.exists():
        print("❌ Ambiente virtual não encontrado!")
        print("Execute primeiro: python3 -m venv venv")
        return 1
    
    # Definir o Python do ambiente virtual
    venv_python = venv_dir / "bin" / "python"
    
    # Verificar dependências
    print("🔍 Verificando dependências...")
    try:
        result = subprocess.run([
            str(venv_python), "-c", 
            "import fastapi, uvicorn, jinja2; print('✅ Todas as dependências estão instaladas!')"
        ], capture_output=True, text=True)
        print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
    except Exception as e:
        print(f"❌ Erro ao verificar dependências: {e}")
        print("Instalando dependências...")
        subprocess.run([str(venv_python), "-m", "pip", "install", "fastapi", "uvicorn", "jinja2", "python-multipart"])
    
    # Iniciar o servidor
    print("🌐 Iniciando servidor web...")
    print("📍 Acesse: http://localhost:8000")
    print("📍 Para parar: Ctrl+C")
    print("==============================================================")
    
    # Executar uvicorn
    subprocess.run([
        str(venv_python), "-m", "uvicorn", 
        "web_app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])

if __name__ == "__main__":
    sys.exit(main())
