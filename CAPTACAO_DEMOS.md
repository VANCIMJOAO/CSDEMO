# 📥 Guia de Captação de Demos - CS2 Analyzer

## Índice
1. [Visão Geral](#visão-geral)
2. [Método 1: Upload Manual via Web](#método-1-upload-manual-via-web)
3. [Método 2: Monitor Automático de Pasta](#método-2-monitor-automático-de-pasta)
4. [Método 3: Integração com Servidor GOTV](#método-3-integração-com-servidor-gotv)
5. [Método 4: Upload via FTP/SFTP](#método-4-upload-via-ftpsftp)
6. [Método 5: Compartilhamento de Rede (LAN Party)](#método-5-compartilhamento-de-rede-lan-party)
7. [Método 6: API REST](#método-6-api-rest)
8. [Combinando Métodos](#combinando-métodos)
9. [Monitoramento e Logs](#monitoramento-e-logs)

---

## Visão Geral

O CS2 Analyzer oferece **múltiplas formas** de captar demos para análise. Você pode usar uma ou combinar várias conforme sua necessidade:

| Método | Complexidade | Uso Ideal | Automático |
|--------|--------------|-----------|------------|
| Upload Web | ⭐ Fácil | Poucos demos, análise pontual | Não |
| Monitor de Pasta | ⭐⭐ Médio | Servidor GOTV, produção contínua | Sim |
| GOTV Integration | ⭐⭐⭐ Avançado | Servidor CS2 próprio | Sim |
| FTP/SFTP | ⭐⭐ Médio | Upload remoto, múltiplos usuários | Parcial |
| Rede Local | ⭐ Fácil | LAN parties, eventos presenciais | Parcial |
| API REST | ⭐⭐⭐ Avançado | Integração com outros sistemas | Parcial |

---

## Método 1: Upload Manual via Web

### Como Funciona
Interface web permite upload direto de arquivos .dem através do navegador.

### Configuração

**Já está ativo por padrão!** Apenas ajuste o tamanho máximo de upload se necessário.

**Nginx (`/etc/nginx/sites-available/cs2analyzer`):**
```nginx
server {
    ...
    client_max_body_size 500M;  # Ajuste conforme necessário
    client_body_timeout 300s;
    ...
}
```

**Reinicie o Nginx:**
```bash
sudo systemctl restart nginx
```

### Uso
1. Acesse a interface web (http://seu-dominio.com)
2. Clique em "Upload Demo" ou "Analisar Nova Demo"
3. Selecione o arquivo .dem
4. Aguarde processamento automático

### Vantagens
✅ Simples e intuitivo
✅ Não requer configuração adicional
✅ Ideal para usuários finais

### Desvantagens
❌ Manual, um arquivo por vez
❌ Requer interação humana

---

## Método 2: Monitor Automático de Pasta

### Como Funciona
O sistema monitora automaticamente uma pasta e processa qualquer arquivo .dem adicionado a ela.

### Arquitetura

```
demos/
├── demo1.dem                    → Análise automática
├── demo2.dem                    → Análise automática
└── campeonatos/                 → Organização por torneio
    ├── torneio_A/
    │   ├── match1.dem
    │   └── match2.dem
    └── torneio_B/
        └── final.dem
```

### Configuração

**1. O monitor já está ativo quando o servidor inicia!**

Verificar em `web_app/main.py` (linhas 86-94):
```python
# === INICIALIZAR MONITOR ===
monitor = DemoMonitor(DEMOS_DIR, ANALYSIS_DIR, interval=30)

@app.on_event("startup")
async def startup_event():
    """Inicia o monitor automático ao subir o servidor"""
    monitor.start()
```

**2. Ajustar intervalo de verificação (opcional):**

Edite `web_app/main.py`:
```python
monitor = DemoMonitor(DEMOS_DIR, ANALYSIS_DIR, interval=10)  # Verifica a cada 10s
```

**3. Estrutura de pastas:**
```bash
cd /home/cs2analyzer/cs2analyzer
mkdir -p demos/campeonatos
chmod 755 demos
chmod 755 demos/campeonatos
```

### Como Usar

**Opção A - Demos avulsos:**
```bash
# Copie demos diretamente para a pasta demos/
cp /caminho/para/demo.dem /home/cs2analyzer/cs2analyzer/demos/

# Ou use rsync para múltiplos arquivos
rsync -av /origem/*.dem /home/cs2analyzer/cs2analyzer/demos/
```

**Opção B - Demos de torneios:**
```bash
# Crie subpasta para o torneio
mkdir -p /home/cs2analyzer/cs2analyzer/demos/campeonatos/brasileiro_2025

# Copie demos do torneio
cp match*.dem /home/cs2analyzer/cs2analyzer/demos/campeonatos/brasileiro_2025/
```

### Monitoramento

Verificar logs do monitor:
```bash
# Ver logs do sistema
sudo journalctl -u cs2analyzer -f | grep "Monitor"

# Ver demos processados
cat /home/cs2analyzer/cs2analyzer/demo_analysis/processed_demos.json
```

### Vantagens
✅ Totalmente automático
✅ Suporta organização por torneios
✅ Processa múltiplos arquivos
✅ Evita reprocessamento (usa hash MD5)
✅ Detecta quando upload ainda está em progresso

### Desvantagens
❌ Requer acesso ao servidor
❌ Não tem interface gráfica

---

## Método 3: Integração com Servidor GOTV

### Como Funciona
Servidor CS2 salva demos automaticamente, script copia para pasta monitorada.

### Pré-requisitos
- Servidor CS2 com GOTV configurado
- Acesso SSH ao servidor CS2

### Configuração do Servidor CS2

**1. Configurar GOTV para salvar demos:**

Edite `csgo/cfg/server.cfg`:
```cfg
// GOTV Configuration
tv_enable 1
tv_delay 30
tv_advertise_watchable 1
tv_autorecord 1
tv_name "CS2 Analyzer GOTV"
```

**2. Demos são salvos em:**
```
/path/to/cs2/csgo/
```

### Script de Sincronização

**Opção A - Servidores no mesmo host:**

Crie `/home/cs2analyzer/sync_gotv.sh`:
```bash
#!/bin/bash

# Configurações
CS2_DEMOS_DIR="/path/to/cs2/csgo"
ANALYZER_DEMOS_DIR="/home/cs2analyzer/cs2analyzer/demos"
LOG_FILE="/home/cs2analyzer/logs/sync_gotv.log"

# Log
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando sincronização GOTV..." >> $LOG_FILE

# Copiar novos demos (apenas arquivos que não existem no destino)
rsync -av --ignore-existing \
    --include="*.dem" \
    --exclude="*" \
    "$CS2_DEMOS_DIR/" \
    "$ANALYZER_DEMOS_DIR/" >> $LOG_FILE 2>&1

# Contar arquivos sincronizados
NEW_FILES=$(rsync -avn --ignore-existing --include="*.dem" --exclude="*" "$CS2_DEMOS_DIR/" "$ANALYZER_DEMOS_DIR/" | grep '\.dem$' | wc -l)

if [ $NEW_FILES -gt 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $NEW_FILES novos demos sincronizados" >> $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  Nenhum novo demo" >> $LOG_FILE
fi
```

**Opção B - Servidores remotos:**

```bash
#!/bin/bash

# Configurações
REMOTE_USER="cs2server"
REMOTE_HOST="192.168.1.100"
REMOTE_PATH="/path/to/cs2/csgo"
ANALYZER_DEMOS_DIR="/home/cs2analyzer/cs2analyzer/demos"
LOG_FILE="/home/cs2analyzer/logs/sync_gotv.log"

# Sincronizar via SSH
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sincronizando de $REMOTE_HOST..." >> $LOG_FILE

rsync -av --ignore-existing \
    -e "ssh -i /home/cs2analyzer/.ssh/id_rsa" \
    --include="*.dem" \
    --exclude="*" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/" \
    "$ANALYZER_DEMOS_DIR/" >> $LOG_FILE 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sincronização concluída" >> $LOG_FILE
```

**3. Tornar executável:**
```bash
chmod +x /home/cs2analyzer/sync_gotv.sh
```

**4. Configurar cron para execução automática:**
```bash
crontab -e
```

Adicione (executa a cada 5 minutos):
```cron
*/5 * * * * /home/cs2analyzer/sync_gotv.sh
```

### Vantagens
✅ Totalmente automático
✅ Captura todas as partidas do servidor
✅ Ideal para ligas e competições

### Desvantagens
❌ Requer servidor CS2 próprio
❌ Configuração mais complexa
❌ Pode gerar muitos demos

---

## Método 4: Upload via FTP/SFTP

### Como Funciona
Usuários fazem upload via FTP/SFTP diretamente para a pasta monitorada.

### Configuração

**1. Instalar servidor SFTP (OpenSSH já tem):**
```bash
sudo apt install openssh-server
```

**2. Criar usuário específico para uploads:**
```bash
# Criar usuário sem acesso shell
sudo useradd -m -s /usr/sbin/nologin demouploader

# Definir senha
sudo passwd demouploader

# Dar permissão na pasta demos
sudo usermod -aG cs2analyzer demouploader
sudo chmod 775 /home/cs2analyzer/cs2analyzer/demos
```

**3. Configurar chroot (opcional, mais seguro):**

Edite `/etc/ssh/sshd_config`:
```
Match User demouploader
    ChrootDirectory /home/cs2analyzer/cs2analyzer/demos
    ForceCommand internal-sftp
    PermitTunnel no
    AllowAgentForwarding no
    AllowTcpForwarding no
    X11Forwarding no
```

Reinicie SSH:
```bash
sudo systemctl restart sshd
```

### Uso

**Clientes podem usar qualquer ferramenta SFTP:**

**FileZilla:**
- Host: sftp://seu-dominio.com
- Username: demouploader
- Password: [senha]
- Port: 22

**Linha de comando:**
```bash
sftp demouploader@seu-dominio.com
put /caminho/para/demo.dem
```

**WinSCP (Windows):**
- Protocol: SFTP
- Host: seu-dominio.com
- Username: demouploader
- Password: [senha]

### Vantagens
✅ Acesso remoto seguro
✅ Múltiplos usuários podem fazer upload
✅ Funciona em qualquer plataforma
✅ Não requer acesso à interface web

### Desvantagens
❌ Requer cliente FTP/SFTP
❌ Usuários precisam de credenciais

---

## Método 5: Compartilhamento de Rede (LAN Party)

### Como Funciona
Pasta de demos é compartilhada via Samba (SMB), usuários na rede local copiam demos diretamente.

### Configuração

**1. Instalar Samba:**
```bash
sudo apt install samba samba-common-bin
```

**2. Configurar compartilhamento:**

Edite `/etc/samba/smb.conf`:
```ini
[CS2Demos]
   comment = CS2 Analyzer - Upload de Demos
   path = /home/cs2analyzer/cs2analyzer/demos
   browseable = yes
   writable = yes
   guest ok = no
   valid users = cs2analyzer, @cs2analyzer
   create mask = 0664
   directory mask = 0775
   force user = cs2analyzer
   force group = cs2analyzer
```

**3. Criar senha Samba para usuário:**
```bash
sudo smbpasswd -a cs2analyzer
```

**4. Reiniciar Samba:**
```bash
sudo systemctl restart smbd
sudo systemctl enable smbd
```

**5. Abrir firewall:**
```bash
sudo ufw allow samba
```

### Uso

**Windows:**
1. Abrir Windows Explorer
2. Digite: `\\IP-DO-SERVIDOR\CS2Demos`
3. Autentique com: cs2analyzer / [senha]
4. Arraste e solte arquivos .dem

**Linux:**
```bash
# Montar compartilhamento
sudo mount -t cifs //IP-DO-SERVIDOR/CS2Demos /mnt/cs2demos -o username=cs2analyzer

# Copiar demos
cp *.dem /mnt/cs2demos/
```

**macOS:**
1. Finder → Go → Connect to Server
2. Digite: `smb://IP-DO-SERVIDOR/CS2Demos`
3. Autentique e arraste arquivos

### Vantagens
✅ Ideal para LAN parties e eventos
✅ Usuários na rede local copiam diretamente
✅ Não precisa internet
✅ Familiar para usuários Windows

### Desvantagens
❌ Apenas na rede local
❌ Questões de segurança se mal configurado
❌ Performance pode variar

---

## Método 6: API REST

### Como Funciona
Upload programático via HTTP POST.

### Endpoint

```
POST http://seu-dominio.com/upload
Content-Type: multipart/form-data

Campos:
- file: arquivo .dem (required)
- team1: nome do time 1 (optional)
- team2: nome do time 2 (optional)
- tournament: ID do torneio (optional)
```

### Exemplo de Uso

**cURL:**
```bash
curl -X POST \
  -F "file=@/caminho/para/demo.dem" \
  -F "team1=FURIA" \
  -F "team2=MIBR" \
  -F "tournament=brasileirao2025" \
  http://seu-dominio.com/upload
```

**Python:**
```python
import requests

url = "http://seu-dominio.com/upload"
files = {'file': open('demo.dem', 'rb')}
data = {
    'team1': 'FURIA',
    'team2': 'MIBR',
    'tournament': 'brasileirao2025'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**JavaScript (Node.js):**
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('demo.dem'));
form.append('team1', 'FURIA');
form.append('team2', 'MIBR');

axios.post('http://seu-dominio.com/upload', form, {
  headers: form.getHeaders()
}).then(response => {
  console.log(response.data);
});
```

### Autenticação (Adicionar se necessário)

Se quiser proteger a API, adicione em `web_app/main.py`:

```python
from fastapi import Header, HTTPException

API_KEY = "sua-chave-secreta-aqui"  # Salvar em .env

@app.post("/upload")
async def upload_demo(
    file: UploadFile,
    x_api_key: str = Header(None)
):
    # Validar API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")

    # Resto do código...
```

Uso com autenticação:
```bash
curl -X POST \
  -H "X-API-Key: sua-chave-secreta-aqui" \
  -F "file=@demo.dem" \
  http://seu-dominio.com/upload
```

### Vantagens
✅ Automação completa
✅ Integração com outros sistemas
✅ Pode adicionar autenticação

### Desvantagens
❌ Requer conhecimento de programação
❌ Necessita implementar autenticação para segurança

---

## Combinando Métodos

### Cenário 1: Liga Profissional

**Setup:**
- Servidor GOTV gravando todas as partidas
- Script rsync sincronizando a cada 5 minutos
- Monitor automático processando demos
- Interface web para gestão manual

**Resultado:** Análise automática de todas as partidas da liga.

---

### Cenário 2: LAN Party / Evento Presencial

**Setup:**
- Compartilhamento Samba na rede local
- Monitor automático processando demos
- Tela exibindo estatísticas em tempo real

**Resultado:** Participantes copiam demos via rede, análise automática, rankings atualizados.

---

### Cenário 3: Comunidade Online

**Setup:**
- Upload web para usuários finais
- FTP/SFTP para organizadores de torneios
- API REST para bots do Discord
- Monitor automático processando tudo

**Resultado:** Múltiplos canais de upload, análise centralizada.

---

## Monitoramento e Logs

### Verificar Status do Monitor

```bash
# Ver se o monitor está rodando
sudo systemctl status cs2analyzer

# Ver logs em tempo real
sudo journalctl -u cs2analyzer -f | grep -i "monitor\|demo"
```

### Ver Demos Processados

```bash
# Arquivo JSON com histórico
cat /home/cs2analyzer/cs2analyzer/demo_analysis/processed_demos.json

# Contar demos processados
cat /home/cs2analyzer/cs2analyzer/demo_analysis/processed_demos.json | jq '. | length'
```

### Logs Úteis

```bash
# Logs do monitor
sudo journalctl -u cs2analyzer -n 100 | grep "Analisando\|Análise concluída"

# Logs de upload web
tail -f /home/cs2analyzer/cs2analyzer/logs/systemd-out.log | grep -i upload

# Logs de sincronização GOTV (se configurado)
tail -f /home/cs2analyzer/logs/sync_gotv.log
```

### Estatísticas

Criar script de estatísticas `/home/cs2analyzer/demo_stats.sh`:
```bash
#!/bin/bash

echo "📊 CS2 Analyzer - Estatísticas de Demos"
echo "========================================"
echo ""

# Demos na pasta de monitoramento
DEMOS_COUNT=$(find /home/cs2analyzer/cs2analyzer/demos -name "*.dem" | wc -l)
echo "📁 Demos na pasta: $DEMOS_COUNT"

# Demos processados
PROCESSED_COUNT=$(cat /home/cs2analyzer/cs2analyzer/demo_analysis/processed_demos.json | jq '. | length')
echo "✅ Demos processados: $PROCESSED_COUNT"

# Análises disponíveis
ANALYSIS_COUNT=$(find /home/cs2analyzer/cs2analyzer/demo_analysis -name "match_info.json" | wc -l)
echo "📈 Análises disponíveis: $ANALYSIS_COUNT"

# Espaço usado
DEMOS_SIZE=$(du -sh /home/cs2analyzer/cs2analyzer/demos | cut -f1)
ANALYSIS_SIZE=$(du -sh /home/cs2analyzer/cs2analyzer/demo_analysis | cut -f1)
echo "💾 Espaço demos: $DEMOS_SIZE"
echo "💾 Espaço análises: $ANALYSIS_SIZE"

echo ""
echo "🕐 Última atualização: $(date '+%Y-%m-%d %H:%M:%S')"
```

---

## Recomendações por Cenário

### Pequena Comunidade
- **Use:** Upload Web + Monitor Automático
- **Complexidade:** Baixa
- **Esforço:** Mínimo

### Servidor GOTV Próprio
- **Use:** Sincronização GOTV + Monitor Automático
- **Complexidade:** Média
- **Esforço:** Configuração inicial apenas

### LAN Party / Evento
- **Use:** Samba Share + Monitor Automático
- **Complexidade:** Baixa
- **Esforço:** Configuração inicial

### Liga Profissional
- **Use:** GOTV + FTP + API + Monitor
- **Complexidade:** Alta
- **Esforço:** Configuração e manutenção

### Integração com Bots
- **Use:** API REST
- **Complexidade:** Alta
- **Esforço:** Desenvolvimento necessário

---

## Troubleshooting

### Monitor não processa demos

**Verificar se o monitor está rodando:**
```bash
sudo systemctl status cs2analyzer
```

**Verificar permissões:**
```bash
ls -la /home/cs2analyzer/cs2analyzer/demos
# Deve ser cs2analyzer:cs2analyzer com permissão 755
```

**Verificar logs:**
```bash
sudo journalctl -u cs2analyzer -n 50
```

### Demos não aparecem após upload

**Verificar hash MD5:**
```bash
# Se o mesmo arquivo for enviado novamente, ele não será reprocessado
# Para forçar reprocessamento, edite processed_demos.json ou renomeie o arquivo
```

**Verificar tamanho do arquivo:**
```bash
# Arquivos muito pequenos ou corrompidos são ignorados
ls -lh /home/cs2analyzer/cs2analyzer/demos/*.dem
```

### Sincronização GOTV não funciona

**Verificar conectividade:**
```bash
ssh usuario@servidor-cs2  # Deve conectar sem pedir senha
```

**Verificar cron:**
```bash
crontab -l  # Deve mostrar o job
grep CRON /var/log/syslog | tail -20  # Ver execuções
```

**Testar script manualmente:**
```bash
bash -x /home/cs2analyzer/sync_gotv.sh
```

---

## Segurança

### Validação de Arquivos

O sistema já valida:
- ✅ Extensão .dem
- ✅ Tamanho máximo (500MB padrão)
- ✅ Hash MD5 para evitar duplicatas

### Recomendações Adicionais

1. **Limite taxa de upload (rate limiting):**
```nginx
# /etc/nginx/sites-available/cs2analyzer
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/m;

location /upload {
    limit_req zone=upload_limit burst=5;
    ...
}
```

2. **Monitorar espaço em disco:**
```bash
# Criar alerta se disco atingir 80%
df -h | awk '$5+0 > 80 {print "⚠️ ALERTA: Disco em " $5}'
```

3. **Backup regular:**
```bash
# Use o script de backup documentado em DEPLOY.md
/home/cs2analyzer/backup.sh
```

---

## Próximos Passos

Após configurar a captação de demos:

1. ✅ Configure backup automático (ver DEPLOY.md)
2. ✅ Configure limpeza de demos antigos (ver DEPLOY.md)
3. ✅ Monitore espaço em disco
4. ✅ Configure alertas de falhas
5. ✅ Documente o processo para sua equipe

---

**Última atualização:** 2025-10-18
**Versão:** 1.0.0

Para mais informações, consulte:
- [DEPLOY.md](DEPLOY.md) - Deployment completo
- [MANUAL_USUARIO.md](MANUAL_USUARIO.md) - Uso da interface
- [README.md](README.md) - Visão geral do projeto
