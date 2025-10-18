# 🎮 CS2 Demo Analyzer - LAN Party Edition

Sistema automático de análise de demos CS2 em tempo real, perfeito para eventos LAN!

## 🚀 Início Rápido

### 1. Iniciar o Sistema

```bash
./start_lan_party.sh
```

O script irá:
- ✅ Verificar e ativar o ambiente virtual
- ✅ Instalar dependências necessárias
- ✅ Criar pastas necessárias
- ✅ Iniciar o servidor web
- ✅ Ativar monitoramento automático
- ✅ Abrir o navegador (opcional)

### 2. Acessar o Dashboard

Abra seu navegador e acesse: **http://localhost:8000**

## 📋 Como Funciona

### Sistema de Monitoramento Automático

O sistema verifica a pasta `demos/` **a cada 30 segundos** em busca de novos arquivos `.dem`:

1. 🔍 **Detecta** novos arquivos
2. ⏳ **Aguarda** a conclusão da gravação
3. 🎯 **Analisa** automaticamente
4. 📊 **Exibe** no dashboard em formato de card

### Gravando Demos no CS2

#### Método 1: Configurar Diretório (Recomendado)

No console do CS2, configure o diretório de destino:

```
demo setdirectory "/home/vancim/cs2analyzer/demos"
```

Depois, em cada partida:

```
demo record nome_da_partida
```

A demo será salva automaticamente na pasta monitorada!

#### Método 2: Mover Manualmente

1. Grave a demo normalmente:
   ```
   demo record nome_da_partida
   demo stop
   ```

2. Mova o arquivo `.dem` para:
   ```
   /home/vancim/cs2analyzer/demos/
   ```

3. O sistema detectará em até 30 segundos!

## 🎯 Recursos

### Dashboard em Tempo Real

- 📱 **Auto-refresh** a cada 10 segundos
- 🎴 **Cards de partidas** com informações essenciais
- 🆕 **Indicador visual** para partidas novas (< 5 min)
- 📊 **Estatísticas instantâneas**: Kills, Rounds, MVP
- 🗺️ **Nome do mapa** da partida

### Informações de Cada Partida

Ao clicar em um card, você acessa:

- 📈 **Gráficos interativos** de performance
- 👥 **Estatísticas detalhadas** de cada jogador
- 🔫 **Kill heatmap** (posições no mapa)
- 🎯 **Análise por round**
- 💀 **K/D ratio, HS%, dano total**
- 🏆 **MVPs e melhores momentos**

## 🛠️ Configurações

### Alterar Intervalo de Verificação

Edite `web_app/main.py`:

```python
monitor = DemoMonitor(DEMOS_DIR, ANALYSIS_DIR, interval=30)  # segundos
```

### Pasta de Demos

Por padrão: `/home/vancim/cs2analyzer/demos/`

Para alterar, edite `start_lan_party.sh` ou `web_app/main.py`

## 📁 Estrutura de Arquivos

```
cs2analyzer/
├── demos/                      # Pasta monitorada (coloque .dem aqui)
├── demo_analysis/              # Análises geradas automaticamente
│   ├── processed_demos.json   # Rastreamento de demos processados
│   └── [nome_da_partida]/     # Dados de cada partida
│       ├── player_stats.csv
│       ├── kills.csv
│       ├── damage.csv
│       ├── rounds_detailed.csv
│       └── match_info.json
├── web_app/                    # Servidor web
│   ├── main.py                # Backend FastAPI
│   └── templates/
│       └── matches.html       # Dashboard com cards
├── monitor.py                  # Sistema de monitoramento
└── start_lan_party.sh         # Script de inicialização
```

## 🔧 Comandos Úteis

### Apenas Monitoramento (sem web)

```bash
python monitor.py
```

### Analisar Demo Específica

```bash
python analyzer.py demos/minha_partida.dem
```

### Modo de Desenvolvimento

```bash
cd web_app
uvicorn main:app --reload --port 8000
```

## 💡 Dicas para LAN Party

### 1. Configuração Inicial

Antes do evento, execute uma vez:

```bash
./start_lan_party.sh
```

Configure o CS2 de cada PC para salvar demos na pasta compartilhada.

### 2. Durante o Evento

- ✅ Deixe o dashboard aberto em uma TV/projetor
- ✅ Partidas aparecem automaticamente após terminar
- ✅ Jogadores podem acessar http://[IP-DO-SERVIDOR]:8000
- ✅ Auto-refresh mantém tudo atualizado

### 3. Compartilhamento em Rede

Para outros PCs acessarem:

```bash
# No script, altere de localhost para:
uvicorn main:app --host 0.0.0.0 --port 8000
```

Outros PCs acessam: `http://[IP-DO-HOST]:8000`

### 4. Verificar IP do Servidor

```bash
ip addr show | grep inet
# ou
hostname -I
```

## 🐛 Solução de Problemas

### Demo não está sendo detectada

1. ✅ Verifique se está na pasta correta: `demos/`
2. ✅ Aguarde até 30 segundos
3. ✅ Verifique se o arquivo terminou de ser escrito
4. ✅ Veja o terminal do servidor para mensagens

### Erro ao analisar demo

1. ✅ Demo pode estar corrompida
2. ✅ Verifique o tamanho do arquivo (> 0 bytes)
3. ✅ Tente analisar manualmente: `python analyzer.py demos/arquivo.dem`

### Dashboard não atualiza

1. ✅ Verifique se o monitor está rodando (indicador verde)
2. ✅ Abra o console do navegador (F12) para ver erros
3. ✅ Force refresh: Ctrl+Shift+R

### Servidor não inicia

1. ✅ Verifique se a porta 8000 está livre: `lsof -i :8000`
2. ✅ Ative o venv: `source venv/bin/activate`
3. ✅ Instale dependências: `pip install -r requirements.txt`

## 🎮 Exemplo de Fluxo Completo

```bash
# Terminal 1: Iniciar sistema
./start_lan_party.sh

# No CS2 (Console):
demo setdirectory "/home/vancim/cs2analyzer/demos"
demo record lan_partida_1

# [Jogar a partida]

# No CS2 (Console):
demo stop

# O sistema automaticamente:
# 1. Detecta o novo arquivo (em até 30s)
# 2. Analisa a partida
# 3. Exibe no dashboard
# 4. Jogadores podem visualizar clicando no card
```

## 🏆 Status do Monitor

Verifique em tempo real:
- **Indicador verde piscando**: Monitor ativo
- **Contador de partidas**: Total analisado
- **Última verificação**: Timestamp da última varredura

## 📊 API Endpoints

Para integração customizada:

```
GET  /api/matches          # Lista todas as partidas
GET  /api/monitor/status   # Status do monitor
GET  /api/analysis/{nome}  # Detalhes de uma partida
GET  /dashboard/{nome}     # Dashboard visual
```

## 🎯 Performance

- ⚡ Análise típica: 10-30 segundos
- 🔄 Verificação: A cada 30 segundos
- 📱 Auto-refresh dashboard: 10 segundos
- 💾 Armazenamento: ~1-5 MB por partida

## 🚀 Próximos Recursos

- [ ] Filtros por mapa/jogador
- [ ] Comparação entre partidas
- [ ] Estatísticas agregadas do evento
- [ ] Exportação de highlights
- [ ] Notificações push

## 📝 Notas

- O sistema mantém um registro de todas as demos processadas em `processed_demos.json`
- Demos são identificadas por hash MD5 (não processa duplicatas)
- Cada partida gera ~10 arquivos CSV com dados detalhados

---

**Desenvolvido para LAN Parties** 🎮  
**Análise profissional em tempo real** 💪  
**100% automatizado** 🤖

