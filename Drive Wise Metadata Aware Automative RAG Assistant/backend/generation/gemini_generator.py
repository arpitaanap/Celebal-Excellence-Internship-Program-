import os
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found in .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# CONSTANT FALLBACK ANSWER
# ============================================================

FALLBACK_ANSWER = (
    "The available brochure information "
    "does not clearly specify this."
)


# ============================================================
# GEMINI ANSWER GENERATOR
# ============================================================

class GeminiGenerator:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        self.model = "gemini-3.6-flash"

        # Number of retries for temporary API failures
        self.max_retries = 2

        print(
            f"✓ Gemini generator initialized: {self.model}"
        )


    # ========================================================
    # BUILD BROCHURE CONTEXT
    # ========================================================

    def build_context(
        self,
        chunks,
        brand,
        model
    ):
        """
        Convert retrieved evidence chunks into a clean,
        numbered context for Gemini.

        Each source contains:
        - brand
        - model
        - section
        - page
        - brochure
        - evidence text
        """

        context_parts = []
        sources = []

        source_number = 1

        for chunk in chunks:

            if not isinstance(chunk, dict):
                continue

            text = str(
                chunk.get("text", "")
            ).strip()

            if not text:
                continue

            section = str(
                chunk.get(
                    "section",
                    "Unknown section"
                )
            ).strip()

            page = chunk.get(
                "page",
                "Unknown"
            )

            brochure = str(
                chunk.get(
                    "brochure",
                    "Unknown brochure"
                )
            ).strip()

            # ------------------------------------------------
            # Ranking metadata
            # ------------------------------------------------

            rerank_score = chunk.get(
                "rerank_score",
                None
            )

            evidence_score = chunk.get(
                "evidence_score",
                None
            )

            ranking_lines = []

            if rerank_score is not None:

                try:

                    ranking_lines.append(
                        f"Relevance score: "
                        f"{float(rerank_score):.4f}"
                    )

                except (TypeError, ValueError):
                    pass

            if evidence_score is not None:

                try:

                    ranking_lines.append(
                        f"Evidence score: "
                        f"{float(evidence_score):.4f}"
                    )

                except (TypeError, ValueError):
                    pass

            ranking_info = ""

            if ranking_lines:

                ranking_info = (
                    "\n".join(ranking_lines)
                )


            # ------------------------------------------------
            # Context block
            # ------------------------------------------------

            context_block = f"""
SOURCE {source_number}

Brand: {brand}
Model: {model}
Section: {section}
Page: {page}
Brochure: {brochure}
{ranking_info}

BROCHURE CONTENT:
{text}
""".strip()

            context_parts.append(
                context_block
            )


            # ------------------------------------------------
            # Source metadata
            # ------------------------------------------------

            sources.append(
                {
                    "source": source_number,
                    "brand": brand,
                    "model": model,
                    "section": section,
                    "page": page,
                    "brochure": brochure
                }
            )

            source_number += 1


        context = "\n\n".join(
            context_parts
        )

        return context, sources


    # ========================================================
    # SYSTEM INSTRUCTION
    # ========================================================

    def _get_system_instruction(self):

        return """
You are Drive Wise, an automotive brochure
question-answering assistant.

Your job is to answer questions using ONLY the
brochure evidence supplied in the user prompt.

============================================================
STRICT GROUNDING RULES
============================================================

1. Use ONLY the provided brochure evidence.

2. Do NOT use outside knowledge.

3. Do NOT use pretrained knowledge about vehicles.

4. Do NOT guess missing information.

5. Do NOT assume information that is not explicitly
   present in the brochure evidence.

6. If the requested information is not explicitly
   supported by the evidence, respond exactly:

"The available brochure information does not clearly specify this."

7. Preserve numerical values exactly as written.

8. Preserve units exactly as written.

9. Do NOT convert:
   - kW to PS
   - kW to BHP
   - Nm to another unit
   - mm to another unit
   - litres to another unit

10. Do not invent numerical values.

============================================================
TECHNICAL SPECIFICATION PRIORITY
============================================================

For technical questions, prioritize evidence in this order:

1. Technical specification tables
2. Exact numerical specifications
3. Variant-specific specifications
4. Direct statements answering the question
5. General descriptive statements

Marketing statements such as:

"powerful"
"exciting performance"
"segment leading"
"excellent performance"

must NOT be treated as numerical specifications.

============================================================
MULTIPLE ENGINE VARIANTS
============================================================

If the brochure contains multiple engine variants:

- Keep each engine separate.
- Do NOT merge specifications.
- Associate each value with its correct engine.
- Do NOT assume that a specification applies to
  every variant.

Example:

1.2 L Petrol:
82 kW @ 5000 r/min

1.2 L TGDi:
96 kW @ 5000 r/min

1.5 L Diesel:
85.8 kW @ 3750 r/min

Do not combine these into one engine specification.

============================================================
MAXIMUM / HIGHEST QUESTIONS
============================================================

When the user asks:

"maximum power"

"highest power"

"most powerful engine"

"maximum torque"

"highest torque"

compare the explicitly stated numerical values
in the provided brochure evidence.

For example:

82 kW
96 kW
85.8 kW

The highest explicitly stated value is:

96 kW

Only make this comparison when the evidence
provides enough information to support it.

============================================================
COMPARISON QUESTIONS
============================================================

For questions such as:

"Which has more power?"

"Compare the engines"

"Which variant has the highest torque?"

use ONLY values explicitly available in the brochure.

Keep different variants separate.

Do not fill missing values from outside knowledge.

============================================================
SOURCE CITATION
============================================================

The brochure evidence contains numbered sources:

SOURCE 1
SOURCE 2
SOURCE 3
etc.

When answering, cite the relevant source number
and brochure page when useful.

Preferred citation format:

(Source 1, Page 14)

or:

According to the brochure (Page 14)...

Do not cite a source that does not support the statement.

============================================================
ANSWER STYLE
============================================================

1. Answer the question first.

2. Keep the answer concise.

3. Use bullets when multiple variants are involved.

4. Include the engine/variant name when relevant.

5. Include brochure page references when useful.

6. Do not unnecessarily repeat the entire brochure.

============================================================
DO NOT REVEAL INTERNAL IMPLEMENTATION
============================================================

Never mention:

- FAISS
- embeddings
- vector database
- vector search
- keyword search
- hybrid retrieval
- reranking
- cross encoder
- RAG
- chunking
- retrieval scores
- internal pipeline
- database implementation

The user only needs the automotive answer.

============================================================
FINAL RULE
============================================================

Every factual statement must be directly supported
by the brochure evidence supplied in the prompt.

Never invent information.
"""


    # ========================================================
    # BUILD USER PROMPT
    # ========================================================

    def _build_user_prompt(
        self,
        question,
        brand,
        model,
        context
    ):

        return f"""
SELECTED VEHICLE

Brand: {brand}
Model: {model}


USER QUESTION

{question}


BROCHURE EVIDENCE

{context}


TASK

Answer the user's question using ONLY the brochure
evidence provided above.

IMPORTANT:

- Find the exact evidence relevant to the question.
- Prefer technical specification tables.
- Preserve numerical values exactly.
- Preserve units exactly.
- Do not convert units.
- Do not use outside knowledge.
- Do not guess.
- If multiple variants are present, keep them separate.
- If the question asks for a maximum or highest value,
  compare only explicitly stated values.
- Mention the relevant brochure page.
- Cite the source number when appropriate.

If the brochure evidence does not clearly support
the requested information, respond exactly:

"The available brochure information does not clearly specify this."
"""


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    def generate_answer(
        self,
        question,
        brand,
        model,
        chunks
    ):

        # ----------------------------------------------------
        # Validate question
        # ----------------------------------------------------

        if not question or not str(question).strip():

            return {
                "answer": (
                    "Please provide a question about "
                    "the selected vehicle."
                ),
                "sources": []
            }


        # ----------------------------------------------------
        # Validate chunks
        # ----------------------------------------------------

        if not chunks:

            return {
                "answer": FALLBACK_ANSWER,
                "sources": []
            }


        # ----------------------------------------------------
        # Build context
        # ----------------------------------------------------

        context, sources = self.build_context(
            chunks=chunks,
            brand=brand,
            model=model
        )


        # ----------------------------------------------------
        # Validate context
        # ----------------------------------------------------

        if not context.strip():

            return {
                "answer": FALLBACK_ANSWER,
                "sources": []
            }


        # ----------------------------------------------------
        # Build prompts
        # ----------------------------------------------------

        system_instruction = (
            self._get_system_instruction()
        )

        user_prompt = self._build_user_prompt(
            question=question,
            brand=brand,
            model=model,
            context=context
        )


        # ====================================================
        # GEMINI REQUEST
        # ====================================================

        print(
            "\nSending request to Gemini..."
        )

        response = None
        last_error = None


        for attempt in range(
            self.max_retries + 1
        ):

            try:

                response = client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config={
                        "system_instruction":
                            system_instruction
                    }
                )

                print(
                    "✓ Gemini response received."
                )

                break


            except Exception as error:

                last_error = error

                error_text = str(
                    error
                )

                print(
                    f"\n✗ Gemini API error "
                    f"(attempt "
                    f"{attempt + 1}/"
                    f"{self.max_retries + 1}):"
                )

                print(
                    error_text
                )


                # ==========================================
                # QUOTA / RATE LIMIT
                # ==========================================

                if (
                    "429" in error_text
                    or
                    "RESOURCE_EXHAUSTED"
                    in error_text
                    or
                    "quota"
                    in error_text.lower()
                ):

                    print(
                        "\n⚠ Gemini API quota "
                        "or rate limit detected."
                    )


                    # --------------------------------------
                    # Daily quota exhausted
                    # --------------------------------------

                    if (
                        "PerDay"
                        in error_text
                        or
                        "per day"
                        in error_text.lower()
                    ):

                        return {
                            "answer": (
                                "The brochure information "
                                "was retrieved successfully, "
                                "but the Gemini API quota "
                                "has been exhausted. "
                                "Please try again after "
                                "the quota resets."
                            ),
                            "sources": sources,
                            "error": error_text
                        }


                    # --------------------------------------
                    # Temporary rate limit
                    # --------------------------------------

                    if attempt < self.max_retries:

                        wait_time = (
                            5 * (attempt + 1)
                        )

                        print(
                            f"Retrying in "
                            f"{wait_time} seconds..."
                        )

                        time.sleep(
                            wait_time
                        )

                        continue


                    return {
                        "answer": (
                            "The brochure information "
                            "was retrieved successfully, "
                            "but the Gemini API is "
                            "temporarily unavailable "
                            "because of a rate limit."
                        ),
                        "sources": sources,
                        "error": error_text
                    }


                # ==========================================
                # OTHER API ERROR
                # ==========================================

                return {
                    "answer": (
                        "I was unable to generate an "
                        "answer from the brochure "
                        "information."
                    ),
                    "sources": sources,
                    "error": error_text
                }


        # ====================================================
        # NO RESPONSE
        # ====================================================

        if response is None:

            return {
                "answer": (
                    "I was unable to generate an answer "
                    "from the brochure information."
                ),
                "sources": sources,
                "error": (
                    str(last_error)
                    if last_error
                    else "Unknown Gemini error"
                )
            }


        # ====================================================
        # EXTRACT GEMINI RESPONSE
        # ====================================================

        answer = ""

        try:

            if response.text:

                answer = response.text.strip()

        except Exception as error:

            print(
                f"✗ Unable to extract Gemini response: "
                f"{error}"
            )

            answer = ""


        # ====================================================
        # EMPTY RESPONSE
        # ====================================================

        if not answer:

            answer = FALLBACK_ANSWER


        # ====================================================
        # FINAL RESULT
        # ====================================================

        return {
            "answer": answer,
            "sources": sources
        }


    # ========================================================
    # ALIAS
    # ========================================================

    def generate(
        self,
        question,
        brand,
        model,
        chunks
    ):

        return self.generate_answer(
            question=question,
            brand=brand,
            model=model,
            chunks=chunks
        )


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE - GEMINI GENERATOR TEST"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # Initialize generator
    # --------------------------------------------------------

    generator = GeminiGenerator()


    # --------------------------------------------------------
    # Vehicle
    # --------------------------------------------------------

    question = (
        "What is the maximum power "
        "of the XUV 3XO?"
    )

    brand = "mahindra"

    model = "xuv3xo"


    # --------------------------------------------------------
    # Brochure evidence
    # --------------------------------------------------------

    chunks = [

        {
            "brand": "mahindra",

            "model": "xuv3xo",

            "section":
                "engine and transmission technical specifications",

            "page": 14,

            "brochure":
                "xuv3xo_brochure.pdf",

            "rerank_score": 0.8750,

            "evidence_score": 1.5359,

            "text": (
                "ENGINE & TRANSMISSION TECHNICAL "
                "SPECIFICATIONS. Engine Type Capacity "
                "Max. Power Max. Torque Transmission Type. "
                "mStallion Turbo Charged Multipoint Fuel "
                "Injection (TCMPFi) engine 1.2 L "
                "82 kW @ 5000 r/min 200 Nm @ 1500-3500 "
                "r/min PETROL 6 MT / 6 AT. "
                "mStallion Turbo Charged Intercooled "
                "Gasoline Direct injection (TGDi) engine "
                "1.2 L 96 kW @ 5000 r/min "
                "230 Nm @ 1500-3750 r/min. "
                "Turbo Diesel with CRDe 1.5 L "
                "85.8 kW @ 3750 r/min "
                "300 Nm @ 1500-2500 r/min."
            )
        },


        {
            "brand": "mahindra",

            "model": "xuv3xo",

            "section":
                "engine and performance",

            "page": 6,

            "brochure":
                "xuv3xo_brochure.pdf",

            "rerank_score": 0.3000,

            "evidence_score": 1.4585,

            "text": (
                "Perfected performance. "
                "Engineered efficiency. "
                "Lead ahead with the most exciting "
                "and peppy engine offering "
                "segment leading power of "
                "96 kW @ 5000 r/min and "
                "230 Nm of torque "
                "@ 1500-3750 r/min."
            )
        }
    ]


    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    result = generator.generate_answer(
        question=question,
        brand=brand,
        model=model,
        chunks=chunks
    )


    # --------------------------------------------------------
    # Answer
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "GENERATED ANSWER"
    )

    print(
        "=" * 70
    )

    print(
        f"\n{result.get('answer', '')}"
    )


    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "SOURCES"
    )

    print(
        "=" * 70
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
    # Error information
    # --------------------------------------------------------

    if result.get("error"):

        print(
            "\n" + "=" * 70
        )

        print(
            "API ERROR"
        )

        print(
            "=" * 70
        )

        print(
            result["error"]
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
