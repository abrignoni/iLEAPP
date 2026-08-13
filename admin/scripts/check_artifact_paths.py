"""Guard artifact `paths` tuples against patterns that collide under Windows.

Every artifact module declares an `__artifacts_v2__` dict whose `paths` entry is a
tuple of fnmatch patterns. `scripts/search_files.py` matches those patterns through
`os.path.normcase`, which is:

    identity on macOS and Linux   -> matching is case-SENSITIVE
    lower() + '/'->'\\' on Windows -> matching is case-INSENSITIVE

So two patterns in one tuple that differ only in case are two distinct patterns off
Windows and **one** pattern on it. The entry point extends `files_found` once per
declared pattern with no dedup, and an artifact that calls `seeker.search()` once per
spelling gets the same first match back from both calls. Either way the artifact
reports one file twice.

That is the mild outcome. The bad one is that the second file, the one the duplicate
pattern was added for, is never read at all, so a value that is present on the device
is reported as absent.

This is what happened in iLEAPP #1946. `messageRetention` declared

    '*/mobile/Library/Preferences/com.apple.MobileSMS.plist'
    '*/mobile/Library/Preferences/com.apple.mobileSMS.plist'

and both spellings exist as different files on 6 of the 20 local corpora that carry
this plist, iOS 14.3 through 26.5.2. On Windows the artifact read the 630-byte
lowercase file twice and never opened the 15 KB one holding the setting, so a device
with "Keep Messages: Forever" was reported as "No value". It looked healthy: rows were
produced, nothing errored, and on macOS the output was correct.

The fix is always a single bracket class, never a second pattern:

    "paths": ('*/mobile/Library/Preferences/com.apple.[Mm]obileSMS.plist',)   # correct
    "paths": ('.../com.apple.MobileSMS.plist', '.../com.apple.mobileSMS.plist')  # WRONG

A bracket class matches both spellings under both `normcase` regimes and matches each
file exactly once on either platform.

The check also fails on a pattern repeated verbatim in one tuple, which double-counts
on every platform rather than only on Windows.

Discovery is recursive over `scripts/`, not a `scripts/artifacts/*.py` glob. Artifact
modules also live in `scripts/alternate_artifacts/` (loadable with
--custom_artifacts_path) and `scripts/test_artifacts/`, and a directory-pinned glob
silently stops covering any directory added later. Modules whose `__artifacts_v2__` is
not a static literal cannot be read without importing them, so they are printed as NOT
CHECKED rather than passing quietly, matching check_claim_language.py.

Usage:
    python admin/scripts/check_artifact_paths.py            # CI mode, exits 1 on a violation
    python admin/scripts/check_artifact_paths.py --list     # also print every tuple checked
    python admin/scripts/check_artifact_paths.py --self-test # prove the check still fires
"""
import argparse
import ast
import collections
import glob
import os
import sys

STANDARD_NOTE = (
    'Replace the case-variant patterns with one bracket class, for example\n'
    "    '*/Library/Preferences/com.apple.[Mm]obileSMS.plist'\n"
    'A bracket class matches every spelling under both os.path.normcase regimes and\n'
    'matches each file once. Two patterns match one file twice on Windows and can\n'
    'leave the other file unread. See admin/docs/artifact_info_block.md.')


def windows_fold(pattern):
    """The pattern as Windows `os.path.normcase` would see it."""
    return pattern.lower().replace('/', '\\')


def find_artifacts_dict(tree):
    """Return the ast node assigned to __artifacts_v2__, or None."""
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__artifacts_v2__':
                return node.value
    return None


def artifact_modules(root):
    """Every module under scripts/ that defines __artifacts_v2__ at top level.

    Deliberately recursive rather than a fixed `scripts/artifacts/*.py` glob. Artifact
    modules also live in `scripts/alternate_artifacts/` (loadable with
    --custom_artifacts_path) and `scripts/test_artifacts/`, and a glob pinned to one
    directory silently stops covering any directory added later. A checker that reports
    zero because it is not looking is indistinguishable from a clean repo.
    """
    pattern = os.path.join(root, 'scripts', '**', '*.py')
    return sorted(p for p in glob.glob(pattern, recursive=True)
                  if '__artifacts_v2__' in _read(p))


def _read(path):
    """File text, or '' if it cannot be read."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            return handle.read()
    except OSError:
        return ''


def load_artifacts(path):
    """Return (artifacts_dict, skip_reason). Exactly one of the two is None.

    A module that merely mentions the token without assigning it is not an artifact
    module and is skipped silently, so the NOT CHECKED list stays meaningful.
    """
    source = _read(path)
    if not source:
        return None, 'could not read file'

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as ex:
        return None, f'could not parse module: {ex}'

    node = find_artifacts_dict(tree)
    if node is None:
        return None, ''

    try:
        artifacts = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as ex:
        return None, f'__artifacts_v2__ is not a literal: {ex}'

    if not isinstance(artifacts, dict):
        return None, '__artifacts_v2__ is not a dict'
    return artifacts, None


def collisions_in(patterns):
    """Return [(folded, [spellings])] for every group of patterns that collide.

    A group of one spelling repeated is reported too: it double-counts everywhere,
    not just on Windows.
    """
    groups = collections.OrderedDict()
    for pattern in patterns:
        groups.setdefault(windows_fold(pattern), []).append(pattern)
    return [(folded, spellings) for folded, spellings in groups.items()
            if len(spellings) > 1]


def scan_file(path):
    """Return (violations, skip_reason, tuples_checked) for one artifact module."""
    artifacts, skip_reason = load_artifacts(path)
    if artifacts is None:
        return [], skip_reason, 0

    violations = []
    checked = 0
    for artifact_key, entry in artifacts.items():
        if not isinstance(entry, dict):
            continue
        paths = entry.get('paths')
        if isinstance(paths, str):
            paths = (paths,)
        if not isinstance(paths, (tuple, list)):
            continue
        literal = [p for p in paths if isinstance(p, str)]
        if not literal:
            continue
        checked += 1
        for folded, spellings in collisions_in(literal):
            violations.append((path, str(artifact_key), folded, spellings))
    return violations, None, checked


def repo_root():
    """Return the repository root, derived from this script's location."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def format_violation(violation):
    """Render one violation as `path:artifact_key` plus the colliding spellings."""
    path, artifact_key, _folded, spellings = violation
    rendered = '\n'.join(f'      {spelling!r}' for spelling in spellings)
    kind = ('the same pattern twice' if len(set(spellings)) == 1
            else 'patterns differing only in case')
    return f'{path}:{artifact_key}: {kind}\n{rendered}'


def self_test():
    """Prove the check fires, so a broken checker cannot pass silently.

    A checker that reports zero because it is reading the wrong thing looks exactly
    like a clean repo. These cases are the ones that motivated the script.
    """
    cases = [
        (('*/a/com.apple.MobileSMS.plist', '*/a/com.apple.mobileSMS.plist'), True,
         'case variant, the iLEAPP #1946 shape'),
        (('*/Windows/INF/setupapi.dev.log', '*/WINDOWS/INF/setupapi.dev.log'), True,
         'case variant, the DLEAPP setupapiSections shape'),
        (('*/a/File.db', '*/a/File.db'), True, 'same pattern twice'),
        (('*/a/com.apple.[Mm]obileSMS.plist',), False, 'bracket class, the fix'),
        (('*/a/File.db', '*/a/Other.db'), False, 'two genuinely different files'),
        (('*/a/File.db', '*/b/File.db'), False, 'same name, different directories'),
    ]
    failures = 0
    for patterns, should_fire, label in cases:
        fired = bool(collisions_in(list(patterns)))
        ok = fired == should_fire
        if not ok:
            failures += 1
        print(f'  {"ok  " if ok else "FAIL"}  expected={"fire" if should_fire else "pass"}  {label}')
    if failures:
        print(f'\nself-test FAILED: {failures} case(s) behaved unexpectedly')
        return 1
    print('\nself-test passed: the check fires on every known-bad shape and on no known-good one.')
    return 0


def main():
    """Scan the artifact modules and report colliding paths patterns."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--list', action='store_true', dest='list_all',
                        help='print every paths tuple checked')
    parser.add_argument('--verbose', action='store_true',
                        help='also report modules whose __artifacts_v2__ could not be read')
    parser.add_argument('--self-test', action='store_true',
                        help='check the checker against known-bad and known-good tuples')
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = repo_root()
    paths = artifact_modules(root)
    if not paths:
        print(f'No artifact modules found under {os.path.join(root, "scripts")}',
              file=sys.stderr)
        return 2

    violations = []
    skipped = []
    tuples_checked = 0
    for path in paths:
        found, skip_reason, checked = scan_file(path)
        tuples_checked += checked
        if skip_reason:
            skipped.append((path, skip_reason))
            continue
        violations.extend(found)

    if skipped and (args.verbose or violations):
        print(f'NOT CHECKED ({len(skipped)}):')
        for path, reason in skipped:
            print(f'  {os.path.relpath(path, root)}: {reason}')
        print()

    if args.list_all:
        print(f'Checked {tuples_checked} paths tuple(s) across '
              f'{len(paths) - len(skipped)} module(s).\n')

    if violations:
        print(f'Artifact paths patterns that collide under Windows normcase '
              f'({len(violations)}):')
        for violation in violations:
            print(f'  {format_violation(violation)}')
        print()
        print(STANDARD_NOTE)
        return 1

    summary = (f'Checked {tuples_checked} paths tuple(s) in '
               f'{len(paths) - len(skipped)} artifact module(s): no colliding patterns.')
    if skipped:
        summary += f' {len(skipped)} module(s) NOT checked.'
    print(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
