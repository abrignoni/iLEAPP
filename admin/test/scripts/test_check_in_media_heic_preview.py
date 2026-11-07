"""check_in_media attaches a HEIC or HEIF image as a JPEG copy, so LAVA can show it.

An image with transparency is attached as a PNG instead, since JPEG cannot hold it.

LAVA shows a media item of type image/heic as "This file could not be shown". fsCachedData
checked its HEIC files in as they were, so on hc_ios18_7 all 917 of its HEIC media read that
way. Five modules converted HEIC on their own; every other caller did not.

These tests check a file and an embedded image in through the shared code and read back the
media item, the media file and the evidence copy. A HEIC that cannot be decoded, and a
caller that forces a type other than HEIC, keep the original bytes.
"""
import hashlib
import io
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest import mock

from PIL import Image
from pillow_heif import register_heif_opener

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs, lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.filetype import guess_mime  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerDir  # pylint: disable=wrong-import-position

register_heif_opener()
CACHE = 'private/var/mobile/Containers/Data/Application/A/Library/Caches/com.example/fsCachedData'


def heic_bytes(colour='red', size=(8, 6), mode='RGB'):
    buffer = io.BytesIO()
    Image.new(mode, size, colour).save(buffer, 'HEIF')
    return buffer.getvalue()


class CheckInMediaHeicPreviewTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        root = pathlib.Path(self.tmpdir)
        self.input = root / 'input'
        self.report = root / 'report'
        self.data_folder = self.report / 'data'
        media_folder = self.report / 'media'
        html_media_folder = self.report / '_HTML' / 'media'
        for folder in (self.input, self.data_folder, media_folder, html_media_folder):
            folder.mkdir(parents=True, exist_ok=True)
        lavafuncs.initialize_lava(str(self.report), str(self.report), 'fs')
        Context.clear()
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(media_folder), html_media_folder=str(html_media_folder),
            data_folder=str(self.data_folder), output_folder_base=str(self.report)))
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

    def _stage(self, name, content):
        rel_path = f'{CACHE}/{name}'
        path = self.input / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        seeker = FileSeekerDir(str(self.input), str(self.data_folder))  # lists the input when made
        Context.set_seeker(seeker)
        found = seeker.search(f'*/fsCachedData/{name}')
        Context.set_files_found(found)
        self.assertEqual(len(found), 1)
        return rel_path, found[0]

    def _media_item(self, media_id):
        return lavafuncs.lava_db.execute(
            'SELECT source_path, extraction_path, type FROM _lava_media_items WHERE id = ?',
            (media_id,)).fetchone()

    def _media_bytes(self, extraction_path):
        return (self.report / extraction_path).read_bytes()

    def test_the_fixture_sniffs_as_heic(self):
        self.assertEqual(guess_mime(heic_bytes()), 'image/heic')

    def test_a_heic_file_is_attached_as_a_jpeg_and_the_evidence_copy_is_untouched(self):
        original = heic_bytes('red', (8, 6))
        rel_path, staged = self._stage('B2AB81F5', original)

        self.assertIsNotNone(ilapfuncs.check_in_media(staged))

        source_path, extraction_path, mime = self._media_item(hashlib.sha1(rel_path.encode()).hexdigest())
        self.assertEqual(source_path, rel_path)
        self.assertEqual(mime, 'image/jpeg')
        self.assertTrue(extraction_path.endswith('.jpg'))
        with Image.open(io.BytesIO(self._media_bytes(extraction_path))) as image:
            self.assertEqual(image.format, 'JPEG')
            self.assertEqual(image.size, (8, 6))
            red, green, blue = image.convert('RGB').getpixel((4, 3))
            self.assertGreater(red, 200)
            self.assertLess(max(green, blue), 60)
        self.assertEqual(pathlib.Path(staged).read_bytes(), original)
        html_copy = self.report / '_HTML' / extraction_path
        self.assertEqual(html_copy.read_bytes(), self._media_bytes(extraction_path))

    def test_an_embedded_heic_is_attached_as_a_jpeg(self):
        _, staged = self._stage('container.db', b'SQLite format 3\x00')

        ref = ilapfuncs.check_in_embedded_media(staged, heic_bytes('blue'), name='thumb')

        self.assertIsNotNone(ref)
        _, extraction_path, mime = lavafuncs.lava_db.execute(
            'SELECT source_path, extraction_path, type FROM _lava_media_items').fetchone()
        self.assertEqual(mime, 'image/jpeg')
        with Image.open(io.BytesIO(self._media_bytes(extraction_path))) as image:
            self.assertEqual(image.format, 'JPEG')

    def test_a_heic_with_transparency_is_attached_as_a_png(self):
        rel_path, staged = self._stage('layer', heic_bytes((255, 0, 0, 0), mode='RGBA'))

        ilapfuncs.check_in_media(staged)

        _, extraction_path, mime = self._media_item(hashlib.sha1(rel_path.encode()).hexdigest())
        self.assertEqual(mime, 'image/png')
        with Image.open(io.BytesIO(self._media_bytes(extraction_path))) as image:
            self.assertEqual(image.format, 'PNG')
            self.assertEqual(image.getchannel('A').getextrema(), (0, 0))

    def test_a_heic_that_cannot_be_decoded_keeps_the_original(self):
        damaged = heic_bytes()[:64]
        self.assertEqual(guess_mime(damaged), 'image/heic')
        rel_path, staged = self._stage('damaged', damaged)

        with mock.patch.object(ilapfuncs, 'logfunc') as log:
            self.assertIsNotNone(ilapfuncs.check_in_media(staged))

        _, extraction_path, mime = self._media_item(hashlib.sha1(rel_path.encode()).hexdigest())
        self.assertEqual(mime, 'image/heic')
        self.assertEqual(self._media_bytes(extraction_path), damaged)
        self.assertTrue(any('could not be converted' in str(call) for call in log.call_args_list))

    def test_a_caller_that_forces_another_type_is_left_as_it_asked(self):
        original = heic_bytes()
        rel_path, staged = self._stage('forced.bin', original)

        ilapfuncs.check_in_media(staged, force_type='application/octet-stream', force_extension='bin')

        _, extraction_path, mime = self._media_item(hashlib.sha1(rel_path.encode()).hexdigest())
        self.assertEqual(mime, 'application/octet-stream')
        self.assertEqual(self._media_bytes(extraction_path), original)

    def test_a_caller_that_forces_the_heic_type_still_gets_a_jpeg(self):
        rel_path, staged = self._stage('forced.heic', heic_bytes())

        ilapfuncs.check_in_media(staged, force_type='image/heic', force_extension='heic')

        _, extraction_path, mime = self._media_item(hashlib.sha1(rel_path.encode()).hexdigest())
        self.assertEqual(mime, 'image/jpeg')
        self.assertTrue(extraction_path.endswith('.jpg'))

    def test_a_jpeg_is_copied_as_it_is(self):
        buffer = io.BytesIO()
        Image.new('RGB', (4, 4), 'green').save(buffer, 'JPEG')
        rel_path, staged = self._stage('photo.jpg', buffer.getvalue())

        ilapfuncs.check_in_media(staged)

        _, extraction_path, mime = self._media_item(hashlib.sha1(rel_path.encode()).hexdigest())
        self.assertEqual(mime, 'image/jpeg')
        self.assertEqual(self._media_bytes(extraction_path), buffer.getvalue())


if __name__ == '__main__':
    unittest.main()
