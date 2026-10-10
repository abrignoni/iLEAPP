"""Artifacts that compare the iOS version return no rows when the input does not record one."""
# pylint: disable=protected-access
import importlib
import inspect
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ilapfuncs import iOS

ARTIFACTS = Path(__file__).resolve().parents[3] / 'scripts' / 'artifacts'

# Modules whose version read is not in the artifact function itself, or comes from the context.
# Each has its own test below.
OWN_TEST = {'filesApp', 'health', 'mobileInstallb', 'springboard'}

# What iOS.get_version() and context.get_installed_os_version() hold before any of the
# version-reading artifacts (lastBuild, systemVersionPlist, iTunesBackupInfo, Ph087) has run.
UNKNOWN = (None, '')


def version_modules():
    """Every artifact module that calls packaging's version.parse."""
    return sorted(path.stem for path in ARTIFACTS.glob('*.py')
                  if 'version.parse(' in path.read_text(encoding='utf-8'))


def load(stem):
    return importlib.import_module('scripts.artifacts.' + stem)


def direct_readers(module):
    """Artifact functions that read iOS.get_version() in their own body."""
    return [name for name in module.__artifacts_v2__
            if 'iOS.get_version()' in inspect.getsource(getattr(module, name).__wrapped__)]


class Context:
    def __init__(self, path, os_version=''):
        self.path = str(path)
        self.os_version = os_version

    def get_files_found(self):
        return [self.path]

    def get_report_folder(self):
        return str(Path(self.path).parent)

    def get_seeker(self):
        return None

    def get_relative_path(self, path):
        return path

    def get_installed_os_version(self):
        return self.os_version

    def get_source_file_path(self, _partial_path):
        return self.path


class TestUnknownIosVersion(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.store = self.database('PhotoData/Photos.sqlite')

    def database(self, relative):
        path = Path(self.directory.name) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.execute('CREATE TABLE placeholder (value)')
        connection.commit()
        connection.close()
        return path

    def assert_logged(self, log):
        self.assertEqual(log.call_count, 1)
        self.assertIn('No iOS version had been read', log.call_args.args[0])

    def test_every_version_module_is_exercised(self):
        for stem in version_modules():
            if stem in OWN_TEST:
                continue
            with self.subTest(module=stem):
                self.assertTrue(
                    direct_readers(load(stem)),
                    stem + ' calls version.parse but no test here runs it with an unknown '
                    'iOS version; add one and list the module in OWN_TEST')

    def test_direct_readers_return_no_rows(self):
        ran = 0
        for stem in version_modules():
            if stem in OWN_TEST:
                continue
            module = load(stem)
            for name in direct_readers(module):
                for unknown in UNKNOWN:
                    with self.subTest(module=stem, artifact=name, version=unknown), \
                            patch.object(iOS, 'get_version', return_value=unknown), \
                            patch.object(module, 'logfunc') as log:
                        _headers, rows, source = getattr(module, name).__wrapped__(
                            Context(self.store))
                        self.assertEqual(list(rows), [])
                        self.assertEqual(source, str(self.store))
                        self.assert_logged(log)
                        ran += 1
        self.assertGreater(ran, 0)

    def test_files_app_libraries(self):
        module = load('filesApp')
        store = self.database('CloudDocs/session/db/client.db')
        for unknown in UNKNOWN:
            with self.subTest(version=unknown), patch.object(module, 'logfunc') as log:
                _headers, rows, source = module.icloud_application_list.__wrapped__(
                    Context(store, unknown))
                self.assertEqual(rows, [])
                self.assertEqual(source, str(store))
                self.assert_logged(log)

    def test_health_heart_rate(self):
        module = load('health')
        for unknown in UNKNOWN:
            with self.subTest(version=unknown), patch.object(module, 'logfunc') as log:
                _headers, rows, source = module.health_heart_rate.__wrapped__(
                    Context(self.store, unknown))
                self.assertEqual(rows, [])
                self.assertEqual(source, str(self.store))
                self.assert_logged(log)

    def test_mobile_installation_logs(self):
        module = load('mobileInstallb')
        for unknown in UNKNOWN:
            with self.subTest(version=unknown), \
                    patch.object(iOS, 'get_version', return_value=unknown):
                with patch.object(module, 'logfunc') as log:
                    self.assertEqual(module._parse(Context(self.store)), ([], ''))
                    self.assert_logged(log)
                with patch.object(module, 'logfunc') as log:
                    _headers, rows, _source = module.mobileInstallb_reboots.__wrapped__(
                        Context(self.store))
                    self.assertEqual(rows, [])
                    self.assert_logged(log)
                with patch.object(module, 'logfunc') as log:
                    added = []
                    module._add_rows(Context(self.store), added.append)
                    self.assertEqual(added, [])
                    self.assert_logged(log)

    def test_springboard_alignment_candidates(self):
        module = load('springboard')
        for unknown in UNKNOWN:
            with self.subTest(version=unknown):
                self.assertEqual(module._cpbitmap_alignment_candidates(unknown), (16, 8, 4))


if __name__ == '__main__':
    unittest.main()
