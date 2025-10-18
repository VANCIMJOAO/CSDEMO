# Documentação Técnica Completa - Dashboard CS2 Tournament

**Projeto:** Sistema de Dashboard em Tempo Real para Campeonatos de Counter-Strike 2  
**Desenvolvido em:** 18 de outubro de 2025  
**Tecnologias:** Node.js, React, TypeScript, tRPC, MySQL/TiDB, Game State Integration (GSI)  
**Autor:** Manus AI

---

## Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura de Diretórios](#estrutura-de-diretórios)
4. [Fluxo de Dados Completo](#fluxo-de-dados-completo)
5. [Banco de Dados](#banco-de-dados)
6. [Backend - Servidor GSI](#backend-servidor-gsi)
7. [Backend - API tRPC](#backend-api-trpc)
8. [Frontend - Dashboard React](#frontend-dashboard-react)
9. [Game State Integration - Dados Disponíveis](#game-state-integration-dados-disponíveis)
10. [Configuração e Deploy](#configuração-e-deploy)
11. [Expansões Futuras](#expansões-futuras)
12. [Troubleshooting](#troubleshooting)

---

## Visão Geral do Projeto

### Objetivo

Criar um sistema web que captura e exibe dados de partidas de Counter-Strike 2 em tempo real para uso em campeonatos de lan houses, permitindo que espectadores acompanhem estatísticas detalhadas dos jogadores.

### Problema Resolvido

Lan houses que organizam campeonatos de CS2 precisam de uma forma de exibir dados das partidas em tempo real para espectadores, sem depender de soluções comerciais caras ou complexas.

### Solução Implementada

Um sistema completo que utiliza o Game State Integration (GSI) oficial da Valve para capturar dados do CS2 e exibi-los em um dashboard web moderno e responsivo.

### Características Principais

- ✅ **Detecção automática** de início e fim de partidas
- ✅ **Atualização em tempo real** (2 segundos de latência)
- ✅ **Estatísticas completas** de jogadores (K/D/A, vida, armas, dinheiro)
- ✅ **Histórico de rounds** com vencedores
- ✅ **Suporte a múltiplos computadores** enviando dados para um servidor central
- ✅ **Interface moderna** com tema escuro e design responsivo
- ✅ **Sem necessidade de modificações no jogo** (usa API oficial)

---

## Arquitetura do Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE JOGO (CS2)                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Counter-Strike 2 (Game Engine)                      │  │
│  │  - Detecta mudanças no estado do jogo                │  │
│  │  - Lê arquivo gamestate_integration_lanhouse.cfg     │  │
│  └────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          │ HTTP POST (JSON)
                          │ Porta: 3001
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE BACKEND                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Servidor GSI (Express.js)                           │  │
│  │  Arquivo: server/gsi-server.ts                       │  │
│  │  Porta: 3001                                         │  │
│  │                                                       │  │
│  │  Responsabilidades:                                  │  │
│  │  - Receber payloads JSON do CS2                     │  │
│  │  - Validar token de autenticação                    │  │
│  │  - Detectar início/fim de partidas                  │  │
│  │  - Processar dados de jogadores                     │  │
│  │  - Detectar fim de rounds                           │  │
│  │  - Persistir dados no banco                         │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Banco de Dados (MySQL/TiDB)                         │  │
│  │  Arquivo: drizzle/schema.ts                          │  │
│  │                                                       │  │
│  │  Tabelas:                                            │  │
│  │  - matches: Dados da partida                        │  │
│  │  - playerStats: Estatísticas dos jogadores          │  │
│  │  - roundHistory: Histórico de rounds                │  │
│  │  - users: Usuários do sistema (auth)                │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API tRPC                                            │  │
│  │  Arquivo: server/routers.ts                          │  │
│  │  Porta: 3000 (endpoint: /api/trpc)                  │  │
│  │                                                       │  │
│  │  Rotas:                                              │  │
│  │  - match.getActive: Busca partida ativa             │  │
│  │  - match.getPlayers: Busca jogadores da partida     │  │
│  │  - match.getRounds: Busca histórico de rounds       │  │
│  └────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          │ HTTP (tRPC)
                          │ Porta: 3000
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE FRONTEND                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dashboard React                                     │  │
│  │  Arquivo: client/src/pages/Home.tsx                  │  │
│  │  Porta: 3000                                         │  │
│  │                                                       │  │
│  │  Componentes:                                        │  │
│  │  - Placar (CT vs T)                                  │  │
│  │  - Tabelas de jogadores por time                    │  │
│  │  - Estatísticas individuais (K/D/A, vida, arma)     │  │
│  │  - Histórico de rounds                               │  │
│  │  - Estado da bomba                                   │  │
│  │                                                       │  │
│  │  Atualização:                                        │  │
│  │  - useQuery com refetchInterval: 2000ms              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

**Backend:**
- **Node.js** 22.13.0
- **Express.js** 4.x - Servidor HTTP
- **tRPC** 11.x - Type-safe API
- **Drizzle ORM** - Database ORM
- **TypeScript** - Linguagem
- **Zod** - Validação de schemas

**Frontend:**
- **React** 19.x
- **TypeScript**
- **Tailwind CSS** 4.x - Estilização
- **shadcn/ui** - Componentes UI
- **Wouter** - Roteamento
- **tRPC Client** - Comunicação com backend

**Banco de Dados:**
- **MySQL** / **TiDB** (compatível com MySQL)

**Infraestrutura:**
- **Vite** - Build tool e dev server
- **pnpm** - Package manager

---

## Estrutura de Diretórios

```
cs2-tournament-dashboard/
├── client/                          # Frontend React
│   ├── public/                      # Arquivos estáticos
│   └── src/
│       ├── components/              # Componentes reutilizáveis
│       │   └── ui/                  # Componentes shadcn/ui
│       ├── contexts/                # React contexts
│       ├── hooks/                   # Custom hooks
│       ├── lib/
│       │   └── trpc.ts             # Cliente tRPC
│       ├── pages/
│       │   ├── Home.tsx            # Dashboard principal
│       │   ├── Instructions.tsx     # Página de instruções
│       │   └── NotFound.tsx        # Página 404
│       ├── App.tsx                 # Configuração de rotas
│       ├── main.tsx                # Entry point
│       └── index.css               # Estilos globais
│
├── server/                          # Backend Node.js
│   ├── _core/                       # Código do framework
│   │   ├── context.ts              # Contexto tRPC
│   │   ├── cookies.ts              # Gerenciamento de cookies
│   │   ├── env.ts                  # Variáveis de ambiente
│   │   ├── index.ts                # Entry point do servidor
│   │   ├── oauth.ts                # Autenticação OAuth
│   │   ├── trpc.ts                 # Configuração tRPC
│   │   └── vite.ts                 # Integração Vite
│   ├── db.ts                       # Funções de banco de dados
│   ├── gsi-server.ts               # Servidor GSI (PORTA 3001)
│   ├── routers.ts                  # Rotas tRPC
│   └── storage.ts                  # Helpers S3
│
├── drizzle/                         # Schema do banco
│   └── schema.ts                   # Definição das tabelas
│
├── shared/                          # Código compartilhado
│   └── const.ts                    # Constantes
│
├── gamestate_integration_lanhouse.cfg  # Arquivo GSI para CS2
├── package.json                    # Dependências
├── tsconfig.json                   # Configuração TypeScript
└── vite.config.ts                  # Configuração Vite
```

### Arquivos Principais

| Arquivo | Descrição | Responsabilidade |
|---------|-----------|------------------|
| `server/gsi-server.ts` | Servidor GSI | Recebe dados do CS2, processa e salva no banco |
| `server/routers.ts` | API tRPC | Define endpoints para o frontend |
| `server/db.ts` | Database helpers | Funções para manipular dados no banco |
| `drizzle/schema.ts` | Schema do banco | Define estrutura das tabelas |
| `client/src/pages/Home.tsx` | Dashboard | Interface principal do usuário |
| `gamestate_integration_lanhouse.cfg` | Config GSI | Configuração para CS2 enviar dados |

---

## Fluxo de Dados Completo

### 1. Inicialização

```
Usuário inicia CS2
  ↓
CS2 carrega gamestate_integration_lanhouse.cfg
  ↓
GSI ativado no CS2
  ↓
CS2 aguarda mudanças no estado do jogo
```

### 2. Início da Partida

```
Jogador carrega mapa (ex: de_dust2)
  ↓
CS2 detecta: map.phase = "warmup"
  ↓
CS2 envia POST para http://localhost:3001
  ↓
Servidor GSI recebe payload
  ↓
Valida token de autenticação
  ↓
Verifica: phase != "live", não cria partida ainda
  ↓
Retorna 200 OK para CS2
```

```
Jogador executa: mp_warmup_end
  ↓
CS2 detecta: map.phase = "live"
  ↓
CS2 envia POST com phase = "live"
  ↓
Servidor GSI detecta: !currentMatchId && phase === "live"
  ↓
Cria novo matchId único: "1729234567890-abc123"
  ↓
INSERT INTO matches (id, mapName, phase, teamCtScore, teamTScore, ...)
  ↓
currentMatchId = "1729234567890-abc123"
  ↓
Retorna 200 OK
```

### 3. Durante a Partida (Atualização Contínua)

```
Jogador mata outro jogador
  ↓
CS2 detecta mudança no estado
  ↓
Aguarda 100ms (buffer)
  ↓
CS2 envia POST com dados atualizados
  ↓
Servidor GSI processa payload
  ↓
UPDATE playerStats SET kills = kills + 1 WHERE id = 'match-steamid'
  ↓
Retorna 200 OK
```

**Frequência de envio do CS2:**
- A cada mudança no jogo (com throttle de 100ms)
- Heartbeat a cada 15 segundos (mesmo sem mudanças)

### 4. Fim de Round

```
Round termina (CT ou T vence)
  ↓
CS2 detecta: round.phase = "over"
  ↓
CS2 envia POST com round.win_team = "CT" ou "T"
  ↓
Servidor GSI detecta mudança de fase
  ↓
Verifica: currentRoundPhase === "over" && lastRoundPhase !== "over"
  ↓
INSERT INTO roundHistory (matchId, roundNumber, winner, reason, ...)
  ↓
UPDATE matches SET teamCtScore = X, teamTScore = Y
  ↓
lastRoundNumber = currentRoundNumber
  ↓
Retorna 200 OK
```

### 5. Fim da Partida

```
Um time atinge 13 rounds (ou vence no overtime)
  ↓
CS2 detecta: map.phase = "gameover"
  ↓
CS2 envia POST com phase = "gameover"
  ↓
Servidor GSI detecta fim
  ↓
UPDATE matches SET phase = 'gameover'
  ↓
currentMatchId = null (reseta para próxima partida)
  ↓
Retorna 200 OK
```

### 6. Frontend (Dashboard)

```
Usuário abre http://localhost:3000
  ↓
React renderiza componente Home
  ↓
useQuery: trpc.match.getActive() com refetchInterval: 2000ms
  ↓
A cada 2 segundos:
  ↓
  Frontend faz request para /api/trpc/match.getActive
  ↓
  Backend executa query: SELECT * FROM matches WHERE phase = 'live'
  ↓
  Retorna dados da partida ativa (ou null)
  ↓
  Frontend atualiza estado React
  ↓
  Re-renderiza interface com novos dados
```

---

## Banco de Dados

### Schema Completo

#### Tabela: `users`

```typescript
export const users = mysqlTable("users", {
  id: varchar("id", { length: 64 }).primaryKey(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow(),
});
```

**Uso:** Sistema de autenticação (não usado para dados de partida)

#### Tabela: `matches`

```typescript
export const matches = mysqlTable("matches", {
  id: varchar("id", { length: 128 }).primaryKey(),
  mapName: varchar("mapName", { length: 64 }),
  gameMode: varchar("gameMode", { length: 32 }),
  phase: varchar("phase", { length: 32 }),
  teamCtScore: varchar("teamCtScore", { length: 10 }),
  teamTScore: varchar("teamTScore", { length: 10 }),
  currentRound: varchar("currentRound", { length: 10 }),
  roundPhase: varchar("roundPhase", { length: 32 }),
  bombState: varchar("bombState", { length: 32 }),
  roundWinner: varchar("roundWinner", { length: 16 }),
  lastUpdate: timestamp("lastUpdate").defaultNow(),
});
```

**Campos:**
- `id`: ID único da partida (gerado: `${timestamp}-${random}`)
- `mapName`: Nome do mapa (ex: "de_dust2")
- `gameMode`: Modo de jogo (ex: "competitive")
- `phase`: Fase da partida ("warmup", "live", "gameover")
- `teamCtScore`: Placar do time CT (string)
- `teamTScore`: Placar do time T (string)
- `currentRound`: Número do round atual
- `roundPhase`: Fase do round ("live", "over", "freezetime")
- `bombState`: Estado da bomba ("planted", "defused", "exploded", "none")
- `roundWinner`: Vencedor do último round ("CT" ou "T")
- `lastUpdate`: Timestamp da última atualização

#### Tabela: `playerStats`

```typescript
export const playerStats = mysqlTable("playerStats", {
  id: varchar("id", { length: 256 }).primaryKey(),
  matchId: varchar("matchId", { length: 128 }),
  steamId: varchar("steamId", { length: 64 }),
  name: varchar("name", { length: 128 }),
  team: varchar("team", { length: 16 }),
  health: varchar("health", { length: 10 }),
  armor: varchar("armor", { length: 10 }),
  kills: varchar("kills", { length: 10 }),
  assists: varchar("assists", { length: 10 }),
  deaths: varchar("deaths", { length: 10 }),
  mvps: varchar("mvps", { length: 10 }),
  score: varchar("score", { length: 10 }),
  money: varchar("money", { length: 10 }),
  currentWeapon: varchar("currentWeapon", { length: 64 }),
  lastUpdate: timestamp("lastUpdate").defaultNow(),
});
```

**Campos:**
- `id`: Chave composta `${matchId}-${steamId}`
- `matchId`: Referência à partida
- `steamId`: Steam ID do jogador
- `name`: Nome do jogador
- `team`: Time ("CT" ou "T")
- `health`: Vida atual (0-100)
- `armor`: Colete atual (0-100)
- `kills`: Total de kills
- `assists`: Total de assistências
- `deaths`: Total de mortes
- `mvps`: Total de MVPs
- `score`: Pontuação total
- `money`: Dinheiro atual
- `currentWeapon`: Arma ativa (ex: "weapon_ak47")
- `lastUpdate`: Timestamp da última atualização

#### Tabela: `roundHistory`

```typescript
export const roundHistory = mysqlTable("roundHistory", {
  id: varchar("id", { length: 128 }).primaryKey(),
  matchId: varchar("matchId", { length: 128 }),
  roundNumber: varchar("roundNumber", { length: 10 }),
  winner: varchar("winner", { length: 16 }),
  reason: varchar("reason", { length: 64 }),
  ctScore: varchar("ctScore", { length: 10 }),
  tScore: varchar("tScore", { length: 10 }),
  timestamp: timestamp("timestamp").defaultNow(),
});
```

**Campos:**
- `id`: ID único do registro
- `matchId`: Referência à partida
- `roundNumber`: Número do round
- `winner`: Time vencedor ("CT" ou "T")
- `reason`: Motivo da vitória ("planted", "defused", "eliminated")
- `ctScore`: Placar CT após este round
- `tScore`: Placar T após este round
- `timestamp`: Quando o round terminou

### Queries Principais

#### Buscar Partida Ativa

```typescript
export async function getActiveMatch() {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db
    .select()
    .from(matches)
    .where(eq(matches.phase, "live"))
    .limit(1);
  
  return result.length > 0 ? result[0] : undefined;
}
```

#### Buscar Jogadores de uma Partida

```typescript
export async function getMatchPlayers(matchId: string) {
  const db = await getDb();
  if (!db) return [];
  
  return await db
    .select()
    .from(playerStats)
    .where(eq(playerStats.matchId, matchId));
}
```

#### Buscar Histórico de Rounds

```typescript
export async function getMatchRounds(matchId: string) {
  const db = await getDb();
  if (!db) return [];
  
  return await db
    .select()
    .from(roundHistory)
    .where(eq(roundHistory.matchId, matchId))
    .orderBy(roundHistory.roundNumber);
}
```

---

## Backend - Servidor GSI

### Arquivo: `server/gsi-server.ts`

Este é o coração do sistema. Recebe dados do CS2 e processa.

### Configuração

```typescript
const GSI_PORT = 3001;
const AUTH_TOKEN = "SenhaSuperSecretaParaSuaLanHouse";
```

### Variáveis de Estado

```typescript
let currentMatchId: string | null = null;  // ID da partida ativa
let lastRoundNumber = 0;                    // Último round processado
let lastRoundPhase = "";                    // Última fase do round
```

### Interface do Payload GSI

```typescript
interface GSIPayload {
  auth?: {
    token?: string;
  };
  provider?: {
    name?: string;
    appid?: number;
    version?: number;
    steamid?: string;
    timestamp?: number;
  };
  map?: {
    mode?: string;
    name?: string;
    phase?: string;
    round?: number;
    team_ct?: {
      score?: number;
    };
    team_t?: {
      score?: number;
    };
  };
  round?: {
    phase?: string;
    bomb?: string;
    win_team?: string;
  };
  allplayers?: {
    [steamId: string]: {
      name?: string;
      team?: string;
      state?: {
        health?: number;
        armor?: number;
        money?: number;
      };
      match_stats?: {
        kills?: number;
        assists?: number;
        deaths?: number;
        mvps?: number;
        score?: number;
      };
      weapons?: {
        [weaponId: string]: {
          name?: string;
          state?: string;
        };
      };
    };
  };
}
```

### Função Principal: `processGSIPayload`

```typescript
async function processGSIPayload(payload: GSIPayload) {
  // 1. VALIDAR TOKEN
  if (payload.auth?.token !== AUTH_TOKEN) {
    console.warn("[GSI] Invalid auth token received");
    return;
  }

  const mapData = payload.map;
  const roundData = payload.round;
  const allPlayers = payload.allplayers;

  // 2. DETECTAR INÍCIO DE NOVA PARTIDA
  if (!currentMatchId && mapData?.phase === "live") {
    currentMatchId = generateId();
    lastRoundNumber = 0;
    console.log(`[GSI] New match started: ${currentMatchId}`);
  }

  if (!currentMatchId) {
    return; // Sem partida ativa
  }

  // 3. ATUALIZAR DADOS DA PARTIDA
  if (mapData) {
    await upsertMatch({
      id: currentMatchId,
      mapName: mapData.name || "unknown",
      gameMode: mapData.mode || "unknown",
      phase: mapData.phase || "warmup",
      teamCtScore: String(mapData.team_ct?.score || 0),
      teamTScore: String(mapData.team_t?.score || 0),
      currentRound: String(mapData.round || 0),
      roundPhase: roundData?.phase || "unknown",
      bombState: roundData?.bomb || "none",
      roundWinner: roundData?.win_team || null,
      lastUpdate: new Date(),
    });
  }

  // 4. DETECTAR FIM DE ROUND
  if (roundData && mapData) {
    const currentRoundNum = mapData.round || 0;
    const currentRoundPhase = roundData.phase || "";
    
    if (
      currentRoundPhase === "over" &&
      lastRoundPhase !== "over" &&
      roundData.win_team &&
      currentRoundNum > lastRoundNumber
    ) {
      await addRoundHistory({
        id: generateId(),
        matchId: currentMatchId,
        roundNumber: String(currentRoundNum),
        winner: roundData.win_team,
        reason: roundData.bomb || "eliminated",
        ctScore: String(mapData.team_ct?.score || 0),
        tScore: String(mapData.team_t?.score || 0),
        timestamp: new Date(),
      });
      
      lastRoundNumber = currentRoundNum;
    }
    
    lastRoundPhase = currentRoundPhase;
  }

  // 5. ATUALIZAR ESTATÍSTICAS DOS JOGADORES
  if (allPlayers) {
    for (const [steamId, playerData] of Object.entries(allPlayers)) {
      // Encontrar arma atual
      let currentWeapon = "none";
      if (playerData.weapons) {
        for (const [weaponId, weaponData] of Object.entries(playerData.weapons)) {
          if (weaponData.state === "active") {
            currentWeapon = weaponData.name || weaponId;
            break;
          }
        }
      }

      await upsertPlayerStat({
        id: `${currentMatchId}-${steamId}`,
        matchId: currentMatchId,
        steamId: steamId,
        name: playerData.name || "Unknown",
        team: playerData.team || "unknown",
        health: String(playerData.state?.health || 0),
        armor: String(playerData.state?.armor || 0),
        kills: String(playerData.match_stats?.kills || 0),
        assists: String(playerData.match_stats?.assists || 0),
        deaths: String(playerData.match_stats?.deaths || 0),
        mvps: String(playerData.match_stats?.mvps || 0),
        score: String(playerData.match_stats?.score || 0),
        money: String(playerData.state?.money || 0),
        currentWeapon: currentWeapon,
        lastUpdate: new Date(),
      });
    }
  }

  // 6. DETECTAR FIM DA PARTIDA
  if (mapData?.phase === "gameover") {
    console.log(`[GSI] Match ${currentMatchId} ended`);
    currentMatchId = null;
    lastRoundNumber = 0;
    lastRoundPhase = "";
  }
}
```

### Endpoints HTTP

```typescript
// POST / - Recebe dados do CS2
app.post("/", async (req, res) => {
  try {
    await processGSIPayload(req.body);
    res.status(200).send("OK");
  } catch (error) {
    console.error("[GSI] Error handling request:", error);
    res.status(500).send("Internal Server Error");
  }
});

// GET /health - Health check
app.get("/health", (req, res) => {
  res.status(200).json({ 
    status: "ok", 
    currentMatch: currentMatchId 
  });
});
```

### Inicialização

```typescript
export function startGSIServer() {
  const app = express();
  
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // ... configurar rotas ...

  app.listen(GSI_PORT, "0.0.0.0", () => {
    console.log(`[GSI] Server listening on port ${GSI_PORT}`);
    console.log(`[GSI] Waiting for CS2 game state data...`);
  });
}
```

---

## Backend - API tRPC

### Arquivo: `server/routers.ts`

Define os endpoints que o frontend pode chamar.

### Rotas Implementadas

```typescript
export const appRouter = router({
  // Rotas de autenticação (não usadas para partidas)
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      // ...
    }),
  }),

  // Rotas de partidas CS2
  match: router({
    // Buscar partida ativa
    getActive: publicProcedure.query(async () => {
      const { getActiveMatch } = await import("./db");
      return await getActiveMatch();
    }),
    
    // Buscar partida por ID
    getById: publicProcedure
      .input(z.string())
      .query(async ({ input }) => {
        const { getMatch } = await import("./db");
        return await getMatch(input);
      }),
    
    // Buscar jogadores de uma partida
    getPlayers: publicProcedure
      .input(z.string())
      .query(async ({ input }) => {
        const { getMatchPlayers } = await import("./db");
        return await getMatchPlayers(input);
      }),
    
    // Buscar rounds de uma partida
    getRounds: publicProcedure
      .input(z.string())
      .query(async ({ input }) => {
        const { getMatchRounds } = await import("./db");
        return await getMatchRounds(input);
      }),
  }),
});
```

### Uso no Frontend

```typescript
// Buscar partida ativa
const { data: match } = trpc.match.getActive.useQuery();

// Buscar jogadores
const { data: players } = trpc.match.getPlayers.useQuery(matchId);

// Buscar rounds
const { data: rounds } = trpc.match.getRounds.useQuery(matchId);
```

---

## Frontend - Dashboard React

### Arquivo: `client/src/pages/Home.tsx`

### Estrutura do Componente

```typescript
export default function Home() {
  const [matchId, setMatchId] = useState<string | null>(null);

  // Buscar partida ativa a cada 2 segundos
  const { data: activeMatch, isLoading: loadingMatch } = 
    trpc.match.getActive.useQuery(undefined, {
      refetchInterval: 2000,
    });

  // Atualizar matchId quando encontrar partida ativa
  useEffect(() => {
    if (activeMatch?.id) {
      setMatchId(activeMatch.id);
    }
  }, [activeMatch]);

  // Buscar jogadores da partida
  const { data: players = [], isLoading: loadingPlayers } = 
    trpc.match.getPlayers.useQuery(matchId || "", {
      enabled: !!matchId,
      refetchInterval: 2000,
    });

  // Buscar histórico de rounds
  const { data: rounds = [], isLoading: loadingRounds } = 
    trpc.match.getRounds.useQuery(matchId || "", {
      enabled: !!matchId,
      refetchInterval: 2000,
    });

  // Separar jogadores por time
  const ctPlayers = players.filter((p) => p.team === "CT");
  const tPlayers = players.filter((p) => p.team === "T");

  // ... renderização ...
}
```

### Componentes Visuais

#### 1. Estado: Aguardando Partida

```tsx
if (!activeMatch) {
  return (
    <Card>
      <Trophy icon />
      <h2>Aguardando Partida</h2>
      <p>Nenhuma partida ativa no momento...</p>
      <Link to="/instructions">Ver Instruções</Link>
    </Card>
  );
}
```

#### 2. Placar da Partida

```tsx
<Card>
  <div className="flex justify-between">
    {/* Time CT */}
    <div>
      <div>COUNTER-TERRORISTS</div>
      <div className="text-6xl">{activeMatch.teamCtScore}</div>
    </div>

    {/* Informações centrais */}
    <div>
      <Badge>🔴 AO VIVO</Badge>
      <div>{activeMatch.mapName}</div>
      <div>Round {activeMatch.currentRound}</div>
    </div>

    {/* Time T */}
    <div>
      <div>TERRORISTS</div>
      <div className="text-6xl">{activeMatch.teamTScore}</div>
    </div>
  </div>

  {/* Estado da bomba */}
  {activeMatch.bombState !== "none" && (
    <Badge>💣 BOMBA: {activeMatch.bombState}</Badge>
  )}
</Card>
```

#### 3. Tabelas de Jogadores

```tsx
<Card>
  <CardHeader>
    <CardTitle>Counter-Terrorists ({ctPlayers.length})</CardTitle>
  </CardHeader>
  <CardContent>
    {ctPlayers.map((player) => (
      <PlayerRow key={player.id} player={player} />
    ))}
  </CardContent>
</Card>
```

#### 4. Componente PlayerRow

```tsx
function PlayerRow({ player }: { player: any }) {
  const kd = player.deaths === "0" 
    ? player.kills 
    : (parseInt(player.kills) / parseInt(player.deaths)).toFixed(2);
  
  const isAlive = parseInt(player.health) > 0;

  return (
    <div className={!isAlive && "opacity-50"}>
      {/* Nome e arma */}
      <div>
        <span>{player.name}</span>
        <span>{player.currentWeapon}</span>
      </div>

      {/* Vida e dinheiro */}
      <div>
        <div>{isAlive ? `${player.health} HP` : "💀 MORTO"}</div>
        <div>${player.money}</div>
      </div>

      {/* Estatísticas */}
      <div>
        <span>K: {player.kills}</span>
        <span>D: {player.deaths}</span>
        <span>A: {player.assists}</span>
        <span>MVP: {player.mvps}</span>
        <span>K/D: {kd}</span>
      </div>
    </div>
  );
}
```

#### 5. Histórico de Rounds

```tsx
<Card>
  <CardHeader>
    <CardTitle>Histórico de Rounds</CardTitle>
  </CardHeader>
  <CardContent>
    {rounds.map((round) => (
      <Badge key={round.id} className={
        round.winner === "CT" 
          ? "bg-blue-900" 
          : "bg-orange-900"
      }>
        R{round.roundNumber}: {round.winner} 
        ({round.ctScore}-{round.tScore})
      </Badge>
    ))}
  </CardContent>
</Card>
```

### Design System

**Cores:**
- Background: Gradiente escuro (slate-900 → slate-800)
- CT: Azul (#3b82f6)
- T: Laranja (#ea580c)
- Texto: Branco/Slate claro
- Acentos: Verde (kills), Vermelho (deaths), Amarelo (MVPs)

**Tipografia:**
- Font: System font stack
- Placar: text-6xl font-black
- Títulos: text-2xl font-bold
- Corpo: text-base

**Componentes shadcn/ui:**
- Card
- Badge
- Button
- Skeleton (loading states)

---

## Game State Integration - Dados Disponíveis

### Estrutura Completa do Payload GSI

O CS2 envia um payload JSON extremamente detalhado. Aqui está **TUDO** que é possível capturar:

### 1. `provider` - Informações do Cliente/Servidor

```json
{
  "provider": {
    "name": "Counter-Strike: Global Offensive",
    "appid": 730,
    "version": 13960,
    "steamid": "76561198012345678",
    "timestamp": 1729234567
  }
}
```

**Campos:**
- `name`: Nome do jogo
- `appid`: ID da aplicação Steam (sempre 730 para CS2)
- `version`: Versão do jogo
- `steamid`: Steam ID do jogador local
- `timestamp`: Unix timestamp

**Uso possível:**
- Identificar qual computador enviou os dados
- Verificar versão do jogo
- Timestamp para sincronização

### 2. `map` - Dados do Mapa e Partida

```json
{
  "map": {
    "mode": "competitive",
    "name": "de_dust2",
    "phase": "live",
    "round": 5,
    "team_ct": {
      "score": 3,
      "consecutive_round_losses": 0,
      "timeouts_remaining": 1,
      "matches_won_this_series": 0
    },
    "team_t": {
      "score": 2,
      "consecutive_round_losses": 1,
      "timeouts_remaining": 1,
      "matches_won_this_series": 0
    },
    "num_matches_to_win_series": 1,
    "current_spectators": 0,
    "souvenirs_total": 0
  }
}
```

**Campos:**
- `mode`: Modo de jogo ("competitive", "casual", "deathmatch", "wingman")
- `name`: Nome do mapa (ex: "de_dust2", "de_mirage")
- `phase`: Fase da partida
  - `"warmup"`: Aquecimento
  - `"live"`: Partida em andamento
  - `"intermission"`: Entre rounds
  - `"gameover"`: Partida finalizada
- `round`: Número do round atual (1-30+)
- `team_ct.score`: Placar do time CT
- `team_t.score`: Placar do time T
- `team_ct.consecutive_round_losses`: Rounds perdidos consecutivos (para loss bonus)
- `team_ct.timeouts_remaining`: Timeouts restantes
- `team_ct.matches_won_this_series`: Mapas vencidos na série (BO3, BO5)
- `num_matches_to_win_series`: Quantos mapas precisa vencer
- `current_spectators`: Número de espectadores
- `souvenirs_total`: Total de souvenirs dropados

**Uso possível:**
- Detectar modo de jogo e ajustar UI
- Mostrar loss bonus dos times
- Indicar timeouts disponíveis
- Mostrar progresso em séries BO3/BO5

### 3. `round` - Dados do Round Atual

```json
{
  "round": {
    "phase": "live",
    "bomb": "planted",
    "win_team": null
  }
}
```

**Campos:**
- `phase`: Fase do round
  - `"freezetime"`: Tempo de compra
  - `"live"`: Round em andamento
  - `"over"`: Round terminado
- `bomb`: Estado da bomba
  - `"planted"`: Bomba plantada
  - `"defused"`: Bomba defusada
  - `"exploded"`: Bomba explodiu
  - `null` ou ausente: Bomba não plantada
- `win_team`: Time vencedor do round
  - `"CT"`: Counter-Terrorists venceram
  - `"T"`: Terrorists venceram
  - `null`: Round ainda em andamento

**Uso possível:**
- Mostrar countdown da bomba
- Indicar visualmente estado da bomba
- Registrar motivo da vitória do round

### 4. `player` - Dados do Jogador Local

```json
{
  "player": {
    "steamid": "76561198012345678",
    "name": "Player1",
    "observer_slot": 1,
    "team": "CT",
    "activity": "playing",
    "state": {
      "health": 100,
      "armor": 100,
      "helmet": true,
      "flashed": 0,
      "smoked": 0,
      "burning": 0,
      "money": 3500,
      "round_kills": 2,
      "round_killhs": 1,
      "round_totaldmg": 250,
      "equip_value": 4700,
      "defusekit": false
    },
    "weapons": {
      "weapon_0": {
        "name": "weapon_ak47",
        "paintkit": "default",
        "type": "Rifle",
        "ammo_clip": 30,
        "ammo_clip_max": 30,
        "ammo_reserve": 90,
        "state": "active"
      },
      "weapon_1": {
        "name": "weapon_glock",
        "paintkit": "default",
        "type": "Pistol",
        "ammo_clip": 20,
        "ammo_clip_max": 20,
        "ammo_reserve": 120,
        "state": "holstered"
      }
    },
    "match_stats": {
      "kills": 12,
      "assists": 3,
      "deaths": 5,
      "mvps": 2,
      "score": 35
    },
    "position": {
      "x": 123.45,
      "y": -456.78,
      "z": 90.12
    },
    "forward": {
      "x": 0.5,
      "y": 0.8,
      "z": 0.0
    }
  }
}
```

**Campos:**
- `steamid`: Steam ID único
- `name`: Nome do jogador
- `observer_slot`: Slot de espectador (1-10)
- `team`: Time ("CT", "T", "Spectator")
- `activity`: Atividade ("playing", "menu", "textinput")
- `state.health`: Vida (0-100)
- `state.armor`: Colete (0-100)
- `state.helmet`: Tem capacete? (boolean)
- `state.flashed`: Nível de flash (0-255)
- `state.smoked`: Dentro de fumaça? (0-255)
- `state.burning`: Queimando? (0-255)
- `state.money`: Dinheiro atual
- `state.round_kills`: Kills neste round
- `state.round_killhs`: Headshots neste round
- `state.round_totaldmg`: Dano total neste round
- `state.equip_value`: Valor total do equipamento
- `state.defusekit`: Tem kit de defuse? (boolean)
- `weapons`: Objeto com todas as armas
  - `name`: Nome da arma
  - `paintkit`: Skin da arma
  - `type`: Tipo ("Rifle", "Pistol", "Knife", "Grenade")
  - `ammo_clip`: Munição no pente
  - `ammo_clip_max`: Capacidade do pente
  - `ammo_reserve`: Munição reserva
  - `state`: Estado ("active", "holstered")
- `match_stats`: Estatísticas da partida
  - `kills`: Total de kills
  - `assists`: Total de assistências
  - `deaths`: Total de mortes
  - `mvps`: Total de MVPs
  - `score`: Pontuação total
- `position`: Posição 3D no mapa
  - `x`, `y`, `z`: Coordenadas
- `forward`: Direção que está olhando
  - `x`, `y`, `z`: Vetor direcional

**Uso possível:**
- Mostrar munição restante
- Indicar se está flashado/queimando
- Mostrar valor do equipamento
- Criar mapa 2D com posições
- Mostrar dano causado no round
- Indicar quem tem kit de defuse

### 5. `allplayers` - Dados de Todos os Jogadores

```json
{
  "allplayers": {
    "76561198012345678": {
      "name": "Player1",
      "observer_slot": 1,
      "team": "CT",
      "state": {
        "health": 100,
        "armor": 100,
        "helmet": true,
        "flashed": 0,
        "smoked": 0,
        "burning": 0,
        "money": 3500,
        "round_kills": 2,
        "round_killhs": 1,
        "equip_value": 4700,
        "defusekit": true
      },
      "weapons": {
        // ... mesma estrutura de player.weapons
      },
      "match_stats": {
        "kills": 12,
        "assists": 3,
        "deaths": 5,
        "mvps": 2,
        "score": 35
      },
      "position": {
        "x": 123.45,
        "y": -456.78,
        "z": 90.12
      },
      "forward": {
        "x": 0.5,
        "y": 0.8,
        "z": 0.0
      }
    },
    "76561198087654321": {
      // ... outro jogador
    }
  }
}
```

**Estrutura:** Objeto onde cada chave é um Steam ID e o valor contém os mesmos dados de `player`.

**Importante:** 
- ❌ **Bots NÃO aparecem** em `allplayers`
- ✅ Apenas jogadores humanos são incluídos
- ✅ Inclui jogadores de ambos os times
- ✅ Inclui espectadores

**Uso possível:**
- Dashboard completo de todos os jogadores
- Comparação de estatísticas entre jogadores
- Mapa com posições de todos
- Ranking de kills/deaths em tempo real

### 6. `phase_countdowns` - Contadores de Tempo

```json
{
  "phase_countdowns": {
    "phase": "bomb",
    "phase_ends_in": "35.5"
  }
}
```

**Campos:**
- `phase`: Fase atual
  - `"freezetime"`: Tempo de compra
  - `"bomb"`: Bomba plantada (countdown até explosão)
  - `"defuse"`: Defusando bomba
  - `"timeout_ct"`: Timeout do CT
  - `"timeout_t"`: Timeout do T
- `phase_ends_in`: Segundos restantes (string com decimal)

**Uso possível:**
- Mostrar countdown da bomba em tempo real
- Indicar tempo de compra restante
- Mostrar duração de timeouts

### 7. `allgrenades` - Granadas Ativas

```json
{
  "allgrenades": {
    "0": {
      "owner": "76561198012345678",
      "position": {
        "x": 100.0,
        "y": -200.0,
        "z": 50.0
      },
      "velocity": {
        "x": 10.5,
        "y": -5.2,
        "z": 8.3
      },
      "type": "smoke",
      "effecttime": "15.0",
      "lifetime": "2.5"
    }
  }
}
```

**Campos:**
- `owner`: Steam ID de quem lançou
- `position`: Posição 3D da granada
- `velocity`: Velocidade da granada
- `type`: Tipo de granada
  - `"frag"`: HE grenade
  - `"smoke"`: Smoke grenade
  - `"flashbang"`: Flashbang
  - `"firebomb"`: Molotov/Incendiary
  - `"decoy"`: Decoy
- `effecttime`: Tempo de efeito restante (segundos)
- `lifetime`: Tempo de vida total (segundos)

**Uso possível:**
- Mostrar granadas ativas no mapa
- Indicar quem lançou cada granada
- Countdown de fumaças/molotovs
- Análise de utility usage

### 8. `bomb` - Dados da Bomba C4

```json
{
  "bomb": {
    "state": "planted",
    "position": {
      "x": 150.0,
      "y": -300.0,
      "z": 25.0
    },
    "countdown": "35.5",
    "player": "76561198012345678"
  }
}
```

**Campos:**
- `state`: Estado da bomba
  - `"carried"`: Sendo carregada
  - `"dropped"`: Dropada no chão
  - `"planting"`: Sendo plantada
  - `"planted"`: Plantada
  - `"defusing"`: Sendo defusada
  - `"defused"`: Defusada
  - `"exploded"`: Explodiu
- `position`: Posição 3D da bomba
- `countdown`: Segundos até explodir (quando plantada)
- `player`: Steam ID de quem está com/defusando a bomba

**Uso possível:**
- Mostrar localização da bomba no mapa
- Countdown preciso até explosão
- Indicar quem está defusando
- Alertas visuais quando bomba é plantada

---

## Dados Atualmente Capturados vs. Disponíveis

### ✅ Dados Capturados e Exibidos

| Dado | Fonte | Tabela | Exibido no Dashboard |
|------|-------|--------|---------------------|
| Nome do mapa | `map.name` | `matches.mapName` | ✅ Sim |
| Modo de jogo | `map.mode` | `matches.gameMode` | ✅ Sim |
| Fase da partida | `map.phase` | `matches.phase` | ✅ Sim (implícito) |
| Placar CT | `map.team_ct.score` | `matches.teamCtScore` | ✅ Sim |
| Placar T | `map.team_t.score` | `matches.teamTScore` | ✅ Sim |
| Round atual | `map.round` | `matches.currentRound` | ✅ Sim |
| Fase do round | `round.phase` | `matches.roundPhase` | ✅ Sim |
| Estado da bomba | `round.bomb` | `matches.bombState` | ✅ Sim |
| Vencedor do round | `round.win_team` | `roundHistory.winner` | ✅ Sim |
| Nome do jogador | `allplayers[].name` | `playerStats.name` | ✅ Sim |
| Time do jogador | `allplayers[].team` | `playerStats.team` | ✅ Sim |
| Vida | `allplayers[].state.health` | `playerStats.health` | ✅ Sim |
| Colete | `allplayers[].state.armor` | `playerStats.armor` | ✅ Sim |
| Kills | `allplayers[].match_stats.kills` | `playerStats.kills` | ✅ Sim |
| Deaths | `allplayers[].match_stats.deaths` | `playerStats.deaths` | ✅ Sim |
| Assists | `allplayers[].match_stats.assists` | `playerStats.assists` | ✅ Sim |
| MVPs | `allplayers[].match_stats.mvps` | `playerStats.mvps` | ✅ Sim |
| Score | `allplayers[].match_stats.score` | `playerStats.score` | ✅ Sim |
| Dinheiro | `allplayers[].state.money` | `playerStats.money` | ✅ Sim |
| Arma atual | `allplayers[].weapons[].name` | `playerStats.currentWeapon` | ✅ Sim |

### ❌ Dados Disponíveis MAS NÃO Capturados

| Dado | Fonte | Uso Possível |
|------|-------|--------------|
| Posição do jogador | `allplayers[].position` | Mapa 2D com posições |
| Direção do olhar | `allplayers[].forward` | Indicar para onde está olhando |
| Capacete | `allplayers[].state.helmet` | Mostrar se tem capacete |
| Flashado | `allplayers[].state.flashed` | Indicar se está flashado |
| Queimando | `allplayers[].state.burning` | Indicar se está em fogo |
| Kills no round | `allplayers[].state.round_kills` | Destacar quem fez ace |
| Headshots no round | `allplayers[].state.round_killhs` | Mostrar precisão |
| Dano no round | `allplayers[].state.round_totaldmg` | Mostrar dano causado |
| Valor do equipamento | `allplayers[].state.equip_value` | Comparar investimento |
| Kit de defuse | `allplayers[].state.defusekit` | Indicar quem pode defusar |
| Munição | `allplayers[].weapons[].ammo_clip` | Mostrar munição restante |
| Skin da arma | `allplayers[].weapons[].paintkit` | Mostrar skins |
| Timeouts restantes | `map.team_ct.timeouts_remaining` | Indicar timeouts disponíveis |
| Loss bonus | `map.team_ct.consecutive_round_losses` | Mostrar economia |
| Countdown da bomba | `phase_countdowns.phase_ends_in` | Timer preciso |
| Granadas ativas | `allgrenades` | Mostrar utility no mapa |
| Posição da bomba | `bomb.position` | Marcar bomba no mapa |
| Quem está defusando | `bomb.player` | Indicar defuser |
| Espectadores | `map.current_spectators` | Contador de viewers |

---

## Configuração e Deploy

### Requisitos do Sistema

**Servidor (Dashboard):**
- Node.js 22.13.0+
- MySQL 8.0+ ou TiDB
- 2GB RAM mínimo
- 10GB espaço em disco
- Porta 3000 e 3001 disponíveis

**Máquinas de Jogo (CS2):**
- CS2 instalado via Steam
- Acesso de escrita na pasta `cfg`
- Conexão de rede com o servidor

### Instalação do Servidor

```bash
# 1. Clonar o projeto
git clone <repository>
cd cs2-tournament-dashboard

# 2. Instalar dependências
pnpm install

# 3. Configurar variáveis de ambiente
# Editar .env com DATABASE_URL e outras configs

# 4. Aplicar schema do banco
pnpm db:push

# 5. Iniciar servidor de desenvolvimento
pnpm dev

# Ou para produção:
pnpm build
pnpm start
```

### Configuração do CS2

```bash
# 1. Copiar arquivo GSI para pasta do CS2
cp gamestate_integration_lanhouse.cfg \
   "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\"

# 2. Editar o arquivo e configurar IP do servidor
# "uri" "http://192.168.1.100:3001"

# 3. Iniciar CS2 e carregar um mapa
# O GSI será ativado automaticamente
```

### Configuração de Rede

**Firewall (Windows):**
```powershell
# Liberar porta 3001 (GSI)
New-NetFirewallRule -DisplayName "CS2 GSI" -Direction Inbound -LocalPort 3001 -Protocol TCP -Action Allow

# Liberar porta 3000 (Dashboard)
New-NetFirewallRule -DisplayName "CS2 Dashboard" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

**Firewall (Linux):**
```bash
# UFW
sudo ufw allow 3000/tcp
sudo ufw allow 3001/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3001 -j ACCEPT
```

### Variáveis de Ambiente

```env
# Banco de Dados
DATABASE_URL=mysql://user:password@localhost:3306/cs2_dashboard

# JWT para sessões
JWT_SECRET=your-secret-key-here

# OAuth (se usar autenticação)
VITE_APP_ID=your-app-id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://oauth.manus.im

# Informações do app
VITE_APP_TITLE=CS2 Tournament Dashboard
VITE_APP_LOGO=/logo.png

# Owner (opcional)
OWNER_OPEN_ID=your-open-id
OWNER_NAME=Admin
```

---

## Expansões Futuras

### 1. Mapa 2D com Posições dos Jogadores

**Implementação:**
1. Adicionar campos `positionX`, `positionY`, `positionZ` na tabela `playerStats`
2. Capturar `allplayers[].position` no GSI server
3. Criar componente `<MiniMap>` no frontend
4. Usar imagem do mapa como background
5. Plotar jogadores como pontos coloridos

**Complexidade:** Média  
**Valor:** Alto (visualização tática)

### 2. Indicador de Vencedor

**Implementação:**
1. Adicionar lógica no frontend para detectar `phase === "gameover"`
2. Comparar `teamCtScore` vs `teamTScore`
3. Exibir badge "🏆 VENCEDOR" no time que ganhou
4. Adicionar animação de confetes

**Complexidade:** Baixa  
**Valor:** Médio (melhor UX)

### 3. Indicador de Overtime

**Implementação:**
1. Verificar se `currentRound > 24`
2. Calcular número do overtime: `Math.floor((currentRound - 24) / 6) + 1`
3. Exibir badge "⚡ OVERTIME X"
4. Destacar visualmente

**Complexidade:** Baixa  
**Valor:** Médio (informação importante)

### 4. Estatísticas Avançadas

**Implementação:**
1. Adicionar campos: `headshotPercentage`, `adr` (average damage per round), `kast`
2. Calcular no backend ou frontend
3. Exibir em tabela expandida

**Complexidade:** Média  
**Valor:** Alto (para análise profissional)

### 5. Histórico de Partidas

**Implementação:**
1. Não deletar partidas antigas, apenas marcar como `archived`
2. Criar página `/history` listando partidas
3. Permitir visualizar detalhes de partidas passadas
4. Exportar para CSV/JSON

**Complexidade:** Média  
**Valor:** Alto (análise pós-jogo)

### 6. Múltiplas Partidas Simultâneas

**Implementação:**
1. Modificar GSI server para aceitar `room_id` no payload
2. Criar tabela `rooms` no banco
3. Modificar frontend para selecionar qual partida visualizar
4. Ou criar grid com múltiplos dashboards

**Complexidade:** Alta  
**Valor:** Alto (para lan houses grandes)

### 7. Modo de Teste com Bots Simulados

**Implementação:**
1. Criar endpoint `/api/test/simulate` que gera dados falsos
2. Popular banco com partida simulada
3. Adicionar botão "Modo Demo" no dashboard
4. Útil para testar sem jogo rodando

**Complexidade:** Baixa  
**Valor:** Médio (facilita desenvolvimento)

### 8. Integração com OBS

**Implementação:**
1. Criar endpoint `/overlay` com layout simplificado
2. Remover navegação e decorações
3. Usar como Browser Source no OBS
4. Adicionar chroma key (fundo verde)

**Complexidade:** Baixa  
**Valor:** Alto (para streaming)

### 9. Sistema de Replay

**Implementação:**
1. Salvar todos os payloads GSI no banco
2. Criar player de replay no frontend
3. Permitir "assistir" partida em velocidade acelerada
4. Pausar/avançar/retroceder

**Complexidade:** Alta  
**Valor:** Muito Alto (análise detalhada)

### 10. Notificações em Tempo Real

**Implementação:**
1. Adicionar WebSocket ao servidor
2. Emitir eventos: "ace", "clutch", "bomb_planted"
3. Exibir notificações toast no dashboard
4. Adicionar efeitos sonoros

**Complexidade:** Média  
**Valor:** Alto (engajamento)

---

## Troubleshooting

### Problema: Dashboard não mostra partida

**Diagnóstico:**
```bash
# 1. Verificar se servidor GSI está rodando
curl http://localhost:3001/health
# Deve retornar: {"status":"ok","currentMatch":null}

# 2. Verificar logs do servidor
# Procurar por: [GSI] Server listening on port 3001

# 3. Verificar se CS2 está enviando dados
# Adicionar log temporário em gsi-server.ts:
console.log("[GSI] Received:", req.body);
```

**Soluções:**
- ✅ Verificar arquivo `.cfg` está na pasta correta
- ✅ Verificar IP no arquivo `.cfg` está correto
- ✅ Verificar token de autenticação
- ✅ Verificar firewall não está bloqueando porta 3001
- ✅ Executar `mp_warmup_end` no CS2 para sair do warmup

### Problema: Jogadores não aparecem

**Causa:** Bots não são detectados pelo GSI

**Solução:**
- Usar jogadores humanos (conta Steam secundária)
- Ou implementar modo de teste com dados simulados

### Problema: Dados não atualizam

**Diagnóstico:**
```typescript
// Verificar refetchInterval no frontend
const { data } = trpc.match.getActive.useQuery(undefined, {
  refetchInterval: 2000, // Deve estar presente
});
```

**Soluções:**
- ✅ Verificar `refetchInterval` está configurado
- ✅ Verificar conexão com banco de dados
- ✅ Verificar logs de erro no console do navegador

### Problema: Erro de CORS

**Solução:**
```typescript
// Em server/_core/index.ts, adicionar:
app.use(cors({
  origin: "*", // Ou especificar domínio
  credentials: true,
}));
```

### Problema: Banco de dados não conecta

**Diagnóstico:**
```bash
# Testar conexão MySQL
mysql -h localhost -u user -p database_name

# Verificar DATABASE_URL no .env
echo $DATABASE_URL
```

**Soluções:**
- ✅ Verificar credenciais do banco
- ✅ Verificar banco de dados existe
- ✅ Executar `pnpm db:push` para criar tabelas

---

## Conclusão

Este documento fornece uma visão completa do sistema de dashboard CS2 Tournament. Com ele, qualquer desenvolvedor (ou Claude Code) pode:

1. ✅ Entender a arquitetura completa
2. ✅ Saber onde cada dado é processado
3. ✅ Conhecer TODOS os dados disponíveis no GSI
4. ✅ Expandir o sistema com novas funcionalidades
5. ✅ Resolver problemas comuns
6. ✅ Fazer deploy em produção

**O sistema está pronto para uso e altamente extensível!** 🎮🏆

---

**Desenvolvido com ❤️ por Manus AI**  
**Data: 18 de outubro de 2025**

