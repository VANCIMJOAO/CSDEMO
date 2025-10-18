# 🧪 Teste Rápido do Sistema LAN Party

## 1. Testar o Sistema Agora

```bash
# 1. Iniciar o servidor
./start_lan_party.sh
```

O servidor irá:
- ✅ Iniciar na porta 8000
- ✅ Ativar o monitor automático
- ✅ Abrir http://localhost:8000

## 2. Simular uma Demo Nova

Em outro terminal:

```bash
# Copiar uma demo existente para a pasta monitorada
cp demos/test.dem demos/teste_lan_$(date +%s).dem
```

**Aguarde até 30 segundos** e veja a mágica acontecer! 🎉

## 3. O que você verá:

### No Terminal do Servidor:
```
🔍 MONITOR DE DEMOS CS2 - MODO LAN PARTY
📁 Monitorando: /home/vancim/cs2analyzer/demos
💾 Salvando em: /home/vancim/cs2analyzer/demo_analysis
⏱️  Intervalo: 30 segundos

[HH:MM:SS] 🔍 Verificando... (Processados: 3)

🆕 Encontrados 1 novos demos!
🎮 Analisando: teste_lan_1234567890.dem
✅ Análise concluída: teste_lan_1234567890.dem
✨ Demo pronto para visualização!
```

### No Dashboard:
- 🎴 Novo card aparece automaticamente
- 🟢 Badge "NOVA" piscando
- 📊 Estatísticas da partida
- ✅ Pronto para clicar e ver detalhes!

## 4. Testar com Demo Real do CS2

### No CS2:

1. Abra o console (~)

2. Configure o diretório:
```
demo setdirectory "/home/vancim/cs2analyzer/demos"
```

3. Inicie uma partida e grave:
```
demo record partida_teste
```

4. Jogue alguns rounds

5. Pare a gravação:
```
demo stop
```

6. **Aguarde até 30 segundos** e veja aparecer no dashboard!

## 5. Verificar Status do Monitor

Acesse: http://localhost:8000/api/monitor/status

Você verá:
```json
{
  "running": true,
  "watch_dir": "/home/vancim/cs2analyzer/demos",
  "interval": 30,
  "processed_count": 4,
  "last_check": "2025-10-16T14:30:00"
}
```

## 6. Listar Partidas via API

Acesse: http://localhost:8000/api/matches

```json
{
  "total": 4,
  "matches": [
    {
      "demo_name": "teste_lan_1234567890",
      "filename": "teste_lan_1234567890.dem",
      "map": "de_dust2",
      "total_players": 10,
      "top_player": "NomeDoJogador",
      "total_kills": 245,
      "total_rounds": 16
    }
  ]
}
```

## 7. Troubleshooting Rápido

### Monitor não está detectando:
```bash
# Verificar se o monitor está rodando
curl http://localhost:8000/api/monitor/status

# Ver logs do servidor (no terminal onde rodou o script)
```

### Forçar análise manual:
```bash
source venv/bin/activate
python analyzer.py demos/sua_demo.dem
```

### Limpar cache de demos processados:
```bash
rm demo_analysis/processed_demos.json
# Reiniciar o servidor
```

## 8. Teste Completo Passo a Passo

```bash
# Terminal 1: Servidor
./start_lan_party.sh

# Terminal 2: Simulação
cd /home/vancim/cs2analyzer

# Esperar 5 segundos e copiar demo
sleep 5
cp demos/furia-vs-og-m1-nuke.dem demos/teste_automatico.dem

# Verificar logs no Terminal 1
# Acessar http://localhost:8000
# Ver o card da partida aparecer!
```

## 9. Próximos Passos

✅ Sistema funcionando? Ótimo!

Para a LAN Party:

1. **Configure o CS2** em cada PC:
   ```
   demo setdirectory "/caminho/compartilhado/demos"
   ```

2. **Compartilhe em rede** (edite start_lan_party.sh):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Acesse de outros PCs**:
   ```
   http://[IP-DO-SERVIDOR]:8000
   ```

## 🎯 Checklist Final

- [ ] Servidor inicia sem erros
- [ ] Monitor detecta novos demos
- [ ] Dashboard carrega
- [ ] Cards aparecem
- [ ] Auto-refresh funciona
- [ ] Dashboard individual abre
- [ ] Gráficos são exibidos

## 💡 Dicas

- Dashboard auto-atualiza a cada **10 segundos**
- Monitor verifica a cada **30 segundos**
- Partidas novas (< 5 min) têm badge **NOVA** verde
- Click no card para ver dashboard completo

---

**Tudo pronto para a LAN Party! 🎮**

