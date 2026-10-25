"""locServicesConfigClients reads the Routine.bundle entry under either key form (SYNTHETIC plists)."""
import plistlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import locServicesconfig

OLD_KEY = 'com.apple.locationd.bundle-/System/Library/LocationBundles/Routine.bundle'
NEW_KEY = 'p/System/Library/LocationBundles/Routine.bundle:'
ENTRY = {'FenceTimeStarted': 794059200.0, 'ReceivingLocationInformationTimeStopped': 794059260.0,
         'BundlePath': '/System/Library/LocationBundles/Routine.bundle'}


def run(plist):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'clients.plist'
        path.write_bytes(plistlib.dumps(plist))
        context = SimpleNamespace(get_files_found=lambda: [str(path)], get_relative_path=lambda value: Path(value).name)
        return locServicesconfig.locServicesConfigClients.__wrapped__(context)[1]


class ClientsTest(unittest.TestCase):
    def test_both_key_forms_give_the_five_rows(self):
        for key in (OLD_KEY, NEW_KEY):
            with self.subTest(key=key):
                rows = run({key: dict(ENTRY), 'p/System/Library/LocationBundles/Other.bundle:': {}})
                self.assertEqual([r[1] for r in rows], [
                    'FenceTimeStarted', 'ConsumptionPeriodBegin', 'ReceivingLocationInformationTimeStopped',
                    'Authorization', 'LocationTimeStopped'])
                self.assertEqual(rows[0][0], '2026-03-01 12:00:00')
                self.assertEqual(rows[1][0], '')

    def test_the_entry_of_another_bundle_gives_nothing(self):
        self.assertEqual(run({'p/System/Library/LocationBundles/Routine.bundle:p/System/Library/LocationBundles/Milod.bundle': dict(ENTRY)}), [])
        self.assertEqual(run({}), [])


if __name__ == '__main__':
    unittest.main()
