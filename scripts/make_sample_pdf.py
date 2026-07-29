from __future__ import annotations

from pathlib import Path
import re

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "samples" / "source" / "ai_application_engineer_jd.md"
OUTPUT = ROOT / "samples" / "pdf" / "ai_application_engineer_jd.pdf"


FONT_NAME = "STSong-Light"
FONT_SIZE = 11
MAX_LINE_WIDTH = letter[0] - 108


def wrap_line(line: str) -> list[str]:
    if not line:
        return [""]

    wrapped: list[str] = []
    current = ""
    for character in line:
        candidate = current + character
        if current and pdfmetrics.stringWidth(candidate, FONT_NAME, FONT_SIZE) > MAX_LINE_WIDTH:
            wrapped.append(current)
            current = character
        else:
            current = candidate
    if current:
        wrapped.append(current)
    return wrapped


def markdown_to_lines(markdown: str) -> list[str]:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        if not line:
            lines.append("")
            continue

        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"^\-\s+", "- ", line)

        lines.extend(wrap_line(line))

    return lines


def build_pdf(lines: list[str], output: Path) -> None:
    page_width, page_height = letter
    left = 54
    top = page_height - 52
    bottom = 52
    line_height = 14

    canvas = Canvas(str(output), pagesize=letter)
    canvas.setTitle("AI 应用工程师岗位说明")
    canvas.setAuthor("LearningHub 示例素材")
    canvas.setFont(FONT_NAME, FONT_SIZE)
    y = top
    for line in lines:
        if y < bottom:
            canvas.showPage()
            canvas.setFont(FONT_NAME, FONT_SIZE)
            y = top
        canvas.drawString(left, y, line)
        y -= line_height
    canvas.save()


def main() -> None:
    pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))
    markdown = SOURCE.read_text(encoding="utf-8")
    lines = markdown_to_lines(markdown)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(lines, OUTPUT)
    print(f"已生成：{OUTPUT}")


if __name__ == "__main__":
    main()

