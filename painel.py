#!/usr/bin/env python3
# NEXUS · Painel Web (sem Ollama por enquanto)
import os, sys, json, re, socket, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context
import urllib.request, urllib.error

NEXUS = Path.home() / "nexus-system"
sys.path.insert(0, str(NEXUS))
try: import memoria
except: memoria = None
try: import cerebro_aprendizado as cerebro
except: cerebro = None
try: import audit
except: audit = None

TOPICOS = NEXUS / "memoria" / "topicos"
TOPICOS.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "nexus-pt"

def ollama_stream(messages):
    payload = {"model": MODEL, "messages": messages, "stream": True,
               "options": {"temperature": 0.3, "num_ctx": 1024, "top_p": 0.85}}
    req = urllib.request.Request(OLLAMA_URL, data=__import__("json").dumps(payload).encode(),
                                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=300)
    except urllib.error.URLError as e:
        yield f"[ERRO] Ollama nao responde: {e}"
        return
    for line in resp:
        if not line.strip(): continue
        try:
            data = __import__("json").loads(line.decode())
            content = data.get("message", {}).get("content", "")
            if content: yield content
            if data.get("done"): break
        except: continue

def slug(t):
    t = re.sub(r'[^\w\s-]', '', t.lower())
    return re.sub(r'[-\s]+', '_', t).strip('_')[:60] or "nota"

@app.route("/")
def home(): return Response(HTML, mimetype="text/html")

@app.route("/api/status")
def status():
    rag = len(memoria.listar()) if memoria else 0
    cb = cerebro.estatisticas() if cerebro else {"total":0,"hoje":0,"aprov":0}
    au = audit.estatisticas() if audit else {"total":0,"ok":0,"erros":0}
    ram = {}
    try:
        with open('/proc/meminfo') as f: info = f.read()
        total = int(re.search(r'MemTotal:\s+(\d+)', info).group(1)) / 1024 / 1024
        avail = int(re.search(r'MemAvailable:\s+(\d+)', info).group(1)) / 1024 / 1024
        usada = total - avail
        ram = {"percent": round(usada/total*100,1), "used_gb": round(usada,2), "total_gb": round(total,2)}
    except: pass
    return jsonify({"rag": rag, "cerebro": cb, "audit": au, "ram": ram, "hora": datetime.now().strftime("%H:%M:%S")})

@app.route("/api/rag/list")
def rag_list(): return jsonify({"itens": memoria.listar() if memoria else []})

@app.route("/api/rag/add", methods=["POST"])
def rag_add():
    d = request.json or {}
    t = (d.get("titulo") or "").strip()
    c = (d.get("conteudo") or "").strip()
    if not t or not c: return jsonify({"erro": "preencha tudo"}), 400
    nome = slug(t) + ".md"
    dst = TOPICOS / nome
    dst.write_text(f"# {t}\n\n**Salvo em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{c}\n", encoding="utf-8")
    if memoria:
        try: memoria.adicionar(dst)
        except: pass
    if cerebro:
        try: cerebro.registrar_aprovacao(t, c[:500], "Painel")
        except: pass
    return jsonify({"ok": True, "arquivo": nome})

@app.route("/api/rag/del/<int:n>", methods=["DELETE"])
def rag_del(n): return jsonify({"ok": memoria.remover(n) if memoria else False})

@app.route("/api/rag/search")
def rag_search():
    q = request.args.get("q", "").strip()
    if not q or not memoria: return jsonify({"resultados": []})
    try:
        r = memoria.buscar(q, limite=8)
        return jsonify({"resultados": [{"num": n, "score": s} for n, s in r]})
    except: return jsonify({"resultados": []})

@app.route("/api/cerebro")
def cb_stats(): return jsonify(cerebro.estatisticas() if cerebro else {"total":0,"top":[],"hoje":0,"aprov":0})

@app.route("/api/cerebro/today")
def cb_today(): return jsonify({"itens": cerebro.o_que_aprendi_hoje() if cerebro else []})

@app.route("/api/aprend/search", methods=["POST"])
def aprend_search():
    termo = (request.json or {}).get("termo", "").strip()
    if not termo: return jsonify({"erro": "termo vazio"}), 400
    resultado = None
    for lang in ["pt", "en"]:
        try:
            s = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(termo)}&format=json&srlimit=3"
            d = json.loads(urllib.request.urlopen(urllib.request.Request(s, headers={"User-Agent":"NEXUS"}), timeout=12).read())
            h = d.get("query", {}).get("search", [])
            if h:
                t = h[0]["title"]
                r = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(t)}"
                sd = json.loads(urllib.request.urlopen(urllib.request.Request(r, headers={"User-Agent":"NEXUS"}), timeout=12).read())
                ext = sd.get("extract", "")
                if ext:
                    resultado = {"titulo": t, "extract": ext, "url": sd.get("content_urls",{}).get("desktop",{}).get("page",""), "fonte": f"Wikipedia ({lang.upper()})"}
                    break
        except: continue
    if not resultado: return jsonify({"erro": "nada encontrado"})
    return jsonify(resultado)

@app.route("/api/aprend/approve", methods=["POST"])
def aprend_approve():
    d = request.json or {}
    titulo = (d.get("titulo") or "").strip()
    extract = (d.get("extract") or "").strip()
    fonte = (d.get("fonte") or "").strip()
    url = (d.get("url") or "").strip()
    if not titulo or not extract: return jsonify({"erro": "dados incompletos"}), 400
    nome = slug(titulo) + ".md"
    dst = TOPICOS / nome
    dst.write_text(f"# {titulo}\n\n**Fonte:** {fonte}\n**URL:** {url}\n**Salvo em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{extract}\n", encoding="utf-8")
    if memoria:
        try: memoria.adicionar(dst)
        except: pass
    if cerebro:
        try: cerebro.registrar_aprovacao(titulo, extract, fonte)
        except: pass
    return jsonify({"ok": True, "arquivo": nome})

@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    msg = (request.json or {}).get("message", "").strip()
    if not msg: return jsonify({"erro": "vazio"}), 400
    ctx, arqs = ("", [])
    if memoria:
        try: ctx, arqs = memoria.montar_contexto(msg, limite=3)
        except: pass
    extra = ""
    if cerebro:
        try:
            c = cerebro.carregar()
            for k, v in c.get("conceitos", {}).items():
                if v["termo"].lower() in msg.lower() and v["historico"]:
                    extra += f"\n[{v['termo']}]: {v['historico'][-1]['trecho']}"
                    break
        except: pass
    system = "Voce e a NEXUS, assistente do Criador Peterson. Responda em portugues, direto e tecnico."
    if ctx: system += f"\n\n[MEMORIA]\n{ctx}"
    if extra: system += f"\n\n[CEREBRO]\n{extra}"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": msg}]
    def generate():
        meta = {"type": "meta", "rag": arqs}
        yield f"data: {__import__('json').dumps(meta)}\n\n"
        full = ""
        for tok in ollama_stream(messages):
            full += tok
            yield f"data: {__import__('json').dumps({'type':'token','content':tok})}\n\n"
        try:
            hd = NEXUS / "historico"; hd.mkdir(exist_ok=True)
            (hd / f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json").write_text(
                __import__("json").dumps({"origem":"web","msg":msg,"resp":full}, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except: pass
        yield f"data: {__import__('json').dumps({'type':'done'})}\n\n"
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/api/audit")
def au_stats(): return jsonify(audit.estatisticas() if audit else {"total":0,"ok":0,"erros":0})

@app.route("/api/audit/recent")
def au_recent():
    a = NEXUS / "logs" / "auditoria.jsonl"
    if not a.exists(): return jsonify({"eventos": []})
    try:
        ls = a.read_text(encoding="utf-8").strip().split("\n")
        evs = []
        for l in ls[-30:]:
            try: evs.append(json.loads(l))
            except: pass
        return jsonify({"eventos": evs[::-1]})
    except: return jsonify({"eventos": []})

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEXUS · Painel</title>
<style>
:root{--bg:#0b0c10;--card:#1f2833;--accent:#66fcf1;--viper:#45a29e;--text:#c5c6c7;--red:#ff5555;--green:#00ff88;--orange:#ffb347}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:-apple-system,sans-serif;display:flex;flex-direction:column;min-height:100vh}
nav{background:#000;border-bottom:1px solid #333;padding:8px;display:flex;overflow-x:auto;gap:4px}
.nav-link{padding:8px 12px;cursor:pointer;color:#888;font-size:.78rem;white-space:nowrap;border-radius:6px;transition:.2s}
.nav-link:hover{background:#1a1a1a;color:var(--accent)}
.nav-link.active{background:rgba(102,252,241,.1);color:var(--accent)}
main{flex:1;padding:16px;overflow-y:auto;background:linear-gradient(135deg,#0b0c10,#1f2833)}
h2{color:var(--accent);font-size:1.1rem;margin-bottom:12px;letter-spacing:1px}
h3{color:var(--viper);font-size:.85rem;margin:10px 0 8px}
.section{display:none}.section.active{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px;margin-bottom:14px}
.card{background:rgba(31,40,51,.7);padding:12px;border-radius:10px;border:1px solid rgba(102,252,241,.12)}
.card .label{font-size:.6rem;color:#888;letter-spacing:1px;text-transform:uppercase}
.card .val{font-size:1.2rem;color:var(--accent);font-weight:700;margin-top:4px;font-family:monospace}
input,textarea,select{width:100%;background:#111;border:1px solid #333;color:white;padding:9px;margin:5px 0;border-radius:6px;font-size:.82rem;outline:none;font-family:inherit}
input:focus,textarea:focus{border-color:var(--accent)}
button{background:var(--accent);color:#000;border:none;padding:9px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.78rem;transition:.2s}
button:hover{background:var(--viper)}
button.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}
button.danger{background:var(--red);color:#fff}
.list-box{max-height:340px;overflow-y:auto}
.item{background:#0a0a0a;border:1px solid #333;padding:8px 11px;border-radius:6px;margin:4px 0;font-size:.76rem;display:flex;justify-content:space-between;align-items:center;gap:8px}
.item .name{color:var(--accent);font-family:monospace;flex:1;word-break:break-word}
.item .info{color:#888;font-size:.7rem;white-space:nowrap}
.spin{display:inline-block;width:12px;height:12px;border:2px solid var(--accent);border-top-color:transparent;border-radius:50%;animation:spin 1s linear infinite;vertical-align:middle;margin-right:6px}
@keyframes spin{to{transform:rotate(360deg)}}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-thumb{background:#333;border-radius:3px}
</style>
</head>
<body>
<nav>
  <div class="nav-link active" data-s="dash" onclick="ir('dash')">📊 Dash</div>
  <div class="nav-link" data-s="chat" onclick="ir('chat')">💬 Chat</div>
  <div class="nav-link" data-s="rag" onclick="ir('rag')">📚 RAG</div>
  <div class="nav-link" data-s="cerebro" onclick="ir('cerebro')">🧠 Cérebro</div>
  <div class="nav-link" data-s="aprend" onclick="ir('aprend')">🎓 Aprender</div>
  <div class="nav-link" data-s="audit" onclick="ir('audit')">🔍 Audit</div>
</nav>
<main>

<div class="section active" id="sec-dash">
  <h2>📊 Dashboard</h2>
  <div class="grid">
    <div class="card"><div class="label">RAG</div><div class="val" id="d-rag">0</div></div>
    <div class="card"><div class="label">Cérebro</div><div class="val" id="d-cer">0</div></div>
    <div class="card"><div class="label">Hoje</div><div class="val" id="d-hoje">0</div></div>
    <div class="card"><div class="label">Audit</div><div class="val" id="d-au">0</div></div>
    <div class="card"><div class="label">RAM</div><div class="val" id="d-ram">—</div></div>
  </div>
</div>


<div class="section" id="sec-chat">
  <h2>💬 Chat NEXUS</h2>
  <div class="chat-box" id="chat-box" style="height:55vh;min-height:280px;background:rgba(0,0,0,.4);border-radius:10px;padding:12px;overflow-y:auto;margin-bottom:10px;border:1px solid #333">
    <div class="item" style="border-left:3px solid var(--accent);background:rgba(102,252,241,.05);padding:10px"><b style="color:var(--accent)">NEXUS:</b> Pronto. RAG e Cérebro ativos. Modelo: nexus-pt</div>
  </div>
  <div style="display:flex;gap:6px">
    <input id="chat-in" placeholder="Pergunte algo..." onkeypress="if(event.key==='Enter')chatEnviar()">
    <button onclick="chatEnviar()" id="chat-btn">→</button>
  </div>
  <div style="margin-top:8px;font-size:.72rem;color:#666;font-family:monospace">↳ Digite /gerar &lt;descrição&gt; para criar código</div>
</div>

<div class="section" id="sec-rag">
  <h2>📚 RAG</h2>
  <input id="r-t" placeholder="Título">
  <textarea id="r-c" rows="3" placeholder="Conteúdo"></textarea>
  <button onclick="ragAdd()">Salvar</button>
  <input id="r-q" placeholder="Buscar..." onkeypress="if(event.key==='Enter')ragSearch()" style="margin-top:8px">
  <button class="ghost" onclick="ragSearch()">Buscar</button>
  <button class="ghost" onclick="ragList()">Listar</button>
  <div class="list-box" id="r-list" style="margin-top:8px"></div>
</div>

<div class="section" id="sec-cerebro">
  <h2>🧠 Cérebro</h2>
  <div class="grid">
    <div class="card"><div class="label">Total</div><div class="val" id="c-tot">0</div></div>
    <div class="card"><div class="label">Aprov.</div><div class="val" id="c-ap">0</div></div>
    <div class="card"><div class="label">Hoje</div><div class="val" id="c-hj">0</div></div>
  </div>
  <h3>Conceitos</h3>
  <div class="list-box" id="c-list"></div>
  <h3 style="margin-top:10px">Aprendido hoje</h3>
  <div class="list-box" id="c-hoje"></div>
</div>

<div class="section" id="sec-aprend">
  <h2>🎓 Aprendizado · Wikipedia</h2>
  <input id="a-t" placeholder="Tema (ex: python, redes)" onkeypress="if(event.key==='Enter')apSearch()">
  <button onclick="apSearch()" id="a-btn">Buscar</button>
  <div id="a-res" style="margin-top:10px"></div>
</div>

<div class="section" id="sec-audit">
  <h2>🔍 Auditoria</h2>
  <div class="grid">
    <div class="card"><div class="label">Total</div><div class="val" id="au-t">0</div></div>
    <div class="card"><div class="label">OK</div><div class="val" id="au-ok">0</div></div>
    <div class="card"><div class="label">Erros</div><div class="val" id="au-er">0</div></div>
  </div>
  <div class="list-box" id="au-list"></div>
</div>

</main>
<script>
function ir(s){
  document.querySelectorAll('.section').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(x=>x.classList.remove('active'));
  document.getElementById('sec-'+s).classList.add('active');
  document.querySelector(`[data-s="${s}"]`).classList.add('active');
  if(s==='dash') loadDash();
  if(s==='rag') ragList();
  if(s==='cerebro') loadCB();
  if(s==='audit') loadAudit();
}
function esc(t){return String(t||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c])}

async function loadDash(){
  try{
    const d = await (await fetch('/api/status')).json();
    document.getElementById('d-rag').textContent = d.rag;
    document.getElementById('d-cer').textContent = d.cerebro.total||0;
    document.getElementById('d-hoje').textContent = d.cerebro.hoje||0;
    document.getElementById('d-au').textContent = d.audit.total||0;
    document.getElementById('d-ram').textContent = d.ram.percent ? d.ram.percent+'%' : '—';
  }catch(e){}
}

async function ragAdd(){
  const t = document.getElementById('r-t').value.trim();
  const c = document.getElementById('r-c').value.trim();
  if(!t||!c) return alert('Preencha tudo');
  const d = await (await fetch('/api/rag/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({titulo:t,conteudo:c})})).json();
  if(d.ok){ document.getElementById('r-t').value=''; document.getElementById('r-c').value=''; alert('Salvo: '+d.arquivo); ragList(); }
  else alert('Erro: '+(d.erro||'?'));
}
async function ragList(){
  const d = await (await fetch('/api/rag/list')).json();
  const b = document.getElementById('r-list');
  if(!d.itens.length){ b.innerHTML='<div class="item"><span class="info">RAG vazio.</span></div>'; return; }
  b.innerHTML = d.itens.map(i=>`<div class="item"><span class="name">[${i.num}] ${esc(i.nome)}</span><span class="info">${i.linhas}l</span><button class="danger" style="padding:3px 8px;font-size:.65rem" onclick="ragDel(${i.num})">X</button></div>`).join('');
}
async function ragDel(n){ if(!confirm('Apagar #'+n+'?')) return; await fetch('/api/rag/del/'+n,{method:'DELETE'}); ragList(); }
async function ragSearch(){
  const q = document.getElementById('r-q').value.trim(); if(!q) return;
  const d = await (await fetch('/api/rag/search?q='+encodeURIComponent(q))).json();
  const b = document.getElementById('r-list');
  b.innerHTML = d.resultados.length ? d.resultados.map(x=>`<div class="item"><span class="name">#${x.num}</span><span class="info">score ${x.score}</span></div>`).join('') : '<div class="item"><span class="info">Nada.</span></div>';
}

async function loadCB(){
  try{
    const d = await (await fetch('/api/cerebro')).json();
    document.getElementById('c-tot').textContent = d.total||0;
    document.getElementById('c-ap').textContent = d.aprov||0;
    document.getElementById('c-hj').textContent = d.hoje||0;
    const b = document.getElementById('c-list');
    b.innerHTML = (d.top&&d.top.length) ? d.top.map(x=>`<div class="item"><span class="name">${x[1].toFixed(1)}</span><span style="flex:1">${esc(x[0])}</span><span class="info">${x[2]}x</span></div>`).join('') : '<div class="item"><span class="info">Vazio.</span></div>';
    const t = await (await fetch('/api/cerebro/today')).json();
    const bh = document.getElementById('c-hoje');
    bh.innerHTML = (t.itens&&t.itens.length) ? t.itens.map(i=>`<div class="item"><span style="color:var(--green)">${i.evento}</span><span style="flex:1">${esc(i.termo)}</span></div>`).join('') : '<div class="item"><span class="info">Nada hoje.</span></div>';
  }catch(e){}
}

async function apSearch(){
  const t = document.getElementById('a-t').value.trim(); if(!t) return;
  const btn = document.getElementById('a-btn'), res = document.getElementById('a-res');
  btn.disabled = true; res.innerHTML = '<div style="color:#888;padding:8px"><span class="spin"></span>Consultando...</div>';
  try{
    const d = await (await fetch('/api/aprend/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({termo:t})})).json();
    if(d.erro) res.innerHTML = '<div style="color:var(--red)">'+esc(d.erro)+'</div>';
    else{
      window._ap = d;
      res.innerHTML = `<div class="card" style="border-color:var(--accent);padding:12px"><h3 style="color:var(--accent);font-size:1rem;margin:0 0 6px 0">${esc(d.titulo)}</h3><div style="color:#888;font-size:.72rem;margin-bottom:8px">${esc(d.fonte)}</div><div style="color:#ddd;font-size:.8rem;line-height:1.5;margin-bottom:10px">${esc(d.extract).slice(0,700)}</div><button onclick="apApprove()">✓ Aprovar e salvar</button></div>`;
    }
  }catch(e){ res.innerHTML = '<div style="color:var(--red)">Erro: '+esc(e.message)+'</div>'; }
  btn.disabled = false;
}
async function apApprove(){
  const d = window._ap; if(!d) return;
  const r = await (await fetch('/api/aprend/approve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({titulo:d.titulo,extract:d.extract,fonte:d.fonte,url:d.url})})).json();
  if(r.ok){ alert('Salvo: '+r.arquivo); document.getElementById('a-res').innerHTML = '<div style="color:var(--green);padding:10px">✓ Salvo no RAG + Cérebro</div>'; }
  else alert('Erro: '+(r.erro||'?'));
}

async function loadAudit(){
  try{
    const s = await (await fetch('/api/audit')).json();
    document.getElementById('au-t').textContent = s.total||0;
    document.getElementById('au-ok').textContent = s.ok||0;
    document.getElementById('au-er').textContent = s.erros||0;
    const d = await (await fetch('/api/audit/recent')).json();
    const b = document.getElementById('au-list');
    b.innerHTML = (d.eventos&&d.eventos.length) ? d.eventos.map(e=>`<div class="item"><span style="color:${e.nivel==='ERROR'?'var(--red)':'var(--green)'};font-family:monospace;font-size:.7rem">${e.nivel}</span><span style="flex:1;font-size:.74rem">${esc((e.msg||'').slice(0,55))}</span><span class="info">${(e.ts||'').slice(11,19)}</span></div>`).join('') : '<div class="item"><span class="info">Sem eventos.</span></div>';
  }catch(e){}
}


async function chatEnviar(){
  const inp = document.getElementById('chat-in'), box = document.getElementById('chat-box'), btn = document.getElementById('chat-btn');
  const msg = inp.value.trim(); if(!msg) return; inp.value=''; btn.disabled=true;
  box.innerHTML += `<div class="item" style="border-left:3px solid var(--viper);padding:10px"><b style="color:var(--viper)">Você:</b> ${esc(msg)}</div>`;
  const idB = 'b'+Date.now();
  box.innerHTML += `<div class="item" id="${idB}" style="border-left:3px solid var(--accent);background:rgba(102,252,241,.05);padding:10px"><b style="color:var(--accent)">NEXUS:</b> <span class="c"></span></div>`;
  box.scrollTop = box.scrollHeight;
  try{
    const resp = await fetch('/api/chat/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    const reader = resp.body.getReader(), dec = new TextDecoder();
    let buf='', full=''; const el = document.getElementById(idB), c = el.querySelector('.c');
    while(true){
      const {done,value} = await reader.read(); if(done) break;
      buf += dec.decode(value,{stream:true});
      const ls = buf.split('\n\n'); buf = ls.pop();
      for(const l of ls){
        if(!l.startsWith('data: ')) continue;
        try{
          const e = JSON.parse(l.slice(6));
          if(e.type==='token'){ full+=e.content; c.textContent=full; box.scrollTop=box.scrollHeight; }
        }catch(_){}
      }
    }
  }catch(e){ document.getElementById(idB).innerHTML = '<b style="color:var(--red)">ERRO:</b> '+esc(e.message); }
  btn.disabled=false; box.scrollTop=box.scrollHeight;
}

loadDash();
setInterval(loadDash, 10000);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   NEXUS · Painel Web                 ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
        print(f"  Local: http://localhost:5001")
        print(f"  Rede:  http://{ip}:5001")
    except: print("  Acesso: http://localhost:5001")
    print()
    print("  CTRL+C para encerrar")
    print()
    app.run(host="0.0.0.0", port=5001, debug=False)
