__artifacts_v2__ = {
    "weChatMessages": {
        "name": "WeChat - Messages",
        "description": "Chat messages from the WeChat (Weixin) iOS client, with the body as stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "WeChat",
        "notes": "WeChat keeps one message table per conversation, named Chat_ followed by the MD5 of "
                 "the conversation's WeChat id, and it splits these across several databases in the "
                 "account's DB folder (MM.sqlite and message_1.sqlite, message_2.sqlite and so on). "
                 "Every one is read. On the two devices tested the message body was in the clear, so "
                 "the Message column carries the text as stored; a row whose type is not text carries "
                 "the client's own payload for that type instead, also as stored. Sent is CreateTime, "
                 "Unix seconds. Direction is the Des column and is reported as stored, because no "
                 "source for the mapping of its two values was established from the closed source "
                 "client; it held 0 and 1 on both devices. Type is the client's message type integer, "
                 "reported as stored: the text messages held type 1, and the other values (which "
                 "accompany images, stickers, links, calls and system notices) are reported without a "
                 "mapping. Chat Partner is the conversation's WeChat id, recovered by matching the "
                 "table's MD5 against the Friend table, and Chat Partner Name is that friend's "
                 "nickname where the contact store holds one. A message table whose MD5 has no "
                 "matching friend is still reported, with the id and name blank, so a conversation "
                 "with a contact the store no longer holds is not lost; on the device tested this "
                 "left 21 of 131 rows without a resolved name. Field mapping was done against two "
                 "private samples; no sample data is recorded for them. The account id is the MD5 "
                 "folder under Documents, and every account folder in the extraction is read.",
        "paths": ('*/Documents/*/DB/message_*.sqlite*',
                  '*/Documents/*/DB/MM.sqlite*',
                  '*/Documents/*/DB/WCDB_Contact.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    },
    "weChatContacts": {
        "name": "WeChat - Contacts",
        "description": "Contacts recorded by the WeChat (Weixin) iOS client",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "WeChat",
        "notes": "Read from the Friend table of WCDB_Contact.sqlite. A row is a contact the client "
                 "holds, which includes the user's friends, chat rooms, and WeChat's own official "
                 "accounts (WeChat-Team, File Transfer, New Friends and the like), so a row is not by "
                 "itself evidence that the account communicated with that contact. WeChat ID is the "
                 "userName column. Nickname is read from the first protobuf field of the "
                 "dbContactRemark blob, which held the contact's display name on every row checked "
                 "against a known official account (the WeChat-Team, File Transfer and New Friends "
                 "accounts each resolved to their published name). The other fields of that blob are "
                 "not decoded here, because no source for their meaning in the closed source client "
                 "was established. Type is reported as stored. Field mapping was done against two "
                 "private samples; no sample data is recorded for them.",
        "paths": ('*/Documents/*/DB/WCDB_Contact.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
}

import hashlib
import os
import re

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, convert_unix_ts_to_utc)
from scripts import blackboxprotobuf

CHAT_TABLE = re.compile(r'^Chat_[0-9a-f]{32}$')
# Chat_<md5>: the 32 hex after the underscore is MD5(userName).
CHAT_MD5 = re.compile(r'^Chat_([0-9a-f]{32})')


def _account_dir(path):
    """The .../Documents/<md5> account directory a WeChat store sits in."""
    found = re.match(r'(?P<root>.*/Documents/[0-9a-f]{32})/', path.replace('\\', '/'))
    if found:
        return found.group('root')
    return os.path.dirname(os.path.dirname(path.replace('\\', '/')))


def _tables(db_path):
    return [row[0] for row in get_sqlite_db_records(
        db_path, "SELECT name FROM sqlite_master WHERE type='table'")]


def _nickname(blob):
    """The display name WeChat packs in the first field of dbContactRemark."""
    if not blob:
        return ''
    try:
        decoded, _ = blackboxprotobuf.decode_message(bytes(blob))
    except Exception:  # pylint: disable=broad-exception-caught
        return ''
    value = decoded.get('1')
    if isinstance(value, (bytes, bytearray)):
        try:
            return bytes(value).decode('utf-8')
        except UnicodeDecodeError:
            return ''
    return ''


def _friends_by_md5(contact_path):
    """MD5(userName) -> (userName, nickname), for linking a Chat table to a contact."""
    by_md5 = {}
    if not contact_path:
        return by_md5
    for row in get_sqlite_db_records(contact_path, 'SELECT userName, dbContactRemark FROM Friend'):
        user = row[0]
        if not user:
            continue
        by_md5[hashlib.md5(user.encode('utf-8')).hexdigest()] = (user, _nickname(row[1]))
    return by_md5


def _stores(context):
    """Group WeChat message databases and the contact store by account directory."""
    grouped = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        name = os.path.basename(file_found.replace('\\', '/'))
        entry = grouped.setdefault(_account_dir(file_found), {})
        if name == 'WCDB_Contact.sqlite':
            entry['contact'] = file_found
        elif name == 'MM.sqlite' or re.match(r'message_\d+\.sqlite$', name):
            entry.setdefault('messages', []).append(file_found)
    return grouped


@artifact_processor
def weChatMessages(context):
    data_headers = (
        ('Sent', 'datetime'),
        'Direction (as stored)',
        'Type (as stored)',
        'Message',
        'Chat Partner',
        'Chat Partner Name',
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_stores(context).items()):
        message_dbs = entry.get('messages') or []
        if not message_dbs:
            continue
        friends = _friends_by_md5(entry.get('contact'))
        for db_path in sorted(message_dbs):
            rows = 0
            for table in _tables(db_path):
                found = CHAT_MD5.match(table)
                if not found or not CHAT_TABLE.match(table):
                    continue
                user, nickname = friends.get(found.group(1), ('', ''))
                query = f'SELECT CreateTime, Des, Type, Message FROM "{table}"'
                for row in get_sqlite_db_records(db_path, query):
                    data_list.append((
                        convert_unix_ts_to_utc(row[0]) if row[0] else '',
                        row[1] if row[1] is not None else '',
                        row[2] if row[2] is not None else '',
                        row[3] or '',
                        user,
                        nickname,
                        context.get_relative_path(db_path),
                    ))
                    rows += 1
            if rows:
                source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def weChatContacts(context):
    data_headers = (
        'WeChat ID',
        'Nickname',
        'Type (as stored)',
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_stores(context).items()):
        contact_path = entry.get('contact')
        if not contact_path:
            continue
        rows = 0
        for row in get_sqlite_db_records(contact_path,
                                         'SELECT userName, dbContactRemark, type FROM Friend'):
            if not row[0]:
                continue
            data_list.append((
                row[0],
                _nickname(row[1]),
                row[2] if row[2] is not None else '',
                context.get_relative_path(contact_path),
            ))
            rows += 1
        if rows:
            source_paths.append(contact_path)

    return data_headers, data_list, '\n'.join(source_paths)
