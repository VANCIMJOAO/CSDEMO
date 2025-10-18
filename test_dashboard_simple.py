#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from pathlib import Path
import pandas as pd
import json

# Testar carregamento dos dados
analysis_dir = Path("demo_analysis/furia-vs-og-m2-inferno")

print(f"📁 Diretório: {analysis_dir}")
print(f"📁 Existe: {analysis_dir.exists()}")

if analysis_dir.exists():
    print("📊 Carregando dados...")
    
    try:
        player_stats = pd.read_csv(analysis_dir / "player_stats.csv")
        kills_df = pd.read_csv(analysis_dir / "kills.csv")
        damage_df = pd.read_csv(analysis_dir / "damage.csv")
        rounds_df = pd.read_csv(analysis_dir / "rounds_detailed.csv")
        round_data = rounds_df.to_dict('records')
        
        print(f"✅ Dados carregados:")
        print(f"  - Players: {len(player_stats)}")
        print(f"  - Kills: {len(kills_df)}")
        print(f"  - Damage: {len(damage_df)}")
        print(f"  - Rounds: {len(round_data)}")
        
        # Preparar dados simples
        chart_data = {
            "rounds": [r['round'] for r in round_data],
            "ct_kills": [r['ct_kills'] for r in round_data],
            "t_kills": [r['t_kills'] for r in round_data],
            "headshots": [r['headshots'] for r in round_data],
            "damage": [0] * len(round_data),
            "player_names": list(player_stats['player']),
            "kd_ratios": list(player_stats['kd_ratio']),
            "hs_percentages": list(player_stats['hs_percent']),
            "heatmap_data": []
        }
        
        print("✅ Dados preparados:")
        print(f"  - Rounds: {len(chart_data['rounds'])}")
        print(f"  - Headshots: {len(chart_data['headshots'])}")
        print(f"  - Damage: {len(chart_data['damage'])}")
        
        # Testar JSON serialization
        json_data = json.dumps(chart_data)
        print("✅ JSON serialization OK")
        
        print("🎯 Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Diretório não encontrado")


