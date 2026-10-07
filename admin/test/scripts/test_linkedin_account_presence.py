"""Actual binary-plist presence boundaries preserve native values."""
from pathlib import Path
import plistlib
import tempfile
from types import SimpleNamespace
import unittest
from scripts.artifacts import LinkedIn


class LinkedInPresenceTests(unittest.TestCase):
    def parse_values(self, values):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for index, value in enumerate(values):
                path = Path(directory) / str(index) / 'com.linkedin.LinkedIn.plist'
                path.parent.mkdir()
                path.write_bytes(plistlib.dumps(value, fmt=getattr(plistlib, "FMT_BINARY")))
                paths.append(str(path))
            context = SimpleNamespace(get_files_found=lambda: paths)
            headers, rows, source = LinkedIn.linkedin_account.__wrapped__(context)
            return headers, rows, source, paths

    def test_absent_keys_suppressed_but_parent_presence_retained(self):
        for value in [{}, {'unrelated': 'value'}]:
            with self.subTest(value=value):
                self.assertEqual(self.parse_values([value])[1], [])
        for value in [{}, None, '', 0, False, [], {'unprojected': 'value'}]:
            with self.subTest(profile=value):
                self.assertEqual(self.parse_values([{'voy.authenticatedDashProfileModel': value}])[1],
                                 [('', '', '', '', '', '')])

    def test_falsey_member_and_native_types_are_not_absence(self):
        for value in [None, '', 0, False, b'', [], {}, 'member', 1.5, b'bytes', ['nested']]:
            with self.subTest(value=value):
                rows = self.parse_values([{'voy.authenticatedMemberId': value}])[1]
                self.assertEqual(rows, [(value, '', '', '', '', '')])
                self.assertIs(type(rows[0][0]), type(value))

    def test_projection_keeps_values_and_ignores_extra_fields(self):
        profile = {'firstName': False, 'lastName': 0, 'headline': None,
                   'geoLocation': {'geo': {'defaultLocalizedName': ['a', 'b']}},
                   'publicIdentifier': {'nested': 'value'}, 'unprojected': 'ignored'}
        rows = self.parse_values([{'voy.authenticatedMemberId': 'member',
                                  'voy.authenticatedDashProfileModel': profile}])[1]
        self.assertEqual(rows, [('member', 0, False, None, ['a', 'b'], {'nested': 'value'})])

    def test_binary_uid_remains_native_and_is_not_presence_falsey(self):
        uid = getattr(plistlib, "UID")(7)
        rows = self.parse_values([{'voy.authenticatedMemberId': uid}])[1]
        self.assertIsInstance(rows[0][0], LinkedIn.ccl_bplist.BplistUID)
        self.assertEqual(rows[0][0].value, 7)
        self.assertEqual(rows[0][1:], ('', '', '', '', ''))

    def test_first_source_stays_selected_even_if_it_yields_zero(self):
        absent = {'unrelated': 'value'}
        present = {'voy.authenticatedMemberId': 'member'}
        for inputs, expected in [([absent, present], []),
                                 ([present, absent], [('member', '', '', '', '', '')])]:
            _, rows, source, paths = self.parse_values(inputs)
            self.assertEqual(rows, expected)
            self.assertEqual(source, paths[0])

    def test_non_dictionary_root_preserves_existing_blank_projection(self):
        for value in [None, [], '', 0, False, ['list']]:
            with self.subTest(value=value):
                self.assertEqual(self.parse_values([value])[1], [('', '', '', '', '', '')])


if __name__ == '__main__':
    unittest.main()
