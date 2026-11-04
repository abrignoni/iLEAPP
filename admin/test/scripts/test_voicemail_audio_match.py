"""A voicemail row's audio and transcript come from its own database folder, by exact name."""
# pylint: disable=protected-access
import unittest

from scripts.artifacts import voicemail

DB = '/x/Library/Voicemail/voicemail.db'
AUDIO = ['/x/Library/Voicemail/12.amr',
         '/x/Library/Voicemail/A-357AF4B1/2.amr',
         '/x/Library/Voicemail/2.amr']


class FileBesideTest(unittest.TestCase):
    def test_exact_name_not_suffix(self):
        self.assertEqual(voicemail._file_beside(AUDIO, DB, '2.amr'), '/x/Library/Voicemail/2.amr')

    def test_per_account_folder_is_not_taken_for_the_top_level_store(self):
        self.assertIsNone(voicemail._file_beside(AUDIO[:2], DB, '2.amr'))

    def test_per_account_store_reads_its_own_folder(self):
        self.assertEqual(voicemail._file_beside(AUDIO, '/x/Library/Voicemail/A-357AF4B1/voicemail.db', '2.amr'),
                         '/x/Library/Voicemail/A-357AF4B1/2.amr')

    def test_missing_file_gives_none(self):
        self.assertIsNone(voicemail._file_beside(AUDIO, DB, '1.amr'))


if __name__ == '__main__':
    unittest.main()
