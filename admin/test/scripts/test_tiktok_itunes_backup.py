"""The TikTok IM artifacts read an iTunes backup, through the backup seeker.

Issue #801 asked for an iTunes-friendly path for the TikTok message parsers, whose
patterns were written against a full filesystem extraction. The backup seeker now
reconstructs an AppDomain file as
private/var/mobile/Containers/Data/Application/<bundle id>/<relativePath>, which the
patterns match, and the artifacts attribute a container named by a bundle id to that app.
Nothing pinned that, so these tests build an unencrypted backup (Manifest.db, Manifest.plist
and the hashed files) holding a TikTok chat store, the db.sqlite-backup copy that sits
beside it on every recorded listing, and an AwemeIM.db, then run the seeker and the
artifacts the way the runner does.

The db.sqlite-backup copy is matched and staged but not read; that is asserted here so a
change to either side of that line shows up.
"""
import hashlib
import os
import pathlib
import plistlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerItunes  # pylint: disable=wrong-import-position
from scripts.artifacts import tikTok, tikTokReplied  # pylint: disable=wrong-import-position

DOMAIN = 'AppDomain-com.zhiliaoapp.musically'
ACCOUNT = '6787436503258760198'
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
    db.commit()
    db.close()
    backup_copy = os.path.join(work, 'db.sqlite-backup')
    shutil.copy2(chat, backup_copy)
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

    files = [(CHAT_STORE, chat), (CHAT_STORE + '-backup', backup_copy), ('Documents/AwemeIM.db', aweme)]
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

    def test_messages_are_read_from_the_backup_and_the_copy_is_staged_but_not_read(self):
        names, rows, source, files_found = self.run_artifact(tikTok, 'tiktok_messages')

        staged = sorted(Context.get_relative_path(path) for path in files_found)
        self.assertEqual(staged, [f'{CONTAINER}/Documents/AwemeIM.db',
                                  f'{CONTAINER}/{CHAT_STORE}',
                                  f'{CONTAINER}/{CHAT_STORE}-backup'])

        self.assertEqual(len(rows), 2)
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

    def test_contacts_are_read_from_the_backup(self):
        names, rows, _, _ = self.run_artifact(tikTok, 'tiktok_contacts')

        self.assertEqual(sorted(row[names.index('Nickname')] for row in rows),
                         ['Contact One', 'The Account'])
        self.assertEqual({row[names.index('Source File')] for row in rows},
                         {f'{CONTAINER}/Documents/AwemeIM.db'})

    def test_replied_messages_run_over_the_backup_without_rows(self):
        _, rows, _, _ = self.run_artifact(tikTokReplied, 'tiktok_replied')

        self.assertEqual(rows, [])


if __name__ == '__main__':
    unittest.main()
