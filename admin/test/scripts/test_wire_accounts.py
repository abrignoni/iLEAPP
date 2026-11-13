"""Wire account files: one row per Accounts/<UUID> JSON, selected account from the group plist."""
import base64
import json
import pathlib
import plistlib
import tempfile
import unittest
from unittest import mock

from scripts.artifacts import wire

PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 16
ACCOUNT_A = '11111111-2222-3333-4444-555555555555'
ACCOUNT_B = 'AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE'


class _Context:
    def __init__(self, files):
        self.files = files

    def __call__(self):
        return self

    def get_files_found(self):
        return self.files


def _group(root, name='GROUP'):
    group = root / 'private/var/mobile/Containers/Shared/AppGroup' / name
    (group / 'Accounts').mkdir(parents=True)
    (group / 'Library/Preferences').mkdir(parents=True)
    return group


def _write_account(group, file_name, payload):
    path = group / 'Accounts' / file_name
    path.write_text(json.dumps(payload) if not isinstance(payload, str) else payload, encoding='utf-8')
    return str(path)


def _write_plist(group, selected):
    path = group / 'Library/Preferences/group.com.wearezeta.zclient.ios.plist'
    data = {'other': 1}
    if selected is not None:
        data['AccountManagerSelectedAccountKey'] = selected
    path.write_bytes(plistlib.dumps(data))
    return str(path)


def _run(files):
    with mock.patch.object(wire, 'check_in_embedded_media', side_effect=lambda src, data, name: f'media:{name}'):
        headers, rows, source = wire.wireAccountFiles.__wrapped__(_Context(files))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return names, [dict(zip(names, row)) for row in rows], source


class WireAccountsTests(unittest.TestCase):
    def test_fields_selected_and_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            group = _group(pathlib.Path(tmp))
            files = [
                _write_account(group, ACCOUNT_A, {
                    'identifier': ACCOUNT_A.lower(), 'name': 'Alice', 'handle': 'alice',
                    'team': 'Team', 'unreadConversationCount': 3,
                    'image': base64.b64encode(PNG).decode(),
                    'loginCredentials': {'emailAddress': 'a@example.invalid', 'hasPassword': True,
                                         'usesCompanyLogin': False}}),
                _write_account(group, ACCOUNT_B, {'identifier': ACCOUNT_B, 'name': 'Bob'}),
                _write_plist(group, ACCOUNT_A.lower()),
            ]
            names, rows, source = _run(files)
            self.assertEqual(len(names), 13)
            self.assertEqual(len(rows), 2)
            alice, bob = rows
            self.assertEqual(alice['Account ID'], ACCOUNT_A.lower())
            self.assertEqual(alice['Selected'], 'Yes')
            self.assertEqual(alice['Email Address'], 'a@example.invalid')
            self.assertIs(alice['Has Password'], True)
            self.assertIs(alice['Uses Company Login'], False)
            self.assertEqual(alice['Unread Count (as stored)'], 3)
            self.assertEqual(alice['Profile Picture'], 'media:profile picture')
            self.assertEqual(alice['Team Picture'], '')
            self.assertEqual(bob['Selected'], 'No')
            self.assertIsNone(bob['Email Address'])
            self.assertIsNone(bob['Has Password'])
            self.assertEqual(bob['Profile Picture'], '')
            self.assertIn('group.com.wearezeta.zclient.ios.plist', source)

    def test_selected_blank_without_plist_and_no_without_key(self):
        for selected, expected in ((None, 'No'), ('missing-plist', '')):
            with self.subTest(selected=selected), tempfile.TemporaryDirectory() as tmp:
                group = _group(pathlib.Path(tmp))
                files = [_write_account(group, ACCOUNT_A, {'identifier': ACCOUNT_A, 'name': 'Alice'})]
                if selected != 'missing-plist':
                    files.append(_write_plist(group, selected))
                _, rows, _ = _run(files)
                self.assertEqual(rows[0]['Selected'], expected)

    def test_plist_of_another_group_is_not_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            group, other = _group(root, 'G1'), _group(root, 'G2')
            files = [_write_account(group, ACCOUNT_A, {'identifier': ACCOUNT_A, 'name': 'Alice'}),
                     _write_plist(other, ACCOUNT_A)]
            _, rows, _ = _run(files)
            self.assertEqual(rows[0]['Selected'], '')

    def test_identifier_differing_from_file_name_shows_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            group = _group(pathlib.Path(tmp))
            files = [_write_account(group, ACCOUNT_A, {'identifier': ACCOUNT_B, 'name': 'Alice'})]
            _, rows, _ = _run(files)
            self.assertEqual(rows[0]['Account ID'], f'{ACCOUNT_B} (file name {ACCOUNT_A})')

    def test_files_that_are_not_wire_accounts_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            group = _group(pathlib.Path(tmp))
            files = [
                _write_account(group, ACCOUNT_A, 'not json'),
                _write_account(group, ACCOUNT_B, ['list']),
                _write_account(group, 'not-a-uuid', {'identifier': ACCOUNT_A, 'name': 'x'}),
                _write_account(group, '99999999-2222-3333-4444-555555555555', {'something': 'else'}),
            ]
            _, rows, _ = _run(files)
            self.assertEqual(rows, [])

    def test_invalid_base64_image_is_left_blank(self):
        with tempfile.TemporaryDirectory() as tmp:
            group = _group(pathlib.Path(tmp))
            files = [_write_account(group, ACCOUNT_A, {'identifier': ACCOUNT_A, 'name': 'A',
                                                       'image': '***not base64***'})]
            _, rows, _ = _run(files)
            self.assertEqual(rows[0]['Profile Picture'], '')


if __name__ == '__main__':
    unittest.main()
