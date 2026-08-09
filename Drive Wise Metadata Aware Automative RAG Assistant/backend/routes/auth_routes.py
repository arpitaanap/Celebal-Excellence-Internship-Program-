from flask import Blueprint, request, jsonify, session

from database.auth import register_user, login_user


# ============================================================
# CREATE BLUEPRINT
# ============================================================

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# ============================================================
# REGISTER
# ============================================================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    name = data.get("name", "").strip()

    email = data.get("email", "").strip().lower()

    password = data.get("password", "")


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name:

        return jsonify({
            "success": False,
            "message": "Name is required."
        }), 400


    if not email:

        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400


    if not password:

        return jsonify({
            "success": False,
            "message": "Password is required."
        }), 400


    if len(password) < 6:

        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters."
        }), 400


    # --------------------------------------------------------
    # REGISTER USER
    # --------------------------------------------------------

    success, message = register_user(
        name,
        email,
        password
    )


    if success:

        return jsonify({
            "success": True,
            "message": message
        }), 201


    return jsonify({
        "success": False,
        "message": message
    }), 400


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400


    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    user = login_user(
        email,
        password
    )


    if not user:

        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401


    # --------------------------------------------------------
    # CREATE SESSION
    # --------------------------------------------------------

    session["user_id"] = user["id"]

    session["user_name"] = user["name"]

    session["user_email"] = user["email"]


    return jsonify({

        "success": True,

        "message": "Login successful.",

        "user": user

    })


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()


    return jsonify({

        "success": True,

        "message": "Logged out successfully."

    })


# ============================================================
# CURRENT USER
# ============================================================

@auth_bp.route("/me", methods=["GET"])
def current_user():

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "authenticated": False

        }), 401


    return jsonify({

        "success": True,

        "authenticated": True,

        "user": {

            "id": session["user_id"],

            "name": session["user_name"],

            "email": session["user_email"]

        }

    })