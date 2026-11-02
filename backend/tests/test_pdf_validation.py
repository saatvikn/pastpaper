import pymupdf
import pytest

from app.services.pdf_validation import InvalidPDFError, validate_pdf


def test_validate_pdf_accepts_page_limit(tmp_path):
    path = tmp_path / "paper.pdf"

    with pymupdf.open() as document:
        document.new_page()
        document.new_page()
        document.save(path)

    assert validate_pdf(path, max_pages=2) == 2


@pytest.mark.parametrize("content", [b"", b"not a PDF"])
def test_validate_pdf_rejects_unreadable_files(tmp_path, content):
    path = tmp_path / "invalid.pdf"
    path.write_bytes(content)

    with pytest.raises(InvalidPDFError, match="Could not read PDF"):
        validate_pdf(path, max_pages=1)


def test_validate_pdf_rejects_too_many_pages(tmp_path):
    path = tmp_path / "paper.pdf"

    with pymupdf.open() as document:
        document.new_page()
        document.new_page()
        document.save(path)

    with pytest.raises(InvalidPDFError, match="maximum page count"):
        validate_pdf(path, max_pages=1)


@pytest.mark.parametrize("user_password", ["reader-test", ""])
def test_validate_pdf_rejects_encrypted_files(tmp_path, user_password):
    path = tmp_path / "encrypted.pdf"

    with pymupdf.open() as document:
        document.new_page()
        document.save(
            path,
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            owner_pw="owner-test",
            user_pw=user_password,
        )

    with pytest.raises(InvalidPDFError, match="Encrypted PDFs"):
        validate_pdf(path, max_pages=1)
