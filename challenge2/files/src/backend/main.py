from flask import Flask, request, render_template_string, redirect
import sqlite3, base64

app = Flask(__name__)
DB_PATH = '/tmp/ch2.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS contracts;
        CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, full_name TEXT, dept TEXT);
        CREATE TABLE contracts (id INTEGER PRIMARY KEY, owner_id INTEGER, title TEXT, content TEXT, confidential INTEGER);
        INSERT INTO users VALUES (1,'jose.a','jose2024','Jose Almodovar','Operaciones');
        INSERT INTO users VALUES (2,'carlos.m','carlos2024','Carlos Martinez','RRHH');
        INSERT INTO users VALUES (3,'admin','adm1n_s3cr3t!','Administrador del Sistema','TI');
        INSERT INTO contracts VALUES (1,1,'Contrato de Servicios Q1','Contrato estandar de servicios para el primer trimestre. Proveedor: TechSupply Inc. Valor: $15,000.',0);
        INSERT INTO contracts VALUES (2,2,'Evaluacion de Desempeno RRHH','Evaluacion interna de RRHH. CONFIDENCIAL.',1);
        INSERT INTO contracts VALUES (3,3,'Credenciales Admin Vault','HACKCON{1D0R_3NC0D3D_4CC3SS} Acceso administrativo al sistema central. NO COMPARTIR.',1);
        INSERT INTO contracts VALUES (4,2,'Plan de Compensaciones 2024','Escala salarial revisada. CONFIDENCIAL.',1);
    """)
    conn.commit(); conn.close()

init_db()

def encode_uid(n):
    inner = base64.b64encode(str(n).encode()).decode()
    outer = base64.b64encode(inner.encode()).decode()
    return outer.replace('=','%3d')

def decode_uid(s):
    try:
        s = s.replace('%3d','=').replace('%3D','=')
        inner = base64.b64decode(s).decode()
        val = base64.b64decode(inner).decode()
        return int(val)
    except: return None

def db(): return sqlite3.connect(DB_PATH)

CSS = """<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#f4f6fa;--surf:#fff;--surf2:#f9fafc;--border:#e2e6f0;--accent:#1a56db;--green:#0e9f6e;--red:#e02424;--text:#1a202c;--dim:#6b7280;--mono:'Space Mono',monospace;--sans:'Space Grotesk',sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;display:flex;flex-direction:column}
nav{background:var(--surf);border-bottom:1px solid var(--border);padding:0 40px;height:60px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.n-logo{font-family:var(--mono);font-size:14px;color:var(--accent);letter-spacing:2px}
.n-tag{font-family:var(--mono);font-size:10px;color:var(--dim)}
main{flex:1;max-width:960px;width:100%;margin:0 auto;padding:40px 24px}
h1{font-size:26px;font-weight:700;margin-bottom:4px}
.page-sub{font-size:13px;color:var(--dim);margin-bottom:28px}
.ct{width:100%;border-collapse:collapse;background:var(--surf);border:1px solid var(--border);border-radius:6px;overflow:hidden}
.ct th{background:#f1f5f9;font-family:var(--mono);font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--dim);padding:12px 16px;text-align:left;border-bottom:1px solid var(--border)}
.ct td{padding:14px 16px;border-bottom:1px solid var(--border);font-size:13px}
.ct tr:last-child td{border-bottom:none}
.ct tr:hover td{background:var(--surf2)}
.badge{font-family:var(--mono);font-size:9px;padding:2px 8px;border-radius:12px}
.badge.open{background:#ecfdf5;color:var(--green);border:1px solid #6ee7b7}
.badge.locked{background:#fef2f2;color:var(--red);border:1px solid #fca5a5}
.view-btn{font-family:var(--mono);font-size:11px;color:var(--accent);text-decoration:none;padding:4px 10px;border:1px solid var(--accent);border-radius:3px;transition:all .2s}
.view-btn:hover{background:var(--accent);color:#fff}
.view-btn.disabled{color:var(--dim);border-color:var(--border);pointer-events:none;cursor:not-allowed;font-family:var(--mono);font-size:11px;padding:4px 10px;border:1px solid var(--border);border-radius:3px;display:inline-block}
.doc-card{background:var(--surf);border:1px solid var(--border);border-radius:6px;overflow:hidden;margin-top:28px}
.doc-hd{background:#1e3a5f;color:#fff;padding:20px 28px;display:flex;align-items:center;justify-content:space-between}
.doc-hd h2{font-size:17px;font-weight:600}
.doc-meta{font-size:11px;opacity:.55;font-family:var(--mono)}
.doc-body{padding:24px;font-size:14px;line-height:1.7}
.doc-body.flag-content{color:var(--green);font-family:var(--mono);font-size:13px;background:#ecfdf5}
.doc-foot{padding:12px 28px;background:var(--surf2);border-top:1px solid var(--border);font-size:11px;color:var(--dim);font-family:var(--mono)}
footer{border-top:1px solid var(--border);padding:14px 40px;display:flex;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--dim);background:var(--surf)}
</style>"""

LIST_TPL = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Contratos IntraCorp</title>""" + CSS + """</head>
<body>
<nav>
  <div class="n-logo">INTRACORP LEGAL</div>
  <span class="n-tag">api.intracorp.local</span>
</nav>
<main>
  <h1>Contratos Internos</h1>
  <p class="page-sub">Documentos del sistema. Solo el propietario del contrato puede leer su contenido.</p>
  <table class="ct">
    <thead><tr><th>ID</th><th>Titulo</th><th>Propietario</th><th>Estado</th><th>Accion</th></tr></thead>
    <tbody>
      {% for c in contracts %}
      <tr>
        <td style="font-family:var(--mono);font-size:11px;color:var(--dim)">#{{ c[0] }}</td>
        <td>{{ c[2] }}</td>
        <td style="font-size:12px;color:var(--dim)">{{ c[5] }}</td>
        <td>{% if c[4]==0 %}<span class="badge open">Publico</span>{% else %}<span class="badge locked">Restringido</span>{% endif %}</td>
        <td>
          {% if c[0] == 1 %}
            <a href="/contracts/view?uid={{ c[6] }}" class="view-btn">Ver documento</a>
          {% else %}
            <span class="view-btn disabled">Sin acceso</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  {% if doc %}
  <div class="doc-card">
    <div class="doc-hd">
      <div>
        <h2>{{ doc[2] }}</h2>
        <div class="doc-meta">#{{ doc[0] }} &mdash; {{ 'CONFIDENCIAL' if doc[4] else 'Publico' }}</div>
      </div>
    </div>
    <div class="doc-body {% if is_flag %}flag-content{% endif %}">{{ doc[3] }}</div>
  </div>
  {% endif %}

  {% if err %}
  <div style="margin-top:20px;padding:14px;border:1px solid #fca5a5;color:#e02424;font-family:var(--mono);font-size:12px;background:#fef2f2;border-radius:4px">{{ err }}</div>
  {% endif %}
</main>
<footer>
  <span>IntraCorp Legal System v2.0</span>
  <span>IntraCorp Internal Systems</span>
</footer>
</body></html>"""

@app.route('/')
def index():
    return redirect('/contracts')

@app.route('/contracts')
def contracts():
    conn = db(); c = conn.cursor()
    c.execute("""SELECT ct.id, ct.owner_id, ct.title, ct.content, ct.confidential, u.full_name
                 FROM contracts ct JOIN users u ON ct.owner_id=u.id""")
    rows = c.fetchall(); conn.close()
    enriched = [r + (encode_uid(r[0]),) for r in rows]
    return render_template_string(LIST_TPL, contracts=enriched, doc=None, err=None, is_flag=False, current_uid=None)

@app.route('/contracts/view')
def view_contract():
    raw_uid = request.args.get('uid', '')
    cid = decode_uid(raw_uid)

    conn = db(); c = conn.cursor()
    c.execute("""SELECT ct.id, ct.owner_id, ct.title, ct.content, ct.confidential, u.full_name
                 FROM contracts ct JOIN users u ON ct.owner_id=u.id""")
    rows = c.fetchall(); conn.close()
    enriched = [r + (encode_uid(r[0]),) for r in rows]

    if cid is None:
        return render_template_string(LIST_TPL, contracts=enriched, doc=None,
            err=f'UID invalido: {raw_uid}', is_flag=False, current_uid=raw_uid)

    conn2 = db(); cx = conn2.cursor()
    cx.execute("SELECT id, owner_id, title, content, confidential FROM contracts WHERE id=?", (cid,))
    doc = cx.fetchone(); conn2.close()

    if not doc:
        return render_template_string(LIST_TPL, contracts=enriched, doc=None,
            err=f'Documento no encontrado para uid={raw_uid}', is_flag=False, current_uid=raw_uid)

    return render_template_string(LIST_TPL, contracts=enriched, doc=doc, err=None,
        is_flag='flag{' in (doc[3] or ''), current_uid=raw_uid)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5022, debug=False)
