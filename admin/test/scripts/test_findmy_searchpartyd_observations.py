"""Decrypting a searchpartyd SQLite store and reading every state of its log, on a synthetic store.

The store is built here: a plain SQLite database with 12 reserved bytes per page, written in WAL
mode, then encrypted page by page the way the searchpartyd stores are (AES-256-OFB, IV = page
number little-endian + the page's reserved bytes, page 1 bytes 16 to 23 left as they are, log
checksums over the encrypted frames). The plain copy is the oracle: the decrypted store must read
the same, state by state, through scripts/sqlite_wal.py.
"""
# pylint: disable=no-member,protected-access
import hashlib
import os
import plistlib
import shutil
import sqlite3
import struct
import tempfile
import unittest
from datetime import datetime
from unittest import mock

from Crypto.Cipher import AES

from scripts import sqlite_wal
from scripts.artifacts import findMySearchpartyd as spd

KEY = bytes(range(32))
OTHER_KEY = bytes(reversed(range(32)))
PAGE = 4096
RESERVED = 12
BEACON = '11111111-2222-3333-4444-555555555555'
OWNED = '66666666-7777-8888-9999-AAAAAAAAAAAA'
SHARED = 'ABCDEFAB-CDEF-ABCD-EFAB-CDEFABCDEFAB'

SCHEMA = '''
CREATE TABLE ObservedAdvertisement ("advId" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "source" INTEGER NOT NULL, "macAddress" BLOB NOT NULL, "advertisementData" BLOB NOT NULL,
    "rssi" INTEGER NOT NULL, "scanDate" TEXT NOT NULL);
CREATE TABLE ObservedAdvertisementLocation ("advId" INTEGER NOT NULL, "latitude" REAL NOT NULL,
    "longitude" REAL NOT NULL, "horizontalAccuracy" REAL NOT NULL, "timestamp" TEXT NOT NULL,
    PRIMARY KEY ("advId"));
CREATE TABLE ObservedAdvertisementBeaconInfo ("advId" INTEGER NOT NULL, "beaconIdentifier" TEXT NOT NULL,
    PRIMARY KEY ("advId"));
'''


def empty_database(path):
    """A one-page empty SQLite database whose pages keep RESERVED bytes unused."""
    header = bytearray(100)
    header[0:16] = b'SQLite format 3\x00'
    header[16:18] = PAGE.to_bytes(2, 'big')
    header[18:24] = bytes((1, 1, RESERVED, 64, 32, 32))
    header[24:28] = (1).to_bytes(4, 'big')      # change counter
    header[28:32] = (1).to_bytes(4, 'big')      # pages
    header[44:48] = (4).to_bytes(4, 'big')      # schema format
    header[56:60] = (1).to_bytes(4, 'big')      # UTF-8
    header[92:96] = (1).to_bytes(4, 'big')      # version-valid-for
    header[96:100] = (3045000).to_bytes(4, 'big')
    leaf = bytes((0x0D, 0, 0, 0, 0)) + (PAGE - RESERVED).to_bytes(2, 'big') + b'\x00'
    with open(path, 'wb') as handle:
        handle.write(bytes(header) + leaf + bytes(PAGE - 100 - len(leaf)))


def encrypt_page(key, page, number):
    # The reserved bytes (the IV) follow from the page, so a page a checkpoint copies from the log
    # into the database file is byte for byte the same in both, as SQLite SEE's copy is.
    reserved = hashlib.sha256(number.to_bytes(4, 'big') + page[:-RESERVED]).digest()[:RESERVED]
    iv = number.to_bytes(4, 'little') + reserved
    body = AES.new(key, AES.MODE_OFB, iv=iv).encrypt(page[:-RESERVED])
    if number == 1:
        body = body[:16] + page[16:24] + body[24:]
    return body + reserved


def encrypt_store(plain_db, out_db, key=KEY, torn_last_frame=False):
    with open(plain_db, 'rb') as handle:
        raw = handle.read()
    with open(out_db, 'wb') as handle:
        for number in range(len(raw) // PAGE):
            handle.write(encrypt_page(key, raw[number * PAGE:(number + 1) * PAGE], number + 1))
    with open(plain_db + '-wal', 'rb') as handle:
        wal = handle.read()
    big = bool(int.from_bytes(wal[:4], 'big') & 1)
    out = bytearray(wal[:32])
    state = struct.unpack('>II', wal[24:32])
    frame = 24 + PAGE
    for index in range((len(wal) - 32) // frame):
        offset = 32 + index * frame
        head = bytearray(wal[offset:offset + 24])
        number = int.from_bytes(head[:4], 'big')
        page = encrypt_page(key, wal[offset + 24:offset + frame], number)
        state = spd._wal_checksum(page, big, spd._wal_checksum(bytes(head[:8]), big, state))
        head[16:24] = struct.pack('>II', *state)
        out += head + page
    if torn_last_frame:
        out[-1] ^= 0xFF
    with open(out_db + '-wal', 'wb') as handle:
        handle.write(bytes(out))


def states(path):
    found = []
    with sqlite_wal.WalStates(path, include=spd._WAL_KINDS) as wal:
        for state in wal.states():
            try:
                rows = sorted(state.connection.execute('SELECT * FROM ObservedAdvertisement').fetchall())
            except sqlite3.OperationalError:
                rows = None  # before the table was created
            found.append((state.kind, state.number, rows))
    return found


class Store(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        spd._key_cache.clear()
        patcher = mock.patch.object(spd, 'logfunc')
        self.log = patcher.start()
        self.addCleanup(patcher.stop)
        self.plain = os.path.join(self.tmp, 'plain', 'Observations.db')
        os.makedirs(os.path.dirname(self.plain))
        empty_database(self.plain)
        self.connection = sqlite3.connect(self.plain, isolation_level=None)
        self.addCleanup(self.connection.close)
        self.connection.execute('PRAGMA journal_mode=WAL')
        self.connection.execute('PRAGMA wal_autocheckpoint=0')
        self.connection.executescript(SCHEMA)
        for number in range(1, 6):
            self.connection.execute('BEGIN')
            self.connection.execute(
                'INSERT INTO ObservedAdvertisement VALUES (NULL, 1, ?, ?, -60, ?)',
                (bytes(range(number, number + 6)), bytes(28), f'2026-01-0{number}T10:00:00.123'))
            self.connection.execute('INSERT INTO ObservedAdvertisementLocation VALUES (?, 1.5, 2.5, 10.0, ?)',
                                    (number, f'2026-01-0{number}T10:00:01.000'))
            if number == 2:
                self.connection.execute('INSERT INTO ObservedAdvertisementBeaconInfo VALUES (2, ?)', (BEACON,))
            self.connection.execute('COMMIT')
        self.connection.execute('DELETE FROM ObservedAdvertisement WHERE advId < 4')
        self.connection.execute('DELETE FROM ObservedAdvertisementLocation WHERE advId < 4')
        self.connection.execute('DELETE FROM ObservedAdvertisementBeaconInfo WHERE advId < 4')
        self.store = os.path.join(self.tmp, 'a', 'mobile', 'Library', spd.STORE_DIR, 'Observations.db')
        os.makedirs(os.path.dirname(self.store))

    def keys(self, secrets, field='v_Data'):
        entries = [{'agrp': 'com.apple.icloud.searchpartyd', 'svce': 'Observations', 'acct': 'searchparty',
                    field: secret} for secret in secrets]
        entries.append({'agrp': 'com.apple.icloud.searchpartyd', 'svce': 'CloudStorage', 'acct': 'searchparty',
                        'v_Data': KEY})
        return mock.patch.multiple(spd, active_keychain_path=mock.Mock(return_value='keychain.plist'),
                                   load_keychain_entries=mock.Mock(return_value=entries))

    def test_plain_store_keeps_its_reserved_bytes(self):
        with open(self.plain, 'rb') as handle:
            self.assertEqual(handle.read(24)[20], RESERVED)
        self.assertEqual(self.connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_every_state_reads_as_the_plain_store_does(self):
        encrypt_store(self.plain, self.store)
        with self.keys([OTHER_KEY, KEY]):
            copy = spd.decrypt_searchpartyd_db(self.store, 'Observations', os.path.join(self.tmp, 'out'))
        self.assertIsNotNone(copy)
        expected = states(self.plain)
        self.assertEqual(len(expected), 12)  # the database file, then eleven committed transactions
        self.assertEqual(states(copy), expected)

    def test_key_in_gena(self):
        encrypt_store(self.plain, self.store)
        with self.keys([KEY], field='gena'):
            self.assertIsNotNone(spd.decrypt_searchpartyd_db(self.store, 'Observations',
                                                             os.path.join(self.tmp, 'out')))

    def test_a_frame_failing_its_stored_checksum_still_fails(self):
        encrypt_store(self.plain, self.store, torn_last_frame=True)
        shutil.copy(self.plain, os.path.join(self.tmp, 'torn.db'))
        with open(self.plain + '-wal', 'rb') as handle:
            wal = bytearray(handle.read())
        wal[-1] ^= 0xFF
        with open(os.path.join(self.tmp, 'torn.db-wal'), 'wb') as handle:
            handle.write(bytes(wal))
        with self.keys([KEY]):
            copy = spd.decrypt_searchpartyd_db(self.store, 'Observations', os.path.join(self.tmp, 'out'))
        expected = states(os.path.join(self.tmp, 'torn.db'))
        self.assertEqual(len(expected), 11)  # the last commit is lost, as SQLite would lose it
        self.assertEqual(states(copy), expected)

    def test_a_damaged_log_header_is_read_as_the_plain_store_does(self):
        # Checkpointed, so the database file matches the log's last commit and scripts/sqlite_wal.py
        # can rebuild the earlier states from the frames alone.
        self.connection.execute('PRAGMA wal_checkpoint(PASSIVE)')
        encrypt_store(self.plain, self.store)
        damaged = os.path.join(self.tmp, 'damaged.db')
        shutil.copy(self.plain, damaged)
        for log in (self.plain + '-wal', self.store + '-wal'):
            with open(log, 'rb') as handle:
                wal = bytes(32) + handle.read()[32:]
            with open(damaged + '-wal' if log == self.plain + '-wal' else log, 'wb') as handle:
                handle.write(wal)
        with self.keys([KEY]):
            copy = spd.decrypt_searchpartyd_db(self.store, 'Observations', os.path.join(self.tmp, 'out'))
        self.assertIn('log header is damaged', self.log.call_args[0][0])
        expected = states(damaged)
        self.assertGreater(len(expected), 1)
        self.assertEqual(states(copy), expected)

    def test_no_key_decrypts_page_one(self):
        encrypt_store(self.plain, self.store)
        with self.keys([OTHER_KEY]):
            self.assertIsNone(spd.decrypt_searchpartyd_db(self.store, 'Observations',
                                                          os.path.join(self.tmp, 'out')))
        self.assertIn('no Observations key', self.log.call_args[0][0])

    def test_no_keychain(self):
        encrypt_store(self.plain, self.store)
        with mock.patch.object(spd, 'active_keychain_path', return_value=None):
            self.assertIsNone(spd.decrypt_searchpartyd_db(self.store, 'Observations',
                                                          os.path.join(self.tmp, 'out')))
        self.assertIn('no keychain', self.log.call_args[0][0])

    def test_other_layout_is_refused(self):
        encrypt_store(self.plain, self.store)
        with open(self.store, 'r+b') as handle:
            handle.seek(20)
            handle.write(b'\x00')
        with self.keys([KEY]):
            self.assertIsNone(spd.decrypt_searchpartyd_db(self.store, 'Observations',
                                                          os.path.join(self.tmp, 'out')))
        self.assertIn('not the encrypted layout', self.log.call_args[0][0])

    def test_artifact_reports_live_and_recovered_rows(self):
        encrypt_store(self.plain, self.store)
        context = mock.Mock()
        context.get_files_found.return_value = [self.store, self.store + '-wal']
        context.get_report_folder.return_value = os.path.join(self.tmp, 'report')
        with self.keys([KEY]):
            headers, rows, source = spd.findMyObservedAdvertisements.__wrapped__(context)
        self.assertEqual(source, self.store)
        by_id = {row[11]: row for row in rows}
        self.assertEqual(sorted(by_id), [1, 2, 3, 4, 5])
        self.assertEqual({row[11] for row in rows if row[12] == 'Live'}, {4, 5})
        recovered = by_id[2]
        self.assertEqual(recovered[12], 'Recovered')
        self.assertEqual(recovered[13], 'WAL committed states')
        self.assertEqual(recovered[14], 'Observations.db-wal, committed states 5 to 8')
        self.assertEqual(recovered[0].isoformat(), '2026-01-02T10:00:00.123000+00:00')
        self.assertEqual(recovered[1].isoformat(), '2026-01-02T10:00:01+00:00')
        self.assertEqual(recovered[7], BEACON)
        self.assertEqual(recovered[8], '02:03:04:05:06:07')
        self.assertEqual(recovered[10], '00' * 28)
        self.assertEqual(len(headers), len(recovered))
        self.assertTrue(os.path.isfile(os.path.join(
            self.tmp, 'report', spd.DECRYPTED_FOLDER, os.listdir(os.path.join(
                self.tmp, 'report', spd.DECRYPTED_FOLDER))[0], 'Observations.db')))


def encrypted_store(directory, name, statements, key=KEY):
    """An encrypted searchpartyd store named name in directory, built from SQL statements."""
    plain = os.path.join(directory, 'plain-' + name)
    empty_database(plain)
    connection = sqlite3.connect(plain, isolation_level=None)
    try:
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('PRAGMA wal_autocheckpoint=0')
        for statement, values in statements:
            connection.execute(statement, values)
        encrypt_store(plain, os.path.join(directory, name), key)
    finally:
        connection.close()


class BeaconAttributes(unittest.TestCase):
    """Names from BeaconAttributes in ItemSharingKeys.db reach the shared beacon rows."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        spd._key_cache.clear()
        patcher = mock.patch.object(spd, 'logfunc')
        patcher.start()
        self.addCleanup(patcher.stop)
        self.store = os.path.join(self.tmp, 'a', 'mobile', 'Library', spd.STORE_DIR)
        os.makedirs(self.store)

    def record(self, relative, document):
        path = os.path.join(self.store, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nonce = bytes(range(16))
        cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plistlib.dumps(document, fmt=plistlib.FMT_BINARY))
        with open(path, 'wb') as handle:
            handle.write(plistlib.dumps([nonce, tag, ciphertext], fmt=plistlib.FMT_BINARY))

    def context(self):
        files = []
        for root, _dirs, names in os.walk(self.store):
            files += [os.path.join(root, name) for name in names if not name.startswith('plain-')]
        context = mock.Mock()
        context.get_files_found.return_value = files
        context.get_report_folder.return_value = os.path.join(self.tmp, 'report')
        return context

    def keys(self):
        entries = [{'agrp': 'com.apple.icloud.searchpartyd', 'svce': service, 'acct': account, 'v_Data': KEY}
                   for service, account in (('BeaconStore', 'BeaconStoreKey'), ('KeyDatabase', 'searchparty'))]
        return mock.patch.multiple(spd, active_keychain_path=mock.Mock(return_value='keychain.plist'),
                                   load_keychain_entries=mock.Mock(return_value=entries))

    def test_shared_beacon_gets_its_name_and_emoji(self):
        when = datetime(2026, 1, 2, 3, 4, 5)
        encrypted_store(self.store, 'ItemSharingKeys.db', [
            ('CREATE TABLE BeaconAttributes (userIdentifier TEXT, beaconIdentifier TEXT, name TEXT, '
             'roleIdentifier INTEGER, emoji TEXT, systemVersion TEXT, serialNumber TEXT)', ()),
            ('INSERT INTO BeaconAttributes VALUES (?, ?, ?, -1, ?, ?, NULL)',
             ('u', SHARED.lower(), 'Shared name', 'e', '1')),
            ('INSERT INTO BeaconAttributes VALUES (?, ?, ?, -1, NULL, ?, NULL)',
             ('u', OWNED, 'Attribute name', '1'))])
        self.record(f'SharedBeacons/{SHARED}.record', {'identifier': SHARED, 'shareDate': when})
        self.record(f'BeaconEstimatedLocation/{SHARED}/e.record', {
            'identifier': 'e', 'associatedBeacon': SHARED, 'latitude': 1.0, 'longitude': 2.0,
            'timestamp': when, 'scanDate': when})
        self.record(f'OwnedBeacons/{OWNED}.record', {'identifier': OWNED, 'pairingDate': when})
        self.record(f'BeaconNamingRecord/{OWNED}/n.record', {
            'identifier': 'n', 'associatedBeacon': OWNED, 'name': 'Naming record name'})
        self.record(f'BeaconEstimatedLocation/{OWNED}/e.record', {
            'identifier': 'f', 'associatedBeacon': OWNED, 'latitude': 1.0, 'longitude': 2.0,
            'timestamp': when, 'scanDate': when})
        with self.keys():
            headers, shared, sources = spd.findMySharedBeacons.__wrapped__(self.context())
            _headers, located, _sources = spd.findMyBeaconEstimatedLocations.__wrapped__(self.context())
        self.assertEqual(headers[2:4], ('Name', 'Emoji'))
        self.assertEqual(shared[0][2:4], ('Shared name', 'e'))
        self.assertIn(os.path.join(self.store, 'ItemSharingKeys.db'), sources.split('\n'))
        self.assertEqual(sorted(row[6] for row in located), ['Naming record name', 'Shared name'])

    def test_without_the_store_the_rows_stay_unnamed(self):
        when = datetime(2026, 1, 2, 3, 4, 5)
        self.record(f'SharedBeacons/{SHARED}.record', {'identifier': SHARED, 'shareDate': when})
        with self.keys():
            _headers, shared, sources = spd.findMySharedBeacons.__wrapped__(self.context())
        self.assertEqual(shared[0][2:4], ('', ''))
        self.assertNotIn('ItemSharingKeys.db', sources)


if __name__ == '__main__':
    unittest.main()
