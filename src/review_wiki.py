import argparse
from datetime import date

from src import wiki_io as W
from src.wiki_lint import run_rules


def get_page(pid):
    if pid.split("/")[0] not in W.LLM_DIRS or not W.page_exists(pid):
        raise SystemExit(f"Not an LLM wiki page: {pid}")
    post = W.load_page(pid)
    return post, dict(post.metadata)


def check_clean(pid):
    issues = [i for i in run_rules() if i[1] == pid and i[0] == "HIGH"]
    if issues:
        for _, _, code, msg in issues:
            print(f"BLOCKED {code}: {msg[:100]}")
        raise SystemExit("Fix the HIGH issues first.")


def list_pages():
    for e in W.index_entries(W.LLM_DIRS):
        print(f"{e['status']:10} | {e['id']} | facts: {e['facts']}")


def approve(pid, comment, reviewer):
    post, meta = get_page(pid)
    if meta.get("status") != "draft":
        raise SystemExit(f"Only draft pages can be approved (status: {meta.get('status')})")
    check_clean(pid)
    meta.update(status="reviewed", last_reviewed=date.today(),
                reviewed_by=reviewer, updated=date.today())
    W.save_page(pid, meta, post.content)
    W.rebuild_index()
    W.append_log("review APPROVED", pid, f"reviewer: {reviewer}\ncomment: {comment}")
    print("Approved:", pid)


def reject(pid, comment, reviewer):
    get_page(pid)
    W.append_log("review REJECTED", pid, f"reviewer: {reviewer}\ncomment: {comment}")
    print("Rejected (stays draft):", pid)


def publish(pid, comment, reviewer):
    post, meta = get_page(pid)
    if meta.get("status") != "reviewed":
        raise SystemExit(f"Only reviewed pages can be published (status: {meta.get('status')})")
    check_clean(pid)
    if input(f"Publish {pid}? Type yes: ").strip().lower() != "yes":
        raise SystemExit("Cancelled.")
    meta.update(status="published", version=int(meta.get("version", 0)) + 1,
                published_on=date.today(), updated=date.today())
    W.save_page(pid, meta, post.content)
    W.rebuild_index()
    W.append_log("PUBLISHED", pid, f"by: {reviewer}\ncomment: {comment}")
    print("Published:", pid)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["list", "approve", "reject", "publish"])
    p.add_argument("page_id", nargs="?")
    p.add_argument("--comment", default="")
    p.add_argument("--reviewer", default="Jawad")
    a = p.parse_args()
    if a.action == "list":
        list_pages()
    else:
        if not a.page_id or not a.comment:
            raise SystemExit("page_id and --comment are required")
        {"approve": approve, "reject": reject, "publish": publish}[a.action](
            a.page_id, a.comment, a.reviewer)