"""
Step 2a: Extract raw text from an uploaded contract PDF.

Handles both digital PDFs (text already embedded) and scanned PDFs
(image-only pages) via OCR fallback.
"""
import fitz  # pymupdf
import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Try direct text extraction first (fast, works for digital PDFs).
    Fall back to OCR per-page if a page has little/no extractable text
    (typical of scanned contracts).
    """
    doc = fitz.open(pdf_path)
    full_text = []

    for page_num, page in enumerate(doc):
        text = page.get_text().strip()

        if len(text) < 20:  # heuristic: near-empty page -> likely scanned image
            text = _ocr_page(pdf_path, page_num)

        full_text.append(text)

    doc.close()
    return "\n\n".join(full_text)


def _ocr_page(pdf_path: str, page_num: int) -> str:
    images = convert_from_path(
        pdf_path, first_page=page_num + 1, last_page=page_num + 1
    )
    if not images:
        return ""
    return pytesseract.image_to_string(images[0])


if __name__ == "__main__":
    # quick manual test: python parser.py path/to/contract.pdf
    import sys

    text = extract_text_from_pdf(sys.argv[1])
    print(text[:2000])
    print(f"\n\n[Total chars extracted: {len(text)}]")
