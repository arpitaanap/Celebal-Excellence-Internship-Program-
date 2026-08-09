import sys
import json
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Add backend/ to Python import path
sys.path.insert(
    0,
    str(BASE_DIR)
)


# ============================================================
# IMPORT
# ============================================================

from rag.metadata_filter import MetadataFilter


# ============================================================
# METADATA FILE
# ============================================================

METADATA_FILE = (
    BASE_DIR
    / "vector_store"
    / "metadata.json"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("DRIVE WISE - METADATA FILTER TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Check metadata file
    # --------------------------------------------------------

    if not METADATA_FILE.exists():

        print(
            "\n❌ Metadata file not found:"
        )

        print(
            METADATA_FILE
        )

        return

    print(
        f"\nMetadata file:"
    )

    print(
        METADATA_FILE
    )

    # --------------------------------------------------------
    # Load metadata
    # --------------------------------------------------------

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

    print(
        f"\nTotal metadata chunks: "
        f"{len(metadata)}"
    )

    # --------------------------------------------------------
    # Create metadata filter
    # --------------------------------------------------------

    metadata_filter = MetadataFilter(
        metadata
    )

    # --------------------------------------------------------
    # Test vehicle
    # --------------------------------------------------------

    brand = "Mahindra"
    model = "XUV 3XO"

    print(
        "\nSelected vehicle:"
    )

    print(
        f"Brand : {brand}"
    )

    print(
        f"Model : {model}"
    )

    # --------------------------------------------------------
    # Apply metadata filtering
    # --------------------------------------------------------

    indices = metadata_filter.filter(
        brand=brand,
        model=model
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("METADATA FILTERING RESULT")
    print("=" * 70)

    print(
        f"\nFiltered chunks: "
        f"{len(indices)}"
    )

    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if not indices:

        print(
            "\n❌ No chunks found for:"
        )

        print(
            f"{brand} {model}"
        )

        return

    # --------------------------------------------------------
    # Successful filtering
    # --------------------------------------------------------

    print(
        "\n✓ Metadata filtering successful."
    )

    # --------------------------------------------------------
    # Verify every returned chunk
    # --------------------------------------------------------

    incorrect = []

    for index in indices:

        item = metadata[index]

        item_brand = str(
            item.get(
                "brand",
                ""
            )
        ).strip().lower()

        item_model = str(
            item.get(
                "model",
                ""
            )
        ).strip().lower()

        if (
            item_brand != brand.lower()
            or
            item_model != model.lower()
        ):

            incorrect.append(
                index
            )

    # --------------------------------------------------------
    # Verification result
    # --------------------------------------------------------

    if incorrect:

        print(
            "\n❌ Incorrect chunks found!"
        )

        print(
            f"Incorrect indices: "
            f"{incorrect}"
        )

    else:

        print(
            "\n✓ All returned chunks belong "
            "to the selected vehicle."
        )

    # --------------------------------------------------------
    # Show sample chunks
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("SAMPLE FILTERED CHUNKS")
    print("=" * 70)

    for number, index in enumerate(
        indices[:5],
        start=1
    ):

        item = metadata[index]

        print(
            f"\nChunk {number}"
        )

        print(
            "-" * 70
        )

        print(
            f"Index   : {index}"
        )

        print(
            f"Brand   : {item.get('brand', '')}"
        )

        print(
            f"Model   : {item.get('model', '')}"
        )

        print(
            f"Section : {item.get('section', '')}"
        )

        print(
            f"Page    : {item.get('page', '')}"
        )

        print(
            f"Brochure: {item.get('brochure', '')}"
        )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    if not incorrect:

        print("\n" + "=" * 70)
        print("✓ PHASE 5.1 METADATA FILTERING PASSED")
        print("=" * 70)

    else:

        print("\n" + "=" * 70)
        print("❌ PHASE 5.1 METADATA FILTERING FAILED")
        print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()