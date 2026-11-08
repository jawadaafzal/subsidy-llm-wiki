import json
import re
from datetime import date
from pathlib import Path

import frontmatter
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, MODEL_MAIN
from src.query import WikiQuery
from src.schema import WikiPage
from src.budget_table import extract_housing_allocations


DRAFT_DIR = Path("wiki/drafts")


def generate_draft(question: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    wiki = WikiQuery()
    results = wiki.search(question, top_k=5)
    housing_rows = extract_housing_allocations()

    housing_total = sum(
        row["amount_million"] or 0
        for row in housing_rows
    )

    housing_context = "\n".join(
        f"- {row['scheme']}: "
        f"{row['amount_million'] if row['amount_million'] is not None else 'No amount listed'} "
        f"(source line {row['source_line']})"
        for row in housing_rows
    )

    housing_context += (
        f"\nVerified combined total: Rs. {housing_total:,} million."
    )

    if not results:
        print("No relevant evidence found.")
        return

    context = "\n\n".join(
        f"SOURCE: {item['source_id']}\n"
        f"LINES: {item['start_line']}-{item['end_line']}\n"
        f"CONTENT:\n{item['text']}"
        for item in results
    )

    prompt = f"""
You are a careful research assistant creating a draft Wiki page
about Pakistani government subsidies.
VERIFIED HOUSING TABLE DATA:
{housing_context}

For housing allocation questions, use these pre-calculated figures.
Do not recalculate from historical-year columns.
Use ONLY the supplied source evidence.

Rules:
- Do not invent facts, figures, dates, or sources.
- Every factual claim must be supported by the supplied evidence.
- Identify the financial year requested by the user.
- If the user does not specify a year, use the latest budget year available.
- When a table contains multiple financial-year columns, use ONLY the column for the requested year.
- Never mix previous-year budget allocations or revised estimates with the requested year's budget.
- Treat a dash (-) as "no amount listed", not automatically as zero.
- When asked for a total, add only relevant allocations from the requested financial-year column.
- Show the individual amounts and explain the calculation.
- Distinguish budget allocations from actual payments.
- If evidence is insufficient or ambiguous, clearly say so.
- Include source IDs and precise line ranges for every factual claim.
- Return valid JSON only. Do not use Markdown code fences.

Return exactly these fields:
{{
  "title": "Page title",
  "summary": "Short summary",
  "main_content": "Detailed explanation with inline source references",
  "key_facts": ["Fact with source reference"],
  "evidence": ["source_id, lines X-Y: supporting evidence"],
  "related_pages": []
}}

USER QUESTION:
{question}

SOURCE EVIDENCE:
{context}
"""

    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(
            timeout=60000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    try:
        response = client.models.generate_content(
            model=MODEL_MAIN,
            contents=prompt,
        )
    finally:
        client.close()

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    text = response.text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    generated = json.loads(text)

    source_ids = sorted({
        item["source_id"] for item in results
    })

    page_data = {
        **generated,
        "page_type": "draft",
        "status": "draft",
        "created": date.today(),
        "updated": date.today(),
        "sources": source_ids,
    }

    page = WikiPage(**page_data)

    post = frontmatter.Post(
        f"# Summary\n\n{page.summary}\n\n"
        f"# Main Content\n\n{page.main_content}\n\n"
        f"# Key Facts\n\n"
        + "\n".join(f"- {fact}" for fact in page.key_facts)
        + "\n\n# Sources and Evidence\n\n"
        + "\n".join(f"- {item}" for item in page.evidence)
        + "\n\n# Related Pages\n\n"
        + (
            "\n".join(f"- {item}" for item in page.related_pages)
            if page.related_pages else "None yet"
        ),
        **page.model_dump(),
    )

    DRAFT_DIR.mkdir(parents=True, exist_ok=True)

    slug = re.sub(
        r"[^a-z0-9]+", "_", page.title.lower()
    ).strip("_")

    output_path = DRAFT_DIR / f"{slug}.md"
    output_path.write_text(
        frontmatter.dumps(post),
        encoding="utf-8",
    )

    print("\nDraft generated and validated.")
    print("Title:", page.title)
    print("Sources:", ", ".join(page.sources))
    print("Saved:", output_path)


if __name__ == "__main__":
    question = input("What Wiki page should I create? ")
    generate_draft(question)