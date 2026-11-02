from app.services.storage import save_pdf_stream
from io import BytesIO
import pytest

from app.services.storage import CHUNK_SIZE, UploadTooLargeError, copy_with_limit


def test_save_pdf_stream(tmp_path):
    content = b"storage test"
    folder = tmp_path / "papers"

    key, size = save_pdf_stream(BytesIO(content), folder, max_bytes=len(content))
    assert (folder / key).read_bytes() == content
    assert size == len(content)

    another_key, _ = save_pdf_stream(BytesIO(content), folder, max_bytes=len(content))
    assert another_key != key


def test_copy_with_limit_accepts_exact_limit():
    content = b"x" * (CHUNK_SIZE + 3)
    destination = BytesIO()

    copied = copy_with_limit(BytesIO(content), destination, max_bytes=len(content))

    assert copied == len(content)
    assert destination.getvalue() == content


def test_copy_with_limit_rejects_oversize():
    with pytest.raises(UploadTooLargeError):
        copy_with_limit(BytesIO(b"1234567"), BytesIO(), max_bytes=6)


def test_save_pdf_stream_removes_partial_file(tmp_path):
    folder = tmp_path / "papers"
    content = b"x" * (CHUNK_SIZE + 1)

    with pytest.raises(UploadTooLargeError):
        save_pdf_stream(BytesIO(content), folder, max_bytes=CHUNK_SIZE)

    assert list(folder.iterdir()) == []
