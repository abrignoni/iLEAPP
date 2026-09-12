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
import sqlite3
import tempfile
import unittest
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts.artifacts import anonymousChat as module


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

    def test_duplicate_basename_does_not_fall_through_to_timestamp(self):
        entries = [entry(DATA_A + '/Library/Caches/a/image.jpg'),
                   entry(DATA_A + '/Library/Caches/b/image.jpg', size=9999)]
        rows = self.media_rows(entries, [reference()])
        self.assertFalse(any(row.get('media_ref') for row in rows))
        self.assertIn('ambiguous', rows[-1]['correlation'])
        self.assertEqual(rows[-1]['filesystem_present'], 'No')

    def test_unique_basename_is_explicitly_inferred(self):
        matches, blocked = module._direct_media_matches(
            [classified()], [reference()], filenames_only=True)
        self.assertFalse(blocked)
        self.assertTrue(matches[0][0][2].startswith('Inferred: unique filename'))

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
                rows = self.media_rows([entry()], [reference(**values)])
                self.assertFalse(any(row.get('media_ref') for row in rows))
                self.assertIn('contradictory', rows[-1]['correlation'])

    def test_filename_comparison_preserves_ios_case(self):
        matched, _method = module._entry_matches_reference(entry()['path'], 'IMAGE.JPG')
        self.assertFalse(matched)

    def test_identical_filenames_are_scoped_to_the_source_container(self):
        rows = self.media_rows([entry(), entry(DATA_B + '/Library/Caches/image.jpg')],
                               [reference()])
        self.assertEqual([row['filesystem_path'] for row in rows if row.get('media_ref')],
                         [entry()['path']])

    def test_data_attachment_cannot_match_same_name_in_bundle_container(self):
        bundle_path = 'private/var/containers/Bundle/Application/' + UUID_A + '/AnonimChat.app/image.jpg'
        rows = self.media_rows([entry(bundle_path)], [reference()])
        self.assertFalse(any(row.get('media_ref') for row in rows))

    def test_repeated_url_retains_separate_typed_message_associations(self):
        refs = [reference(), reference(message_id='message-2',
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
        self.assertEqual(module._recipient(message()), 'local.synthetic')
        self.assertEqual(module._recipient(message(sender_flag=0,
                                                  sender_name='local.synthetic')),
                         'remote.synthetic')
        self.assertEqual(module._recipient(message(sender_flag=99)), '')

    def test_malformed_url_is_retained_without_crashing_or_linking(self):
        malformed = 'https://[invalid/image.jpg'
        rows = self.media_rows([entry()], [reference(reference=malformed)])
        self.assertFalse(any(row.get('media_ref') for row in rows))
        self.assertEqual(rows[-1]['local_path'], malformed)

    def test_nonpositive_or_invalid_sizes_are_unavailable(self):
        for value in (None, '', 0, -1, 0.5, 'nan', 'inf', 'bad'):
            with self.subTest(value=value):
                self.assertIsNone(module._media_size(value))
                self.assertEqual(module._inferred_media_matches(
                    [classified(size=0)], [reference(size=value)], set(), set()), {})
        self.assertEqual(module._media_size('1234'), 1234)

    def test_timestamp_ties_competing_messages_and_window_reject_ambiguity(self):
        ref = reference(reference='')
        files = [classified(DATA_A + '/Library/Caches/a.jpg'),
                 classified(DATA_A + '/Library/Caches/b.jpg')]
        self.assertEqual(module._inferred_media_matches(files, [ref], set(), set()), {})
        self.assertEqual(module._inferred_media_matches(
            files[:1], [ref, reference(reference='', message_id='message-2')],
            set(), set()), {})
        late = classified(modified_at=WHEN + timedelta(seconds=301))
        self.assertEqual(module._inferred_media_matches([late], [ref], set(), set()), {})
        self.assertTrue(module._inferred_media_matches(files[:1], [ref], set(), set()))

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

    def test_media_table_timestamps_never_bridge_databases(self):
        media = reference(kind='Media Table Metadata', media_timestamp=WHEN)
        direct = {0: [(0, media, 'Direct: stored path')]}
        refs = [media, reference(source=DB_B)]
        self.assertEqual(module._media_table_message_matches(
            [classified()], refs, direct, {0}), {})
        refs[1]['source'] = DB_A
        self.assertTrue(module._media_table_message_matches([classified()], refs, direct, {0}))
        refs[1]['size'] = 9999
        self.assertEqual(module._media_table_message_matches(
            [classified()], refs, direct, {0}), {})
        refs[1]['size'] = 1234
        refs.append(reference(message_id='message-2'))
        self.assertEqual(module._media_table_message_matches(
            [classified()], refs, direct, {0}), {})

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
            self.assertIn('var/mobile/Media/DCIM/100APPLE/SYNTH001.JPG',
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
            self.assertEqual(artifact['author'], 'Darren Rooney')
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
        matches = [(0, reference(mime='image/png'), 'Inferred: Photos original')]
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
                    handle.infolist.return_value = [item]
                    context.seeker = SimpleNamespace(zip_file=handle)
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

    def test_directory_filter_skips_unrelated_files_before_stat(self):
        context = MetadataContext()
        context.seeker = SimpleNamespace(_all_files=['C:/synthetic/unrelated.txt'], directory='C:/synthetic')
        with patch.object(module.os, 'stat', side_effect=AssertionError('Unrelated stat')):
            self.assertEqual(list(module._iter_source_entries(context, include=lambda _: False)), [])


if __name__ == '__main__':
    unittest.main()
