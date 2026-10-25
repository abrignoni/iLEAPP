#!/usr/bin/env python3
"""Build a SYNTHETIC Messages database (sms.db) for the sms* deep-field artifacts.

Everything here is fabricated: handles are in the reserved 555-01xx range, texts are fixed
sentences, GUIDs are derived from a fixed namespace, and times are fixed offsets from one base
date. Nothing comes from a real device. The table and column layout follows the Messages
database of iOS 26 (message, handle, chat, chat_message_join, attachment, message_attachment_join,
chat_recoverable_message_join, recoverable_message_part), reduced to the columns the artifacts read
plus a few unrelated ones, and the blobs follow the formats the artifacts decode:

* attributedBody, edit versions and part_text: NSAttributedString typedstream archives, written
  here by ``typedstream_bytes`` from the byte layout of the format (class names, a length-prefixed
  UTF-8 string, the attribute dictionary), and read back by the same library the artifacts use.
* message_summary_info: binary property list with the keys ec, ep, otr, rp.
* payload_data: NSKeyedArchiver archive, written by ``keyed_archive`` with plistlib.

    python synthetic_sms_deep.py out.db [ios26|ios16]

``build(path, variant)`` writes the file and returns {name: expected} counts the tests compare
against; ``variant`` 'ios16' leaves out the columns and tables older iOS versions do not have.
"""
import plistlib
import sqlite3
import sys
import uuid

_NS = uuid.UUID('12345678-1234-5678-1234-567812345678')
# 2026-03-01 12:00:00 UTC as Cocoa seconds
BASE = 794059200.0
NS = 1_000_000_000

ME = '+15550100000'
ALICE = '+15550100001'
BOB = '+15550100002'

_HEAD = (b'\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x19NSMutableAttributedString\x00'
         b'\x84\x84\x12NSAttributedString\x00\x84\x84\x08NSObject\x00\x85\x92\x84\x84\x84\x0f'
         b'NSMutableString\x01\x84\x84\x08NSString\x01\x95\x84\x01+')
_TAIL = (b'\x86\x84\x02iI\x01{count}\x92\x84\x84\x84\x0cNSDictionary\x00\x95\x84\x01i\x01\x92\x84\x98'
         b'\x98\x1d__kIMMessagePartAttributeName\x86\x92\x84\x84\x84\x08NSNumber\x00\x84\x84\x07'
         b'NSValue\x00\x95\x84\x01*\x84\x9b\x9b\x00\x86\x86\x86')


def _length(n):
    if n < 128:
        return bytes([n])
    return b'\x81' + n.to_bytes(2, 'little')


def typedstream_bytes(text):
    """An NSAttributedString typedstream archive holding ``text``."""
    raw = text.encode('utf-8')
    return _HEAD + _length(len(raw)) + raw + _TAIL.replace(b'{count}', _length(len(text)))


def keyed_archive(root):
    """An NSKeyedArchiver archive whose root object is the dict ``root`` of strings and ints.

    Dict values that are dicts with the keys ``NS.relative`` (and optionally ``NS.base``) are
    archived as NSURL objects, the way Messages stores a URL.
    """
    objects = ['$null']

    def add(value):
        if isinstance(value, dict) and 'NS.relative' in value:
            objects.append(None)
            index = len(objects) - 1
            relative = add(value['NS.relative'])
            base = add(value.get('NS.base'))
            klass = add({'$classname': 'NSURL', '$classes': ['NSURL', 'NSObject']})
            objects[index] = {'NS.base': plistlib.UID(base), 'NS.relative': plistlib.UID(relative),
                              '$class': plistlib.UID(klass)}
            return index
        if isinstance(value, dict) and '$classname' in value:
            objects.append(value)
            return len(objects) - 1
        if isinstance(value, dict):
            objects.append(None)
            index = len(objects) - 1
            keys = [add(key) for key in value]
            values = [add(item) for item in value.values()]
            klass = add({'$classname': 'NSDictionary', '$classes': ['NSDictionary', 'NSObject']})
            objects[index] = {'NS.keys': [plistlib.UID(k) for k in keys],
                              'NS.objects': [plistlib.UID(v) for v in values],
                              '$class': plistlib.UID(klass)}
            return index
        if value is None:
            return 0
        objects.append(value)
        return len(objects) - 1

    top = add(root)
    return plistlib.dumps({'$archiver': 'NSKeyedArchiver', '$version': 100000,
                           '$objects': objects, '$top': {'root': plistlib.UID(top)}},
                          fmt=plistlib.PlistFormat.FMT_BINARY)


def guid(label):
    return str(uuid.uuid5(_NS, label)).upper()


def cocoa_ns(offset_seconds):
    return int((BASE + offset_seconds) * NS)


_MESSAGE_COLUMNS = (
    ('ROWID', 'INTEGER PRIMARY KEY AUTOINCREMENT', False), ('guid', 'TEXT', False),
    ('text', 'TEXT', False), ('handle_id', 'INTEGER DEFAULT 0', False), ('attributedBody', 'BLOB', False),
    ('service', 'TEXT', False), ('account', 'TEXT', False), ('date', 'INTEGER', False),
    ('date_read', 'INTEGER', False), ('date_delivered', 'INTEGER', False),
    ('is_from_me', 'INTEGER DEFAULT 0', False), ('cache_has_attachments', 'INTEGER DEFAULT 0', False),
    ('associated_message_guid', 'TEXT', False), ('associated_message_type', 'INTEGER DEFAULT 0', False),
    ('associated_message_range_location', 'INTEGER DEFAULT 0', False),
    ('associated_message_range_length', 'INTEGER DEFAULT 0', False),
    ('associated_message_emoji', 'TEXT', True), ('balloon_bundle_id', 'TEXT', False),
    ('payload_data', 'BLOB', False), ('message_summary_info', 'BLOB', True),
    ('destination_caller_id', 'TEXT', False), ('reply_to_guid', 'TEXT', True),
    ('thread_originator_guid', 'TEXT', True), ('thread_originator_part', 'TEXT', True),
    ('date_retracted', 'INTEGER DEFAULT 0', True), ('date_edited', 'INTEGER DEFAULT 0', True),
    ('part_count', 'INTEGER', True),
)

_OTHER_TABLES = '''
CREATE TABLE handle (ROWID INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT, service TEXT);
CREATE TABLE chat (ROWID INTEGER PRIMARY KEY AUTOINCREMENT, guid TEXT, chat_identifier TEXT,
                   display_name TEXT, service_name TEXT);
CREATE TABLE chat_handle_join (chat_id INTEGER, handle_id INTEGER);
CREATE TABLE chat_message_join (chat_id INTEGER, message_id INTEGER, message_date INTEGER DEFAULT 0,
                                PRIMARY KEY (chat_id, message_id));
CREATE TABLE attachment (ROWID INTEGER PRIMARY KEY AUTOINCREMENT, guid TEXT, filename TEXT,
                         mime_type TEXT, transfer_name TEXT, total_bytes INTEGER, is_sticker INTEGER DEFAULT 0);
CREATE TABLE message_attachment_join (message_id INTEGER, attachment_id INTEGER);
'''

_RECOVERABLE_TABLES = '''
CREATE TABLE chat_recoverable_message_join (chat_id INTEGER, message_id INTEGER, delete_date INTEGER,
                                            ck_sync_state INTEGER DEFAULT 0, PRIMARY KEY (chat_id, message_id));
CREATE TABLE recoverable_message_part (chat_id INTEGER, message_id INTEGER, part_index INTEGER,
                                       delete_date INTEGER, part_text BLOB, ck_sync_state INTEGER DEFAULT 0,
                                       PRIMARY KEY (chat_id, message_id, part_index));
'''


def _schema(variant):
    """The iOS 26 layout, or the same without the columns and tables older versions lack."""
    new = variant == 'ios26'
    columns = ', '.join(f'{name} {decl}' for name, decl, newer in _MESSAGE_COLUMNS if new or not newer)
    return f'CREATE TABLE message ({columns});' + _OTHER_TABLES + (_RECOVERABLE_TABLES if new else '')


def build(path, variant='ios26'):
    """Write the database to ``path``; return the expected counts the tests check."""
    db = sqlite3.connect(path)
    db.executescript(_schema(variant))
    new = variant == 'ios26'
    for handle in (ALICE, BOB):
        db.execute('INSERT INTO handle (id, service) VALUES (?, ?)', (handle, 'iMessage'))
    db.execute('INSERT INTO chat (guid, chat_identifier, display_name, service_name) VALUES (?,?,?,?)',
               ('iMessage;-;' + ALICE, ALICE, '', 'iMessage'))
    db.execute('INSERT INTO chat (guid, chat_identifier, display_name, service_name) VALUES (?,?,?,?)',
               ('iMessage;+;chat-synthetic', 'chat-synthetic', 'Synthetic Group', 'iMessage'))
    db.execute('INSERT INTO chat_handle_join VALUES (1, 1)')
    db.execute('INSERT INTO chat_handle_join VALUES (2, 1)')
    db.execute('INSERT INTO chat_handle_join VALUES (2, 2)')

    next_row = [0]

    def message(label, offset, chat, from_me, handle=1, text=None, body=None, **extra):
        values = {'guid': guid(label), 'text': text, 'handle_id': 0 if from_me else handle,
                  'attributedBody': body, 'service': 'iMessage', 'date': cocoa_ns(offset),
                  'is_from_me': from_me, 'destination_caller_id': ME}
        values.update(extra)
        names = [c for c in values]
        db.execute(f'INSERT INTO message ({",".join(names)}) VALUES ({",".join("?" * len(names))})',
                   [values[c] for c in names])
        next_row[0] += 1
        if chat:
            db.execute('INSERT INTO chat_message_join (chat_id, message_id, message_date) VALUES (?,?,?)',
                       (chat, next_row[0], cocoa_ns(offset)))
        return next_row[0]

    expected = {}

    # 1 plain messages: text column, attributedBody only, and a group message from Bob
    message('plain-1', 0, 1, 0, text='Synthetic plain message one')
    message('plain-2', 60, 1, 1, body=typedstream_bytes('Synthetic body-only message'))
    message('plain-3', 120, 2, 0, handle=2, text='Synthetic group message')

    # 2 reactions: loved, liked removal, emoji, sticker, one pointing at a missing message, one of type 2
    message('react-love', 130, 1, 1, text='Loved a message', associated_message_type=2000,
            associated_message_guid='p:0/' + guid('plain-1'), associated_message_range_location=0,
            associated_message_range_length=27)
    message('react-like-remove', 140, 1, 0, text='', associated_message_type=3001,
            associated_message_guid='p:0/' + guid('plain-2'))
    message('react-emoji', 150, 2, 1, text='Reacted to a message', associated_message_type=2006,
            associated_message_guid='p:0/' + guid('plain-3'),
            **({'associated_message_emoji': '\U0001F44D'} if new else {}))
    sticker = message('react-sticker', 160, 1, 0, text='', associated_message_type=1000,
                      associated_message_guid='p:0/' + guid('plain-1'), associated_message_range_location=2,
                      associated_message_range_length=5)
    message('react-missing', 170, 1, 0, text='Laughed at a message', associated_message_type=2003,
            associated_message_guid='bp:' + guid('gone'))
    message('react-type2', 180, 1, 0, text='�', associated_message_type=2,
            associated_message_guid=guid('plain-1'), balloon_bundle_id='com.example.balloon')
    db.execute("INSERT INTO attachment (guid, filename, mime_type, transfer_name, total_bytes, is_sticker) "
               "VALUES (?,?,?,?,?,1)", (guid('att-sticker'), '~/Library/SMS/Attachments/x/sticker.png',
                                        'image/png', 'sticker.png', 10))
    db.execute('INSERT INTO message_attachment_join VALUES (?, 1)', (sticker,))
    expected['reactions'] = 5   # love, like removal, emoji, sticker, missing target; type 2 is excluded

    if new:
        # 3 edited message: three versions of part 0; unsent message; unsent part of a multi-part message
        history = {'0': [{'d': BASE + 200.0, 't': typedstream_bytes('First draft')},
                         {'d': BASE + 230.0, 't': typedstream_bytes('Second draft')},
                         {'d': BASE + 290.0, 't': typedstream_bytes('Final text')}]}
        summary = plistlib.dumps({'ec': history, 'ep': [0], 'otr': {'0': {'lo': 0, 'le': 11}}, 'ust': True},
                                 fmt=plistlib.PlistFormat.FMT_BINARY)
        message('edited', 200, 1, 1, body=typedstream_bytes('Final text'), message_summary_info=summary,
                date_edited=cocoa_ns(290), part_count=1)
        unsent = plistlib.dumps({'rp': [0], 'otr': {'0': {'lo': 0, 'le': 18}}, 'ust': True},
                                fmt=plistlib.PlistFormat.FMT_BINARY)
        message('unsent', 300, 1, 0, message_summary_info=unsent, date_edited=cocoa_ns(330), part_count=0)
        partial = plistlib.dumps({'rp': [1], 'otr': {'0': {'lo': 0, 'le': 4}, '1': {'lo': 5, 'le': 9}}},
                                 fmt=plistlib.PlistFormat.FMT_BINARY)
        message('partial-unsent', 400, 1, 1, body=typedstream_bytes('Kept'), message_summary_info=partial,
                date_edited=cocoa_ns(415), part_count=1)
        # damaged summary info and an edit history entry that is not a typedstream
        message('bad-summary', 500, 1, 1, text='Damaged summary', message_summary_info=b'not a plist',
                date_edited=cocoa_ns(510))
        broken = plistlib.dumps({'ec': {'0': [{'d': BASE + 600.0, 't': b'garbage'},
                                              {'d': BASE + 620.0, 't': typedstream_bytes('Repaired')}]},
                                 'otr': {'0': {'lo': 0, 'le': 7}}}, fmt=plistlib.PlistFormat.FMT_BINARY)
        message('broken-version', 600, 1, 1, body=typedstream_bytes('Repaired'), message_summary_info=broken,
                date_edited=cocoa_ns(620))
        expected['edit_history_rows'] = 3 + 2          # 3 versions + 2 versions (one undecodable)
        expected['unsent_rows'] = 2                    # unsent, partial-unsent

        # 4 replies: one with the originator present, one whose originator is missing
        message('reply-1', 700, 1, 0, text='Synthetic reply', thread_originator_guid=guid('plain-1'),
                thread_originator_part='0:0:27')
        message('reply-2', 710, 1, 1, text='Orphan reply', thread_originator_guid=guid('deleted-original'),
                thread_originator_part='0:0:5')
        expected['replies'] = 2

        # 5 recently deleted: a message kept without a chat link, and a deleted part of a linked message
        kept = message('deleted-1', 800, None, 1, body=typedstream_bytes('Synthetic deleted message'))
        db.execute('INSERT INTO chat_recoverable_message_join VALUES (1, ?, ?, 1)', (kept, cocoa_ns(900)))
        multipart = message('multipart', 810, 1, 0, text='Remaining part')
        db.execute('INSERT INTO recoverable_message_part VALUES (1, ?, 1, ?, ?, 1)',
                   (multipart, cocoa_ns(905), typedstream_bytes('Synthetic deleted part')))
        db.execute('INSERT INTO recoverable_message_part VALUES (1, ?, 2, ?, ?, 1)',
                   (multipart, cocoa_ns(906), b'unreadable'))
        expected['recently_deleted'] = 1
        expected['recently_deleted_parts'] = 2

    # 6 payloads: a link preview, an older-format link preview, an app message, an undecodable payload
    link = {'richLinkIsPlaceholder': False,
            'richLinkMetadata': {'URL': {'NS.relative': 'https://example.com/page'},
                                 'originalURL': {'NS.relative': 'https://example.com/original'},
                                 'title': 'Synthetic title', 'summary': 'Synthetic summary',
                                 'siteName': 'Example', 'itemType': 'article', 'version': 1}}
    message('link-1', 1000, 1, 1, text='https://example.com/page', balloon_bundle_id='com.apple.messages.URLBalloonProvider',
            payload_data=keyed_archive(link))
    old_link = {'hasCompletedFetch': True, 'hasFetchedSubresources': True,
                'metadata': {'URL': {'NS.relative': 'https://example.org/'}, 'title': 'Old format', 'version': 1}}
    message('link-2', 1010, 1, 0, text='https://example.org/', payload_data=keyed_archive(old_link))
    app = {'an': 'ExampleApp', 'ldtext': 'Example summary', 'layoutClass': 'MSMessageTemplateLayout',
           'userInfo': {'caption': 'Synthetic caption', 'subcaption': 'Synthetic subcaption',
                        'image-title': 'Synthetic image title'},
           'URL': {'NS.relative': 'data:example?x=1'}, 'sessionIdentifier': guid('session')}
    message('app-1', 1020, 1, 1, text='￼',
            balloon_bundle_id='com.apple.messages.MSMessageExtensionBalloonPlugin:0000000000:com.example.app',
            payload_data=keyed_archive(app))
    message('app-2', 1030, 1, 0, text='￼', balloon_bundle_id='com.example.handwriting',
            payload_data=b'\x01\x02 not a property list')
    message('chatbot', 1040, 1, 0, text='Bot message', balloon_bundle_id='com.apple.messages.chatbot')
    expected['link_previews'] = 2
    expected['app_messages'] = 2

    db.commit()
    db.close()
    return expected


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'ios26')
