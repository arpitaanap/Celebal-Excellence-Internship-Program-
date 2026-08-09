import os

from flask import Flask, send_from_directory, jsonify
from dotenv import load_dotenv

from routes.chat_routes import chat_bp
from routes.auth_routes import auth_bp
from routes.car_routes import vehicle_bp
from routes.history_routes import history_bp


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

CSS_DIR = os.path.join(
    FRONTEND_DIR,
    "css"
)

JS_DIR = os.path.join(
    FRONTEND_DIR,
    "js"
)


# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# SECRET KEY
# ============================================================

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "development-secret-key"
)


# ============================================================
# REGISTER BLUEPRINTS
# ============================================================

# Chat / RAG
app.register_blueprint(chat_bp)

# Login / Register / Logout / Current User
app.register_blueprint(auth_bp)

# Brands / Cars
app.register_blueprint(vehicle_bp)

# User Question History
app.register_blueprint(history_bp)


# ============================================================
# DEBUG PATH CHECK
# ============================================================

print()
print("=" * 70)
print("DRIVE WISE FRONTEND PATH CHECK")
print("=" * 70)

print()

print("BASE_DIR:")
print(BASE_DIR)

print()

print("FRONTEND_DIR:")
print(FRONTEND_DIR)

print()

print("CSS_DIR:")
print(CSS_DIR)

print()

print("JS_DIR:")
print(JS_DIR)

print()

print(
    "login.html:",
    os.path.exists(
        os.path.join(
            FRONTEND_DIR,
            "login.html"
        )
    )
)

print(
    "register.html:",
    os.path.exists(
        os.path.join(
            FRONTEND_DIR,
            "register.html"
        )
    )
)

print(
    "dashboard.html:",
    os.path.exists(
        os.path.join(
            FRONTEND_DIR,
            "dashboard.html"
        )
    )
)

print(
    "style.css:",
    os.path.exists(
        os.path.join(
            CSS_DIR,
            "style.css"
        )
    )
)

print(
    "auth.js:",
    os.path.exists(
        os.path.join(
            JS_DIR,
            "auth.js"
        )
    )
)

print(
    "dashboard.js:",
    os.path.exists(
        os.path.join(
            JS_DIR,
            "dashboard.js"
        )
    )
)

print(
    "history_routes.py:",
    os.path.exists(
        os.path.join(
            BASE_DIR,
            "routes",
            "history_routes.py"
        )
    )
)

print()

print("=" * 70)
print()


# ============================================================
# LOGIN PAGE
# ============================================================

@app.route("/")
def login_page():

    return send_from_directory(
        FRONTEND_DIR,
        "login.html"
    )


# ============================================================
# REGISTER PAGE
# ============================================================

@app.route("/register")
def register_page():

    return send_from_directory(
        FRONTEND_DIR,
        "register.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard_page():

    return send_from_directory(
        FRONTEND_DIR,
        "dashboard.html"
    )


# ============================================================
# CSS FILES
# ============================================================

@app.route("/css/<path:filename>")
def css_files(filename):

    return send_from_directory(
        CSS_DIR,
        filename
    )


# ============================================================
# JAVASCRIPT FILES
# ============================================================

@app.route("/js/<path:filename>")
def js_files(filename):

    return send_from_directory(
        JS_DIR,
        filename
    )
# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({
        "success": True,
        "message": "Drive Wise API is running."
    }), 200


# ============================================================
# AUTHENTICATION TEST
# ============================================================

@app.route(
    "/api/test-login",
    methods=["POST"]
)
def test_login():

    return jsonify({
        "success": True,
        "message": "Login API connection is working."
    }), 200


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({
        "success": False,
        "message": "API endpoint or page not found."
    }), 404


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )