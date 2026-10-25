__artifacts_v2__ = {
    "smsEditHistory": {
        "name": "SMS & iMessage - Edit History",
        "description": "The versions stored for an edited iMessage part, read from the edit history in "
                       "message.message_summary_info (key ec), with the time of each version.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per stored version of one edited part of a message whose date_edited is set "
                 "and whose message_summary_info holds an ec (edit history) entry. Version is the "
                 "position in the stored list (1 is the first stored version) and Versions in Part is "
                 "the list length. Version Timestamp is the d value stored with the version, Cocoa "
                 "seconds converted to UTC. Version Text is the text of the NSAttributedString "
                 "(typedstream) stored with the version; the text column of an edited message is empty "
                 "and the current text is in attributedBody. Observed on 9 databases from "
                 "full-filesystem extractions (iOS 18.1.1 and iOS 26.2.1 to 26.6.2): 466 edited "
                 "messages, each with one ec entry; 452 lists hold 2 versions and 14 hold 3, so a list "
                 "is not limited to one edit. 463 of the 466 were edited on part 0, and in all 463 the "
                 "first version's timestamp equals the message date. In 463 of the 466 the last stored "
                 "version has the same text as the current attributedBody; the other 3 are edits to a "
                 "part other than 0 of a message with several parts, where attributedBody holds the "
                 "whole message. date_edited equals the timestamp of the last stored version in 466 of "
                 "466 (to within 2 ms). The keys ec, otr, rp, d and t, and the order of the list (the "
                 "first item is the original text and the last is the current text), follow the layout "
                 "described in the imessage-exporter project (imessage-database/src/message_types/"
                 "edited.rs, lines 81 to 96, https://github.com/ReagentX/imessage-exporter/blob/"
                 "4d90fc8d20a745c0a8acc1e01c0631c4bab89cb4/imessage-database/src/message_types/"
                 "edited.rs#L81-L96) and match the data counted here. Current Version marks the last "
                 "stored version. Edit Count is Versions in Part minus 1 and assumes the list holds the "
                 "original and every later version; the project documents the list that way, but the "
                 "database itself does not state it. Original Text Length is "
                 "the le value of the otr (original text range) entry for the part, as stored. A "
                 "message with several parts keeps the part number as the dictionary key, shown in Part; "
                 "Part was 0 on 463 of the 466 messages, so the column is constant on most databases and "
                 "is kept for the other cases. The ep (edited parts) list is not reported because it "
                 "repeated Part on every row. This is what the database stores for each "
                 "version; it does not establish who edited or from which device, and a version that "
                 "Messages removed from the list is not recoverable here. Not covered: edit history held "
                 "only in iCloud, edits made before iOS 16 (the feature did not exist), and the euh "
                 "(edited-unread handles) key, which is not decoded. iOS 16 and 17 databases were not "
                 "available; those versions are unverified on real data.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "edit",
        "sample_data": {
            "local_ios26_5_2_a": "iOS 26.5.2 | 441 rows",
            "local_ios26_2_1_b": "iOS 26.2.1 | 48 rows",
            "local_ios26_3_1_c": "iOS 26.3.1 | 20 rows",
            "local_ios26_3_1_d": "iOS 26.3.1 | 10 rows",
            "local_ios26_3_1_e": "iOS 26.3.1 | 53 rows",
            "local_ios26_6_f": "iOS 26.6 | 30 rows",
            "local_ios26_6_1_g": "iOS 26.6.1 | 117 rows",
            "local_ios26_6_2_h": "iOS 26.6.2 | 66 rows",
            "local_ios18_1_1_i": "iOS 18.1.1 | 161 rows",
        },
    },
    "smsUnsentMessages": {
        "name": "SMS & iMessage - Unsent Message Parts",
        "description": "Message parts marked retracted (unsent) in message.message_summary_info (key rp), "
                       "with the time stored in date_edited and the original text length.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per part listed in the rp (retracted parts) list of message_summary_info, and "
                 "one per message whose date_retracted column is set. When a part is unsent Messages "
                 "keeps the row but not the text: in 7 of 9 databases checked (iOS 18.1.1 and iOS 26.2.1 "
                 "to 26.6.2) 184 messages had an rp entry (192 parts); all 184 had no text, and had no "
                 "attributedBody unless another part of the message was kept (part_count shows the "
                 "parts that remain). Original Text Length is the le value of the otr entry for the "
                 "part, as stored; it is the only trace of the removed text that this artifact reports "
                 "and the text itself is not recoverable from these columns. Unsent Timestamp is "
                 "date_edited, converted to UTC. For the 184 messages date_edited was between 2.8 and "
                 "118.7 seconds after the message date, which agrees with a two-minute unsend window; it "
                 "is the time stored with the change, and the column does not name the action, so a row "
                 "is labelled unsent because of the rp entry and not because of the time. "
                 "date_retracted was 0 on every row of the 9 databases (it is reported as stored in "
                 "Retracted Timestamp and is blank when 0), so on those versions the rp entry is what "
                 "marks an unsent part. A message with no rp entry and no date_retracted is not shown, "
                 "and a message that was deleted from the database leaves no row, so an empty result is "
                 "not evidence that nothing was unsent. Remaining Text is the text of the kept parts, "
                 "blank when the whole message was unsent. This artifact does not establish who unsent "
                 "the message or from which device. Service and Destination Caller ID are the message row's "
                 "values as stored and are uniform on a device that used one service and one line. iOS "
                 "16 and 17 databases were not available; those versions are unverified on real data.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "message-off",
        "sample_data": {
            "local_ios26_5_2_a": "iOS 26.5.2 | 31 rows",
            "local_ios26_2_1_b": "iOS 26.2.1 | 59 rows",
            "local_ios26_3_1_c": "iOS 26.3.1 | 0 rows",
            "local_ios26_3_1_d": "iOS 26.3.1 | 1 row",
            "local_ios26_3_1_e": "iOS 26.3.1 | 61 rows",
            "local_ios26_6_f": "iOS 26.6 | 0 rows",
            "local_ios26_6_1_g": "iOS 26.6.1 | 4 rows",
            "local_ios26_6_2_h": "iOS 26.6.2 | 6 rows",
            "local_ios18_1_1_i": "iOS 18.1.1 | 30 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, null_absent_columns
from scripts.sms_deep import (cocoa_to_utc, message_columns, message_text, summary_info,
                              typedstream_text)

MESSAGE_CONTEXT = '''
        SELECT m.ROWID, m.guid, m.date, m.date_edited, {retracted}, m.is_from_me,
               CASE WHEN m.is_from_me = 0 THEN h.id END, c.chat_identifier, c.display_name,
               cmj.chat_id, m.service, m.destination_caller_id, m.text, m.attributedBody,
               m.message_summary_info, {part_count}
        FROM message m
        LEFT JOIN handle h ON h.ROWID = m.handle_id
        LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
        LEFT JOIN chat c ON c.ROWID = cmj.chat_id
        WHERE {where}
        ORDER BY m.date, m.ROWID
'''


def read_rows(source_path, where_template):
    """Message rows with context for the edit and unsend artifacts; [] when the columns are absent."""
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    try:
        columns = message_columns(db)
        if 'message_summary_info' not in columns or 'date_edited' not in columns:
            return []
        retracted = 'm.date_retracted' if 'date_retracted' in columns else 'NULL'
        part_count = 'm.part_count' if 'part_count' in columns else 'NULL'
        where = where_template.format(retracted=retracted)
        query = null_absent_columns(source_path, MESSAGE_CONTEXT.format(
            retracted=retracted, part_count=part_count, where=where))
        return db.execute(query).fetchall()
    finally:
        db.close()


def part_sort_key(part):
    return (0, int(part)) if str(part).isdigit() else (1, str(part))


@artifact_processor
def smsEditHistory(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Version Timestamp', 'datetime'), 'Part', 'Version', 'Versions in Part', 'Current Version',
        'Version Text', 'Edit Count', ('Message Timestamp', 'datetime'),
        ('Last Edited Timestamp', 'datetime'), 'Original Text Length',
        'From Me', 'Sender', 'Chat Contact ID', 'Chat Name', 'Service', 'Destination Caller ID',
        'Chat ID', 'Message Row ID', 'Message GUID')
    data_list = []
    rows = read_rows(source_path, 'm.date_edited > 0 AND m.message_summary_info IS NOT NULL')
    for row in rows:
        (rowid, guid, date, edited, _retracted, from_me, sender, chat_identifier, chat_name,
         chat_id, service, caller_id, _text, _body, summary_blob, _parts) = row
        info = summary_info(summary_blob)
        history = info.get('ec')
        if not isinstance(history, dict):
            continue
        original_range = info.get('otr') if isinstance(info.get('otr'), dict) else {}
        for part in sorted(history, key=part_sort_key):
            versions = history[part]
            if not isinstance(versions, list):
                continue
            span = original_range.get(part) if isinstance(original_range.get(part), dict) else {}
            for number, version in enumerate(versions, start=1):
                if not isinstance(version, dict):
                    continue
                data_list.append((
                    cocoa_to_utc(version.get('d')), part, number, len(versions),
                    'Yes' if number == len(versions) else '',
                    typedstream_text(version.get('t')) or '', len(versions) - 1,
                    cocoa_to_utc(date), cocoa_to_utc(edited),
                    span.get('le', ''), from_me, sender or '',
                    chat_identifier or '', chat_name or '', service or '', caller_id or '',
                    chat_id, rowid, guid))
    return data_headers, data_list, source_path


@artifact_processor
def smsUnsentMessages(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Unsent Timestamp', 'datetime'), 'Unsent Part', 'Original Text Length',
        'Remaining Text', 'Parts Remaining (as stored)', ('Message Timestamp', 'datetime'),
        ('Retracted Timestamp', 'datetime'), 'From Me', 'Sender', 'Chat Contact ID',
        'Chat Name', 'Service', 'Destination Caller ID', 'Chat ID', 'Message Row ID',
        'Message GUID')
    data_list = []
    rows = read_rows(source_path, '(m.date_edited > 0 OR {retracted} > 0)')
    for row in rows:
        (rowid, guid, date, edited, retracted, from_me, sender, chat_identifier, chat_name,
         chat_id, service, caller_id, text, body, summary_blob, part_count) = row
        info = summary_info(summary_blob)
        retracted_parts = info.get('rp')
        if not isinstance(retracted_parts, list):
            retracted_parts = []
        if not retracted_parts and not retracted:
            continue
        original_range = info.get('otr') if isinstance(info.get('otr'), dict) else {}
        remaining = message_text(text, body) or ''
        parts = retracted_parts or ['']
        for part in parts:
            span = original_range.get(str(part)) if isinstance(original_range.get(str(part)), dict) else {}
            data_list.append((
                cocoa_to_utc(edited), part, span.get('le', ''), remaining,
                '' if part_count is None else part_count, cocoa_to_utc(date),
                cocoa_to_utc(retracted), from_me, sender or '', chat_identifier or '',
                chat_name or '', service or '', caller_id or '', chat_id, rowid, guid))
    return data_headers, data_list, source_path
