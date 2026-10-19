#!/usr/bin/env python3
import os, sys, json, re, urllib.request, urllib.parse, subprocess, time
from pathlib import Path

NEXUS = Path.home() / "nexus-system"
sys.path.insert(0, str(NEXUS))

try: import memoria
except: memoria = None
try: import cerebro_aprendizado as cerebro
except: cerebro = None

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "nexus-pt"
TOPICOS = NEXUS / "memoria" / "topicos"
TOPICOS.mkdir(parents=True, exist_ok=True)
ULTIMO_CHAT = NEXUS / ".ultimo_chat.json"
CONFIG_SINAPSE = NEXUS / "sinapse_config.json"

class C:
    R="\033[0m"; B="\033[1m"; CY="\033[38;5;51m"; CB="\033[38;5;45m"
    GD="\033[38;5;220m"; GR="\033[38;5;46m"; RD="\033[38;5;203m"
    GY="\033[38;5;245m"; MG="\033[38;5;207m"

UA = {"User-Agent": "NexusLocalSystem/14.0 (Termux; Android)"}

def clear(): os.system('clear')

def load_system():
    sf = NEXUS / "system.txt"
    return sf.read_text(encoding="utf-8").strip() if sf.exists() else "Voce e a NEXUS. Responda em portugues."

def slug(t):
    t = re.sub(r'[^\w\s-]', '', t.lower())
    return re.sub(r'[-\s]+', '_', t).strip('_')[:50]

def banner():
    clear()
    print(f"""
{C.CY}{C.B}+==============================================================+
|   ◈  N E X U S   T U I   v14.0  ·  Criador Peterson         |
+==============================================================+{C.R}
""")

# --- FUNÇÕES DO CHAT E MEMÓRIA ---
def chat():
    global historico_atual
    banner()
    print(f"  {C.GY}Digite /sair para voltar. A conversa será salva temporariamente.{C.R}\n")
    historico_atual = []
    while True:
        try:
            user = input(f"  {C.GD}{C.B}❯{C.R} ").strip()
            if user.lower() in ('/sair', 'sair', '0'):
                if historico_atual:
                    ULTIMO_CHAT.write_text(json.dumps(historico_atual), encoding="utf-8")
                    print(f"\n  {C.GY}(Histórico guardado).{C.R}")
                break
            if not user: continue
            ctx, arqs = ("", [])
            if memoria:
                try: ctx, arqs = memoria.montar_contexto(user, limite=3)
                except: pass
            system = load_system()
            if ctx: system += f"\n\n[MEMORIA]\n{ctx}"
            messages = [{"role": "system", "content": system}] + historico_atual + [{"role": "user", "content": user}]
            print(f"\n  {C.CB}{C.B}◈ NEXUS{C.R} {C.GY}(Pensando...){C.R}\n  ", end="")
            resp_completa = ""
            payload = {"model": MODEL, "messages": messages, "stream": True, "options": {"temperature": 0.3, "num_ctx": 2048}}
            req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=300)
            buf = b""
            for line in resp:
                buf += line
                while b"\n" in buf:
                    ln, buf = buf.split(b"\n", 1)
                    if not ln.strip(): continue
                    try:
                        data = json.loads(ln.decode())
                        content = data.get("message", {}).get("content", "")
                        if content:
                            print(content, end="", flush=True)
                            resp_completa += content
                        if data.get("done"): print("\n"); break
                    except: continue
            historico_atual.append({"role": "user", "content": user})
            historico_atual.append({"role": "assistant", "content": resp_completa})
        except KeyboardInterrupt: break

def gerenciar_memoria():
    while True:
        banner()
        print(f"  {C.CY}📂 Central de Conhecimento{C.R}\n")
        print(f"  {C.GD}1{C.R} · Ver / Apagar Memórias (Arquivos .md)")
        print(f"  {C.GD}2{C.R} · Pesquisar na Internet (Wikipedia)")
        print(f"  {C.GD}3{C.R} · Adicionar Texto Manual")
        print(f"  {C.GD}4{C.R} · Salvar Última Conversa do Chat")
        print(f"  {C.GD}0{C.R} · Voltar\n")
        esc = input(f"  {C.GY}Escolha:{C.R} ").strip()
        if esc == '0': break
        elif esc == '1': ver_apagar()
        elif esc == '2': pesquisar_web()
        elif esc == '3': adicionar_manual()
        elif esc == '4': salvar_ultimo_chat()

def ver_apagar():
    while True:
        banner()
        arquivos = sorted(list(TOPICOS.glob("*.md")))
        if not arquivos:
            print(f"  {C.GY}Memória vazia.{C.R}"); input("\n  ENTER..."); return
        for i, arq in enumerate(arquivos, 1): print(f"  {C.GD}[{i}]{C.R} {arq.name}")
        print(f"\n  {C.GD}[0]{C.R} Voltar")
        esc = input(f"\n  {C.CB}Número para VER/APAGAR:{C.R} ").strip()
        if esc == '0': break
        try:
            idx = int(esc) - 1
            if idx < 0 or idx >= len(arquivos): continue
            arquivo = arquivos[idx]
            conteudo = arquivo.read_text(encoding="utf-8", errors="ignore")
            banner()
            print(f"  {C.CY}Conteúdo: {arquivo.name}{C.R}\n")
            print(f"{C.GY}{'-'*60}{C.R}")
            print(conteudo)
            print(f"{C.GY}{'-'*60}{C.R}\n")
            acao = input(f"  {C.RD}Digite 'apagar' para remover:{C.R} ").strip().lower()
            if acao == 'apagar':
                arquivo.unlink()
                if cerebro:
                    c = cerebro.carregar(); k = slug(arquivo.stem)
                    if k in c["conceitos"]: del c["conceitos"][k]
                    cerebro.salvar(c)
                if memoria:
                    idx_json = memoria.carregar()
                    idx_json["itens"] = [x for x in idx_json["itens"] if x["nome"] != arquivo.name]
                    memoria.salvar(idx_json)
                print(f"\n  {C.GR}✓ Apagada!{C.R}"); input("  ENTER...")
        except ValueError: pass

def pesquisar_web():
    banner()
    termo = input("  Tema para pesquisar: ").strip()
    if not termo: return
    print(f"\n  {C.GY}Consultando...{C.R}")
    try:
        s = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(termo)}&format=json&srlimit=1"
        req = urllib.request.Request(s, headers=UA)
        d = json.loads(urllib.request.urlopen(req, timeout=10).read())
        t = d["query"]["search"][0]["title"]
        r = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(t)}"
        req_sum = urllib.request.Request(r, headers=UA)
        sd = json.loads(urllib.request.urlopen(req_sum, timeout=10).read())
        extract = sd.get("extract", "")
        
        banner()
        print(f"  {C.CB}> {t}{C.R}\n")
        print(f"{C.GY}{'-'*60}{C.R}")
        print(extract)
        print(f"{C.GY}{'-'*60}{C.R}\n")
        
        if input(f"  {C.GD}Salvar? [s/N]: {C.R}").strip().lower() == 's':
            dst = TOPICOS / (slug(t) + ".md")
            dst.write_text(f"# {t}\n\n{extract}\n", encoding="utf-8")
            if memoria: memoria.adicionar(dst)
            if cerebro: cerebro.registrar_aprovacao(t, extract, "Wikipedia")
            print(f"\n  {C.GR}✓ Salvo!{C.R}")
    except Exception as e: print(f"\n  {C.RD}Erro: {e}{C.R}")
    input("\n  ENTER...")

def adicionar_manual():
    banner()
    titulo = input("  Título: ").strip()
    if not titulo: return
    print("  Conteúdo (2 ENTERs para finalizar):")
    linhas = []
    while True:
        l = input()
        if not l and len(linhas) > 0 and linhas[-1] == "": break
        linhas.append(l)
    conteudo = "\n".join(linhas).strip()
    if conteudo:
        dst = TOPICOS / (slug(titulo) + ".md")
        dst.write_text(f"# {titulo}\n\n{conteudo}\n", encoding="utf-8")
        if memoria: memoria.adicionar(dst)
        if cerebro: cerebro.registrar_aprovacao(titulo, conteudo, "Manual")
        print(f"\n  {C.GR}✓ Salvo!{C.R}")
    input("\n  ENTER...")

def salvar_ultimo_chat():
    banner()
    if not ULTIMO_CHAT.exists():
        print(f"  {C.RD}Nenhuma conversa recente.{C.R}"); input("  ENTER..."); return
    try:
        hist = json.loads(ULTIMO_CHAT.read_text(encoding="utf-8"))
        print(f"  {C.GY}Gerando resumo com a IA...{C.R}")
        texto = "\n".join([f"{m['role']}: {m['content']}" for m in hist])
        prompt = f"Resuma a conversa abaixo em um artigo técnico curto. Markdown.\n\n{texto}"
        payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False}
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
        resumo = resp["message"]["content"]
        titulo = hist[0]['content'][:30].replace('\n', ' ')
        dst = TOPICOS / (slug(titulo) + ".md")
        dst.write_text(f"# Resumo: {titulo}\n\n{resumo}", encoding="utf-8")
        if memoria: memoria.adicionar(dst)
        if cerebro: cerebro.registrar_aprovacao(titulo, resumo, "Chat History")
        ULTIMO_CHAT.unlink()
        print(f"\n  {C.GR}✓ Salvo como {dst.name}!{C.R}")
    except Exception as e: print(f"\n  {C.RD}Erro: {e}{C.R}")
    input("  ENTER...")

def ver_apagar_sinapses():
    while True:
        banner()
        if not cerebro:
            print(f"  {C.RD}Cérebro offline.{C.R}"); input("  ENTER..."); return
            
        c = cerebro.carregar()
        conceitos = c.get("conceitos", {})
        sinapses = [(k, v) for k, v in conceitos.items() if v["termo"].startswith("Sinapse:")]
        
        if not sinapses:
            print(f"  {C.GY}Nenhum pensamento autônomo gerado ainda.{C.R}")
            input("\n  ENTER..."); return
            
        print(f"  {C.CY}🧠 Pensamentos Autônomos (Sinapses){C.R}\n")
        for i, (k, v) in enumerate(sinapses, 1):
            print(f"  {C.GD}[{i}]{C.R} {v['termo'][:60]}")
            
        print(f"\n  {C.GD}[0]{C.R} Voltar")
        esc = input(f"\n  {C.CB}Número para LER/APAGAR:{C.R} ").strip()
        
        if esc == '0': break
        try:
            idx = int(esc) - 1
            if idx < 0 or idx >= len(sinapses): continue
            
            chave, dados = sinapses[idx]
            texto_completo = dados["historico"][-1]["trecho"] if dados.get("historico") else "Sem conteúdo."
            
            banner()
            print(f"  {C.CY}Sinapse: {dados['termo']}{C.R}\n")
            print(f"{C.GY}{'-'*60}{C.R}")
            print(texto_completo)
            print(f"{C.GY}{'-'*60}{C.R}\n")
            print(f"  {C.GY}Peso no Cérebro: {dados['peso']:.1f}{C.R}\n")
            
            acao = input(f"  {C.RD}Digite 'apagar' para destruir esse pensamento:{C.R} ").strip().lower()
            
            if acao == 'apagar':
                del conceitos[chave]
                cerebro.salvar(c)
                print(f"\n  {C.GR}✓ Pensamento apagado do Cérebro!{C.R}")
                input("  ENTER para continuar...")
                
        except ValueError: pass

def ver_cerebro():
    while True:
        banner()
        print(f"  {C.CY}🧠 Análise do Cérebro{C.R}\n")
        print(f"  {C.GD}1{C.R} · Estatísticas Gerais")
        print(f"  {C.GD}2{C.R} · Ver / Apagar Pensamentos Autônomos (Sinapses)")
        print(f"  {C.GD}3{C.R} · Ver Conceitos Aprendidos (Pesos)")
        print(f"  {C.GD}0{C.R} · Voltar\n")
        esc = input(f"  {C.GY}Escolha:{C.R} ").strip()
        
        if esc == '0': break
        elif esc == '2':
            ver_apagar_sinapses()
            continue
            
        if not cerebro:
            print("  Módulo offline."); input("  ENTER..."); continue
            
        c = cerebro.carregar()
        conceitos = c.get("conceitos", {})
        
        if esc == '1':
            sinapses = [v for k, v in conceitos.items() if v["termo"].startswith("Sinapse:")]
            e = cerebro.estatisticas()
            banner()
            print(f"  {C.CY}Estatísticas{C.R}\n")
            print(f"  Total de Conceitos:   {C.GD}{e.get('total',0)}{C.R}")
            print(f"  Total de Sinapses:    {C.GD}{len(sinapses)}{C.R}")
            print(f"  Aprovações:           {C.GD}{e.get('aprov',0)}{C.R}\n")
            input("  ENTER...")
            
        elif esc == '3':
            banner()
            print(f"  {C.CY}Conceitos Aprendidos{C.R}\n")
            for k, v in sorted(conceitos.items()):
                if not v["termo"].startswith("Sinapse:"):
                    print(f"  {C.GD}[{v['peso']:.1f}]{C.R} {v['termo'][:40]} ({v['aprovacoes']}x)")
            input("\n  ENTER...")

def controle_pensamento():
    while True:
        banner()
        try: conf = json.loads(CONFIG_SINAPSE.read_text(encoding="utf-8"))
        except: conf = {"intervalo_segundos": 300, "conexoes_por_ciclo": 2, "modo": "pausado"}
        
        rodando = subprocess.run(["pgrep", "-f", "sinapse.py"], capture_output=True).returncode == 0
        status = f"{C.GR}RODANDO{C.R}" if rodando else f"{C.RD}PARADO{C.R}"
        modo = conf.get("modo", "pausado").upper()
        
        print(f"  {C.CY}⚙️ Controle de Pensamento Autônomo{C.R}\n")
        print(f"  Status: {status}  |  Modo: {C.GD}{modo}{C.R}")
        print(f"  Intervalo: {C.GD}{conf.get('intervalo_segundos')}{C.R}s  |  Conexões: {C.GD}{conf.get('conexoes_por_ciclo')}{C.R}\n")
        
        print(f"  {C.GD}1{C.R} · Alternar Modo (Livre / Pausado)")
        print(f"  {C.GD}2{C.R} · Definir Intervalo (segundos)")
        print(f"  {C.GD}3{C.R} · Definir Quantidade de Conexões")
        print(f"  {C.GD}0{C.R} · Voltar\n")
        
        esc = input(f"  {C.GY}Escolha:{C.R} ").strip()
        if esc == '0': break
        elif esc == '1':
            conf["modo"] = "livre" if conf["modo"] == "pausado" else "pausado"
            CONFIG_SINAPSE.write_text(json.dumps(conf), encoding="utf-8")
            if not rodando:
                subprocess.Popen(["nohup", "python", str(NEXUS / "sinapse.py")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"\n  {C.GR}✓ Modo {conf['modo'].upper()}!{C.R}"); time.sleep(1)
        elif esc == '2':
            try:
                conf["intervalo_segundos"] = int(input("  Novo intervalo (seg): ").strip())
                CONFIG_SINAPSE.write_text(json.dumps(conf), encoding="utf-8")
                print(f"\n  {C.GR}✓ Alterado!{C.R}")
            except: print(f"\n  {C.RD}Inválido.{C.R}")
            time.sleep(1)
        elif esc == '3':
            try:
                conf["conexoes_por_ciclo"] = int(input("  Conexões por ciclo: ").strip())
                CONFIG_SINAPSE.write_text(json.dumps(conf), encoding="utf-8")
                print(f"\n  {C.GR}✓ Alterado!{C.R}")
            except: print(f"\n  {C.RD}Inválido.{C.R}")
            time.sleep(1)

def menu():
    while True:
        banner()
        ollama_ok = False
        try:
            urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1)
            ollama_ok = True
        except: pass
        status_ol = f"{C.GR}ONLINE{C.R}" if ollama_ok else f"{C.RD}OFFLINE{C.R}"
        rodando = subprocess.run(["pgrep", "-f", "sinapse.py"], capture_output=True).returncode == 0
        status_sin = f"{C.GR}ON{C.R}" if rodando else f"{C.RD}OFF{C.R}"
        
        print(f"  Ollama: {status_ol} | Sinapse: {status_sin} | Modelo: {C.GD}{MODEL}{C.R}\n")
        
        print(f"  {C.GD}1{C.R} · {C.CB}💬 Chat com NEXUS{C.R}")
        print(f"  {C.GD}2{C.R} · {C.CB}📂 Central de Conhecimento{C.R}")
        print(f"  {C.GD}3{C.R} · {C.CB}🧠 Analisar Cérebro{C.R}")
        print(f"  {C.GD}4{C.R} · {C.CB}⚙️ Controle de Pensamento (Autônomo){C.R}")
        print(f"  {C.GD}0{C.R} · {C.CB}Sair{C.R}\n")
        
        esc = input(f"  {C.GY}Escolha uma opção:{C.R} ").strip()
        if esc == '0': break
        elif esc == '1': chat()
        elif esc == '2': gerenciar_memoria()
        elif esc == '3': ver_cerebro()
        elif esc == '4': controle_pensamento()

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n\n  {C.GY}Até logo, Arquiteto.{C.R}\n")
