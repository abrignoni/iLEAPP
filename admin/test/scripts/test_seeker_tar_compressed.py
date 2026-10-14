"""Pin how the tar seeker reads a compressed tar: decompressed once, then read as a plain tar.

A compressed stream seeks backwards by decompressing again from its start, and artifacts
search one after another, so a compressed tar read in place rewinds over and over. On a
5.36 GB Android extraction that was 56 rewinds and 220 GB decompressed as a .tar.gz (347 s
against 33 s for the plain tar), and about two hours projected as a .tar.xz. The seeker
now decompresses a compressed tar once into the report folder, reads that copy, and deletes
it in cleanup(). When the copy cannot be written it reads the archive in place as before.

The archives are built here with tarfile, in every compressed format this Python can
write. Every expected value is one of the member contents defined below. The same file
runs in all five LEAPP cores.
"""
import errno
import hashlib
import io
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.search_files as search_files  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerTar  # pylint: disable=wrong-import-position

# 64 KiB that does not compress, so cutting a compressed archive in half always lands
# inside this member's data and never inside the first header.
MIDDLE = b''.join(hashlib.sha256(i.to_bytes(4, 'big')).digest() for i in range(2048))
MEMBERS = (
    ('a/first.txt', b'FIRST'),
    ('m/middle.bin', MIDDLE),
    ('z/last.txt', b'LAST'),
)
SPOOL_NAME = '_decompressed_input.tar'


def _compressed_modes():
    modes = ['w:gz', 'w:bz2', 'w:xz']
    try:
        import compression.zstd  # pylint: disable=import-outside-toplevel,unused-import
        modes.append('w:zst')     # Python 3.14 and later
    except ImportError:
        pass
    return modes


class TestCompressedTarIsReadOnce(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_seeker_tar_compressed_')
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def _archive(self, mode, name):
        path = os.path.join(self.tmp, name)
        with tarfile.open(path, mode) as archive:
            for member, content in MEMBERS:
                info = tarfile.TarInfo(member)
                info.size = len(content)
                info.mtime = 1000
                archive.addfile(info, io.BytesIO(content))
        return path

    def _report(self, label):
        report = os.path.join(self.tmp, label)
        os.makedirs(report)
        return report, os.path.join(report, 'data')

    @staticmethod
    def _read(path):
        with open(path, 'rb') as handle:
            return handle.read()

    def test_a_compressed_tar_is_read_from_one_decompressed_copy(self):
        for mode in _compressed_modes():
            with self.subTest(mode=mode):
                path = self._archive(mode, f'case.tar.{mode[2:]}')
                report, data = self._report(f'report_{mode[2:]}')
                seeker = FileSeekerTar(path, data)
                spool = os.path.join(report, SPOOL_NAME)
                self.assertTrue(os.path.isfile(spool))
                self.assertNotIsInstance(seeker.tar_file.fileobj, search_files._compressed_tar_streams())  # pylint: disable=protected-access
                # out of archive order: the last member first, then the first
                self.assertEqual(self._read(seeker.search('*/last.txt', return_on_first_hit=True)), b'LAST')
                self.assertEqual(self._read(seeker.search('*/first.txt', return_on_first_hit=True)), b'FIRST')
                self.assertEqual(self._read(seeker.search('*/middle.bin', return_on_first_hit=True)), MIDDLE)
                seeker.cleanup()
                self.assertFalse(os.path.exists(spool))
                self.assertEqual(sorted(os.listdir(report)), ['data'])

    def test_a_plain_tar_is_read_in_place(self):
        path = self._archive('w', 'case.tar')
        report, data = self._report('report_plain')
        seeker = FileSeekerTar(path, data)
        self.assertIsNone(seeker._spool_path)  # pylint: disable=protected-access
        self.assertFalse(os.path.exists(os.path.join(report, SPOOL_NAME)))
        self.assertEqual(self._read(seeker.search('*/last.txt', return_on_first_hit=True)), b'LAST')
        seeker.cleanup()

    def test_the_archive_is_read_in_place_when_the_copy_cannot_be_written(self):
        path = self._archive('w:xz', 'full.tar.xz')
        report, data = self._report('report_full')
        messages = []
        disk_full = OSError(errno.ENOSPC, 'No space left on device')
        with mock.patch.object(search_files, 'copyfileobj', side_effect=disk_full), \
                mock.patch.object(search_files, 'logfunc', side_effect=messages.append):
            seeker = FileSeekerTar(path, data)
        self.assertIsNone(seeker._spool_path)  # pylint: disable=protected-access
        self.assertFalse(os.path.exists(os.path.join(report, SPOOL_NAME)))
        self.assertIsInstance(seeker.tar_file.fileobj, search_files._compressed_tar_streams())  # pylint: disable=protected-access
        self.assertTrue(any('No space left on device' in m and 'in place' in m for m in messages), messages)
        self.assertEqual(self._read(seeker.search('*/last.txt', return_on_first_hit=True)), b'LAST')
        self.assertEqual(self._read(seeker.search('*/first.txt', return_on_first_hit=True)), b'FIRST')
        seeker.cleanup()

    def test_a_truncated_archive_still_fails_and_leaves_no_copy(self):
        for mode in ('w:gz', 'w:xz'):
            with self.subTest(mode=mode):
                path = self._archive(mode, f'cut.tar.{mode[2:]}')
                with open(path, 'r+b') as handle:
                    handle.truncate(os.path.getsize(path) // 2)
                report, data = self._report(f'report_cut_{mode[2:]}')
                with self.assertRaises(EOFError):
                    FileSeekerTar(path, data)
                self.assertFalse(os.path.exists(os.path.join(report, SPOOL_NAME)))


if __name__ == '__main__':
    unittest.main()
