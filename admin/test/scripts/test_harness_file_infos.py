"""The test harness must record for a staged file what the zip seeker records.

process_artifact stages a case zip and hands the artifact a seeker. In a real run
of the same zip, FileSeekerZip.search (scripts/search_files.py) records each staged
file's member name as its source path and the creation and modification times its
extended timestamp field carries, or None, and sets the staged file's modification
time from the member's date and time. These tests run a probe artifact through
process_artifact and check it sees exactly that, the same way on every run.
"""
import os
import struct
import sys
import tempfile
import time
import types
import unittest
import zipfile
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

import test_module as tm  # noqa: E402  pylint: disable=wrong-import-position
import scripts.artifacts  # noqa: E402  pylint: disable=wrong-import-position

REPO_ROOT = Path(__file__).resolve().parents[3]
PROBE = '_harness_file_infos_probe'
PROBE_MODULE = f'scripts.artifacts.{PROBE}'

# An extended timestamp field (0x5455) carrying a modification and a creation time.
MODIFIED = 1_700_000_000
CREATED = 1_600_000_000
EXTENDED_TIMESTAMP = struct.pack('<HHBII', 0x5455, 9, 0x01 | 0x04, MODIFIED, CREATED)


def probe(context):
    """What an artifact can read about each staged file."""
    seeker = context.get_seeker()
    rows = []
    for path in sorted(context.get_files_found()):
        info = seeker.file_infos.get(path)
        rows.append((
            os.path.basename(path),
            path in seeker.file_infos,
            info.source_path if info else None,
            info.creation_date if info else None,
            info.modification_date if info else None,
            os.path.getmtime(path),
            seeker.file_infos.get(path + '.not-in-the-zip'),
        ))
    return ('Name', 'Known', 'Source', 'Created', 'Modified', 'Staged mtime', 'Other'), rows, ''


class HarnessFileInfosTests(unittest.TestCase):

    def setUp(self):
        self._cwd = os.getcwd()
        os.chdir(REPO_ROOT)  # process_artifact stages under the relative admin/test/temp
        module = types.ModuleType(PROBE_MODULE)
        module.__file__ = tm.__file__
        module.__artifacts_v2__ = {}
        module.probe = probe
        sys.modules[PROBE_MODULE] = module
        setattr(scripts.artifacts, PROBE, module)
        self._tmp = tempfile.TemporaryDirectory()
        self.zip_path = os.path.join(self._tmp.name, 'case.zip')
        with zipfile.ZipFile(self.zip_path, 'w') as archive:
            with_times = zipfile.ZipInfo('Dump/data/one.db', date_time=(2021, 5, 6, 7, 8, 10))
            with_times.extra = EXTENDED_TIMESTAMP
            archive.writestr(with_times, b'one')
            archive.writestr(zipfile.ZipInfo('Dump/data/two.txt', date_time=(2019, 1, 2, 3, 4, 6)),
                             b'two')
            archive.writestr(zipfile.ZipInfo('Dump/data/sub/', date_time=(2019, 1, 2, 3, 4, 6)), b'')

    def tearDown(self):
        sys.modules.pop(PROBE_MODULE, None)
        if hasattr(scripts.artifacts, PROBE):
            delattr(scripts.artifacts, PROBE)
        self._tmp.cleanup()
        os.chdir(self._cwd)

    def run_probe(self):
        _headers, rows, *_ = tm.process_artifact(self.zip_path, PROBE, 'probe', {})
        return {row[0]: row[1:] for row in rows}

    def test_member_with_an_extended_timestamp(self):
        known, source, created, modified, staged, other = self.run_probe()['one.db']
        self.assertTrue(known)
        self.assertEqual(source, 'Dump/data/one.db')
        self.assertEqual((created, modified), (1_600_000_000, 1_700_000_000))
        self.assertEqual(staged, time.mktime((2021, 5, 6, 7, 8, 10, 0, 0, -1)))
        self.assertIsNone(other)

    def test_member_without_one_records_none(self):
        known, source, created, modified, staged, _ = self.run_probe()['two.txt']
        self.assertTrue(known)
        self.assertEqual(source, 'Dump/data/two.txt')
        self.assertEqual((created, modified), (None, None))
        self.assertEqual(staged, time.mktime((2019, 1, 2, 3, 4, 6, 0, 0, -1)))

    def test_only_file_members_are_staged_as_files(self):
        self.assertEqual(sorted(self.run_probe()), ['one.db', 'two.txt'])

    def test_two_runs_see_the_same_values(self):
        self.assertEqual(self.run_probe(), self.run_probe())


if __name__ == '__main__':
    unittest.main()
