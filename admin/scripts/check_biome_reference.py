"""Check Biome modules against the saved Apple framework reference.

admin/data/biome_framework_reference.json holds the stream, class, field and enum names
read from BiomeLibrary and CoreDuet on macOS 27.2.1 (26B131). This check compares what
each Biome module states with it:

  * stream: a class the artifact's notes name against the streams in its paths
  * field: each typedef field's wire type
  * field_name: a field number and Apple field name stated together in a comment or notes
  * enum: each number-to-name table
  * version_enum: a table that follows a record's data version
  * dk_label: a _DKEvent metadata index-to-label table

Every item ends in one of three outcomes. Only "different" fails the run.

  confirmed        the reference has the item and agrees
  different        the reference has the item and contradicts it
  could not check  the reference has nothing to compare, or the binding is ambiguous

An item missing from the reference is not a contradiction. The reference comes from one
macOS build, so a stream or field from another OS version can be missing from it.

A deliberate exception goes in admin/data/biome_reference_exceptions.json, keyed to the
exact module, kind, item and key, with the stored value and a reason. An exception that
matches nothing fails the run, so it cannot outlive the code it covers.
"""
import argparse
import ast
import collections
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REFERENCE = os.path.join(REPO_ROOT, 'admin', 'data', 'biome_framework_reference.json')
EXCEPTIONS = os.path.join(REPO_ROOT, 'admin', 'data', 'biome_reference_exceptions.json')

CONFIRMED, DIFFERENT, UNCHECKED = 'confirmed', 'different', 'could not check'
KINDS = ('stream', 'field', 'field_name', 'enum', 'version_enum', 'dk_label')

# scripts/blackboxprotobuf/lib/types/type_maps.py WIRETYPES
TYPE_WIRE = {'uint': 0, 'int': 0, 'sint': 0, 'fixed32': 5, 'sfixed32': 5, 'float': 5,
             'fixed64': 1, 'sfixed64': 1, 'double': 1, 'bytes': 2, 'str': 2, 'string': 2,
             'bytes_hex': 2, 'message': 2}
SEGMENT = re.compile(r'streams/(?:\*|public|restricted|private)?/?([A-Za-z0-9_.\-]+)/(?:local|remote|\*)')
NOTE_CLASS = re.compile(r'\b(_?BM[A-Z][A-Za-z0-9]+) class\b')
CITED = re.compile(r'\b_?(BM[A-Z][A-Za-z0-9]+)\b')
VERSION_NAME = re.compile(r'_V\d+$')
FIELD_STATEMENTS = (
    (re.compile(r'\bfield (\d+) \(([a-z][A-Za-z0-9]+)\)'), 1, 2),
    (re.compile(r'\bfield (\d+),? ([a-z]+[A-Z][A-Za-z0-9]+)\b'), 1, 2),
    (re.compile(r'\b([a-z][A-Za-z0-9]+) \(field (\d+)\)'), 2, 1),
    (re.compile(r'\b([a-z]+[A-Z][A-Za-z0-9]+),? field (\d+)\b'), 2, 1),
    (re.compile(r'^\s*#\s*(\d+)\s*->.*\(([a-z][A-Za-z0-9]+)\)\s*$', re.M), 1, 2),
)
DK_EVENT_CLASS = '_DKPREvent'
DK_FLOOR = 1000


Item = collections.namedtuple('Item', 'module kind item key status detail')


def norm(text):
    return re.sub(r'[^a-z0-9]', '', str(text).lower())


def common_prefix(names):
    """The normalized prefix every name of a reference enum shares."""
    return os.path.commonprefix([norm(n) for n in names]) if len(names) >= 2 else ''


def same_name(stated, reference, prefix=''):
    """A module may space or drop the enum's shared prefix for the reader; that is not a conflict."""
    one, two = norm(stated), norm(reference)
    if not one or not two:
        return False
    return one == two or (bool(prefix) and two.startswith(prefix) and one == two[len(prefix):])


class Reference:
    def __init__(self, data):
        self.streams = data['streams']
        self.classes = {name: {row[0]: row for row in rows} for name, rows in data['classes'].items()}
        self.enums = {key: {int(k): v for k, v in table.items()} for key, table in data['enums'].items()}
        self.versioned = {key: {int(k): v for k, v in table.items()}
                          for key, table in data['versioned_enums'].items()}
        self.dk_metadata = {int(k): v for k, v in data['dk_metadata'].items()}
        self.by_segment = {}
        for sid, stream in self.streams.items():
            self.by_segment[sid] = sid
            for legacy in stream['legacy']:
                self.by_segment.setdefault(legacy, sid)

    def reach(self, names):
        seen, todo = set(), [n for n in names if n in self.classes]
        while todo:
            name = todo.pop()
            if name in seen:
                continue
            seen.add(name)
            todo.extend(row[3] for row in self.classes[name].values()
                         if row[3] and row[3] in self.classes)
        return seen

    def stream_class(self, segment):
        sid = self.by_segment.get(segment)
        return self.streams[sid]['class'] if sid else None

    def typedef_class(self, segment):
        if segment.startswith('_DKEvent.'):
            return DK_EVENT_CLASS
        return self.stream_class(segment)

    def scoped(self, table, scope, cited, segments=()):
        out = {}
        for key, val in table.items():
            owner = key.split('.')[0]
            if owner in scope or any(key.startswith(c) for c in cited) or any(
                    key.startswith(f'{s}.') for s in segments):
                out[key] = val
        return out


def compare_table(table, candidates):
    """Return (status, candidate, conflicts) for an {int: name} table.

    The candidate that agrees on the most entries is the binding, so a smaller enum that
    happens to share two names cannot vouch for a table with a wrong third name.
    """
    scored = []
    for key, ref in candidates.items():
        prefix = common_prefix(list(ref.values()))
        shared = [k for k in table if k in ref]
        conflicts = [k for k in shared if not same_name(table[k], ref[k], prefix)]
        scored.append((len(shared) - len(conflicts), key, conflicts))
    if not scored:
        return UNCHECKED, None, []
    top = max(row[0] for row in scored)
    if top < 2:
        return UNCHECKED, None, []
    best = [row for row in scored if row[0] == top]
    clean = [row for row in best if not row[2]]
    if clean:
        return CONFIRMED, clean[0][1], []
    # The same enum can be saved twice (a field's table and its AsString function). Tied
    # candidates are one binding when they say the same thing about the disputed entries.
    readings = {tuple((k, candidates[row[1]][k]) for k in row[2]) for row in best}
    if len(readings) == 1 and top >= len(best[0][2]):
        return DIFFERENT, best[0][1], best[0][2]
    return UNCHECKED, None, []


def literal_table(node):
    """An {int: str} dict, or a tuple/list of strings read as positions."""
    if isinstance(node, ast.Dict) and len(node.keys) >= 2:
        pairs = {}
        for key, val in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and type(key.value) is int):
                return None
            if not (isinstance(val, ast.Constant) and isinstance(val.value, str)):
                return None
            pairs[key.value] = val.value
        return pairs
    if isinstance(node, (ast.Tuple, ast.List)) and len(node.elts) >= 3:
        if all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts):
            return {i: e.value for i, e in enumerate(node.elts)}
    return None


def is_typedef(node):
    if not isinstance(node, ast.Dict) or not node.keys:
        return False
    typed = 0
    for key, val in zip(node.keys, node.values):
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str) and key.value.isdigit()):
            return False
        if isinstance(val, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == 'type'
                                             for k in val.keys):
            typed += 1
    return typed > 0


def field_spec(node):
    spec = {}
    for key, val in zip(node.keys, node.values):
        if isinstance(key, ast.Constant):
            spec[key.value] = val
    return spec


def constant(node):
    return node.value if isinstance(node, ast.Constant) else None


def artifacts_of(tree):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == '__artifacts_v2__' for t in node.targets):
            try:
                return ast.literal_eval(node.value)
            except ValueError:
                return {}
    return {}


def path_segments(entry):
    paths = entry.get('paths') or ()
    paths = (paths,) if isinstance(paths, str) else paths
    found = set()
    for pattern in paths:
        found.update(SEGMENT.findall(pattern))
    return found


class ModuleCheck:
    def __init__(self, reference, path):
        self.ref = reference
        self.module = os.path.basename(path)
        with open(path, encoding='utf-8', errors='replace') as handle:
            self.source = handle.read()
        self.tree = ast.parse(self.source)
        self.artifacts = artifacts_of(self.tree)
        self.items = []
        self.segments = {name: path_segments(entry) for name, entry in self.artifacts.items()
                         if isinstance(entry, dict)}
        every = set().union(*self.segments.values()) if self.segments else set()
        self.every_segment = every
        self.all_classes = {self.ref.typedef_class(s) for s in every} - {None}
        cited = set(CITED.findall(self.source))
        self.cited_classes = {c for c in cited if c in self.ref.classes}
        self.cited_tables = {c for c in cited if c.endswith('AsString')}
        self.scope = self.ref.reach(self.all_classes | self.cited_classes)
        self.is_dk = any(s.startswith('_DKEvent') for s in every) or 'METADATA_KEYS' in self.source

    def add(self, kind, item, key, status, detail=''):
        self.items.append(Item(self.module, kind, item, str(key), status, detail))

    def run(self):
        self.check_streams()
        self.check_typedefs()
        self.check_field_statements()
        self.check_tables()
        return self.items

    def check_streams(self):
        for name, entry in self.artifacts.items():
            if not isinstance(entry, dict):
                continue
            segments = self.segments[name]
            classes = {self.ref.stream_class(s) for s in segments}
            for segment in sorted(segments):
                status = CONFIRMED if self.ref.stream_class(segment) else UNCHECKED
                self.add('stream', name, segment, status)
            notes = str(entry.get('notes') or '')
            reach = self.ref.reach(classes - {None})
            for stated in sorted({c.lstrip('_') for c in NOTE_CLASS.findall(notes)}):
                if stated not in self.ref.classes or not segments or None in classes:
                    status, detail = UNCHECKED, ''
                elif stated in reach:
                    status, detail = CONFIRMED, ''
                else:
                    status = DIFFERENT
                    detail = f'notes name {stated}; its streams use {sorted(classes)}'
                self.add('stream', name, f'class {stated}', status, detail)

    def typedef_classes(self, function):
        if function and function in self.segments:
            found = {self.ref.typedef_class(s) for s in self.segments[function]}
            if found and None not in found:
                return found
            return set()
        return set(self.all_classes)

    def check_typedefs(self):
        nested = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Dict) and is_typedef(node):
                for val in node.values:
                    if isinstance(val, ast.Dict):
                        for sub in field_spec(val).values():
                            nested.add(sub)
        functions = [n for n in self.tree.body if isinstance(n, ast.FunctionDef)]
        owner = {}
        for function in functions:
            for node in ast.walk(function):
                owner[node] = function.name
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Dict) and is_typedef(node) and node not in nested:
                classes = self.typedef_classes(owner.get(node))
                self.walk_typedef(node, classes, f'line {node.lineno}', '')

    def walk_typedef(self, node, classes, where, prefix):
        for key, val in zip(node.keys, node.values):
            if not isinstance(val, ast.Dict):
                continue
            number = int(key.value)
            spec = field_spec(val)
            label = f'{where} field {prefix}{number}'
            stated_type = constant(spec.get('type'))
            wire = TYPE_WIRE.get(stated_type)
            rows = [self.ref.classes[c].get(number) for c in classes if c in self.ref.classes]
            present = [r for r in rows if r]
            subs = {r[3] for r in present if r[3]}
            if not rows or len(present) < len(rows) or wire is None:
                self.add('field', label, stated_type, UNCHECKED)
            elif any(r[4] and wire == 2 for r in present) or any(r[2] == wire for r in present):
                self.add('field', label, stated_type, CONFIRMED)
            else:
                names = sorted({r[1] for r in present})
                self.add('field', label, stated_type, DIFFERENT,
                         f'{stated_type} is wire {wire}; reference {names} is wire '
                         f'{sorted({r[2] for r in present})}')
            sub = spec.get('message_typedef')
            if isinstance(sub, ast.Dict) and sub.keys:
                self.walk_typedef(sub, subs if len(present) == len(rows) else set(),
                                  where, f'{prefix}{number}.')

    def check_field_statements(self):
        """Judge "field N (name)" text only when name is a real field of a class in scope."""
        rows = [row for name in self.scope for row in self.ref.classes[name].values()]
        known = {row[1] for row in rows}
        seen = set()
        for pattern, number_group, name_group in FIELD_STATEMENTS:
            for match in pattern.finditer(self.source):
                number, name = int(match.group(number_group)), match.group(name_group)
                if (number, name) in seen:
                    continue
                seen.add((number, name))
                label = f'field {number} {name}'
                if name not in known:
                    self.add('field_name', label, name, UNCHECKED)
                elif any(row[0] == number and row[1] == name for row in rows):
                    self.add('field_name', label, name, CONFIRMED)
                elif self.nearby_field_holds(match, number, rows):
                    # "the bundleURL of the parameter title (field 4)": the number can belong
                    # to the other field named in the phrase, so the binding is ambiguous.
                    self.add('field_name', label, name, UNCHECKED)
                else:
                    at = sorted({row[0] for row in rows if row[1] == name})
                    self.add('field_name', label, name, DIFFERENT,
                             f'classes in scope hold {name} at field {at}')

    def nearby_field_holds(self, match, number, rows):
        before = self.source[max(0, match.start() - 60):match.start()]
        return any(row[0] == number and re.search(rf'\b{re.escape(row[1])}\b', before) for row in rows)

    def version_inner(self):
        inner = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Dict) and node.keys and all(
                    isinstance(k, ast.Constant) and type(k.value) is int for k in node.keys):
                for val in node.values:
                    if isinstance(val, ast.Name):
                        inner.add(val.id)
        return inner

    def named_tables(self):
        seen = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(
                    node.targets[0], ast.Name):
                table = literal_table(node.value)
                if table:
                    seen.add(id(node.value))
                    yield node.targets[0].id, table, isinstance(node.value, ast.Dict)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Dict) and id(node) not in seen:
                table = literal_table(node)
                if table:
                    yield f'line {node.lineno}', table, True

    def check_tables(self):
        inner = self.version_inner()
        field_enums = self.ref.scoped(self.ref.enums, self.scope, self.cited_tables,
                                      self.every_segment)
        versioned = self.ref.scoped(self.ref.versioned, self.scope, ())
        for name, table, is_dict in self.named_tables():
            if is_dict and min(table) >= DK_FLOOR and self.is_dk:
                self.check_dk(name, table)
                continue
            if name in inner or VERSION_NAME.search(name):
                self.check_versioned(name, table, field_enums, versioned)
                continue
            status, key, conflicts = compare_table(table, field_enums)
            if not is_dict and status == UNCHECKED:
                continue  # a plain tuple of strings that matches no enum is not an enum table
            self.report_table('enum', name, table, status, key, conflicts, field_enums)

    def check_versioned(self, name, table, field_enums, versioned):
        status, key, conflicts = compare_table(table, versioned)
        if status == CONFIRMED:
            self.add('version_enum', name, key, CONFIRMED)
        elif compare_table(table, field_enums)[0] == CONFIRMED:
            self.add('version_enum', name, 'latest', CONFIRMED)
        else:
            self.report_table('version_enum', name, table, status, key, conflicts, versioned)

    def report_table(self, kind, name, table, status, key, conflicts, candidates):
        if status == DIFFERENT:
            for value in conflicts:
                self.add(kind, name, value, DIFFERENT,
                         f'{table[value]!r}; {key} has {candidates[key][value]!r}')
        else:
            self.add(kind, name, key or '', status)

    def check_dk(self, name, table):
        for index, label in sorted(table.items()):
            stored = self.ref.dk_metadata.get(index)
            if stored is None:
                self.add('dk_label', name, index, UNCHECKED)
            elif same_name(label, stored.rsplit('-', 1)[-1]):
                self.add('dk_label', name, index, CONFIRMED)
            else:
                self.add('dk_label', name, index, DIFFERENT, f'{label!r}; reference has {stored!r}')


def module_paths(root):
    folder = os.path.join(root, 'scripts', 'artifacts')
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.py'):
            continue
        path = os.path.join(folder, name)
        if name.startswith('biome'):
            yield path
            continue
        with open(path, encoding='utf-8', errors='replace') as handle:
            if 'Biome/streams' in handle.read():
                yield path


def load_exceptions(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def apply_exceptions(items, exceptions):
    """Return (remaining items, stale exceptions)."""
    index = {(e['module'], e['kind'], e['item'], str(e['key'])): e for e in exceptions}
    used, out = set(), []
    for item in items:
        key = (item.module, item.kind, item.item, item.key)
        if item.status == DIFFERENT and key in index:
            used.add(key)
            out.append(item._replace(status=CONFIRMED, detail=f"exception: {index[key]['reason']}"))
        else:
            out.append(item)
    return out, [index[k] for k in index if k not in used]


def check(root=REPO_ROOT, reference_path=REFERENCE, exceptions_path=EXCEPTIONS):
    with open(reference_path, encoding='utf-8') as handle:
        reference = Reference(json.load(handle))
    items = []
    for path in module_paths(root):
        items.extend(ModuleCheck(reference, path).run())
    return apply_exceptions(items, load_exceptions(exceptions_path))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', default=REPO_ROOT)
    parser.add_argument('--unchecked', action='store_true', help='list items that could not be checked')
    args = parser.parse_args(argv)
    items, stale = check(args.root)
    counts = collections.Counter((i.kind, i.status) for i in items)
    print(f"{'kind':<14}{CONFIRMED:>11}{DIFFERENT:>11}{UNCHECKED:>17}")
    for kind in KINDS:
        print(f'{kind:<14}{counts[kind, CONFIRMED]:>11}{counts[kind, DIFFERENT]:>11}'
              f'{counts[kind, UNCHECKED]:>17}')
    if args.unchecked:
        for item in items:
            if item.status == UNCHECKED:
                print(f'could not check: {item.module} {item.kind} {item.item} {item.key}')
    different = [i for i in items if i.status == DIFFERENT]
    for item in different:
        print(f'DIFFERENT: {item.module} [{item.kind}] {item.item} key {item.key}: {item.detail}')
    for entry in stale:
        print(f"STALE EXCEPTION: {entry['module']} [{entry['kind']}] {entry['item']} key {entry['key']}")
    if different or stale:
        print('\nFix the module, or if the difference is deliberate add an exact entry to '
              'admin/data/biome_reference_exceptions.json with a reason.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
