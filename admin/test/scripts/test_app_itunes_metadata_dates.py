"""Apps - Itunes Metadata must report purchaseDate and releaseDate as UTC datetimes.

An app's iTunesMetadata.plist carries com.apple.iTunesStore.downloadInfo/purchaseDate and
a top-level releaseDate. In the corpus images checked both are ISO 8601 text ending in Z,
which the artifact passed through as text. These tests run the artifact over constructed
plists holding each date as a plist <date>, as Z text and as text with no offset, and read
back the two columns. Both stated forms come back as the same UTC datetime; text that
states no offset comes back blank.
"""
import datetime
import pathlib
import plistlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.artifacts import appItunesmeta  # pylint: disable=wrong-import-position

STAMP = datetime.datetime(2019, 5, 14, 9, 30, 15)
FORMS = {
    'com.example.plistdate': STAMP,
    'com.example.isostring': '2019-05-14T09:30:15Z',
    'com.example.nooffset': '2019-05-14T09:30:15',
}


class AppItunesMetadataDateTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        tmp = pathlib.Path(self.tmpdir)
        files = []
        for bundle_id, value in FORMS.items():
            folder = tmp / 'Containers' / 'Bundle' / 'Application' / bundle_id
            folder.mkdir(parents=True)
            plist = folder / 'iTunesMetadata.plist'
            plist.write_bytes(plistlib.dumps({
                'softwareVersionBundleId': bundle_id,
                'releaseDate': value,
                'com.apple.iTunesStore.downloadInfo': {'purchaseDate': value},
            }))
            files.append(str(plist))
        Context.clear()
        Context.set_files_found(files)
        Context.set_module_name('appItunesmeta')
        Context.set_artifact_name('Apps - Itunes Metadata')

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_purchase_and_release_dates_read_as_utc_datetimes(self):
        headers, rows, _ = appItunesmeta.get_appItunesmeta.__wrapped__(Context)

        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertIn(('App Release Date', 'datetime'), headers)
        by_bundle = {row[names.index('Bundle ID')]: row for row in rows}
        self.assertEqual(set(by_bundle), set(FORMS))
        expected = STAMP.replace(tzinfo=datetime.timezone.utc)
        for column in ('App Purchase Date', 'App Release Date'):
            index = names.index(column)
            self.assertEqual(by_bundle['com.example.plistdate'][index], expected, column)
            self.assertEqual(by_bundle['com.example.isostring'][index], expected, column)
            self.assertEqual(by_bundle['com.example.nooffset'][index], '', column)


if __name__ == '__main__':
    unittest.main()
