import io
import os
from pathlib import Path

import pymupdf
import pytesseract

from PIL import Image


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

BROCHURE_DIR = BASE_DIR / "data" / "brochures"


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# CONVERT PDF PAGE INTO IMAGE
# ============================================================

def render_page(page):

    matrix = pymupdf.Matrix(
        2,
        2
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False
    )

    image_bytes = pixmap.tobytes(
        "png"
    )

    image = Image.open(
        io.BytesIO(image_bytes)
    )

    return image


# ============================================================
# EXTRACT TEXT FROM IMAGE USING OCR
# ============================================================

def extract_text_from_image(image):

    try:

        text = pytesseract.image_to_string(
            image
        )

        return text.strip()

    except Exception as error:

        print(
            f"OCR failed: {error}"
        )

        return ""


# ============================================================
# PROCESS ONE BROCHURE
# ============================================================

def process_brochure(pdf_path):

    print(
        f"\nProcessing: {pdf_path.name}"
    )

    document = pymupdf.open(
        pdf_path
    )

    extracted_pages = []

    for page_number, page in enumerate(
        document,
        start=1
    ):

        print(
            f"Checking page {page_number}..."
        )

        # ----------------------------------------------------
        # Extract normal PDF text
        # ----------------------------------------------------

        text = page.get_text(
            "text"
        ).strip()

        # ----------------------------------------------------
        # Check whether the page contains images
        # ----------------------------------------------------

        images = page.get_images(
            full=True
        )

        image_text = ""

        # ----------------------------------------------------
        # Run OCR if images are present
        # ----------------------------------------------------

        if images:

            page_image = render_page(
                page
            )

            image_text = extract_text_from_image(
                page_image
            )

        # ----------------------------------------------------
        # Combine normal text and OCR text
        # ----------------------------------------------------

        combined_text = text

        if image_text:

            if combined_text:

                combined_text += "\n\n"

            combined_text += image_text

        # ----------------------------------------------------
        # Store extracted page
        # ----------------------------------------------------

        if combined_text:

            extracted_pages.append({

                "page": page_number,

                "text": combined_text,

                "normal_text": text,

                "ocr_text": image_text,

                "image_count": len(images)

            })

    document.close()

    return extracted_pages


# ============================================================
# PROCESS ALL BROCHURES
# ============================================================

def process_all_brochures():

    if not BROCHURE_DIR.exists():

        print(
            "Brochure directory not found."
        )

        print(
            f"Expected location: {BROCHURE_DIR}"
        )

        return

    pdf_files = list(
        BROCHURE_DIR.rglob("*.pdf")
    )

    if not pdf_files:

        print(
            "No PDF brochures found."
        )

        return

    print(
        f"Found {len(pdf_files)} brochure(s)."
    )

    total_pages = 0

    for pdf_path in pdf_files:

        pages = process_brochure(
            pdf_path
        )

        total_pages += len(
            pages
        )

        print(
            f"Extracted pages: {len(pages)}"
        )

        print(
            "-" * 60
        )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "IMAGE-AWARE EXTRACTION COMPLETED"
    )

    print("=" * 60)

    print(
        f"Brochures processed : {len(pdf_files)}"
    )

    print(
        f"Pages processed     : {total_pages}"
    )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    process_all_brochures()