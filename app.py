import os
import secrets
from functools import wraps
from flask import Flask, render_template, request, jsonify, session
from database import DatabaseManager
from auth import evaluate_password_strength
from password_generator import generate_password

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

db = DatabaseManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"success": False, "error": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

# --- Auth & Status Endpoints ---

@app.route("/api/status", methods=["GET"])
def get_status():
    has_master = db.has_master_password()
    is_authenticated = session.get("authenticated", False)
    return jsonify({
        "success": True,
        "has_master_password": has_master,
        "authenticated": is_authenticated
    })

@app.route("/api/setup", methods=["POST"])
def setup_master():
    if db.has_master_password():
        return jsonify({"success": False, "error": "Master Password already configured."}), 400

    data = request.get_json() or {}
    password = data.get("password", "").strip()

    if not password or len(password) < 6:
        return jsonify({"success": False, "error": "Master Password must be at least 6 characters."}), 400

    db.set_master_password(password)
    session["authenticated"] = True
    return jsonify({"success": True, "message": "Master Password configured successfully!"})

@app.route("/api/login", methods=["POST"])
def login():
    if not db.has_master_password():
        return jsonify({"success": False, "error": "Master Password not set up yet."}), 400

    data = request.get_json() or {}
    password = data.get("password", "").strip()

    if not password:
        return jsonify({"success": False, "error": "Password is required."}), 400

    if db.verify_master_password(password):
        session["authenticated"] = True
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "error": "Incorrect Master Password."}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/api/eval-strength", methods=["POST"])
def eval_strength():
    data = request.get_json() or {}
    pwd = data.get("password", "")
    score, label, color = evaluate_password_strength(pwd)
    return jsonify({
        "success": True,
        "score": score,
        "label": label,
        "color": color
    })

# --- Credentials CRUD Endpoints ---

@app.route("/api/credentials", methods=["GET"])
@login_required
def get_credentials():
    query = request.args.get("query", "").strip()
    category = request.args.get("category", "All").strip()
    results = db.search_credentials(query=query, category_filter=category)
    return jsonify({"success": True, "data": results})

@app.route("/api/credentials/<int:cred_id>", methods=["GET"])
@login_required
def get_credential(cred_id):
    cred = db.get_credential_by_id(cred_id)
    if not cred:
        return jsonify({"success": False, "error": "Credential not found."}), 404
    return jsonify({"success": True, "data": cred})

@app.route("/api/credentials", methods=["POST"])
@login_required
def add_credential():
    data = request.get_json() or {}
    website = data.get("website", "")
    username = data.get("username", "")
    password = data.get("password", "")
    category = data.get("category", "Other")
    notes = data.get("notes", "")

    success, msg = db.add_credential(website, username, password, category, notes)
    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "error": msg}), 400

@app.route("/api/credentials/<int:cred_id>", methods=["PUT"])
@login_required
def update_credential(cred_id):
    data = request.get_json() or {}
    website = data.get("website", "")
    username = data.get("username", "")
    password = data.get("password", "")
    category = data.get("category", "Other")
    notes = data.get("notes", "")

    success, msg = db.update_credential(cred_id, website, username, password, category, notes)
    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "error": msg}), 400

@app.route("/api/credentials/<int:cred_id>", methods=["DELETE"])
@login_required
def delete_credential(cred_id):
    success = db.delete_credential(cred_id)
    if success:
        return jsonify({"success": True, "message": "Credential deleted successfully."})
    else:
        return jsonify({"success": False, "error": "Could not delete credential."}), 400

# --- Generator Endpoint ---

@app.route("/api/generate-password", methods=["POST"])
def api_generate_password():
    data = request.get_json() or {}
    length = int(data.get("length", 16))
    use_upper = bool(data.get("use_upper", True))
    use_lower = bool(data.get("use_lower", True))
    use_digits = bool(data.get("use_digits", True))
    use_symbols = bool(data.get("use_symbols", True))

    pwd = generate_password(
        length=length,
        use_upper=use_upper,
        use_lower=use_lower,
        use_digits=use_digits,
        use_symbols=use_symbols
    )
    return jsonify({"success": True, "password": pwd})


if __name__ == "__main__":
    print("Starting SecureVault Web Application on http://localhost:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
