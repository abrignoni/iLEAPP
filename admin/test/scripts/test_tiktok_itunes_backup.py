"""The TikTok IM artifacts read an iTunes backup, through the backup seeker.

Issue #801 asked for an iTunes-friendly path for the TikTok message parsers, whose
patterns were written against a full filesystem extraction. The backup seeker now
reconstructs an AppDomain file as
private/var/mobile/Containers/Data/Application/<bundle id>/<relativePath>, which the
patterns match, and the artifacts attribute a container named by a bundle id to that app.
Nothing pinned that, so these tests build an unencrypted backup (Manifest.db, Manifest.plist
and the hashed files) holding a TikTok chat store, the db.sqlite-backup file that sits
beside it, and an AwemeIM.db, then run the seeker and the artifacts the way the runner does.

The db.sqlite-backup file is matched and staged but not read; that is asserted here so a
change to either side of that line shows up. It is not a SQLite database: on the two
registered Hickman iTunes backups it is under 2 KB and begins with the magic WCDB's
deprecated repair module defines for the file it saves sqlite_master information to
(SQLITERK_SM_MAGIC), so the stand-in built here is that header and nothing else.
"""
from contextlib import closing
import hashlib
import json
import os
import pathlib
import plistlib
import shutil
import sqlite3
import struct
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.artifact_report import ArtifactHtmlReport  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerItunes  # pylint: disable=wrong-import-position
from scripts.artifacts import tikTok, tikTokReplied  # pylint: disable=wrong-import-position

DOMAIN = 'AppDomain-com.zhiliaoapp.musically'
ACCOUNT = '7000000000000000002'
CONTACT = '7000000000000000001'
CONTAINER = 'private/var/mobile/Containers/Data/Application/com.zhiliaoapp.musically'
CHAT_STORE = f'Library/Application Support/ChatFiles/{ACCOUNT}/db.sqlite'


def build_backup(backup):
    work = tempfile.mkdtemp()
    chat = os.path.join(work, 'db.sqlite')
    db = sqlite3.connect(chat)
    db.executescript(f'''
        CREATE TABLE TIMMessageORM(identifier TEXT, localcreatedat INTEGER, servercreatedat INTEGER,
            sender INTEGER, content TEXT, belongingConversationIdentifier TEXT, deleted INTEGER);
        CREATE TABLE TIMParticipantORM(userID INTEGER, belongingConversationIdentifier TEXT);
        CREATE TABLE TIMMessageKVORM(rowid INTEGER PRIMARY KEY, belongingMessageID TEXT, key TEXT, value TEXT);
        INSERT INTO TIMParticipantORM VALUES ({ACCOUNT}, 'conv1'), ({CONTACT}, 'conv1');
        INSERT INTO TIMMessageORM VALUES
            ('m1', 1700000000, 1700000001, {ACCOUNT}, '{{"text":"sent"}}', 'conv1', 0),
            ('m2', 1700000100, 1700000101, {CONTACT}, '{{"text":"received"}}', 'conv1', 0);
    ''')
    # m2 is a reply to m1: the store keeps its own copy of the replied-to message.
    hint = json.dumps({'content': json.dumps({'text': 'sent'}), 'refmsg_uid': int(ACCOUNT)})
    db.execute('INSERT INTO TIMMessageKVORM(belongingMessageID, key, value) VALUES (?,?,?)',
               ('m2', 'ref', json.dumps({'ref_msg_type': 7, 'ref_msg_id': 'm1', 'hint': hint})))
    db.commit()
    db.close()
    backup_file = os.path.join(work, 'db.sqlite-backup')
    with open(backup_file, 'wb') as f:
        # magic, version, entity count, 16-byte salt field; no entities follow.
        f.write(b'\x00dBmSt' + struct.pack('<HI', 1, 0) + bytes(16))
    aweme = os.path.join(work, 'AwemeIM.db')
    db = sqlite3.connect(aweme)
    db.executescript(f'''
        CREATE TABLE AwemeContactsV5(uid INTEGER, customid TEXT, nickname TEXT, url1 TEXT,
            latestchattimestamp INTEGER);
        INSERT INTO AwemeContactsV5 VALUES
            ({CONTACT}, 'contact_one', 'Contact One', 'https://example.invalid/1.jpg', 1700000100),
            ({ACCOUNT}, 'the_account', 'The Account', 'https://example.invalid/0.jpg', 1700000000);
    ''')
    db.commit()
    db.close()

    files = [(CHAT_STORE, chat), (CHAT_STORE + '-backup', backup_file), ('Documents/AwemeIM.db', aweme)]
    meta = plistlib.dumps({'Birth': 1700000000, 'LastModified': 1700000200}, fmt=plistlib.PlistFormat.FMT_BINARY)
    manifest = sqlite3.connect(os.path.join(backup, 'Manifest.db'))
    manifest.execute('CREATE TABLE Files(fileID TEXT PRIMARY KEY, domain TEXT, relativePath TEXT, '
                     'flags INTEGER, file BLOB)')
    for relative_path, source in files:
        file_id = hashlib.sha1(f'{DOMAIN}-{relative_path}'.encode()).hexdigest()
        os.makedirs(os.path.join(backup, file_id[:2]), exist_ok=True)
        shutil.copy2(source, os.path.join(backup, file_id[:2], file_id))
        manifest.execute('INSERT INTO Files VALUES (?,?,?,?,?)', (file_id, DOMAIN, relative_path, 1, meta))
        parent = os.path.dirname(relative_path)
        while parent:
            parent_id = hashlib.sha1(f'{DOMAIN}-{parent}'.encode()).hexdigest()
            manifest.execute('INSERT OR IGNORE INTO Files VALUES (?,?,?,?,?)',
                             (parent_id, DOMAIN, parent, 2, meta))
            parent = os.path.dirname(parent)
    manifest.commit()
    manifest.close()
    with open(os.path.join(backup, 'Manifest.plist'), 'wb') as f:
        plistlib.dump({'IsEncrypted': False, 'Version': '10.0'}, f)
    shutil.rmtree(work)


class TikTokITunesBackupTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        tmp = pathlib.Path(self.tmpdir)
        self.backup = tmp / 'backup'
        self.backup.mkdir()
        build_backup(str(self.backup))
        report = tmp / 'report'
        self.data_folder = report / 'data'
        for folder in (self.data_folder, report / 'media', report / '_HTML' / 'media'):
            folder.mkdir(parents=True)
        self.seeker = FileSeekerItunes(str(self.backup), str(self.data_folder), 'db', None)
        Context.clear()
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(report / 'media'), html_media_folder=str(report / '_HTML' / 'media'),
            data_folder=str(self.data_folder), output_folder_base=str(report)))
        Context.set_data_folder(str(self.data_folder))
        Context.set_report_folder(str(report))
        Context.set_seeker(self.seeker)

    def tearDown(self):
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_artifact(self, module, name):
        # The runner searches each declared pattern in turn and hands the union over.
        files_found = []
        for pattern in module.__artifacts_v2__[name]['paths']:
            files_found.extend(self.seeker.search(pattern))
        Context.set_module_name(module.__name__.rsplit('.', 1)[-1])
        Context.set_artifact_name(module.__artifacts_v2__[name]['name'])
        Context.set_files_found(files_found)
        headers, rows, source = getattr(module, name).__wrapped__(Context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return names, rows, source, files_found

    def test_messages_are_read_and_the_backup_file_is_staged_but_not_read(self):
        names, rows, source, files_found = self.run_artifact(tikTok, 'tiktok_messages')

        staged = sorted(Context.get_relative_path(path) for path in files_found)
        self.assertEqual(staged, [f'{CONTAINER}/Documents/AwemeIM.db',
                                  f'{CONTAINER}/{CHAT_STORE}',
                                  f'{CONTAINER}/{CHAT_STORE}-backup'])

        self.assertEqual(len(rows), 2)
        self.assertEqual(names[:2], ['Timestamp', 'Server Created Timestamp'])
        self.assertTrue(all(row[names.index('Message Type')] is None for row in rows))
        self.assertTrue(all(row[names.index('Deleted')] == 0 for row in rows))
        by_message = {row[names.index('Message')]: row for row in rows}
        self.assertEqual(by_message['sent'][names.index('Direction')], 'Outgoing')
        self.assertEqual(by_message['sent'][names.index('Nickname')], 'The Account')
        self.assertEqual(by_message['received'][names.index('Direction')], 'Incoming')
        self.assertEqual(by_message['received'][names.index('Nickname')], 'Contact One')
        self.assertEqual({row[names.index('Account ID')] for row in rows}, {ACCOUNT})
        self.assertEqual(
            by_message['sent'][names.index('Source File')],
            f'{CONTAINER}/{CHAT_STORE}; {CONTAINER}/Documents/AwemeIM.db')

        read = sorted(Context.get_relative_path(path) for path in source.splitlines())
        self.assertEqual(read, [f'{CONTAINER}/Documents/AwemeIM.db', f'{CONTAINER}/{CHAT_STORE}'])

    def chat_store_path(self):
        file_id = hashlib.sha1(f'{DOMAIN}-{CHAT_STORE}'.encode()).hexdigest()
        return self.backup / file_id[:2] / file_id

    def set_first_message(self, content, message_type=7, deleted=0):
        with closing(sqlite3.connect(self.chat_store_path())) as db:
            db.execute('ALTER TABLE TIMMessageORM ADD COLUMN type INTEGER')
            db.execute('UPDATE TIMMessageORM SET content=?, type=?, deleted=? WHERE identifier=?',
                       (content, message_type, deleted, 'm1'))
            db.commit()

    def test_placeholder_and_raw_flags_are_reported(self):
        self.set_first_message('placeholder', message_type=15, deleted=1)
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        self.assertEqual(len(rows), 2)
        row = dict(zip(names, rows[0]))
        self.assertEqual(row['Message'], 'placeholder')
        self.assertEqual(row['Message Type'], 15)
        self.assertEqual(row['Deleted'], 1)
        self.assertEqual(row['Direction'], 'Outgoing')
        self.assertEqual(row['Nickname'], 'The Account')
        self.assertEqual(row['Conversation ID'], 'conv1')

    def test_non_json_content_is_preserved_verbatim(self):
        contents = ['plain text', '{broken JSON', '<script>alert("test")</script>', '', '  ']
        with closing(sqlite3.connect(self.chat_store_path())) as db:
            for index, content in enumerate(contents):
                db.execute('INSERT INTO TIMMessageORM VALUES (?,?,?,?,?,?,?)',
                           (f'literal{index}', 1700010000 + index, 1700010001 + index,
                            int(CONTACT), content, 'conv1', 0))
            db.commit()
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        self.assertEqual(len(rows), 2 + len(contents))
        self.assertEqual([row[names.index('Message')] for row in rows[2:]], contents)

        page = ArtifactHtmlReport('TikTok literal content')
        page.start_artifact_report(self.tmpdir, 'literal-message')
        page.write_artifact_data_table(names, rows, 'constructed chat database')
        page.end_artifact_report()
        rendered = pathlib.Path(self.tmpdir, 'literal-message.temphtml').read_text(encoding='utf8')
        self.assertIn('&lt;script&gt;alert(&quot;test&quot;)&lt;/script&gt;', rendered)
        self.assertNotIn('<td><script>', rendered)

    def test_json_without_text_does_not_become_a_literal_message(self):
        contents = ['{"display_name":"sticker","url":{"url_list":["https://example.invalid/s"]}}',
                    '{"text":null}', 'null', '[]', '"a JSON string"']
        with closing(sqlite3.connect(self.chat_store_path())) as db:
            for index, content in enumerate(contents):
                db.execute('INSERT INTO TIMMessageORM VALUES (?,?,?,?,?,?,?)',
                           (f'json{index}', 1700010000 + index, 1700010001 + index,
                            int(CONTACT), content, 'conv1', 0))
            db.commit()
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        self.assertEqual(len(rows), 2 + len(contents))
        self.assertTrue(all(row[names.index('Message')] is None for row in rows[2:]))
        row = dict(zip(names, rows[2]))
        self.assertEqual(row['Content Display Name'], 'sticker')
        self.assertEqual(row['Content URL'], 'https://example.invalid/s')

    def test_readable_text_can_be_flagged_deleted_without_losing_text(self):
        self.set_first_message('{"text":"still stored"}', message_type=7, deleted=1)
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        row = dict(zip(names, rows[0]))
        self.assertEqual(row['Message'], 'still stored')
        self.assertEqual(row['Message Type'], 7)
        self.assertEqual(row['Deleted'], 1)

    def test_unfamiliar_flags_are_preserved_without_guessing(self):
        self.set_first_message('{"text":"sent"}', message_type=12345, deleted=9)
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        self.assertEqual(rows[0][names.index('Message Type')], 12345)
        self.assertEqual(rows[0][names.index('Deleted')], 9)

    def test_null_flags_remain_unknown(self):
        self.set_first_message('{"text":"sent"}', message_type=None, deleted=None)
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        self.assertIsNone(rows[0][names.index('Message Type')])
        self.assertIsNone(rows[0][names.index('Deleted')])

    def test_both_optional_columns_can_be_absent(self):
        with closing(sqlite3.connect(self.chat_store_path())) as db:
            db.execute('ALTER TABLE TIMMessageORM DROP COLUMN deleted')
            db.commit()
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        self.assertEqual(len(rows), 2)
        self.assertEqual([row[names.index('Message')] for row in rows], ['sent', 'received'])
        self.assertTrue(all(row[names.index('Message Type')] is None for row in rows))
        self.assertTrue(all(row[names.index('Deleted')] is None for row in rows))

    def test_type_present_when_deleted_column_is_absent(self):
        self.set_first_message('placeholder', message_type=15)
        with closing(sqlite3.connect(self.chat_store_path())) as db:
            db.execute('ALTER TABLE TIMMessageORM DROP COLUMN deleted')
            db.commit()
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_messages')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][names.index('Message')], 'placeholder')
        self.assertEqual(rows[0][names.index('Message Type')], 15)
        self.assertIsNone(rows[0][names.index('Deleted')])

    def test_contacts_are_read_from_the_backup(self):
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_contacts')

        self.assertEqual(sorted(row[names.index('Nickname')] for row in rows),
                         ['Contact One', 'The Account'])
        self.assertEqual({row[names.index('Source File')] for row in rows},
                         {f'{CONTAINER}/Documents/AwemeIM.db'})

    def test_a_replied_message_is_read_from_the_backup(self):
        names, rows, _, _ = self.run_artifact(tikTokReplied, 'tiktok_replied')

        self.assertEqual(len(rows), 1)
        row = dict(zip(names, rows[0]))
        self.assertEqual(row['BelongingMessageID'], 'm2')
        self.assertEqual(row['ref_msg_id'], 'm1')
        self.assertEqual(row['Referenced Text'], 'sent')
        self.assertEqual(row['Ref Msg Sender Nickname'], 'The Account')
        self.assertEqual(row['Reply Text'], 'received')
        self.assertEqual(row['Reply Sender Nickname'], 'Contact One')
        self.assertEqual(row['Deleted'], 'False')
        self.assertEqual(row['Parser Table'], 'TIMMessageKVORM')
        self.assertEqual(row['Account ID'], ACCOUNT)
        self.assertEqual(row['Source File'],
                         f'{CONTAINER}/{CHAT_STORE}; {CONTAINER}/Documents/AwemeIM.db')


if __name__ == '__main__':
    unittest.main()
