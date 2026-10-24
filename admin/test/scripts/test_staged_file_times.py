"""Pin the times --hash records for each staged file, and where they came from.

Beside the SHA-256 and the kind, a run with --hash records the modification, access,
change and creation times the evidence container records for each staged file, in
UTC, the source they came from (one fixed vocabulary), and for a zip member its DOS
date and time as text with no zone (modified_no_zone). A time the container does not
record is blank, never filled
from another time or from the staged copy. Without --hash, _file_path_list keeps its
columns and no staged-files TSV is written. The inputs are built here; every expected
value is a literal or the value written into the input.
"""
import contextlib
import io
import os
import pathlib
import plistlib
import shutil
import site
import sqlite3
import struct
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.raw_image import volume_times  # pylint: disable=wrong-import-position
from scripts.search_files import (  # pylint: disable=wrong-import-position
    FileSeekerDir, FileSeekerTar, FileSeekerZip, StagedTimes, staged_files_tsv_line,
    staged_time_values)
from scripts.version_info import leapp_name  # pylint: disable=wrong-import-position

try:
    import msgpack
except ImportError:
    msgpack = None

FILETIME_AT_UNIX_EPOCH = 116444736000000000
NS = 1_000_000_000
INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
MODIFIED = 1706459928.5   # 2024-01-28 16:38:48.5 UTC
ACCESSED = 1706460000.25
CHANGED = 1706461000
CREATED = 1600000000.75
DOS = (2024, 1, 28, 11, 38, 48)
DOS_TEXT = '2024-01-28 11:38:48'
VOCABULARY = ('NTFS extra field', 'four-value extended timestamp',
              'Info-ZIP extended timestamp', 'CLBX metadata', 'tar header', 'file system',
              'FAT directory entry', 'exFAT directory entry', 'iTunes Manifest.db', 'none')
PROFILE_SUFFIX = {'aleapp': 'alprofile', 'ileapp': 'ilprofile', 'rleapp': 'rlprofile',
                  'vleapp': 'vlprofile', 'dleapp': 'dlprofile'}
TIME_COLUMNS = [('modified_time', 'REAL'), ('accessed_time', 'REAL'), ('changed_time', 'REAL'),
                ('created_time', 'REAL'), ('time_source', 'TEXT'), ('modified_no_zone', 'TEXT'),
                ('created_no_zone', 'TEXT'), ('accessed_no_zone', 'TEXT'),
                ('utc_offsets_as_stored', 'TEXT')]
TSV_TIME_HEADERS = ['Modified', 'Accessed', 'Changed', 'Created', 'Time Source',
                    'Modified (no zone, as stored)', 'Created (no zone, as stored)',
                    'Accessed (no zone, as stored)', 'UTC offsets (as stored)']


def filetime(seconds):
    return int(round(seconds * 10_000_000)) + FILETIME_AT_UNIX_EPOCH if seconds else 0


def ntfs_field(modified=MODIFIED, accessed=ACCESSED, created=CREATED):
    body = struct.pack('<IHH', 0, 0x0001, 24) + struct.pack(
        '<QQQ', filetime(modified), filetime(accessed), filetime(created))
    return struct.pack('<HH', 0x000a, len(body)) + body


def ut_field(flags, *times):
    body = struct.pack('<B', flags) + b''.join(struct.pack('<I', int(t)) for t in times)
    return struct.pack('<HH', 0x5455, len(body)) + body


def quiet():
    return mock.patch.object(search_files, 'logfunc', lambda *_a, **_k: None)


class StagedTimesTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_staged_times_')
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def out(self):
        return tempfile.mkdtemp(dir=self.tmp)

    def zip_times(self, extra, date_time=DOS, name='Dump/data/one.db', members=None):
        """Stage one zip member; return its FileInfo."""
        path = os.path.join(self.out(), 'in.zip')
        with zipfile.ZipFile(path, 'w') as archive:
            for member_name, data in (members or {}).items():
                archive.writestr(member_name, data)
            info = zipfile.ZipInfo(name, date_time=date_time)
            info.extra = extra
            archive.writestr(info, b'content')
        with quiet(), contextlib.redirect_stdout(io.StringIO()):
            seeker = FileSeekerZip(path, self.out())
            staged = seeker.search(f'*/{os.path.basename(name)}', return_on_first_hit=True)
        self.addCleanup(seeker.cleanup)
        return seeker.file_infos[staged]

    def clbx_times(self, record):
        """Stage one CLBX member whose metadata record holds record; return its FileInfo."""
        path = os.path.join(self.out(), 'EXTRACTION_FFS.zip')
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('version', b'CLBX-0.3.1')
            archive.writestr('metadata1/metadata.msgpack',
                             msgpack.packb({'private/var/one.db': dict(record, mode=0o100600)}))
            info = zipfile.ZipInfo('filesystem1/private/var/one.db', date_time=DOS)
            info.extra = ut_field(0x07, 1, 1, 1)  # never read for a CLBX member
            archive.writestr(info, b'content')
        with quiet(), contextlib.redirect_stdout(io.StringIO()):
            seeker = FileSeekerZip(path, self.out())
            staged = seeker.search('*/one.db', return_on_first_hit=True)
        self.addCleanup(seeker.cleanup)
        return seeker.file_infos[staged]


class TimeSourceTests(StagedTimesTestCase):
    """Each Time Source, and the times it fills."""

    def test_the_vocabulary_is_fixed(self):
        self.assertEqual(search_files.TIME_SOURCES, VOCABULARY)

    def test_ntfs_extra_field(self):
        info = self.zip_times(ntfs_field())
        self.assertAlmostEqual(info.times.modified, MODIFIED, places=6)
        self.assertAlmostEqual(info.times.accessed, ACCESSED, places=6)
        self.assertIsNone(info.times.changed)  # the field records no change time
        self.assertAlmostEqual(info.times.created, CREATED, places=6)
        self.assertEqual(info.times.source, 'NTFS extra field')
        self.assertEqual((info.times.created, info.times.modified),
                         (info.creation_date, info.modification_date))

    def test_info_zip_extended_timestamp(self):
        info = self.zip_times(ut_field(0x07, 1706400000, 1706400001, 1500000000))
        self.assertEqual(info.times[:5], (1706400000, 1706400001, None, 1500000000,
                                          'Info-ZIP extended timestamp'))

    def test_four_value_extended_timestamp(self):
        info = self.zip_times(ut_field(0x0f, 1706400000, 1706400001, 1706400002, 1500000000))
        self.assertEqual(info.times[:5], (1706400000, 1706400001, 1706400002, 1500000000,
                                          'four-value extended timestamp'))
        self.assertEqual((info.creation_date, info.modification_date), (1500000000, 1706400000))

    def test_a_member_with_both_fields_names_both(self):
        # Each time comes from the field the FileInfo time comes from: the NTFS field
        # first, then the extended timestamp for a time the NTFS field leaves at 0.
        info = self.zip_times(ntfs_field(modified=0) + ut_field(0x01, 1706400000))
        self.assertEqual(info.times.modified, 1706400000)
        self.assertAlmostEqual(info.times.created, CREATED, places=6)
        self.assertEqual(info.times.source, 'NTFS extra field; Info-ZIP extended timestamp')
        self.assertEqual((info.times.created, info.times.modified),
                         (info.creation_date, info.modification_date))

    @unittest.skipUnless(msgpack, 'msgpack is needed to write and read the CLBX metadata')
    def test_clbx_metadata(self):
        info = self.clbx_times({'mtime': int(MODIFIED * NS), 'atime': int(ACCESSED * NS),
                                'ctime': CHANGED * NS, 'btime': int(CREATED * NS)})
        for got, want in zip(info.times[:4], (MODIFIED, ACCESSED, CHANGED, CREATED)):
            self.assertAlmostEqual(got, want, places=6)  # nanoseconds read as float seconds
        self.assertEqual(info.times[4:], ('CLBX metadata', DOS_TEXT, None, None, None))

    def tar_times(self, member, fmt=tarfile.USTAR_FORMAT):
        path = os.path.join(self.out(), 'in.tar')
        with tarfile.open(path, 'w', format=fmt) as archive:
            member.size = 7
            archive.addfile(member, io.BytesIO(b'content'))
        with quiet():
            seeker = FileSeekerTar(path, self.out())
            staged = seeker.search('*/one.db', return_on_first_hit=True)
        self.addCleanup(seeker.cleanup)
        return seeker.file_infos[staged]

    def test_tar_header(self):
        member = tarfile.TarInfo('data/one.db')
        member.mtime = 1706400000
        info = self.tar_times(member)
        self.assertEqual(info.times[:5], (1706400000, None, None, None, 'tar header'))
        self.assertEqual(info.times[5:], (None, None, None, None))

    def test_tar_pax_access_and_change_times(self):
        member = tarfile.TarInfo('data/one.db')
        member.mtime = 1706400000
        member.pax_headers = {'atime': '1706400001.5', 'ctime': '1706400002.25'}
        info = self.tar_times(member, tarfile.PAX_FORMAT)
        self.assertEqual(info.times[:5], (1706400000, 1706400001.5, 1706400002.25, None,
                                          'tar header'))

    def test_a_tar_time_of_zero_is_kept(self):
        member = tarfile.TarInfo('data/one.db')
        member.mtime = 0
        info = self.tar_times(member)
        self.assertEqual(info.times[:5], (0, None, None, None, 'tar header'))
        self.assertEqual(staged_files_tsv_line(info, 'file', None).split('\t')[3],
                         '1970-01-01T00:00:00Z')

    def test_file_system_times_are_what_the_reader_exposes(self):
        class Listing:  # entry() only: a modification time
            pass

        class Stamps:  # NTFS, ReFS, F2FS: (created, modified, accessed)
            @staticmethod
            def stamps(_node):
                return (CREATED, MODIFIED, ACCESSED)

        class Times:  # Btrfs: all four, as (seconds, nanoseconds)
            @staticmethod
            def times(_node):
                return {'modified': (1706400000, 0), 'accessed': (1706400001, 500_000_000),
                        'changed': (1706400002, 0), 'created': (0, 0)}

        self.assertEqual(volume_times(Listing(), None, MODIFIED, 0, 0)[:5],
                         (MODIFIED, None, None, None, 'file system'))
        self.assertEqual(volume_times(Stamps(), None, MODIFIED, ACCESSED, CREATED)[:5],
                         (MODIFIED, ACCESSED, None, CREATED, 'file system'))
        # a creation time the reader leaves at 0 is not recorded
        self.assertEqual(volume_times(Times(), None, 1706400000, 0, 0)[:5],
                         (1706400000, 1706400001.5, 1706400002, None, 'file system'))
        # FAT and exFAT record no instant: nothing is filled
        self.assertEqual(volume_times(Listing(), None, 0, 0, 0)[:5],
                         (None, None, None, None, 'none'))

    @unittest.skipUnless(getattr(search_files, 'FileSeekerItunes', None), 'only iLEAPP reads iTunes backups')
    def test_itunes_manifest(self):
        backup = self.out()
        file_id = 'ab' + '0' * 38
        os.makedirs(os.path.join(backup, file_id[:2]))
        with open(os.path.join(backup, file_id[:2], file_id), 'wb') as handle:
            handle.write(b'content')
        record = plistlib.dumps({'LastModified': 1706400000, 'LastStatusChange': 1706400002,
                                 'Birth': 1500000000, 'Size': 7}, fmt=plistlib.PlistFormat.FMT_BINARY)
        db = sqlite3.connect(os.path.join(backup, 'Manifest.db'))
        db.execute('CREATE TABLE Files (fileID TEXT, domain TEXT, relativePath TEXT, '
                   'flags INTEGER, file BLOB)')
        db.execute('INSERT INTO Files VALUES (?, ?, ?, 1, ?)',
                   (file_id, 'HomeDomain', 'Library/one.db', record))
        db.commit()
        db.close()
        with quiet():
            seeker = getattr(search_files, 'FileSeekerItunes')(backup, self.out(), 'db', None)
            staged = seeker.search('*/one.db', return_on_first_hit=True)
        info = seeker.file_infos[staged]
        # the backup records no access time
        self.assertEqual(info.times[:5], (1706400000, None, 1706400002, 1500000000,
                                          'iTunes Manifest.db'))

    def test_a_folder_input_records_no_evidence_times(self):
        folder = os.path.join(self.tmp, 'folder', 'data')
        os.makedirs(folder)
        with open(os.path.join(folder, 'one.db'), 'wb') as handle:
            handle.write(b'content')
        os.utime(os.path.join(folder, 'one.db'), (MODIFIED, MODIFIED))
        with quiet():
            seeker = FileSeekerDir(os.path.dirname(folder), self.out())
            staged = seeker.search('*/one.db', return_on_first_hit=True)
        info = seeker.file_infos[staged]
        # the copy on the examiner's disk has a modification time; it is not the evidence's
        self.assertEqual(info.times, StagedTimes())
        self.assertEqual(info.times.source, 'none')


class BlankNotGuessedTests(StagedTimesTestCase):

    def test_a_zip_member_with_no_time_field_records_none(self):
        info = self.zip_times(b'')
        self.assertEqual(info.times, StagedTimes(None, None, None, None, 'none', DOS_TEXT))
        # the staged copy still takes the DOS date and time; the record does not
        self.assertEqual(info.times.modified, None)

    def test_a_time_the_central_copy_omits_is_blank(self):
        # flags 0x07 name three times, the central copy holds the modification time only
        info = self.zip_times(ut_field(0x07, 1706400000))
        self.assertEqual(info.times[:5], (1706400000, None, None, None,
                                          'Info-ZIP extended timestamp'))

    def test_a_zip_slot_stored_as_zero_is_blank(self):
        # the shape an acquisition tool's zip holds: access and creation slots at 0
        info = self.zip_times(ut_field(0x07, 1706477929, 0, 0))
        self.assertEqual(info.times[:5], (1706477929, None, None, None,
                                          'Info-ZIP extended timestamp'))

    def test_blank_times_are_null_in_lava_and_empty_in_the_tsv(self):
        info = self.zip_times(ut_field(0x01, 1706400000))
        values = staged_time_values(info)
        self.assertEqual(values, {'modified_time': 1706400000, 'accessed_time': None,
                                  'changed_time': None, 'created_time': None,
                                  'time_source': 'Info-ZIP extended timestamp',
                                  'modified_no_zone': DOS_TEXT, 'created_no_zone': None,
                                  'accessed_no_zone': None, 'utc_offsets_as_stored': None})
        cells = staged_files_tsv_line(info, 'file', None).rstrip('\n').split('\t')
        self.assertEqual(cells, ['Dump/data/one.db', 'file', '', '2024-01-28T00:00:00Z', '', '',
                                 '', 'Info-ZIP extended timestamp', DOS_TEXT, '', '', ''])

    def test_a_far_future_time_is_kept_as_stored(self):
        far = 4290000000  # 2105-12-13, near the end of what the 4-byte field holds
        info = self.zip_times(ut_field(0x01, far))
        self.assertEqual(info.times.modified, far)


@unittest.skipUnless(msgpack, 'msgpack is needed to write and read the CLBX metadata')
class ClbxEmptyTimeTests(StagedTimesTestCase):

    def test_int64_max_and_min_are_blank(self):
        info = self.clbx_times({'mtime': int(MODIFIED * NS), 'atime': INT64_MAX,
                                                 'ctime': INT64_MIN, 'btime': INT64_MAX})
        self.assertEqual(info.times[:5], (MODIFIED, None, None, None, 'CLBX metadata'))

    def test_a_record_with_no_time_is_none(self):
        info = self.clbx_times({'mtime': INT64_MAX, 'atime': INT64_MAX,
                                                 'ctime': INT64_MAX, 'btime': INT64_MIN})
        self.assertEqual(info.times, StagedTimes(None, None, None, None, 'none', DOS_TEXT))


class ZipTimeTextTests(StagedTimesTestCase):

    def test_the_dos_date_and_time_is_text_as_stored(self):
        for date_time, text in (((2024, 1, 28, 11, 38, 48), '2024-01-28 11:38:48'),
                                ((1980, 1, 1, 0, 0, 0), '1980-01-01 00:00:00'),
                                ((2107, 12, 31, 23, 59, 58), '2107-12-31 23:59:58')):
            with self.subTest(text):
                info = self.zip_times(ntfs_field(), date_time=date_time)
                # beside the UTC times, never derived from them or they from it
                self.assertEqual(info.times.modified_no_zone, text)
                self.assertAlmostEqual(info.times.modified, MODIFIED, places=6)
                # a zip member records no creation or access reading with no zone
                self.assertEqual((info.times.created_no_zone, info.times.accessed_no_zone,
                                  info.times.utc_offsets), (None, None, None))
                self.assertEqual(info.times.source, 'NTFS extra field')

    def test_the_no_zone_columns_are_text(self):
        lavafuncs, db = self.lava_db()
        lavafuncs.lava_add_file_path_columns(search_files.STAGED_TIME_SQL_COLUMNS)
        columns = [(row[1], row[2]) for row in db.execute('PRAGMA table_info(_file_path_list)')]
        self.assertEqual(columns[4:], TIME_COLUMNS)

    def lava_db(self):
        import scripts.lavafuncs as lavafuncs  # pylint: disable=import-outside-toplevel
        db = sqlite3.connect(':memory:')
        db.execute('CREATE TABLE _file_path_list (id INTEGER PRIMARY KEY, file_path TEXT NOT NULL, '
                   'sha256 TEXT, kind TEXT)')
        patcher = mock.patch.object(lavafuncs, 'lava_db', db)
        patcher.start()
        self.addCleanup(patcher.stop)
        return lavafuncs, db


class OptInTests(unittest.TestCase):
    """A real run of this LEAPP on a small zip, with and without --hash."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='leapp_staged_times_run_')
        core = leapp_name.lower()
        plugins = os.path.join(cls.tmp, 'plugins')
        os.makedirs(plugins)
        with open(os.path.join(plugins, 'stagedTimesProbe.py'), 'w', encoding='utf8') as handle:
            handle.write("def probe(*_args, **_kwargs):\n    return None\n\n\n"
                         "__artifacts__ = {'stagedTimesProbe': "
                         "('Staged Times Probe', ('*/probe/*',), probe)}\n")
        cls.profile = os.path.join(cls.tmp, f'probe.{PROFILE_SUFFIX[core]}')
        with open(cls.profile, 'w', encoding='utf8') as handle:
            handle.write('{"leapp": "%s", "format_version": 1, "plugins": ["stagedTimesProbe"]}'
                         % core)
        cls.zip = os.path.join(cls.tmp, 'in.zip')
        with zipfile.ZipFile(cls.zip, 'w') as archive:
            info = zipfile.ZipInfo('data/probe/one.db', date_time=DOS)
            info.extra = ut_field(0x01, 1706400000)
            archive.writestr(info, b'content')
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
        # the run's history goes to a private HOME; the packages stay where they are
        env = dict(os.environ, HOME=home, APPDATA=home, XDG_CONFIG_HOME=home,
                   PYTHONUSERBASE=os.environ.get('PYTHONUSERBASE') or site.getuserbase())
        command = [sys.executable, str(REPO_ROOT / f'{core}.py'), '-t', 'zip', '-i', cls.zip,
                   '-o', out, '-m', cls.profile, '--custom_artifacts_path', plugins]
        if hashed:
            command.append('--hash')
        done = subprocess.run(command, cwd=str(REPO_ROOT), env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=600, check=False)
        reports = list(pathlib.Path(out).glob('*/_lava_artifacts.db'))
        if len(reports) != 1:
            raise AssertionError(f'no report from {command}:\n{done.stdout}\n{done.stderr}')
        report = reports[0].parent
        db = sqlite3.connect(str(reports[0]))
        try:
            columns = [(row[1], row[2]) for row in db.execute('PRAGMA table_info(_file_path_list)')]
            rows = db.execute('SELECT * FROM _file_path_list').fetchall()
        finally:
            db.close()
        tsv = report / '_TSV Exports' / '_Staged files SHA-256.tsv'
        return columns, rows, tsv.read_text(encoding='utf8') if tsv.exists() else None

    def test_off_keeps_the_columns_and_writes_no_tsv(self):
        columns, rows, tsv = self.runs[False]
        self.assertEqual(columns, [('id', 'INTEGER'), ('file_path', 'TEXT'), ('sha256', 'TEXT'),
                                   ('kind', 'TEXT')])
        self.assertEqual([row[1:] for row in rows], [('data/probe/one.db', None, 'file')])
        self.assertIsNone(tsv)

    def test_on_adds_the_time_columns_and_the_tsv_carries_them(self):
        columns, rows, tsv = self.runs[True]
        self.assertEqual(columns[4:], TIME_COLUMNS)
        self.assertEqual([row[3:] for row in rows],
                         [('file', 1706400000.0, None, None, None, 'Info-ZIP extended timestamp',
                           DOS_TEXT, None, None, None)])
        self.assertEqual(tsv.splitlines()[0].split('\t'),
                         ['Path in evidence', 'Kind', 'SHA-256'] + TSV_TIME_HEADERS)
        self.assertEqual(tsv.splitlines()[1].split('\t')[3:],
                         ['2024-01-28T00:00:00Z', '', '', '', 'Info-ZIP extended timestamp',
                          DOS_TEXT, '', '', ''])


if __name__ == '__main__':
    unittest.main()
