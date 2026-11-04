"""Devices an earlier database state held and the current one does not are listed once, marked, with where
they were read."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import bluetoothOther, bluetoothPairedLE


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)) if path else ''


def wal_writer(path, create):
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('PRAGMA wal_autocheckpoint=0')
    connection.execute(create)
    connection.commit()
    connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    return connection


def snapshot(source_db, target_dir):
    target_dir.mkdir()
    files = []
    for source in source_db.parent.iterdir():
        target = target_dir / source.name
        shutil.copy2(source, target)
        files.append(target)
    return files


class BluetoothLeWalRowsTest(unittest.TestCase):
    def test_other_devices_deleted_device_listed_once_and_updates_not_listed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer/com.apple.MobileBluetooth.ledevices.other.db'
            writer = wal_writer(path, 'CREATE TABLE OtherDevices(Name, Address, LastSeenTime, Uuid)')
            writer.executemany('INSERT INTO OtherDevices VALUES (?,?,?,?)',
                               [('kept', 'a-1', 10, 'uuid-1'), ('gone', 'a-2', 20, 'uuid-2')])
            writer.commit()
            writer.execute("UPDATE OtherDevices SET LastSeenTime = 21 WHERE Uuid = 'uuid-2'")
            writer.commit()
            writer.execute("UPDATE OtherDevices SET LastSeenTime = 11 WHERE Uuid = 'uuid-1'")
            writer.execute("DELETE FROM OtherDevices WHERE Uuid = 'uuid-2'")
            writer.commit()
            files = snapshot(path, root / 'snapshot')
            writer.close()

            headers, rows, _ = bluetoothOther.get_bluetoothOtherLE.__wrapped__(Context(root, files))

            self.assertEqual(headers[4:6], ('Record State', 'Read From'))
            self.assertEqual([row[:5] for row in rows],
                             [(11, 'kept', 'a-1', 'uuid-1', 'Current'),
                              (21, 'gone', 'a-2', 'uuid-2', 'Not in current state')])
            self.assertEqual(rows[0][5], '')
            self.assertEqual(rows[1][5], 'com.apple.MobileBluetooth.ledevices.other.db-wal, committed state 2')
            self.assertEqual(rows[1][6], 'snapshot/com.apple.MobileBluetooth.ledevices.other.db')

    def test_paired_device_only_in_log(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer/com.apple.MobileBluetooth.ledevices.paired.db'
            writer = wal_writer(path, 'CREATE TABLE PairedDevices(Uuid, Name, NameOrigin, Address, '
                                      'ResolvedAddress, LastSeenTime, LastConnectionTime)')
            writer.execute("INSERT INTO PairedDevices VALUES ('uuid-9', 'n', 1, 'a', 'r', 5, 6)")
            writer.commit()
            writer.execute('DELETE FROM PairedDevices')
            writer.commit()
            files = snapshot(path, root / 'snapshot')
            writer.close()

            headers, rows, _ = bluetoothPairedLE.get_bluetoothPairedLE.__wrapped__(Context(root, files))

            self.assertEqual(headers[7:9], ('Record State', 'Read From'))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][:8], (6, 5, 'uuid-9', 'n', 1, 'a', 'r', 'Not in current state'))
            self.assertIn('-wal, committed state', rows[0][8])

    def test_device_in_database_file_and_removed_by_a_log_commit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer/com.apple.MobileBluetooth.ledevices.other.db'
            writer = wal_writer(path, 'CREATE TABLE OtherDevices(Name, Address, LastSeenTime, Uuid)')
            writer.execute("INSERT INTO OtherDevices VALUES ('old', 'a-3', 30, 'uuid-3')")
            writer.commit()
            writer.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            writer.execute("INSERT INTO OtherDevices VALUES ('new', 'a-4', 40, 'uuid-4')")
            writer.commit()
            writer.execute("DELETE FROM OtherDevices WHERE Uuid = 'uuid-3'")
            writer.commit()
            files = snapshot(path, root / 'snapshot')
            writer.close()

            _, rows, _ = bluetoothOther.get_bluetoothOtherLE.__wrapped__(Context(root, files))

            self.assertEqual([row[3:6] for row in rows],
                             [('uuid-4', 'Current', ''),
                              ('uuid-3', 'Not in current state',
                               'com.apple.MobileBluetooth.ledevices.other.db without its -wal, through '
                               'com.apple.MobileBluetooth.ledevices.other.db-wal committed state 1')])

    def test_no_log_gives_current_rows_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'com.apple.MobileBluetooth.ledevices.paired.db'
            connection = sqlite3.connect(path)
            connection.execute('CREATE TABLE PairedDevices(Uuid, Name, NameOrigin, Address, '
                               'ResolvedAddress, LastSeenTime, LastConnectionTime)')
            connection.execute("INSERT INTO PairedDevices VALUES ('u', 'n', 1, 'a', 'r', 5, 6)")
            connection.commit()
            connection.close()

            _, rows, _ = bluetoothPairedLE.get_bluetoothPairedLE.__wrapped__(Context(root, [path]))

            self.assertEqual([row[7:9] for row in rows], [('Current', '')])


if __name__ == '__main__':
    unittest.main()
