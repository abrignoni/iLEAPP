"""Wire calls, message media from the asset cache, the media listing and contacts with cached pictures."""
import collections
import datetime
import hashlib
import pathlib
import plistlib
from plistlib import FMT_BINARY  # pylint: disable=no-name-in-module
import sqlite3
import tempfile
import unittest
import uuid
from unittest import mock

from scripts.artifacts import wire

ACCOUNT = '11111111-2222-3333-4444-555555555555'
SELF_ID = uuid.UUID(ACCOUNT)
PEER_ID = uuid.UUID('66666666-7777-8888-9999-aaaaaaaaaaaa')
CONV_ID = uuid.UUID('bbbbbbbb-cccc-dddd-eeee-ffffffffffff')
NONCE_RECEIVED = uuid.UUID('00000000-0000-0000-0000-000000000001')
NONCE_SENT = uuid.UUID('00000000-0000-0000-0000-000000000002')
EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 8


class _Context:
    def __init__(self, files):
        self.files = files

    def __call__(self):
        return self

    def get_files_found(self):
        return self.files


def _key(nonce, sender, conversation, identifier=None, encrypted=False):
    parts = [str(nonce), str(sender), str(conversation), identifier, 'encrypted' if encrypted else None]
    return hashlib.sha256('_'.join(p for p in parts if p).encode()).hexdigest()


def _build(root, account=ACCOUNT):
    group = root / 'private/var/mobile/Containers/Shared/AppGroup/GROUP'
    store = group / 'AccountData' / account / 'store'
    cache = group / 'Library/Caches' / f'wire-account-{account}'
    store.mkdir(parents=True)
    cache.mkdir(parents=True)
    db = store / 'store.wiredatabase'
    connection = sqlite3.connect(db)
    connection.executescript('''
        CREATE TABLE ZSESSION (Z_PK, ZSELFUSER);
        CREATE TABLE ZUSER (Z_PK, ZNAME, ZHANDLE, ZEMAILADDRESS, ZREMOTEIDENTIFIER_DATA,
                            ZCOMPLETEPROFILEASSETIDENTIFIER, ZPREVIEWPROFILEASSETIDENTIFIER);
        CREATE TABLE ZUSERCLIENT (ZUSER, ZACTIVATIONDATE);
        INSERT INTO ZUSERCLIENT VALUES (1, 100.0), (2, 200.0);
        CREATE TABLE ZCONNECTION (Z_PK, ZTO, ZSTATUS);
        CREATE TABLE ZCONVERSATION (Z_PK, ZCONVERSATIONTYPE, ZUSERDEFINEDNAME, ZREMOTEIDENTIFIER_DATA);
        CREATE TABLE ZMESSAGE (ZSERVERTIMESTAMP, ZNORMALIZEDTEXT, ZCACHEDCATEGORY, ZSENDER,
                               ZVISIBLEINCONVERSATION, ZSYSTEMMESSAGETYPE, ZDURATION, ZNONCE_DATA);
    ''')
    connection.execute('INSERT INTO ZSESSION VALUES (1, 1)')
    connection.executemany('INSERT INTO ZUSER VALUES (?,?,?,?,?,?,?)', [
        (1, 'Self', 'me', None, SELF_ID.bytes, '3-1-self-complete', '3-1-self-preview'),
        (2, 'Peer', 'peer', None, PEER_ID.bytes, '3-1-peer-complete', '3-1-peer-preview'),
        (3, 'Stranger', None, None, uuid.UUID(int=9).bytes, None, None)])
    connection.executemany('INSERT INTO ZCONNECTION VALUES (?,?,?)', [(1, 2, 1), (2, 2, 4), (3, 3, 99)])
    connection.execute('INSERT INTO ZCONVERSATION VALUES (10, 3, ?, ?)', ('Group', CONV_ID.bytes))
    connection.executemany('INSERT INTO ZMESSAGE VALUES (?,?,?,?,?,?,?,?)', [
        (1000.0, None, 8, 2, 10, None, None, NONCE_RECEIVED.bytes),
        (2000.0, None, 8, 1, 10, None, None, NONCE_SENT.bytes),
        (3000.0, None, 0, 2, 10, 18, 90.5, uuid.UUID(int=3).bytes),
        (4000.0, None, 0, 1, 10, 18, 0.0, uuid.UUID(int=4).bytes),
        (5000.0, None, 0, 2, 10, 7, None, uuid.UUID(int=5).bytes),
        (6000.0, None, 0, 1, 10, 1, 0.0, uuid.UUID(int=6).bytes)])
    connection.commit()
    connection.close()

    files = [str(db)]
    for name in (_key(NONCE_RECEIVED, PEER_ID, CONV_ID, 'medium'),
                 _key(NONCE_SENT, SELF_ID, CONV_ID, 'original'),
                 _key(NONCE_SENT, SELF_ID, CONV_ID, 'medium'),
                 'f' * 64):
        (cache / name).write_bytes(b'\xff\xd8\xff' + name.encode())
        files.append(str(cache / name))
    for cache_name, user, asset in (('largeUserImages', PEER_ID, '3-1-peer-complete'),
                                    ('smallUserImages', PEER_ID, '3-1-peer-preview'),
                                    ('largeUserImages', SELF_ID, 'stale-asset')):
        folder = cache / f'com.pinterest.PINDiskCache.{cache_name}'
        folder.mkdir(exist_ok=True)
        archive = {'$archiver': 'NSKeyedArchiver', '$version': 100000, '$top': {},
                   '$objects': ['$null', PNG + cache_name.encode()]}
        path = folder / f'{user}-{asset}'
        path.write_bytes(plistlib.dumps(archive, fmt=FMT_BINARY))
        files.append(str(path))
    return files, cache


def _patched(function, files):
    with mock.patch.object(wire, 'check_in_media', side_effect=lambda path, *a, **k: 'm:' + pathlib.Path(path).name), \
            mock.patch.object(wire, 'check_in_embedded_media', side_effect=lambda src, data, name: 'e:' + data[len(PNG):].decode()):
        headers, rows, source = function.__wrapped__(_Context(files))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return names, [dict(zip(names, row)) for row in rows], source


class WireCallsAndMediaTests(unittest.TestCase):
    def test_calls_and_message_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, _ = _build(pathlib.Path(tmp))
            names, rows, source = _patched(wire.wireMessages, files)
            self.assertEqual(names[:7], ['Date / Time', 'Call Connected', 'Direction', 'Display Name',
                                         'Conversation', 'Message', 'Media'])
            received, sent, call_in, call_out, missed, other_system = rows
            self.assertEqual(received['Media'], 'm:' + _key(NONCE_RECEIVED, PEER_ID, CONV_ID, 'medium'))
            # The original wins over the medium copy of the same message.
            self.assertEqual(sent['Media'], 'm:' + _key(NONCE_SENT, SELF_ID, CONV_ID, 'original'))
            self.assertEqual(call_in['Message Type'], 'Call')
            self.assertEqual(call_in['Direction'], 'Incoming')
            self.assertEqual(call_in['Call Duration (seconds)'], 90.5)
            # Converted like Date / Time, which keeps whole seconds.
            self.assertEqual(call_in['Call Connected'], EPOCH + datetime.timedelta(seconds=2909))
            self.assertEqual(call_out['Direction'], 'Outgoing')
            self.assertIsNone(call_out['Call Connected'])
            self.assertEqual(missed['Message Type'], 'Missed Call')
            self.assertIsNone(missed['Call Duration (seconds)'])
            self.assertEqual(other_system['Message Type'], 'None (uncategorized)')
            self.assertIsNone(other_system['Call Duration (seconds)'])
            self.assertEqual(source.count('\n'), 2)

    def test_media_listing_matches_and_keeps_orphans(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, _ = _build(pathlib.Path(tmp))
            _, rows, _ = _patched(wire.wireMedia, files)
            self.assertEqual(len(rows), 4)
            by_name = {row['Cache File Name']: row for row in rows}
            orphan = by_name['f' * 64]
            self.assertIsNone(orphan['Format'])
            self.assertIsNone(orphan['Message Date / Time'])
            self.assertEqual(orphan['Media'], 'm:' + 'f' * 64)
            self.assertEqual(orphan['Account'], ACCOUNT)
            medium = by_name[_key(NONCE_SENT, SELF_ID, CONV_ID, 'medium')]
            self.assertEqual((medium['Format'], medium['Direction'], medium['Sender']),
                             ('medium', 'Outgoing', 'Self'))
            self.assertEqual(medium['Conversation'], 'Group')

    def test_cache_of_another_account_is_not_matched(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, cache = _build(pathlib.Path(tmp))
            other = cache.parent / 'wire-account-99999999-0000-0000-0000-000000000000'
            other.mkdir()
            name = _key(NONCE_RECEIVED, PEER_ID, CONV_ID, 'medium')
            (other / name).write_bytes(b'x')
            files.append(str(other / name))
            _, rows, _ = _patched(wire.wireMedia, files)
            foreign = [row for row in rows if row['Account'].startswith('99999999')]
            self.assertEqual(len(foreign), 1)
            self.assertIsNone(foreign[0]['Format'])
            _, messages, _ = _patched(wire.wireMessages, files)
            self.assertEqual(messages[0]['Media'], 'm:' + name)
            self.assertNotIn(str(other / name), _patched(wire.wireMessages, files)[2])


class WireTwoAccountTests(unittest.TestCase):
    """Two accounts with identical stores: every artifact doubles, nothing crosses accounts."""

    SECOND = '99999999-8888-7777-6666-555555555555'

    def _two_accounts(self, root):
        first, _ = _build(root)
        second, _ = _build(root, self.SECOND)
        return first, first + second

    def test_every_artifact_doubles_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            one, both = self._two_accounts(pathlib.Path(tmp))
            for function in (wire.wireUsers, wire.wireMessages, wire.wireContacts, wire.wireMedia):
                with self.subTest(artifact=function.__name__):
                    _, single, _ = _patched(function, one)
                    _, double, source = _patched(function, both)
                    self.assertEqual(len(double), 2 * len(single))
                    self.assertEqual(
                        collections.Counter(row['Account'] for row in double),
                        {ACCOUNT: len(single), self.SECOND: len(single)})
                    self.assertEqual(sum(line.endswith('/store.wiredatabase')
                                         for line in source.split('\n')), 2)

    def test_media_stays_with_its_own_account(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, both = self._two_accounts(pathlib.Path(tmp))
            _, messages, _ = _patched(wire.wireMessages, both)
            for row in messages:
                if row['Media']:
                    # The stub names the media after the checked-in path's file name, so the
                    # account is checked through the path handed to check_in_media instead.
                    self.assertTrue(row['Conversation Key'].startswith(row['Account'] + '/'))
            with mock.patch.object(wire, 'check_in_media',
                                   side_effect=lambda path, *a, **k: str(path)):
                headers, rows, _ = wire.wireMessages.__wrapped__(_Context(both))
            names = [h[0] if isinstance(h, tuple) else h for h in headers]
            for row in (dict(zip(names, r)) for r in rows):
                if row['Media']:
                    self.assertIn(f"wire-account-{row['Account']}", row['Media'])
            _, media, _ = _patched(wire.wireMedia, both)
            matched = collections.Counter(row['Account'] for row in media if row['Format'])
            self.assertEqual(matched, {ACCOUNT: 3, self.SECOND: 3})

    def test_conversation_view_keeps_the_accounts_apart(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, both = self._two_accounts(pathlib.Path(tmp))
            _, messages, _ = _patched(wire.wireMessages, both)
            self.assertEqual(len({row['Conversation ID'] for row in messages}), 1)
            self.assertEqual(len({row['Conversation Key'] for row in messages}), 2)
            self.assertEqual(wire.__artifacts_v2__['wireMessages']['data_views']['conversation']
                             ['conversationDiscriminatorColumn'], 'Conversation Key')


class WireContactsTests(unittest.TestCase):
    def test_contacts_status_self_and_pictures(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, _ = _build(pathlib.Path(tmp))
            names, rows, source = _patched(wire.wireContacts, files)
            self.assertEqual(len(names), 10)
            self.assertEqual({row['Account'] for row in rows}, {ACCOUNT})
            self_row, peer, stranger = rows
            self.assertEqual(self_row['Self'], 'Yes')
            self.assertIsNone(self_row['Connection Status'])
            # A picture cached under an asset id the user no longer has is not shown.
            self.assertEqual(self_row['Profile Picture'], '')
            self.assertEqual(peer['Self'], '')
            # The first ZCONNECTION row by Z_PK decides.
            self.assertEqual(peer['Connection Status'], 'Accepted')
            self.assertEqual(peer['Profile Picture'], 'e:largeUserImages')
            self.assertEqual(peer['Profile Picture Preview'], 'e:smallUserImages')
            self.assertEqual(stranger['Connection Status'], 99)
            self.assertEqual(stranger['Profile Picture'], '')
            self.assertEqual(source.count('\n'), 2)

    def test_no_database_gives_no_rows(self):
        _, rows, source = _patched(wire.wireContacts, [])
        self.assertEqual((rows, source), ([], ''))


if __name__ == '__main__':
    unittest.main()
