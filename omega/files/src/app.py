from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import json
import base64
import os

app = Flask(__name__)
# Configuración DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///omega.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DB ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# --- UTILIDADES DE COOKIE ---
def create_session_cookie(username, role):
    # Creamos un JSON simple y lo pasamos a Base64
    data = {"username": username, "role": role}
    json_str = json.dumps(data)
    b64_str = base64.b64encode(json_str.encode()).decode()
    return b64_str

def read_session_cookie(cookie_value):
    try:
        # Decodificamos Base64 y leemos el JSON (CONFIANZA CIEGA)
        json_str = base64.b64decode(cookie_value).decode()
        return json.loads(json_str)
    except:
        return {}

# --- RUTAS ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        
        if User.query.filter_by(username=user).first():
            msg = "El usuario ya existe."
        else:
            new_user = User(username=user, password=pwd)
            db.session.add(new_user)
            db.session.commit()
            msg = "Cuenta creada. Ahora puedes iniciar sesion."
            
    return render_template('register.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        
        account = User.query.filter_by(username=user, password=pwd).first()
        
        if account:
            # LOGIN EXITOSO -> CREAMOS COOKIE DEFAULT 'user'
            resp = make_response(redirect(url_for('dashboard')))
            cookie_val = create_session_cookie(account.username, "user")
            resp.set_cookie('omega_session', cookie_val)
            return resp
        else:
            msg = "Credenciales incorrectas."
            
    return render_template('login.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    cookie = request.cookies.get('omega_session')
    
    if not cookie:
        return redirect(url_for('login'))
    
    # LEEMOS LA COOKIE
    session_data = read_session_cookie(cookie)
    username = session_data.get('username', 'Anon')
    role = session_data.get('role', 'user')
        
    flag = "HCRD{r4w_h7ml_c00k13_m4n1pul4t10n}"
    
    return render_template('dashboard.html', username=username, role=role, flag=flag)

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('omega_session', '', expires=0)
    return resp

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    if not os.path.exists('omega.db'):
        init_db()
    app.run(host='0.0.0.0', port=5003)
