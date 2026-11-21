"""Reading Find My cache files in their JSON and encrypted forms, on synthetic files."""
# pylint: disable=no-member
import json
import os
import plistlib
import tempfile
import unittest
from unittest import mock

from Crypto.Cipher import ChaCha20_Poly1305

from scripts import findmy_cache

KEY = bytes(range(32))
OTHER_KEY = bytes(reversed(range(32)))
NONCE = bytes(range(12))


def keychain_value(key):
    return plistlib.dumps({'privateKey': {'key': {'data': b'x'}}, 'symmetricKey': {'key': {'data': key}}},
                          fmt=plistlib.FMT_BINARY)


def encrypted_file(document, key=KEY):
    plain = plistlib.dumps(document, fmt=plistlib.FMT_BINARY)
    cipher = ChaCha20_Poly1305.new(key=key, nonce=NONCE)
    ciphertext, tag = cipher.encrypt_and_digest(plain)
    return plistlib.dumps({'encryptedData': NONCE + ciphertext + tag, 'signature': b's' * 64},
                          fmt=plistlib.FMT_BINARY)


class ReadFindMyCache(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = os.path.join(tmp.name, 'com.apple.findmy.fmipcore')
        os.makedirs(self.folder)
        self.path = os.path.join(self.folder, 'Devices.data')
        patcher = mock.patch.object(findmy_cache, 'logfunc')
        self.log = patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, raw):
        with open(self.path, 'wb') as cache_file:
            cache_file.write(raw)

    def read_with(self, secrets, keychain='keychain.plist'):
        with mock.patch.object(findmy_cache, 'active_keychain_path', return_value=keychain), \
                mock.patch.object(findmy_cache, 'find_keychain_secrets', return_value=secrets) as find:
            result = findmy_cache.read_find_my_cache(self.path)
        return result, find

    def test_json_needs_no_keychain(self):
        self.write(json.dumps([{'name': 'a'}]).encode())
        result, find = self.read_with([])
        self.assertEqual(result, [{'name': 'a'}])
        find.assert_not_called()

    def test_decrypts_and_restores_nulls(self):
        self.write(encrypted_file([{'name': 'a', 'location': '$null', 'nested': ['$null', {'b': 1}]}]))
        result, find = self.read_with([keychain_value(KEY)])
        self.assertEqual(result, [{'name': 'a', 'location': None, 'nested': [None, {'b': 1}]}])
        find.assert_called_once_with('keychain.plist', 'com.apple.findmy', 'FMIPDataManagerKey', 'FMIPDataManager')

    def test_fmf_folder_uses_fmf_key(self):
        folder = os.path.join(os.path.dirname(self.folder), 'com.apple.findmy.fmfcore')
        os.makedirs(folder)
        self.path = os.path.join(folder, 'FriendCacheData.data')
        self.write(encrypted_file({'following': []}))
        result, find = self.read_with([keychain_value(KEY)])
        self.assertEqual(result, {'following': []})
        find.assert_called_once_with('keychain.plist', 'com.apple.findmy', 'FMFDataManagerKey', 'FMFDataManager')

    def test_second_candidate_key_is_tried(self):
        self.write(encrypted_file(['ok']))
        result, _find = self.read_with([keychain_value(OTHER_KEY), keychain_value(KEY)])
        self.assertEqual(result, ['ok'])

    def test_wrong_key_gives_nothing_and_logs(self):
        self.write(encrypted_file(['secret']))
        result, _find = self.read_with([keychain_value(OTHER_KEY)])
        self.assertIsNone(result)
        self.assertIn('did not verify', self.log.call_args[0][0])

    def test_tampered_ciphertext_is_refused(self):
        raw = plistlib.loads(encrypted_file(['secret']))
        blob = bytearray(raw['encryptedData'])
        blob[14] ^= 1
        raw['encryptedData'] = bytes(blob)
        self.write(plistlib.dumps(raw, fmt=plistlib.FMT_BINARY))
        result, _find = self.read_with([keychain_value(KEY)])
        self.assertIsNone(result)

    def test_no_keychain_is_logged(self):
        self.write(encrypted_file(['secret']))
        result, _find = self.read_with([], keychain=None)
        self.assertIsNone(result)
        self.assertIn('--keychain', self.log.call_args[0][0])

    def test_keychain_without_the_item_is_logged(self):
        self.write(encrypted_file(['secret']))
        result, _find = self.read_with([])
        self.assertIsNone(result)
        self.assertIn('holds no key', self.log.call_args[0][0])

    def test_short_blob_is_refused(self):
        self.write(plistlib.dumps({'encryptedData': b'short', 'signature': b's'}, fmt=plistlib.FMT_BINARY))
        result, _find = self.read_with([keychain_value(KEY)])
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
