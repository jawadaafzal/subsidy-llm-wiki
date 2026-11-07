import re
from pathlib import Path

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def create_chunks(text: str, max_chars: int = 2500) -> list[dict]:
    lines = text.splitlines()
    chunks = []
    current_lines = []
    start_line = 1
    current_size = 0

    for line_number, line in enumerate(lines, start=1):
        if current_size + len(line) > max_chars and current_lines:
            chunks.append({
                "text": "\n".join(current_lines),
                "start_line": start_line,
                "end_line": line_number - 1,
            })
            current_lines = []
            current_size = 0
            start_line = line_number

        current_lines.append(line)
        current_size += len(line) + 1

    if current_lines:
        chunks.append({
            "text": "\n".join(current_lines),
            "start_line": start_line,
            "end_line": len(lines),
        })

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