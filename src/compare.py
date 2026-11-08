import frontmatter

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, MODEL_MAIN
from src.query import WikiQuery


DRAFT_PATH = (
    "wiki/drafts/"
    "pakistani_government_subsidies_in_the_fy2026_27_budget.md"
)


def compare_methods(question):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    wiki = WikiQuery()
    results = wiki.search(question, top_k=5)

    if not results:
        print("No RAG evidence found.")
        return

    post = frontmatter.load(DRAFT_PATH)

    if post.metadata.get("status") not in ("reviewed", "published"):
        raise ValueError("Wiki page must be reviewed before comparison.")

    rag_context = "\n\n".join(
        f"Source: {item['source_id']}, "
        f"lines {item['start_line']}-{item['end_line']}\n"
        f"{item['text']}"
        for item in results
    )

    wiki_context = post.content

    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(
            timeout=60000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    try:
        rag_response = client.models.generate_content(
            model=MODEL_MAIN,
            contents=f"""
Answer the question using only this retrieved source evidence.
Include source IDs and line ranges in your answer.
If evidence is insufficient, say so.

Question: {question}

Evidence:
{rag_context}
""",
        )

        wiki_response = client.models.generate_content(
            model=MODEL_MAIN,
            contents=f"""
Answer the question using only this reviewed Wiki page.
Preserve its citations and do not invent facts.
If information is missing, say so.

Question: {question}

Wiki page:
{wiki_context}
""",
        )
    finally:
        client.close()

    print("\n========== RAG ANSWER ==========\n")
    print(rag_response.text or "No answer returned.")

    print("\n========== WIKI ANSWER ==========\n")
    print(wiki_response.text or "No answer returned.")


if __name__ == "__main__":
    question = input("Enter a comparison question: ").strip()

    if question:
        compare_methods(question)