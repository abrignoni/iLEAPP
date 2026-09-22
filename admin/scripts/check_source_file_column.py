"""Guard against a per-row Source File column that repeats one path on every row.

An artifact returns `(data_headers, data_list, source_path)`. The third element
already carries the evidence location: `artifact_processor` splits it on newlines,
reduces each piece with `Context.get_relative_path`, prints it as the report's

    <artifact name> located at: <source_path>

line, and writes it into the LAVA manifest, where it shows in the artifact
information modal. So when an artifact reads exactly one file, a per-row
`Source File` column adds a column to every row of the report that holds the
same string the modal already shows. It costs width in a table an examiner reads
under time pressure and tells them nothing the modal did not.

The column earns its place only when the source can differ between rows. That is
the case whenever the artifact's declared `paths` can match more than one file:

  * a wildcard in the file name (`*.evtx`, `*.lnk`, `*.pf`, `$I*`),
  * a wildcard directory segment, so the pattern matches per-instance folders,
  * a user-relative root (`Users/`, `Library/`, `AppData/`, ...), which repeats
    once per user profile on the image,
  * several patterns naming genuinely different files.

This check flags the opposite: a `Source File` column on an artifact whose paths
are a single, system-anchored, fixed file name.

Deliberately NOT flagged, because "one source on the images we happen to hold" is
not the same claim as "one source":

  * A per-user artifact that reads one hive on a single-user test image. Its path
    is user-relative, so it is treated as multi-source and keeps its column. That
    column is what attributes a row to a user on a multi-user machine, and
    dropping it there would be a real loss of attribution.

To silence a case this reads wrongly, add it to ALLOWLIST with a reason.
"""

import ast
import os
import re
import sys

ARTIFACTS_DIR = os.path.join('scripts', 'artifacts')

_SOURCE_COLUMN = re.compile(r'^source\s*(file|path)s?$', re.IGNORECASE)

# A path segment under which files repeat once per user profile.
_USER_ROOT = re.compile(
    r'(^|/)\*?/?(Users|Library|AppData|Documents|Profiles|Accounts|\.config)(/|$)',
    re.IGNORECASE)
# Android exposes one app directory under several storage views (data/data,
# data/user/<n>, data_mirror/...) and once per Android user, so a pattern naming
# an app directory matches several real files even though it names one logical
# store. The reverse-DNS segment is the tell, and the same shape names an app
# container on iOS.
_PACKAGE_SEGMENT = re.compile(r'^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_-]+)+$')
_ANDROID_ROOT = re.compile(
    r'(^|/)(data/data|data/user|data_mirror|shared_prefs|databases)(/|$)',
    re.IGNORECASE)
# A path anchored at a directory that exists once per machine. Flagging is
# positive: unless the pattern is anchored at one of these, it is assumed it can
# match more than one file and the column is left alone. That keeps the check
# conservative, because a wrongly removed column costs per-row attribution while
# a wrongly kept one costs only a repeated cell.
_SYSTEM_ROOT = re.compile(
    r'(^|/)(Windows|ProgramData|System32|PerfLogs'          # Windows
    r'|system|misc|efs'                                     # Android /data/system, /data/misc, /efs
    r'|private/var/db|var/db)(/|$)',                        # iOS and macOS
    re.IGNORECASE)

# module:artifact -> reason. Keep each entry keyed to the exact artifact and say why.
#
# The ALEAPP entries below are artifacts whose own notes state that their path
# pattern is tolerant, so a second copy of the system file elsewhere in an
# extraction would contribute its rows again and the column names the file each
# row came from. That is a deliberate design decision by the artifact's author,
# documented in examiner-facing notes, so the column stays.
_TOLERANT_SYSTEM_COPY = ('the artifact\'s notes state its path pattern is tolerant, so a '
                         'second copy of this system file in an extraction adds its rows '
                         'again and the column names the file each row came from')
ALLOWLIST = {
    'adbAuthorizations.py:adb_authorizations': _TOLERANT_SYSTEM_COPY,
    'appOpsAccesses.py:appops_accesses': _TOLERANT_SYSTEM_COPY,
    'installSessions.py:install_sessions': _TOLERANT_SYSTEM_COPY,
    'packageDexUsage.py:package_dex_usage_app_code': _TOLERANT_SYSTEM_COPY,
    'packageDexUsage.py:package_dex_usage_cross_package': _TOLERANT_SYSTEM_COPY,
    'packageDexUsage.py:package_dex_usage_secondary': _TOLERANT_SYSTEM_COPY,
    'packageDexUsageList.py:package_dex_usage_list_cross_package': _TOLERANT_SYSTEM_COPY,
    'packageDexUsageList.py:package_dex_usage_list_secondary': _TOLERANT_SYSTEM_COPY,
    'sRecoveryhist.py:get_sRecoveryhist': _TOLERANT_SYSTEM_COPY,
}


def _file_name(pattern):
    return pattern.rstrip('/').split('/')[-1]


def _can_match_several_files(patterns):
    """True when the declared paths can match more than one file on one image."""
    if len({_file_name(p).lower() for p in patterns}) > 1:
        return True
    for pattern in patterns:
        if '*' in _file_name(pattern):
            return True
        body = pattern.lstrip('*').lstrip('/')
        if any('*' in segment for segment in body.split('/')[:-1]):
            return True
        if _USER_ROOT.search('/' + body) and not _SYSTEM_ROOT.search('/' + body):
            return True
        if not _SYSTEM_ROOT.search('/' + body):
            # Not anchored at a once-per-machine directory, so assume it can match
            # more than one file rather than risk removing real attribution.
            return True
        if _ANDROID_ROOT.search('/' + body):
            return True
        if any(_PACKAGE_SEGMENT.match(segment) for segment in body.split('/')[:-1]):
            return True
    return False


def _artifact_paths(tree):
    """artifact key -> declared paths, from a literal __artifacts_v2__."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(getattr(t, 'id', '') == '__artifacts_v2__' for t in node.targets):
            continue
        try:
            block = ast.literal_eval(node.value)
        except (ValueError, TypeError, SyntaxError):
            return None
        found = {}
        for key, value in block.items():
            if isinstance(value, dict):
                paths = value.get('paths')
                if isinstance(paths, str):
                    paths = [paths]
                found[key] = list(paths) if paths else []
        return found
    return {}


def _source_columns(function):
    """The source-file style column names in a function's data_headers, or None
    when the headers are not statically readable."""
    headers = None
    for node in ast.walk(function):
        if isinstance(node, ast.Assign) and any(
                getattr(t, 'id', '') == 'data_headers' for t in node.targets):
            try:
                headers = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError):
                return None
    if headers is None:
        return None
    names = [h[0] if isinstance(h, (tuple, list)) else h for h in headers]
    return [n for n in names if isinstance(n, str) and _SOURCE_COLUMN.match(n.strip())]


def _processors(tree):
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        names = [d.id if isinstance(d, ast.Name) else getattr(d, 'attr', None)
                 for d in node.decorator_list]
        if 'artifact_processor' in [n for n in names if n]:
            yield node


def main():
    problems = []
    not_checked = []
    checked = 0

    for file_name in sorted(os.listdir(ARTIFACTS_DIR)):
        if not file_name.endswith('.py'):
            continue
        path = os.path.join(ARTIFACTS_DIR, file_name)
        with open(path, 'r', encoding='utf-8') as handle:
            try:
                tree = ast.parse(handle.read())
            except SyntaxError as exc:
                not_checked.append(f'{file_name}: could not parse ({exc})')
                continue
        paths_by_artifact = _artifact_paths(tree)
        if paths_by_artifact is None:
            not_checked.append(f'{file_name}: __artifacts_v2__ is not a literal')
            continue
        for function in _processors(tree):
            columns = _source_columns(function)
            if columns is None:
                not_checked.append(f'{file_name}:{function.name}: data_headers is not literal')
                continue
            checked += 1
            if not columns:
                continue
            declared = paths_by_artifact.get(function.name)
            if not declared:
                continue
            if _can_match_several_files(declared):
                continue
            if f'{file_name}:{function.name}' in ALLOWLIST:
                continue
            problems.append(
                f'  {file_name}:{function.name}: {columns[0]} repeats one path on every '
                f'row. Its paths match a single system-wide file '
                f'({declared[0]}), and the location already reaches the report and the '
                f'LAVA manifest through the third return element. Drop the column, or '
                f'allowlist it with a reason.')

    if problems:
        print('A Source File column repeats one path on every row:\n')
        print('\n'.join(problems))
        print(f'\nChecked {checked} artifact(s); {len(problems)} need attention.')
        return 1

    print(f'Checked {checked} artifact(s): no Source File column repeats a single path.')
    if not_checked:
        print(f'{len(not_checked)} artifact(s)/module(s) NOT checked:')
        for entry in not_checked:
            print(f'  {entry}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
