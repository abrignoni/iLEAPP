"""Pin the times --hash records for a file staged from an ext4, APFS or HFS+ volume.

The vendored qnxprobe gives these readers' modification, access, change and creation
times as (seconds, nanoseconds) pairs (times()), and the staged-file record keeps all
four as Unix seconds, UTC, the fraction kept, with the source "file system". The
modification time comes from times() as well, not from the listing (entry()), which
reads an ext inode's seconds unsigned with no epoch bits and an HFS+ record's dates
from 1904 whatever its flags say. A time stored as 0 is recorded as none, as for every
disk image reader. The staged copy's own mtime is the listing's whole seconds, as it
was before this record took times().

The images are copies of qnxprobe's fixtures (admin/test/data/raw_images/README.md).
Every expected value is a literal read by a reader other than qnxprobe:

- ext4-times: e2fsprogs 1.47.4's debugfs ``stat``, which prints each stored base and
  extra field in hex, decoded here by the kernel's rule (fs/ext4/ext4.h at v7.3,
  c03c1a14507dfaf8b856c2608f9ac216021fc222: the base is signed 32-bit seconds, an
  extra field's low two bits add that many 2^32 seconds and its upper 30 bits are the
  nanoseconds). debugfs's own date text reads the base unsigned, so it is not used.
- apfs-times and hfsplus-times: macOS 27's ``stat -f %Fa %Fm %Fc %FB`` over the image
  attached read only with hdiutil (the image's SHA-256 the same before and after).

A REAL holds about a quarter of a microsecond at these magnitudes, so values are
compared to within two microseconds.
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
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.raw_image as raw_image  # pylint: disable=wrong-import-position
from scripts.raw_image import FileSeekerRaw  # pylint: disable=wrong-import-position
from scripts.search_files import staged_files_tsv_line  # pylint: disable=wrong-import-position
from scripts.version_info import leapp_name  # pylint: disable=wrong-import-position

FIXTURES = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images'
PROFILE_SUFFIX = {'aleapp': 'alprofile', 'ileapp': 'ilprofile', 'rleapp': 'rlprofile',
                  'vleapp': 'vlprofile', 'dleapp': 'dlprofile'}
TOLERANCE = 2e-6
# seconds from 1904-01-01 to 1970-01-01, the HFS+ epoch (Apple TN1150, "HFS Plus Dates")
HFS_EPOCH_DELTA = 2082844800

# (image, file, (modified, accessed, changed, created) as (seconds, nanoseconds) or
# None, the staged copy's mtime). A comment gives what debugfs prints for an ext
# inode: base:extra in hex, in the order mtime, atime, ctime, crtime.
CASES = (
    # 0x5f000003:4f784154 0x5f000001:1a7d6b1c 0x5f000002:34fad638 0x5f000000:69f5ac70
    ('ext4-times', 'plain.txt',
     ((1593835523, 333320277), (1593835521, 111106759), (1593835522, 222213518),
      (1593835520, 444427036)), 1593835523),
    # 0xf0000000:0 0x80000000:0 0x00000000:0 0xffffffff:3. The change time is stored
    # as 0. The listing reads the mtime base unsigned (4026531840, in 2097), and the
    # staged copy keeps that.
    ('ext4-times', 'pre1970.txt',
     ((-268435456, 0), (-2147483648, 0), None, (12884901887, 0)), 4026531840),
    # 0x83000000:15 0x10000000:1 0x90000000:2 0x7fffffff:0
    ('ext4-times', 'y2040.txt',
     ((2197815296, 5), (4563402752, 0), (6710886400, 0), (2147483647, 0)), 2197815296),
    # 0x60000003:78 0x60000001:28 0x60000002:50, no crtime: 16 bytes of extra fields
    ('ext4-times', 'nocrtime.txt',
     ((1610612739, 30), (1610612737, 10), (1610612738, 20), None), 1610612739),
    # 0x61000003 0x61000001 0x61000002, no extra fields at all
    ('ext4-times', 'noextra.txt',
     ((1627389955, 0), (1627389953, 0), (1627389954, 0), None), 1627389955),
    ('apfs-times', 'plain.txt',
     ((1593835523, 333333333), (1593835521, 111111111), (1792853230, 944626006),
      (1593835520, 444444444)), 1593835523),
    # macOS reads the access time as 0: stored as 0
    ('apfs-times', 'zero.txt',
     ((1627389955, 0), None, (1792853230, 944739840), (1627389952, 0)), 1627389955),
    # a hard link: macOS gives both names the one inode's times
    ('apfs-times', 'hard_a.txt',
     ((1610612739, 0), (1610612737, 0), (1792853230, 944701715), (1610612736, 0)),
     1610612739),
    ('hfsplus-times', 'plain.txt',
     ((1593835523, 0), (1593835521, 0), (1792853233, 0), (1593835520, 0)), 1593835523),
    ('hfsplus-times', 'zero.txt',
     ((1627389955, 0), None, (1792853233, 0), (1627389952, 0)), 1627389955),
    # a hard link, answered from its indirect node
    ('hfsplus-times', 'hard_a.txt',
     ((1610612739, 0), (1610612737, 0), (1792853233, 0), (1610612736, 0)), 1610612739),
)


def seconds(stamp):
    return None if stamp is None else stamp[0] + stamp[1] / 1_000_000_000


def gunzip(stem, folder):
    path = os.path.join(folder, f'{stem}.img')
    with gzip.open(FIXTURES / f'{stem}.img.gz', 'rb') as src, open(path, 'wb') as dst:
        shutil.copyfileobj(src, dst)
    return path


class VolumeTimesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='leapp_volume_times_')
        cls.images = {stem: gunzip(stem, cls.work) for stem in {case[0] for case in CASES}}

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

    def assertTimes(self, got, want):
        """got: four Unix seconds or None; want: four (seconds, nanoseconds) or None."""
        for name, value, stamp in zip(('modified', 'accessed', 'changed', 'created'), got, want):
            with self.subTest(name):
                if stamp is None:
                    self.assertIsNone(value)
                else:
                    self.assertIsNotNone(value)
                    self.assertLess(abs(value - seconds(stamp)), TOLERANCE, (value, stamp))


class RecordedTimesTests(VolumeTimesTestCase):
    """Each fixture file: all four times, the source, and the staged copy's mtime."""

    def test_each_file_records_what_an_independent_reader_reads(self):
        for stem, wanted, want, copy_mtime in CASES:
            with self.subTest(f'{stem} {wanted}'):
                path, info = self.stage(self.images[stem], wanted)
                self.assertTimes(info.times[:4], want)
                self.assertEqual(info.times.source, 'file system')
                self.assertEqual(info.times[5:], (None, None, None, None))
                # the staged copy and the run's FileInfo keep the listing's whole seconds
                self.assertEqual(os.stat(path).st_mtime, copy_mtime)
                self.assertEqual(info.modification_date, copy_mtime)

    def test_the_tsv_carries_the_times_in_utc(self):
        _path, info = self.stage(self.images['ext4-times'], 'pre1970.txt')
        cells = staged_files_tsv_line(info, 'file', None).rstrip('\n').split('\t')
        # -268435456, -2147483648, none and 12884901887 seconds from 1970-01-01 UTC
        self.assertEqual(cells[3:8], ['1961-06-30T02:35:44Z', '1901-12-13T20:45:52Z', '',
                                      '2378-04-22T19:24:47Z', 'file system'])


class HfsExpandedTimesTests(VolumeTimesTestCase):
    """An HFS+ record flagged kHFSCatExpandedTimesMask (0x1000 in its flags, Apple
    hfs-715.120.4 core/hfs_format.h) stores Unix seconds, which Apple's to_bsd_time
    returns unconverted (core/MacOSStubs.c). macOS writes no such record here, so the
    flag is set on plain.txt's file record in a copy of the image: the same stored
    words then read HFS_EPOCH_DELTA seconds later than macOS read them."""

    def test_a_record_flagged_for_expanded_times_reads_unix_seconds(self):
        image = os.path.join(tempfile.mkdtemp(dir=self.work), 'hfsplus-times.img')
        shutil.copyfile(self.images['hfsplus-times'], image)
        # createDate, contentModDate, attributeModDate and accessDate, at record
        # offsets 12 to 24 (TN1150, HFSPlusCatalogFile), from macOS's reading
        dates = (1593835520, 1593835523, 1792853233, 1593835521)
        with open(image, 'r+b') as handle:
            data = bytearray(handle.read())
            stored = struct.pack('>4I', *(value + HFS_EPOCH_DELTA for value in dates))
            at = data.find(stored)
            self.assertGreater(at, 0)
            self.assertEqual(data.find(stored, at + 1), -1, 'the dates are stored once')
            record = at - 12
            self.assertEqual(struct.unpack_from('>H', data, record)[0], 2, 'a file record')
            flags = struct.unpack_from('>H', data, record + 2)[0]
            struct.pack_into('>H', data, record + 2, flags | 0x1000)
            handle.seek(0)
            handle.write(data)
        path, info = self.stage(image, 'plain.txt')
        created, modified, changed, accessed = (value + HFS_EPOCH_DELTA for value in dates)
        self.assertTimes(info.times[:4], ((modified, 0), (accessed, 0), (changed, 0),
                                          (created, 0)))
        # the listing ignores the flag, and the staged copy keeps its reading
        self.assertEqual(os.stat(path).st_mtime, 1593835523)


class ListingFallbackTests(unittest.TestCase):
    """times() gives the modification time; the listing's is used only when times()
    gives nothing for the node."""

    def test_times_wins_and_the_listing_is_the_fallback(self):
        class Times:
            def __init__(self, answer):
                self.answer = answer

            def times(self, _node):
                if isinstance(self.answer, Exception):
                    raise self.answer
                return self.answer

        read = {'modified': (-86400, 0), 'accessed': None, 'changed': (5, 250_000_000),
                'created': (0, 0)}
        self.assertEqual(raw_image.volume_times(Times(read), None, 4294880896, 0, 0)[:5],
                         (-86400, None, 5.25, None, 'file system'))
        # a time times() gives as None is not filled from the listing
        self.assertIsNone(raw_image.volume_times(Times(dict(read, modified=None)), None,
                                                 4294880896, 0, 0).modified)
        for answer in (None, ValueError('unreadable inode')):
            with self.subTest(answer=answer):
                self.assertEqual(raw_image.volume_times(Times(answer), None, 4294880896,
                                                        0, 0)[:5],
                                 (4294880896, None, None, None, 'file system'))


class OptInVolumeTests(unittest.TestCase):
    """A real run of this LEAPP on the ext4 fixture, with and without --hash."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='leapp_volume_times_run_')
        core = leapp_name.lower()
        plugins = os.path.join(cls.tmp, 'plugins')
        os.makedirs(plugins)
        with open(os.path.join(plugins, 'volumeTimesProbe.py'), 'w', encoding='utf8') as handle:
            handle.write("def probe(*_args, **_kwargs):\n    return None\n\n\n"
                         "__artifacts__ = {'volumeTimesProbe': "
                         "('Volume Times Probe', ('*/plain.txt', '*/pre1970.txt'), probe)}\n")
        cls.profile = os.path.join(cls.tmp, f'probe.{PROFILE_SUFFIX[core]}')
        with open(cls.profile, 'w', encoding='utf8') as handle:
            handle.write('{"leapp": "%s", "format_version": 1, "plugins": ["volumeTimesProbe"]}'
                         % core)
        cls.image = gunzip('ext4-times', cls.tmp)
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
        return columns, rows

    def test_off_keeps_the_columns(self):
        columns, rows = self.runs[False]
        self.assertEqual(columns, ['id', 'file_path', 'sha256', 'kind'])
        self.assertTrue(rows)

    def test_on_records_all_four_times(self):
        columns, rows = self.runs[True]
        row = next(row for row in rows if row['file_path'].endswith('/plain.txt'))
        self.assertEqual(row['time_source'], 'file system')
        got = [row[name] for name in ('modified_time', 'accessed_time', 'changed_time',
                                      'created_time')]
        for value, stamp in zip(got, ((1593835523, 333320277), (1593835521, 111106759),
                                      (1593835522, 222213518), (1593835520, 444427036))):
            self.assertLess(abs(value - seconds(stamp)), TOLERANCE, (value, stamp))
        self.assertIn('created_time', columns)


if __name__ == '__main__':
    unittest.main()
