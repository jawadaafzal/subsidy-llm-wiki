import json
from pathlib import Path

from src.query import WikiQuery


EVAL_FILE = Path("eval/eval_set.json")


def run_evaluation():
    test_cases = json.loads(
        EVAL_FILE.read_text(encoding="utf-8")
    )

    wiki = WikiQuery()

    passed = 0

    print("\nRETRIEVAL EVALUATION\n")

    for number, test in enumerate(test_cases, start=1):
        results = wiki.search(test["question"], top_k=5)

        retrieved_sources = {
            result["source_id"] for result in results
        }

        expected_source = test["source"]
        success = expected_source in retrieved_sources

        if success:
            passed += 1

        status = "PASS" if success else "FAIL"

        print(f"{number}. {status}")
        print("Question:", test["question"])
        print("Expected source:", expected_source)
        print("Retrieved sources:", ", ".join(retrieved_sources) or "None")
        print()

    total = len(test_cases)
    accuracy = (passed / total) * 100 if total else 0

    print("EVALUATION SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Source retrieval accuracy: {accuracy:.1f}%")


if __name__ == "__main__":
    run_evaluation()