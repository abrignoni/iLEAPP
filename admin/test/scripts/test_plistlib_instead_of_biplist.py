"""chatgpt, discordChats and kikBplistmeta read their plists with plistlib, not biplist.

biplist is unmaintained and calls datetime.utcfromtimestamp(), deprecated and scheduled for
removal. Decoding every plist in the josh_ios17_ffs, josh_ios15_ffs, mvs_ios_2023 and
belkasoft_ctf6 test cases with both libraries gave the same value for all 136 that biplist
read, and plistlib also read the 44 that biplist rejected. These tests run the migrated code
on constructed files.
"""
import os
import plistlib
import shutil
import tempfile
import unittest

from scripts.artifacts import chatgpt, discordChats
from scripts.context import Context


class PlistlibInsteadOfBiplistTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        Context.set_data_folder(self.tmpdir)

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def write(self, name, value, fmt=plistlib.PlistFormat.FMT_BINARY):
        path = os.path.join(self.tmpdir, name)
        with open(path, 'wb') as f:
            plistlib.dump(value, f, fmt=fmt)
        return path

    def test_chatgpt_preferences_read_both_files_and_the_nested_traits(self):
        statsig = self.write('com.openai.chat.StatsigService.plist', {
            'accountID': 'acct', 'userID': 'user', 'userEmail': 'a@example.com', 'planType': 'free'})
        traits = plistlib.dumps({'plan_type': 'plus', 'has_paid_plan': True, 'workspace_id': 'w',
                                 'device_id': 'd'}, fmt=plistlib.PlistFormat.FMT_BINARY)
        segment = self.write('com.segment.storage.oai.plist', {
            'segment.userId': 'user', 'segment.traits': traits, 'segment.events': 'e'},
            fmt=plistlib.PlistFormat.FMT_XML)
        Context.set_files_found([statsig, segment])

        _, rows, _ = chatgpt.chatgptPreferences.__wrapped__(Context)

        self.assertEqual(sorted(rows), sorted([
            ('acct', 'user', 'a@example.com', 'free', '', '', '', ''),
            ('', 'user', '', 'plus', True, 'w', 'd', 'e')]))

    def test_chatgpt_skips_a_file_that_is_not_a_plist(self):
        path = os.path.join(self.tmpdir, 'com.openai.chat.StatsigService.plist')
        with open(path, 'wb') as f:
            f.write(b'not a plist')
        Context.set_files_found([path])

        _, rows, _ = chatgpt.chatgptPreferences.__wrapped__(Context)

        self.assertEqual(rows, [])

    def test_discord_reads_the_model_from_the_activation_record(self):
        token = b'{\n\t"ProductType" = "iPhone16,2";\n}'
        path = self.write('activation_record.plist', {'AccountToken': token})

        resolution = discordChats._activation_resolution([path])  # pylint: disable=protected-access

        self.assertEqual(resolution['Model ID'], 'iPhone16,2')


if __name__ == '__main__':
    unittest.main()
