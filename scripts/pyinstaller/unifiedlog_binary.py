"""Locate the unifiedlog_iterator binary for the PyInstaller specs.

Shared by all six spec files so the bundling rule lives in one place.

The binary is not committed to this repository. Run
`python admin/scripts/fetch_unifiedlog_iterator.py` before building to place a verified
copy in bin/. When it is absent the build still succeeds and simply ships without native
Apple Unified Log support, which is what happens today.

It is added as a *binary* rather than as data because PyInstaller preserves the execute
permission for binaries; a data file arrives without it on macOS and Linux, and
scripts/unifiedlogs.py would then skip it as not executable.
"""
import os

# Directory holding the binaries, relative to this file: <repo root>/bin
BIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'bin')

LICENSE_NAME = 'LICENSE-unifiedlog_iterator'


def unifiedlog_binaries(windows=False):
    """Return the PyInstaller `binaries` entries for the parser, or [] when it is absent."""
    name = 'unifiedlog_iterator.exe' if windows else 'unifiedlog_iterator'
    path = os.path.join(BIN_DIR, name)
    if not os.path.isfile(path):
        print(f'unifiedlog_iterator not found at {path}; '
              f'building without native Unified Log support')
        return []
    return [(path, 'bin')]


def unifiedlog_datas(windows=False):
    """Return the `datas` entries carrying the parser's Apache-2.0 license text.

    Apache-2.0 section 4(a) requires that recipients of a redistribution get a copy of the
    license, so it ships next to the binary and only when the binary ships.
    """
    if not unifiedlog_binaries(windows):
        return []
    license_path = os.path.join(BIN_DIR, LICENSE_NAME)
    if not os.path.isfile(license_path):
        raise SystemExit(
            f'{license_path} is missing. The unifiedlog_iterator binary is Apache-2.0 '
            f'licensed and may not be redistributed without it. Re-run '
            f'admin/scripts/fetch_unifiedlog_iterator.py.')
    return [(license_path, 'bin')]
