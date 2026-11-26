"""Daily Find My addresses derived from an OwnedBeacons record, on synthetic records and stores.

The oracle derives each key in the form Lost_Apples gives, u*P + v*G from the public key alone, with
plain P-224 arithmetic written here, while the module computes (d*u + v)*G from the private scalar.
The two agree only if both follow the same chain.
"""
# pylint: disable=no-member,protected-access
import hashlib
import os
import plistlib
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

from Crypto.Cipher import AES
from Crypto.PublicKey import ECC

from admin.test.scripts.test_findmy_searchpartyd_observations import KEY, encrypted_store
from scripts.artifacts import findMySearchpartyd as spd

P = 2 ** 224 - 2 ** 96 + 1
A = P - 3
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFF16A2E0B8F03E13DD29455C5C2A3D
G = (0xB70E0CBD6BB4BF7F321390B94A03C1D356C21122343280D6115C1D21,
     0xBD376388B5F723FB4C22DFE6CD4375A05A07476444D5819985007E34)
BEACON = 'ABCDEFAB-CDEF-ABCD-EFAB-CDEFABCDEFAB'
SCALAR = 0x1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF12345678
SECONDARY = hashlib.sha256(b'synthetic secondary').digest()
PAIRED = datetime(2026, 1, 1, 12, 0, 0)


def add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    if p1[0] == p2[0] and (p1[1] + p2[1]) % P == 0:
        return None
    if p1 == p2:
        slope = (3 * p1[0] * p1[0] + A) * pow(2 * p1[1], -1, P) % P
    else:
        slope = (p2[1] - p1[1]) * pow(p2[0] - p1[0], -1, P) % P
    x = (slope * slope - p1[0] - p2[0]) % P
    return x, (slope * (p1[0] - x) - p1[1]) % P


def multiply(k, point):
    result = None
    while k:
        if k & 1:
            result = add(result, point)
        point = add(point, point)
        k >>= 1
    return result


def kdf(secret, info, length):
    out, counter = b'', 1
    while len(out) < length:
        out += hashlib.sha256(secret + counter.to_bytes(4, 'big') + info).digest()
        counter += 1
    return out[:length]


def oracle_keys(public_point, secret, days):
    keys = []
    for _ in range(days):
        secret = kdf(secret, b'update', 32)
        derived = kdf(secret, b'diversify', 72)
        u = int.from_bytes(derived[:36], 'big') % (N - 1) + 1
        v = int.from_bytes(derived[36:], 'big') % (N - 1) + 1
        keys.append(add(multiply(u, public_point), multiply(v, G))[0].to_bytes(28, 'big'))
    return keys


def mac_of(key):
    return bytes([key[0] | 0xC0]) + key[1:6]


class DailyAddresses(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        spd._key_cache.clear()
        patcher = mock.patch.object(spd, 'logfunc')
        self.log = patcher.start()
        self.addCleanup(patcher.stop)
        self.store = os.path.join(self.tmp, 'a', 'mobile', 'Library', spd.STORE_DIR)
        os.makedirs(self.store)
        point = ECC.construct(curve='P-224', d=SCALAR).pointQ
        self.public = (int(point.x), int(point.y))
        x, y = (value.to_bytes(28, 'big') for value in self.public)
        self.record = {'identifier': BEACON, 'pairingDate': PAIRED,
                       'privateKey': {'key': {'data': b'\x04' + x + y + SCALAR.to_bytes(28, 'big')}},
                       'publicKey': {'key': {'data': b'\x04' + x + y}},
                       'secondarySharedSecret': {'key': {'data': SECONDARY}}}

    def write_record(self, relative, document):
        path = os.path.join(self.store, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nonce = bytes(range(16))
        cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plistlib.dumps(document, fmt=plistlib.FMT_BINARY))
        with open(path, 'wb') as handle:
            handle.write(plistlib.dumps([nonce, tag, ciphertext], fmt=plistlib.FMT_BINARY))

    def observations(self, mac, when):
        encrypted_store(self.store, 'Observations.db', [
            ('CREATE TABLE ObservedAdvertisement (advId INTEGER PRIMARY KEY, macAddress BLOB, '
             'advertisementData BLOB, rssi INTEGER, scanDate TEXT)', ()),
            ('CREATE TABLE ObservedAdvertisementLocation (advId INTEGER PRIMARY KEY, latitude REAL, '
             'longitude REAL, horizontalAccuracy REAL, timestamp TEXT)', ()),
            ('CREATE TABLE ObservedAdvertisementBeaconInfo (advId INTEGER PRIMARY KEY, beaconIdentifier TEXT)', ()),
            ('INSERT INTO ObservedAdvertisement VALUES (1, ?, ?, -60, ?)', (mac, mac, when)),
            ('INSERT INTO ObservedAdvertisementBeaconInfo VALUES (1, ?)', (BEACON,))])

    def run_artifact(self):
        files = []
        for root, _dirs, names in os.walk(self.store):
            files += [os.path.join(root, name) for name in names if not name.startswith('plain-')]
        context = mock.Mock()
        context.get_files_found.return_value = files
        context.get_report_folder.return_value = os.path.join(self.tmp, 'report')
        entries = [{'agrp': 'com.apple.icloud.searchpartyd', 'svce': service, 'acct': account, 'v_Data': KEY}
                   for service, account in (('BeaconStore', 'BeaconStoreKey'), ('Observations', 'searchparty'))]
        with mock.patch.multiple(spd, active_keychain_path=mock.Mock(return_value='keychain.plist'),
                                 load_keychain_entries=mock.Mock(return_value=entries)):
            return spd.findMyBeaconDailyAddresses.__wrapped__(context)

    def test_keys_match_the_public_key_derivation_and_a_recorded_address(self):
        expected = oracle_keys(self.public, SECONDARY, 7)
        self.write_record(f'OwnedBeacons/{BEACON}.record', self.record)
        self.observations(mac_of(expected[2]), '2026-01-04T10:00:00.000')
        _headers, rows, _sources = self.run_artifact()
        # Observations reach 2026-01-04 10:00, 2 days and 22 hours after pairing: 2 whole days plus the margin.
        days = 2 + spd.DAY_MARGIN
        self.assertEqual([row[5] for row in rows], list(range(1, days + 1)))
        self.assertEqual([row[7] for row in rows], [key.hex() for key in oracle_keys(self.public, SECONDARY, days)])
        self.assertEqual([row[6] for row in rows], [mac_of(key).hex(':') for key in oracle_keys(self.public, SECONDARY, days)])
        self.assertEqual(rows[2][1].isoformat(), '2026-01-04T10:00:00+00:00')
        self.assertEqual([index for index, row in enumerate(rows, 1) if row[1]], [3])
        self.assertEqual(rows[0][0], (PAIRED + timedelta(days=1)).date().isoformat())

    def test_no_secondary_secret_gives_no_rows(self):
        del self.record['secondarySharedSecret']
        self.write_record(f'OwnedBeacons/{BEACON}.record', self.record)
        _headers, rows, _sources = self.run_artifact()
        self.assertEqual(rows, [])
        self.assertIn('no secondarySharedSecret', self.log.call_args[0][0])

    def test_a_private_key_that_does_not_match_the_public_key_gives_no_rows(self):
        private = bytearray(self.record['privateKey']['key']['data'])
        private[-1] ^= 1
        self.record['privateKey'] = {'key': {'data': bytes(private)}}
        self.write_record(f'OwnedBeacons/{BEACON}.record', self.record)
        _headers, rows, _sources = self.run_artifact()
        self.assertEqual(rows, [])
        self.assertIn('not in the layout read here', self.log.call_args_list[0][0][0])

    def test_pairing_date_reads_as_utc(self):
        self.write_record(f'OwnedBeacons/{BEACON}.record', self.record)
        _headers, rows, _sources = self.run_artifact()
        self.assertEqual(len(rows), spd.DAY_MARGIN)
        self.assertEqual(rows[0][0], '2026-01-02')
        self.assertEqual(PAIRED.replace(tzinfo=timezone.utc).date().isoformat(), '2026-01-01')


if __name__ == '__main__':
    unittest.main()
