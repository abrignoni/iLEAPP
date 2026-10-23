"""Build fabricated generic Mixpanel and Crashlytics regression fixtures."""
import fnmatch
import json
import tempfile
import zipfile
from pathlib import Path

from admin.test.scripts.test_crashlytics import write_log, breadcrumb
from admin.test.scripts.test_mixpanel import analytics, metadata
from scripts.artifacts import crashlytics, mixpanel


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


def _crashlytics_sources(root):
    write_log(root, [
        ('Synthetic activity breadcrumb', 0),
        (breadcrumb('_vs', {'_sn': 'Home', '_sc': 'RootController'}), 1700000000125),
        (breadcrumb('select_content', {'item_id': 'synthetic'}), 1700000001000),
    ])
    write_log(root, [('Synthetic unlock', 1700000002000)],
              'com.enchantedcloud.photovault', 'vault')
    write_log(root, [(breadcrumb('screen_view', {'screen_name': 'Vault',
                                              'screen_class': 'VaultController'}), 1700000003000)],
              'com.enchantedcloud.photovaultpro', 'pro')
    write_log(root, [('$A$:{', 1700000004000)], 'com.example.beta', 'beta')


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
        _mixpanel_sources(root)
        _crashlytics_sources(root)
        _write_case(repo, root, crashlytics,
                    'Fabricated multi-app Crashlytics messages and analytics breadcrumbs.')
        _write_case(repo, root, mixpanel,
                    'Fabricated Multi-app Mixpanel queues including absent and conflicting app IDs '
                    'and zero timestamps.')


if __name__ == '__main__':
    main()
