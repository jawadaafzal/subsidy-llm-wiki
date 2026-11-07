import re
import frontmatter

from src.schema import WikiPage


def get_section(content: str, heading: str) -> str:
    pattern = rf"^# {re.escape(heading)}\s*$"
    match = re.search(pattern, content, re.MULTILINE)

    if not match:
        return ""

    remaining = content[match.end():]
    next_heading = re.search(r"^# ", remaining, re.MULTILINE)

    if next_heading:
        remaining = remaining[:next_heading.start()]

    return remaining.strip()


def get_bullet_items(content: str) -> list[str]:
    return [
        line.strip()[2:].strip()
        for line in content.splitlines()
        if line.strip().startswith("- ")
    ]


def load_wiki_page(file_path: str) -> WikiPage:
    post = frontmatter.load(file_path)
    content = post.content

    data = dict(post.metadata)

    data["summary"] = get_section(content, "Summary")
    data["main_content"] = get_section(content, "Main Content")
    data["key_facts"] = get_bullet_items(
        get_section(content, "Key Facts")
    )
    data["evidence"] = get_bullet_items(
        get_section(content, "Sources and Evidence")
    )
    data["related_pages"] = get_bullet_items(
        get_section(content, "Related Pages")
    )

    data["related_pages"] = [
        item for item in data["related_pages"]
        if item.lower() not in ("none", "none yet")
    ]

    return WikiPage(**data)


if __name__ == "__main__":
    page = load_wiki_page(
        "wiki/sources/pakistan_federal_budget_2026_27.md"
    )

    print("Wiki page loaded and validated")
    print("Title:", page.title)
    print("Type:", page.page_type)
    print("Facts:", len(page.key_facts))
    print("Evidence references:", len(page.evidence))