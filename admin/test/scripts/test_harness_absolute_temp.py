"""The test harness must stage a case into an absolute folder.

On Windows get_sqlite_db_path (scripts/ilapfuncs.py) puts the extended-length
prefix \\\\?\\ in front of every database path, and that prefix is only valid on an
absolute path. When process_artifact staged into the relative admin/test/temp,
every SQLite open in a case run failed with "unable to open database file". These
tests run a probe artifact through process_artifact and check that every path it
is handed is absolute and that a staged database opens through the read-only
helper the artifacts use. The path checks fail on any platform when the folder is
relative; the open fails only on Windows, so windows_smoke.yml runs this file too.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest import mock

sys.path.append(os.path.dirname(__file__))

import test_module as tm  # noqa: E402  pylint: disable=wrong-import-position
import scripts.artifacts  # noqa: E402  pylint: disable=wrong-import-position
from scripts import ilapfuncs  # noqa: E402  pylint: disable=wrong-import-position

REPO_ROOT = Path(__file__).resolve().parents[3]
PROBE = '_harness_absolute_temp_probe'
PROBE_MODULE = f'scripts.artifacts.{PROBE}'


def probe(context):
    """Each path the artifact is handed, and what a read-only open of the database returns."""
    rows = [('data folder', context.get_data_folder(), None),
            ('report folder', context.get_report_folder(), None)]
    for path in context.get_files_found():
        rows.append(('file found', path, None))
    for path in context.get_seeker().file_infos:
        rows.append(('file info', path, None))
    for path in context.get_files_found():
        if path.endswith('.db'):
            db = ilapfuncs.open_sqlite_db_readonly(path)
            value = db.execute('SELECT value FROM t').fetchone()[0] if db else None
            if db:
                db.close()
            rows.append(('opened', path, value))
    return ('Kind', 'Path', 'Value'), rows, ''


class HarnessAbsoluteTempTests(unittest.TestCase):

    def setUp(self):
        self._cwd = os.getcwd()
        os.chdir(REPO_ROOT)  # the harness stages under admin/test/temp in the working directory
        module = types.ModuleType(PROBE_MODULE)
        module.__file__ = tm.__file__
        module.__artifacts_v2__ = {}
        module.probe = probe
        sys.modules[PROBE_MODULE] = module
        setattr(scripts.artifacts, PROBE, module)
        self._tmp = tempfile.TemporaryDirectory()
        db_path = os.path.join(self._tmp.name, 'source.db')
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE t (value TEXT)')
        db.execute("INSERT INTO t VALUES ('staged')")
        db.commit()
        db.close()
        self.zip_path = os.path.join(self._tmp.name, 'case.zip')
        with zipfile.ZipFile(self.zip_path, 'w') as archive:
            archive.write(db_path, 'Dump/data/one.db')
            archive.writestr('Dump/data/two.txt', b'two')

    def tearDown(self):
        sys.modules.pop(PROBE_MODULE, None)
        if hasattr(scripts.artifacts, PROBE):
            delattr(scripts.artifacts, PROBE)
        self._tmp.cleanup()
        os.chdir(self._cwd)

    def run_probe(self):
        _headers, rows, *_ = tm.process_artifact(self.zip_path, PROBE, 'probe', {})
        return rows

    def test_every_path_handed_to_the_artifact_is_absolute(self):
        rows = self.run_probe()
        kinds = {kind for kind, _path, _value in rows}
        self.assertEqual(kinds, {'data folder', 'report folder', 'file found', 'file info', 'opened'})
        for kind, path, _value in rows:
            self.assertTrue(os.path.isabs(path), f'{kind} is relative: {path}')

    def test_the_folder_is_admin_test_temp_in_the_working_directory(self):
        data_folder = next(path for kind, path, _ in self.run_probe() if kind == 'data folder')
        self.assertEqual(Path(data_folder.removeprefix('\\\\?\\')).parent,
                         REPO_ROOT / 'admin' / 'test' / 'temp')

    @unittest.skipUnless(os.name == 'nt', r'the \\?\ prefix is Windows-only')
    def test_windows_stages_under_the_extended_length_prefix(self):
        # A run puts \\?\ in front of its output folder on Windows; the harness does too.
        for kind, path, _value in self.run_probe():
            if kind in ('data folder', 'report folder', 'file found'):
                self.assertTrue(path.startswith('\\\\?\\'), f'{kind} has no \\\\?\\ prefix: {path}')

    def test_a_staged_database_opens_read_only(self):
        opened = [value for kind, _path, value in self.run_probe() if kind == 'opened']
        self.assertEqual(opened, ['staged'])

    def test_a_recorded_staged_path_holds_no_local_folder(self):
        rows = self.run_probe()
        _headers, recorded = tm.process_data(('Kind', 'Path', 'Value'), rows)
        local = str(REPO_ROOT)
        for _kind, path, _value in recorded:
            self.assertNotIn(local, path)
            self.assertNotIn(REPO_ROOT.as_posix(), path)
        data_folder = next(path for kind, path, _ in recorded if kind == 'data folder')
        self.assertEqual(Path(data_folder).parent, Path('admin/test/temp'))

    def test_a_windows_spelling_of_the_staged_path_is_made_relative_too(self):
        prefixes = [('C:\\repo\\admin\\test\\temp\\', 'admin\\test\\temp\\'),
                    ('C:/repo/admin/test/temp/', 'admin/test/temp/')]
        self.assertEqual(tm.relative_temp_path('C:\\repo\\admin\\test\\temp\\extract_a_1\\x.db', prefixes),
                         'admin\\test\\temp\\extract_a_1\\x.db')
        self.assertEqual(tm.relative_temp_path('C:/repo/admin/test/temp/extract_a_1/x.db', prefixes),
                         'admin/test/temp/extract_a_1/x.db')
        self.assertEqual(tm.relative_temp_path('Dump/data/one.db', prefixes), 'Dump/data/one.db')

    def test_a_temp_folder_name_is_never_reused(self):
        base = Path(tempfile.mkdtemp())
        try:
            first = tm.unused_temp_dir(base, 'mod', 'art')
            first.mkdir()
            with mock.patch.object(tm.time, 'time_ns', return_value=int(first.name.rsplit('_', 1)[1])):
                second = tm.unused_temp_dir(base, 'mod', 'art')
            self.assertNotEqual(first, second)
            self.assertFalse(second.exists())
            self.assertRegex(second.name, r'^extract_mod_art_\d+$')
        finally:
            shutil.rmtree(base)

    def test_an_extended_length_spelling_is_made_relative_without_its_prefix(self):
        prefixes = tm.staged_temp_prefixes()
        backslashed = '\\\\?\\' + str(REPO_ROOT).replace('/', '\\')
        forward = '//?/' + REPO_ROOT.as_posix()
        self.assertEqual(
            tm.relative_temp_path(backslashed + '\\admin\\test\\temp\\extract_a_1\\x.db', prefixes),
            'admin\\test\\temp\\extract_a_1\\x.db')
        self.assertEqual(tm.relative_temp_path(forward + '/admin/test/temp/extract_a_1/x.db', prefixes),
                         'admin/test/temp/extract_a_1/x.db')


if __name__ == '__main__':
    unittest.main()
