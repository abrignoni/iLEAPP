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


def collect_imports():
    """Counter of (module, name) over artifact modules, one count per importing module."""
    counts = Counter()
    for path in sorted(ARTIFACTS.rglob('*.py')):
        tree = _parse(path)
        if tree is None or not _has_artifact_block(tree):
            continue
        seen = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0 \
                    and node.module.startswith('scripts.'):
                for alias in node.names:
                    seen.add((node.module, alias.name))
            elif isinstance(node, ast.ImportFrom) and node.module == 'scripts' and node.level == 0:
                for alias in node.names:
                    seen.add((f'scripts.{alias.name}', '*'))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('scripts.'):
                        seen.add((alias.name, '*'))
        counts.update(seen)
    return counts


def _signature(node):
    """name(arguments), with | escaped so a union annotation does not split the table cell."""
    args = ast.unparse(node.args)
    return f'{node.name}({args})'.replace('|', '\\|')


def _doc_line(node):
    doc = ast.get_docstring(node)
    if not doc:
        return ''
    return doc.strip().splitlines()[0].strip().replace('|', '\\|')


def _public(nodes):
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and not node.name.startswith('_'):
            yield node


def build():
    counts = collect_imports()
    modules = sorted({module for module, _name in counts})
    helper_sections = []
    other_rows = []
    for module in modules:
        path = _module_path(module)
        used = {name: n for (mod, name), n in counts.items() if mod == module}
        if path is None:
            other_rows.append((module, max(used.values()), 'package'))
            continue
        tree = _parse(path)
        if tree is None:
            other_rows.append((module, max(used.values()), 'not parseable'))
            continue
        is_artifact = path.is_relative_to(ARTIFACTS) and _has_artifact_block(tree)
        if is_artifact or _is_vendored(path):
            other_rows.append((module, max(used.values()),
                               'artifact module' if is_artifact else 'vendored or generated'))
            continue
        rows = []
        for node in _public(tree.body):
            kind = 'class' if isinstance(node, ast.ClassDef) else 'function'
            signature = node.name if kind == 'class' else _signature(node)
            rows.append((used.get(node.name, 0), node.name, kind, signature, _doc_line(node), node))
        rows.sort(key=lambda row: (-row[0], row[1].lower()))
        helper_sections.append((module, path.relative_to(ROOT).as_posix(), rows, used.get('*', 0),
                                max([used.get('*', 0)] + list(used.values()))))
    helper_sections.sort(key=lambda section: (-section[4], section[0]))

    lines = [
        '# Helper functions artifacts use',
        '',
        'Generated by `admin/scripts/helper_index.py` from the code on this branch. Do not edit by',
        'hand; run the script instead. The documentation workflow rewrites it after a merge that',
        'changes anything under `scripts/`.',
        '',
        'Read this before writing a helper of your own: a reader, a timestamp conversion, a path',
        'shortener or a storage-view collapse may already be here. "Used by" is the number of artifact',
        'modules that import the name. A class\'s public methods are listed under it, since artifacts',
        'call them on an object (`context.get_files_found()`). The first line of each docstring is',
        'shown; open the module for the rest. `admin/docs/helper_functions.md` explains where the five',
        'cores\' helpers differ.',
        '',
    ]
    for module, relative, rows, whole, _rank in helper_sections:
        lines += [f'## `{module}`', '', f'`{relative}`', '']
        if whole:
            lines += [f'Imported as a module by {whole} artifact module(s), whose uses of its names are not '
                      'counted below.', '']
        lines += ['| Used by | Name | Signature | First docstring line |', '| ---: | --- | --- | --- |']
        for used, name, kind, signature, doc, node in rows:
            label = f'class `{name}`' if kind == 'class' else f'`{name}`'
            lines.append(f'| {used} | {label} | `{signature}` | {doc or "(no docstring)"} |'
                         if kind == 'function' else f'| {used} | {label} | | {doc or "(no docstring)"} |')
            if kind == 'class':
                for method in _public(node.body):
                    if isinstance(method, ast.ClassDef):
                        continue
                    lines.append(f'| | `{name}.{method.name}` | `{_signature(method)}` | '
                                 f'{_doc_line(method) or "(no docstring)"} |')
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


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='exit 1 if the index is out of date')
    args = parser.parse_args()
    text = build()
    if args.check:
        current = OUTPUT.read_text(encoding='utf-8') if OUTPUT.exists() else ''
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
