"""Flags artifact categories that are not in admin/data/artifact_categories.json.

Artifacts are grouped into a short, agreed list of categories, which the GUI's category picker
and the report sidebar show. A new artifact that fits none of them may need a new category, and
the maintainer wants to know when one appears. This check never fails a PR: it tells.

In a pull request (GITHUB_TOKEN and PR_NUMBER set) it reads the PR's added and changed files
under scripts/artifacts/ as text through the GitHub API, never running them, and keeps one
sticky comment on the PR that mentions the maintainer when a category outside the list shows
up. Locally, with no token, it reads the working tree and prints what it finds.

Artifact entries are read wherever they are written: in __artifacts_v2__, in a dict a helper
function returns, or in a helper's metadata["category"] = "..." line.

Usage: python admin/scripts/check_new_categories.py [--strict]
  --strict  exit 1 when a category outside the list is found (local use and tests)
"""
import ast
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_PATH = ROOT / "admin" / "data" / "artifact_categories.json"
ARTIFACTS = "scripts/artifacts/"
MARKER = "<!-- leapp-new-category-check -->"
MAINTAINER = "abrignoni"
LABEL = ("new-category", "fbca04", "Adds an artifact category that is not in the agreed list")
API = "https://api.github.com"


def allowed_categories(path=ALLOWED_PATH):
    """The agreed categories."""
    return set(json.loads(Path(path).read_text(encoding="utf-8"))["categories"])


def categories_in_source(text):
    """(categories, unreadable) for one module's source.

    categories: the "category" string of every dict literal that also has a "name" key (an
    artifact entry, in __artifacts_v2__ or built by a helper), and of every
    x["category"] = "..." assignment.
    unreadable: line numbers of such "category" values that are not a plain string literal,
    plus 0 when the file does not parse.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set(), [0]
    found, unreadable = set(), []

    def take(value):
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            found.add(value.value)
        else:
            unreadable.append(value.lineno)

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            fields = {k.value: v for k, v in zip(node.keys, node.values)
                      if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            # An artifact entry carries a name beside its category; a data row that
            # happens to have a "category" field does not.
            if "category" in fields and "name" in fields:
                take(fields["category"])
        elif isinstance(node, ast.Assign):
            # metadata["category"] = "..." in a helper that copies another entry
            for target in node.targets:
                if (isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant)
                        and target.slice.value == "category"
                        and isinstance(node.value, ast.Constant)
                        and isinstance(node.value.value, str)):
                    found.add(node.value.value)
    return found, unreadable


def review(sources, allowed):
    """{module: (new categories, unreadable lines)} for modules with anything to report."""
    report = {}
    for module, text in sorted(sources.items()):
        found, unreadable = categories_in_source(text)
        new = sorted(found - allowed)
        if new or unreadable:
            report[module] = (new, unreadable)
    return report


def render_comment(report):
    """The sticky comment body for a review result."""
    if not report:
        return (f"{MARKER}\nEvery artifact category in this PR is in "
                "`admin/data/artifact_categories.json`.")
    lines = [MARKER, f"@{MAINTAINER} this PR uses artifact categories that are not in "
             "`admin/data/artifact_categories.json`:", ""]
    for module, (new, unreadable) in report.items():
        for category in new:
            lines.append(f"- `{module}`: new category \"{category}\"")
        for line in unreadable:
            where = "the file does not parse" if line == 0 else f"line {line} is not a plain string"
            lines.append(f"- `{module}`: category could not be read ({where})")
    lines += ["", "If one of the existing categories fits, please use it. If none does, "
              "add the new category to `admin/data/artifact_categories.json` in this PR "
              "so it can be reviewed with the artifact."]
    return "\n".join(lines)


def api_request(token, url, method="GET", body=None, accept="application/vnd.github+json"):
    """One GitHub API call; returns parsed JSON, raw text, or None on 404."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as ex:
        if ex.code == 404:
            return None
        raise RuntimeError(f"{method} {url} -> HTTP {ex.code}: {ex.read().decode()[:300]}") from ex
    if accept.endswith("raw+json"):
        return raw
    return json.loads(raw) if raw else {}


def paginate(token, url):
    """Yields items from a paginated list endpoint."""
    page = 1
    sep = "&" if "?" in url else "?"
    while True:
        batch = api_request(token, f"{url}{sep}per_page=100&page={page}")
        if not batch:
            return
        yield from batch
        if len(batch) < 100:
            return
        page += 1


def pr_sources(token, repo, pr_number):
    """{module: source text} for the artifact modules the PR adds or changes."""
    sources = {}
    for f in paginate(token, f"{API}/repos/{repo}/pulls/{pr_number}/files"):
        path = f["filename"]
        if f["status"] == "removed" or not path.startswith(ARTIFACTS) or not path.endswith(".py"):
            continue
        text = api_request(token, f["contents_url"], accept="application/vnd.github.raw+json")
        sources[Path(path).stem] = text or ""
    return sources


def tree_sources(root=ROOT):
    """{module: source text} for every artifact module in a working tree."""
    return {p.stem: p.read_text(encoding="utf-8")
            for p in sorted((root / ARTIFACTS).glob("*.py"))}


def apply_state(token, repo, pr_number, report):
    """Upserts the sticky comment and the label."""
    body = render_comment(report)
    existing = None
    for comment in paginate(token, f"{API}/repos/{repo}/issues/{pr_number}/comments"):
        if MARKER in comment.get("body", ""):
            existing = comment
            break
    if existing:
        if existing["body"] != body:
            api_request(token, f"{API}/repos/{repo}/issues/comments/{existing['id']}",
                        method="PATCH", body={"body": body})
    elif report:
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/comments",
                    method="POST", body={"body": body})
    name, color, description = LABEL
    current = {l["name"] for l in api_request(token, f"{API}/repos/{repo}/issues/{pr_number}")["labels"]}
    if report and name not in current:
        if api_request(token, f"{API}/repos/{repo}/labels/{name}") is None:
            api_request(token, f"{API}/repos/{repo}/labels", method="POST",
                        body={"name": name, "color": color, "description": description})
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/labels",
                    method="POST", body={"labels": [name]})
    elif not report and name in current:
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/labels/{name}", method="DELETE")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    allowed = allowed_categories()
    token, pr_number = os.environ.get("GITHUB_TOKEN"), os.environ.get("PR_NUMBER")
    if token and pr_number:
        repo = os.environ["GITHUB_REPOSITORY"]
        report = review(pr_sources(token, repo, int(pr_number)), allowed)
        print(render_comment(report))
        apply_state(token, repo, int(pr_number), report)
        return 0
    report = review(tree_sources(), allowed)
    print(render_comment(report))
    return 1 if report and "--strict" in argv else 0


if __name__ == "__main__":
    sys.exit(main())
