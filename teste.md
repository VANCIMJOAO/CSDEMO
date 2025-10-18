🔍 RELATÓRIO DE AUDITORIA - CS2 Analyzer (Sistema de Torneios)

  ⚠️ PROBLEMAS CRÍTICOS (Alta Prioridade)

  1. Perda de Dados na Atualização de Torneio

  Localização: /home/vancim/cs2analyzer/web_app/main.py:1804-1814

  Problema: O endpoint PUT /api/manage-tournaments/{slug} não preserva todos os campos do torneio ao atualizar.

  Campos perdidos:
  - prize_pool, format, location
  - prize_1st, prize_2nd, prize_3rd
  - bracket

  Impacto: Ao editar um torneio, dados de premiação, formato e bracket são apagados.

  Código atual:
  tournaments[i] = {
      "slug": slug,
      "name": tournament_data.get("name"),
      "description": tournament_data.get("description", ""),
      "start_date": tournament_data.get("start_date", ""),
      "end_date": tournament_data.get("end_date", ""),
      "logo": tournament_data.get("logo", ""),
      "team_ids": tournament_data.get("team_ids", tournament.get("team_ids", [])),
      "created_at": tournament.get("created_at", datetime.now().isoformat()),
      "updated_at": datetime.now().isoformat()
  }
  # Faltam: prize_pool, format, location, prize_1st, prize_2nd, prize_3rd, bracket

  ---
  2. Race Condition no Salvamento de JSON

  Localização: Múltiplos endpoints que manipulam tournaments.json

  Problema: Não há mecanismo de locking ao ler/escrever tournaments.json. Requisições simultâneas podem sobrescrever dados.

  Cenário:
  1. Usuário A lê tournaments.json (10 torneios)
  2. Usuário B lê tournaments.json (10 torneios)
  3. Usuário A adiciona torneio e salva (11 torneios)
  4. Usuário B adiciona torneio e salva (11 torneios, mas o torneio de A é perdido)

  Impacto: Perda de dados em cenários de uso concorrente.

  ---
  3. Lógica de Identificação de Times Frágil

  Localização: /home/vancim/cs2analyzer/web_app/main.py:2266-2271

  Problema: A função find_team_by_players usa apenas verificação de "qualquer SteamID coincidente" para identificar times.

  def find_team_by_players(steamid_list):
      for team in teams:
          team_steamids = [str(p['steamid']) for p in team.get('players', [])]
          if any(sid in team_steamids for sid in steamid_list):
              return team['name']
      return None

  Cenários problemáticos:
  - Jogador participa de 2 times diferentes no mesmo torneio (substituto)
  - Partida custom com lineup diferente do registrado
  - Apenas 1 jogador coincidindo já considera como o time inteiro

  Impacto: Resultados de bracket incorretos, times avançando indevidamente.

  ---
  🔴 PROBLEMAS GRAVES (Média Prioridade)

  4. Array Bounds não verificado no Bracket

  Localização: /home/vancim/cs2analyzer/web_app/main.py:2328-2353

  Problema: Código assume que opening_round sempre terá 4+ partidas.

  if len(opening_matches) >= 4:
      winner1 = opening_matches[0].get('winner')  # OK
      winner2 = opening_matches[1].get('winner')  # OK
      # ...
      winner3 = opening_matches[2].get('winner')  # Pode dar IndexError se só tiver 2 partidas
      winner4 = opening_matches[3].get('winner')  # Pode dar IndexError

  Impacto: Crash da aplicação se bracket tiver menos de 4 partidas na opening round.

  ---
  5. Validação de Datas Ausente no Frontend

  Localização: /home/vancim/cs2analyzer/web_app/templates/manage_tournaments.html:650-652

  Problema: Não há validação JavaScript para garantir que end_date >= start_date.

  Impacto: Usuário pode criar torneios com datas inválidas (ex: fim antes do início).

  ---
  6. Erros Silenciosos no Processamento de Bracket

  Localização: /home/vancim/cs2analyzer/web_app/main.py:2293-2295

  Problema: Exceções no processamento de partidas são apenas logadas, não reportadas ao usuário.

  except Exception as e:
      print(f"Erro ao processar partida: {e}")
      continue

  Impacto: Bracket pode ficar inconsistente sem o usuário saber o motivo. Partidas podem não avançar e o sistema não indica o erro.

  ---
  🟡 PROBLEMAS MODERADOS (Baixa Prioridade)

  7. Formatação de Datas Inconsistente

  Localização: /home/vancim/cs2analyzer/web_app/templates/manage_tournaments.html:561-562

  Problema: Uso de toLocaleDateString('pt-BR') sem opções pode gerar formatos diferentes em browsers diferentes.

  const startDate = tournament.start_date ? new Date(tournament.start_date).toLocaleDateString('pt-BR') : 'N/A';

  Impacto: Interface pode mostrar datas em formatos diferentes dependendo do browser/OS.

  Sugestão: Especificar opções do formato:
  .toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

  ---
  8. Falta Validação de Tipos no Backend

  Localização: Endpoints POST/PUT de torneios

  Problema: Backend aceita qualquer tipo de dado sem validar:
  - prize_pool poderia ser string não-numérica
  - team_ids poderia não ser array
  - Datas em formato inválido

  Impacto: Dados inconsistentes no JSON, problemas ao renderizar no frontend.

  Sugestão: Usar Pydantic models ou validação manual.

  ---
  9. Lógica de Quarters Sobrescreve Dados

  Localização: /home/vancim/cs2analyzer/web_app/main.py:2347-2350

  Problema: Se quarters[0] já existe, ele é sobrescrito sem preservar outros campos (como winner, loser, score).

  if winner1 and winner2:
      quarters[0]['team1_id'] = winner1
      quarters[0]['team2_id'] = winner2
      quarters[0]['status'] = 'pending'
      # Outros campos como 'winner', 'loser' são perdidos

  Impacto: Resultados já processados podem ser perdidos se a função for executada novamente.

  ---
  10. Frontend: Timezone Inconsistency

  Localização: /home/vancim/cs2analyzer/web_app/templates/tournament.html:1221-1222

  Problema: Mesmo com correção de T00:00:00, ainda pode haver problemas se o servidor estiver em timezone diferente do cliente.

  Impacto: Datas podem aparecer diferentes para usuários em fusos horários diferentes.

  ---
  📊 RESUMO

  | Severidade  | Quantidade | Descrição                                      |
  |-------------|------------|------------------------------------------------|
  | 🔴 Crítica  | 3          | Perda de dados, race conditions, lógica frágil |
  | 🟠 Grave    | 3          | Crashes potenciais, validações ausentes        |
  | 🟡 Moderada | 4          | Inconsistências, falta de validação            |
  | TOTAL       | 10         | Problemas identificados                        |

  ---
  ✅ PONTOS POSITIVOS

  1. ✅ Sistema tem fallback quando torneio não existe no JSON
  2. ✅ Validação de bracket no frontend funciona bem para o caso de 8 times
  3. ✅ Tratamento de exceções genérico existe (mesmo que silencioso)
  4. ✅ Slug generation é robusto e trata caracteres especiais
  5. ✅ Confirmação antes de deletar torneio

  ---
  🔧 RECOMENDAÇÕES GERAIS

  1. Implementar locking de arquivo para operações em tournaments.json
  2. Adicionar Pydantic models para validação de dados no backend
  3. Melhorar identificação de times - exigir maioria dos jogadores, não apenas 1
  4. Adicionar testes unitários para lógica de bracket
  5. Implementar logging estruturado (não apenas print)
  6. Adicionar endpoint de validação que verifica integridade do bracket
  7. Frontend: Adicionar validações de formulário antes de enviar ao backend
  8. Considerar usar banco de dados em vez de JSON para evitar race conditions

● Auditoria completa!

  Identifiquei 10 problemas de lógica no sistema de torneios, organizados por severidade:

  🔴 Críticos (3 problemas):

  1. Perda de dados ao atualizar torneio - campos como prize_pool, bracket são deletados
  2. Race condition no salvamento do JSON - requisições simultâneas podem sobrescrever dados
  3. Identificação de times frágil - 1 jogador coincidente já considera como o time inteiro

  🟠 Graves (3 problemas):

  4. Array bounds não verificado - crash se bracket tiver menos de 4 partidas
  5. Sem validação de datas no frontend - permite data fim antes da data início
  6. Erros silenciosos - bracket fica inconsistente sem feedback ao usuário

  🟡 Moderados (4 problemas):

  7. Formatação de datas inconsistente entre browsers
  8. Backend aceita qualquer tipo de dado sem validar
  9. Atualização de quarters sobrescreve dados existentes
  10. Inconsistência de timezone entre servidor e cliente

  Principais recomendações:
  - Implementar locking de arquivo para tournaments.json
  - Adicionar Pydantic models para validação
  - Melhorar lógica de identificação de times (exigir maioria dos jogadores)
  - Adicionar validações de formulário no frontend
  - Considerar migrar de JSON para banco de dados

  O relatório completo está acima com localizações exatas de código, impactos e sugestões de correção.
