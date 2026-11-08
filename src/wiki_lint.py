import argparse
import re
from datetime import date, datetime
from pathlib import Path

from src import wiki_io as W
from src.llm import ask_json


def run_rules():
    issues = []
    ids = W.all_page_ids()
    idset = set(ids)
    inbound = {i: 0 for i in ids}
    norm_cache = {}

    def source_lines(sid):
        if sid not in norm_cache:
            lines = W.load_source_lines(sid)
            norm_cache[sid] = None if lines is None else [W.norm(x) for x in lines]
        return norm_cache[sid]

    for pid in ids:
        post = W.load_page(pid)
        meta = post.metadata
        links = set(meta.get("related") or []) | set(re.findall(r"\[\[([^\]]+)\]\]", post.content))
        for link in links:
            if link not in idset:
                issues.append(("MEDIUM", pid, "BROKEN_LINK", f"links to missing page: {link}"))
            elif link != pid:
                inbound[link] += 1

        is_llm_page = pid.split("/")[0] in W.LLM_DIRS
        facts = meta.get("facts") or []
        if is_llm_page and not facts:
            issues.append(("MEDIUM", pid, "EMPTY_PAGE", "page has no verified facts"))

        for f in facts:
            nl = source_lines(f.get("source_id", ""))
            if nl is None:
                issues.append(("HIGH", pid, "SOURCE_MISSING",
                               f"raw/{f.get('source_id')}.md not found for: {f['fact'][:80]}"))
            elif W.locate(f["quote"], nl) is None:
                issues.append(("HIGH", pid, "QUOTE_NOT_FOUND", f["fact"][:100]))
            elif not W.nums(f["fact"]) <= W.nums(f["quote"]):
                issues.append(("HIGH", pid, "FIGURE_MISMATCH", f["fact"][:100]))

        vu = meta.get("valid_until")
        if vu:
            try:
                if datetime.strptime(str(vu), "%Y-%m-%d").date() < date.today():
                    issues.append(("HIGH", pid, "OUTDATED", f"valid_until {vu} has passed"))
            except ValueError:
                issues.append(("LOW", pid, "BAD_DATE", f"invalid valid_until: {vu}"))

        for c in meta.get("conflicts") or []:
            issues.append(("HIGH", pid, "CONFLICT",
                           f"{c.get('existing_fact', '')[:80]} VS {c.get('new_fact', '')[:80]}"))

        if is_llm_page and meta.get("status") == "draft":
            issues.append(("INFO", pid, "PENDING_REVIEW", "status is draft"))

    for pid, count in inbound.items():
        if pid.split("/")[0] in W.LLM_DIRS and count == 0:
            issues.append(("LOW", pid, "ORPHAN", "no other page links here"))
    return issues


def llm_scan():
    items = []
    for pid in W.all_page_ids(W.LLM_DIRS):
        for f in W.load_page(pid).metadata.get("facts") or []:
            items.append((pid, f["fact"]))
    issues, seen = [], set()
    size, step = 80, 50
    start = 0
    while start < len(items):
        batch = items[start:start + size]
        listing = "\n".join(f"F{start + i} | {pid} | {fact}" for i, (pid, fact) in enumerate(batch))
        prompt = (
            "Find real contradictions between these wiki facts: different values or "
            "dates for the SAME item and the SAME period. Ignore facts that are merely "
            "different. Return JSON "
            '{"contradictions": [{"a": "F1", "b": "F7", "explanation": "..."}]}. '
            f"Empty list if none.\n\n{listing}"
        )
        data = ask_json(prompt, "You check a knowledge base for contradictions. Return JSON only.")
        for c in (data.get("contradictions", []) if isinstance(data, dict) else []):
            try:
                a, b = int(str(c["a"])[1:]), int(str(c["b"])[1:])
                key = tuple(sorted((a, b)))
                if key in seen:
                    continue
                seen.add(key)
                issues.append(("HIGH", items[a][0], "LLM_CONFLICT",
                               f"{items[a][1][:80]} VS ({items[b][0]}) {items[b][1][:80]} | {c.get('explanation', '')}"))
            except (KeyError, ValueError, IndexError):
                continue
        start += step
        if start + 30 >= len(items):
            break
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="also run LLM contradiction scan")
    args = parser.parse_args()

    issues = run_rules()
    if args.llm:
        issues += llm_scan()

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
    issues.sort(key=lambda x: order[x[0]])

    lines = ["# Wiki Lint Report", "", f"Date: {date.today()}", ""]
    counts = {}
    for sev, pid, code, msg in issues:
        counts[sev] = counts.get(sev, 0) + 1
        lines.append(f"- **{sev}** | {code} | {pid} | {msg}")
    lines.insert(3, "Counts: " + ", ".join(f"{k}={v}" for k, v in counts.items()) + "\n")

    Path("docs").mkdir(exist_ok=True)
    Path("docs/lint_report.md").write_text("\n".join(lines), encoding="utf-8")

    for sev, pid, code, msg in issues:
        print(f"{sev:6} | {code:15} | {pid} | {msg[:120]}")
    print("\nCounts:", counts or "no issues")
    print("Report saved: docs/lint_report.md")
    W.append_log("lint", "wiki", f"issues: {counts}")


if __name__ == "__main__":
    main()