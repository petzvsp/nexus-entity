from flask import Flask
app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>NEXUS</title>
<style>
body{background:#0b0c10;color:#c5c6c7;font-family:sans-serif;padding:30px;text-align:center}
h1{color:#66fcf1;letter-spacing:3px}
.card{background:#1f2833;padding:20px;border-radius:12px;margin:20px auto;max-width:400px;border:1px solid #66fcf1}
.dot{display:inline-block;width:10px;height:10px;background:#00ff88;border-radius:50%;margin-right:8px;box-shadow:0 0 10px #00ff88}
</style>
</head>
<body>
<h1>◈ NEXUS</h1>
<div class="card">
<p><span class="dot"></span><b>SISTEMA ONLINE</b></p>
<p style="color:#888;font-size:.85rem">Painel mínimo funcionando</p>
<p style="color:#66fcf1;font-family:monospace;margin-top:15px">Se você está vendo isso no navegador, o Flask funciona.</p>
</div>
</body>
</html>"""

@app.route("/")
def home():
    return HTML

if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════╗")
    print("  ║   NEXUS · Painel Minimo           ║")
    print("  ╚══════════════════════════════════╝")
    print()
    print("  Abra no navegador do celular:")
    print("    http://localhost:5001")
    print()
    print("  CTRL+C para encerrar")
    print()
    app.run(host="0.0.0.0", port=5001, debug=False)
