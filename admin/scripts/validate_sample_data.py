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
This script closes that gap in four escalating steps:

1. Structure. Always runs, needs no test data, safe for CI. Checks that every
   `sample_data` block is a mapping of non-empty strings and reports which
   values carry a row count this script can compare later.

2. Registry. With ``--registry``, checks that every key an artifact cites
   exists in the registry, that each registered corpus is present on disk, and
   with ``--verify-hashes`` that its SHA-256 still matches what was recorded.

3. Counts. With ``--run KEY``, parses that corpus end to end and compares the
   rows each artifact actually produced against the rows it declares. The run must
   reach its own completion marker before any count is read, and a run that caught a
   database error or disabled a capability is reported, because a count taken from
   one of those describes the tool rather than the evidence. The produced count is
   read from the run's LAVA manifest, so an artifact whose ``output_types`` exclude
   LAVA is reported as uncheckable rather than as zero, and the run log is kept so
   a genuine zero can be explained.

4. Emit. With ``--emit IMAGE``, parses that image (a zip, tar, gz, or an
   extraction directory; no registry needed) and prints paste-ready
   ``sample_data`` values for the artifact modules changed on the current
   branch, or for the modules named with ``--modules``. The same run-integrity
   checks as ``--run`` apply before anything is printed, a zero is printed with
   a caveat rather than as a bare measurement, and nothing is written to any
   module: the values are for a person to review and paste.

Usage::

    python3 admin/scripts/validate_sample_data.py
    python3 admin/scripts/validate_sample_data.py --registry /path/samples.json
    python3 admin/scripts/validate_sample_data.py --registry /path/samples.json --verify-hashes
    python3 admin/scripts/validate_sample_data.py --registry /path/samples.json --run corpus_key
    python3 admin/scripts/validate_sample_data.py --emit /path/image.zip --key my_pixel6_a14
    python3 admin/scripts/validate_sample_data.py --emit /path/image.zip --modules myApp

The registry path may also be supplied through the ``iLEAPP_SAMPLES``
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

# The three names that differ between the LEAPP cores. Everything below reads
# these, so the five copies of this script stay identical apart from this block.
TOOL = "ileapp.py"
SAMPLES_ENV = "iLEAPP_SAMPLES"
RUN_PREFIX = "ileapp-validate-"

# The tool prints this once, last, when a run has finished its work. Exit status alone
# does not distinguish a finished run from one that stopped early with a usable-looking
# partial LAVA file, so the marker is asserted before any count is read.
COMPLETION_MARKER = "Report generation Completed."

# Artifacts catch their own database errors and log them in their own format, so the
# framework's "artifact had errors!" banner stays clean while a table comes back short.
# A count taken from such a run describes the failure, not the evidence.
CAUGHT_ERROR_RE = re.compile(
    r"no such column|no such table|malformed|file is not a database", re.I)

# A capability disabled for a missing optional dependency makes its artifacts report
# zero rows on a run that is otherwise healthy. Comparing against that produces a
# mismatch that invites deleting a correct declared count.
DEGRADED_RE = re.compile(
    r"(?:artifacts? disabled|not available|No module named|ImportError)", re.I)

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
    """Map an evidence source to the tool's -t input type.

    The registry's match key is spelled "zip" for historical reasons but may
    point at any container the tool accepts, and --emit may also hand this an
    extraction directory. Returns None when nothing names a known type, so the
    caller reports it instead of guessing.
    """
    if source.is_dir():
        return "fs"
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

    The import is lazy and only reached from --run and --emit, which already run
    the tool and therefore already need its dependencies. The structure step
    stays import-free and safe for CI. If the import fails, the caller compares
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


def execute_tool(source, label, log_name, report, keep=False):
    """Parse one evidence source and return its per-artifact LAVA row counts.

    Returns (produced, output_root, log_path); produced is None when the run
    cannot be trusted, and every reason is reported. The run must exit 0 and
    reach its own completion marker, and any caught database error or disabled
    capability in the transcript is reported, because a count taken from such a
    run describes the tool rather than the evidence. The output folder is
    deleted unless keep is set; the run log is written beside it and survives,
    because an artifact that produced nothing has usually logged why.
    """
    input_type = input_type_for(source)
    if input_type is None:
        report.error(f"{label}: cannot pick a -t input type for {source.name}; "
                     "known inputs are a directory, .zip, .tar, .tar.gz, .tgz")
        return None, None, None

    output_root = tempfile.mkdtemp(prefix=RUN_PREFIX)
    folder = "validate_run"
    command = [sys.executable, str(REPO_ROOT / TOOL), "-t", input_type,
               "-i", str(source), "-o", output_root, "--custom_output_folder", folder]
    print(f"  running {source.name} ...")
    completed = subprocess.run(command, cwd=str(REPO_ROOT),
                               capture_output=True, text=True, check=False)

    log_path = Path(output_root).parent / f"{RUN_PREFIX}{log_name}.log"
    try:
        log_path.write_text((completed.stdout or "") + (completed.stderr or ""),
                            encoding="utf-8")
    except OSError as ex:
        report.warn(f"{label}: could not write the run log: {ex}")
        log_path = None

    def clean_up():
        if not keep:
            shutil.rmtree(output_root, ignore_errors=True)

    if completed.returncode != 0:
        report.error(f"{label}: {TOOL} exited {completed.returncode}, so no count "
                     f"was taken; run log at {log_path}\n{completed.stdout[-600:]}")
        clean_up()
        return None, output_root, log_path

    # A run is only evidence about the source once it is shown to have finished, and
    # to have finished without swallowing an error or silently dropping a capability.
    transcript = f"{completed.stdout}\n{completed.stderr}"
    if COMPLETION_MARKER not in transcript:
        report.error(f"{label}: {TOOL} exited 0 but never printed "
                     f"{COMPLETION_MARKER!r}, so it did not finish; no count was read\n"
                     f"{completed.stdout[-600:]}")
        clean_up()
        return None, output_root, log_path

    caught = sorted({line.strip() for line in transcript.splitlines()
                     if CAUGHT_ERROR_RE.search(line)})
    for line in caught[:20]:
        report.error(f"{label}: an artifact caught a database error, so any "
                     f"short table below may be the error and not the evidence: {line}")
    if len(caught) > 20:
        report.error(f"{label}: {len(caught) - 20} further caught database error(s)")

    degraded = sorted({line.strip() for line in transcript.splitlines()
                       if DEGRADED_RE.search(line)})
    for line in degraded[:20]:
        report.error(f"{label}: a capability was disabled for this run, so its "
                     f"artifacts report zero rows here regardless of the evidence: {line}")

    lava_path = Path(output_root) / folder / "_lava_data.lava"
    try:
        with open(lava_path, "r", encoding="utf-8") as handle:
            lava = json.load(handle)
    except (OSError, ValueError) as ex:
        report.error(f"{label}: could not read {lava_path}: {ex}")
        clean_up()
        return None, output_root, log_path

    produced = {}
    for entries in (lava.get("artifacts") or {}).values():
        for item in entries:
            produced[item.get("name")] = item.get("record_count", 0)

    if keep:
        report.note(f"{label}: run output kept at {output_root}")
    else:
        shutil.rmtree(output_root, ignore_errors=True)
    if log_path:
        report.note(f"{label}: run log at {log_path}")
    return produced, output_root, log_path


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

    produced, _, _ = execute_tool(source, f"--run '{corpus}'", corpus, report, keep=keep)
    if produced is None:
        return

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


def changed_artifact_modules(report):
    """Artifact modules changed on the current branch, by file name.

    Diffs the working tree (committed, staged and unstaged) against the merge
    base with origin/main, falling back to main, and adds untracked files under
    scripts/artifacts so a brand-new module is seen before its first commit.
    """
    def git(*args):
        return subprocess.run(["git", *args], cwd=str(REPO_ROOT),
                              capture_output=True, text=True, check=False)

    base = None
    for candidate in ("origin/main", "main"):
        probe = git("merge-base", "HEAD", candidate)
        if probe.returncode == 0 and probe.stdout.strip():
            base = probe.stdout.strip()
            break
    if base is None:
        report.error("--emit: could not find a merge base with origin/main or main, "
                     "so the changed modules cannot be detected; name them with --modules")
        return []

    changed = git("diff", "--name-only", base)
    if changed.returncode != 0:
        report.error(f"--emit: git diff against {base[:12]} failed: "
                     f"{changed.stderr.strip()}")
        return []
    untracked = git("ls-files", "--others", "--exclude-standard",
                    "--", "scripts/artifacts")
    names = set(changed.stdout.splitlines()) | set(untracked.stdout.splitlines())
    return sorted({Path(name).name for name in names
                   if name.replace("\\", "/").startswith("scripts/artifacts/")
                   and name.endswith(".py")})


def resolve_emit_modules(modules_arg, artifacts, report):
    """The artifact modules --emit reports on, resolved and counted before the run.

    A name that matches no artifact module is an error, never silently dropped:
    an empty selection would otherwise run the whole image and print nothing,
    which reads as success.
    """
    by_module = {}
    for key, (module, info) in artifacts.items():
        by_module.setdefault(module, []).append((key, info))

    if modules_arg:
        wanted = []
        for raw in modules_arg.split(","):
            name = raw.strip()
            if not name:
                continue
            if not name.endswith(".py"):
                name += ".py"
            wanted.append(name)
        unknown = [name for name in wanted if name not in by_module]
        if unknown:
            known = ", ".join(sorted(by_module)[:5])
            report.error(f"--modules names no artifact module: {', '.join(unknown)} "
                         f"(module file names look like: {known}, ...)")
            return {}
        selected = wanted
    else:
        selected = [name for name in changed_artifact_modules(report)
                    if name in by_module]
        if not selected:
            if not report.errors:
                report.error("--emit: no changed artifact modules detected on this "
                             "branch; name the module(s) with --modules")
            return {}

    picked = {name: sorted(by_module[name]) for name in selected}
    total = sum(len(entries) for entries in picked.values())
    print(f"  emitting for {total} artifact(s) in {len(picked)} module(s): "
          f"{', '.join(picked)}")
    return picked


def emit_counts(image, key, modules_arg, artifacts, report, keep=False):
    """Step 4: parse one image and print paste-ready sample_data values.

    Prints, never writes: the values go through a person, who prefixes the app
    name and version seen on the image and checks any zero against the source
    store before recording it. A zero here is a claim about this run, not yet
    about the evidence.
    """
    source = Path(image)
    if not source.exists():
        report.error(f"--emit: {source} does not exist")
        return

    picked = resolve_emit_modules(modules_arg, artifacts, report)
    if not picked:
        return

    if not key:
        key = re.sub(r"[^a-z0-9]+", "_", source.stem.lower()).strip("_") or "my_image"
        report.note(f"--emit: no --key given, so the image key defaults to '{key}'; "
                    "pick a name that identifies the image to you")

    errors_before = len(report.errors)
    produced, _, _ = execute_tool(source, "--emit", key, report, keep=keep)
    if produced is None:
        return

    writes_to_lava = lava_output_predicate(report)
    run_was_clean = len(report.errors) == errors_before
    print(f"\nPaste-ready sample_data values for '{key}' ({source.name}):\n")
    for module, entries in picked.items():
        for artifact_key, info in entries:
            print(f"# {module} :: {artifact_key}")
            output_types = info.get("output_types", DEFAULT_OUTPUT_TYPES)
            if writes_to_lava is not None and not writes_to_lava("lava", output_types):
                print(f"#   output_types={output_types!r} never reaches the LAVA "
                      "manifest, so this script cannot count it; describe the "
                      "coverage in words instead\n")
                continue
            actual = produced.get(info.get("name"), 0)
            caveat = ""
            if actual == 0:
                caveat = ("  # unverified zero: confirm the source store is "
                          "actually empty before recording it")
            print("    \"sample_data\": {")
            print(f"        \"{key}\": \"{actual} rows\",{caveat}")
            print("    },\n")
    print("Prefix each value with the app name and version seen on the image, "
          "for example \"AppName 1.2.3 | 123 rows\".")
    if not run_was_clean:
        print("The run was NOT clean (see the errors below); resolve those before "
              "recording any of these values.")


def main():
    parser = argparse.ArgumentParser(
        description="Validate artifact sample_data blocks against a corpus registry.")
    parser.add_argument("--registry", default=os.environ.get(SAMPLES_ENV),
                        help=f"path to samples.json (or set {SAMPLES_ENV})")
    parser.add_argument("--verify-hashes", action="store_true",
                        help="re-hash every registered corpus; slow on large images")
    parser.add_argument("--run", metavar="KEY",
                        help="parse this corpus and compare produced rows to declared rows")
    parser.add_argument("--emit", metavar="IMAGE",
                        help="parse this image (zip, tar, gz, or extraction directory) and "
                             "print paste-ready sample_data values; no registry needed")
    parser.add_argument("--key", metavar="NAME",
                        help="image key to print in the emitted values (with --emit)")
    parser.add_argument("--modules", metavar="NAMES",
                        help="comma-separated artifact module file names to emit for; "
                             "defaults to the modules changed on the current branch")
    parser.add_argument("--keep", action="store_true",
                        help="keep the run output folder instead of deleting it")
    args = parser.parse_args()

    report = Report()
    artifacts = read_artifacts()
    if not artifacts:
        print("No v2 artifacts found.")
        return 1

    print("Structure")
    check_structure(artifacts, report)

    if args.run and args.emit:
        report.error("--run and --emit are separate steps; pass one at a time")
    elif args.emit:
        print("Emit")
        emit_counts(args.emit, args.key, args.modules, artifacts, report, keep=args.keep)
    elif args.key or args.modules:
        report.error("--key and --modules only mean something with --emit")

    if args.registry:
        print("Registry")
        registry = load_registry(args.registry, report)
        if registry:
            check_registry(artifacts, registry, args.registry, args.verify_hashes, report)
            if args.run:
                print("Row counts")
                run_corpus(registry, args.registry, args.run, report, keep=args.keep)
    elif not args.emit:
        if args.run or args.verify_hashes:
            report.error(f"--run and --verify-hashes need --registry (or {SAMPLES_ENV})")
        report.note("no registry given, so only structure was checked")

    print()
    return report.emit()


if __name__ == "__main__":
    sys.exit(main())
