"""CD0568: distinct plist matches retain rows, provenance, and embedded exports."""
import importlib
import pathlib
import plistlib
import sys
import tempfile
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

MODULES = (
    ('Ph080comappleMobileSlideShowPlist', 'com.apple.mobileslideshow.plist'),
    ('Ph081comappleCameraPlist', 'com.apple.camera.plist'),
    ('Ph082comappleMediaAnalysisDPlist', 'com.apple.mediaanalysisd.plist'),
    ('Ph083comapplePurpleBuddyPlist', 'com.apple.purplebuddy.plist'),
    ('Ph085acntsdcloudServiceEnableLogplist', 'com.apple.accountsd/cloudServiceEnableLog.plist'),
    ('Ph086astsdcloudServiceEnableLogplist', 'com.apple.assetsd/cloudServiceEnableLog.plist'),
)
EMBEDDED = {
    'Ph080comappleMobileSlideShowPlist': ('TipKitEligibleContents-com.apple.mobileslideshow.one-up-photo',),
    'Ph081comappleCameraPlist': (
        'CAMUserPreferenceSharedLibraryLastDiscoveryLocation',
        'CAMUserPreferenceSharedLibraryLastLocation',
        'CAMUserPreferenceSharedLibraryLastUserActionLocation',
        'CAMUserPreferenceExposureBiasByMode',
    ),
}


class PhotosPreferencesMultifile(unittest.TestCase):
    def test_all_matches_keep_values_sources_and_side_effects(self):
        for module_name, filename in MODULES:
            with self.subTest(module=module_name), tempfile.TemporaryDirectory() as tmp:
                module = importlib.import_module('scripts.artifacts.' + module_name)
                parser = getattr(module, next(iter(module.__artifacts_v2__))).__wrapped__
                root = pathlib.Path(tmp)
                report = root / 'report'
                report.mkdir()
                files = []
                embedded_bytes = []
                for index in (1, 2):
                    prefix = 'PhotoData/private' if 'cloudService' in filename else 'mobile/Library/Preferences'
                    source = root / f'copy{index}' / prefix / filename
                    source.parent.mkdir(parents=True)
                    value = {'Property': f'value{index}'}
                    payload = plistlib.dumps({'copy': index}, fmt=plistlib.FMT_BINARY)
                    embedded_bytes.append(payload)
                    value.update({key: payload for key in EMBEDDED.get(module_name, ())})
                    if module_name.startswith('Ph080'):
                        value.update(downloadAndKeepOriginals=index, PhotosSharedLibrarySyncingIsActive=index)
                    if module_name.startswith('Ph083'):
                        value['SetupState'] = index
                    if 'cloudService' in filename:
                        value = [{'timestamp': datetime(2026, 1, index), 'type': f'CPL{index}', 'enabled': index == 1}]
                    with source.open('wb') as fp:
                        plistlib.dump(value, fp)
                    files.append(source)
                context = SimpleNamespace(
                    get_files_found=lambda: [files[0], str(files[0]), files[1]],
                    get_report_folder=lambda: str(report),
                    get_relative_path=lambda path: str(pathlib.Path(path).relative_to(root)),
                )
                with patch.object(module, 'device_info', create=True) as device, \
                     patch.object(module, 'logfunc', create=True), \
                     patch.object(module, 'nd', create=True) as nd:
                    nd.deserialize_plist.side_effect = lambda fp: plistlib.load(fp)
                    headers, rows, sources = parser(context)
                self.assertEqual(sources.splitlines(), list(map(str, files)))
                self.assertEqual(headers[-1], 'Source File')
                expected_per_input = 1 + len(EMBEDDED.get(module_name, ()))
                self.assertEqual(len(rows), 2 * expected_per_input)
                for index, file in enumerate(files, 1):
                    selected = [row for row in rows if row[-1] == str(file.relative_to(root))]
                    self.assertEqual(len(selected), expected_per_input)
                    if 'cloudService' in filename:
                        self.assertEqual(headers[0], ('TimestampUTC', 'datetime'))
                        self.assertEqual(selected[0][:-1], (datetime(2026, 1, index), f'CPL{index}', index == 1))
                    else:
                        self.assertIn(('Property', f'value{index}', str(file.relative_to(root))), selected)
                        for key in EMBEDDED.get(module_name, ()):
                            self.assertIn((key, str({'copy': index}), str(file.relative_to(root))), selected)
                            self.assertEqual((report / f'{key}-{index}.bplist').read_bytes(), embedded_bytes[index - 1])
                expected_device_keys = 2 if module_name.startswith('Ph080') else 1 if module_name.startswith('Ph083') else 0
                self.assertEqual(device.call_count, 2 * expected_device_keys)
                if expected_device_keys:
                    self.assertEqual([call.args[-1] for call in device.call_args_list],
                                     [str(file) for file in files for _ in range(expected_device_keys)])

    def test_empty_match_lists(self):
        for module_name, _ in MODULES:
            with self.subTest(module=module_name):
                module = importlib.import_module('scripts.artifacts.' + module_name)
                parser = getattr(module, next(iter(module.__artifacts_v2__))).__wrapped__
                _, rows, source = parser(SimpleNamespace(get_files_found=lambda: [], get_report_folder=lambda: 'unused'))
                self.assertEqual(rows, [])
                self.assertEqual(source, '')


if __name__ == '__main__':
    unittest.main()
