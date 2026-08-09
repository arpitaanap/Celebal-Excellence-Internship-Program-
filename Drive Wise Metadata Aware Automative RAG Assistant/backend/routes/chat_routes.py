from flask import Blueprint, request, jsonify

from services.chat_service import ChatService


# ============================================================
# CHAT BLUEPRINT
# ============================================================

chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/chat"
)


# ============================================================
# CHAT SERVICE
# ============================================================

chat_service = ChatService()


# ============================================================
# ASK QUESTION
# ============================================================

@chat_bp.route("/", methods=["POST"])
def ask_question():

    try:

        # ----------------------------------------------------
        # Get JSON request
        # ----------------------------------------------------

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body is required."
            }), 400

        # ----------------------------------------------------
        # Extract values
        # ----------------------------------------------------

        brand = str(
            data.get("brand", "")
        ).strip()

        model = str(
            data.get("model", "")
        ).strip()

        question = str(
            data.get("question", "")
        ).strip()

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if not brand:

            return jsonify({
                "success": False,
                "error": "Brand is required."
            }), 400

        if not model:

            return jsonify({
                "success": False,
                "error": "Model is required."
            }), 400

        if not question:

            return jsonify({
                "success": False,
                "error": "Question is required."
            }), 400

        # ====================================================
        # CALL CHAT SERVICE
        # ====================================================

        result = chat_service.ask(
            question=question,
            brand=brand,
            model=model
        )

        # ====================================================
        # RETURN RESPONSE
        # ====================================================

        return jsonify({
            "success": True,
            "brand": brand,
            "model": model,
            "question": question,
            "answer": result.get(
                "answer",
                ""
            ),
            "sources": result.get(
                "sources",
                []
            )
        }), 200

    except Exception as error:

        print(
            f"\nChat route error: {error}"
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500