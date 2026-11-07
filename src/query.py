import json
from pathlib import Path

from rank_bm25 import BM25Okapi

from src.retriever import tokenize


CHUNKS_PATH = Path("raw/processed/all_sources.chunks.json")


class WikiQuery:
    def __init__(self):
        if not CHUNKS_PATH.exists():
            raise FileNotFoundError(
                f"Chunk file not found: {CHUNKS_PATH}. Run ingestion first."
            )

        self.chunks = json.loads(
            CHUNKS_PATH.read_text(encoding="utf-8")
        )

        if not self.chunks:
            raise ValueError("No chunks found. Run ingestion first.")

        tokenized_chunks = [
            tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.index = BM25Okapi(tokenized_chunks)

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        query_tokens = tokenize(question)

        if not query_tokens:
            return []

        scores = self.index.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )

        results = []

        for index, score in ranked:
            if score <= 0:
                continue

            chunk = self.chunks[index]

            results.append({
                "source_id": chunk["source_id"],
                "source_file": chunk["source_file"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "score": round(float(score), 3),
                "text": chunk["text"],
            })

            if len(results) >= top_k:
                break

        return results


def main():
    wiki = WikiQuery()

    question = input("Ask a question about Pakistan's subsidies: ")

    results = wiki.search(question)

    if not results:
        print("\nNo relevant information found.")
        return

    print(f"\nTop {len(results)} results:\n")

    for number, result in enumerate(results, start=1):
        print(f"--- Result {number} ---")
        print(f"Source: {result['source_id']}")
        print(
            f"Lines: {result['start_line']}-{result['end_line']}"
        )
        print(f"BM25 score: {result['score']}")
        print(result["text"][:5000])
        print()


if __name__ == "__main__":
    main()