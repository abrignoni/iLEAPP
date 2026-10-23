"""Guard the third return element against anything but real paths, newline joined.

An artifact returns `(data_headers, data_list, source_path)`. The third element is
not decoration. `artifact_processor` splits it on newlines, passes each piece
through `Context.get_relative_path`, prints it as the report's

    <artifact name> located at: <source_path>

line, and writes it into the LAVA manifest as `source_path`. So it has to be real
paths, newline joined.

The first defect this catches is a string constant standing in for one:

    return data_headers, data_list, 'See source file(s) below'   # WRONG
    return data_headers, data_list, 'Path column in the report'  # WRONG

It reads as helpful and it is not. It points the examiner at a column that often
holds a basename rather than a path, so the location of the evidence is nowhere in
the report, and the LAVA manifest records prose where a consumer expects a path.

The second is real paths listed with some other separator:

    return data_headers, data_list, ', '.join(source_paths)          # WRONG
    return data_headers, data_list, f'{db_path}; {wal_path}'         # WRONG
    return data_headers, data_list, str(history) + ', ' + str(web)   # WRONG

The wrapper splits on newlines only, so the whole list reaches it as one piece. It
is then one entry in the LAVA manifest, and a path that itself holds ', ' cannot be
told apart from two paths.

The third is a label or prose composed into the value with an f-string or a '+'
chain, around real paths or instead of them:

    return data_headers, data_list, f'ATX Database: {atx_db}'              # WRONG
    return data_headers, data_list, f'{count} databases - see Source File'  # WRONG

Each line of the result is taken as a path, so the label becomes part of the path
the report prints and the manifest records.

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

The join check follows the value to where it was built: straight into the return,
through a variable of the decorated function (including tuple unpacking and `+=`),
and into a helper function defined in the same module. A streamed result's
`source_path=` keyword and `set_source_path(...)` argument are followed the same
way. It reports the line where the separator is written, which is the line to fix.

The composed-label check follows the value the same way and reads the literal text
of each f-string and '+' chain it reaches. ' >> ' counts as a path separator. The
text is split into lines at '\n', and a line is reported as a label or prose when:

  * it is all literal, with no interpolated value on it, and holds neither '/' nor
    '\\' (a hardcoded path keeps its separators; 'See Source File column' has none),
  * or it is written next to an interpolated value with whitespace on the side
    that touches the value ('ATX Database: {path}', '{count} databases').

A path built from values is joined to them by a separator or a suffix with no
space at the join ('{folder}/{name}', '{db}-wal', '{root}/Application Support/x'),
so neither rule fires on it. A literal touching a value with no space between them
('{path}(copy)') is not caught.

The reached-literal check follows the value the same way and reports a whole string
literal that gets there by any route but the plain return the prose check reads:
either side of a conditional expression, any operand of an 'or' or 'and', any one
of several assignments to a variable, a module constant, or a helper's return:

    return data_headers, data_list, source_path or 'activeUser'          # WRONG
    source = 'See source paths in data' if sources else ''               # WRONG
    report_file = 'Unknown'   # later replaced by real paths              # WRONG

The literal is reported when one of its lines holds text and neither '/' nor '\\',
the same reading the composed-label check gives a literal line. A fallback that is
only ever returned with no rows is still reported, because the check cannot tell
that from the code: write `''` there, or start from an empty list and join it.

What deliberately does NOT fail:

  * `''` on a branch that also returns an empty `data_list`. The wrapper writes no
    report at all when there are no rows, so that string never reaches a report.
    A "not found" message there is pointless but harmless, and `''` is correct.
    The same branch is not checked for joins either.
  * A variable holding a real path, however it was built. Only literal text is
    reported as prose: a string literal, wherever it reaches the source path from,
    and the literal text of an f-string or '+' chain that the rule above reads as a
    label.
  * `''` anywhere, including as the other side of a conditional or an 'or'.
  * Building one path: `'/'.join(parts)`, `''.join(parts)`, `os.path.join(...)`,
    `f'{folder}/{name}'`, and archive member notation, `f'{archive} >> {member}'`.

The prose check was found by sweeping all five cores in 2026-08: 54 sites. iLEAPP
had already been swept once (PRs #2022 and #2024, 140 modules) and the class had
come back in ALEAPP and RLEAPP, which is why it is now a check rather than a sweep.
The composed-label check was added after a sweep of all five cores in 2026-10 found
four sites the literal check could not see, three in ALEAPP and one in iLEAPP.
The reached-literal check was added after a later 2026-10 sweep found 87 artifacts
whose literal neither check could see, 17 in ALEAPP and 70 in iLEAPP.

Usage:
  check_source_path.py [--root REPO_ROOT]

Exits 1 when anything is found, 0 otherwise.
"""

import argparse
import ast
import os
import sys

DECORATORS = {'artifact_processor', 'artifact_processor_streaming'}
RESULT_BUILDERS = {'create_artifact_result', 'ArtifactResult'}

# Join separators that build one path rather than list several.
ONE_PATH_JOINS = {'\n', '/', '\\', '', ' >> '}
MEMBER_NOTATION = ' >> '
LIST_MARKS = (',', ';', '|')

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


def path_triples(func):
    return [n for n in ast.walk(func)
            if isinstance(n, ast.Return)
            and isinstance(n.value, ast.Tuple)
            and len(n.value.elts) == 3]


def scan_function(func):
    """(line, text) for every literal masquerading as a source path."""
    found = []
    for ret in path_triples(func):
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


SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def own_scope(func):
    """Every node of `func` that is not inside a function or class nested in it.

    A nested function's `return lat, lng, names` is not the artifact's return, and
    a name it assigns is not the outer function's variable.
    """
    pending = list(ast.iter_child_nodes(func))
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, SCOPES):
            pending.extend(ast.iter_child_nodes(node))


def own_triples(func):
    return [n for n in own_scope(func)
            if isinstance(n, ast.Return)
            and isinstance(n.value, ast.Tuple)
            and len(n.value.elts) == 3]


def module_constants(tree):
    """Top-level names bound once, to a string literal."""
    bound = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    bound.setdefault(target.id, []).append(node.value)
    return {name: values[0].value for name, values in bound.items()
            if len(values) == 1 and isinstance(values[0], ast.Constant)
            and isinstance(values[0].value, str)}


def bindings(func, name):
    """(value, position, augmented) for every assignment to `name` in `func`.

    `position` is the tuple index when the name is unpacked from a value that is
    not itself a tuple literal (a call, typically), None otherwise.
    """
    found = []
    for node in own_scope(func):
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                found.append((node.value, None, True))
            continue
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name:
                found.append((value, None, False))
            elif isinstance(target, (ast.Tuple, ast.List)):
                for index, element in enumerate(target.elts):
                    if not (isinstance(element, ast.Name) and element.id == name):
                        continue
                    if (isinstance(value, (ast.Tuple, ast.List))
                            and len(value.elts) == len(target.elts)):
                        found.append((value.elts[index], None, False))
                    else:
                        found.append((value, index, False))
    return found


def lists_values(text):
    """Whether a literal placed between two values lists them instead of joining a path."""
    rest = text.replace(MEMBER_NOTATION, '')
    if any(mark in rest for mark in LIST_MARKS):
        return True
    return bool(rest) and not rest.strip() and '\n' not in rest


def composes_prose(text, touches_left, touches_right):
    """Whether literal text placed in a composed source path is a label or prose.

    `touches_left` and `touches_right` say whether an interpolated value sits
    directly before or after the text in the composed string.
    """
    lines = text.replace(MEMBER_NOTATION, '/').split('\n')
    last = len(lines) - 1
    for index, line in enumerate(lines):
        left = touches_left and index == 0
        right = touches_right and index == last
        if not left and not right:
            if line.strip() and '/' not in line and '\\' not in line:
                return True
        elif (left and line[:1].isspace()) or (right and line[-1:].isspace()):
            return True
    return False


def flatten_add(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return flatten_add(node.left) + flatten_add(node.right)
    return [node]


class JoinFinder:
    """Follows a source_path expression back to where a separator was written."""

    def __init__(self, tree):
        self.helpers = {n.name: n for n in tree.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.constants = module_constants(tree)
        # (line, text) for each label or prose composed into a source path.
        self.prose = set()
        # (line, text) for each whole literal that reaches a source path through a
        # branch, an 'or'/'and', a variable or a helper.
        self.reached = set()

    def note_literal(self, node, text):
        """Record a whole literal that reaches a source path, when it reads as prose."""
        if text and composes_prose(text, False, False):
            self.reached.add((node.lineno, text))

    def literal(self, func, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            values = [value for value, _, _ in bindings(func, node.id)]
            if not values:
                return self.constants.get(node.id)
            if (all(isinstance(v, ast.Constant) and isinstance(v.value, str) for v in values)
                    and len({v.value for v in values}) == 1):
                return values[0].value
        return None

    def helper_returns(self, call, position, seen):
        func = call.func
        if not (isinstance(func, ast.Name) and func.id in self.helpers):
            return
        key = ('helper', func.id, position)
        if key in seen:
            return
        seen.add(key)
        helper = self.helpers[func.id]
        for ret in own_scope(helper):
            if not isinstance(ret, ast.Return) or ret.value is None:
                continue
            value = ret.value
            if position is not None:
                if not (isinstance(value, ast.Tuple) and len(value.elts) > position):
                    continue
                value = value.elts[position]
            yield from self.find(helper, value, seen)

    def note_prose(self, func, parts, leading_counts):
        """Record literal text in an f-string or '+' chain that reads as a label."""
        runs = []  # [line, text] for each run of adjacent literal parts, None for a value
        for part in parts:
            text = (part.value if isinstance(part, ast.Constant)
                    and isinstance(part.value, str) else None)
            if text is None and not isinstance(part, (ast.Constant, ast.FormattedValue)):
                text = self.literal(func, part)
            if text is None:
                runs.append(None)
            elif runs and runs[-1] is not None:
                runs[-1][1] += text
            else:
                runs.append([part.lineno, text])
        for index, run in enumerate(runs):
            if run is None or lists_values(run[1]):
                continue
            touches_left = index > 0 or leading_counts
            touches_right = index < len(runs) - 1
            if composes_prose(run[1], touches_left, touches_right):
                self.prose.add((run[0], run[1]))

    def pieces(self, func, parts, seen, leading_counts=False):
        """Findings for the parts of an f-string or a '+' chain."""
        self.note_prose(func, parts, leading_counts)
        for index, part in enumerate(parts):
            if isinstance(part, ast.Constant):
                if isinstance(part.value, str) and lists_values(part.value):
                    if leading_counts or 0 < index < len(parts) - 1:
                        yield part.lineno, part.value
            elif isinstance(part, ast.FormattedValue):
                yield from self.find(func, part.value, seen)
            else:
                yield from self.find(func, part, seen)

    def find(self, func, node, seen):
        """(line, separator) for each listing separator that reaches `node`."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                self.note_literal(node, node.value)
        elif isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Attribute) and target.attr == 'join':
                separator = self.literal(func, target.value)
                if separator is not None and separator not in ONE_PATH_JOINS:
                    yield node.lineno, separator
                return
            yield from self.helper_returns(node, None, seen)
        elif isinstance(node, ast.JoinedStr):
            yield from self.pieces(func, node.values, seen)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            yield from self.pieces(func, flatten_add(node), seen)
        elif isinstance(node, ast.IfExp):
            yield from self.find(func, node.body, seen)
            yield from self.find(func, node.orelse, seen)
        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                yield from self.find(func, value, seen)
        elif isinstance(node, ast.Name):
            key = (func.name, func.lineno, node.id)
            if key in seen:
                return
            seen.add(key)
            found = bindings(func, node.id)
            if not found and node.id in self.constants:
                self.note_literal(node, self.constants[node.id])
            for value, position, augmented in found:
                if augmented:
                    if isinstance(value, ast.JoinedStr):
                        parts = value.values
                    else:
                        parts = flatten_add(value)
                    yield from self.pieces(func, parts, seen, leading_counts=True)
                elif position is not None:
                    if isinstance(value, ast.Call):
                        yield from self.helper_returns(value, position, seen)
                else:
                    yield from self.find(func, value, seen)


def parse(path):
    module = os.path.basename(path)
    try:
        with open(path, encoding='utf-8', errors='replace') as handle:
            return module, ast.parse(handle.read()), None
    except SyntaxError as err:
        return module, None, f'{module}: could not parse ({err})'


def decorated(tree):
    for node in ast.walk(tree):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and DECORATORS.intersection(decorator_names(node))):
            yield node


def scan_module(path):
    """Prose returned as a source path: [(module, function, line, text)]."""
    module, tree, problem = parse(path)
    if problem:
        return [], problem
    violations = []
    for node in decorated(tree):
        for line, text in scan_function(node):
            violations.append((module, node.name, line, text))
    return violations, None


def reaching_values(node):
    """Every expression of a decorated function that becomes its source path."""
    reaching = [ret.value.elts[2] for ret in own_triples(node)
                if not returns_no_rows(ret)]
    # A streamed result carries the same value on the ArtifactResult instead.
    for call in own_scope(node):
        if not isinstance(call, ast.Call):
            continue
        called = (call.func.attr if isinstance(call.func, ast.Attribute)
                  else getattr(call.func, 'id', ''))
        if called in RESULT_BUILDERS:
            reaching.extend(k.value for k in call.keywords if k.arg == 'source_path')
        elif called == 'set_source_path' and call.args:
            reaching.append(call.args[0])
    return reaching


def follow(tree):
    """Run the finder over every decorated function.

    Returns (joins, composed prose, reached literals), each a set of
    (function, line, text).
    """
    finder = JoinFinder(tree)
    joins, prose, reached = set(), set(), set()
    for node in decorated(tree):
        finder.prose, finder.reached = set(), set()
        for value in reaching_values(node):
            for line, separator in finder.find(node, value, set()):
                joins.add((node.name, line, separator))
        prose.update((node.name, line, text) for line, text in finder.prose)
        reached.update((node.name, line, text) for line, text in finder.reached)
    return joins, prose, reached


def scan_module_joins(path):
    """Paths listed with a separator other than a newline.

    Returns [(module, function, line, separator)], the line being where the
    separator is written.
    """
    module, tree, problem = parse(path)
    if problem:
        return [], problem
    joins, _, _ = follow(tree)
    violations = [(module, func, line, separator) for func, line, separator in joins]
    return sorted(violations, key=lambda v: (v[2], v[1], v[3])), None


def scan_module_composed(path):
    """A label or prose composed into a source path with an f-string or '+'.

    Returns [(module, function, line, text)], the line being where the text is
    written.
    """
    module, tree, problem = parse(path)
    if problem:
        return [], problem
    _, prose, _ = follow(tree)
    violations = [(module, func, line, text) for func, line, text in prose]
    return sorted(violations, key=lambda v: (v[2], v[1], v[3])), None


def scan_module_reached(path):
    """A prose literal that reaches a source path by any route but the plain one.

    The routes are a conditional expression, an 'or'/'and', any assignment of a
    variable (not only a sole one), a module constant and a helper's return. A
    literal the prose check already reports for the same function is left to it.

    Returns [(module, function, line, text)], the line being where the literal is
    written.
    """
    module, tree, problem = parse(path)
    if problem:
        return [], problem
    plain = {(node.name, text) for node in decorated(tree)
             for _, text in scan_function(node)}
    _, _, reached = follow(tree)
    violations = [(module, func, line, text) for func, line, text in reached
                  if (func, text) not in plain]
    return sorted(violations, key=lambda v: (v[2], v[1], v[3])), None


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

    violations, joins, composed, reached, unreadable, modules = [], [], [], [], [], 0
    for name in sorted(os.listdir(artifacts)):
        if not name.endswith('.py'):
            continue
        modules += 1
        path = os.path.join(artifacts, name)
        found, problem = scan_module(path)
        violations.extend(found)
        if problem:
            unreadable.append(problem)
            continue
        found, _ = scan_module_joins(path)
        joins.extend(found)
        found, _ = scan_module_composed(path)
        composed.extend(found)
        found, _ = scan_module_reached(path)
        reached.extend(found)

    if violations:
        print(f'Artifacts returning prose as source_path ({len(violations)}):')
        for module, func, line, text in violations:
            print(f'  {module}:{line}  {func}()  {text!r}')
        print()
    if joins:
        print('Artifacts joining source paths with a separator other than a '
              f'newline ({len(joins)}):')
        for module, func, line, separator in joins:
            print(f'  {module}:{line}  {func}()  joined with {separator!r}')
        print()
    if composed:
        print('Artifacts composing a label or prose into a source path '
              f'({len(composed)}):')
        for module, func, line, text in composed:
            print(f'  {module}:{line}  {func}()  {text!r}')
        print()
    if reached:
        print('Artifacts reaching a source path with prose through a branch, an '
              f"'or'/'and', a variable, a constant or a helper ({len(reached)}):")
        for module, func, line, text in reached:
            print(f'  {module}:{line}  {func}()  {text!r}')
        print()
    if violations or joins or composed or reached:
        print(STANDARD_NOTE)
        return 1

    summary = (f'Checked {modules} artifact module(s): no prose, no composed label, '
               'no reached literal and no non-newline join returned as a source path.')
    if unreadable:
        summary += f' {len(unreadable)} module(s) NOT checked.'
    print(summary)
    for problem in unreadable:
        print(f'  {problem}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
