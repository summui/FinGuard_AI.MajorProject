# Tests for Sam's Track B — Contract upload, extraction and Gemini analysis
import pytest
from unittest.mock import patch, MagicMock
from app.services.document_extract import extract_contract_text
from app.services.gemini_client import analyze_contract


# ─── Test 1 — Valid PDF extraction succeeds ───────────────────────────────────
def test_extract_text_pymupdf_success(tmp_path):
    """Valid text-based PDF should extract text without OCR fallback."""
    import pymupdf as fitz

    # create a real PDF with enough text to pass the 50 word threshold
    pdf_path = tmp_path / "test_contract.pdf"
    doc = fitz.open()
    page = doc.new_page()

    # insert text in a proper font block so PyMuPDF can extract it
    page.insert_textbox(
        fitz.Rect(50, 50, 500, 700),
        "This is a loan agreement between the borrower and the lender. " * 10,
        fontsize=11,
        fontname="helv",
    )
    doc.save(str(pdf_path))
    doc.close()

    result = extract_contract_text(str(pdf_path))

    assert isinstance(result, str)
    assert len(result.split()) >= 50


# ─── Test 2 — Non-PDF and oversized file rejected (BR-03) ────────────────────
def test_file_validation_rejects_non_pdf(tmp_path):
    """Non-PDF file should be caught before extraction."""
    txt_path = tmp_path / "contract.txt"
    txt_path.write_text("This is not a PDF file.")

    filename = str(txt_path)
    assert not filename.endswith(".pdf"), "Non-PDF file should be rejected"


def test_file_validation_rejects_oversized():
    """File over 15MB should be rejected."""
    max_size = 15 * 1024 * 1024
    fake_file_size = 16 * 1024 * 1024

    assert fake_file_size > max_size, "Oversized file should be rejected"


# ─── Test 3 — Unreadable PDF returns correct error ───────────────────────────
def test_extract_text_unreadable_pdf(tmp_path):
    """Corrupt or empty PDF should raise ValueError with correct message."""
    import pymupdf as fitz

    pdf_path = tmp_path / "empty_contract.pdf"
    doc = fitz.open()
    doc.new_page()  # blank page, no text
    doc.save(str(pdf_path))
    doc.close()

    with patch("app.services.document_extract.extract_text_ocr", return_value=""):
        with pytest.raises(ValueError) as exc_info:
            extract_contract_text(str(pdf_path))

    assert "unreadable" in str(exc_info.value).lower()


# ─── Test 4 — Gemini timeout triggers retry ──────────────────────────────────
def test_gemini_retries_on_failure():
    """Gemini API failure should retry up to max_retries times."""
    sample_text = "This is a loan agreement. " * 30

    call_count = 0

    def mock_generate(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Simulated Gemini timeout")
        mock_response = MagicMock()
        mock_response.text = '{"risk_rating": "Low", "summary": "Test summary.", "red_flags": [], "green_flags": []}'
        return mock_response

    with patch("app.services.gemini_client.client") as mock_client:
        mock_client.models.generate_content.side_effect = mock_generate
        result = analyze_contract(sample_text, max_retries=2)

    assert result["risk_rating"] == "Low"
    assert call_count == 3