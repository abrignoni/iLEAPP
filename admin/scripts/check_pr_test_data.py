#!/usr/bin/env python3
"""Comments on pull requests that change artifact modules without test data.

Runs from .github/workflows/request_test_data.yml on pull_request_target, so
the copy of this script that executes is always the one on the base branch,
never the contributor's. The pull request's own code is fetched as text for
ast parsing and is never imported or executed.

Decision per changed artifact module:

- the PR also touches admin/test/cases/testdata.<module>.json or anything
  under admin/test/cases/data/<module>/  -> covered, nothing to ask
- the module's __artifacts_v2__ sample_data (read at the PR head) cites a
  corpus key present in admin/image_manifest.json -> a maintainer can
  generate the fixture from the public image (fixture-needed label)
- otherwise -> ask the contributor for a fixture (needs-test-data label)

Authors with write or admin permission on the repository, and bot accounts,
are skipped. The comment is sticky: one marker comment per PR, edited in
place, including flipping to a resolved note once data arrives. This is a
request, not a gate: the job succeeds whatever the outcome.

Environment: GITHUB_TOKEN, GITHUB_REPOSITORY, PR_NUMBER. Set DRY_RUN=1 to
print intended writes instead of performing them (reads still happen).
"""
import ast
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "admin" / "image_manifest.json"
MARKER = "<!-- leapp-test-data-check -->"
TEST_LABEL = "bot-test"
LABEL_ASK = "needs-test-data"
LABEL_FIXTURE = "fixture-needed"
LABELS = {
    LABEL_ASK: ("d93f0b", "Artifact PR without test data for the changed modules"),
    LABEL_FIXTURE: ("c5def5", "Cites a public image; a maintainer can generate the fixture"),
}
API = "https://api.github.com"


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
    if accept.endswith("raw+json") or accept.endswith(".raw"):
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


def artifact_modules(files):
    """{module_name: status} for artifact files the PR adds or changes."""
    modules = {}
    for f in files:
        path, status = f["filename"], f["status"]
        if status == "removed":
            continue
        parts = path.split("/")
        if parts[:2] == ["scripts", "artifacts"] and len(parts) == 3 and path.endswith(".py"):
            modules[parts[2][:-3]] = status
    return modules


def covered_modules(files, modules):
    """Modules whose test data the same PR touches."""
    covered = set()
    for f in files:
        if f["status"] == "removed":
            continue
        path = f["filename"]
        for module in modules:
            if (path == f"admin/test/cases/testdata.{module}.json"
                    or path.startswith(f"admin/test/cases/data/{module}/")):
                covered.add(module)
    return covered


def sample_data_keys_from_source(source_text):
    """Corpus keys cited in a module's __artifacts_v2__ sample_data blocks.

    Parsed with ast only; nothing is imported or executed. A module whose
    metadata is not a literal yields no keys, which routes it to the full ask.
    """
    keys = set()
    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return keys
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "__artifacts_v2__" for t in node.targets):
            continue
        try:
            block = ast.literal_eval(node.value)
        except ValueError:
            continue
        if isinstance(block, dict):
            for info in block.values():
                sample_data = info.get("sample_data") if isinstance(info, dict) else None
                if isinstance(sample_data, dict):
                    keys.update(k for k in sample_data if isinstance(k, str))
    return keys


def manifest_keys(manifest_path=MANIFEST_PATH):
    """Every name the image manifest answers to (public images only).

    A repo without a manifest gets an empty set, which routes every module to
    the full ask rather than the maintainer-can-generate note.
    """
    if not Path(manifest_path).exists():
        return set()
    with open(manifest_path, encoding="utf-8") as f:
        entries = json.load(f)["images"]
    names = set()
    for e in entries:
        names.update(filter(None, (e.get("image_name"), e.get("sample_data_key"))))
    return names


def classify(modules, covered, cited_by_module, public):
    """Splits uncovered modules into (fixture_modules, ask_modules)."""
    fixture, ask = {}, []
    for module in sorted(modules):
        if module in covered:
            continue
        cited = sorted(cited_by_module.get(module, set()) & public)
        if cited:
            fixture[module] = cited
        else:
            ask.append(module)
    return fixture, ask


def render_comment(repo, fixture, ask):
    """The sticky comment body for the current state."""
    doc = f"https://github.com/{repo}/blob/main/admin/docs/testing"
    if not fixture and not ask:
        return (f"{MARKER}\nTest data is now included for every changed artifact module. "
                "Thank you!")
    lines = [MARKER, "Thanks for the contribution!", ""]
    if ask:
        lines += [
            "This PR changes artifact modules without test data for them. A small fixture "
            "with each artifact change lets reviewers run the module against real data, and "
            "the committed case keeps guarding the module after merge.", ""]
    else:
        lines += [
            "The changed artifact modules cite public research images in their `sample_data`, "
            "so a maintainer can generate the test fixtures from those images. Nothing is "
            "needed from you, though you are welcome to add the fixtures yourself with "
            "`admin/test/scripts/make_test_data.py`.", ""]
    for module, cited in fixture.items():
        cited_text = ", ".join(f"`{k}`" for k in cited)
        lines.append(f"- `{module}.py`: cites {cited_text}; a maintainer can generate the fixture.")
    for module in ask:
        lines.append(f"- `{module}.py`: please include a fixture with this PR.")
    if ask:
        lines += [
            "", "**Adding a fixture**", "",
            "Generate it from your extraction with the helper (details in "
            f"[create_module_test_cases.md]({doc}/create_module_test_cases.md)):", "",
            "    python admin/test/scripts/make_test_data.py <module> --case <case_number> "
            "--input <extraction.zip>", "",
            "It writes `admin/test/cases/testdata.<module>.json` and one zip per artifact "
            "under `admin/test/cases/data/<module>/`.", "",
            "Size rules:", "",
            "- Under 10 MB per zip: commit the files in this PR.",
            "- 10 to 25 MB: commit the case JSON in the PR and attach the zip to a comment here.",
            "- Over 25 MB: say so here and a maintainer will arrange a handoff.", "",
            "If your extraction cannot be shared:", "",
            "- If the app appears on a public research image, generate the fixture from that "
            f"instead. [public_corpus_images.md]({doc}/public_corpus_images.md) lists the "
            "images and where to download them.",
            "- Or sanitize the real file in place: keep the file the app wrote and overwrite "
            "only the personal values, which keeps the format honest.",
            "- Or script a known session: install the app on a test device with a throwaway "
            "account, perform documented actions, and extract that.", "",
            "If none of those fit, say so here and we will work it out. The PR can still be "
            "reviewed and merged with the gap recorded in the artifact's `notes`.", "",
            "This is a request, not a gate. Nothing here blocks review."]
    return "\n".join(lines)


def desired_labels(fixture, ask):
    labels = set()
    if fixture:
        labels.add(LABEL_FIXTURE)
    if ask:
        labels.add(LABEL_ASK)
    return labels


def should_skip(login, permission, label_names):
    """Returns (skip, reason) for authors the bot would not normally address.

    A maintainer-applied bot-test label overrides the skip so the whole flow
    can be exercised end to end on any PR. Applying labels needs triage
    access, so contributors cannot trigger that on themselves.
    """
    if TEST_LABEL in label_names:
        return False, f"'{TEST_LABEL}' label present; treating the author as external"
    if login.endswith("[bot]"):
        return True, f"author {login} is a bot"
    if permission in ("admin", "write"):
        return True, f"author {login} has {permission} access"
    return False, f"author {login} has {permission} access"


def find_marker_comment(token, repo, pr_number):
    for comment in paginate(token, f"{API}/repos/{repo}/issues/{pr_number}/comments"):
        if MARKER in comment.get("body", ""):
            return comment
    return None


def author_permission(token, repo, login):
    """Repo permission for a user: admin, write, read, or none."""
    result = api_request(token, f"{API}/repos/{repo}/collaborators/{login}/permission")
    return (result or {}).get("permission", "none")


def apply_state(token, repo, pr_number, body, labels, dry_run):
    """Upserts the sticky comment and reconciles our two labels."""
    existing = find_marker_comment(token, repo, pr_number)
    resolved = not labels
    if dry_run:
        print(f"DRY_RUN: would {'edit' if existing else 'create'} comment; labels -> {sorted(labels)}")
        print("---- comment body ----")
        print(body)
        return
    if existing:
        if existing["body"] != body:
            api_request(token, f"{API}/repos/{repo}/issues/comments/{existing['id']}",
                        method="PATCH", body={"body": body})
    elif not resolved:
        # Never open a resolved-state comment on a PR that was never asked.
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/comments",
                    method="POST", body={"body": body})
    current = {l["name"] for l in api_request(token, f"{API}/repos/{repo}/issues/{pr_number}") ["labels"]}
    for name in labels - current:
        if api_request(token, f"{API}/repos/{repo}/labels/{name}") is None:
            color, description = LABELS[name]
            api_request(token, f"{API}/repos/{repo}/labels", method="POST",
                        body={"name": name, "color": color, "description": description})
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/labels",
                    method="POST", body={"labels": [name]})
    for name in (current & set(LABELS)) - labels:
        api_request(token, f"{API}/repos/{repo}/issues/{pr_number}/labels/{name}", method="DELETE")


def main():
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])
    dry_run = os.environ.get("DRY_RUN") == "1"

    pr = api_request(token, f"{API}/repos/{repo}/pulls/{pr_number}")
    login = pr["user"]["login"]
    label_names = {l["name"] for l in pr.get("labels", [])}
    permission = author_permission(token, repo, login)
    skip, reason = should_skip(login, permission, label_names)
    print(reason)
    if skip:
        print("Skipping.")
        if not dry_run:
            return
        print("DRY_RUN: continuing anyway to show the decision.")

    files = list(paginate(token, f"{API}/repos/{repo}/pulls/{pr_number}/files"))
    modules = artifact_modules(files)
    if not modules:
        print("No artifact modules added or changed; nothing to do.")
        return
    covered = covered_modules(files, modules)

    cited_by_module = {}
    contents_by_module = {f["filename"].split("/")[2][:-3]: f.get("contents_url")
                          for f in files if f["filename"].startswith("scripts/artifacts/")}
    for module in modules:
        if module in covered:
            continue
        url = contents_by_module.get(module)
        source = api_request(token, url, accept="application/vnd.github.raw+json") if url else None
        cited_by_module[module] = sample_data_keys_from_source(source or "")

    fixture, ask = classify(modules, covered, cited_by_module, manifest_keys())
    print(f"modules: {sorted(modules)}  covered: {sorted(covered)}  "
          f"fixture: {sorted(fixture)}  ask: {ask}")
    body = render_comment(repo, fixture, ask)
    apply_state(token, repo, pr_number, body, desired_labels(fixture, ask), dry_run)
    print("Done.")


if __name__ == "__main__":
    main()
