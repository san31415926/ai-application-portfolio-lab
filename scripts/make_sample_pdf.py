from __future__ import annotations

from pathlib import Path
import re
import textwrap


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "samples" / "source" / "ai_application_engineer_jd.md"
OUTPUT = ROOT / "samples" / "pdf" / "ai_application_engineer_jd.pdf"


def markdown_to_lines(markdown: str) -> list[str]:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        if not line:
            lines.append("")
            continue

        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"^\-\s+", "- ", line)

        wrapped = textwrap.wrap(line, width=88) or [""]
        lines.extend(wrapped)

    return lines


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(lines: list[str]) -> bytes:
    page_width = 612
    page_height = 792
    left = 54
    top = 740
    line_height = 14
    max_lines = 48

    pages = [lines[i : i + max_lines] for i in range(0, len(lines), max_lines)]
    objects: list[bytes] = []

    def add_object(body: str) -> int:
        objects.append(body.encode("latin-1"))
        return len(objects)

    catalog_id = add_object("<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add_object("PLACEHOLDER")
    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids: list[int] = []

    for page_lines in pages:
        content_parts = ["BT", f"/F1 11 Tf", f"{left} {top} Td"]
        first_line = True
        for line in page_lines:
            if not first_line:
                content_parts.append(f"0 -{line_height} Td")
            first_line = False
            content_parts.append(f"({escape_pdf_text(line)}) Tj")
        content_parts.append("ET")
        stream = "\n".join(content_parts)
        content_id = add_object(
            f"<< /Length {len(stream.encode('latin-1'))} >>\n"
            f"stream\n{stream}\nendstream"
        )
        page_id = add_object(
            "<< /Type /Page "
            "/Parent 2 0 R "
            f"/MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = (
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"
    ).encode("latin-1")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{idx} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("latin-1")
    )
    return bytes(pdf)


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    ascii_markdown = markdown.encode("ascii", errors="ignore").decode("ascii")
    lines = markdown_to_lines(ascii_markdown)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(build_pdf(lines))
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()

