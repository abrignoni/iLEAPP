"""Exercise real EXIF image files through filesystem and ZIP discovery."""
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from PIL import Image
from pillow_heif import register_heif_opener
from scripts.artifacts.photosDbexif import __artifacts_v2__
from scripts.search_files import FileSeekerDir, FileSeekerZip


class TestPhotosExifDiscoveryCases(unittest.TestCase):
    def test_actual_formats_cases_and_layouts_filesystem_and_zip(self):
        register_heif_opener()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source'
            expected = set()
            counter = 0
            for directory in ('DCIM/100APPLE', 'PhotoData/PhotoCloudSharingData/a/b/c'):
                for extension, fmt in (('HEIC', 'HEIF'), ('HEIF', 'HEIF'),
                                       ('JPG', 'JPEG'), ('JPEG', 'JPEG'), ('PNG', 'PNG')):
                    for suffix in (extension, extension.lower(), extension.title()):
                        counter += 1
                        relative = f'private/var/mobile/Media/{directory}/{counter}.{suffix}'
                        path = source / relative
                        path.parent.mkdir(parents=True, exist_ok=True)
                        exif = Image.Exif()
                        exif[306] = '2024:01:02 03:04:05'
                        Image.new('RGB', (8, 8), (counter, 70, 100)).save(
                            path, format=fmt, exif=exif)
                        expected.add(relative)
            for name in ('negative.GIF', 'negative.JPG.bak'):
                path = source / 'private/var/mobile/Media/DCIM/100APPLE' / name
                Image.new('RGB', (8, 8)).save(path, format='PNG')
            archive = root / 'source.zip'
            with zipfile.ZipFile(archive, 'w') as zipped:
                for path in sorted(source.rglob('*')):
                    if path.is_file():
                        zipped.write(path, str(path.relative_to(source)))
            patterns = __artifacts_v2__['photosDbexif']['paths']
            with patch('scripts.search_files.logfunc'):
                for kind, seeker_type, input_path in (
                        ('fs', FileSeekerDir, source), ('zip', FileSeekerZip, archive)):
                    with self.subTest(kind=kind):
                        destination = root / kind
                        destination.mkdir()
                        seeker = seeker_type(str(input_path), str(destination))
                        found = set()
                        for pattern in patterns:
                            found.update(seeker.search(pattern))
                        self.assertEqual({seeker.file_infos[p].source_path for p in found}, expected)
                        self.assertEqual(len(found), 30)
                        for path in found:
                            with Image.open(path) as image:
                                self.assertEqual(image.getexif()[306], '2024:01:02 03:04:05')
                        close = getattr(seeker, 'close', None)
                        if close:
                            close()


if __name__ == '__main__':
    unittest.main()
