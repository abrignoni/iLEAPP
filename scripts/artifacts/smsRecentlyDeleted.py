__artifacts_v2__ = {
    "smsRecentlyDeleted": {
        "name": "SMS & iMessage - Recently Deleted Messages",
        "description": "Messages kept for recovery after deletion (chat_recoverable_message_join in sms.db), "
                       "with the deletion time and the message that is still held in the message table.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per row of chat_recoverable_message_join (chat_id, message_id, delete_date, "
                 "ck_sync_state), joined to the message row with that ROWID. Deleted Timestamp is "
                 "delete_date, nanoseconds since 2001-01-01 converted to UTC. The message row stays in the message table with its text in message.text or attributedBody, and in the 204 rows found none of "
                 "these message rows had a chat_message_join row (Still Linked to Chat is No), which is "
                 "how they differ from messages shown in a conversation. Text is message.text, or the "
                 "text decoded from attributedBody where text is empty. Chat Contact ID and Chat Name "
                 "come from the chat the join row names. Attachments is the transfer name of each "
                 "attachment joined to the message. Sync State is ck_sync_state as stored; its values "
                 "are not interpreted. Sync State was constant within each database (0 or 1). Still Linked to Chat was No on every row, so it is a constant column kept as the check "
                 "that separates these rows from messages in a conversation. Deleted Timestamp is not limited to a fixed window in the data: "
                 "in one iOS 26.5.2 database the earliest and latest Deleted Timestamp are 60 days "
                 "apart, so the rows cannot be assumed to be from the last 30 days. A message removed "
                 "from Recently Deleted leaves no row, so an empty result is not evidence that nothing "
                 "was deleted. This is the state of the database when it was copied; it does not show "
                 "who deleted a message or from which device. Observed on 5 of 9 databases from "
                 "full-filesystem extractions (iOS 26.3.1 to 26.6.2: 204 rows); the other four (iOS "
                 "18.1.1, 26.2.1 and two iOS 26.3.1) held none. The tables are not present before iOS 16. Deleted parts of a message that stays in a conversation are in 'SMS & "
                 "iMessage - Recently Deleted Message Parts'; the sync_deleted_* and "
                 "unsynced_removed_recoverable_messages tables hold only identifiers and are not "
                 "reported."
                 " On single databases of the nine Destination Caller ID and From Me held one value on every row, Sender and Chat Contact ID were identical on every row (one-to-one chats), Chat Name was empty on every row (no named group chat), Attachments was empty on every row (text only), and Sender was empty on every row (it is filled only for received messages). The artifact ran without error on the 22 of 32 corpus iOS images that hold an sms.db (iOS 12.4 to 26.5.2); the other 10 had no sms.db. sample_data lists six of the 22, iOS 14.3 to 26.5.2.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "trash",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 25 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
    "smsRecentlyDeletedParts": {
        "name": "SMS & iMessage - Recently Deleted Message Parts",
        "description": "Message parts kept for recovery after deletion (recoverable_message_part in sms.db), "
                       "with the text of each part.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per row of recoverable_message_part (chat_id, message_id, part_index, "
                 "delete_date, part_text, ck_sync_state). Part Text is the text of the "
                 "NSAttributedString (typedstream) in part_text. Deleted Timestamp is delete_date, "
                 "nanoseconds since 2001-01-01 converted to UTC. In the 11 rows found, the message rows "
                 "named by the parts were still linked to their chat (Still Linked to Chat is Yes), so "
                 "the rest of the message is shown in the conversation; Remaining Message Text is the "
                 "text the message row still holds (blank when none). Part Index is the index as "
                 "stored. Sync State was constant (1) on all rows, Still Linked to Chat was uniform (Yes) "
                 "and Chat Name was blank on all rows of the first device; the columns are kept because "
                 "they come from the same joins as the other artifact. In the iOS 26.5.2 database the Deleted Timestamps of these rows are from one "
                 "to three years before the extraction, so the rows are kept long after the deletion "
                 "time they carry. Rows were found on 2 of the 9 databases checked (iOS 26.3.1 and "
                 "26.5.2); the other seven held none, and no corpus image held a row, so this artifact has been exercised on two devices. A part removed from Recently "
                 "Deleted leaves no row, so an empty result is not evidence that no part was deleted."
                 " On a single image Sender was empty on every row (it is filled only for received messages). The artifact ran without error on the 22 of 32 corpus iOS images that hold an sms.db (iOS 12.4 to 26.5.2); the other 10 had no sms.db. sample_data lists six of the 22, iOS 14.3 to 26.5.2.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "trash",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly
from scripts.sms_deep import time_first, cocoa_to_utc, message_text, table_exists, typedstream_text

ATTACHMENTS = ("(SELECT group_concat(a.transfer_name, ', ') FROM message_attachment_join j "
               "JOIN attachment a ON a.ROWID = j.attachment_id WHERE j.message_id = m.ROWID)")

MESSAGE_SELECT = f'''
    SELECT {{delete_date}}, m.date, m.text, m.attributedBody, m.is_from_me,
           CASE WHEN m.is_from_me = 0 THEN h.id END, c.chat_identifier, c.display_name,
           {ATTACHMENTS}, EXISTS(SELECT 1 FROM chat_message_join x WHERE x.message_id = m.ROWID),
           {{extra}}, m.service, m.destination_caller_id, r.chat_id, m.ROWID, m.guid
    FROM {{table}} r
    JOIN message m ON m.ROWID = r.message_id
    LEFT JOIN handle h ON h.ROWID = m.handle_id
    LEFT JOIN chat c ON c.ROWID = r.chat_id
    ORDER BY r.delete_date, m.ROWID
'''


@artifact_processor
def smsRecentlyDeleted(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Deleted Timestamp', 'datetime'), ('Message Timestamp', 'datetime'), 'From Me', 'Sender',
        'Chat Contact ID', 'Chat Name', 'Text', 'Attachments', 'Still Linked to Chat',
        'Sync State (as stored)', 'Service', 'Destination Caller ID', 'Chat ID',
        'Message Row ID', 'Message GUID')
    data_list = []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return data_headers, data_list, source_path
    try:
        if not table_exists(db, 'chat_recoverable_message_join'):
            return data_headers, data_list, source_path
        rows = db.execute(MESSAGE_SELECT.format(
            delete_date='r.delete_date', extra='r.ck_sync_state',
            table='chat_recoverable_message_join')).fetchall()
    finally:
        db.close()
    for (deleted, date, text, body, from_me, sender, chat_identifier, chat_name, attachments,
         linked, sync_state, service, caller_id, chat_id, rowid, guid) in rows:
        data_list.append((
            cocoa_to_utc(deleted), cocoa_to_utc(date), from_me, sender or '',
            chat_identifier or '', chat_name or '', message_text(text, body) or '',
            attachments or '', 'Yes' if linked else 'No', sync_state, service or '',
            caller_id or '', chat_id, rowid, guid))
    return time_first(data_headers, data_list) + (source_path,)


@artifact_processor
def smsRecentlyDeletedParts(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Deleted Timestamp', 'datetime'), 'Part Index', 'Part Text', ('Message Timestamp', 'datetime'),
        'From Me', 'Sender', 'Chat Contact ID', 'Chat Name', 'Remaining Message Text',
        'Still Linked to Chat', 'Sync State (as stored)', 'Service', 'Destination Caller ID',
        'Chat ID', 'Message Row ID', 'Message GUID')
    data_list = []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return data_headers, data_list, source_path
    try:
        if not table_exists(db, 'recoverable_message_part'):
            return data_headers, data_list, source_path
        rows = db.execute('''
            SELECT r.delete_date, r.part_index, r.part_text, m.date, m.text, m.attributedBody,
                   m.is_from_me, CASE WHEN m.is_from_me = 0 THEN h.id END, c.chat_identifier,
                   c.display_name,
                   EXISTS(SELECT 1 FROM chat_message_join x WHERE x.message_id = m.ROWID),
                   r.ck_sync_state, m.service, m.destination_caller_id, r.chat_id, m.ROWID, m.guid
            FROM recoverable_message_part r
            JOIN message m ON m.ROWID = r.message_id
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            LEFT JOIN chat c ON c.ROWID = r.chat_id
            ORDER BY r.delete_date, m.ROWID, r.part_index
        ''').fetchall()
    finally:
        db.close()
    for (deleted, part_index, part_text, date, text, body, from_me, sender, chat_identifier,
         chat_name, linked, sync_state, service, caller_id, chat_id, rowid, guid) in rows:
        data_list.append((
            cocoa_to_utc(deleted), part_index, typedstream_text(part_text) or '',
            cocoa_to_utc(date), from_me, sender or '', chat_identifier or '', chat_name or '',
            message_text(text, body) or '', 'Yes' if linked else 'No', sync_state,
            service or '', caller_id or '', chat_id, rowid, guid))
    return time_first(data_headers, data_list) + (source_path,)
