from pathlib import Path
from uuid import uuid4
from typing import BinaryIO
from hashlib import sha256

CHUNK_SIZE = 64 * 1024


class UploadTooLargeError(ValueError):
    pass


def copy_with_limit(
    source: BinaryIO,
    destination: BinaryIO,
    max_bytes: int,
) -> tuple[int, str]:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    total = 0
    hasher = sha256()
    while True:
        chunk = source.read(CHUNK_SIZE)
        if not chunk:
            break

        total += len(chunk)
        if total > max_bytes:
            raise UploadTooLargeError("File exceeds maximum size")

        destination.write(chunk)
        hasher.update(chunk)

    return total, hasher.hexdigest()


def save_pdf_stream(
    source: BinaryIO,
    storage_dir: Path,
    max_bytes: int,
) -> tuple[str, int, str]:
    storage_dir.mkdir(parents=True, exist_ok=True)

    storage_key = f"{uuid4().hex}.pdf"
    target = storage_dir / storage_key
    created = False

    try:
        with target.open("xb") as destination:
            created = True
            size, content_hash = copy_with_limit(source, destination, max_bytes)
    except Exception:
        if created:
            target.unlink(missing_ok=True)
        raise

    return storage_key, size, content_hash
