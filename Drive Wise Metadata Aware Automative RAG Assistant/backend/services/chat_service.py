from rag.pipeline import RAGPipeline


class ChatService:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        print("\n" + "=" * 70)
        print("INITIALIZING CHAT SERVICE")
        print("=" * 70)

        # ----------------------------------------------------
        # RAG Pipeline
        # ----------------------------------------------------

        print("\n[1] Loading RAG pipeline...")

        self.rag_pipeline = RAGPipeline()

        print("\n✓ Chat service ready")

    # ========================================================
    # ASK QUESTION
    # ========================================================

    def ask(
        self,
        question,
        brand,
        model
    ):
        """
        Complete Drive Wise question-answering service.

        Flow:

        User Question
              ↓
        RAG Pipeline
              ↓
        Hybrid Retrieval
              ↓
        Cross-Encoder Reranking
              ↓
        Technical Evidence Ranking
              ↓
        Context Building
              ↓
        Gemini Generation
              ↓
        Answer + Sources
        """

        # ====================================================
        # VALIDATE QUESTION
        # ====================================================

        if not question or not str(question).strip():

            return {
                "answer": "Please enter a question.",
                "sources": [],
                "retrieved_chunks": 0
            }

        # ====================================================
        # VALIDATE VEHICLE
        # ====================================================

        if not brand or not str(brand).strip():

            return {
                "answer": (
                    "Please select a vehicle brand "
                    "before asking a question."
                ),
                "sources": [],
                "retrieved_chunks": 0
            }

        if not model or not str(model).strip():

            return {
                "answer": (
                    "Please select a vehicle model "
                    "before asking a question."
                ),
                "sources": [],
                "retrieved_chunks": 0
            }

        # ====================================================
        # CLEAN INPUT
        # ====================================================

        question = str(
            question
        ).strip()

        brand = str(
            brand
        ).strip().lower()

        model = str(
            model
        ).strip().lower()

        # ====================================================
        # LOG REQUEST
        # ====================================================

        print("\n" + "-" * 70)
        print("CHAT SERVICE — PROCESSING QUESTION")
        print("-" * 70)

        print(
            f"\nBrand    : {brand}"
        )

        print(
            f"Model    : {model}"
        )

        print(
            f"Question : {question}"
        )

        # ====================================================
        # RUN COMPLETE RAG PIPELINE
        # ====================================================

        try:

            result = self.rag_pipeline.answer(
                query=question,
                brand=brand,
                model=model,
                retrieval_top_k=30,
                rerank_top_k=5
            )

        except Exception as error:

            print(
                f"\n✗ Chat service error: {error}"
            )

            return {
                "answer": (
                    "Unable to process the question "
                    "using the selected vehicle brochure."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "error": str(error)
            }

        # ====================================================
        # SAFETY CHECK
        # ====================================================

        if not isinstance(result, dict):

            return {
                "answer": (
                    "The brochure information could "
                    "not be processed correctly."
                ),
                "sources": [],
                "retrieved_chunks": 0
            }

        # ====================================================
        # EXTRACT RESULT
        # ====================================================

        answer = result.get(
            "answer",
            ""
        )

        sources = result.get(
            "sources",
            []
        )

        retrieved_chunks = result.get(
            "retrieved_chunks",
            0
        )

        # ====================================================
        # EMPTY ANSWER
        # ====================================================

        if not answer:

            answer = (
                "The available brochure information "
                "does not clearly specify this."
            )

        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        response = {

            "answer": answer,

            "sources": sources,

            "retrieved_chunks":
                retrieved_chunks,

            "context_characters":
                result.get(
                    "context_characters",
                    0
                ),

            "retrieval_time":
                result.get(
                    "retrieval_time",
                    0.0
                ),

            "reranking_time":
                result.get(
                    "reranking_time",
                    0.0
                ),

            "evidence_time":
                result.get(
                    "evidence_time",
                    0.0
                ),

            "context_time":
                result.get(
                    "context_time",
                    0.0
                ),

            "generation_time":
                result.get(
                    "generation_time",
                    0.0
                ),

            "response_time":
                result.get(
                    "response_time",
                    0.0
                )
        }

        print(
            "\n✓ Chat service completed successfully"
        )

        return response


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE - CHAT SERVICE TEST"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Create service
    # --------------------------------------------------------

    service = ChatService()

    # --------------------------------------------------------
    # Vehicle
    # --------------------------------------------------------

    brand = "mahindra"

    model = "xuv3xo"

    # --------------------------------------------------------
    # Question
    # --------------------------------------------------------

    question = (
        "What is the maximum power "
        "of the XUV 3XO?"
    )

    # --------------------------------------------------------
    # Ask question
    # --------------------------------------------------------

    result = service.ask(
        question=question,
        brand=brand,
        model=model
    )

    # --------------------------------------------------------
    # Display answer
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL CHAT RESPONSE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nAnswer:\n"
        f"{result.get('answer', '')}"
    )

    # --------------------------------------------------------
    # Display sources
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "SOURCES"
    )

    print(
        "-" * 70
    )

    sources = result.get(
        "sources",
        []
    )

    if not sources:

        print(
            "\nNo sources available."
        )

    else:

        for source in sources:

            print(
                f"\nSource "
                f"{source.get('source', '')}"
            )

            print(
                f"Brand   : "
                f"{source.get('brand', '')}"
            )

            print(
                f"Model   : "
                f"{source.get('model', '')}"
            )

            print(
                f"Section : "
                f"{source.get('section', '')}"
            )

            print(
                f"Page    : "
                f"{source.get('page', '')}"
            )

            print(
                f"Brochure: "
                f"{source.get('brochure', '')}"
            )

    # --------------------------------------------------------
    # Pipeline statistics
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "PIPELINE STATISTICS"
    )

    print(
        "-" * 70
    )

    print(
        f"\nRetrieved chunks : "
        f"{result.get('retrieved_chunks', 0)}"
    )

    print(
        f"Context chars    : "
        f"{result.get('context_characters', 0)}"
    )

    print(
        f"Retrieval time   : "
        f"{result.get('retrieval_time', 0):.4f} sec"
    )

    print(
        f"Reranking time   : "
        f"{result.get('reranking_time', 0):.4f} sec"
    )

    print(
        f"Evidence time    : "
        f"{result.get('evidence_time', 0):.4f} sec"
    )

    print(
        f"Context time     : "
        f"{result.get('context_time', 0):.4f} sec"
    )

    print(
        f"Generation time  : "
        f"{result.get('generation_time', 0):.4f} sec"
    )

    print(
        f"Total time       : "
        f"{result.get('response_time', 0):.4f} sec"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()

