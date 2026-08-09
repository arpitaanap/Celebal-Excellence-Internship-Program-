class SourceAttributor:

    def __init__(self):
        print("✓ Source attribution system initialized")

    # ========================================================
    # BUILD SOURCES
    # ========================================================

    def build_sources(self, results):

        if not results:
            return []

        sources = []

        for number, result in enumerate(
            results,
            start=1
        ):

            source = {
                "source": number,

                "brand": result.get(
                    "brand",
                    ""
                ),

                "model": result.get(
                    "model",
                    ""
                ),

                "brochure": result.get(
                    "brochure",
                    ""
                ),

                "section": result.get(
                    "section",
                    ""
                ),

                "page": result.get(
                    "page",
                    ""
                ),

                "chunk_index": result.get(
                    "_index",
                    result.get(
                        "chunk_index",
                        ""
                    )
                )
            }

            sources.append(
                source
            )

        return sources

    # ========================================================
    # FORMAT SOURCES FOR USER
    # ========================================================

    def format_sources(self, sources):

        if not sources:
            return "No sources available."

        lines = []

        lines.append(
            "SOURCES"
        )

        lines.append(
            "=" * 60
        )

        for source in sources:

            lines.append(
                f"\n[{source['source']}] "
                f"{source['brochure']}"
            )

            lines.append(
                f"    Brand   : "
                f"{source['brand']}"
            )

            lines.append(
                f"    Model   : "
                f"{source['model']}"
            )

            lines.append(
                f"    Section : "
                f"{source['section']}"
            )

            lines.append(
                f"    Page    : "
                f"{source['page']}"
            )

            if source.get(
                "chunk_index"
            ) != "":

                lines.append(
                    f"    Chunk   : "
                    f"{source['chunk_index']}"
                )

        return "\n".join(
            lines
        )


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE - SOURCE ATTRIBUTION TEST"
    )

    print(
        "=" * 70
    )

    results = [

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "brochure": "X3XO_brochure.pdf",
            "section": "Engine",
            "page": 12,
            "_index": 105
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "brochure": "X3XO_brochure.pdf",
            "section": "Engine Specifications",
            "page": 13,
            "_index": 106
        }
    ]

    attributor = SourceAttributor()

    sources = attributor.build_sources(
        results
    )

    print(
        "\nStructured Sources:"
    )

    for source in sources:
        print(source)

    print(
        "\n" + "=" * 70
    )

    print(
        attributor.format_sources(
            sources
        )
    )


if __name__ == "__main__":
    main()