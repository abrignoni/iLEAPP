"""Pin the times --hash records for a file staged from a FAT12, FAT16, FAT32 or exFAT volume.

FAT keeps a wall-clock reading and no zone, exFAT one with a UTC offset beside it, so
the staged-file record keeps each reading as text exactly as the vendored qnxprobe lists it
(listdir_records), in modified_no_zone, created_no_zone and accessed_no_zone, leaves
the UTC times empty, and names the source "FAT directory entry" or "exFAT directory
entry". exFAT's UTC offsets are reported as stored in utc_offsets_as_stored and never
applied. The staged copy's own mtime is what it was before this record existed.

The images are the fixtures under admin/test/data/raw_images/. Each expected reading
is a literal, decoded from the directory entry's bytes by the field layout in
Microsoft's FAT and exFAT specifications (The Sleuth Kit 4.15.0's istat gives the same
dates and times to the second, showing the FAT access date as midnight), and checked against the vendored qnxprobe's own listing as
well, so the test cannot agree with the code by construction.
"""
import contextlib
import gzip
import io
import os
import pathlib
import shutil
import site
import sqlite3
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.raw_image as raw_image  # pylint: disable=wrong-import-position
import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.raw_image import FileSeekerRaw  # pylint: disable=wrong-import-position
from scripts.search_files import (  # pylint: disable=wrong-import-position
    staged_files_tsv_line, staged_time_values)
from scripts.vendor import qnxprobe  # pylint: disable=wrong-import-position
from scripts.version_info import leapp_name  # pylint: disable=wrong-import-position

FIXTURES = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images'
PROFILE_SUFFIX = {'aleapp': 'alprofile', 'ileapp': 'ilprofile', 'rleapp': 'rlprofile',
                  'vleapp': 'vlprofile', 'dleapp': 'dlprofile'}

# (image, file, walker class, (modified, created, accessed) as the directory entry
# stores them, the UTC offsets as stored). FAT keeps the modification time to two
# seconds, the creation time with its hundredths and the access date with no time.
CASES = (
    ('fat12-fixture', 'readme.txt', 'Fat12Walker',
     ('2026-10-10 16:53:58', '2026-10-10 16:53:59.69', '2026-10-10'), None),
    ('fat12-fixture', 'logs/deep/inner.bin', 'Fat12Walker',
     ('2026-10-10 16:53:58', '2026-10-10 16:53:59.78', '2026-10-10'), None),
    ('fat16-fixture', 'c.bin', 'Fat16Walker',
     ('2026-10-10 16:30:20', '2026-10-10 16:30:21.20', '2026-10-10'), None),
    ('fat32-deleted', 'a.bin', 'Fat32Walker',
     ('2026-09-11 01:01:24', '2026-09-11 01:01:24.94', '2026-09-11'), None),
    ('exfat-deleted', 'a.bin', 'ExfatWalker',
     ('2026-09-11 09:01:29.36', '2026-09-11 09:01:29.36', '2026-09-11 09:01:28'),
     'modified +04:00; created +04:00; accessed +04:00'),
)
SOURCE = {'Fat12Walker': 'FAT directory entry', 'Fat16Walker': 'FAT directory entry',
          'Fat32Walker': 'FAT directory entry', 'ExfatWalker': 'exFAT directory entry'}


def gunzip(stem, folder):
    path = os.path.join(folder, f'{stem}.img')
    with gzip.open(FIXTURES / f'{stem}.img.gz', 'rb') as src, open(path, 'wb') as dst:
        shutil.copyfileobj(src, dst)
    return path


def qnxprobe_listing(image, wanted):
    """The vendored qnxprobe's own recorded times for one file, by path in the volume."""
    with open(image, 'rb') as handle:
        kind = os.path.basename(image).split('-')[0]
        walker = qnxprobe.walker_for(kind, handle, 0)
        node = walker.root
        parts = wanted.split('/')
        for depth, part in enumerate(parts):
            for name, child, recorded in walker.listdir_records(node):
                if name == part:
                    if depth == len(parts) - 1:
                        return type(walker).__name__, recorded
                    node = child
                    break
            else:
                raise AssertionError(f'{wanted} is not in {image}')
    raise AssertionError(f'{wanted} is not in {image}')


def exfat_set_checksum(raw):
    """The SetChecksum of an exFAT directory entry set (exFAT specification 6.3.3)."""
    total = 0
    for index, byte in enumerate(raw):
        if index in (2, 3):
            continue
        total = (((total << 15) | (total >> 1)) + byte) & 0xFFFF
    return total


def set_exfat_offsets(image, name, offsets):
    """Write the three UTC offset bytes of one file's exFAT entry set (create, modify,
    access, at offsets 22, 23 and 24 of its File directory entry) and its checksum."""
    with open(image, 'r+b') as handle:
        data = bytearray(handle.read())
        marker = b'\xc1\x00' + name.encode('utf-16-le')
        at = data.find(marker)
        if at < 64 or data.find(marker, at + 1) != -1 or data[at - 64] != 0x85:
            raise AssertionError(f'no single live entry set for {name}')
        start = at - 64
        length = 32 * (data[start + 1] + 1)
        data[start + 22:start + 25] = bytes(offsets)
        struct.pack_into('<H', data, start + 2, exfat_set_checksum(data[start:start + length]))
        handle.seek(0)
        handle.write(data)


class FatExfatTimesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='leapp_fat_times_')
        cls.images = {stem: gunzip(stem, cls.work)
                      for stem in {case[0] for case in CASES}}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, True)

    def stage(self, image, wanted):
        out = tempfile.mkdtemp(dir=self.work)
        with mock.patch.object(raw_image, 'logfunc', lambda *_a, **_k: None), \
                contextlib.redirect_stdout(io.StringIO()):
            seeker = FileSeekerRaw(image, out)
            staged = seeker.search(f'*/{wanted}')
        self.addCleanup(seeker.cleanup)
        staged = [path for path in staged if path.replace('\\', '/').endswith('/' + wanted)]
        self.assertEqual(len(staged), 1, staged)
        return staged[0], seeker.file_infos[staged[0]]


class ReadingsTests(FatExfatTimesTestCase):
    """Each FAT and exFAT fixture: the readings, the source, and empty UTC times."""

    def test_each_reading_is_kept_as_stored(self):
        for stem, wanted, walker, readings, offsets in CASES:
            with self.subTest(f'{stem} {wanted}'):
                image = self.images[stem]
                path, info = self.stage(image, wanted)
                times = info.times
                self.assertEqual((times.modified_no_zone, times.created_no_zone,
                                  times.accessed_no_zone), readings)
                self.assertEqual(times.utc_offsets, offsets)
                self.assertEqual(times.source, SOURCE[walker])
                # no instant is recorded for a reading with no zone
                self.assertEqual(times[:4], (None, None, None, None))
                self.assertEqual((info.creation_date, info.modification_date), (0, 0))
                # the vendored reader's own listing says the same, key for key
                kind, recorded = qnxprobe_listing(image, wanted)
                self.assertEqual(kind, walker)
                accessed_key = 'accessed' if walker == 'ExfatWalker' else 'accessed date'
                self.assertEqual(readings, (recorded['modified'], recorded['created'],
                                            recorded[accessed_key]))
                # the staged copy's own mtime is the modification reading placed in
                # this machine's zone, as it was before the record kept the readings
                stamp = time.mktime(time.strptime(readings[0][:19], '%Y-%m-%d %H:%M:%S'))
                self.assertEqual(os.stat(path).st_mtime, stamp)

    def test_the_columns_and_the_tsv_carry_the_readings(self):
        _path, info = self.stage(self.images['exfat-deleted'], 'a.bin')
        self.assertEqual(staged_time_values(info), {
            'modified_time': None, 'accessed_time': None, 'changed_time': None,
            'created_time': None, 'time_source': 'exFAT directory entry',
            'modified_no_zone': '2026-09-11 09:01:29.36',
            'created_no_zone': '2026-09-11 09:01:29.36',
            'accessed_no_zone': '2026-09-11 09:01:28',
            'utc_offsets_as_stored': 'modified +04:00; created +04:00; accessed +04:00'})
        cells = staged_files_tsv_line(info, 'file', None).rstrip('\n').split('\t')
        self.assertEqual(cells[3:], ['', '', '', '', 'exFAT directory entry',
                                     '2026-09-11 09:01:29.36', '2026-09-11 09:01:29.36',
                                     '2026-09-11 09:01:28',
                                     'modified +04:00; created +04:00; accessed +04:00'])
        _path, info = self.stage(self.images['fat16-fixture'], 'c.bin')
        cells = staged_files_tsv_line(info, 'file', None).rstrip('\n').split('\t')
        self.assertEqual(cells[3:], ['', '', '', '', 'FAT directory entry',
                                     '2026-10-10 16:30:20', '2026-10-10 16:30:21.20',
                                     '2026-10-10', ''])


class ExfatOffsetTests(FatExfatTimesTestCase):
    """The offsets are reported only where the entry marks them set (bit 7)."""

    def offsets_after(self, offset_bytes):
        image = os.path.join(tempfile.mkdtemp(dir=self.work), 'exfat-deleted.img')
        shutil.copyfile(self.images['exfat-deleted'], image)
        set_exfat_offsets(image, 'a.bin', offset_bytes)
        _path, info = self.stage(image, 'a.bin')
        return info.times

    def test_no_offset_set_is_null(self):
        # the offset values with the valid bit clear are not offsets
        times = self.offsets_after((0x10, 0x10, 0x00))
        self.assertIsNone(times.utc_offsets)
        self.assertEqual(times.modified_no_zone, '2026-09-11 09:01:29.36')
        self.assertEqual(times.source, 'exFAT directory entry')

    def test_an_unset_offset_is_left_out(self):
        # create unset, modify -05:00 (108 is -20 fifteen-minute steps), access +00:00
        times = self.offsets_after((0x10, 0x80 | 108, 0x80))
        self.assertEqual(times.utc_offsets, 'modified -05:00; accessed +00:00')
        # never applied: the readings are the same text either way
        self.assertEqual((times.modified_no_zone, times.created_no_zone, times.accessed_no_zone),
                         ('2026-09-11 09:01:29.36', '2026-09-11 09:01:29.36',
                          '2026-09-11 09:01:28'))
        self.assertEqual(times[:4], (None, None, None, None))


class OtherReadersTests(unittest.TestCase):

    def test_a_reader_that_is_not_fat_or_exfat_records_no_readings(self):
        recorded = {'modified': '2026-01-01 00:00:00', 'created': '2026-01-01 00:00:00'}
        self.assertEqual(raw_image.directory_entry_readings(object(), recorded), {})
        self.assertEqual(raw_image.volume_times(object(), None, 1706400000, 0, 0, recorded)[4:],
                         ('file system', None, None, None, None))

    def test_a_fat_entry_with_no_reading_records_none(self):
        walker = qnxprobe.Fat32Walker.__new__(qnxprobe.Fat32Walker)
        times = raw_image.volume_times(walker, None, 0, 0, 0,
                                       {'modified': '', 'created': '', 'accessed date': ''})
        self.assertEqual(times, search_files.StagedTimes())


class OptInRawTests(unittest.TestCase):
    """A real run of this LEAPP on the FAT12 fixture, with and without --hash."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='leapp_fat_times_run_')
        core = leapp_name.lower()
        plugins = os.path.join(cls.tmp, 'plugins')
        os.makedirs(plugins)
        with open(os.path.join(plugins, 'fatTimesProbe.py'), 'w', encoding='utf8') as handle:
            handle.write("def probe(*_args, **_kwargs):\n    return None\n\n\n"
                         "__artifacts__ = {'fatTimesProbe': "
                         "('FAT Times Probe', ('*/readme.txt',), probe)}\n")
        cls.profile = os.path.join(cls.tmp, f'probe.{PROFILE_SUFFIX[core]}')
        with open(cls.profile, 'w', encoding='utf8') as handle:
            handle.write('{"leapp": "%s", "format_version": 1, "plugins": ["fatTimesProbe"]}'
                         % core)
        cls.image = gunzip('fat12-fixture', cls.tmp)
        cls.runs = {hashed: cls.run_leapp(core, plugins, hashed) for hashed in (False, True)}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, True)

    @classmethod
    def run_leapp(cls, core, plugins, hashed):
        out = os.path.join(cls.tmp, f'out_{hashed}')
        home = os.path.join(cls.tmp, f'home_{hashed}')
        os.makedirs(out)
        os.makedirs(home)
        env = dict(os.environ, HOME=home, APPDATA=home, XDG_CONFIG_HOME=home,
                   PYTHONUSERBASE=os.environ.get('PYTHONUSERBASE') or site.getuserbase())
        command = [sys.executable, str(REPO_ROOT / f'{core}.py'), '-t', 'raw', '-i', cls.image,
                   '-o', out, '-m', cls.profile, '--custom_artifacts_path', plugins]
        if hashed:
            command.append('--hash')
        done = subprocess.run(command, cwd=str(REPO_ROOT), env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=600, check=False)
        reports = list(pathlib.Path(out).glob('*/_lava_artifacts.db'))
        if len(reports) != 1:
            raise AssertionError(f'no report from {command}:\n{done.stdout}\n{done.stderr}')
        db = sqlite3.connect(str(reports[0]))
        try:
            columns = [row[1] for row in db.execute('PRAGMA table_info(_file_path_list)')]
            rows = [dict(zip(columns, row)) for row in
                    db.execute('SELECT * FROM _file_path_list ORDER BY file_path')]
        finally:
            db.close()
        tsv = reports[0].parent / '_TSV Exports' / '_Staged files SHA-256.tsv'
        return columns, rows, tsv.read_text(encoding='utf8') if tsv.exists() else None

    def test_off_keeps_the_columns_and_writes_no_tsv(self):
        columns, rows, tsv = self.runs[False]
        self.assertEqual(columns, ['id', 'file_path', 'sha256', 'kind'])
        self.assertTrue(rows)
        self.assertIsNone(tsv)

    def test_on_records_the_readings(self):
        columns, rows, tsv = self.runs[True]
        self.assertEqual(columns[-4:], ['modified_no_zone', 'created_no_zone', 'accessed_no_zone',
                                        'utc_offsets_as_stored'])
        row = next(row for row in rows if row['file_path'].endswith('/readme.txt')
                   and '/._' not in row['file_path'])
        self.assertEqual({key: row[key] for key in columns[4:]}, {
            'modified_time': None, 'accessed_time': None, 'changed_time': None,
            'created_time': None, 'time_source': 'FAT directory entry',
            'modified_no_zone': '2026-10-10 16:53:58',
            'created_no_zone': '2026-10-10 16:53:59.69', 'accessed_no_zone': '2026-10-10',
            'utc_offsets_as_stored': None})
        self.assertIn('\t'.join(['', '', '', '', 'FAT directory entry', '2026-10-10 16:53:58',
                                 '2026-10-10 16:53:59.69', '2026-10-10', '']) + '\n', tsv)


if __name__ == '__main__':
    unittest.main()
