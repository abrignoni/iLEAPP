"""Parent sections supplement unchanged selected plist values."""
import datetime
import json
import pathlib
import plistlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import mobileBackupplist as parser


def document():
    date = datetime.datetime(2020, 1, 2, 3, 4, 5)
    return {'BackupStateInfo': {'isCloud': False, 'date': date, 'errors': [date, b'\x00\xff'], 'ignored': 'not selected'},
            'RestoreInfo': {'BackupBuildVersion': '', 'DeviceBuildVersion': 0, 'WasCloudRestore': True, 'RestoreDate': date, 'date': 'ignored repeated name'},
            'DeviceTransferInfo': {'BytesTransferred': -1, 'RestoreDuration': 1.25, 'BuildVersion': b'\x00\xff', 'ConnectionType': {'nested': date}, 'SourceDeviceUDID': '  '},
            'FSEventState': {'eventId': 0, 'eventDatabaseUUID': b'\x00\xff', 'dateCreated': date, 'date': 'ignored repeated name'},
            'Unknown': {'date': date}}


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: paths,
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


def write(root, relative, data, fmt):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(plistlib.dumps(data, fmt=fmt, sort_keys=False))
    return str(path)


class MobileBackupSectionTest(unittest.TestCase):
    def test_xml_binary_native_cells_sections_and_ignored_repeated_keys(self):
        expected = [('isCloud', False, 'BackupStateInfo'), ('date', '2020-01-02 03:04:05', 'BackupStateInfo'),
                    ('errors', json.dumps([datetime.datetime(2020, 1, 2, 3, 4, 5), b'\x00\xff'], default=str), 'BackupStateInfo'),
                    ('BackupBuildVersion', '', 'RestoreInfo'), ('DeviceBuildVersion', 0, 'RestoreInfo'),
                    ('WasCloudRestore', True, 'RestoreInfo'), ('RestoreDate', '2020-01-02 03:04:05', 'RestoreInfo'),
                    ('BytesTransferred', -1, 'DeviceTransferInfo'), ('RestoreDuration', 1.25, 'DeviceTransferInfo'),
                    ('BuildVersion', '00ff', 'DeviceTransferInfo'), ('ConnectionType', '{"nested": "2020-01-02 03:04:05"}', 'DeviceTransferInfo'),
                    ('SourceDeviceUDID', '  ', 'DeviceTransferInfo'), ('eventId', 0, 'FSEventState'),
                    ('eventDatabaseUUID', '00ff', 'FSEventState'), ('dateCreated', '2020-01-02 03:04:05', 'FSEventState')]
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            for fmt in [plistlib.PlistFormat.FMT_XML, plistlib.PlistFormat.FMT_BINARY]:
                path = write(root, str(fmt.value)+'/com.apple.MobileBackup.plist', document(), fmt)
                headers, rows, source = parser.mobilebackupplist.__wrapped__(context(root, [path]))
                self.assertEqual(headers, ('Key', 'Value', 'Section'))
                self.assertEqual(rows, expected)
                self.assertEqual([type(r[1]) for r in rows], [type(r[1]) for r in expected])
                self.assertEqual(source, str(pathlib.Path(path).relative_to(root)))
                self.assertEqual(sum(r[0]=='date' for r in rows), 1)

    def test_first_input_null_and_nondict_sections_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            first = write(root, 'first/com.apple.MobileBackup.plist', {'BackupStateInfo': {'isCloud': None}, 'RestoreInfo': ['not a block']}, plistlib.PlistFormat.FMT_BINARY)
            later = write(root, 'later/com.apple.MobileBackup.plist', document(), plistlib.PlistFormat.FMT_XML)
            headers, rows, source = parser.mobilebackupplist.__wrapped__(context(root, [first, later, first]))
            self.assertEqual(rows, [('isCloud', None, 'BackupStateInfo')])
            self.assertEqual(source, 'first/com.apple.MobileBackup.plist')
            self.assertEqual(len(headers), 3)
            headers, rows, source = parser.mobilebackupplist.__wrapped__(context(root, []))
            self.assertEqual((headers, rows, source), (('Key', 'Value', 'Section'), [], ''))


if __name__ == '__main__':
    unittest.main()
