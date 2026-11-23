"""Guard reports against the time of a staged copy.

Every seeker copies a matched file into the report's data folder, so a path an artifact is
handed names a copy on the examiner's machine. That copy's own times are not evidence. A FAT
or exFAT directory entry and a zip entry with only a DOS date record a wall-clock reading with
no zone, and the seekers stamp the copy with that reading in the examiner's local zone. One
stored 12:00 then reads as 12:00, 16:00 or 03:00 UTC on machines set to UTC, New York or Tokyo.
Its change and access times are the moment of staging.

Read the times the seeker recorded instead, from seeker.file_infos[path]:

    info.times.modified            Unix seconds, UTC, or None
    info.modification_date         the same for the seekers that record no times object
    info.times.modified_no_zone    the reading with no zone, as text, shown as stored

Never put modified_no_zone in a column typed datetime: the LAVA writer reads zone-less ISO
text as UTC.

This check fails on any read of a file's stat times under scripts/, however it is spelled,
except in the seekers (which set those times), vendored code and the places listed in ALLOWED.
A use that never reaches a report, such as a cache key or a cleanup cutoff, belongs in ALLOWED
with its reason. An entry names the core, the file, the function and how many reads it holds,
so a new read in an allowed function fails, and an entry that no longer matches fails too.
"""
import argparse
import ast
import os
import re
import sys

STAT_NAMES = {'getmtime', 'getctime', 'getatime'}
STAT_ATTRIBUTES = {'st_mtime', 'st_mtime_ns', 'st_ctime', 'st_ctime_ns', 'st_atime', 'st_atime_ns',
                   'st_birthtime', 'st_birthtime_ns', 'ST_MTIME', 'ST_CTIME', 'ST_ATIME'}
STAT_TUPLE_INDEXES = {7, 8, 9}
SKIPPED_FILES = {'scripts/search_files.py', 'scripts/raw_image.py'}
SKIPPED_FOLDERS = ('scripts/vendor/',)

# {core: {file: {function: (reads, why it never reaches a report)}}}
ALLOWED = {
    'iLEAPP': {
        'scripts/alternate_artifacts/appInventory.py': {
            '_iter_extraction_files': (1, 'reads the input folder itself, not a staged copy')},
        'scripts/artifacts/fileSystemEvents.py': {
            '_remove_stale_caches': (1, 'cleanup cutoff for its own cache files'),
            '_cache_key': (1, 'cache key')},
        'scripts/artifacts/powerlog.py': {
            '_remove_stale_gz_temps': (1, 'cleanup cutoff for its own temporary files')},
    },
    'ALEAPP': {
        'scripts/alternate_artifacts/appInventory.py': {
            '_iter_extraction_files': (1, 'reads the input folder itself, not a staged copy')},
        'scripts/dumpstate_reader.py': {'read_report': (1, 'cache key')},
    },
    'RLEAPP': {
        'scripts/meta_records.py': {'load': (1, 'cache key')},
        'scripts/artifacts/binanceReturns.py': {'_workbooks': (1, 'cache key')},
        'scripts/artifacts/robinhoodReturns.py': {'_parsed_pdfs': (1, 'cache key')},
    },
    'VLEAPP': {},
    'DLEAPP': {
        'scripts/linux_links.py': {'recorded_time': (1, "a link's own time in the input folder")},
        'scripts/outlook_pst.py': {'_index': (1, 'cache key')},
        'scripts/windows_ntfs.py': {'mft_index': (1, 'cache key')},
        'scripts/artifacts/windowsDomainAuthEvents.py': {'domain_records': (1, 'cache key')},
        'scripts/artifacts/windowsDriverInstallEvents.py': {'install_records': (1, 'cache key')},
        'scripts/artifacts/windowsNtdsAccounts.py': {'_directory': (1, 'cache key')},
        'scripts/artifacts/windowsPolicyChangeEvents.py': {'policy_records': (1, 'cache key')},
        'scripts/artifacts/windowsSecurityAccessEvents.py': {'access_records': (1, 'cache key')},
        'scripts/artifacts/windowsServiceEvents.py': {'service_records': (1, 'cache key')},
        'scripts/artifacts/windowsSrum.py': {'_open': (1, 'cache key')},
        'scripts/artifacts/windowsUserAccessLogging.py': {'_open': (1, 'cache key')},
    },
}


class Reads(ast.NodeVisitor):
    """Every read of a stat time in one module: (line, what, enclosing function)."""

    def __init__(self):
        self.stack = []
        self.found = []

    def _add(self, node, what):
        self.found.append((node.lineno, what, '.'.join(self.stack) or '<module>'))

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name in STAT_NAMES or alias.name in STAT_ATTRIBUTES:
                self._add(node, alias.name)

    def visit_Attribute(self, node):
        if node.attr in STAT_NAMES or node.attr in STAT_ATTRIBUTES:
            self._add(node, node.attr)
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in STAT_NAMES or node.id in STAT_ATTRIBUTES:
            self._add(node, node.id)

    def visit_Call(self, node):
        name = node.func.id if isinstance(node.func, ast.Name) else ''
        if name == 'getattr' and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                and node.args[1].value in (STAT_NAMES | STAT_ATTRIBUTES):
            self._add(node, node.args[1].value)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        value, index = node.value, node.slice
        if isinstance(value, ast.Call) and isinstance(index, ast.Constant) and index.value in STAT_TUPLE_INDEXES:
            name = value.func.attr if isinstance(value.func, ast.Attribute) else getattr(value.func, 'id', '')
            if name in ('stat', 'lstat'):
                self._add(node, f'{name}()[{index.value}]')
        self.generic_visit(node)


def reads_in(source, filename='<source>'):
    """[(line, what, function)] for one module's source."""
    visitor = Reads()
    visitor.visit(ast.parse(source, filename))
    return sorted(visitor.found)


def core_of(root):
    """The core this checkout is, from scripts/version_info.py."""
    with open(os.path.join(root, 'scripts', 'version_info.py'), encoding='utf-8') as handle:
        match = re.search(r"""^leapp_name\s*=\s*['"]([^'"]+)['"]""", handle.read(), re.M)
    if not match or match.group(1) not in ALLOWED:
        raise SystemExit('could not tell which LEAPP this checkout is from scripts/version_info.py')
    return match.group(1)


def python_files(root):
    for folder, dirs, files in os.walk(os.path.join(root, 'scripts')):
        dirs[:] = sorted(d for d in dirs if d != '__pycache__')
        for name in sorted(files):
            if name.endswith('.py'):
                relative = os.path.relpath(os.path.join(folder, name), root).replace(os.sep, '/')
                if relative not in SKIPPED_FILES and not relative.startswith(SKIPPED_FOLDERS):
                    yield relative


def scan(root, allowed=None):
    """(number of files read, [problem text])."""
    allowed = ALLOWED[core_of(root)] if allowed is None else allowed
    problems, seen, count = [], {}, 0
    for relative in python_files(root):
        count += 1
        with open(os.path.join(root, relative), encoding='utf-8', errors='surrogateescape') as handle:
            source = handle.read()
        try:
            found = reads_in(source, relative)
        except (SyntaxError, ValueError) as error:
            problems.append(f'{relative}: could not be parsed, so it was not checked: {error}')
            continue
        per_function = {}
        for line, what, function in found:
            per_function.setdefault(function, []).append((line, what))
        for function, reads in per_function.items():
            seen[(relative, function)] = len(reads)
            expected = allowed.get(relative, {}).get(function)
            if expected is None or expected[0] != len(reads):
                for line, what in reads:
                    problems.append(f'{relative}:{line}: {what} in {function} reads a file stat time. Report the '
                                    "time the seeker recorded (seeker.file_infos[path].times) instead, or, if "
                                    'it never reaches a report, add it to ALLOWED with the reason.')
    for relative, functions in allowed.items():
        for function, (reads, _why) in functions.items():
            if seen.get((relative, function)) != reads:
                problems.append(f'{relative}: ALLOWED names {function} with {reads} read(s) and the file holds '
                                f'{seen.get((relative, function), 0)}. Update or remove the entry.')
    return count, sorted(set(problems))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        help='repository root')
    arguments = parser.parse_args()
    count, problems = scan(arguments.root)
    for problem in problems:
        print(problem)
    if problems:
        print(f'\n{len(problems)} problem(s) in {count} file(s).')
        return 1
    print(f'Checked {count} file(s): no staged file time reaches a report.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
