__artifacts_v2__ = {
    "line": {
        "name": "Line - Messages",
        "description": "Line messages, with the attachment file shown on the message it belongs "
                       "to, and message direction inferred from the absence of a sender reference",
        "author": "Elliot Glendye",
        "creation_date": "2023-11-22",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Line",
        "notes": "Direction is inferred: rows without a sender reference (ZSENDER null) are "
                 "reported as Outgoing and every other row as Incoming. The store holds no user "
                 "row for the signed in account itself on any tested image, so a message that "
                 "account sent has no user row to point at, which is what that reading expects. "
                 "Username names the other party rather than the sender of every row: it was "
                 "filled on all 66 Incoming rows across the four tested images; it is blank on "
                 "every Outgoing row (54 rows) by construction, because the name comes from the "
                 "sender reference. Every Line.sqlite in the extraction is read rather than only "
                 "the first one found. Each Line.sqlite sits under a folder named for an account, "
                 "and Account ID carries that name so rows from two accounts on one device stay "
                 "apart. A store that does not sit under such a folder leaves Account ID blank. "
                 "Rows from all stores are ordered together, newest first. Timestamp is "
                 "ZMESSAGE.ZTIMESTAMP read as Unix milliseconds and shown in UTC. Every tested "
                 "image held one account, so the two account case was checked on a tree built by "
                 "hand from one of them: the rows doubled to sixteen under each of two accounts, "
                 "and a message altered in the added copy appeared only against that copy's "
                 "account. "
                 "Attachment shows the file the app kept for that message, on the message's own "
                 "row. The link is one the app recorded rather than a match on size or time: an "
                 "attachment file is named for the identifier of the message it belongs to with an "
                 "extension added. Measured across the four tested images, all ten attachment "
                 "files were named for a message the store beside them holds, and on the two "
                 "images that also carry an attachment database all four of its rows named one "
                 "too; each of those ten messages carries text the app itself wrote saying a photo "
                 "was sent, which is a second record of the same link. A file whose name matches "
                 "no message is not reported here, so this column does not account for every file "
                 "in the folder. The files sit in the app's own container while the databases sit "
                 "in the app group container, so the two are paired on the account the private "
                 "store folder is named for; a store outside such a folder is paired with nothing. "
                 "Attachment File Name is taken from the attachment database as well as from the "
                 "file, so a name can be reported for a file the extraction does not carry, but "
                 "every recorded row on the two images carrying that database also had its file, "
                 "so a name with no picture was not seen on any tested image. The separate "
                 "Line - Message Attachments artifact reports the same files with the sizes, "
                 "content types and stored timestamps the attachment database carries.",
        "paths": ('**/Line.sqlite*',
                  '*/Containers/*/*/Library/Application Support/PrivateStore/P_*/Messages/MessageAttachmentInfo.sqlite*',
                  '*/Containers/*/*/Library/Application Support/PrivateStore/P_*/Message Attachments/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | group.com.linecorp.line | 62 rows",
            "hickman_ios13": "iOS 13.3.1 | group.com.linecorp.line | 15 rows",
            "hickman_ios14": "iOS 14.3 | group.com.linecorp.line | 16 rows",
            "hickman_ios15": "iOS 15.3.1 | group.com.linecorp.line | 27 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Username",
                "textColumn": "Message",
                "directionColumn": "Sent / Received",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Username",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Attachment"
            }
        },
    },
    "lineCalls": {
        "name": "Line - Calls",
        "description": "Line voice and video calls, from the call messages Line keeps in Line.sqlite, with "
                       "duration, direction and the other party",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Line",
        "notes": ("One row per message of content type 6 (ZMESSAGE.ZCONTENTTYPE) in each Line.sqlite, the "
                  "content type that carried every call record on the four tested images. Call Ended is that "
                  "message's ZTIMESTAMP read as Unix milliseconds; Duration is DURATION from the keyed archive "
                  "in ZCONTENTMETADATA, stored as milliseconds and shown in seconds; Call Started is Call Ended"
                  " minus Duration. Type, Result and Cause are TYPE, RESULT and CAUSE from the same archive, as"
                  " stored (A and V; NORMAL with 16 and CANCELED with 77 seen). Direction follows the Line - "
                  "Messages reading: a call message with no sender reference is Outgoing. Contact is the name "
                  "of the first user whose MID matches the chat's ZMID, and Contact MID is that ZMID. These "
                  "readings were checked against a second record of the same calls, the u<MID>_CallHistory.db "
                  "keyed archive Line keeps under Library/NCXVoIP in its app group: on the four tested images "
                  "all 20 calls matched one call message, with the end time within 1 second, the same duration,"
                  " the same direction, the call's video flag set exactly where TYPE is V, the start time equal"
                  " to the derived Call Started and the call's peer equal to the chat's ZMID; the 2 CANCELED "
                  "calls had 0 duration in both records. The call history file itself is not read. No call in a"
                  " group chat was seen on the tested images, which hold no group chats. A chat whose ZMID has "
                  "no user row leaves Contact blank. Account ID is the account the private store folder is "
                  "named for, as in Line - Messages."),
        "paths": ('**/Line.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | group.com.linecorp.line | 8 rows",
            "hickman_ios13": "iOS 13.3.1 | group.com.linecorp.line | 4 rows",
            "hickman_ios14": "iOS 14.3 | group.com.linecorp.line | 4 rows",
            "hickman_ios15": "iOS 15.3.1 | group.com.linecorp.line | 4 rows",
        }
    }
}

import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import (artifact_processor, check_in_media, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

# The app keeps one store per signed in account, under a folder named for that account.
_PRIVATE_STORE = re.compile(r'.*/PrivateStore/P_([^/]+)/', re.I)


def _account_id(path):
    '''The account the private store folder is named for, or '' when there is no such folder.'''
    match = _PRIVATE_STORE.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _attachment_files(files_found):
    '''{(account, message id): [(file name, path)]} for the attachment files in the extraction.

    An attachment file is named for the identifier of the message it belongs to with an
    extension added, so the file itself carries the link the app recorded.
    '''
    found = {}
    for entry in files_found:
        path = str(entry)
        if os.path.isdir(path):
            continue
        if '/Message Attachments/' not in path.replace('\\', '/'):
            continue
        name = os.path.basename(path)
        key = (_account_id(path), os.path.splitext(name)[0])
        found.setdefault(key, []).append((name, path))
    for pairs in found.values():
        pairs.sort()
    return found


def _attachment_names(files_found):
    '''{(account, message id): [file name]} the attachment databases record.

    A device can hold the file with no database, and a database row with no file, so the
    two are read separately and the file name is reported either way.
    '''
    named = {}
    for entry in files_found:
        path = str(entry)
        if os.path.isdir(path) or os.path.basename(path) != 'MessageAttachmentInfo.sqlite':
            continue
        if not does_table_exist_in_db(path, 'ZMESSAGEATTACHMENTINFO'):
            continue
        try:
            rows = get_sqlite_db_records(
                path, 'SELECT ZMESSAGEID, ZFILENAME FROM ZMESSAGEATTACHMENTINFO')
        except sqlite3.Error as ex:
            logfunc(f'Line: could not read {path}: {ex}')
            continue
        account = _account_id(path)
        for (message_id, filename) in rows:
            if message_id is None or not filename:
                continue
            named.setdefault((account, str(message_id)), []).append(str(filename))
    for names in named.values():
        names.sort()
    return named


@artifact_processor
def line(context):
    data_headers = (('Timestamp', 'datetime'), 'Sent / Received', 'Username', 'Message',
                    ('Attachment', 'media'), 'Attachment File Name', 'Message ID', 'Account ID')
    data_list = []
    files_found = context.get_files_found()
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found) or not file_found.endswith('Line.sqlite'):
            continue
        if file_found not in sources:
            sources.append(file_found)
    if not sources:
        return data_headers, data_list, ''

    on_disk = _attachment_files(files_found)
    recorded = _attachment_names(files_found)

    query = '''
    SELECT
        datetime(ZMESSAGE.ZTIMESTAMP / 1000, 'unixepoch'),
        CASE WHEN ZMESSAGE.ZSENDER IS NULL THEN 'Outgoing' ELSE 'Incoming' END,
        ZUSER.ZNAME,
        ZMESSAGE.ZTEXT,
        ZMESSAGE.ZID
    FROM ZMESSAGE
    LEFT JOIN ZUSER ON ZMESSAGE.ZSENDER = ZUSER.Z_PK
    ORDER BY ZMESSAGE.ZTIMESTAMP DESC
    '''
    read = []
    attached = 0
    for source_path in sources:
        try:
            rows = get_sqlite_db_records(source_path, query)
        except sqlite3.Error as ex:
            logfunc(f'Error reading Line messages: {ex}')
            continue
        read.append(source_path)
        account = _account_id(source_path)
        for (timestamp, direction, username, message, message_id) in rows:
            key = (account, '' if message_id is None else str(message_id))
            media = ''
            names = list(recorded.get(key, []))
            for (name, path) in on_disk.get(key, []):
                reference = check_in_media(path, name)
                if reference:
                    media += reference
                    attached += 1
                if name not in names:
                    names.append(name)
            data_list.append((timestamp, direction, username, message, media, ', '.join(names),
                              '' if message_id is None else str(message_id), account))

    if attached:
        logfunc(f'Line: attached {attached} file{"" if attached == 1 else "s"} to messages')

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    return data_headers, data_list, '\n'.join(read)


# ZMESSAGE.ZCONTENTTYPE of the message Line writes for a call
CALL_CONTENT_TYPE = 6


def _call_metadata(blob):
    """The keyed archive in a call message's ZCONTENTMETADATA, or {} when it does not decode."""
    if not isinstance(blob, (bytes, bytearray)):
        return {}
    try:
        metadata = nd.deserialize_plist_from_string(bytes(blob))
    except (ValueError, TypeError, nd.DeserializeError) as ex:
        logfunc(f'Line - Calls: call metadata not decoded: {ex}')
        return {}
    return metadata if isinstance(metadata, dict) else {}


@artifact_processor
def lineCalls(context):
    data_headers = (('Call Started', 'datetime'), ('Call Ended', 'datetime'), 'Direction', 'Contact',
                    'Contact MID', 'Type (as stored)', 'Duration (seconds)', 'Result (as stored)',
                    'Cause (as stored)', 'Message ID', 'Account ID')
    data_list = []
    sources = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isfile(file_found) and file_found.endswith('Line.sqlite') and file_found not in sources:
            sources.append(file_found)

    query = f'''
    SELECT ZMESSAGE.ZTIMESTAMP, ZMESSAGE.ZSENDER IS NULL,
           (SELECT ZUSER.ZNAME FROM ZUSER WHERE ZUSER.ZMID = ZCHAT.ZMID ORDER BY ZUSER.Z_PK LIMIT 1),
           ZCHAT.ZMID, ZMESSAGE.ZCONTENTMETADATA, ZMESSAGE.ZID
    FROM ZMESSAGE
    LEFT JOIN ZCHAT ON ZMESSAGE.ZCHAT = ZCHAT.Z_PK
    WHERE ZMESSAGE.ZCONTENTTYPE = {CALL_CONTENT_TYPE}
    '''
    read = []
    for source_path in sources:
        try:
            rows = get_sqlite_db_records(source_path, query)
        except sqlite3.Error as ex:
            logfunc(f'Line - Calls: could not read {source_path}: {ex}')
            continue
        read.append(source_path)
        account = _account_id(source_path)
        for (timestamp, outgoing, name, mid, blob, message_id) in rows:
            metadata = _call_metadata(blob)
            ended = datetime.fromtimestamp(timestamp / 1000, timezone.utc) if timestamp else ''
            duration = metadata.get('DURATION')
            try:
                seconds = int(duration) / 1000
            except (TypeError, ValueError):
                seconds = ''
            started = ended - timedelta(seconds=seconds) if ended and seconds != '' else ''
            data_list.append((started, ended, 'Outgoing' if outgoing else 'Incoming', name or '',
                              mid or '', metadata.get('TYPE', ''), seconds,
                              metadata.get('RESULT', ''), metadata.get('CAUSE', ''),
                              '' if message_id is None else str(message_id), account))

    data_list.sort(key=lambda row: str(row[1]), reverse=True)
    return data_headers, data_list, '\n'.join(read)
