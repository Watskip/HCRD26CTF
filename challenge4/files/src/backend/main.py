from flask import Flask, request, render_template_string
import os

app = Flask(__name__)



HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IntraCorp &mdash; Billing</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{--bg:#faf8f4;--surf:#fff;--border:#e8e4dc;--dark:#1a0a2e;--gold:#c4a35a;--red:#d4342a;--green:#1a6b3c;--text:#2a2420;--dim:#8a8278;--mono:'DM Mono',monospace;--serif:'Playfair Display',serif;--sans:'DM Sans',sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;display:flex;flex-direction:column}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg,var(--dark),var(--gold))}
header{border-bottom:1px solid var(--border);padding:0 60px;height:64px;display:flex;align-items:center;justify-content:space-between;background:var(--surf)}
.logo{font-family:var(--serif);font-size:20px;font-weight:700;color:var(--dark)}
.logo span{color:var(--gold)}
.badge{font-family:var(--mono);font-size:10px;padding:4px 12px;border:1px solid var(--red);color:var(--red);background:rgba(212,52,42,.05);letter-spacing:2px}
main{flex:1;display:flex;align-items:flex-start;justify-content:center;padding:60px 20px}
.container{width:100%;max-width:680px}
.ptag{font-family:var(--mono);font-size:10px;color:var(--gold);letter-spacing:4px;text-transform:uppercase;margin-bottom:12px}
h1{font-family:var(--serif);font-size:40px;font-weight:700;color:var(--dark);margin-bottom:6px;line-height:1.1}
.sub{font-family:var(--mono);font-size:11px;color:var(--dim);margin-bottom:48px}
.inv{background:var(--surf);border:1px solid var(--border);box-shadow:0 4px 24px rgba(0,0,0,.06);overflow:hidden;margin-bottom:24px}
.inv-hd{padding:24px 32px;background:var(--dark);color:#fff;display:flex;align-items:center;justify-content:space-between}
.inv-hd h2{font-family:var(--serif);font-size:18px}
.inv-num{font-family:var(--mono);font-size:11px;color:rgba(255,255,255,.4);letter-spacing:2px}
.inv-body{padding:32px}
.fg{margin-bottom:22px}
label{display:block;font-family:var(--mono);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--dim);margin-bottom:7px}
input,select{width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);font-family:var(--sans);font-size:14px;padding:11px 14px;outline:none;transition:border-color .2s;-webkit-appearance:none}
input:focus,select:focus{border-color:var(--gold)}
.row{display:flex;gap:16px}.row .fg{flex:1}
.btn{width:100%;background:var(--dark);color:#fff;border:none;font-family:var(--mono);font-size:12px;letter-spacing:3px;text-transform:uppercase;padding:15px;cursor:pointer;transition:all .2s}
.btn:hover{background:#2d1454;box-shadow:0 4px 20px rgba(26,10,46,.3)}
.result{padding:22px 32px;font-family:var(--mono);font-size:13px;line-height:1.7;border-top:1px solid var(--border);word-break:break-all}
.result.normal{color:var(--text)}
.result.blocked{color:var(--red);background:#fef9f9}
.result.flag{color:var(--green);background:#f0fdf4;font-weight:600;font-size:14px}
.finfo{background:var(--surf);border:1px solid var(--border);border-left:3px solid var(--gold);padding:22px 26px}
.finfo h3{font-family:var(--mono);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:12px}
.finfo p{font-size:13px;color:var(--dim);line-height:1.75;margin-bottom:8px}
.finfo code{font-family:var(--mono);font-size:12px;color:var(--dark);background:rgba(26,10,46,.06);padding:2px 6px}
.finfo .ok{color:var(--green);background:rgba(26,107,60,.06)}
footer{border-top:1px solid var(--border);padding:18px 60px;display:flex;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--dim);background:var(--surf)}
</style>
</head>
<body>
<header>
  <div class="logo">Intra<span>Corp</span> Billing</div>
  <div class="badge">Billing Portal</div>
</header>
<main>
<div class="container">
  <div class="ptag">billing.intracorp.local</div>
  <h1>Invoice<br>Generator</h1>
  <p class="sub">// Facturacion Interna </p>

  <div class="inv">
    <div class="inv-hd">
      <h2>Nueva Factura</h2>
      <span class="inv-num">INV-2026-####</span>
    </div>
    <div class="inv-body">
      <form method="POST" action="/invoice">
        <div class="fg">
          <label>Nombre del Cliente</label>
          <input type="text" name="customer_name" placeholder="Ej: Acme Corp" value="{{ customer or '' }}" autocomplete="off">
        </div>
        <div class="row">
          <div class="fg"><label>Monto (USD)</label><input type="number" name="amount" placeholder="0.00" min="0" step="0.01" value="{{ amount or '' }}"></div>
          <div class="fg"><label>Servicio</label>
            <select name="service">
              <option>Consultor&iacute;a</option><option>Licencias</option>
              <option>Soporte</option><option>Infraestructura</option>
            </select>
          </div>
        </div>
        <button class="btn" type="submit">&rarr; GENERAR FACTURA</button>
      </form>
    </div>
    {% if result %}
    <div class="result {{ rclass }}">{{ result }}</div>
    {% endif %}
  </div>

  <div class="finfo">
    <h3>//LEE LA SIGUIENTE LINEA</h3>
    <p>Dios te ilumine</p>
    </div>
</div>
</main>
<footer>
  <span>IntraCorp Billing Engine v3.4</span>
  <span>IntraCorp Internal Systems</span>
</footer>
</body>
</html>"""

import re

def is_blocked(s):
    s_lower = s.lower()

    # 1. eliminar secuencia permitida ('o''s')
    cleaned = re.sub(r"'o''s'", "", s_lower)

    # 2. bloquear "os" o 'os'
    if re.search(r"""(['"])os\1""", cleaned):
        return True

    # 3. bloquear os "bare"
    if re.search(r"\bos\b", cleaned):
        return True

    return False

@app.route('/')
def index():
    return render_template_string(HTML, result=None, rclass='', customer=None, amount=None)

@app.route('/invoice', methods=['POST'])
def invoice():
    customer = request.form.get('customer_name', '')
    amount   = request.form.get('amount', '0.00')

    # Validar que amount sea numérico (solo dígitos y punto decimal)
    import re as _re
    if not _re.match(r'^\d+(\.\d{1,2})?$', amount.strip()):
        return render_template_string(HTML,
            result='[ERROR] El campo Monto solo acepta valores numéricos (ej: 100 o 99.99).',
            rclass='blocked', customer=customer, amount=amount)

    if is_blocked(customer):
        return render_template_string(HTML,
            result='“Ese payload vino sin imaginación incluida.”',
            rclass='blocked', customer=customer, amount=amount)

    try:
        tpl = f"Factura generada para: {customer} | Monto: ${amount}"
        rendered = render_template_string(tpl)
        is_flag = 'flag{' in rendered
        return render_template_string(HTML,
            result=rendered,
            rclass='flag' if is_flag else 'normal',
            customer=customer, amount=amount)
    except Exception as e:
        return render_template_string(HTML,
            result=f'Error de template: {e}',
            rclass='blocked', customer=customer, amount=amount)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
