"""Fail CI only on pylint warnings a change actually introduces.

The lint job runs pylint over the files a pull request touches. Several long-lived
modules carry pre-existing warnings that are deliberate rather than fixable --
`ileapp.py` uses wildcard imports as its module architecture, `scripts/ilapfuncs.py`
re-exports names it does not itself use so that older artifact modules keep importing
them. Any pull request that touches one of those files therefore went red for reasons
that had nothing to do with the change, which pushes contributors toward either
unrelated refactors or blanket file-level `# pylint: disable` comments. Both are worse
than the debt.

This script lints the same file set twice, once at the merge base and once at the
change, and fails only when a (file, warning) pair appears more often than it did
before. New code is held to the full standard; existing debt neither blocks a pull
request nor gets silently widened.

Two details matter for a stable comparison, both learned the hard way:

* pylint's results depend on which files are analysed together, because it infers
  across the set. Both runs therefore lint the same list of paths.
* pylint caches results between runs and will otherwise report stale data, so both
  runs pass --persistent=no.

Usage:
    python admin/scripts/lint_changed.py --base-ref <sha> <file> [<file> ...]
"""

import argparse
import collections
import json
import os
import subprocess
import sys
import tempfile

PYLINT_ARGS = ['--disable=C,R', '--persistent=no', '--output-format=json']


VENDOR_PREFIX = 'scripts/vendor/'


def run_pylint(repo_dir, paths):
    """Return Counter keyed by (path, symbol) for paths that exist in repo_dir."""
    present = [p for p in paths if os.path.exists(os.path.join(repo_dir, p))]
    if not present:
        return collections.Counter()

    env = dict(os.environ, PYTHONPATH='.')
    result = subprocess.run(
        [sys.executable, '-m', 'pylint', *present, *PYLINT_ARGS],
        cwd=repo_dir, env=env, capture_output=True, text=True, check=False)

    stdout = result.stdout.strip()
    if not stdout:
        # No JSON at all means pylint failed to start rather than finding nothing.
        if result.returncode not in (0,):
            print(f'pylint produced no output (exit {result.returncode}):\n{result.stderr}',
                  file=sys.stderr)
            sys.exit(2)
        return collections.Counter()

    try:
        messages = json.loads(stdout)
    except json.JSONDecodeError:
        print(f'could not parse pylint output:\n{stdout[:2000]}', file=sys.stderr)
        sys.exit(2)

    return collections.Counter((m['path'], m['symbol']) for m in messages)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-ref', required=True,
                        help='commit to compare against, normally the merge base')
    parser.add_argument('paths', nargs='*', help='changed Python files')
    args = parser.parse_args()

    paths = [p for p in args.paths if p.endswith('.py')]

    # scripts/vendor/ is code copied verbatim from another repository. Linting it
    # would fail this job on warnings that are not ours to fix, and the only ways to
    # silence them are editing the copy or adding a file-level disable, both of which
    # make the next re-vendor a merge instead of a copy. check_vendored.py is what
    # guards that directory, by hash rather than by style.
    skipped = [p for p in paths if p.replace(os.sep, '/').startswith(VENDOR_PREFIX)]
    if skipped:
        print('Not linting vendored files (guarded by check_vendored.py instead):\n'
              + '\n'.join(f'  {p}' for p in skipped) + '\n')
        paths = [p for p in paths if p not in skipped]

    if not paths:
        print('No Python files to lint.')
        return 0

    print('Linting:\n' + '\n'.join(f'  {p}' for p in paths) + '\n')
    after = run_pylint('.', paths)

    # A detached worktree gives the base revision with full repo context, so pylint
    # resolves imports there the same way it does for the change.
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = os.path.join(tmp, 'base')
        subprocess.run(['git', 'worktree', 'add', '--detach', '--quiet', base_dir,
                        args.base_ref], check=True, capture_output=True)
        try:
            before = run_pylint(base_dir, paths)
        finally:
            subprocess.run(['git', 'worktree', 'remove', '--force', base_dir],
                           check=False, capture_output=True)

    introduced = {key: count - before.get(key, 0)
                  for key, count in after.items() if count > before.get(key, 0)}

    total_before, total_after = sum(before.values()), sum(after.values())
    print(f'pre-existing warnings in these files: {total_before}')
    print(f'warnings now:                         {total_after}')

    if not introduced:
        removed = total_before - total_after
        if removed > 0:
            print(f'\nNo new warnings introduced ({removed} fewer than before). PASS')
        else:
            print('\nNo new warnings introduced. PASS')
        return 0

    print('\nThis change introduces new pylint warnings:\n')
    for (path, symbol), count in sorted(introduced.items()):
        print(f'  {path}: {symbol} (+{count})')
    print('\nRe-run locally with:')
    print(f'  PYTHONPATH=. python -m pylint {" ".join(paths)} {" ".join(PYLINT_ARGS[:2])}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
