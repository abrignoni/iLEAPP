__artifacts_v2__ = {
    "zoom_ios_chat_messages": {
        "name": "Zoom - Chat Messages",
        "description": "Chat messages the Zoom app stored per conversation, with the direction "
                       "each row records and the file attached where one is linked.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per row of every per conversation message table in the account's own "
                 "store, Documents/data/<account>@xmpp.zoom.us/<account>@xmpp.zoom.us.asyn.db. "
                 "The tables are named for the conversation, so they are found by their name "
                 "pattern rather than listed: the one tested image that holds the store has three "
                 "of them and only one carries rows, six of them. Timestamp is the row's "
                 "millisecond time, reported in UTC, and the six fall inside fifteen minutes of "
                 "one day in the period the image covers. **Direction is recorded, not "
                 "inferred**: the row carries a sent by me flag, and it gives 3 outgoing and 3 "
                 "incoming here, with the sender name on the row agreeing three and three. Two "
                 "messages name a file, and both are attached: the file table in the same store "
                 "names the message and gives the path the app wrote the copy to, and that copy "
                 "was found in the account's own folder inside the same container. The other four "
                 "rows name no file. Message Type, Message State and Read are reported as stored. "
                 "Conversation ID and Source Table hold one value each across the six rows "
                 "because only one conversation table carries any, Message ID and Thread ID are "
                 "identical on every row, and Giphy ID is empty on every row, so none of the six "
                 "is an animation. Tables in this store that nothing here reads are named so the "
                 "omission is visible: the device tables, which hold a certificate, a key and a "
                 "password for the account's device and from which **no key material is "
                 "reported**; the configuration table, 52 rows of app settings; the notification "
                 "store, 11 rows; the session table, whose three rows carry a last update time "
                 "and a last message identifier on one and zeros on the other two; the buddy, "
                 "thread time block and file download tables, which repeat identifiers reported "
                 "elsewhere; and sixteen tables that were empty, among them the end to end "
                 "encrypted message table for this conversation.",
        "paths": ('*/Containers/Data/Application/*/Documents/data/*@xmpp.zoom.us/*.asyn.db*',
                  '*/Containers/Data/Application/*/Documents/data/*@xmpp.zoom.us/*/*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
                           "hickman_ios13": "iOS 13.3.1 | Zoom | 6 rows",
                       },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Attachment",
            }
        },
    },
    "zoom_ios_call_history": {
        "name": "Zoom - Call History",
        "description": "Calls the Zoom app recorded, with the two parties and the coded direction, "
                       "length and state each row stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per row of the call history table in the account's own store. Timestamp "
                 "is Unix seconds, reported in UTC. The one tested image that holds the store has "
                 "a single row, and it carries both party names, a number, and a direction, "
                 "length, state and call type that are stored as numbers whose meanings nothing "
                 "here establishes, so all four are reported as stored rather than translated. "
                 "The caller and callee identifiers are the two accounts the message table shows "
                 "talking to each other, so the row belongs to that conversation. One row cannot "
                 "show what the table looks like on a device with more calls.",
        "paths": ('*/Containers/Data/Application/*/Documents/data/*@xmpp.zoom.us/*.asyn.db*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
                           "hickman_ios13": "iOS 13.3.1 | Zoom | 1 row",
                       },
    },
    "zoom_ios_shared_files": {
        "name": "Zoom - Shared Files",
        "description": "Files the Zoom app recorded as shared in a chat, with the owner, the size "
                       "and the copy stored on the device where there is one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per row of the file table in the account's own store, joined to the web "
                 "file and file share tables on the identifier they share for the recorded size, "
                 "the owner and the time the file was shared. Shared is a millisecond time, "
                 "reported in UTC, taken from the share record and falling back to the web file "
                 "record and then to the file row, which on the two rows here differ from each "
                 "other by under half a second. Both rows on the one tested image that holds the "
                 "store were found on the device and are attached. File Bytes equals Recorded "
                 "Size (as stored) on both, at 188173 and 188051 bytes, which is the file on disk "
                 "agreeing with what the store wrote down. Direction comes from the row's own "
                 "sent by me flag and gives one each way. The file is looked for by the name the "
                 "store recorded, inside the account's own folder in the same container, so a "
                 "file from another account or another app cannot be picked up.",
        "paths": ('*/Containers/Data/Application/*/Documents/data/*@xmpp.zoom.us/*.asyn.db*',
                  '*/Containers/Data/Application/*/Documents/data/*@xmpp.zoom.us/*/*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
                           "hickman_ios13": "iOS 13.3.1 | Zoom | 2 rows",
                       },
    },
    "zoom_ios_giphy": {
        "name": "Zoom - Giphy Images",
        "description": "Animations the Zoom app recorded from the Giphy picker, with the address "
                       "and the copy stored on the device where there is one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per row of the giphy table in the account's own store. A row records an "
                 "animation the app kept from its Giphy picker, with the page address, the mobile "
                 "and full size addresses, and the path it wrote a copy to. All eight rows on the "
                 "one tested image that holds the store were found on the device and are "
                 "attached, looked for by the recorded name inside the account's own folder in "
                 "the same container. The table carries no time, so a row does not say when the "
                 "animation was chosen or whether it was sent. The message table carries a giphy "
                 "identifier column and no message on this image fills it, so none of these eight "
                 "is recorded as having been sent in the conversation the store holds. File "
                 "Present reads Yes on all eight because every one was found.",
        "paths": ('*/Containers/Data/Application/*/Documents/data/*@xmpp.zoom.us/*.asyn.db*',
                  '*/Containers/Data/Application/*/Documents/data/*@xmpp.zoom.us/*/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
                           "hickman_ios13": "iOS 13.3.1 | Zoom | 8 rows",
                       },
    },
}

import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import (artifact_processor, check_in_media, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

_CONTAINER = re.compile(r'(.*/Containers/Data/Application/[^/]+)/', re.I)
_ACCOUNT = re.compile(r'/Documents/data/([^/]+@xmpp\.zoom\.us)/', re.I)


def _stores(files_found):
    '''Every per account asyn.db among the matches, directories and sidecars skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or path.endswith(('-wal', '-shm')):
            continue
        if path.endswith('.asyn.db') and path not in seen:
            seen.append(path)
    return seen


def _container(path):
    '''The app data container a file sits in, or '' when it is not under one.'''
    match = _CONTAINER.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _account(path):
    '''The account folder a file sits under, or ''.'''
    match = _ACCOUNT.search(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _stored_files(files_found):
    '''{(container, account, file name): path} for files under an account's own folders.'''
    index = {}
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or path.endswith(('.asyn.db', '-wal', '-shm')):
            continue
        account = _account(path)
        if account:
            index.setdefault((_container(path), account, os.path.basename(path)), path)
    return index


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        return []
    try:
        return list(get_sqlite_db_records(path, f'SELECT {columns} FROM {table}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Zoom: could not read {table}: {error}')
        return []


def _message_tables(path):
    '''Every per conversation message table in the store.'''
    try:
        rows = get_sqlite_db_records(
            path, "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'msg\\_t\\_%' "
                  "ESCAPE '\\'")
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Zoom: could not list message tables: {error}')
        return []
    return [r[0] for r in rows]


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _unix_to_utc(value):
    '''Unix seconds to an aware UTC datetime, or ''.'''
    if value in (None, '', 0, '0'):
        return ''
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _unix_ms_to_utc(value):
    '''Unix milliseconds to an aware UTC datetime, or ''.'''
    if value in (None, '', 0, '0'):
        return ''
    try:
        return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _attach(index, container, account, local_path):
    '''(media reference, present, size) for a recorded local path, without inventing a match.'''
    name = os.path.basename(_text(local_path))
    if not name:
        return '', '', ''
    path = index.get((container, account, name))
    if not path:
        return '', 'No', ''
    try:
        size = str(os.path.getsize(path))
    except OSError:
        size = ''
    return check_in_media(path, name), 'Yes', size


@artifact_processor
def zoom_ios_chat_messages(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    index = _stored_files(files_found)
    for source_path in _stores(files_found):
        sources.append(source_path)
        container, account = _container(source_path), _account(source_path)
        by_message = {}
        for (message_id, name, local_path) in _rows(
                source_path, 'zoom_mm_file', 'messageID, name, localPath'):
            if message_id:
                by_message[_text(message_id)] = (_text(name), _text(local_path))
        for table in _message_tables(source_path):
            for (stamp, stamp_ms, sender, body, sent_by_me, buddy, group, message_id,
                 msg_type, msg_state, readed, giphy, thread) in _rows(
                    source_path, table,
                    'timeStamp, messageTimestamp, senderName, body, sentByMe, buddyID, groupID, '
                    'messageID, msgType, msgState, readed, giphyID, thread_id'):
                name, local_path = by_message.get(_text(message_id), ('', ''))
                media, present, size = _attach(index, container, account, local_path)
                data_list.append((
                    _unix_ms_to_utc(stamp_ms) or _unix_to_utc(stamp),
                    'Outgoing' if str(sent_by_me) == '1' else 'Incoming',
                    _text(sender), _text(body), media, name, present, size,
                    _text(buddy) or _text(group), _text(message_id), _text(msg_type),
                    _text(msg_state), _text(readed), _text(giphy), _text(thread), table,
                    account,
                ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', 'Sender Name', 'Message',
        ('Attachment', 'media'), 'Attachment Name', 'Attachment Present', 'Attachment Bytes',
        'Conversation ID', 'Message ID', 'Message Type (as stored)', 'Message State (as stored)',
        'Read (as stored)', 'Giphy ID', 'Thread ID', 'Source Table', 'Account',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zoom_ios_call_history(context):
    data_list = []
    sources = []
    for source_path in _stores(context.get_files_found()):
        sources.append(source_path)
        for (stamp, caller_name, callee_name, number, direction, length, state, call_type,
             caller_jid, callee_jid, call_id) in _rows(
                source_path, 'zoom_mm_call_history',
                'time, caller_name, callee_name, number, direction, len, state, call_type, '
                'caller_jid, callee_jid, call_id'):
            data_list.append((
                _unix_to_utc(stamp), _text(caller_name), _text(callee_name), _text(number),
                _text(direction), _text(length), _text(state), _text(call_type),
                _text(caller_jid), _text(callee_jid), _text(call_id), _account(source_path),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Timestamp', 'datetime'), 'Caller Name', 'Callee Name', 'Number',
        'Direction (as stored)', 'Length (as stored)', 'State (as stored)',
        'Call Type (as stored)', 'Caller JID', 'Callee JID', 'Call ID', 'Account',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zoom_ios_shared_files(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    index = _stored_files(files_found)
    for source_path in _stores(files_found):
        sources.append(source_path)
        container, account = _container(source_path), _account(source_path)
        shared = {}
        for (web_id, share_time, share_to, ext) in _rows(
                source_path, 'zoom_mm_file_share_info',
                'web_file_id, share_time, share_to, file_ext'):
            shared[_text(web_id)] = (share_time, _text(share_to), _text(ext))
        web = {}
        for (web_id, name, size, created, owner) in _rows(
                source_path, 'zoom_mm_web_file_info',
                'webFileID, name, fileSize, create_time, owner'):
            web[_text(web_id)] = (_text(name), _text(size), created, _text(owner))
        for (name, local_path, size, stamp, message_id, web_id, sent_by_me,
             owner, downloaded, file_type) in _rows(
                source_path, 'zoom_mm_file',
                'name, localPath, fileSize, timestamp, messageID, webFileID, sentByMe, owner, '
                'downloaded, type'):
            media, present, on_disk = _attach(index, container, account, local_path)
            share_time, share_to, ext = shared.get(_text(web_id), ('', '', ''))
            web_name, web_size, created, web_owner = web.get(_text(web_id), ('', '', '', ''))
            data_list.append((
                _unix_ms_to_utc(share_time) or _unix_ms_to_utc(created)
                or _unix_ms_to_utc(stamp),
                _text(name) or web_name, media, present, on_disk, _text(size) or web_size,
                'Outgoing' if str(sent_by_me) == '1' else 'Incoming',
                _text(owner) or web_owner, share_to, _text(ext), _text(message_id),
                _text(web_id), _text(downloaded), _text(file_type), account,
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Shared', 'datetime'), 'File Name', ('File', 'media'), 'File Present', 'File Bytes',
        'Recorded Size (as stored)', 'Direction', 'Owner', 'Shared To', 'Extension',
        'Message ID', 'Web File ID', 'Downloaded (as stored)', 'File Type (as stored)',
        'Account',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zoom_ios_giphy(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    index = _stored_files(files_found)
    for source_path in _stores(files_found):
        sources.append(source_path)
        container, account = _container(source_path), _account(source_path)
        for (giphy_id, url, local_path, mobile_url, big_url, big_path, tags) in _rows(
                source_path, 'zoom_giphy_info',
                'giphyID, url, localPath, mobileUrl, bigPicUrl, bigPicPath, tags'):
            media, present, size = _attach(index, container, account, local_path)
            if not media:
                media, present, size = _attach(index, container, account, big_path)
            data_list.append((
                _text(giphy_id), media, present, size, _text(url), _text(mobile_url),
                _text(big_url), _text(tags), account,
            ))

    data_list.sort(key=lambda row: str(row[0]))
    data_headers = (
        'Giphy ID', ('Animation', 'media'), 'File Present', 'File Bytes', 'Page URL',
        'Mobile URL', 'Full Size URL', 'Tags', 'Account',
    )
    return data_headers, data_list, '\n'.join(sources)
