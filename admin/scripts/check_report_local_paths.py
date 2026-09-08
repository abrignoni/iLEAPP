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

Two shapes hid a path from this check until 2026-09, and both have to keep failing here.
A path handed to a formatter came back untracked, so `textwrap.fill(file_found)` reported
clean while publishing the absolute path. And `strip` sat among the methods treated as
reducing a path, though it hands back the whole string, so `file_found.strip()` cleared
the taint too. ALEAPP's torrentinfo carried both at once.

A third audit, 2026-09-06, scanned real report output instead of source and found 122
leaking cells in four ALEAPP modules that this check had passed. Three gaps, all now
closed and pinned in the test file:

  * `unique_files(context)`, the storage-view dedupe helper artifacts are told to use,
    was not a taint source, so `for file_found in unique_files(context)` was untainted
    despite the name. torThumbs and three xiaohongshu artifacts leaked through it.
  * `or`, `and` and `x if c else y` were not propagated, so `source = source or
    file_found` cleared the taint. xiaohongshu's account artifact leaked through it.
  * Taint stopped at a function boundary. A module-level helper that returns a staged
    path, or records carrying one, is now a taint source for the functions that call it,
    tracked by tuple position so the other fields of a record stay untainted. Tuple
    unpacking in `for` and assignment, `+=`, `:=` and subscript stores propagate too.

The framework helper that leaked the accounts artifacts lives in ilapfuncs.py and is
outside this check's scope; that one is pinned by its own unit test.

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
TAINT_PLAIN_CALLS = {'get_file_path', 'unique_files'}
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

# Formatters that hand back a rewrapped copy of what they were given. A path put through
# one of these is still that path, so the taint has to survive the call.
REFORMATTING_CALLS = {'fill', 'shorten', 'indent', 'dedent'}

# Calls and attributes that reduce a full path to something publishable.
SANITIZERS = {
    'basename', 'get_relative_path', 'relative_to', 'sanitize_report_name',
    'safe_local_path', 'check_in_media',
}
# Attributes that yield a NAME or a component rather than a path. `parents` is
# deliberately absent: `Path(p).parents[1]` is a full directory path and has leaked.
SAFE_ATTRS = {'name', 'stem', 'suffix', 'parts'}
# Methods whose result is a PIECE of the string. `strip` and `replace` are deliberately
# absent: both hand back the whole path, so neither reduces it to anything publishable.
PATH_REDUCING_METHODS = {'split', 'rsplit', 'partition', 'rpartition'}

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


WHOLE = 'whole'   # a helper whose whole return value is a staged path or a list of them


def _names_in_target(target):
    """Every plain name bound by an assignment or loop target, with its tuple position.

    `a` binds position 0 and `(a, b)` binds a at 0 and b at 1. A nested tuple flattens
    to its outer position, which is the conservative reading."""
    if isinstance(target, ast.Name):
        return [(target.id, 0)]
    if isinstance(target, (ast.Tuple, ast.List)):
        out = []
        for index, element in enumerate(target.elts):
            if isinstance(element, ast.Starred):
                element = element.value
            for name, _pos in _names_in_target(element):
                out.append((name, index))
        return out
    return []


class FunctionScan:
    """Taint over one artifact function.

    `tainted` is the set of names holding a staged path or a container of them.
    `positions` maps a name holding records (tuples) to the tuple indexes that carry a
    path, so unpacking `for path, rows in records` taints `path` and not `rows`.
    `helpers` maps a module-level function name to WHOLE or a frozenset of positions,
    for helpers whose return value carries a staged path."""

    def __init__(self, func, helpers=None):
        self.func = func
        self.helpers = helpers or {}
        self.positions = {}
        # Names unpacked from a tainted record whose path position is unknown. They are
        # tracked so nothing downstream is mistaken for clean, but they are never
        # reported: a database row read from a store path is not itself a path.
        self.possible = set()
        self.tainted = self._collect()

    def is_tainted(self, node):
        if node is None:
            return False
        if isinstance(node, ast.Name):
            return node.id in self.tainted and node.id not in self.positions
        if isinstance(node, ast.Subscript):
            # x[0] of a tainted container is still a path; a component of .parts is not.
            if isinstance(node.value, ast.Attribute) and node.value.attr in SAFE_ATTRS:
                return False
            if isinstance(node.slice, ast.Slice):
                return False
            positions = self._positions_of(node.value)
            if positions is not None:
                return isinstance(node.slice, ast.Constant) and node.slice.value in positions
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
        if isinstance(node, ast.BoolOp):
            # `a or b` and `a and b` evaluate to one of their operands.
            return any(self.is_tainted(value) for value in node.values)
        if isinstance(node, ast.IfExp):
            return self.is_tainted(node.body) or self.is_tainted(node.orelse)
        if isinstance(node, ast.NamedExpr):
            return self.is_tainted(node.value)
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            return self._comprehension_tainted(node)
        if isinstance(node, (ast.Tuple, ast.List)):
            return any(self.is_tainted(element) for element in node.elts)
        return False

    def _comprehension_tainted(self, node):
        """A comprehension is tainted when its ELEMENT is, with the loop names it binds
        from a tainted iterable counted as tainted. `[basename(p) for p in files_found]`
        is a list of names, not of paths, and must not taint what it feeds."""
        bound = set()
        for gen in node.generators:
            if self.is_tainted(gen.iter) or self._positions_of(gen.iter) is not None \
                    or (isinstance(gen.iter, ast.Name) and gen.iter.id in TAINT_PARAM_NAMES):
                positions = self._positions_of(gen.iter)
                for name, index in _names_in_target(gen.target):
                    if positions is None or index in positions \
                            or isinstance(gen.target, ast.Name):
                        bound.add(name)
        if not bound:
            return False
        saved = self.tainted
        self.tainted = saved | bound
        try:
            return self.is_tainted(node.elt)
        finally:
            self.tainted = saved

    def _possible(self, node):
        """Whether `node` could carry a path, counting `possible` names as tainted."""
        saved = self.tainted
        self.tainted = saved | self.possible
        try:
            return self.is_tainted(node)
        finally:
            self.tainted = saved

    def _positions_of(self, node):
        """The tuple positions carrying a path when `node` yields records, else None."""
        if isinstance(node, ast.Name):
            return self.positions.get(node.id)
        if isinstance(node, (ast.Tuple, ast.List)):
            hit = frozenset(i for i, e in enumerate(node.elts) if self.is_tainted(e))
            return hit or None
        if isinstance(node, (ast.ListComp, ast.GeneratorExp)) \
                and isinstance(node.elt, (ast.Tuple, ast.List)):
            bound = set()
            for gen in node.generators:
                if self.is_tainted(gen.iter) or (isinstance(gen.iter, ast.Name)
                                                and gen.iter.id in TAINT_PARAM_NAMES):
                    bound |= {n for n, _i in _names_in_target(gen.target)}
            if not bound:
                return None
            saved = self.tainted
            self.tainted = saved | bound
            try:
                hit = frozenset(i for i, e in enumerate(node.elt.elts) if self.is_tainted(e))
            finally:
                self.tainted = saved
            return hit or None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            spec = self.helpers.get(node.func.id)
            if isinstance(spec, frozenset):
                return spec
        return None

    @staticmethod
    def _sanitizes(node):
        """Whether this expression is an explicit reduction of a path."""
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, 'id', '')
            return name in SANITIZERS or name in PATH_REDUCING_METHODS
        if isinstance(node, ast.Attribute):
            return node.attr in SAFE_ATTRS
        return False

    @staticmethod
    def _strips_data_folder(node):
        """`x.replace(seeker.data_folder, '')` is get_relative_path written by hand."""
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'replace' and node.args):
            return False
        first = node.args[0]
        return ((isinstance(first, ast.Attribute) and first.attr == 'data_folder')
                or (isinstance(first, ast.Call) and isinstance(first.func, ast.Attribute)
                    and first.func.attr == 'get_data_folder'))

    def _call_tainted(self, node):
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, 'id', '')
        if name in SANITIZERS or name in PATH_REDUCING_METHODS:
            return False
        if self._strips_data_folder(node):
            return False
        # Wrappers and formatters that hand back whatever they were given. Reached as a
        # bare name (`Path(x)`) or through a module (`pathlib.Path(x)`,
        # `os.path.abspath(x)`, `textwrap.fill(x)`).
        if name in PASSTHROUGH_CALLS or name in REFORMATTING_CALLS:
            return any(self.is_tainted(a) for a in node.args)
        if isinstance(func, ast.Attribute):
            if name in TAINT_ATTR_CALLS and receiver_name(func) in TAINT_ATTR_CALLS[name]:
                return True
            if name in ('join', 'format'):
                # os.path.join(tainted, ...) is still a full path, and a path
                # interpolated by str.format is still inside the string returned.
                return any(self.is_tainted(a) for a in node.args)
            # Any other method called ON a path returns something derived from that path,
            # so the taint survives. Only PATH_REDUCING_METHODS above cuts it down.
            return self.is_tainted(func.value)
        if name in TAINT_PLAIN_CALLS:
            return True
        # A module-level helper whose whole return value is a path or a list of paths.
        # One returning records is tracked by position instead, see _positions_of.
        return self.helpers.get(name) == WHOLE

    def _bind(self, target, value, tainted):
        """Taint the names a target binds from `value`, by position where known."""
        names = _names_in_target(target)
        if not names:
            return
        if isinstance(target, ast.Name):
            positions = self._positions_of(value)
            if isinstance(value, (ast.Tuple, ast.List)) and positions is not None:
                # `record = (name, path)` holds a path at one position, not everywhere.
                tainted.add(target.id)
                self.positions[target.id] = positions
                return
            if self.is_tainted(value):
                tainted.add(target.id)
                if positions is not None:
                    self.positions[target.id] = positions
            elif self._positions_of(value) is not None:
                self.positions[target.id] = self._positions_of(value)
            elif self._possible(value):
                self.possible.add(target.id)
            return
        # Tuple target. A tuple literal of the same length binds position by position;
        # a record source binds only its path positions; anything else tainted binds all.
        if isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(target.elts):
            for element, source in zip(target.elts, value.elts):
                self._bind(element, source, tainted)
            return
        positions = self._positions_of(value)
        if positions is not None:
            for name, index in names:
                if index in positions:
                    tainted.add(name)
            return
        if self.is_tainted(value) or self._possible(value):
            for name, _index in names:
                self.possible.add(name)

    def _collect(self):
        tainted = {a.arg for a in self.func.args.args if a.arg in TAINT_PARAM_NAMES}
        for _ in range(8):
            before = (len(tainted), len(self.possible),
                      sum(len(v) for v in self.positions.values()))
            self.tainted = tainted
            for node in ast.walk(self.func):
                if isinstance(node, (ast.For, ast.comprehension)):
                    iterable = node.iter
                    is_source = (isinstance(iterable, ast.Name)
                                 and iterable.id in TAINT_PARAM_NAMES)
                    certain = is_source or self.is_tainted(iterable)
                    if certain or self._positions_of(iterable) is not None \
                            or self._possible(iterable):
                        # Each item of a record source is a record; bind its positions.
                        positions = self._positions_of(iterable)
                        if positions is not None and not isinstance(node.target, ast.Name):
                            for name, index in _names_in_target(node.target):
                                if index in positions:
                                    tainted.add(name)
                        elif positions is not None:
                            tainted.add(node.target.id)
                            self.positions[node.target.id] = positions
                        elif isinstance(node.target, ast.Name) and certain:
                            # An item of a list of paths is a path.
                            tainted.add(node.target.id)
                        else:
                            # A record with no known path position, or an item of a
                            # possibly tainted iterable: track, do not report.
                            for name, _index in _names_in_target(node.target):
                                self.possible.add(name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Subscript) \
                                and isinstance(target.value, ast.Name):
                            # store['k'] = path taints the container.
                            if self.is_tainted(node.value):
                                tainted.add(target.value.id)
                            continue
                        if self.is_tainted(node.value) \
                                or self._positions_of(node.value) is not None \
                                or self._possible(node.value):
                            self._bind(target, node.value, tainted)
                        elif self._sanitizes(node.value):
                            # Only an explicit reduction clears taint. A bare
                            # `db_files = []` must not, or it races the later
                            # `db_files.append(file_found)` on every pass of the
                            # fixed point and the loop over that list is never seen
                            # as tainted.
                            for name, _index in _names_in_target(target):
                                tainted.discard(name)
                elif isinstance(node, ast.AugAssign):
                    if isinstance(node.target, ast.Name):
                        if self.is_tainted(node.value):
                            tainted.add(node.target.id)
                        elif self._possible(node.value):
                            self.possible.add(node.target.id)
                elif isinstance(node, ast.NamedExpr):
                    if self.is_tainted(node.value):
                        tainted.add(node.target.id)
                    elif self._possible(node.value):
                        self.possible.add(node.target.id)
                elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                    call = node.value
                    # A list built by appending a tainted value is itself tainted, so
                    # iterating it later yields tainted names. Appending a record
                    # remembers which positions carry the path.
                    if (isinstance(call.func, ast.Attribute)
                            and call.func.attr in ('append', 'add', 'extend')
                            and isinstance(call.func.value, ast.Name)
                            and call.args):
                        container = call.func.value.id
                        arg = call.args[0]
                        if isinstance(arg, (ast.Tuple, ast.List)) \
                                and call.func.attr != 'extend':
                            hit = {i for i, e in enumerate(arg.elts) if self.is_tainted(e)}
                            if hit:
                                tainted.add(container)
                                self.positions[container] = \
                                    frozenset(self.positions.get(container, frozenset()) | hit)
                        elif self._positions_of(arg) is not None and call.func.attr != 'extend':
                            tainted.add(container)
                            self.positions[container] = frozenset(
                                self.positions.get(container, frozenset()) | self._positions_of(arg))
                        elif call.func.attr == 'extend' and self._positions_of(arg) is not None:
                            tainted.add(container)
                            self.positions[container] = frozenset(
                                self.positions.get(container, frozenset()) | self._positions_of(arg))
                        elif self.is_tainted(arg):
                            tainted.add(container)
                            self.positions.pop(container, None)
            after = (len(tainted), len(self.possible),
                     sum(len(v) for v in self.positions.values()))
            if after == before:
                break
        self.tainted = tainted
        return tainted

    def return_spec(self):
        """WHOLE, a frozenset of record positions, or None, for what this function returns.

        Used to decide whether a module-level helper is a taint source for its callers."""
        spec = set()
        for node in ast.walk(self.func):
            if isinstance(node, (ast.Return, ast.Yield)) and node.value is not None:
                value = node.value
                positions = self._positions_of(value)
                if isinstance(value, (ast.Tuple, ast.List)):
                    hit = {i for i, e in enumerate(value.elts) if self.is_tainted(e)}
                    if hit:
                        spec |= hit
                elif positions is not None:
                    spec |= set(positions)
                elif self.is_tainted(value):
                    return WHOLE
        return frozenset(spec) if spec else None


def helper_sources(tree):
    """Module-level undecorated functions whose return carries a staged path.

    Their bodies are not scanned for rows (a helper handing a full path between
    functions is normal); what matters is that a caller receiving that path treats it
    as one. Helpers calling helpers are resolved by iterating to a fixed point."""
    helpers = {}
    candidates = [node for node in tree.body
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and not DECORATORS.intersection(decorator_names(node))]
    for _ in range(4):
        before = dict(helpers)
        for func in candidates:
            spec = FunctionScan(func, helpers).return_spec()
            if spec is not None:
                helpers[func.name] = spec
        if helpers == before:
            break
    return helpers


def row_containers(func, streaming):
    """Names whose contents reach the report: the second element of a returned tuple,
    the second argument of write_artifact_data_table, a yielded name, and anything
    extended into one of those. Empty when the function gives no such signal, in
    which case the name hints alone decide."""
    roots = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Return) and isinstance(node.value, (ast.Tuple, ast.List)) \
                and len(node.value.elts) >= 2 and isinstance(node.value.elts[1], ast.Name):
            roots.add(node.value.elts[1].id)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'write_artifact_data_table' and len(node.args) >= 2
                and isinstance(node.args[1], ast.Name)):
            roots.add(node.args[1].id)
        if streaming and isinstance(node, ast.Yield) and isinstance(node.value, ast.Name):
            roots.add(node.value.id)
    if not roots:
        return None
    for _ in range(4):
        before = len(roots)
        for node in ast.walk(func):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == 'extend' and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in roots and node.args
                    and isinstance(node.args[0], ast.Name)):
                roots.add(node.args[0].id)
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Name) \
                    and node.value.id in roots:
                roots |= {n for n, _i in _names_in_target(node.targets[0])}
        if len(roots) == before:
            break
    return roots


def scan_function(func, module, streaming, helpers=None):
    """Violations for one decorated artifact function."""
    scan = FunctionScan(func, helpers)
    if not scan.tainted:
        return []
    found = []
    reaching = row_containers(func, streaming)

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
            if reaching is not None and name not in reaching:
                # A working list that never reaches the report, however it is named.
                continue
            arg = node.args[0]
            if isinstance(arg, (ast.Tuple, ast.List)):
                elements = list(enumerate(arg.elts))
            elif scan._positions_of(arg) is not None:  # pylint: disable=protected-access
                # A whole record appended by name: its path positions are the columns.
                elements = [(i, arg) for i in sorted(scan._positions_of(arg))]  # pylint: disable=protected-access
                for index, _ in elements:
                    record(node.lineno, 'row-value', f'{ast.unparse(arg)}[{index}]', index)
                continue
            else:
                elements = [(0, arg)]
            for index, element in elements:
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
    helpers = helper_sources(tree)
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = decorator_names(node)
        if not DECORATORS.intersection(decorators):
            continue
        streaming = STREAMING_DECORATOR in decorators
        for line, kind, expr, column in scan_function(node, module, streaming, helpers):
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
