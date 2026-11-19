__artifacts_v2__ = {
    "get_biomeNotificationDelivery": {
        "name": "Biome - Notification Delivery",
        "description": "Notifications delivered to the device, from the Biome Notification.Delivery stream, "
                       "with the delivering app and the app's own identifier for the notified item. Messages "
                       "notifications are matched to sms.db on message.guid.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are not sourced from Apple code; they are inferred from one image (iOS 27.2, "
                  "24B119), whose stream held 52 written and 164 deleted records. Item Identifier is field 1 and "
                  "Bundle ID field 2. Delivery Date is field 3, a double read as Unix seconds: on 51 of the 52 "
                  "written rows it is within seconds of the SEGB timestamp; on one Life360 row it is about a day "
                  "earlier. For com.apple.MobileSMS rows field 1 held a message GUID, and both such rows matched "
                  "sms.db message.guid; the matched message's date, sender handle, direction and text are shown. "
                  "On one of them the message date is six days before the delivery date, so the delivery date is "
                  "not the time the message was sent. For com.apple.mobilemail rows field 1 held small "
                  "integers; that they are Envelope Index row ids is not verified and they are not matched. "
                  "Deleted records keep only their SEGB timestamp. On the tested image the stream held one "
                  "SEGB file, so Filename held one value on all 216 rows."),
        "paths": ('*/Biome/streams/restricted/Notification.Delivery/local/*',
                  '*/mobile/Library/SMS/sms.db*'),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | 216 rows",
        }
    }
}

import os
import struct
from datetime import timezone
from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, logfunc,
                               open_sqlite_db_readonly, convert_ts_int_to_utc)

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)

_TYPEDEF = {
    '1': {'type': 'bytes', 'name': ''},
    '2': {'type': 'bytes', 'name': ''},
    '3': {'type': 'double', 'name': ''},
}

_SMS_BUNDLE = 'com.apple.MobileSMS'


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None else str(value)


def _sms_lookup(sms_db):
    """guid -> (date, handle, direction, text) for every message in sms.db."""
    if not sms_db:
        return {}
    messages = {}
    try:
        db = open_sqlite_db_readonly(sms_db)
        rows = db.execute('''
            SELECT message.guid, message.date, handle.id, message.is_from_me, message.text
            FROM message LEFT JOIN handle ON message.handle_id = handle.ROWID''').fetchall()
        db.close()
    except Exception as ex:  # pylint: disable=broad-except
        logfunc(f'Biome Notification Delivery: could not read {sms_db}: {ex}')
        return {}
    for guid, date, handle, from_me, text in rows:
        if not guid:
            continue
        # sms.db dates are nanoseconds since 2001-01-01 from iOS 11 on, seconds before that
        seconds = date / 1e9 if date and date > 1e11 else date
        when = convert_ts_int_to_utc(int(seconds) + 978307200) if seconds else ''
        messages[guid] = (when, handle or '', 'Outgoing' if from_me else 'Incoming', text or '')
    return messages


@artifact_processor
def get_biomeNotificationDelivery(context):
    files = [str(f) for f in context.get_files_found()]
    sms_db = next((f for f in files if f.endswith('sms.db')), '')
    sms = _sms_lookup(sms_db)

    data_list = []
    source_dirs = set()
    for file_found in files:
        filename = os.path.basename(file_found)
        if (filename.startswith('.') or not os.path.isfile(file_found)
                or 'Notification.Delivery' not in file_found
                or 'tombstone' in context.get_relative_path(file_found)):
            continue
        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            offset = record.data_start_offset
            if record.state == EntryState.Written:
                try:
                    proto, _ = blackboxprotobuf.decode_message(record.data, _TYPEDEF)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Notification Delivery: could not decode record at offset '
                            f'{offset} in {filename}: {ex}')
                    continue
                item_id = _text(proto.get('1'))
                bundle = _text(proto.get('2'))
                delivered = proto.get('3')
                delivered = convert_unix_ts_to_utc(delivered) if isinstance(delivered, float) else None
                match = sms.get(item_id) if bundle == _SMS_BUNDLE else None
                msg_date, handle, direction, text = match if match else ('', '', '', '')
                data_list.append((ts, delivered, record.state.name, bundle, item_id,
                                  msg_date or None, handle, direction, text, filename, offset))
            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None,
                                  None, None, None, None, filename, offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Delivery Date', 'datetime'), 'SEGB State',
                    'Bundle ID', 'Item Identifier', ('Matched Message Date', 'datetime'),
                    'Matched Message Handle', 'Matched Message Direction', 'Matched Message Text',
                    'Filename', 'Offset')
    sources = sorted(source_dirs) + ([sms_db] if sms_db else [])
    return data_headers, data_list, '\n'.join(sources)
