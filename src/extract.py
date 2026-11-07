from pathlib import Path
import pymupdf4llm


def extract_pdf(pdf_path: str, output_path: str):
    pdf = Path(pdf_path)
    output = Path(output_path)

    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found: {pdf}")

    markdown = pymupdf4llm.to_markdown(str(pdf))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")

    print(f"Extraction complete: {output}")
    print(f"Characters extracted: {len(markdown)}")


if __name__ == "__main__":
    extract_pdf(
        "raw/pakistan_federal_budget_2026_27.pdf",
        "raw/pakistan_federal_budget_2026_27.md",
    )
