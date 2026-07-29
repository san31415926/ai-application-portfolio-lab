from pathlib import Path

from pypdf import PdfReader

from app.core.config import ALLOWED_EXTENSIONS


def validate_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"unsupported file type: {suffix or '(none)'}. allowed: {allowed}")
    return suffix


def read_pdf_bytes(content: bytes) -> str:
    from io import BytesIO

    reader = PdfReader(BytesIO(content))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def read_document_bytes(filename: str, content: bytes) -> str:
    suffix = validate_extension(filename)
    if suffix == ".pdf":
        return read_pdf_bytes(content)
    return content.decode("utf-8", errors="ignore").strip()


def read_document_path(path: Path) -> str:
    suffix = validate_extension(path.name)
    if suffix == ".pdf":
        return read_pdf_bytes(path.read_bytes())
    return path.read_text(encoding="utf-8").strip()
