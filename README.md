# CS2 Analyzer

<div align="center">

**Plataforma profissional de análise de demos Counter-Strike 2 com interface inspirada no HLTV**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Go](https://img.shields.io/badge/Go-1.19+-00ADD8.svg)](https://golang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Recursos](#-recursos) • [Instalação](#-instalação-rápida) • [Documentação](#-documentação) • [Tecnologias](#-tecnologias)

</div>

---

## Visão Geral

CS2 Analyzer é uma aplicação web completa para análise profissional de demos do Counter-Strike 2. Desenvolvida com FastAPI e interface moderna inspirada no HLTV, oferece análise detalhada de partidas, estatísticas de jogadores, gerenciamento de times e sistema completo de torneios com brackets.

### Demonstração

- **Dashboard**: Visão geral com últimas demos analisadas e estatísticas
- **Análise de Demos**: Upload e processamento automático de arquivos .dem
- **Perfil de Jogadores**: Estatísticas detalhadas, histórico de partidas, gráficos de performance
- **Gestão de Times**: Cadastro de equipes, logos, rosters com jogadores profissionais
- **Sistema de Torneios**: Criação de competições, brackets interativos, acompanhamento de resultados
- **Estatísticas Avançadas**: K/D, ADR, KAST, HS%, Win Rate por mapa e muito mais

---

## Recursos

### Análise de Demos
- Upload de demos CS2 (.dem) via interface web
- Processamento automático com parser demoinfocs-golang
- Extração completa de eventos: kills, deaths, dano, rounds, bombas
- Exportação em CSV e JSON
- Suporte a múltiplos schemas de dados

### Estatísticas de Jogadores
- Perfil individual com foto, nome, país, idade, time
- Histórico completo de partidas com filtros
- Métricas: K/D, ADR, HS%, KAST, Rating, Clutches
- Gráficos de performance ao longo do tempo
- Comparação entre jogadores
- Top jogadores do sistema

### Gestão de Times
- Cadastro de times com logo, tag, país, redes sociais
- Roster completo com jogadores ativos
- Histórico de partidas por time
- Estatísticas consolidadas
- Rankings de times

### Sistema de Torneios
- Criação de torneios com nome, data, prêmio, formato
- Bracket interativo de eliminação simples
- Gerenciamento de times participantes
- Placar de partidas (BO1, BO3, BO5)
- Acompanhamento em tempo real
- Histórico de torneios

### Interface Profissional
- Design inspirado no HLTV
- Tema dark com paleta azul/laranja
- Cards responsivos com hover effects
- Bandeiras de países
- Navegação intuitiva
- Animações suaves

---

## Instalação Rápida

### Desenvolvimento

```bash
# Clone o repositório
git clone <url-do-repositorio> cs2analyzer
cd cs2analyzer

# Crie o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou .\\venv\\Scripts\\activate  # Windows

# Instale dependências
pip install --upgrade pip
pip install -r requirements.txt

# Crie estrutura de pastas
mkdir -p demo_analysis web_app/static/team_logos logs
echo "[]" > teams.json
echo "[]" > tournaments.json

# Compile o parser CS2 (veja DEPLOY.md para detalhes)
# ... instalação do demoinfocs-golang

# Inicie o servidor
uvicorn web_app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000**

### Produção

Para instalação completa em ambiente de produção com Nginx, SSL e Systemd, consulte [DEPLOY.md](DEPLOY.md).

---

## Documentação

- **[DEPLOY.md](DEPLOY.md)** - Manual completo de deployment
  - Requisitos do sistema
  - Instalação para desenvolvimento e produção
  - Configuração de Nginx e SSL
  - Serviço Systemd
  - Backup e manutenção
  - Troubleshooting

- **[CAPTACAO_DEMOS.md](CAPTACAO_DEMOS.md)** - Guia de captação de demos
  - Upload manual via web
  - Monitor automático de pasta
  - Integração com servidor GOTV
  - Upload via FTP/SFTP
  - Compartilhamento de rede (LAN Party)
  - API REST para integração
  - Combinação de métodos

- **[MANUAL_USUARIO.md](MANUAL_USUARIO.md)** - Manual do usuário
  - Introdução ao sistema
  - Upload e análise de demos
  - Navegação no dashboard
  - Gerenciamento de times
  - Criação de torneios
  - Visualização de estatísticas
  - FAQ e dicas

---

## Estrutura do Projeto

```
cs2analyzer/
├── web_app/                          # Aplicação web FastAPI
│   ├── main.py                       # Backend principal (API endpoints)
│   ├── templates/                    # Templates Jinja2
│   │   ├── home.html                 # Dashboard principal
│   │   ├── players.html              # Lista de jogadores
│   │   ├── player_profile.html       # Perfil de jogador
│   │   ├── teams.html                # Lista de times
│   │   ├── tournament.html           # Página de torneio
│   │   └── ...
│   └── static/                       # Arquivos estáticos
│       ├── team_logos/               # Logos dos times
│       └── player_photos/            # Fotos dos jogadores
├── demo_analysis/                    # Demos e análises
│   └── [nome_demo]/
│       ├── demo.dem                  # Arquivo original
│       ├── match_info.json           # Info da partida
│       ├── kills.csv                 # Dados de kills
│       ├── damage.csv                # Dados de dano
│       └── player_stats.csv          # Estatísticas
├── teams.json                        # Banco de dados de times
├── tournaments.json                  # Banco de dados de torneios
├── cs2-parser                        # Parser demoinfocs-golang
├── monitor.py                        # Monitor automático de demos
├── requirements.txt                  # Dependências Python
├── DEPLOY.md                         # Manual de deployment
├── CAPTACAO_DEMOS.md                 # Guia de captação de demos
├── MANUAL_USUARIO.md                 # Manual do usuário
└── README.md                         # Este arquivo
```

---

## Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **Pandas** - Análise e manipulação de dados
- **Python-Multipart** - Upload de arquivos
- **Aiofiles** - I/O assíncrono de arquivos

### Parser
- **demoinfocs-golang** - Parser de demos CS2 em Go
- Extração completa de eventos, jogadores, rounds
- Suporte a formato CS2 atualizado

### Frontend
- **Jinja2** - Template engine
- **HTML5/CSS3** - Interface moderna
- **JavaScript** - Interatividade
- **Chart.js** - Gráficos de estatísticas (futuro)

### Infraestrutura
- **Nginx** - Reverse proxy e servir arquivos estáticos
- **Systemd** - Gerenciamento de serviço
- **Let's Encrypt** - Certificados SSL/TLS
- **UFW/Fail2ban** - Segurança

---

## Arquitetura

### Fluxo de Análise de Demo

1. **Upload**: Usuário faz upload de .dem via interface web
2. **Validação**: Sistema verifica formato e tamanho do arquivo
3. **Processamento**: Parser demoinfocs-golang extrai todos os eventos
4. **Agregação**: Dados são consolidados e estatísticas calculadas
5. **Armazenamento**: CSV, JSON salvos em `demo_analysis/[nome]/`
6. **Exibição**: Interface apresenta resultados com gráficos e tabelas

### Schemas de Dados

O sistema suporta dois formatos de `match_info.json`:

**Schema A (Header-based):**
```json
{
  "header": {
    "map_name": "de_dust2"
  },
  "extraction_time": "2025-10-18 14:30:00"
}
```

**Schema B (Flat):**
```json
{
  "map": "dust2",
  "date": "2025-10-18"
}
```

### API Endpoints

#### Páginas
- `GET /` - Dashboard principal
- `GET /players` - Lista de jogadores
- `GET /player/{steamid}` - Perfil de jogador
- `GET /pro/{steamid}` - Perfil de pro player
- `GET /teams` - Lista de times
- `GET /tournament/{id}` - Página de torneio

#### API REST
- `POST /upload` - Upload de demo
- `GET /api/matches` - Lista de partidas
- `GET /api/players` - Lista de jogadores
- `POST /api/teams` - Criar/atualizar time
- `POST /api/tournaments` - Criar torneio
- `PUT /api/tournament/{id}/match` - Atualizar placar

---

## Recursos Avançados

### Sistema de Torneios

Suporta criação de brackets de eliminação simples:
- 4, 8, 16 ou 32 times
- BO1, BO3, BO5
- Avanço automático de vencedores
- Interface drag-and-drop para criação

### Análise de Performance

Estatísticas calculadas:
- **K/D Ratio**: Kills / Deaths
- **ADR**: Average Damage per Round
- **HS%**: Porcentagem de headshots
- **KAST**: Kill, Assist, Survived, Traded
- **Rating**: Cálculo inspirado no HLTV
- **Clutch**: Situações 1vX vencidas

### Integração de Dados

- Importação automática de dados de demos
- Associação de jogadores a times
- Vínculo de partidas a torneios
- Histórico completo mantido

---

## Requisitos do Sistema

### Hardware Mínimo
- CPU: 4 cores (recomendado: 8+)
- RAM: 8GB (recomendado: 16GB+)
- Armazenamento: 50GB+ (demos ~100-500MB cada)
- Rede: 100Mbps+

### Software
- Sistema Operacional: Linux (Ubuntu 20.04+, Debian 11+) ou Windows 10/11
- Python: 3.9+
- Go: 1.19+ (para compilar parser)
- Node.js: 16+ (opcional)

### Dependências Python
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pandas==2.1.3
jinja2==3.1.2
aiofiles==23.2.1
```

---

## Uso

### Upload de Demo

1. Acesse a interface web
2. Clique em "Upload Demo" ou "Analisar Nova Demo"
3. Selecione arquivo .dem (até 500MB)
4. Aguarde processamento (30s - 5min)
5. Visualize resultados automaticamente

### Cadastro de Time

1. Vá para "Times"
2. Clique em "Criar Novo Time"
3. Preencha: Nome, Tag, País, Logo
4. Adicione jogadores ao roster
5. Salve

### Criação de Torneio

1. Vá para "Torneios"
2. Clique em "Criar Torneio"
3. Preencha: Nome, Data, Prêmio, Formato
4. Selecione times participantes (4/8/16/32)
5. Sistema gera bracket automaticamente
6. Atualize placares conforme partidas ocorrem

---

## Performance e Otimização

### Produção

- Use múltiplos workers Uvicorn (4 = CPU cores)
- Configure cache de arquivos estáticos no Nginx
- Ative gzip compression
- Use SSL/TLS com HTTP/2

### Backup

Execute script automático diário:
```bash
/home/cs2analyzer/backup.sh
```

Mantém últimos 7 dias de:
- Demos e análises
- teams.json / tournaments.json
- Logos e fotos

### Limpeza

Script semanal remove demos antigas:
```bash
/home/cs2analyzer/cleanup.sh
```

---

## Troubleshooting

### Servidor não inicia
```bash
sudo journalctl -u cs2analyzer -n 100
sudo lsof -ti:8000 | xargs kill -9
sudo systemctl restart cs2analyzer
```

### Parser falha
```bash
chmod +x cs2-parser
./cs2-parser -demo /path/to/demo.dem
```

### Upload falha
- Verifique `client_max_body_size` no Nginx
- Confirme permissões em `demo_analysis/`
- Veja logs: `tail -f logs/app.log`

Consulte [DEPLOY.md - Troubleshooting](DEPLOY.md#troubleshooting) para mais detalhes.

---

## Roadmap

### Próximas Funcionalidades

- [ ] Sistema de usuários e autenticação
- [ ] Gráficos interativos com Chart.js/D3.js
- [ ] Heatmaps de posicionamento
- [ ] Análise tática: execuções, retakes, economy
- [ ] Comparação lado-a-lado de jogadores
- [ ] Exportação em PDF de relatórios
- [ ] API pública com documentação
- [ ] Integração com APIs de terceiros (Steam, HLTV)
- [ ] Sistema de ranking ELO
- [ ] Notificações em tempo real

### Melhorias Planejadas

- [ ] Cache de estatísticas calculadas
- [ ] Background jobs com Celery
- [ ] Banco de dados relacional (PostgreSQL)
- [ ] Testes automatizados (pytest)
- [ ] CI/CD pipeline
- [ ] Docker containerization
- [ ] WebSocket para updates em tempo real
- [ ] Mobile-responsive aprimorado

---

## Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFuncionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### Diretrizes

- Siga PEP 8 para código Python
- Adicione docstrings em funções
- Mantenha compatibilidade com Python 3.9+
- Teste localmente antes de submeter PR

---

## Segurança

### Boas Práticas

- Variáveis sensíveis em `.env` (nunca commitar)
- SECRET_KEY gerado com `openssl rand -hex 32`
- Validação de uploads (tipo, tamanho)
- CORS configurado adequadamente
- Rate limiting em produção
- SSL/TLS obrigatório em produção
- Firewall configurado (UFW)
- Fail2ban para proteção contra brute force

### Reportar Vulnerabilidades

Se encontrar uma vulnerabilidade de segurança, por favor NÃO abra uma issue pública. Entre em contato diretamente com a equipe de desenvolvimento.

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## Suporte

### Documentação
- [DEPLOY.md](DEPLOY.md) - Guia completo de instalação
- [CAPTACAO_DEMOS.md](CAPTACAO_DEMOS.md) - Métodos de captação de demos
- [MANUAL_USUARIO.md](MANUAL_USUARIO.md) - Manual do usuário

### Comunidade
- Abra uma [Issue](../../issues) para bugs ou sugestões
- Consulte [FAQ no Manual do Usuário](MANUAL_USUARIO.md#-faq)

### Contato
- Email: suporte@cs2analyzer.com
- Discord: [Link do servidor]
- Twitter: [@cs2analyzer]

---

## Agradecimentos

- **markus-wa/demoinfocs-golang** - Parser de demos CS2
- **HLTV.org** - Inspiração de design e métricas
- **FastAPI** - Framework web incrível
- **Comunidade CS** - Feedback e testes

---

<div align="center">

**Desenvolvido com dedicação para a comunidade Counter-Strike**

[⬆ Voltar ao topo](#cs2-analyzer)

</div>
