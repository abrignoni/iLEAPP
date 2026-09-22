"""check_in_media reads only the bytes the type sniffer looks at.

It used to read every media file whole before checking it in, but for a file on
disk the data only feeds guess_mime and guess_extension, and the sniffer in
scripts/filetype.py looks at no more than the first 8,192 bytes. A multi-GB video
was held in memory in full to identify its type. These tests pin that a large file
is read no further than that, that the type and extension recorded are the ones the
sniffer gives for the whole file, and that a file smaller than the signature is
still read in full.
"""
import builtins
import hashlib
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs, lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.filetype import guess_extension, guess_mime  # pylint: disable=wrong-import-position

SIGNATURE_BYTES = 8192
JPEG_HEAD = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00'
PNG_HEAD = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'


class _ReadCounter:
    """Wraps an open file and records how many bytes each read() returns."""

    def __init__(self, handle, log):
        self._handle = handle
        self._log = log

    def read(self, *args):
        data = self._handle.read(*args)
        self._log.append(len(data))
        return data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._handle.__exit__(*exc)

    def __getattr__(self, name):
        return getattr(self._handle, name)


class CheckInMediaReadTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        root = pathlib.Path(self.tmpdir)
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        self.data_folder = root / 'data'
        media_folder = root / 'media'
        html_media_folder = root / '_HTML' / 'media'
        for folder in (self.data_folder, media_folder, html_media_folder):
            folder.mkdir(parents=True, exist_ok=True)
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(media_folder), html_media_folder=str(html_media_folder),
            data_folder=str(self.data_folder)))
        Context.set_module_name('test_module')
        Context.set_artifact_name('Test Artifact')

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            try:
                lavafuncs.lava_db.close()
            except sqlite3.ProgrammingError:
                pass
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _stage(self, rel_path, content):
        staged = self.data_folder / rel_path
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(content)
        staged = str(staged)
        Context.set_files_found([staged])
        Context.set_seeker(types.SimpleNamespace(file_infos={
            staged: types.SimpleNamespace(source_path=rel_path, creation_date=0, modification_date=0)}))
        return staged

    def _check_in_counting_reads(self, staged, rel_path):
        """Check the file in and return the byte counts of every read() of it."""
        reads = []
        real_open = builtins.open

        def counting_open(file, *args, **kwargs):
            handle = real_open(file, *args, **kwargs)
            mode = args[0] if args else kwargs.get('mode', 'r')
            if (isinstance(file, (str, bytes, os.PathLike)) and os.fspath(file) == staged
                    and 'b' in mode and 'r' in mode):
                return _ReadCounter(handle, reads)
            return handle

        with mock.patch('builtins.open', counting_open):
            ref_id = ilapfuncs.check_in_media(rel_path)
        self.assertIsNotNone(ref_id)
        self.assertTrue(reads, 'the staged file was never read, so the counter proves nothing')
        return reads

    def _recorded(self, rel_path):
        media_id = hashlib.sha1(rel_path.encode()).hexdigest()
        return lavafuncs.lava_db.execute(
            'SELECT type, extraction_path FROM _lava_media_items WHERE id = ?', (media_id,)).fetchone()

    def test_a_large_file_is_read_no_further_than_the_sniffer_looks(self):
        rel_path = 'private/var/mobile/Media/DCIM/100APPLE/IMG_0001.JPG'
        content = JPEG_HEAD + b'\x00' * (1024 * 1024)
        staged = self._stage(rel_path, content)

        reads = self._check_in_counting_reads(staged, rel_path)

        self.assertLessEqual(sum(reads), SIGNATURE_BYTES)
        mime, extraction_path = self._recorded(rel_path)
        self.assertEqual(mime, 'image/jpeg')
        self.assertEqual(mime, guess_mime(content))
        self.assertTrue(extraction_path.endswith('.JPG'))

    def test_an_extensionless_file_gets_the_sniffed_extension_from_the_head(self):
        rel_path = 'Library/Attachments/0a/00/attachment-without-extension'
        content = PNG_HEAD + b'\x00' * (256 * 1024)
        staged = self._stage(rel_path, content)

        reads = self._check_in_counting_reads(staged, rel_path)

        self.assertLessEqual(sum(reads), SIGNATURE_BYTES)
        mime, extraction_path = self._recorded(rel_path)
        self.assertEqual(mime, 'image/png')
        self.assertEqual(mime, guess_mime(content))
        self.assertTrue(extraction_path.endswith('.' + guess_extension(content)))

    def test_a_file_smaller_than_the_signature_is_read_whole(self):
        rel_path = 'private/var/mobile/Media/DCIM/100APPLE/IMG_0002.PNG'
        content = PNG_HEAD + b'\x00' * 100
        staged = self._stage(rel_path, content)

        reads = self._check_in_counting_reads(staged, rel_path)

        self.assertEqual(sum(reads), len(content))
        mime, _ = self._recorded(rel_path)
        self.assertEqual(mime, 'image/png')


if __name__ == '__main__':
    unittest.main()
