"""The two emoji preference artifacts read com.apple.EmojiPreferences.plist as the
EmojiFoundation framework writes it.

The structure here follows the key vocabulary the framework carries and the shape of a
macOS instance of the file: EMFDefaultsKey holds EMFRecentsKey (a list of emoji),
EMFUsageHistoryKey (emoji to a list of sequence numbers) and EMFRecentSequenceNumberKey,
beside other keys. An iOS instance was not available, so this is constructed data.
"""
import os
import pathlib
import plistlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.artifacts import emojiPreferences as module  # pylint: disable=wrong-import-position

RELATIVE = 'private/var/mobile/Library/Preferences/com.apple.EmojiPreferences.plist'
PLIST = {
    'EMFDefaultsKey': {
        'EMFRecentSequenceNumberKey': 6,
        'EMFRecentsKey': ['😀', '👍', '🎉'],
        'EMFUsageHistoryKey': {'😀': [0, 3, 5], '👍': [1], '🔥': [2, 4]},
        'EMFSkinToneBaseKey': {'👍': '👍🏽'},
        'EMFDidDisplaySkinToneHelpKey': True,
    },
    'com.apple.stickers.recency.generation': 2,
    'com.apple.stickers.recency.order': ['sticker-a', 'sticker-b'],
}


class EmojiPreferencesTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        data = os.path.join(self.tmpdir, 'data')
        self.staged = os.path.join(data, RELATIVE)
        os.makedirs(os.path.dirname(self.staged))
        with open(self.staged, 'wb') as f:
            plistlib.dump(PLIST, f)
        Context.clear()
        Context.set_data_folder(data)
        Context.set_files_found([self.staged])

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_recents_and_usage_are_joined_per_emoji(self):
        headers, rows, source = module.emojiRecents.__wrapped__(Context)

        self.assertEqual(headers, ('Recents Rank', 'Emoji', 'Uses Recorded',
                                   'First Use Sequence', 'Last Use Sequence'))
        self.assertEqual(source, self.staged)
        self.assertEqual(rows, [
            (1, '😀', 3, 0, 5),
            (2, '👍', 1, 1, 1),
            (3, '🎉', '', '', ''),      # recent with no usage history
            ('', '🔥', 2, 2, 4),        # usage history without a recents position
        ])

    def test_the_other_keys_are_flattened_and_the_joined_ones_left_out(self):
        headers, rows, source = module.emojiPreferenceKeys.__wrapped__(Context)

        self.assertEqual(headers, ('Key', 'Value'))
        self.assertEqual(source, self.staged)
        self.assertEqual(rows, [
            ('EMFDefaultsKey.EMFDidDisplaySkinToneHelpKey', 'True'),
            ('EMFDefaultsKey.EMFRecentSequenceNumberKey', '6'),
            ('EMFDefaultsKey.EMFSkinToneBaseKey.👍', '👍🏽'),
            ('com.apple.stickers.recency.generation', '2'),
            ('com.apple.stickers.recency.order[0]', 'sticker-a'),
            ('com.apple.stickers.recency.order[1]', 'sticker-b'),
        ])

    def test_a_file_without_the_defaults_dictionary_reports_nothing_but_its_keys(self):
        with open(self.staged, 'wb') as f:
            plistlib.dump({'Other': 'x'}, f)

        _, recents, _ = module.emojiRecents.__wrapped__(Context)
        _, keys, _ = module.emojiPreferenceKeys.__wrapped__(Context)

        self.assertEqual(recents, [])
        self.assertEqual(keys, [('Other', 'x')])

    def test_a_file_list_without_the_plist_reports_no_rows(self):
        other = os.path.join(self.tmpdir, 'data', 'private/var/mobile/Library/Preferences/other.plist')
        shutil.copy2(self.staged, other)
        Context.set_files_found([other])
        for artifact in (module.emojiRecents, module.emojiPreferenceKeys):
            _, rows, source = artifact.__wrapped__(Context)
            self.assertEqual((rows, source), ([], ''))


if __name__ == '__main__':
    unittest.main()
