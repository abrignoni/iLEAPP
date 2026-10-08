"""End-to-end iLEAPP reports from newly generated metadata; no media payloads.

Run from an iLEAPP checkout. These tests never accept an extraction supplied by
the caller, launch a browser, or open rendered media. All inputs are disposable
synthetic SQLite/plist/JSON files produced by the fixture builder.
"""

import gzip
import hashlib
import html
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
from pathlib import Path

from test_anonymous_chat_fixture import BUILDER
from scripts.artifacts import anonymousChat as module


@unittest.skipUnless((Path.cwd() / 'ileapp.py').is_file(), 'Run from an iLEAPP checkout')
class AnonymousChatCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-cli-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.extraction = self.root / 'extraction'
        self.archive = BUILDER.build_fixture(self.extraction)
        self.profile = self.root / 'synthetic.ilprofile'
        self.profile.write_text(json.dumps({
            'leapp': 'ileapp', 'format_version': 1,
            'plugins': list(module.__artifacts_v2__),
        }), encoding='utf-8')

    def run_report(self, input_type, tenants=1, confirmed_account=True,
                   duplicate_roots=False, wrapped=False, source_roots=None):
        input_path = self.archive if input_type == 'zip' else self.extraction
        if input_type == 'zip' and wrapped:
            input_path = self.root / 'synthetic-wrapped.zip'
            with zipfile.ZipFile(input_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(self.extraction.rglob('*')):
                    if path.is_file():
                        archive.write(path, 'iphone-backup/' +
                                      path.relative_to(self.extraction).as_posix())
        if input_type == 'tar':
            input_path = self.root / 'synthetic.tar'
            with tarfile.open(input_path, 'w') as archive:
                for path in sorted(self.extraction.rglob('*')):
                    if path.is_file():
                        relative = path.relative_to(self.extraction).as_posix()
                        archive.add(path, arcname=('iphone-backup/' + relative
                                                   if wrapped else relative))
        if input_type == 'itunes':
            input_path = self.build_itunes_backup()
        completed = subprocess.run([
            sys.executable, 'ileapp.py', '-t', input_type,
            '-i', str(input_path),
            '-o', str(self.root), '-m', str(self.profile), '-tz', 'UTC',
            '--custom_output_folder', 'synthetic-report',
        ], capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=60, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = self.root / 'synthetic-report'
        manifest = json.loads((report / '_lava_data.lava').read_text(encoding='utf-8'))
        self.assertEqual(manifest['processing_status'], 'Complete')
        artifacts = manifest['artifacts']['Anonymous Chat & Fun']
        self.assertEqual({a['artifact_key']: a['record_count'] for a in artifacts}, {
            'anonymousChat_appInfo': 2 if duplicate_roots else 1,
            'anonymousChat_accounts': tenants,
            'anonymousChat_conversations': tenants, 'anonymousChat_messages': 3 * tenants,
            'anonymousChat_blocked': tenants, 'anonymousChat_media': 3 * tenants,
        })
        messages = next(a for a in artifacts if a['artifact_key'] == 'anonymousChat_messages')
        view = messages['data_views']['conversation']
        self.assertEqual(view['conversationDiscriminatorColumn'], 'conversation_key')
        self.assertEqual(view['conversationLabelColumn'], 'other_party')
        self.assertEqual(view['mediaColumn'], 'media')
        for artifact in artifacts:
            self.assertTrue(artifact['source_path'])
            self.assertNotIn(str(self.root), artifact['source_path'])
        db = sqlite3.connect((report / '_lava_artifacts.db').as_uri() + '?mode=ro', uri=True)
        try:
            rows = db.execute('SELECT message_id, conversation_key, other_party, direction, media '
                              'FROM anonymouschat_messages ORDER BY message_id').fetchall()
            self.assertEqual([row[0] for row in rows],
                             sorted(['message-1', 'message-2', 'message-3'] * tenants))
            self.assertEqual(len({row[1] for row in rows}), tenants)
            others = ({'remote.synthetic'} if duplicate_roots else
                      {'remote.synthetic'} if tenants == 1 else
                      {'remote.synthetic', 'remote.synthetic.second'})
            if not confirmed_account:
                others = {'Participants: local.synthetic, remote.synthetic'}
            self.assertEqual({row[2] for row in rows}, others,
                             completed.stdout + completed.stderr)
            expected_directions = (['Outgoing'] * tenants + ['Incoming'] * (2 * tenants)
                                   if confirmed_account else [''] * (3 * tenants))
            self.assertEqual([row[3] for row in rows], expected_directions)
            self.assertTrue(all(not row[4] for row in rows))
            account_rows = db.execute(
                'SELECT account_identifier, evidence, source '
                'FROM anonymouschat_accounts').fetchall()
            evidence_by_account = {row[0]: row[1] for row in account_rows}
            self.assertEqual('app manifest signed-in username' in
                             evidence_by_account['local.synthetic'], confirmed_account)
            if confirmed_account:
                account_evidence = evidence_by_account['local.synthetic'].replace('\\', '/')
                self.assertIn('AsyncStorage evidence source(s):',
                              account_evidence)
                self.assertIn('RCTAsyncLocalStorage_V1/manifest.json',
                              account_evidence)
            if tenants == 2 and not duplicate_roots:
                self.assertIn('app manifest signed-in username',
                              evidence_by_account['local.synthetic.second'])
            if duplicate_roots:
                self.assertEqual(len(account_rows), 2)
                self.assertEqual({row[0] for row in account_rows}, {'local.synthetic'})
                for _account, evidence, source in account_rows:
                    roots = {root for root in ('extraction-a', 'extraction-b')
                             if root in evidence or root in source}
                    self.assertEqual(len(roots), 1)
            if source_roots is not None:
                message_sources = db.execute(
                    'SELECT DISTINCT source FROM anonymouschat_messages').fetchall()
                self.assertEqual(len(message_sources), tenants)
                self.assertEqual({root for (source,) in message_sources
                                  for root in source_roots if root in source},
                                 set(source_roots))
                media_sources = db.execute(
                    'SELECT DISTINCT source FROM anonymouschat_media '
                    'WHERE message_id = ?', ('message-3',)).fetchall()
                self.assertEqual(len(media_sources), tenants)
                self.assertEqual({root for (source,) in media_sources
                                  for root in source_roots if root in source},
                                 set(source_roots))
            self.assertEqual(db.execute('SELECT COUNT(1) FROM _lava_media_items').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(1) FROM _lava_media_references').fetchone()[0], 0)
            recipients = db.execute('SELECT recipient_username FROM anonymouschat_media '
                                    'WHERE message_id = ?', ('message-3',)).fetchall()
            expected = ({'local.synthetic'} if duplicate_roots or tenants == 1 else
                        {'local.synthetic', 'local.synthetic.second'})
            if not confirmed_account:
                expected = {''}
            self.assertEqual({row[0] for row in recipients}, expected)
        finally:
            db.close()
        return report

    def make_duplicate_extraction_roots(self, second_is_target=True):
        """Put the same synthetic UUIDs under distinct source-root prefixes."""
        first = self.extraction / 'extraction-a'
        second = self.extraction / 'extraction-b'
        first.mkdir()
        shutil.move(str(self.extraction / 'private'), str(first / 'private'))
        shutil.copytree(first / 'private', second / 'private')
        for root, target in ((first, True), (second, second_is_target)):
            data = root / BUILDER.DATA_ROOT
            bundle = root / BUILDER.BUNDLE_ROOT
            group = (root / 'private/var/mobile/Containers/Shared/AppGroup' /
                     '33333333-3333-4333-8333-333333333333')
            group.mkdir(parents=True)
            (group / '.com.apple.mobile_container_manager.metadata.plist').write_bytes(
                plistlib.dumps({'MCMMetadataIdentifier':
                                'group.com.anonimchat.app.shared' if target else
                                'group.com.other.app'}))
            if target:
                continue
            (data / '.com.apple.mobile_container_manager.metadata.plist').write_bytes(
                plistlib.dumps({'MCMMetadataIdentifier': 'com.other.app'}))
            (data / 'Library/Preferences/com.anonimchat.app.plist').unlink()
            bundle_metadata = bundle / '.com.apple.mobile_container_manager.metadata.plist'
            bundle_metadata.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': 'com.other.app'}))
            info_path = bundle / 'AnonimChat.app/Info.plist'
            info = plistlib.loads(info_path.read_bytes())
            info['CFBundleIdentifier'] = 'com.other.app'
            info_path.write_bytes(plistlib.dumps(info))
            store_path = bundle / 'iTunesMetadata.plist'
            store = plistlib.loads(store_path.read_bytes())
            store['softwareVersionBundleId'] = 'com.other.app'
            store_path.write_bytes(plistlib.dumps(store))

    def build_itunes_backup(self):
        """Build an iTunes-style backup from the synthetic data container."""
        backup = self.root / 'itunes-backup'
        backup.mkdir()
        data_root = self.extraction / BUILDER.DATA_ROOT
        manifest = sqlite3.connect(backup / 'Manifest.db')
        try:
            manifest.execute('''
                CREATE TABLE Files (
                    fileID TEXT, domain TEXT, relativePath TEXT,
                    flags INTEGER, file BLOB
                )
            ''')
            domain = 'AppDomain-com.anonimchat.app'
            for path in sorted(data_root.rglob('*')):
                if not path.is_file():
                    continue
                relative = path.relative_to(data_root).as_posix()
                file_id = hashlib.sha1(
                    f'{domain}-{relative}'.encode('utf-8')).hexdigest()
                destination = backup / file_id[:2] / file_id
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(path.read_bytes())
                manifest.execute(
                    'INSERT INTO Files VALUES (?, ?, ?, ?, ?)',
                    (file_id, domain, relative, 1, b''))
            photos = (self.extraction / 'private/var/mobile/Media/PhotoData/'
                      'Photos.sqlite')
            domain = 'CameraRollDomain'
            relative = 'Media/PhotoData/Photos.sqlite'
            file_id = hashlib.sha1(f'{domain}-{relative}'.encode('utf-8')).hexdigest()
            destination = backup / file_id[:2] / file_id
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(photos.read_bytes())
            manifest.execute('INSERT INTO Files VALUES (?, ?, ?, ?, ?)',
                             (file_id, domain, relative, 1, b''))
            manifest.commit()
        finally:
            manifest.close()
        return backup

    def test_zip_cli_produces_all_six_lava_artifacts_and_no_media(self):
        self.run_report('zip')

    def test_tar_cli_produces_all_six_lava_artifacts_and_no_media(self):
        self.run_report('tar')

    def test_zip_wrapper_cli_preserves_evidence_relative_paths(self):
        self.run_report('zip', wrapped=True)

    def test_tar_wrapper_cli_preserves_evidence_relative_paths(self):
        self.run_report('tar', wrapped=True)

    def test_raw_cli_completes_on_available_non_ios_image_fixture(self):
        fixture = (Path(__file__).resolve().parents[1] / 'data' / 'raw_images' /
                   'ntfs-fixture.img.gz')
        image = self.root / 'ntfs-fixture.img'
        with gzip.open(fixture, 'rb') as compressed, image.open('wb') as output:
            shutil.copyfileobj(compressed, output)
        completed = subprocess.run([
            sys.executable, 'ileapp.py', '-t', 'raw', '-i', str(image),
            '-o', str(self.root), '-m', str(self.profile), '-tz', 'UTC',
            '--custom_output_folder', 'synthetic-raw-report',
        ], capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=90, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        manifest = json.loads((self.root / 'synthetic-raw-report' /
                               '_lava_data.lava').read_text(encoding='utf-8'))
        self.assertEqual(manifest['processing_status'], 'Complete')
        # This public NTFS image has no iOS/app evidence, so iLEAPP correctly
        # does not emit an Anonymous Chat artifact group for it.
        self.assertNotIn('Anonymous Chat & Fun', manifest['artifacts'])

    def test_itunes_cli_discovers_bundle_id_data_domain(self):
        self.run_report('itunes')

    def test_two_app_containers_do_not_merge_reused_conversation_ids(self):
        second = self.extraction / BUILDER.DATA_ROOT.parent / '33333333-3333-4333-8333-333333333333'
        shutil.copytree(self.extraction / BUILDER.DATA_ROOT, second)
        db = sqlite3.connect(second / 'Library/LocalDatabase/anonimchat.db')
        try:
            db.execute('UPDATE conversations SET from_username = ?, to_username = ?',
                       ('local.synthetic.second', 'remote.synthetic.second'))
            db.execute('UPDATE messages SET sender_name = CASE sender WHEN 0 THEN ? ELSE ? END',
                       ('local.synthetic.second', 'remote.synthetic.second'))
            db.commit()
        finally:
            db.close()
        manifest = (second / 'Library/Application Support/com.anonimchat.app/'
                    'RCTAsyncLocalStorage_V1/manifest.json')
        manifest.write_bytes(json.dumps({'signedInUsername': 'local.synthetic.second'}).encode())
        self.run_report('fs', tenants=2)

    def test_unverified_duplicate_uuid_in_second_root_is_excluded_by_cli(self):
        self.make_duplicate_extraction_roots(second_is_target=False)
        self.run_report('fs', source_roots=['extraction-a'])

    def test_two_valid_duplicate_uuid_roots_remain_separate_in_cli(self):
        self.make_duplicate_extraction_roots(second_is_target=True)
        self.run_report('fs', tenants=2, duplicate_roots=True,
                        source_roots=['extraction-a', 'extraction-b'])

    def test_directory_missing_manifest_leaves_direction_unconfirmed(self):
        manifest = (self.extraction / BUILDER.DATA_ROOT /
                    'Library/Application Support/com.anonimchat.app/'
                    'RCTAsyncLocalStorage_V1/manifest.json')
        manifest.unlink()
        self.run_report('fs', confirmed_account=False)

    def test_directory_conflicting_manifest_leaves_direction_unconfirmed(self):
        manifest = (self.extraction / BUILDER.DATA_ROOT /
                    'Library/Application Support/com.anonimchat.app/'
                    'RCTAsyncLocalStorage_V1/manifest.json')
        manifest.write_bytes(json.dumps({'signedInUsername': 'unrelated.synthetic'}).encode())
        self.run_report('fs', confirmed_account=False)

    def test_legacy_documents_manifest_and_md5_sidecar_confirm_account(self):
        data_root = self.extraction / BUILDER.DATA_ROOT
        current = (data_root / 'Library/Application Support/com.anonimchat.app/'
                   'RCTAsyncLocalStorage_V1/manifest.json')
        current.unlink()
        legacy_dir = data_root / 'Documents/RCTAsyncLocalStorage_V1'
        legacy_dir.mkdir(parents=True)
        key = 'signedInUsername'
        digest = hashlib.md5(key.encode('utf-8'), usedforsecurity=False).hexdigest()
        (legacy_dir / 'manifest.json').write_text(
            json.dumps({key: None}), encoding='utf-8')
        (legacy_dir / digest).write_text('local.synthetic', encoding='utf-8')
        self.run_report('tar')

    def test_directory_cli_escapes_hostile_metadata_in_html(self):
        payload = '<img src="https://example.invalid/never-fetched" onerror="alert(1)">'
        db = sqlite3.connect(self.extraction / BUILDER.DATA_ROOT / 'Library/LocalDatabase/anonimchat.db')
        try:
            db.execute('UPDATE messages SET message = ? WHERE message_id = ?', (payload, 'message-1'))
            db.commit()
        finally:
            db.close()
        report = self.run_report('fs')
        page = (report / '_HTML/Anonymous_Chat_&_Fun_-_Messages.html').read_text(encoding='utf-8')
        self.assertNotIn(payload, page)
        self.assertIn(html.escape(payload), page)


if __name__ == '__main__':
    unittest.main()
