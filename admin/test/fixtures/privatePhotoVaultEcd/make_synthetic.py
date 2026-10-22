"""Build only fabricated PPV records for the committed regression snapshots."""
import fnmatch
import json
import plistlib
import tempfile
import zipfile
from pathlib import Path

from admin.test.scripts.test_private_photo_vault_ecd import store, analytics
from scripts.artifacts import privatePhotoVaultEcd as parser


def main():
    repo = Path(__file__).resolve().parents[4]
    module = 'privatePhotoVaultEcd'
    destination = repo / 'admin/test/cases/data' / module
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        store(root)
        store(root, 'beta')
        for container, bundle in (('alpha', 'com.enchantedcloud.photovault'),
                                  ('beta', 'com.enchantedcloud.photovault'),
                                  ('foreign', 'com.example.other')):
            marker = root/'private/var/mobile/Containers/Data/Application'/container/'.com.apple.mobile_container_manager.metadata.plist'
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': bundle}))
        analytics(root, [{'event': 'Synthetic conflicting container', 'properties': {
            'bundleId': 'com.enchantedcloud.photovault', 'time': 1700000000}}], 'foreign')
        analytics(root, [
            {'event': 'app_unlock', 'properties': {'time': 1700000000.125,
                'bundleId': 'com.enchantedcloud.photovault'}},
            {'event': '$ae_session', 'properties': {'time': 1700000000125,
                '$ae_session_length': 12, 'sessionParams': {'bundleId': 'com.enchantedcloud.photovault',
                'itemsViewed': 8, 'albumsViewed': 0, 'timeSpent': {'gallery': 0, 'thumbnails': 4.5}}}},
            {'event': 'Synthetic oversized time', 'properties': {'time': 10**399,
                'bundleId': 'com.enchantedcloud.photovault'}},
            {'event': 'Synthetic after oversized time', 'properties': {'time': 1700000001,
                'bundleId': 'com.enchantedcloud.photovault'}},
            {'event': 'Synthetic unlabelled event', 'properties': {'time': 1700000002}},
        ])
        log = root / 'Library/Caches/com.crashlytics.data/com.enchantedcloud.photovault/v5/report/log_a.clsrecord'
        log.parent.mkdir(parents=True)
        log.write_text('\n'.join(json.dumps({'log': {'msg': 'Synthetic unlock'.encode().hex(), 'time': stamp}})
                                 for stamp in (1700000000125, 10**399, 1700000001000)) + '\n')
        for name, meta in parser.__artifacts_v2__.items():
            paths = [p for p in root.rglob('*') if p.is_file() and any(
                fnmatch.fnmatchcase('root/' + p.relative_to(root).as_posix(), pat) for pat in meta['paths'])]
            with zipfile.ZipFile(destination / f'testdata.{module}.{name}.synthetic.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                for p in sorted(paths):
                    entry = zipfile.ZipInfo(p.relative_to(root).as_posix(), (2024, 1, 1, 0, 0, 0))
                    z.writestr(entry, p.read_bytes())
            artifacts[name] = {'search_patterns': list(meta['paths']), 'file_count': len(paths)}
    case = {'synthetic': {'description': 'Fabricated multi-container ECD, analytics and diagnostic records.',
                         'maker': '@CyberMike81', 'os_name': 'iOS', 'os_version': 'synthetic',
                         'image_info': {'os_name': 'iOS', 'os_version': 'synthetic'},
                         'artifacts': artifacts}}
    (repo / f'admin/test/cases/testdata.{module}.json').write_text(json.dumps(case, indent=2) + '\n')


if __name__ == '__main__':
    main()
