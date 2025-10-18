# 🎮 CS2 Demo Analyzer - Guia de Instalação para Windows

## 📋 Requisitos

- **Windows 10 ou 11**
- **Python 3.9 ou superior** (será instalado automaticamente se necessário)
- **Conexão com a internet** (para baixar dependências)

## 🚀 Instalação Rápida (Automática)

### Método 1: Instalação Automática Completa

1. **Baixe o projeto**
   - Clone o repositório: `git clone https://github.com/VANCIMJOAO/CSDEMO.git`
   - Ou baixe o ZIP e extraia

2. **Execute o instalador automático**
   - Dê um duplo clique em `start_lan_party.bat`
   - O script irá:
     - ✅ Verificar se o Python está instalado
     - ✅ Instalar o Python se necessário (abrirá o site oficial)
     - ✅ Criar o ambiente virtual Python
     - ✅ Instalar todas as dependências automaticamente
     - ✅ Criar as pastas necessárias
     - ✅ Iniciar o servidor web

3. **Pronto!**
   - O navegador abrirá automaticamente em `http://localhost:8000`
   - Você pode acessar de outros PCs na rede local usando `http://SEU_IP:8000`

---

## 🔧 Instalação Manual (Caso necessário)

Se preferir instalar manualmente ou se o script automático não funcionar:

### Passo 1: Instalar Python

1. Acesse https://www.python.org/downloads/
2. Baixe a versão mais recente do Python 3 (3.9+)
3. **IMPORTANTE**: Durante a instalação, marque a opção **"Add Python to PATH"**
4. Clique em "Install Now"

### Passo 2: Verificar Instalação

Abra o Prompt de Comando (CMD) e digite:

```cmd
python --version
pip --version
```

Deve mostrar as versões instaladas.

### Passo 3: Criar Ambiente Virtual

No diretório do projeto, execute:

```cmd
python -m venv venv
venv\Scripts\activate
```

### Passo 4: Instalar Dependências

```cmd
pip install -r requirements.txt
```

### Passo 5: Criar Pastas Necessárias

```cmd
mkdir demos
mkdir demo_analysis
```

### Passo 6: Iniciar o Servidor

```cmd
cd web_app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎯 Como Usar

### Configurar o CS2

1. Abra o CS2
2. Abra o console (tecla `~` ou `` ` ``)
3. Configure o diretório de demos (apenas uma vez):

```
demo setdirectory "C:\caminho\para\cs2analyzer\demos"
```

**Exemplo:**
```
demo setdirectory "C:\Users\SeuNome\CSDEMO\demos"
```

### Gravar uma Partida

1. **Iniciar gravação** (antes da partida começar):
```
demo record nome_da_partida
```

2. **Jogar normalmente**

3. **Parar gravação** (após a partida):
```
demo stop
```

4. **O sistema detectará automaticamente** a nova demo e fará a análise!

### Fazer Upload Manual

Se preferir, acesse `http://localhost:8000/upload` e faça upload da demo manualmente.

---

## 🌐 Acessar de Outros PCs (LAN Party)

1. Descubra seu IP:
   ```cmd
   ipconfig
   ```
   Procure por "Endereço IPv4" (geralmente algo como `192.168.1.X`)

2. No PC onde o servidor está rodando:
   - Certifique-se de que o firewall permite conexões na porta 8000
   - **Windows Firewall**: Pode pedir permissão automaticamente, clique em "Permitir"

3. Nos outros PCs da LAN:
   - Abra o navegador
   - Acesse: `http://IP_DO_SERVIDOR:8000`
   - Exemplo: `http://192.168.1.100:8000`

---

## 📂 Estrutura do Projeto

```
cs2analyzer/
├── start_lan_party.bat       # Script de instalação e inicialização automática
├── requirements.txt           # Dependências Python
├── demos/                     # Coloque suas demos aqui (.dem)
├── demo_analysis/             # Análises geradas automaticamente
└── web_app/                   # Aplicação web
    ├── main.py                # Backend FastAPI
    ├── templates/             # Templates HTML
    └── static/                # CSS, JS, imagens
```

---

## ❓ Solução de Problemas

### Python não encontrado

**Erro:** `'python' não é reconhecido como um comando interno ou externo`

**Solução:**
1. Reinstale o Python marcando "Add Python to PATH"
2. Ou adicione manualmente ao PATH:
   - Busque "variáveis de ambiente" no Windows
   - Edite a variável PATH
   - Adicione: `C:\Users\SeuNome\AppData\Local\Programs\Python\Python3XX`

### Erro ao instalar dependências

**Erro:** Falha ao instalar `demoparser2` ou outras bibliotecas

**Solução:**
```cmd
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

### Porta 8000 já está em uso

**Erro:** `Address already in use`

**Solução:**
1. Feche outros programas usando a porta 8000
2. Ou mude a porta no comando:
```cmd
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Demos não são detectadas automaticamente

**Solução:**
1. Verifique se a demo está na pasta `demos/`
2. Certifique-se de que o arquivo tem extensão `.dem`
3. Reinicie o servidor

---

## 🆘 Suporte

Se encontrar problemas:

1. Verifique se seguiu todos os passos corretamente
2. Abra uma issue no GitHub: https://github.com/VANCIMJOAO/CSDEMO/issues
3. Inclua:
   - Versão do Windows
   - Versão do Python (`python --version`)
   - Mensagem de erro completa
   - Captura de tela do erro

---

## 📝 Funcionalidades

- ✅ **Análise automática de demos**
- ✅ **Dashboard interativo com gráficos**
- ✅ **Estatísticas detalhadas por jogador**
- ✅ **Suporte a Overtime (OT)**
- ✅ **Detecção de times registrados**
- ✅ **Sistema de torneios**
- ✅ **Upload manual de demos**
- ✅ **Acesso via rede local (LAN Party)**

---

## 🔄 Atualizações

Para atualizar o projeto:

```cmd
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

---

**Desenvolvido para análise de demos de Counter-Strike 2**

Para mais informações, visite: https://github.com/VANCIMJOAO/CSDEMO
