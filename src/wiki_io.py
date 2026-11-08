import re
from datetime import datetime, timezone
from pathlib import Path

import frontmatter

WIKI = Path("wiki")
RAW = Path("raw")
PAGE_DIRS = ["sources", "concepts", "entities", "drafts", "published"]
LLM_DIRS = ["concepts", "entities"]


# ---------- pages ----------

def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:80] or "untitled"


def page_path(pid):
    return WIKI / f"{pid}.md"


def page_exists(pid):
    return page_path(pid).exists()


def all_page_ids(dirs=None):
    ids = []
    for d in dirs or PAGE_DIRS:
        folder = WIKI / d
        if folder.exists():
            for p in sorted(folder.glob("*.md")):
                ids.append(f"{d}/{p.stem}")
    return ids


def load_page(pid):
    return frontmatter.load(page_path(pid))


def save_page(pid, meta, body):
    path = page_path(pid)
    path.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(body, **meta)
    path.write_text(frontmatter.dumps(post), encoding="utf-8")


def get_section(body, name):
    pattern = rf"^##\s+{re.escape(name)}\s*\n(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, body, re.S | re.M)
    return match.group(1).strip() if match else ""


def render_body(meta, summary, main_content):
    facts = meta.get("facts") or []
    out = [
        "## Summary", "", (summary or "").strip() or "Pending.", "",
        "## Main Content", "", (main_content or "").strip() or "Pending.", "",
        "## Key Facts", "",
    ]
    for f in facts:
        out.append(f"- {f['fact']} [{f['source_id']}:{f['lines']}]")
    out += ["", "## Sources and Evidence", ""]
    for f in facts:
        out.append(f"- [{f['source_id']}:{f['lines']}] \"{f['quote']}\"")
    out += ["", "## Related Pages", ""]
    for r in meta.get("related") or []:
        out.append(f"- [[{r}]]")
    conflicts = meta.get("conflicts") or []
    if conflicts:
        out += ["", "## Open Conflicts", ""]
        for c in conflicts:
            out.append(
                f"- Existing: {c.get('existing_fact', '')} | "
                f"New: {c.get('new_fact', '')} | {c.get('explanation', '')}"
            )
    return "\n".join(out) + "\n"


# ---------- index and log ----------

def index_entries(dirs=None):
    entries = []
    for pid in all_page_ids(dirs):
        post = load_page(pid)
        meta = post.metadata
        summary_lines = get_section(post.content, "Summary").splitlines()
        summary = summary_lines[0] if summary_lines else str(meta.get("summary", ""))
        entries.append({
            "id": pid,
            "title": meta.get("title", pid),
            "status": meta.get("status", "?"),
            "facts": len(meta.get("facts") or []),
            "summary": summary.strip(),
        })
    return entries


def rebuild_index():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Wiki Index", "",
        f"Auto-generated. Last rebuilt: {now}", "",
        "Page IDs are used as citations, for example [[concepts/power_subsidy]].", "",
    ]
    for d in PAGE_DIRS:
        entries = index_entries([d])
        if not entries:
            continue
        lines += [f"## {d.capitalize()}", ""]
        for e in entries:
            lines.append(
                f"- [[{e['id']}]] | {e['title']} | status: {e['status']} "
                f"| facts: {e['facts']} | {e['summary'][:150]}"
            )
        lines.append("")
    (WIKI / "index.md").write_text("\n".join(lines), encoding="utf-8")


def append_log(action, title, detail=""):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n## [{now}] {action} | {title}\n{detail}\n"
    with open(WIKI / "log.md", "a", encoding="utf-8") as f:
        f.write(entry)


# ---------- evidence checking ----------

def norm(text):
    """Compact form: lowercase, drop <br>, keep only letters, digits . , %"""
    text = text.lower().replace("<br>", "")
    return re.sub(r"[^a-z0-9.,%]+", "", text)


def nums(text):
    """Significant numbers in text (years and tiny numbers ignored)."""
    out = set()
    for m in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        m = m.rstrip(",")
        t = m.replace(",", "")
        digits = t.replace(".", "")
        if len(t) == 4 and t.isdigit() and 1900 <= int(t) <= 2100:
            continue
        if len(digits) >= 3 or "," in m or "." in m:
            out.add(t)
    return out


def load_source_lines(source_id):
    path = RAW / f"{source_id}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").splitlines()


def locate(quote, norm_lines, max_span=8):
    """Find the quote in the source. Returns 'start-end' line range or None."""
    q = norm(quote)
    if len(q) < 8:
        return None
    n = len(norm_lines)
    for span in range(1, max_span + 1):
        for i in range(n - span + 1):
            chunk = norm_lines[i] if span == 1 else "".join(norm_lines[i:i + span])
            if q in chunk:
                return f"{i + 1}-{i + span}"
    return None