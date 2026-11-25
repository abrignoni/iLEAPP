"""
input_type.decrypt_itunes_backup on a small encrypted backup made here: a real keybag with the
keys wrapped as iOS wraps them (RFC 3394), but a few PBKDF2 iterations so the test is fast.
"""

import hashlib
import os
import plistlib
import tempfile
import unittest
from unittest import mock

from Crypto.Cipher import AES

from leapp_functions.app import input_type

PASSWORD = 'secret'
MANIFEST_CLASS = 3


def entry(tag, value):
    """ One keybag entry: tag, big-endian length, value. """
    if isinstance(value, int):
        value = value.to_bytes(4, byteorder='big')
    return tag + len(value).to_bytes(4, byteorder='big') + value


def wrap(key, data):
    """ AES key wrap (RFC 3394). """
    return AES.new(key, AES.MODE_KW).seal(data)


def make_backup(folder, class_keys, manifest_db_key, manifest_class=MANIFEST_CLASS):
    """ Write the Manifest.plist of an encrypted backup into folder. """
    salt, double_salt = b'S' * 20, b'D' * 20
    initial = hashlib.pbkdf2_hmac('sha256', PASSWORD.encode(), double_salt, 2)
    password_key = hashlib.pbkdf2_hmac('sha1', initial, salt, 3, dklen=32)
    keybag = (entry(b'VERS', 3) + entry(b'TYPE', 1) + entry(b'UUID', b'K' * 16)
              + entry(b'HMCK', b'H' * 40) + entry(b'WRAP', 0) + entry(b'SALT', salt)
              + entry(b'ITER', 3) + entry(b'DPWT', 1) + entry(b'DPIC', 2)
              + entry(b'DPSL', double_salt))
    for number, key in class_keys.items():
        keybag += (entry(b'UUID', bytes([number]) * 16) + entry(b'CLAS', number)
                   + entry(b'WRAP', 3) + entry(b'KTYP', 0)
                   + entry(b'WPKY', wrap(password_key, key)))
    manifest_key = (manifest_class.to_bytes(4, byteorder='little')
                    + wrap(class_keys.get(manifest_class, b'\0' * 32), manifest_db_key))
    with open(os.path.join(folder, 'Manifest.plist'), 'wb') as manifest:
        plistlib.dump({'IsEncrypted': True, 'BackupKeyBag': keybag, 'ManifestKey': manifest_key},
                      manifest)


class TestDecryptItunesBackup(unittest.TestCase):
    """ The keys come back with the right password, and each failure says why. """

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.folder = self.temp.name
        self.class_keys = {1: bytes(range(32)), MANIFEST_CLASS: bytes(range(32, 64))}
        self.manifest_db_key = bytes(range(64, 96))

    def tearDown(self):
        self.temp.cleanup()

    def decrypt(self, password=PASSWORD):
        """ decrypt_itunes_backup with logfunc kept quiet. """
        with mock.patch.object(input_type, 'logfunc'):
            return input_type.decrypt_itunes_backup(self.folder, password)

    def test_the_right_password_gives_the_manifest_db_key(self):
        """ The key of Manifest.db and every class key come back unwrapped. """
        make_backup(self.folder, self.class_keys, self.manifest_db_key)
        (classes, manifest_db_key), message = self.decrypt()
        self.assertEqual(message, 'Decryption successful')
        self.assertEqual(manifest_db_key, self.manifest_db_key)
        self.assertEqual({number: value['Unwrapped'] for number, value in classes.items()},
                         self.class_keys)
        self.assertEqual(classes[MANIFEST_CLASS]['CLAS'], MANIFEST_CLASS)

    def test_a_wrong_password_is_refused(self):
        """ A wrong password cannot unwrap the class keys. """
        make_backup(self.folder, self.class_keys, self.manifest_db_key)
        self.assertEqual(self.decrypt('not it'), (None, 'Incorrect password'))

    def test_no_password(self):
        """ Cancelling gives None, which is not a password. """
        make_backup(self.folder, self.class_keys, self.manifest_db_key)
        self.assertEqual(self.decrypt(None), (None, 'No password provided'))

    def test_a_manifest_class_missing_from_the_keybag(self):
        """ Manifest.db names a protection class the keybag does not hold. """
        make_backup(self.folder, self.class_keys, self.manifest_db_key, manifest_class=4)
        self.assertEqual(self.decrypt(),
                         (None, 'Could not find protection class for Manifest.db'))

    def test_unwrap_matches_rfc_3394(self):
        """ The unwrap is the standard one. """
        # RFC 3394, 4.1: 128 bits of key data wrapped with a 128-bit key
        kek = bytes.fromhex('000102030405060708090A0B0C0D0E0F')
        wrapped = bytes.fromhex('1FA68B0A8112B447AEF34BD8FB5A7B829D3E862371D2CFE5')
        self.assertEqual(input_type.unwrap(kek, wrapped).hex().upper(),
                         '00112233445566778899AABBCCDDEEFF')


if __name__ == '__main__':
    unittest.main()
