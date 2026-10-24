"""FileSeekerZip takes a member's times from its NTFS or extended timestamp field.

A zip member's DOS date and time records no time zone. The NTFS extra field
(0x000a, APPNOTE.TXT 6.3.10 section 4.5.5) and the extended timestamp field
(0x5455, Info-ZIP extrafld.txt) record times in UTC. The seeker prefers the NTFS
field, then the extended timestamp, and only then the DOS date and time, for the
FileInfo times and for the staged copy's modification time. A malformed field is
logged and skipped, and the member is still staged.

An extended timestamp block with flag bit 3 set is read as having the four-value
layout of the GrayKey-style files_full.zip writer (modification, access, change,
birth), so its creation time is the fourth value. A Cellebrite CLBX zip takes its times from
metadata<suffix>/metadata.msgpack, never from its extended timestamp fields.
"""
import contextlib
import io
import os
import struct
import sys
import tempfile
import time
import unittest
import zipfile
from unittest import mock

sys.path.append(os.path.dirname(__file__))

from scripts.search_files import FileSeekerZip, zip_member_times  # noqa: E402  pylint: disable=wrong-import-position

FILETIME_AT_UNIX_EPOCH = 116444736000000000
MODIFIED = 1706459928.5   # 2024-01-28 16:38:48.5 UTC
CREATED = 1600000000.25   # 2020-09-13 12:26:40.25 UTC
ACCESSED = 1706460000.0
UT_MODIFIED = 1706400000  # a different instant, so the source of a value is visible
UT_CREATED = 1500000000
UT_CHANGED = 1706450000
# The writer's local wall clock for MODIFIED at UTC-5, as a DOS date and time.
DOS = (2024, 1, 28, 11, 38, 48)


def filetime(seconds):
    return int(round(seconds * 10_000_000)) + FILETIME_AT_UNIX_EPOCH


def ntfs_field(modified=MODIFIED, accessed=ACCESSED, created=CREATED, size=24, raw=None):
    if raw is None:
        raw = struct.pack('<QQQ', filetime(modified) if modified else 0,
                          filetime(accessed), filetime(created) if created else 0)
    body = struct.pack('<IHH', 0, 0x0001, size) + raw
    return struct.pack('<HH', 0x000a, len(body)) + body


def ut_field(flags, *times):
    body = struct.pack('<B', flags) + b''.join(struct.pack('<I', t) for t in times)
    return struct.pack('<HH', 0x5455, len(body)) + body


def block(header_id, body):
    return struct.pack('<HH', header_id, len(body)) + body


def dos_local(date_time=DOS):
    return time.mktime(date_time + (0, 0, -1))


class ZipExtraTimesTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.log = []
        patcher = mock.patch('scripts.search_files.logfunc', self.log.append)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self._tmp.cleanup()

    def stage(self, extra, date_time=DOS, name='Dump/data/one.db'):
        """Stage one member carrying extra; return (FileInfo, staged mtime)."""
        folder = tempfile.mkdtemp(dir=self.tmp)
        path = os.path.join(folder, 'source.zip')
        with zipfile.ZipFile(path, 'w') as archive:
            info = zipfile.ZipInfo(name, date_time=date_time)
            info.extra = extra
            archive.writestr(info, b'content')
        seeker = FileSeekerZip(path, os.path.join(folder, 'data'))
        self.addCleanup(seeker.cleanup)
        with contextlib.redirect_stdout(io.StringIO()):
            staged = seeker.search(f'*/{os.path.basename(name)}', return_on_first_hit=True)
        self.assertTrue(staged, 'the member must be staged whatever its extra field holds')
        with open(staged, 'rb') as fh:
            self.assertEqual(fh.read(), b'content')
        return seeker.file_infos[staged], os.stat(staged).st_mtime

    # Well-formed fields

    def test_ntfs_times_are_recorded_and_set_on_the_staged_copy(self):
        info, mtime = self.stage(ntfs_field())
        self.assertAlmostEqual(info.modification_date, MODIFIED, places=6)
        self.assertAlmostEqual(info.creation_date, CREATED, places=6)
        self.assertAlmostEqual(mtime, MODIFIED, places=5)
        self.assertEqual(self.log, [])

    def test_extended_timestamp_mtime_is_set_on_the_staged_copy(self):
        # The central directory shape macOS and Linux writers leave: flags 0x03, mtime only.
        info, mtime = self.stage(ut_field(0x03, UT_MODIFIED))
        self.assertEqual((info.creation_date, info.modification_date), (None, UT_MODIFIED))
        self.assertEqual(mtime, UT_MODIFIED)

    def test_ntfs_is_preferred_over_the_extended_timestamp(self):
        for extra in (ut_field(0x05, UT_MODIFIED, UT_CREATED) + ntfs_field(),
                      ntfs_field() + ut_field(0x05, UT_MODIFIED, UT_CREATED)):
            with self.subTest(first=extra[:2].hex()):
                info, mtime = self.stage(extra)
                self.assertAlmostEqual(info.modification_date, MODIFIED, places=6)
                self.assertAlmostEqual(info.creation_date, CREATED, places=6)
                self.assertAlmostEqual(mtime, MODIFIED, places=5)

    def test_no_time_field_keeps_the_dos_date_and_time(self):
        info, mtime = self.stage(b'')
        self.assertEqual((info.creation_date, info.modification_date), (None, None))
        self.assertEqual(mtime, dos_local())

    def test_other_fields_around_the_time_field_are_stepped_over(self):
        owner = struct.pack('<HHBBIBI', 0x7875, 11, 1, 4, 1000, 4, 1000)
        info, mtime = self.stage(owner + ntfs_field() + owner)
        self.assertAlmostEqual(info.modification_date, MODIFIED, places=6)
        self.assertAlmostEqual(mtime, MODIFIED, places=5)

    def test_extended_timestamp_times_are_read_in_flag_bit_order(self):
        # Flags 0x07 with all three times in the central directory: modification,
        # access, creation. The access time is stepped over, not read as creation.
        info, _ = self.stage(ut_field(0x07, UT_MODIFIED, 1, UT_CREATED))
        self.assertEqual((info.creation_date, info.modification_date), (UT_CREATED, UT_MODIFIED))
        info, _ = self.stage(ut_field(0x05, UT_MODIFIED, UT_CREATED))
        self.assertEqual((info.creation_date, info.modification_date), (UT_CREATED, UT_MODIFIED))
        # Access flagged but the block ends before the creation time: none is read.
        info, _ = self.stage(ut_field(0x07, UT_MODIFIED, 1))
        self.assertEqual((info.creation_date, info.modification_date), (None, UT_MODIFIED))

    def test_a_four_value_block_takes_creation_from_the_fourth_value(self):
        # Flags 0x0f, 17 bytes: modification, access, change, birth (gkls). The
        # change time is never the creation time.
        info, mtime = self.stage(ut_field(0x0f, UT_MODIFIED, 1, UT_CHANGED, UT_CREATED))
        self.assertEqual((info.creation_date, info.modification_date), (UT_CREATED, UT_MODIFIED))
        self.assertEqual(mtime, UT_MODIFIED)
        self.assertEqual(self.log, [])
        # Bit 3 set and the block ends before the fourth value: no creation time,
        # and the third value is still not read as one.
        info, _ = self.stage(ut_field(0x0f, UT_MODIFIED, 1, UT_CHANGED))
        self.assertEqual((info.creation_date, info.modification_date), (None, UT_MODIFIED))
        info, _ = self.stage(ut_field(0x0f, UT_MODIFIED))
        self.assertEqual((info.creation_date, info.modification_date), (None, UT_MODIFIED))

    def test_a_three_value_block_keeps_the_bit_order_reading(self):
        info, mtime = self.stage(ut_field(0x07, UT_MODIFIED, 1, UT_CREATED))
        self.assertEqual((info.creation_date, info.modification_date), (UT_CREATED, UT_MODIFIED))
        self.assertEqual(mtime, UT_MODIFIED)
        created, modified, staged, problems = zip_member_times(
            zipfile.ZipInfo('a', date_time=DOS))
        self.assertEqual((created, modified, staged, problems), (None, None, dos_local(), []))

    def test_a_creation_time_the_central_copy_omits_is_not_read_from_the_next_field(self):
        # Flags describe the local header, so 0x07 with 5 bytes holds only the mtime.
        info, mtime = self.stage(ut_field(0x07, UT_MODIFIED) + block(0x7875, b'\x01\x04\xe8\x03\x00\x00'))
        self.assertEqual((info.creation_date, info.modification_date), (None, UT_MODIFIED))
        self.assertEqual(mtime, UT_MODIFIED)
        self.assertEqual(self.log, [])

    def test_a_zero_ntfs_modification_time_falls_through(self):
        info, mtime = self.stage(ntfs_field(modified=0) + ut_field(0x01, UT_MODIFIED))
        self.assertEqual(info.modification_date, UT_MODIFIED)
        self.assertAlmostEqual(info.creation_date, CREATED, places=6)
        self.assertEqual(mtime, UT_MODIFIED)
        info, mtime = self.stage(ntfs_field(modified=0, created=0))
        self.assertEqual((info.creation_date, info.modification_date), (None, None))
        self.assertEqual(mtime, dos_local())

    # Malformed fields: logged, skipped, never fatal

    def assert_logged(self, text):
        self.assertTrue(any(text in line for line in self.log), (text, self.log))

    def test_malformed_ntfs_fields_fall_back(self):
        cases = {
            'shorter than its reserved bytes': block(0x000a, b'\x00\x00'),
            'times attribute too short': ntfs_field(size=16, raw=b'\x00' * 16),
            'attribute overruns the block': block(0x000a, struct.pack('<IHH', 0, 1, 24) + b'\x00' * 8),
            'time after the year 9999': ntfs_field(raw=struct.pack('<QQQ', 2 ** 63, 0, 0)),
        }
        for label, extra in cases.items():
            for fallback, expected in ((b'', dos_local()), (ut_field(0x01, UT_MODIFIED), UT_MODIFIED)):
                with self.subTest(label, fallback=bool(fallback)):
                    del self.log[:]
                    info, mtime = self.stage(extra + fallback)
                    self.assertEqual(mtime, expected)
                    self.assertEqual(info.modification_date, UT_MODIFIED if fallback else None)
                    self.assert_logged('NTFS extra field (0x000a) not read')

    def test_malformed_extended_timestamps_fall_back(self):
        for label, extra in {'no flags byte': block(0x5455, b''),
                             'mtime flagged, too short': block(0x5455, b'\x01\x00\x00')}.items():
            with self.subTest(label):
                del self.log[:]
                info, mtime = self.stage(extra)
                self.assertEqual((info.creation_date, info.modification_date), (None, None))
                self.assertEqual(mtime, dos_local())
                self.assert_logged('extended timestamp field (0x5455) not read')

    def test_a_cut_extra_block_is_reported_not_raised(self):
        # zipfile refuses to open an archive whose central extra field is cut, so this
        # shape reaches the reader only from a ZipInfo built some other way.
        info = zipfile.ZipInfo('a', date_time=DOS)
        info.extra = ntfs_field()[:-4]
        created, modified, staged, problems = zip_member_times(info)
        self.assertEqual((created, modified, staged), (None, None, dos_local()))
        self.assertEqual(len(problems), 1)
        self.assertIn('declares', problems[0])

    def test_a_time_the_volume_refuses_falls_back_to_the_dos_date_and_time(self):
        real = os.utime
        calls = []

        def refuse_first(path, times):
            calls.append(times)
            if len(calls) == 1:
                raise OverflowError('timestamp out of range for platform time_t')
            return real(path, times)

        with mock.patch('scripts.search_files.os.utime', refuse_first):
            info, mtime = self.stage(ntfs_field())
        self.assertAlmostEqual(info.modification_date, MODIFIED, places=6)
        self.assertEqual(mtime, dos_local())
        self.assert_logged('could not be set')


try:
    import msgpack
except ImportError:
    msgpack = None

# The int64 extremes: values the seeker treats as no time. INT64_MAX was seen as an
# mtime on two corpus CLBX zips; INT64_MIN was not seen on any.
INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
NS = 1_000_000_000
CLBX_MODIFIED = 1706459928  # 2024-01-28 16:38:48 UTC
CLBX_BIRTH = 1600000000
CLBX_ATIME = 1706470000      # what the extended timestamp fields hold, which must not be used
# A name stored as its UTF-8 bytes read as Latin-1, as on two corpus CLBX zips.
STORED_TWICE_ENCODED = 'café.db'.encode('utf-8').decode('latin-1')


def clbx_record(btime, mtime):
    return {'mode': 0o100600, 'uid': 501, 'gid': 501, 'size': 7, 'inode': 1, 'links': 1,
            'mtime': mtime, 'ctime': mtime, 'atime': CLBX_ATIME * NS, 'btime': btime,
            'prot': 3, 'xattr': {}}


@unittest.skipUnless(msgpack, 'msgpack is needed to write and read the CLBX metadata')
class ClbxTimesTests(unittest.TestCase):
    """A CLBX zip's times come from metadata<suffix>/metadata.msgpack."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.log = []
        patcher = mock.patch('scripts.search_files.logfunc', self.log.append)
        patcher.start()
        self.addCleanup(patcher.stop)
        records = {
            'private/var/one.db': clbx_record(CLBX_BIRTH * NS + 250_000_000, CLBX_MODIFIED * NS),
            'private/var/no_birth.db': clbx_record(INT64_MIN, CLBX_MODIFIED * NS),
            'private/var/no_times.db': clbx_record(INT64_MIN, INT64_MAX),
            'private/var/café.db': clbx_record(CLBX_BIRTH * NS, CLBX_MODIFIED * NS),
            'private/var/not_extracted.db': clbx_record(CLBX_BIRTH * NS, CLBX_MODIFIED * NS),
        }
        self.path = os.path.join(self._tmp.name, 'EXTRACTION_FFS.zip')
        atime_field = ut_field(0x07, CLBX_ATIME, CLBX_ATIME, CLBX_ATIME)
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('version', b'CLBX-0.3.1')
            archive.writestr('metadata1/filesystem.msgpack', msgpack.packb({'mount_point': '/'}))
            archive.writestr('metadata1/metadata.msgpack', msgpack.packb(records))
            for name in ('one.db', 'no_birth.db', 'no_times.db', 'no_record.db', STORED_TWICE_ENCODED):
                info = zipfile.ZipInfo(f'filesystem1/private/var/{name}', date_time=DOS)
                info.extra = atime_field
                archive.writestr(info, b'content')

    def stage(self, name):
        seeker = FileSeekerZip(self.path, tempfile.mkdtemp(dir=self._tmp.name))
        self.addCleanup(seeker.cleanup)
        with contextlib.redirect_stdout(io.StringIO()):
            staged = seeker.search(f'*/private/var/{name}', return_on_first_hit=True)
        self.assertTrue(staged)
        return seeker.file_infos[staged], os.stat(staged).st_mtime

    def test_times_come_from_the_metadata_not_the_extended_timestamp(self):
        info, mtime = self.stage('one.db')
        self.assertEqual(info.modification_date, CLBX_MODIFIED)
        self.assertAlmostEqual(info.creation_date, CLBX_BIRTH + 0.25, places=6)
        self.assertEqual(mtime, CLBX_MODIFIED)

    def test_the_int64_extremes_are_no_time(self):
        info, mtime = self.stage('no_birth.db')
        self.assertEqual((info.creation_date, info.modification_date), (None, CLBX_MODIFIED))
        self.assertEqual(mtime, CLBX_MODIFIED)
        info, mtime = self.stage('no_times.db')
        self.assertEqual((info.creation_date, info.modification_date), (None, None))
        self.assertEqual(mtime, dos_local())

    def test_a_name_stored_as_latin1_finds_its_record(self):
        info, mtime = self.stage(STORED_TWICE_ENCODED)
        self.assertEqual((info.creation_date, info.modification_date), (CLBX_BIRTH, CLBX_MODIFIED))
        self.assertEqual(mtime, CLBX_MODIFIED)

    def test_a_member_with_no_record_falls_back_to_the_dos_date_and_time(self):
        info, mtime = self.stage('no_record.db')
        self.assertEqual((info.creation_date, info.modification_date), (None, None))
        self.assertEqual(mtime, dos_local())
        self.assertEqual(sum('has no record in the metadata' in line for line in self.log), 1)

    def test_without_msgpack_the_dos_date_and_time_is_used(self):
        with mock.patch.dict(sys.modules, {'msgpack': None}):
            info, mtime = self.stage('one.db')
        self.assertEqual((info.creation_date, info.modification_date), (None, None))
        self.assertEqual(mtime, dos_local())
        self.assertEqual(sum('msgpack package is not installed' in line for line in self.log), 1)

    def test_a_version_file_alone_is_not_clbx(self):
        os.remove(self.path)
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('version', b'CLBX-0.3.1')
            info = zipfile.ZipInfo('filesystem1/private/var/one.db', date_time=DOS)
            info.extra = ut_field(0x07, UT_MODIFIED, 1, UT_CREATED)
            archive.writestr(info, b'content')
        info, mtime = self.stage('one.db')
        self.assertEqual((info.creation_date, info.modification_date), (UT_CREATED, UT_MODIFIED))
        self.assertEqual(mtime, UT_MODIFIED)


if __name__ == '__main__':
    unittest.main()
