"""Pin which Chromium profile folders the chrome.py artifacts select on iOS.

The paths named only Chrome/Default, so Chrome's other profiles, kept in a folder named by
a UUID, and every Edge profile (Microsoft/Edge/Default and Default-AAD) were never parsed.
Login Data also reads the Google app's stores, kept directly under Application Support.
Each store must be matched by exactly one pattern of an artifact, because the matches of
every pattern are added to the files found without removing repeats.
"""
import ast
import fnmatch
import pathlib
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
APP = 'root/private/var/mobile/Containers/Data/Application/550E4CE8-9B02-4908-A2E5-8CA81748F454'
SUPPORT = f'{APP}/Library/Application Support'
PROFILES = (
    'Google/Chrome/Default',
    'Google/Chrome/5D1B4F0A-7C3E-4E2B-9A61-0F7D2C8B3E14',
    'Microsoft/Edge/Default',
    'Microsoft/Edge/Default-AAD',
    'Chromium/Default',
)
# The files each artifact reads, as its basename test in chrome.py requires.
STORES = {
    'chromeWebHistory': 'History', 'chromeWebVisits': 'History', 'chromeWebSearch': 'History',
    'chromeDownloads': 'History', 'chromeKeywordSearchTerms': 'History',
    'chromeAutofillEntries': 'Web Data', 'chromeAutofillProfiles': 'Web Data',
    'chromeBookmarks': 'Bookmarks', 'chromeCookies': 'Cookies', 'chromeLoginData': ('Login Data', 'Login Data For Account'),
    'chromeTopSites': 'Top Sites', 'chromeOfflinePages': 'Offline Pages/metadata/OfflinePages.db',
    'chromeMediaHistorySessions': 'Media History', 'chromeMediaHistoryPlaybacks': 'Media History',
    'chromeMediaHistoryOrigins': 'Media History',
    'chromeNetworkActionPredictor': 'Network Action Predictor',
}


def chrome_paths():
    tree = ast.parse((REPO_ROOT / 'scripts/artifacts/chrome.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == '__artifacts_v2__':
            return {k: v['paths'] for k, v in ast.literal_eval(node.value).items()}
    raise AssertionError('no __artifacts_v2__ block in chrome.py')


class TestChromeProfilePaths(unittest.TestCase):

    def test_every_artifact_is_listed(self):
        self.assertEqual(set(chrome_paths()), set(STORES))

    def test_each_profile_store_is_matched_once(self):
        for artifact, patterns in chrome_paths().items():
            stores = STORES[artifact]
            for store in (stores,) if isinstance(stores, str) else stores:
                for profile in PROFILES:
                    path = f'{SUPPORT}/{profile}/{store}'
                    with self.subTest(artifact=artifact, profile=profile, store=store):
                        matches = [p for p in patterns if fnmatch.fnmatchcase(path, p)]
                        self.assertEqual(len(matches), 1, matches)

    def test_google_app_login_stores_are_matched_once(self):
        # The Google app keeps its Chromium stores directly under Application Support.
        patterns = chrome_paths()['chromeLoginData']
        for store in STORES['chromeLoginData']:
            path = f'{SUPPORT}/{store}'
            with self.subTest(store=store):
                matches = [p for p in patterns if fnmatch.fnmatchcase(path, p)]
                self.assertEqual(len(matches), 1, matches)


if __name__ == '__main__':
    unittest.main()
