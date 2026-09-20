"""Pin what burnerCache's device path helper returns for each spelling a path arrives in.

The helper feeds the Source file name column. A staged path is reduced through
Context.get_relative_path; a media item's recorded source path is already the
evidence path and only loses its leading slash. It no longer cuts a path down to its
first '/private/': on an archive whose members begin with a slash and carry a folder
above /private, that made this column drop the folder while the report's own
processed-files list and the LAVA source path kept it.
"""
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.artifacts.burnerCache import _device_relative  # pylint: disable=wrong-import-position

DATA = '/case/report/data'


class TestDeviceRelative(unittest.TestCase):

    def setUp(self):
        self._saved = Context.get_data_folder()
        Context.set_data_folder(DATA)

    def tearDown(self):
        Context.set_data_folder(self._saved)

    def test_staged_path_reduces_to_the_evidence_path(self):
        self.assertEqual(_device_relative(DATA + '/private/var/mobile/x.db'),
                         'private/var/mobile/x.db')
        self.assertEqual(_device_relative(DATA + '/filesystem2/mobile/x.db'),
                         'filesystem2/mobile/x.db')

    def test_recorded_source_path_only_loses_its_leading_slash(self):
        self.assertEqual(_device_relative('/private/var/mobile/x.db'), 'private/var/mobile/x.db')
        self.assertEqual(_device_relative('filesystem2/mobile/x.db'), 'filesystem2/mobile/x.db')

    def test_a_folder_above_private_is_kept(self):
        self.assertEqual(_device_relative('/wrapper/private/var/mobile/x.db'),
                         'wrapper/private/var/mobile/x.db')


if __name__ == '__main__':
    unittest.main()
