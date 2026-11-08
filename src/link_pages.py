from src import wiki_io as W
from src.llm import ask_json


def main():
    entries = W.index_entries(W.LLM_DIRS)
    ids = {e["id"] for e in entries}
    listing = "\n".join(
        f'{e["id"]} | {e["title"]} | {e["summary"][:200]}' for e in entries
    )
    prompt = (
        "These are pages of a wiki about Pakistani federal subsidies.\n"
        "Decide which pages are genuinely related (same topic area, one is a part "
        "or a funding stream of the other, or they should be read together).\n"
        "Rules: use only the page ids listed. Every page should get at least one "
        "link if a reasonable partner exists. Do not link everything to everything.\n"
        'Return JSON {"links": [{"from": "id", "to": "id", "reason": "short"}]}.\n\n'
        f"PAGES:\n{listing}"
    )
    data = ask_json(prompt, "You connect wiki pages. Return JSON only.")
    links = data.get("links", []) if isinstance(data, dict) else []

    wanted = {pid: set() for pid in ids}
    for link in links:
        a, b = link.get("from"), link.get("to")
        if a in ids and b in ids and a != b:
            wanted[a].add(b)
            wanted[b].add(a)  # links go both ways

    changed = 0
    for pid, targets in wanted.items():
        post = W.load_page(pid)
        meta = dict(post.metadata)
        current = list(meta.get("related") or [])
        merged = list(dict.fromkeys(current + sorted(targets)))
        if merged == current:
            continue
        meta["related"] = merged
        W.save_page(pid, meta, W.render_body(
            meta,
            W.get_section(post.content, "Summary"),
            W.get_section(post.content, "Main Content"),
        ))
        changed += 1
        print(f"linked {pid} -> {len(merged)} related")

    W.rebuild_index()
    W.append_log("link", "wiki", f"pages with new links: {changed}")
    print("Done. Pages changed:", changed)


if __name__ == "__main__":
    main()