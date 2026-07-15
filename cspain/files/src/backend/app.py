from flask import Flask, render_template_string, request, redirect, abort, make_response, session
import threading


TEMPLATE_LOGIN = r"""<!DOCTYPE html>
<html lang="es" class="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Restringido - Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>

<body class="bg-slate-950 flex items-center justify-center min-h-screen p-4 relative overflow-hidden">

    <!-- Background Decor -->
    <div class="absolute -top-40 -right-40 w-96 h-96 bg-blue-600/10 rounded-full blur-[100px]"></div>
    <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-[100px]"></div>

    <div
        class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl relative z-10 overflow-hidden">

        <div class="h-2 w-full bg-gradient-to-r from-blue-500 to-indigo-600"></div>

        <div class="p-8">
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-500/10 mb-4">
                    <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z">
                        </path>
                    </svg>
                </div>
                <h2 class="text-2xl font-bold text-white mb-2">Acceso al Sistema</h2>
                <p class="text-sm text-slate-400">Autenticación requerida para continuar</p>
            </div>

            <form action="/login" method="POST" class="space-y-6">
                <div>
                    <label for="username" class="block text-sm font-medium text-slate-300 mb-2">Usuario</label>
                    <input type="text" id="username" name="username" required
                        class="w-full px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        placeholder="Ingresa tu usuario">
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-slate-300 mb-2">Contraseña</label>
                    <input type="password" id="password" name="password" required
                        class="w-full px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        placeholder="••••••••">
                </div>

                <button type="submit"
                    class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 focus:ring-offset-slate-900 transition-colors mt-2">
                    Iniciar Sesión
                </button>
            </form>


        </div>

        <div class="bg-slate-950/50 border-t border-slate-800 p-4 text-center">
            <p class="text-xs text-slate-500 font-mono mt-2">Created by <a href="https://github.com/mil4ne" target="_blank" class="text-indigo-400 hover:text-indigo-300 transition-colors font-bold">mil4ne</a></p>
        </div>
    </div>
</body>

</html>"""
TEMPLATE_FAIL = r"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Denegado</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-950 flex items-center justify-center min-h-screen p-4">
    
    <div class="text-center space-y-6 max-w-md">
        <div class="inline-flex items-center justify-center w-24 h-24 rounded-full bg-rose-500/10 mb-2 animate-pulse">
            <svg class="w-12 h-12 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        </div>
        
        <h1 class="text-4xl font-bold text-white">401 No Autorizado</h1>
        <p class="text-slate-400 text-lg">Credenciales incorrectas o acceso no permitido.</p>
        
        <div class="pt-8 block">
            <a href="/login" class="text-sm font-medium px-6 py-3 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition-colors border border-slate-700">
                Volver al Login
            </a>
        </div>
    </div>

</body>
</html>
"""
TEMPLATE_PANEL = r"""<!DOCTYPE html>
<html lang="es" class="dark">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Usuario</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap"
        rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }

        code {
            font-family: 'JetBrains Mono', monospace;
        }
    </style>
</head>

<body class="bg-slate-950 text-slate-300 min-h-screen">


    <nav class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16 items-center">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                        <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z">
                            </path>
                        </svg>
                    </div>
                    <span class="font-bold text-white text-lg tracking-tight">User Portal</span>
                </div>
                <div>
                    <a href="/"
                        class="text-sm font-medium px-4 py-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors border border-transparent hover:border-slate-700">
                        Cerrar Sesión
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Contenido principal -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

        <div class="mb-8">
            <h1 class="text-3xl font-bold text-white tracking-tight">Panel de Control</h1>
            <p class="mt-2 text-slate-400">Gestiona y supervisa tus herramientas de red.</p>
        </div>

        {% if report_msg %}
        <div class="mb-8 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-6 py-4 rounded-xl flex items-center">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ report_msg }}
        </div>
        {% endif %}

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">

            <!-- Estado del sistema -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm p-6 relative overflow-hidden">
                <div class="absolute top-0 right-0 p-6">
                    <span class="flex h-3 w-3 relative">
                        <span
                            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                    </span>
                </div>
                <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01">
                        </path>
                    </svg>
                    Estado del Sistema
                </h3>

                <div class="space-y-4">
                    <div class="flex justify-between items-center py-2 border-b border-slate-800">
                        <span class="text-slate-400">Estado</span>
                        <span
                            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            Operativo
                        </span>
                    </div>
                    <div class="flex justify-between items-center py-2 border-b border-slate-800">
                        <span class="text-slate-400">Último Acceso</span>
                        <code class="text-slate-300 text-sm">24/08/2024 18:45</code>
                    </div>
                </div>
            </div>


        </div>

        <!-- Nuevo apartado: Enviar Reporte -->
        <div class="bg-indigo-900/20 border border-indigo-500/30 rounded-2xl shadow-sm p-6 relative overflow-hidden">
            <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z">
                    </path>
                </svg>
                Reportar Incidencia
            </h3>
            <p class="text-xs text-slate-400 mb-4">Usa este formulario para reportar fallas en la red. El administrador
                revisará cada reporte individualmente.</p>
            <form action="/report" method="POST" class="space-y-4">
                <div>
                    <input type="text" name="title" required placeholder="Título del reporte (ej: Caída de DNS)"
                        class="w-full px-4 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors">
                </div>
                <div>
                    <textarea name="desc" placeholder="Descripción breve..." rows="2"
                        class="w-full px-4 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"></textarea>
                </div>
                <button type="submit"
                    class="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg transition-colors">Enviar
                    Reporte Urgente</button>
            </form>
        </div>
        </div>
        <div class="mt-6 bg-slate-900 border border-slate-800 rounded-2xl shadow-sm p-6 relative overflow-hidden">
            <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z">
                    </path>
                </svg>
                Buscador de Logs
            </h3>

            <form action="" method="GET" class="flex gap-4">
                <input type="text" name="q" placeholder="Buscar por IP o Protocolo..."
                    class="w-full px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                <button type="submit"
                    class="px-6 py-3 border border-transparent rounded-xl shadow-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 focus:outline-none transition-colors">Buscar</button>
            </form>


            <div class="mt-4 text-slate-400 text-sm">
                {% if query %}
                Resultados para búsqueda: <span class="text-white break-all">{{ query | safe }}</span>
                {% else %}
                Mostrando registro completo de tráfico de red:
                {% endif %}

                <div class="mt-4 border border-slate-700/50 rounded-lg overflow-hidden bg-slate-900/50">
                    <div class="bg-slate-800/80 px-4 py-3 text-xs font-semibold text-slate-300 uppercase tracking-wider border-b border-slate-700/50">
                        Capturas de Tráfico Reciente (Wireshark Logs)</div>

                    {% if logs %}
                    <ul class="divide-y divide-slate-800/50 font-mono text-xs overflow-y-auto max-h-96">
                        {% for log in logs %}
                        <li
                            class="p-3 hover:bg-slate-800/30 flex flex-col md:flex-row gap-2 md:gap-4 transition-colors">
                            <span class="{{ log['color'] }} font-bold w-16 shrink-0">[{{ log['proto'] }}]</span>
                            <span class="text-slate-500 w-24 shrink-0">{{ log['time'] }}</span>
                            <span class="text-slate-400 break-all">{{ log['desc'] }}</span>
                        </li>
                        {% endfor %}
                    </ul>
                    {% else %}
                    <p class="text-slate-500 italic p-6 text-center">No se encontraron paquetes o eventos de red para la
                        instrucción actual.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </main>

    <footer class="py-6 mt-auto">
        <div class="text-center text-sm text-slate-500 font-mono">
            Created by <a href="https://github.com/mil4ne" target="_blank"
                class="text-indigo-400 hover:text-indigo-300 font-bold">mil4ne</a>
        </div>
    </footer>

    <!-- Cuidao' -->
    <script src="/api/status?callback=initApp"></script>
</body>

</html>"""
TEMPLATE_VIEW_REPORT = r"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizando Reporte</title>
    <!-- Tailwind allowed via CSP -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-300 min-h-screen p-8">
    <div class="max-w-2xl mx-auto bg-slate-900 border border-slate-800 rounded-2xl shadow-sm p-8">
        <h1 class="text-2xl font-bold text-white mb-2">Revisión de Reporte</h1>
        <p class="text-sm text-slate-400 mb-6">El sistema automatizado está inspeccionando el siguiente reporte reportado por un empleado.</p>
        
        <div class="bg-slate-950 border border-slate-700 rounded-lg p-6">
            <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Título del Reporte</h2>
            <div class="text-lg text-white font-medium break-all">
                {{ title | safe }}
            </div>
        </div>

        <div class="mt-6 flex justify-end">
            <button class="px-4 py-2 bg-indigo-600/50 text-indigo-200 cursor-not-allowed rounded-lg text-sm font-semibold opacity-50">Cerrar Ticket (Solo Admin)</button>
        </div>
    </div>
    
    <script src="/api/status?callback=initApp"></script>
</body>
</html>
"""

app = Flask(__name__)
app.secret_key = "cspain_super_secret_key_13377468245823572_mil4ne"

bot_lock = threading.Lock()
active_bots = 0

# Simulated Network Traffic Logs
import random
from datetime import datetime, timedelta

def generate_fake_logs():
    logs = []
    base_time = datetime.strptime("08:00:00.000", "%H:%M:%S.%f")
    protocols = [
        ("TCP", "text-indigo-400", "10.88.0.5:{} -> 10.88.0.2:80 [SYN] Seq=0 Win=65535 Len=0"),
        ("TCP", "text-indigo-400", "10.88.0.2:80 -> 10.88.0.5:{} [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0"),
        ("TCP", "text-indigo-400", "10.88.0.5:{} -> 10.88.0.2:80 [ACK] Seq=1 Ack=1 Win=65535 Len=0"),
        ("HTTP", "text-sky-400", "GET /assets/style.css HTTP/1.1 - 200 OK"),
        ("HTTP", "text-sky-400", "GET /api/health HTTP/1.1 - 404 Not Found"),
        ("HTTP", "text-sky-400", "POST /admin/login HTTP/1.1 - 302 Found"),
        ("SSH", "text-rose-400", "Failed password for invalid user admin from 192.168.1.10{} port 38212 ssh2"),
        ("SSH", "text-rose-400", "Disconnected from user root 10.88.0.50 port 44123"),
        ("UDP", "text-emerald-400", "Standard query 0x1a2b A info.cspain.hl"),
        ("DNS", "text-purple-400", "Standard query response 0x1a2b A 10.88.0.2"),
        ("ICMP", "text-teal-400", "Echo (ping) request id=0x1121, seq={}, ttl=64"),
        ("SMTP", "text-fuchsia-400", "220 mail.cspain.hl ESMTP Postfix"),
        ("QUIC", "text-pink-400", "Payload: Initial, DCID=0x1a2b3c4d, SCID=0x9f8e7d6c"),
    ]
    
    for i in range(120):
        base_time += timedelta(seconds=random.randint(1, 120), milliseconds=random.randint(0, 999))
        proto, color, desc_temp = random.choice(protocols)
        if "{}" in desc_temp:
            if proto == "TCP":
                desc = desc_temp.format(random.randint(10000, 60000))
            elif proto == "SSH":
                desc = desc_temp.format(random.randint(0, 9))
            elif proto == "ICMP":
                desc = desc_temp.format(i)
            else:
                desc = desc_temp
        else:
            desc = desc_temp
            
        logs.append({
            "proto": proto,
            "color": color,
            "time": base_time.strftime("%H:%M:%S.%f")[:-3],
            "desc": desc
        })
        
    logs.insert(75, {"proto": "FTP", "color": "text-amber-400", "time": "12:22:45.001", "desc": "USER anonymous - Login successful."})
    logs.insert(76, {"proto": "FTP", "color": "text-amber-400", "time": "12:23:10.452", "desc": "Response: 530 Login incorrect. [USER: backup_admin | PASS: b4ckup_p4ssw0rd_2024!]"})
    logs.insert(77, {"proto": "FTP", "color": "text-amber-400", "time": "12:25:01.992", "desc": "QUIT - Goodbye."})
    
    logs.sort(key=lambda x: x['time'])
    return logs

fake_logs = generate_fake_logs()

def visit_url(url):
    global active_bots
    driver = None
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--no-proxy-server')
        
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get('http://127.0.0.1:9745/')
        driver.add_cookie({"name": "flag", "value": "HCRD{CSP_Kill3r_Da4mm}", "path": "/"})
        
        driver.get(url)
        
        import time
        time.sleep(3)
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        with bot_lock:
            active_bots -= 1

@app.route('/')
@app.route('/login')
def login_page():
    return render_template_string(TEMPLATE_LOGIN)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if username == "user" and password == "user":
        session['logged_in'] = True
        return redirect('/panel')
    
    return redirect('/fail')

@app.route('/fail')
def fail():
    return render_template_string(TEMPLATE_FAIL)

@app.route('/panel')
def user_panel():
    if request.remote_addr != '127.0.0.1' and not session.get('logged_in'):
        return redirect('/login')

    query = request.args.get('q', '')
    report_msg = request.args.get('report_msg', '')
        
    filtered_logs = fake_logs
    if query:
        q_upper = query.upper()
        filtered_logs = [log for log in fake_logs if q_upper in log['proto'].upper() or q_upper in log['desc'].upper()]

    resp = make_response(render_template_string(TEMPLATE_PANEL, query=query, logs=filtered_logs, report_msg=report_msg))
    
    # Panel: solo scripts de cdn.jsdelivr.net (no inline). El jugador debe alojar su JS en GitHub.
    csp = "default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'self' https://cdn.tailwindcss.com cdn.jsdelivr.net;"
    resp.headers['Content-Security-Policy'] = csp
    return resp

@app.route('/report', methods=['POST'])
def submit_report():
    if request.remote_addr != '127.0.0.1' and not session.get('logged_in'):
        return redirect('/login')

    title = request.form.get('title', '')
    
    if title:
        global active_bots
        with bot_lock:
            if active_bots < 3:
                active_bots += 1
                import urllib.parse
                t_val = urllib.parse.quote(title)
                bot_url = f"http://127.0.0.1:9745/report/view?title={t_val}"
                threading.Thread(target=visit_url, args=(bot_url,)).start()
                
    return redirect('/panel?report_msg=El administrador va a revisar tu reporte en breve.')

@app.route('/report/view')
def view_report():
    # Solo el admin bot visita esta página
    if request.remote_addr != '127.0.0.1':
        return redirect('/')
        
    title = request.args.get('title', 'Sin título')
    
    resp = make_response(render_template_string(TEMPLATE_VIEW_REPORT, title=title))
    
    # CSP: script-src limitado a cdn.jsdelivr.net
    csp = "default-src 'self'; script-src cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com;"
    resp.headers['Content-Security-Policy'] = csp
    return resp

@app.route('/api/status')
def api_status():
    cb = request.args.get('callback', 'initApp')
    resp = make_response(f"{cb}({{\"status\": \"Sistemas Up\"}});")
    resp.headers['Content-Type'] = 'application/javascript'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9745)
