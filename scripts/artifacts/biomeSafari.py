__artifacts_v2__ = {
    "get_biomeSafari": {
        "name": "Biome - Safari",
        "description": "Parses safari entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on macOS "
                  "27.2.1 (26B131); no iOS copy of the class was read. Start Date is field 2 (startDate) "
                  "and was reported before as Timestamp. Stream Name is field 1.1 and was reported before "
                  "as Activity. String Value is field 4.3 (the value's stringValue) and was reported before "
                  "as URL; on the 21 iOS images tested (17 held written records of this stream), which include the sample_data keys, 236 of the 236 written values began with http or https. "
                  "Source ID, Source Bundle ID and Source Group ID are fields 6.1, 6.2 and 6.4 (sourceID, "
                  "bundleID and groupID) and were reported before as Detail, Detail 2 and Detail 3; fields "
                  "6.3 (itemID) and 6.6 (userID) are not reported. Identifier is field 5 and was reported "
                  "before as GUID. Title is the metadata entry with index 28000, which CoreDuet's own "
                  "conversion of synthetic records names title. Before, Title took the value of the record's "
                  "only metadata entry whatever its index; on the 21 iOS images tested (17 held written records of this stream), which include the sample_data keys, each of the 236 written records "
                  "held one entry, with index 28000, so the Title values did not change. On iphone12_ios18 (18 written rows) Stream Name, Source ID, Source Bundle ID, Source Group ID and Time Zone Offset (seconds) each held one value. Fields 3 (endDate) and 8 (creationDate) are not reported. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (17 held written records of this stream), which include the sample_data keys, it was set on each of the 236 written rows, with 7 distinct values, each a whole number of quarter hours within 14 hours of GMT."),
        "paths": ('*/[Bb]iome/streams/restricted/_DKEvent.Safari.History/local/*',),
        "output_types": "standard",
        "artifact_icon": "compass",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 8 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
            "iphone12_ios18": "iOS 18.7 | 18 rows",
            "iphone14plus_ios18": "iOS 18.0 | 17 rows",
            "otto_ios17": "iOS 17.5.1 | 108 rows",
            "abe_ios16": "iOS 16.5 | 100 rows",
            "felix23_ios16": "iOS 16.5 | 7 rows",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
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

# Metadata index for the page title, read from CoreDuet.framework on macOS 27.2.1 (26B131) by
# converting synthetic _DKPREvent records with _DKEvent fromPBCodable:
# 28000 _DKSafariHistoryMetadataKey-title.
_TITLE_INDEX = 28000


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _metadata_by_index(entries):
    """Metadata entries keyed by their integer index (field 7.N.3), with the string value (7.N.2.3)."""
    if isinstance(entries, dict):
        entries = [entries]
    found = {}
    for entry in entries or []:
        if not isinstance(entry, dict) or not isinstance(entry.get('3'), int):
            continue
        value = entry.get('2')
        found[entry['3']] = _text(value.get('3')) if isinstance(value, dict) else ''
    return found


@artifact_processor
def get_biomeSafari(context):

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
                '3': {'type': 'str', 'name': ''},
                '4': {'type': 'str', 'name': ''},
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
                        '3': {'type': 'bytes', 'name': ''}
                    },
                    'name': ''
                },
                '3': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
        '8': {'type': 'fixed64', 'name': ''},
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
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Safari: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                activity = (protostuff['1']['1'])
                timestart = (webkit_timestampsconv(protostuff['2']))
                url = (protostuff['4']['3'])
                guid = (protostuff['5'])
                detail1 = (protostuff['6']['1'])
                detail2 = (protostuff['6']['2'])
                detail3 = (protostuff['6']['4'])
                title = _metadata_by_index(protostuff.get('7')).get(_TITLE_INDEX, '')
                tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''

                data_list.append((ts, timestart, tz_offset, record.state.name, activity, title, url, detail1, detail2, detail3, guid, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, record.state.name, None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), 'Time Zone Offset (seconds)', 'SEGB State',
                    'Stream Name', 'Title',
                    'String Value', 'Source ID', 'Source Bundle ID', 'Source Group ID', 'Identifier', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
