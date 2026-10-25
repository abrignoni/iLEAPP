__artifacts_v2__ = {
    "smsReactions": {
        "name": "SMS & iMessage - Reactions",
        "description": "Tapbacks, emoji reactions and stickers placed on a message, and tapback removals, "
                       "read from message.associated_message_type and associated_message_guid in sms.db, "
                       "with the message they point to.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per message row whose associated_message_type is 1000 (sticker) or in the range "
                 "2000 to 3007. The SMS artifact lists the same rows as ordinary messages whose text is "
                 "the system-written phrase; this artifact reads them as reactions and resolves the "
                 "target. Reaction is the name for the stored type: 2000 Loved, 2001 Liked, 2002 "
                 "Disliked, 2003 Laughed at, 2004 Emphasized, 2005 Questioned, 2006 Emoji (the emoji is "
                 "in associated_message_emoji, iOS 17 and later), 1000 Sticker (the row has a sticker "
                 "attachment). The names were checked against the system-written text of the same rows: "
                 "in 9 databases, 28,076 of the 29,574 rows of type 2000 to 2005 start with the verb that "
                 "matches the type (Loved, Liked, Disliked, Laughed at, Emphasized, Questioned), none "
                 "starts with a verb that belongs to another type, and the remaining 1,498 start with "
                 "something else (empty text or another language). That text is not copied here. A "
                 "stored type 3000 to 3007 is read as the removal of the reaction numbered 1000 lower. "
                 "That reading and the names above follow the mapping in the imessage-exporter project "
                 "(imessage-database/src/tables/messages/message.rs at commit 4d90fc8d, lines 1243 to 1265, "
                 "https://github.com/ReagentX/imessage-exporter/blob/"
                 "4d90fc8d20a745c0a8acc1e01c0631c4bab89cb4/imessage-database/src/tables/messages/"
                 "message.rs#L1243-L1265, which also lists 2007 and 3007 as Sticker; only 1000 was "
                 "observed) and are only partly checked against data: of 76 removal rows "
                 "in the 9 databases, 9 have an add row of the matching type for the same target still "
                 "in the table, and for the others the add row is not in the database, so the absence "
                 "of an add row says nothing about whether a reaction was added; the same project documents "
                 "that the add row is removed when a tapback is removed (imessage-database/src/"
                 "message_types/variants.rs, lines 18 to 28, "
                 "https://github.com/ReagentX/imessage-exporter/blob/"
                 "4d90fc8d20a745c0a8acc1e01c0631c4bab89cb4/imessage-database/src/message_types/"
                 "variants.rs#L18-L28). Stored types 2 and 3 "
                 "appear on rows that carry a balloon bundle identifier and are app message updates, "
                 "not reactions, so they are not reported; other values between 2008 and 2999 are "
                 "reported as 'Other (as stored)' with the number. Target is found through the message "
                 "guid the row points to (associated_message_guid, 'p:<part>/<guid>' or 'bp:<guid>'). "
                 "Target Part is the part index in that value; Target Range is "
                 "associated_message_range_location and length as stored. Target Message Text is "
                 "message.text or the text decoded from attributedBody and is blank when the target row "
                 "is no longer in the database (a deleted message); Target Found says which. Sender is "
                 "the handle of a received row and blank on a sent row. Sticker File is blank except on "
                 "sticker rows. This is what the database "
                 "stores about each reaction; it does not establish that the person saw the target "
                 "message or read the reaction. Not covered: reactions kept only in iCloud, and the "
                 "system-written text of the row. Observed on 9 databases from full-filesystem "
                 "extractions, iOS 18.1.1 and iOS 26.2.1 to 26.6.2; iOS 16 and 17 databases were not "
                 "available, so those versions are unverified on real data.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "mood-smile",
        "sample_data": {
            "local_ios26_5_2_a": "iOS 26.5.2 | 4,174 rows",
            "local_ios26_2_1_b": "iOS 26.2.1 | 79 rows",
            "local_ios26_3_1_c": "iOS 26.3.1 | 23,375 rows",
            "local_ios26_3_1_d": "iOS 26.3.1 | 37 rows",
            "local_ios26_3_1_e": "iOS 26.3.1 | 89 rows",
            "local_ios26_6_f": "iOS 26.6 | 148 rows",
            "local_ios26_6_1_g": "iOS 26.6.1 | 1,301 rows",
            "local_ios26_6_2_h": "iOS 26.6.2 | 1,251 rows",
            "local_ios18_1_1_i": "iOS 18.1.1 | 362 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, null_absent_columns
from scripts.sms_deep import (cocoa_to_utc, message_columns, messages_by_guid,
                              split_associated_guid, table_exists)

REACTIONS = {
    1000: 'Sticker',
    2000: 'Loved',
    2001: 'Liked',
    2002: 'Disliked',
    2003: 'Laughed at',
    2004: 'Emphasized',
    2005: 'Questioned',
    2006: 'Emoji',
    2007: 'Sticker',
}


def describe_type(value):
    """(Action, Reaction) for a stored associated_message_type."""
    if value in REACTIONS:
        return ('Placed' if value in (1000, 2007) else 'Added'), REACTIONS[value]
    if 3000 <= value <= 3007 and (value - 1000) in REACTIONS:
        return 'Removed', REACTIONS[value - 1000]
    return 'Other (as stored)', f'Type {value}'


def reactions_query(columns):
    emoji = 'm.associated_message_emoji' if 'associated_message_emoji' in columns else 'NULL'
    attachments = (
        "(SELECT group_concat(a.transfer_name, ', ') FROM message_attachment_join j "
        "JOIN attachment a ON a.ROWID = j.attachment_id WHERE j.message_id = m.ROWID)")
    return f'''
        SELECT m.date, m.is_from_me, CASE WHEN m.is_from_me = 0 THEN h.id END, c.chat_identifier,
               m.associated_message_type, {emoji}, m.associated_message_guid,
               m.associated_message_range_location, m.associated_message_range_length,
               {attachments}, m.service, m.destination_caller_id, cmj.chat_id, c.display_name,
               m.ROWID, m.guid
        FROM message m
        LEFT JOIN handle h ON h.ROWID = m.handle_id
        LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
        LEFT JOIN chat c ON c.ROWID = cmj.chat_id
        WHERE m.associated_message_type = 1000 OR m.associated_message_type BETWEEN 2000 AND 3007
        ORDER BY m.date, m.ROWID
    '''


@artifact_processor
def smsReactions(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Reaction Timestamp', 'datetime'), 'Action', 'Reaction', 'Emoji', 'From Me', 'Sender',
        'Chat Contact ID', 'Chat Name', 'Target Message Text', 'Target Sender', 'Target Part',
        'Target Range (Location, Length)', ('Target Timestamp', 'datetime'), 'Target Found',
        'Sticker File', 'Stored Type', 'Service', 'Destination Caller ID', 'Chat ID',
        'Message Row ID', 'Message GUID', 'Target Message GUID')
    data_list = []

    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return data_headers, data_list, source_path
    try:
        columns = message_columns(db)
        if not {'associated_message_type', 'associated_message_guid'} <= columns \
                or not table_exists(db, 'chat_message_join'):
            return data_headers, data_list, source_path
        query = null_absent_columns(source_path, reactions_query(columns))
        rows = db.execute(query).fetchall()
        parsed = [split_associated_guid(row[6]) for row in rows]
        targets = messages_by_guid(db, {guid for _, guid in parsed if guid})
    finally:
        db.close()

    for row, (part, target_guid) in zip(rows, parsed):
        (date, from_me, sender, chat_identifier, stored_type, emoji, _assoc_guid, range_loc,
         range_len, sticker_file, service, caller_id, chat_id, chat_name, rowid, guid) = row
        action, reaction = describe_type(stored_type)
        target = targets.get(target_guid)
        if target:
            _t_rowid, t_date, t_from_me, t_sender, t_text = target
            t_sender_label = 'Me' if t_from_me else (t_sender or '')
            data_target = (t_text or '', t_sender_label, cocoa_to_utc(t_date), 'Yes')
        else:
            data_target = ('', '', '', 'No' if target_guid else '')
        target_range = '' if range_loc is None and range_len is None else f'{range_loc}, {range_len}'
        data_list.append((
            cocoa_to_utc(date), action, reaction, emoji or '', from_me, sender or '',
            chat_identifier or '', chat_name or '', data_target[0], data_target[1],
            '' if part is None else part, target_range, data_target[2], data_target[3],
            sticker_file or '', stored_type, service or '', caller_id or '', chat_id, rowid, guid,
            target_guid))

    return data_headers, data_list, source_path
