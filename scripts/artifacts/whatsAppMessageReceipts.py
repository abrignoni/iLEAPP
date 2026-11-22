"""WhatsApp iOS per-user message receipts from MessagingInfraDatabase.sqlite.

The receipt_device table is unique on stanza, chat, user, device and associated bot. Each row is linked to
ChatStorage.sqlite by its stanza id, either to a message (ZWAMESSAGE.ZSTANZAID) or to a reaction
(the key id of a field 7 entry in ZWAMESSAGEINFO.ZRECEIPTINFO).
"""

__artifacts_v2__ = {
    "whatsAppMessageReceipts": {
        "name": "WhatsApp - Message Receipts",
        "description": "Send, delivered, read and played times per user and device from the receipt_device table of "
                       "WhatsApp's MessagingInfraDatabase.sqlite, matched by stanza id and chat JID to a message or a "
                       "reaction entry in ChatStorage.sqlite where one exists.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-22",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row per receipt_device row in MessagingInfraDB_v2/MessagingInfraDatabase.sqlite, read read-only."
                 " The column names in the table are the source for Send, Delivered, Read and Played; what each moment"
                 " means to WhatsApp is not established beyond those names. User JID is the table's user_jid. Measured"
                 " on hill_iphone15pro_ios26 and wilkerson_iphone16_ios26. Every stored time on these two images is a "
                 "10-digit integer, read as Unix seconds and shown in UTC. The 87 Message rows belong to 54 messages. "
                 "Send Timestamp is within 60 seconds of the linked message's ZMESSAGEDATE on 79 of the 87 rows, and "
                 "later by more than 60 seconds, up to about 4.2 days, on the other 8 (4 group chat messages, 2 rows "
                 "each). On 4 of those 8 rows Delivered Timestamp is earlier than Send Timestamp, and on 1 of the 4 "
                 "Read Timestamp is also earlier than Send Timestamp; why is not established. On the 74 rows that have"
                 " both, Read Timestamp is never earlier than Delivered Timestamp, and 8 Message rows have a Read "
                 "Timestamp with no Delivered Timestamp. Item is Message where stanza_id and chat_jid match "
                 "ZWAMESSAGE.ZSTANZAID and the chat's ZCONTACTJID, Reaction where stanza_id equals the key id of a "
                 "field 7.1 or 7.2 entry in a ZWAMESSAGEINFO.ZRECEIPTINFO blob and chat_jid equals the ZCONTACTJID of "
                 "that blob's message, and Not linked otherwise. Of the 112 rows, 87 are Message, 25 are Reaction and "
                 "none are Not linked. On Reaction rows, Chat Name, Message, Message Type and Message Timestamp are "
                 "those of the message whose ZRECEIPTINFO blob holds the reaction entry. All 25 are field 7.2 entries "
                 "on messages with ZISFROMME 0; each has a Send Timestamp within 1 second of the millisecond time "
                 "stored in the entry (field 3) and no Delivered or Read Timestamp. No row matched a field 7.1 entry. "
                 "Every linked Message row on these images has ZISFROMME 1. Delivered and read times were not found in"
                 " the ZRECEIPTINFO blobs of the 54 linked messages on these two images. Message is blank on 46 of the"
                 " 87 Message rows; Message Type shows ZMESSAGETYPE as stored, and attachments are not shown here. "
                 "Played Timestamp has no value on any of the 112 rows, so its unit is not measured. Device ID held 0 "
                 "on all 112 rows and its meaning is not established. User Push Name is from ZWAPROFILEPUSHNAME, User "
                 "Address Book Name is the ZFULLNAME of the ContactsV2 contact whose ZLID matches, and User Phone "
                 "Number is the one number LID.sqlite stores for the user's LID (all 112 came from ZWAZACCOUNT). All "
                 "112 user_jid values end in @lid; a user_jid in another form gets no address book name or phone "
                 "number, and that branch is unexercised. The two name columns are blank on the same 4 rows. "
                 "device_version is not shown because its meaning is not established, and associated_bot_jid held no "
                 "value on any of the 112 rows and is not shown. The status_receipt_device and status_seen_receipt "
                 "tables in statusDB/Status.sqlite held 0 rows on hill_iphone15pro_ios26 and wilkerson_iphone16_ios26 "
                 "and are not read. receipt_device held 0 rows on hc_ios26.",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | WhatsApp Messenger 26.28.75 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | WhatsApp Messenger 26.38.74 | 42 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | WhatsApp Messenger 26.39.75 | 70 rows",
        },
        "paths": (
            '*/mobile/Containers/Shared/AppGroup/*/MessagingInfraDB_v2/MessagingInfraDatabase.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/LID.sqlite*',
            '*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',
        ),
        "output_types": "standard",
        "artifact_icon": "circle-check",
    },
}

import os
import sqlite3

from scripts import blackboxprotobuf

from scripts.artifacts.whatsAppLID import _Lid, _bare
from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc, convert_unix_ts_to_utc,
                               does_column_exist_in_db, does_table_exist_in_db, logfunc, open_sqlite_db_readonly)

_INFRA = 'MessagingInfraDatabase.sqlite'
_SIBLINGS = ('ChatStorage.sqlite', 'LID.sqlite', 'ContactsV2.sqlite')


def _stores(context):
    """[(infra path, {sibling name: path})], pairing each receipts store with its own app group folder."""
    infra, siblings = [], {}
    for path in context.get_files_found():
        path = str(path)
        if os.path.isdir(path):
            continue
        name = os.path.basename(path)
        if name == _INFRA and os.path.basename(os.path.dirname(path)) == 'MessagingInfraDB_v2':
            infra.append(path)
        elif name in _SIBLINGS:
            siblings.setdefault(os.path.dirname(path), {})[name] = path
    return [(p, siblings.get(os.path.dirname(os.path.dirname(p)), {})) for p in sorted(set(infra))]


def _fetch(path, sql):
    db = open_sqlite_db_readonly(path)
    if db is None:
        return []
    try:
        db.row_factory = sqlite3.Row
        return db.execute(sql).fetchall()
    except sqlite3.Error as error:
        logfunc(f'WhatsApp Message Receipts: could not read {os.path.basename(path)}: {error}')
        return []
    finally:
        db.close()


def _entries(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _text(value):
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    return '' if value is None else str(value)


def _time(value):
    return convert_unix_ts_to_utc(value) if value else ''


def _message_index(chat_db):
    """Messages keyed by (stanza id, chat JID), and reactions keyed by (key id, chat JID)."""
    messages, reactions = {}, {}
    if not chat_db or not does_table_exist_in_db(chat_db, 'ZWAMESSAGE'):
        return messages, reactions
    rows = _fetch(chat_db, '''
        SELECT m.ZSTANZAID, m.ZMESSAGEDATE, m.ZMESSAGETYPE, m.ZTEXT, i.ZRECEIPTINFO,
               s.ZCONTACTJID, s.ZPARTNERNAME
        FROM ZWAMESSAGE m
        LEFT JOIN ZWAMESSAGEINFO i ON i.Z_PK = m.ZMESSAGEINFO
        LEFT JOIN ZWACHATSESSION s ON s.Z_PK = m.ZCHATSESSION''')
    for row in rows:
        chat = row['ZCONTACTJID']
        if row['ZSTANZAID']:
            messages[(row['ZSTANZAID'], chat)] = row
        if not row['ZRECEIPTINFO']:
            continue
        try:
            decoded, _ = blackboxprotobuf.decode_message(row['ZRECEIPTINFO'])
        except Exception as ex:  # pylint: disable=broad-exception-caught
            # blackboxprotobuf raises library-internal types
            logfunc(f'WhatsApp Message Receipts: a ZRECEIPTINFO blob could not be decoded ({type(ex).__name__})')
            continue
        for sub in _entries(decoded.get('7')):
            if not isinstance(sub, dict):
                continue
            for field, emoji_field in (('1', '3'), ('2', '2')):
                for entry in _entries(sub.get(field)):
                    if isinstance(entry, dict) and entry.get('1'):
                        reactions[(_text(entry['1']), chat)] = (row, _text(entry.get(emoji_field)))
    return messages, reactions


def _push_names(chat_db):
    if not chat_db or not does_table_exist_in_db(chat_db, 'ZWAPROFILEPUSHNAME'):
        return {}
    return {row['ZJID']: _text(row['ZPUSHNAME'])
            for row in _fetch(chat_db, 'SELECT ZJID, ZPUSHNAME FROM ZWAPROFILEPUSHNAME') if row['ZJID']}


@artifact_processor
def whatsAppMessageReceipts(context):
    data_list = []
    sources = []
    for infra, files in _stores(context):
        if not does_table_exist_in_db(infra, 'receipt_device'):
            sources.append(infra)
            continue
        played = 'played_timestamp' if does_column_exist_in_db(infra, 'receipt_device', 'played_timestamp') else 'NULL'
        rows = _fetch(infra, f'''
            SELECT stanza_id, chat_jid, user_jid, device_id, send_timestamp, delivered_timestamp,
                   read_timestamp, {played} AS played_timestamp
            FROM receipt_device ORDER BY send_timestamp, _id''')
        sources.append(infra)
        if not rows:
            continue
        chat_db = files.get('ChatStorage.sqlite')
        messages, reactions = _message_index(chat_db)
        names = _push_names(chat_db)
        lid = _Lid(files)
        sources.extend(path for path in files.values() if path)
        for row in rows:
            key = (row['stanza_id'], row['chat_jid'])
            emoji = ''
            if key in messages:
                item, parent = 'Message', messages[key]
            elif key in reactions:
                parent, emoji = reactions[key]
                item = 'Reaction'
            else:
                item, parent = 'Not linked', None
            is_lid = _text(row['user_jid']).endswith('@lid')
            bare = _bare(row['user_jid'])
            data_list.append((
                _time(row['send_timestamp']), _time(row['delivered_timestamp']), _time(row['read_timestamp']),
                _time(row['played_timestamp']),
                convert_cocoa_core_data_ts_to_utc(parent['ZMESSAGEDATE']) if parent else '',
                item, row['user_jid'], names.get(row['user_jid'], ''),
                lid.book_by_lid.get(bare, '') if is_lid else '', lid.phone(bare)[0] if is_lid else '',
                row['device_id'], row['chat_jid'],
                _text(parent['ZPARTNERNAME']) if parent else '', emoji,
                _text(parent['ZTEXT']) if parent else '', parent['ZMESSAGETYPE'] if parent else '',
                row['stanza_id']))

    data_headers = (('Send Timestamp', 'datetime'), ('Delivered Timestamp', 'datetime'),
                    ('Read Timestamp', 'datetime'), ('Played Timestamp', 'datetime'),
                    ('Message Timestamp', 'datetime'), 'Item', 'User JID', 'User Push Name',
                    'User Address Book Name', ('User Phone Number', 'phonenumber'), 'Device ID', 'Chat JID',
                    'Chat Name', 'Reaction', 'Message', 'Message Type (as stored)', 'Stanza ID')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
