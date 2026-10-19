import logging, time, json
from functools import wraps
from pathlib import Path
from datetime import datetime

NEXUS = Path.home() / "nexus-system"; LOGS = NEXUS / "logs"; LOGS.mkdir(parents=True, exist_ok=True)

def registrar(ev, det=""):
    arq = LOGS / "auditoria.jsonl"
    with open(arq, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.now().isoformat(), "nivel": "INFO", "modulo": "NEXUS", "msg": f"{ev} | {det}"}, ensure_ascii=False) + "\n")

def estatisticas():
    a = LOGS / "auditoria.jsonl"
    if not a.exists(): return {"total": 0, "ok": 0, "erros": 0}
    t = ok = er = 0
    for l in a.read_text(encoding="utf-8").strip().split("\n"):
        try:
            d = json.loads(l); t += 1
            if d.get("nivel") == "ERROR": er += 1
            else: ok += 1
        except: pass
    return {"total": t, "ok": ok, "erros": er}
