"""Pin the raw image seeker (scripts/raw_image.py) against independent readings.

FileSeekerRaw reads a disk image or an E01 acquisition in place through the
vendored qnxprobe and stages only the files an artifact's pattern selects. The
fixtures under admin/test/data/raw_images/ each come with a list of their files
and SHA-256 written by a different reader (see the README there), so a staged
copy is checked against what an independent reader saw, not against the reader
under test.

The E01 and split-segment paths are exercised by wrapping the same NTFS fixture
at test time: a small EWF writer lives in this file (copied from ewfprobe's own
test suite, MIT), and a split set is the raw image cut into numbered pieces.
The expected values are the fixture's, written out, never read back from the
seeker.
"""
import gzip
import hashlib
import os
import pathlib
import shutil
import struct
import sys
import tempfile
import time
import unittest
import zlib
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.raw_image as raw_image  # pylint: disable=wrong-import-position
from scripts.raw_image import (  # pylint: disable=wrong-import-position
    RAW_IMAGE_FILESYSTEMS, RAW_IMAGE_SUFFIXES, FileSeekerRaw, split_image_sibling)
from scripts.vendor import ewfprobe, qnxprobe  # pylint: disable=wrong-import-position

FIXTURES = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images'


def _hash_list(path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        digest, _, rel = line.partition('  ')
        if rel:
            out[rel.strip()] = digest.strip()
    return out


def _sha256(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# ---- a minimal EWF writer, from ewfprobe's test suite ------------------------

def _section(out, name, payload, last=False):
    start = out.tell()
    size = ewfprobe.SECTION_SIZE + len(payload)
    nxt = start if last else start + size
    head = struct.pack("<16sQQ40s", name.encode("ascii").ljust(16, b"\x00"), nxt, size,
                       b"\x00" * 40)
    out.write(head + struct.pack("<I", zlib.adler32(head) & 0xFFFFFFFF) + payload)


def _volume(chunk_count, sectors_per_chunk, sector_size, sector_count):
    data = bytearray(1052)
    data[0] = 0x01
    struct.pack_into("<III", data, 4, chunk_count, sectors_per_chunk, sector_size)
    struct.pack_into("<Q", data, 16, sector_count)
    data[52] = 0x01
    return bytes(data)


def _pack_chunks(chunks, compress):
    blob = bytearray()
    entries = []
    for chunk in chunks:
        rel = len(blob)
        if compress:
            packed = zlib.compress(chunk, 6)
            if len(packed) < len(chunk):
                entries.append(rel | ewfprobe._COMPRESSED_BIT)  # pylint: disable=protected-access
                blob += packed
                continue
        entries.append(rel)
        blob += chunk + struct.pack("<I", zlib.adler32(chunk) & 0xFFFFFFFF)
    return bytes(blob), entries


def _table_payload(entries, base):
    head = struct.pack("<IIQI", len(entries), 0, base, 0)
    payload = head + struct.pack("<I", zlib.adler32(head) & 0xFFFFFFFF)
    body = b"".join(struct.pack("<I", e) for e in entries)
    return payload + body + struct.pack("<I", zlib.adler32(body) & 0xFFFFFFFF)


def write_ewf(folder, stem, data, chunk_size=32768, sector_size=512, chunks_per_segment=None):
    """Write data as an EWF-E01 set and return the segment paths in order."""
    data = data + b"\x00" * (-len(data) % sector_size)
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)] or [b""]
    per_segment = chunks_per_segment or len(chunks)
    groups = [chunks[i:i + per_segment] for i in range(0, len(chunks), per_segment)]
    paths = []
    for index, group in enumerate(groups):
        path = os.path.join(folder, f"{stem}.E{index + 1:02d}")
        paths.append(path)
        with open(path, "wb") as out:
            out.write(struct.pack("<8sBHH", ewfprobe.SIGNATURE, 1, index + 1, 0))
            if index == 0:
                _section(out, "header", zlib.compress(b"1\nmain\nc\n\n"))
                _section(out, "volume", _volume(len(chunks), chunk_size // sector_size,
                                                sector_size, len(data) // sector_size))
            blob, entries = _pack_chunks(group, True)
            base = out.tell() + ewfprobe.SECTION_SIZE
            _section(out, "sectors", blob)
            _section(out, "table", _table_payload(entries, base))
            if index == len(groups) - 1:
                _section(out, "hash", hashlib.md5(data).digest() + b"\x00" * 16)
                _section(out, "done", b"", last=True)
            else:
                _section(out, "next", b"", last=True)
    return paths


def with_mbr(volume_bytes, start_lba=2048):
    """The volume behind an MBR whose one entry covers it in full, as a disk carries it."""
    entry = bytearray(16)
    entry[4] = 0x07                                        # NTFS/exFAT type byte
    struct.pack_into("<II", entry, 8, start_lba, len(volume_bytes) // 512)
    mbr = bytearray(start_lba * 512)
    mbr[446:462] = entry
    mbr[510:512] = b"\x55\xaa"
    return bytes(mbr) + volume_bytes


class _Recorder:
    """Stands in for logfunc so a test can read what the seeker said."""

    def __init__(self):
        self.lines = []

    def __call__(self, message=''):
        self.lines.append(str(message))

    def text(self):
        return '\n'.join(self.lines)


class RawImageSeekerTest(unittest.TestCase):
    """Staged bytes against an independent reader, on NTFS, FAT32, exFAT, E01 and split sets."""

    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.mkdtemp(prefix='raw_image_test_')
        for stem in ('ntfs-fixture', 'fat32-deleted', 'exfat-deleted'):
            with gzip.open(FIXTURES / f'{stem}.img.gz', 'rb') as src, \
                    open(os.path.join(cls.work, f'{stem}.img'), 'wb') as dst:
                shutil.copyfileobj(src, dst)
        cls.ntfs = os.path.join(cls.work, 'ntfs-fixture.img')
        cls.fat32 = os.path.join(cls.work, 'fat32-deleted.img')
        cls.exfat = os.path.join(cls.work, 'exfat-deleted.img')
        cls.ntfs_hashes = _hash_list(FIXTURES / 'ntfs-fixture.sha256')
        cls.fat32_hashes = _hash_list(FIXTURES / 'fat32-deleted.live.sha256')
        cls.exfat_hashes = _hash_list(FIXTURES / 'exfat-deleted.live.sha256')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.work, ignore_errors=True)

    def setUp(self):
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        self.log = _Recorder()
        patcher = mock.patch.object(raw_image, 'logfunc', self.log)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _seeker(self, image):
        seeker = FileSeekerRaw(image, self.data)
        self.addCleanup(seeker.cleanup)
        return seeker

    def _staged_by_source(self, seeker, volume):
        """{path within the volume: staged path} for every file the seeker staged."""
        out = {}
        for staged, info in seeker.file_infos.items():
            prefix = volume + '/'
            if info.source_path.startswith(prefix) and not info.source_path.endswith('/'):
                out[info.source_path[len(prefix):]] = staged
        return out

    def _check_volume(self, image, expected):
        # each seeker gets its own data folder: two volumes holding a file of the
        # same name would otherwise meet in one folder and exercise the
        # case-collision guard, which is not what this checks
        self.data = tempfile.mkdtemp(prefix='raw_image_data_')
        self.addCleanup(shutil.rmtree, self.data, True)
        seeker = self._seeker(image)
        self.assertEqual([v['name'] for v in seeker.volumes], ['lba0'])
        found = seeker.search('*')
        self.assertTrue(found)
        staged = self._staged_by_source(seeker, 'lba0')
        missing = sorted(set(expected) - set(staged))
        self.assertEqual(missing, [], 'files the independent reader saw and the seeker did not stage')
        differ = [rel for rel, digest in expected.items() if _sha256(staged[rel]) != digest]
        self.assertEqual(differ, [])
        return seeker, staged

    # ---- bytes -----------------------------------------------------------------

    def test_every_ntfs_file_matches_the_independent_hash_list(self):
        seeker, staged = self._check_volume(self.ntfs, self.ntfs_hashes)
        self.assertEqual(len(self.ntfs_hashes), 475)
        self.assertGreaterEqual(len(staged), 475)
        # every staged member is one the run can name back to the image
        for path, info in seeker.file_infos.items():
            self.assertTrue(info.source_path.startswith('lba0/'), info.source_path)
            if info.source_path.endswith('/'):
                self.assertTrue(os.path.isdir(path))
            else:
                self.assertTrue(os.path.isfile(path))

    def test_fat32_and_exfat_files_match_the_macos_driver(self):
        self._check_volume(self.fat32, self.fat32_hashes)
        self._check_volume(self.exfat, self.exfat_hashes)

    def test_only_matched_files_are_staged(self):
        import fnmatch
        pattern = '*/many/file_00[0-4]?.txt'
        expected = [rel for rel in self.ntfs_hashes if fnmatch.fnmatch('lba0/' + rel, pattern)]
        self.assertTrue(20 < len(expected) < 475)
        seeker = self._seeker(self.ntfs)
        found = seeker.search(pattern)
        self.assertEqual(len(found), len(expected))
        self.assertEqual(len(seeker.copied), len(expected))
        staged_files = sum(len(files) for _r, _d, files in os.walk(self.data))
        self.assertEqual(staged_files, len(expected))

    def test_a_pattern_is_matched_once_and_cached(self):
        seeker = self._seeker(self.ntfs)
        first = seeker.search('*/many/file_0001.txt')
        again = seeker.search('*/many/file_0001.txt')
        self.assertEqual(first, again)
        self.assertEqual(seeker.search('*/many/file_0001.txt', return_on_first_hit=True), first[0])

    # ---- members and metadata ---------------------------------------------------

    def test_directories_are_members_with_a_trailing_slash(self):
        seeker = self._seeker(self.ntfs)
        dirs = [m for m in seeker.name_list if m.endswith('/')]
        self.assertIn('lba0/many/', dirs)
        found = seeker.search('*/many/')
        self.assertEqual(len(found), 1)
        self.assertTrue(os.path.isdir(found[0]))
        self.assertEqual(seeker.file_infos[found[0]].source_path, 'lba0/many/')

    def test_ntfs_instants_reach_file_info_and_the_staged_copy(self):
        seeker = self._seeker(self.ntfs)
        path = seeker.search('*/many/file_0001.txt')[0]
        info = seeker.file_infos[path]
        self.assertGreater(info.creation_date, 1_600_000_000)
        self.assertGreater(info.modification_date, 1_600_000_000)
        self.assertEqual(int(os.path.getmtime(path)), int(info.modification_date))

    def test_fat_readings_stamp_the_copy_and_record_no_instant(self):
        seeker = self._seeker(self.fat32)
        path = seeker.search('*/a.bin')[0]
        info = seeker.file_infos[path]
        self.assertEqual((info.creation_date, info.modification_date), (0, 0))
        entry = seeker._entries['lba0/a.bin']  # pylint: disable=protected-access
        self.assertTrue(entry.reading)
        expected = time.mktime(time.strptime(entry.reading[:19], '%Y-%m-%d %H:%M:%S'))
        self.assertEqual(int(os.path.getmtime(path)), int(expected))

    def test_the_run_log_names_the_volumes(self):
        self._seeker(self.ntfs)
        text = self.log.text()
        self.assertIn('lba0', text)
        self.assertIn('ntfs', text)
        self.assertRegex(text, r'walked lba0: 4\d\d files')
        self.assertNotIn('WARNING', text)

    # ---- containers -------------------------------------------------------------

    def test_an_e01_set_reads_like_the_raw_image(self):
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        folder = tempfile.mkdtemp(prefix='raw_image_e01_', dir=self.work)
        paths = write_ewf(folder, 'ntfs', data, chunks_per_segment=200)
        self.assertGreater(len(paths), 1)
        seeker = self._seeker(paths[0])
        self.assertIn('an EWF acquisition of', self.log.text())
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertEqual(len(seeker.name_list), len(self._seeker(self.ntfs).name_list))

    def test_a_split_set_is_joined_from_any_one_segment(self):
        folder = tempfile.mkdtemp(prefix='raw_image_split_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            data = handle.read()
        piece = 3 * 1024 * 1024
        for index, offset in enumerate(range(0, len(data), piece), start=1):
            with open(os.path.join(folder, f'ntfs.img.{index:03d}'), 'wb') as out:
                out.write(data[offset:offset + piece])
        first = os.path.join(folder, 'ntfs.img.001')
        self.assertEqual(split_image_sibling(first), os.path.join(folder, 'ntfs.img.002'))
        seeker = self._seeker(first)
        self.assertIn('segments joined in order', self.log.text())
        found = seeker.search('*/many/file_0400.txt')
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0400.txt'])

    def test_a_partitioned_disk_names_its_volume_by_partition_and_lba(self):
        folder = tempfile.mkdtemp(prefix='raw_image_mbr_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            disk = with_mbr(handle.read())
        image = os.path.join(folder, 'disk.img')
        with open(image, 'wb') as out:
            out.write(disk)
        seeker = self._seeker(image)
        self.assertEqual([v['name'] for v in seeker.volumes], ['p1_lba2048'])
        found = seeker.search('*/many/file_0007.txt')
        self.assertEqual(len(found), 1)
        self.assertEqual(seeker.file_infos[found[0]].source_path, 'p1_lba2048/many/file_0007.txt')
        self.assertEqual(_sha256(found[0]), self.ntfs_hashes['many/file_0007.txt'])
        self.assertNotIn('WARNING', self.log.text())

    def test_a_lone_first_segment_warns_and_does_not_stage_a_cut_file(self):
        folder = tempfile.mkdtemp(prefix='raw_image_cut_', dir=self.work)
        with open(self.ntfs, 'rb') as handle:
            disk = with_mbr(handle.read())
        cut = os.path.join(folder, 'disk.img.001')
        with open(cut, 'wb') as out:
            out.write(disk[:len(disk) // 2])
        seeker = self._seeker(cut)
        text = self.log.text()
        self.assertIn('WARNING: the image is shorter than the volumes it describes', text)
        self.assertIn('bytes past the end of the image', text)
        found = seeker.search('*')
        self.assertTrue(found)
        # whatever was staged is whole and correct; a file the cut runs through is
        # named in the log and never handed over
        for path in found:
            if os.path.isfile(path):
                rel = seeker.file_infos[path].source_path[len('p1_lba2048/'):]
                if rel in self.ntfs_hashes:
                    self.assertEqual(_sha256(path), self.ntfs_hashes[rel], rel)
        self.assertIn('Not staged', self.log.text())
        self.assertIn('the image ends before the file does', self.log.text())

    # ---- edges -------------------------------------------------------------------

    def test_an_image_the_reader_cannot_place_has_no_members(self):
        blank = os.path.join(self.work, 'blank.img')
        with open(blank, 'wb') as out:
            out.write(b'\x00' * (2 * 1024 * 1024))
        seeker = self._seeker(blank)
        self.assertEqual(seeker.name_list, [])
        self.assertEqual([v['kind'] for v in seeker.volumes], ['not recognised'])
        self.assertEqual(seeker.search('*'), [])

    def test_a_failed_build_releases_the_image(self):
        closed = []
        real_open = qnxprobe.open_image

        def spy_open(path, segments=None):
            handle = real_open(path, segments)
            original = handle.close
            handle.close = lambda: (closed.append(True), original())
            return handle

        with mock.patch.object(qnxprobe, 'open_image', spy_open), \
                mock.patch.object(qnxprobe, 'volumes', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                FileSeekerRaw(self.ntfs, self.data)
        self.assertEqual(closed, [True])

    def test_cleanup_closes_the_image(self):
        seeker = FileSeekerRaw(self.ntfs, self.data)
        seeker.cleanup()
        self.assertIsNone(seeker._image)  # pylint: disable=protected-access
        seeker.cleanup()  # a second call is harmless

    def test_the_reader_finds_its_ewf_module_when_imported_as_a_package(self):
        self.assertIs(sys.modules['ewfprobe'], ewfprobe)
        self.assertIs(qnxprobe.ewfprobe, ewfprobe)

    def test_the_filesystem_list_names_only_kinds_the_reader_walks(self):
        walkers = {'QNX6': qnxprobe.Qnx6Walker, 'QNX4': qnxprobe.Qnx4Walker,
                   'ETFS': qnxprobe.EtfsWalker, 'EFS': qnxprobe.EfsWalker,
                   'ext2/3/4': qnxprobe.ExtWalker, 'F2FS': qnxprobe.F2fsWalker,
                   'FAT32': qnxprobe.Fat32Walker,
                   'exFAT': qnxprobe.ExfatWalker, 'NTFS': qnxprobe.NtfsWalker,
                   'HFS+': qnxprobe.HfsPlusWalker, 'APFS': qnxprobe.ApfsWalker,
                   'QNX IFS': qnxprobe.IfsWalker}
        names = [name.strip() for name in RAW_IMAGE_FILESYSTEMS.split(',')]
        self.assertEqual(sorted(names), sorted(walkers))
        for cls in walkers.values():
            for method in ('listdir', 'entry', 'read_file'):
                self.assertTrue(callable(getattr(cls, method)), f'{cls.__name__}.{method}')

    def test_gui_suffixes_cover_the_conventional_names(self):
        for suffix in ('img', 'dd', 'bin', 'raw', '001', 'e01'):
            self.assertIn(suffix, RAW_IMAGE_SUFFIXES)
        self.assertNotIn('zip', RAW_IMAGE_SUFFIXES)


class SplitImageSiblingTest(unittest.TestCase):
    """A numbered suffix with the next number beside it is a split image."""

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='raw_image_sibling_')
        self.addCleanup(shutil.rmtree, self.folder, True)

    def touch(self, name):
        path = os.path.join(self.folder, name)
        with open(path, 'wb') as handle:
            handle.write(b'x')
        return path

    def test_first_segment_with_its_successor(self):
        first = self.touch('image.001')
        second = self.touch('image.002')
        self.assertEqual(split_image_sibling(first), second)

    def test_first_segment_alone_is_an_image(self):
        self.assertIsNone(split_image_sibling(self.touch('image.001')))

    def test_a_gap_is_not_a_successor(self):
        first = self.touch('image.001')
        self.touch('image.003')
        self.assertIsNone(split_image_sibling(first))

    def test_width_is_kept_across_the_carry(self):
        ninth = self.touch('image.009')
        tenth = self.touch('image.010')
        self.assertEqual(split_image_sibling(ninth), tenth)

    def test_a_conventional_extension_is_not_a_segment(self):
        image = self.touch('image.img')
        self.touch('image.002')
        self.assertIsNone(split_image_sibling(image))

    def test_an_e01_is_not_a_numbered_segment(self):
        self.assertIsNone(split_image_sibling(self.touch('image.E01')))


if __name__ == '__main__':
    unittest.main()
