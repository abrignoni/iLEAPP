"""Flags artifact categories that are not in admin/data/artifact_categories.json.

Artifacts are grouped into a short, agreed list of categories, which the GUI's category picker
and the report sidebar show. A new artifact that fits none of them may need a new category, and
the maintainer wants to know when one appears. This check never fails a PR: it tells.

In a pull request (GITHUB_TOKEN and PR_NUMBER set) it reads the PR's added and changed files
under scripts/artifacts/ as text through the GitHub API, never running them, and keeps one
sticky comment on the PR that mentions the maintainer when a category outside the list shows
up. Locally, with no token, it reads the working tree and prints what it finds.

Artifact entries are read wherever they are written: in __artifacts_v2__, in a dict a helper
function returns, in a helper's metadata["category"] = "..." line, or as the first element of an
entry in the older __artifacts__ = {key: (category, paths, function)} form.

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
        if isinstance(node, ast.Assign):
            # The older form: __artifacts__ = {key: (category, paths, function)}
            if (any(isinstance(t, ast.Name) and t.id == "__artifacts__" for t in node.targets)
                    and isinstance(node.value, ast.Dict)):
                for entry in node.value.values:
                    if isinstance(entry, ast.Tuple) and entry.elts:
                        take(entry.elts[0])
                    else:
                        unreadable.append(entry.lineno)
            # metadata["category"] = "..." in a helper that copies another entry
            for target in node.targets:
                if (isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant)
                        and target.slice.value == "category"):
                    take(node.value)
    return found, unreadable


def categories_from_list(text):
    """The categories a copy of artifact_categories.json holds, or an empty set when the text
    is not a JSON object whose "categories" is a list of strings."""
    try:
        data = json.loads(text or "{}")
    except ValueError:
        return set()
    values = data.get("categories") if isinstance(data, dict) else None
    if not isinstance(values, list):
        return set()
    return {v for v in values if isinstance(v, str)}


def review(sources, allowed):
    """{module: (new categories, unreadable lines)} for modules with anything to report."""
    report = {}
    for module, text in sorted(sources.items()):
        found, unreadable = categories_in_source(text)
        new = sorted(found - allowed)
        if new or unreadable:
            report[module] = (new, unreadable)
    return report


def inert(value):
    """A PR-supplied name as a single-line code span: no Markdown, links or mentions."""
    text = " ".join(str(value).split()).replace("`", "'")
    return f"`{text[:200]}`"


def render_comment(report, added=frozenset()):
    """The sticky comment body for a review result.

    added: categories this PR itself adds to admin/data/artifact_categories.json. They are
    still reported, so the maintainer sees each new category, but the PR is not asked to do
    what it already did.
    """
    if not report:
        return (f"{MARKER}\nEvery artifact category in this PR is in "
                "`admin/data/artifact_categories.json`.")
    lines = [MARKER, f"@{MAINTAINER} this PR uses artifact categories that are not in "
             "`admin/data/artifact_categories.json` on the base branch:", ""]
    for module, (new, unreadable) in report.items():
        for category in new:
            how = "added to the list in this PR" if category in added else "not in the list"
            lines.append(f"- {inert(module)}: new category {inert(category)} ({how})")
        for line in unreadable:
            where = "the file does not parse" if line == 0 else f"line {line} is not a plain string"
            lines.append(f"- {inert(module)}: category could not be read ({where})")
    missing = any(c not in added for new, _ in report.values() for c in new)
    if missing or any(unreadable for _, unreadable in report.values()):
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
        if batch is None:
            # A missing page is not an empty one: stop the run instead of reading a partial list.
            raise RuntimeError(f"{url} page {page} returned 404")
        if not batch:
            return
        yield from batch
        if len(batch) < 100:
            return
        page += 1


def pr_sources(token, repo, pr_number):
    """({module: source text} for the artifact modules the PR adds or changes,
    the categories the PR's own copy of the list holds, or None when it leaves the list alone,
    the paths whose contents could not be fetched). The list is read as JSON data, never run."""
    sources, proposed, missing = {}, None, []
    list_path = ALLOWED_PATH.relative_to(ROOT).as_posix()
    for f in paginate(token, f"{API}/repos/{repo}/pulls/{pr_number}/files"):
        path = f["filename"]
        if f["status"] == "removed":
            continue
        if path == list_path:
            text = api_request(token, f["contents_url"], accept="application/vnd.github.raw+json")
            if text is None:
                # An unread list is an incomplete scan, not an empty list.
                missing.append(path)
                continue
            proposed = categories_from_list(text)
            continue
        if not path.startswith(ARTIFACTS) or not path.endswith(".py"):
            continue
        text = api_request(token, f["contents_url"], accept="application/vnd.github.raw+json")
        if text is None:
            missing.append(path)
            continue
        sources[Path(path).stem] = text
    return sources, proposed, missing


def tree_sources(root=ROOT):
    """{module: source text} for every artifact module in a working tree."""
    return {p.stem: p.read_text(encoding="utf-8")
            for p in sorted((root / ARTIFACTS).glob("*.py"))}


BOT = "github-actions[bot]"


def own_comment(comments):
    """The workflow's own sticky comment: the marker in a comment the bot wrote. A person
    who quotes the marker does not get their comment edited."""
    for comment in comments:
        if MARKER in comment.get("body", "") and (comment.get("user") or {}).get("login") == BOT:
            return comment
    return None


def apply_state(token, repo, pr_number, report, added=frozenset()):
    """Upserts the sticky comment and the label."""
    body = render_comment(report, added)
    existing = own_comment(paginate(token, f"{API}/repos/{repo}/issues/{pr_number}/comments"))
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
            try:
                api_request(token, f"{API}/repos/{repo}/labels", method="POST",
                            body={"name": name, "color": color, "description": description})
            except RuntimeError:
                # Another run may have created it a moment ago; go on only if it now exists.
                if api_request(token, f"{API}/repos/{repo}/labels/{name}") is None:
                    raise
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/labels",
                    method="POST", body={"labels": [name]})
    elif not report and name in current:
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/labels/{name}", method="DELETE")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    allowed = allowed_categories()
    token, pr_number = os.environ.get("GITHUB_TOKEN"), os.environ.get("PR_NUMBER")
    if token and pr_number:
        # Advisory: an API failure is a warning in the log, never a failed check.
        try:
            repo = os.environ["GITHUB_REPOSITORY"]
            sources, proposed, missing = pr_sources(token, repo, int(pr_number))
            report = review(sources, allowed)
            added = frozenset((proposed or set()) - allowed)
            print(render_comment(report, added))
            if missing:
                # An incomplete scan must not replace an earlier alert: it would drop the
                # findings for the modules it could not read.
                print(f"::warning::Could not read {', '.join(missing)}; left the alert as it was.")
            else:
                apply_state(token, repo, int(pr_number), report, added)
        except Exception as ex:  # pylint: disable=broad-except
            print(f"::warning::New category check could not finish: {ex}")
        return 0
    report = review(tree_sources(), allowed)
    print(render_comment(report))
    return 1 if report and "--strict" in argv else 0


if __name__ == "__main__":
    sys.exit(main())
