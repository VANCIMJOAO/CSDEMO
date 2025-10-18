# Guia Completo: Capturando Dados de Partidas de CS2 em Tempo Real com Game State Integration (GSI)

**Autor:** Manus AI
**Data:** 18 de outubro de 2025

## Introdução

Este guia detalha o processo de captura de dados de partidas de Counter-Strike 2 (CS2) em tempo real, utilizando o recurso nativo **Game State Integration (GSI)**. Esta solução é ideal para a criação de aplicações web, como a que você deseja para os campeonatos em sua lan house, permitindo a exibição de estatísticas e eventos ao vivo.

O GSI é um sistema robusto e oficial da Valve que permite que o cliente do CS2 envie informações detalhadas da partida para um servidor HTTP local ou remoto. A comunicação é feita através de requisições POST contendo dados em formato JSON, eliminando a necessidade de mods ou softwares de terceiros que possam interferir com o jogo.

---

## 1. Como Funciona o Game State Integration

O processo de integração é relativamente simples e se baseia em três componentes principais:

1.  **Arquivo de Configuração (.cfg):** Um arquivo de texto que você cria e coloca na pasta de configuração do CS2. Este arquivo instrui o jogo a enviar os dados da partida para um endereço (URI) específico.
2.  **Servidor HTTP (Endpoint):** Uma aplicação que você desenvolve para "ouvir" as requisições POST enviadas pelo jogo. Este servidor será responsável por receber, processar e armazenar os dados da partida.
3.  **Aplicação Web (Frontend):** A página web que se conecta ao seu servidor para obter os dados processados e exibi-los de forma amigável para os espectadores.

O fluxo de dados ocorre da seguinte maneira: `CS2 Game Client` -> `Arquivo .cfg` -> `Servidor HTTP (Backend)` -> `Aplicação Web (Frontend)`.

---

## 2. Configurando o CS2 para Enviar Dados

O primeiro passo é criar o arquivo de configuração que ativará o GSI no cliente do CS2.

### Passo 1: Localize a Pasta de Configuração

O arquivo de configuração deve ser colocado no seguinte diretório de instalação do Steam:

```
.../Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg/
```

> **Nota:** Embora o nome da pasta ainda seja `Counter-Strike Global Offensive`, este é o diretório correto para a instalação padrão do CS2.

### Passo 2: Crie o Arquivo de Configuração

Dentro da pasta `cfg`, crie um novo arquivo de texto. O nome do arquivo deve seguir o padrão `gamestate_integration_*.cfg`. Por exemplo, você pode nomeá-lo `gamestate_integration_lanhouse.cfg`.

### Passo 3: Adicione o Conteúdo ao Arquivo

Copie e cole o conteúdo abaixo no arquivo que você criou. Esta configuração é otimizada para capturar o máximo de dados possível de uma partida, ideal para o modo espectador em campeonatos.

```
"CS2 Lan House Integration v.1"
{
 "uri" "http://127.0.0.1:3000"      // Endereço do seu servidor
 "timeout" "5.0"
 "buffer"  "0.1"
 "throttle" "0.1"
 "heartbeat" "15.0"                 // Envia dados a cada 15s, mesmo sem eventos
 "auth"
 {
   "token" "SenhaSuperSecretaParaSuaLanHouse" // Token para autenticar as requisições
 }
 "data"
 {
   "provider"                  "1",
   "map"                       "1",
   "round"                     "1",
   "player_id"                 "1",
   "allplayers_id"             "1",
   "allplayers_state"          "1",
   "allplayers_match_stats"    "1",
   "allplayers_weapons"        "1",
   "allplayers_position"       "1",
   "phase_countdowns"          "1",
   "allgrenades"               "1"
 }
}

```

### Tabela de Parâmetros de Configuração

| Parâmetro | Descrição                                                                                             |
| :-------- | :---------------------------------------------------------------------------------------------------- |
| `uri`       | O endereço do seu servidor que receberá os dados. `127.0.0.1:3000` aponta para a máquina local na porta 3000. Você pode alterar para o IP do seu servidor na rede da lan house. |
| `timeout`   | Tempo em segundos que o jogo espera por uma resposta do seu servidor antes de considerar a requisição falha. |
| `buffer`    | Agrupa múltiplos eventos ocorridos em um curto período em uma única requisição, otimizando a comunicação. |
| `throttle`  | Intervalo mínimo em segundos entre o envio de duas requisições para evitar sobrecarregar o servidor.     |
| `heartbeat` | Força o envio de um pacote de dados completo em intervalos regulares, mesmo que nada tenha mudado no jogo. Útil para saber se o jogo ainda está ativo. |
| `auth/token`| Um token secreto que o jogo enviará em cada requisição. Seu servidor deve verificar este token para garantir que os dados são legítimos. **É altamente recomendado usar esta opção.** |
| `data`      | Seção onde você define quais "componentes" de dados do jogo você deseja receber. O valor `"1"` significa "ativado". |

---

## 3. Os Dados da Partida (Payload)

O CS2 envia um objeto JSON rico em detalhes. Abaixo estão os principais componentes que você pode solicitar na configuração.

### Tabela de Componentes de Dados

| Componente                 | Descrição                                                                                             |
| :------------------------- | :---------------------------------------------------------------------------------------------------- |
| `provider`                 | Informações sobre o jogo (AppID, SteamID do jogador, timestamp).                                        |
| `map`                      | Dados do mapa (nome, modo de jogo, fase da partida, placar dos times).                                  |
| `round`                    | Estado do round atual (fase - `live`, `freezetime`, `over`), estado da bomba (`planted`, `defused`).      |
| `allplayers_*`             | Conjunto de dados para **todos os jogadores** na partida. Inclui estado (vida, colete), estatísticas (kills, mortes), armas e SteamID. **Essencial para o modo espectador.** |
| `allplayers_position`      | Coordenadas X, Y, Z de todos os jogadores no mapa.                                                    |
| `phase_countdowns`         | Contadores de tempo para as fases do jogo (tempo restante do round, tempo para a bomba explodir).     |
| `allgrenades`              | Informações sobre todas as granadas e molotovs/incendiárias ativas no mapa (posição, tipo, tempo de vida). |

---

## 4. Próximos Passos: Desenvolvendo o Servidor

Com o CS2 configurado, o próximo passo é criar o servidor que receberá esses dados. Para isso, você pode usar diversas tecnologias, como Node.js (com Express ou o módulo `http` nativo) ou Python (com Flask ou FastAPI).

O servidor terá as seguintes responsabilidades:

1.  **Receber as requisições POST** na porta e no endereço configurados no arquivo `.cfg`.
2.  **Validar o token de autenticação** para garantir a segurança.
3.  **Processar o corpo (body) da requisição**, que contém o JSON com os dados da partida.
4.  **Armazenar ou retransmitir os dados** para a aplicação web (frontend), por exemplo, via WebSockets, para garantir a atualização em tempo real na tela dos espectadores.

No próximo passo, apresentarei um projeto de exemplo funcional com um servidor backend e uma página web frontend para ilustrar a implementação completa.

## Referências

- [1] Valve Developer Community. (2025). *Counter-Strike: Global Offensive Game State Integration*. [https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration)
- [2] tsuriga. (2015). *Quick Start guide to CS:GO Game State Integration*. [https://github.com/tsuriga/csgo-gsi-qsguide](https://github.com/tsuriga/csgo-gsi-qsguide)
- [3] arturn-dev. (N.d.). *csgo-gsi-ui*. [https://github.com/arturn-dev/csgo-gsi-ui](https://github.com/arturn-dev/csgo-gsi-ui)




---

## 5. Aplicação Web Desenvolvida

Foi desenvolvida uma aplicação web completa que demonstra a implementação prática do GSI para campeonatos de lan house. A aplicação inclui:

### Componentes do Sistema

**Backend (Node.js + Express):**
- Servidor GSI dedicado na porta 3001 que recebe os dados do CS2
- Processamento em tempo real dos payloads JSON
- Armazenamento em banco de dados MySQL/TiDB
- API tRPC para comunicação com o frontend

**Frontend (React + TypeScript):**
- Dashboard em tempo real com atualização automática a cada 2 segundos
- Exibição do placar da partida (CT vs T)
- Tabela de estatísticas dos jogadores separada por time
- Histórico de rounds com vencedores
- Design responsivo e moderno com tema escuro

**Banco de Dados:**
- Tabela `matches`: Armazena informações da partida (mapa, placar, fase)
- Tabela `playerStats`: Estatísticas individuais dos jogadores
- Tabela `roundHistory`: Histórico completo dos rounds

### Funcionalidades Implementadas

1. **Detecção Automática de Partidas:** O sistema detecta automaticamente quando uma nova partida começa
2. **Atualização em Tempo Real:** Todos os dados são atualizados automaticamente sem necessidade de refresh
3. **Estatísticas Detalhadas:** Kills, deaths, assists, MVPs, K/D ratio, dinheiro, vida, colete
4. **Estado dos Jogadores:** Indica visualmente jogadores vivos/mortos e suas armas atuais
5. **Histórico de Rounds:** Registra o vencedor de cada round e o motivo (bomba explodida, defusada, etc)

### Como Usar a Aplicação

1. **Instalar o arquivo de configuração GSI** no CS2 seguindo as instruções fornecidas
2. **Iniciar o servidor** da aplicação (já está rodando automaticamente)
3. **Abrir o dashboard** no navegador
4. **Iniciar uma partida** no CS2 (contra bots ou online)
5. **Assistir os dados** sendo atualizados em tempo real no dashboard

### Configuração para Múltiplos Computadores

Para receber dados de várias máquinas na lan house:

1. Identifique o IP do servidor onde o dashboard está rodando
2. Em cada computador da lan house, edite o arquivo `.cfg` e altere:
   ```
   "uri" "http://IP_DO_SERVIDOR:3001"
   ```
3. Certifique-se de que a porta 3001 está acessível na rede local

### Arquivo de Configuração Fornecido

O arquivo `gamestate_integration_lanhouse.cfg` está incluído no projeto e já está configurado para:
- Enviar dados para `http://127.0.0.1:3001` (localhost)
- Incluir todos os dados necessários para o dashboard
- Usar autenticação com token
- Atualizar a cada 0.1 segundos com heartbeat de 15 segundos

---

## 6. Próximos Passos e Melhorias Possíveis

Com o sistema básico funcionando, você pode expandir com:

1. **Múltiplas Partidas Simultâneas:** Modificar o sistema para suportar várias partidas ao mesmo tempo
2. **Replay de Partidas:** Salvar e reproduzir partidas anteriores
3. **Estatísticas Avançadas:** Gráficos de desempenho, mapas de calor, análise de economia
4. **Transmissão ao Vivo:** Integrar com OBS ou outras ferramentas de streaming
5. **Sistema de Torneios:** Gerenciar brackets, eliminatórias e classificações
6. **Notificações:** Alertas para eventos importantes (ace, clutch, etc)
7. **Modo Espectador Avançado:** Visualização de posições dos jogadores no mapa

---

## Conclusão

O Game State Integration é uma ferramenta poderosa e oficial da Valve que permite criar experiências ricas para espectadores e jogadores. A implementação é relativamente simples e não requer modificações no jogo, tornando-a ideal para uso em lan houses e campeonatos.

O sistema desenvolvido fornece uma base sólida que pode ser expandida conforme as necessidades específicas dos seus campeonatos. Todo o código está organizado e documentado para facilitar futuras modificações e melhorias.

