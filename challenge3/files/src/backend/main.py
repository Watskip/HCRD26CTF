from flask import Flask, request, render_template_string
import subprocess, os, re
from urllib.parse import parse_qs, unquote

app = Flask(__name__)



HTML = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IntraCorp — Network Tools</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Barlow:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0c0e08;--s:#131508;--border:#232810;--acc:#a8ff00;--acc2:#ff4d00;--text:#c8d4a0;--dim:#4a5530;--mono:"JetBrains Mono",monospace;--sans:"Barlow",sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;display:flex;flex-direction:column}
body::before{content:"";position:fixed;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 20% 80%,rgba(168,255,0,.04) 0%,transparent 50%),radial-gradient(ellipse at 80% 20%,rgba(168,255,0,.02) 0%,transparent 50%);pointer-events:none}
header{border-bottom:1px solid var(--border);padding:0 40px;height:60px;display:flex;align-items:center;justify-content:space-between;background:rgba(12,14,8,.98);position:relative;z-index:10}
.logo{font-family:var(--mono);font-size:14px;color:var(--acc);letter-spacing:4px}
.logo span{color:var(--dim)}
.badge{font-family:var(--mono);font-size:10px;padding:3px 10px;border:1px solid var(--acc2);color:var(--acc2);letter-spacing:2px}
main{flex:1;display:flex;align-items:flex-start;justify-content:center;padding:60px 20px;position:relative;z-index:10}
.container{width:100%;max-width:720px}
.page-tag{font-family:var(--mono);font-size:10px;color:var(--acc);letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;opacity:.7}
h1{font-size:36px;font-weight:700;color:#fff;margin-bottom:6px;line-height:1}
.subtitle{font-family:var(--mono);font-size:12px;color:var(--dim);margin-bottom:40px}
.tool-card{background:var(--s);border:1px solid var(--border);position:relative;overflow:hidden}
.tool-card::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,var(--acc),transparent 70%)}
.tool-header{padding:16px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px}
.tool-dot{width:8px;height:8px;background:var(--acc);border-radius:50%;animation:blink 1.5s step-end infinite}
@keyframes blink{50%{opacity:0}}
.tool-name{font-family:var(--mono);font-size:12px;color:var(--acc);letter-spacing:2px;text-transform:uppercase}
.tool-body{padding:24px}
.form-group{margin-bottom:20px}
label{display:block;font-family:var(--mono);font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--dim);margin-bottom:8px}
.input-wrap{display:flex;align-items:stretch;border:1px solid var(--border);transition:border-color .2s}
.input-wrap:focus-within{border-color:var(--acc)}
.input-prefix{font-family:var(--mono);font-size:12px;padding:12px 14px;background:rgba(168,255,0,.05);color:var(--acc);border-right:1px solid var(--border);white-space:nowrap}
input{flex:1;background:var(--bg);border:none;color:var(--text);font-family:var(--mono);font-size:14px;padding:12px 14px;outline:none}
button{width:100%;background:var(--acc);color:#000;border:none;font-family:var(--mono);font-size:12px;font-weight:700;letter-spacing:3px;text-transform:uppercase;padding:14px;cursor:pointer;transition:all .2s}
button:hover{background:#c8ff30;box-shadow:0 0 30px rgba(168,255,0,.3)}
.terminal{margin-top:24px;background:#050605;border:1px solid var(--border);font-family:var(--mono);font-size:13px;overflow:hidden}
.terminal-bar{padding:8px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px;background:rgba(168,255,0,.03)}
.t-dot{width:6px;height:6px;border-radius:50%}
.terminal-output{padding:20px;color:var(--text);white-space:pre-wrap;word-break:break-all;max-height:320px;overflow-y:auto;line-height:1.6}
.terminal-output.flag-found{color:var(--acc);text-shadow:0 0 10px rgba(168,255,0,.5)}
.terminal-output.blocked{color:var(--acc2)}
.filter-panel{margin-top:24px;background:var(--s);border:1px solid var(--border);padding:20px 24px}
.filter-panel h3{font-family:var(--mono);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--acc);margin-bottom:14px;opacity:.7}
.filter-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.filter-row{display:flex;align-items:center;gap:10px;padding:8px 12px;background:rgba(0,0,0,.3);border:1px solid var(--border)}
.filter-key{font-family:var(--mono);font-size:12px;color:#fff;background:rgba(255,77,0,.15);border:1px solid rgba(255,77,0,.3);padding:2px 8px}
.filter-desc{font-size:12px;color:var(--dim)}
.filter-status{font-family:var(--mono);font-size:9px;letter-spacing:1px;color:var(--acc2);margin-left:auto}
footer{border-top:1px solid var(--border);padding:20px 40px;display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;color:var(--dim);position:relative;z-index:10}
</style>
</head>
<body>
<header>
  <div class="logo">INTRA<span>CORP</span> / TOOLS</div>
  <div class="badge">&#9888; Internal Tools</div>
</header>
<main>
  <div class="container">
    <div class="page-tag">tools.intracorp.local</div>
    <h1>Network<br>Diagnostics</h1>
    <p class="subtitle">// Herramientas internas de diagnostico de red</p>
    <div class="tool-card">
      <div class="tool-header">
        <div class="tool-dot"></div>
        <span class="tool-name">ping - Utilidad de diagnostico</span>
      </div>
      <div class="tool-body">
        <form method="POST" action="/tools/ping">
          <div class="form-group">
            <label>Target Host / IP</label>
            <div class="input-wrap">
              <div class="input-prefix">ping -c 2</div>
              <input type="text" name="target" placeholder="8.8.8.8" value="{{ target or '' }}" autocomplete="off">
            </div>
          </div>
          <button type="submit">Ejecutar Ping</button>
        </form>
        {% if output is not none %}
        <div class="terminal">
          <div class="terminal-bar">
            <div class="t-dot" style="background:#ff5f56"></div>
            <div class="t-dot" style="background:#ffbd2e"></div>
            <div class="t-dot" style="background:#27c93f"></div>
            <span style="font-family:var(--mono);font-size:10px;color:var(--dim);margin-left:8px">tools.intracorp.local - bash</span>
          </div>
          <div class="terminal-output {{ out_class }}">{{ output }}</div>
        </div>
        {% endif %}
      </div>
    </div>
    <div class="filter-panel">
      <h3>// FRASE MOTIVADORA </h3>
      <div class="filter-grid">
        <div class="filter-row"><span class="filter-key">😵‍💫</span><span class="filter-desc">“Que la lógica te acompañe… porque la suerte ya se fue.”</span><span class="filter-status">SUERTE</span></div>
      </div>
    </div>
  </div>
</main>
<footer>
  <span>IntraCorp NetTools v1.8</span>
  <span>IntraCorp Internal Systems</span>
</footer>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML, output=None, out_class='', target='')

@app.route('/tools/ping', methods=['POST'])
def ping():
    raw_body = request.get_data(as_text=True)
    parsed = parse_qs(raw_body, keep_blank_values=True)
    target_list = parsed.get('target', [''])
    target_raw = target_list[0] if target_list else ''
    target = unquote(target_raw)

    blacklist_chars = [';', '&', '|', '$']
    for bad in blacklist_chars:
        if bad in target:
            return render_template_string(HTML,
                output="[BLOQUEADO] Caracter no permitido detectado: '" + bad + "'",
                out_class='blocked', target=target_raw)

    if re.search(r'\bcat\b', target):
        return render_template_string(HTML,
            output="[BLOQUEADO] Comando 'cat' no permitido.",
            out_class='blocked', target=target_raw)

    try:
        result = subprocess.run(
            'ping -c 2 ' + target,
            shell=True,
            capture_output=True,
            text=True,
            timeout=12
        )
        output = result.stdout + result.stderr
        if not output.strip():
            output = "[sin salida del comando]"
        flag_found = 'flag{' in output
        return render_template_string(HTML,
            output=output,
            out_class='flag-found' if flag_found else '',
            target=target_raw)
    except subprocess.TimeoutExpired:
        return render_template_string(HTML, output="Timeout: el host no responde.", out_class='blocked', target=target_raw)
    except Exception as e:
        return render_template_string(HTML, output="Error: " + str(e), out_class='blocked', target=target_raw)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
