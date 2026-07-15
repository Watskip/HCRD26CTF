from flask import Flask, request, render_template_string, jsonify
import subprocess
import platform

app = Flask(__name__)

# Middleware para verificar User-Agent en todas las rutas
@app.before_request
def check_compatibility():
    ua = request.headers.get('User-Agent', '')
    # Windows XP se identifica típicamente como 'Windows NT 5.1'
    if 'Windows NT 5.1' not in ua:
        return render_template_string("""
            <html>
            <body style="background-color: #000; color: red; font-family: monospace; text-align: center; padding-top: 50px;">
                <h1>403 FORBIDDEN</h1>
                <p>SYSTEM ERROR: INCOMPATIBLE OS DETECTED.</p>
                <p>This legacy management console is only accessible from validated <b>Windows XP Workstations</b>.</p>
                <p>Your User-Agent identifies as: {{ ua }}</p>
            </body>
            </html>
        """, ua=ua), 403

@app.route('/')
def index():
    return render_template_string("""
    <html>
    <head><title>WinXP Admin Panel</title></head>
    <body style="background-color:#ece9d8; font-family: Tahoma, sans-serif;">
        <div style="background-color:#0054e3; color:white; padding:10px; font-weight:bold;">
            Windows XP Professional - Administration Tool
        </div>
        <div style="padding:20px;">
            <h3>Available Modules:</h3>
            <ul>
                <li><a href="/api/status">System Health Check</a> (v1.0)</li>
                <li><a href="/api/logs">Event Viewer Logs</a> (Read-Only)</li>
                <li><a href="/tools/network">Network Diagnostic Tool</a> (Ping Utility)</li>
            </ul>
        </div>
        <div style="position:fixed; bottom:0; width:100%; text-align:center; font-size:10px; color:gray;">
            Microsoft Corporation - Internal Use Only
        </div>
    </body>
    </html>
    """)

# Endpoint 1: Seguro - Información estática
@app.route('/api/status')
def status():
    return jsonify({
        "cpu_load": "12%",
        "memory_free": "512MB",
        "uptime": "42 days",
        "service_status": "HEALTHY"
    })

# Endpoint 2: Seguro - Logs falsos
@app.route('/api/logs')
def logs():
    return jsonify([
        {"id": 101, "msg": "Service started successfully"},
        {"id": 102, "msg": "User Admin logged in"},
        {"id": 103, "msg": "Backup completed"}
    ])

# Endpoint 3: UI de la herramienta de diagnóstico de red
@app.route('/tools/network', methods=['GET'])
def net_tool_ui():
    return render_template_string("""
    <html>
    <body style="background-color:#ece9d8; font-family: Tahoma;">
        <h3>Network Diagnostic Utility</h3>
        <form action="/api/net-diag" method="POST">
            Target IP: <input type="text" name="ip" value="127.0.0.1">
            <input type="submit" value="Ping">
        </form>
    </body>
    </html>
    """)

# Endpoint 4: ejecución del diagnóstico de red
@app.route('/api/net-diag', methods=['POST'])
def net_tool_exec():
    target = request.form.get('ip', '')
    
    if not target:
        return "Error: IP required", 400

    cmd = f"ping -c 2 {target}"

    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return f"<pre>{output.decode('utf-8')}</pre>"
    except subprocess.CalledProcessError as e:
        # Retornamos el output incluso en error para facilitar el debugging al atacante (CTF Básico)
        return f"<pre>Execution Error:\n{e.output.decode('utf-8') if e.output else 'Unknown Error'}</pre>"
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
