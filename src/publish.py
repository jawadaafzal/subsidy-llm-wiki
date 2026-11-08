
from datetime import datetime, timezone
from pathlib import Path

import frontmatter

from src.wiki_loader import load_wiki_page


LOG_FILE = Path("wiki/log.md")
PUBLISHED_DIR = Path("wiki/published")


def publish_page(draft_path: str):
    path = Path(draft_path)

    if not path.exists():
        raise FileNotFoundError(f"Page not found: {path}")

    page = load_wiki_page(str(path))

    if page.status != "reviewed":
        print(f"Cannot publish. Current status: {page.status}")
        print("Only reviewed pages can be published.")
        return

    destination = PUBLISHED_DIR / path.name

    if destination.exists():
        print(f"A page with this filename already exists: {destination}")
        return

    print("\nPUBLISH PAGE")
    print("Title:", page.title)

    decision = input("\nPublish this page? (yes/no): ").strip().lower()

    if decision != "yes":
        print("Publishing cancelled.")
        return

    comment = input("Publisher comment: ").strip()

    post = frontmatter.load(path)
    post.metadata["status"] = "published"

    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    destination.write_text(
        frontmatter.dumps(post),
        encoding="utf-8",
    )

    path.unlink()

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    log_entry = (
        f"## Publish — {timestamp}\n\n"
        f"- Page: {page.title}\n"
        f"- Status: PUBLISHED\n"
        f"- Location: {destination}\n"
        f"- Comment: {comment or 'No comment'}\n\n"
    )

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(log_entry)

    print("\nPage successfully published!")
    print("New location:", destination)


if __name__ == "__main__":
    publish_page(
        "wiki/drafts/pakistani_government_subsidies_in_the_federal_budget.md"
    )
