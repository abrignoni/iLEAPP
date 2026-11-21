"""Local delivery and fixture context for the iLEAPP review pilot. See pr_review_pilot.md."""
import argparse
import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path
from urllib.parse import quote

import check_pr_test_data as fixtures


REPO = "repos/abrignoni/iLEAPP"
OWNER = 28718987  # abrignoni's immutable GitHub account ID
STATE = Path.home() / "Library/Application Support/iLEAPP/PR Review"


def api(path, *, pages=False, body=None, raw=False):
    args = ["gh", "api", path]
    if pages:
        args.extend(["--paginate", "--slurp"])
    if raw:
        args.extend(["-H", "Accept: application/vnd.github.raw+json"])
    if body is not None:
        args.extend(["--method", "POST", "--input", "-"])
    response = subprocess.run(args, input=json.dumps(body) if body is not None else None,
                              capture_output=True, text=True, check=True).stdout
    if raw:
        return response
    data = json.loads(response)
    return [item for page in data for item in page] if pages else data


def revision(pr):
    return pr["head"]["sha"]


def route(pr):
    author = pr["user"]
    if not isinstance(author.get("id"), int) or not author.get("login"):
        raise ValueError("PR author could not be verified")
    if author["id"] == OWNER or author["login"].casefold() == "abrignoni":
        return "private"
    return "contributor"


def get_pr(number):
    pr = api(f"{REPO}/pulls/{number}")
    if pr["base"]["repo"]["full_name"].casefold() != "abrignoni/ileapp":
        raise ValueError("Unexpected PR base")
    return pr


def context(number):
    pr = get_pr(number)
    files = api(f"{REPO}/pulls/{number}/files?per_page=100", pages=True)
    if len(files) != pr["changed_files"]:
        raise ValueError("Incomplete changed-file list")
    modules = fixtures.artifact_modules(files)
    touched = fixtures.covered_modules(files, modules)
    refs = {}
    manifest = set()
    if modules.keys() - touched:
        data = api(f"{REPO}/contents/admin/image_manifest.json?ref={pr['base']['sha']}", raw=True)
        for entry in json.loads(data)["images"]:
            manifest.update((entry.get("image_name"), entry.get("sample_data_key")))
    for module in modules.keys() - touched:
        path = quote(f"scripts/artifacts/{module}.py")
        data = api(f"{REPO}/contents/{path}?ref={revision(pr)}", raw=True)
        refs[module] = fixtures.sample_data_keys_from_source(data)
    maintainer, contributor = fixtures.classify(modules, touched, refs, manifest)
    if revision(get_pr(number)) != revision(pr):
        raise ValueError("PR changed while reading fixture context")
    return {"number": number, "head": revision(pr), "delivery": route(pr),
            "test_files_touched": sorted(touched), "manifest_matches": maintainer,
            "fixture_bot_would_ask": contributor,
            "changed_paths": [f["filename"] for f in files]}


def database():
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    db = sqlite3.connect(STATE / "reviews.sqlite3", timeout=60)
    db.execute("CREATE TABLE IF NOT EXISTS reviews "
               "(pr INTEGER, head TEXT, result TEXT, PRIMARY KEY (pr, head))")
    return db


def queue(db):
    prs = api(f"{REPO}/pulls?state=open&per_page=100", pages=True)
    return [{"number": p["number"], "head": revision(p), "delivery": route(p)}
            for p in prs if not p["draft"] and not db.execute(
                "SELECT 1 FROM reviews WHERE pr=? AND head=?", (p["number"], revision(p))).fetchone()]


def checked_pr(number, head):
    pr = get_pr(number)
    if pr["state"] != "open" or pr["draft"] or revision(pr) != head:
        raise ValueError("PR closed, in draft, or superseded")
    return pr


def finish(db, number, head, summary, comments):
    if not summary.strip() or not isinstance(comments, list):
        raise ValueError("Expected a private summary and an inline comment list")
    with db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM reviews WHERE pr=? AND head=?", (number, head)).fetchone():
            return "Already delivered"
        audience = route(checked_pr(number, head))
        if audience == "private" and comments:
            raise ValueError("Owner PR accepts only a private summary")
        if audience == "contributor" and comments:
            endpoint = f"{REPO}/pulls/{number}/reviews"
            marker = f"<!-- ileapp-fixture-review:{head} -->"
            reviewer = api("user")["id"]
            prior = api(endpoint + "?per_page=100", pages=True)
            delivered = any(r["user"]["id"] == reviewer and r.get("commit_id") == head
                            and marker in (r.get("body") or "") for r in prior)
            if not delivered:
                lines = []
                for c in comments:
                    if (not isinstance(c["line"], int) or c["line"] < 1 or
                            not c["path"].strip() or not c["body"].strip()):
                        raise ValueError("Expected a changed path, line and actionable finding")
                    lines.append({"path": c["path"], "line": c["line"],
                                  "side": "RIGHT", "body": c["body"]})
                if route(checked_pr(number, head)) != "contributor":
                    raise ValueError("Unexpected delivery route")
                api(endpoint, body={"commit_id": head, "event": "COMMENT", "comments": lines,
                                    "body": f"{marker}\nAutomated iLEAPP review."})
        db.execute("INSERT INTO reviews VALUES (?, ?, ?)", (number, head, summary))
    return f"Recorded {audience} review"


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("queue")
    inspect = commands.add_parser("context")
    inspect.add_argument("number", type=int)
    record = commands.add_parser("finish")
    record.add_argument("number", type=int)
    record.add_argument("head")
    record.add_argument("summary", type=Path)
    record.add_argument("--public-comments", type=Path)
    args = parser.parse_args()
    if args.command == "context":
        print(json.dumps(context(args.number), indent=2))
        return
    db = database()
    try:
        if args.command == "queue":
            print(json.dumps(queue(db)))
        else:
            if not re.fullmatch("[0-9a-f]{40}", args.head):
                parser.error("expected a full commit SHA")
            comments = json.loads(args.public_comments.read_text()) if args.public_comments else []
            print(finish(db, args.number, args.head, args.summary.read_text(), comments))
    finally:
        db.close()


if __name__ == "__main__":
    main()
