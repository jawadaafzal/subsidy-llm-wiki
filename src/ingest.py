import json
from pathlib import Path

from src.extract import extract_pdf
from src.retriever import create_chunks
from src.wiki_loader import load_wiki_page
from src.wiki_index import get_source_pages, update_index, update_log


RAW_DIR = Path("raw")
WIKI_SOURCES_DIR = Path("wiki/sources")
PROCESSED_DIR = RAW_DIR / "processed"


def ingest_all_sources():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    all_records = []

    wiki_files = sorted(WIKI_SOURCES_DIR.glob("*.md"))

    for wiki_file in wiki_files:
        source_id = wiki_file.stem
        pdf_path = RAW_DIR / f"{source_id}.pdf"
        markdown_path = RAW_DIR / f"{source_id}.md"

        print(f"\nProcessing: {source_id}")

        if not pdf_path.exists():
            print(f"PDF not found, skipping: {pdf_path}")
            continue

        page = load_wiki_page(str(wiki_file))
        print(f"Wiki page validated: {page.title}")

        extract_pdf(str(pdf_path), str(markdown_path))

        markdown = markdown_path.read_text(encoding="utf-8")
        chunks = create_chunks(markdown)

        records = []

        for number, chunk in enumerate(chunks, start=1):
            record = {
                "chunk_id": f"{source_id}_{number}",
                "source_id": source_id,
                "source_file": str(markdown_path),
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "text": chunk["text"],
            }

            records.append(record)

        output_path = PROCESSED_DIR / f"{source_id}.chunks.json"
        output_path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        all_records.extend(records)

        print(f"Chunks created: {len(records)}")
        print(f"Saved: {output_path}")

    master_path = PROCESSED_DIR / "all_sources.chunks.json"
    master_path.write_text(
        json.dumps(all_records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    pages = get_source_pages()
    update_index(pages)
    update_log(pages)

    print("\nIngestion completed.")
    print(f"Total source pages: {len(pages)}")
    print(f"Total chunks: {len(all_records)}")
    print(f"Master file: {master_path}")


if __name__ == "__main__":
    ingest_all_sources()