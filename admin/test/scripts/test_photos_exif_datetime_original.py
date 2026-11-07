"""photosDbexif reads DateTimeOriginal from the Exif sub-IFD, where cameras store it.

_read_file_exif walked only the main image IFD, so tag 36867, which lives in the Exif
sub-IFD (0x8769), was never read: on hc_ios18_7 the column was blank on all 25 rows while
16 of the files carry the tag. These tests write it where a camera does and read it back,
for a JPEG through Pillow and for a HEIC through heicreader.
"""
import pathlib
import sys
import tempfile
import unittest

from PIL import Image

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import heicreader  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts import photosDbexif  # pylint: disable=wrong-import-position

HEIC_FIXTURES = REPO_ROOT / 'admin' / 'test' / 'fixtures' / 'heic'


class DateTimeOriginalTests(unittest.TestCase):

    def test_datetime_original_is_read_from_the_exif_sub_ifd(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'photo.jpg'
            exif = Image.Exif()
            exif[306] = '2024:01:02 03:04:05'
            exif.get_ifd(0x8769)[36867] = '2024:01:02 03:00:00'
            Image.new('RGB', (8, 8), 'gray').save(path, format='JPEG', exif=exif)

            dt, dt_original, _lat, _lon, tags = photosDbexif._read_file_exif(path)  # pylint: disable=protected-access

        self.assertEqual(dt, '2024:01:02 03:04:05')
        self.assertEqual(dt_original, '2024:01:02 03:00:00')
        self.assertIn('DateTime: 2024:01:02 03:04:05', tags)

    def test_a_file_without_datetime_original_leaves_it_blank(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'photo.jpg'
            exif = Image.Exif()
            exif[306] = '2024:01:02 03:04:05'
            Image.new('RGB', (8, 8), 'gray').save(path, format='JPEG', exif=exif)

            _dt, dt_original, _lat, _lon, _tags = photosDbexif._read_file_exif(path)  # pylint: disable=protected-access

        self.assertEqual(dt_original, '')

    @unittest.skipUnless(heicreader.available(), 'heicreader has no helper for this platform')
    def test_a_heic_is_read_through_heicreader_with_its_stored_orientation(self):
        dt, _dto, _lat, _lon, tags = photosDbexif._read_file_exif(  # pylint: disable=protected-access
            HEIC_FIXTURES / 'orientation.heic')
        self.assertEqual(dt, '2026:11:07 10:00:00')
        self.assertIn('Orientation: 6', tags)


if __name__ == '__main__':
    unittest.main()
