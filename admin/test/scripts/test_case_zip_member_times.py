"""A case zip's members keep the times their source members recorded.

The case-zip cutter (make_test_data.py, or make_case_data.py in DLEAPP) copies the
files an artifact matches out of a source archive. The seekers record a staged file's
times from the archive it came from, and the test harness stages a case zip the way
FileSeekerZip does, so a case zip member has to carry what its source member recorded
for an artifact to get the same times in a test case as in a run of the source. These
tests stage a source zip and a source tar with the real seekers, stage the cut case
zip with the harness, and compare what each records.
"""
import contextlib
import importlib
import io
import os
import struct
import sys
import tarfile
import tempfile
import unittest
import zipfile

sys.path.append(os.path.dirname(__file__))

import test_module as tm  # noqa: E402  pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerTar, FileSeekerZip  # noqa: E402  pylint: disable=wrong-import-position

CUTTER_NAME = ('make_case_data'
               if os.path.exists(os.path.join(os.path.dirname(__file__), 'make_case_data.py'))
               else 'make_test_data')
cutter = importlib.import_module(CUTTER_NAME)

# The fields an acquisition tool's zip holds for a file (measured on a UFED full file
# system zip): an extended timestamp with modification, access and creation times,
# a Unix owner record and a zip64 record.
TIMESTAMP = struct.pack('<HHBIII', 0x5455, 13, 0x07, 1706477929, 0, 0)
OWNER = struct.pack('<HHBBIBI', 0x7875, 11, 1, 4, 1000, 4, 1000)
ZIP64 = struct.pack('<HHQ', 0x0001, 8, 0)
ZIP_MEMBERS = (
    ('Dump/data/one.db', b'one', (2024, 1, 28, 16, 38, 48), TIMESTAMP + OWNER + ZIP64),
    ('Dump/data/two.txt', b'two', (2019, 1, 2, 3, 4, 6), b''),
)
TAR_MEMBERS = (
    ('Dump/data/three.db', b'three', 1722020041),
    ('Dump/data/old.txt', b'old', 100),
)


def _quietly(function, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args)


class CaseZipMemberTimesTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.source_zip = os.path.join(self.tmp, 'source.zip')
        with zipfile.ZipFile(self.source_zip, 'w') as archive:
            for name, content, date_time, extra in ZIP_MEMBERS:
                info = zipfile.ZipInfo(name, date_time=date_time)
                info.extra = extra
                archive.writestr(info, content)
        self.source_tar = os.path.join(self.tmp, 'source.tar')
        with tarfile.open(self.source_tar, 'w') as archive:
            for name, content, mtime in TAR_MEMBERS:
                member = tarfile.TarInfo(name)
                member.size = len(content)
                member.mtime = mtime
                archive.addfile(member, io.BytesIO(content))

    def tearDown(self):
        self._tmp.cleanup()

    def cut(self, source_path, opener, patterns, file_list=None):
        """Cuts a case zip from source_path and returns its path."""
        matched = _quietly(cutter.process_archive, source_path, {'probe': patterns}, file_list)
        case_zip = os.path.join(self.tmp, f'case_{os.path.basename(source_path)}.zip')
        with opener(source_path) as source:
            _quietly(cutter.write_case_zip, case_zip, matched['probe'], source, source_path)
        return case_zip

    def harness_view(self, case_zip):
        """What the harness records for each member of a case zip: name -> (times, mtime)."""
        folder = os.path.join(self.tmp, 'harness')
        infos = {}
        with zipfile.ZipFile(case_zip) as archive:
            tm.stage_case_members(archive, folder, infos)
        return {info.source_path: ((info.creation_date, info.modification_date), os.path.getmtime(path))
                for path, info in infos.items()}

    def seeker_view(self, seeker, names):
        """What a real seeker records for each named member: name -> (times, mtime)."""
        view = {}
        for name in names:
            staged = seeker.search(f'*/{name}', return_on_first_hit=True)
            info = seeker.file_infos[staged]
            view[name] = ((info.creation_date, info.modification_date), os.path.getmtime(staged))
        return view

    def test_zip_member_times_match_the_zip_seeker(self):
        names = [name for name, *_ in ZIP_MEMBERS]
        case_zip = self.cut(self.source_zip, zipfile.ZipFile, ('*/one.db', '*/two.txt'))
        seeker = FileSeekerZip(self.source_zip, os.path.join(self.tmp, 'seeker'))
        self.assertEqual(self.harness_view(case_zip), self.seeker_view(seeker, names))
        self.assertEqual(self.harness_view(case_zip)['Dump/data/one.db'][0], (0, 1706477929))

    def test_a_file_path_list_cut_keeps_the_same_times(self):
        names = [name for name, *_ in ZIP_MEMBERS]
        case_zip = self.cut(self.source_zip, zipfile.ZipFile, ('*/one.db', '*/two.txt'), names)
        seeker = FileSeekerZip(self.source_zip, os.path.join(self.tmp, 'seeker'))
        self.assertEqual(self.harness_view(case_zip), self.seeker_view(seeker, names))

    def test_the_zip64_record_is_dropped_and_the_other_records_kept(self):
        case_zip = self.cut(self.source_zip, zipfile.ZipFile, ('*/one.db',))
        with zipfile.ZipFile(case_zip) as archive:
            info = archive.getinfo('Dump/data/one.db')
            self.assertEqual(info.extra, TIMESTAMP + OWNER)
            self.assertEqual(info.date_time, (2024, 1, 28, 16, 38, 48))
            self.assertEqual(archive.read(info), b'one')

    def test_tar_member_times_match_the_tar_seeker(self):
        case_zip = self.cut(self.source_tar, tarfile.open, ('*/three.db', '*/old.txt'))
        seeker = FileSeekerTar(self.source_tar, os.path.join(self.tmp, 'seeker'))
        seen = self.seeker_view(seeker, [name for name, *_ in TAR_MEMBERS])
        harness = self.harness_view(case_zip)
        for name, _content, mtime in TAR_MEMBERS:
            self.assertEqual(harness[name][0], seen[name][0])
            self.assertEqual(harness[name][0], (0, mtime))

    def test_a_tar_time_is_carried_as_a_utc_date_clamped_to_the_zip_span(self):
        case_zip = self.cut(self.source_tar, tarfile.open, ('*/three.db', '*/old.txt'))
        with zipfile.ZipFile(case_zip) as archive:
            self.assertEqual(archive.getinfo('Dump/data/three.db').date_time, (2024, 7, 26, 18, 54, 0))
            self.assertEqual(archive.getinfo('Dump/data/old.txt').date_time, (1980, 1, 1, 0, 0, 0))


if __name__ == '__main__':
    unittest.main()
