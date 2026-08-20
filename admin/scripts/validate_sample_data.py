"""
Validates the `sample_data` blocks declared by artifacts.

An artifact's `sample_data` records which test corpora it has been run against
and what each produced, for example::

    "sample_data": {
        "corpus_key": "AppName 1.2.3 | 12940 rows",
    }

Those keys are meant to name entries in a corpus registry (`samples.json`),
which lives with the test data rather than in this repository because the data
is usually private. Nothing enforced any of that, so a key could name a corpus
that does not exist and a row count could drift silently after a parser change.
This script closes that gap in three escalating steps:

1. Structure. Always runs, needs no test data, safe for CI. Checks that every
   `sample_data` block is a mapping of non-empty strings and reports which
   values carry a row count this script can compare later.

2. Registry. With ``--registry``, checks that every key an artifact cites
   exists in the registry, that each registered corpus is present on disk, and
   with ``--verify-hashes`` that its SHA-256 still matches what was recorded.

3. Counts. With ``--run KEY``, parses that corpus end to end and compares the
   rows each artifact actually produced against the rows it declares. The
   produced count is read from the run's LAVA manifest, so an artifact whose
   ``output_types`` exclude LAVA is reported as uncheckable rather than as
   zero, and the run log is kept so a genuine zero can be explained.

Usage::

    python3 admin/scripts/validate_sample_data.py
    python3 admin/scripts/validate_sample_data.py --registry /path/samples.json
    python3 admin/scripts/validate_sample_data.py --registry /path/samples.json --verify-hashes
    python3 admin/scripts/validate_sample_data.py --registry /path/samples.json --run corpus_key

The registry path may also be supplied through the ``ILEAPP_SAMPLES``
environment variable. Exit status is 1 if any error was reported; warnings
alone do not fail the run.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = REPO_ROOT / "scripts" / "artifacts"
ROW_COUNT_RE = re.compile(r"(\d[\d,]*)\s+rows?\b", re.I)
HASH_CHUNK = 1 << 22
# What artifact_processor falls back to when an artifact declares no output_types.
DEFAULT_OUTPUT_TYPES = ["html", "tsv", "timeline", "lava", "kml"]


class Report:
    """Collects findings so the whole run is reported at once."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, message):
        self.errors.append(message)

    def warn(self, message):
        self.warnings.append(message)

    def note(self, message):
        self.notes.append(message)

    def emit(self):
        for line in self.notes:
            print(f"  {line}")
        for line in self.warnings:
            print(f"  WARNING  {line}")
        for line in self.errors:
            print(f"  ERROR    {line}")
        print(f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return 1 if self.errors else 0


def read_artifacts():
    """Return {artifact_key: (module, info)} for every v2 artifact.

    Metadata is read with ast.literal_eval rather than imported, so a module
    with missing third-party dependencies still validates.
    """
    artifacts = {}
    for path in sorted(ARTIFACTS_DIR.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as ex:
            print(f"  WARNING  could not parse {path.name}: {ex}")
            continue
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == "__artifacts_v2__"
                       for t in node.targets):
                continue
            try:
                block = ast.literal_eval(node.value)
            except ValueError:
                print(f"  WARNING  {path.name}: __artifacts_v2__ is not a literal")
                continue
            if isinstance(block, dict):
                for key, info in block.items():
                    artifacts[key] = (path.name, info)
    return artifacts


def declared_rows(value):
    """Row count stated in a sample_data value, or None if it states none."""
    match = ROW_COUNT_RE.search(value or "")
    return int(match.group(1).replace(",", "")) if match else None


def check_structure(artifacts, report):
    """Step 1: every sample_data block is well formed."""
    with_data = 0
    comparable = 0
    for key, (module, info) in sorted(artifacts.items()):
        sample_data = info.get("sample_data")
        if sample_data is None:
            continue
        with_data += 1
        if not isinstance(sample_data, dict):
            report.error(f"{module}:{key} sample_data is {type(sample_data).__name__}, expected a dict")
            continue
        if not sample_data:
            report.warn(f"{module}:{key} sample_data is empty")
            continue
        for corpus, value in sample_data.items():
            if not isinstance(corpus, str) or not corpus.strip():
                report.error(f"{module}:{key} has a non-string or empty corpus key")
                continue
            if not isinstance(value, str) or not value.strip():
                report.error(f"{module}:{key} sample_data['{corpus}'] is empty")
                continue
            if declared_rows(value) is None:
                report.warn(f"{module}:{key} sample_data['{corpus}'] states no row count, "
                            f"so --run cannot check it: {value!r}")
            else:
                comparable += 1
    report.note(f"{len(artifacts)} artifact(s); {with_data} declare sample_data; "
                f"{comparable} value(s) carry a comparable row count")
    return with_data


def load_registry(path, report):
    """Read and shallow-validate a samples.json registry."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            registry = json.load(handle)
    except (OSError, ValueError) as ex:
        report.error(f"could not read registry {path}: {ex}")
        return None
    if not isinstance(registry, dict) or "samples" not in registry:
        report.error(f"registry {path} has no 'samples' object")
        return None
    if not isinstance(registry["samples"], dict):
        report.error(f"registry {path}: 'samples' is not an object")
        return None
    return registry


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_registry(artifacts, registry, registry_path, verify_hashes, report):
    """Step 2: cited keys resolve, and registered corpora are present and intact."""
    samples = registry["samples"]
    base = Path(registry_path).resolve().parent

    cited = {}
    for key, (module, info) in sorted(artifacts.items()):
        for corpus in (info.get("sample_data") or {}):
            cited.setdefault(corpus, []).append(f"{module}:{key}")

    for corpus, users in sorted(cited.items()):
        if corpus not in samples:
            report.error(f"corpus '{corpus}' is cited by {len(users)} artifact(s) "
                         f"but is not in the registry (first: {users[0]})")

    for name, entry in sorted(samples.items()):
        match = (entry or {}).get("match") or {}
        relative = match.get("zip")
        if not relative:
            report.warn(f"registry entry '{name}' has no match.zip")
            continue
        target = base / relative
        if not target.is_file():
            report.error(f"registry entry '{name}' points at a missing file: {target}")
            continue
        expected = match.get("sha256")
        if not expected:
            report.warn(f"registry entry '{name}' has no sha256 recorded")
        elif verify_hashes:
            actual = sha256_of(target)
            if actual != expected:
                report.error(f"registry entry '{name}' hash mismatch\n"
                             f"             expected {expected}\n"
                             f"             actual   {actual}")
            else:
                report.note(f"'{name}' hash verified")

    unused = sorted(set(samples) - set(cited))
    if unused:
        report.note(f"registered but not cited by any artifact: {', '.join(unused)}")
    report.note(f"registry {registry_path} holds {len(samples)} sample(s); "
                f"artifacts cite {len(cited)}")


def input_type_for(source):
    """Map a corpus file's extension to the tool's -t input type.

    The registry's match key is spelled "zip" for historical reasons but may
    point at any container the tool accepts. Returns None when the extension
    names no known type, so the caller reports it instead of guessing.
    """
    name = source.name.lower()
    if name.endswith((".tar.gz", ".tgz", ".gz")):
        return "gz"
    if name.endswith(".tar"):
        return "tar"
    if name.endswith(".zip"):
        return "zip"
    return None


def lava_output_predicate(report):
    """The core's own output_types predicate, or None if it cannot be imported.

    Row counts below are read from the LAVA manifest, so an artifact whose
    output_types exclude LAVA reads as zero no matter how many rows it produced.
    Telling those apart needs the same predicate the core dispatches on, imported
    rather than copied so the two cannot drift.

    The import is lazy and only reached from --run, which already runs ileapp.py
    and therefore already needs its dependencies. The structure step stays
    import-free and safe for CI. If the import fails, the caller compares
    everything as before, which keeps a real regression visible rather than
    hiding it behind a skip.
    """
    try:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from scripts.ilapfuncs import check_output_types
        return check_output_types
    except Exception as ex:  # pylint: disable=broad-except
        report.warn(f"could not import check_output_types from the core ({ex}), so "
                    "artifacts that never write to LAVA cannot be told apart from "
                    "artifacts that produced nothing; every count was compared")
        return None


def run_corpus(registry, registry_path, corpus, report, keep=False):
    """Step 3: parse a corpus and compare produced rows against declared rows."""
    entry = registry["samples"].get(corpus)
    if entry is None:
        report.error(f"--run '{corpus}' is not in the registry")
        return
    relative = ((entry.get("match") or {}).get("zip"))
    if not relative:
        report.error(f"--run '{corpus}' has no match.zip to parse")
        return
    source = (Path(registry_path).resolve().parent / relative)
    if not source.is_file():
        report.error(f"--run '{corpus}' points at a missing file: {source}")
        return

    input_type = input_type_for(source)
    if input_type is None:
        report.error(f"--run '{corpus}': cannot pick a -t input type for {source.name}; "
                     "known extensions are .zip, .tar, .tar.gz, .tgz")
        return

    output_root = tempfile.mkdtemp(prefix="ileapp-validate-")
    folder = "validate_run"
    command = [sys.executable, str(REPO_ROOT / "ileapp.py"), "-t", input_type,
               "-i", str(source), "-o", output_root, "--custom_output_folder", folder]
    print(f"  running {source.name} ...")
    completed = subprocess.run(command, cwd=str(REPO_ROOT),
                               capture_output=True, text=True, check=False)
    # Kept beside the output rather than inside it, so it outlives the cleanup below.
    # An artifact that produced nothing has usually logged why, and that reason is the
    # difference between a regression and an input this corpus does not carry.
    log_path = Path(output_root).parent / f"ileapp-validate-{corpus}.log"
    try:
        log_path.write_text((completed.stdout or "") + (completed.stderr or ""),
                            encoding="utf-8")
    except OSError as ex:
        report.warn(f"--run '{corpus}': could not write the run log: {ex}")
        log_path = None
    if completed.returncode != 0:
        report.error(f"--run '{corpus}': ileapp.py exited {completed.returncode}, so no "
                     f"count was taken; run log at {log_path}\n"
                     f"{completed.stdout[-600:]}")
        if not keep:
            shutil.rmtree(output_root, ignore_errors=True)
        return

    lava_path = Path(output_root) / folder / "_lava_data.lava"
    try:
        with open(lava_path, "r", encoding="utf-8") as handle:
            lava = json.load(handle)
    except (OSError, ValueError) as ex:
        report.error(f"--run '{corpus}': could not read {lava_path}: {ex}")
        if not keep:
            shutil.rmtree(output_root, ignore_errors=True)
        return

    produced = {}
    for entries in (lava.get("artifacts") or {}).values():
        for item in entries:
            produced[item.get("name")] = item.get("record_count", 0)

    writes_to_lava = lava_output_predicate(report)
    errors_before = len(report.errors)
    checked = skipped = 0
    no_lava = []
    for key, (module, info) in sorted(read_artifacts().items()):
        value = (info.get("sample_data") or {}).get(corpus)
        if value is None:
            continue
        expected = declared_rows(value)
        if expected is None:
            skipped += 1
            continue
        output_types = info.get("output_types", DEFAULT_OUTPUT_TYPES)
        if writes_to_lava is not None and not writes_to_lava("lava", output_types):
            # Nothing this artifact produces reaches the manifest read above, so
            # comparing it would report zero for every corpus whatever it found.
            no_lava.append(f"{module}:{key} (output_types={output_types!r})")
            continue
        # An artifact that finds nothing is absent from the LAVA output.
        actual = produced.get(info.get("name"), 0)
        checked += 1
        if actual != expected:
            report.error(f"{module}:{key} declares {expected} row(s) for '{corpus}' "
                         f"but the run's LAVA output holds {actual}")
    report.note(f"--run '{corpus}': compared {checked} artifact(s) against the LAVA "
                f"manifest, skipped {skipped} without a row count")
    if no_lava:
        report.note(f"--run '{corpus}': {len(no_lava)} artifact(s) declare a row count but "
                    f"do not write to LAVA, so --run cannot check them: {', '.join(no_lava)}")
    if len(report.errors) > errors_before:
        report.note(f"--run '{corpus}': a produced count of 0 can mean the artifact found "
                    "nothing, that its input is absent from this corpus, or that a tool it "
                    "needs is not installed here. The artifact usually logged which.")
    if keep:
        report.note(f"--run output kept at {output_root}")
    else:
        shutil.rmtree(output_root, ignore_errors=True)
    if log_path:
        report.note(f"--run '{corpus}': run log at {log_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate artifact sample_data blocks against a corpus registry.")
    parser.add_argument("--registry", default=os.environ.get("ILEAPP_SAMPLES"),
                        help="path to samples.json (or set ILEAPP_SAMPLES)")
    parser.add_argument("--verify-hashes", action="store_true",
                        help="re-hash every registered corpus; slow on large images")
    parser.add_argument("--run", metavar="KEY",
                        help="parse this corpus and compare produced rows to declared rows")
    parser.add_argument("--keep", action="store_true",
                        help="keep the --run output folder instead of deleting it")
    args = parser.parse_args()

    report = Report()
    artifacts = read_artifacts()
    if not artifacts:
        print("No v2 artifacts found.")
        return 1

    print("Structure")
    check_structure(artifacts, report)

    if args.registry:
        print("Registry")
        registry = load_registry(args.registry, report)
        if registry:
            check_registry(artifacts, registry, args.registry, args.verify_hashes, report)
            if args.run:
                print("Row counts")
                run_corpus(registry, args.registry, args.run, report, keep=args.keep)
    else:
        if args.run or args.verify_hashes:
            report.error("--run and --verify-hashes need --registry (or ILEAPP_SAMPLES)")
        report.note("no registry given, so only structure was checked")

    print()
    return report.emit()


if __name__ == "__main__":
    sys.exit(main())
