"""Garmin Connect and Tutanota: an AppGroup container with no readable metadata plist is
identified by its own Library/Preferences/<group id>.plist file name, and a readable plist wins."""
import plistlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position,protected-access
from scripts.artifacts import garminConnect, tutanota

META = '.com.apple.mobile_container_manager.metadata.plist'
GROUPS = ((garminConnect, 'group.com.garmin.connect'), (tutanota, 'group.de.tutao.tutanota'))


def write(root, rel, data=b'x'):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


def meta(identifier):
    return plistlib.dumps({'MCMMetadataIdentifier': identifier})


class TestGroupPrefsIdentity(unittest.TestCase):
    def test_missing_plist_uses_group_prefs_name(self):
        for module, group in GROUPS:
            with tempfile.TemporaryDirectory() as d:
                base = 'mobile/Containers/Shared/AppGroup/G1'
                prefs = write(d, f'{base}/Library/Preferences/{group}.plist')
                found = module._containers([prefs])
                self.assertEqual(found, {str(Path(d) / base): group}, module.__name__)

    def test_readable_plist_wins_over_prefs_name(self):
        for module, group in GROUPS:
            with tempfile.TemporaryDirectory() as d:
                base = 'mobile/Containers/Shared/AppGroup/G1'
                plist = write(d, f'{base}/{META}', meta('group.other.app'))
                prefs = write(d, f'{base}/Library/Preferences/{group}.plist')
                self.assertEqual(module._containers([plist, prefs]), {}, module.__name__)

    def test_unreadable_plist_falls_back(self):
        for module, group in GROUPS:
            with tempfile.TemporaryDirectory() as d:
                base = 'mobile/Containers/Shared/AppGroup/G1'
                prefs = write(d, f'{base}/Library/Preferences/{group}.plist')
                for bad in (b'not a plist', b'<?xml version="1.0"?><plist><dict>'):
                    plist = write(d, f'{base}/{META}', bad)
                    self.assertEqual(module._containers([plist, prefs]),
                                     {str(Path(d) / base): group}, module.__name__)

    def test_other_shapes_are_not_identified(self):
        for module, group in GROUPS:
            with tempfile.TemporaryDirectory() as d:
                wrong_name = write(d, 'mobile/Containers/Shared/AppGroup/G1/Library/Preferences/'
                                      'group.other.app.plist')
                deeper = write(d, f'mobile/Containers/Shared/AppGroup/G2/Library/Caches/x/Library/'
                                  f'Preferences/{group}.plist')
                data_container = write(d, f'mobile/Containers/Data/Application/A1/Library/'
                                          f'Preferences/{group}.plist')
                self.assertEqual(module._containers([wrong_name, deeper, data_container]), {},
                                 module.__name__)


if __name__ == '__main__':
    unittest.main()
