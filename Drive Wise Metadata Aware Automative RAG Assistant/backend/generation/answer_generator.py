import os
from pathlib import Path

from google import genai


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# ANSWER GENERATOR
# ============================================================

class AnswerGenerator:

    def __init__(self):

        print("\nLoading answer generation system...")

        print(
            f"✓ Gemini model configured: {MODEL_NAME}"
        )


    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    def build_context(
        self,
        results
    ):

        if not results:
            return ""

        context_parts = []

        for number, result in enumerate(
            results,
            start=1
        ):

            brand = result.get(
                "brand",
                ""
            )

            model = result.get(
                "model",
                ""
            )

            section = result.get(
                "section",
                ""
            )

            page = result.get(
                "page",
                ""
            )

            brochure = result.get(
                "brochure",
                ""
            )

            text = result.get(
                "text",
                ""
            )

            context_parts.append(
                f"""
SOURCE {number}

Brand: {brand}
Model: {model}
Section: {section}
Page: {page}
Brochure: {brochure}

Content:
{text}
"""
            )

        return "\n".join(
            context_parts
        )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    def generate(
        self,
        query,
        brand,
        model,
        results
    ):

        if not results:

            return {
                "answer": (
                    "I could not find this information "
                    "in the selected vehicle brochure."
                ),
                "sources": []
            }


        # ----------------------------------------------------
        # Build brochure context
        # ----------------------------------------------------

        context = self.build_context(
            results
        )


        # ----------------------------------------------------
        # System instructions
        # ----------------------------------------------------

        prompt = f"""
You are Drive Wise, a brochure-grounded automotive
question answering assistant.

Your task is to answer the user's question using ONLY
the brochure information provided in the context.

Vehicle:
Brand: {brand}
Model: {model}

User Question:
{query}

BROCHURE CONTEXT:
{context}


IMPORTANT RULES:

1. Answer ONLY from the provided brochure context.

2. Do NOT use outside knowledge.

3. Do NOT guess or assume information.

4. If the brochure context does not contain enough
   information to answer the question, clearly say:

   "The brochure information provided does not contain
   enough information to answer this question."

5. Do not invent specifications.

6. Do not combine information from unrelated sections
   unless it directly helps answer the question.

7. Give a direct answer first.

8. Keep the answer concise and easy to understand.

9. If the question asks for a number, specification,
   feature, capacity, dimension, seating, mileage,
   engine information, safety feature, etc., provide
   the exact value only when it is explicitly supported
   by the context.

10. When the context contains a feature table, interpret
    the table carefully instead of guessing from nearby
    descriptive text.

11. Do not mention retrieval scores, embeddings,
    reranking scores, or internal system details.

12. Do not claim that a feature exists simply because
    the word appears in an unrelated sentence.

13. If the information is ambiguous, say that the
    brochure context is insufficient rather than guessing.


Return ONLY the final answer.
"""


        # ----------------------------------------------------
        # Gemini request
        # ----------------------------------------------------

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )


            answer = response.text.strip()


            return {
                "answer": answer,
                "sources": self.extract_sources(
                    results
                )
            }


        except Exception as error:

            print(
                f"\nAnswer generation failed: {error}"
            )

            return {
                "answer": (
                    "Unable to generate an answer "
                    "at the moment."
                ),
                "sources": []
            }


    # ========================================================
    # SOURCE EXTRACTION
    # ========================================================

    def extract_sources(
        self,
        results
    ):

        sources = []

        for number, result in enumerate(
            results,
            start=1
        ):

            sources.append(
                {
                    "source": number,

                    "brand": result.get(
                        "brand"
                    ),

                    "model": result.get(
                        "model"
                    ),

                    "section": result.get(
                        "section"
                    ),

                    "page": result.get(
                        "page"
                    ),

                    "brochure": result.get(
                        "brochure"
                    )
                }
            )

        return sources


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 60
    )

    print(
        "DRIVE WISE ANSWER GENERATION TEST"
    )

    print(
        "=" * 60
    )


    generator = AnswerGenerator()


    # --------------------------------------------------------
    # Test data
    #
    # In the actual application these results will come
    # directly from HybridRetriever.search()
    # --------------------------------------------------------

    results = [

        {
            "brand": "mahindra",
            "model": "thar",
            "section": "interior and comfort",
            "page": 10,
            "brochure": "thar_brochure.pdf",

            "text": (
                "Front-facing rear seats with "
                "50:50 split that let rear seat "
                "passengers travel comfortably."
            )
        }

    ]


    query = (
        "How many seats does the Thar have?"
    )


    result = generator.generate(
        query=query,
        brand="mahindra",
        model="thar",
        results=results
    )


    print(
        "\nANSWER"
    )

    print(
        "-" * 60
    )

    print(
        result["answer"]
    )


    print(
        "\nSOURCES"
    )

    print(
        "-" * 60
    )

    for source in result["sources"]:

        print(
            f"Source {source['source']}: "
            f"{source['brochure']} | "
            f"{source['section']} | "
            f"Page {source['page']}"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()