import os
import re

from flask import Flask, render_template, request, redirect, session
from typing import TypedDict, Optional

app = Flask(__name__)
app.secret_key = "kill3r_super_secret_key_9999_mil4ne"

FLAG = os.environ.get("KILL3RTRICK_FLAG", "HCRD{LDAP_Inj3ct0r_Pwn3d}")

# Banco de datos LDAP simulado
class LdapUser(TypedDict):
    uid: str
    password: str
    role: str
    name: str


MOCK_LDAP_DB: list[LdapUser] = [
    {
        "uid": "user",
        "password": "password123",
        "role": "user",
        "name": "Invitado Temporal",
    },
    {
        "uid": "telecom_master",
        "password": FLAG,
        "role": "admin",
        "name": "Administrador de Red",
    },
]


def ldap_unescape_assertion_value(value: str) -> str:
    """
    Valor de aserción dentro de un filtro LDAP (RFC 4515): secuencias \\XX en hex.
    Un * sin codificar es comodín de subcadena; \\2a es un asterisco literal.
    """
    out: list[str] = []
    i = 0
    n = len(value)
    while i < n:
        if value[i] == "\\" and i + 2 < n:
            pair = value[i + 1 : i + 3]
            if len(pair) == 2 and all(c in "0123456789abcdefABCDEF" for c in pair):
                out.append(chr(int(pair, 16)))
                i += 3
                continue
        out.append(value[i])
        i += 1
    return "".join(out)


def ldap_substring_assertion_matches(stored: str, pattern: str) -> bool:
    """
    Aserción de subcadena LDAP: sin * es igualdad exacta (octeto a octeto).
    Con *, cada * coincide con cualquier subcadena (incl. vacía), como en RFC 4517.
    Ej.: H*, *d, *CR*, a*b*c
    """
    if "*" not in pattern:
        return stored == pattern
    parts = pattern.split("*")
    chunks: list[str] = []
    for i, part in enumerate(parts):
        if part:
            chunks.append(re.escape(part))
        if i < len(parts) - 1:
            chunks.append(".*")
    rx = re.compile("^" + "".join(chunks) + "$", re.DOTALL)
    return rx.fullmatch(stored) is not None


def check_ldap(username: str, password: str) -> Optional[LdapUser]:
    """
    Simula un bind contra una entrada cuyo filtro sería equivalente a:
      (&(uid=<username>)(userPassword=<password>))
    Ambas aserciones usan la misma semántica de subcadena LDAP (tras aplicar \\XX).
    Si más de una entrada coincide, gana la primera en MOCK_LDAP_DB.
    """
    uid_pat = ldap_unescape_assertion_value(username)
    pwd_pat = ldap_unescape_assertion_value(password)

    for user in MOCK_LDAP_DB:
        if ldap_substring_assertion_matches(
            user["uid"], uid_pat
        ) and ldap_substring_assertion_matches(user["password"], pwd_pat):
            return user
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user_match = check_ldap(username, password)
    
    if user_match:
        session['logged_in'] = True
        session['user_role'] = user_match['role']
        session['user_name'] = user_match['name']
        return redirect('/dashboard')
    
    return redirect('/fail')

@app.route('/fail')
def fail():
    return render_template('fail.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')
    
    is_admin = session.get('user_role') == 'admin'
    return render_template('dashboard.html', 
                           name=session.get('user_name'),
                           is_admin=is_admin)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4003)
