"""Regression tests using invented metadata only; never read a media payload.

Run from an iLEAPP checkout with this file in admin/test/scripts. All filesystem
media entries are dictionaries; signature and Media Manager calls are mocked.
SQLite tests create fresh disposable databases, never take a casework input.
"""

# These tests intentionally exercise private correlation helpers and data builders.
# pylint: disable=protected-access

import fnmatch
import hashlib
import json
import plistlib
import sqlite3
import stat
import tempfile
import unittest
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts.artifacts import anonymousChat as module
from scripts.search_files import FileSeekerItunes


UUID_A = '11111111-1111-4111-8111-111111111111'
UUID_B = '33333333-3333-4333-8333-333333333333'
DATA_A = f'private/var/mobile/Containers/Data/Application/{UUID_A}'
DATA_B = f'private/var/mobile/Containers/Data/Application/{UUID_B}'
DB_A = DATA_A + '/Library/LocalDatabase/anonimchat.db'
DB_B = DATA_B + '/Library/LocalDatabase/anonimchat.db'
WHEN = datetime(2030, 1, 1, tzinfo=timezone.utc)
URL = 'https://example.invalid/synthetic/image.jpg'


class MetadataContext:
    def __init__(self, files=()):
        self.files = list(files)
        self.seeker = Mock()
        self.seeker.search.return_value = []

    def get_files_found(self):
        return self.files

    def get_seeker(self):
        return self.seeker

    def get_artifact_name(self):
        return 'Anonymous Chat & Fun - Synthetic Regression'

    def get_relative_path(self, path):
        return str(path)


def reference(**values):
    result = dict.fromkeys((
        'media_timestamp', 'media_id', 'duration', 'media_origin', 'media_show'), '')
    result.update(
        kind='Message Attachment Reference', reference=URL, source=DB_A,
        message_timestamp=WHEN, conversation_id='chat-1', message_id='message-1',
        message_uuid='synthetic-uuid-1', direction='Incoming',
        sender='remote.synthetic', recipient='local.synthetic',
        filename='image.jpg', mime='image/jpeg', size=1234)
    result.update(values)
    return result


def entry(path=None, **values):
    result = dict(path=path or DATA_A + '/Library/Caches/image.jpg',
                  size=1234, created='', modified='', modified_at=WHEN,
                  accessed='', kind='invented metadata')
    result.update(values)
    return result


def classified(path=None, category='Image', **values):
    return dict(entry=entry(path, **values), category=category)


def message(**values):
    result = dict(message_id='message-1', conversation_id='chat-1',
                  msg_uuid='synthetic-uuid-1', message_time=int(WHEN.timestamp()),
                  sender_flag=1, sender_name='remote.synthetic',
                  from_username='local.synthetic', to_username='remote.synthetic')
    result.update(values)
    return result


def report_dicts(result):
    headers, rows, source = result
    names = [header[0] if isinstance(header, tuple) else header for header in headers]
    return [dict(zip(names, row)) for row in rows], source


class AnonymousChatHardeningTests(unittest.TestCase):
    def setUp(self):
        # Fail closed if a future refactor attempts to inspect real media.
        self.guard = ExitStack()
        self.addCleanup(self.guard.close)
        self.signature = self.guard.enter_context(patch.object(
            module, '_signature_from_entry',
            side_effect=AssertionError('Media reads forbidden in metadata tests')))
        self.checkin = self.guard.enter_context(patch.object(
            module, 'check_in_media',
            side_effect=AssertionError('Media processing forbidden in metadata tests')))

    def media_rows(self, entries, references):
        with patch.object(module, '_target_containers',
                          return_value=(set(), {UUID_A, UUID_B}, set(), {})), \
                patch.object(module, '_attachment_references', return_value=references), \
                patch.object(module, '_photos_asset_paths', return_value={}), \
                patch.object(module, '_iter_source_entries', return_value=entries), \
                patch.object(module, '_media_reference',
                             side_effect=lambda _ctx, file, *_: 'mock:' + file['path']):
            return module._media_rows([DB_A, DB_B], MetadataContext())

    def test_same_size_and_timestamp_decoy_is_not_a_message_match(self):
        entries = [entry(DATA_A + '/Library/Caches/decoy.jpg')]
        rows = self.media_rows(entries, [reference(reference=URL)])
        self.assertFalse(any(row.get('media_ref') for row in rows))
        self.assertIn('no stored app-to-file relationship', rows[-1]['correlation'])
        self.assertEqual(rows[-1]['filesystem_present'], 'No')

    def test_remote_url_basename_is_not_a_local_file_link(self):
        entries = [entry(DATA_A + '/Library/Caches/image.jpg'),
                   entry(DATA_A + '/synthetic/image.jpg')]
        rows = self.media_rows(entries, [reference(reference=URL)])
        self.assertFalse(any(row.get('media_ref') for row in rows))
        self.assertTrue(all('no stored app-to-file relationship' in row['correlation']
                            for row in rows if row['kind'] == 'Filesystem Media'))

    def test_message_filename_alone_is_not_a_match(self):
        matches, blocked = module._direct_media_matches(
            [classified()], [reference()], filenames_only=True)
        self.assertFalse(blocked)
        self.assertEqual(matches, {})

    def test_exact_path_disambiguates_same_basename(self):
        target = DATA_A + '/Library/Caches/a/image.jpg'
        rows = self.media_rows([entry(target), entry(DATA_A + '/Library/Caches/b/image.jpg')],
                               [reference(reference=target)])
        linked = [row for row in rows if row.get('media_ref')]
        self.assertEqual(len(linked), 1)
        self.assertEqual(linked[0]['filesystem_path'], target)
        self.assertTrue(linked[0]['correlation'].startswith('Direct:'))

    def test_distinct_urls_with_same_basename_are_not_arbitrarily_assigned(self):
        refs = [reference(), reference(reference='https://example.invalid/other/image.jpg',
                                       message_id='message-2')]
        rows = self.media_rows([entry()], refs)
        self.assertFalse(any(row.get('media_ref') for row in rows))

    def test_filename_cannot_reuse_a_file_owned_by_conflicting_exact_reference(self):
        target = entry()['path']
        refs = [reference(reference=target), reference(message_id='message-2')]
        rows = self.media_rows([entry()], refs)
        linked = [row for row in rows if row.get('media_ref')]
        self.assertEqual([row['message_id'] for row in linked], ['message-1'])

    def test_conflicting_size_or_category_blocks_filename_and_timestamp(self):
        for values in ({'size': 9999}, {'mime': 'video/mp4'}):
            with self.subTest(values=values):
                rows = self.media_rows([entry()],
                                       [reference(reference=entry()['path'], **values)])
                self.assertFalse(any(row.get('media_ref') for row in rows))
                self.assertIn('contradictory', rows[-1]['correlation'])

    def test_filename_comparison_preserves_ios_case(self):
        matched, _method = module._entry_matches_reference(entry()['path'], 'IMAGE.JPG')
        self.assertFalse(matched)

    def test_identical_filenames_are_scoped_to_the_source_container(self):
        rows = self.media_rows([entry(), entry(DATA_B + '/Library/Caches/image.jpg')],
                               [reference(reference=DATA_A + '/Library/Caches/image.jpg')])
        self.assertEqual([row['filesystem_path'] for row in rows if row.get('media_ref')],
                         [entry()['path']])

    def test_data_attachment_cannot_match_same_name_in_bundle_container(self):
        bundle_path = 'private/var/containers/Bundle/Application/' + UUID_A + '/AnonimChat.app/image.jpg'
        rows = self.media_rows([entry(bundle_path)], [reference()])
        self.assertFalse(any(row.get('media_ref') for row in rows))

    def test_repeated_url_retains_separate_typed_message_associations(self):
        target = DATA_A + '/Library/Caches/image.jpg'
        refs = [reference(reference=target), reference(reference=target, message_id='message-2',
                                       message_timestamp=WHEN + timedelta(seconds=30))]
        rows = self.media_rows([entry()], refs)
        linked = [row for row in rows if row.get('media_ref')]
        self.assertEqual([row['message_id'] for row in linked], ['message-1', 'message-2'])
        self.assertEqual([row['message_timestamp'] for row in linked],
                         [WHEN, WHEN + timedelta(seconds=30)])
        self.assertTrue(all(row['recipient'] == 'local.synthetic' for row in linked))

    def test_equal_ranked_local_files_do_not_select_first(self):
        key = module._message_key(DB_A, 'message-1', 'chat-1', 'synthetic-uuid-1')
        rows = [dict(kind='Filesystem Media', media_ref=ref, _message_key=key,
                     correlation='Direct: stored path') for ref in ('a', 'b')]
        with patch.object(module, '_media_rows', return_value=rows):
            links = module._message_media_references([DB_A], MetadataContext())
        self.assertEqual(links[key]['media_ref'], '')
        self.assertIn('Ambiguous', links[key]['correlation'])

    def test_message_links_and_conversation_keys_are_database_scoped(self):
        key_a = module._message_key(DB_A, 'message-1', 'chat-1', 'synthetic-uuid-1')
        with patch.object(module, '_target_db_paths', return_value=[DB_A, DB_B]), \
                patch.object(module, '_message_rows', return_value=[message()]), \
                patch.object(module, '_manifest_account_identifiers',
                             return_value={DATA_A: {'local.synthetic'},
                                           DATA_B: {'local.synthetic'}}), \
                patch.object(module, '_message_media_references',
                             return_value={key_a: {'media_ref': 'mock:only-A'}}):
            rows, _ = report_dicts(module.anonymousChat_messages.__wrapped__(MetadataContext()))
        self.assertEqual([row['Media'] for row in rows], ['mock:only-A', ''])
        self.assertNotEqual(rows[0]['Conversation Key'], rows[1]['Conversation Key'])
        self.assertEqual([row['Conversation ID'] for row in rows], ['chat-1', 'chat-1'])
        self.assertTrue(all(row['Other Party'] == 'remote.synthetic' for row in rows))

    def test_missing_conversation_id_uses_message_identity(self):
        self.assertNotEqual(module._conversation_key(DB_A, None, '1'),
                            module._conversation_key(DB_A, None, '2'))
        self.assertEqual(json.loads(module._conversation_key(DB_A, 'chat-1')),
                         [DB_A, 'conversation', 'chat-1'])

    def test_incoming_and_outgoing_recipient_are_opposite_sender(self):
        accounts = {'local.synthetic'}
        self.assertEqual(module._recipient(message(), accounts), 'local.synthetic')
        self.assertEqual(module._recipient(message(sender_flag=0,
                                                  sender_name='local.synthetic'), accounts),
                         'remote.synthetic')
        self.assertEqual(module._recipient(message(sender_flag=99), accounts), '')

    def test_account_conflict_cannot_fall_back_to_sender_flag_or_owner_label(self):
        row = message(sender_flag=0, sender_name='remote.synthetic',
                      from_username='remote.synthetic', to_username='local.synthetic')
        accounts = {'local.synthetic'}
        self.assertEqual(module._direction(row, accounts), '')
        self.assertEqual(module._recipient(row, accounts), '')
        self.assertEqual(module._other_party(row, accounts), 'remote.synthetic')
        # The sender and flag can agree even when the stored endpoints are reversed.
        row['sender_flag'] = 1
        self.assertEqual(module._direction(row, accounts), 'Incoming')
        self.assertEqual(module._recipient(row, accounts), 'local.synthetic')

    def test_direction_requires_one_confirmed_local_endpoint(self):
        for accounts in ((), {'unrelated.synthetic'}, {'local.synthetic', 'remote.synthetic'}):
            with self.subTest(accounts=accounts):
                self.assertEqual(module._direction(message(), accounts), '')
                self.assertEqual(module._recipient(message(), accounts), '')
                self.assertEqual(module._other_party(message(), accounts),
                                 'Participants: local.synthetic, remote.synthetic')
        self.assertEqual(module._direction(message(sender_name='REMOTE.SYNTHETIC'),
                                           {'LOCAL.SYNTHETIC'}), 'Incoming')

    def test_cached_contact_usernames_are_not_signed_in_evidence(self):
        manifest = {'username': 'local.synthetic',
                    'contacts': [{'username': 'remote.synthetic'}],
                    'messages': json.dumps([{'user': {'username': 'another.synthetic'}}]),
                    'session': json.dumps({'username': 'session.synthetic'})}
        self.assertEqual(module._manifest_usernames(manifest),
                         {'local.synthetic', 'session.synthetic'})
        self.assertEqual(module._manifest_usernames({'signedInUsername': ' local.synthetic '}),
                         {'local.synthetic'})

    def test_manifest_evidence_cannot_cross_container_or_input_root(self):
        suffix = ('/Library/Application Support/com.anonimchat.app/'
                  'RCTAsyncLocalStorage_V1/manifest.json')
        manifests = {DATA_A + suffix: {'signedInUsername': 'local.synthetic'},
                     DATA_B + suffix: {'signedInUsername': 'other.synthetic'},
                     'copy/' + DATA_A + suffix: {'signedInUsername': 'copy.synthetic'},
                     DATA_A + '/Library/Caches/manifest.json': {'signedInUsername': 'decoy'}}
        context = MetadataContext(manifests)
        with patch.object(module, '_target_containers',
                          return_value=(set(), {UUID_A, UUID_B}, set(), {})), \
                patch.object(module, '_read_json', side_effect=manifests.get):
            accounts = module._manifest_account_identifiers(context)
        self.assertEqual(accounts, {DATA_A: {'local.synthetic'}, DATA_B: {'other.synthetic'},
                                    'copy/' + DATA_A: {'copy.synthetic'}})
        with patch.object(module, '_target_db_paths', return_value=[DB_A, DB_B]), \
                patch.object(module, '_manifest_account_identifiers', return_value=accounts), \
                patch.object(module, '_message_rows', return_value=[message()]), \
                patch.object(module, '_message_media_references', return_value={}):
            rows, _ = report_dicts(module.anonymousChat_messages.__wrapped__(context))
        self.assertEqual([row['Direction'] for row in rows], ['Incoming', ''])
        self.assertEqual(rows[1]['Other Party'], 'Participants: local.synthetic, remote.synthetic')

    def test_malformed_url_is_retained_without_crashing_or_linking(self):
        malformed = 'https://[invalid/image.jpg'
        rows = self.media_rows([entry()], [reference(reference=malformed)])
        self.assertFalse(any(row.get('media_ref') for row in rows))
        self.assertEqual(rows[-1]['local_path'], malformed)

    def test_nonpositive_or_invalid_sizes_are_unavailable(self):
        for value in (None, '', 0, -1, 0.5, 'nan', 'inf', 'bad'):
            with self.subTest(value=value):
                self.assertIsNone(module._media_size(value))
        self.assertEqual(module._media_size('1234'), 1234)

    def test_timestamp_and_size_are_never_matching_evidence(self):
        ref = reference(reference=URL)
        files = [entry(DATA_A + '/Library/Caches/a.jpg'),
                 entry(DATA_A + '/Library/Caches/b.jpg')]
        rows = self.media_rows(files, [ref])
        self.assertFalse(any(row.get('media_ref') for row in rows))
        self.assertIn('size/timestamp/name-only matching not used', rows[-1]['correlation'])

    def test_sdimagecache_hashes_url_text_and_handles_unknown_size(self):
        key = hashlib.md5(URL.encode(), usedforsecurity=False).hexdigest()
        path = DATA_A + '/Library/Caches/com.hackemist.sdimagecache/default/' + key
        matches = module._sdimagecache_url_matches(
            [classified(path)], [reference(size=0)], set(), set())
        self.assertIn('SDImageCache URL-derived filename', matches[0][0][2])
        self.signature.assert_not_called()
        self.checkin.assert_not_called()

    def test_duplicate_cache_keys_are_scoped_and_contradictions_block_fallback(self):
        key = hashlib.md5(URL.encode(), usedforsecurity=False).hexdigest()
        suffix = '/Library/Caches/com.hackemist.sdimagecache/default/' + key
        files = [classified(DATA_A + suffix), classified(DATA_B + suffix)]
        self.assertEqual(set(module._sdimagecache_url_matches(
            files, [reference()], set(), set())), {0})
        blocked = set()
        self.assertEqual(module._sdimagecache_url_matches(
            files, [reference(size=9999)], set(), set(), blocked), {})
        self.assertEqual(blocked, {0})

    def test_media_table_message_link_requires_explicit_join(self):
        media = reference(kind='Media Table Metadata', media_id='ph://synthetic-asset',
                          filename='asset.jpg', reference='asset.jpg', source=DB_A,
                          join_tokens=['ph://synthetic-asset', 'asset.jpg'])
        message_ref = reference(source=DB_A, reference='', message_id='message-2',
                                join_tokens=['ph://synthetic-asset'])
        direct = {0: [(0, media, 'Direct: media-table stored filename')]}
        matches = module._explicit_media_table_message_matches(
            [classified()], [media, message_ref], direct, {0})
        self.assertEqual([item[1]['message_id'] for item in matches[0]], ['message-2'])
        self.assertEqual(matches[0][0][1]['media_id'], 'ph://synthetic-asset')
        self.assertIn('explicit message_info media join', matches[0][0][2])

        other_database = dict(message_ref, source=DB_B, message_id='message-3')
        self.assertEqual(module._explicit_media_table_message_matches(
            [classified()], [media, other_database], direct, {0}), {})
        duplicate_media = dict(media, media_id='ph://other-asset',
                               join_tokens=['ph://synthetic-asset'])
        self.assertEqual(module._explicit_media_table_message_matches(
            [classified()], [media, duplicate_media, message_ref], direct, {0}), {})

    def test_photos_uuid_requires_unique_safe_relative_path(self):
        photo_uuid = 'AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA'
        refs = [reference(kind='Media Table Metadata', media_id='ph://' + photo_uuid + '/L0/001')]
        context = MetadataContext()
        context.seeker.search.return_value = ['C:/synthetic/Photos.sqlite']
        safe = dict(uuid=photo_uuid, directory='DCIM/100APPLE', filename='SYNTH001.JPG')
        for assets in ([safe, safe], [dict(safe, directory='DCIM/../elsewhere')],
                       [dict(safe, filename='../outside.jpg')]):
            with patch.object(module, '_query_rows', return_value=assets):
                self.assertEqual(module._photos_asset_paths(context, refs), {})
        with patch.object(module, '_query_rows', return_value=[safe]):
            self.assertIn('DCIM/100APPLE/SYNTH001.JPG',
                          module._photos_asset_paths(context, refs))
        other_uuid = 'BBBBBBBB-BBBB-4BBB-8BBB-BBBBBBBBBBBB'
        refs.append(reference(kind='Media Table Metadata', media_id='ph://' + other_uuid))
        with patch.object(module, '_query_rows', return_value=[safe, dict(safe, uuid=other_uuid)]):
            self.assertEqual(module._photos_asset_paths(context, refs), {})

    def test_fnmatch_literals_do_not_stage_a_different_file(self):
        target = DATA_A + '/Library/Caches/image[1]?.jpg'
        patterns = module._media_search_patterns(target)
        self.assertTrue(any(fnmatch.fnmatchcase(target, pattern) for pattern in patterns))
        self.assertFalse(any(fnmatch.fnmatchcase(
            DATA_A + '/Library/Caches/image1a.jpg', pattern) for pattern in patterns))

    def test_discovery_paths_cover_lowercase_bundle_and_omit_unused_plugin_paths(self):
        path = ('private/var/containers/Bundle/Application/' + UUID_A +
                '/AnonimChat.app/Info.plist')
        for artifact in module.__artifacts_v2__.values():
            self.assertIsInstance(artifact['author'], str)
            self.assertTrue(artifact['author'].strip())
            self.assertTrue(any(fnmatch.fnmatchcase(path, pattern)
                                for pattern in artifact['paths']))
            self.assertFalse(any('PluginKitPlugin' in pattern for pattern in artifact['paths']))

    def test_aggregates_ignore_malformed_times_but_preserve_message_counts(self):
        messages = [message(), message(message_time='not a timestamp'),
                    message(message_time=10**100)]
        with patch.object(module, '_target_db_paths', return_value=[DB_A, DB_B]), \
                patch.object(module, '_message_rows', return_value=messages), \
                patch.object(module, '_conversation_rows', return_value=[{'conversation_id': 'chat-1'}]):
            accounts, source = report_dicts(module.anonymousChat_accounts.__wrapped__(MetadataContext()))
            chats, _ = report_dicts(module.anonymousChat_conversations.__wrapped__(MetadataContext()))
        self.assertEqual(accounts[0]['Message Count'], 6)
        self.assertEqual(accounts[0]['Conversation Count'], 2)
        self.assertEqual(accounts[0]['First Message Timestamp'], WHEN)
        self.assertEqual(chats[0]['Message Count'], 3)
        self.assertEqual(source, DB_A + '\n' + DB_B)

    def test_sqlite_optional_columns_wal_and_readonly_connection(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-') as root, ExitStack() as cleanup:
            path = str(Path(root) / 'synthetic.db')
            writer = sqlite3.connect(path)
            cleanup.callback(writer.close)
            writer.execute('PRAGMA journal_mode=WAL')
            writer.execute('PRAGMA wal_autocheckpoint=0')
            writer.execute('CREATE TABLE messages (message_id TEXT, message TEXT, media_data BLOB)')
            writer.execute('INSERT INTO messages (message_id, message) VALUES (?, ?)',
                           ('synthetic-1', 'Invented metadata only'))
            writer.commit()
            # Inspect only schema-authorized text columns; the BLOB column stays NULL.
            statements = []
            connections = []
            real_open = module.open_sqlite_db_readonly

            def open_readonly(db_path):
                connection = real_open(db_path)
                connection.set_trace_callback(statements.append)
                connections.append(connection)
                cleanup.callback(connection.close)
                return connection

            with patch.object(module, 'open_sqlite_db_readonly', side_effect=open_readonly):
                rows = module._message_rows(path)
            self.assertEqual(rows[0]['message_text'], 'Invented metadata only')
            self.assertIsNone(rows[0]['media_size'])
            self.assertFalse(any('media_data' in sql.lower() for sql in statements))
            with self.assertRaises(sqlite3.ProgrammingError):
                connections[0].execute('SELECT 1')
            with real_open(path) as reader:
                with self.assertRaises(sqlite3.OperationalError):
                    reader.execute('DELETE FROM messages')
            reader.close()
            self.assertTrue(Path(path + '-wal').exists())
            writer.close()

    def test_missing_and_corrupt_databases_return_no_rows(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-') as root:
            missing = str(Path(root) / 'missing.db')
            corrupt = Path(root) / 'invalid.db'
            corrupt.write_text('Synthetic deliberately invalid database', encoding='utf-8')
            with patch.object(module, 'logfunc'):
                self.assertEqual(module._message_rows(missing), [])
                self.assertEqual(module._message_rows(str(corrupt)), [])
            self.assertFalse(Path(missing).exists())

    def test_known_file_type_takes_precedence_over_reference_mime(self):
        matches = [(0, reference(mime='image/png'), 'Direct: Photos original')]
        self.assertEqual(module._media_force_type('JPEG', matches), 'image/jpeg')

    def test_optional_columns_in_every_metadata_table(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-') as root:
            path = str(Path(root) / 'partial.db')
            db = sqlite3.connect(path)
            try:
                db.executescript('''
                    CREATE TABLE conversations (conversation_id TEXT);
                    INSERT INTO conversations VALUES ('chat-1');
                    CREATE TABLE blocked (block_id TEXT);
                    INSERT INTO blocked VALUES ('block-1');
                    CREATE TABLE media (media_id TEXT);
                    INSERT INTO media VALUES ('synthetic-media-1');
                    CREATE TABLE messages (message_id TEXT, conversation_id TEXT);
                    INSERT INTO messages VALUES ('message-1', 'chat-1');
                ''')
                db.commit()
            finally:
                db.close()
            self.assertEqual(module._conversation_rows(path)[0]['conversation_id'], 'chat-1')
            self.assertEqual(module._blocked_rows(path)[0]['block_id'], 'block-1')
            self.assertEqual(module._media_table_rows(path)[0]['media_id'], 'synthetic-media-1')
            self.assertEqual(module._message_rows(path)[0]['message_id'], 'message-1')

    def test_bundle_versions_remain_with_the_correct_container(self):
        paths = [f'private/var/containers/Bundle/Application/{uuid}/AnonimChat.app/Info.plist'
                 for uuid in (UUID_A, UUID_B)]
        info = {path: {'CFBundleIdentifier': 'com.anonimchat.app',
                       'CFBundleShortVersionString': version}
                for path, version in zip(paths, ('1.0', '2.0'))}
        with patch.object(module, '_read_plist', side_effect=info.get):
            rows, source = report_dicts(module.anonymousChat_appInfo.__wrapped__(MetadataContext(paths)))
        self.assertEqual([(row['Bundle Container UUID'], row['Version']) for row in rows],
                         [(UUID_A, '1.0'), (UUID_B, '2.0')])
        self.assertEqual(source, '\n'.join(paths))

    def test_database_name_alone_does_not_authorize_an_unrelated_container(self):
        context = MetadataContext([DB_A, DB_B, DATA_A + '/Library/Preferences/com.anonimchat.app.plist'])
        with patch.object(module, '_read_plist', return_value={}):
            self.assertEqual(module._target_db_paths(context), [DB_A])

    def test_itunes_manifest_app_domain_uses_bundle_id_data_container(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-itunes-') as root:
            root = Path(root)
            backup = root / 'backup'
            stage = root / 'stage'
            backup.mkdir()
            stage.mkdir()
            database_payload = root / 'anonimchat.db'
            db = sqlite3.connect(database_payload)
            try:
                db.execute('CREATE TABLE conversations (conversation_id TEXT)')
                db.execute('INSERT INTO conversations VALUES (?)', ('synthetic-chat',))
                db.commit()
            finally:
                db.close()
            database_hash = 'a' * 40
            preference_hash = 'b' * 40
            for digest, payload in (
                    (database_hash, database_payload.read_bytes()),
                    (preference_hash, plistlib.dumps({'synthetic_fixture': True}))):
                folder = backup / digest[:2]
                folder.mkdir(parents=True, exist_ok=True)
                (folder / digest).write_bytes(payload)
            manifest = sqlite3.connect(backup / 'Manifest.db')
            try:
                manifest.execute('''
                    CREATE TABLE Files (
                        fileID TEXT, domain TEXT, relativePath TEXT,
                        flags INTEGER, file BLOB
                    )
                ''')
                manifest.executemany(
                    'INSERT INTO Files VALUES (?, ?, ?, ?, ?)',
                    [
                        (database_hash, 'AppDomain-com.anonimchat.app',
                         'Library/LocalDatabase/anonimchat.db', 1, b''),
                        (preference_hash, 'AppDomain-com.anonimchat.app',
                         'Library/Preferences/com.anonimchat.app.plist', 1, b''),
                    ])
                manifest.commit()
            finally:
                manifest.close()
            seeker = FileSeekerItunes(str(backup), str(stage), 'db', [])
            try:
                database_staged = seeker.search(
                    '*/Library/LocalDatabase/anonimchat.db*', return_on_first_hit=True)
                context = MetadataContext([database_staged])
                context.seeker = seeker
                self.assertEqual(module._container_location(database_staged),
                                 ('data', module._BUNDLE_ID.upper()))
                self.assertEqual(module._target_db_paths(context), [database_staged])
            finally:
                seeker.cleanup()

    def test_app_group_metadata_matches_app_specific_group_identifier(self):
        bundle_info = ('private/var/containers/Bundle/Application/' + UUID_A +
                       '/AnonimChat.app/Info.plist')
        group_metadata = ('private/var/mobile/Containers/Shared/AppGroup/' + UUID_B +
                          '/.com.apple.mobile_container_manager.metadata.plist')
        plist_values = {
            bundle_info: {'CFBundleIdentifier': module._BUNDLE_ID},
            group_metadata: {'MCMMetadataIdentifier': 'group.com.anonimchat.app.shared'},
        }
        with patch.object(module, '_read_plist', side_effect=plist_values.get):
            containers = module._target_containers(
                MetadataContext([bundle_info, group_metadata]))
        self.assertEqual(containers[2], {UUID_B})

    def test_zip_and_tar_inventory_never_open_media(self):
        context = MetadataContext()
        for kind in ('zip', 'tar'):
            with self.subTest(kind=kind):
                handle = Mock()
                item = Mock()
                if kind == 'zip':
                    item.is_dir.return_value = False
                    item.filename, item.file_size = entry()['path'], 1234
                    item.date_time = (2030, 1, 1, 0, 0, 0)
                    item.extra = b''
                    handle.infolist.return_value = [item]
                    context.seeker = SimpleNamespace(
                        zip_file=handle,
                        decode_extended_timestamp=lambda _extra: (None, WHEN.timestamp()),
                    )
                else:
                    item.isfile.return_value = True
                    item.name, item.size, item.mtime = entry()['path'], 1234, WHEN.timestamp()
                    handle.getmembers.return_value = [item]
                    context.seeker = SimpleNamespace(tar_file=handle)
                rows = list(module._iter_source_entries(context))
                self.assertEqual(rows[0]['size'], 1234)
                self.assertEqual(rows[0]['modified_at'], WHEN)
                handle.open.assert_not_called()
                handle.extractfile.assert_not_called()

    def test_raw_inventory_uses_on_image_metadata_without_reading_media(self):
        path = 'lba0/' + DATA_A + '/Library/Caches/image.jpg'
        raw_entry = SimpleNamespace(size=1234, mtime=WHEN.timestamp(), reading='')
        seeker = SimpleNamespace(name_list=[path], _entries={path: raw_entry})
        context = MetadataContext()
        context.seeker = seeker
        rows = list(module._iter_source_entries(context))
        self.assertEqual(rows[0]['kind'], 'raw')
        self.assertEqual(rows[0]['size'], 1234)
        self.assertEqual(rows[0]['modified_at'], WHEN)

        seeker.search = Mock(return_value='C:/synthetic/staged-image.jpg')
        self.assertEqual(module._stage_media_entry(context, rows[0]),
                         'C:/synthetic/staged-image.jpg')
        seeker.search.assert_called()

    def seeker_media_rows(self, context, references):
        with patch.object(module, '_target_containers',
                          return_value=(set(), {UUID_A, UUID_B, module._BUNDLE_ID.upper()},
                                        set(), {})), \
                patch.object(module, '_attachment_references', return_value=references), \
                patch.object(module, '_photos_asset_paths', return_value={}), \
                patch.object(module, 'check_in_media', return_value='mock:registered') as checkin:
            rows = module._media_rows([ref['source'] for ref in references], context)
        return rows, checkin

    def test_raw_extensionless_cache_links_via_url_mime_without_header_reads(self):
        key = hashlib.md5(URL.encode(), usedforsecurity=False).hexdigest()
        path = 'lba0/' + DATA_A + '/Library/Caches/com.hackemist.sdimagecache/default/' + key
        context = MetadataContext()
        context.seeker = SimpleNamespace(
            name_list=[path],
            _entries={path: SimpleNamespace(size=1234, mtime=WHEN.timestamp(), reading='')},
            search=Mock(return_value='C:/synthetic/staged/' + key))
        rows, checkin = self.seeker_media_rows(context, [reference()])
        media = [row for row in rows if row['kind'] == 'Filesystem Media']
        self.assertEqual(len(media), 1)
        self.assertEqual(media[0]['message_id'], 'message-1')
        self.assertEqual(media[0]['media_ref'], 'mock:registered')
        self.assertIn('SDImageCache URL', media[0]['identification'])
        self.assertEqual(checkin.call_args.kwargs['force_type'], 'image/jpeg')
        context.seeker.search.assert_called_once()
        self.signature.assert_not_called()

    def test_raw_unknown_cache_is_an_unlinked_candidate_not_silently_dropped(self):
        path = 'lba0/' + DATA_A + '/Library/Caches/unknown-cache-object'
        context = MetadataContext()
        context.seeker = SimpleNamespace(
            name_list=[path],
            _entries={path: SimpleNamespace(size=1234, mtime=0, reading='')}, search=Mock())
        rows, checkin = self.seeker_media_rows(context, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['kind'], 'Filesystem Candidate')
        self.assertEqual(rows[0]['detected_type'], 'Unknown')
        self.assertEqual(rows[0]['database_referenced'], 'No')
        self.assertEqual(rows[0]['media_ref'], '')
        checkin.assert_not_called()
        context.seeker.search.assert_not_called()
        self.signature.assert_not_called()

    def test_itunes_dictionary_inventory_links_cache_and_uses_manifest_times(self):
        key = hashlib.md5(URL.encode(), usedforsecurity=False).hexdigest()
        root = 'private/var/mobile/Containers/Data/Application/com.anonimchat.app'
        path = root + '/Library/Caches/com.hackemist.sdimagecache/default/' + key
        for backup_type, encrypted in (('db', False), ('db', True), ('mbdb', False)):
            with self.subTest(backup_type=backup_type, encrypted=encrypted):
                # A real seeker class with invented listing/property metadata.
                # Neither the original nor staged media files exist in this test.
                seeker = object.__new__(FileSeekerItunes)
                seeker.directory = 'C:/synthetic/backup'
                seeker.backup_type = backup_type
                seeker.decryption_keys = ['synthetic-key'] if encrypted else []
                seeker._all_files = {path: 'a' * 40}
                seeker._all_file_meta = {}
                seeker.files_metadata = {'a' * 40: plistlib.dumps({
                    'Size': 1234, 'Birth': int(WHEN.timestamp()),
                    'LastModified': int(WHEN.timestamp()) + 60})}
                seeker.search = Mock(return_value='C:/synthetic/staged/' + key)
                context = MetadataContext()
                context.seeker = seeker
                file_stat = SimpleNamespace(st_mode=stat.S_IFREG,
                                            st_size=1248 if encrypted else 1234)
                with patch.object(module.os, 'stat', return_value=file_stat) as stat_call:
                    rows, checkin = self.seeker_media_rows(
                        context, [reference(source=root + '/Library/LocalDatabase/anonimchat.db')])
                media = next(row for row in rows if row['kind'] == 'Filesystem Media')
                self.assertEqual(media['media_ref'], 'mock:registered')
                self.assertEqual(media['filesystem_size'], 1234)
                self.assertIn('2030-01-01 00:00:00', media['created'])
                self.assertIn('2030-01-01 00:01:00', media['modified'])
                self.assertEqual(media['accessed'], '')
                expected_hash_path = ('aa/' if backup_type == 'db' else '') + 'a' * 40
                self.assertTrue(str(stat_call.call_args.args[0]).replace('\\', '/')
                                .endswith(expected_hash_path))
                self.assertEqual(checkin.call_args.kwargs['force_type'], 'image/jpeg')
                seeker.search.assert_called_once()
        self.signature.assert_not_called()

    def test_itunes_missing_properties_do_not_report_backup_copy_times(self):
        path = DATA_A + '/Library/Caches/image.jpg'
        seeker = SimpleNamespace(directory='C:/synthetic', _all_files={path: 'a' * 40},
                                 backup_type='db', files_metadata={}, decryption_keys=[])
        context = MetadataContext()
        context.seeker = seeker
        file_stat = SimpleNamespace(st_mode=stat.S_IFREG, st_size=1234)
        with patch.object(module.os, 'stat', return_value=file_stat):
            rows = list(module._iter_source_entries(context))
        self.assertEqual(rows[0]['size'], 1234)
        self.assertEqual([rows[0][key] for key in ('created', 'modified', 'accessed')], ['', '', ''])
        with patch.object(module.os, 'stat', side_effect=FileNotFoundError):
            self.assertEqual(list(module._iter_source_entries(context)), [])
        with patch.object(module.os, 'stat', side_effect=AssertionError('Unrelated stat')):
            self.assertEqual(list(module._iter_source_entries(context, include=lambda _: False)), [])

    def test_extensionless_classification_does_not_scan_every_reference(self):
        urls = [f'https://example.invalid/synthetic/{index}.jpg' for index in range(120)]
        references = [reference(reference=url, message_id=f'message-{index}')
                      for index, url in enumerate(urls[:80])]
        entries = [entry(DATA_A + '/Library/Caches/com.hackemist.sdimagecache/default/' +
                         hashlib.md5(url.encode(), usedforsecurity=False).hexdigest(), kind='raw')
                   for url in urls]
        with patch.object(module, '_entry_matches_reference',
                          wraps=module._entry_matches_reference) as comparisons:
            rows = self.media_rows(entries, references)
        self.assertEqual(sum(bool(row['media_ref']) for row in rows), 80)
        self.assertLessEqual(comparisons.call_count, 2 * (len(entries) + len(references)))
        self.signature.assert_not_called()

    def test_media_analysis_is_shared_but_registration_is_per_artifact(self):
        path = DATA_A + '/Library/Caches/image.jpg'
        context = MetadataContext()
        context.seeker = SimpleNamespace(
            name_list=[path], _entries={path: SimpleNamespace(size=1234, mtime=0, reading='')},
            search=Mock(return_value='C:/synthetic/staged/image.jpg'))
        references = [reference(reference='Library/Caches/image.jpg')]
        with patch.object(module, '_iter_source_entries',
                          wraps=module._iter_source_entries) as inventory:
            for name in ('Messages', 'Media'):
                with patch.object(context, 'get_artifact_name', return_value=name):
                    rows, checkin = self.seeker_media_rows(context, references)
                self.assertTrue(any(row['media_ref'] == 'mock:registered' for row in rows))
                checkin.assert_called_once()
        inventory.assert_called_once()

    def test_raw_unknown_mtime_preserves_filesystem_reading_without_utc_epoch(self):
        path = 'lba0/' + DATA_A + '/Library/Caches/image.jpg'
        raw_entry = SimpleNamespace(size=1234, mtime=0,
                                    reading='2030-01-01 00:00:00')
        context = MetadataContext()
        context.seeker = SimpleNamespace(name_list=[path], _entries={path: raw_entry})
        rows = list(module._iter_source_entries(context))
        self.assertIsNone(rows[0]['modified_at'])
        self.assertIn('timezone not recorded', rows[0]['modified'])

    def test_directory_filter_skips_unrelated_files_before_stat(self):
        context = MetadataContext()
        context.seeker = SimpleNamespace(_all_files=['C:/synthetic/unrelated.txt'], directory='C:/synthetic')
        with patch.object(module.os, 'stat', side_effect=AssertionError('Unrelated stat')):
            self.assertEqual(list(module._iter_source_entries(context, include=lambda _: False)), [])


if __name__ == '__main__':
    unittest.main()
