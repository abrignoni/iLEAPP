"""Guard the third return element against prose standing in for a path.

An artifact returns `(data_headers, data_list, source_path)`. The third element is
not decoration. `artifact_processor` splits it on newlines, passes each piece
through `Context.get_relative_path`, prints it as the report's

    <artifact name> located at: <source_path>

line, and writes it into the LAVA manifest as `source_path`. So it has to be real
paths, newline joined.

The defect this catches is a string constant standing in for one:

    return data_headers, data_list, 'See source file(s) below'   # WRONG
    return data_headers, data_list, 'Path column in the report'  # WRONG

It reads as helpful and it is not. It points the examiner at a column that often
holds a basename rather than a path, so the location of the evidence is nowhere in
the report, and the LAVA manifest records prose where a consumer expects a path.

The shape to write instead, accumulating after the function's own skip guards so a
file that was matched but not parsed is not claimed as a source:

    source_paths = set()
    for file_found in files_found:
        if <skip guard>:
            continue
        source_paths.add(str(file_found))
        ...
    return data_headers, data_list, '\\n'.join(sorted(source_paths))

Pass the full staged path. The wrapper reduces it for you; that is the one place
that reduction is done for the artifact.

Two things this deliberately does NOT fail on:

  * `''` on a branch that also returns an empty `data_list`. The wrapper writes no
    report at all when there are no rows, so that string never reaches a report.
    A "not found" message there is pointless but harmless, and `''` is correct.
  * A variable holding a real path, however it was built. Only string literals are
    reported, including a literal reached through a variable that is never assigned
    anything else.

Found by sweeping all five cores in 2026-08: 54 sites. iLEAPP had already been
swept once (PRs #2022 and #2024, 140 modules) and the class had come back in
ALEAPP and RLEAPP, which is why it is now a check rather than a sweep.

Usage:
  check_source_path.py [--root REPO_ROOT]

Exits 1 when anything is found, 0 otherwise.
"""

import argparse
import ast
import os
import sys

DECORATORS = {'artifact_processor', 'artifact_processor_streaming'}

STANDARD_NOTE = (
    "Return the paths the function actually parsed, newline joined: "
    "'\\n'.join(sorted(source_paths)). The wrapper makes them extraction relative."
)


def decorator_names(node):
    names = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.append(dec.attr)
        elif isinstance(dec, ast.Call):
            func = dec.func
            names.append(func.id if isinstance(func, ast.Name)
                         else getattr(func, 'attr', ''))
    return names


def returns_no_rows(node):
    """Whether this return also hands back an empty data_list literal."""
    rows = node.value.elts[1]
    return isinstance(rows, (ast.List, ast.Tuple)) and not rows.elts


def scan_function(func):
    """(line, text) for every literal masquerading as a source path."""
    triples = [n for n in ast.walk(func)
               if isinstance(n, ast.Return)
               and isinstance(n.value, ast.Tuple)
               and len(n.value.elts) == 3]
    found = []
    for ret in triples:
        tail = ret.value.elts[2]

        # Written straight into the return.
        if isinstance(tail, ast.Constant) and isinstance(tail.value, str):
            if tail.value and not returns_no_rows(ret):
                found.append((ret.lineno, tail.value))
            continue

        # The quiet spelling: a name that is only ever assigned string literals.
        if isinstance(tail, ast.Name):
            assigns = [a for a in ast.walk(func) if isinstance(a, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == tail.id
                               for t in a.targets)]
            if not assigns:
                continue
            values = [a.value for a in assigns]
            if not all(isinstance(v, ast.Constant) and isinstance(v.value, str)
                       for v in values):
                continue
            for text in sorted({v.value for v in values}):
                if text:
                    found.append((ret.lineno, text))
    return found


def scan_module(path):
    module = os.path.basename(path)
    try:
        with open(path, encoding='utf-8', errors='replace') as handle:
            tree = ast.parse(handle.read())
    except SyntaxError as err:
        return [], f'{module}: could not parse ({err})'
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not DECORATORS.intersection(decorator_names(node)):
            continue
        for line, text in scan_function(node):
            violations.append((module, node.name, line, text))
    return violations, None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', default=None, help='repository root')
    args = parser.parse_args()

    root = args.root or os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifacts = os.path.join(root, 'scripts', 'artifacts')
    if not os.path.isdir(artifacts):
        print(f'No scripts/artifacts under {root}', file=sys.stderr)
        return 2

    violations, unreadable, modules = [], [], 0
    for name in sorted(os.listdir(artifacts)):
        if not name.endswith('.py'):
            continue
        modules += 1
        found, problem = scan_module(os.path.join(artifacts, name))
        violations.extend(found)
        if problem:
            unreadable.append(problem)

    if violations:
        print(f'Artifacts returning prose as source_path ({len(violations)}):')
        for module, func, line, text in violations:
            print(f'  {module}:{line}  {func}()  {text!r}')
        print()
        print(STANDARD_NOTE)
        return 1

    summary = (f'Checked {modules} artifact module(s): '
               'no prose returned as a source path.')
    if unreadable:
        summary += f' {len(unreadable)} module(s) NOT checked.'
    print(summary)
    for problem in unreadable:
        print(f'  {problem}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
