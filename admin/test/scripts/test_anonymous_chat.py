"""Tests for scripts/artifacts/anonymousChat.py on synthetic data.

These prove the module's own rules (container scoping, the SDWebImage cache-name
link, the account keys it reads), compare folder/ZIP/TAR inputs, and exercise the
iTunes AppDomain fallback using a generated synthetic backup. They cannot prove
what the real app stores: every value comes from build_anonymous_chat_fixture.py.

Run from an iLEAPP checkout:
    python -m unittest discover -s admin/test/scripts -p "test_anonymous_chat*.py"
"""
# pylint: disable=protected-access  # the tests call the module's helpers directly

import csv
import hashlib
import importlib.util
import json
import plistlib
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from contextlib import closing
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))

from scripts.artifacts import anonymousChat as module  # noqa: E402  pylint: disable=wrong-import-position

SPEC = importlib.util.spec_from_file_location('anonymous_chat_fixture_builder',
                                              HERE / 'build_anonymous_chat_fixture.py')
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

SECOND_UUID = '33333333-3333-4333-8333-333333333333'
DECOY_UUID = '44444444-4444-4444-8444-444444444444'


def build_itunes_backup(output_root, data_root):
    """Build an unencrypted synthetic AppDomain backup without container metadata."""
    domain = 'AppDomain-com.anonimchat.app'
    output_root.mkdir(parents=True)
    manifest_rows = []
    for path in sorted(data_root.rglob('*')):
        if not path.is_file() or path.name in (
                '.com.apple.mobile_container_manager.metadata.plist',
                'com.anonimchat.app.plist'):
            continue
        relative = path.relative_to(data_root).as_posix()
        file_id = hashlib.sha1(f'{domain}-{relative}'.encode('utf-8')).hexdigest()
        hashed_path = output_root / file_id[:2] / file_id
        hashed_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, hashed_path)
        metadata = plistlib.dumps({'Birth': 0, 'LastModified': 0})
        manifest_rows.append((file_id, domain, relative, 1, metadata))

    with closing(sqlite3.connect(output_root / 'Manifest.db')) as db:
        db.execute('CREATE TABLE Files (fileID TEXT, domain TEXT, relativePath TEXT, '
                   'flags INTEGER, file BLOB)')
        db.executemany('INSERT INTO Files VALUES (?, ?, ?, ?, ?)', manifest_rows)
        db.commit()
    with (output_root / 'Manifest.plist').open('wb') as handle:
        plistlib.dump({'IsEncrypted': False}, handle)
    return output_root


def input_hashes(path):
    """Hash synthetic test inputs to detect writes by the parser."""
    if path.is_file():
        return {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}
    return {
        file.relative_to(path).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(path.rglob('*')) if file.is_file()
    }


class CacheNameTests(unittest.TestCase):
    def test_md5_of_the_url_plus_its_extension(self):
        # Computed independently with `md5 -s` on macOS.
        self.assertEqual(module._cache_name('https://example.invalid/synthetic/photo.png'),
                         '2e7c9ff3e567104f8251dcb6a6c0c961.png')

    def test_no_extension_gives_the_bare_md5(self):
        self.assertRegex(module._cache_name('https://example.invalid/avatar'), r'^[0-9a-f]{32}$')

    def test_both_sdwebimage_cache_folders_are_read(self):
        data = 'private/var/mobile/Containers/Data/Application/U'
        sources = [f'{data}/Library/Caches/com.hackemist.SDImageCache/default/a.png',
                   f'{data}/Library/Caches/default/com.hackemist.SDWebImageCache.default/b.png',
                   f'{data}/Library/Caches/other/c.png']
        files = module._cache_files([(source, source, data) for source in sources])
        self.assertEqual(sorted(name for _, name in files), ['a.png', 'b.png'])

    def test_only_http_urls_have_a_cache_name(self):
        for value in ('', None, 'photo.png', '/var/mobile/photo.png', 'file:///photo.png'):
            self.assertEqual(module._cache_name(value), '', value)


class AccountKeyTests(unittest.TestCase):
    def test_reads_account_keys_and_named_account_objects(self):
        self.assertEqual(module._usernames({'signedInUsername': 'a'}), {'a'})
        self.assertEqual(module._usernames({'session': json.dumps({'username': 'b'})}), {'b'})

    def test_ignores_usernames_outside_account_keys(self):
        self.assertEqual(module._usernames({'username': 'top-level'}), set())
        self.assertEqual(module._usernames({'contacts': [{'username': 'c'}]}), set())
        self.assertEqual(module._usernames({'session': {'friends': {'username': 'd'}}}), set())

    def test_two_signed_in_names_leave_direction_blank(self):
        row = {'from_username': 'a', 'to_username': 'b', 'sender_name': 'a', 'sender_flag': 0}
        self.assertEqual(module._direction(row, {'a': set()}), 'Outgoing')
        self.assertEqual(module._direction(row, {'a': set(), 'b': set()}), '')
        self.assertEqual(module._direction(row, {}), '')


class ContainerTests(unittest.TestCase):
    def test_container_is_the_folder_through_its_id(self):
        self.assertEqual(
            module._container('private/var/mobile/Containers/Data/Application/U/Library/x'),
            ('private/var/mobile/Containers/Data/Application/U', 'data'))
        self.assertEqual(module._container('wrap/var/containers/Bundle/Application/B/a.app/x'),
                         ('wrap/var/containers/Bundle/Application/B', 'bundle'))
        self.assertEqual(module._container('private/var/mobile/Media/DCIM/x.png'), (None, None))


@unittest.skipUnless((REPO / 'ileapp.py').is_file(), 'Run from an iLEAPP checkout')
class EndToEndTests(unittest.TestCase):
    """One tree, three containers: the fixture's, a second data container of the app
    with one extra message, and a decoy with the same layout under another bundle ID."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='anonymouschat-test-')
        root = Path(cls.temp.name)
        tree = root / 'tree'
        BUILDER.build_fixture(tree)
        data = tree / BUILDER.DATA_ROOT
        second = data.parent / SECOND_UUID
        decoy = data.parent / DECOY_UUID
        shutil.copytree(data, second)
        shutil.rmtree(second / 'Library/Caches/com.hackemist.SDImageCache')
        legacy_cache = second / 'Library/Caches/default/com.hackemist.SDWebImageCache.default'
        legacy_cache.mkdir(parents=True)
        (legacy_cache / BUILDER.cache_name(BUILDER.CACHED_URL)).write_bytes(BUILDER.png(5))
        (legacy_cache / BUILDER.cache_name(BUILDER.UNREFERENCED_URL)).write_bytes(BUILDER.png(6))
        shutil.copytree(data, decoy)
        with closing(sqlite3.connect(second / 'Library/LocalDatabase/anonimchat.db')) as db:
            db.execute("INSERT INTO messages (message_id, conversation_id, message, "
                       "message_time, sender, sender_name) VALUES ('message-4', "
                       "'conversation-1', 'Second container only', 1770000003, 1, "
                       "'remote.synthetic')")
            db.commit()
        # An AppleDouble sidecar, as macOS archivers add beside files with attributes.
        cached = data / BUILDER.SDIMAGECACHE / BUILDER.cache_name(BUILDER.CACHED_URL)
        cached.with_name('._' + cached.name).write_bytes(b'\x00\x05\x16\x07' + bytes(78))
        (decoy / 'Library/Preferences/com.anonimchat.app.plist').unlink()
        with (decoy / '.com.apple.mobile_container_manager.metadata.plist').open('wb') as f:
            plistlib.dump({'MCMMetadataIdentifier': 'com.example.other'}, f)
        members = sorted(path for path in tree.rglob('*') if path.is_file())
        with zipfile.ZipFile(root / 'tree.zip', 'w') as archive:
            for path in members:
                archive.write(path, path.relative_to(tree).as_posix())
        with tarfile.open(root / 'tree.tar', 'w') as archive:
            for path in members:
                archive.add(path, path.relative_to(tree).as_posix())
        itunes = build_itunes_backup(root / 'itunes', data)
        profile = root / 'profile.ilprofile'
        profile.write_text(json.dumps({'leapp': 'ileapp', 'format_version': 1,
                                       'plugins': list(module.__artifacts_v2__)}))
        cls.reports = {}
        cls.output_bases = {}
        cls.input_sources = {'fs': tree, 'zip': root / 'tree.zip',
                             'tar': root / 'tree.tar', 'itunes': itunes}
        cls.input_hashes = {input_type: input_hashes(source)
                            for input_type, source in cls.input_sources.items()}
        for input_type, source in cls.input_sources.items():
            output = root / f'out-{input_type}'
            output.mkdir()
            completed = subprocess.run(
                [sys.executable, 'ileapp.py', '-t', input_type, '-i', str(source),
                 '-o', str(output), '-m', str(profile)],
                cwd=REPO, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                check=False, timeout=600)
            if completed.returncode:
                raise AssertionError(completed.stdout[-2000:] + completed.stderr[-2000:])
            output_base = next(output.glob('iLEAPP_Output_*'))
            cls.output_bases[input_type] = output_base
            cls.reports[input_type] = output_base / '_TSV Exports'

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def rows(self, input_type, name):
        path = self.reports[input_type] / f'Anonymous Chat & Fun - {name}.tsv'
        if not path.exists():
            return []
        with path.open(newline='', encoding='utf-8-sig') as handle:
            return list(csv.DictReader(handle, delimiter='\t'))

    def test_folder_zip_and_tar_give_the_same_rows(self):
        for name in ('Application Info', 'Accounts', 'Conversations', 'Messages',
                     'Blocked Users', 'Media'):
            counts = {t: len(self.rows(t, name)) for t in ('fs', 'zip', 'tar')}
            self.assertEqual(len(set(counts.values())), 1, (name, counts))

    def test_itunes_backup_rows_are_limited_to_its_app_domain(self):
        counts = {name: len(self.rows('itunes', name)) for name in (
            'Application Info', 'Accounts', 'Conversations', 'Messages',
            'Blocked Users', 'Media')}
        self.assertEqual(counts, {
            'Application Info': 1, 'Accounts': 2, 'Conversations': 1,
            'Messages': 3, 'Blocked Users': 1, 'Media': 4,
        })
        info = self.rows('itunes', 'Application Info')
        self.assertEqual(info[0]['Container ID'], 'com.anonimchat.app')
        self.assertEqual(info[0]['Identified By'], 'iTunes backup AppDomain')

    def test_source_evidence_is_unchanged(self):
        for input_type, source in self.input_sources.items():
            self.assertEqual(input_hashes(source), self.input_hashes[input_type], input_type)

    def test_lava_exports_the_conversation_view(self):
        for input_type in ('fs', 'itunes'):
            lava_path = self.output_bases[input_type] / '_lava_data.lava'
            self.assertTrue(lava_path.is_file(), input_type)
            with lava_path.open(encoding='utf-8') as handle:
                lava = json.load(handle)
            messages = [artifact for category in lava['artifacts'].values()
                        for artifact in category
                        if artifact.get('name') == 'Anonymous Chat & Fun - Messages']
            self.assertEqual(len(messages), 1, input_type)
            view = messages[0]['data_views']['conversation']
            self.assertEqual(view['conversationDiscriminatorColumn'], 'conversation_key')
            self.assertEqual(view['textColumn'], 'message_text')
            self.assertEqual(view['mediaColumn'], 'media')
            self.assertEqual(view['directionSentValue'], 'Outgoing')

    def test_two_app_containers_count_once_each_and_the_decoy_adds_nothing(self):
        for input_type in ('fs', 'zip', 'tar'):
            messages = self.rows(input_type, 'Messages')
            self.assertEqual(len(messages), 3 + 4, input_type)
            self.assertEqual(sum('message-4' == row['Message ID'] for row in messages), 1)
            self.assertFalse(any(DECOY_UUID in row['Source'] for row in messages))
            info = self.rows(input_type, 'Application Info')
            self.assertEqual(sorted(row['Container ID'] for row in info),
                             sorted([BUILDER.BUNDLE_UUID, BUILDER.DATA_UUID, SECOND_UUID]))
        messages = self.rows('itunes', 'Messages')
        self.assertEqual(len(messages), 3)
        self.assertFalse(any(DECOY_UUID in row['Source'] for row in messages))

    def test_cached_image_links_inside_its_own_container_only(self):
        cached = BUILDER.cache_name(BUILDER.CACHED_URL)
        for input_type in self.reports:
            media = self.rows(input_type, 'Media')
            linked = [row for row in media if row['Record Type'] == 'Message Media'
                      and row['Media']]
            expected_links = 1 if input_type == 'itunes' else 2
            self.assertEqual(len(linked), expected_links, input_type)
            for row in linked:
                self.assertTrue(row['Cache File'].endswith('/' + cached))
                self.assertEqual(row['Cache File'].split('/Library/')[0],
                                 row['Source Database'].split('/Library/')[0])
            if input_type != 'itunes':
                linked_paths = ' '.join(row['Cache File'] for row in linked)
                self.assertIn('com.hackemist.SDImageCache', linked_paths)
                self.assertIn('com.hackemist.SDWebImageCache', linked_paths)
            missing = [row for row in media if row['Media URL or Name'] == BUILDER.UNCACHED_URL]
            self.assertTrue(missing and not any(row['Media'] for row in missing))
            unreferenced = [row for row in media if row['Record Type'] == 'Cached Image']
            self.assertEqual(len(unreferenced), expected_links)
            self.assertTrue(all(row['Media'] for row in unreferenced))
            names = ' '.join(row['Cache File'] for row in media)
            self.assertNotIn('decoy.png', names)
            self.assertNotIn('icon.png', names)

    def test_direction_needs_the_signed_in_username(self):
        for input_type in self.reports:
            directions = {row['Message ID']: row['Direction']
                          for row in self.rows(input_type, 'Messages')
                          if DECOY_UUID not in row['Source']}
            self.assertEqual(directions['message-1'], 'Outgoing')
            self.assertEqual(directions['message-2'], 'Incoming')


if __name__ == '__main__':
    unittest.main()
