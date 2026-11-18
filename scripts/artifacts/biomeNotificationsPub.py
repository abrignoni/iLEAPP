__artifacts_v2__ = {
    "get_biomeNotificationsPub": {
        "name": "Biome - Notifications",
        "description": "Notification events from the public Notification biome stream, seen on the tested "
                       "iOS 15 and iOS 16 images: the usage "
                       "type (received, cleared, expired and so on), the app bundle id, the title "
                       "and subtitle.",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names and Usage Type names are those of the BMNotificationUsage class, read "
                 "from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class "
                 "was read. Usage Type is field 3 (usageType), for example 1 Receive, 2 "
                 "DefaultAction, 4 Clear, 7 Hidden, 11 Expired, 17 ReceivedAndDeliveredActively and "
                 "18 ReceivedAndDeliveredPassively; the integer is in Usage Type (raw). On the "
                 "tested iOS 15 and iOS 16 images every reported record carried a usage type the class names; "
                 "records in tombstone files are not read. Bundle ID is field 4 (bundleID). The "
                 "record also stores field 14 (sectionID); it held the same text as field 4 on every "
                 "reported record on the tested images, so it is not a separate column. Title is "
                 "field 8, Subtitle field 9, Thread ID field 12, Contact IDs field 15, Is Group "
                 "Message field 16, Body Length field 18 (bodyLength), Notification ID field 5 and "
                 "Unique ID field 1. Body Length held no value on any row of the tested iOS 15 and iOS 16 images. The class defines a body field (10); no reported record "
                 "on the tested images stored it. Timestamp is field 2 (absoluteTimestamp), a Cocoa "
                 "epoch (seconds since 2001-01-01 UTC); it held 0 on 44 of the 5,569 written records "
                 "on the tested images, and those rows leave Timestamp blank where it showed "
                 "2001-01-01 before. Timestamp and SEGB Timestamp differ by more than a day on 1,579 "
                 "of the 5,525 records with a non-zero Timestamp on the tested images; which of the "
                 "two marks the usage event is not established. SEGB Timestamp is the SEGB record "
                 "timestamp. Deleted SEGB records are reported as rows with no fields. Before, field 14 was reported as Bundle ID and fields 8 and 12 as "
                 "Field 1 and Field 3."),
        "paths": ('*/Biome/streams/public/Notification/local/*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 8397 rows",
            "felix23_ios16": "iOS 16.5 | 852 rows",
            "jess_ios15": "iOS 15.0.2 | 325 rows",
            "magnet_ios16": "iOS 16.1.1 | 269 rows",
        }
    }
}


import os
import struct
from datetime import timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# Field names and usageType names are those of the BMNotificationUsage class, read from
# BiomeLibrary.framework on macOS 27.2.1 (26B131).
USAGE_TYPES = {0: 'Unknown', 1: 'Receive', 2: 'DefaultAction', 3: 'SuppAction', 4: 'Clear', 5:
               'ClearAll', 6: 'IndirectClear', 7: 'Hidden', 8: 'Orb', 9: 'Dismiss', 10:
               'AppLaunch', 11: 'Expired', 12: 'TapCoalesce', 13: 'Deduped', 14:
               'DevActivated', 15: 'DevUnlocked', 16: 'Pulldown', 17:
               'ReceivedAndDeliveredActively', 18: 'ReceivedAndDeliveredPassively', 19:
               'Modified', 20: 'TapExpand', 21: 'ShortLookDefaultAction', 22:
               'ShortLookDismiss', 23: 'ShortLookClear', 24: 'LongLookDefaultAction', 25:
               'LongLookCustomAction', 26: 'LongLookDismiss', 27: 'LongLookRepark'}

TYPESS = {
    '1': {'type': 'str', 'name': ''},     # uniqueID
    '2': {'type': 'double', 'name': ''},  # absoluteTimestamp (Cocoa epoch)
    '3': {'type': 'int', 'name': ''},     # usageType
    '4': {'type': 'str', 'name': ''},     # bundleID
    '5': {'type': 'str', 'name': ''},     # notificationID
    '8': {'type': 'str', 'name': ''},     # title
    '9': {'type': 'str', 'name': ''},     # subtitle
    '11': {'type': 'int', 'name': ''},    # badge
    '12': {'type': 'str', 'name': ''},    # threadID
    '14': {'type': 'str', 'name': ''},    # sectionID
    '15': {'type': 'str', 'name': ''},    # contactIDs
    '16': {'type': 'int', 'name': ''},    # isGroupMessage
    '18': {'type': 'int', 'name': ''},    # bodyLength
}

DATA_HEADERS = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State',
                'Usage Type', 'Usage Type (raw)', 'Bundle ID', 'Title', 'Subtitle',
                'Thread ID', 'Contact IDs', 'Is Group Message', 'Body Length',
                ('Notification ID', 'hash'), ('Unique ID', 'hash'), 'Filename', 'Offset')


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _row(ts, record, protostuff, filename):
    raw_ts = protostuff.get('2')
    timestart = webkit_timestampsconv(raw_ts) if isinstance(raw_ts, (int, float)) and raw_ts else None
    usage = protostuff.get('3')
    contacts = protostuff.get('15')
    if isinstance(contacts, list):
        contacts = ', '.join(_text(c) for c in contacts)
    group = protostuff.get('16')
    return (ts, timestart, record.state.name,
            USAGE_TYPES.get(usage, '') if isinstance(usage, int) else '', _text(usage),
            _text(protostuff.get('4')), _text(protostuff.get('8')), _text(protostuff.get('9')),
            _text(protostuff.get('12')), _text(contacts),
            {1: 'True', 0: 'False'}.get(group, '') if isinstance(group, int) else '',
            _text(protostuff.get('18')), _text(protostuff.get('5')), _text(protostuff.get('1')),
            filename, record.data_start_offset)



@artifact_processor
def get_biomeNotificationsPub(context):

    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Notifications: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                
                data_list.append(_row(ts, record, protostuff, filename))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name) + (None,) * 11 +
                                 (filename, record.data_start_offset))

    data_headers = DATA_HEADERS

    return data_headers, data_list, '\n'.join(sorted(source_dirs))

