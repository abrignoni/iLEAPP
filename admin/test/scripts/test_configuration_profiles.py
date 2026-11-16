"""Configuration Profiles on a synthetic container (values invented for the test)."""
import datetime
import pathlib
import plistlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import configurationProfiles as parser  # noqa: E402

BASE = 'private/var/containers/Shared/SystemGroup/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles'
WHEN = datetime.datetime(2026, 1, 2, 3, 4, 5)


def _profile(identifier, **extra):
    data = {'PayloadIdentifier': identifier, 'PayloadUUID': identifier.upper(), 'PayloadDisplayName': identifier,
            'PayloadContent': [{'PayloadType': 'com.apple.webClip.managed'}, {'PayloadType': 'com.apple.vpn.managed'}]}
    data.update(extra)
    return plistlib.dumps(data)


def fixture(root):
    base = root / BASE
    (base / 'phone').mkdir(parents=True)
    files = {
        'profile-aaa.stub': _profile('carrier.one', InstallDate=WHEN, MCProfileIsRemovalStub=False,
                                     InstallOptions={'carrierName': 'Carrier', 'isInstalledInteractively': False}),
        'profile-bbb.stub': _profile('user.two', InstallDate=WHEN,
                                     InstallOptions={'installedBy': 'com.apple.Preferences',
                                                     'isInstalledInteractively': True}),
        'profile-ccc.stub': _profile('orphan.three', InstallDate=WHEN),
        'PayloadManifest.plist': plistlib.dumps({'HiddenProfiles': ['carrier.one'], 'OrderedProfiles': ['user.two']}),
        'phone/profile-ddd.pdata': _profile('waiting.four'),
        'phone/profile-eee.pdata': b'0\x82\x05\x00 signed envelope bytes',
        'phone/HoldingTankManifest.plist': plistlib.dumps({'waiting.four': WHEN}),
    }
    paths = []
    for name, data in files.items():
        path = base / name
        path.write_bytes(data)
        paths.append(str(path))
    return paths


class ConfigurationProfilesTest(unittest.TestCase):
    def test_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = fixture(root)
            headers, rows, source = parser.configuration_profiles.__wrapped__(
                SimpleNamespace(get_files_found=lambda: paths))
        self.assertTrue(all(len(r) == len(headers) for r in rows))
        by_id = {r[4]: r for r in rows}
        self.assertEqual(by_id['carrier.one'][9], 'Hidden')
        self.assertEqual(by_id['carrier.one'][12], 'Carrier')
        self.assertEqual(by_id['user.two'][9], 'Listed')
        self.assertEqual(by_id['user.two'][10], 'com.apple.Preferences')
        self.assertEqual(by_id['orphan.three'][9], 'Not in PayloadManifest')
        self.assertEqual(by_id['user.two'][8], 'com.apple.webClip.managed, com.apple.vpn.managed')
        self.assertEqual(by_id['user.two'][0].tzinfo, datetime.timezone.utc)
        self.assertEqual(by_id['waiting.four'][2], 'Downloaded, not installed')
        self.assertEqual(by_id['waiting.four'][1].replace(tzinfo=None), WHEN)
        self.assertIn('', by_id)  # the undecodable download keeps a row
        self.assertEqual(by_id[''][2], 'Downloaded, not installed; file not decoded (not a plain plist)')
        self.assertEqual(len(rows), 5)
        self.assertEqual(len(source.splitlines()), 7)


if __name__ == '__main__':
    unittest.main()
