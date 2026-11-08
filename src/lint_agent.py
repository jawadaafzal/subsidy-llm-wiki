
import json
import re
from pathlib import Path

import frontmatter
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, MODEL_MAIN
from src.query import WikiQuery
from src.wiki_loader import get_section, get_bullet_items
from src.budget_table import extract_housing_allocations, SOURCE_FILE


DRAFT_PATH = (
    "wiki/drafts/"
    "pakistani_government_subsidies_for_housing_schemes_in_fy_2026_27.md"
)


def extract_claims(content):
    """Extract complete factual claims from Wiki sections."""

    claims = []

    # Collect key facts
    key_facts = get_bullet_items(
        get_section(content, "Key Facts")
    )

    claims.extend(
        fact for fact in key_facts
        if fact.endswith((".", "!", "?"))
    )

    main_content = get_section(content, "Main Content")

    paragraphs = []
    current_lines = []

    for line in main_content.splitlines():
        line = line.strip()

        if not line or line.startswith(("-", "*", "#")):
            if current_lines:
                paragraphs.append(" ".join(current_lines))
                current_lines = []
            continue

        current_lines.append(line)

    if current_lines:
        paragraphs.append(" ".join(current_lines))

    for paragraph in paragraphs:
        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z])",
            paragraph,
        )

        for sentence in sentences:
            sentence = sentence.strip()

            # Ignore incomplete fragments and headings
            if (
                len(sentence) > 25
                and sentence.endswith((".", "!", "?"))
            ):
                claims.append(sentence)

    return list(dict.fromkeys(claims))



def lint_draft(draft_path: str):
    path = Path(draft_path)

    if not path.exists():
        raise FileNotFoundError(f"Draft not found: {path}")

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    post = frontmatter.load(path)
    claims = extract_claims(post.content)

    if not claims:
        print("No factual claims found in the draft.")
        return

    wiki = WikiQuery()

    claim_evidence = []

    print(f"\nChecking {len(claims)} factual claims...\n")

    for number, claim in enumerate(claims, start=1):
        results = wiki.search(claim, top_k=3)

        evidence = []

        for item in results:
            evidence.append({
                "source_id": item["source_id"],
                "start_line": item["start_line"],
                "end_line": item["end_line"],
                "text": item["text"],
            })

        claim_evidence.append({
            "claim_id": number,
            "claim": claim,
            "evidence": evidence,
        })

    prompt = f"""
You are a strict claim-level fact-checking agent.

Check every claim independently against its retrieved official evidence.

For each claim, assign exactly one status:

SUPPORTED:
The supplied evidence directly states or clearly supports the claim.

DERIVED:
The source provides the necessary individual figures, and the claim
is a correct mathematical calculation from those figures.
Show the calculation in the explanation. Verify every input figure
and its financial-year column against the evidence.

UNSUPPORTED:
The evidence does not provide sufficient support, and the claim
cannot be verified as a valid calculation from the evidence.

CONTRADICTED:
The evidence directly conflicts with the claim.

UNCLEAR:
The evidence is incomplete, ambiguous, or insufficient to decide.   

Rules:
- Never assume a claim is true.
- Check figures, financial years and units carefully.
- Distinguish budget allocations from actual payments.
- Do not invent source IDs, line numbers or citations.
- Only cite evidence supplied for that specific claim.
- If no evidence is supplied, use UNCLEAR.
- Explain the reason for each decision.
- A calculated total does not need to be explicitly printed in the source to qualify as DERIVED.
- Never classify a calculated total as SUPPORTED if the source only lists its individual components.
- Verify arithmetic and units before assigning DERIVED.
Return valid JSON only, using this structure:

{{
  "claim_results": [
    {{
      "claim_id": 1,
      "claim": "Original claim",
      "status": "SUPPORTED",
      "explanation": "Reason for the decision",
      "citations": [
        {{
          "source_id": "source ID",
          "lines": "start-end"
        }}
      ]
    }}
  ],
  "summary": "Overall assessment"
}}

Check every claim. Do not omit any claim.

CLAIMS AND THEIR RETRIEVED EVIDENCE:

{json.dumps(claim_evidence, indent=2, ensure_ascii=False)}
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

    output = response.text.strip()
    output = re.sub(r"^```(?:json)?\s*", "", output)
    output = re.sub(r"\s*```$", "", output)

    report = json.loads(output)

    results = report.get("claim_results", [])

    valid_statuses = {
        "SUPPORTED",
        "DERIVED",
        "UNSUPPORTED",
        "CONTRADICTED",
        "UNCLEAR",
    }

    if len(results) != len(claims):
        raise ValueError(
            "Lint agent did not return a result for every claim."
        )

    for result in results:
        if result.get("status") not in valid_statuses:
            raise ValueError("Invalid claim status returned by Gemini.")
            # Deterministically verify calculated housing totals.
    housing_rows = extract_housing_allocations()

    housing_total = sum(
        row["amount_million"] or 0
        for row in housing_rows
    )

    housing_lines = [
        row["source_line"]
        for row in housing_rows
        if row["amount_million"] is not None
    ]

    for result in results:
        claim = result["claim"].lower()

        if (
            "housing" in claim
            and "combined total" in claim
            and f"{housing_total:,}" in claim
        ):
            result["status"] = "DERIVED"

            result["explanation"] = (
                f"Python verified the total using the FY 2026-27 "
                f"housing allocations. Calculation: "
                f"{' + '.join(str(row['amount_million']) for row in housing_rows if row['amount_million'] is not None)} "
                f"= {housing_total:,} million."
            )

            result["citations"] = [{
                "source_id": SOURCE_FILE.stem,
                "lines": (
                    f"{min(housing_lines)}-{max(housing_lines)}"
                ),
            }]

    accepted_statuses = {"SUPPORTED", "DERIVED"}

    all_accepted = all(
        result["status"] in accepted_statuses
        for result in results
    )

    has_derived = any(
        result["status"] == "DERIVED"
        for result in results
    )

    if not all_accepted:
        overall_status = "NEEDS_REVIEW"
    elif has_derived:
        overall_status = "PASS_WITH_DERIVED_CLAIMS"
    else:
        overall_status = "PASS"

    print("\n========== CLAIM-LEVEL LINT REPORT ==========\n")

    for result in results:
        print(f"Claim {result['claim_id']}: {result['status']}")
        print("Claim:", result["claim"])
        print("Explanation:", result["explanation"])

        citations = result.get("citations", [])

        if citations:
            for citation in citations:
                print(
                    "Citation:",
                    citation["source_id"],
                    "| Lines:",
                    citation["lines"],
                )
        else:
            print("Citation: None provided")

        print()

    print("OVERALL STATUS:", overall_status)
    print("SUMMARY:", report.get("summary", ""))

    report["overall_status"] = overall_status

    return report


if __name__ == "__main__":
    lint_draft(DRAFT_PATH)
