"""Pin the source path the two iTunes backup Info.plist artifacts record.

For an iTunes backup input, the runner hands itunes_backup_info and
itunes_backup_installed_applications the Info.plist at the root of the backup folder
itself. The seeker never stages that file, so the path is the backup's location on the
examiner's machine, and neither the data folder nor the report folder is a prefix of it
for Context.get_relative_path to remove. Both artifacts recorded it as given: in the
"located at" line and LAVA manifest source_path, in the device information each property
was recorded with, and as the source of every app icon in the LAVA media table.

Measured on a constructed unencrypted backup before the fix: the absolute Info.plist path
was in the manifest source_path of both artifacts and in _lava_media_items.source_path.

These tests run the two artifacts the way the runner does, with the backup outside the
report folder, and read back what each recorded.
"""
import copy
import hashlib
import os
import pathlib
import plistlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs, lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.artifacts import iTunesBackupInfo  # pylint: disable=wrong-import-position

ICON = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\x00' * 48
BUNDLE_ID = 'com.example.constructed'


class ITunesBackupInfoSourcePathTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        tmp = pathlib.Path(self.tmpdir)
        report = tmp / 'report'
        data_folder = report / 'data'
        media_folder = report / 'media'
        html_media_folder = report / '_HTML' / 'media'
        for folder in (data_folder, media_folder, html_media_folder):
            folder.mkdir(parents=True, exist_ok=True)
        # The backup is the input: outside the report folder, never staged.
        self.backup = tmp / 'backup'
        self.backup.mkdir()
        info_plist = self.backup / 'Info.plist'
        info_plist.write_bytes(plistlib.dumps({
            'Product Name': 'iPhone',
            'Device Name': 'constructed',
            'Installed Applications': [BUNDLE_ID],
            'Applications': {BUNDLE_ID: {
                'iTunesMetadata': plistlib.dumps({'itemName': 'Constructed App'}),
                'PlaceholderIcon': ICON}},
        }))
        lavafuncs.initialize_lava(str(self.backup), str(report), 'itunes')
        self.saved_identifiers = copy.deepcopy(ilapfuncs.identifiers)
        ilapfuncs.identifiers.pop('iTunes Backup Information', None)
        Context.clear()
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(media_folder), html_media_folder=str(html_media_folder),
            data_folder=str(data_folder), output_folder_base=str(report)))
        Context.set_files_found([str(info_plist)])
        Context.set_seeker(types.SimpleNamespace(file_infos={}, directory=str(self.backup)))
        Context.set_module_name('iTunesBackupInfo')

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            try:
                lavafuncs.lava_db.close()
            except sqlite3.ProgrammingError:
                pass
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        ilapfuncs.identifiers.clear()
        ilapfuncs.identifiers.update(self.saved_identifiers)
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def assert_not_on_examiners_machine(self, value):
        self.assertNotIn(self.tmpdir, value)
        self.assertFalse(os.path.isabs(value), f'still absolute: {value!r}')

    def test_the_installed_applications_record_the_file_by_its_place_in_the_backup(self):
        Context.set_artifact_name('iTunes Backup - Installed Applications')

        _, rows, source = iTunesBackupInfo.itunes_backup_installed_applications.__wrapped__(Context)

        self.assertEqual(len(rows), 1)
        self.assertEqual(source, 'Info.plist')
        recorded = lavafuncs.lava_db.execute(
            'SELECT source_path FROM _lava_media_items WHERE id = ?',
            (hashlib.sha1(ICON).hexdigest(),)).fetchone()
        self.assertIsNotNone(recorded, 'the app icon was not checked in')
        self.assertEqual(recorded[0], 'Info.plist')
        self.assert_not_on_examiners_machine(recorded[0])

    def test_the_backup_information_records_the_file_by_its_place_in_the_backup(self):
        Context.set_artifact_name('iTunes Backup Information')

        _, rows, source = iTunesBackupInfo.itunes_backup_info.__wrapped__(Context)

        self.assertTrue(rows)
        self.assertEqual(source, 'Info.plist')
        recorded = ilapfuncs.identifiers['iTunes Backup Information']
        self.assertEqual(set(recorded), {'Product Name', 'Device Name'})
        for entries in recorded.values():
            for entry in (entries if isinstance(entries, list) else [entries]):
                self.assertEqual(entry['source_file'], 'Info.plist')


if __name__ == '__main__':
    unittest.main()
