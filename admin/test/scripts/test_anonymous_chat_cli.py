"""End-to-end iLEAPP reports from newly generated metadata; no media payloads.

Run from an iLEAPP checkout. These tests never accept an extraction supplied by
the caller, launch a browser, or open rendered media. All inputs are disposable
synthetic SQLite/plist/JSON files produced by the fixture builder.
"""

import html
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import unittest
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

    def run_report(self, input_type, tenants=1):
        input_path = self.archive if input_type == 'zip' else self.extraction
        if input_type == 'tar':
            input_path = self.root / 'synthetic.tar'
            with tarfile.open(input_path, 'w') as archive:
                for path in sorted(self.extraction.rglob('*')):
                    if path.is_file():
                        archive.add(path, arcname=path.relative_to(self.extraction).as_posix())
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
            'anonymousChat_appInfo': 1, 'anonymousChat_accounts': tenants,
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
            others = {'remote.synthetic'} if tenants == 1 else {'remote.synthetic', 'remote.synthetic.second'}
            self.assertEqual({row[2] for row in rows}, others)
            self.assertEqual([row[3] for row in rows], ['Outgoing'] * tenants + ['Incoming'] * (2 * tenants))
            self.assertTrue(all(not row[4] for row in rows))
            account_rows = db.execute(
                'SELECT account_identifier, evidence FROM anonymouschat_accounts').fetchall()
            evidence_by_account = dict(account_rows)
            self.assertIn('app manifest signed-in username',
                          evidence_by_account['local.synthetic'])
            if tenants == 2:
                self.assertNotIn('app manifest signed-in username',
                                 evidence_by_account['local.synthetic.second'])
            self.assertEqual(db.execute('SELECT COUNT(1) FROM _lava_media_items').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(1) FROM _lava_media_references').fetchone()[0], 0)
            recipients = db.execute('SELECT recipient_username FROM anonymouschat_media '
                                    'WHERE message_id = ?', ('message-3',)).fetchall()
            expected = {'local.synthetic'} if tenants == 1 else {'local.synthetic', 'local.synthetic.second'}
            self.assertEqual({row[0] for row in recipients}, expected)
        finally:
            db.close()
        return report

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
            manifest.commit()
        finally:
            manifest.close()
        return backup

    def test_zip_cli_produces_all_six_lava_artifacts_and_no_media(self):
        self.run_report('zip')

    def test_tar_cli_produces_all_six_lava_artifacts_and_no_media(self):
        self.run_report('tar')

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
        self.run_report('fs', tenants=2)

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
