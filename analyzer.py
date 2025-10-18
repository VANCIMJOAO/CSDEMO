from demoparser2 import DemoParser
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from rich.console import Console

console = Console()

class CS2DemoAnalyzer:
    def __init__(self, demo_path: str):
        self.demo_path = demo_path
        self.parser = DemoParser(demo_path)
        self.demo_name = Path(demo_path).stem
        self.results = {}

    def extract_match_info(self):
        """Extrai informações básicas da partida"""
        console.print("📊 Extraindo informações da partida...", style="bold cyan")
        header = self.parser.parse_header()
        player_info = self.parser.parse_player_info()

        # Calcular score final
        score_info = self.calculate_final_score(player_info)

        return {
            'demo_name': self.demo_name,
            'header': header,
            'players': player_info.to_dict('records') if not player_info.empty else [],
            'score': score_info,
            'extraction_time': datetime.now().isoformat()
        }

    def calculate_final_score(self, player_info):
        """Calcula o placar final usando propriedades team_rounds_total do game state"""
        try:
            console.print("🎯 Calculando placar final...", style="bold cyan")

            # Identificar jogadores de cada time organizacional
            team2_players = set(player_info[player_info['team_number'] == 2]['name'].tolist())
            team3_players = set(player_info[player_info['team_number'] == 3]['name'].tolist())

            if not team2_players or not team3_players:
                console.print("⚠️  Times não identificados", style="bold yellow")
                return {'team2_score': 0, 'team3_score': 0, 'total_rounds': 0}

            team2_player = list(team2_players)[0]
            team3_player = list(team3_players)[0]

            # Obter total de rounds da partida
            round_end = self.parser.parse_event("round_end", other=["total_rounds_played"])
            total_rounds = int(round_end['total_rounds_played'].max()) if not round_end.empty else 0

            console.print(f"  Team 2 player: {team2_player}", style="dim")
            console.print(f"  Team 3 player: {team3_player}", style="dim")
            console.print(f"  Extraindo team_rounds_total...", style="dim")

            # Extrair team_rounds_total para TODOS os jogadores em TODOS os ticks
            # Isso nos dá o score de cada time ao longo do jogo
            ticks_data = self.parser.parse_ticks(["team_rounds_total", "team_clan_name"])

            if ticks_data.empty:
                console.print("⚠️  Não foi possível extrair team_rounds_total", style="bold yellow")
                return {'team2_score': 0, 'team3_score': 0, 'total_rounds': total_rounds}

            # Filtrar apenas pelos jogadores que identificamos de cada time
            team2_data = ticks_data[ticks_data['name'] == team2_player]
            team3_data = ticks_data[ticks_data['name'] == team3_player]

            if team2_data.empty or team3_data.empty:
                console.print("⚠️  Dados de time não encontrados", style="bold yellow")
                return {'team2_score': 0, 'team3_score': 0, 'total_rounds': total_rounds}

            # Pegar o score máximo (final) de cada time
            team2_score = int(team2_data['team_rounds_total'].max())
            team3_score = int(team3_data['team_rounds_total'].max())

            console.print(f"✅ Score: Team2 {team2_score} x {team3_score} Team3 (Total: {total_rounds} rounds)", style="bold green")

            return {
                'team2_score': team2_score,
                'team3_score': team3_score,
                'total_rounds': total_rounds
            }

        except Exception as e:
            console.print(f"❌ Erro ao calcular score: {str(e)}", style="bold red")
            import traceback
            traceback.print_exc()
            return {'team2_score': 0, 'team3_score': 0, 'total_rounds': 0}

    def extract_kills_analysis(self):
        """Análise completa de kills com dados abrangentes"""
        console.print("💀 Analisando kills...", style="bold red")
        try:
            result = self.parser.parse_event(
                "player_death",
                player=["X", "Y", "Z", "name", "team_name"],
                other=[
                    "user_name", "user_team_name",
                    "attacker_name", "attacker_team_name",
                    "weapon", "headshot", "penetrated",
                    "thrusmoke", "attackerblind", "noscope", "distance",
                    "total_rounds_played", "hitgroup"
                ]
            )
            console.print(f"✅ {len(result)} kills encontrados", style="bold green")
            return result
        except Exception as e:
            console.print(f"❌ Erro: {str(e)}", style="bold red")
            return pd.DataFrame()

    def extract_damage_analysis(self):
        """Análise de dano com hitgroups"""
        console.print("🎯 Analisando dano...", style="bold yellow")
        try:
            result = self.parser.parse_event(
                "player_hurt",
                player=["X", "Y", "Z", "health", "armor_value", "name", "team_name"],
                other=[
                    "attacker_name", "attacker_team_name",
                    "weapon", "dmg_health", "dmg_armor",
                    "hitgroup", "total_rounds_played"
                ]
            )
            console.print(f"✅ {len(result)} eventos de dano", style="bold green")
            return result
        except Exception as e:
            console.print(f"❌ Erro: {str(e)}", style="bold red")
            return pd.DataFrame()

    def extract_grenades(self):
        """Extrai dados de granadas (trajetórias e detonações)"""
        console.print("💣 Analisando granadas...", style="bold magenta")
        try:
            grenades = self.parser.parse_grenades()
            console.print(f"✅ {len(grenades)} eventos de granada", style="bold green")
            return grenades
        except Exception as e:
            console.print(f"❌ Erro: {str(e)}", style="bold red")
            return pd.DataFrame()

    def extract_round_summaries(self):
        """Análise detalhada de rounds"""
        console.print("🔄 Analisando rounds...", style="bold blue")
        rounds = {}
        try:
            rounds['start'] = self.parser.parse_event("round_start", other=["total_rounds_played"])
        except:
            rounds['start'] = pd.DataFrame()

        try:
            rounds['end'] = self.parser.parse_event("round_end", other=["winner", "reason", "total_rounds_played"])
        except:
            rounds['end'] = pd.DataFrame()

        # Análise detalhada por round
        rounds['detailed'] = self.analyze_rounds_detailed()
        return rounds

    def analyze_rounds_detailed(self):
        """Análise detalhada de cada round"""
        try:
            kills_df = self.results.get('kills', pd.DataFrame())
            if kills_df.empty:
                return pd.DataFrame()

            round_stats = []
            for round_num in sorted(kills_df['total_rounds_played'].unique()):
                round_data = kills_df[kills_df['total_rounds_played'] == round_num]

                round_info = {
                    'round': int(round_num),
                    'total_kills': len(round_data),
                    'ct_kills': len(round_data[round_data['attacker_team_name'] == 'CT']),
                    't_kills': len(round_data[round_data['attacker_team_name'].isin(['T', 'TERRORIST'])]),
                    'headshots': int(round_data['headshot'].sum()),
                    'penetrated': int(round_data['penetrated'].sum()),
                    'thrusmoke': int(round_data['thrusmoke'].sum()),
                    'avg_distance': float(round_data['distance'].mean()) if 'distance' in round_data.columns else 0
                }

                # Top fragger do round
                if not round_data.empty and 'attacker_name' in round_data.columns:
                    top_fragger = round_data['attacker_name'].value_counts()
                    if len(top_fragger) > 0:
                        round_info['top_fragger'] = top_fragger.index[0]
                        round_info['top_fragger_kills'] = int(top_fragger.iloc[0])
                    else:
                        round_info['top_fragger'] = 'N/A'
                        round_info['top_fragger_kills'] = 0

                round_stats.append(round_info)

            return pd.DataFrame(round_stats)
        except Exception as e:
            console.print(f"❌ Erro na análise de rounds: {str(e)}", style="bold red")
            return pd.DataFrame()

    def calculate_player_statistics(self):
        """Estatísticas abrangentes de jogadores"""
        console.print("📊 Calculando estatísticas de jogadores...", style="bold cyan")

        kills_df = self.results.get('kills', pd.DataFrame())
        damage_df = self.results.get('damage', pd.DataFrame())

        if kills_df.empty:
            console.print("⚠️  Nenhum dado de kills", style="bold yellow")
            return pd.DataFrame()

        try:
            # Kills por atacante
            kills_by_player = kills_df.groupby('attacker_name').size()

            # Deaths por vítima
            deaths_by_player = kills_df.groupby('user_name').size()

            # Estatísticas agregadas
            kills_stats = kills_df.groupby('attacker_name').agg({
                'attacker_team_name': 'first',
                'headshot': 'sum',
                'penetrated': lambda x: int(x.sum()) if 'penetrated' in kills_df.columns else 0,
                'thrusmoke': lambda x: int(x.sum()) if 'thrusmoke' in kills_df.columns else 0,
                'distance': 'mean'
            }).rename(columns={'attacker_team_name': 'team'})

            kills_stats['total_kills'] = kills_by_player
            kills_stats['deaths'] = deaths_by_player.reindex(kills_stats.index, fill_value=0)
            kills_stats['kd_ratio'] = (kills_stats['total_kills'] / kills_stats['deaths'].replace(0, 1)).round(2)
            kills_stats['hs_percent'] = (kills_stats['headshot'] / kills_stats['total_kills'] * 100).round(2)
            kills_stats['avg_kill_distance'] = kills_stats['distance'].round(2)

            # Dano total
            if not damage_df.empty and 'attacker_name' in damage_df.columns:
                dmg = damage_df.groupby('attacker_name')['dmg_health'].sum()
                kills_stats['total_damage'] = dmg
                kills_stats['adr'] = (dmg / len(kills_df['total_rounds_played'].unique())).round(1)
            else:
                kills_stats['total_damage'] = 0
                kills_stats['adr'] = 0.0

            result = kills_stats.reset_index().rename(columns={'attacker_name': 'player'})
            console.print(f"✅ Stats calculadas para {len(result)} jogadores", style="bold green")
            return result

        except Exception as e:
            console.print(f"❌ Erro: {str(e)}", style="bold red")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def analyze_full_demo(self):
        """Análise completa do demo"""
        console.print(f"\n🎮 Análise completa: {self.demo_name}\n", style="bold green")

        self.results['match_info'] = self.extract_match_info()
        self.results['kills'] = self.extract_kills_analysis()
        self.results['damage'] = self.extract_damage_analysis()
        self.results['grenades'] = self.extract_grenades()
        self.results['rounds'] = self.extract_round_summaries()
        self.results['player_stats'] = self.calculate_player_statistics()

        console.print("✅ Análise concluída!\n", style="bold green")
        return self.results

    def save_results(self, output_dir="demo_analysis"):
        """Salva todos os resultados"""
        output_path = Path(output_dir) / self.demo_name
        output_path.mkdir(parents=True, exist_ok=True)

        # Salvar DataFrames como CSV
        for k, v in self.results.items():
            if isinstance(v, pd.DataFrame) and not v.empty:
                v.to_csv(output_path / f"{k}.csv", index=False)
                console.print(f"📄 {k}.csv ({len(v)} registros)", style="dim")
            elif k == 'rounds' and isinstance(v, dict):
                for round_type, round_df in v.items():
                    if isinstance(round_df, pd.DataFrame) and not round_df.empty:
                        round_df.to_csv(output_path / f"rounds_{round_type}.csv", index=False)
                        console.print(f"📄 rounds_{round_type}.csv ({len(round_df)} registros)", style="dim")

        # Salvar match_info como JSON
        match_info = self.results.get('match_info', {})
        serializable_match_info = {}

        for key, value in match_info.items():
            if isinstance(value, pd.DataFrame):
                serializable_match_info[key] = value.to_dict('records') if not value.empty else []
            elif isinstance(value, list):
                serializable_match_info[key] = value
            else:
                serializable_match_info[key] = value

        with open(output_path / "match_info.json", "w", encoding='utf-8') as f:
            json.dump(serializable_match_info, f, indent=2, ensure_ascii=False)

        console.print(f"💾 Resultados salvos em {output_path}", style="bold green")

def main():
    import sys
    if len(sys.argv) < 2:
        console.print("❌ Use: python analyzer.py caminho/para/demo.dem", style="bold red")
        sys.exit(1)

    demo_path = sys.argv[1]
    analyzer = CS2DemoAnalyzer(demo_path)
    analyzer.analyze_full_demo()
    analyzer.save_results()

if __name__ == "__main__":
    main()
