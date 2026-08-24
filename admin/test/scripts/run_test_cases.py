#!/usr/bin/env python3
"""Runs every committed test case and compares the output to its recorded baseline.

The interactive recorder is admin/test/scripts/test_module.py: it runs a module's
artifacts against the case zips and writes timestamped snapshots (headers plus
full rows) under admin/test/results/<module>/. This script is the other half:
it re-runs the same artifacts through the same machinery and fails when the
output no longer matches the latest snapshot, so the committed cases act as
regression tests in CI.

Baselines are ordinary committed files. To accept a new baseline after a
deliberate parser change, re-record it in the same PR:

    python admin/test/scripts/test_module.py <module> -a all -c all

then commit the new snapshot (and delete the superseded one), so the reviewer
sees the row-level diff next to the code that caused it.

Comparison notes:
- Rows are compared as unordered multisets: SQLite result order without an
  ORDER BY is not stable across platforms and a reorder is not a regression.
- Both sides are normalized before comparison: values are passed through a
  JSON round-trip (matching how snapshots were serialized) and the per-run
  extraction directory admin/test/temp/extract_<name>_<epoch> is replaced by
  a fixed token, since its epoch differs on every run by construction.

Units listed in admin/test/cases/known_failures.json (unit -> reason) run and
report but do not gate, so a unit can be excluded deliberately, with a stated
reason, instead of blocking every PR while it is being repaired. A known
failure that passes again is flagged so the entry gets removed.

Exit status is 1 if any non-excluded unit failed, errored, or has no
baseline; 0 otherwise.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT))

CASES_DIR = REPO_ROOT / "admin" / "test" / "cases"
RESULTS_DIR = REPO_ROOT / "admin" / "test" / "results"
TEMP_EXTRACT_RE = re.compile(r"admin/test/temp/extract_[A-Za-z0-9_]+_\d+")
TEMP_TOKEN = "<extract-dir>"
KNOWN_FAILURES_PATH = CASES_DIR / "known_failures.json"
COMPLETION_MARKER = "Test case comparison complete"


def discover_modules():
    """Module names that have a committed case file."""
    return sorted(p.name[len("testdata."):-len(".json")]
                  for p in CASES_DIR.glob("testdata.*.json"))


def latest_baseline(module, artifact, case):
    """Path of the newest snapshot for one (module, artifact, case), or None."""
    pattern = f"{module}.{artifact}.{case}.*.json"
    candidates = sorted((RESULTS_DIR / module).glob(pattern))
    return candidates[-1] if candidates else None


def normalize_rows(rows):
    """Rows as a sorted list of JSON strings, with per-run paths tokenized."""
    normalized = []
    for row in rows:
        text = json.dumps(row, default=str, ensure_ascii=False)
        normalized.append(TEMP_EXTRACT_RE.sub(TEMP_TOKEN, text))
    return sorted(normalized)


def normalize_headers(headers):
    return json.loads(json.dumps(headers, default=str))


def compare(fresh_headers, fresh_rows, baseline):
    """Returns a list of difference descriptions; empty means match."""
    problems = []
    base_headers = normalize_headers(baseline.get("headers", []))
    if normalize_headers(fresh_headers) != base_headers:
        problems.append(f"headers differ: now {normalize_headers(fresh_headers)!r}, "
                        f"recorded {base_headers!r}")
    now = normalize_rows(fresh_rows)
    recorded = normalize_rows(baseline.get("data", []))
    if now != recorded:
        now_set, rec_set = set(now), set(recorded)
        gained = sorted(now_set - rec_set)
        lost = sorted(rec_set - now_set)
        problems.append(f"rows differ: now {len(now)}, recorded {len(recorded)}; "
                        f"{len(gained)} new, {len(lost)} missing")
        for label, rows in (("new", gained), ("missing", lost)):
            for row in rows[:2]:
                problems.append(f"  {label}: {row[:160]}")
    return problems


def run_one(test_module, module, artifact, case, case_data):
    """Runs one artifact against one case zip; returns (status, detail)."""
    zip_path = CASES_DIR / "data" / module / f"testdata.{module}.{artifact}.{case}.zip"
    if not zip_path.exists():
        return "BROKEN", f"case declares files but zip is missing: {zip_path}"
    baseline_path = latest_baseline(module, artifact, case)
    if baseline_path is None:
        return "NO_BASELINE", ("no recorded snapshot; record one with "
                               f"test_module.py {module} -a {artifact} -c {case}")
    try:
        os_version = case_data.get("image_info", {}).get("os_version")
        headers, rows, _elapsed, _commit, _media, _embedded = test_module.process_artifact(
            zip_path, module, artifact, case_data["artifacts"][artifact],
            target_os_version=os_version)
        headers, rows = test_module.process_data(headers, rows)
    except Exception as ex:  # pylint: disable=broad-except
        return "ERROR", f"{type(ex).__name__}: {ex}"
    with open(baseline_path, encoding="utf-8") as f:
        baseline = json.load(f)
    problems = compare(headers, rows, baseline)
    if problems:
        return "FAIL", "\n    ".join([f"vs {baseline_path.name}"] + problems)
    return "PASS", f"{len(rows)} rows match {baseline_path.name}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--module", action="append",
                        help="limit to this module (repeatable; default: all)")
    parser.add_argument("--list", action="store_true", help="list runnable units and exit")
    parser.add_argument("--strict", action="store_true",
                        help="ignore known_failures.json and gate on everything")
    args = parser.parse_args(argv)

    known = {}
    if KNOWN_FAILURES_PATH.exists() and not args.strict:
        with open(KNOWN_FAILURES_PATH, encoding="utf-8") as f:
            known = json.load(f)

    os.chdir(REPO_ROOT)
    import test_module  # noqa: E402  imported late so sys.path is set

    modules = args.module or discover_modules()
    counts = {}
    failures = []
    for module in modules:
        cases_file = CASES_DIR / f"testdata.{module}.json"
        if not cases_file.exists():
            print(f"{module}: no case file", flush=True)
            failures.append((module, "-", "-", "BROKEN", "case file missing"))
            continue
        with open(cases_file, encoding="utf-8") as f:
            cases = json.load(f)
        for case, case_data in sorted(cases.items()):
            for artifact, artifact_data in sorted(case_data.get("artifacts", {}).items()):
                if artifact_data.get("file_count", 0) == 0:
                    continue
                if args.list:
                    print(f"{module} {artifact} {case}")
                    continue
                status, detail = run_one(test_module, module, artifact, case, case_data)
                unit = f"{module}.{artifact}.{case}"
                if unit in known and status != "PASS":
                    print(f"[KNOWN_FAIL ] {unit}: {status}; excluded: {known[unit]}", flush=True)
                    counts["KNOWN_FAIL"] = counts.get("KNOWN_FAIL", 0) + 1
                    continue
                counts[status] = counts.get(status, 0) + 1
                if unit in known and status == "PASS":
                    detail += " (listed in known_failures.json; remove its entry)"
                print(f"[{status:11s}] {unit}: {detail}", flush=True)
                if status != "PASS":
                    failures.append((module, artifact, case, status, detail))
    if args.list:
        return 0

    print()
    print(f"{COMPLETION_MARKER}: " +
          ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) if counts else "nothing ran")
    if failures:
        print(f"\n{len(failures)} unit(s) need attention:")
        for module, artifact, case, status, _detail in failures:
            print(f"  {status:11s} {module}.{artifact}.{case}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
