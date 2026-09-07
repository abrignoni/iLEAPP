#!/usr/bin/env python3
"""Check that every artifact relying on a container marker declares one itself.

Some artifacts read a directory whose name belongs to a third party library rather
than to the application that owns the container, so they accept a file only when the
same container also holds a file the application itself writes. Those marker files
have to arrive through the artifact's own ``paths`` patterns: the framework builds
``files_found`` per artifact, so a marker declared by a sibling artifact is not
visible, and the marker set comes back empty.

An empty marker set is the failure this checks for. A guard that fails closed then
rejects every candidate and the artifact reports nothing, on exactly the images where
the application IS installed. Nothing raises, no row count moves on an image without
the app, and the run log line reads like a correct skip.

The check: for a module that declares a container marker constant, find every
artifact whose processor reaches the code that reads it, and require each of those
artifacts to declare a pattern that can match one of the markers.

Exit status is 1 when an artifact reaches the markers without declaring one.

Modules scope container reads in more than one way. This covers the explicit
``CONTAINER_MARKERS`` constant only, and prints the modules it could not analyse so a
clean pass is not read as covering the repository.
"""

import argparse
import ast
import os
import sys

ARTIFACT_DIR = os.path.join('scripts', 'artifacts')
MARKER_NAMES = ('CONTAINER_MARKERS', '_CONTAINER_MARKERS')

# Named so an unanalysed module is visible rather than silently passing.
CONTAINER_HINTS = ('container', '_roots', 'in_container')


def _artifacts(tree):
    """The __artifacts_v2__ mapping, or {} when the module has none."""
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__artifacts_v2__':
                try:
                    return ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    return {}
    return {}


def _marker_constants(tree):
    """{constant name: [marker strings]} for the module's marker declarations."""
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name) or target.id not in MARKER_NAMES:
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            if isinstance(value, (tuple, list)) and all(
                    isinstance(item, str) for item in value):
                found[target.id] = list(value)
    return found


def _functions(tree):
    """{function name: node} for the module's top level functions."""
    return {node.name: node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _names_used(node):
    """Every bare name referenced anywhere inside a function."""
    return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}


def _reaches_markers(functions, marker_names):
    """Function names that read a marker constant, directly or through a call.

    Resolved to a fixed point, so a processor three helpers away from the constant is
    still reported.
    """
    reaching = {name for name, node in functions.items()
                if _names_used(node) & marker_names}
    changed = True
    while changed:
        changed = False
        for name, node in functions.items():
            if name in reaching:
                continue
            if _names_used(node) & reaching:
                reaching.add(name)
                changed = True
    return reaching


def _declares_marker(paths, markers):
    """The markers an artifact's own path patterns could match."""
    if isinstance(paths, str):
        paths = (paths,)
    return [marker for marker in markers
            if any(marker in str(pattern) for pattern in paths)]


def _check_module(path, report):
    with open(path, encoding='utf-8') as handle:
        source = handle.read()
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        report['errors'].append(f'{os.path.basename(path)}: cannot parse: {error}')
        return

    module = os.path.basename(path)
    artifacts = _artifacts(tree)
    if not artifacts:
        return

    constants = _marker_constants(tree)
    functions = _functions(tree)

    if not constants:
        # Nothing to check here, but say so when the module looks container scoped,
        # so the absence of a finding is not mistaken for a clean result.
        if any(hint in name.lower() for name in functions for hint in CONTAINER_HINTS):
            report['unanalysed'].append(module)
        return

    markers = [marker for values in constants.values() for marker in values]
    reaching = _reaches_markers(functions, set(constants))
    report['analysed'].append(module)

    for name in sorted(artifacts):
        if name not in reaching:
            continue
        declared = _declares_marker(artifacts[name].get('paths', ()), markers)
        report['checked'] += 1
        if declared:
            report['ok'].append(f'{module}:{name}')
        else:
            report['failures'].append(
                f'{module}:{name} reaches {sorted(constants)[0]} but declares no marker '
                f'pattern in its own paths, so its marker set is always empty and a '
                f'guard that fails closed reports nothing. Add one of: '
                f'{", ".join(markers)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--artifacts-dir', default=ARTIFACT_DIR,
                        help='directory of artifact modules to check')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='list each artifact that passed')
    args = parser.parse_args()

    if not os.path.isdir(args.artifacts_dir):
        print(f'No artifact directory at {args.artifacts_dir}', file=sys.stderr)
        return 2

    report = {'analysed': [], 'unanalysed': [], 'checked': 0,
              'ok': [], 'failures': [], 'errors': []}
    for entry in sorted(os.listdir(args.artifacts_dir)):
        if entry.endswith('.py') and not entry.startswith('__'):
            _check_module(os.path.join(args.artifacts_dir, entry), report)

    for error in report['errors']:
        print(f'  ERROR    {error}')
    if args.verbose:
        for line in report['ok']:
            print(f'  ok       {line}')
    for failure in report['failures']:
        print(f'  FAIL     {failure}')

    print(f"Checked {report['checked']} artifact(s) in "
          f"{len(report['analysed'])} module(s) declaring container markers: "
          f"{', '.join(report['analysed']) or 'none'}.")
    if report['unanalysed']:
        print(f"{len(report['unanalysed'])} module(s) express container scoping another "
              f"way and are not analysed: {', '.join(report['unanalysed'])}.")
    if report['failures']:
        print(f"{len(report['failures'])} artifact(s) reach a container marker "
              f"without declaring one.")
        return 1
    print('No artifact reaches a container marker without declaring one.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
