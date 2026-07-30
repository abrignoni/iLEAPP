"""Native Apple Unified Log (.tracev3) reading, without Apple's `log` command.

The established iLEAPP workflow needs a Mac: rebuild a .logarchive package, generate an
evidence-specific Info.plist (harder since macOS 26.4), run
`log show --style json --info --debug`, and hand iLEAPP a JSON file 15-25x the size of the
archive. Most examiners running iLEAPP are not on a Mac, and the JSON step alone produced
26.7 GB from a 1.16 GB archive in local testing.

This module removes that detour. It drives Mandiant's `unifiedlog_iterator`
(https://github.com/mandiant/macos-UnifiedLogs), a Rust parser that reads the tracev3
format directly. Three properties make it a fit:

  * it runs on Windows, Linux and macOS, so the workflow no longer needs Apple tooling;
  * it reads a plain directory holding the *contents* of `diagnostics` and `uuidtext`,
    so no .logarchive bundle and no Info.plist are required;
  * with no -o argument it streams JSONL to stdout, so records reach SQLite without a
    multi-gigabyte intermediate file ever touching disk.

On a 1.16 GB / 29.3M event store it parsed in 250s against 355s for `log show` on the
same data, so this path is not a speed trade-off.

The binary is not vendored in this repository. `find_iterator()` looks for it in an
explicit environment variable, then alongside the packaged application, then on PATH;
when it is absent the artifact reports that and does nothing, leaving the existing JSON
workflow as the supported route.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

from scripts.ilapfuncs import logfunc, is_platform_windows

BINARY_NAME = 'unifiedlog_iterator.exe' if is_platform_windows() else 'unifiedlog_iterator'

# Environment override, so an examiner can point at a build they downloaded and hashed
# themselves rather than whatever happens to be bundled.
BINARY_ENV_VAR = 'ILEAPP_UNIFIEDLOG_ITERATOR'

# Directory names that make up a logarchive. `diagnostics` supplies the tracev3 streams
# and the timesync data; `uuidtext` supplies the format strings needed to render them.
# The two never use the same top-level names, which is why their contents can be merged
# into a single directory.
DIAGNOSTICS_DIR = 'diagnostics'
UUIDTEXT_DIR = 'uuidtext'

# How many parser errors to surface before going quiet. The parser logs one line per
# record it cannot decode; a handful is normal and thousands would drown the iLEAPP log.
MAX_REPORTED_ERRORS = 20

# One parser error class dumps a whole decoded struct on a single line.
MAX_DIAGNOSTIC_LINE_LENGTH = 300


def _bundled_binary_dirs():
    """Directories to search for a binary shipped with iLEAPP, frozen or from source."""
    dirs = []
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        dirs.append(os.path.join(meipass, 'bin'))
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dirs.append(os.path.join(repo_root, 'scripts', 'bin'))
    return dirs


def find_iterator():
    """Locate the unifiedlog_iterator binary, or return None when it is unavailable."""
    override = os.environ.get(BINARY_ENV_VAR)
    if override:
        # An explicit path that does not resolve is a configuration mistake worth
        # reporting, rather than something to silently fall through.
        if os.path.isfile(override) and os.access(override, os.X_OK):
            return override
        logfunc(f'{BINARY_ENV_VAR} is set to "{override}" but that is not an executable file')
        return None

    for directory in _bundled_binary_dirs():
        candidate = os.path.join(directory, BINARY_NAME)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return shutil.which(BINARY_NAME)


def _path_components(path):
    return os.path.normpath(path).replace('\\', '/').split('/')


def find_archive_roots(files_found):
    """Work out what to hand the parser from the paths the seeker returned.

    Returns (logarchive_dir, diagnostics_dir, uuidtext_dir), where either the first item
    is set (the examiner supplied a ready-made .logarchive) or the other two are.
    """
    logarchive = None
    diagnostics = None
    uuidtext = None

    for path in files_found:
        components = _path_components(path)
        for index, component in enumerate(components):
            if component.lower().endswith('.logarchive'):
                logarchive = logarchive or '/'.join(components[:index + 1])
            elif component == DIAGNOSTICS_DIR:
                diagnostics = diagnostics or '/'.join(components[:index + 1])
            elif component == UUIDTEXT_DIR:
                uuidtext = uuidtext or '/'.join(components[:index + 1])

    return logarchive, diagnostics, uuidtext


def _link_file(source, destination):
    """Materialize one file at destination as cheaply as the filesystem allows.

    uuidtext alone runs to hundreds of megabytes, so copying it for every run is worth
    avoiding. Hardlinks cost nothing but fail across volumes and on filesystems that do
    not support them, hence the copy fallback.

    Symlinks are deliberately not used, including for whole directories, which would
    otherwise be the cheapest option by far. The parser lists directory entries without
    following links, so a symlinked Persist/ is silently skipped and the import comes back
    empty with no error anywhere.
    """
    try:
        os.link(source, destination)
    except (OSError, NotImplementedError, AttributeError):
        shutil.copy2(source, destination)


def assemble_archive(diagnostics_dir, uuidtext_dir, workdir):
    """Merge the contents of diagnostics/ and uuidtext/ into one directory.

    This is the shape the parser expects, and it is also exactly what the manual
    .logarchive reconstruction produces, minus the Info.plist that the parser does not
    need. Real directories are created and their files linked into place.
    """
    os.makedirs(workdir, exist_ok=True)

    for source_dir in (diagnostics_dir, uuidtext_dir):
        if not source_dir or not os.path.isdir(source_dir):
            continue
        for root, _, filenames in os.walk(source_dir):
            relative = os.path.relpath(root, source_dir)
            target_dir = workdir if relative == '.' else os.path.join(workdir, relative)
            os.makedirs(target_dir, exist_ok=True)
            for filename in filenames:
                destination = os.path.join(target_dir, filename)
                if os.path.exists(destination):
                    continue
                _link_file(os.path.join(root, filename), destination)

    return workdir


def _report_parser_diagnostics(stderr_file):
    """Summarize what the parser complained about, without flooding the iLEAPP log."""
    stderr_file.seek(0)
    reported = 0
    total = 0
    for line in stderr_file:
        line = line.strip()
        if not line:
            continue
        total += 1
        if reported < MAX_REPORTED_ERRORS:
            # One class of parser error dumps an entire decoded struct, which runs to
            # well over a kilobyte on a single line.
            logfunc(f'unifiedlog_iterator: {line[:MAX_DIAGNOSTIC_LINE_LENGTH]}')
            reported += 1
    if total > reported:
        logfunc(f'unifiedlog_iterator reported {total:,} messages in total; first {reported} shown. '
                f'These are per-record decode failures; the rest of the import is unaffected.')


def stream_records(binary, archive_dir):
    """Yield one decoded record per log entry, as the parser produces them.

    Deliberately a generator over the child's stdout: the parser emits tens of gigabytes
    of JSONL for a full archive, and nothing here should ever hold more than the record
    being handled.

    stderr goes to a temporary file rather than a second pipe. The parser logs one line
    per record it cannot decode, which on a real archive runs to thousands of lines; with
    stderr on a pipe that nothing drains until stdout is exhausted, the child blocks once
    the 64 KB pipe buffer fills and the import deadlocks.
    """
    command = [binary, '--mode', 'log-archive', '--input', archive_dir, '--format', 'jsonl']

    with tempfile.TemporaryFile(mode='w+', encoding='utf-8', errors='replace') as stderr_file:
        with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=stderr_file,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1) as process:

            malformed = 0
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    malformed += 1
                    if malformed <= MAX_REPORTED_ERRORS:
                        logfunc('unifiedlog_iterator emitted a line that is not valid JSON: '
                                f'{line[:MAX_DIAGNOSTIC_LINE_LENGTH]}')

            return_code = process.wait()

        if malformed > MAX_REPORTED_ERRORS:
            logfunc(f'{malformed:,} unreadable output lines in total from unifiedlog_iterator')

        _report_parser_diagnostics(stderr_file)

    # A non-zero exit after records were already yielded means a partial parse. Say so
    # rather than letting the artifact look complete.
    if return_code != 0:
        logfunc(f'unifiedlog_iterator exited with code {return_code}; results may be incomplete')
