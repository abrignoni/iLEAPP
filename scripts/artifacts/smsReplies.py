__artifacts_v2__ = {
    "smsReplies": {
        "name": "SMS & iMessage - Inline Replies",
        "description": "Messages sent as an inline reply to an earlier message (message.thread_originator_guid "
                       "in sms.db), with the message they reply to.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "One row per message row whose thread_originator_guid is set (the iOS 14 inline "
                 "reply feature). Reply Text is message.text, or the text decoded from attributedBody "
                 "where text is empty. Originator is the message row whose guid equals "
                 "thread_originator_guid; Originator Found is No when that row is no longer in the "
                 "database, for example a deleted message, and its columns are then blank. The column "
                 "holds the guid of the message that started the thread; this artifact does not claim "
                 "that it is the message directly above a reply. Originator Part is "
                 "thread_originator_part as stored; it has three colon-separated numbers and the third "
                 "equals the length of the originator's text in 4,913 of the 6,017 replies whose "
                 "originator was found, so it is shown as stored and not interpreted. The reply_to_guid "
                 "column is not used: in the iOS 26.5.2 database checked it holds a 36-character guid on "
                 "49,981 of 68,136 rows, including messages that are not replies, and it equals "
                 "thread_originator_guid in only 56 of the 1,360 replies there, so it is not a reply "
                 "marker on that version. Replies keep their own sender, time and chat as stored. This is "
                 "what the database stores; it does not establish that the sender read the originator "
                 "message before replying. Observed on 9 databases from full-filesystem extractions "
                 "(iOS 18.1.1 and iOS 26.2.1 to 26.6.2): 6,035 replies. The column exists from iOS 14."
                 " On single databases of the nine Chat Name was empty on every row (no named group chat), Originator Found held one value (Yes) on every row, and Service and Destination Caller ID held one value on every row (one iMessage line). The artifact ran without error on the 22 of 32 corpus iOS images that hold an sms.db (iOS 12.4 to 26.5.2); the other 10 had no sms.db. sample_data lists six of the 22, iOS 14.3 to 26.5.2.",
        "paths": ('*/Library/SMS/sms.db*',),
        "output_types": "standard",
        "artifact_icon": "corner-down-right",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "hickman_ios15": "iOS 15.3.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, null_absent_columns
from scripts.sms_deep import time_first, cocoa_to_utc, message_columns, message_text, messages_by_guid


@artifact_processor
def smsReplies(context):
    """ see artifact description """
    source_path = get_file_path(context.get_files_found(), "sms.db")
    data_headers = (
        ('Reply Timestamp', 'datetime'), 'From Me', 'Sender', 'Chat Contact ID', 'Chat Name',
        'Reply Text', 'Originator Text', 'Originator Sender', ('Originator Timestamp', 'datetime'),
        'Originator Found', 'Originator Part (as stored)', 'Service', 'Destination Caller ID',
        'Chat ID', 'Message Row ID', 'Message GUID', 'Originator GUID')
    data_list = []

    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return data_headers, data_list, source_path
    try:
        if 'thread_originator_guid' not in message_columns(db):
            return data_headers, data_list, source_path
        query = null_absent_columns(source_path, '''
            SELECT m.date, m.is_from_me, CASE WHEN m.is_from_me = 0 THEN h.id END,
                   c.chat_identifier, c.display_name, m.text, m.attributedBody,
                   m.thread_originator_guid, m.thread_originator_part, m.service,
                   m.destination_caller_id, cmj.chat_id, m.ROWID, m.guid
            FROM message m
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            LEFT JOIN chat c ON c.ROWID = cmj.chat_id
            WHERE m.thread_originator_guid IS NOT NULL AND m.thread_originator_guid != ''
            ORDER BY m.date, m.ROWID
        ''')
        rows = db.execute(query).fetchall()
        originators = messages_by_guid(db, {row[7] for row in rows})
    finally:
        db.close()

    for (date, from_me, sender, chat_identifier, chat_name, text, body, originator_guid,
         originator_part, service, caller_id, chat_id, rowid, guid) in rows:
        originator = originators.get(originator_guid)
        if originator:
            _rowid, o_date, o_from_me, o_sender, o_text = originator
            found = ('Yes', o_text or '', 'Me' if o_from_me else (o_sender or ''),
                     cocoa_to_utc(o_date))
        else:
            found = ('No', '', '', '')
        data_list.append((
            cocoa_to_utc(date), from_me, sender or '', chat_identifier or '', chat_name or '',
            message_text(text, body) or '', found[1], found[2], found[3], found[0],
            originator_part or '', service or '', caller_id or '', chat_id, rowid, guid,
            originator_guid))
    return time_first(data_headers, data_list) + (source_path,)
