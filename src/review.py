from datetime import datetime, timezone
from pathlib import Path

import frontmatter

from src.wiki_loader import load_wiki_page


LOG_FILE = Path("wiki/log.md")


def review_draft(draft_path: str):
    path = Path(draft_path)

    if not path.exists():
        raise FileNotFoundError(f"Draft not found: {path}")

    page = load_wiki_page(str(path))

    if page.status != "draft":
        print(f"This page is already marked as: {page.status}")
        return

    print("\nDRAFT REVIEW")
    print("Title:", page.title)
    print("Summary:", page.summary)
    print("\nKey facts:")

    for fact in page.key_facts:
        print("-", fact)

    print("\nSources:", ", ".join(page.sources))

    decision = input("\nDecision (approve/reject): ").strip().lower()

    if decision not in ("approve", "reject"):
        print("Invalid decision. No changes made.")
        return

    comment = input("Reviewer comment: ").strip()

    post = frontmatter.load(path)

    if decision == "approve":
        post.metadata["status"] = "reviewed"
        result = "APPROVED"
    else:
        post.metadata["status"] = "draft"
        result = "REJECTED — remains a draft"

    path.write_text(
        frontmatter.dumps(post),
        encoding="utf-8",
    )

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    log_entry = (
        f"## Review — {timestamp}\n\n"
        f"- Page: {page.title}\n"
        f"- Decision: {result}\n"
        f"- Comment: {comment or 'No comment'}\n\n"
    )

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(log_entry)

    print(f"\nReview recorded: {result}")
    print("Page:", path)


if __name__ == "__main__":
    review_draft(
        "wiki/drafts/pakistani_government_subsidies_in_the_fy2026_27_budget.md"
    )