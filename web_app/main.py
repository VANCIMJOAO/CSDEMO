from fastapi import FastAPI, UploadFile, Form, Request, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import subprocess
import os
import pandas as pd
import json
import sys
import time
from datetime import datetime
import fcntl
from contextlib import contextmanager

# Importar o monitor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from monitor import DemoMonitor

# === CONFIGURAÇÃO BASE ===
BASE_DIR = Path(__file__).resolve().parent.parent
DEMOS_DIR = BASE_DIR / "demos"
ANALYSIS_DIR = BASE_DIR / "demo_analysis"

DEMOS_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)

# === FILE LOCKING UTILITIES ===
@contextmanager
def locked_tournaments_file(mode='r'):
    """
    Context manager para ler/escrever tournaments.json com file locking.
    Previne race conditions em operações concorrentes.

    Args:
        mode: 'r' para leitura, 'r+' para leitura/escrita

    Yields:
        tuple: (file_handle, tournaments_list)

    Example:
        # Leitura
        with locked_tournaments_file('r') as (f, tournaments):
            # use tournaments list

        # Escrita
        with locked_tournaments_file('r+') as (f, tournaments):
            tournaments.append(new_tournament)
            f.seek(0)
            json.dump(tournaments, f, indent=2, ensure_ascii=False)
            f.truncate()
    """
    tournaments_file = BASE_DIR / "tournaments.json"

    # Criar arquivo vazio se não existir
    if not tournaments_file.exists():
        with open(tournaments_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

    # Abrir arquivo com lock
    file_handle = open(tournaments_file, mode, encoding='utf-8')

    try:
        # Adquirir lock exclusivo (LOCK_EX) para escrita ou compartilhado (LOCK_SH) para leitura
        lock_type = fcntl.LOCK_EX if '+' in mode or 'w' in mode else fcntl.LOCK_SH
        fcntl.flock(file_handle.fileno(), lock_type)

        # Ler dados
        file_handle.seek(0)
        content = file_handle.read()
        tournaments = json.loads(content) if content.strip() else []

        yield file_handle, tournaments

    finally:
        # Liberar lock e fechar arquivo
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        file_handle.close()

app = FastAPI(title="CS2 Demo Analyzer Web - LAN Party Edition")

app.mount("/static", StaticFiles(directory=BASE_DIR / "web_app" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "web_app" / "templates")

# === HELPER FUNCTIONS ===

def calculate_overtime_info(analysis_path: Path, team2_score: int, team3_score: int):
    """
    Calcula informações detalhadas sobre overtime.

    Retorna:
        dict com:
        - has_overtime: bool
        - overtime_rounds: int (total de rounds no OT)
        - team2_ot_score: int
        - team3_ot_score: int
        - team2_regulation: dict com {ct, t}
        - team3_regulation: dict com {ct, t}
    """
    result = {
        'has_overtime': False,
        'overtime_rounds': 0,
        'team2_ot_score': 0,
        'team3_ot_score': 0,
        'team2_regulation': {'ct': 0, 't': 0},
        'team3_regulation': {'ct': 0, 't': 0},
        'num_overtimes': 0
    }

    # Verificar se foi para OT (mais de 30 rounds ou qualquer score > 16)
    total_rounds = team2_score + team3_score
    if total_rounds <= 30 and team2_score <= 16 and team3_score <= 16:
        return result

    result['has_overtime'] = True

    # Ler rounds_end.csv para calcular detalhes
    rounds_end_file = analysis_path / "rounds_end.csv"
    if not rounds_end_file.exists():
        return result

    try:
        df = pd.read_csv(rounds_end_file)
        df = df[df['winner'].notna() & (df['winner'] != '')]

        # Determinar qual time começou como CT analisando os primeiros rounds
        # Assumir que Team 2 começou como CT (pode ser refinado depois)
        team2_started_as_ct = True  # Padrão

        team2_reg_score = 0
        team3_reg_score = 0
        team2_ot = 0
        team3_ot = 0

        for idx, row in df.iterrows():
            round_num = int(row['total_rounds_played'])
            winner_side = row['winner']

            if round_num <= 12:
                # Primeiro half
                if team2_started_as_ct:
                    if winner_side == 'CT':
                        team2_reg_score += 1
                        result['team2_regulation']['ct'] += 1
                    else:
                        team3_reg_score += 1
                        result['team3_regulation']['t'] += 1
                else:
                    if winner_side == 'T':
                        team2_reg_score += 1
                        result['team2_regulation']['t'] += 1
                    else:
                        team3_reg_score += 1
                        result['team3_regulation']['ct'] += 1

            elif round_num <= 24:
                # Segundo half (lados trocados)
                if team2_started_as_ct:
                    if winner_side == 'T':
                        team2_reg_score += 1
                        result['team2_regulation']['t'] += 1
                    else:
                        team3_reg_score += 1
                        result['team3_regulation']['ct'] += 1
                else:
                    if winner_side == 'CT':
                        team2_reg_score += 1
                        result['team2_regulation']['ct'] += 1
                    else:
                        team3_reg_score += 1
                        result['team3_regulation']['t'] += 1
            else:
                # Overtime
                ot_round_num = round_num - 24
                ot_number = ((ot_round_num - 1) // 6) + 1
                round_in_ot = ((ot_round_num - 1) % 6) + 1

                # Team começa no lado OPOSTO no OT
                team2_is_t_in_ot = not team2_started_as_ct

                # Determinar lado atual
                if ot_number % 2 == 1:  # OT ímpar
                    if round_in_ot <= 3:
                        team2_is_t = team2_is_t_in_ot
                    else:
                        team2_is_t = not team2_is_t_in_ot
                else:  # OT par
                    if round_in_ot <= 3:
                        team2_is_t = not team2_is_t_in_ot
                    else:
                        team2_is_t = team2_is_t_in_ot

                # Atribuir vitória
                if team2_is_t:
                    if winner_side == 'T':
                        team2_ot += 1
                    else:
                        team3_ot += 1
                else:
                    if winner_side == 'CT':
                        team2_ot += 1
                    else:
                        team3_ot += 1

        result['team2_ot_score'] = team2_ot
        result['team3_ot_score'] = team3_ot
        result['overtime_rounds'] = team2_ot + team3_ot
        result['num_overtimes'] = (result['overtime_rounds'] + 5) // 6  # Arredondar para cima

    except Exception as e:
        print(f"Erro ao calcular OT: {e}")

    return result

# === INICIALIZAR MONITOR ===
monitor = DemoMonitor(DEMOS_DIR, ANALYSIS_DIR, interval=30)

@app.on_event("startup")
async def startup_event():
    """Inicia o monitor automático ao subir o servidor"""
    print("\n🚀 Iniciando monitor automático de demos...")
    monitor.start()
    print(f"✅ Monitor ativo - Verificando pasta a cada {monitor.interval} segundos\n")

# === ROTAS ===

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Página inicial com resumo (modo LAN Party)"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/upload-page", response_class=HTMLResponse)
def upload_page(request: Request):
    """Página de upload manual (modo antigo)"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_demo(request: Request, file: UploadFile):
    # Salvar demo enviada
    demo_path = DEMOS_DIR / file.filename
    with open(demo_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Rodar o analisador usando o Python do ambiente virtual
    venv_python = BASE_DIR / "venv" / "bin" / "python"
    command = f"{venv_python} {BASE_DIR}/analyzer.py {demo_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=BASE_DIR)

    # Tentar carregar estatísticas dos jogadores se a análise foi bem-sucedida
    player_stats = None
    demo_name = file.filename.replace('.dem', '')
    stats_file = ANALYSIS_DIR / demo_name / "player_stats.csv"
    
    if stats_file.exists() and result.returncode == 0:
        try:
            import pandas as pd
            df = pd.read_csv(stats_file)
            player_stats = df.to_dict('records')
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")

    # Mostrar resultado na tela
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": f"✅ Análise concluída de {file.filename}",
        "log": result.stdout,
        "error": result.stderr,
        "player_stats": player_stats,
        "demo_name": demo_name
    })

@app.get("/download/{demo_name}")
def download_result(demo_name: str):
    file_path = ANALYSIS_DIR / demo_name / "player_stats.csv"
    if file_path.exists():
        return FileResponse(file_path, filename=f"{demo_name}_player_stats.csv")
    return {"error": "Arquivo não encontrado"}

@app.get("/dashboard/{demo_name}", response_class=HTMLResponse)
def dashboard(request: Request, demo_name: str):
    """Dashboard com gráficos interativos"""
    analysis_dir = ANALYSIS_DIR / demo_name
    print(f"🔍 Dashboard request for: {demo_name}")
    print(f"📁 Analysis dir: {analysis_dir}")
    print(f"✅ Analysis dir exists: {analysis_dir.exists()}")
    
    if not analysis_dir.exists():
        print(f"❌ Analysis dir not found for {demo_name}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Análise para {demo_name} não encontrada"
        })
    
    try:
        # Carregar dados
        player_stats = pd.read_csv(analysis_dir / "player_stats.csv")
        kills_df = pd.read_csv(analysis_dir / "kills.csv")
        damage_df = pd.read_csv(analysis_dir / "damage.csv")

        # Inicializar placares com valores padrão
        score_team2 = 0
        score_team3 = 0

        # Ler match_info primeiro para obter placares
        match_info_file = analysis_dir / "match_info.json"
        if match_info_file.exists():
            with open(match_info_file, 'r', encoding='utf-8') as f:
                match_info_temp = json.load(f)
                score_info = match_info_temp.get('score', {})
                score_team2 = score_info.get('team2_score', 0)
                score_team3 = score_info.get('team3_score', 0)

        # Criar aliases para compatibilidade com código antigo
        # NOTA: Estes valores serão usados para cálculos internos
        score_t = score_team2
        score_ct = score_team3

        # Carregar dados de rounds se existir
        rounds_file = analysis_dir / "rounds_detailed.csv"
        rounds_end_file = analysis_dir / "rounds_end.csv"

        if rounds_file.exists():
            round_data = pd.read_csv(rounds_file).to_dict('records')

            # Enriquecer com dados do rounds_end.csv
            if rounds_end_file.exists():
                rounds_end_df = pd.read_csv(rounds_end_file)

                # Determinar qual lado cada team começou
                # Contar vitórias por lado em cada half
                first_half_rounds = 12  # CS2 padrão
                ct_wins_first = len(rounds_end_df[(rounds_end_df['total_rounds_played'] <= first_half_rounds) & (rounds_end_df['winner'] == 'CT')])
                t_wins_first = len(rounds_end_df[(rounds_end_df['total_rounds_played'] <= first_half_rounds) & (rounds_end_df['winner'] == 'T')])
                ct_wins_second = len(rounds_end_df[(rounds_end_df['total_rounds_played'] > first_half_rounds) & (rounds_end_df['winner'] == 'CT')])
                t_wins_second = len(rounds_end_df[(rounds_end_df['total_rounds_played'] > first_half_rounds) & (rounds_end_df['winner'] == 'T')])

                # Team2 começou como CT se: ct_first + t_second = team2_score
                # Vamos usar o score final do match_info se disponível
                team2_score_final = score_t  # Do match_info, team2_score
                team3_score_final = score_ct  # Do match_info, team3_score

                # Verificar cenários
                scenario1_team2 = ct_wins_first + t_wins_second  # Team2 começou como CT
                scenario2_team2 = t_wins_first + ct_wins_second  # Team2 começou como T

                if scenario1_team2 == team2_score_final:
                    # Team2 começou como CT
                    team2_started_as_ct = True
                else:
                    # Team2 começou como T
                    team2_started_as_ct = False

                # Calcular placar acumulado POR TIME (não por lado)
                team2_score_accumulated = 0
                team3_score_accumulated = 0

                for round_item in round_data:
                    round_num = round_item['round']
                    # Encontrar o round correspondente no rounds_end usando total_rounds_played
                    # rounds_detailed round 0 = rounds_end total_rounds_played 1
                    round_end_row = rounds_end_df[rounds_end_df['total_rounds_played'] == round_num + 1]
                    if not round_end_row.empty:
                        round_item['reason'] = round_end_row.iloc[0]['reason']
                        side_winner = round_end_row.iloc[0]['winner']  # CT ou T
                        round_item['winner'] = side_winner

                        # Determinar qual TEAM ganhou baseado no lado e no half
                        is_first_half = round_num < first_half_rounds

                        if team2_started_as_ct:
                            # Team2 é CT no 1º half, T no 2º half
                            if is_first_half:
                                team_winner = 'team2' if side_winner == 'CT' else 'team3'
                            else:
                                team_winner = 'team2' if side_winner == 'T' else 'team3'
                        else:
                            # Team2 é T no 1º half, CT no 2º half
                            if is_first_half:
                                team_winner = 'team2' if side_winner == 'T' else 'team3'
                            else:
                                team_winner = 'team2' if side_winner == 'CT' else 'team3'

                        # Atualizar placar acumulado por TEAM
                        if team_winner == 'team2':
                            team2_score_accumulated += 1
                        else:
                            team3_score_accumulated += 1
                    else:
                        # Para rounds sem dados em rounds_end, inferir vencedor pelos kills
                        # Contar kills por time atacante neste round
                        if not kills_df.empty and 'total_rounds_played' in kills_df.columns:
                            round_kills = kills_df[kills_df['total_rounds_played'] == round_num]
                            ct_kills_count = len(round_kills[round_kills['attacker_team_name'] == 'CT']) if 'attacker_team_name' in round_kills.columns else 0
                            t_kills_count = len(round_kills[round_kills['attacker_team_name'] == 'T']) if 'attacker_team_name' in round_kills.columns else 0
                        else:
                            ct_kills_count = 0
                            t_kills_count = 0

                        if ct_kills_count > t_kills_count:
                            round_item['reason'] = 't_killed'
                            side_winner = 'CT'
                            round_item['winner'] = 'CT'
                        elif t_kills_count > ct_kills_count:
                            round_item['reason'] = 'ct_killed'
                            side_winner = 'T'
                            round_item['winner'] = 'T'
                        else:
                            round_item['reason'] = 'unknown'
                            round_item['winner'] = 'unknown'
                            side_winner = None

                        if side_winner:
                            is_first_half = round_num < first_half_rounds
                            if team2_started_as_ct:
                                if is_first_half:
                                    team_winner = 'team2' if side_winner == 'CT' else 'team3'
                                else:
                                    team_winner = 'team2' if side_winner == 'T' else 'team3'
                            else:
                                if is_first_half:
                                    team_winner = 'team2' if side_winner == 'T' else 'team3'
                                else:
                                    team_winner = 'team2' if side_winner == 'CT' else 'team3'

                            if team_winner == 'team2':
                                team2_score_accumulated += 1
                            else:
                                team3_score_accumulated += 1

                    # Armazenar placar acumulado por TEAM (será invertido no template se ORBITAL ROXA)
                    round_item['score_team2'] = team2_score_accumulated
                    round_item['score_team3'] = team3_score_accumulated

            # Enriquecer com kills do round
            if not kills_df.empty:
                for round_item in round_data:
                    round_num = round_item['round']
                    # Pegar kills deste round (kills.csv usa total_rounds_played que corresponde ao round)
                    # rounds_detailed round 0 = kills total_rounds_played 0
                    round_kills = kills_df[kills_df['total_rounds_played'] == round_num]

                    kills_list = []
                    for _, kill in round_kills.iterrows():
                        # Ignorar kills do world (suicídio, queda, etc)
                        if pd.notna(kill.get('attacker_name')) and kill.get('attacker_name') != '':
                            kill_data = {
                                'attacker': str(kill.get('attacker_name', '')),
                                'victim': str(kill.get('user_name', '')),
                                'weapon': str(kill.get('weapon', 'unknown')),
                                'headshot': bool(kill.get('headshot', False)),
                                'attacker_team': str(kill.get('attacker_team_name', '')),
                                'victim_team': str(kill.get('user_team_name', ''))
                            }
                            # Adicionar assister se existir
                            if pd.notna(kill.get('assister_name')) and kill.get('assister_name') != '':
                                kill_data['assister'] = str(kill.get('assister_name', ''))

                            kills_list.append(kill_data)

                    round_item['kills'] = kills_list
        else:
            round_data = []

        # Preparar dados melhorados
        
        # Calcular dano por round
        damage_per_round = []
        for r in round_data:
            round_num = r['round']
            if not damage_df.empty and 'total_rounds_played' in damage_df.columns:
                round_damage = damage_df[damage_df['total_rounds_played'] == round_num]
                damage_sum = round_damage['dmg_health'].sum() if 'dmg_health' in round_damage.columns else 0
                damage_per_round.append(int(damage_sum))  # Converter para int nativo
            else:
                damage_per_round.append(0)
        
        # Preparar dados para heatmap
        heatmap_data = []
        if not kills_df.empty and 'user_X' in kills_df.columns and 'user_Y' in kills_df.columns:
            valid_positions = kills_df[
                (kills_df['user_X'].notna()) & 
                (kills_df['user_Y'].notna()) &
                (kills_df['user_X'] != 0) &
                (kills_df['user_Y'] != 0)
            ]
            
            heatmap_data = [
                {
                    'x': float(row['user_X']),
                    'y': float(row['user_Y']),
                    'team': str(row.get('user_team_name', 'Unknown'))
                }
                for _, row in valid_positions.iterrows()
            ]
        
        # Calcular ct_kills, t_kills e headshots por round a partir dos kills
        ct_kills_per_round = []
        t_kills_per_round = []
        headshots_per_round = []

        for r in round_data:
            round_num = r['round']
            if not kills_df.empty and 'total_rounds_played' in kills_df.columns:
                round_kills = kills_df[kills_df['total_rounds_played'] == round_num]

                # Contar kills por time atacante
                ct_kills = len(round_kills[round_kills['attacker_team_name'] == 'CT']) if 'attacker_team_name' in round_kills.columns else 0
                t_kills = len(round_kills[round_kills['attacker_team_name'] == 'T']) if 'attacker_team_name' in round_kills.columns else 0
                headshots = int(round_kills['headshot'].sum()) if 'headshot' in round_kills.columns else 0

                ct_kills_per_round.append(ct_kills)
                t_kills_per_round.append(t_kills)
                headshots_per_round.append(headshots)
            else:
                ct_kills_per_round.append(0)
                t_kills_per_round.append(0)
                headshots_per_round.append(0)

        chart_data = {
            "rounds": [int(r['round']) for r in round_data],
            "ct_kills": ct_kills_per_round,
            "t_kills": t_kills_per_round,
            "headshots": headshots_per_round,
            "damage": damage_per_round,
            "player_names": [str(name) for name in player_stats['player']],
            "kd_ratios": [float(kd) for kd in player_stats['kd_ratio']],
            "hs_percentages": [float(hs) for hs in player_stats['hs_percent']],
            "heatmap_data": heatmap_data
        }

        # Debug: Verificar dados dos gráficos
        print(f"📊 Chart Data Debug:")
        print(f"  - Rounds: {len(chart_data['rounds'])} items - {chart_data['rounds'][:5]}...")
        print(f"  - CT Kills: {len(chart_data['ct_kills'])} items - {chart_data['ct_kills'][:5]}...")
        print(f"  - T Kills: {len(chart_data['t_kills'])} items - {chart_data['t_kills'][:5]}...")
        print(f"  - Headshots: {len(chart_data['headshots'])} items - {chart_data['headshots'][:5]}...")
        print(f"  - Damage: {len(chart_data['damage'])} items - {chart_data['damage'][:5]}...")
        print(f"  - Players: {len(chart_data['player_names'])} items - {chart_data['player_names']}")
        print(f"  - K/D: {chart_data['kd_ratios']}")
        print(f"  - HS%: {chart_data['hs_percentages']}")
        
        # Estatísticas gerais
        total_kills = len(kills_df)
        total_hs = int(kills_df['headshot'].sum()) if 'headshot' in kills_df.columns else 0
        hs_percentage = (total_hs / total_kills * 100) if total_kills > 0 else 0
        round_count = len(round_data) if round_data else 0
        
        # Preparar dados dos jogadores - NÃO ordenar ainda, será feito por time
        player_stats_list = player_stats.to_dict('records')

        # Inicializar match_info como dicionário vazio
        match_info = {}

        # Detectar times baseado nas Steam IDs
        team_info = {}
        player_team_info = {}

        # Inicializar mapa
        map_name = "Mapa desconhecido"

        # Ler match_info para obter Steam IDs
        if match_info_file.exists():
            with open(match_info_file, 'r', encoding='utf-8') as f:
                match_info = json.load(f)

            # Extrair nome do mapa (suporta formato novo e antigo)
            if 'map' in match_info:
                # Formato novo: campo 'map' direto
                map_name = match_info['map']
            else:
                # Formato antigo: 'header.map_name'
                header_info = match_info.get('header', {})
                map_name = header_info.get('map_name', 'Mapa desconhecido')

            # Remover o prefixo "de_" se existir e capitalizar
            if map_name.startswith('de_'):
                map_name = map_name[3:].capitalize()
            elif map_name != 'Mapa desconhecido':
                map_name = map_name.capitalize()

            # Carregar rounds_end para calcular halves considerando troca de lado
            rounds_end_file = analysis_dir / "rounds_end.csv"
            team2_first_half = 0
            team2_second_half = 0
            team3_first_half = 0
            team3_second_half = 0
            team2_ot_score = 0
            team3_ot_score = 0
            has_overtime = False

            # Verificar se o match_info já tem os dados de rounds no formato novo
            rounds_info_in_match = match_info.get('rounds', {})
            use_new_format = 'team2_rounds_ct' in rounds_info_in_match and 'team2_rounds_t' in rounds_info_in_match

            # Inicializar variáveis de cenário (serão definidas em cada caso)
            scenario1_team2 = 0
            scenario1_team3 = 0
            team2_started_as_ct = True

            if use_new_format:
                # Formato novo: match_info.json já tem os rounds separados
                team2_ct_total = rounds_info_in_match.get('team2_rounds_ct', 0)
                team2_t_total = rounds_info_in_match.get('team2_rounds_t', 0)
                team3_ct_total = rounds_info_in_match.get('team3_rounds_ct', 0)
                team3_t_total = rounds_info_in_match.get('team3_rounds_t', 0)

                # Determinar quem começou como CT baseado nos totais
                # O 1º half SEMPRE tem 12 rounds totais
                # Se Team2 fez mais rounds como CT do que como T, provavelmente começou como CT
                if team2_ct_total >= team2_t_total:
                    # Team 2 começou como CT
                    team2_started_as_ct = True
                    # Team2 jogou CT no 1º half e T no 2º half
                    team2_first_half = team2_ct_total
                    team2_second_half = team2_t_total
                    # Team3 foi o oposto (T no 1º, CT no 2º)
                    team3_first_half = 12 - team2_first_half  # 1º half sempre soma 12
                    team3_second_half = score_ct - team3_first_half  # Total Team3 - 1º half
                else:
                    # Team 2 começou como T
                    team2_started_as_ct = False
                    team2_first_half = team2_t_total
                    team2_second_half = team2_ct_total
                    team3_first_half = 12 - team2_first_half
                    team3_second_half = score_ct - team3_first_half

                print(f"✅ Usando formato novo do match_info.json")
                print(f"📊 Team 2: 1º half={team2_first_half}, 2º half={team2_second_half}")
                print(f"📊 Team 3: 1º half={team3_first_half}, 2º half={team3_second_half}")

                # Definir variáveis de cenário para uso posterior
                scenario1_team2 = team2_first_half + team2_second_half
                scenario1_team3 = team3_first_half + team3_second_half

            elif rounds_end_file.exists():
                rounds_end_df = pd.read_csv(rounds_end_file)

                # Contar vitórias por side separando regulamentar (1-24) de OT (25+)
                ct_wins_first = len(rounds_end_df[(rounds_end_df['total_rounds_played'] <= 12) & (rounds_end_df['winner'] == 'CT')])
                t_wins_first = len(rounds_end_df[(rounds_end_df['total_rounds_played'] <= 12) & (rounds_end_df['winner'] == 'T')])
                ct_wins_second = len(rounds_end_df[(rounds_end_df['total_rounds_played'] > 12) & (rounds_end_df['total_rounds_played'] <= 24) & (rounds_end_df['winner'] == 'CT')])
                t_wins_second = len(rounds_end_df[(rounds_end_df['total_rounds_played'] > 12) & (rounds_end_df['total_rounds_played'] <= 24) & (rounds_end_df['winner'] == 'T')])

                # Determinar qual team começou em qual side testando os dois cenários
                # Cenário 1: Team 2 começa como CT
                scenario1_team2_reg = ct_wins_first + t_wins_second
                scenario1_team3_reg = t_wins_first + ct_wins_second

                # Cenário 2: Team 2 começa como T
                scenario2_team2_reg = t_wins_first + ct_wins_second
                scenario2_team3_reg = ct_wins_first + t_wins_second

                # Verificar se houve OT
                total_rounds_played = score_t + score_ct
                has_overtime = total_rounds_played > 30

                if has_overtime:
                    # Usar a função calculate_overtime_info
                    ot_info = calculate_overtime_info(analysis_dir, score_t, score_ct)
                    team2_ot_score = ot_info['team2_ot_score']
                    team3_ot_score = ot_info['team3_ot_score']

                    # Verificar qual cenário está correto usando apenas os scores do regulamentar
                    team2_reg_score = score_t - team2_ot_score
                    team3_reg_score = score_ct - team3_ot_score

                    if scenario1_team2_reg == team2_reg_score and scenario1_team3_reg == team3_reg_score:
                        team2_started_as_ct = True
                        team2_first_half = ct_wins_first
                        team2_second_half = t_wins_second
                        team3_first_half = t_wins_first
                        team3_second_half = ct_wins_second
                    else:
                        team2_started_as_ct = False
                        team2_first_half = t_wins_first
                        team2_second_half = ct_wins_second
                        team3_first_half = ct_wins_first
                        team3_second_half = t_wins_second
                else:
                    # Sem OT, verificar com scores totais
                    if scenario1_team2_reg == score_t and scenario1_team3_reg == score_ct:
                        team2_started_as_ct = True
                        team2_first_half = ct_wins_first
                        team2_second_half = t_wins_second
                        team3_first_half = t_wins_first
                        team3_second_half = ct_wins_second
                    else:
                        team2_started_as_ct = False
                        team2_first_half = t_wins_first
                        team2_second_half = ct_wins_second
                        team3_first_half = ct_wins_first
                        team3_second_half = t_wins_second

                print(f"📊 Team 2: 1º half={team2_first_half}, 2º half={team2_second_half}, OT={team2_ot_score}")
                print(f"📊 Team 3: 1º half={team3_first_half}, 2º half={team3_second_half}, OT={team3_ot_score}")

                # Definir variáveis de cenário para uso posterior
                scenario1_team2 = team2_first_half + team2_second_half
                scenario1_team3 = team3_first_half + team3_second_half

            # Agrupar Steam IDs por time
            ct_steamids = []
            t_steamids = []

            for player in match_info.get('players', []):
                if player.get('team_number') == 3:  # CT
                    ct_steamids.append(player['steamid'])
                elif player.get('team_number') == 2:  # T
                    t_steamids.append(player['steamid'])
            
            # Detectar times
            ct_team = detect_team_by_steamids(ct_steamids)
            t_team = detect_team_by_steamids(t_steamids)
            
            # LÓGICA DE ATRIBUIÇÃO DE TIMES PADRONIZADA
            print(f"🔍 Times detectados: CT={ct_team['name'] if ct_team else 'None'}, T={t_team['name'] if t_team else 'None'}")

            # Se encontrou ORBITAL ROXA no time T, tratar como CT na interface (regra especial)
            if t_team and t_team['name'] == 'ORBITAL ROXA':
                print(f"🔄 ORBITAL ROXA detectado como T, aplicando regra especial de inversão")
                team_info['CT'] = t_team  # ORBITAL ROXA aparece como CT na interface
                team_info['score_ct'] = score_t  # Inverter placar também
                if ct_team:
                    team_info['TERRORIST'] = ct_team  # CT real aparece como T na interface
                    team_info['score_t'] = score_ct  # Inverter placar também
                else:
                    team_info['score_t'] = score_ct
            else:
                # Lógica normal: CT é CT, T é T
                if ct_team:
                    team_info['CT'] = ct_team
                    team_info['score_ct'] = score_ct
                if t_team:
                    team_info['TERRORIST'] = t_team
                    team_info['score_t'] = score_t

            print(f"🏆 team_info final: CT={team_info.get('CT', {}).get('name', 'None')}, T={team_info.get('TERRORIST', {}).get('name', 'None')}")
            print(f"🎯 Placar: CT {team_info.get('score_ct', 0)} x {team_info.get('score_t', 0)} T")
            
            # LÓGICA PADRONIZADA DE ATRIBUIÇÃO DE DISPLAY_TEAM
            print(f"👥 Processando {len(match_info.get('players', []))} jogadores...")
            
            for player in match_info.get('players', []):
                steamid = player['steamid']
                team_number = player['team_number']
                player_name = player['name']
                
                player_team_data = get_player_team_info(steamid)
                if player_team_data:
                    # Jogador cadastrado no teams.json
                    team_name = player_team_data['team']['name']
                    
                    # Aplicar regra especial para ORBITAL ROXA
                    if team_name == 'ORBITAL ROXA':
                        display_team = 'CT'  # ORBITAL ROXA sempre aparece como CT
                        print(f"  🟣 {player_name} ({steamid}) -> {display_team} (ORBITAL ROXA - regra especial)")
                    else:
                        # Para outros times cadastrados, usar lógica normal
                        display_team = 'CT' if team_number == 3 else 'TERRORIST'
                        print(f"  🔵 {player_name} ({steamid}) -> {display_team} (Time: {team_name})")
                    
                    player_team_info[str(steamid)] = {
                        'team': player_team_data['team'],
                        'player_info': player_team_data['player_info'],
                        'display_team': display_team
                    }
                else:
                    # Jogador não cadastrado, usar team_number
                    display_team = 'CT' if team_number == 3 else 'TERRORIST'
                    print(f"  ⚪ {player_name} ({steamid}) -> {display_team} (Não cadastrado)")
                    
                    player_team_info[str(steamid)] = {
                        'display_team': display_team
                    }
        
        # Adicionar Steam IDs aos dados dos jogadores (movido para depois da leitura do match_info)
        for player in match_info.get('players', []):
            for player_stat in player_stats_list:
                if player_stat['player'] == player['name']:
                    player_stat['steamid'] = str(player['steamid'])
                    break
        
        # LÓGICA PADRONIZADA DE ORDENAÇÃO E SEPARAÇÃO POR TIME REAL
        print(f"🔍 Iniciando lógica padronizada para {demo_name}")
        
        # 1. Agrupar jogadores por time real (baseado no teams.json)
        teams_players = {}
        
        for player_stat in player_stats_list:
            player_steamid = player_stat.get('steamid', '')
            player_team_info_item = player_team_info.get(player_steamid, {})
            
            # Determinar o time real do jogador
            if player_team_info_item.get('team'):
                # Jogador cadastrado no teams.json
                team_name = player_team_info_item['team']['name']
                team_id = player_team_info_item['team']['id']
            else:
                # Jogador não cadastrado - usar fallback baseado no team_number
                team_name = 'Unknown Team'
                team_id = f"unknown_{player_stat.get('team', 'CT')}"
            
            # Debug: mostrar qual time cada jogador foi atribuído
            print(f"  👤 {player_stat['player']} ({player_steamid}) -> {team_name} (ID: {team_id})")
            
            # Adicionar jogador ao time correspondente
            if team_id not in teams_players:
                teams_players[team_id] = {
                    'team_name': team_name,
                    'team_id': team_id,
                    'players': []
                }
            teams_players[team_id]['players'].append(player_stat)
        
        # 2. Ordenar cada time por K/D ratio (maior para menor)
        for team_id, team_data in teams_players.items():
            team_data['players'].sort(key=lambda x: x['kd_ratio'], reverse=True)
        
        # 3. Debug: mostrar ordenação final por time
        for team_id, team_data in teams_players.items():
            team_name = team_data['team_name']
            players = team_data['players']
            players_str = [p['player'] + f' (K/D: {p["kd_ratio"]:.2f})' for p in players]
            print(f"📊 {team_name} ({len(players)}): {players_str}")
        
        # 4. Combinar todos os jogadores mantendo ordem por time
        # Ordenar times por nome para consistência
        sorted_teams = sorted(teams_players.items(), key=lambda x: x[1]['team_name'])
        
        player_stats_list = []
        for team_id, team_data in sorted_teams:
            player_stats_list.extend(team_data['players'])
        
        print(f"✅ Lógica padronizada aplicada: {len(teams_players)} times, {len(player_stats_list)} jogadores total")
        
        # Preparar half_data com base nos times detectados
        # t_team é detectado nos jogadores do team_number=2
        # ct_team é detectado nos jogadores do team_number=3
        orbital_roxa_detected = (t_team and t_team.get('name') == 'ORBITAL ROXA')

        # Determinar qual lado cada team jogou baseado no cenário detectado
        # Verificando qual cenário foi usado comparando os scores
        if scenario1_team2 == score_t and scenario1_team3 == score_ct:
            # Cenário 1: Team 2 começou como CT, Team 3 começou como T
            team2_side_first = 'CT'
            team2_side_second = 'T'
            team3_side_first = 'T'
            team3_side_second = 'CT'
        else:
            # Cenário 2: Team 2 começou como T, Team 3 começou como CT
            team2_side_first = 'T'
            team2_side_second = 'CT'
            team3_side_first = 'CT'
            team3_side_second = 'T'

        if orbital_roxa_detected:
            # ORBITAL ROXA está no team_number=2 mas aparece como CT na interface (esquerda)
            half_data = {
                'ct_first': team2_first_half,
                't_first': team3_first_half,
                'ct_second': team2_second_half,
                't_second': team3_second_half,
                'ct_ot': team2_ot_score,
                't_ot': team3_ot_score,
                'has_overtime': has_overtime,
                'team_left_side_first': team2_side_first,    # Lado que time da esquerda jogou no 1º half
                'team_left_side_second': team2_side_second,   # Lado que time da esquerda jogou no 2º half
                'team_right_side_first': team3_side_first,    # Lado que time da direita jogou no 1º half
                'team_right_side_second': team3_side_second   # Lado que time da direita jogou no 2º half
            }
            print(f"🟣 ORBITAL ROXA detected - Lados: Esq 1º={team2_side_first}({team2_first_half}), Esq 2º={team2_side_second}({team2_second_half}), OT=({team2_ot_score}), Dir 1º={team3_side_first}({team3_first_half}), Dir 2º={team3_side_second}({team3_second_half}), OT=({team3_ot_score})")
        else:
            # Lógica normal: team3 aparece como CT (esquerda), team2 aparece como T (direita)
            half_data = {
                'ct_first': team3_first_half,
                't_first': team2_first_half,
                'ct_second': team3_second_half,
                't_second': team2_second_half,
                'ct_ot': team3_ot_score,
                't_ot': team2_ot_score,
                'has_overtime': has_overtime,
                'team_left_side_first': team3_side_first,    # Lado que time da esquerda jogou no 1º half
                'team_left_side_second': team3_side_second,   # Lado que time da esquerda jogou no 2º half
                'team_right_side_first': team2_side_first,    # Lado que time da direita jogou no 1º half
                'team_right_side_second': team2_side_second   # Lado que time da direita jogou no 2º half
            }
            print(f"✅ Lados: Esq 1º={team3_side_first}({team3_first_half}), Esq 2º={team3_side_second}({team3_second_half}), OT=({team3_ot_score}), Dir 1º={team2_side_first}({team2_first_half}), Dir 2º={team2_side_second}({team2_second_half}), OT=({team2_ot_score})")

        # Converter booleanos Python para JavaScript no JSON
        chart_data_json = json.dumps(chart_data).replace('True', 'true').replace('False', 'false')

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "demo_name": demo_name,
            "chart_data": chart_data_json,
            "round_data": round_data,
            "player_stats": player_stats_list,
            "total_kills": total_kills,
            "total_hs": total_hs,
            "hs_percentage": f"{hs_percentage:.1f}",
            "round_count": round_count,
            "match_duration": "N/A",
            "map_name": map_name,
            "team_info": team_info,
            "player_team_info": player_team_info,
            "player_team_info_json": json.dumps(player_team_info),
            "half_data": half_data,
            "score_ct": team_info.get('score_ct', score_ct) if team_info else score_ct,
            "score_t": team_info.get('score_t', score_t) if team_info else score_t,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        print(f"❌ Erro no dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Erro ao carregar dashboard: {str(e)}"
        })

def prepare_chart_data(kills_df, damage_df, player_stats):
    """Preparar dados para os gráficos"""
    try:
        # Dados por round
        rounds = sorted(kills_df['total_rounds_played'].unique()) if not kills_df.empty else []
        ct_kills = []
        t_kills = []
        headshots = []
        damage = []
        
        for round_num in rounds:
            round_data = kills_df[kills_df['total_rounds_played'] == round_num]
            ct_kills.append(len(round_data[round_data['user_team_name'] == 'CT']))
            t_kills.append(len(round_data[round_data['user_team_name'] == 'TERRORIST']))
            headshots.append(round_data['headshot'].sum() if 'headshot' in round_data.columns else 0)
            
            # Dano por round
            round_damage = damage_df[damage_df['total_rounds_played'] == round_num]
            damage.append(round_damage['dmg_health'].sum() if not round_damage.empty and 'dmg_health' in round_damage.columns else 0)
        
        # Dados dos jogadores
        player_names = player_stats['player'].tolist()
        kd_ratios = player_stats['kd_ratio'].tolist()
        hs_percentages = player_stats['hs_percent'].tolist()
        
        # Posições de kills para heatmap
        kill_positions_x = kills_df['user_X'].tolist() if 'user_X' in kills_df.columns else []
        kill_positions_y = kills_df['user_Y'].tolist() if 'user_Y' in kills_df.columns else []
        
        return {
            "rounds": [int(r) for r in rounds],
            "ct_kills": ct_kills,
            "t_kills": t_kills,
            "headshots": headshots,
            "damage": damage,
            "player_names": player_names,
            "kd_ratios": kd_ratios,
            "hs_percentages": hs_percentages,
            "kill_positions_x": kill_positions_x,
            "kill_positions_y": kill_positions_y
        }
    except Exception as e:
        print(f"Erro ao preparar dados dos gráficos: {e}")
        return {}

def prepare_chart_data_improved(kills_df, damage_df, player_stats, round_data):
    """Preparar dados para os gráficos com análise melhorada"""
    try:
        # Dados por round (usando dados já processados)
        rounds = [int(r['round']) for r in round_data]
        ct_kills = [int(r['ct_kills']) for r in round_data]
        t_kills = [int(r['t_kills']) for r in round_data]
        headshots = [int(r['headshots']) for r in round_data]
        
        # Calcular dano por round
        damage = []
        for round_num in rounds:
            if not damage_df.empty and 'total_rounds_played' in damage_df.columns:
                round_damage = damage_df[damage_df['total_rounds_played'] == round_num]
                damage_sum = round_damage['dmg_health'].sum() if 'dmg_health' in round_damage.columns else 0
                damage.append(int(damage_sum))
            else:
                damage.append(0)
        
        # Dados dos jogadores
        player_names = [str(name) for name in player_stats['player']]
        kd_ratios = [float(kd) for kd in player_stats['kd_ratio']]
        hs_percentages = [float(hs) for hs in player_stats['hs_percent']]
        
        # Dados para heatmap (posições dos kills)
        heatmap_data = []
        if not kills_df.empty and 'user_X' in kills_df.columns and 'user_Y' in kills_df.columns:
            # Filtrar posições válidas
            valid_positions = kills_df[
                (kills_df['user_X'].notna()) & 
                (kills_df['user_Y'].notna()) &
                (kills_df['user_X'] != 0) &
                (kills_df['user_Y'] != 0)
            ]
            
            heatmap_data = [
                {
                    'x': float(row['user_X']),
                    'y': float(row['user_Y']),
                    'team': str(row.get('user_team_name', 'Unknown'))
                }
                for _, row in valid_positions.iterrows()
            ]
        
        return {
            "rounds": rounds,
            "ct_kills": ct_kills,
            "t_kills": t_kills,
            "headshots": headshots,
            "damage": damage,
            "player_names": player_names,
            "kd_ratios": kd_ratios,
            "hs_percentages": hs_percentages,
            "heatmap_data": heatmap_data
        }
        
    except Exception as e:
        print(f"Erro ao preparar dados melhorados: {e}")
        import traceback
        traceback.print_exc()
        return {
            "rounds": [],
            "ct_kills": [],
            "t_kills": [],
            "headshots": [],
            "damage": [],
            "player_names": [],
            "kd_ratios": [],
            "hs_percentages": [],
            "heatmap_data": []
        }

@app.get("/api/analysis/{demo_name}")
def get_analysis_summary(demo_name: str):
    """API endpoint para obter resumo da análise"""
    analysis_dir = ANALYSIS_DIR / demo_name
    if not analysis_dir.exists():
        return {"error": "Análise não encontrada"}
    
    try:
        # Ler estatísticas dos jogadores
        stats_file = analysis_dir / "player_stats.csv"
        if stats_file.exists():
            import pandas as pd
            df = pd.read_csv(stats_file)
            return {
                "demo_name": demo_name,
                "players": df.to_dict('records'),
                "total_players": len(df)
            }
    except Exception as e:
        return {"error": f"Erro ao ler dados: {str(e)}"}
    
    return {"error": "Dados não disponíveis"}

@app.get("/api/matches")
def list_matches():
    """Lista todas as partidas processadas"""
    try:
        processed_demos = monitor.get_processed_list()

        # Carregar times cadastrados
        teams_file = BASE_DIR / "teams.json"
        registered_teams = []
        if teams_file.exists():
            with open(teams_file, 'r', encoding='utf-8') as f:
                registered_teams = json.load(f)

        # Enriquecer com informações adicionais
        matches = []
        for demo in processed_demos:
            demo_name = demo.get('demo_name', '')

            # Resolver analysis_path - pode ser relativo ou absoluto
            analysis_path_str = demo.get('analysis_path', '')
            analysis_path = Path(analysis_path_str)

            # Se o path não for absoluto, resolver em relação ao BASE_DIR
            if not analysis_path.is_absolute():
                analysis_path = BASE_DIR / analysis_path

            # Se ainda não existir, tentar diretamente em ANALYSIS_DIR
            if not analysis_path.exists():
                analysis_path = ANALYSIS_DIR / demo_name

            match_info = {
                'demo_name': demo_name,
                'filename': demo.get('filename', ''),
                'processed_at': demo.get('processed_at', ''),
                'file_size': demo.get('file_size', 0),
                'status': 'ready'
            }

            # Tentar carregar informações adicionais da partida
            if analysis_path.exists():
                try:
                    # Carregar match_info.json se existir
                    match_json = analysis_path / "match_info.json"
                    if match_json.exists():
                        with open(match_json, 'r') as f:
                            info = json.load(f)
                            # Buscar mapa - pode estar em 'map' ou 'header.map_name'
                            match_info['map'] = info.get('map', info.get('header', {}).get('map_name', 'Unknown'))

                            # Extrair score (Team2 x Team3)
                            score = info.get('score', {})
                            match_info['team2_score'] = score.get('team2_score', 0)
                            match_info['team3_score'] = score.get('team3_score', 0)

                            # Buscar total_rounds - pode estar em 'rounds.total_rounds' ou 'score.total_rounds'
                            rounds_info = info.get('rounds', {})
                            match_info['total_rounds'] = rounds_info.get('total_rounds', score.get('total_rounds', 0))

                            # Extrair nomes dos times verificando nos times cadastrados
                            players = info.get('players', [])
                            team2_steamids = [str(p['steamid']) for p in players if p.get('team_number') == 2]
                            team3_steamids = [str(p['steamid']) for p in players if p.get('team_number') == 3]

                            def find_team_by_player(steamid_list):
                                for team in registered_teams:
                                    team_steamids = [str(p['steamid']) for p in team.get('players', [])]
                                    # Verificar se pelo menos 2 jogadores do time estão na lista
                                    matches = sum(1 for sid in steamid_list if sid in team_steamids)
                                    if matches >= 2:  # Pelo menos 2 jogadores do time devem estar na partida
                                        return team['name']
                                return None

                            team2_name = find_team_by_player(team2_steamids) or "Team 2"
                            team3_name = find_team_by_player(team3_steamids) or "Team 3"

                            # Obter scores
                            team2_score = match_info.get('team2_score', 0)
                            team3_score = match_info.get('team3_score', 0)

                            # Calcular informações de OT
                            ot_info = calculate_overtime_info(analysis_path, team2_score, team3_score)

                            # Adicionar informações de OT ao match_info
                            if ot_info['has_overtime']:
                                match_info['has_overtime'] = True
                                match_info['overtime_score'] = f"{ot_info['team2_ot_score']}-{ot_info['team3_ot_score']}"
                                match_info['num_overtimes'] = ot_info['num_overtimes']
                                match_info['regulation_score'] = f"12-12"
                            else:
                                match_info['has_overtime'] = False

                            # Garantir que o time vencedor fique sempre à esquerda
                            if team3_score > team2_score:
                                # Team 3 venceu, inverter a ordem
                                match_info['team2_name'] = team3_name
                                match_info['team3_name'] = team2_name
                                match_info['team2_score'] = team3_score
                                match_info['team3_score'] = team2_score

                                # Inverter também as informações de OT se existir
                                if ot_info['has_overtime']:
                                    match_info['overtime_score'] = f"{ot_info['team3_ot_score']}-{ot_info['team2_ot_score']}"
                            else:
                                # Team 2 venceu ou empate, manter ordem normal
                                match_info['team2_name'] = team2_name
                                match_info['team3_name'] = team3_name

                    # Carregar estatísticas dos jogadores
                    stats_file = analysis_path / "player_stats.csv"
                    if stats_file.exists():
                        df = pd.read_csv(stats_file)
                        match_info['total_players'] = len(df)

                        # Criar mapeamento de team_id para side (CT/T) se necessário
                        # Isso é necessário quando o CSV tem IDs de times (team_123) ao invés de CT/T
                        team_id_to_side = {}
                        if 'team' in df.columns and df['team'].astype(str).str.startswith('team_').any():
                            # Ler kills.csv para obter o mapeamento de team_id para CT/T
                            kills_file = analysis_path / "kills.csv"
                            if kills_file.exists():
                                try:
                                    kills_df = pd.read_csv(kills_file, nrows=1)
                                    if 'ct_team_name' in kills_df.columns and 't_team_name' in kills_df.columns:
                                        ct_team_id = str(kills_df['ct_team_name'].iloc[0])
                                        t_team_id = str(kills_df['t_team_name'].iloc[0])
                                        team_id_to_side[ct_team_id] = 'CT'
                                        team_id_to_side[t_team_id] = 'TERRORIST'
                                except Exception as e:
                                    print(f"Erro ao ler mapeamento de times: {e}")

                        # Encontrar o jogador com mais kills
                        if len(df) > 0:
                            top_player_row = df.nlargest(1, 'total_kills').iloc[0]
                            match_info['top_player'] = str(top_player_row['player'])

                            # Mapear team ID para side se necessário
                            team_value = str(top_player_row.get('team', 'CT'))
                            if team_value in team_id_to_side:
                                match_info['top_player_team'] = team_id_to_side[team_value]
                            else:
                                match_info['top_player_team'] = team_value

                            match_info['top_player_kills'] = int(top_player_row.get('total_kills', 0))
                            match_info['top_player_deaths'] = int(top_player_row.get('deaths', 0))
                            match_info['top_player_assists'] = 0  # Não disponível no CSV atual
                            match_info['top_player_adr'] = float(top_player_row.get('adr', 0))
                            match_info['top_player_rating'] = float(top_player_row.get('kd_ratio', 0))
                            match_info['top_player_hs'] = float(top_player_row.get('hs_percent', 0))
                        else:
                            match_info['top_player'] = 'N/A'
                            match_info['top_player_team'] = 'CT'
                            match_info['top_player_kills'] = 0
                            match_info['top_player_deaths'] = 0
                            match_info['top_player_assists'] = 0
                            match_info['top_player_adr'] = 0
                            match_info['top_player_rating'] = 0
                            match_info['top_player_hs'] = 0

                        match_info['total_kills'] = int(df['total_kills'].sum())

                except Exception as e:
                    import traceback
                    print(f"Erro ao carregar info de {demo_name}: {e}")
                    traceback.print_exc()

            matches.append(match_info)
        
        return {
            "total": len(matches),
            "matches": matches
        }
    except Exception as e:
        return {"error": f"Erro ao listar partidas: {str(e)}"}

@app.get("/api/monitor/status")
def monitor_status():
    """Retorna status do monitor"""
    return {
        "running": monitor.running,
        "watch_dir": str(monitor.watch_dir),
        "interval": monitor.interval,
        "processed_count": len(monitor.processed_demos),
        "last_check": datetime.now().isoformat()
    }

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    """Página de upload de demos"""
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/api/upload-demo")
async def upload_demo(
    file: UploadFile = File(...),
    is_tournament: bool = Form(False),
    tournament_name: str = Form("")
):
    """Recebe upload de demo e processa"""
    try:
        # Validar extensão do arquivo
        if not file.filename.endswith('.dem'):
            return {"success": False, "error": "Arquivo deve ser uma demo (.dem)"}

        # Gerar nome único para evitar conflitos
        demo_name = file.filename
        demo_path = DEMOS_DIR / demo_name

        # Se já existe, adicionar timestamp
        if demo_path.exists():
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = demo_name.replace('.dem', '')
            demo_name = f"{base_name}_{timestamp}.dem"
            demo_path = DEMOS_DIR / demo_name

        # Salvar arquivo
        with open(demo_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        print(f"✅ Demo salva: {demo_path}")
        print(f"📋 Campeonato: {tournament_name if is_tournament else 'Não'}")

        # Criar arquivo de metadados para o monitor processar
        if is_tournament and tournament_name:
            meta_file = demo_path.with_suffix('.meta.json')
            import json
            with open(meta_file, 'w') as f:
                json.dump({
                    'tournament': tournament_name,
                    'uploaded_at': datetime.now().isoformat()
                }, f)

        return {
            "success": True,
            "message": f"Demo '{demo_name}' enviada com sucesso! O processamento iniciará em breve.",
            "demo_name": demo_name,
            "is_tournament": is_tournament,
            "tournament_name": tournament_name if is_tournament else None
        }

    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.get("/matches", response_class=HTMLResponse)
def matches_page(request: Request):
    """Página principal com cards de todas as partidas"""
    return templates.TemplateResponse("matches.html", {"request": request})

@app.get("/players", response_class=HTMLResponse)
def players_page(request: Request):
    """Página com lista de todos os jogadores"""
    return templates.TemplateResponse("players.html", {"request": request})

@app.get("/tournaments", response_class=HTMLResponse)
def tournaments_page(request: Request):
    """Página com lista de todos os torneios"""
    return templates.TemplateResponse("tournaments.html", {"request": request})

@app.get("/tournament/{slug}", response_class=HTMLResponse)
def tournament_page(request: Request, slug: str):
    """Página individual do torneio"""
    return templates.TemplateResponse("tournament.html", {"request": request})

@app.get("/manage-tournaments", response_class=HTMLResponse)
def manage_tournaments_page(request: Request):
    """Página de gerenciamento de campeonatos"""
    return templates.TemplateResponse("manage_tournaments.html", {"request": request})

# ==========================================
# PLAYER PROFILE API
# ==========================================

@app.get("/player/{steamid}", response_class=HTMLResponse)
async def player_profile(request: Request, steamid: str):
    """Página pessoal do jogador"""
    try:
        # Buscar informações do jogador no teams.json
        player_info = get_player_team_info(steamid)
        
        # Buscar todas as demos processadas
        demo_analysis_dir = ANALYSIS_DIR
        player_stats = []
        matches_played = []
        
        if demo_analysis_dir.exists():
            for demo_dir in demo_analysis_dir.iterdir():
                if demo_dir.is_dir():
                    match_info_file = demo_dir / "match_info.json"
                    player_stats_file = demo_dir / "player_stats.csv"
                    
                    if match_info_file.exists() and player_stats_file.exists():
                        # Verificar se o jogador participou desta demo
                        with open(match_info_file, 'r', encoding='utf-8') as f:
                            match_info = json.load(f)
                        
                        player_found = False
                        for player in match_info.get('players', []):
                            if str(player['steamid']) == steamid:
                                player_found = True
                                break
                        
                        if player_found:
                            # Encontrar o nome do jogador no match_info
                            player_name = None
                            for player in match_info.get('players', []):
                                if str(player['steamid']) == steamid:
                                    player_name = player['name']
                                    break
                            
                            if player_name:
                                # Ler estatísticas do jogador pelo nome
                                import pandas as pd
                                df = pd.read_csv(player_stats_file)
                                player_row = df[df['player'] == player_name]
                                
                                if not player_row.empty:
                                    stats = player_row.iloc[0].to_dict()
                                    stats['demo_name'] = demo_dir.name
                                    stats['match_info'] = match_info
                                    player_stats.append(stats)
                                    
                                    matches_played.append({
                                        'demo_name': demo_dir.name,
                                        'map': match_info.get('map', match_info.get('header', {}).get('map_name', 'Unknown')),
                                        'date': match_info.get('date', match_info.get('extraction_time', '')),
                                        'score': match_info.get('score', {}),
                                        'player_stats': stats
                                    })
        
        # Calcular estatísticas agregadas
        if player_stats:
            total_kills = sum(stats.get('total_kills', 0) for stats in player_stats)
            total_deaths = sum(stats.get('deaths', 0) for stats in player_stats)
            total_damage = sum(stats.get('total_damage', 0) for stats in player_stats)
            total_hs = sum(stats.get('headshot', 0) for stats in player_stats)
            
            # Calcular total de rounds
            total_rounds = 0
            for match in matches_played:
                score_info = match.get('score', {})
                total_rounds += score_info.get('total_rounds', 0) if isinstance(score_info, dict) else 0
            
            avg_kd = total_kills / total_deaths if total_deaths > 0 else 0
            avg_adr = total_damage / total_rounds if total_rounds > 0 else 0
            avg_hs_percent = (total_hs / total_kills * 100) if total_kills > 0 else 0
            
            aggregated_stats = {
                'total_matches': len(player_stats),
                'total_kills': total_kills,
                'total_deaths': total_deaths,
                'total_damage': total_damage,
                'avg_kd': avg_kd,
                'avg_adr': avg_adr,
                'avg_hs_percent': avg_hs_percent,
                'total_hs': total_hs
            }
        else:
            aggregated_stats = {
                'total_matches': 0,
                'total_kills': 0,
                'total_deaths': 0,
                'total_damage': 0,
                'avg_kd': 0,
                'avg_adr': 0,
                'avg_hs_percent': 0,
                'total_hs': 0
            }
        
        return templates.TemplateResponse("player_profile.html", {
            "request": request,
            "steamid": steamid,
            "player_info": player_info,
            "aggregated_stats": aggregated_stats,
            "matches_played": matches_played,
            "player_stats": player_stats
        })
        
    except Exception as e:
        print(f"Erro na página do jogador: {e}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("player_profile.html", {
            "request": request,
            "steamid": steamid,
            "player_info": None,
            "aggregated_stats": {},
            "matches_played": [],
            "player_stats": []
        })

@app.get("/pro/{steamid}", response_class=HTMLResponse)
async def player_profile_pro_main(request: Request, steamid: str):
    """Página de perfil profissional do jogador - rota oficial"""
    return await player_profile_pro_handler(request, steamid)

@app.get("/player/{steamid}/pro")
async def player_profile_pro(request: Request, steamid: str):
    """Página de perfil profissional do jogador - inspirada no HLTV (rota legada)"""
    return await player_profile_pro_handler(request, steamid)

async def player_profile_pro_handler(request: Request, steamid: str):
    """Handler compartilhado para perfil profissional do jogador"""
    try:
        # Buscar informações do jogador
        player_info = get_player_team_info(steamid)

        # Inicializar estatísticas agregadas
        aggregated_stats = {
            'total_matches': 0,
            'total_kills': 0,
            'total_deaths': 0,
            'total_damage': 0,
            'total_hs': 0,
            'avg_kd': 0.0,
            'avg_adr': 0.0,
            'avg_hs_percent': 0.0,
            'total_rounds': 0
        }

        matches_played = []
        player_stats = []

        # Iterar através de todas as pastas de análise de demo
        demo_analysis_path = ANALYSIS_DIR
        if demo_analysis_path.exists():
            for demo_folder in demo_analysis_path.iterdir():
                if demo_folder.is_dir() and demo_folder.name != "processed_demos.json":
                    match_info_path = demo_folder / "match_info.json"

                    if match_info_path.exists():
                        with open(match_info_path, 'r', encoding='utf-8') as f:
                            match_info = json.load(f)

                        # Verificar se o jogador participou desta partida
                        player_found = False
                        player_name = None

                        # Verificar na lista de players do match_info
                        if 'players' in match_info:
                            for player in match_info['players']:
                                if str(player.get('steamid')) == str(steamid):
                                    player_found = True
                                    player_name = player.get('name')
                                    break

                        if player_found and player_name:
                            print(f"🎯 Jogador encontrado: {player_name} (Steam ID: {steamid}) na demo: {demo_folder.name}")
                            # Ler estatísticas do jogador
                            player_stats_path = demo_folder / "player_stats.csv"
                            if player_stats_path.exists():
                                df = pd.read_csv(player_stats_path)
                                player_row = df[df['player'] == player_name]

                                if not player_row.empty:
                                    stats = player_row.iloc[0].to_dict()
                                    print(f"📊 Stats encontradas: {stats}")

                                    # Extrair mapa e data corretamente - suporta ambos schemas
                                    map_name = match_info.get('map', match_info.get('header', {}).get('map_name', 'Unknown'))
                                    # Remover prefixo "de_" se existir
                                    if map_name.startswith('de_'):
                                        map_name = map_name[3:].capitalize()

                                    extraction_time = match_info.get('date', match_info.get('extraction_time', ''))

                                    # Adicionar à lista de estatísticas
                                    player_stats.append({
                                        'demo_name': demo_folder.name,
                                        'map': map_name,
                                        'date': extraction_time,
                                        'player_stats': stats
                                    })

                                    # Acumular estatísticas
                                    aggregated_stats['total_matches'] += 1
                                    aggregated_stats['total_kills'] += stats.get('total_kills', 0)
                                    aggregated_stats['total_deaths'] += stats.get('deaths', 0)
                                    aggregated_stats['total_damage'] += stats.get('total_damage', 0)
                                    aggregated_stats['total_hs'] += stats.get('headshot', 0)

                                    # Obter total de rounds do score
                                    score_info = match_info.get('score', {})
                                    total_rounds = score_info.get('total_rounds', 20)
                                    aggregated_stats['total_rounds'] += total_rounds

                                    # Adicionar à lista de partidas
                                    matches_played.append({
                                        'demo_name': demo_folder.name,
                                        'map': map_name,
                                        'date': extraction_time,
                                        'player_stats': stats
                                    })

        # Calcular médias
        if aggregated_stats['total_matches'] > 0:
            total_rounds = aggregated_stats['total_rounds']
            if total_rounds > 0:
                aggregated_stats['avg_adr'] = aggregated_stats['total_damage'] / total_rounds
            else:
                aggregated_stats['avg_adr'] = aggregated_stats['total_damage'] / aggregated_stats['total_matches'] / 20

            if aggregated_stats['total_deaths'] > 0:
                aggregated_stats['avg_kd'] = aggregated_stats['total_kills'] / aggregated_stats['total_deaths']
            else:
                aggregated_stats['avg_kd'] = 0.0

            if aggregated_stats['total_kills'] > 0:
                aggregated_stats['avg_hs_percent'] = (aggregated_stats['total_hs'] / aggregated_stats['total_kills']) * 100
            else:
                aggregated_stats['avg_hs_percent'] = 0.0

            # Calcular distância média de kill (usando dados das partidas)
            total_kill_distance = 0
            kill_count = 0
            for match in matches_played:
                if 'player_stats' in match:
                    stats = match['player_stats']
                    if 'avg_kill_distance' in stats:
                        total_kill_distance += stats['avg_kill_distance']
                        kill_count += 1

            if kill_count > 0:
                aggregated_stats['avg_kill_distance'] = total_kill_distance / kill_count
            else:
                aggregated_stats['avg_kill_distance'] = 0.0

        # Calcular estatísticas por mapa
        maps_stats = {}
        for match in matches_played:
            map_name = match['map']
            if map_name not in maps_stats:
                maps_stats[map_name] = {
                    'matches': 0,
                    'kills': 0,
                    'deaths': 0,
                    'damage': 0,
                    'hs': 0
                }

            stats = match.get('player_stats', {})
            maps_stats[map_name]['matches'] += 1
            maps_stats[map_name]['kills'] += stats.get('total_kills', 0)
            maps_stats[map_name]['deaths'] += stats.get('deaths', 0)
            maps_stats[map_name]['damage'] += stats.get('total_damage', 0)
            maps_stats[map_name]['hs'] += stats.get('headshot', 0)

        return templates.TemplateResponse("player_profile_pro.html", {
            "request": request,
            "player_info": player_info,
            "aggregated_stats": aggregated_stats,
            "matches_played": matches_played,
            "player_stats": player_stats,
            "maps_stats": maps_stats,
            "steamid": steamid
        })

    except Exception as e:
        print(f"Erro na página profissional do jogador: {e}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("player_profile_pro.html", {
            "request": request,
            "player_info": None,
            "aggregated_stats": {},
            "matches_played": [],
            "player_stats": [],
            "maps_stats": {},
            "steamid": steamid
        })

@app.get("/api/player/{steamid}/stats")
async def get_player_stats_by_side(steamid: str, side: str = "both"):
    """API para obter estatísticas do jogador filtradas por side (CT, T ou both)"""
    try:
        # Buscar informações do jogador
        player_info = get_player_team_info(steamid)

        # Inicializar estatísticas
        stats = {
            'total_kills': 0,
            'total_deaths': 0,
            'total_damage': 0,
            'total_hs': 0,
            'total_rounds': 0,
            'total_matches': 0,
            'avg_kd': 0.0,
            'avg_adr': 0.0,
            'avg_hs_percent': 0.0,
            'avg_kills_per_round': 0.0
        }

        demo_analysis_path = ANALYSIS_DIR
        if not demo_analysis_path.exists():
            return stats

        for demo_folder in demo_analysis_path.iterdir():
            if not demo_folder.is_dir() or demo_folder.name == "processed_demos.json":
                continue

            match_info_path = demo_folder / "match_info.json"
            kills_path = demo_folder / "kills.csv"
            damage_path = demo_folder / "damage.csv"

            if not match_info_path.exists():
                continue

            # Carregar match_info
            with open(match_info_path, 'r', encoding='utf-8') as f:
                match_info = json.load(f)

            # Verificar se jogador está na partida
            player_found = False
            player_name = None
            player_team_number = None

            for player in match_info.get('players', []):
                if str(player.get('steamid')) == str(steamid):
                    player_found = True
                    player_name = player.get('name')
                    player_team_number = player.get('team_number')  # 2=T, 3=CT
                    break

            if not player_found or not player_name:
                continue

            stats['total_matches'] += 1

            # Determinar qual lado o jogador jogou em cada half
            # Em CS2, times trocam de lado no round 12 (half = 12 rounds)
            first_half_end = 12

            # Se side == "both", contar tudo
            if side == "both":
                # Usar player_stats.csv para estatísticas totais
                player_stats_path = demo_folder / "player_stats.csv"
                if player_stats_path.exists():
                    df = pd.read_csv(player_stats_path)
                    player_row = df[df['player'] == player_name]
                    if not player_row.empty:
                        row_stats = player_row.iloc[0]
                        # Converter numpy types para Python types
                        stats['total_kills'] += int(row_stats.get('total_kills', 0))
                        stats['total_deaths'] += int(row_stats.get('deaths', 0))
                        stats['total_damage'] += int(row_stats.get('total_damage', 0))
                        stats['total_hs'] += int(row_stats.get('headshot', 0))

                        # Calcular rounds (aproximado)
                        score_info = match_info.get('score', {})
                        total_rounds = score_info.get('total_rounds', 20)
                        stats['total_rounds'] += int(total_rounds)
            else:
                # Filtrar por side específico (CT ou T)
                if not kills_path.exists() or not damage_path.exists():
                    continue

                kills_df = pd.read_csv(kills_path)
                damage_df = pd.read_csv(damage_path)

                # Filtrar kills onde o jogador é o attacker
                player_kills = kills_df[kills_df['attacker_name'] == player_name].copy()

                # Filtrar deaths onde o jogador é a vítima
                player_deaths = kills_df[kills_df['user_name'] == player_name].copy()

                # Filtrar damage causado pelo jogador
                player_damage = damage_df[damage_df['attacker_name'] == player_name].copy()

                # Determinar qual side o jogador estava em cada round
                # team_number 2 = começou como T, team_number 3 = começou como CT
                # Após round 12, os times trocam

                rounds_counted = set()

                for _, kill in player_kills.iterrows():
                    round_num = int(kill.get('total_rounds_played', 0))

                    # Determinar side do jogador neste round
                    if player_team_number == 2:  # Começou como T
                        player_side_in_round = 'T' if round_num < first_half_end else 'CT'
                    else:  # Começou como CT
                        player_side_in_round = 'CT' if round_num < first_half_end else 'T'

                    # Filtrar pelo side desejado
                    if (side == "CT" and player_side_in_round == "CT") or \
                       (side == "T" and player_side_in_round == "T"):
                        stats['total_kills'] += 1
                        if kill.get('headshot', False):
                            stats['total_hs'] += 1
                        rounds_counted.add(round_num)

                # Contar deaths
                for _, death in player_deaths.iterrows():
                    round_num = int(death.get('total_rounds_played', 0))

                    if player_team_number == 2:
                        player_side_in_round = 'T' if round_num < first_half_end else 'CT'
                    else:
                        player_side_in_round = 'CT' if round_num < first_half_end else 'T'

                    if (side == "CT" and player_side_in_round == "CT") or \
                       (side == "T" and player_side_in_round == "T"):
                        stats['total_deaths'] += 1
                        rounds_counted.add(round_num)

                # Calcular damage
                total_damage_match = 0
                for _, dmg in player_damage.iterrows():
                    round_num = int(dmg.get('total_rounds_played', 0))

                    if player_team_number == 2:
                        player_side_in_round = 'T' if round_num < first_half_end else 'CT'
                    else:
                        player_side_in_round = 'CT' if round_num < first_half_end else 'T'

                    if (side == "CT" and player_side_in_round == "CT") or \
                       (side == "T" and player_side_in_round == "T"):
                        total_damage_match += int(dmg.get('dmg_health', 0))
                        rounds_counted.add(round_num)

                stats['total_damage'] += total_damage_match

                # Contar rounds reais onde o jogador participou
                stats['total_rounds'] += len(rounds_counted)

        # Calcular médias e converter para float Python nativo
        if stats['total_deaths'] > 0:
            stats['avg_kd'] = float(stats['total_kills'] / stats['total_deaths'])

        if stats['total_rounds'] > 0:
            stats['avg_adr'] = float(stats['total_damage'] / stats['total_rounds'])
            stats['avg_kills_per_round'] = float(stats['total_kills'] / stats['total_rounds'])

        if stats['total_kills'] > 0:
            stats['avg_hs_percent'] = float((stats['total_hs'] / stats['total_kills']) * 100)

        # Garantir que todos os valores são tipos Python nativos
        return {
            'total_kills': int(stats['total_kills']),
            'total_deaths': int(stats['total_deaths']),
            'total_damage': int(stats['total_damage']),
            'total_hs': int(stats['total_hs']),
            'total_rounds': int(stats['total_rounds']),
            'total_matches': int(stats['total_matches']),
            'avg_kd': float(stats['avg_kd']),
            'avg_adr': float(stats['avg_adr']),
            'avg_hs_percent': float(stats['avg_hs_percent']),
            'avg_kills_per_round': float(stats['avg_kills_per_round'])
        }

    except Exception as e:
        print(f"Erro ao buscar estatísticas do jogador: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# ==========================================
# TOURNAMENTS API
# ==========================================

@app.get("/api/tournaments")
def list_tournaments():
    """Lista todos os torneios detectados automaticamente"""
    try:
        campeonatos_dir = DEMOS_DIR / "campeonatos"
        tournaments = []

        if not campeonatos_dir.exists():
            return []

        # Listar todas as subpastas (cada uma é um torneio)
        for tournament_dir in campeonatos_dir.iterdir():
            if tournament_dir.is_dir() and tournament_dir.name != "README.md":
                # Buscar demos deste torneio no processed_demos
                processed_demos = monitor.get_processed_list()
                tournament_matches = [demo for demo in processed_demos if demo.get('tournament') == tournament_dir.name]

                tournaments.append({
                    'slug': tournament_dir.name,
                    'name': tournament_dir.name.replace('-', ' ').replace('_', ' ').title(),
                    'total_matches': len(tournament_matches),
                    'created_at': datetime.fromtimestamp(tournament_dir.stat().st_ctime).isoformat()
                })

        # Ordenar por data de criação (mais recente primeiro)
        tournaments.sort(key=lambda x: x['created_at'], reverse=True)
        return tournaments

    except Exception as e:
        print(f"Erro ao listar torneios: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/api/tournaments/{slug}")
def get_tournament(slug: str):
    """Retorna informações de um torneio específico"""
    try:
        # Buscar torneio no tournaments.json
        tournaments_file = BASE_DIR / "tournaments.json"
        tournament_data = None

        if tournaments_file.exists():
            with open(tournaments_file, 'r', encoding='utf-8') as f:
                tournaments = json.load(f)
                for t in tournaments:
                    if t['slug'] == slug:
                        tournament_data = t
                        break

        # Se não encontrou no tournaments.json, retornar erro
        if not tournament_data:
            # Fallback: verificar se a pasta existe
            campeonatos_dir = DEMOS_DIR / "campeonatos"
            tournament_dir = campeonatos_dir / slug
            if not tournament_dir.exists():
                return {"error": "Torneio não encontrado"}

            # Criar dados mínimos do torneio
            tournament_data = {
                'slug': slug,
                'name': slug.replace('-', ' ').replace('_', ' ').title(),
                'team_ids': [],
                'created_at': datetime.fromtimestamp(tournament_dir.stat().st_ctime).isoformat()
            }

        # Buscar demos deste torneio
        processed_demos = monitor.get_processed_list()
        tournament_matches = [demo for demo in processed_demos if demo.get('tournament') == slug]

        # Buscar times completos pelo IDs
        team_names = []
        if tournament_data.get('team_ids'):
            teams = get_teams_by_ids(tournament_data['team_ids'])
            team_names = [team['name'] for team in teams]

        return {
            'slug': tournament_data['slug'],
            'name': tournament_data.get('name', slug.replace('-', ' ').replace('_', ' ').title()),
            'description': tournament_data.get('description', ''),
            'logo': tournament_data.get('logo', ''),
            'start_date': tournament_data.get('start_date', ''),
            'end_date': tournament_data.get('end_date', ''),
            'prize_pool': tournament_data.get('prize_pool', ''),
            'format': tournament_data.get('format', ''),
            'location': tournament_data.get('location', ''),
            'prize_1st': tournament_data.get('prize_1st', ''),
            'prize_2nd': tournament_data.get('prize_2nd', ''),
            'prize_3rd': tournament_data.get('prize_3rd', ''),
            'team_ids': tournament_data.get('team_ids', []),
            'total_matches': len(tournament_matches),
            'teams': team_names,
            'created_at': tournament_data.get('created_at', '')
        }

    except Exception as e:
        print(f"Erro ao obter torneio: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/tournaments/{slug}/matches")
def get_tournament_matches(slug: str):
    """Lista todas as partidas de um torneio específico"""
    try:
        # Carregar times cadastrados
        teams_file = BASE_DIR / "teams.json"
        registered_teams = []
        if teams_file.exists():
            with open(teams_file, 'r', encoding='utf-8') as f:
                registered_teams = json.load(f)

        processed_demos = monitor.get_processed_list()
        tournament_matches = [demo for demo in processed_demos if demo.get('tournament') == slug]

        # Enriquecer com informações adicionais (mesma lógica do /api/matches)
        matches = []
        for demo in tournament_matches:
            demo_name = demo.get('demo_name', '')
            analysis_path = Path(demo.get('analysis_path', ''))

            match_info = {
                'demo_name': demo_name,
                'filename': demo.get('filename', ''),
                'processed_at': demo.get('processed_at', ''),
                'file_size': demo.get('file_size', 0),
                'status': 'ready',
                'tournament': slug
            }

            if analysis_path.exists():
                try:
                    match_json = analysis_path / "match_info.json"
                    if match_json.exists():
                        with open(match_json, 'r') as f:
                            info = json.load(f)
                            # Buscar mapa - pode estar em 'map' ou 'header.map_name'
                            match_info['map'] = info.get('map', info.get('header', {}).get('map_name', 'Unknown'))
                            score = info.get('score', {})
                            match_info['team2_score'] = score.get('team2_score', 0)
                            match_info['team3_score'] = score.get('team3_score', 0)
                            match_info['total_rounds'] = info.get('rounds', {}).get('total_rounds', score.get('total_rounds', 0))

                            # Extrair nomes dos times verificando nos times cadastrados
                            players = info.get('players', [])
                            team2_steamids = [str(p['steamid']) for p in players if p.get('team_number') == 2]
                            team3_steamids = [str(p['steamid']) for p in players if p.get('team_number') == 3]

                            # Função para encontrar o time de um jogador
                            def find_team_by_player(steamid_list):
                                for team in registered_teams:
                                    team_steamids = [str(p['steamid']) for p in team.get('players', [])]
                                    # Se algum jogador da partida está no time cadastrado
                                    if any(sid in team_steamids for sid in steamid_list):
                                        return team['name']
                                return None

                            # Buscar nomes reais dos times
                            match_info['team2_name'] = find_team_by_player(team2_steamids) or "Team 2"
                            match_info['team3_name'] = find_team_by_player(team3_steamids) or "Team 3"

                    stats_file = analysis_path / "player_stats.csv"
                    if stats_file.exists():
                        df = pd.read_csv(stats_file)
                        match_info['total_players'] = len(df)

                        if len(df) > 0:
                            top_player_row = df.nlargest(1, 'total_kills').iloc[0]
                            match_info['top_player'] = str(top_player_row['player'])
                            match_info['top_player_kills'] = int(top_player_row.get('total_kills', 0))

                        match_info['total_kills'] = int(df['total_kills'].sum())

                except Exception as e:
                    print(f"Erro ao carregar info de {demo_name}: {e}")

            matches.append(match_info)

        return {
            "tournament": slug,
            "total": len(matches),
            "matches": matches
        }

    except Exception as e:
        print(f"Erro ao listar partidas do torneio: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/tournaments/{slug}/players")
def get_tournament_players(slug: str, limit: int = 1000):
    """Lista jogadores de um torneio com stats agregadas"""
    try:
        processed_demos = monitor.get_processed_list()
        tournament_matches = [demo for demo in processed_demos if demo.get('tournament') == slug]

        players_stats = {}

        for demo in tournament_matches:
            analysis_path = Path(demo.get('analysis_path', ''))
            if not analysis_path.exists():
                continue

            match_info_file = analysis_path / "match_info.json"
            player_stats_file = analysis_path / "player_stats.csv"

            if not match_info_file.exists() or not player_stats_file.exists():
                continue

            with open(match_info_file, 'r', encoding='utf-8') as f:
                match_info = json.load(f)

            df = pd.read_csv(player_stats_file)

            for player in match_info.get('players', []):
                steamid = str(player['steamid'])
                player_name = player['name']

                player_row = df[df['player'] == player_name]
                if player_row.empty:
                    continue

                stats = player_row.iloc[0]

                if steamid not in players_stats:
                    players_stats[steamid] = {
                        'steamid': steamid,
                        'name': player_name,
                        'total_kills': 0,
                        'total_deaths': 0,
                        'total_matches': 0,
                        'total_damage': 0,
                        'total_hs': 0
                    }

                players_stats[steamid]['total_kills'] += int(stats.get('total_kills', 0))
                players_stats[steamid]['total_deaths'] += int(stats.get('deaths', 0))
                players_stats[steamid]['total_matches'] += 1
                players_stats[steamid]['total_damage'] += int(stats.get('total_damage', 0))
                players_stats[steamid]['total_hs'] += int(stats.get('headshot', 0))

        # Calcular K/D e preparar lista
        top_players = []
        for steamid, stats in players_stats.items():
            kd_ratio = stats['total_kills'] / stats['total_deaths'] if stats['total_deaths'] > 0 else float(stats['total_kills'])

            player_team_info = get_player_team_info(steamid)
            team_name = None
            team_logo = None
            photo = None

            if player_team_info:
                team = player_team_info.get('team', {})
                team_name = team.get('name')
                team_logo = team.get('logo')
                player_info = player_team_info.get('player_info', {})
                photo = player_info.get('photo')

            top_players.append({
                'steamid': steamid,
                'name': stats['name'],
                'kd_ratio': round(kd_ratio, 2),
                'total_kills': stats['total_kills'],
                'total_deaths': stats['total_deaths'],
                'total_matches': stats['total_matches'],
                'team_name': team_name,
                'team_logo': team_logo,
                'photo': photo
            })

        top_players.sort(key=lambda x: x['kd_ratio'], reverse=True)
        top_players = top_players[:limit]

        return top_players

    except Exception as e:
        print(f"Erro ao listar jogadores do torneio: {e}")
        import traceback
        traceback.print_exc()
        return []

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_teams_by_ids(team_ids):
    """Retorna os times completos baseado nos IDs"""
    try:
        teams_file = BASE_DIR / "teams.json"
        if not teams_file.exists():
            return []

        with open(teams_file, 'r', encoding='utf-8') as f:
            all_teams = json.load(f)

        # Filtrar apenas os times com IDs especificados
        return [team for team in all_teams if team['id'] in team_ids]
    except Exception as e:
        print(f"Erro ao carregar times: {e}")
        return []

# ==========================================
# TOURNAMENTS MANAGEMENT API (CRUD)
# ==========================================

@app.get("/api/manage-tournaments")
def list_managed_tournaments():
    """Lista todos os campeonatos cadastrados (do arquivo tournaments.json)"""
    try:
        tournaments_file = BASE_DIR / "tournaments.json"
        tournaments = []

        if tournaments_file.exists():
            with open(tournaments_file, 'r', encoding='utf-8') as f:
                tournaments = json.load(f)

        # Enriquecer com número de partidas
        for tournament in tournaments:
            processed_demos = monitor.get_processed_list()
            tournament_matches = [demo for demo in processed_demos if demo.get('tournament') == tournament['slug']]
            tournament['total_matches'] = len(tournament_matches)

        return tournaments
    except Exception as e:
        print(f"Erro ao listar campeonatos gerenciados: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/api/manage-tournaments/{slug}")
def get_managed_tournament(slug: str):
    """Retorna informações de um campeonato específico"""
    try:
        tournaments_file = BASE_DIR / "tournaments.json"

        if not tournaments_file.exists():
            return {"error": "Nenhum campeonato cadastrado"}

        with open(tournaments_file, 'r', encoding='utf-8') as f:
            tournaments = json.load(f)

        for tournament in tournaments:
            if tournament['slug'] == slug:
                # Enriquecer com número de partidas
                processed_demos = monitor.get_processed_list()
                tournament_matches = [demo for demo in processed_demos if demo.get('tournament') == slug]
                tournament['total_matches'] = len(tournament_matches)
                return tournament

        return {"error": "Campeonato não encontrado"}
    except Exception as e:
        print(f"Erro ao obter campeonato: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/api/manage-tournaments")
async def create_tournament(tournament_data: dict):
    """Cria um novo campeonato e sua pasta"""
    try:
        # Gerar slug a partir do nome
        name = tournament_data.get("name", "")
        slug = name.lower()\
            .replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')\
            .replace('ã', 'a').replace('õ', 'o').replace('ç', 'c')\
            .replace(' ', '-').replace('_', '-')

        # Remover caracteres especiais
        import re
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')

        if not slug:
            return {"error": "Nome inválido para gerar slug"}

        # Usar context manager com file locking
        with locked_tournaments_file('r+') as (f, tournaments):
            # Verificar duplicata
            for t in tournaments:
                if t['slug'] == slug:
                    return {"error": f"Já existe um campeonato com o slug '{slug}'"}

            # Criar pasta do campeonato
            tournament_dir = DEMOS_DIR / "campeonatos" / slug
            tournament_dir.mkdir(parents=True, exist_ok=True)

            # Adicionar campeonato ao arquivo
            new_tournament = {
                "slug": slug,
                "name": name,
                "description": tournament_data.get("description", ""),
                "start_date": tournament_data.get("start_date", ""),
                "end_date": tournament_data.get("end_date", ""),
                "logo": tournament_data.get("logo", ""),
                "prize_pool": tournament_data.get("prize_pool", ""),
                "format": tournament_data.get("format", ""),
                "location": tournament_data.get("location", ""),
                "prize_1st": tournament_data.get("prize_1st", ""),
                "prize_2nd": tournament_data.get("prize_2nd", ""),
                "prize_3rd": tournament_data.get("prize_3rd", ""),
                "team_ids": tournament_data.get("team_ids", []),
                "bracket": tournament_data.get("bracket"),
                "created_at": datetime.now().isoformat()
            }

            tournaments.append(new_tournament)

            # Escrever de volta ao arquivo (com lock exclusivo ativo)
            f.seek(0)
            json.dump(tournaments, f, indent=2, ensure_ascii=False)
            f.truncate()

            print(f"✅ Campeonato criado: {slug}")
            print(f"📁 Pasta criada em: {tournament_dir}")
            print(f"👥 Times selecionados: {len(new_tournament.get('team_ids', []))}")

            return {"success": True, "slug": slug}
    except Exception as e:
        print(f"Erro ao criar campeonato: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.put("/api/manage-tournaments/{slug}")
async def update_tournament(slug: str, tournament_data: dict):
    """Atualiza um campeonato (não altera o slug ou pasta)"""
    try:
        # Usar context manager com file locking
        with locked_tournaments_file('r+') as (f, tournaments):
            # Encontrar e atualizar campeonato
            found = False
            for i, tournament in enumerate(tournaments):
                if tournament['slug'] == slug:
                    tournaments[i] = {
                        "slug": slug,  # Slug não muda
                        "name": tournament_data.get("name"),
                        "description": tournament_data.get("description", ""),
                        "start_date": tournament_data.get("start_date", ""),
                        "end_date": tournament_data.get("end_date", ""),
                        "logo": tournament_data.get("logo", ""),
                        "prize_pool": tournament_data.get("prize_pool", tournament.get("prize_pool", "")),
                        "format": tournament_data.get("format", tournament.get("format", "")),
                        "location": tournament_data.get("location", tournament.get("location", "")),
                        "prize_1st": tournament_data.get("prize_1st", tournament.get("prize_1st", "")),
                        "prize_2nd": tournament_data.get("prize_2nd", tournament.get("prize_2nd", "")),
                        "prize_3rd": tournament_data.get("prize_3rd", tournament.get("prize_3rd", "")),
                        "team_ids": tournament_data.get("team_ids", tournament.get("team_ids", [])),
                        "bracket": tournament_data.get("bracket", tournament.get("bracket")),
                        "created_at": tournament.get("created_at", datetime.now().isoformat()),
                        "updated_at": datetime.now().isoformat()
                    }
                    found = True
                    break

            if not found:
                return {"error": "Campeonato não encontrado"}

            # Escrever de volta ao arquivo (com lock exclusivo ativo)
            f.seek(0)
            json.dump(tournaments, f, indent=2, ensure_ascii=False)
            f.truncate()

            print(f"✅ Campeonato atualizado: {slug}")
            return {"success": True}
    except Exception as e:
        print(f"Erro ao atualizar campeonato: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.delete("/api/manage-tournaments/{slug}")
def delete_tournament(slug: str):
    """Exclui um campeonato (apenas metadados, não exclui pasta)"""
    try:
        # Usar context manager com file locking
        with locked_tournaments_file('r+') as (f, tournaments):
            # Remover campeonato
            tournaments = [t for t in tournaments if t['slug'] != slug]

            # Escrever de volta ao arquivo (com lock exclusivo ativo)
            f.seek(0)
            json.dump(tournaments, f, indent=2, ensure_ascii=False)
            f.truncate()

            print(f"✅ Campeonato excluído: {slug}")
            print(f"⚠️  A pasta demos/campeonatos/{slug} não foi excluída")
            return {"success": True}
    except Exception as e:
        print(f"Erro ao excluir campeonato: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# ==========================================
# TEAMS MANAGEMENT API
# ==========================================

@app.get("/teams", response_class=HTMLResponse)
def teams_page(request: Request):
    """Página de gerenciamento de times"""
    return templates.TemplateResponse("teams.html", {"request": request})

@app.get("/api/teams")
def get_teams():
    """API para listar todos os times"""
    try:
        teams_file = BASE_DIR / "teams.json"
        if teams_file.exists():
            with open(teams_file, 'r', encoding='utf-8') as f:
                teams = json.load(f)
            return teams
        return []
    except Exception as e:
        print(f"Erro ao carregar times: {e}")
        return []

@app.get("/api/teams/{team_id}")
def get_team(team_id: str):
    """API para obter um time específico"""
    try:
        teams_file = BASE_DIR / "teams.json"
        if teams_file.exists():
            with open(teams_file, 'r', encoding='utf-8') as f:
                teams = json.load(f)
            
            for team in teams:
                if team['id'] == team_id:
                    return team
            return {"error": "Time não encontrado"}
        return {"error": "Nenhum time cadastrado"}
    except Exception as e:
        print(f"Erro ao carregar time: {e}")
        return {"error": "Erro interno"}

@app.post("/api/teams")
async def create_team(team_data: dict):
    """API para criar um novo time"""
    try:
        teams_file = BASE_DIR / "teams.json"
        teams = []
        
        if teams_file.exists():
            with open(teams_file, 'r', encoding='utf-8') as f:
                teams = json.load(f)
        
        # Gerar ID único
        team_id = f"team_{int(time.time())}"
        
        new_team = {
            "id": team_id,
            "name": team_data.get("name"),
            "logo": team_data.get("logo", ""),
            "players": team_data.get("players", []),
            "created_at": datetime.now().isoformat()
        }
        
        teams.append(new_team)
        
        with open(teams_file, 'w', encoding='utf-8') as f:
            json.dump(teams, f, indent=2, ensure_ascii=False)
        
        return {"success": True, "team_id": team_id}
    except Exception as e:
        print(f"Erro ao criar time: {e}")
        return {"error": "Erro interno"}

@app.put("/api/teams/{team_id}")
async def update_team(team_id: str, team_data: dict):
    """API para atualizar um time"""
    try:
        teams_file = BASE_DIR / "teams.json"
        if not teams_file.exists():
            return {"error": "Nenhum time cadastrado"}
        
        with open(teams_file, 'r', encoding='utf-8') as f:
            teams = json.load(f)
        
        for i, team in enumerate(teams):
            if team['id'] == team_id:
                teams[i] = {
                    "id": team_id,
                    "name": team_data.get("name"),
                    "logo": team_data.get("logo", ""),
                    "players": team_data.get("players", []),
                    "created_at": team.get("created_at", datetime.now().isoformat()),
                    "updated_at": datetime.now().isoformat()
                }
                
                with open(teams_file, 'w', encoding='utf-8') as f:
                    json.dump(teams, f, indent=2, ensure_ascii=False)
                
                return {"success": True}
        
        return {"error": "Time não encontrado"}
    except Exception as e:
        print(f"Erro ao atualizar time: {e}")
        return {"error": "Erro interno"}

@app.delete("/api/teams/{team_id}")
def delete_team(team_id: str):
    """API para excluir um time"""
    try:
        teams_file = BASE_DIR / "teams.json"
        if not teams_file.exists():
            return {"error": "Nenhum time cadastrado"}
        
        with open(teams_file, 'r', encoding='utf-8') as f:
            teams = json.load(f)
        
        teams = [team for team in teams if team['id'] != team_id]
        
        with open(teams_file, 'w', encoding='utf-8') as f:
            json.dump(teams, f, indent=2, ensure_ascii=False)
        
        return {"success": True}
    except Exception as e:
        print(f"Erro ao excluir time: {e}")
        return {"error": "Erro interno"}

@app.get("/api/steamids")
def get_steam_ids():
    """API para obter todas as Steam IDs encontradas nas demos"""
    try:
        steam_ids = []
        analysis_dir = ANALYSIS_DIR

        if analysis_dir.exists():
            for demo_dir in analysis_dir.iterdir():
                if demo_dir.is_dir():
                    match_info_file = demo_dir / "match_info.json"
                    if match_info_file.exists():
                        with open(match_info_file, 'r', encoding='utf-8') as f:
                            match_info = json.load(f)

                        for player in match_info.get('players', []):
                            steamid = str(player['steamid'])

                            # Buscar informações do jogador no teams.json
                            player_team_info = get_player_team_info(steamid)
                            photo = None

                            if player_team_info and player_team_info.get('player_info'):
                                photo = player_team_info['player_info'].get('photo')

                            steam_ids.append({
                                'steamid': steamid,
                                'name': player['name'],
                                'demo_name': demo_dir.name,
                                'photo': photo
                            })

        # Remover duplicatas (manter o primeiro encontrado)
        unique_steam_ids = []
        seen_steamids = set()
        for steam_id in steam_ids:
            if steam_id['steamid'] not in seen_steamids:
                unique_steam_ids.append(steam_id)
                seen_steamids.add(steam_id['steamid'])

        return unique_steam_ids
    except Exception as e:
        print(f"Erro ao carregar Steam IDs: {e}")
        return []

@app.get("/api/top-players")
def get_top_players(limit: int = 8):
    """API para obter os top jogadores baseado em K/D ratio"""
    try:
        players_stats = {}  # Dict para agregar stats por steamid
        analysis_dir = ANALYSIS_DIR

        print(f"🔍 Top Players: Analisando diretório {analysis_dir}")

        if not analysis_dir.exists():
            print(f"❌ Diretório {analysis_dir} não existe")
            return []

        # Iterar por todas as demos
        for demo_dir in analysis_dir.iterdir():
            if not demo_dir.is_dir():
                continue

            print(f"📁 Processando demo: {demo_dir.name}")

            match_info_file = demo_dir / "match_info.json"
            player_stats_file = demo_dir / "player_stats.csv"

            if not match_info_file.exists() or not player_stats_file.exists():
                print(f"⚠️  Arquivos faltando em {demo_dir.name}")
                continue

            # Carregar match_info para obter steamids
            with open(match_info_file, 'r', encoding='utf-8') as f:
                match_info = json.load(f)

            # Carregar stats dos jogadores
            df = pd.read_csv(player_stats_file)
            print(f"  📊 {len(df)} jogadores no CSV")

            # Para cada jogador na partida
            players_in_match = match_info.get('players', [])
            print(f"  👥 {len(players_in_match)} jogadores no match_info")

            for player in players_in_match:
                steamid = str(player['steamid'])
                player_name = player['name']

                # Encontrar stats do jogador no CSV
                player_row = df[df['player'] == player_name]
                if player_row.empty:
                    print(f"    ⚠️  {player_name} não encontrado no CSV")
                    continue

                stats = player_row.iloc[0]

                # Inicializar jogador se não existe
                if steamid not in players_stats:
                    players_stats[steamid] = {
                        'steamid': steamid,
                        'name': player_name,
                        'total_kills': 0,
                        'total_deaths': 0,
                        'total_matches': 0,
                        'total_damage': 0,
                        'total_hs': 0
                    }
                    print(f"    ✅ Adicionado: {player_name} ({steamid})")

                # Agregar estatísticas
                players_stats[steamid]['total_kills'] += int(stats.get('total_kills', 0))
                players_stats[steamid]['total_deaths'] += int(stats.get('deaths', 0))
                players_stats[steamid]['total_matches'] += 1
                players_stats[steamid]['total_damage'] += int(stats.get('total_damage', 0))
                players_stats[steamid]['total_hs'] += int(stats.get('headshot', 0))

        # Calcular K/D ratio e preparar lista final
        top_players = []
        for steamid, stats in players_stats.items():
            # Calcular K/D
            kd_ratio = stats['total_kills'] / stats['total_deaths'] if stats['total_deaths'] > 0 else float(stats['total_kills'])

            # Calcular HS%
            hs_percent = round((stats['total_hs'] / stats['total_kills'] * 100) if stats['total_kills'] > 0 else 0, 1)

            # Calcular rating simplificado (baseado em HLTV rating 2.0)
            # Rating = 0.0073*KAST + 0.3591*KPR - 0.5329*DPR + 0.2372*Impact + 0.0032*ADR + 0.1587
            # Simplificado: baseado apenas em K/D e impacto
            rating = round(0.5 + (kd_ratio - 1) * 0.4, 2)

            # Buscar informações do time
            player_team_info = get_player_team_info(steamid)
            team_name = None
            team_logo = None
            photo = None

            if player_team_info:
                team = player_team_info.get('team', {})
                team_name = team.get('name')
                team_logo = team.get('logo')
                player_info = player_team_info.get('player_info', {})
                photo = player_info.get('photo')

            top_players.append({
                'steamid': steamid,
                'name': stats['name'],
                'kd_ratio': round(kd_ratio, 2),
                'total_kills': stats['total_kills'],
                'total_deaths': stats['total_deaths'],
                'total_matches': stats['total_matches'],
                'hs_percent': hs_percent,
                'rating': rating,
                'team_name': team_name,
                'team_logo': team_logo,
                'photo': photo
            })

        # Ordenar por K/D ratio (maior para menor) e limitar
        top_players.sort(key=lambda x: x['kd_ratio'], reverse=True)
        top_players = top_players[:limit]

        return top_players

    except Exception as e:
        print(f"Erro ao carregar top players: {e}")
        import traceback
        traceback.print_exc()
        return []

def detect_team_by_steamids(player_steamids):
    """Detecta o time baseado nas Steam IDs dos jogadores"""
    try:
        teams_file = BASE_DIR / "teams.json"
        if not teams_file.exists():
            return None

        with open(teams_file, 'r', encoding='utf-8') as f:
            teams = json.load(f)

        # Converter para set para comparação mais eficiente
        player_steamids_set = set(str(sid) for sid in player_steamids)

        for team in teams:
            team_steamids = set(str(player['steamid']) for player in team.get('players', []))

            # Verificar quantos jogadores do time estão presentes
            matching_players = player_steamids_set.intersection(team_steamids)

            # Se pelo menos 3 jogadores do time estão presentes, detecta o time
            if len(matching_players) >= 3:
                return team

        return None
    except Exception as e:
        print(f"Erro ao detectar time: {e}")
        return None

def get_player_team_info(player_steamid):
    """Obtém informações do time para um jogador específico"""
    try:
        teams_file = BASE_DIR / "teams.json"
        if not teams_file.exists():
            print(f"⚠️  teams.json não encontrado em {teams_file}")
            return None

        with open(teams_file, 'r', encoding='utf-8') as f:
            teams = json.load(f)

        player_steamid_str = str(player_steamid)

        for team in teams:
            for player in team.get('players', []):
                if str(player['steamid']) == player_steamid_str:
                    return {
                        'team': team,
                        'player_info': player
                    }

        return None
    except Exception as e:
        print(f"❌ Erro ao obter info do time: {e}")
        import traceback
        traceback.print_exc()
        return None

# ==========================================
# BRACKET MANAGEMENT
# ==========================================

def update_tournament_bracket(tournament_slug):
    """
    Atualiza o bracket de um torneio baseado nos resultados das partidas processadas.
    Calcula automaticamente os confrontos das rodadas seguintes.
    """
    try:
        # Carregar torneio com file locking (leitura)
        with locked_tournaments_file('r') as (_, tournaments):
            tournament = None
            tournament_index = None
            for i, t in enumerate(tournaments):
                if t['slug'] == tournament_slug:
                    tournament = t
                    tournament_index = i
                    break

            if not tournament or not tournament.get('bracket'):
                return {"error": "Torneio ou bracket não encontrado"}

        # Carregar times
        teams_file = BASE_DIR / "teams.json"
        teams = []
        if teams_file.exists():
            with open(teams_file, 'r', encoding='utf-8') as f:
                teams = json.load(f)

        # Carregar partidas processadas do torneio
        processed_demos = monitor.get_processed_list()
        tournament_matches = [demo for demo in processed_demos if demo.get('tournament') == tournament_slug]

        # Função auxiliar para obter nome do time pelo ID
        def get_team_name(team_id):
            for team in teams:
                if team['id'] == team_id:
                    return team['name']
            return None

        # Função auxiliar para verificar resultado de uma partida
        def get_match_result(team1_name, team2_name):
            """Retorna o vencedor de uma partida entre dois times, ou None se não jogaram"""
            for match in tournament_matches:
                analysis_path = Path(match.get('analysis_path', ''))
                if not analysis_path.exists():
                    continue

                try:
                    match_json = analysis_path / "match_info.json"
                    if match_json.exists():
                        with open(match_json, 'r') as f:
                            info = json.load(f)

                            # Extrair nomes dos times do match
                            players = info.get('players', [])
                            team2_steamids = [str(p['steamid']) for p in players if p.get('team_number') == 2]
                            team3_steamids = [str(p['steamid']) for p in players if p.get('team_number') == 3]

                            def find_team_by_players(steamid_list):
                                for team in teams:
                                    team_steamids = [str(p['steamid']) for p in team.get('players', [])]
                                    if any(sid in team_steamids for sid in steamid_list):
                                        return team['name']
                                return None

                            match_team2_name = find_team_by_players(team2_steamids)
                            match_team3_name = find_team_by_players(team3_steamids)

                            # Verificar se é a partida que estamos procurando
                            teams_match = {match_team2_name, match_team3_name}
                            teams_search = {team1_name, team2_name}

                            if teams_match == teams_search:
                                # Encontramos a partida! Verificar quem ganhou
                                score = info.get('score', {})
                                team2_score = score.get('team2_score', 0)
                                team3_score = score.get('team3_score', 0)

                                if team2_score > team3_score:
                                    return match_team2_name
                                elif team3_score > team2_score:
                                    return match_team3_name
                                else:
                                    return None  # Empate (não deveria acontecer em CS)

                except Exception as e:
                    print(f"Erro ao processar partida: {e}")
                    continue

            return None

        # Atualizar bracket
        bracket = tournament['bracket']

        # Processar Upper Bracket - Opening Round
        if 'upper_bracket' in bracket and 'opening_round' in bracket['upper_bracket']:
            opening_matches = bracket['upper_bracket']['opening_round']

            # Preparar próximas rodadas se não existirem
            if 'quarters' not in bracket['upper_bracket']:
                bracket['upper_bracket']['quarters'] = []

            quarters = bracket['upper_bracket']['quarters']

            # Processar cada partida da opening round
            for match in opening_matches:
                team1_id = match.get('team1_id')
                team2_id = match.get('team2_id')
                team1_name = get_team_name(team1_id)
                team2_name = get_team_name(team2_id)

                if team1_name and team2_name:
                    winner = get_match_result(team1_name, team2_name)

                    if winner:
                        match['status'] = 'completed'
                        match['winner'] = team1_id if winner == team1_name else team2_id
                        match['loser'] = team2_id if winner == team1_name else team1_id

            # Construir Quarters baseado nos vencedores da Opening Round
            if len(opening_matches) >= 4:
                # Quarter 1: Vencedor Opening 1 vs Vencedor Opening 2
                winner1 = opening_matches[0].get('winner') if opening_matches[0].get('status') == 'completed' else None
                winner2 = opening_matches[1].get('winner') if opening_matches[1].get('status') == 'completed' else None

                if len(quarters) == 0:
                    quarters.append({
                        'match_id': 'ub_quarters_1',
                        'team1_id': winner1,
                        'team2_id': winner2,
                        'status': 'pending' if (winner1 and winner2) else 'waiting'
                    })
                    quarters.append({
                        'match_id': 'ub_quarters_2',
                        'team1_id': None,
                        'team2_id': None,
                        'status': 'waiting'
                    })
                else:
                    if winner1 and winner2:
                        quarters[0]['team1_id'] = winner1
                        quarters[0]['team2_id'] = winner2
                        quarters[0]['status'] = 'pending'

                # Quarter 2: Vencedor Opening 3 vs Vencedor Opening 4
                winner3 = opening_matches[2].get('winner') if opening_matches[2].get('status') == 'completed' else None
                winner4 = opening_matches[3].get('winner') if opening_matches[3].get('status') == 'completed' else None

                if len(quarters) >= 2:
                    if winner3 and winner4:
                        quarters[1]['team1_id'] = winner3
                        quarters[1]['team2_id'] = winner4
                        quarters[1]['status'] = 'pending'

            # Verificar resultados das quarters
            for quarter_match in quarters:
                if quarter_match.get('status') == 'pending':
                    team1_id = quarter_match.get('team1_id')
                    team2_id = quarter_match.get('team2_id')
                    team1_name = get_team_name(team1_id)
                    team2_name = get_team_name(team2_id)

                    if team1_name and team2_name:
                        winner = get_match_result(team1_name, team2_name)

                        if winner:
                            quarter_match['status'] = 'completed'
                            quarter_match['winner'] = team1_id if winner == team1_name else team2_id
                            quarter_match['loser'] = team2_id if winner == team1_name else team1_id

        # ========================================
        # PROCESSAR LOWER BRACKET
        # ========================================
        if 'lower_bracket' not in bracket:
            bracket['lower_bracket'] = {}

        # Lower Round 1: Perdedores do Opening Round
        if 'upper_bracket' in bracket and 'opening_round' in bracket['upper_bracket']:
            opening_matches = bracket['upper_bracket']['opening_round']

            # Coletar perdedores do Opening Round
            losers_opening = []
            for match in opening_matches:
                if match.get('status') == 'completed' and match.get('loser'):
                    losers_opening.append(match['loser'])

            # Criar Lower Round 1 com os perdedores (2 partidas com 4 perdedores)
            if 'round1' not in bracket['lower_bracket']:
                bracket['lower_bracket']['round1'] = []

            lr1_matches = bracket['lower_bracket']['round1']

            if len(losers_opening) >= 4:
                # LR1 Match 1: Loser Opening 1 vs Loser Opening 2
                if len(lr1_matches) == 0:
                    lr1_matches.append({
                        'match_id': 'lb_r1_1',
                        'team1_id': losers_opening[0] if len(losers_opening) > 0 else None,
                        'team2_id': losers_opening[1] if len(losers_opening) > 1 else None,
                        'status': 'pending' if len(losers_opening) >= 2 else 'waiting'
                    })
                    lr1_matches.append({
                        'match_id': 'lb_r1_2',
                        'team1_id': losers_opening[2] if len(losers_opening) > 2 else None,
                        'team2_id': losers_opening[3] if len(losers_opening) > 3 else None,
                        'status': 'pending' if len(losers_opening) >= 4 else 'waiting'
                    })
                else:
                    # Atualizar partidas existentes
                    if len(lr1_matches) >= 1:
                        lr1_matches[0]['team1_id'] = losers_opening[0]
                        lr1_matches[0]['team2_id'] = losers_opening[1]
                        lr1_matches[0]['status'] = 'pending'

                    if len(lr1_matches) >= 2:
                        lr1_matches[1]['team1_id'] = losers_opening[2]
                        lr1_matches[1]['team2_id'] = losers_opening[3]
                        lr1_matches[1]['status'] = 'pending'

            # Verificar resultados do LR1
            for lr1_match in lr1_matches:
                if lr1_match.get('status') == 'pending':
                    team1_id = lr1_match.get('team1_id')
                    team2_id = lr1_match.get('team2_id')
                    team1_name = get_team_name(team1_id)
                    team2_name = get_team_name(team2_id)

                    if team1_name and team2_name:
                        winner = get_match_result(team1_name, team2_name)

                        if winner:
                            lr1_match['status'] = 'completed'
                            lr1_match['winner'] = team1_id if winner == team1_name else team2_id
                            lr1_match['loser'] = team2_id if winner == team1_name else team1_id

        # Lower Round 2: Vencedores LR1 + Perdedores Quarters
        if 'round2' not in bracket['lower_bracket']:
            bracket['lower_bracket']['round2'] = []

        lr2_matches = bracket['lower_bracket']['round2']

        # Coletar vencedores do LR1
        lr1_winners = []
        if 'round1' in bracket['lower_bracket']:
            for match in bracket['lower_bracket']['round1']:
                if match.get('status') == 'completed' and match.get('winner'):
                    lr1_winners.append(match['winner'])

        # Coletar perdedores das Quarters
        losers_quarters = []
        if 'upper_bracket' in bracket and 'quarters' in bracket['upper_bracket']:
            for match in bracket['upper_bracket']['quarters']:
                if match.get('status') == 'completed' and match.get('loser'):
                    losers_quarters.append(match['loser'])

        # Criar LR2 Matches
        if len(lr1_winners) >= 2 and len(losers_quarters) >= 2:
            if len(lr2_matches) == 0:
                lr2_matches.append({
                    'match_id': 'lb_r2_1',
                    'team1_id': lr1_winners[0] if len(lr1_winners) > 0 else None,
                    'team2_id': losers_quarters[0] if len(losers_quarters) > 0 else None,
                    'status': 'pending'
                })
                lr2_matches.append({
                    'match_id': 'lb_r2_2',
                    'team1_id': lr1_winners[1] if len(lr1_winners) > 1 else None,
                    'team2_id': losers_quarters[1] if len(losers_quarters) > 1 else None,
                    'status': 'pending'
                })
            else:
                if len(lr2_matches) >= 1:
                    lr2_matches[0]['team1_id'] = lr1_winners[0]
                    lr2_matches[0]['team2_id'] = losers_quarters[0]
                    lr2_matches[0]['status'] = 'pending'

                if len(lr2_matches) >= 2:
                    lr2_matches[1]['team1_id'] = lr1_winners[1]
                    lr2_matches[1]['team2_id'] = losers_quarters[1]
                    lr2_matches[1]['status'] = 'pending'

        # Verificar resultados do LR2
        for lr2_match in lr2_matches:
            if lr2_match.get('status') == 'pending':
                team1_id = lr2_match.get('team1_id')
                team2_id = lr2_match.get('team2_id')
                team1_name = get_team_name(team1_id)
                team2_name = get_team_name(team2_id)

                if team1_name and team2_name:
                    winner = get_match_result(team1_name, team2_name)

                    if winner:
                        lr2_match['status'] = 'completed'
                        lr2_match['winner'] = team1_id if winner == team1_name else team2_id
                        lr2_match['loser'] = team2_id if winner == team1_name else team1_id

        # Salvar bracket atualizado com file locking (escrita)
        with locked_tournaments_file('r+') as (f, tournaments_latest):
            # Re-localizar o torneio (pode ter mudado desde a leitura inicial)
            for i, t in enumerate(tournaments_latest):
                if t['slug'] == tournament_slug:
                    tournaments_latest[i] = tournament
                    break

            # Escrever de volta ao arquivo (com lock exclusivo ativo)
            f.seek(0)
            json.dump(tournaments_latest, f, indent=2, ensure_ascii=False)
            f.truncate()

        return {"success": True, "bracket": bracket}

    except Exception as e:
        print(f"Erro ao atualizar bracket: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/tournaments/{slug}/bracket")
def get_tournament_bracket(slug: str):
    """Retorna o bracket atualizado de um torneio"""
    try:
        # Atualizar bracket baseado nos resultados
        result = update_tournament_bracket(slug)

        if 'error' in result:
            return result

        # Carregar torneio atualizado
        tournaments_file = BASE_DIR / "tournaments.json"
        with open(tournaments_file, 'r', encoding='utf-8') as f:
            tournaments = json.load(f)

        tournament = None
        for t in tournaments:
            if t['slug'] == slug:
                tournament = t
                break

        if not tournament or not tournament.get('bracket'):
            return {"error": "Torneio ou bracket não encontrado"}

        # Carregar nomes dos times para o frontend
        teams_file = BASE_DIR / "teams.json"
        teams = {}
        if teams_file.exists():
            with open(teams_file, 'r', encoding='utf-8') as f:
                teams_list = json.load(f)
                teams = {team['id']: team for team in teams_list}

        return {
            "bracket": tournament['bracket'],
            "teams": teams
        }

    except Exception as e:
        print(f"Erro ao obter bracket: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
