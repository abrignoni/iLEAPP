"""Pin how get_browser_name names the browser behind a Chromium file.

The name used to come from substrings of the whole staged path, so the examiner's own
folders above the data folder decided it: a case folder holding "microsoft" made every
row Edge, and one holding "chrome" made any unnamed file Chrome. Brave on iOS keeps its
profile under Application Support/Chromium, so a full file system named it Chromium.
The name now comes from the container's bundle identifier, then from the folders inside
the container.
"""
import pathlib
import plistlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.artifacts import chrome  # pylint: disable=wrong-import-position

APP = 'private/var/mobile/Containers/Data/Application'
CHROME = '550E4CE8-9B02-4908-A2E5-8CA81748F454'
BRAVE = '1B5AD18E-8383-48CF-855B-AAF876A8718B'
GOOGLE = 'BD043E32-DAF4-4BA1-B6B5-3B018CD36828'
NOTES = '6C1E2A40-3B7D-4F59-9E0A-7D2F5B8C1A36'
NO_PLIST = '82FD7DCE-31F2-4DB1-8D53-9E3BCD30897F'
META = '.com.apple.mobile_container_manager.metadata.plist'


class FakeSeeker:
    """Return the staged files whose evidence path matches, as the seekers do."""

    def __init__(self, data):
        self.data = data
        self.patterns = []

    def search(self, pattern):
        self.patterns.append(pattern)
        container = pattern.split('/')[-2]
        return [str(p) for p in self.data.rglob(META) if p.parent.name == container]


class TestGetBrowserName(unittest.TestCase):

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        # The examiner's own folders, holding every word the old test looked for.
        self.data = self.tmp / 'Microsoft Fraud brave opera chromium chrome app_sbrowser' / 'data'
        for container, identifier in ((CHROME, 'com.google.chrome.ios'),
                                      (BRAVE, 'com.brave.ios.browser'),
                                      (GOOGLE, 'com.google.GoogleMobile'),
                                      (NOTES, 'com.apple.mobilenotes')):
            folder = self.data / APP / container
            folder.mkdir(parents=True)
            (folder / META).write_bytes(plistlib.dumps({'MCMMetadataIdentifier': identifier}))
        self._saved = (Context.get_data_folder(), Context._seeker)  # pylint: disable=protected-access
        self.seeker = FakeSeeker(self.data)
        Context.set_data_folder(str(self.data))
        Context.set_seeker(self.seeker)
        getattr(chrome, '_container_identifiers', {}).clear()

    def tearDown(self):
        Context.set_data_folder(self._saved[0])
        Context.set_seeker(self._saved[1])
        getattr(chrome, '_container_identifiers', {}).clear()
        shutil.rmtree(self.tmp)

    def staged(self, relative):
        return str(self.data / relative)

    def test_container_identifier_names_the_browser(self):
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{APP}/{CHROME}/Library/Application Support/Google/Chrome/Default/History')), 'Chrome')
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{APP}/{BRAVE}/Library/Application Support/Chromium/Default/History')), 'Brave')
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{APP}/{GOOGLE}/Library/Application Support/Login Data For Account')), 'Google')

    def test_examiner_folders_never_name_the_browser(self):
        # A container of an app that is not mapped: nothing inside the extraction names a browser.
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{APP}/{NOTES}/Library/Application Support/Web Data')), 'Unknown')
        self.assertEqual(chrome.get_browser_name(self.staged('Some/Loose/History')), 'Unknown')

    def test_folders_inside_the_container_without_its_metadata(self):
        base = f'{APP}/{NO_PLIST}/Library/Application Support'
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{base}/Microsoft/Edge/Default/Web Data')), 'Edge')
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{base}/Google/Chrome/Default/Web Data')), 'Chrome')
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{base}/Chromium/Default/History')), 'Chromium')

    def test_backup_container_folder_is_the_bundle_identifier(self):
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{APP}/com.brave.ios.browser/Library/Application Support/Chromium/Default/History')),
            'Brave')
        self.assertEqual(self.seeker.patterns, [])

    def test_samsung_internet_is_read_inside_the_extraction(self):
        self.assertEqual(chrome.get_browser_name(self.staged(
            'data/data/com.sec.android.app.sbrowser/app_sbrowser/Default/History')), 'Browser')

    def test_metadata_is_read_once_per_container(self):
        path = self.staged(f'{APP}/{CHROME}/Library/Application Support/Google/Chrome/Default/History')
        chrome.get_browser_name(path)
        chrome.get_browser_name(path)
        self.assertEqual(len(self.seeker.patterns), 1)

    def test_metadata_of_another_root_with_the_same_guid_is_ignored(self):
        other = self.data / 'copy' / APP / NO_PLIST
        other.mkdir(parents=True)
        (other / META).write_bytes(plistlib.dumps({'MCMMetadataIdentifier': 'com.microsoft.msedge'}))
        self.assertEqual(chrome.get_browser_name(self.staged(
            f'{APP}/{NO_PLIST}/Library/Application Support/Google/Chrome/Default/History')), 'Chrome')


if __name__ == '__main__':
    unittest.main()
