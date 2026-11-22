__artifacts_v2__ = {
    "get_biomeNotificationDelivery": {
        "name": "Biome - Notification Delivery",
        "description": "Notifications delivered to the device, from the Biome Notification.Delivery stream, "
                       "with the delivering app and the app's own identifier for the notified item. Messages "
                       "notifications are matched to sms.db on message.guid.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are not sourced from Apple code; they are inferred from one image, whose stream held both written and deleted records. Item Identifier is field 1 and "
                  "Bundle ID field 2. Delivery Date is field 3, a double read as Unix seconds. On the tested image it was within seconds of the SEGB timestamp on most written rows and as much as a day earlier on others. On the tested image field 1 of the com.apple.MobileSMS rows held a message GUID, and every such row matched sms.db message.guid. Matches use the SMS database beside the same Biome library. The handle, "
                  "direction, date and available text (including attributedBody) refer to the matched message. "
                  "A matched message's date can be days before the delivery date, so the delivery date is "
                  "not the time the message was sent. For com.apple.mobilemail rows field 1 held small "
                  "integers; that they are Envelope Index row ids is not verified and they are not matched. "
                  "Deleted records keep only their SEGB timestamp. On the tested image the stream held one "
                  "SEGB file, so Source File held one value on every row."),
        "paths": ('*/Biome/streams/restricted/Notification.Delivery/local/*',
                  '*/mobile/Library/SMS/sms.db*'),
        "output_types": "standard",
        "artifact_icon": "bell",
    }
}

import sqlite3
import struct
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import PurePosixPath

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.biome_stream_records import local_records
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.sms_deep import message_columns, message_text, query_chunks


_TYPEDEF = {
    '1': {'type': 'bytes', 'name': ''},
    '2': {'type': 'bytes', 'name': ''},
    '3': {'type': 'double', 'name': ''},
}
_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_COCOA_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)
_SMS_BUNDLE = 'com.apple.MobileSMS'


def _date(epoch, seconds):
    if seconds is None:
        return None
    try:
        return epoch + timedelta(seconds=seconds)
    except (TypeError, ValueError, OverflowError):
        return None


def _sms_lookup(path, guids):
    """Look up only notification GUIDs in this device's database."""
    matches = {}
    try:
        db = open_sqlite_db_readonly(path)
        if db is None:
            return matches
        with closing(db):
            body = 'm.attributedBody' if 'attributedBody' in message_columns(db) else 'NULL'
            sql = (f'SELECT m.guid, m.date, h.id, m.is_from_me, m.text, {body} FROM message m '
                   'LEFT JOIN handle h ON m.handle_id = h.ROWID WHERE m.guid IN ({marks})')
            for guid, date, handle, from_me, text, attributed in query_chunks(db, sql, guids):
                seconds = date
                if isinstance(date, (int, float)) and abs(date) > 1e11:
                    seconds = date / 1e9
                when = _date(_COCOA_EPOCH, seconds) if seconds else None
                direction = {0: 'Incoming', 1: 'Outgoing'}.get(from_me, '')
                matches[guid] = (when, handle, direction, message_text(text, attributed))
    except sqlite3.Error as error:
        logfunc(f'Biome Notification Delivery: could not read SMS database: {error}')
    return matches


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'backslashreplace')
    return '' if value is None else str(value)


@artifact_processor
def get_biomeNotificationDelivery(context):
    databases = defaultdict(set)
    for found in map(str, context.get_files_found()):
        path = PurePosixPath(context.get_relative_path(found).replace('\\', '/'))
        if path.parts[-2:] == ('SMS', 'sms.db'):
            databases[path].add(found)

    rows = []
    pending = defaultdict(lambda: defaultdict(list))
    sources = set()
    for source, record in local_records(context, 'Notification.Delivery'):
        sources.add(str(source))
        proto = {}
        if record.state == EntryState.Written:
            try:
                proto, _ = blackboxprotobuf.decode_message(record.data, _TYPEDEF)
            except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as error:
                logfunc(f'Biome Notification Delivery: could not decode offset {record.data_start_offset} '
                        f'in {source}: {error}')
        bundle = _text(proto.get('2'))
        item = _text(proto.get('1'))
        if bundle == _SMS_BUNDLE and item:
            # The stream lives at <Library>/Biome/streams/restricted/<stream>/local/<file>.
            database = source.parents[5] / 'SMS' / 'sms.db'
            pending[database][item].append(len(rows))
        rows.append([record.timestamp1.replace(tzinfo=timezone.utc), _date(_UNIX_EPOCH, proto.get('3')),
                     None, record.state.name, bundle, item, None, None, None, str(source), record.data_start_offset])

    for database, guids in pending.items():
        candidates = databases.get(database, set())
        if len(candidates) != 1:
            continue
        sources.add(str(database))
        for guid, (when, handle, direction, text) in _sms_lookup(next(iter(candidates)), guids).items():
            for index in guids[guid]:
                rows[index][2] = when
                rows[index][6:9] = (handle, direction, text)
    data_headers = (('SEGB Timestamp', 'datetime'), ('Delivery Date', 'datetime'), ('Matched Message Date', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Item Identifier', 'Matched Message Handle', 'Matched Message Direction',
                    'Matched Message Text', 'Source File', 'Offset')
    return data_headers, rows, '\n'.join(sorted(sources))
