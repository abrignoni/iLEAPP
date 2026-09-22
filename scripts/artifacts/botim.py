__artifacts_v2__ = {
    "botimMessages": {
        "name": "BOTIM - Messages",
        "description": "Messages from the BOTIM iOS client's search index",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "BOTIM",
        "notes": "Read from the kFtsMessageTable full text search index in the client's "
                 "t_common_db_<id>.sqlite store. This is the client's own search index of its "
                 "messages, not the primary message store, so it holds the messages the client "
                 "indexed for search rather than necessarily every message, and an examiner should "
                 "treat the count as a lower bound. The message text is in the clear here. Sent is "
                 "the timestamp column, Unix milliseconds. Message is taken from the contentStrings "
                 "array the row carries in its data_extra JSON, the non empty parts joined; the "
                 "table's own content column holds the same text in the search index's concatenated "
                 "form. Type is the client's message type integer, reported as stored: no mapping was "
                 "established from the closed source client, and on the devices tested the rows "
                 "carrying text held one value. Session ID is the conversation the message belongs "
                 "to, and Sender UID is the sender, resolved to Sender Name against the user index in "
                 "the same store where it holds a matching row. Field mapping was done against two "
                 "private samples; no sample data is recorded for them.",
        "paths": ('*/Library/DB/t_common_db_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    },
    "botimUsers": {
        "name": "BOTIM - Users",
        "description": "Users from the BOTIM iOS client's search index",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "BOTIM",
        "notes": "Read from the kFtsUserTable full text search index in t_common_db_<id>.sqlite. A "
                 "row is a user the client indexed, which includes the account's contacts and the "
                 "senders of indexed messages, so a row is not by itself evidence of a conversation. "
                 "UID is the user id the message index refers to. Name is the client's own searchable "
                 "name string for the user, from the content column. The row also carries a data_extra "
                 "JSON with separate name parts under short keys (fn, ln, nn); these are reported as "
                 "stored under their own columns rather than being given meaning, because no source "
                 "for the keys in the closed source client was established. Field mapping was done "
                 "against two private samples; no sample data is recorded for them.",
        "paths": ('*/Library/DB/t_common_db_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
}

import json
import os
import re

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, convert_unix_ts_to_utc)

REQUIRED_TABLES = {'kFtsMessageTable', 'kFtsUserTable'}


def _tables(db_path):
    return {row[0] for row in get_sqlite_db_records(
        db_path, "SELECT name FROM sqlite_master WHERE type='table'")}


def _stores(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.basename(file_found.replace('\\', '/')).endswith('.sqlite'):
            continue
        if not re.search(r'/t_common_db_\d+\.sqlite$', file_found.replace('\\', '/')):
            continue
        if REQUIRED_TABLES <= _tables(file_found):
            yield file_found


def _content_strings(data_extra):
    if not data_extra:
        return ''
    try:
        parts = json.loads(data_extra).get('contentStrings') or []
    except (ValueError, TypeError):
        return ''
    return ' '.join(str(part) for part in parts if part)


def _users_by_uid(db_path):
    users = {}
    for row in get_sqlite_db_records(db_path, 'SELECT uid, content FROM kFtsUserTable'):
        if row[0] is not None:
            users[str(row[0])] = (row[1] or '').rstrip(',')
    return users


@artifact_processor
def botimMessages(context):
    data_headers = (
        ('Sent', 'datetime'),
        'Type (as stored)',
        'Session ID',
        'Sender UID',
        'Sender Name',
        'Message',
        'Source File',
    )
    data_list = []
    source_paths = []

    for db_path in _stores(context):
        users = _users_by_uid(db_path)
        query = ('SELECT timestamp, type, sessionId, senderUid, content, data_extra '
                 'FROM kFtsMessageTable')
        rows = 0
        for row in get_sqlite_db_records(db_path, query):
            sender = str(row[3]) if row[3] is not None else ''
            message = _content_strings(row[5]) or (row[4] or '').rstrip(',')
            data_list.append((
                convert_unix_ts_to_utc(row[0] / 1000) if row[0] else '',
                row[1] if row[1] is not None else '',
                row[2] or '',
                sender,
                users.get(sender, ''),
                message,
                context.get_relative_path(db_path),
            ))
            rows += 1
        if rows:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def botimUsers(context):
    data_headers = (
        'UID',
        'Name',
        'fn (as stored)',
        'ln (as stored)',
        'nn (as stored)',
        'Source File',
    )
    data_list = []
    source_paths = []

    for db_path in _stores(context):
        rows = 0
        for row in get_sqlite_db_records(db_path, 'SELECT uid, content, data_extra FROM kFtsUserTable'):
            extra = {}
            if row[2]:
                try:
                    extra = json.loads(row[2])
                except (ValueError, TypeError):
                    extra = {}
            data_list.append((
                row[0] if row[0] is not None else '',
                (row[1] or '').rstrip(','),
                extra.get('fn', ''),
                extra.get('ln', ''),
                extra.get('nn', ''),
                context.get_relative_path(db_path),
            ))
            rows += 1
        if rows:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)
