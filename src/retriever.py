import re
from pathlib import Path

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z0-9]+\b", text.lower())



def create_chunks(
    text: str,
    max_chars: int = 4000,
    overlap_lines: int = 10,
) -> list[dict]:
    lines = text.splitlines()
    chunks = []
    start = 0

    while start < len(lines):
        end = start
        current_size = 0

        while end < len(lines):
            line_size = len(lines[end]) + 1

            if current_size + line_size > max_chars and end > start:
                break

            current_size += line_size
            end += 1

        chunks.append({
            "text": "\n".join(lines[start:end]),
            "start_line": start + 1,
            "end_line": end,
        })

        if end >= len(lines):
            break

        start = max(start + 1, end - overlap_lines)

    return chunks


class WikiRetriever:
    def __init__(self, markdown_path: str):
        path = Path(markdown_path)
        text = path.read_text(encoding="utf-8")

        self.chunks = create_chunks(text)

        tokenized_chunks = [
            tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.index = BM25Okapi(tokenized_chunks)

    def search(self, question: str, top_k: int = 3) -> list[dict]:
        query_tokens = tokenize(question)
        scores = self.index.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )

        results = []

        for index, score in ranked[:top_k]:
            if score <= 0:
                continue

            result = self.chunks[index].copy()
            result["score"] = round(float(score), 3)
            results.append(result)

        return results


if __name__ == "__main__":
    retriever = WikiRetriever(
        "raw/pakistan_federal_budget_2026_27.md"
    )

    results = retriever.search(
        "Power Sector WAPDA PEPCO KESC tariff differential subsidy 2026-27",
        top_k=5,
    )

    for result in results:
        print("\nSource lines:", result["start_line"], "-", result["end_line"])
        print("Score:", result["score"])
        print(result["text"])