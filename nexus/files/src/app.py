from flask import Flask, request, render_template
from lxml import etree

app = Flask(__name__)

KNOWN_EMPLOYEES = {
    "102030": (
        "Verified — ID 102030\n"
        "Name: Sr. Castillo\n"
        "Role: Confidential agent (external field ops)\n"
        "Notes: Handled under sealed dossier; no public registry entry."
    ),
    "102031": (
        "Verified — ID 102031\n"
        "Name: Sr. Waos\n"
        "Role: Internal informant (covert liaison)\n"
        "Notes: Embedded with partner cells; report chain is air-gapped."
    ),
    "0": (
        "Verified — ID 0\n"
        "Name: [REDACTED — root roster slot]\n"
        "Role: System placeholder / legacy bootstrap account\n"
        "Notes: Pre-dates numbered agents; used only for gateway smoke tests and archival sync."
    ),
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/system/verify_id', methods=['POST'])
def verify():
    # Simulación de sistema estricto
    if 'application/xml' not in request.content_type:
        return "HTTP 400: Content-Type must be application/xml", 400

    try:
        parser = etree.XMLParser(resolve_entities=True, no_network=False)
        tree = etree.fromstring(request.data, parser=parser)
        
        # Buscamos el nodo <employeeId>
        root_node = tree.find('employeeId')
        
        if root_node is not None and root_node.text:
            emp_id = root_node.text.strip()

            if emp_id in KNOWN_EMPLOYEES:
                return KNOWN_EMPLOYEES[emp_id]

            return f"Error: User ID '{emp_id}' not found in internal database."
            
        return "Error: XML missing <employeeId> tag"

    except Exception as e:
        return f"HTTP 500: XML Parsing Failed. Check syntax."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)
