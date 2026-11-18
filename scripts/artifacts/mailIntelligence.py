__artifacts_v2__ = {
    "mailIntelligenceEvents": {
        "name": "Apple Mail - mailIntelligence Stream Events",
        "description": "Events recorded in the mailIntelligence stream under "
                       "Library/Mail/BiomeStream, with the subject and sender address of the "
                       "message each names where a row of the Envelope Index carries the same "
                       "global message ID.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Apple Mail",
        "notes": "One row per written record of each SEGB file under "
                 "Library/Mail/BiomeStream/mailIntelligence/local. On both tested images every "
                 "record is an NSKeyedArchiver archive holding EFPropertyKey_eventName, "
                 "EFPropertyKey_messageId and EFPropertyKey_payload. Event is the event name as "
                 "stored; ten names were seen on wilkerson_iphone16_ios26 (app_launch, app_resume, "
                 "app_background, message_fetched, message_view_start, message_view_end, "
                 "read_changed, message_sent, message_moved, link_clicked) and one on "
                 "hill_iphone15pro_ios26 (message_fetched). What each event marks is read from its "
                 "name only, and the units of duration are not established. Boolean payload values "
                 "(scrolled_to_end, categorization_enabled, value) are shown as Yes or No; other "
                 "payload values are shown as stored. Message ID is EFPropertyKey_messageId as "
                 "stored; what it identifies was not checked against the Envelope Index. SEGB "
                 "Timestamp is the SEGB record time; what it marks was not checked against another "
                 "record. Subject, Sender Address and Sender Comment come from a messages row of "
                 "the Envelope Index whose global_message_id equals the payload's globalMessageID; "
                 "where several rows share the ID the first by row order is used, and on "
                 "wilkerson_iphone16_ios26 97 IDs had more than one row and the rows agreed. The "
                 "subject, address and comment are read from the Protected Index with the joins "
                 "the Apple Email artifact uses. In Envelope Index says whether such a row exists. "
                 "It is empty for events with no globalMessageID (app_launch, app_resume, "
                 "app_background and one message_sent on wilkerson_iphone16_ios26), and on every "
                 "row when no Envelope Index with a global_message_id column is found or the join "
                 "cannot be read; those paths were not exercised on the tested images. On "
                 "hill_iphone15pro_ios26 all 80 records are message_fetched and all name a message "
                 "in the Envelope Index, so Event and In Envelope Index held one value on every "
                 "row and Duration, Scrolled To End, Value, Mailbox Type, Scheme, Categorization "
                 "Enabled and Account ID are empty on every row there; Global Message ID and "
                 "Persistent ID are identical on every row there. On wilkerson_iphone16_ios26 the "
                 "1,091 records span March to October 2026; 453 of the 959 records that carry a "
                 "globalMessageID have no messages row with that ID (219 distinct IDs), among them "
                 "52 message_view_start and 52 message_view_end records, and why the row is absent "
                 "is not established. Other Payload Fields holds any payload key without a column "
                 "and was empty on every row of both images. Only records in the written state are "
                 "reported; every record on both images was in that state. A tombstone folder "
                 "under the stream is skipped; none of the three images has one. Each image has "
                 "one stream file, so SEGB File held one value on every row; it is kept for images "
                 "with several. iphone11_ios17 has the stream folder with no file in it.",
        "paths": ('*/mobile/Library/Mail/BiomeStream/mailIntelligence/local/*',
                  '*/mobile/Library/Mail/Envelope Index*',
                  '*/mobile/Library/Mail/Protected Index*'),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 80 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1091 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, stream folder with no file",
        },
    }
}


import json
import os
import plistlib
import sqlite3
from datetime import timezone

import nska_deserialize as nd

from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import (artifact_processor, attach_sqlite_db_readonly,
                               does_column_exist_in_db, is_sqlite_sidecar, logfunc,
                               open_sqlite_db_readonly)

_ARCHIVE_ERRORS = (nd.DeserializeError, plistlib.InvalidFileException, ValueError, TypeError,
                   KeyError, IndexError)
# Payload keys given their own column; any other key is kept in Other Payload Fields.
_SHOWN = ('globalMessageID', 'persistentID', 'duration', 'scrolled_to_end',
          'categorization_enabled', 'value', 'mailbox_type', 'scheme', 'accountID')


def _messages(files_found):
    '''({global message id: (subject, sender address, sender comment)}, paths read).

    The first value is None when the Envelope Index cannot be read, so the caller can tell a
    failed join from a message that has no row.
    '''
    envelope = next((path for path in files_found if os.path.basename(path) == 'Envelope Index'
                     and not is_sqlite_sidecar(path)), '')
    if not envelope or not does_column_exist_in_db(envelope, 'messages', 'global_message_id'):
        return None, []
    protected = os.path.join(os.path.dirname(envelope), 'Protected Index')
    has_protected = os.path.isfile(protected)
    if has_protected:
        query = '''
            SELECT main.messages.global_message_id, PI.subjects.subject, PI.addresses.address,
                   PI.addresses.comment
            FROM main.messages
            LEFT JOIN PI.subjects ON PI.subjects.ROWID = main.messages.subject
            LEFT JOIN PI.addresses ON PI.addresses.ROWID = main.messages.sender
            ORDER BY main.messages.ROWID
        '''
    else:
        query = 'SELECT global_message_id, NULL, NULL, NULL FROM messages ORDER BY ROWID'
    db = open_sqlite_db_readonly(envelope)
    if db is None:
        return None, []
    try:
        cursor = db.cursor()
        if has_protected:
            cursor.execute(attach_sqlite_db_readonly(protected, 'PI'))
        rows = cursor.execute(query).fetchall()
    except sqlite3.Error as error:
        logfunc(f'Mail mailIntelligence: could not read the Envelope Index: {error}')
        return None, []
    finally:
        db.close()
    messages = {}
    for row in rows:
        if row[0] is not None:
            messages.setdefault(row[0], (row[1], row[2], row[3]))
    return messages, [envelope] + ([protected] if has_protected else [])


def _text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    return str(value)


@artifact_processor
def mailIntelligenceEvents(context):
    files_found = sorted(str(path) for path in context.get_files_found())
    messages, read_indexes = _messages(files_found)
    data_list, read = [], set()
    for found in files_found:
        relative = context.get_relative_path(found).replace('\\', '/')
        if '/mailIntelligence/local/' not in relative or '/tombstone/' in relative:
            continue
        if not os.path.isfile(found) or os.path.basename(found).startswith('.'):
            continue
        read.add(found)
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                event = nd.deserialize_plist_from_string(record.data)
            except _ARCHIVE_ERRORS as error:
                logfunc(f'Mail mailIntelligence: could not read record at offset '
                        f'{record.data_start_offset} in {os.path.basename(found)}: {error}')
                continue
            if not isinstance(event, dict):
                continue
            payload = event.get('EFPropertyKey_payload')
            payload = payload if isinstance(payload, dict) else {}
            global_id = payload.get('globalMessageID')
            message = messages.get(global_id) if messages is not None and global_id is not None else None
            if messages is None or global_id is None:
                state = ''
            else:
                state = 'Yes' if message else 'No'
            other = {key: value for key, value in payload.items() if key not in _SHOWN}
            data_list.append((
                record.timestamp1.replace(tzinfo=timezone.utc),
                _text(event.get('EFPropertyKey_eventName')),
                _text(message[1]) if message else '',
                _text(message[2]) if message else '',
                _text(message[0]) if message else '',
                state,
                _text(payload.get('duration')),
                _text(payload.get('scrolled_to_end')),
                _text(payload.get('value')),
                _text(payload.get('mailbox_type')),
                _text(payload.get('scheme')),
                _text(payload.get('categorization_enabled')),
                _text(payload.get('accountID')),
                _text(global_id),
                _text(payload.get('persistentID')),
                _text(event.get('EFPropertyKey_messageId')),
                json.dumps(other, default=str) if other else '',
                os.path.basename(found),
                record.data_start_offset,
            ))
    data_headers = (
        ('SEGB Timestamp', 'datetime'), 'Event', 'Sender Address', 'Sender Comment', 'Subject',
        'In Envelope Index', 'Duration (as stored)', 'Scrolled To End', 'Value',
        'Mailbox Type (as stored)', 'Scheme (as stored)', 'Categorization Enabled', 'Account ID',
        'Global Message ID', 'Persistent ID', 'Message ID (as stored)', 'Other Payload Fields',
        'SEGB File', 'Offset')
    sources = sorted(read) + (read_indexes if data_list else [])
    return data_headers, data_list, '\n'.join(sources)
