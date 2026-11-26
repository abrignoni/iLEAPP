"""Reading searchpartyd .record files and joining them per store, on synthetic files."""
# pylint: disable=no-member,protected-access
import os
import plistlib
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

from Crypto.Cipher import AES

from scripts.artifacts import findMySearchpartyd as spd

KEY = bytes(range(32))
OTHER_KEY = bytes(reversed(range(32)))
NONCE = bytes(range(16))
BEACON = '11111111-2222-3333-4444-555555555555'
OTHER_BEACON = '66666666-7777-8888-9999-AAAAAAAAAAAA'


def record_bytes(document, key=KEY):
    cipher = AES.new(key, AES.MODE_GCM, nonce=NONCE)
    ciphertext, tag = cipher.encrypt_and_digest(plistlib.dumps(document, fmt=plistlib.FMT_BINARY))
    return plistlib.dumps([NONCE, tag, ciphertext], fmt=plistlib.FMT_BINARY)


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        spd._key_cache.clear()
        patcher = mock.patch.object(spd, 'logfunc')
        self.log = patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, store, relative, raw):
        path = os.path.join(self.tmp, store, 'mobile', 'Library', spd.STORE_DIR, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as record_file:
            record_file.write(raw)
        return path

    def keys(self, secrets, keychain='keychain.plist', field='v_Data',
             group='com.apple.icloud.searchpartyd'):
        entries = [{'agrp': group, 'svce': b'BeaconStore', 'acct': b'BeaconStoreKey', field: secret}
                   for secret in secrets]
        entries.append({'agrp': group, 'svce': 'Other', 'acct': 'searchparty', 'v_Data': KEY})
        return mock.patch.multiple(spd, active_keychain_path=mock.Mock(return_value=keychain),
                                   load_keychain_entries=mock.Mock(return_value=entries))


class ReadRecord(Base):
    def test_decrypts_with_the_beacon_store_key(self):
        path = self.write('a', 'OwnedBeacons/x.record', record_bytes({'identifier': BEACON}))
        with self.keys([KEY]):
            self.assertEqual(spd.read_searchpartyd_record(path), {'identifier': BEACON})
            spd.load_keychain_entries.assert_called_once_with('keychain.plist')

    def test_key_in_gena_of_the_older_access_group(self):
        path = self.write('a', 'OwnedBeacons/x.record', record_bytes({'identifier': BEACON}))
        with self.keys([KEY], field='gena', group='searchpartyd-baa-fmna-group'):
            self.assertEqual(spd.read_searchpartyd_record(path), {'identifier': BEACON})

    def test_other_items_are_not_candidates(self):
        path = self.write('a', 'OwnedBeacons/x.record', record_bytes({'identifier': BEACON}))
        with self.keys([KEY], group='com.example.app'):
            self.assertIsNone(spd.read_searchpartyd_record(path))
        self.assertIn('no readable BeaconStore key', self.log.call_args[0][0])

    def test_second_candidate_key_is_tried(self):
        path = self.write('a', 'OwnedBeacons/x.record', record_bytes({'identifier': BEACON}))
        with self.keys([OTHER_KEY, KEY]):
            self.assertEqual(spd.read_searchpartyd_record(path), {'identifier': BEACON})

    def test_key_of_wrong_length_is_ignored(self):
        path = self.write('a', 'OwnedBeacons/x.record', record_bytes({'identifier': BEACON}))
        with self.keys([KEY + b'x']):
            self.assertIsNone(spd.read_searchpartyd_record(path))
        self.assertIn('no readable BeaconStore key', self.log.call_args[0][0])

    def test_wrong_key_gives_nothing_and_logs(self):
        path = self.write('a', 'OwnedBeacons/x.record', record_bytes({'identifier': BEACON}))
        with self.keys([OTHER_KEY]):
            self.assertIsNone(spd.read_searchpartyd_record(path))
        self.assertIn('did not verify', self.log.call_args[0][0])

    def test_tampered_ciphertext_is_refused(self):
        nonce, tag, ciphertext = plistlib.loads(record_bytes({'identifier': BEACON}))
        ciphertext = bytes([ciphertext[0] ^ 1]) + ciphertext[1:]
        path = self.write('a', 'OwnedBeacons/x.record',
                          plistlib.dumps([nonce, tag, ciphertext], fmt=plistlib.FMT_BINARY))
        with self.keys([KEY]):
            self.assertIsNone(spd.read_searchpartyd_record(path))

    def test_no_keychain_is_logged(self):
        path = self.write('a', 'OwnedBeacons/x.record', record_bytes({'identifier': BEACON}))
        with self.keys([], keychain=None):
            self.assertIsNone(spd.read_searchpartyd_record(path))
        self.assertIn('--keychain', self.log.call_args[0][0])

    def test_unreadable_file_is_logged_not_raised(self):
        path = os.path.join(self.tmp, 'missing.record')
        with self.keys([KEY]):
            self.assertIsNone(spd.read_searchpartyd_record(path))
        self.assertIn('could not read record', self.log.call_args[0][0])

    def test_other_layouts_are_refused(self):
        for raw in (b'not a plist', plistlib.dumps({'encryptedData': b'x'}, fmt=plistlib.FMT_BINARY),
                    plistlib.dumps([b'x' * 12, b't' * 16, b'c'], fmt=plistlib.FMT_BINARY)):
            path = self.write('a', 'OwnedBeacons/x.record', raw)
            with self.keys([KEY]):
                self.assertIsNone(spd.read_searchpartyd_record(path))
            self.assertIn('not a nonce, tag and ciphertext list', self.log.call_args[0][0])


class Artifacts(Base):
    def context(self):
        files = []
        for root, _dirs, names in os.walk(self.tmp):
            files += [os.path.join(root, name) for name in names]
        ctx = mock.Mock()
        ctx.get_files_found.return_value = files
        return ctx

    def populate(self, store, beacon, name, when):
        self.write(store, f'OwnedBeacons/{beacon}.record', record_bytes(
            {'identifier': beacon, 'pairingDate': when, 'model': 'm', 'systemVersion': '1',
             'batteryLevel': 0, 'productId': 1, 'vendorId': 2, 'isZeus': False,
             'stableIdentifier': ['s'], 'privateKey': {'key': {'data': b'k'}}}))
        self.write(store, f'BeaconNamingRecord/{beacon}/n.record', record_bytes(
            {'identifier': 'n', 'associatedBeacon': beacon, 'name': name, 'roleId': 0}))
        self.write(store, f'BeaconEstimatedLocation/{beacon}/e1.record', record_bytes(
            {'identifier': 'e1', 'associatedBeacon': beacon, 'latitude': 1.5, 'longitude': 2.5,
             'horizontalAccuracy': 10.0, 'locationSource': 3, 'timestamp': when, 'scanDate': '$null'}))
        self.write(store, 'LeashRecords/l.record', record_bytes(
            {'identifier': 'l', 'associatedBeacons': [beacon]}))

    def test_estimated_location_row_and_null_scan_date(self):
        when = datetime(2026, 1, 2, 3, 4, 5)
        self.populate('a', BEACON, 'Keys', when)
        with self.keys([KEY]):
            _headers, data, sources = spd.findMyBeaconEstimatedLocations.__wrapped__(self.context())
        self.assertEqual(data, [(when.replace(tzinfo=timezone.utc), '', 1.5, 2.5, 10.0, 3, 'Keys', 'OwnedBeacons', BEACON)])
        self.assertTrue(sources.endswith('e1.record'))

    def test_unreadable_record_does_not_hide_the_others(self):
        self.populate('a', BEACON, 'Keys', datetime(2026, 1, 2, 3, 4, 5))
        ctx = self.context()
        missing = os.path.join(self.tmp, 'a', 'mobile', 'Library', spd.STORE_DIR,
                               'OwnedBeacons', 'gone.record')
        ctx.get_files_found.return_value = [missing] + ctx.get_files_found.return_value
        with self.keys([KEY]):
            _headers, data, _sources = spd.findMyOwnedBeacons.__wrapped__(ctx)
        self.assertEqual([row[10] for row in data], [BEACON])

    def test_names_join_only_within_one_store(self):
        when = datetime(2026, 1, 2, 3, 4, 5)
        self.populate('a', BEACON, 'Keys', when)
        self.populate('b', OTHER_BEACON, 'Bag', when)
        # A naming record for BEACON in store b must not rename BEACON in store a.
        self.write('b', f'BeaconNamingRecord/{BEACON}/x.record', record_bytes(
            {'identifier': 'x', 'associatedBeacon': BEACON, 'name': 'Wrong', 'roleId': 0}))
        with self.keys([KEY]):
            _headers, data, _sources = spd.findMyOwnedBeacons.__wrapped__(self.context())
        names = sorted((row[10], row[2]) for row in data)
        self.assertEqual(names, [(BEACON, 'Keys'), ('66666666-7777-8888-9999-AAAAAAAAAAAA', 'Bag')])
        self.assertEqual([row[8] for row in data], [1, 1])
        self.assertEqual([row[9] for row in data], [1, 1])

    def test_shared_beacon_row_and_location_link(self):
        when = datetime(2026, 1, 2, 3, 4, 5)
        self.write('a', f'SharedBeacons/{OTHER_BEACON}.record', record_bytes(
            {'identifier': OTHER_BEACON, 'shareDate': when, 'accepted': True, 'shareType': 1,
             'ownerHandle': {'destination': 'owner@example.com', 'type': 1}, 'model': 'm',
             'systemVersion': '1', 'productId': -1, 'vendorId': -1,
             'name': {'ownerBeaconIdentifier': BEACON, 'version': 1}}))
        self.write('a', f'BeaconEstimatedLocation/{OTHER_BEACON}/e.record', record_bytes(
            {'identifier': 'e', 'associatedBeacon': OTHER_BEACON, 'latitude': 1.0, 'longitude': 2.0,
             'horizontalAccuracy': 5.0, 'locationSource': 8, 'timestamp': when, 'scanDate': when}))
        with self.keys([KEY]):
            _headers, shared, _sources = spd.findMySharedBeacons.__wrapped__(self.context())
            _headers, located, _sources = spd.findMyBeaconEstimatedLocations.__wrapped__(self.context())
        utc = when.replace(tzinfo=timezone.utc)
        self.assertEqual(shared, [(utc, utc, 'owner@example.com', 'm', '1', 1, -1, -1, 1,
                                   OTHER_BEACON, BEACON)])
        self.assertEqual([row[7] for row in located], ['SharedBeacons'])


if __name__ == '__main__':
    unittest.main()
