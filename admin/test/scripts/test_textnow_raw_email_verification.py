"""Retain SQLite verification observations without inventing a negative state."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import textNow

COLUMNS = (
    'ZUSERNAME ZPHONENUMBER ZEMAIL ZFIRSTNAME ZLASTNAME ZACCOUNTSTATUS '
    'ZEMAILVERIFIED ZUSERID ZUSERIDHEX ZSIPUSERNAME ZSIPHOST ZSIPCLIENTIP '
    'ZCREDITS ZTEXTNOWCREDIT ZCURRENCY ZISUNLIMITED ZSHOWADS ZLOCALTIMESTAMP '
    'ZREMOTETIMESTAMP ZLASTWALLETUPDATETIMESTAMP ZADREMOVALEXPIRYDATE ZSIPPASSWORD'
).split()
VALUES = [None, 0, 1, -7, 2.5, '', '1', 'No', b'\x00\xff', 1]


def account_row(verified):
    """Declared source record, with distinct unaffected fields."""
    return ('name', '001234', 'mail@example.invalid', ' First ', ' Last ', 'state',
            verified, 'uid', '0x01', 'sip-user', 'sip-host', '192.0.2.1', 5, 10,
            'USD', 0, 1, 1000, 2000, 3000, 4000, 'stored password')


def write_fixture(path, values, missing=False, wal=False):
    """Create a real SQLite store; caller keeps WAL writer alive when requested."""
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    columns = [name for name in COLUMNS if not (missing and name == 'ZEMAILVERIFIED')]
    db.execute('CREATE TABLE ZTMOACCOUNTINFO (' + ','.join(columns) + ')')
    db.commit()
    if wal:
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    records = [account_row(value) for value in values]
    if missing:
        records = [row[:6] + row[7:] for row in records]
    db.executemany('INSERT INTO ZTMOACCOUNTINFO VALUES (' + ','.join('?' for _ in columns) + ')', records)
    db.commit()
    return db


class TestRawEmailVerification(unittest.TestCase):
    """Exercise native parser values through actual schema and WAL readers."""
    def test_storage_classes_and_repeated_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '1234567890store'
            db = write_fixture(path, VALUES)
            kinds = {r[0] for r in db.execute('SELECT typeof(ZEMAILVERIFIED) FROM ZTMOACCOUNTINFO')}
            self.assertEqual(kinds, {'null', 'integer', 'real', 'text', 'blob'})
            db.close()
            headers, rows, source = textNow.textnow_ios_account.__wrapped__(
                SimpleNamespace(get_files_found=lambda: [str(path)]))
            self.assertEqual(len(headers), 21)
            self.assertEqual(headers[9], 'Email Verified (as stored)')
            self.assertEqual(source, str(path))
            self.assertEqual([r[9] for r in rows], VALUES)
            self.assertEqual([type(r[9]) for r in rows], [type(v) for v in VALUES])
            for row in rows:
                self.assertEqual(row[4:9], ('name', '001234', 'mail@example.invalid', 'First Last', 'state'))
                self.assertEqual(row[10:], ('uid', '0x01', 'sip-user', 'sip-host', '192.0.2.1',
                                            'Yes', '5', '10', 'USD', '0', '1'))
            self.assertEqual(rows[2], rows[-1])

    def test_missing_column_and_empty_table(self):
        with tempfile.TemporaryDirectory() as directory:
            for missing, values in [(True, [1, 0]), (False, [])]:
                path = Path(directory) / ('missing' if missing else 'empty')
                db = write_fixture(path, values, missing=missing)
                db.close()
                _, rows, _ = textNow.textnow_ios_account.__wrapped__(
                    SimpleNamespace(get_files_found=lambda path=path: [str(path)]))
                self.assertEqual([r[9] for r in rows], [None] * len(values))

    def test_uncheckpointed_wal_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '1234567890store'
            db = write_fixture(path, [None, b'wal', 0, 1], wal=True)
            try:
                self.assertGreater(Path(str(path) + '-wal').stat().st_size, 32)
                _, rows, _ = textNow.textnow_ios_account.__wrapped__(
                    SimpleNamespace(get_files_found=lambda: [str(path)]))
                self.assertEqual([r[9] for r in rows], [None, b'wal', 0, 1])
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
