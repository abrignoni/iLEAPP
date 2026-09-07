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
        "notes": "Direction is inferred: rows without a sender reference are treated as outgoing; "
                 "established through testing. The store holds no user row for the signed in "
                 "account itself on any tested image, so a message that account sent has no user "
                 "row to point at, which is what that reading expects. Username names the other "
                 "party rather than the sender of every row: it was filled on all 66 incoming rows "
                 "and on none of the 54 outgoing rows across the four tested images. "
                 "Every Line.sqlite in the extraction is read rather "
                 "than only the first one found. Each Line.sqlite sits under a folder named for "
                 "an account, and Account ID carries that name so rows "
                 "from two accounts on one device stay apart. A store that does not sit under such "
                 "a folder leaves Account ID blank. Rows from all stores are ordered together, "
                 "newest first. Every tested image held one account, so the two account case was "
                 "checked on a tree built by hand from one of them: the rows doubled to sixteen "
                 "under each of two accounts, and a message altered in the added copy appeared "
                 "only against that copy's account. Read the way it was before this change, the "
                 "same tree returned one of the two stores and sixteen of the thirty two rows. "
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
    }
}

import os
import re
import sqlite3

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
