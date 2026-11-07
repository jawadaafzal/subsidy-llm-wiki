
import json
from pathlib import Path

from src.extract import extract_pdf
from src.retriever import create_chunks
from src.wiki_loader import load_wiki_page
from src.wiki_index import get_source_pages, update_index, update_log

PDF_PATH = "raw/pakistan_federal_budget_2026_27.pdf"
MARKDOWN_PATH = "raw/pakistan_federal_budget_2026_27.md"
WIKI_PATH = "wiki/sources/pakistan_federal_budget_2026_27.md"
OUTPUT_PATH = "raw/processed/pakistan_federal_budget_2026_27.chunks.json"


def ingest_source():
    # 1. Check source PDF
    if not Path(PDF_PATH).exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    # 2. Extract PDF into Markdown
    extract_pdf(PDF_PATH, MARKDOWN_PATH)

    # 3. Validate existing Wiki page
    if not Path(WIKI_PATH).exists():
        raise FileNotFoundError(f"Wiki page not found: {WIKI_PATH}")

    page = load_wiki_page(WIKI_PATH)
    print(f"Wiki page validated: {page.title}")

    # 4. Read extracted Markdown
    markdown = Path(MARKDOWN_PATH).read_text(encoding="utf-8")

    # 5. Create overlapping chunks
    chunks = create_chunks(markdown)

    # 6. Save chunks with source references
    output = Path(OUTPUT_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)

    records = []

    for number, chunk in enumerate(chunks, start=1):
        records.append({
            "chunk_id": number,
            "source_id": "pakistan_federal_budget_2026_27",
            "source_file": MARKDOWN_PATH,
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "text": chunk["text"],
        })

    output.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Chunks created: {len(records)}")
    print(f"Chunk data saved: {output}")
    print("Ingestion completed successfully.")

    pages = get_source_pages()
    update_index(pages)
    update_log(pages)

if __name__ == "__main__":
    ingest_source()
