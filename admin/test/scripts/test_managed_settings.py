"""managedSettings: sysdiagnose logs/ManagedSettings property lists, SYNTHETIC input only."""
import importlib.util
import plistlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import managedSettings as module

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_managed_settings', HERE / 'synthetic_managed_settings.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)

STORE_META = ('StoreName', 'Properties', 'version')


def _context(files):
    return SimpleNamespace(get_files_found=lambda: [str(path) for path in files],
                           get_relative_path=lambda value: Path(value.split(' >> ')[0]).name)


def _run(function, files):
    return function.__wrapped__(_context(files))


def _write_tree(folder, files):
    """Write {path below logs/ManagedSettings: bytes} as an extracted sysdiagnose folder; return the paths."""
    base = Path(folder) / 'sysdiagnose_SYNTHETIC_iPhone-OS_iPhone_00A000' / 'logs' / 'ManagedSettings'
    out = []
    for name, data in files.items():
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        out.append(path)
    return out


def independent_setting_count(files):
    """Rows the artifact must give for the readable property lists, counted straight from the plists."""
    total = 0
    for name, data in files.items():
        leaf = name.rsplit('/', 1)[-1]
        if leaf.endswith('.tokenized.plist') or leaf in ('DataVersion.plist', 'SettingRecords.plist'):
            continue
        try:
            obj = plistlib.loads(data)
        except plistlib.InvalidFileException:
            total += 1
            continue
        keys = [key for key in obj if key not in STORE_META]
        total += max(1, len(keys))
    return total


def independent_store_count(files):
    total = 0
    for name, data in files.items():
        if name.endswith('DataVersion.plist'):
            total += 1
        elif name.endswith('SettingRecords.plist'):
            for record in plistlib.loads(data):
                total += max(1, len(record['storeDirectory']))
    return total


class ManagedSettingsTest(unittest.TestCase):
    def _files(self, variant, edge=True):
        files = SYNTH.build_files(variant)
        if edge:
            files.update(SYNTH.edge_files())
        return files

    def test_row_counts_match_an_independent_count_in_both_versions(self):
        for variant in ('ios27', 'ios26'):
            files = self._files(variant)
            with tempfile.TemporaryDirectory() as folder:
                paths = _write_tree(folder, files)
                headers, rows, _ = _run(module.managedSettings, paths)
                s_headers, s_rows, _ = _run(module.managedSettingsStores, paths)
            self.assertEqual(len(rows), independent_setting_count(files), variant)
            self.assertEqual(len(s_rows), independent_store_count(files), variant)
            self.assertTrue(all(len(row) == len(headers) for row in rows))
            self.assertTrue(all(len(row) == len(s_headers) for row in s_rows))

    def test_both_versions_report_their_own_store_names(self):
        names = {}
        for variant in ('ios27', 'ios26'):
            with tempfile.TemporaryDirectory() as folder:
                headers, rows, _ = _run(module.managedSettings, _write_tree(folder, self._files(variant)))
            column = headers.index('Store Name')
            names[variant] = {row[column] for row in rows if row[headers.index('File Kind')] == 'Store file'}
        self.assertTrue({'ContentAndPrivacy', 'Restrictions', 'defaultGroup', 'bedtime'} <= names['ios27'])
        self.assertTrue({'SafariStore', 'UserSafetyStore', 'DeviceActivityStore'} <= names['ios26'])
        self.assertFalse(names['ios27'] & {'SafariStore', 'DeviceActivityStore'})

    def test_values_are_written_as_stored_without_a_verdict(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.managedSettings, _write_tree(folder, self._files('ios27')))
        by_key = {}
        for row in rows:
            if row[headers.index('File Kind')] == 'Store file':
                by_key.setdefault((row[headers.index('Store Name')], row[headers.index('Key (as stored)')]),
                                  row[headers.index('Value (as stored)')])
        self.assertEqual(by_key[('Restrictions', 'appStore.denyAppStoreAppInstallation')], 'true')
        self.assertEqual(by_key[('Restrictions', 'appStore.maximumRating')], '200')
        self.assertEqual(by_key[('Restrictions', 'webContent.blockedByFilter')], 'neverAllow: []; policy: 1')
        self.assertEqual(by_key[('defaultGroup', 'shield.applicationCategories')],
                         'activities: [com.example.shielded1, com.example.shielded2]; '
                         'categories: [SYNTH-CAT-1, SYNTH-CAT-2]')
        self.assertEqual(by_key[('defaultGroup', 'screenTime.categoryShieldPolicies')],
                         '[SYNTH-CAT-1=warn, SYNTH-CAT-2=block]')
        self.assertEqual(by_key[('ContentAndPrivacy', 'siri.denySiri')], 'true')
        self.assertEqual(by_key[('Restrictions', 'userSafety.scanningPolicy')], '(empty)')
        scanning = next(v for (store, key), v in by_key.items() if key == 'userSafety.scanningPolicy' and v != '(empty)')
        self.assertIn('onServices: [photos, messages]', scanning)

    def test_labels_groups_and_item_counts(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.managedSettings, _write_tree(folder, self._files('ios27')))
        row = next(r for r in rows if r[headers.index('Key (as stored)')] == 'screenTime.categoryShieldPolicies')
        self.assertEqual(row[headers.index('Group')], 'Shield')
        self.assertEqual(row[headers.index('Setting')], 'Category shield policies')
        self.assertEqual(row[headers.index('Items')], 2)
        row = next(r for r in rows if r[headers.index('Key (as stored)')] == 'shield.applicationCategories')
        self.assertEqual(row[headers.index('Items')], 4)
        row = next(r for r in rows if r[headers.index('Key (as stored)')] == 'siri.denySiri')
        self.assertEqual(row[headers.index('Group')], 'Siri and intelligence')

    def test_unknown_key_unreadable_file_and_empty_store(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.managedSettings, _write_tree(folder, self._files('ios27')))
        future = [r for r in rows if r[headers.index('Client Folder')] == 'com.example.future']
        self.assertEqual({r[headers.index('Key (as stored)')] for r in future}, {'example.futureKey', 'example.when'})
        key_row = next(r for r in future if r[headers.index('Key (as stored)')] == 'example.futureKey')
        self.assertEqual(key_row[headers.index('Setting')], 'Setting not described by this parser')
        self.assertEqual(key_row[headers.index('Group')], 'Other')
        self.assertEqual(key_row[headers.index('Value (as stored)')], 'a: x; b: [1, 2]')
        self.assertIn('extra', key_row[headers.index('Notes')])
        broken = [r for r in rows if r[headers.index('Client Folder')] == 'com.example.broken']
        self.assertEqual(len(broken), 1)
        self.assertEqual(broken[0][headers.index('Setting')], '(file could not be read as a property list)')
        empty = [r for r in rows if r[headers.index('Store Name')] == 'bedtime']
        self.assertEqual([r[headers.index('Setting')] for r in empty], ['(no setting key in this file)'])
        self.assertEqual(empty[0][headers.index('Store Active')], 'false')

    def test_key_material_is_never_copied(self):
        for variant in ('ios27',):
            with tempfile.TemporaryDirectory() as folder:
                headers, rows, _ = _run(module.managedSettings, _write_tree(folder, self._files(variant)))
        text = repr(rows)
        self.assertNotIn(repr(SYNTH.TOKEN_KEY), text)
        self.assertNotIn(SYNTH.TOKEN_KEY.hex(), text.lower())
        row = next(r for r in rows if r[headers.index('Key (as stored)')] == 'managedSettings.tokenEncodingKey')
        self.assertEqual(row[headers.index('Value (as stored)')], '<32 bytes, not copied>')
        row = next(r for r in rows if r[headers.index('Key (as stored)')] == 'managedSettings.tokenDecodingKeys')
        self.assertEqual(row[headers.index('Value (as stored)')], '[1 item(s), not copied]')

    def test_tokenized_copies_sidecars_and_other_folders_are_not_read(self):
        files = self._files('ios27')
        files['User/._EffectiveSettings.plist'] = b'\x00\x05\x16\x07'
        files['User/com.apple.Preferences/extra.tokenized.plist'] = plistlib.dumps({'version': 3, 'decoy': True})
        with tempfile.TemporaryDirectory() as folder:
            paths = _write_tree(folder, files)
            decoy = Path(folder) / 'other' / 'ManagedSettings' / 'User' / 'EffectiveSettings.plist'
            decoy.parent.mkdir(parents=True)
            decoy.write_bytes(plistlib.dumps({'version': 3, 'decoy': True}))
            _, rows, source = _run(module.managedSettings, paths + [decoy])
        self.assertNotIn('decoy', repr(rows))
        self.assertNotIn('tokenized', source)
        self.assertEqual(len(rows), independent_setting_count(self._files('ios27')))

    def test_store_directory_says_whether_the_store_file_is_in_the_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            headers, rows, _ = _run(module.managedSettingsStores, _write_tree(folder, self._files('ios27')))
        found = headers.index('Store File In Archive')
        entries = [r for r in rows if r[headers.index('Row Kind')] == 'Store entry']
        missing = [r for r in entries if r[headers.index('Client')] == 'com.example.missing']
        self.assertEqual([r[found] for r in missing], ['no'])
        self.assertEqual({r[found] for r in entries if r[headers.index('Client')] != 'com.example.missing'
                          and r[headers.index('Store Name')]}, {'yes'})
        empty = next(r for r in entries if r[headers.index('Client')] == 'com.example.empty')
        self.assertEqual(empty[headers.index('Store Name')], '')
        self.assertEqual(empty[headers.index('Notes')], 'The record has no store entry.')
        versions = [r for r in rows if r[headers.index('Row Kind')] == 'Data version']
        self.assertEqual(sorted(r[headers.index('Scope')] for r in versions), ['System', 'User'])
        self.assertEqual({r[headers.index('Data Version')] for r in versions}, {8})

    def test_sysdiagnose_archive_and_extracted_folder_give_the_same_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'sysdiagnose_2026.09.29_19-00-00-0400_iPhone-OS_iPhone_24A437.tar.gz'
            SYNTH.write_archive(archive, 'ios27', SYNTH.edge_files())
            _, from_archive, source = _run(module.managedSettings, [archive])
            _, stores_archive, _ = _run(module.managedSettingsStores, [archive])
            tree = Path(folder) / 'tree'
            paths = _write_tree(tree, self._files('ios27'))
            _, from_folder, _ = _run(module.managedSettings, paths)
            _, stores_folder, _ = _run(module.managedSettingsStores, paths)
        self.assertEqual(sorted(repr(r[:-1]) for r in from_archive), sorted(repr(r[:-1]) for r in from_folder))
        self.assertEqual(sorted(repr(r[:-1]) for r in stores_archive), sorted(repr(r[:-1]) for r in stores_folder))
        self.assertIn(' >> sysdiagnose_SYNTHETIC_iPhone-OS_iPhone_24A437/logs/ManagedSettings/User/', source)
        self.assertNotIn('decoy', repr(from_archive))

    def test_empty_input_gives_no_rows(self):
        headers, rows, source = _run(module.managedSettings, [])
        self.assertEqual((rows, source), ([], ''))
        self.assertTrue(headers)


if __name__ == '__main__':
    unittest.main()
