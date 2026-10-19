import time, json, urllib.request, random, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "nexus-system"))
try:
    import cerebro_aprendizado as cerebro
except: pass

CONFIG_FILE = Path.home() / "nexus-system/sinapse_config.json"

def carregar_config():
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except:
        return {"intervalo_segundos": 600, "conexoes_por_ciclo": 1, "modo": "manual"}

def pensar_cruzado():
    while True:
        config = carregar_config()
        
        if config.get("modo") == "pausado":
            time.sleep(10)
            continue
            
        try:
            c = cerebro.carregar()
            conceitos = [k for k in c.get("conceitos", {}).keys() if not k.startswith("sinapse_")]
            
            if len(conceitos) >= 2:
                conexoes = config.get("conexoes_por_ciclo", 1)
                
                for _ in range(conexoes):
                    tema_a, tema_b = random.sample(conceitos, 2)
                    nome_a = tema_a.replace('_', ' ').title()
                    nome_b = tema_b.replace('_', ' ').title()
                    
                    # PROMPT OTIMIZADO PARA CABER EM 250 TOKENS
                    prompt = f"""Você é a NEXUS. Crie uma SINAPSE CRUZADA técnica e concisa unindo os conceitos '{nome_a}' e '{nome_b}'. Explique a relação entre eles em no máximo 2 parágrafos."""
                    
                    # num_predict reduzido para 250 para evitar Timeout
                    payload = {"model": "nexus-pt", "prompt": prompt, "stream": False, "options": {"num_predict": 250}}
                    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
                    resp = json.loads(urllib.request.urlopen(req, timeout=180).read())
                    pensamento = resp.get("response", "").strip()
                    
                    if pensamento:
                        termo_sinapse = f"Sinapse: {nome_a} + {nome_b}"
                        cerebro.registrar_aprovacao(termo_sinapse, pensamento, "Autônomo")
                        with open(Path.home() / "nexus-system/logs/sinapse.log", "a") as f:
                            f.write(f"[{time.ctime()}] {termo_sinapse}:\n{pensamento}\n{'-'*40}\n")
                            
            if config.get("modo") == "manual":
                config["modo"] = "pausado"
                CONFIG_FILE.write_text(json.dumps(config), encoding="utf-8")
                
        except Exception as e:
            pass
            
        # Volta para o tempo configurado (600s = 10 min)
        time.sleep(config.get("intervalo_segundos", 600))

if __name__ == "__main__":
    pensar_cruzado()
