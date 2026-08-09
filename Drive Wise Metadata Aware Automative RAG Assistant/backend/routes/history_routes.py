from flask import Blueprint, jsonify, request, session

from database.history import (
    save_history,
    get_chat_history
)


# ============================================================
# HISTORY BLUEPRINT
# ============================================================

history_bp = Blueprint(
    "history",
    __name__,
    url_prefix="/api/history"
)


# ============================================================
# GET HISTORY
# GET /api/history
# ============================================================

@history_bp.route(
    "",
    methods=["GET"]
)
def get_history():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    try:

        history_data = get_chat_history(
            user_id
        )

        return jsonify({

            "success": True,

            "history": history_data

        }), 200

    except Exception as error:

        print(
            "GET HISTORY ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message": "Unable to load history.",

            "error": str(error)

        }), 500


# ============================================================
# SAVE HISTORY
# POST /api/history
# ============================================================

@history_bp.route(
    "",
    methods=["POST"]
)
def save_history_route():

    # --------------------------------------------------------
    # CHECK LOGIN
    # --------------------------------------------------------

    if "user_id" not in session:

        print("SAVE HISTORY: User not logged in")

        return jsonify({

            "success": False,

            "message": "Please login first."

        }), 401


    # --------------------------------------------------------
    # READ JSON
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    )


    print(
        "SAVE HISTORY REQUEST:",
        data
    )


    if not data:

        return jsonify({

            "success": False,

            "message": "Invalid request."

        }), 400


    # --------------------------------------------------------
    # GET VALUES
    # --------------------------------------------------------

    brand = str(
        data.get("brand", "")
    ).strip()


    model = str(
        data.get("model", "")
    ).strip()


    question = str(
        data.get("question", "")
    ).strip()


    answer = str(
        data.get("answer", "")
    ).strip()


    print("Brand:", brand)
    print("Model:", model)
    print("Question:", question)
    print("Answer:", answer)


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not brand:

        return jsonify({
            "success": False,
            "message": "Brand is required."
        }), 400


    if not model:

        return jsonify({
            "success": False,
            "message": "Model is required."
        }), 400


    if not question:

        return jsonify({
            "success": False,
            "message": "Question is required."
        }), 400


    if not answer:

        return jsonify({
            "success": False,
            "message": "Answer is required."
        }), 400


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        saved = save_history(

            user_id=session["user_id"],

            brand=brand,

            model=model,

            question=question,

            answer=answer

        )


        print(
            "SAVE HISTORY RESULT:",
            saved
        )


        if not saved:

            return jsonify({

                "success": False,

                "message": "Database did not save history."

            }), 500


        return jsonify({

            "success": True,

            "message": "History saved successfully."

        }), 201


    except Exception as error:

        print(
            "SAVE HISTORY ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message": "Unable to save history.",

            "error": str(error)

        }), 500