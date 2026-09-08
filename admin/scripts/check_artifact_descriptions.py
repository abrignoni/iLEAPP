"""Fail CI when an artifact's description is missing, runs to more than one line,
only repeats the artifact's name, or duplicates another artifact's in the same module.

Every artifact module declares an `__artifacts_v2__` dict whose `description` is the
one line the HTML report, the LAVA manifest and the module index quote for it. It is
the sentence somebody reads to decide what the artifact is. Four defects in it are
purely mechanical and this script fails on them:

* missing, or not a string;
* empty once stripped;
* more than one line;
* the same text as the artifact's `name`, which says nothing the name did not;
* the same text as another artifact's description in the same module, which cannot be
  right for both, since two artifacts exist because they report different things.
  The commonest cause is a block copied for a sibling and not finished.

The other half of a description audit is not mechanical and this script does not try
to be a gate for it: whether a description claims past a limit the artifact's own notes
already concede. Seven merged artifacts were found doing exactly that in one day by
reading each description beside the sentences in its notes that concede a limit. That
is a judgement pass and it belongs before the pull request. `--review` lays the pair
out for it: for each artifact in the named modules it prints the description and every
sentence of the notes that carries limiting vocabulary, and never fails.

Usage:
  check_artifact_descriptions.py [--root REPO_ROOT]
  check_artifact_descriptions.py --review MODULE [MODULE ...]

Exit status 0 when every description passes the mechanical rules, 1 when any fails,
2 when the artifact tree cannot be found.
"""
import argparse
import ast
import os
import re
import sys

# Vocabulary that marks a sentence in `notes` as conceding a limit. This drives the
# review listing only; nothing here is a claim in itself.
CONCESSION = re.compile(
    r"\b(?:not established|not evidence|is not|are not|was not|were not|does not|"
    r"do not|did not|cannot|could not|never|no row|not reported|not parsed|"
    r"not decoded|not resolved|ships with|already present|only|absence of|"
    r"blank|empty|unexercised|as stored)\b", re.IGNORECASE)

STANDARD_NOTE = (
    'A description is the one line quoted for the artifact. Say what the rows are and '
    'where they come from; a description that repeats the name or a sibling says '
    'nothing, and one that claims past its own notes is the defect --review exists '
    'to surface.')


def artifact_blocks(path):
    """The __artifacts_v2__ dict of one module as {key: info}, or (None, problem)."""
    try:
        with open(path, encoding='utf-8', errors='replace') as handle:
            tree = ast.parse(handle.read())
    except (OSError, SyntaxError) as err:
        return None, f'{os.path.basename(path)}: could not parse ({err})'
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == '__artifacts_v2__' for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return None, f'{os.path.basename(path)}: __artifacts_v2__ is not a literal'
            return (value if isinstance(value, dict) else {}), None
    return {}, None


def _normal(text):
    return ' '.join(str(text).split()).lower()


def check_module(path):
    """(violations, problem) for one module. Each violation is (module, key, reason)."""
    blocks, problem = artifact_blocks(path)
    if blocks is None:
        return [], problem
    module = os.path.basename(path)
    violations = []
    seen = {}
    for key, info in blocks.items():
        if not isinstance(info, dict):
            continue
        description = info.get('description')
        if not isinstance(description, str):
            violations.append((module, key, 'description is missing or not a string'))
            continue
        if not description.strip():
            violations.append((module, key, 'description is empty'))
            continue
        if '\n' in description:
            violations.append((module, key, 'description runs to more than one line'))
        name = info.get('name')
        if isinstance(name, str) and _normal(name) == _normal(description):
            violations.append((module, key, 'description only repeats the name'))
        normal = _normal(description)
        if normal in seen:
            violations.append((module, key,
                               f'description duplicates {seen[normal]!r} in the same module'))
        else:
            seen[normal] = key
    return violations, None


def concession_sentences(notes):
    """The sentences of a notes field that concede a limit, for the review listing."""
    if not isinstance(notes, str):
        return []
    sentences = [s.strip() for s in re.split(r'(?<=[.])\s+', notes) if s.strip()]
    return [s for s in sentences if CONCESSION.search(s)]


def review(paths):
    """Print each description beside the limits its own notes concede. Never fails."""
    for path in paths:
        blocks, problem = artifact_blocks(path)
        print(f'\n{"=" * 78}\n{os.path.basename(path)}')
        if blocks is None:
            print(f'  {problem}')
            continue
        for key, info in blocks.items():
            if not isinstance(info, dict):
                continue
            print(f'\n  {key}')
            print(f'     description: {info.get("description")!r}')
            limits = concession_sentences(info.get('notes'))
            for sentence in limits[:8]:
                print(f'     notes limit: {sentence[:160]}')
            if not limits:
                print('     notes limit: (none conceded)')
    print('\nJudge each description against the limits beside it: it must not claim past them.')


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', default=None, help='repository root')
    parser.add_argument('--review', nargs='+', metavar='MODULE',
                        help='print each description beside its notes\' conceded limits '
                             'for the named artifact modules, and exit 0')
    args = parser.parse_args()

    root = args.root or os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifacts = os.path.join(root, 'scripts', 'artifacts')
    if not os.path.isdir(artifacts):
        print(f'No scripts/artifacts under {root}', file=sys.stderr)
        return 2

    if args.review:
        paths = []
        for name in args.review:
            base = name if name.endswith('.py') else name + '.py'
            candidate = base if os.path.isabs(base) else os.path.join(artifacts, os.path.basename(base))
            if not os.path.isfile(candidate):
                print(f'No such artifact module: {name}', file=sys.stderr)
                return 2
            paths.append(candidate)
        review(paths)
        return 0

    violations, unreadable, modules = [], [], 0
    for name in sorted(os.listdir(artifacts)):
        if not name.endswith('.py'):
            continue
        modules += 1
        found, problem = check_module(os.path.join(artifacts, name))
        violations.extend(found)
        if problem:
            unreadable.append(problem)

    if violations:
        print(f'Artifact descriptions that say nothing ({len(violations)}):')
        for module, key, reason in violations:
            print(f'  {module}::{key}  {reason}')
        print()
        print(STANDARD_NOTE)
        return 1

    summary = f'Checked {modules} artifact module(s): every description is present, one line, and its own.'
    if unreadable:
        summary += f' {len(unreadable)} module(s) NOT checked.'
    print(summary)
    for problem in unreadable:
        print(f'  {problem}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
