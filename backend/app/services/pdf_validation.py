from pathlib import Path

import pymupdf


class InvalidPDFError(ValueError):
    pass


def validate_pdf(path: Path, max_pages: int) -> int:
    if max_pages <= 0:
        raise ValueError("max_pages must be positive")

    try:
        with pymupdf.open(path) as document:
            if not document.is_pdf:
                raise InvalidPDFError("Only PDF files are supported")

            if document.needs_pass or (document.metadata or {}).get("encryption"):
                raise InvalidPDFError("Encrypted PDFs are not supported")

            page_count = document.page_count

            if page_count < 1:
                raise InvalidPDFError("PDF contains no pages")
            if page_count > max_pages:
                raise InvalidPDFError("PDF exceeds maximum page count")

            return page_count
    except pymupdf.FileDataError as exc:
        raise InvalidPDFError("Could not read PDF") from exc
