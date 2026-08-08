__artifacts_v2__ = {
    "mega_chat_messages": {
        "name": "MEGA - Chat Messages",
        "description": "Chat messages from the MEGA (karere) chat store, with the sender resolved to "
                       "an email where possible, the message text, and shared locations with their "
                       "map thumbnail",
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "MEGA",
        "notes": "Read from the karere-*.db history table. Direction is set by comparing the sender "
                 "handle to the account's own handle, which the store keeps in vars as my_handle. "
                 "Text messages (type 1) hold their content directly. Location shares (type 104) "
                 "carry a JSON body with a maps URL, latitude and longitude and a base64 JPEG "
                 "thumbnail, which is decoded and checked in. Other type values are management "
                 "events and are reported with their stored type number and no body.",
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
        "description": "Chats listed in the MEGA karere store, with the peer resolved to an email "
                       "and the creation time",
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "MEGA",
        "notes": "A peer handle of 0 is used by the store for group or self chats rather than a "
                 "one-to-one contact.",
        "paths": ('*/karere-*.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | MEGA | 2 rows",
        },
    },
    "mega_contacts": {
        "name": "MEGA - Contacts",
        "description": "Contacts stored in the MEGA karere store, with the email and the time the "
                       "contact relationship was recorded",
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "MEGA",
        "notes": "",
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


def _karere_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if 'karere-' in file_found and file_found.endswith('.db'):
            return file_found
    return ''


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
    source_path = _karere_db(context.get_files_found())
    data_list = []

    own = _own_handle(source_path)
    own_email = ''
    emails = _contact_emails(source_path)
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
        maps_url = ''
        media = ''
        msg_type = record[3]

        if record[5]:
            message = '<encrypted>'
        elif msg_type == 1:
            message = _decode_text(record[4])
        elif record[4]:
            payload = _embedded_json(record[4])
            if isinstance(payload, dict):
                maps_url = payload.get('textMessage', '')
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
                message = maps_url

        data_list.append((
            convert_unix_ts_to_utc(record[0]),
            'Outgoing' if outgoing else 'Incoming',
            sender,
            message,
            media,
            latitude,
            longitude,
            maps_url,
            str(record[1]),
            msg_type,
            'Yes' if record[5] else 'No',
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Sender',
        'Message',
        ('Location Map', 'media'),
        'Latitude',
        'Longitude',
        'Maps URL',
        'Chat ID',
        'Message Type Value',
        'Was Encrypted',
    )
    return data_headers, data_list, source_path


@artifact_processor
def mega_chats(context):
    source_path = _karere_db(context.get_files_found())
    data_list = []
    emails = _contact_emails(source_path)

    query = '''
    SELECT ts_created, chatid, peer, title, shard, mode
    FROM chats
    ORDER BY ts_created
    '''
    for record in get_sqlite_db_records(source_path, query):
        peer_handle = str(record[2])
        data_list.append((
            convert_unix_ts_to_utc(record[0]),
            str(record[1]),
            emails.get(peer_handle, peer_handle if record[2] else ''),
            record[3],
            record[4],
            record[5],
        ))

    data_headers = (
        ('Created', 'datetime'),
        'Chat ID',
        'Peer',
        'Title',
        'Shard',
        'Mode',
    )
    return data_headers, data_list, source_path


@artifact_processor
def mega_contacts(context):
    source_path = _karere_db(context.get_files_found())
    data_list = []

    query = 'SELECT since, userid, email, visibility FROM contacts ORDER BY since'
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_unix_ts_to_utc(record[0]),
            str(record[1]),
            record[2],
            record[3],
        ))

    data_headers = (
        ('Since', 'datetime'),
        'User ID',
        'Email',
        'Visibility Value',
    )
    return data_headers, data_list, source_path
