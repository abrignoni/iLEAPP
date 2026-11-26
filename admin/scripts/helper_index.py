"""Write admin/docs/generated/helper_functions_index.md: the helpers artifact modules use here.

The index lists every public function and class of each module under scripts/ that artifact
modules import from (ilapfuncs, context, lavafuncs, and helper modules such as
storagePathViews), with its signature, the first line of its docstring and how many artifact
modules import it. Public methods of those classes are listed under the class, because
artifacts call them on an object (context.get_files_found()) rather than import them.

The code is read with ast only. Nothing under scripts/ is imported, so the script runs in
the documentation workflow, which installs no packages. The file is identical in the five
LEAPP cores; what it writes differs because each core's helpers differ.

    python admin/scripts/helper_index.py           write the index
    python admin/scripts/helper_index.py --check   exit 1 if the index is out of date
"""
import argparse
import ast
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'scripts'
ARTIFACTS = SCRIPTS / 'artifacts'
OUTPUT = ROOT / 'admin' / 'docs' / 'generated' / 'helper_functions_index.md'
# Folders under scripts/ that hold code kept as its authors wrote it.
VENDOR_FOLDERS = ('vendor', 'blackboxprotobuf')


def _parse(path):
    try:
        return ast.parse(path.read_text(encoding='utf-8'))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return None


def _has_artifact_block(tree):
    return any(isinstance(node, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id == '__artifacts_v2__' for target in node.targets)
        for node in tree.body)


def _module_path(dotted):
    """The file a dotted scripts.* name refers to, or None for a package or a missing file."""
    candidate = ROOT.joinpath(*dotted.split('.'))
    if candidate.with_suffix('.py').is_file():
        return candidate.with_suffix('.py')
    return None


def _is_vendored(path):
    """A file kept as another project wrote it, or generated: lint-skipped, or under a vendor folder."""
    text = path.read_text(encoding='utf-8', errors='replace')
    if 'pylint: skip-file' in text[:2000]:
        return True
    top = path.relative_to(SCRIPTS).parts[0]
    return top in VENDOR_FOLDERS or top.startswith('ccl')


# Keys in the import counter for a module used as a whole rather than name by name.
WHOLE = '<module>'
STAR = '<star>'
# Helper modules listed whether or not an artifact imports them: artifacts get a Context from
# artifact_processor without importing it, and call its methods on that object.
ALWAYS_LISTED = ('scripts.context',)


def _child_module(package, name):
    """scripts.<package>.<name> when that names a module file, else None."""
    dotted = f'{package}.{name}'
    return dotted if _module_path(dotted) else None


def collect_imports():
    """Counter of (module, name) over artifact modules, one count per importing module.

    name is WHOLE for a module imported as a whole (import scripts.x, from scripts import x,
    from scripts.pkg import module) and STAR for from scripts.x import *.
    """
    counts = Counter()
    for path in sorted(ARTIFACTS.rglob('*.py')):
        tree = _parse(path)
        if tree is None or not _has_artifact_block(tree):
            continue
        seen = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module \
                    and (node.module == 'scripts' or node.module.startswith('scripts.')):
                for alias in node.names:
                    if alias.name == '*':
                        seen.add((node.module, STAR))
                        continue
                    child = _child_module(node.module, alias.name)
                    if child:
                        seen.add((child, WHOLE))
                    elif node.module != 'scripts':
                        seen.add((node.module, alias.name))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('scripts.'):
                        seen.add((alias.name, WHOLE))
        counts.update(seen)
    return counts


def _md(text):
    """Text for a table cell: | escaped everywhere, < and > escaped outside code spans."""
    parts = text.split('`')
    for index in range(0, len(parts), 2):
        parts[index] = parts[index].replace('<', '&lt;').replace('>', '&gt;')
    return '`'.join(parts).replace('|', '\\|')


def _signature(node, name=None, drop_self=False):
    """name(arguments), with | escaped so a union annotation does not split the table cell."""
    args = node.args
    if drop_self and args.args:
        args = ast.arguments(posonlyargs=args.posonlyargs, args=args.args[1:], vararg=args.vararg,
                             kwonlyargs=args.kwonlyargs, kw_defaults=args.kw_defaults, kwarg=args.kwarg,
                             defaults=args.defaults[1:] if len(args.defaults) == len(args.args) else args.defaults)
    return f'{name or node.name}({ast.unparse(args)})'.replace('|', '\\|')


def _doc_line(node):
    doc = ast.get_docstring(node)
    if not doc:
        return ''
    return _md(doc.strip().splitlines()[0].strip())


def _public(nodes):
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and not node.name.startswith('_'):
            yield node


def _is_property(node):
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id in ('property', 'cached_property'):
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr in ('setter', 'deleter', 'cached_property'):
            return True
    return False


def _class_signature(node):
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == '__init__':
            return _signature(item, name=node.name, drop_self=True)
    return ''


def _member_rows(node):
    """Rows for a class's public methods and properties, a property shown once and without a call."""
    rows = []
    shown = set()
    for member in _public(node.body):
        if isinstance(member, ast.ClassDef) or member.name in shown:
            continue
        shown.add(member.name)
        if _is_property(member):
            rows.append(f'| | `{node.name}.{member.name}` | property | {_doc_line(member) or "(no docstring)"} |')
        else:
            rows.append(f'| | `{node.name}.{member.name}` | `{_signature(member)}` | '
                        f'{_doc_line(member) or "(no docstring)"} |')
    return rows


def _reexports(tree):
    """{name: source module} for the scripts.* names a module imports at its top level."""
    sources = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module \
                and node.module.startswith('scripts.'):
            for alias in node.names:
                if alias.name != '*':
                    sources[alias.asname or alias.name] = (node.module, alias.name)
    return sources


def _definition(module, name):
    """The top-level def or class called name in module, or None."""
    path = _module_path(module)
    tree = _parse(path) if path else None
    if tree is None:
        return None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return node
    return None


def _row(used, name, node, source=None):
    label = f'class `{name}`' if isinstance(node, ast.ClassDef) else f'`{name}`'
    signature = _class_signature(node) if isinstance(node, ast.ClassDef) else _signature(node, name=name)
    doc = _doc_line(node) or '(no docstring)'
    if source:
        doc = f'Defined in `{source}`. {doc}'
    cell = f' `{signature}` ' if signature else ' '
    return f'| {used} | {label} |{cell}| {doc} |'


def build():
    counts = collect_imports()
    modules = sorted({module for module, _name in counts} | {
        module for module in ALWAYS_LISTED if _module_path(module)})
    helper_sections = []
    other_rows = []
    for module in modules:
        path = _module_path(module)
        used = {name: n for (mod, name), n in counts.items() if mod == module}
        rank = max(used.values(), default=0)
        if path is None:
            other_rows.append((module, rank, 'package'))
            continue
        tree = _parse(path)
        if tree is None:
            other_rows.append((module, rank, 'not parseable'))
            continue
        is_artifact = path.is_relative_to(ARTIFACTS) and _has_artifact_block(tree)
        if is_artifact or _is_vendored(path):
            other_rows.append((module, rank, 'artifact module' if is_artifact else 'vendored or generated'))
            continue
        local = {node.name: node for node in _public(tree.body)}
        rows = [(used.get(name, 0), name, node, None) for name, node in local.items()]
        reexported = _reexports(tree)
        for name, count in used.items():
            if name in (WHOLE, STAR) or name in local or name not in reexported:
                continue
            source, original = reexported[name]
            node = _definition(source, original)
            if node is not None:
                rows.append((count, name, node, source))
        rows.sort(key=lambda row: (-row[0], row[1].lower()))
        helper_sections.append((module, path.relative_to(ROOT).as_posix(), rows, used.get(WHOLE, 0),
                                used.get(STAR, 0), rank))
    helper_sections.sort(key=lambda section: (-section[5], section[0]))

    lines = [
        '# Helper functions artifacts use',
        '',
        'Generated by `admin/scripts/helper_index.py` from the code on this branch. Do not edit by',
        'hand; run the script instead. The documentation workflow rewrites it after a merge that',
        'changes anything under `scripts/`.',
        '',
        'Read this before writing a helper of your own: a reader, a timestamp conversion, a path',
        'shortener or a storage-view collapse may already be here. "Used by" is the number of artifact',
        'modules that import the name. A class row shows its constructor, and its public methods and',
        'properties are listed under it, since artifacts call them on an object',
        '(`context.get_files_found()`). `scripts.context` is listed even where no artifact imports it,',
        'because artifacts are handed a Context. A name a module imports from another one is listed',
        'with the module it is defined in. The first line of each docstring is shown; open the module',
        'for the rest. `admin/docs/helper_functions.md` explains where the five cores\' helpers differ.',
        '',
    ]
    for module, relative, rows, whole, star, _rank in helper_sections:
        lines += [f'## `{module}`', '', f'`{relative}`', '']
        if whole:
            lines += [f'Imported as a module by {whole} artifact module(s), whose uses of its names are not '
                      'counted below.', '']
        if star:
            lines += [f'Imported with `*` by {star} artifact module(s), whose uses of its names are not '
                      'counted below.', '']
        lines += ['| Used by | Name | Signature | First docstring line |', '| ---: | --- | --- | --- |']
        for used, name, node, source in rows:
            lines.append(_row(used, name, node, source))
            if isinstance(node, ast.ClassDef):
                lines += _member_rows(node)
        lines.append('')
    if other_rows:
        lines += ['## Other modules artifacts import', '',
                  'Vendored readers, packages and other artifact modules. "Used by" is the largest number of',
                  'artifact modules importing any one name from it, or the module itself.', '',
                  '| Used by | Module | Kind |', '| ---: | --- | --- |']
        for module, used, kind in sorted(other_rows, key=lambda row: (-row[1], row[0])):
            lines.append(f'| {used} | `{module}` | {kind} |')
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='exit 1 if the index is out of date')
    args = parser.parse_args(argv)
    text = build()
    if args.check:
        current = OUTPUT.read_text(encoding='utf-8') if OUTPUT.exists() else None
        if current != text:
            print(f'{OUTPUT.relative_to(ROOT)} is out of date; run python admin/scripts/helper_index.py')
            return 1
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding='utf-8')
    print(f'wrote {OUTPUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
