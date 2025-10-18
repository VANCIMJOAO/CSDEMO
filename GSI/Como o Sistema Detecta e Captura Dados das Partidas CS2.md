# Como o Sistema Detecta e Captura Dados das Partidas CS2

**Autor:** Manus AI  
**Data:** 18 de outubro de 2025

## Visão Geral do Fluxo de Dados

O sistema funciona de forma completamente automática. Aqui está o fluxo completo:

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTADOR COM CS2                        │
│                                                              │
│  ┌──────────────┐                                           │
│  │   CS2 Game   │  1. Jogo detecta mudanças no estado      │
│  │   Engine     │     (round começa, jogador mata, etc)    │
│  └──────┬───────┘                                           │
│         │                                                    │
│         │ 2. Envia dados JSON via HTTP POST                │
│         ▼                                                    │
│  ┌──────────────────────────────────────┐                  │
│  │  gamestate_integration_lanhouse.cfg  │                  │
│  │  - Define ONDE enviar (URI)          │                  │
│  │  - Define O QUE enviar (data)        │                  │
│  │  - Define QUANDO enviar (throttle)   │                  │
│  └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ HTTP POST com JSON
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              SERVIDOR DO DASHBOARD (porta 3001)              │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  gsi-server.ts (Servidor Express)                │      │
│  │                                                   │      │
│  │  3. Recebe o payload JSON                        │      │
│  │  4. Valida o token de autenticação               │      │
│  │  5. Processa os dados                            │      │
│  └────────────────┬─────────────────────────────────┘      │
│                   │                                          │
│                   ▼                                          │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Lógica de Detecção de Partida                   │      │
│  │                                                   │      │
│  │  - Se map.phase === "live" E não há partida ativa│      │
│  │    → Cria nova partida no banco                  │      │
│  │                                                   │      │
│  │  - Se map.phase === "gameover"                   │      │
│  │    → Marca partida como finalizada               │      │
│  └────────────────┬─────────────────────────────────┘      │
│                   │                                          │
│                   ▼                                          │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Banco de Dados (MySQL/TiDB)                     │      │
│  │  - Tabela: matches                               │      │
│  │  - Tabela: playerStats                           │      │
│  │  - Tabela: roundHistory                          │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ API tRPC
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Dashboard React)                      │
│                                                              │
│  6. Busca dados a cada 2 segundos via tRPC                  │
│  7. Atualiza interface em tempo real                        │
│  8. Exibe placar, estatísticas, rounds                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Como o CS2 Envia os Dados (Game State Integration)

### O Arquivo de Configuração GSI

O arquivo `gamestate_integration_lanhouse.cfg` é lido pelo CS2 quando o jogo inicia. Vamos entender cada parte:

```
"CS2 Lan House Integration v.1"
{
 "uri" "http://127.0.0.1:3001"      // ONDE enviar os dados
 "timeout" "5.0"                     // Timeout da conexão HTTP
 "buffer"  "0.1"                     // Aguardar 0.1s antes de enviar
 "throttle" "0.1"                    // Enviar no máximo a cada 0.1s
 "heartbeat" "15.0"                  // Enviar heartbeat a cada 15s
 
 "auth"
 {
   "token" "SenhaSuperSecretaParaSuaLanHouse"  // Token de segurança
 }
 
 "data"
 {
   "provider"                  "1"   // Informações do servidor/cliente
   "map"                       "1"   // Dados do mapa e placar
   "round"                     "1"   // Dados do round atual
   "player_id"                 "1"   // ID do jogador local
   "allplayers_id"             "1"   // IDs de todos os jogadores
   "allplayers_state"          "1"   // Estado (vida, colete, etc)
   "allplayers_match_stats"    "1"   // Estatísticas (K/D/A)
   "allplayers_weapons"        "1"   // Armas dos jogadores
   "allplayers_position"       "1"   // Posições no mapa
   "phase_countdowns"          "1"   // Contadores de tempo
   "allgrenades"               "1"   // Granadas no mapa
 }
}
```

### Quando o CS2 Envia Dados?

O CS2 envia dados automaticamente quando **qualquer coisa muda** no jogo:

- ✅ Partida começa (warmup → live)
- ✅ Round começa
- ✅ Jogador mata outro jogador
- ✅ Jogador morre
- ✅ Jogador compra arma
- ✅ Jogador troca de arma
- ✅ Vida ou colete muda
- ✅ Bomba é plantada/defusada
- ✅ Round termina
- ✅ Placar muda
- ✅ A cada 15 segundos (heartbeat), mesmo sem mudanças

### Exemplo de Payload JSON Enviado

Quando algo acontece no jogo, o CS2 envia um POST HTTP com JSON assim:

```json
{
  "auth": {
    "token": "SenhaSuperSecretaParaSuaLanHouse"
  },
  "provider": {
    "name": "Counter-Strike: Global Offensive",
    "appid": 730,
    "version": 13960,
    "steamid": "76561198012345678",
    "timestamp": 1729234567
  },
  "map": {
    "mode": "competitive",
    "name": "de_dust2",
    "phase": "live",
    "round": 5,
    "team_ct": {
      "score": 3
    },
    "team_t": {
      "score": 2
    }
  },
  "round": {
    "phase": "live",
    "bomb": "planted",
    "win_team": null
  },
  "allplayers": {
    "76561198012345678": {
      "name": "Player1",
      "team": "CT",
      "state": {
        "health": 100,
        "armor": 100,
        "money": 3500
      },
      "match_stats": {
        "kills": 12,
        "assists": 3,
        "deaths": 5,
        "mvps": 2,
        "score": 35
      },
      "weapons": {
        "weapon_0": {
          "name": "weapon_ak47",
          "state": "active"
        }
      }
    }
  }
}
```

---

## 2. Como o Servidor Detecta o Início da Partida

Vamos analisar o código do `gsi-server.ts`:

### Detecção Automática de Nova Partida

```typescript
let currentMatchId: string | null = null;
let lastRoundNumber = 0;

async function processGSIPayload(payload: GSIPayload) {
  // 1. VALIDAR TOKEN
  if (payload.auth?.token !== AUTH_TOKEN) {
    console.warn("[GSI] Invalid auth token received");
    return;  // Ignora dados não autorizados
  }

  const mapData = payload.map;
  
  // 2. DETECTAR INÍCIO DE NOVA PARTIDA
  if (!currentMatchId && mapData?.phase === "live") {
    currentMatchId = generateId();  // Gera ID único
    lastRoundNumber = 0;
    console.log(`[GSI] New match started: ${currentMatchId}`);
  }
  
  // Se não há partida ativa, não faz nada
  if (!currentMatchId) {
    return;
  }
  
  // 3. ATUALIZAR DADOS DA PARTIDA
  await upsertMatch({
    id: currentMatchId,
    mapName: mapData.name || "unknown",
    teamCtScore: String(mapData.team_ct?.score || 0),
    teamTScore: String(mapData.team_t?.score || 0),
    // ... outros dados
  });
  
  // 4. DETECTAR FIM DA PARTIDA
  if (mapData?.phase === "gameover") {
    console.log(`[GSI] Match ${currentMatchId} ended`);
    currentMatchId = null;  // Reseta para próxima partida
  }
}
```

### Estados da Partida (map.phase)

O CS2 informa o estado da partida através do campo `map.phase`:

| Fase | Significado | O que o sistema faz |
|------|-------------|---------------------|
| `warmup` | Aquecimento antes da partida | Aguarda, não cria partida ainda |
| `live` | Partida em andamento | **Cria nova partida** se não existir |
| `intermission` | Entre rounds | Continua atualizando dados |
| `gameover` | Partida finalizada | **Marca partida como encerrada** |

### Detecção de Fim de Round

```typescript
// Detectar quando um round termina
if (roundData && mapData) {
  const currentRoundNum = mapData.round || 0;
  const currentRoundPhase = roundData.phase || "";
  
  // Se o round acabou de terminar E tem vencedor
  if (
    currentRoundPhase === "over" &&
    lastRoundPhase !== "over" &&
    roundData.win_team &&
    currentRoundNum > lastRoundNumber
  ) {
    // Salvar no histórico
    await addRoundHistory({
      matchId: currentMatchId,
      roundNumber: String(currentRoundNum),
      winner: roundData.win_team,  // "CT" ou "T"
      reason: roundData.bomb || "eliminated",
      ctScore: String(mapData.team_ct?.score || 0),
      tScore: String(mapData.team_t?.score || 0),
    });
    
    lastRoundNumber = currentRoundNum;
  }
  
  lastRoundPhase = currentRoundPhase;
}
```

---

## 3. Frequência de Atualização

### Configuração no arquivo .cfg

```
"buffer"  "0.1"      // Espera 100ms antes de enviar
"throttle" "0.1"     // Envia no máximo a cada 100ms (10x por segundo)
"heartbeat" "15.0"   // Envia heartbeat a cada 15s mesmo sem mudanças
```

### O que isso significa?

- **Buffer (0.1s):** Quando algo muda no jogo, o CS2 espera 100ms para ver se mais coisas mudam, depois envia tudo junto
- **Throttle (0.1s):** Mesmo que muitas coisas mudem rapidamente, só envia no máximo 10 vezes por segundo
- **Heartbeat (15s):** Mesmo que nada mude, envia um "ping" a cada 15 segundos para confirmar que está vivo

### No Frontend (Dashboard)

```typescript
// Busca dados a cada 2 segundos
const { data: activeMatch } = trpc.match.getActive.useQuery(undefined, {
  refetchInterval: 2000,  // 2000ms = 2 segundos
});
```

**Por que 2 segundos e não 0.1s?**
- Evita sobrecarga do banco de dados
- Evita renderizações excessivas no React
- 2 segundos é suficientemente rápido para parecer "tempo real"
- Economiza recursos do servidor

---

## 4. Fluxo Completo: Do Jogo ao Dashboard

### Cenário: Jogador mata outro jogador

**Tempo 0ms:**
```
CS2 detecta: Player1 matou Player2 com AK-47
```

**Tempo 100ms (buffer):**
```
CS2 prepara payload JSON com:
- Player1: kills = 13 (era 12)
- Player2: deaths = 6 (era 5)
- Player2: health = 0 (estava 100)
```

**Tempo 100ms:**
```
CS2 envia HTTP POST para http://127.0.0.1:3001
```

**Tempo 105ms:**
```
Servidor GSI recebe o payload
Valida o token
Processa os dados
```

**Tempo 110ms:**
```
Atualiza banco de dados:
- playerStats: Player1 kills = 13
- playerStats: Player2 deaths = 6, health = 0
```

**Tempo 2000ms (próximo intervalo):**
```
Frontend faz query tRPC
Busca dados atualizados do banco
Atualiza interface React
```

**Tempo 2050ms:**
```
Usuário vê no dashboard:
- Player1 agora tem 13 kills
- Player2 agora tem 6 deaths e está marcado como morto
```

---

## 5. Testando o Sistema

### Verificar se o GSI está funcionando

**1. Verificar se o servidor está rodando:**
```bash
# No navegador ou curl
http://localhost:3001/health

# Resposta esperada:
{"status":"ok","currentMatch":null}
```

**2. Verificar logs do servidor:**
```
[GSI] Server listening on port 3001
[GSI] Waiting for CS2 game state data...
```

**3. Iniciar uma partida no CS2:**

Quando você carregar um mapa, deve ver:
```
[GSI] New match started: 1729234567890-abc123def
```

**4. Durante a partida:**

A cada mudança, você verá dados sendo processados (se ativar logs detalhados).

**5. Quando o round termina:**
```
[GSI] Round 1 ended. Winner: CT
```

**6. Quando a partida termina:**
```
[GSI] Match 1729234567890-abc123def ended
```

### Verificar se o Dashboard está recebendo dados

**1. Abra o dashboard:**
```
http://localhost:3000
```

**2. Sem partida ativa:**
```
Você verá: "Aguardando Partida"
```

**3. Com partida ativa:**
```
Você verá:
- Placar (CT vs T)
- Lista de jogadores
- Estatísticas em tempo real
```

**4. Verifique a atualização:**
```
Mate um bot no jogo
Aguarde até 2 segundos
O kill deve aparecer no dashboard
```

---

## 6. Troubleshooting: Sistema Não Detecta Partida

### Problema: Dashboard não mostra partida mesmo com jogo rodando

**Checklist de diagnóstico:**

**1. Verificar se o servidor GSI está rodando:**
```bash
curl http://localhost:3001/health
```
Se não responder → Servidor não está rodando

**2. Verificar se o arquivo .cfg está no lugar certo:**
```
Windows:
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\gamestate_integration_lanhouse.cfg
```

**3. Verificar se o CS2 está enviando dados:**

Adicione logs no servidor (temporariamente):
```typescript
app.post("/", async (req, res) => {
  console.log("[GSI] Received payload:", JSON.stringify(req.body, null, 2));
  // ...
});
```

Se não aparecer nada → CS2 não está enviando

**4. Verificar o token:**

No arquivo .cfg:
```
"token" "SenhaSuperSecretaParaSuaLanHouse"
```

No código (gsi-server.ts):
```typescript
const AUTH_TOKEN = "SenhaSuperSecretaParaSuaLanHouse";
```

Devem ser **exatamente iguais**!

**5. Verificar a fase da partida:**

O sistema só cria partida quando `map.phase === "live"`.

Durante warmup, não cria partida ainda.

**Solução:** Execute no console do CS2:
```
mp_warmup_end
```

**6. Verificar firewall:**

Temporariamente desative o firewall para testar.

Se funcionar → Crie regra para porta 3001.

---

## 7. Customizações Possíveis

### Mudar a frequência de atualização do frontend

Em `client/src/pages/Home.tsx`:

```typescript
// Atualizar a cada 1 segundo (mais rápido)
refetchInterval: 1000,

// Atualizar a cada 5 segundos (mais lento, economiza recursos)
refetchInterval: 5000,
```

### Mudar a frequência de envio do CS2

No arquivo `.cfg`:

```
// Enviar mais rápido (a cada 50ms)
"throttle" "0.05"

// Enviar mais devagar (a cada 500ms)
"throttle" "0.5"
```

**Atenção:** Valores muito baixos podem sobrecarregar o servidor!

### Adicionar logs detalhados

Em `gsi-server.ts`:

```typescript
async function processGSIPayload(payload: GSIPayload) {
  console.log("[GSI] Received payload from:", payload.provider?.steamid);
  console.log("[GSI] Map:", payload.map?.name, "Phase:", payload.map?.phase);
  console.log("[GSI] Score: CT", payload.map?.team_ct?.score, "vs T", payload.map?.team_t?.score);
  // ...
}
```

---

## 8. Resumo

### Como o sistema sabe que a partida começou?

1. **CS2 envia dados automaticamente** quando o arquivo `.cfg` está instalado
2. **Servidor verifica** se `map.phase === "live"`
3. **Se não há partida ativa** (`currentMatchId === null`) **E** fase é "live"
4. **Cria nova partida** com ID único
5. **Começa a armazenar** todos os dados no banco
6. **Frontend busca** dados a cada 2 segundos e exibe

### É automático?

**100% automático!** Você só precisa:
1. Instalar o arquivo `.cfg` no CS2
2. Rodar o dashboard
3. Iniciar uma partida no CS2

O resto acontece sozinho! 🎮✨

---

## Conclusão

O Game State Integration é um sistema elegante e poderoso. O CS2 faz todo o trabalho pesado de detectar mudanças e enviar dados. Nosso servidor apenas recebe, valida e armazena. O dashboard busca periodicamente e exibe.

Tudo funciona de forma completamente automática, sem necessidade de intervenção manual!

