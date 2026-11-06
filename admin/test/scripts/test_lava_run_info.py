"""The run info initialize_lava() records in parser_info.

platform() leaves the architecture out on Windows, so it is recorded on its own.
"""
import pathlib
import platform
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position


class TestRunInfoArchitecture(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            lavafuncs.lava_db.close()
        lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        lavafuncs.lava_db_path = None
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_architecture_is_what_the_process_reports(self):
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        parser_info = lavafuncs.lava_data['parser_info']
        self.assertEqual(parser_info['architecture'], platform.machine())
        self.assertEqual(parser_info['OS'], platform.platform())

    def test_architecture_comes_from_machine_not_the_os_string(self):
        # A planted value proves the field is read from machine() and not parsed out of
        # the OS string, which has no architecture on Windows.
        with mock.patch.object(lavafuncs, 'machine', return_value='ARM64'), \
                mock.patch.object(lavafuncs, 'platform', return_value='Windows-11-10.0.26100-SP0'):
            lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        parser_info = lavafuncs.lava_data['parser_info']
        self.assertEqual(parser_info['architecture'], 'ARM64')
        self.assertEqual(parser_info['OS'], 'Windows-11-10.0.26100-SP0')


if __name__ == '__main__':
    unittest.main()
