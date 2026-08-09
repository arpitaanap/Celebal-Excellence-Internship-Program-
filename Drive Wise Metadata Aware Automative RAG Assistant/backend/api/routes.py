from flask import Blueprint, request, jsonify

from rag.pipeline import RAGPipeline


# ============================================================
# API BLUEPRINT
# ============================================================

api = Blueprint(
    "api",
    __name__
)


# ============================================================
# RAG PIPELINE
# ============================================================

pipeline = None


def get_pipeline():
    """
    Load the RAG pipeline only when required.
    This avoids unnecessary initialization during import.
    """

    global pipeline

    if pipeline is None:
        print("\nLoading Drive Wise RAG pipeline...")
        pipeline = RAGPipeline()
        print("✓ RAG pipeline loaded")

    return pipeline


# ============================================================
# HEALTH CHECK
# ============================================================

@api.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "ok",
        "service": "Drive Wise RAG API"
    })


# ============================================================
# ASK QUESTION
# ============================================================

@api.route(
    "/ask",
    methods=["POST"]
)
def ask():

    try:

        # ----------------------------------------------------
        # Read JSON request
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body must be JSON."
            }), 400


        # ----------------------------------------------------
        # Extract fields
        # ----------------------------------------------------

        query = str(
            data.get("query", "")
        ).strip()

        brand = str(
            data.get("brand", "")
        ).strip().lower()

        model = str(
            data.get("model", "")
        ).strip().lower()


        # ----------------------------------------------------
        # Validate query
        # ----------------------------------------------------

        if not query:

            return jsonify({
                "success": False,
                "error": "Query is required."
            }), 400


        # ----------------------------------------------------
        # Validate brand
        # ----------------------------------------------------

        if not brand:

            return jsonify({
                "success": False,
                "error": "Brand is required."
            }), 400


        # ----------------------------------------------------
        # Validate model
        # ----------------------------------------------------

        if not model:

            return jsonify({
                "success": False,
                "error": "Model is required."
            }), 400


        print("\n" + "=" * 70)
        print("API REQUEST")
        print("=" * 70)

        print(f"Brand : {brand}")
        print(f"Model : {model}")
        print(f"Query : {query}")


        # ----------------------------------------------------
        # Get RAG pipeline
        # ----------------------------------------------------

        rag = get_pipeline()


        # ----------------------------------------------------
        # Run RAG
        # ----------------------------------------------------

        result = rag.answer(
            query=query,
            brand=brand,
            model=model,
            retrieval_top_k=30,
            rerank_top_k=5
        )


        # ----------------------------------------------------
        # Prepare response
        # ----------------------------------------------------

        response = {

            "success": True,

            "query": query,

            "vehicle": {
                "brand": brand,
                "model": model
            },

            "answer": result.get(
                "answer",
                ""
            ),

            "sources": result.get(
                "sources",
                []
            ),

            "metadata": {

                "retrieved_chunks": result.get(
                    "retrieved_chunks",
                    0
                ),

                "context_characters": result.get(
                    "context_characters",
                    0
                ),

                "retrieval_time": result.get(
                    "retrieval_time",
                    0
                ),

                "reranking_time": result.get(
                    "reranking_time",
                    0
                ),

                "evidence_time": result.get(
                    "evidence_time",
                    0
                ),

                "context_time": result.get(
                    "context_time",
                    0
                ),

                "generation_time": result.get(
                    "generation_time",
                    0
                ),

                "response_time": result.get(
                    "response_time",
                    0
                )
            }
        }


        print("\n✓ API response generated")


        return jsonify(
            response
        ), 200


    except Exception as error:

        print(
            f"\n✗ API error: {error}"
        )

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500