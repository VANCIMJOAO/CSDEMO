#!/usr/bin/env python3
"""
Sistema de Monitoramento Automático de Demos CS2
Monitora uma pasta alvo e analisa automaticamente novos arquivos .dem
"""

import time
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
import subprocess
import hashlib
import threading

console = Console()

class DemoMonitor:
    def __init__(self, watch_dir: Path, analysis_dir: Path, interval: int = 30):
        """
        Args:
            watch_dir: Pasta a ser monitorada
            analysis_dir: Pasta onde as análises serão salvas
            interval: Intervalo de verificação em segundos (padrão: 30)
        """
        self.watch_dir = Path(watch_dir)
        self.analysis_dir = Path(analysis_dir)
        self.interval = interval
        self.processed_db = self.analysis_dir / "processed_demos.json"
        self.processed_demos = self.load_processed_demos()
        self.running = False
        
        # Criar diretórios se não existirem
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
    def load_processed_demos(self) -> dict:
        """Carrega lista de demos já processados"""
        if self.processed_db.exists():
            try:
                with open(self.processed_db, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"⚠️ Erro ao carregar DB: {e}", style="yellow")
                return {}
        return {}
    
    def save_processed_demos(self):
        """Salva lista de demos processados"""
        try:
            with open(self.processed_db, 'w') as f:
                json.dump(self.processed_demos, f, indent=2)
        except Exception as e:
            console.print(f"❌ Erro ao salvar DB: {e}", style="red")
    
    def get_file_hash(self, file_path: Path) -> str:
        """Gera hash MD5 do arquivo para garantir que é único"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def is_file_complete(self, file_path: Path, wait_time: int = 2) -> bool:
        """
        Verifica se o arquivo terminou de ser escrito
        Aguarda e verifica se o tamanho do arquivo não mudou
        """
        try:
            initial_size = file_path.stat().st_size
            time.sleep(wait_time)
            final_size = file_path.stat().st_size
            return initial_size == final_size and final_size > 0
        except Exception:
            return False
    
    def scan_for_new_demos(self) -> list:
        """Escaneia pasta em busca de novos arquivos .dem (incluindo subpastas de campeonatos)"""
        new_demos = []

        try:
            # Escanear demos na raiz
            for demo_file in self.watch_dir.glob("*.dem"):
                # Verificar se o arquivo está completo
                if not self.is_file_complete(demo_file):
                    console.print(f"⏳ Arquivo ainda sendo escrito: {demo_file.name}", style="yellow")
                    continue

                # Gerar hash do arquivo
                file_hash = self.get_file_hash(demo_file)

                # Verificar se já foi processado
                if file_hash not in self.processed_demos:
                    new_demos.append({
                        'path': demo_file,
                        'hash': file_hash,
                        'name': demo_file.stem,
                        'tournament': None  # Não é de torneio
                    })

            # Escanear demos em subpastas de campeonatos
            campeonatos_dir = self.watch_dir / "campeonatos"
            if campeonatos_dir.exists():
                for tournament_dir in campeonatos_dir.iterdir():
                    if tournament_dir.is_dir():
                        tournament_slug = tournament_dir.name

                        for demo_file in tournament_dir.glob("*.dem"):
                            # Verificar se o arquivo está completo
                            if not self.is_file_complete(demo_file):
                                console.print(f"⏳ Arquivo ainda sendo escrito: {demo_file.name}", style="yellow")
                                continue

                            # Gerar hash do arquivo
                            file_hash = self.get_file_hash(demo_file)

                            # Verificar se já foi processado
                            if file_hash not in self.processed_demos:
                                new_demos.append({
                                    'path': demo_file,
                                    'hash': file_hash,
                                    'name': demo_file.stem,
                                    'tournament': tournament_slug  # Identificador do torneio
                                })
                                console.print(f"🏆 Demo de torneio detectado: {tournament_slug}/{demo_file.name}", style="bold magenta")
        except Exception as e:
            console.print(f"❌ Erro ao escanear pasta: {e}", style="red")

        return new_demos
    
    def analyze_demo(self, demo_info: dict) -> bool:
        """
        Analisa uma demo usando o analyzer.py
        Returns: True se análise foi bem-sucedida
        """
        demo_path = demo_info['path']
        console.print(f"\n🎮 Analisando: {demo_path.name}", style="bold cyan")
        
        try:
            # Usar o Python do venv para rodar o analyzer
            base_dir = Path(__file__).parent
            venv_python = base_dir / "venv" / "bin" / "python"
            analyzer_script = base_dir / "analyzer.py"
            
            # Executar análise
            result = subprocess.run(
                [str(venv_python), str(analyzer_script), str(demo_path)],
                capture_output=True,
                text=True,
                cwd=base_dir
            )
            
            if result.returncode == 0:
                console.print(f"✅ Análise concluída: {demo_path.name}", style="bold green")

                # Registrar demo como processado
                demo_record = {
                    'filename': demo_path.name,
                    'demo_name': demo_info['name'],
                    'processed_at': datetime.now().isoformat(),
                    'file_size': demo_path.stat().st_size,
                    'analysis_path': str(self.analysis_dir / demo_info['name'])
                }

                # Adicionar informação de torneio se existir
                if demo_info.get('tournament'):
                    demo_record['tournament'] = demo_info['tournament']
                    console.print(f"🏆 Torneio: {demo_info['tournament']}", style="bold magenta")

                self.processed_demos[demo_info['hash']] = demo_record
                self.save_processed_demos()
                return True
            else:
                console.print(f"❌ Erro na análise de {demo_path.name}", style="bold red")
                console.print(f"STDERR: {result.stderr}", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Erro ao processar {demo_path.name}: {e}", style="bold red")
            return False
    
    def monitor_loop(self):
        """Loop principal de monitoramento"""
        console.print("\n" + "="*60, style="bold cyan")
        console.print("🔍 MONITOR DE DEMOS CS2 - MODO LAN PARTY", style="bold green")
        console.print("="*60 + "\n", style="bold cyan")
        console.print(f"📁 Monitorando: {self.watch_dir}", style="cyan")
        console.print(f"💾 Salvando em: {self.analysis_dir}", style="cyan")
        console.print(f"⏱️  Intervalo: {self.interval} segundos", style="cyan")
        console.print(f"📊 Demos processados: {len(self.processed_demos)}\n", style="cyan")
        
        self.running = True
        
        while self.running:
            try:
                # Escanear por novos demos
                new_demos = self.scan_for_new_demos()
                
                if new_demos:
                    console.print(f"\n🆕 Encontrados {len(new_demos)} novos demos!", style="bold yellow")
                    
                    for demo_info in new_demos:
                        success = self.analyze_demo(demo_info)
                        if success:
                            console.print(f"✨ Demo pronto para visualização!", style="bold green")
                else:
                    # Mensagem silenciosa de verificação
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    console.print(f"[{timestamp}] 🔍 Verificando... (Processados: {len(self.processed_demos)})", 
                                style="dim")
                
                # Aguardar próximo ciclo
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                console.print("\n\n⏹️  Monitor interrompido pelo usuário", style="bold yellow")
                self.running = False
                break
            except Exception as e:
                console.print(f"\n❌ Erro no loop de monitoramento: {e}", style="bold red")
                time.sleep(self.interval)
    
    def start(self):
        """Inicia o monitoramento em thread separada"""
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop(self):
        """Para o monitoramento"""
        self.running = False
        console.print("\n🛑 Parando monitor...", style="bold yellow")

    def get_processed_list(self) -> list:
        """Retorna lista de demos processados ordenados por data (mais recente primeiro)"""
        demos = []
        for hash_key, info in self.processed_demos.items():
            demos.append({
                'hash': hash_key,
                **info
            })
        # Ordenar por data de processamento (mais recente primeiro)
        demos.sort(key=lambda x: x.get('processed_at', ''), reverse=True)
        return demos


def main():
    """Modo standalone - executa apenas o monitor"""
    import sys
    from pathlib import Path
    
    # Configuração padrão
    BASE_DIR = Path(__file__).parent
    WATCH_DIR = BASE_DIR / "demos"  # Pasta onde os demos serão salvos
    ANALYSIS_DIR = BASE_DIR / "demo_analysis"
    
    # Permitir override via argumentos
    if len(sys.argv) > 1:
        WATCH_DIR = Path(sys.argv[1])
    
    console.print("\n" + "🎮"*30, style="bold cyan")
    console.print("  CS2 DEMO ANALYZER - MONITOR AUTOMÁTICO", style="bold green")
    console.print("🎮"*30 + "\n", style="bold cyan")
    
    # Criar e iniciar monitor
    monitor = DemoMonitor(WATCH_DIR, ANALYSIS_DIR, interval=30)
    
    try:
        monitor.monitor_loop()
    except KeyboardInterrupt:
        console.print("\n\n👋 Encerrando monitor...", style="bold yellow")
        sys.exit(0)


if __name__ == "__main__":
    main()

