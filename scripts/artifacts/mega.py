__artifacts_v2__ = {
    "mega_chat_messages": {
        "name": "MEGA - Chat Messages",
        "description": "Chat messages from the MEGA (karere) chat store, with the sender resolved to "
                       "an email where possible, the message text, and the coordinates and embedded "
                       "image stored in a message's JSON body",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "MEGA",
        "notes": "Read from the history table of every karere-*.db file matched; the Source File "
                 "column names the file each row came from. Sender and Direction are resolved "
                 "inside that file only. The app, its app group and its extensions can each hold a karere "
                 "file: a file whose rows equal those of a file already reported is left out, "
                 "and the located-at line still lists every file read. On hc_ios26 three "
                 "containers hold a karere file with the same rows, so they are reported once. "
                 "Direction is set by "
                 "comparing the sender handle to the account's own handle, which the store keeps "
                 "in vars as my_handle. Rows with type 1 hold their text directly. For any row "
                 "that is not type 1, is not flagged encrypted and whose body holds a JSON object, "
                 "the object's textMessage is reported under Message and under textMessage (as "
                 "stored), and the first 'extra' entry's la, lng and img as Latitude, Longitude "
                 "and Location Map; the img "
                 "value is base64 decoded and checked in as a JPEG. The code does not check the "
                 "type or that the text is a maps link, so another kind of type 104 row would be "
                 "reported the same way. On hc_ios26 the 2 rows this applied to were type 104 and "
                 "each held a maps link, coordinates and a thumbnail; the same was true of 2 rows "
                 "on hc_ios18_7 and 8 rows on iphone11_ios17. On iphone11_ios17 16 type 101 rows "
                 "also held a JSON object, with no textMessage, and are reported with a blank "
                 "Message and textMessage (as stored). Other type values are reported with "
                 "their stored type number. Rows whose is_encrypted value is not 0 are reported "
                 "with '<encrypted>' in place of a body and Yes under Was Encrypted; what each "
                 "non-zero value means is not sourced here. MEGA publishes both vocabularies in "
                 "the MEGAchat file src/chatdMsg.h, which is not yet cited at a pinned commit.",
        "paths": ('*/karere-*.db*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | MEGA | 10 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Location Map",
            }
        },
    },
    "mega_chats": {
        "name": "MEGA - Chats",
        "description": "Chats listed in the MEGA karere stores, with creation time and a peer "
                       "display value from a contacts.email lookup or the stored peer rendered as "
                       "text. The value does not establish identity.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "MEGA",
        "notes": "Read from the chats table of every karere-*.db file matched; the Source File "
                 "column names the file each row came from, and the contact lookup uses that "
                 "file's own contacts table. Peer Display Value uses a lookup "
                 "of str(peer) against str(contacts.userid). A truthy contacts.email value takes "
                 "precedence; it is not validated as an email or an identity. For duplicate string "
                 "keys the last truthy email read wins, and false values do not replace an earlier "
                 "entry. On a lookup miss, any non-NULL peer is rendered with str(), including "
                 "numeric zero, REAL zero and an empty BLOB (as a bytes representation). SQL NULL "
                 "has a blank fallback; the existing lookup can still match its literal 'None' key. "
                 "This mixed display field does not preserve the peer's native type or establish "
                 "the meaning of zero. Original parser contribution: @AlexisBrignoni, Claude.",
        "paths": ('*/karere-*.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | MEGA | 2 rows",
        },
    },
    "mega_contacts": {
        "name": "MEGA - Contacts",
        "description": "Contacts stored in the MEGA karere store, with the email and the stored "
                       "'since' time, read as Unix seconds; what that time marks is not established",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "MEGA",
        "notes": "Read from the contacts table of every karere-*.db file matched; the Source "
                 "File column names the file each row came from.",
        "paths": ('*/karere-*.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | MEGA | 1 row",
        },
    },
}

import base64
import json

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
)


def _karere_dbs(files_found):
    """Every matched karere-*.db file, once each, in the order found."""
    found = []
    for file_found in files_found:
        file_found = str(file_found)
        if 'karere-' in file_found and file_found.endswith('.db'):
            found.append(file_found)
    return list(dict.fromkeys(found))


def _drop_repeated_files(data_list, skip=()):
    """Rows of each file, leaving out a file whose rows equal those of a file already kept.

    The app, its app group and its extensions can each hold a karere file with the same
    content. The last cell of a row is its Source File; cells listed in skip (the rendered
    media cell) are left out of the comparison.
    """
    by_file = {}
    for row in data_list:
        by_file.setdefault(row[-1], []).append(row)
    kept, seen = [], []
    for rows in by_file.values():
        content = sorted(repr(tuple(cell for index, cell in enumerate(row[:-1]) if index not in skip))
                         for row in rows)
        if content in seen:
            continue
        seen.append(content)
        kept.extend(rows)
    return kept


def _own_handle(source_path):
    for record in get_sqlite_db_records(
            source_path, "SELECT value FROM vars WHERE name = 'my_handle'"):
        return str(record[0])
    return None


def _contact_emails(source_path):
    emails = {}
    for record in get_sqlite_db_records(source_path, 'SELECT userid, email FROM contacts'):
        if record[1]:
            emails[str(record[0])] = record[1]
    return emails


def _decode_text(blob):
    if blob is None:
        return ''
    if isinstance(blob, (bytes, bytearray)):
        try:
            return blob.decode('utf-8')
        except UnicodeDecodeError:
            return ''
    return str(blob)


def _embedded_json(blob):
    """Rich-message blobs (e.g. location shares) carry a short binary header before a
    JSON body, so the object is located by its outermost braces rather than assumed at
    the start."""
    if not isinstance(blob, (bytes, bytearray)):
        return None
    start = blob.find(b'{')
    end = blob.rfind(b'}')
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(blob[start:end + 1].decode('utf-8', 'replace'))
    except ValueError:
        return None


@artifact_processor
def mega_chat_messages(context):
    data_list = []
    sources = _karere_dbs(context.get_files_found())
    for source_path in sources:
        _chat_message_rows(context, source_path, data_list)
    data_list = _drop_repeated_files(data_list, skip=(4,))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Sender',
        'Message',
        ('Location Map', 'media'),
        'Latitude',
        'Longitude',
        'textMessage (as stored)',
        'Chat ID',
        'Message Type Value',
        'Was Encrypted',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


def _chat_message_rows(context, source_path, data_list):
    own = _own_handle(source_path)
    own_email = ''
    emails = _contact_emails(source_path)
    source_file = context.get_relative_path(source_path)
    for record in get_sqlite_db_records(source_path, "SELECT value FROM vars WHERE name = 'my_email'"):
        own_email = record[0]

    query = '''
    SELECT ts, chatid, userid, type, data, is_encrypted, msgid
    FROM history
    ORDER BY ts
    '''
    for record in get_sqlite_db_records(source_path, query):
        sender_handle = str(record[2])
        outgoing = own is not None and sender_handle == own
        if outgoing:
            sender = own_email or sender_handle
        else:
            sender = emails.get(sender_handle, sender_handle)

        message = ''
        latitude = ''
        longitude = ''
        text_message = ''
        media = ''
        msg_type = record[3]

        if record[5]:
            message = '<encrypted>'
        elif msg_type == 1:
            message = _decode_text(record[4])
        elif record[4]:
            payload = _embedded_json(record[4])
            if isinstance(payload, dict):
                text_message = payload.get('textMessage', '')
                extra = payload.get('extra')
                if isinstance(extra, list) and extra and isinstance(extra[0], dict):
                    latitude = extra[0].get('la', '')
                    longitude = extra[0].get('lng', '')
                    thumb = extra[0].get('img')
                    if thumb:
                        try:
                            raw = base64.b64decode(thumb)
                            media = check_in_embedded_media(
                                source_path, raw, f'mega_location_{record[6]}.jpg',
                                force_type='image/jpeg', force_extension='jpg') or ''
                        except (ValueError, TypeError):
                            media = ''
                message = text_message

        data_list.append((
            convert_unix_ts_to_utc(record[0]),
            'Outgoing' if outgoing else 'Incoming',
            sender,
            message,
            media,
            latitude,
            longitude,
            text_message,
            str(record[1]),
            msg_type,
            'Yes' if record[5] else 'No',
            source_file,
        ))


@artifact_processor
def mega_chats(context):
    data_list = []
    sources = _karere_dbs(context.get_files_found())

    query = '''
    SELECT ts_created, chatid, peer, title, shard, mode
    FROM chats
    ORDER BY ts_created
    '''
    for source_path in sources:
        emails = _contact_emails(source_path)
        source_file = context.get_relative_path(source_path)
        for record in get_sqlite_db_records(source_path, query):
            peer_handle = str(record[2])
            data_list.append((
                convert_unix_ts_to_utc(record[0]),
                str(record[1]),
                emails.get(peer_handle, peer_handle if record[2] is not None else ''),
                record[3],
                record[4],
                record[5],
                source_file,
            ))

    data_list = _drop_repeated_files(data_list)

    data_headers = (
        ('Created', 'datetime'),
        'Chat ID',
        'Peer Display Value',
        'Title',
        'Shard',
        'Mode',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def mega_contacts(context):
    data_list = []
    sources = _karere_dbs(context.get_files_found())

    query = 'SELECT since, userid, email, visibility FROM contacts ORDER BY since'
    for source_path in sources:
        source_file = context.get_relative_path(source_path)
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                convert_unix_ts_to_utc(record[0]),
                str(record[1]),
                record[2],
                record[3],
                source_file,
            ))

    data_list = _drop_repeated_files(data_list)

    data_headers = (
        ('Since', 'datetime'),
        'User ID',
        'Email',
        'Visibility Value',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
