# 📖 Manual do Usuário - CS2 Analyzer

## Índice
1. [Visão Geral](#visão-geral)
2. [Primeiros Passos](#primeiros-passos)
3. [Upload e Análise de Demos](#upload-e-análise-de-demos)
4. [Navegação na Dashboard](#navegação-na-dashboard)
5. [Gerenciamento de Times](#gerenciamento-de-times)
6. [Criação e Gerenciamento de Torneios](#criação-e-gerenciamento-de-torneios)
7. [Visualização de Estatísticas de Jogadores](#visualização-de-estatísticas-de-jogadores)
8. [Recursos Avançados](#recursos-avançados)
9. [FAQ - Perguntas Frequentes](#faq---perguntas-frequentes)

---

## Visão Geral

O **CS2 Analyzer** é uma plataforma completa para análise de demos do Counter-Strike 2, oferecendo:

✨ **Recursos Principais:**
- 📤 Upload de arquivos .dem (demos do CS2)
- 🔍 Análise automática de partidas
- 📊 Estatísticas detalhadas por jogador
- 🏆 Sistema de torneios com brackets
- 👥 Gerenciamento de times
- 📈 Visualização de dados em tempo real
- 🎮 Perfis profissionais de jogadores

**Público-alvo:**
- Organizadores de torneios LAN
- Equipes competitivas de CS2
- Analistas de e-sports
- Jogadores que desejam melhorar performance

---

## Primeiros Passos

### Acessando o Sistema

1. **Abra seu navegador** (Chrome, Firefox, Edge)
2. **Acesse a URL**: `http://seu-servidor:8000` ou seu domínio configurado
3. **Página inicial** será exibida automaticamente

### Interface Principal

A interface é dividida em 5 seções principais:

#### 🏠 **Sidebar Menu** (Esquerda)
```
┌─────────────────┐
│ CS2 Analyzer    │
├─────────────────┤
│ 🏠 Início       │
│ 🎮 Partidas     │
│ 👥 Players      │
│ 🏆 Torneios     │
└─────────────────┘
```

#### 📊 **Área de Conteúdo** (Centro)
- Dashboards interativos
- Tabelas de dados
- Gráficos e estatísticas

#### 🔍 **Filtros e Busca** (Topo)
- Barra de pesquisa
- Filtros por time, K/D, data, etc.

---

## Upload e Análise de Demos

### Passo 1: Obter Arquivo .dem

**Como baixar demos do CS2:**

1. Abra o CS2
2. Vá para **Watch > Your Matches**
3. Selecione a partida desejada
4. Clique em **Download**
5. O arquivo `.dem` será salvo em: `C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\replays\`

### Passo 2: Upload do Demo

#### Via Interface Web

1. **Acesse a página inicial** (`/`)
2. **Localize a seção "Upload de Demo"**
3. **Clique no botão "Choose File"** ou arraste o arquivo para a área de drop
4. **Aguarde o upload** (barra de progresso será exibida)
5. **Análise automática** começará imediatamente

#### Via API (Avançado)

```bash
curl -X POST http://seu-servidor:8000/upload \
  -F "demo_file=@/caminho/para/demo.dem"
```

### Passo 3: Acompanhar Análise

Após o upload, você será redirecionado para:

**📊 Monitor de Status** (`/monitor`)

Você verá:
```
┌──────────────────────────────────────────┐
│ Status da Análise                        │
├──────────────────────────────────────────┤
│ ⏳ Processando demo...                   │
│ ├─ Extraindo eventos (30%)               │
│ ├─ Calculando estatísticas (60%)         │
│ └─ Gerando relatórios (90%)              │
│                                           │
│ ⏱️ Tempo estimado: 2 minutos             │
└──────────────────────────────────────────┘
```

**Tempo médio:**
- Demos curtas (16 rounds): ~1-2 minutos
- Demos longas (30 rounds): ~3-5 minutos

### Passo 4: Visualizar Resultados

Quando a análise terminar:

1. **Automaticamente** será redirecionado para a Dashboard
2. Ou acesse **Partidas** no menu lateral
3. Clique na partida desejada

---

## Navegação na Dashboard

### Dashboard de Partida

Acesse: `/dashboard/{nome-da-demo}`

#### Seção 1: Informações Gerais

```
┌────────────────────────────────────────────────┐
│ 🗺️ Mapa: Dust2                                │
│ 📅 Data: 19/10/2025                            │
│ 🏆 Score: 16 - 14                              │
│ ⏱️ Rounds: 30 rounds                           │
└────────────────────────────────────────────────┘
```

#### Seção 2: Estatísticas de Times

**Time 1 vs Time 2:**
```
┌─────────────┬──────┬──────┬──────┬────────┐
│ Time        │ K    │ D    │ K/D  │ Rating │
├─────────────┼──────┼──────┼──────┼────────┤
│ G5 Esports  │ 320  │ 280  │ 1.14 │ 1.05   │
│ Cansados    │ 280  │ 320  │ 0.88 │ 0.95   │
└─────────────┴──────┴──────┴──────┴────────┘
```

#### Seção 3: Top Jogadores da Partida

Cards exibindo:
- 🎯 **K/D Ratio**
- ⭐ **Rating**
- 🔫 **Total de Kills**
- 💀 **Deaths**
- 🎯 **Headshot %**
- 📊 **Barra de Accuracy**

#### Seção 4: Tabela Detalhada de Jogadores

Colunas disponíveis:
- **Jogador**: Nome + Avatar
- **Time**: Nome do time
- **K**: Kills totais
- **D**: Deaths
- **A**: Assists
- **K/D**: Ratio
- **HS%**: Headshot percentage
- **ADR**: Average Damage per Round
- **Rating**: HLTV-style rating

**Funcionalidades:**
- ✅ Ordenação por coluna (clique no header)
- ✅ Filtro por time
- ✅ Busca por nome de jogador

#### Seção 5: Mapa de Calor (Heatmap)

Visualização de:
- 💀 Posições de morte
- 🎯 Locais de kill
- 🔫 Spray patterns
- 📍 Posicionamento de times

#### Seção 6: Economia

Gráfico mostrando:
- 💰 Economia de cada time por round
- 💸 Investimento em equipamento
- 🏆 Rounds ganhos/perdidos por economia

---

## Gerenciamento de Times

### Criar Novo Time

1. **Acesse**: Menu lateral > **Teams** ou `/teams`
2. **Clique**: Botão **"+ Criar Novo Time"**
3. **Preencha o formulário**:

```
┌─────────────────────────────────────────┐
│ Criar Novo Time                         │
├─────────────────────────────────────────┤
│ Nome do Time:                           │
│ [________________________]              │
│                                         │
│ Logo (URL ou upload):                   │
│ [________________________] [Browse...]  │
│                                         │
│ Jogadores:                              │
│ ┌─────────────────────────────────────┐ │
│ │ Nome       │ SteamID          │ [+] │ │
│ │ ferreira   │ 76561199175...   │ [-] │ │
│ │ renzo      │ 76561198320...   │ [-] │ │
│ │ vittim     │ 76561199263...   │ [-] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Cancelar]           [Criar Time] ✅    │
└─────────────────────────────────────────┘
```

4. **Adicione jogadores**:
   - Clique em **[+]** para adicionar linha
   - Digite **Nome** e **SteamID64**
   - Clique **[-]** para remover

5. **Upload da Logo**:
   - **Opção 1**: Cole URL de imagem pública
   - **Opção 2**: Clique em **Browse** e selecione arquivo local (PNG, JPG)

6. **Clique "Criar Time"**

### Editar Time Existente

1. **Acesse**: `/teams`
2. **Localize o time** na lista
3. **Clique no ícone ✏️ (Editar)**
4. **Modifique os campos** desejados
5. **Clique "Salvar Alterações"**

### Deletar Time

1. **Acesse**: `/teams`
2. **Clique no ícone 🗑️ (Deletar)**
3. **Confirme a ação** (não pode ser desfeita!)

### Visualizar Detalhes do Time

Clique no **card do time** para ver:
- 👥 **Lista completa de jogadores**
- 📊 **Estatísticas agregadas**
- 🏆 **Histórico de partidas**
- 🎯 **Performance geral**

---

## Criação e Gerenciamento de Torneios

### Criar Torneio

1. **Acesse**: Menu > **Torneios** > **"+ Criar Torneio"**
2. **Preencha o formulário**:

```
┌──────────────────────────────────────────────┐
│ Criar Novo Torneio                           │
├──────────────────────────────────────────────┤
│ Nome do Torneio:                             │
│ [_____________________________________]       │
│                                              │
│ Data Início:         Data Fim:               │
│ [19/10/2025] ▼      [20/10/2025] ▼          │
│                                              │
│ Formato:                                     │
│ (•) Best of 1  ( ) Best of 3  ( ) Best of 5  │
│                                              │
│ Prize Pool:                                  │
│ R$ [__________]                              │
│                                              │
│ Distribuição de Prêmios:                     │
│ 1º Lugar: R$ [______]                        │
│ 2º Lugar: R$ [______]                        │
│ 3º Lugar: R$ [______]                        │
│                                              │
│ Times Participantes:                         │
│ ☑ G5 Esports                                 │
│ ☑ Cansados                                   │
│ ☑ ArtGamerz                                  │
│ ☐ Big Juice                                  │
│ ☑ Xilimbrim e-Sports                         │
│                                              │
│ [Cancelar]      [Criar Torneio] ✅           │
└──────────────────────────────────────────────┘
```

3. **Selecione times**:
   - Marque checkbox dos times participantes
   - Mínimo: 2 times
   - Máximo: Ilimitado

4. **Clique "Criar Torneio"**

### Visualizar Torneio

Acesse: `/tournament/{slug-do-torneio}`

**Abas disponíveis:**

#### 🔍 **Visão Geral**
- **Banner do torneio** com informações principais
- **Times Participantes** (cards com hover para ver jogadores)
- **Premiação** (distribuição de prêmios)
- **Chaves do Torneio** (bracket)
  - Upper Bracket
  - Lower Bracket (se aplicável)
- **Pool de Mapas**
- **Partidas Recentes**

#### 🎮 **Partidas**
- Lista completa de todas as partidas
- Score, data, mapa
- Clique para ver dashboard

#### 📊 **Estatísticas**
- Top jogadores do torneio
- Rankings por K/D, ADR, Rating
- Filtros e ordenação

### Editar Torneio

1. **Acesse**: `/manage-tournaments`
2. **Localize o torneio**
3. **Clique em ✏️ (Editar)**
4. **Modifique campos**
5. **Salve alterações**

### Gerenciar Bracket

**Funcionalidades:**
- ✅ Visualização de Upper/Lower Bracket
- ✅ Indicação de próxima partida
- ✅ Resultados atualizados automaticamente
- ✅ Navegação para dashboard da partida

**Estados da partida:**
- 🟢 **Completa**: Winner destacado em ciano
- 🟡 **Pendente**: Times definidos, aguardando jogo
- ⚪ **TBD**: Aguardando definição de times

---

## Visualização de Estatísticas de Jogadores

### Página de Players

Acesse: `/players`

**Recursos:**

#### 1. **Busca e Filtros**
```
┌────────────────────────────────────────┐
│ 🔍 Buscar Jogadores                    │
│ [Search by name, team, SteamID... ]    │
│                                        │
│ Filtros:                               │
│ Time: [Todos os times ▼]               │
│ K/D:  [Qualquer K/D ▼]                 │
│ Sort: [K/D Ratio ▼]                    │
│                                        │
│ [✅ Aplicar] [🔄 Resetar]              │
└────────────────────────────────────────┘
```

#### 2. **Cards de Jogadores**

Cada card exibe:
- 🖼️ **Foto/Avatar** (full-width no topo)
- 🏅 **Ranking** (#1, #2, #3 com cores especiais)
- 👤 **Nome do jogador**
- 🏷️ **Time**
- 📊 **Estatísticas**:
  - K/D Ratio
  - Rating
  - Total Kills
  - Total Deaths
  - HS%
- 📈 **Barra de Headshot Accuracy**

#### 3. **Paginação**
- Exibe 12 jogadores por página
- Botão **"Carregar Mais"** para próxima página

### Perfil Individual do Jogador

Acesse: `/player/{steamid}` ou `/pro/{steamid}`

**Seções do perfil:**

#### 📊 **Estatísticas Gerais**
```
┌──────────────────────────────────────┐
│ 👤 Nome do Jogador                   │
│ 🏷️ Time                              │
├──────────────────────────────────────┤
│ Partidas Jogadas: 15                 │
│ Total Kills: 320                     │
│ Total Deaths: 280                    │
│ K/D Ratio: 1.14                      │
│ Headshot %: 45%                      │
│ Rating: 1.05                         │
└──────────────────────────────────────┘
```

#### 📋 **Histórico de Partidas**

Tabela com:
- 🗺️ **Mapa**
- 📅 **Data**
- 🏆 **Score**
- 🎯 **Kills**
- 💀 **Deaths**
- 📊 **K/D**
- 🔗 **Link para dashboard**

**Funcionalidades:**
- Ordenação por coluna
- Filtro por mapa
- Paginação

#### 📈 **Estatísticas por Lado (CT/T)**

Comparativo de performance:
- Como **Counter-Terrorist**
- Como **Terrorist**

Métricas:
- K/D Ratio
- Win Rate
- Average Kills/Round
- Headshot %

#### 🎯 **Mapas Favoritos**

Top 5 mapas com melhor performance:
- Nome do mapa
- Partidas jogadas
- Win rate
- K/D médio

---

## Recursos Avançados

### Download de Estatísticas (CSV)

**Por Partida:**
1. Acesse dashboard da partida
2. Clique em **"📥 Download CSV"**
3. Arquivo será baixado com:
   - Nome do jogador
   - Todas as estatísticas
   - Round-by-round data

**Formato do arquivo:**
```csv
player,team,kills,deaths,assists,hs_percent,adr,rating
ferreira,ORBITAL ROXA,25,18,5,52,85.3,1.15
renzo,ORBITAL ROXA,22,20,7,48,78.2,1.02
```

### Exportar Bracket do Torneio

1. Acesse página do torneio
2. Clique em **"Exportar Bracket"**
3. Escolha formato:
   - PNG (imagem)
   - PDF (documento)
   - JSON (dados brutos)

### Integração com API

**Endpoints disponíveis:**

```bash
# Listar todas as partidas
GET /api/matches

# Detalhes de uma partida
GET /api/analysis/{demo_name}

# Top jogadores
GET /api/top-players?limit=10

# Estatísticas de jogador
GET /api/player/{steamid}/stats

# Times
GET /api/teams

# Torneios
GET /api/tournaments
```

**Exemplo de uso:**
```python
import requests

# Buscar top 10 jogadores
response = requests.get('http://seu-servidor:8000/api/top-players?limit=10')
players = response.json()

for player in players:
    print(f"{player['name']}: K/D {player['kd_ratio']}")
```

### Temas e Personalização

**Cores personalizadas** (futuro):
- Temas escuros/claros
- Cores de time customizadas
- Layout personalizável

---

## FAQ - Perguntas Frequentes

### 1. **Que tipo de arquivo posso fazer upload?**
✅ Apenas arquivos `.dem` do Counter-Strike 2
❌ Não aceita demos do CS:GO

### 2. **Qual o tamanho máximo do arquivo?**
📦 **500 MB** por padrão
⚙️ Pode ser configurado pelo administrador

### 3. **Quanto tempo leva para analisar um demo?**
⏱️ **1-5 minutos** dependendo do tamanho
- 16 rounds: ~1-2 min
- 30 rounds: ~3-5 min

### 4. **Como obtenho meu SteamID64?**
1. Acesse https://steamid.io/
2. Cole seu perfil Steam
3. Copie o **steamID64**

Ou use: https://steamcommunity.com/my/

### 5. **Posso deletar uma partida?**
🔒 Apenas administradores podem deletar demos
📁 Arquivos ficam em `/demo_analysis/`

### 6. **Como adiciono logo do time?**
**Opção 1**: URL pública da imagem
**Opção 2**: Upload local (PNG/JPG)
📏 Tamanho recomendado: 200x200px

### 7. **O que é Rating?**
⭐ **Rating** é uma métrica estilo HLTV 2.0
📊 Leva em conta: K/D, impacto, sobrevivência, ADR
🎯 1.00 = média, >1.20 = excelente, <0.80 = abaixo da média

### 8. **Como funciona o sistema de bracket?**
🏆 **Double Elimination** (padrão)
- Upper Bracket: Times vencedores
- Lower Bracket: Times que perderam uma vez
- Grand Final: Winner UB vs Winner LB

### 9. **Posso comparar dois jogadores?**
📊 Ainda não disponível nativamente
💡 Workaround: Abra dois perfis em abas separadas

### 10. **Como reportar um bug?**
🐛 Entre em contato com o administrador
📧 Ou abra issue no repositório do projeto

### 11. **O sistema funciona offline?**
✅ Sim, desde que esteja na mesma rede local
🌐 Não precisa de internet após instalação

### 12. **Posso usar em campeonatos oficiais?**
✅ Sim! Foi feito especialmente para LAN parties
🏆 Usado em torneios competitivos

### 13. **Como adiciono foto do jogador?**
📸 Ao criar/editar time, cole URL da foto
🖼️ Formatos: JPG, PNG, WEBP
📏 Recomendado: 200x200px ou maior

### 14. **O que significa cada estatística?**

| Sigla | Nome | Descrição |
|-------|------|-----------|
| **K** | Kills | Total de eliminações |
| **D** | Deaths | Total de mortes |
| **A** | Assists | Assistências em kills |
| **K/D** | Kill/Death Ratio | Kills dividido por Deaths |
| **HS%** | Headshot % | % de kills com headshot |
| **ADR** | Average Damage per Round | Dano médio por round |
| **Rating** | Rating 2.0 | Métrica geral de performance |

### 15. **Posso exportar dados para Excel?**
✅ Sim! Clique em **"Download CSV"**
📊 Abra no Excel, Google Sheets, etc.

---

## Dicas e Boas Práticas

### 🎯 **Para Organizadores de Torneios**
1. ✅ Crie todos os times **antes** do torneio
2. ✅ Teste upload de demos com antecedência
3. ✅ Prepare logos dos times (200x200px)
4. ✅ Configure prize pool antes de iniciar
5. ✅ Monitore espaço em disco (demos ocupam ~300MB cada)

### 📊 **Para Análise de Jogadores**
1. ✅ Compare K/D Ratio entre mapas diferentes
2. ✅ Verifique HS% para avaliar precisão
3. ✅ Analise ADR para impacto econômico
4. ✅ Use Rating como métrica geral
5. ✅ Compare CT vs T para entender estilo de jogo

### 🏆 **Para Times Competitivos**
1. ✅ Revise demos após cada partida
2. ✅ Identifique padrões de morte (heatmap)
3. ✅ Analise economia round-by-round
4. ✅ Compare performance entre jogadores
5. ✅ Use CSV para análises mais profundas

### 🔧 **Manutenção**
1. ✅ Faça backup semanal (`teams.json`, `tournaments.json`)
2. ✅ Delete demos antigas (>30 dias)
3. ✅ Monitore uso de espaço em disco
4. ✅ Verifique logs em caso de erros

---

## Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl + K` | Abrir busca rápida |
| `Esc` | Fechar modal/popup |
| `Tab` | Navegar entre campos de formulário |
| `Enter` | Submeter formulário |
| `Ctrl + R` | Recarregar página |

---

## Glossário de Termos

**ADR** - Average Damage per Round - Dano médio por round
**Bracket** - Chave de eliminação em torneios
**Demo** - Arquivo de replay de partida (.dem)
**HS%** - Headshot Percentage - Porcentagem de headshots
**K/D** - Kill/Death Ratio - Razão entre kills e deaths
**LAN** - Local Area Network - Rede local
**MVP** - Most Valuable Player - Jogador mais valioso
**Rating** - Métrica de performance geral
**SteamID** - Identificador único do Steam
**TBD** - To Be Determined - A ser definido
**Upper/Lower Bracket** - Chave superior/inferior em double elimination

---

## Suporte e Contato

**Problemas técnicos:**
- 📧 Email: suporte@cs2analyzer.com
- 💬 Discord: [Link do servidor]
- 🐛 Issues: [GitHub repository]

**Sugestões de melhorias:**
- 💡 Abra uma issue no GitHub
- 📝 Entre em contato via email

---

**Última atualização:** 2025-10-18
**Versão do manual:** 1.0.0
**Desenvolvido com ❤️ para a comunidade CS2**
