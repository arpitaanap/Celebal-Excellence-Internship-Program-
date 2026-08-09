from typing import List, Dict


class ContextBuilder:

    def __init__(
        self,
        max_chunks=5,
        max_characters=12000
    ):
        """
        Controls how much retrieved information
        is finally sent to the LLM.
        """

        self.max_chunks = max_chunks
        self.max_characters = max_characters

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    def build_context(
        self,
        results: List[Dict]
    ) -> str:

        if not results:
            return ""

        selected_chunks = []

        total_characters = 0

        # ----------------------------------------------------
        # Results are expected to already be ranked.
        # ----------------------------------------------------

        for result in results:

            if len(selected_chunks) >= self.max_chunks:
                break

            text = str(
                result.get(
                    "text",
                    ""
                )
            ).strip()

            if not text:
                continue

            # ------------------------------------------------
            # Avoid exceeding context limit
            # ------------------------------------------------

            remaining = (
                self.max_characters
                - total_characters
            )

            if remaining <= 0:
                break

            if len(text) > remaining:

                text = text[:remaining]

            # ------------------------------------------------
            # Build source information
            # ------------------------------------------------

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

            chunk = (
                f"[Source]\n"
                f"Brand: {brand}\n"
                f"Model: {model}\n"
                f"Section: {section}\n"
                f"Page: {page}\n"
                f"Brochure: {brochure}\n"
                f"Content:\n"
                f"{text}\n"
            )

            selected_chunks.append(
                chunk
            )

            total_characters += len(text)

        return "\n" + "=" * 60 + "\n".join(
            selected_chunks
        )

    # ========================================================
    # BUILD STRUCTURED SOURCES
    # ========================================================

    def build_sources(
        self,
        results: List[Dict]
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
                    ),
                    "rerank_score": result.get(
                        "rerank_score"
                    )
                }
            )

        return sources


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE - CONTEXT BUILDER TEST"
    )

    print(
        "=" * 70
    )

    builder = ContextBuilder(
        max_chunks=3,
        max_characters=3000
    )

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
                "The maximum power output of "
                "the XUV 3XO is 130 PS."
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
                "The XUV 3XO is available with "
                "advanced engine options designed "
                "for performance and efficiency."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Performance",
            "page": 14,
            "brochure": "xuv3xo_brochure.pdf",
            "rerank_score": 5.9,
            "text": (
                "The vehicle provides strong "
                "performance with responsive "
                "acceleration."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Safety",
            "page": 20,
            "brochure": "xuv3xo_brochure.pdf",
            "rerank_score": 2.1,
            "text": (
                "The XUV 3XO includes several "
                "advanced safety features."
            )
        }
    ]

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context = builder.build_context(
        results
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL CONTEXT"
    )

    print(
        "=" * 70
    )

    print(context)

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    sources = builder.build_sources(
        results[:3]
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

    for source in sources:

        print(source)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()