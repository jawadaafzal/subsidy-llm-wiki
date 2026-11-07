
from pathlib import Path
from datetime import datetime, timezone
import frontmatter


WIKI_DIR = Path("wiki")
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"


def get_source_pages():
    pages = []

    for file_path in (WIKI_DIR / "sources").glob("*.md"):
        post = frontmatter.load(file_path)

        pages.append({
            "title": post.metadata.get("title", file_path.stem),
            "page_type": post.metadata.get("page_type", "unknown"),
            "status": post.metadata.get("status", "draft"),
            "path": file_path.as_posix(),
            "sources": post.metadata.get("sources", []),
        })

    return pages


def update_index(pages):
    lines = [
        "# Wiki Index",
        "",
        f"Last updated: {datetime.now().date()}",
        "",
        "## Source Pages",
        "",
    ]

    for page in pages:
        lines.extend([
            f"### {page['title']}",
            f"- Type: {page['page_type']}",
            f"- Status: {page['status']}",
            f"- Path: `{page['path']}`",
            f"- Source IDs: {', '.join(page['sources']) or 'Not assigned'}",
            "",
        ])

    INDEX_FILE.write_text("\n".join(lines), encoding="utf-8")


def update_log(pages):
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    if not LOG_FILE.exists() or not LOG_FILE.read_text(
        encoding="utf-8"
    ).strip():
        LOG_FILE.write_text(
            "# Wiki Activity Log\n\n",
            encoding="utf-8",
        )

    entry = (
        f"## Ingestion Run — {timestamp}\n\n"
        f"- Source pages found: {len(pages)}\n"
        "- Action: Index refreshed\n"
        "- Status: Successful\n\n"
    )

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(entry)


def main():
    pages = get_source_pages()

    update_index(pages)
    update_log(pages)

    print(f"Source pages indexed: {len(pages)}")
    print(f"Index updated: {INDEX_FILE}")
    print(f"Activity log updated: {LOG_FILE}")


if __name__ == "__main__":
    main()
