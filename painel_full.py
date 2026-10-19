import os, sys, json, re, socket, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_with_context

NEXUS = Path.home() / "nexus-system"
sys.path.insert(0, str(NEXUS))

try: import memoria
except: memoria = None
try: import cerebro_aprendizado as cerebro
except: cerebro = None
try: import apis_publicas as apis
except: apis = None

app = Flask(__name__)
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "nexus-pt"
TOPICOS = NEXUS / "memoria" / "topicos"
TOPICOS.mkdir(parents=True, exist_ok=True)

def load_system():
    sf = NEXUS / "system.txt"
    return sf.read_text(encoding="utf-8").strip() if sf.exists() else "Voce e a NEXUS. Responda em portugues."

def ollama_stream(messages):
    payload = {"model": MODEL, "messages": messages, "stream": True, "options": {"temperature": 0.3, "num_ctx": 2048}}
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=300)
    except Exception as e:
        yield f"[ERRO] Ollama offline: {e}"; return
    for line in resp:
        if not line.strip(): continue
        try:
            data = json.loads(line.decode())
            content = data.get("message", {}).get("content", "")
            if content: yield content
            if data.get("done"): break
        except: continue

def slug(t):
    return re.sub(r'[^\w\s-]', '', t.lower()).strip().replace(' ', '_')[:50]

@app.route("/")
def index(): return Response(HTML, mimetype="text/html")

@app.route("/api/status")
def api_status():
    ram = {}
    try:
        with open('/proc/meminfo') as f: info = f.read()
        total = int(re.search(r'MemTotal:\s+(\d+)', info).group(1)) / 1024 / 1024
        avail = int(re.search(r'MemAvailable:\s+(\d+)', info).group(1)) / 1024 / 1024
        ram = {"percent": round(((total-avail)/total)*100, 1)}
    except: pass
    ollama_ok = False
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1); ollama_ok = True
    except: pass
    cb = cerebro.estatisticas() if cerebro else {"total": 0, "hoje": 0}
    return jsonify({"rag": len(memoria.listar()) if memoria else 0, "cb": cb, "ram": ram, "ollama": ollama_ok})

@app.route("/api/chat/stream", methods=["POST"])
def api_chat():
    msg = request.json.get("message", "").strip()
    if not msg: return jsonify({"erro": "vazio"}), 400
    ctx, arqs = ("", [])
    if memoria:
        try: ctx, arqs = memoria.montar_contexto(msg, limite=3)
        except: pass
    system = load_system()
    if ctx: system += f"\n\n[MEMORIA]\n{ctx}"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": msg}]
    def generate():
        yield f"data: {json.dumps({'type':'meta','rag':arqs})}\n\n"
        full = ""
        for tok in ollama_stream(messages):
            full += tok
            yield f"data: {json.dumps({'type':'token','content':tok})}\n\n"
        yield f"data: {json.dumps({'type':'done'})}\n\n"
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/api/rag/add", methods=["POST"])
def api_rag_add():
    d = request.json
    nome = slug(d['titulo']) + ".md"
    dst = TOPICOS / nome
    dst.write_text(f"# {d['titulo']}\n\n{d['conteudo']}", encoding="utf-8")
    if memoria: memoria.adicionar(dst)
    if cerebro: cerebro.registrar_aprovacao(d['titulo'], d['conteudo'], "Web")
    return jsonify({"ok": True})

@app.route("/api/rag/list")
def api_rag_list(): return jsonify({"itens": memoria.listar() if memoria else []})

@app.route("/api/cerebro")
def api_cb(): return jsonify(cerebro.estatisticas() if cerebro else {"total":0, "top":[], "hoje":0})

@app.route("/api/aprend/search", methods=["POST"])
def api_search():
    termo = request.json.get("termo", "")
    try:
        s = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(termo)}&format=json&srlimit=1"
        d = json.loads(urllib.request.urlopen(s, timeout=10).read())
        t = d["query"]["search"][0]["title"]
        r = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(t)}"
        sd = json.loads(urllib.request.urlopen(r, timeout=10).read())
        return jsonify({"titulo": t, "extract": sd["extract"], "fonte": "Wikipedia"})
    except: return jsonify({"erro": "Nada encontrado"}), 404

@app.route("/api/aprend/approve", methods=["POST"])
def api_approve():
    d = request.json
    nome = slug(d['titulo']) + ".md"
    dst = TOPICOS / nome
    dst.write_text(f"# {d['titulo']}\n\n{d['extract']}", encoding="utf-8")
    if memoria: memoria.adicionar(dst)
    if cerebro: cerebro.registrar_aprovacao(d['titulo'], d['extract'], d['fonte'])
    return jsonify({"ok": True})

@app.route("/api/apis/list")
def api_apis_list(): return jsonify({"apis": [{"key":k, "nome":v["nome"]} for k,v in apis.APIS.items()]} if apis else {"apis":[]})

@app.route("/api/apis/query", methods=["POST"])
def api_apis_query():
    d = request.json
    r = apis.buscar(d['key'], d['termo']) if apis else None
    if r: return jsonify({"titulo": r[0], "texto": r[1], "fonte": r[2]})
    return jsonify({"erro": "Falha na API"}), 500

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEXUS FULL</title>
<style>
:root{--bg:#06040e;--card:#1f2833;--acc:#66fcf1;--txt:#c5c6c7;--red:#ff5555;--grn:#00ff88}
*{margin:0;padding:0;box-sizing:border-box;font-family:sans-serif}
body{background:var(--bg);color:var(--txt);display:flex;flex-direction:column;height:100vh}
nav{background:#000;display:flex;overflow-x:auto;padding:8px;gap:4px;border-bottom:1px solid #333}
.nav{padding:8px 12px;color:#888;cursor:pointer;border-radius:6px;font-size:.8rem;white-space:nowrap}
.nav.on{background:rgba(102,252,241,.1);color:var(--acc)}
main{flex:1;padding:15px;overflow-y:auto}
.sec{display:none}.sec.on{display:block}
h2{color:var(--acc);font-size:1.1rem;margin-bottom:12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:15px}
.card{background:var(--card);padding:12px;border-radius:8px;border:1px solid rgba(102,252,241,.1)}
.card .l{font-size:.6rem;color:#888;text-transform:uppercase}.card .v{font-size:1.2rem;color:var(--acc);font-weight:bold}
input,textarea,select{width:100%;background:#111;border:1px solid #333;color:#fff;padding:10px;margin-bottom:8px;border-radius:6px}
button{background:var(--acc);color:#000;border:none;padding:10px;border-radius:6px;font-weight:bold;cursor:pointer;width:100%}
.chat{height:60vh;overflow-y:auto;background:#000;border:1px solid #333;border-radius:8px;padding:10px;margin-bottom:10px;display:flex;flex-direction:column;gap:8px}
.msg{padding:8px;border-radius:6px;font-size:.85rem;white-space:pre-wrap}
.msg.u{border-left:3px solid var(--grn);background:#111}
.msg.n{border-left:3px solid var(--acc);background:rgba(102,252,241,.05)}
.item{background:#000;border:1px solid #333;padding:8px;border-radius:6px;margin-bottom:4px;font-size:.8rem}
</style>
</head>
<body>
<nav>
<div class="nav on" onclick="ir('dash',this)">📊 Dash</div>
<div class="nav" onclick="ir('chat',this)">💬 Chat</div>
<div class="nav" onclick="ir('rag',this)">📚 RAG</div>
<div class="nav" onclick="ir('cb',this)">🧠 Cérebro</div>
<div class="nav" onclick="ir('ap',this)">🎓 Aprender</div>
<div class="nav" onclick="ir('api',this)">🌐 APIs</div>
</nav>
<main>

<div class="sec on" id="s-dash">
  <h2>Dashboard</h2>
  <div class="grid">
    <div class="card"><div class="l">Ollama</div><div class="v" id="v-ollama">-</div></div>
    <div class="card"><div class="l">RAM</div><div class="v" id="v-ram">-</div></div>
    <div class="card"><div class="l">RAG</div><div class="v" id="v-rag">0</div></div>
    <div class="card"><div class="l">Cérebro</div><div class="v" id="v-cb">0</div></div>
  </div>
</div>

<div class="sec" id="s-chat">
  <h2>Chat NEXUS</h2>
  <div class="chat" id="box"><div class="msg n"><b>NEXUS:</b> Pronto.</div></div>
  <input id="i-chat" placeholder="Pergunte..." onkeypress="if(event.key==='Enter')enviar()">
  <button onclick="enviar()" id="b-chat">Enviar</button>
</div>

<div class="sec" id="s-rag">
  <h2>RAG</h2>
  <input id="r-t" placeholder="Título">
  <textarea id="r-c" rows="3" placeholder="Conteúdo"></textarea>
  <button onclick="addRag()">Salvar no RAG</button>
  <div style="margin-top:15px" id="l-rag"></div>
</div>

<div class="sec" id="s-cb">
  <h2>Cérebro</h2>
  <div class="grid">
    <div class="card"><div class="l">Total</div><div class="v" id="v-cb2">0</div></div>
    <div class="card"><div class="l">Hoje</div><div class="v" id="v-cbh">0</div></div>
  </div>
  <div id="l-cb"></div>
</div>

<div class="sec" id="s-ap">
  <h2>Aprender</h2>
  <input id="a-t" placeholder="Tema (ex: python)" onkeypress="if(event.key==='Enter')buscar()">
  <button onclick="buscar()" id="b-ap">Buscar</button>
  <div id="res-ap" style="margin-top:10px"></div>
</div>

<div class="sec" id="s-api">
  <h2>APIs</h2>
  <select id="api-sel" size="5" style="margin-bottom:8px"></select>
  <input id="api-t" placeholder="Termo">
  <button onclick="apiQ()">Consultar</button>
  <div id="res-api" style="margin-top:10px"></div>
</div>

</main>
<script>
function ir(id, el){
  document.querySelectorAll('.sec').forEach(s=>s.classList.remove('on'));
  document.querySelectorAll('.nav').forEach(n=>n.classList.remove('on'));
  document.getElementById('s-'+id).classList.add('on');
  el.classList.add('on');
  if(id==='dash') loadDash();
  if(id==='rag') loadRag();
  if(id==='cb') loadCb();
  if(id==='api' && !window.apiOn) loadApis();
}
async function loadDash(){
  const d = await (await fetch('/api/status')).json();
  document.getElementById('v-ollama').innerHTML = d.ollama ? '<span style="color:var(--grn)">ON</span>' : '<span style="color:var(--red)">OFF</span>';
  document.getElementById('v-ram').innerText = d.ram.percent ? d.ram.percent+'%' : '-';
  document.getElementById('v-rag').innerText = d.rag;
  document.getElementById('v-cb').innerText = d.cb.total;
}
async function enviar(){
  const i=document.getElementById('i-chat'), b=document.getElementById('box'), btn=document.getElementById('b-chat');
  if(!i.value.trim()) return;
  b.innerHTML += `<div class="msg u"><b>Você:</b> ${i.value}</div>`;
  const txt = i.value; i.value=''; btn.disabled=true;
  const id='m'+Date.now();
  b.innerHTML += `<div class="msg n" id="${id}"><b>NEXUS:</b> <span class="c"></span></div>`;
  b.scrollTop = b.scrollHeight;
  const res = await fetch('/api/chat/stream', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:txt})});
  const rd = res.body.getReader(); const dec = new TextDecoder();
  let full='', buf=''; const c = document.querySelector(`#${id} .c`);
  while(true){
    const {done,value} = await rd.read(); if(done) break;
    buf += dec.decode(value,{stream:true});
    const ls = buf.split('\n\n'); buf=ls.pop();
    for(const l of ls){
      if(l.startsWith('data: ')){
        const d = JSON.parse(l.slice(6));
        if(d.type==='token'){ full+=d.content; c.innerText=full; b.scrollTop=b.scrollHeight; }
      }
    }
  }
  btn.disabled=false;
}
async function addRag(){
  const t=document.getElementById('r-t').value, c=document.getElementById('r-c').value;
  if(!t||!c) return;
  await fetch('/api/rag/add', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({titulo:t, conteudo:c})});
  document.getElementById('r-t').value=''; document.getElementById('r-c').value='';
  alert('Salvo!'); loadRag();
}
async function loadRag(){
  const d = await (await fetch('/api/rag/list')).json();
  document.getElementById('l-rag').innerHTML = d.itens.map(i=>`<div class="item">[${i.num}] ${i.nome}</div>`).join('');
}
async function loadCb(){
  const d = await (await fetch('/api/cerebro')).json();
  document.getElementById('v-cb2').innerText = d.total;
  document.getElementById('v-cbh').innerText = d.hoje;
  document.getElementById('l-cb').innerHTML = d.top.map(t=>`<div class="item"><b style="color:var(--acc)">${t[1].toFixed(1)}</b> - ${t[0]}</div>`).join('');
}
async function buscar(){
  const t=document.getElementById('a-t').value; if(!t)return;
  const btn=document.getElementById('b-ap'), r=document.getElementById('res-ap');
  btn.disabled=true; r.innerHTML='Buscando...';
  const d = await (await fetch('/api/aprend/search', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({termo:t})})).json();
  if(d.erro) r.innerHTML = `<span style="color:red">${d.erro}</span>`;
  else {
    window._d = d;
    r.innerHTML = `<div class="card"><h3>${d.titulo}</h3><p style="font-size:.8rem;margin:8px 0">${d.extract.slice(0,300)}...</p><button onclick="aprovar()">Aprovar</button></div>`;
  }
  btn.disabled=false;
}
async function aprovar(){
  await fetch('/api/aprend/approve', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(window._d)});
  alert('Salvo no RAG!'); document.getElementById('res-ap').innerHTML='';
}
async function loadApis(){
  window.apiOn = true;
  const d = await (await fetch('/api/apis/list')).json();
  document.getElementById('api-sel').innerHTML = d.apis.map(a=>`<option value="${a.key}">${a.nome}</option>`).join('');
}
async function apiQ(){
  const k=document.getElementById('api-sel').value, t=document.getElementById('api-t').value;
  const r=document.getElementById('res-api'); r.innerHTML='Buscando...';
  const d = await (await fetch('/api/apis/query', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:k, termo:t})})).json();
  if(d.erro) r.innerHTML = `<span style="color:red">${d.erro}</span>`;
  else r.innerHTML = `<div class="card"><b>${d.titulo}</b><p style="font-size:.8rem;margin-top:8px">${d.texto.slice(0,300)}...</p></div>`;
}
loadDash();
</script>
</body>
</html>
