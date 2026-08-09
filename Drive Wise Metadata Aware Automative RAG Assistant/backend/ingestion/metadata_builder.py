import json
import re
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

BROCHURE_DIR = BASE_DIR / "data" / "brochures"

PROCESSED_DIR = BASE_DIR / "processed"

INPUT_FILE = PROCESSED_DIR / "brochure_pages.json"

OUTPUT_FILE = PROCESSED_DIR / "structured_chunks.json"


# ============================================================
# CHUNK SETTINGS
# ============================================================

CHUNK_SIZE = 700

CHUNK_OVERLAP = 100


# ============================================================
# BROCHURE SECTION KEYWORDS
# ============================================================

SECTION_KEYWORDS = {

    "engine and performance": [
        "engine",
        "power",
        "torque",
        "performance",
        "transmission",
        "horsepower",
        "rpm"
    ],

    "fuel efficiency": [
        "mileage",
        "fuel efficiency",
        "fuel economy",
        "kmpl",
        "range"
    ],

    "safety": [
        "safety",
        "airbag",
        "abs",
        "ebd",
        "esc",
        "brake",
        "collision",
        "camera",
        "adas"
    ],

    "dimensions": [
        "dimension",
        "length",
        "width",
        "height",
        "wheelbase",
        "ground clearance",
        "boot space"
    ],

    "interior and comfort": [
        "interior",
        "seat",
        "seating",
        "comfort",
        "climate",
        "air conditioner",
        "sunroof"
    ],

    "infotainment and connectivity": [
        "infotainment",
        "touchscreen",
        "bluetooth",
        "android auto",
        "apple carplay",
        "connectivity",
        "speaker",
        "audio"
    ],

    "exterior": [
        "exterior",
        "headlamp",
        "led",
        "alloy",
        "bumper",
        "grille",
        "tail lamp"
    ],

    "technology": [
        "technology",
        "connected",
        "wireless",
        "digital",
        "smart",
        "assist"
    ]
}


# ============================================================
# LOAD EXTRACTED PAGES
# ============================================================

def load_pages():

    if not INPUT_FILE.exists():

        print(
            "Input file was not found."
        )

        print(
            f"Expected: {INPUT_FILE}"
        )

        return []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# DETECT BROCHURE SECTION
# ============================================================

def detect_section(text):

    text_lower = text.lower()

    section_scores = {}

    for section, keywords in SECTION_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text_lower:

                score += 1

        section_scores[section] = score

    best_section = max(
        section_scores,
        key=section_scores.get
    )

    best_score = section_scores[
        best_section
    ]

    if best_score == 0:

        return "general"

    return best_section


# ============================================================
# GET VEHICLE DETAILS
# ============================================================

def get_vehicle_details(
    brochure_name,
    page_data
):

    brochure_path = None

    # --------------------------------------------------------
    # Search for the matching brochure
    # --------------------------------------------------------

    matches = list(
        BROCHURE_DIR.rglob(
            brochure_name
        )
    )

    if matches:

        brochure_path = matches[0]

    if brochure_path:

        model = brochure_path.parent.name

        brand = brochure_path.parent.parent.name

    else:

        brand = "unknown"

        model = "unknown"

    return brand, model


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(text):

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(chunk)

        start += (
            CHUNK_SIZE - CHUNK_OVERLAP
        )

    return chunks


# ============================================================
# CREATE STRUCTURED RECORDS
# ============================================================

def build_metadata_records(pages):

    records = []

    chunk_id = 1

    for page_data in pages:

        brochure_name = page_data.get(
            "brochure",
            ""
        )

        page_number = page_data.get(
            "page",
            0
        )

        text = page_data.get(
            "text",
            ""
        )

        if not text:

            continue

        # ----------------------------------------------------
        # Clean extracted text
        # ----------------------------------------------------

        text = clean_text(
            text
        )

        # ----------------------------------------------------
        # Get brand and model
        # ----------------------------------------------------

        brand, model = get_vehicle_details(
            brochure_name,
            page_data
        )

        # ----------------------------------------------------
        # Detect section
        # ----------------------------------------------------

        section = detect_section(
            text
        )

        # ----------------------------------------------------
        # Determine content type
        # ----------------------------------------------------

        normal_text = page_data.get(
            "normal_text",
            ""
        )

        ocr_text = page_data.get(
            "ocr_text",
            ""
        )

        if ocr_text:

            content_type = "text_and_ocr"

        else:

            content_type = "text"

        # ----------------------------------------------------
        # Create smaller structured chunks
        # ----------------------------------------------------

        text_chunks = create_chunks(
            text
        )

        for chunk in text_chunks:

            record = {

                "chunk_id": chunk_id,

                "brand": brand,

                "model": model,

                "section": section,

                "page": page_number,

                "brochure": brochure_name,

                "version": "latest",

                "content_type": content_type,

                "text": chunk

            }

            records.append(
                record
            )

            chunk_id += 1

    return records


# ============================================================
# SAVE STRUCTURED CHUNKS
# ============================================================

def save_records(records):

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print("\n" + "=" * 60)

    print(
        "BUILDING BROCHURE METADATA"
    )

    print("=" * 60)

    pages = load_pages()

    if not pages:

        print(
            "No extracted brochure pages found."
        )

        return

    print(
        f"Pages loaded: {len(pages)}"
    )

    records = build_metadata_records(
        pages
    )

    save_records(
        records
    )

    print("\n" + "=" * 60)

    print(
        "STRUCTURED CHUNKING COMPLETED"
    )

    print("=" * 60)

    print(
        f"Pages processed : {len(pages)}"
    )

    print(
        f"Chunks created  : {len(records)}"
    )

    print(
        f"Output file     : {OUTPUT_FILE}"
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()