from flask import Flask, render_template, request, make_response, redirect, url_for
import base64
import os
import threading
import time

app = Flask(__name__)

FLAG = base64.b64encode(
    os.environ.get("FLAG", "HCRD{CSP_k1ll3r_d4mn}").encode()
).decode()
ADMIN_PATH = "M100JcI_CV0b24c_1bcy"

PRESCRIPTIONS = [
    {
        "name": "Lisinopril",
        "generic": "lisinopril (ACE inhibitor)",
        "strength": "10 mg",
        "form": "tablet",
        "sig": "Take 1 tablet by mouth once daily",
        "qty": 90,
        "refills": 2,
        "next_fill": "Apr 12, 2026",
        "prescriber": "Dr. Elena Ruiz, MD",
        "status": "active",
    },
    {
        "name": "Metformin ER",
        "generic": "metformin extended-release",
        "strength": "500 mg",
        "form": "tablet",
        "sig": "Take 1 tablet with evening meal",
        "qty": 60,
        "refills": 1,
        "next_fill": "Mar 31, 2026",
        "prescriber": "Dr. James Okonkwo, DO",
        "status": "active",
    },
    {
        "name": "Levothyroxine",
        "generic": "levothyroxine sodium",
        "strength": "75 mcg",
        "form": "tablet",
        "sig": "Take 1 tablet on empty stomach in the morning",
        "qty": 30,
        "refills": 5,
        "next_fill": "Apr 02, 2026",
        "prescriber": "Dr. Priya Nair, MD",
        "status": "active",
    },
    {
        "name": "Amoxicillin",
        "generic": "amoxicillin",
        "strength": "500 mg",
        "form": "capsule",
        "sig": "Take 1 capsule three times daily until finished",
        "qty": 21,
        "refills": 0,
        "next_fill": "Completed",
        "prescriber": "Dr. Elena Ruiz, MD",
        "status": "completed",
    },
    {
        "name": "Fluticasone Nasal",
        "generic": "fluticasone propionate",
        "strength": "50 mcg/spray",
        "form": "nasal spray",
        "sig": "2 sprays per nostril once daily",
        "qty": 1,
        "refills": 3,
        "next_fill": "May 08, 2026",
        "prescriber": "Dr. James Okonkwo, DO",
        "status": "active",
    },
    {
        "name": "Sertraline",
        "generic": "sertraline HCl",
        "strength": "50 mg",
        "form": "tablet",
        "sig": "Take 1 tablet by mouth once daily",
        "qty": 30,
        "refills": 2,
        "next_fill": "Apr 18, 2026",
        "prescriber": "Dr. Priya Nair, MD",
        "status": "active",
    },
]


@app.after_request
def add_csp_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "img-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src https://cdnjsdeliver.net https://cdn.jsdelivr.net; "
        "object-src 'none'"
    )
    return response


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "")
    reflected_result = f"Showing results for: {query}" if query else ""
    return render_template("index.html", q=query, reflected_result=reflected_result)


@app.route("/feedback", methods=["GET"])
def feedback():
    contact_status = request.args.get("sent", "")
    return render_template("feedback.html", contact_status=contact_status)


@app.route("/prescriptions", methods=["GET"])
def prescriptions():
    return render_template("prescriptions.html", prescriptions=PRESCRIPTIONS)


@app.route(f"/{ADMIN_PATH}")
def admin_panel():
    resp = make_response("Welcome back, admin.")
    resp.set_cookie("flag", FLAG, httponly=False, samesite="Lax")
    return resp


@app.route("/contact", methods=["POST"])
def contact():
    comment = request.form.get("comment", "").strip()
    if not comment:
        return redirect(url_for("feedback", sent="invalid"))
    threading.Thread(target=visit_comment, args=(comment,), daemon=True).start()
    return redirect(url_for("feedback", sent="ok"))


def visit_comment(comment):
    from urllib.parse import quote
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(10)
        driver.get(f"http://localhost:4020/{ADMIN_PATH}")
        time.sleep(2)
        driver.get(f"http://localhost:4020/?q={quote(comment)}")
        time.sleep(5)
    except Exception as e:
        print(f"[bot] {e}", flush=True)
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4020, debug=False)
