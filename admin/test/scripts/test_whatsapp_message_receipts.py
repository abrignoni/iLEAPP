"""whatsAppMessageReceipts links receipts to messages and reactions (SYNTHETIC databases)."""
import os
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.artifacts import whatsAppMessageReceipts as module

GROUP_CHAT = '100@g.us'
USER = '200@lid'
ITEM, REACTION, MESSAGE, SEND, PLAYED, CHAT = 5, 13, 14, 0, 3, 11


def _varint(value):
    out = bytearray()
    while True:
        low = value & 0x7f
        value >>= 7
        if value:
            out.append(low | 0x80)
        else:
            out.append(low)
            return bytes(out)


def _text(field, value):
    raw = value if isinstance(value, bytes) else value.encode()
    return _varint(field << 3 | 2) + _varint(len(raw)) + raw


def _int(field, value):
    return _varint(field << 3) + _varint(value)


def shape_one(key, emoji):
    entry = _text(1, key) + _text(2, USER) + _text(3, emoji) + _int(4, 1_790_000_000_000)
    return _text(7, _text(1, entry))


def shape_two(key, emoji):
    entry = _text(1, key) + _text(2, emoji) + _int(3, 1_790_000_000_000)
    return _text(7, _text(2, entry))


def make_infra(folder, rows, played=True):
    path = os.path.join(folder, 'MessagingInfraDB_v2')
    os.makedirs(path)
    path = os.path.join(path, 'MessagingInfraDatabase.sqlite')
    column = ', played_timestamp INTEGER' if played else ''
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE receipt_device (_id INTEGER PRIMARY KEY, stanza_id TEXT, chat_jid TEXT, user_jid TEXT, '
               f'device_id INTEGER, send_timestamp INTEGER, delivered_timestamp INTEGER, read_timestamp INTEGER{column})')
    for stanza, chat in rows:
        db.execute('INSERT INTO receipt_device (stanza_id, chat_jid, user_jid, device_id, send_timestamp, '
                   'delivered_timestamp, read_timestamp) VALUES (?, ?, ?, 0, 1790000000, 1790000001, 1790000002)',
                   (stanza, chat, USER))
    db.commit()
    db.close()
    return path


def make_chat(folder, messages):
    """messages: (stanza id, chat JID, text, ZRECEIPTINFO)."""
    path = os.path.join(folder, 'ChatStorage.sqlite')
    db = sqlite3.connect(path)
    db.executescript('''
        CREATE TABLE ZWACHATSESSION (Z_PK INTEGER PRIMARY KEY, ZCONTACTJID TEXT, ZPARTNERNAME TEXT);
        CREATE TABLE ZWAMESSAGEINFO (Z_PK INTEGER PRIMARY KEY, ZRECEIPTINFO BLOB);
        CREATE TABLE ZWAMESSAGE (Z_PK INTEGER PRIMARY KEY, ZSTANZAID TEXT, ZMESSAGEDATE REAL, ZMESSAGETYPE INTEGER,
                                 ZTEXT TEXT, ZCHATSESSION INTEGER, ZMESSAGEINFO INTEGER);''')
    chats = {}
    for number, (stanza, chat, text, blob) in enumerate(messages, 1):
        chats.setdefault(chat, len(chats) + 1)
        db.execute('INSERT OR IGNORE INTO ZWACHATSESSION VALUES (?, ?, ?)', (chats[chat], chat, 'Chat ' + chat))
        db.execute('INSERT INTO ZWAMESSAGEINFO VALUES (?, ?)', (number, blob))
        db.execute('INSERT INTO ZWAMESSAGE VALUES (?, ?, 811692800.0, 0, ?, ?, ?)',
                   (number, stanza, text, chats[chat], number))
    db.commit()
    db.close()
    return path


def run(paths):
    context = SimpleNamespace(get_files_found=lambda: paths, get_relative_path=os.path.basename)
    return module.whatsAppMessageReceipts.__wrapped__(context)


class ReceiptLinkTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name

    def group(self, name):
        path = os.path.join(self.root, name)
        os.makedirs(path)
        return path

    def test_message_and_both_reaction_shapes(self):
        folder = self.group('a')
        infra = make_infra(folder, [('M1', GROUP_CHAT), ('R1', GROUP_CHAT), ('R2', GROUP_CHAT), ('X', GROUP_CHAT)])
        chat = make_chat(folder, [('M1', GROUP_CHAT, 'sent', None),
                                  ('P1', GROUP_CHAT, 'one', shape_one('R1', 'A')),
                                  ('P2', GROUP_CHAT, 'two', shape_two('R2', 'B'))])
        rows = {row[-1]: row for row in run([infra, chat])[1]}
        self.assertEqual((rows['M1'][ITEM], rows['M1'][MESSAGE]), ('Message', 'sent'))
        self.assertEqual((rows['R1'][ITEM], rows['R1'][REACTION], rows['R1'][MESSAGE]), ('Reaction', 'A', 'one'))
        self.assertEqual((rows['R2'][ITEM], rows['R2'][REACTION], rows['R2'][MESSAGE]), ('Reaction', 'B', 'two'))
        self.assertEqual(rows['X'][ITEM], 'Not linked')

    def test_same_stanza_in_another_chat_does_not_link(self):
        folder = self.group('a')
        infra = make_infra(folder, [('M1', GROUP_CHAT)])
        chat = make_chat(folder, [('M1', '999@g.us', 'other chat', None)])
        self.assertEqual(run([infra, chat])[1][0][ITEM], 'Not linked')

    def test_missing_siblings_keep_the_receipt(self):
        infra = make_infra(self.group('a'), [('M1', GROUP_CHAT)])
        headers, rows, source = run([infra])
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][ITEM], 'Not linked')
        self.assertEqual(source, infra)

    def test_app_groups_do_not_cross(self):
        first, second = self.group('a'), self.group('b')
        infra_a = make_infra(first, [('M1', GROUP_CHAT)])
        infra_b = make_infra(second, [('M1', GROUP_CHAT)])
        chat_a = make_chat(first, [('M1', GROUP_CHAT, 'from a', None)])
        chat_b = make_chat(second, [('M1', GROUP_CHAT, 'from b', None)])
        rows = run([infra_a, chat_a, infra_b, chat_b])[1]
        self.assertEqual(sorted(row[MESSAGE] for row in rows), ['from a', 'from b'])

    def test_absent_played_column(self):
        folder = self.group('a')
        infra = make_infra(folder, [('M1', GROUP_CHAT)], played=False)
        chat = make_chat(folder, [('M1', GROUP_CHAT, 'sent', None)])
        row = run([infra, chat])[1][0]
        self.assertEqual(row[PLAYED], '')
        self.assertTrue(row[SEND])

    def test_bad_blob_is_logged_with_its_row_and_others_still_link(self):
        folder = self.group('a')
        infra = make_infra(folder, [('R2', GROUP_CHAT)])
        chat = make_chat(folder, [('P0', GROUP_CHAT, 'bad', b'\xff\xff\xff'),
                                  ('P2', GROUP_CHAT, 'two', shape_two('R2', 'B'))])
        with mock.patch.object(module, 'logfunc') as log:
            rows = run([infra, chat])[1]
        self.assertEqual(rows[0][ITEM], 'Reaction')
        logged = ' '.join(str(call.args[0]) for call in log.call_args_list)
        self.assertIn('ZWAMESSAGEINFO row 1', logged)
        self.assertIn('ChatStorage.sqlite', logged)

    def test_blobs_are_not_decoded_when_every_key_is_a_message(self):
        folder = self.group('a')
        infra = make_infra(folder, [('M1', GROUP_CHAT)])
        chat = make_chat(folder, [('M1', GROUP_CHAT, 'sent', shape_two('R9', 'B'))])
        with mock.patch.object(module.blackboxprotobuf, 'decode_message') as decode:
            run([infra, chat])
        decode.assert_not_called()


if __name__ == '__main__':
    unittest.main()
