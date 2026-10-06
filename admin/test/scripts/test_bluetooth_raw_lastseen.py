"""Actual OtherDevices SQLite values, ordering and WAL state remain as stored."""
import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import bluetoothOther as module


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)) if path else ''


SQL = 'SELECT Name, Address, LastSeenTime, Uuid FROM OtherDevices order by Name desc, OtherDevices.rowid'


def write_database(path, affinity='', wal=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    if wal:
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('PRAGMA wal_autocheckpoint=0')
    connection.execute(f'CREATE TABLE OtherDevices(Name, Address, LastSeenTime {affinity}, Uuid, unused)')
    connection.commit()
    if wal:
        connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    values = [None, 0, 1, -1, 9223372036854775807, 0.0, 123.456789, -0.25, '0', '', 'opaque']
    rows = [('same', f'addr-{index}', value, f'uid-{index}', 'ignored')
            for index, value in enumerate(values)]
    rows += [rows[0], (None, '', 0, None, 'ignored')]
    connection.executemany('INSERT INTO OtherDevices VALUES (?,?,?,?,?)', rows)
    connection.commit()
    return connection


class BluetoothRawLastSeenTest(unittest.TestCase):
    def test_native_values_affinities_repeats_and_source_order(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = []
            expected = []
            for index, affinity in enumerate(['', 'REAL']):
                path = root / str(index) / 'com.apple.MobileBluetooth.ledevices.other.db'
                connection = write_database(path, affinity)
                raw = connection.execute(SQL).fetchall()
                connection.close()
                files.append(path)
                expected.extend((row[2], row[0], row[1], row[3], str(path.relative_to(root))) for row in raw)
            headers, rows, source = module.get_bluetoothOtherLE.__wrapped__(Context(root, files))
            self.assertEqual(headers, ('LastSeenTime (As Stored)', 'Name', 'Address', 'UUID', 'Source File'))
            self.assertEqual(rows, expected)
            self.assertEqual([[type(value) for value in row] for row in rows],
                             [[type(value) for value in row] for row in expected])
            self.assertEqual(len(rows), 26)
            self.assertEqual(source.splitlines(), list(map(str, files)))

    def test_committed_wal_rows_and_complete_snapshot_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer/com.apple.MobileBluetooth.ledevices.other.db'
            writer = write_database(path, wal=True)
            snapshot = root / 'snapshot'
            snapshot.mkdir()
            files = []
            for source in path.parent.iterdir():
                target = snapshot / source.name
                shutil.copy2(source, target)
                target.chmod(0o444)
                files.append(target)
            snapshot.chmod(0o555)
            main_only = root / 'main-only.db'
            shutil.copy2(path, main_only)
            connection = sqlite3.connect(f'file:{main_only}?mode=ro', uri=True)
            self.assertEqual(connection.execute('SELECT count(*) FROM OtherDevices').fetchone()[0], 0)
            connection.close()
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            main = snapshot / path.name
            sidecars = [p for p in files if p != main]
            _, rows, _ = module.get_bluetoothOtherLE.__wrapped__(Context(root, sidecars + [main]))
            self.assertEqual(len(rows), 13)
            self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
            writer.close()
            snapshot.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
