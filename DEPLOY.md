# 🚀 Manual de Deploy - CS2 Analyzer

## Índice
1. [Requisitos do Sistema](#requisitos-do-sistema)
2. [Instalação - Desenvolvimento](#instalação---desenvolvimento)
3. [Instalação - Produção](#instalação---produção)
4. [Configuração do Servidor Web](#configuração-do-servidor-web)
5. [Configuração do Serviço Systemd](#configuração-do-serviço-systemd)
6. [Backup e Manutenção](#backup-e-manutenção)
7. [Troubleshooting](#troubleshooting)

---

## Requisitos do Sistema

### Hardware Mínimo
- **CPU**: 4 cores (recomendado: 8+ cores para análise paralela)
- **RAM**: 8GB (recomendado: 16GB+)
- **Armazenamento**: 50GB+ (demos ocupam ~100MB-500MB cada)
- **Rede**: 100Mbps+ para upload/download de demos

### Software Necessário
- **Sistema Operacional**: Linux (Ubuntu 20.04+, Debian 11+) ou Windows 10/11
- **Python**: 3.9 ou superior
- **Go**: 1.19+ (para o demoinfocs-golang parser)
- **Node.js**: 16+ (opcional, para ferramentas de build)

### Dependências Python
Todas listadas em `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pandas==2.1.3
jinja2==3.1.2
aiofiles==23.2.1
```

---

## Instalação - Desenvolvimento

### 1. Clone o Repositório
```bash
cd /home/seu-usuario
git clone <url-do-repositorio> cs2analyzer
cd cs2analyzer
```

### 2. Crie o Ambiente Virtual Python
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

### 3. Instale as Dependências Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instale o Parser CS2 (demoinfocs-golang)

**Linux/Mac:**
```bash
# Instale Go se ainda não tiver
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Clone e compile o parser
cd /tmp
git clone https://github.com/markus-wa/demoinfocs-golang.git
cd demoinfocs-golang/examples/print_events
go build -o cs2-parser

# Mova para a pasta do projeto
mv cs2-parser /home/seu-usuario/cs2analyzer/
```

**Windows:**
```powershell
# Baixe e instale Go de https://go.dev/dl/

# Clone e compile o parser
cd C:\temp
git clone https://github.com/markus-wa/demoinfocs-golang.git
cd demoinfocs-golang\examples\print_events
go build -o cs2-parser.exe

# Mova para a pasta do projeto
move cs2-parser.exe C:\cs2analyzer\
```

### 5. Crie as Pastas Necessárias
```bash
mkdir -p demo_analysis
mkdir -p web_app/static/team_logos
mkdir -p logs
```

### 6. Crie Arquivos de Configuração Iniciais
```bash
# Arquivo de times (vazio inicialmente)
echo "[]" > teams.json

# Arquivo de torneios (vazio inicialmente)
echo "[]" > tournaments.json
```

### 7. Execute o Servidor de Desenvolvimento
```bash
source venv/bin/activate
uvicorn web_app.main:app --reload --host 0.0.0.0 --port 8000
```

**Acesse**: http://localhost:8000

---

## Instalação - Produção

### 1. Preparação do Servidor

**Atualize o sistema:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Instale dependências do sistema:**
```bash
sudo apt install -y python3-pip python3-venv git curl wget nginx supervisor
```

### 2. Crie Usuário para o Serviço
```bash
sudo useradd -m -s /bin/bash cs2analyzer
sudo su - cs2analyzer
```

### 3. Clone e Configure o Projeto
```bash
cd /home/cs2analyzer
git clone <url-do-repositorio> cs2analyzer
cd cs2analyzer

# Crie o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install --upgrade pip
pip install -r requirements.txt

# Instale o parser (mesmo processo do desenvolvimento)
# ... (veja seção anterior)

# Crie estrutura de pastas
mkdir -p demo_analysis web_app/static/team_logos logs
echo "[]" > teams.json
echo "[]" > tournaments.json
```

### 4. Configure Variáveis de Ambiente

Crie arquivo `.env`:
```bash
nano /home/cs2analyzer/cs2analyzer/.env
```

Conteúdo:
```env
# Produção
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Segurança
SECRET_KEY=sua-chave-secreta-aqui-gere-com-openssl-rand-hex-32
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Uploads
MAX_UPLOAD_SIZE=524288000  # 500MB em bytes
DEMO_ANALYSIS_DIR=/home/cs2analyzer/cs2analyzer/demo_analysis

# Parser
PARSER_PATH=/home/cs2analyzer/cs2analyzer/cs2-parser
PARSER_TIMEOUT=300  # 5 minutos

# Logs
LOG_LEVEL=INFO
LOG_FILE=/home/cs2analyzer/cs2analyzer/logs/app.log
```

### 5. Teste o Servidor
```bash
source venv/bin/activate
uvicorn web_app.main:app --host 0.0.0.0 --port 8000
```

Pressione `Ctrl+C` para parar.

---

## Configuração do Servidor Web

### Nginx como Reverse Proxy

**1. Crie arquivo de configuração:**
```bash
sudo nano /etc/nginx/sites-available/cs2analyzer
```

**Conteúdo:**
```nginx
upstream cs2analyzer {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    client_max_body_size 500M;
    client_body_timeout 300s;

    # Logs
    access_log /var/log/nginx/cs2analyzer-access.log;
    error_log /var/log/nginx/cs2analyzer-error.log;

    # Arquivos estáticos
    location /static/ {
        alias /home/cs2analyzer/cs2analyzer/web_app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy para FastAPI
    location / {
        proxy_pass http://cs2analyzer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout para uploads grandes
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

**2. Ative a configuração:**
```bash
sudo ln -s /etc/nginx/sites-available/cs2analyzer /etc/nginx/sites-enabled/
sudo nginx -t  # Testa a configuração
sudo systemctl restart nginx
```

### SSL/HTTPS com Let's Encrypt

**1. Instale Certbot:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

**2. Obtenha certificado:**
```bash
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

**3. Auto-renovação:**
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Configuração do Serviço Systemd

### 1. Crie o Arquivo de Serviço
```bash
sudo nano /etc/systemd/system/cs2analyzer.service
```

**Conteúdo:**
```ini
[Unit]
Description=CS2 Analyzer - Counter-Strike 2 Demo Analysis Platform
After=network.target

[Service]
Type=simple
User=cs2analyzer
Group=cs2analyzer
WorkingDirectory=/home/cs2analyzer/cs2analyzer
Environment="PATH=/home/cs2analyzer/cs2analyzer/venv/bin"
ExecStart=/home/cs2analyzer/cs2analyzer/venv/bin/uvicorn web_app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Restart
Restart=always
RestartSec=10

# Logs
StandardOutput=append:/home/cs2analyzer/cs2analyzer/logs/systemd-out.log
StandardError=append:/home/cs2analyzer/cs2analyzer/logs/systemd-err.log

# Limites
LimitNOFILE=65535
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### 2. Ative e Inicie o Serviço
```bash
sudo systemctl daemon-reload
sudo systemctl enable cs2analyzer
sudo systemctl start cs2analyzer
```

### 3. Comandos Úteis
```bash
# Ver status
sudo systemctl status cs2analyzer

# Parar serviço
sudo systemctl stop cs2analyzer

# Reiniciar serviço
sudo systemctl restart cs2analyzer

# Ver logs em tempo real
sudo journalctl -u cs2analyzer -f

# Ver logs do arquivo
tail -f /home/cs2analyzer/cs2analyzer/logs/systemd-out.log
```

---

## Backup e Manutenção

### Script de Backup Automático

**Crie o script:**
```bash
sudo nano /home/cs2analyzer/backup.sh
```

**Conteúdo:**
```bash
#!/bin/bash

# Configurações
BACKUP_DIR="/home/cs2analyzer/backups"
PROJECT_DIR="/home/cs2analyzer/cs2analyzer"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="cs2analyzer_backup_${DATE}.tar.gz"

# Criar pasta de backup
mkdir -p $BACKUP_DIR

# Fazer backup
cd $PROJECT_DIR
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    demo_analysis/ \
    teams.json \
    tournaments.json \
    web_app/static/team_logos/

# Manter apenas os últimos 7 dias
find $BACKUP_DIR -name "cs2analyzer_backup_*.tar.gz" -mtime +7 -delete

echo "✅ Backup criado: ${BACKUP_NAME}"
```

**Torne executável e configure cron:**
```bash
chmod +x /home/cs2analyzer/backup.sh

# Adicione ao crontab (backup diário às 3h)
crontab -e
# Adicione a linha:
0 3 * * * /home/cs2analyzer/backup.sh >> /home/cs2analyzer/logs/backup.log 2>&1
```

### Limpeza de Demos Antigas

**Script de limpeza:**
```bash
nano /home/cs2analyzer/cleanup.sh
```

**Conteúdo:**
```bash
#!/bin/bash

# Remove demos mais antigas que 30 dias
find /home/cs2analyzer/cs2analyzer/demo_analysis -name "*.dem" -mtime +30 -delete

# Remove análises órfãs (sem .dem correspondente)
cd /home/cs2analyzer/cs2analyzer/demo_analysis
for dir in */; do
    if [ ! -f "${dir}demo.dem" ]; then
        echo "🗑️ Removendo análise órfã: $dir"
        rm -rf "$dir"
    fi
done

echo "✅ Limpeza concluída"
```

```bash
chmod +x /home/cs2analyzer/cleanup.sh

# Cron semanal (todo domingo às 4h)
crontab -e
# Adicione:
0 4 * * 0 /home/cs2analyzer/cleanup.sh >> /home/cs2analyzer/logs/cleanup.log 2>&1
```

### Monitoramento de Recursos

**Instale htop:**
```bash
sudo apt install htop
```

**Monitore em tempo real:**
```bash
htop -u cs2analyzer
```

---

## Troubleshooting

### Problema: Servidor não inicia

**Verifique logs:**
```bash
sudo journalctl -u cs2analyzer -n 100
tail -f /home/cs2analyzer/cs2analyzer/logs/systemd-err.log
```

**Verifique porta:**
```bash
sudo lsof -i :8000
```

**Mate processos:**
```bash
sudo lsof -ti:8000 | xargs kill -9
sudo systemctl restart cs2analyzer
```

### Problema: Parser não funciona

**Teste o parser manualmente:**
```bash
cd /home/cs2analyzer/cs2analyzer
./cs2-parser -demo /caminho/para/demo.dem
```

**Verifique permissões:**
```bash
chmod +x cs2-parser
```

**Recompile:**
```bash
cd /tmp/demoinfocs-golang/examples/print_events
go build -o cs2-parser
mv cs2-parser /home/cs2analyzer/cs2analyzer/
```

### Problema: Upload falha

**Verifique tamanho máximo no Nginx:**
```nginx
# /etc/nginx/sites-available/cs2analyzer
client_max_body_size 500M;
```

**Verifique permissões da pasta:**
```bash
sudo chown -R cs2analyzer:cs2analyzer /home/cs2analyzer/cs2analyzer/demo_analysis
chmod 755 /home/cs2analyzer/cs2analyzer/demo_analysis
```

### Problema: Alto uso de memória

**Reduza workers:**
```bash
# /etc/systemd/system/cs2analyzer.service
ExecStart=... --workers 2  # Ao invés de 4
```

**Limite memória do processo:**
```ini
# Adicione ao [Service]
MemoryMax=4G
```

### Problema: Análise trava

**Aumente timeout:**
```bash
# .env
PARSER_TIMEOUT=600  # 10 minutos
```

**Verifique espaço em disco:**
```bash
df -h
```

### Logs Úteis

**Nginx:**
```bash
tail -f /var/log/nginx/cs2analyzer-error.log
tail -f /var/log/nginx/cs2analyzer-access.log
```

**Aplicação:**
```bash
tail -f /home/cs2analyzer/cs2analyzer/logs/systemd-out.log
tail -f /home/cs2analyzer/cs2analyzer/logs/app.log
```

**Systemd:**
```bash
journalctl -u cs2analyzer -f
journalctl -u nginx -f
```

---

## Atualização do Sistema

### 1. Faça Backup
```bash
/home/cs2analyzer/backup.sh
```

### 2. Pare o Serviço
```bash
sudo systemctl stop cs2analyzer
```

### 3. Atualize o Código
```bash
cd /home/cs2analyzer/cs2analyzer
git pull origin main
```

### 4. Atualize Dependências
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 5. Reinicie o Serviço
```bash
sudo systemctl start cs2analyzer
sudo systemctl status cs2analyzer
```

---

## Configurações de Segurança

### Firewall (UFW)
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Fail2ban (proteção contra brute force)
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Permissões Restritas
```bash
# Somente owner pode escrever
chmod 644 teams.json tournaments.json
chmod 755 demo_analysis/

# Proteja arquivos sensíveis
chmod 600 .env
```

---

## Performance e Otimização

### 1. Use Múltiplos Workers
```bash
# /etc/systemd/system/cs2analyzer.service
ExecStart=... --workers 4  # CPU cores
```

### 2. Configure Cache no Nginx
```nginx
# Cache de arquivos estáticos
location /static/ {
    alias /home/cs2analyzer/cs2analyzer/web_app/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
    gzip on;
    gzip_types text/css application/javascript image/svg+xml;
}
```

### 3. Otimize Uploads
```nginx
# Buffer para uploads grandes
client_body_buffer_size 128k;
client_body_in_file_only off;
```

---

## Checklist de Deploy

- [ ] Servidor atualizado (`apt update && apt upgrade`)
- [ ] Python 3.9+ instalado
- [ ] Go 1.19+ instalado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Parser compilado e funcionando
- [ ] Pastas criadas (demo_analysis, logs, etc.)
- [ ] Arquivos .json inicializados
- [ ] Variáveis de ambiente configuradas (.env)
- [ ] Nginx instalado e configurado
- [ ] SSL/HTTPS configurado (Let's Encrypt)
- [ ] Serviço systemd criado e ativado
- [ ] Firewall configurado (UFW)
- [ ] Backup automático configurado
- [ ] Limpeza automática configurada
- [ ] Monitoramento ativo
- [ ] Testes realizados (upload, análise, visualização)

---

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs primeiro
2. Consulte a seção Troubleshooting
3. Abra uma issue no repositório do projeto
4. Entre em contato com a equipe de suporte

---

**Última atualização:** 2025-10-18
**Versão do documento:** 1.0.0
