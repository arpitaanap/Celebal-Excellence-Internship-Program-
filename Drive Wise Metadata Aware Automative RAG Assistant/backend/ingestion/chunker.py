import json
import re
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "processed"

INPUT_FILE = PROCESSED_DIR / "brochure_pages.json"
OUTPUT_FILE = PROCESSED_DIR / "structured_chunks.json"


# ============================================================
# CHUNK CONFIGURATION
# ============================================================

# Maximum approximate characters per chunk.
MAX_CHUNK_SIZE = 1800

# Minimum characters required for a useful chunk.
MIN_CHUNK_SIZE = 100


# ============================================================
# SECTION KEYWORDS
# ============================================================

SECTION_KEYWORDS = {

    "Engine": [
        "engine",
        "power",
        "torque",
        "displacement",
        "cylinder",
        "petrol",
        "diesel",
        "turbo"
    ],

    "Performance": [
        "performance",
        "acceleration",
        "top speed",
        "drive mode",
        "driving mode"
    ],

    "Transmission": [
        "transmission",
        "manual",
        "automatic",
        "gearbox",
        "amt",
        "dct",
        "imt",
        "cvt"
    ],

    "Mileage": [
        "mileage",
        "fuel efficiency",
        "fuel economy",
        "kmpl"
    ],

    "Safety": [
        "safety",
        "airbag",
        "airbags",
        "abs",
        "ebd",
        "esp",
        "brake",
        "hill hold",
        "hill descent",
        "seat belt",
        "parking sensor",
        "camera"
    ],

    "Dimensions": [
        "dimensions",
        "length",
        "width",
        "height",
        "wheelbase",
        "ground clearance"
    ],

    "Exterior": [
        "exterior",
        "headlamp",
        "headlight",
        "tail lamp",
        "alloy wheel",
        "tyre",
        "wheel",
        "sunroof",
        "roof"
    ],

    "Interior": [
        "interior",
        "dashboard",
        "seat",
        "seats",
        "seating",
        "upholstery",
        "cabin",
        "steering"
    ],

    "Comfort": [
        "comfort",
        "climate control",
        "air conditioning",
        "air conditioner",
        "ventilated seat",
        "seat adjustment",
        "armrest"
    ],

    "Infotainment": [
        "infotainment",
        "touchscreen",
        "touch screen",
        "display",
        "speaker",
        "audio"
    ],

    "Connectivity": [
        "connectivity",
        "apple carplay",
        "android auto",
        "bluetooth",
        "usb",
        "wireless"
    ],

    "Fuel": [
        "fuel tank",
        "tank capacity",
        "fuel type",
        "petrol",
        "diesel"
    ],

    "Features": [
        "features",
        "feature",
        "technology",
        "convenience"
    ]
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text)

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# DETECT SECTION
# ============================================================

def detect_section(text):

    normalized = normalize_text(
        text
    ).lower()

    if not normalized:
        return "General"


    scores = {}

    for section, keywords in SECTION_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            keyword = keyword.lower()

            # Give slightly more importance to
            # exact phrase matches.

            if keyword in normalized:

                score += 1

                if (
                    f" {keyword} "
                    in f" {normalized} "
                ):
                    score += 0.5

        if score > 0:

            scores[section] = score


    if not scores:

        return "General"


    return max(
        scores,
        key=scores.get
    )


# ============================================================
# EXTRACT METADATA
# ============================================================

def extract_metadata(page):

    brand = str(
        page.get(
            "brand",
            ""
        )
    ).strip().lower()

    model = str(
        page.get(
            "model",
            ""
        )
    ).strip().lower()

    brochure = page.get(
        "brochure",
        page.get(
            "file",
            page.get(
                "filename",
                ""
            )
        )
    )

    page_number = page.get(
        "page",
        page.get(
            "page_number",
            None
        )
    )

    return {
        "brand": brand,
        "model": model,
        "brochure": brochure,
        "page": page_number
    }


# ============================================================
# SPLIT LARGE TEXT
# ============================================================

def split_large_text(
    text,
    max_size=MAX_CHUNK_SIZE
):

    text = normalize_text(
        text
    )

    if len(text) <= max_size:

        return [text]


    # Try paragraph-based splitting first.

    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    chunks = []

    current = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue


        # If adding the paragraph still fits.

        if (
            len(current)
            + len(paragraph)
            + 2
            <= max_size
        ):

            if current:

                current += (
                    "\n\n"
                    + paragraph
                )

            else:

                current = paragraph

        else:

            if current:

                chunks.append(
                    current.strip()
                )

            # If a single paragraph itself
            # is too large, split by sentences.

            if len(paragraph) > max_size:

                sentences = re.split(
                    r"(?<=[.!?])\s+",
                    paragraph
                )

                current = ""

                for sentence in sentences:

                    sentence = sentence.strip()

                    if not sentence:
                        continue

                    if (
                        len(current)
                        + len(sentence)
                        + 1
                        <= max_size
                    ):

                        if current:

                            current += (
                                " "
                                + sentence
                            )

                        else:

                            current = sentence

                    else:

                        if current:

                            chunks.append(
                                current.strip()
                            )

                        current = sentence

                if current:

                    chunks.append(
                        current.strip()
                    )

                current = ""

            else:

                current = paragraph


    if current:

        chunks.append(
            current.strip()
        )


    return [
        chunk
        for chunk in chunks
        if len(chunk) >= MIN_CHUNK_SIZE
    ]


# ============================================================
# CREATE STRUCTURED CHUNKS
# ============================================================

def create_chunks(pages):

    chunks = []

    chunk_id = 0


    for page in pages:

        metadata = extract_metadata(
            page
        )

        text = page.get(
            "text",
            ""
        )

        text = normalize_text(
            text
        )

        if not text:

            continue


        # ----------------------------------------------------
        # Detect logical brochure section
        # ----------------------------------------------------

        section = page.get(
            "section",
            ""
        )

        if not section:

            section = detect_section(
                text
            )

        section = str(
            section
        ).strip()

        if not section:

            section = "General"


        # ----------------------------------------------------
        # Split page into manageable chunks
        # ----------------------------------------------------

        text_chunks = split_large_text(
            text
        )


        for chunk_number, chunk_text in enumerate(
            text_chunks,
            start=1
        ):

            if not chunk_text:

                continue


            chunk = {

                "chunk_id": chunk_id,

                "brand": metadata[
                    "brand"
                ],

                "model": metadata[
                    "model"
                ],

                "section": section,

                "page": metadata[
                    "page"
                ],

                "brochure": metadata[
                    "brochure"
                ],

                "chunk_number": chunk_number,

                "text": chunk_text
            }


            chunks.append(
                chunk
            )

            chunk_id += 1


    return chunks


# ============================================================
# SAVE CHUNKS
# ============================================================

def save_chunks(chunks):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# SHOW STATISTICS
# ============================================================

def show_statistics(chunks):

    print(
        "\n" + "=" * 70
    )

    print(
        "STRUCTURED CHUNKING RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTotal chunks: {len(chunks)}"
    )


    # --------------------------------------------------------
    # Brand/model distribution
    # --------------------------------------------------------

    vehicles = {}

    for chunk in chunks:

        key = (
            chunk.get("brand", ""),
            chunk.get("model", "")
        )

        vehicles[key] = (
            vehicles.get(
                key,
                0
            )
            + 1
        )


    print(
        f"Vehicles: {len(vehicles)}"
    )


    print(
        "\nVehicle chunk distribution:"
    )

    for (
        brand,
        model
    ), count in sorted(
        vehicles.items()
    ):

        print(
            f"  {brand} / {model}: "
            f"{count}"
        )


    # --------------------------------------------------------
    # Section distribution
    # --------------------------------------------------------

    sections = {}

    for chunk in chunks:

        section = chunk.get(
            "section",
            "General"
        )

        sections[section] = (
            sections.get(
                section,
                0
            )
            + 1
        )


    print(
        "\nSection distribution:"
    )

    for section, count in sorted(
        sections.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"  {section}: {count}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE - STRUCTURED CHUNKING"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"\nInput file not found:\n"
            f"{INPUT_FILE}"
        )


    print(
        f"\nInput:\n{INPUT_FILE}"
    )

    print(
        f"\nOutput:\n{OUTPUT_FILE}"
    )


    # --------------------------------------------------------
    # Load page data
    # --------------------------------------------------------

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        pages = json.load(
            file
        )


    print(
        f"\nLoaded pages: {len(pages)}"
    )


    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    print(
        "\nCreating structured chunks..."
    )

    chunks = create_chunks(
        pages
    )


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_chunks(
        chunks
    )


    print(
        "\n✓ Structured chunks created."
    )

    print(
        f"✓ Saved {len(chunks)} chunks."
    )


    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    show_statistics(
        chunks
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "PHASE 5.2 CHUNKING COMPLETE"
    )

    print(
        "=" * 70
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()

