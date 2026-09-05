# Document text extraction service using PyMuPDF and Tesseract OCR for contracts — Sam
import pymupdf as fitz
import pytesseract
from PIL import Image
import io

# Windows — tell pytesseract where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

MIN_WORDS_THRESHOLD = 50  # per SRS edge case spec


def extract_text_pymupdf(pdf_path: str) -> str:
    """Extract text from a digital/text-based PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()


def extract_text_ocr(pdf_path: str) -> str:
    """Extract text from a scanned/image PDF using Tesseract OCR via PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        text += pytesseract.image_to_string(img) + "\n"
    doc.close()
    return text.strip()


def extract_contract_text(pdf_path: str) -> str:
    """
    Main extraction function.
    Tries PyMuPDF first. Falls back to Tesseract OCR if text is too short.
    Raises ValueError if document is unreadable after both attempts.
    """
    text = extract_text_pymupdf(pdf_path)

    if len(text.split()) < MIN_WORDS_THRESHOLD:
        print("PyMuPDF returned too little text — falling back to OCR...")
        text = extract_text_ocr(pdf_path)

    if len(text.split()) < MIN_WORDS_THRESHOLD:
        raise ValueError("Document unreadable. Please upload a clearer PDF copy.")

    return text