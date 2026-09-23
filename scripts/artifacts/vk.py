__artifacts_v2__ = {
    "vkMessages": {
        "name": "VK - Messages",
        "description": "VK Messenger messages from the iOS client's messages store",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "VK",
        "notes": "Read from the message table of messages-store.sqlite in the client's "
                 "VKM_<account id> folder under Application Support, one folder per signed in account. "
                 "Each message row carries a data column holding the message as JSON in the clear, and "
                 "the fields here are read from that JSON: Sent is the date value, Unix seconds; "
                 "Message is the text; From ID is the from_id; Direction is Outgoing when the JSON out "
                 "flag is 1 and Incoming when it is 0, which is the client's own marking of a sent "
                 "message. Conversation is the peer the message belongs to, resolved to a title from "
                 "the peer_title table in the same store where present, otherwise the numeric peer id. "
                 "From Name resolves From ID against the user records in the sibling content-store.sqlite "
                 "where the sender is a user. Attachments lists the types the message JSON records "
                 "(for example photo, doc, audio, link), reported as stored; the attachment bytes "
                 "themselves are cached elsewhere by the client and are not rendered here. Forwarded is "
                 "the count of forwarded messages the JSON carries. Reactions and Action are reported as "
                 "stored. Field mapping was done against a private sample; no sample data is recorded "
                 "for it. The account id is the number in the VKM_ folder name.",
        "paths": ('*/Library/Application Support/VKM_*/messages-store.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Peer",
                "conversationLabelColumn": "Conversation",
                "timeColumn": "Sent",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "senderColumn": "From Name",
                "textColumn": "Message",
            }
        },
    },
    "vkUsers": {
        "name": "VK - Users",
        "description": "VK users cached by the iOS client",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "VK",
        "notes": "Read from the user table of content-store.sqlite in the client's VKM_<account id> "
                 "folder. Each row is a user the client cached, which includes the account's own "
                 "contacts and the senders of cached messages, so a row is not by itself evidence of a "
                 "conversation. User ID, First Name, Last Name, Screen Name, Nickname, Sex, Verified "
                 "and Is Closed are read from the JSON data column, reported as stored. Field mapping "
                 "was done against a private sample; no sample data is recorded for it.",
        "paths": ('*/Library/Application Support/VKM_*/content-store.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
}

import json
import os
import sqlite3

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records,
                               convert_unix_ts_to_utc)


def _load_json(value):
    if isinstance(value, (bytes, bytearray)):
        try:
            value = bytes(value).decode('utf-8')
        except UnicodeDecodeError:
            return {}
    if not isinstance(value, str):
        return {}
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _peer_titles(db_path):
    titles = {}
    try:
        for row in get_sqlite_db_records(db_path, 'SELECT docid, title FROM peer_title'):
            if row[0] is not None and row[1]:
                titles[str(row[0])] = row[1]
    except sqlite3.Error:
        pass
    return titles


def _user_names(content_store_path):
    """Map VK user id to a display name from the sibling content-store user table."""
    names = {}
    if not os.path.exists(content_store_path):
        return names
    try:
        rows = get_sqlite_db_records(content_store_path, 'SELECT id, data FROM user')
    except sqlite3.Error:
        return names
    for row in rows:
        data = _load_json(row[1])
        name = ' '.join(part for part in (data.get('first_name', ''),
                                          data.get('last_name', '')) if part).strip()
        if row[0] is not None and name:
            names[str(row[0])] = name
    return names


def _attachment_types(data):
    types = [att.get('type', '') for att in data.get('attachments') or []
             if isinstance(att, dict) and att.get('type')]
    return ', '.join(types)


@artifact_processor
def vkMessages(context):
    data_headers = (
        ('Sent', 'datetime'), 'Direction', 'From Name', 'Conversation', 'Message', 'From ID',
        'Peer', 'Attachments', 'Forwarded', 'Reactions', 'Action', 'Source File')
    data_list = []
    source_paths = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.replace('\\', '/').endswith('messages-store.sqlite'):
            continue
        titles = _peer_titles(file_found)
        content_store = file_found.replace('messages-store.sqlite', 'content-store.sqlite')
        names = _user_names(content_store)
        try:
            rows = get_sqlite_db_records(file_found, 'SELECT cmid, peer, date, data FROM message')
        except sqlite3.Error:
            continue
        count = 0
        for row in rows:
            data = _load_json(row[3])
            peer = str(row[1]) if row[1] is not None else ''
            from_id = data.get('from_id')
            from_id_str = str(from_id) if from_id is not None else ''
            reactions = data.get('reactions') or []
            action = data.get('action') or ''
            data_list.append((
                convert_unix_ts_to_utc(data.get('date')) if data.get('date') else '',
                'Outgoing' if data.get('out') == 1 else 'Incoming',
                names.get(from_id_str, ''),
                titles.get(peer, peer),
                data.get('text', ''),
                from_id_str,
                peer,
                _attachment_types(data),
                len(data.get('fwd_messages') or []),
                len(reactions) if reactions else '',
                action.get('type', '') if isinstance(action, dict) else action,
                context.get_relative_path(file_found),
            ))
            count += 1
        if count:
            source_paths.append(file_found)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def vkUsers(context):
    data_headers = (
        'User ID', 'First Name', 'Last Name', 'Screen Name', 'Nickname', 'Sex', 'Verified',
        'Is Closed', 'Source File')
    data_list = []
    source_paths = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.replace('\\', '/').endswith('content-store.sqlite'):
            continue
        try:
            rows = get_sqlite_db_records(file_found, 'SELECT id, data FROM user')
        except sqlite3.Error:
            continue
        count = 0
        for row in rows:
            data = _load_json(row[1])
            data_list.append((
                row[0] if row[0] is not None else '',
                data.get('first_name', ''),
                data.get('last_name', ''),
                data.get('screen_name', ''),
                data.get('nickname', ''),
                data.get('sex', ''),
                data.get('is_verified', data.get('verified', '')),
                data.get('is_closed', ''),
                context.get_relative_path(file_found),
            ))
            count += 1
        if count:
            source_paths.append(file_found)

    return data_headers, data_list, '\n'.join(source_paths)
