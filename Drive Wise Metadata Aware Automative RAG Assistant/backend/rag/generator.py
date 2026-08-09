from typing import List, Dict


class RAGGenerator:
    """
    Connects the retrieved brochure context
    to the final answer generation stage.

    The actual LLM/Gemini call will be added
    in the next stage.
    """

    def __init__(self):
        print("\nRAG Generator initialized.")

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    def build_prompt(
        self,
        query: str,
        context: str
    ) -> str:
        """
        Build the prompt that will eventually
        be sent to the LLM.
        """

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not context:
            context = (
                "No relevant brochure information "
                "was retrieved."
            )

        prompt = f"""
You are Drive Wise, an automotive brochure assistant.

Answer the user's question using ONLY the
provided brochure context.

If the answer is not present in the context,
say that the information is not available
in the provided brochure.

Do not invent specifications.

User Question:
{query}

Brochure Context:
{context}

Answer:
""".strip()

        return prompt

    # ========================================================
    # PREPARE REQUEST
    # ========================================================

    def prepare(
        self,
        query: str,
        results: List[Dict]
    ) -> Dict:
        """
        Prepare retrieved results for the
        generation stage.

        ContextBuilder is intentionally imported
        here so that the pipeline becomes:

        Retriever
             ↓
        Reranker
             ↓
        ContextBuilder
             ↓
        Generator
        """

        from rag.context_builder import ContextBuilder

        context_builder = ContextBuilder(
            max_chunks=5,
            max_characters=12000
        )

        context = context_builder.build_context(
            results
        )

        sources = context_builder.build_sources(
            results
        )

        prompt = self.build_prompt(
            query=query,
            context=context
        )

        return {
            "query": query,
            "context": context,
            "prompt": prompt,
            "sources": sources
        }


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE - RAG GENERATOR TEST"
    )

    print(
        "=" * 70
    )

    generator = RAGGenerator()

    # --------------------------------------------------------
    # Simulated reranked results
    # --------------------------------------------------------

    results = [

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Engine Specifications",
            "page": 13,
            "brochure": "xuv3xo_brochure.pdf",
            "rerank_score": 8.2,
            "text": (
                "The maximum power output "
                "of the XUV 3XO is 130 PS."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Engine",
            "page": 12,
            "brochure": "xuv3xo_brochure.pdf",
            "rerank_score": 6.8,
            "text": (
                "The XUV 3XO is available "
                "with advanced engine options."
            )
        }
    ]

    query = (
        "What is the maximum power "
        "of the XUV 3XO?"
    )

    # --------------------------------------------------------
    # Prepare generation request
    # --------------------------------------------------------

    request = generator.prepare(
        query=query,
        results=results
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "GENERATED PROMPT"
    )

    print(
        "=" * 70
    )

    print(
        request["prompt"]
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "SOURCES"
    )

    print(
        "=" * 70
    )

    for source in request["sources"]:

        print(
            source
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()