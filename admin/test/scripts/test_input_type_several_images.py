"""Several files given as the source of the window: the member images of a RAID set.

The window's Source step hands its paths to leapp_functions.app.input_type.detect, which
decides, without opening anything beyond the first bytes, whether they are read together
as one raw input. This replaces the tests of the old window's input field, whose
functions were read from ileappGUI.py's source. Showing the first image and how many
more, and reading a path typed over the field, are raw_image.selection_text and
selected_paths, tested in test_raw_image_seeker.py.
"""
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from leapp_functions.app import input_type  # pylint: disable=wrong-import-position

AD1 = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images' / 'lean-multi-ntfs-c9.ad1'


class SeveralImagesTest(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='input_type_images_')
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.images = [self.blank(name) for name in ('disk0.img', 'disk1.img', 'disk2.img')]

    def blank(self, name):
        path = os.path.join(self.folder, name)
        with open(path, 'wb') as handle:
            handle.write(b'\0' * 4096)
        return path

    def test_several_images_are_read_together_as_raw(self):
        detected = input_type.detect(self.images)
        self.assertEqual(detected.kind, 'raw')
        self.assertEqual(detected.label, '3 disk images')
        self.assertEqual(detected.problem, '')

    def test_one_image_is_read_as_raw(self):
        detected = input_type.detect(self.images[:1])
        self.assertEqual(detected.kind, 'raw')
        self.assertEqual(detected.problem, '')

    def test_several_files_that_are_not_images_are_refused(self):
        archive = os.path.join(self.folder, 'extraction.zip')
        with open(archive, 'wb') as handle:
            handle.write(b'PK')
        detected = input_type.detect([self.images[0], archive])
        self.assertEqual(detected.kind, '')
        self.assertIn('only as disk images', detected.problem)

    def test_several_images_are_raw_whatever_the_first_is_named(self):
        # numbered pieces of two different images: the first one's suffix alone does
        # not name a raw image type
        detected = input_type.detect([self.blank('first.002'), self.blank('second.003')])
        self.assertEqual(detected.kind, 'raw')
        self.assertEqual(detected.problem, '')

    def test_logical_evidence_with_other_images_is_refused(self):
        detected = input_type.detect([self.images[0], str(AD1)])
        self.assertEqual(detected.kind, '')
        self.assertIn('is logical evidence', detected.problem)

    def test_a_missing_image_is_refused(self):
        missing = os.path.join(self.folder, 'disk9.img')
        detected = input_type.detect([self.images[0], missing])
        self.assertEqual(detected.kind, '')
        self.assertIn('does not exist', detected.problem)

    def test_empty_paths_are_left_out(self):
        self.assertIsNone(input_type.detect(['', '']))
        self.assertEqual(input_type.detect(['', self.images[0]]).kind, 'raw')


if __name__ == '__main__':
    unittest.main()
