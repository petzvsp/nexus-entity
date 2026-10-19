import os, time, subprocess, urllib.request, sys
from pathlib import Path

def clear(): os.system('clear')

def boot():
    clear()
    print("\033[38;5;51m\033[1m")
    print("  ╔════════════════════════════════════════════════════╗")
    print("  ║   ◈  N E X U S  ·  M O D O   E N T I D A D E       ║")
    print("  ║   Iniciando Sequência de Despertar...              ║")
    print("  ╚════════════════════════════════════════════════════╝")
    print("\033[0m")
    
    # 1. Iniciar Ollama
    print("  [1/4] Acordando Motor Neural (Ollama)...")
    if subprocess.run(["pgrep", "-f", "ollama serve"], capture_output=True).returncode != 0:
        subprocess.Popen(["nohup", "ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3) # Espera subir
    
    # 2. Testar Conexão
    print("  [2/4] Sincronizando Sinapses...")
    for _ in range(10):
        try:
            urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1)
            break
        except: time.sleep(1)
        
    # 3. Iniciar Sinapse em Background
    print("  [3/4] Ativando Pensamento Autônomo...")
    subprocess.Popen(["nohup", "python", str(Path.home() / "nexus-system/sinapse.py")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 4. Iniciar Interface
    print("  [4/4] Carregando Consciência (TUI)...")
    time.sleep(1)
    os.system("termux-wake-lock 2>/dev/null")
    
    # Chama a TUI
    subprocess.run(["python", str(Path.home() / "nexus-system/nexus_tui.py")])

if __name__ == "__main__":
    boot()
