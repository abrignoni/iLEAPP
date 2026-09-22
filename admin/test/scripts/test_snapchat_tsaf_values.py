"""A key with no value in Snapchat's user.plist must read as absent, not as the next key.

Documents/user.plist is a TSAF container: strings written as a 0x08 byte, the text and a
0x00 terminator, each key followed by its value. A signed-out account's file keeps its
username, user_id and laguna_id keys with a single 0x00 where the value would be. The reader
used to take the next string in the file as the value, so the Account artifact reported
username as "user_id". A value now has to begin exactly where its key ends.

Every value below is synthetic.
"""
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import snapchat  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

USER_ID = '11111111-2222-4333-8444-555555555555'
LAGUNA_ID = '66666666-7777-4888-9999-aaaaaaaaaaaa'
CLIENT_ID = 'BBBBBBBB-CCCC-4DDD-8EEE-FFFFFFFFFFFF'
HEADER = b'TSAF\x03\x00\x04\x00\x02\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00,'


def _string(text):
    return b'\x08' + text.encode('utf-8') + b'\x00'


def _field(key, value):
    '''A key and its value, or the key and a single 0x00 when value is None.'''
    return _string(key) + (b'\x00' if value is None else _string(value))


def _user_plist(username, user_id, laguna_id):
    return (HEADER + _string('User') + _string('SyntheticTypeName0000') + b'.'
            + _field('username', username) + _field('user_id', user_id)
            + _field('laguna_id', laguna_id) + _string('client_encryption') + b','
            + _string('SCClientEncryption') + _field('identifier', CLIENT_ID)
            + _field('encryption_key', 'c3ludGhldGljIGtleQ==')
            + _field('initialization_vector', 'c3ludGhldGljIGl2') + b'\x00\x00')


class TestSnapchatTsafValues(unittest.TestCase):

    def _account_rows(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'Documents' / 'user.plist'
            path.parent.mkdir()
            path.write_bytes(data)
            Context.clear()
            Context.set_files_found([str(path)])
            _, data_list, _ = snapchat.snapchatAccount.__wrapped__(Context)
            local_user_id = snapchat._local_user_id(str(path), '')  # pylint: disable=protected-access
        return {key: value for key, value, _source in data_list}, local_user_id

    def test_signed_in_file_reports_each_value(self):
        rows, local_user_id = self._account_rows(
            _user_plist('synthetic_user', USER_ID, LAGUNA_ID))
        self.assertEqual(rows, {
            'username': 'synthetic_user',
            'user_id': USER_ID,
            'laguna_id': LAGUNA_ID,
            'client_encryption identifier': CLIENT_ID,
            'client_encryption encryption_key': 'c3ludGhldGljIGtleQ==',
            'client_encryption initialization_vector': 'c3ludGhldGljIGl2',
        })
        self.assertEqual(local_user_id, USER_ID)

    def test_signed_out_file_reports_no_identity_value(self):
        """The old reader reported username = 'user_id' here."""
        rows, local_user_id = self._account_rows(_user_plist(None, None, None))
        self.assertNotIn('username', rows)
        self.assertNotIn('user_id', rows)
        self.assertNotIn('laguna_id', rows)
        self.assertNotIn('user_id', rows.values())
        self.assertEqual(rows['client_encryption identifier'], CLIENT_ID)
        self.assertEqual(local_user_id, '')

    def test_one_empty_value_does_not_shift_the_next(self):
        rows, _ = self._account_rows(_user_plist(None, USER_ID, LAGUNA_ID))
        self.assertNotIn('username', rows)
        self.assertEqual(rows['user_id'], USER_ID)
        self.assertEqual(rows['laguna_id'], LAGUNA_ID)


if __name__ == '__main__':
    unittest.main()
