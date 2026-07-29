import re

from app.core.config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    clean_text = normalize_text(text)
    if not clean_text:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", clean_text) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            step = max(1, chunk_size - overlap)
            for start in range(0, len(paragraph), step):
                piece = paragraph[start : start + chunk_size].strip()
                if piece:
                    chunks.append(piece)
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current.strip())
            suffix = current[-overlap:].strip() if current else ""
            current = f"{suffix}\n\n{paragraph}".strip() if suffix else paragraph

    if current:
        chunks.append(current.strip())

    return chunks
