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
    def _run(self, func):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = fixture(root)
            return func.__wrapped__(SimpleNamespace(get_files_found=lambda: paths))

    def test_installed(self):
        headers, rows, source = self._run(parser.configuration_profiles)
        self.assertTrue(all(len(r) == len(headers) for r in rows))
        by_id = {r[2]: r for r in rows}
        self.assertEqual(sorted(by_id), ['carrier.one', 'orphan.three', 'user.two'])
        self.assertEqual(by_id['carrier.one'][7], 'HiddenProfiles')
        self.assertEqual(by_id['carrier.one'][10], 'Carrier')
        self.assertEqual(by_id['user.two'][7], 'OrderedProfiles')
        self.assertEqual(by_id['user.two'][8], 'com.apple.Preferences')
        self.assertEqual(by_id['orphan.three'][7], 'Not in PayloadManifest')
        self.assertEqual(by_id['user.two'][6], 'com.apple.webClip.managed, com.apple.vpn.managed')
        self.assertEqual(by_id['user.two'][0].tzinfo, datetime.timezone.utc)
        self.assertEqual(len(source.splitlines()), 4)

    def test_holding_tank(self):
        headers, rows, source = self._run(parser.configuration_profiles_holding_tank)
        self.assertTrue(all(len(r) == len(headers) for r in rows))
        by_id = {r[3]: r for r in rows}
        self.assertEqual(by_id['waiting.four'][1], 'Yes')
        self.assertEqual(by_id['waiting.four'][0].replace(tzinfo=None), WHEN)
        self.assertEqual(by_id[''][1], 'No')           # the undecodable download keeps a row
        self.assertEqual(by_id[''][0], '')
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(source.splitlines()), 3)


if __name__ == '__main__':
    unittest.main()
