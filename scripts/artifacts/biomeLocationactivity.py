__artifacts_v2__ = {
    "get_biomeLocationactivity": {
        "name": "Biome - Location Activity",
        "description": "Parses records from the _DKEvent.App.LocationActivity biome stream: start "
                       "and end times, the bundle id, the source id and source bundle id and the metadata entries "
                       "stored with the record.",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class on macOS 27.2.1 (26B131); no "
                 "iOS copy of the class was read. Source ID and Source Bundle ID are fields 6.1 "
                 "and 6.2 (sourceID and bundleID); on the 4 corpus images with written records, Source "
                 "Bundle ID equalled Bundle ID on all 193; fields 6.3 (itemID) and 6.6 (userID) are not "
                 "reported. Metadata lists every metadata entry as "
                 "key=value. The key is the CoreDuet name for the entry's integer index (the "
                 "_DKApplicationActivityMetadataKey names 18000 to 18013 and the calendar keys "
                 "47000 to 47002), or the index itself for any index outside that table; an entry's "
                 "own key string would be used first, but no entry on these images had one. 1,735 of "
                 "the 3,666 entries on the 4 corpus images kept a numeric index (41000 to 41012, "
                 "which this macOS build does not name). A blob value that is a URL plist shows its "
                 "URL; any other blob shows its size in bytes (102 entries). Before, this artifact "
                 "read metadata list positions 2, 3, 4, 10, 13 and 16 (counting from 0) as Data 1 to Data 6, "
                 "although the key at each position varied between records, and skipped any record "
                 "with fewer than 17 entries: 69 written records on iphone12_ios18 gave no row. "
                 "Data 0 and Bundle ID 2 are now Source ID and Source Bundle ID."),
        "paths": ('*/[Bb]iome/streams/restricted/_DKEvent.App.LocationActivity/local/*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 435 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 19 rows",
            "iphone11_ios17": "iOS 17.3 | 93 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 32 rows",
            "iphone12_ios18": "iOS 18.7 | 161 rows",
            "abe_ios16": "iOS 16.5 | 79 rows",
            "felix23_ios16": "iOS 16.5 | 44 rows",
            "magnet_ios16": "iOS 16.1.1 | 8 rows",
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
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, get_plist_content, logfunc


# Metadata index to key name, read from CoreDuet.framework on macOS 27.2.1 (26B131) by converting
# synthetic _DKPREvent records with _DKEvent fromPBCodable: (_DKApplicationActivityMetadataKey).
# Indexes this macOS build does not name stay numeric.
METADATA_KEYS = {
    18000: 'itemIdentifier', 18001: 'userActivityUUID', 18002: 'title', 18003: 'activityType',
    18004: 'expirationDate', 18005: 'itemRelatedUniqueIdentifier', 18006: 'itemRelatedContentURL',
    18007: 'isPubliclyIndexable', 18008: 'isEligibleForPrediction',
    18009: 'userActivityRequiredString', 18010: 'contentDescription',
    18011: 'suggestedInvocationPhrase', 18012: 'beginningOfActivity', 18013: 'shortcutAvailability',
    47000: 'com.apple.calendarUIKit.userActivity.date',
    47001: 'com.apple.calendarUIKit.userActivity.externalID',
    47002: 'com.apple.calendarUIKit.userActivity.endDate',
}
_PREFIX = '_DKApplicationActivityMetadataKey-'


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _value(payload):
    """A _DKPRValue: 3 string, 4 integer, 5 double, 6 blob, 7 date (Cocoa seconds)."""
    if not isinstance(payload, dict):
        return ''
    if '3' in payload:
        return _text(payload['3'])
    if '4' in payload:
        return _text(payload['4'])
    for field in ('5', '7'):
        if isinstance(payload.get(field), int):
            seconds = struct.unpack('<d', struct.pack('<Q', payload[field]))[0]
            if field == '7':
                try:
                    converted = webkit_timestampsconv(seconds)
                    return converted.isoformat() if converted != '' else str(seconds)
                except (OverflowError, OSError, ValueError):
                    return str(seconds)
            return str(seconds)
    blob = payload.get('6')
    if isinstance(blob, bytes):
        plist = get_plist_content(blob)
        if isinstance(plist, dict) and plist.get('NS.relative'):
            return _text(plist.get('NS.relative'))
        return f'<{len(blob)} bytes>'
    return ''


def _metadata(entries):
    """Every metadata entry as key=value, keyed by its key string or its index."""
    if isinstance(entries, dict):
        entries = [entries]
    parts = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        key = _text(entry.get('1')).replace(_PREFIX, '')
        if not key:
            index = entry.get('3')
            key = METADATA_KEYS.get(index, _text(index))
        parts.append(f'{key}={_value(entry.get("2"))}')
    return '; '.join(parts)


@artifact_processor
def get_biomeLocationactivity(context):

    typess = {
        '1': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'str', 'name': ''},
                '2': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {'type': 'int', 'name': ''},
                        '2': {'type': 'int', 'name': ''}
                    },
                    'name': ''
                }
            },
            'name': ''
        },
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'double', 'name': ''},
        '4': {
            'type': 'message',
            'message_typedef': {
                '1': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {'type': 'int', 'name': ''},
                        '2': {'type': 'int', 'name': ''}
                    },
                    'name': ''
                },
                '3': {'type': 'str', 'name': ''}
            },
            'name': ''
        },
        '5': {'type': 'str', 'name': ''},
        '6': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'str', 'name': ''},
                '2': {'type': 'str', 'name': ''},
                '3': {'type': 'bytes', 'name': ''},
                '6': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
        '7': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'bytes', 'name': ''},
                '2': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {
                            'type': 'message',
                            'message_typedef': {
                                '1': {'type': 'int', 'name': ''},
                                '2': {'type': 'int', 'name': ''}
                            },
                            'name': ''
                        },
                        '3': {'type': 'bytes', 'name': ''},
                        '5': {'type': 'fixed64', 'name': ''},
                        '4': {'type': 'int', 'name': ''},
                        '6': {'type': 'bytes', 'name': ''},
                        '7': {'type': 'fixed64', 'name': ''}
                    },
                    'name': ''
                },
                '3': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
        '8': {'type': 'double', 'name': ''},
        '10': {'type': 'int', 'name': ''}
    }

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
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                    activity = (protostuff['1']['1'])
                    timestart = (webkit_timestampsconv(protostuff['2']))
                    timeend = (webkit_timestampsconv(protostuff['3']))

                    bundle = (protostuff['4']['3'])
                    actionguid = (protostuff['5'])
                    source = protostuff.get('6') if isinstance(protostuff.get('6'), dict) else {}
                    source_id = _text(source.get('1'))
                    source_bundle = _text(source.get('2'))
                    metadata = _metadata(protostuff.get('7'))

                    timewrite = (webkit_timestampsconv(protostuff['8']))
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeLocationactivity record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

                data_list.append((ts, timestart, timeend, timewrite, record.state.name, activity, bundle,
                                  source_id, source_bundle, metadata, actionguid, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name) + (None,) * 6 +
                                 (filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), ('Time End', 'datetime'),
                    ('Time Write', 'datetime'), 'SEGB State', 'Activity', 'Bundle ID', 'Source ID', 'Source Bundle ID', 'Metadata',
                    'Action GUID', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
