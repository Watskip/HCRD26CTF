from flask import Flask, request, render_template, Response
import os
import requests
import socket

app = Flask(__name__)

# BLACKLIST: Bloquea cadenas exactas.
BLACKLIST = ['127.0.0.1', 'localhost', '::1', '0.0.0.0']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '')

        # WAF simple
        if any(blocked in url for blocked in BLACKLIST):
             return render_template('index.html', error=f"Security Alert: Restricted IP detected! ({url})")

        try:
            # SSRF
            # allow_redirects=False para evitar bucles raros
            r = requests.get(url, timeout=3, allow_redirects=False)
            return render_template('index.html', result=r.text)
        except Exception as e:
            return render_template('index.html', error=f"Error reaching URL: {str(e)}")

    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return Response("User-agent: *\\nDisallow: /flag", mimetype="text/plain")

@app.route('/flag')
def flag():
    # Validación de IP de origen
    if request.remote_addr == '127.0.0.1':
        return render_template('flag.html', FLAG=os.environ.get("FLAG", "HCRD{TEST_FLAG}"))
    else:
        return render_template('forbidden.html'), 403

if __name__ == '__main__':
    # Escuchamos en el puerto 80 estándar
    app.run(host="0.0.0.0", port=80)
