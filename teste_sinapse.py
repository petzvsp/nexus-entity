import time, json, urllib.request, random, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "nexus-system"))
import cerebro_aprendizado as cerebro

print("\n  [1] Lendo o Cérebro...")
c = cerebro.carregar()
conceitos = [k for k in c.get("conceitos", {}).keys() if not k.startswith("sinapse_")]

if len(conceitos) < 2:
    print("  ❌ ERRO: Cérebro não tem conceitos suficientes.")
    sys.exit()

tema_a, tema_b = random.sample(conceitos, 2)
print(f"  [2] Cruzando: {tema_a} + {tema_b}")
print(f"  [3] Chamando o Ollama (Aguarde, isso pode demorar)...\n")

# ALTERAÇÃO AQUI: num_predict reduzido de 512 para 250
prompt = f"Crie uma SINAPSE CRUZADA técnica e concisa unindo '{tema_a}' e '{tema_b}'. Máximo de 2 parágrafos."
payload = {"model": "nexus-pt", "prompt": prompt, "stream": False, "options": {"num_predict": 250}}
req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})

try:
    # Aumentei o timeout para 180s por garantia
    resp = urllib.request.urlopen(req, timeout=180)
    pensamento = json.loads(resp.read()).get("response", "").strip()
    
    print("  ✅ RESPOSTA RECEBIDA:\n")
    print("-" * 60)
    print(pensamento)
    print("-" * 60)
    
    print("\n  Salvando no Cérebro...")
    cerebro.registrar_aprovacao(f"Sinapse: {tema_a} + {tema_b}", pensamento, "Teste")
    print("  ✅ Salvo com sucesso!")
except Exception as e:
    print(f"\n  ❌ ERRO NA CONEXÃO: {e}")
