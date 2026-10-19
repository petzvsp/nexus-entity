# viper.py

import os
import json
import datetime
from flask import Flask, render_template_string, request, jsonify
from collections import Counter

app = Flask(__name__)

# --- CORE SYSTEM ENGINE ---
class ViperOrchestrator:
    def __init__(self):
        self.memory = {
            "modules": {},
            "audit_logs": [],
            "logic_weights": {},
            "conversations": []
        }
        self.api_key = "AIzaSyBwk8etVufUe3eurRGi7pltQrhcW7v0gJ8"

    def auto_describe(self, name, content):
        """Gera e incorpora uma descrição baseada no conteúdo do módulo"""
        keywords = [word for word in content.lower().split() if len(word) > 3]
        common = Counter(keywords).most_common(2)
        top_topics = ", ".join([w[0] for w in common]) if common else "Lógica Geral"
        
        description = f"Módulo [{name}] focado em {top_topics}. "
        description += f"Integrado em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}."
        return description

    def save_module(self, name, content, description=None):
        if not description:
            description = self.auto_describe(name, content)
        
        self.memory["modules"][name] = {
            "content": content,
            "description": description,
            "last_audit": datetime.datetime.now().isoformat(),
            "status": "Operacional",
            "weight": round(len(content) / 100, 2)
        }
        self.update_logic()
        return self.memory["modules"][name]

    def delete_module(self, name):
        if name in self.memory["modules"]:
            del self.memory["modules"][name]
            self.update_logic()
            return True
        return False

    def update_logic(self):
        """Calcula a densidade semântica e probabilidade de evolução"""
        all_text = " ".join([m["content"] for m in self.memory["modules"].values()])
        words = all_text.lower().split()
        if words:
            self.memory["logic_weights"] = Counter(words).most_common(10)

    def get_stats(self):
        return {
            "total_modules": len(self.memory["modules"]),
            "memory_usage": f"{len(str(self.memory)) / 1024:.2f} KB",
            "logic_density": len(self.memory["logic_weights"])
        }

viper = ViperOrchestrator()

# --- INTERFACE WEB (MODERN DASHBOARD) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>VIPER SPACE | Control Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0c10; --card: #1f2833; --accent: #66fcf1; --viper: #45a29e; --text: #c5c6c7;
        }
        body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        
        /* Sidebar */
        nav { width: 260px; background: #000; border-right: 1px solid #333; padding: 20px; display: flex; flex-direction: column; }
        .logo-area { text-align: center; margin-bottom: 40px; }
        .logo-area h1 { font-size: 1.2rem; color: var(--accent); letter-spacing: 3px; margin: 10px 0; }
        .nav-link { padding: 12px; margin: 5px 0; border-radius: 8px; cursor: pointer; transition: 0.3s; color: #888; text-decoration: none; display: block; }
        .nav-link:hover { background: var(--card); color: var(--accent); }

        /* Main Content */
        main { flex: 1; padding: 30px; overflow-y: auto; background: linear-gradient(135deg, #0b0c10 0%, #1f2833 100%); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: rgba(31, 40, 51, 0.7); backdrop-filter: blur(10px); padding: 20px; border-radius: 15px; border: 1px solid rgba(102, 252, 241, 0.1); }
        
        /* Module Section */
        .module-entry { background: #000; border: 1px solid var(--viper); padding: 20px; border-radius: 12px; }
        textarea, input { width: 100%; background: #111; border: 1px solid #333; color: white; padding: 10px; margin: 10px 0; border-radius: 5px; font-family: 'JetBrains Mono'; }
        button { background: var(--accent); color: #000; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; }
        
        /* Chat Area */
        .chat-container { height: 300px; background: rgba(0,0,0,0.4); border-radius: 12px; padding: 15px; overflow-y: auto; margin-top: 20px; border: 1px solid #333; }
        .msg { margin-bottom: 10px; padding: 8px; border-radius: 5px; }
        .msg.viper { border-left: 3px solid var(--accent); background: rgba(102, 252, 241, 0.05); }
    </style>
</head>
<body>
    <nav>
        <div class="logo-area">
            <span style="font-size: 40px;">🐍</span>
            <h1>VIPER SPACE</h1>
        </div>
        <a class="nav-link">Dashboard</a>
        <a class="nav-link">Auditores de Sistema</a>
        <a class="nav-link">Base de Dados</a>
        <a class="nav-link">Configurações</a>
    </nav>

    <main>
        <div class="grid">
            <div class="card">
                <h3>Total de Módulos</h3>
                <h2 id="count-mod" style="color: var(--accent);">0</h2>
            </div>
            <div class="card">
                <h3>Peso Lógico</h3>
                <h2 id="logic-weight" style="color: var(--accent);">0.00</h2>
            </div>
            <div class="card">
                <h3>Status API</h3>
                <h2 style="color: #00ff00;">ONLINE</h2>
            </div>
        </div>

        <div class="grid" style="grid-template-columns: 2fr 1fr;">
            <div class="module-entry">
                <h3>Central de Comando: Adicionar Módulo</h3>
                <input type="text" id="m-name" placeholder="Nome do Módulo (ex: NeuroLink)">
                <textarea id="m-content" rows="5" placeholder="Insira a lógica ou funções do sistema aqui..."></textarea>
                <button onclick="saveModule()">Incorporar e Evoluir</button>
                
                <div id="module-list" style="margin-top: 20px;">
                    </div>
            </div>

            <div class="card">
                <h3>Viper Intelligence Chat</h3>
                <div class="chat-container" id="chat">
                    <div class="msg viper">Viper: Sistema auditado. Como posso aperfeiçoar sua lógica hoje?</div>
                </div>
                <input type="text" id="chat-input" placeholder="Pergunte ao Viper...">
                <button onclick="sendChat()" style="width: 100%;">Interagir</button>
            </div>
        </div>
    </main>

    <script>
        async function updateUI() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('count-mod').innerText = data.stats.total_modules;
            
            const list = document.getElementById('module-list');
            list.innerHTML = '<h4>Módulos Ativos</h4>';
            Object.keys(data.modules).forEach(name => {
                const m = data.modules[name];
                list.innerHTML += `
                    <div style="background:#1a1a1a; padding:10px; margin:5px 0; border-radius:5px; border:1px solid #333">
                        <b>${name}</b><br>
                        <small style="color:var(--accent)">${m.description}</small><br>
                        <button onclick="deleteModule('${name}')" style="background:red; color:white; padding:2px 10px; font-size:10px; margin-top:5px;">APAGAR</button>
                    </div>
                `;
            });
        }

        async function saveModule() {
            const name = document.getElementById('m-name').value;
            const content = document.getElementById('m-content').value;
            await fetch('/api/module', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, content})
            });
            updateUI();
        }

        async function deleteModule(name) {
            await fetch(`/api/module/${name}`, { method: 'DELETE' });
            updateUI();
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            const chat = document.getElementById('chat');
            const msg = input.value;
            chat.innerHTML += `<div class="msg">Você: ${msg}</div>`;
            
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            chat.innerHTML += `<div class="msg viper">Viper: ${data.response}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;
        }

        setInterval(updateUI, 3000);
        updateUI();
    </script>
</body>
</html>
"""

# --- API ENDPOINTS ---
@app.route('/')
def index(): return render_template_string(HTML_UI)

@app.route('/api/status')
def get_status():
    return jsonify({"stats": viper.get_stats(), "modules": viper.memory["modules"]})

@app.route('/api/module', methods=['POST'])
def add_mod():
    data = request.json
    mod = viper.save_module(data['name'], data['content'])
    return jsonify(mod)

@app.route('/api/module/<name>', methods=['DELETE'])
def del_mod(name):
    success = viper.delete_module(name)
    return jsonify({"success": success})

@app.route('/api/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '').lower()
    # Lógica de interação Viper
    response = "Análise concluída. "
    if "evoluir" in msg or "aperfeiçoar" in msg:
        response += f"Com base nos {len(viper.memory['modules'])} módulos, sugiro fortalecer a lógica de dados centrais."
    else:
        response += "Sua instrução foi armazenada na memória volátil para cálculos de probabilidade futura."
    return jsonify({"response": response})

if __name__ == '__main__':
    print(">>> VIPER SPACE INICIALIZADO")
    print(">>> ENDEREÇO: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
