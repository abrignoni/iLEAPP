__artifacts_v2__ = {
    "get_biomeBattperc": {
        "name": "Biome - Battery Percentage",
        "description": "Parses battery percentage entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on macOS "
                  "27.2.1 (26B131); no iOS copy of the class was read. Start Date, End Date and Creation "
                  "Date are fields 2, 3 and 8 (startDate, endDate and creationDate) and were reported "
                  "before as Time Start, Time End and Time Write. Stream Name is field 1.1 and was reported "
                  "before as Activity. Double Value is field 4.5 (the value's doubleValue) and was reported "
                  "before as Battery Percentage; on the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, 14,187 of the 14,191 written values "
                  "were above 1 and at most 100, and 4 were at most 1. Identifier is field 5 and was reported before as Action GUID. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, it was set on each of the 14,191 written rows, with 10 distinct values, each a whole number of quarter hours within 14 hours of GMT. Fully Charged is the integer value of the metadata entry with index 37000, which CoreDuet's own conversion of synthetic records names _DKDeviceBatteryPercentageMetadataKey-fullyCharged (macOS 27.2.1 (26B131); no iOS copy was read). It is shown as stored and was not reported before. On the 21 iOS images tested (20 held written records of this stream) it was set on 153 of 14,191 written rows, on 19 images, with the value 1 on each. Double Value on those rows was 100 on 102 and from 89 to 99 on 51, and 167 of the 269 written rows with a Double Value of 100 did not carry the entry, so the two columns do not say the same thing."),
        "paths": ('*/[Bb]iome/streams/restricted/_DKEvent.Device.BatteryPercentage/local/*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 4321 rows",
            "felix_ios17": "iOS 17.6.1 | 1676 rows",
            "fsfull002_ios17": "iOS 17.1 | 1857 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4021 rows",
            "iphone11_ios17": "iOS 17.3 | 6159 rows",
            "iphone12_ios18": "iOS 18.7 | 1146 rows",
            "iphone14plus_ios18": "iOS 18.0 | 450 rows",
            "otto_ios17": "iOS 17.5.1 | 4307 rows",
            "abe_ios16": "iOS 16.5 | 8138 rows",
            "felix23_ios16": "iOS 16.5 | 2945 rows",
            "magnet_ios16": "iOS 16.1.1 | 960 rows",
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

# _DKEvent metadata index that CoreDuet names _DKDeviceBatteryPercentageMetadataKey-fullyCharged
# (read from _DKEvent fromPBCodable: on synthetic records, macOS 27.2.1, 26B131).
_FULLY_CHARGED_INDEX = 37000


def _metadata_int(entries, index):
    """Integer value (field 7.N.2.4) of the metadata entry whose index (7.N.3) is index, or ''."""
    if isinstance(entries, dict):
        entries = [entries]
    for entry in entries or []:
        if isinstance(entry, dict) and entry.get('3') == index:
            value = entry.get('2')
            if isinstance(value, dict) and type(value.get('4')) is int:
                return value['4']
    return ''


@artifact_processor
def get_biomeBattperc(context):

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
                '5': {'type': 'double', 'name': ''}
            },
            'name': ''
        },
        '5': {'type': 'str', 'name': ''},
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
                        '4': {'type': 'int', 'name': ''}
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
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Battery Percentage: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                
                activity = (protostuff['1']['1'])
                # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                timestart = (webkit_timestampsconv(protostuff['2']) or None)
                timeend = (webkit_timestampsconv(protostuff['3']) or None)
                timewrite = (webkit_timestampsconv(protostuff['8']) or None)
                
                percent = (protostuff['4']['5'])
                fully_charged = _metadata_int(protostuff.get('7'), _FULLY_CHARGED_INDEX)
                actionguid = (protostuff['5'])
                
                tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''
                data_list.append((ts, timestart, timeend, timewrite, tz_offset, record.state.name, activity, percent, fully_charged, actionguid,
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, None, record.state.name, None, None, None, None, filename,
                                  record.data_start_offset))


    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'),
                    ('Creation Date', 'datetime'), 'Time Zone Offset (seconds)', 'SEGB State', 'Stream Name', 'Double Value', 'Fully Charged', 'Identifier',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))

