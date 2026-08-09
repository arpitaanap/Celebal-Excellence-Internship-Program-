import time

from retrieval.hybrid_retriever import HybridRetriever
from generation.gemini_generator import GeminiGenerator


# ============================================================
# DRIVE WISE - MAIN APPLICATION
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("                    DRIVE WISE")
    print("        Metadata-Aware Automotive RAG Assistant")
    print("=" * 70)

    # --------------------------------------------------------
    # Load Retrieval System
    # --------------------------------------------------------

    print("\nLoading retrieval system...")

    retriever = HybridRetriever()

    print("✓ Retrieval system ready")

    # --------------------------------------------------------
    # Load Gemini Generator
    # --------------------------------------------------------

    print("\nLoading answer generation system...")

    generator = GeminiGenerator()

    print("✓ Gemini answer generator ready")

    # --------------------------------------------------------
    # Vehicle Selection
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("Select Vehicle")
    print("-" * 70)

    brand = input("\nEnter brand: ").strip()
    model = input("Enter model: ").strip()

    if not brand or not model:

        print(
            "\nBrand and model cannot be empty."
        )

        return

    # --------------------------------------------------------
    # Verify vehicle exists
    # --------------------------------------------------------

    allowed_indices = retriever.filter_metadata(
        brand,
        model
    )

    if not allowed_indices:

        print(
            "\nNo brochure found for:"
        )

        print(
            f"Brand : {brand}"
        )

        print(
            f"Model : {model}"
        )

        return

    print("\n✓ Vehicle brochure found")

    print(
        f"✓ Available brochure chunks: "
        f"{len(allowed_indices)}"
    )

    # --------------------------------------------------------
    # Start Question Answering Loop
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        "Ask questions about this vehicle."
    )

    print(
        "Type 'exit' to close Drive Wise."
    )

    print("=" * 70)

    while True:

        # ----------------------------------------------------
        # Get user question
        # ----------------------------------------------------

        question = input(
            "\nAsk your question: "
        ).strip()

        # ----------------------------------------------------
        # Exit condition
        # ----------------------------------------------------

        if question.lower() in {
            "exit",
            "quit",
            "q"
        }:

            print(
                "\nThank you for using Drive Wise."
            )

            break

        # ----------------------------------------------------
        # Empty question
        # ----------------------------------------------------

        if not question:

            print(
                "\nPlease enter a question."
            )

            continue

        # ----------------------------------------------------
        # Start response timer
        # ----------------------------------------------------

        start_time = time.perf_counter()

        # ====================================================
        # STEP 1
        # RETRIEVAL
        # ====================================================

        print(
            "\nSearching brochure..."
        )

        try:

            chunks = retriever.search(
                query=question,
                brand=brand,
                model=model,
                top_k=5
            )

        except Exception as error:

            print(
                "\nRetrieval error:"
            )

            print(error)

            continue

        # ----------------------------------------------------
        # Retrieval result count
        # ----------------------------------------------------

        print(
            f"✓ Retrieved {len(chunks)} "
            f"relevant chunks"
        )

        # ====================================================
        # STEP 2
        # NO RETRIEVAL RESULT
        # ====================================================

        if not chunks:

            answer = (
                "I could not find this information "
                "in the selected vehicle brochure."
            )

            print(
                "\n" + "-" * 70
            )

            print("Drive Wise:")

            print(answer)

            print("-" * 70)

            continue

        # ====================================================
        # STEP 3
        # GENERATE ANSWER USING GEMINI
        # ====================================================

        print(
            "✓ Generating brochure-grounded answer..."
        )

        try:

            result = generator.generate_answer(
                question=question,
                brand=brand,
                model=model,
                chunks=chunks
            )

        except Exception as error:

            print(
                "\nGemini generation error:"
            )

            print(error)

            continue

        # ----------------------------------------------------
        # Extract answer
        # ----------------------------------------------------

        answer = result.get(
            "answer",
            ""
        )

        sources = result.get(
            "sources",
            []
        )

        # ----------------------------------------------------
        # Response time
        # ----------------------------------------------------

        response_time = (
            time.perf_counter()
            - start_time
        )

        # ====================================================
        # STEP 4
        # DISPLAY ANSWER
        # ====================================================

        print(
            "\n" + "=" * 70
        )

        print("DRIVE WISE ANSWER")

        print("=" * 70)

        print(
            f"\n{answer}"
        )

        # ====================================================
        # STEP 5
        # DISPLAY SOURCES
        # ====================================================

        if sources:

            print(
                "\n" + "-" * 70
            )

            print(
                "Sources"
            )

            print(
                "-" * 70
            )

            for source in sources:

                print(
                    f"\nSource {source.get('source')}"
                )

                print(
                    f"Section : "
                    f"{source.get('section')}"
                )

                print(
                    f"Page    : "
                    f"{source.get('page')}"
                )

                print(
                    f"Brochure: "
                    f"{source.get('brochure')}"
                )

        # ====================================================
        # STEP 6
        # RESPONSE TIME
        # ====================================================

        print(
            "\n" + "-" * 70
        )

        print(
            f"Response time: "
            f"{response_time:.2f} seconds"
        )

        print(
            "-" * 70
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()