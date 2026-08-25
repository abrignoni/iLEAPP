"""Guard report output against the examiner's own filesystem paths.

Every seeker copies a matched evidence file into a staging directory before an artifact
sees it:

    <report folder>/data/<evidence relative path>

so every entry in `files_found` is an ABSOLUTE path on the machine running the tool. It
carries the account name, the case folder and the report directory layout. None of that
belongs in a report that gets handed to someone else.

`artifact_processor` normalizes exactly one thing: the third element of an artifact's
return tuple. It splits that on newlines and passes each piece through
`Context.get_relative_path`, which strips the staging prefix.

    return data_headers, data_list, source_path      # <- normalized for you

NOTHING ELSE IS NORMALIZED. A value placed in a data row is written verbatim to the HTML
report, the TSV export, the timeline, the KML and the LAVA database, so a staged path put
in a column is published five ways and persisted in two of them. The same applies to a
path handed straight to `report.write_artifact_data_table`, whose third argument becomes
the page's "located at" line with no normalization at all.

The fix is always to reduce the value where it enters the row, never afterwards:

    data_list.append((ts, msg, context.get_relative_path(file_found)))   # correct
    data_list.append((ts, msg, file_found))                             # WRONG

`os.path.basename(...)` and `Path(...).name` are equally accepted when a bare filename is
what the column is for.

Two things make this defect invisible without a check like this one. The column is never
empty and the row count is always right, so no snapshot, row-count assertion or lint rule
notices. And `Context.get_relative_path` FAILS OPEN: given a path that does not carry the
staging prefix it returns the string unchanged rather than raising. The committed test
harness never sets `Context._data_folder`, so in that harness the function is a no-op and
a leaking artifact and a correct one record identical output. That is why this check reads
the source rather than a recorded baseline.

Scope: functions decorated with `artifact_processor` or `artifact_processor_streaming`,
which are the ones whose return value reaches a report. A helper that carries a full path
between functions is fine and is not reported; what matters is the value at the row.

Found by auditing all five cores in 2026-08: 38 sites across 31 artifacts, including all
16 Chromium artifacts in iLEAPP's chrome.py (which build their own per-browser reports and
so bypass the wrapper) and a 1,085-row LAVA column in appGrouplisting.

Usage:
  check_report_local_paths.py [--root REPO_ROOT] [--verbose]

Exits 1 when anything is found, 0 otherwise.

Allowlist
---------
A genuine exception goes in ALLOWLIST below, keyed "<module>.py:<function>:<expression>",
with a reason. Keep it short: a value that legitimately belongs in a column is nearly
always a filename or a device-internal path, and neither trips this check.
"""

import argparse
import ast
import os
import sys

# "<module>.py:<function>:<expression>" -> why this one is not a leak.
ALLOWLIST = {}

DECORATORS = {'artifact_processor', 'artifact_processor_streaming'}
STREAMING_DECORATOR = 'artifact_processor_streaming'

# Names that hold a full staged path when they come from the framework.
TAINT_PARAM_NAMES = {'files_found', 'file_found'}

# Calls returning a full staged path. Attribute calls are only taint sources when the
# receiver is the framework object, so `re.search(...)` and `message.walk()` are not
# mistaken for `seeker.search(...)` and `os.walk(...)`.
TAINT_PLAIN_CALLS = {'get_file_path'}
TAINT_ATTR_CALLS = {
    'search': {'seeker', 'self'},
    'walk': {'os'},
    'get_files_found': {'context', 'Context'},
    'get_report_folder': {'context', 'Context'},
    'get_source_file_path': {'context', 'Context'},
}

# Wrappers that return their argument unchanged for our purposes, whether written bare
# or through a module (`Path(x)`, `pathlib.Path(x)`, `os.path.abspath(x)`).
PASSTHROUGH_CALLS = {
    'str', 'Path', 'PurePath', 'PurePosixPath', 'PureWindowsPath',
    'sorted', 'set', 'list', 'tuple', 'abspath', 'realpath', 'normpath',
}

# Calls and attributes that reduce a full path to something publishable.
SANITIZERS = {
    'basename', 'get_relative_path', 'relative_to', 'sanitize_report_name',
    'safe_local_path', 'check_in_media',
}
# Attributes that yield a NAME or a component rather than a path. `parents` is
# deliberately absent: `Path(p).parents[1]` is a full directory path and has leaked.
SAFE_ATTRS = {'name', 'stem', 'suffix', 'parts'}
# Methods whose result is a piece of the string, not the whole path.
SAFE_METHODS = {'split', 'rsplit', 'partition', 'rpartition', 'replace', 'strip'}

ROW_VARS = ('data_list', 'data_rows', 'rows', 'records', 'entries')

STANDARD_NOTE = (
    'Reduce the value where it enters the row: context.get_relative_path(x) for a path, '
    'or os.path.basename(x) when the column is a filename. The third element of the '
    'return tuple is normalized for you and does not need this.'
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
            names.append(func.id if isinstance(func, ast.Name) else getattr(func, 'attr', ''))
    return names


def receiver_name(node):
    """The left-hand name of an attribute access, or ''."""
    value = node.value
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Attribute):
        return value.attr
    return ''


class FunctionScan:
    """Taint over one artifact function."""

    def __init__(self, func):
        self.func = func
        self.tainted = self._collect()

    def is_tainted(self, node):
        if node is None:
            return False
        if isinstance(node, ast.Name):
            return node.id in self.tainted
        if isinstance(node, ast.Subscript):
            # x[0] of a tainted container is still a path; a component of .parts is not.
            if isinstance(node.value, ast.Attribute) and node.value.attr in SAFE_ATTRS:
                return False
            return self.is_tainted(node.value)
        if isinstance(node, ast.Attribute):
            if node.attr in SANITIZERS or node.attr in SAFE_ATTRS:
                return False
            return self.is_tainted(node.value)
        if isinstance(node, ast.Call):
            return self._call_tainted(node)
        if isinstance(node, ast.JoinedStr):
            return any(self.is_tainted(part.value) for part in node.values
                       if isinstance(part, ast.FormattedValue))
        if isinstance(node, ast.BinOp):
            return self.is_tainted(node.left) or self.is_tainted(node.right)
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            return any(self.is_tainted(gen.iter) for gen in node.generators)
        return False

    @staticmethod
    def _sanitizes(node):
        """Whether this expression is an explicit reduction of a path."""
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, 'id', '')
            return name in SANITIZERS or name in SAFE_METHODS
        if isinstance(node, ast.Attribute):
            return node.attr in SAFE_ATTRS
        return False

    def _call_tainted(self, node):
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, 'id', '')
        if name in SANITIZERS or name in SAFE_METHODS:
            return False
        # Wrappers that hand back whatever they were given. Reached as a bare name
        # (`Path(x)`) or through a module (`pathlib.Path(x)`, `os.path.abspath(x)`).
        if name in PASSTHROUGH_CALLS:
            return any(self.is_tainted(a) for a in node.args)
        if isinstance(func, ast.Attribute):
            if name in TAINT_ATTR_CALLS and receiver_name(func) in TAINT_ATTR_CALLS[name]:
                return True
            if name == 'join':
                # os.path.join(tainted, ...) is still a full path.
                return any(self.is_tainted(a) for a in node.args)
            return False
        return name in TAINT_PLAIN_CALLS

    def _collect(self):
        tainted = {a.arg for a in self.func.args.args if a.arg in TAINT_PARAM_NAMES}
        for _ in range(8):
            before = len(tainted)
            self.tainted = tainted
            for node in ast.walk(self.func):
                if isinstance(node, ast.For):
                    if self.is_tainted(node.iter) or (
                            isinstance(node.iter, ast.Name)
                            and node.iter.id in TAINT_PARAM_NAMES):
                        if isinstance(node.target, ast.Name):
                            tainted.add(node.target.id)
                elif isinstance(node, ast.Assign):
                    if self.is_tainted(node.value):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                tainted.add(target.id)
                    elif self._sanitizes(node.value):
                        # Only an explicit reduction clears taint. A bare
                        # `db_files = []` must not, or it races the later
                        # `db_files.append(file_found)` on every pass and the
                        # loop over that list is never seen as tainted.
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                tainted.discard(target.id)
                elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                    call = node.value
                    # A list built by appending a tainted value is itself tainted, so
                    # iterating it later yields tainted names.
                    if (isinstance(call.func, ast.Attribute)
                            and call.func.attr in ('append', 'add', 'extend')
                            and isinstance(call.func.value, ast.Name)
                            and call.args and self.is_tainted(call.args[0])):
                        tainted.add(call.func.value.id)
            if len(tainted) == before:
                break
        self.tainted = tainted
        return tainted


def scan_function(func, module, streaming):
    """Violations for one decorated artifact function."""
    scan = FunctionScan(func)
    if not scan.tainted:
        return []
    found = []

    def record(line, kind, expr, column):
        key = f'{module}:{func.name}:{expr}'
        if key in ALLOWLIST:
            return
        found.append((line, kind, expr, column))

    for node in ast.walk(func):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'write_artifact_data_table' and len(node.args) >= 3):
            if scan.is_tainted(node.args[2]):
                record(node.lineno, 'located-at', ast.unparse(node.args[2]), None)

        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ('append', 'extend') and node.args):
            target = node.func.value
            name = target.id if isinstance(target, ast.Name) else ''
            if not any(hint in name.lower() for hint in ROW_VARS):
                continue
            arg = node.args[0]
            elements = arg.elts if isinstance(arg, (ast.Tuple, ast.List)) else [arg]
            for index, element in enumerate(elements):
                if scan.is_tainted(element):
                    record(node.lineno, 'row-value', ast.unparse(element), index)

        if streaming and isinstance(node, ast.Expr) and isinstance(node.value, ast.Yield):
            value = node.value.value
            if isinstance(value, (ast.Tuple, ast.List)):
                for index, element in enumerate(value.elts):
                    if scan.is_tainted(element):
                        record(node.lineno, 'yielded-row', ast.unparse(element), index)
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
        decorators = decorator_names(node)
        if not DECORATORS.intersection(decorators):
            continue
        streaming = STREAMING_DECORATOR in decorators
        for line, kind, expr, column in scan_function(node, module, streaming):
            violations.append((module, node.name, line, kind, expr, column))
    return violations, None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', default=None, help='repository root')
    parser.add_argument('--verbose', action='store_true',
                        help='list every artifact function checked')
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

    if args.verbose:
        for module, func, line, kind, expr, column in violations:
            print(f'{module}:{line} {func} {kind} {expr}')

    if violations:
        print(f'Local filesystem paths reaching report output ({len(violations)}):')
        for module, func, line, kind, expr, column in violations:
            where = f'column {column}' if column is not None else '"located at" line'
            print(f'  {module}:{line}  {func}()  {kind}  {where}')
            print(f'      {expr}')
        print()
        print(STANDARD_NOTE)
        if ALLOWLIST:
            print(f'{len(ALLOWLIST)} allowlisted expression(s) were not reported.')
        return 1

    summary = f'Checked {modules} artifact module(s): no local paths reach report output.'
    if unreadable:
        summary += f' {len(unreadable)} module(s) NOT checked.'
    print(summary)
    for problem in unreadable:
        print(f'  {problem}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
