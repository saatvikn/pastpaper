from pathlib import Path
from uuid import uuid4
from typing import BinaryIO

CHUNK_SIZE = 64 * 1024


class UploadTooLargeError(ValueError):
    pass


def copy_with_limit(
    source: BinaryIO,
    destination: BinaryIO,
    max_bytes: int,
) -> int:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    total = 0
    while True:
        chunk = source.read(CHUNK_SIZE)
        if not chunk:
            break

        total += len(chunk)
        if total > max_bytes:
            raise UploadTooLargeError("File exceeds maximum size")

        destination.write(chunk)

    return total


def save_pdf_stream(
    source: BinaryIO,
    storage_dir: Path,
    max_bytes: int,
) -> tuple[str, int]:
    storage_dir.mkdir(parents=True, exist_ok=True)

    storage_key = f"{uuid4().hex}.pdf"
    target = storage_dir / storage_key
    created = False

    try:
        with target.open("xb") as destination:
            created = True
            size = copy_with_limit(source, destination, max_bytes)
    except Exception:
        if created:
            target.unlink(missing_ok=True)
        raise

    return storage_key, size
