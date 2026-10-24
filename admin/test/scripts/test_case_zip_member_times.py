"""A case zip's members keep the times their source members recorded.

The case-zip cutter (make_test_data.py, or make_case_data.py in DLEAPP) copies the
files an artifact matches out of a source archive. The seekers record a staged file's
times from the archive it came from, and the test harness stages a case zip the way
FileSeekerZip does, so a case zip member has to carry what its source member recorded
for an artifact to get the same times in a test case as in a run of the source. These
tests stage a source zip and a source tar with the real seekers, stage the cut case
zip with the harness, and compare what each records.

A Cellebrite CLBX zip records its file times in metadata<suffix>/metadata.msgpack,
not in its members' extra fields, and FileSeekerZip reads a zip as CLBX only when
it holds a root version member starting with CLBX-. So a case cut from a CLBX zip
keeps the version member and the metadata records of the members it copies, and
the harness stages it through the seeker's own reading of those records.
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

import msgpack

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

# A CLBX zip (https://github.com/cellebrite-labs/clbx): each member's extended timestamp
# holds one time three times over, and the times FileSeekerZip reads come from the
# metadata record keyed by the path under filesystem1/. The record for cafe.txt is keyed
# by its UTF-8 bytes while the member name is those bytes read as Latin-1, which the
# seeker also accepts. other.db is not cut, so its record must not be carried.
CLBX_VERSION = b'CLBX-0.3.1'
CLBX_ACCESSED = 1_650_000_000
CLBX_STAMP = struct.pack('<HHBIII', 0x5455, 13, 0x07, CLBX_ACCESSED, CLBX_ACCESSED, CLBX_ACCESSED)
CLBX_CAFE_KEY = 'private/var/caf\u00e9.txt'.encode('utf-8')
CLBX_RECORDS = (
    (b'private/var/one.db', {'btime': 1_500_000_000_250_000_000, 'mtime': 1_600_000_000_500_000_000,
                             'atime': CLBX_ACCESSED * 10**9, 'ctime': 1_610_000_000_000_000_000,
                             'size': 3, 'mode': 0o100644, 'xattr': {'com.apple.x': b'\x01'}}),
    (b'private/var/other.db', {'btime': 1, 'mtime': 2, 'atime': 3, 'ctime': 4, 'size': 5}),
    (CLBX_CAFE_KEY, {'btime': 1_400_000_000_000_000_000, 'mtime': (1 << 63) - 1,
                     'atime': CLBX_ACCESSED * 10**9, 'ctime': 1_420_000_000_000_000_000, 'size': 4}),
)
CLBX_MEMBERS = (
    ('filesystem1/private/var/one.db', b'one'),
    ('filesystem1/private/var/other.db', b'other'),
    ('filesystem1/' + CLBX_CAFE_KEY.decode('latin-1'), b'cafe'),
)
CLBX_CUT = ('filesystem1/private/var/one.db', 'filesystem1/' + CLBX_CAFE_KEY.decode('latin-1'))


def _packed_map(pairs):
    packer = msgpack.Packer(use_bin_type=True)
    return packer.pack_map_header(len(pairs)) + b''.join(packer.pack(k) + packer.pack(v) for k, v in pairs)


def _clbx_metadata_pairs(archive, member):
    """(key bytes, record bytes) for each record of a metadata.msgpack, exactly as stored."""
    data = archive.read(member)
    unpacker = msgpack.Unpacker(raw=True)
    unpacker.feed(data)
    pairs = []
    for _ in range(unpacker.read_map_header()):
        start = unpacker.tell()
        key = unpacker.unpack()
        middle = unpacker.tell()
        unpacker.skip()
        pairs.append((key, data[start:middle], data[middle:unpacker.tell()]))
    return pairs


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



class ClbxCaseZipTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.source_zip = os.path.join(self.tmp, 'clbx.zip')
        with zipfile.ZipFile(self.source_zip, 'w') as archive:
            archive.writestr(zipfile.ZipInfo('version', date_time=(1980, 1, 1, 0, 0, 0)), CLBX_VERSION)
            archive.writestr(zipfile.ZipInfo('filesystem1/', date_time=(2023, 6, 29, 1, 2, 4)), b'')
            for name, content in CLBX_MEMBERS:
                info = zipfile.ZipInfo(name, date_time=(2023, 6, 29, 1, 2, 4))
                info.extra = CLBX_STAMP
                archive.writestr(info, content)
            archive.writestr(zipfile.ZipInfo('metadata1/metadata.msgpack', date_time=(2023, 6, 29, 1, 2, 4)),
                             _packed_map(CLBX_RECORDS))

    def tearDown(self):
        self._tmp.cleanup()

    def cut(self, file_list=None):
        matched = _quietly(cutter.process_archive, self.source_zip, {'probe': ('*/one.db', '*/caf*')},
                           file_list)
        case_zip = os.path.join(self.tmp, 'case.zip')
        with zipfile.ZipFile(self.source_zip) as source:
            _quietly(cutter.write_case_zip, case_zip, matched['probe'], source, self.source_zip)
        return case_zip

    def harness_view(self, case_zip):
        infos = {}
        with zipfile.ZipFile(case_zip) as archive:
            _quietly(tm.stage_case_members, archive, os.path.join(self.tmp, 'harness'), infos)
        return {info.source_path: ((info.creation_date, info.modification_date), os.path.getmtime(path))
                for path, info in infos.items()}

    def seeker_view(self, names=CLBX_CUT):
        seeker = _quietly(FileSeekerZip, self.source_zip, os.path.join(self.tmp, 'seeker'))
        view = {}
        try:
            for name in names:
                staged = _quietly(seeker.search, f'*/{name}', True)
                info = seeker.file_infos[staged]
                view[name] = ((info.creation_date, info.modification_date), os.path.getmtime(staged))
        finally:
            seeker.cleanup()
        return view

    def test_the_cut_keeps_the_version_member_and_the_filesystem_layout(self):
        with zipfile.ZipFile(self.cut()) as archive:
            self.assertEqual(archive.read('version'), CLBX_VERSION)
            self.assertEqual(sorted(archive.namelist()),
                             sorted(('version', 'metadata1/metadata.msgpack') + CLBX_CUT))

    def test_the_metadata_holds_only_the_cut_members_records_as_the_source_stores_them(self):
        with zipfile.ZipFile(self.source_zip) as source:
            stored = {key: (key_bytes, record) for key, key_bytes, record
                      in _clbx_metadata_pairs(source, 'metadata1/metadata.msgpack')}
        with zipfile.ZipFile(self.cut()) as archive:
            carried = _clbx_metadata_pairs(archive, 'metadata1/metadata.msgpack')
        self.assertEqual([key for key, *_ in carried], [b'private/var/one.db', CLBX_CAFE_KEY])
        for key, key_bytes, record in carried:
            self.assertEqual((key_bytes, record), stored[key])

    def test_a_file_path_list_cut_carries_the_same_metadata(self):
        with zipfile.ZipFile(self.cut()) as archive:
            direct = archive.read('metadata1/metadata.msgpack')
        with zipfile.ZipFile(self.cut(list(CLBX_CUT))) as archive:
            self.assertEqual(archive.read('metadata1/metadata.msgpack'), direct)

    def test_the_harness_reads_the_times_from_the_metadata_as_the_seeker_does(self):
        harness = self.harness_view(self.cut())
        self.assertEqual(harness, self.seeker_view())
        times, staged = harness['filesystem1/private/var/one.db']
        self.assertEqual(times, (1_500_000_000.25, 1_600_000_000.5))
        self.assertEqual(staged, 1_600_000_000.5)
        self.assertNotIn(CLBX_ACCESSED, times)
        # INT64_MAX is no time, so the staged copy falls back to the zip date and time
        self.assertEqual(harness[CLBX_CUT[1]][0], (1_400_000_000, None))

    def test_the_harness_stages_a_clbx_zip_through_the_seekers_reading(self):
        names = [name for name, _content in CLBX_MEMBERS]
        harness = self.harness_view(self.source_zip)
        self.assertEqual(harness, self.seeker_view(names))
        self.assertEqual(harness['filesystem1/private/var/other.db'][0], (1e-09, 2e-09))

    def test_the_harness_stages_only_the_cut_members(self):
        self.assertEqual(sorted(self.harness_view(self.cut())), sorted(CLBX_CUT))


if __name__ == '__main__':
    unittest.main()
