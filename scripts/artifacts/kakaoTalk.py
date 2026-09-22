__artifacts_v2__ = {
    "kakaoTalkMessages": {
        "name": "KakaoTalk - Messages",
        "description": "Message records from the KakaoTalk iOS client, with the body decrypted",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "KakaoTalk",
        "notes": "Read from the Message table of Message.sqlite in the app's PrivateDocuments "
                 "folder. Most of each row's content sits in the write ahead log rather than in the "
                 "database file, so the -wal and -shm sidecars are in the declared paths and must be "
                 "staged with it. The message body and the attachment metadata are encrypted at rest: "
                 "on the two devices tested every non empty value of the message column, and of the "
                 "attachment column, was base64 ciphertext. The Message and Attachment columns are decrypted here: the client encrypts "
                 "each of these fields on its own with AES-CBC, under a key derived from the user "
                 "id that owns the row by PBKDF2-HMAC-SHA1 with two iterations, and a key and "
                 "initialisation vector hardcoded in the client. That derivation and the two "
                 "constants were recovered from the client binary and validated against the "
                 "stored ciphertext: two iterations decrypted every value on the devices tested "
                 "(all message and all attachment rows), while one and three iterations decrypted "
                 "none, and the wrong user id decrypted none. A value that does not decrypt is "
                 "left as the stored base64 rather than dropped. The published description of the "
                 "scheme is D. Kim, B. Kim, Y. Yang, H. Jang, 'Decryption and Artifact Analysis "
                 "of KakaoTalk Data in the iOS Environment', Journal of Digital Contents Society, "
                 "Vol. 26, No. 5, pp. 1363-1373, May 2025, "
                 "http://dx.doi.org/10.9728/dcs.2025.26.5.1363. Everything else in the row "
                 "is in the clear: the chat it belongs to, the sender, the type, and the times. Two "
                 "epochs appear in this one table and each is converted on its own: sentAt and "
                 "readAt are Cocoa seconds from 2001, and updateAt in the same row is Unix seconds. "
                 "That was measured rather than assumed, by converting the newest row of each device "
                 "both ways and keeping the reading that falls inside the acquisition period. Sender "
                 "Name is resolved from the ZUSER table of Talk.sqlite in the same app container by "
                 "the numeric user id the message records, which is a link the store keeps rather "
                 "than a correlation; a sender with no matching user row is reported with the id and "
                 "a blank name. Type is reported as stored: no mapping for the integer was "
                 "recoverable, because the client is closed source. Media renders the local file a message's "
                 "decrypted attachment names, inline on that message's own row: the attachment and "
                 "the file name share a token, and the file is matched inside the message's own "
                 "chat folder, so it is a link the store records rather than a correlation. Five of "
                 "the six media messages on the device with media resolved to a file this way; a "
                 "message with no media, or whose file the store no longer holds, has a blank "
                 "Media column, and the Chat Media artifact lists every kept file including those. "
                 "Field mapping was done against two private samples; no sample data is recorded for "
                 "them. A Message.sqlite that does not carry this client's own table and column "
                 "layout is skipped and logged, so another app's file of the same name cannot be "
                 "reported as KakaoTalk.",
        "paths": ('*/Library/PrivateDocuments/Message.sqlite*',
                  '*/Library/PrivateDocuments/Talk.sqlite*',
                  '*/Library/PrivateDocuments/chat/*/*',
                  '*/Library/PrivateDocuments/chatVideo/*/*',
                  '*/Library/PrivateDocuments/chatAudio/*/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "textColumn": "Message",
                "timeColumn": "Sent",
                "senderColumn": "Sender Name",
                "mediaColumn": "Media"
            }
        },
    },
    "kakaoTalkChats": {
        "name": "KakaoTalk - Chats",
        "description": "Chat rooms recorded by the KakaoTalk iOS client",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "KakaoTalk",
        "notes": "Read from the ZCHAT table of Talk.sqlite, a Core Data store, with the folder name "
                 "taken from ZCHATFOLDER where the chat's id appears in that folder's id list. "
                 "Updated is ZUPDATEDAT, Cocoa seconds from 2001. Room Name is the ZROOMNAME column "
                 "and was blank on most rows of the devices tested: a one to one chat carries no "
                 "room name, and the display name an examiner sees in the app is built from the "
                 "members instead, so a blank here is not a missing value. Chat Type and View Type "
                 "are reported as stored. Member Count is the app's own active member count, and Unread "
                 "Count was zero on every row of the devices tested, kept because a chat with "
                 "unread messages would show it. The "
                 "last message is reported by its id and type only, because the last message text "
                 "the row also carries is encrypted, in the same way the message bodies are. Field "
                 "mapping was done against two private samples; no sample data is recorded for them.",
        "paths": ('*/Library/PrivateDocuments/Talk.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "messages"
    },
    "kakaoTalkUsers": {
        "name": "KakaoTalk - Users",
        "description": "User records the KakaoTalk iOS client holds, with phone numbers decrypted",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "KakaoTalk",
        "notes": "Read from the ZUSER table of Talk.sqlite. A row is a user the client knows about, "
                 "which includes friends, members of chats the account is in, and official accounts, "
                 "so a row is not by itself evidence that the account communicated with that user. "
                 "Friend Type, Block Type and User Type are reported as stored: no mapping for the "
                 "integers was recoverable from the closed source client. Name, Nickname and Custom "
                 "Name are separate columns the store keeps separately, and they differed on rows of "
                 "the devices tested, so all three are reported rather than one being chosen. Phone "
                 "Number is encrypted at rest and is decrypted here with the same per record scheme as "
                 "the message bodies, keyed on the row's own user id; it decrypted to a phone number "
                 "on all 6 of the populated user rows of each device. A value that does not decrypt is "
                 "left as stored. Profile "
                 "photo URLs are reported as stored and are remote addresses the report does not "
                 "fetch. Status Message and Email were blank, and Hidden and Favorite were zero, "
                 "on every row of the two devices tested; each is kept because a populated store "
                 "would carry these and their absence here is itself the finding. Field mapping "
                 "was done against two private samples; no sample data is "
                 "recorded for them.",
        "paths": ('*/Library/PrivateDocuments/Talk.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "kakaoTalkContacts": {
        "name": "KakaoTalk - Address Book Matches",
        "description": "Device address book entries the KakaoTalk iOS client matched to its users",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "KakaoTalk",
        "notes": "Read from the ZCONTACT table of Talk.sqlite, which holds entries the client took "
                 "from the device address book when contact syncing was on. A row records a name and "
                 "number held on the device, not a KakaoTalk account, and the linked user id is "
                 "present only where the client matched that entry to one. The name is in the clear and "
                 "the numbers are not: both number columns were base64 text on every row of the two "
                 "devices tested and are reported as stored, encrypted in the same way as the message "
                 "bodies. A third column, ZORIGINALPHONENUMBER, held a value identical to the "
                 "normalised one on every row of both devices, so it is not reported separately; the "
                 "raw column, where the schema has it, differed from the normalised one on all 15 "
                 "rows of the device that carries it and is reported. The raw number and contact id "
                 "columns are absent from the older of the two schemas seen, so each is resolved per "
                 "store and left blank where the column does not exist, rather than costing the "
                 "artifact its rows. Field mapping was done against two private samples; "
                 "no sample data is recorded for them.",
        "paths": ('*/Library/PrivateDocuments/Talk.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "address-book"
    },
    "kakaoTalkMedia": {
        "name": "KakaoTalk - Chat Media",
        "description": "Media files the KakaoTalk iOS client stored under its per chat folders",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "KakaoTalk",
        "notes": "One row per file under the client's chat, chatVideo and chatAudio folders, with "
                 "the file rendered where its bytes are a type the report can show. The folder a "
                 "file sits in is named with a chat id, which is the link the store records, so each "
                 "file is attributed to a chat rather than correlated to one: on the device with "
                 "media, seven distinct chat folder ids appeared, five of them present in the chat "
                 "table and two not, and those two are reported with the id and no room name. This artifact lists every media "
                 "file the client kept, including one whose message the store no longer holds, which "
                 "the Messages artifact cannot. Where a message's decrypted attachment names the file, "
                 "the Messages artifact also renders it inline on that message's own row, so the two "
                 "are complementary. Files whose name begins with a thumbnail marker are "
                 "the client's own reduced copies and are labelled as such rather than dropped. Chat Room "
                 "Name was blank on every media row of the devices tested: the media in these folders "
                 "belonged to chats the store left without a room name, and the one chat that did carry "
                 "a room name had no media here. The "
                 "content type is taken from the bytes, not from the name, because these files "
                 "carry no extension. Field mapping was done against two private samples; no sample "
                 "data is recorded for them.",
        "paths": ('*/Library/PrivateDocuments/chat/*/*',
                  '*/Library/PrivateDocuments/chatVideo/*/*',
                  '*/Library/PrivateDocuments/chatAudio/*/*',
                  '*/Library/PrivateDocuments/Talk.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "photo"
    },
}

import base64
import hashlib
import os
import re
import sqlite3

from Crypto.Cipher import AES

from scripts.ilapfuncs import (artifact_processor, check_in_media, get_sqlite_db_records,
                               convert_unix_ts_to_utc, convert_cocoa_core_data_ts_to_utc, logfunc)

# Message.sqlite and Talk.sqlite are generic names. A store is this client's only when it
# carries the client's own layout, so each is confirmed before a row is reported.
MESSAGE_MARKERS = {'sentAt', 'chatId', 'serverLogId', 'clientMsgId'}
TALK_TABLES = {'ZCHAT', 'ZUSER'}

MEDIA_DIR = re.compile(r'/PrivateDocuments/(?P<kind>chat|chatVideo|chatAudio)/(?P<chatid>\d+)/')
THUMB = re.compile(r'(^|/)(_th_|.*-thum$)')

# KakaoTalk iOS field decryption. The client encrypts the message body, the attachment
# metadata and some phone numbers per record, and derives the AES key from the owning user
# id. The key derivation and the two hardcoded constants below were recovered from the
# client binary (TalkSharedBase, +[KAODatabaseCrypto makeKeyWithIdentifier:]) and validated
# against real ciphertext: a PBKDF2 iteration count of 2 decrypted every tested value, while
# 1 and 3 decrypted none, and the wrong user id decrypted none. The constants match those of
# the published Android scheme; only the derivation differs (PBKDF2-HMAC-SHA1 on iOS).
_KAKAO_KEY = bytes.fromhex('1608096f02172b0821210a1003030706')
_KAKAO_IV = bytes.fromhex('0f080100194725dc15f517e0e1150c35')


def _decrypt_field(user_id, b64_value):
    """Decrypt one KakaoTalk iOS per-record field, or return None if it cannot be decrypted.

    user_id is the KakaoTalk user id that owns the field: Message.userId for a message, or
    the row's own ZID for a ZUSER phone number.
    """
    if not b64_value:
        return b64_value
    try:
        ciphertext = base64.b64decode(b64_value)
    except (ValueError, TypeError):
        return None
    if not ciphertext or len(ciphertext) % 16 != 0:
        return None
    salt = (str(user_id).encode('ascii', 'ignore') + b'\x00' * 16)[:16]
    key = hashlib.pbkdf2_hmac('sha1', _KAKAO_KEY, salt, 2, 32)
    try:
        plain = AES.new(key, AES.MODE_CBC, _KAKAO_IV).decrypt(ciphertext)
    except ValueError:
        return None
    pad = plain[-1] if plain else 0
    if pad < 1 or pad > 16 or pad > len(plain) or plain[-pad:] != bytes([pad]) * pad:
        return None
    try:
        return plain[:-pad].decode('utf-8')
    except UnicodeDecodeError:
        return None


def _container_of(path):
    found = re.match(r'(?P<root>.*/Data/Application/[^/]+)/', path.replace('\\', '/'))
    if found:
        return found.group('root')
    return os.path.dirname(path.replace('\\', '/'))


def _columns(db_path, table):
    try:
        with sqlite3.connect(f'file:{db_path}?mode=ro', uri=True) as con:
            return {row[1] for row in con.execute(f'PRAGMA table_info("{table}")')}
    except sqlite3.Error:
        return set()


def _tables(db_path):
    try:
        with sqlite3.connect(f'file:{db_path}?mode=ro', uri=True) as con:
            return {row[0] for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
    except sqlite3.Error:
        return set()


def _stores(context):
    """Group this client's confirmed stores by the container they sit in."""
    grouped = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        name = os.path.basename(file_found.replace('\\', '/'))
        entry = grouped.setdefault(_container_of(file_found), {})
        if name == 'Message.sqlite':
            if MESSAGE_MARKERS <= _columns(file_found, 'Message'):
                entry['messages'] = file_found
            else:
                logfunc(f'KakaoTalk: {name} does not carry the client\'s layout, skipped')
        elif name == 'Talk.sqlite':
            if TALK_TABLES <= _tables(file_found):
                entry['talk'] = file_found
            else:
                logfunc(f'KakaoTalk: {name} does not carry the client\'s layout, skipped')
        elif MEDIA_DIR.search(file_found):
            entry.setdefault('media', []).append(file_found)
    return grouped


def _users_by_id(talk_path):
    if not talk_path:
        return {}
    users = {}
    for row in get_sqlite_db_records(talk_path, 'SELECT ZID, ZNAME, ZNICKNAME FROM ZUSER'):
        if row[0] is not None:
            users[str(row[0])] = row[1] or row[2] or ''
    return users


def _chats_by_id(talk_path):
    if not talk_path:
        return {}
    chats = {}
    for row in get_sqlite_db_records(talk_path, 'SELECT ZID, ZROOMNAME, ZTYPE FROM ZCHAT'):
        if row[0] is not None:
            chats[str(row[0])] = (row[1] or '', row[2] if row[2] is not None else '')
    return chats


def _media_index(media_files):
    """Per chat id, the media files under that chat's folder, non-thumbnails first.

    A file's own folder is named with the chat id, so a message's media is looked up in
    its chat and then matched by the token the decrypted attachment shares with the name.
    """
    index = {}
    for path in media_files or []:
        found = MEDIA_DIR.search(path.replace('\\', '/'))
        if not found:
            continue
        name = os.path.basename(path.replace('\\', '/'))
        index.setdefault(found.group('chatid'), []).append((name, path))
    for chat_id in index:
        index[chat_id].sort(key=lambda item: bool(THUMB.search(item[0])))
    return index


def _attachment_media(attachment_json, chat_id, media_by_chat):
    """The local media file a message's decrypted attachment names, or ''.

    The attachment carries tokens (in its url, thumbnailUrl and key fields) that also appear
    in the local file's name; the file is matched inside the message's own chat only, so the
    link is the token the store records rather than a correlation.
    """
    if not attachment_json or chat_id not in media_by_chat:
        return ''
    tokens = set(re.findall(r'[A-Za-z0-9_-]{16,}', attachment_json))
    if not tokens:
        return ''
    for name, path in media_by_chat[chat_id]:
        if any(token in name for token in tokens):
            return path
    return ''


@artifact_processor
def kakaoTalkMessages(context):
    data_headers = (
        ('Sent', 'datetime'),
        ('Read', 'datetime'),
        ('Updated', 'datetime'),
        'Sender Name',
        'Message',
        ('Media', 'media'),
        'Chat ID',
        'Sender User ID',
        'Type',
        'Attachment',
        'Server Log ID',
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_stores(context).items()):
        message_path = entry.get('messages')
        if not message_path:
            continue
        users = _users_by_id(entry.get('talk'))
        media_by_chat = _media_index(entry.get('media'))
        query = ('SELECT sentAt, readAt, updateAt, chatId, userId, type, message, attachment, '
                 'serverLogId FROM Message')
        rows = 0
        for row in get_sqlite_db_records(message_path, query):
            sender = str(row[4]) if row[4] is not None else ''
            message = _decrypt_field(sender, row[6])
            attachment = _decrypt_field(sender, row[7])
            media_ref = ''
            media_path = _attachment_media(attachment, str(row[3]), media_by_chat)
            if media_path:
                media_ref = check_in_media(media_path, os.path.basename(media_path)) or ''
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row[0]) if row[0] else '',
                convert_cocoa_core_data_ts_to_utc(row[1]) if row[1] else '',
                convert_unix_ts_to_utc(row[2]) if row[2] else '',
                users.get(sender, ''),
                message if message is not None else (row[6] or ''),
                media_ref,
                row[3] if row[3] is not None else '',
                sender,
                row[5] if row[5] is not None else '',
                attachment if attachment is not None else (row[7] or ''),
                row[8] if row[8] is not None else '',
                context.get_relative_path(message_path),
            ))
            rows += 1
        if rows:
            source_paths.append(message_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def kakaoTalkChats(context):
    data_headers = (
        ('Updated', 'datetime'),
        'Chat ID',
        'Room Name',
        'Chat Type (as stored)',
        'View Type (as stored)',
        'Member Count',
        'Unread Count',
        'Last Message ID',
        'Last Message Type (as stored)',
        'Folder',
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_stores(context).items()):
        talk_path = entry.get('talk')
        if not talk_path:
            continue
        folders = {}
        for row in get_sqlite_db_records(talk_path, 'SELECT ZNAME, ZCHATIDS FROM ZCHATFOLDER'):
            for chat_id in re.findall(r'\d+', str(row[1] or '')):
                folders[chat_id] = row[0] or ''
        query = ('SELECT ZUPDATEDAT, ZID, ZROOMNAME, ZTYPE, ZVIEWTYPE, ZACTIVEMEMBERCOUNT, '
                 'ZUNREADCOUNT, ZLASTMESSAGEID, ZLASTMESSAGETYPE FROM ZCHAT')
        rows = 0
        for row in get_sqlite_db_records(talk_path, query):
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(row[0]) if row[0] else '',
                row[1] if row[1] is not None else '',
                row[2] or '',
                row[3] if row[3] is not None else '',
                row[4] if row[4] is not None else '',
                row[5] if row[5] is not None else '',
                row[6] if row[6] is not None else '',
                row[7] if row[7] is not None else '',
                row[8] if row[8] is not None else '',
                folders.get(str(row[1]), ''),
                context.get_relative_path(talk_path),
            ))
            rows += 1
        if rows:
            source_paths.append(talk_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def kakaoTalkUsers(context):
    data_headers = (
        'User ID',
        'Account ID',
        'Name',
        'Nickname',
        'Custom Name',
        'Status Message',
        'Email',
        'Phone Number',
        'Friend Type (as stored)',
        'Block Type (as stored)',
        'User Type (as stored)',
        'Hidden',
        'Favorite',
        'Profile Photo URL',
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_stores(context).items()):
        talk_path = entry.get('talk')
        if not talk_path:
            continue
        query = ('SELECT ZID, ZACCOUNTID, ZNAME, ZNICKNAME, ZCUSTOMNAME, ZSTATUSMESSAGE, ZEMAIL, '
                 'ZPHONENUMBER, ZFRIENDTYPE, ZBLOCKTYPE, ZUSERTYPE, ZHIDDEN, ZFAVORITE, ZPHOTOURL '
                 'FROM ZUSER')
        rows = 0
        for row in get_sqlite_db_records(talk_path, query):
            values = [value if value is not None else '' for value in row]
            # ZPHONENUMBER (index 7) is encrypted, keyed on this row's own ZID (index 0).
            phone = _decrypt_field(row[0], row[7])
            values[7] = phone if phone is not None else values[7]
            data_list.append(tuple(values) + (context.get_relative_path(talk_path),))
            rows += 1
        if rows:
            source_paths.append(talk_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def kakaoTalkContacts(context):
    data_headers = (
        'Name',
        'Phone Number (encrypted, as stored)',
        'Raw Phone Number (encrypted, as stored)',
        'Contact ID',
        'Linked User ID',
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_stores(context).items()):
        talk_path = entry.get('talk')
        if not talk_path:
            continue
        columns = _columns(talk_path, 'ZCONTACT')
        raw = 'ZRAWPHONENUMBER' if 'ZRAWPHONENUMBER' in columns else "''"
        contact_id = 'ZCONTACTID' if 'ZCONTACTID' in columns else "''"
        query = (f'SELECT ZNAME, ZPHONENUMBER, {raw}, {contact_id}, ZUSER '
                 'FROM ZCONTACT')
        rows = 0
        for row in get_sqlite_db_records(talk_path, query):
            data_list.append(tuple(
                (value if value is not None else '') for value in row
            ) + (context.get_relative_path(talk_path),))
            rows += 1
        if rows:
            source_paths.append(talk_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def kakaoTalkMedia(context):
    data_headers = (
        'Chat ID',
        'Chat Room Name',
        'Folder',
        'File Name',
        'Is Thumbnail',
        'Size (bytes)',
        ('Media', 'media'),
        'Source File',
    )
    data_list = []
    source_paths = []

    for _, entry in sorted(_stores(context).items()):
        media_files = entry.get('media') or []
        if not media_files:
            continue
        chats = _chats_by_id(entry.get('talk'))
        for file_found in sorted(media_files):
            found = MEDIA_DIR.search(file_found.replace('\\', '/'))
            if not found:
                continue
            chat_id = found.group('chatid')
            name = os.path.basename(file_found.replace('\\', '/'))
            try:
                size = os.path.getsize(file_found)
            except OSError:
                size = ''
            data_list.append((
                chat_id,
                chats.get(chat_id, ('', ''))[0],
                found.group('kind'),
                name,
                'Yes' if THUMB.search(name) else 'No',
                size,
                check_in_media(file_found, name) or '',
                context.get_relative_path(file_found),
            ))
            source_paths.append(file_found)

    return data_headers, data_list, '\n'.join(source_paths)
