from flask import Flask, request, render_template_string, session, redirect
import sqlite3
import re 

app = Flask(__name__)
app.secret_key = 'intracorp_sqli_xK9'
DB = '/tmp/ch1.db'

def init_db():
    c = sqlite3.connect(DB)
    c.executescript("""
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS sneakers;
        DROP TABLE IF EXISTS secrets;
        CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT);
        CREATE TABLE sneakers (id INTEGER PRIMARY KEY, brand TEXT, model TEXT, price TEXT, colorway TEXT, img_url TEXT);
        CREATE TABLE secrets (id INTEGER PRIMARY KEY, flag TEXT, note TEXT);
        INSERT INTO users VALUES (1,'admin','$3CuR3_P@55!','admin');
        INSERT INTO users VALUES (2,'jperez','juan2024','user');
        INSERT INTO users VALUES (3,'mrodriguez','maria123','user');
        INSERT INTO users VALUES (4,'super_user','ByP@55_M3!','superadmin');
        INSERT INTO sneakers VALUES (1,'Nike','Air Max 90','$120','White/Red','https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto,u_9ddf04c7-2a9a-4d76-add1-d15af8f0263d,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/5f270e53-71aa-42c4-9acb-20604a8184af/AIR+MAX+90+%28GS%29.png');
        INSERT INTO sneakers VALUES (2,'Adidas','Ultraboost 22','$180','Core Black','https://sneakernews.com/wp-content/uploads/2021/12/adidas-UltraBOOST-22-GZ0127-0.jpg?w=1140');
        INSERT INTO sneakers VALUES (3,'Jordan','Air Jordan 1 Retro','$220','Chicago Red','https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto,u_126ab356-44d8-4a06-89b4-fcdcc8df0245,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/b68c2282-4519-498d-8b47-445375212252/WMNS+AIR+JORDAN+1+MID+SE+EDG.png');
        INSERT INTO sneakers VALUES (4,'New Balance','990v5','$175','Grey/Navy','https://www.holabirdsports.com/cdn/shop/files/049395_3.jpg?v=1762450690&width=1000');
        INSERT INTO sneakers VALUES (5,'Converse','Chuck Taylor','$65','Classic White','https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto,u_9ddf04c7-2a9a-4d76-add1-d15af8f0263d,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/wcyxzampg1jvtjmdj3ag/YTHS+CT+CORE+HI+OPT+WHT.png');
        INSERT INTO sneakers VALUES (6,'Vans','Old Skool','$75','Black/White','https://assets.vans.eu/images/t_img/c_fill,g_center,f_auto,h_815,e_unsharp_mask:100,w_652/dpr_2.0/v1769593424/VN000E9TJDU-HERO/Old-Skool-Shoes-VANS-Blue-HERO.jpg');
        INSERT INTO secrets VALUES (1,'HCRD{SQL1_F1LT3R_BYP4SS}','IntraCorp Admin Vault');
    """)
    c.commit(); c.close()

init_db()

# ─── login input filter ─────────────────────────────────────────────────────
LOGIN_BL = ['union','select','drop','insert','delete','/*','*/','1=1']

def bl_hit(s):
    lo = s.lower()
    return any(w in lo for w in LOGIN_BL)

# ─── sneaker search input filter ─────────────────────────────────────────────
SEARCH_BL = ['--','drop','delete','insert']

def search_blocked(s):
    lo = s.lower()

    # bloquear comentarios de línea
    if '--' in lo:
        return True

    return False


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn
# ─── CSS ────────────────────────────────────────────────────────────────────
BASE = """<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0c10;--surf:#111318;--surf2:#161c28;--b:#1e2330;--acc:#00d4ff;--red:#ff3c6e;--grn:#00ff88;--gold:#ffd060;--tx:#c9d1e0;--dim:#5a6480;--mo:'IBM Plex Mono',monospace;--sa:'IBM Plex Sans',sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--tx);font-family:var(--sa);min-height:100vh;display:flex;flex-direction:column}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(0,212,255,.04) 0%,transparent 55%);pointer-events:none;z-index:0}
/* NAV */
nav{background:var(--surf);border-bottom:1px solid var(--b);padding:0 40px;height:62px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
.nlogo{font-family:var(--mo);font-size:15px;color:var(--acc);letter-spacing:3px}
.nlogo span{color:var(--dim)}
.nlinks{display:flex;gap:28px}
.nlink{font-family:var(--mo);font-size:11px;color:var(--dim);text-decoration:none;letter-spacing:1px;transition:color .2s}
.nlink:hover,.nlink.on{color:var(--acc)}
.nusr{display:flex;align-items:center;gap:10px;font-family:var(--mo);font-size:11px}
.navatar{width:30px;height:30px;background:var(--acc);color:#000;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px}
.nrole{color:var(--grn);font-size:9px;letter-spacing:1px}
.logout{font-family:var(--mo);font-size:10px;color:var(--red);text-decoration:none;padding:3px 9px;border:1px solid var(--red);transition:all .2s}
.logout:hover{background:var(--red);color:#000}
/* HERO BANNER */
.hero{background:linear-gradient(135deg,#0b1120,#0f1822);border-bottom:1px solid var(--b);padding:36px 40px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:20px}
.hero h2{font-size:24px;font-weight:700;color:#fff;margin-bottom:4px}
.hero p{font-size:13px;color:var(--dim)}
.hstats{display:flex;gap:28px}
.hsv{font-family:var(--mo);font-size:22px;font-weight:600;color:var(--acc);display:block}
.hsl{font-family:var(--mo);font-size:8px;color:var(--dim);letter-spacing:2px;text-transform:uppercase}
/* CONTENT */
.content{flex:1;padding:36px 40px;max-width:1200px;width:100%;margin:0 auto;position:relative;z-index:1}
.stitle{font-family:var(--mo);font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--dim);margin-bottom:18px;display:flex;align-items:center;gap:12px}
.stitle::after{content:'';flex:1;height:1px;background:var(--b)}
/* SEARCH CARD */
.scard{background:var(--surf);border:1px solid var(--b);padding:26px;margin-bottom:28px;position:relative}
.scard::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--acc),transparent)}
.ainfo{padding:10px 14px;border:1px solid rgba(0,212,255,.25);color:var(--acc);background:rgba(0,212,255,.04);font-family:var(--mo);font-size:11px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.srow{display:flex;gap:10px;margin-top:4px}
.sinput{flex:1;background:var(--bg);border:1px solid var(--b);color:var(--tx);font-family:var(--mo);font-size:13px;padding:11px 14px;outline:none;transition:border-color .2s}
.sinput:focus{border-color:var(--acc)}
.sbtn{background:var(--acc);color:#000;border:none;font-family:var(--mo);font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:11px 22px;cursor:pointer;transition:all .2s;white-space:nowrap}
.sbtn:hover{background:#fff;box-shadow:0 0 16px rgba(0,212,255,.35)}
/* SNEAKER GRID */
.sgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:16px;margin-top:22px}
.skcard{background:var(--surf2);border:1px solid var(--b);overflow:hidden;transition:border-color .2s,transform .2s}
.skcard:hover{border-color:var(--acc);transform:translateY(-3px)}
.skimg{width:100%;height:160px;object-fit:cover;display:block;background:#0d1018}
.skinfo{padding:14px}
.skbrand{font-family:var(--mo);font-size:9px;color:var(--dim);letter-spacing:2px;text-transform:uppercase;margin-bottom:3px}
.skmodel{font-size:13px;font-weight:600;color:#fff;margin-bottom:6px}
.skcolor{font-size:11px;color:var(--dim);margin-bottom:8px}
.skprice{font-family:var(--mo);font-size:16px;color:var(--acc);font-weight:600}
/* RAW OUTPUT */
.rawout{background:#050608;border:1px solid var(--b);padding:18px;font-family:var(--mo);font-size:12px;white-space:pre-wrap;word-break:break-all;margin-top:18px;max-height:340px;overflow-y:auto;line-height:1.65;color:var(--tx)}
.rawout.flag{border-color:var(--grn);color:var(--grn);box-shadow:0 0 20px rgba(0,255,136,.06)}
.rawout.err{border-color:var(--red);color:var(--red)}
/* LOGIN */
main{flex:1;display:flex;align-items:center;justify-content:center;padding:60px 20px;position:relative;z-index:1}
.card{background:var(--surf);border:1px solid var(--b);padding:40px;width:100%;max-width:460px;position:relative}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--acc),transparent)}
.ltag{font-family:var(--mo);font-size:10px;color:var(--acc);letter-spacing:3px;text-transform:uppercase;margin-bottom:10px}
h1{font-size:28px;font-weight:700;color:#fff;margin-bottom:4px}
.sub{font-family:var(--mo);font-size:11px;color:var(--dim);margin-bottom:30px}
.fg{margin-bottom:18px}
label{display:block;font-family:var(--mo);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--dim);margin-bottom:7px}
input{width:100%;background:var(--bg);border:1px solid var(--b);color:var(--tx);font-family:var(--mo);font-size:13px;padding:11px 14px;outline:none;transition:border-color .2s}
input:focus{border-color:var(--acc)}
.btn{width:100%;background:var(--acc);color:#000;border:none;font-family:var(--mo);font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:13px;cursor:pointer;transition:all .2s;margin-top:6px}
.btn:hover{background:#fff;box-shadow:0 0 20px rgba(0,212,255,.35)}
.msg{margin-top:18px;padding:14px;font-family:var(--mo);font-size:12px;border:1px solid var(--b);background:rgba(0,0,0,.25);white-space:pre-wrap;word-break:break-all}
.msg.ok{border-color:var(--grn);color:var(--grn)}
.msg.err{border-color:var(--red);color:var(--red)}
footer{border-top:1px solid var(--b);padding:14px 40px;display:flex;justify-content:space-between;font-family:var(--mo);font-size:10px;color:var(--dim);position:relative;z-index:1}
</style>"""

LOGIN_TPL = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>IntraCorp Portal</title>""" + BASE + """</head>
<body>
<nav>
  <div class="nlogo">INTRA<span>CORP</span></div>
  <span style="font-family:var(--mo);font-size:10px;color:var(--dim);letter-spacing:2px">CTF-01 &middot; IntraCorp</span>
</nav>
<main>
<div class="card">
  <div class="ltag">portal.intracorp.local</div>
  <h1>Employee Portal</h1>
  <p class="sub">// Acceso restringido &mdash; Personal autorizado</p>
  <form method="POST" action="/login">
    <div class="fg"><label>Username</label><input name="username" placeholder="username" autocomplete="off" value="{{ uval or '' }}"></div>
    <div class="fg"><label>Password</label><input type="password" name="password" placeholder="password" value="{{ pval or '' }}">
    <button class="btn" type="submit">&rarr; Iniciar Sesi&oacute;n</button>
  </form>
  {% if msg %}<div class="msg {{ cls }}">{{ msg }}</div>{% endif %}
</div>
</main>
  <footer><span>IntraCorp Portal v3.1</span><span></span></footer>
  </body></html>"""

DASH_TPL = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>IntraCorp Dashboard</title>""" + BASE + """</head>
<body>
<nav>
  <div class="nlogo">INTRA<span>CORP</span></div>
  <div class="nlinks">
    <a href="/dashboard" class="nlink on">Dashboard</a>
    <a href="/sneakers" class="nlink">Sneakers</a>
  </div>
  <div class="nusr">
    <div class="navatar">{{ session.get('username','?')[0]|upper }}</div>
    <div><div>{{ session.get('username','') }}</div><div class="nrole">{{ session.get('role','') }}</div></div>
    <a href="/logout" class="logout">SALIR</a>
  </div>
</nav>
<div class="hero">
  <div>
    <h2>Bienvenido, {{ session.get('username','') }} &#128075;</h2>
    <p>Panel de control interno &mdash; IntraCorp Employee Portal</p>
  </div>
  <div class="hstats">
    <div><span class="hsv">6</span><span class="hsl">Sneakers</span></div>
    <div><span class="hsv" style="color:var(--grn)">&#11044;</span><span class="hsl">Online</span></div>
  </div>
</div>
<div class="content">
  <div class="stitle">Cat&aacute;logo</div>
  <div class="scard">
    <div class="ainfo"> "Cada intento fallido te acerca… o te confunde más." </div>
    <form method="POST" action="/sneakers/search">
      <div class="srow">
        <input class="sinput" name="q" placeholder="Buscar por marca o modelo" value="{{ q or '' }}" autocomplete="off">
        <button class="sbtn" type="submit">&#128269; BUSCAR</button>
      </div>
    </form>

    {% if result_mode == 'grid' and sneakers %}
      <div class="sgrid">
        {% for s in sneakers %}
        <div class="skcard">
          <img class="skimg" src="{{ s['img_url'] }}" alt="{{ s['brand'] }} {{ s['model'] }}" loading="lazy" onerror="this.style.background='#1a2030';this.style.height='160px'">
          <div class="skinfo">
            <div class="skbrand">{{ s['brand'] }}</div>
            <div class="skmodel">{{ s['model'] }}</div>
            <div class="skcolor">{{ s['colorway'] }}</div>
            <div class="skprice">{{ s['price'] }}</div>
          </div>
        </div>
        {% endfor %}
      </div>
    {% elif result_mode == 'raw' %}
      <div class="rawout {% if is_flag %}flag{% elif is_err %}err{% endif %}">{{ raw }}</div>
    {% elif result_mode == 'empty' %}
      <div class="rawout err">Sin resultados para: "{{ q }}"</div>
    {% endif %}
  </div>
</div>
<footer><span>IntraCorp Employee Portal v3.1</span><span>IntraCorp CTF-01</span></footer>
</body></html>"""

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template_string(LOGIN_TPL, msg=None, cls='', uval='', pval='')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username','')
    password = request.form.get('password','')

    if bl_hit(username):
        return render_template_string(LOGIN_TPL,
            msg='[WAF] Username bloqueado.', cls='err', uval=username, pval=password)

    try:
        conn = db()
        q = f"SELECT id, username, role FROM users WHERE username='{username}' AND password='{password}'"
        row = conn.execute(q).fetchone()
        conn.close()
        if row:
            session['uid']      = row['id']
            session['username'] = row['username']
            session['role']     = row['role']
            return redirect('/dashboard')
        return render_template_string(LOGIN_TPL,
            msg='Credenciales incorrectas.', cls='err', uval=username, pval=password)
    except Exception as e:
        return render_template_string(LOGIN_TPL,
            msg=f'DB Error: {e}', cls='err', uval=username, pval=password)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect('/')
    return render_template_string(DASH_TPL,
        result_mode=None, sneakers=None, q=None, raw=None, is_flag=False, is_err=False)

@app.route('/sneakers')
def sneakers_page():
    if 'username' not in session: return redirect('/')
    conn = db()
    rows = conn.execute("SELECT * FROM sneakers").fetchall()
    conn.close()
    return render_template_string(DASH_TPL,
        result_mode='grid', sneakers=rows, q='', raw=None, is_flag=False, is_err=False)

@app.route('/sneakers/search', methods=['POST'])
def sneakers_search():
    if 'username' not in session: return redirect('/')
    q = request.form.get('q','').strip()
    if not q:
        return redirect('/sneakers')

    hits = [w for w in SEARCH_BL if w in q.lower()]
    if hits:
        return render_template_string(DASH_TPL,
            result_mode='raw', sneakers=None, q=q,
            raw=f"[WAF] Palabras bloqueadas detectadas: {hits}",
            is_flag=False, is_err=True)

    try:
        conn = sqlite3.connect(DB)  # plain connect so rows are tuples
        cur = conn.cursor()
        sql = f"SELECT * FROM sneakers WHERE brand LIKE '%{q}%' OR model LIKE '%{q}%'"
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return render_template_string(DASH_TPL,
                result_mode='empty', sneakers=None, q=q, raw=None, is_flag=False, is_err=False)

        # Detect non-standard output vs normal sneaker rows
        # Normal sneaker has 6 cols: id,brand,model,price,colorway,img_url
        is_injection = False
        for r in rows:
            joined = ' '.join(str(x) for x in r)
            if 'flag{' in joined:
                is_injection = True
                break
            if len(r) != 6:
                is_injection = True
                break
            # if img_url column doesn't look like a URL, treat as non-standard data
            if r[5] and not str(r[5]).startswith('http'):
                is_injection = True
                break

        if is_injection:
            raw_text = '\n'.join([str(list(r)) for r in rows])
            is_flag = 'flag{' in raw_text
            return render_template_string(DASH_TPL,
                result_mode='raw', sneakers=None, q=q,
                raw=raw_text, is_flag=is_flag, is_err=False)

        # Normal display using Row objects for template
        conn2 = db()
        rows2 = conn2.execute(
            f"SELECT * FROM sneakers WHERE brand LIKE '%{q}%' OR model LIKE '%{q}%'"
        ).fetchall()
        conn2.close()
        return render_template_string(DASH_TPL,
            result_mode='grid', sneakers=rows2, q=q, raw=None, is_flag=False, is_err=False)

    except Exception as e:
        return render_template_string(DASH_TPL,
            result_mode='raw', sneakers=None, q=q,
            raw=f'DB Error: {e}', is_flag=False, is_err=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6401, debug=False)

