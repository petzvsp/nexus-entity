import re, json, shutil, ast, unicodedata
from pathlib import Path
from collections import Counter
from datetime import datetime

NEXUS = Path.home() / "nexus-system"
MEM = NEXUS / "memoria"; ARQ = MEM / "arquivos"; IDX = MEM / "indice.json"
ARQ.mkdir(parents=True, exist_ok=True)
STOP = {"a","o","e","de","da","do","em","no","na","que","qual","como","por","para","com","sem","um","uma","ao","se","ser","sou","foi","vai","tem","posso","pode","sim","não","mais","já","aqui","este","essa","isso","eu","você","meu","seu","faz","self","def","return","import","from","class","true","false","none","print","with","for","while","else"}

def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

def tokens(t):
    return [w for w in re.findall(r"\b[a-z0-9_]{3,}\b", norm(t)) if w not in STOP]

def analisar(p):
    try: txt = p.read_text(encoding="utf-8", errors="ignore")
    except: return None
    if len(txt) < 30: return None
    i = {"nome": p.name, "linhas": txt.count("\n")+1, "bytes": len(txt), "keywords": [w for w,_ in Counter(tokens(txt)).most_common(15)]}
    if p.suffix == ".py":
        try:
            t = ast.parse(txt)
            for n in ast.walk(t):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): i["keywords"].append(n.name.lower())
        except: pass
    return i

def carregar():
    if IDX.exists():
        try: return json.loads(IDX.read_text(encoding="utf-8"))
        except: pass
    return {"itens": [], "mapa": {}}

def salvar(idx): IDX.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")

def adicionar(caminho):
    p = Path(caminho).expanduser()
    if not p.exists() or not p.is_file(): return None, "nao existe"
    info = analisar(p)
    if not info: return None, "nao analisavel"
    idx = carregar()
    n = len(idx["itens"]) + 1
    dst = ARQ / f"{n:04d}_{p.name}"
    try: shutil.copy2(p, dst)
    except Exception as e: return None, str(e)
    item = {**info, "num": n, "caminho_memoria": str(dst), "adicionado": datetime.now().strftime("%Y-%m-%d %H:%M")}
    idx["itens"].append(item)
    for k in info["keywords"]:
        k = norm(k).strip()
        if len(k) >= 3:
            idx["mapa"].setdefault(k, [])
            if n not in idx["mapa"][k]: idx["mapa"][k].append(n)
    salvar(idx); return item, None

def remover(n):
    idx = carregar()
    alvo = next((x for x in idx["itens"] if x["num"] == n), None)
    if not alvo: return False
    try: Path(alvo["caminho_memoria"]).unlink(missing_ok=True)
    except: pass
    idx["itens"] = [x for x in idx["itens"] if x["num"] != n]
    m = {}
    for it in idx["itens"]:
        for k in it.get("keywords", []):
            k = norm(k).strip()
            if len(k) >= 3: m.setdefault(k, []).append(it["num"])
    idx["mapa"] = m; salvar(idx); return True

def listar(): return carregar()["itens"]

def buscar(pergunta, limite=3):
    idx = carregar()
    ps = set(tokens(pergunta))
    if not ps: return []
    sc = {}
    for k in ps:
        for n in idx["mapa"].get(k, []): sc[n] = sc.get(n, 0) + 1
    return sorted(sc.items(), key=lambda x: -x[1])[:limite]

def montar_contexto(p, limite=3):
    res = buscar(p, limite)
    if not res: return "", []
    idx = carregar()
    partes = []; nomes = []
    for n, s in res:
        it = next((x for x in idx["itens"] if x["num"] == n), None)
        if not it: continue
        try: txt = Path(it["caminho_memoria"]).read_text(encoding="utf-8", errors="ignore")[:1500]
        except: continue
        partes.append(f"[{it['nome']}]\n{txt}")
        nomes.append(it["nome"])
    return "\n\n".join(partes), nomes
