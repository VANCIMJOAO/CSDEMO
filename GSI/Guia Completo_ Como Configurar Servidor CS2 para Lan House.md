# Guia Completo: Como Configurar Servidor CS2 para Lan House

**Autor:** Manus AI**Data:** 18 de outubro de 2025

## Introdução

Este guia explica como configurar um servidor dedicado de Counter-Strike 2 (CS2) para sua lan house e conectá-lo ao dashboard de campeonatos que desenvolvemos. Existem duas abordagens principais que você pode usar, dependendo das suas necessidades.

---

## Opção 1: Servidor Local Simples (Recomendado para Lan House)

Esta é a opção mais simples e recomendada para lan houses. Um dos computadores da lan house roda o jogo normalmente e hospeda a partida, enquanto os outros jogadores se conectam a ele.

### Vantagens

- ✅ Não requer servidor dedicado separado

- ✅ Configuração muito simples

- ✅ Funciona perfeitamente em rede local

- ✅ Não precisa de token de servidor Steam

- ✅ Ideal para campeonatos locais

### Passo a Passo

#### 1. Preparar o Computador Host

Escolha um dos computadores da lan house para ser o host da partida. Este computador deve ter o CS2 instalado e o dashboard rodando (se quiser monitorar a partida).

#### 2. Configurar o Arquivo GSI no Host

No computador que vai hospedar a partida, instale o arquivo `gamestate_integration_lanhouse.cfg` na pasta:

```
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\
```

**Importante:** Se o dashboard estiver rodando em outro computador da rede, edite o arquivo `.cfg` e altere a linha:

```
"uri" "http://127.0.0.1:3001"
```

Para:

```
"uri" "http://IP_DO_COMPUTADOR_COM_DASHBOARD:3001"
```

Por exemplo: `"uri" "http://192.168.1.100:3001"`

#### 3. Iniciar a Partida no CS2

No computador host, abra o CS2 e siga estes passos:

1. **Abra o console** (tecla `~` - se não funcionar, ative nas configurações)

1. **Configure o servidor para LAN:**

1. **Configure o modo de jogo** (escolha um):

1. **Carregue o mapa:**

1. **Adicione bots se necessário:**

#### 4. Conectar os Outros Jogadores

Nos outros computadores da lan house:

1. Abra o CS2

1. Abra o console (`~`)

1. Digite o comando:

**Dica:** Para descobrir o IP do host:

- **Windows:** Abra o Prompt de Comando e digite `ipconfig`

- Procure por "Endereço IPv4" na seção da sua placa de rede

#### 5. Comandos Úteis para o Host

Durante a partida, o host pode usar estes comandos no console:

```
// Iniciar a partida (pular warmup)
mp_warmup_end

// Reiniciar o round atual
mp_restartgame 1

// Pausar a partida
pause

// Despausar
unpause

// Trocar jogador de time
mp_switchteams

// Configurar tempo do round (em segundos)
mp_roundtime 1.92  // 1:55 (competitivo)

// Configurar tempo de compra (em segundos)
mp_buytime 20

// Ativar/desativar fogo amigo
mp_friendlyfire 0

// Configurar dinheiro inicial
mp_startmoney 800

// Dar dinheiro a todos
mp_maxmoney 16000
```

---

## Opção 2: Servidor Dedicado (Para Uso Avançado)

Se você quiser um servidor que roda 24/7 ou precisa de mais controle, pode configurar um servidor dedicado. Esta opção é mais complexa.

### Requisitos Mínimos

- **RAM:** 2GB

- **Armazenamento:** 65GB

- **CPU:** x86-64-v2 (com POPCNT/SSE4.2)

- **Sistema Operacional:** Windows 10/11 ou Linux (Ubuntu 20.04+)

- **Conexão de Internet:** Estável com boa velocidade de upload

### Passo a Passo para Windows

#### 1. Instalar o SteamCMD

1. Baixe o SteamCMD: [https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip](https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip)

1. Extraia para uma pasta, por exemplo: `C:\steamcmd\`

1. Execute `steamcmd.exe`

#### 2. Baixar o Servidor CS2

No SteamCMD, digite os seguintes comandos:

```
force_install_dir C:\cs2-server\
login anonymous
app_update 730 validate
quit
```

**Nota:** O download é de aproximadamente 60GB e pode demorar bastante.

#### 3. Obter um Game Server Login Token (GSLT)

Para que outros jogadores possam se conectar ao seu servidor pela internet, você precisa de um token:

1. Acesse: [https://steamcommunity.com/dev/managegameservers](https://steamcommunity.com/dev/managegameservers)

1. Faça login com sua conta Steam

1. Em "App ID", digite: `730`

1. Em "Memo", coloque um nome para identificar (ex: "Servidor Lan House")

1. Clique em "Create"

1. **Copie o token gerado** (você vai precisar dele)

#### 4. Criar Arquivo de Configuração

Crie um arquivo chamado `server.cfg` na pasta:

```
C:\cs2-server\game\csgo\cfg\
```

Com o seguinte conteúdo:

```
// Nome do servidor
hostname "Lan House - Servidor CS2"

// Senha do servidor (deixe vazio para público)
sv_password ""

// Configurações de rede
sv_lan 0  // 0 = internet, 1 = apenas LAN
sv_region 1  // 1 = América do Sul

// Configurações de jogo
mp_maxrounds 30
mp_roundtime 1.92
mp_buytime 20
mp_startmoney 800
mp_friendlyfire 0

// Logs
sv_logfile 1
sv_logecho 1

// RCON (administração remota)
rcon_password "SuaSenhaAqui"
```

#### 5. Criar Script de Inicialização

Crie um arquivo `start_server.bat` na pasta `C:\cs2-server\` com:

```
@echo off
cd /d C:\cs2-server\game\bin\win64\
cs2.exe -dedicated -console +map de_dust2 +game_alias competitive +sv_setsteamaccount SEU_TOKEN_AQUI -maxplayers 10 -port 27015
```

**Importante:** Substitua `SEU_TOKEN_AQUI` pelo token que você obteve no passo 3.

#### 6. Configurar Firewall e Portas

Você precisa liberar as seguintes portas no firewall e no roteador:

- **27015** (UDP/TCP) - Porta do jogo

- **27020** (UDP) - SourceTV

**No Windows Firewall:**

1. Painel de Controle → Sistema e Segurança → Firewall do Windows

1. Configurações avançadas → Regras de Entrada

1. Nova Regra → Porta → UDP → 27015, 27020

1. Permitir conexão

**No Roteador:** Configure o Port Forwarding para o IP do computador do servidor.

#### 7. Iniciar o Servidor

Execute o arquivo `start_server.bat` que você criou. O servidor começará a rodar.

#### 8. Conectar ao Servidor

Para conectar ao servidor:

1. Abra o CS2

1. Abra o console

1. Digite:

Para descobrir seu IP público, acesse: [https://www.whatismyip.com/](https://www.whatismyip.com/)

---

## Configurando o Dashboard para Servidor Dedicado

Se você está usando um servidor dedicado, precisa configurar o GSI para enviar dados para o dashboard.

### Se o Dashboard está no mesmo computador do servidor:

Use o arquivo `.cfg` padrão com:

```
"uri" "http://127.0.0.1:3001"
```

### Se o Dashboard está em outro computador:

1. Descubra o IP do computador onde o dashboard está rodando

1. Edite o arquivo `gamestate_integration_lanhouse.cfg`

1. Altere para:

### Instalação do arquivo GSI no servidor dedicado:

Copie o arquivo `gamestate_integration_lanhouse.cfg` para:

```
C:\cs2-server\game\csgo\cfg\
```

**Importante:** O GSI só funciona quando alguém está espectando ou jogando no servidor. Para monitorar partidas sem jogadores humanos, você precisa ter pelo menos um espectador conectado.

---

## Configuração para Múltiplos Computadores na Lan House

Para que todos os computadores da lan house enviem dados para o mesmo dashboard:

1. **Instale o dashboard em um computador central** (pode ser o servidor ou um computador separado)

1. **Em cada computador da lan house:**
  - Instale o arquivo `gamestate_integration_lanhouse.cfg` na pasta do CS2
  - Edite o arquivo e configure o IP do computador com o dashboard:

1. **Certifique-se de que a porta 3001 está acessível:**
  - Desative o firewall temporariamente para testar
  - Se funcionar, crie uma regra para liberar a porta 3001

1. **Teste a conexão:**
  - Abra o navegador em qualquer computador da lan house
  - Acesse: `http://IP_DO_DASHBOARD:3000`
  - Você deve ver o dashboard

---

## Comandos Úteis do Servidor

### Gerenciamento de Partida

```
// Mudar de mapa
changelevel de_mirage

// Executar arquivo de configuração
exec server.cfg

// Listar jogadores conectados
status

// Kickar jogador
kick "nome_do_jogador"

// Banir jogador
banid 0 STEAMID

// Adicionar admin (via RCON)
rcon_password "sua_senha"
rcon sv_cheats 1
```

### Configurações de Modo de Jogo

```
// Competitivo 5v5
game_alias competitive
mp_maxrounds 30
mp_overtime_enable 1

// Wingman 2v2
game_alias wingman
mp_maxrounds 16

// Casual
game_alias casual
mp_maxrounds 15

// Deathmatch
game_alias deathmatch
mp_timelimit 10
```

---

## Solução de Problemas

### Dashboard não recebe dados

1. **Verifique se o servidor GSI está rodando:**
  - Acesse: `http://localhost:3001/health`
  - Deve retornar: `{"status":"ok"}`

1. **Verifique o arquivo .cfg:**
  - Confirme que está na pasta correta
  - Verifique se o IP está correto
  - Confirme que não há erros de sintaxe

1. **Verifique o firewall:**
  - Temporariamente desative o firewall para testar
  - Se funcionar, crie regra para porta 3001

1. **Verifique os logs do servidor:**
  - No terminal onde o dashboard está rodando, procure por mensagens `[GSI]`
  - Deve aparecer: `[GSI] Server listening on port 3001`

### Jogadores não conseguem conectar

1. **Servidor LAN:**
  - Confirme que todos estão na mesma rede
  - Use `ipconfig` para verificar IPs
  - Tente fazer ping: `ping IP_DO_HOST`

1. **Servidor Dedicado:**
  - Verifique se as portas estão abertas no firewall
  - Confirme o port forwarding no roteador
  - Teste a conexão de dentro da rede primeiro

### Servidor não inicia

1. **Verifique se o Steam está instalado** (necessário no Windows)

1. **Confirme que o token GSLT está correto**

1. **Verifique os logs de erro** no console do servidor

---

## Recomendações para Campeonatos

### Antes do Campeonato

1. **Teste tudo com antecedência:**
  - Faça uma partida teste completa
  - Verifique se o dashboard está recebendo dados
  - Confirme que todos os computadores conseguem conectar

1. **Prepare configurações:**
  - Crie arquivos `.cfg` para diferentes modos de jogo
  - Tenha uma lista de mapas disponíveis
  - Configure senhas se necessário

1. **Backup:**
  - Faça backup dos arquivos de configuração
  - Tenha o instalador do CS2 pronto caso precise reinstalar

### Durante o Campeonato

1. **Monitore o dashboard** em um monitor/TV separado para os espectadores

1. **Use comandos de pausa** se houver problemas técnicos

1. **Salve demos** das partidas importantes (ativado por padrão)

### Configurações Recomendadas para Competitivo

```
mp_maxrounds 30
mp_overtime_enable 1
mp_overtime_maxrounds 6
mp_roundtime 1.92
mp_roundtime_defuse 1.92
mp_buytime 20
mp_buy_anywhere 0
mp_freezetime 15
mp_friendlyfire 1
mp_autokick 0
mp_autoteambalance 0
mp_limitteams 0
sv_alltalk 0
sv_deadtalk 0
```

---

## Conclusão

Para a maioria das lan houses, a **Opção 1 (Servidor Local Simples)** é mais do que suficiente. É fácil de configurar, não requer hardware adicional e funciona perfeitamente para campeonatos locais.

A **Opção 2 (Servidor Dedicado)** é recomendada apenas se você:

- Quer que o servidor rode 24/7

- Precisa que jogadores de fora da lan house se conectem

- Quer separar completamente o servidor dos computadores dos jogadores

Em ambos os casos, o dashboard que desenvolvemos funcionará perfeitamente para exibir os dados das partidas em tempo real!

---

## Referências

- [Documentação Oficial - CS2 Dedicated Servers](https://developer.valvesoftware.com/wiki/Counter-Strike_2/Dedicated_Servers)

- [SteamCMD](https://developer.valvesoftware.com/wiki/SteamCMD)

- [Game Server Login Token](https://steamcommunity.com/dev/managegameservers)

---

## Configuração Avançada de Rede para Lan House

### Otimizando a Rede Local

Para garantir a melhor experiência nos campeonatos, siga estas recomendações:

#### 1. Use Cabos Ethernet

- **Sempre prefira cabo ao Wi-Fi** para jogos competitivos

- Use cabos Cat5e ou Cat6 (mínimo)

- Evite cabos muito longos (máximo 100 metros)

- Teste os cabos antes do campeonato

#### 2. Configure um Switch Gigabit

- Use um switch gerenciável se possível

- Ative QoS (Quality of Service) para priorizar tráfego de jogos

- Desative spanning tree se não for necessário

- Configure VLANs se tiver muitos computadores

#### 3. Configure IPs Estáticos (Opcional mas Recomendado)

Para facilitar a gestão, configure IPs fixos para cada computador:

**No Windows:**

1. Painel de Controle → Rede e Internet → Central de Rede e Compartilhamento

1. Clique na conexão ativa → Propriedades

1. Selecione "Protocolo IP Versão 4 (TCP/IPv4)" → Propriedades

1. Marque "Usar o seguinte endereço IP"

1. Configure:
  - **IP:** 192.168.1.10 (incremente para cada PC: .11, .12, .13, etc)
  - **Máscara:** 255.255.255.0
  - **Gateway:** 192.168.1.1 (IP do roteador)
  - **DNS:** 8.8.8.8 e 8.8.4.4 (Google DNS)

#### 4. Otimize as Configurações de Rede do Windows

Execute estes comandos no PowerShell como Administrador:

```
# Desabilitar economia de energia da placa de rede
powercfg /setacvalueindex SCHEME_CURRENT SUB_NONE CONSOLELOCK 0

# Otimizar buffer de rede
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=enabled
netsh int tcp set global dca=enabled
netsh int tcp set global netdma=enabled

# Reduzir latência
netsh int tcp set supplemental Internet congestionprovider=ctcp
```

---

## Integrando o Dashboard com Múltiplas Partidas

Se você quiser rodar múltiplos servidores/partidas simultaneamente e monitorar todos no dashboard:

### Arquitetura Recomendada

```
┌─────────────────────────────────────────┐
│     Computador Central (Dashboard)      │
│  - Dashboard Web (porta 3000)           │
│  - Servidor GSI (porta 3001)            │
└─────────────────────────────────────────┘
                    ▲
                    │ Dados GSI
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐    ┌────▼───┐    ┌─────▼──┐
│ Sala 1 │    │ Sala 2 │    │ Sala 3 │
│ CS2    │    │ CS2    │    │ CS2    │
└────────┘    └────────┘    └────────┘
```

### Configuração

1. **No computador central:**
  - Rode o dashboard normalmente
  - Anote o IP (ex: 192.168.1.100)

1. **Em cada sala/computador host:**
  - Configure o arquivo GSI com o IP do dashboard:

1. **Limitação Atual:**
  - O dashboard atual mostra apenas UMA partida ativa por vez
  - A última partida que enviar dados será exibida
  - Para múltiplas partidas simultâneas, seria necessário modificar o código

### Modificação para Múltiplas Partidas (Avançado)

Se você quiser exibir múltiplas partidas, precisaria:

1. Modificar o banco de dados para identificar partidas por sala/computador

1. Adicionar um campo `room_id` ou `computer_id` no GSI

1. Criar uma interface no dashboard para selecionar qual partida visualizar

1. Ou criar um dashboard com múltiplas visualizações simultâneas

**Isso requer conhecimento de programação.** Se precisar dessa funcionalidade, posso ajudar a implementar.

---

## Criando um Pacote de Configuração para Lan House

Para facilitar a configuração de todos os computadores, crie um pacote padronizado:

### 1. Crie uma Pasta de Configuração

```
LanHouse_CS2_Config/
├── gamestate_integration_lanhouse.cfg
├── server.cfg
├── competitive.cfg
├── casual.cfg
├── autoexec.cfg
└── README.txt
```

### 2. Arquivo `autoexec.cfg` (Para Jogadores)

Crie um arquivo que será executado automaticamente quando o CS2 iniciar:

```
// Configurações de rede
rate 786432
cl_updaterate 128
cl_cmdrate 128
cl_interp 0
cl_interp_ratio 1

// Configurações de áudio
snd_mixahead 0.05
snd_headphone_pan_exponent 2

// Configurações de vídeo para performance
fps_max 300
mat_queue_mode 2

// HUD
cl_hud_radar_scale 1.0
cl_radar_scale 0.5

// Crosshair personalizada (exemplo)
cl_crosshairsize 2
cl_crosshairthickness 1
cl_crosshairstyle 4
cl_crosshaircolor 1

// Console
con_enable 1
```

### 3. Arquivo `competitive.cfg` (Para Servidor)

```
// Modo Competitivo 5v5
game_alias competitive

// Rounds
mp_maxrounds 30
mp_overtime_enable 1
mp_overtime_maxrounds 6
mp_overtime_startmoney 10000

// Tempo
mp_roundtime 1.92
mp_roundtime_defuse 1.92
mp_freezetime 15
mp_buytime 20

// Dinheiro
mp_startmoney 800
mp_maxmoney 16000

// Regras
mp_friendlyfire 1
mp_autokick 0
mp_autoteambalance 0
mp_limitteams 0
mp_forcecamera 1

// Comunicação
sv_alltalk 0
sv_deadtalk 0
sv_talk_enemy_dead 0
sv_talk_enemy_living 0

// Votação
sv_vote_allow_spectators 0
mp_endmatch_votenextmap 1

// Warmup
mp_warmup_pausetimer 1
mp_warmuptime 60
```

### 4. Script de Instalação Automática (Windows)

Crie um arquivo `instalar_configs.bat`:

```
@echo off
echo ============================================
echo   Instalador de Configs CS2 - Lan House
echo ============================================
echo.

REM Detectar pasta do CS2
set "CS2_PATH=C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg"

if not exist "%CS2_PATH%" (
    echo ERRO: Pasta do CS2 nao encontrada!
    echo Por favor, edite o script com o caminho correto.
    pause
    exit
)

echo Copiando arquivos de configuracao...
copy /Y "gamestate_integration_lanhouse.cfg" "%CS2_PATH%\"
copy /Y "server.cfg" "%CS2_PATH%\"
copy /Y "competitive.cfg" "%CS2_PATH%\"
copy /Y "casual.cfg" "%CS2_PATH%\"
copy /Y "autoexec.cfg" "%CS2_PATH%\"

echo.
echo ============================================
echo   Instalacao concluida com sucesso!
echo ============================================
echo.
echo Arquivos instalados em:
echo %CS2_PATH%
echo.
pause
```

### 5. Distribuição

1. Copie a pasta `LanHouse_CS2_Config` para um pendrive

1. Em cada computador da lan house:
  - Copie a pasta
  - Execute `instalar_configs.bat` como Administrador
  - Pronto!

---

## Checklist Pré-Campeonato

Use este checklist antes de cada campeonato:

### 1 Semana Antes

- [ ] Atualizar CS2 em todos os computadores

- [ ] Testar conexão de rede entre todos os PCs

- [ ] Verificar cabos ethernet

- [ ] Atualizar o dashboard para última versão

- [ ] Fazer backup das configurações

### 1 Dia Antes

- [ ] Executar partida teste completa

- [ ] Verificar se o dashboard está recebendo dados

- [ ] Testar som em todos os computadores

- [ ] Verificar periféricos (mouse, teclado, headset)

- [ ] Preparar configurações de servidor para o modo do campeonato

### No Dia do Campeonato

- [ ] Ligar todos os computadores 30min antes

- [ ] Iniciar o dashboard

- [ ] Configurar monitor/TV para exibir o dashboard

- [ ] Testar conexão com uma partida rápida

- [ ] Preparar comandos úteis em um arquivo texto

- [ ] Ter backup de configurações em pendrive

### Durante o Campeonato

- [ ] Monitorar o dashboard constantemente

- [ ] Ter console aberto no servidor para comandos rápidos

- [ ] Anotar problemas para resolver depois

- [ ] Fazer screenshots das estatísticas finais

### Após o Campeonato

- [ ] Salvar demos das partidas importantes

- [ ] Fazer backup dos dados do dashboard

- [ ] Exportar estatísticas se necessário

- [ ] Documentar problemas encontrados

---

## Comandos de Emergência

Tenha estes comandos prontos para situações de emergência:

### Problemas com Jogadores

```
// Kickar jogador
kick "nome_do_jogador"

// Mover jogador para espectador
mp_spectators_restricted 0
mp_forcerespawn

// Trocar jogador de time
mp_switchteams

// Resetar score
mp_backup_restore_load_file backup_round0.txt
```

### Problemas com o Servidor

```
// Reiniciar round atual
mp_restartgame 1

// Pausar partida
pause

// Despausar
unpause

// Recarregar configurações
exec server.cfg
exec competitive.cfg

// Mudar de mapa
changelevel de_dust2
```

### Problemas de Rede

```
// Verificar status do servidor
status

// Ver latência dos jogadores
net_graph 1

// Forçar atualização de taxa
sv_maxrate 0
sv_minrate 196608
```

---

## Perguntas Frequentes (FAQ)

### P: Preciso de internet para rodar o servidor?

**R:** Não! Para LAN local, você não precisa de internet. Configure `sv_lan 1` e tudo funcionará offline. Porém, para o dashboard funcionar, o computador com o dashboard precisa estar na mesma rede.

### P: Quantos jogadores posso ter em um servidor?

**R:** O CS2 suporta oficialmente até 64 jogadores, mas para competitivo recomenda-se 10 jogadores (5v5). Para casual, até 20 jogadores (10v10) funciona bem.

### P: O dashboard funciona com partidas online?

**R:** Sim! Se você configurar o GSI em qualquer computador jogando CS2 (mesmo online), o dashboard receberá os dados. Basta que o computador consiga acessar o IP do dashboard na porta 3001.

### P: Posso usar mapas customizados?

**R:** Sim! Baixe mapas da Workshop e use o comando:

```
host_workshop_map <workshop_id>
```

### P: Como salvo demos das partidas?

**R:** As demos são salvas automaticamente em:

```
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\
```

Para reproduzir: `playdemo nome_do_arquivo`

### P: O que fazer se o dashboard não receber dados?

**R:** Verifique:

1. Servidor GSI está rodando? ([http://localhost:3001/health](http://localhost:3001/health))

1. Arquivo .cfg está na pasta correta?

1. IP no arquivo .cfg está correto?

1. Firewall está bloqueando a porta 3001?

1. Há uma partida ativa no CS2?

### P: Posso usar o dashboard em um tablet/celular?

**R:** Sim! Basta acessar `http://IP_DO_DASHBOARD:3000` no navegador do dispositivo móvel. O dashboard é responsivo e funciona em qualquer dispositivo.

---

## Recursos Adicionais

### Comunidades e Suporte

- **Reddit:** r/GlobalOffensive - Comunidade ativa de CS2

- **Discord:** Servidores de CS2 Brasil

- **Steam Community:** Fóruns oficiais do CS2

### Ferramentas Úteis

- **HLAE (Half-Life Advanced Effects):** Para gravação profissional de demos

- **CS2 Server Browser:** Para encontrar servidores públicos

- **Refrag:** Plataforma brasileira para campeonatos

### Mapas Recomendados para Competitivo

- **Active Duty Pool (Oficiais):**
  - de_dust2
  - de_inferno
  - de_mirage
  - de_nuke
  - de_ancient
  - de_anubis
  - de_vertigo

- **Mapas Clássicos:**
  - de_train
  - de_cache
  - de_cobblestone

---

## Suporte e Contato

Se você encontrar problemas ou tiver dúvidas sobre a configuração do servidor ou do dashboard, você pode:

1. Revisar este guia cuidadosamente

1. Verificar a documentação oficial da Valve

1. Consultar a comunidade CS2 Brasil

1. Testar em um ambiente controlado antes do campeonato

**Boa sorte com seus campeonatos! 🎮🏆**

