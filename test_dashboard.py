#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from pathlib import Path
import pandas as pd

# Testar carregamento dos dados
analysis_dir = Path("demo_analysis/furia-vs-og-m2-inferno")

print(f"📁 Diretório: {analysis_dir}")
print(f"📁 Existe: {analysis_dir.exists()}")

if analysis_dir.exists():
    print("📊 Carregando dados...")
    
    try:
        player_stats = pd.read_csv(analysis_dir / "player_stats.csv")
        print(f"✅ Player stats: {len(player_stats)} linhas")
        print(f"Colunas: {list(player_stats.columns)}")
        
        kills_df = pd.read_csv(analysis_dir / "kills.csv")
        print(f"✅ Kills: {len(kills_df)} linhas")
        
        rounds_df = pd.read_csv(analysis_dir / "rounds_detailed.csv")
        print(f"✅ Rounds: {len(rounds_df)} linhas")
        print(f"Colunas rounds: {list(rounds_df.columns)}")
        
        round_data = rounds_df.to_dict('records')
        print(f"✅ Round data: {len(round_data)} rounds")
        
        print("🎯 Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Diretório não encontrado")
