"""Guard the column order of conversation artifacts.

An artifact that reports messages declares, in its `__artifacts_v2__` entry, a
`data_views.conversation` block naming which of its columns carry the time, the
direction, the sender, the conversation label, the message text and the media.
Those declarations already exist for LAVA's conversation view, so the report
table can be ordered from them rather than from per-artifact taste.

The order this check enforces:

    1. the declared timeColumn
    2. every other column typed 'datetime' or 'date'
    3. directionColumn, senderColumn, conversationLabelColumn, textColumn,
       mediaColumn, in that relative order
    4. everything else, in whatever order the artifact already used

The point is the examiner's first read. Before this order was applied, the
declared direction column sat at a median of column 9 and as far right as column
23, so the single field that says whether a message was sent or received was off
the visible width of a wide table. Two artifacts did not even have their declared
time column first.

The check parses each module with `ast`, resolves `data_headers` (a literal in
the artifact function, a module-level constant, or a concatenation of the two),
and reports:

  * a declared timeColumn that is not the first column
  * declared role columns that appear out of the order above
  * a declared role naming a column the artifact does not emit, which would also
    leave LAVA's conversation view without that field

Headers built at run time cannot be resolved statically. Those modules are listed
as unchecked rather than silently passed, so the gap stays visible.
"""
import argparse
import ast
import os
import sys

ROLE_SEQUENCE = ['directionColumn', 'senderColumn', 'conversationLabelColumn',
                 'textColumn', 'mediaColumn']
# Older modules spell two of the keys differently; lavafuncs remaps them on write.
CONVERT = {'threadDiscriminatorColumn': 'conversationDiscriminatorColumn',
           'threadLabelColumn': 'conversationLabelColumn'}
DATE_TYPES = ('datetime', 'date')

STANDARD_NOTE = (
    'Order a conversation artifact\'s columns as: the declared timeColumn, then any other\n'
    'datetime/date columns, then direction, sender, conversation label, message text and\n'
    'media, then everything else unchanged. Reorder the row tuple in the same edit, or\n'
    'every value lands under the wrong header.')


def artifacts_block(tree):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == '__artifacts_v2__':
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, TypeError, SyntaxError):
                        return None
    return None


def module_constants(tree):
    """Module-level names bound to a tuple/list literal, for header constants."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Tuple, ast.List)):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    try:
                        out[t.id] = list(ast.literal_eval(node.value))
                    except (ValueError, TypeError, SyntaxError):
                        pass
    return out


def resolve(expr, consts):
    """Evaluate a header expression: literal, module constant, or their concatenation."""
    if isinstance(expr, (ast.Tuple, ast.List)):
        try:
            return list(ast.literal_eval(expr))
        except (ValueError, TypeError, SyntaxError):
            return None
    if isinstance(expr, ast.Name):
        return list(consts[expr.id]) if expr.id in consts else None
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        left, right = resolve(expr.left, consts), resolve(expr.right, consts)
        return None if left is None or right is None else left + right
    return None


def headers_for(tree, func_name, consts):
    """Headers an artifact function returns, or None when built at run time."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != func_name:
            continue
        for n in ast.walk(node):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name) and t.id == 'data_headers':
                        got = resolve(n.value, consts)
                        if got is not None:
                            return got
        # No local assignment: a return of a constant, or a delegation to another artifact.
        for n in ast.walk(node):
            if isinstance(n, ast.Return) and isinstance(n.value, ast.Tuple) and n.value.elts:
                got = resolve(n.value.elts[0], consts)
                if got is not None:
                    return got
            if (isinstance(n, ast.Return) and isinstance(n.value, ast.Call)
                    and isinstance(n.value.func, ast.Attribute)
                    and n.value.func.attr == '__wrapped__'
                    and isinstance(n.value.func.value, ast.Name)):
                return headers_for(tree, n.value.func.value.id, consts)
    return None


def expected(names, types, view):
    order, used = [], set()
    tc = view.get('timeColumn')
    if tc in names:
        i = names.index(tc)
        order.append(i)
        used.add(i)
    for i, t in enumerate(types):
        if i not in used and t in DATE_TYPES:
            order.append(i)
            used.add(i)
    for role in ROLE_SEQUENCE:
        c = view.get(role)
        if c in names and names.index(c) not in used:
            i = names.index(c)
            order.append(i)
            used.add(i)
    order += [i for i in range(len(names)) if i not in used]
    return order


def check_module(path):
    problems, unchecked, checked = [], [], 0
    src = open(path, encoding='utf-8', errors='replace').read()
    if 'data_views' not in src:
        return problems, unchecked, checked
    try:
        tree = ast.parse(src)
    except SyntaxError as ex:
        return [f'{os.path.basename(path)}: could not parse ({ex})'], unchecked, checked
    blk = artifacts_block(tree)
    if not isinstance(blk, dict):
        return problems, unchecked, checked
    consts = module_constants(tree)
    rel = os.path.basename(path)

    for art, meta in blk.items():
        dv = (meta or {}).get('data_views') or {}
        if not isinstance(dv, dict):
            continue
        raw = dv.get('conversation') or dv.get('chat')
        if not raw:
            continue
        view = {CONVERT.get(k, k): v for k, v in raw.items()}
        headers = headers_for(tree, art, consts)
        if headers is None:
            unchecked.append(f'{rel}::{art} (headers built at run time)')
            continue
        checked += 1
        names = [h[0] if isinstance(h, (tuple, list)) else h for h in headers]
        types = [(h[1] if isinstance(h, (tuple, list)) and len(h) > 1 else None) for h in headers]

        for role in ['timeColumn'] + ROLE_SEQUENCE:
            col = view.get(role)
            if col and col not in names:
                problems.append(f'{rel}::{art}: {role} names {col!r}, which is not a column '
                                f'this artifact emits')

        tc = view.get('timeColumn')
        if tc in names and names[0] != tc:
            problems.append(f'{rel}::{art}: timeColumn {tc!r} is column '
                            f'{names.index(tc) + 1}, not column 1')

        want = expected(names, types, view)
        if want != list(range(len(names))):
            shown = [names[i] for i in want]
            problems.append(f'{rel}::{art}: columns are not in declared-role order\n'
                            f'      is:     {names[:7]}\n'
                            f'      expect: {shown[:7]}')
    return problems, unchecked, checked


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*', help='artifact modules to check (default: all)')
    args = ap.parse_args()

    paths = args.paths
    if not paths:
        root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), 'scripts', 'artifacts')
        paths = [os.path.join(root, f) for f in sorted(os.listdir(root)) if f.endswith('.py')]

    problems, unchecked, checked = [], [], 0
    for p in paths:
        if not p.endswith('.py') or not os.path.exists(p):
            continue
        pr, un, ck = check_module(p)
        problems += pr
        unchecked += un
        checked += ck

    if unchecked:
        print(f'{len(unchecked)} conversation artifact(s) NOT checked, headers are '
              f'not statically resolvable:')
        for u in sorted(unchecked):
            print(f'  {u}')
        print()

    if problems:
        print(f'{len(problems)} conversation artifact column-order problem(s):')
        for p in sorted(problems):
            print(f'  {p}')
        print()
        print(STANDARD_NOTE)
        return 1

    print(f'Checked {checked} conversation artifact(s): columns follow the declared-role order.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
