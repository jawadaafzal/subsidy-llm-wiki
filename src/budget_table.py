import re
from pathlib import Path


SOURCE_FILE = Path("raw/pakistan_federal_budget_2026_27.md")


def clean_cell(value):
    value = re.sub(r"<br\s*/?>", " ", value)
    value = value.replace("**", "")
    return " ".join(value.split())


def extract_housing_allocations():
    lines = SOURCE_FILE.read_text(encoding="utf-8").splitlines()

    header_index = next(
        i for i, line in enumerate(lines)
        if "Classification" in line and "2026-27" in line
    )

    allocations = []

    for line_number, line in enumerate(
        lines[header_index + 1:], start=header_index + 2
    ):
        if "TOTAL SUBSIDIES" in line:
            break

        if not line.startswith("|"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]

        if len(cells) < 5:
            continue

        row_number = clean_cell(cells[0])

        if not row_number.isdigit():
            continue

        scheme = clean_cell(cells[1])

        if not re.search(r"housing|ghar", scheme, re.IGNORECASE):
            continue

        amount_text = clean_cell(cells[4])

        amount = (
            int(amount_text.replace(",", ""))
            if amount_text != "-"
            else None
        )

        allocations.append({
            "scheme": scheme,
            "amount_million": amount,
            "source_line": line_number,
        })

    return allocations


if __name__ == "__main__":
    rows = extract_housing_allocations()

    total = sum(
        row["amount_million"] or 0
        for row in rows
    )

    for row in rows:
        print(row)

    print(f"\nTotal listed allocation: Rs. {total:,} million")