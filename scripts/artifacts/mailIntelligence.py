__artifacts_v2__ = {
    "mailIntelligenceEvents": {
        "name": "Apple Mail - Intelligence Events",
        "description": "Events recorded in Mail's mailIntelligence biome stream (app launch, "
                       "message fetched, viewed, read changed, sent, moved, link clicked), with "
                       "the subject and sender of the message each names where the Envelope "
                       "Index still holds it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Apple Mail",
        "notes": "One row per written record of the SEGB file at "
                 "Library/Mail/BiomeStream/mailIntelligence. Each record is an NSKeyedArchiver "
                 "archive holding EFPropertyKey_eventName, EFPropertyKey_messageId and "
                 "EFPropertyKey_payload; Event is the event name as stored and the payload keys "
                 "are reported in their own columns as stored. No Apple documentation of this "
                 "stream was found, so what each event marks is read from its name only, and the "
                 "units of duration are not established. SEGB Timestamp is the SEGB record time; "
                 "what it marks was not checked against another record. Subject, Sender Address "
                 "and Sender Name come from the Envelope Index row whose global_message_id equals "
                 "the payload's globalMessageID, with the subject and address read from the "
                 "Protected Index beside it, the same join the Apple Email artifact uses; In "
                 "Envelope Index says whether such a row exists, and is empty for events with no "
                 "globalMessageID (app_launch, app_resume, app_background and one message_sent on "
                 "wilkerson_iphone16_ios26). On hill_iphone15pro_ios26 all 80 records are "
                 "message_fetched and all name a message in the Envelope Index, so Event and In "
                 "Envelope Index held one value on every row and Duration, Scrolled To End, Value, "
                 "Mailbox Type, Link Scheme, Categorization Enabled and Account ID are empty on "
                 "every row there; Global Message ID and Persistent ID are identical on every row "
                 "there. On wilkerson_iphone16_ios26 the 1,091 records span March to October 2026; "
                 "453 of the 959 records that carry a globalMessageID name no message in the "
                 "Envelope Index (219 distinct IDs), among them 52 message_view_start and 52 "
                 "message_view_end records. For those, the stream names a message the Envelope "
                 "Index does not hold; why it is absent is not established. Other Payload Fields "
                 "holds any payload key without a column and was empty on every row of both "
                 "images. Only records in the written state are reported, and the stream's "
                 "tombstone folder is not read. Each image has one stream file, so SEGB File held "
                 "one value on every row. iphone11_ios17 holds no stream file.",
        "paths": ('*/mobile/Library/Mail/BiomeStream/mailIntelligence/local/*',
                  '*/mobile/Library/Mail/Envelope Index*',
                  '*/mobile/Library/Mail/Protected Index*'),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 80 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1091 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no stream file",
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
                               does_column_exist_in_db, get_sqlite_db_records, is_sqlite_sidecar,
                               logfunc)

_ARCHIVE_ERRORS = (nd.DeserializeError, plistlib.InvalidFileException, ValueError, TypeError,
                   KeyError, IndexError)
# Payload keys given their own column; any other key is kept in Other Payload Fields.
_SHOWN = ('globalMessageID', 'persistentID', 'duration', 'scrolled_to_end',
          'categorization_enabled', 'value', 'mailbox_type', 'scheme', 'accountID')


def _messages(files_found):
    '''({global message id: (subject, sender address, sender comment)}, Envelope Index path).'''
    envelope = next((path for path in files_found if os.path.basename(path) == 'Envelope Index'
                     and not is_sqlite_sidecar(path)), '')
    if not envelope or not does_column_exist_in_db(envelope, 'messages', 'global_message_id'):
        return None, envelope
    protected = os.path.join(os.path.dirname(envelope), 'Protected Index')
    query = '''
        SELECT main.messages.global_message_id, PI.subjects.subject, PI.addresses.address,
               PI.addresses.comment
        FROM main.messages
        LEFT JOIN PI.subjects ON PI.subjects.ROWID = main.messages.subject
        LEFT JOIN PI.addresses ON PI.addresses.ROWID = main.messages.sender
    '''
    if not os.path.isfile(protected):
        query = ('SELECT global_message_id, NULL, NULL, NULL FROM messages')
    try:
        rows = get_sqlite_db_records(
            envelope, query,
            attach_query=attach_sqlite_db_readonly(protected, 'PI') if os.path.isfile(protected) else None)
    except sqlite3.Error as error:
        logfunc(f'Mail Intelligence: could not read the Envelope Index: {error}')
        return None, envelope
    messages = {}
    for row in rows:
        if row[0] is not None:
            messages.setdefault(row[0], (row[1], row[2], row[3]))
    return messages, envelope


def _text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    return str(value)


@artifact_processor
def mailIntelligenceEvents(context):
    files_found = sorted(str(path) for path in context.get_files_found())
    messages, envelope = _messages(files_found)
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
                logfunc(f'Mail Intelligence: could not read record at offset '
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
        ('SEGB Timestamp', 'datetime'), 'Event', 'Sender Address', 'Sender Name', 'Subject',
        'In Envelope Index', 'Duration (as stored)', 'Scrolled To End', 'Value (as stored)',
        'Mailbox Type (as stored)', 'Link Scheme', 'Categorization Enabled', 'Account ID',
        'Global Message ID', 'Persistent ID', 'Event Message ID', 'Other Payload Fields',
        'SEGB File', 'Offset')
    sources = sorted(read) + ([envelope] if envelope and data_list else [])
    return data_headers, data_list, '\n'.join(sources)
