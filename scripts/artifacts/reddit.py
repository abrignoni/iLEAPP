__artifacts_v2__ = {
    "reddit_chats": {
        "name": "Reddit Chats",
        "description": "Parses chat messages from Reddit",
        "author": "@stark4n6",
        "creation_date": "2026-04-28",
        "requirements": "none",
        "category": "Reddit",
        "notes": "",
        "paths": (
            '*/Library/Caches/MatrixChat/roomsAccount/*/Account-*/Account.db*',
            '*/Library/Caches/MatrixChat/roomsAccount/*/Downloads-*/ContentService.db*',
            '*/Library/Caches/MatrixChat/roomsAccount/*/Downloads-*/Files/*'
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Room ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Server Timestamp",
                "senderColumn": "Sender Display Name",
                "mediaColumn": "Attachment"
            }
        },
    }
}

import json

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, attach_sqlite_db_readonly, check_in_media


def _reddit_owner_id(source_path):
    """Own Matrix user id from the .m.rule.invite_for_me push rule (its
    state_key pattern is the account's own id, server-populated)."""
    rows = get_sqlite_db_records(
        source_path,
        "SELECT ZDATA FROM ZACCOUNTSTORAGEACCOUNTDATAITEM WHERE ZEVENTTYPEFIELD = 'm.push_rules'")
    for (blob,) in rows:
        try:
            rules = json.loads(blob.decode('utf-8', 'replace') if isinstance(blob, (bytes, bytearray)) else blob)
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        for section in ((rules.get('content') or {}).get('global') or {}).values():
            if not isinstance(section, list):
                continue
            for rule in section:
                if rule.get('rule_id') == '.m.rule.invite_for_me':
                    for cond in rule.get('conditions') or []:
                        if cond.get('key') == 'state_key' and cond.get('pattern'):
                            return cond['pattern']
    return ''

@artifact_processor
def reddit_chats(context):
    data_list = []
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "Account.db")
    attachDB = get_file_path(files_found, "ContentService.db")
    
    attach_query = attach_sqlite_db_readonly(attachDB, 'content')
    
    query = '''
    SELECT 
    datetime(m.ZORIGINSERVERDATE + 978307200,'unixepoch') AS 'Timestamp',
	substr(m.ZITEMIDFIELD, instr(m.ZITEMIDFIELD, '|') + 1) AS 'Event ID',
    (SELECT json_extract(u.ZDATA, '$.content.displayname') 
     FROM ZACCOUNTSTORAGETIMELINEITEM u 
     WHERE u.ZSTATEKEYFIELD = m.ZSENDERFIELD 
     AND u.ZEVENTTYPEFIELD = 'm.room.member'
     LIMIT 1) AS 'Sender',
	 m.ZSENDERFIELD,
    GROUP_CONCAT(
        DISTINCT json_extract(rec.ZDATA, '$.content.displayname')
    ) AS 'Recipient(s)',
	CASE 
		WHEN m.ZEVENTTYPEFIELD = 'm.room.message' THEN 'Message'
		WHEN m.ZEVENTTYPEFIELD = 'm.reaction' THEN 'Reaction'
		WHEN m.ZEVENTTYPEFIELD = 'm.room.redaction' THEN 'Deletion for Event ID: ' || json_extract(m.ZDATA, '$.redacts')
		ELSE m.ZEVENTTYPEFIELD
	END AS 'Event Type',
	CASE
		WHEN json_extract(m.ZDATA, '$.content.msgtype') IS NULL AND m.ZEVENTTYPEFIELD = 'm.room.message' THEN 'MESSAGE DELETED'
		WHEN json_extract(m.ZDATA, '$.content.msgtype') = 'm.text' THEN 'Text'
		WHEN json_extract(m.ZDATA, '$.content.msgtype') = 'm.image' THEN 'Image'
		ELSE json_extract(m.ZDATA, '$.content.msgtype')
	END AS 'Message Type',
	CASE
		WHEN m.ZEVENTTYPEFIELD = 'm.reaction' THEN json_extract(m.ZDATA, '$.content."m.relates_to".key')
		ELSE json_extract(m.ZDATA, '$.content.body')
	END AS 'Message',
    att.ZFILENAME AS 'Attachment File',
    substr(m.ZITEMIDFIELD, 1, instr(m.ZITEMIDFIELD, '|') - 1) AS 'Room ID',
	m.ZDATA
    FROM ZACCOUNTSTORAGETIMELINEITEM AS m
    LEFT JOIN content.ZKEYVALUESTORAGEBASEELEMENT AS att
        ON json_extract(m.ZDATA, '$.content.url') = att.ZKEY
    LEFT JOIN ZACCOUNTSTORAGETIMELINEITEM AS rec
        ON substr(rec.ZITEMIDFIELD, 1, instr(rec.ZITEMIDFIELD, '|') - 1) = substr(m.ZITEMIDFIELD, 1, instr(m.ZITEMIDFIELD, '|') - 1)
        AND rec.ZEVENTTYPEFIELD = 'm.room.member'
        AND rec.ZSTATEKEYFIELD != m.ZSENDERFIELD  -- Don't list the sender as a receiver
        AND json_extract(rec.ZDATA, '$.content.membership') = 'join'
    WHERE m.ZEVENTTYPEFIELD = 'm.room.message' OR m.ZEVENTTYPEFIELD = 'm.room.redaction' OR m.ZEVENTTYPEFIELD = 'm.reaction'
    GROUP BY m.ZORIGINSERVERDATE, m.ZITEMIDFIELD
    ORDER BY "Timestamp" ASC;
    '''

    data_headers = (('Server Timestamp', 'datetime'),'Event ID', 'Sender Display Name','Sender ID','Recipient(s)','Event Type','Message Type','Message','Attachment Cached Name',('Attachment','media'),'Room ID','Direction')

    owner_id = _reddit_owner_id(source_path)

    db_records = get_sqlite_db_records(source_path, query, attach_query)

    for record in db_records:
        attachment = ''
        for x in files_found:
            if str(record[8]) in x:
                attachment = check_in_media(x,str(record[8]))
        if owner_id and record[3]:
            direction = 'Outgoing' if record[3] == owner_id else 'Incoming'
        else:
            direction = ''
        data_list.append((record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], attachment, record[9], direction))

    return data_headers, data_list, source_path