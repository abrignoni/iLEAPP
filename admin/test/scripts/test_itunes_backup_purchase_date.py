"""itunes_backup_installed_applications must accept purchaseDate in the two stored forms seen so far.

An app's iTunesMetadata, embedded in the backup's Info.plist, carries
com.apple.iTunesStore.downloadInfo/purchaseDate either as an ISO-8601 string with a
trailing Z or as a plist <date>, which plistlib loads as a datetime.datetime. The
artifact sliced the value as a string, so a backup storing the date form (reported on an
iOS 12.3 backup, #1950) raised TypeError on the first such app and produced no rows at all.

These tests run the artifact the way the runner does over a constructed backup holding one
app of each form, plus text with no offset, and read back the Purchase Date column. Both
stated forms come back as the same UTC datetime; text that states no offset comes back blank.
releaseDate, at the top level of the same iTunesMetadata, is read the same way into the
Release Date column.
"""
import datetime
import pathlib
import plistlib
import shutil
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.artifacts import iTunesBackupInfo  # pylint: disable=wrong-import-position

DATE_APP = 'com.example.plistdate'
STRING_APP = 'com.example.isostring'
NO_OFFSET_APP = 'com.example.nooffset'
PURCHASED = datetime.datetime(2019, 5, 14, 9, 30, 15)


def _metadata(purchase_date):
    return plistlib.dumps({
        'itemName': 'Constructed App',
        'releaseDate': purchase_date,
        'com.apple.iTunesStore.downloadInfo': {
            'accountInfo': {'AppleID': 'examiner@example.com'},
            'purchaseDate': purchase_date,
        },
    })


class ITunesBackupPurchaseDateTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        tmp = pathlib.Path(self.tmpdir)
        report = tmp / 'report'
        for folder in ('data', 'media', '_HTML/media'):
            (report / folder).mkdir(parents=True, exist_ok=True)
        backup = tmp / 'backup'
        backup.mkdir()
        info_plist = backup / 'Info.plist'
        info_plist.write_bytes(plistlib.dumps({
            'Product Name': 'iPhone',
            'Installed Applications': [DATE_APP, STRING_APP, NO_OFFSET_APP],
            'Applications': {
                # plistlib writes a datetime as <date>, and reads it back as one.
                DATE_APP: {'iTunesMetadata': _metadata(PURCHASED)},
                STRING_APP: {'iTunesMetadata': _metadata('2019-05-14T09:30:15Z')},
                NO_OFFSET_APP: {'iTunesMetadata': _metadata('2019-05-14T09:30:15')},
            },
        }))
        Context.clear()
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(report / 'media'), html_media_folder=str(report / '_HTML' / 'media'),
            data_folder=str(report / 'data'), output_folder_base=str(report)))
        Context.set_files_found([str(info_plist)])
        Context.set_seeker(types.SimpleNamespace(file_infos={}, directory=str(backup)))
        Context.set_module_name('iTunesBackupInfo')
        Context.set_artifact_name('iTunes Backup - Installed Applications')

    def tearDown(self):
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_both_purchase_date_forms_read_as_the_same_utc_datetime(self):
        headers, rows, _ = iTunesBackupInfo.itunes_backup_installed_applications.__wrapped__(Context)

        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        by_bundle = {row[names.index('Bundle ID')]: row for row in rows}
        self.assertEqual(set(by_bundle), {DATE_APP, STRING_APP, NO_OFFSET_APP})

        purchase = names.index('Purchase Date')
        expected = PURCHASED.replace(tzinfo=datetime.timezone.utc)
        self.assertEqual(by_bundle[DATE_APP][purchase], expected)
        self.assertEqual(by_bundle[STRING_APP][purchase], expected)
        self.assertEqual(by_bundle[NO_OFFSET_APP][purchase], '')

    def test_release_date_reads_like_purchase_date(self):
        headers, rows, _ = iTunesBackupInfo.itunes_backup_installed_applications.__wrapped__(Context)

        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        by_bundle = {row[names.index('Bundle ID')]: row for row in rows}
        release = names.index('Release Date')
        expected = PURCHASED.replace(tzinfo=datetime.timezone.utc)
        self.assertEqual(by_bundle[DATE_APP][release], expected)
        self.assertEqual(by_bundle[STRING_APP][release], expected)
        self.assertEqual(by_bundle[NO_OFFSET_APP][release], '')


if __name__ == '__main__':
    unittest.main()
