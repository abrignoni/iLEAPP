"""Build fabricated Private Photo Vault and Mixpanel regression fixtures."""
import fnmatch
import json
import sqlite3
import tempfile
import zipfile
from pathlib import Path

from admin.test.scripts.test_private_photo_vault_ecd import store
from admin.test.scripts.test_mixpanel import analytics, metadata
from scripts.artifacts import privatePhotoVaultEcd, mixpanel


def _ecd_sources(root):
    for container in ('alpha', 'beta'):
        path = store(root, container)
        with sqlite3.connect(path) as db:
            db.execute('ALTER TABLE ecdPersistentAlbum ADD COLUMN albumType')
            db.execute('ALTER TABLE ecdPersistentMediaItem ADD COLUMN fileType')
            db.execute('UPDATE ecdPersistentAlbum SET albumType=7')
            db.execute('UPDATE ecdPersistentMediaItem SET fileType=2')
            if container == 'alpha':
                db.execute('UPDATE ecdPersistentAlbum SET createdDate=0')
                db.execute('UPDATE ecdPersistentMediaItem SET createdDate=0,modifiedDate=0 '
                           'WHERE __objectid=1')


def _mixpanel_sources(root):
    metadata(root, 'com.example.alpha', 'alpha')
    metadata(root, 'com.example.beta', 'beta')
    analytics(root, [
        {'event': 'synthetic_start', 'properties': {'time': 1700000000.125,
            'bundleId': 'com.example.alpha', 'mp_lib': 'iphone', '$lib_version': 'synthetic'}},
        {'event': 'synthetic_zero', 'properties': {'time': 0, 'bundleId': 'com.example.alpha'}},
        {'event': 'synthetic_session', 'properties': {'time': 1700000000125,
            '$ae_session_length': 12, 'sessionParams': {'bundleId': 'com.example.alpha',
                'itemsViewed': 8, 'albumsViewed': 0, 'timeSpent': {'thumbnails': 4.5, 'gallery': 0}}}},
        {'event': 'synthetic_conflict', 'properties': {'time': 1700000001,
            'bundleId': 'com.example.alpha', 'sessionParams': {'bundleId': 'com.example.beta'}}},
    ], 'alpha')
    analytics(root, [
        {'event': 'synthetic_metadata_identity', 'properties': {'time': 1700000002}},
        {'event': 'synthetic_explicit_other', 'properties': {'time': 1700000003,
            'bundleId': 'com.example.other'}},
    ], 'beta')
    analytics(root, [{'event': 'synthetic_unknown', 'properties': {'time': 1700000004}}], 'unknown')


def _diagnostic_source(root):
    log = root / ('private/var/mobile/Containers/Data/Application/alpha/Library/Caches/'
                  'com.crashlytics.data/com.enchantedcloud.photovault/v5/report/log_a.clsrecord')
    log.parent.mkdir(parents=True)
    message = 'Synthetic activity breadcrumb'.encode().hex()
    log.write_text('\n'.join(json.dumps({'log': {'msg': message, 'time': stamp}})
                             for stamp in (0, 1700000000125)), encoding='utf-8')


def _write_case(repo, root, parser, description):
    module = parser.__name__.rsplit('.', 1)[-1]
    destination = repo / 'admin/test/cases/data' / module
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, meta in parser.__artifacts_v2__.items():
        paths = sorted(p for p in root.rglob('*') if p.is_file() and any(
            fnmatch.fnmatchcase(str(p), pattern) for pattern in meta['paths']))
        target = destination / f'testdata.{module}.{name}.synthetic.zip'
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                entry = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2000, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, path.read_bytes())
        artifacts[name] = {'search_patterns': list(meta['paths']), 'file_count': len(paths)}
    case = {'synthetic': {'description': description, 'maker': '@CyberMike81',
                         'os_name': 'iOS', 'os_version': 'synthetic',
                         'image_info': {'os_name': 'iOS', 'os_version': 'synthetic'},
                         'artifacts': artifacts}}
    (repo / f'admin/test/cases/testdata.{module}.json').write_text(
        json.dumps(case, indent=2) + '\n', encoding='utf-8')


def main(destination_repo=None):
    repo = Path(destination_repo) if destination_repo is not None else Path(__file__).resolve().parents[4]
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _ecd_sources(root)
        _mixpanel_sources(root)
        _diagnostic_source(root)
        _write_case(repo, root, privatePhotoVaultEcd,
                    'Fabricated ECD album/media and Crashlytics records with zero timestamps.')
        _write_case(repo, root, mixpanel,
                    'Fabricated Multi-app Mixpanel queues including absent and conflicting app IDs '
                    'and zero timestamps.')


if __name__ == '__main__':
    main()
