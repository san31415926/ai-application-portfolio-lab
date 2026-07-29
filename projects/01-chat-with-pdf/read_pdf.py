from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_PATH = PROJECT_ROOT / "samples" / "pdf" / "ai_application_engineer_jd.pdf"


def read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(pdf_path)
    pages_text: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages_text.append(page_text)

    return "\n".join(pages_text)


def main() -> None:
    text = read_pdf_text(PDF_PATH)

    print(f"PDF 路径：{PDF_PATH}")
    print(f"页数：{len(PdfReader(PDF_PATH).pages)}")
    print(f"字符数：{len(text)}")
    print("-" * 60)
    print(text[:500])


if __name__ == "__main__":
    main()

