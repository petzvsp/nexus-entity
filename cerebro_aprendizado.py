import json, re, threading, time, unicodedata
from datetime import datetime
from pathlib import Path

NEXUS = Path.home() / "nexus-system"
CB = NEXUS / "cerebro"; CB.mkdir(parents=True, exist_ok=True)
CONH = CB / "conhecimento.json"; LOG = CB / "log_aprendizado.jsonl"; EXP = CB / "expansoes"
EXP.mkdir(exist_ok=True)

try: import apis_publicas as apis
except: apis = None

def slug(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r'[^a-z0-9]+', '_', t).strip('_')[:60] or "tema"

def carregar():
    if CONH.exists():
        try: return json.loads(CONH.read_text(encoding="utf-8"))
        except: pass
    return {"conceitos": {}, "total_aprovacoes": 0, "total_expansoes": 0}

def salvar(c): CONH.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")

def reg_log(termo, ev, det=""):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.now().isoformat(), "termo": termo, "evento": ev, "detalhe": det}, ensure_ascii=False) + "\n")

def registrar_aprovacao(termo, conteudo, fonte):
    c = carregar(); k = slug(termo)
    if k not in c["conceitos"]:
        c["conceitos"][k] = {"termo": termo, "peso": 0, "aprovacoes": 0, "fontes": [], "expansoes": [], "ultima": None, "historico": []}
    c["conceitos"][k]["aprovacoes"] += 1
    c["conceitos"][k]["peso"] = min(10.0, c["conceitos"][k]["peso"] + 1.0)
    if fonte not in c["conceitos"][k]["fontes"]: c["conceitos"][k]["fontes"].append(fonte)
    c["conceitos"][k]["ultima"] = datetime.now().isoformat()
    
    # CORREÇÃO: Removido o corte de [:200]. Agora salva até 5000 caracteres.
    c["conceitos"][k]["historico"].append({"ts": datetime.now().isoformat(), "fonte": fonte, "trecho": conteudo[:5000]})
    
    c["total_aprovacoes"] += 1; salvar(c)
    reg_log(termo, "aprovado", fonte)
    # Não vamos rodar a expansão da web no background aqui para não travar o celular na hora do salvamento
    
def o_que_aprendi_hoje():
    hoje = datetime.now().date()
    if not LOG.exists(): return []
    it = []
    for l in LOG.read_text(encoding="utf-8").strip().split("\n"):
        try:
            d = json.loads(l)
            if datetime.fromisoformat(d["ts"]).date() == hoje: it.append(d)
        except: pass
    return it

def estatisticas():
    c = carregar(); co = c.get("conceitos", {})
    top = sorted(co.values(), key=lambda x: -x["peso"])[:10]
    return {"total": len(co), "top": [(x["termo"], x["peso"], x["aprovacoes"], x["fontes"]) for x in top], "hoje": len(o_que_aprendi_hoje()), "aprov": c.get("total_aprovacoes", 0), "exp": c.get("total_expansoes", 0)}

def montar_contexto_enriquecido(p, limite=3):
    c = carregar(); co = c.get("conceitos", {})
    ps = set(re.findall(r'\b[a-z0-9_]{3,}\b', slug(p).replace('_', ' ')))
    rel = []
    for k, v in co.items():
        s = 0
        for p_ in ps:
            if p_ in k: s += 2
        if v["termo"].lower() in p.lower(): s += 5
        s += v["peso"] * 0.5
        if s > 0: rel.append((s, v))
    rel.sort(reverse=True, key=lambda x: x[0])
    return rel[:limite]
