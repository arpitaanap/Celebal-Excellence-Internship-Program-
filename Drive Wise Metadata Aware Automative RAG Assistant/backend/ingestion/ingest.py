import json
import os
from pathlib import Path

import fitz


# ---------------------------------------------------------
# Project paths
# ------------------f---------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

BROCHURE_DIR = BASE_DIR / "data" / "brochures"
OUTPUT_DIR = BASE_DIR / "processed"

OUTPUT_FILE = OUTPUT_DIR / "brochure_pages.json"


# ---------------------------------------------------------
# Extract text from one PDF
# ---------------------------------------------------------

def extract_pdf_pages(pdf_path):
    pages = []

    try:
        document = fitz.open(pdf_path)

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text").strip()

            pages.append({
                "page": page_number,
                "text": text
            })

        document.close()

    except Exception as error:
        print(f"Could not read {pdf_path.name}: {error}")

    return pages


# ---------------------------------------------------------
# Get brand and model from folder structure
# ---------------------------------------------------------

def get_vehicle_details(pdf_path):

    model_folder = pdf_path.parent
    brand_folder = model_folder.parent

    brand = brand_folder.name
    model = model_folder.name

    return brand, model


# ---------------------------------------------------------
# Process all brochures
# ---------------------------------------------------------

def process_brochures():

    if not BROCHURE_DIR.exists():

        print("Brochure folder was not found.")
        print(BROCHURE_DIR)

        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    all_pages = []

    pdf_files = list(
        BROCHURE_DIR.rglob("*.pdf")
    )

    if not pdf_files:

        print("No brochure PDFs were found.")
        return

    print(f"\nFound {len(pdf_files)} brochure(s).\n")

    for pdf_path in pdf_files:

        brand, model = get_vehicle_details(
            pdf_path
        )

        print(f"Processing: {brand} / {model}")
        print(f"File: {pdf_path.name}")

        pages = extract_pdf_pages(
            pdf_path
        )

        for page_data in pages:

            text = page_data["text"]

            if not text:
                continue

            record = {
                "brand": brand,
                "model": model,
                "brochure": pdf_path.name,
                "page": page_data["page"],
                "content_type": "text",
                "text": text
            }

            all_pages.append(record)

        print(
            f"Pages extracted: {len(pages)}"
        )
        print("-" * 50)

    # -----------------------------------------------------
    # Save extracted information
    # -----------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_pages,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print("BROCHURE INGESTION COMPLETED")
    print("=" * 60)

    print(f"Brochures processed : {len(pdf_files)}")
    print(f"Pages stored        : {len(all_pages)}")
    print(f"Output file         : {OUTPUT_FILE}")


# ---------------------------------------------------------
# Start the program
# ---------------------------------------------------------

if __name__ == "__main__":

    process_brochures()