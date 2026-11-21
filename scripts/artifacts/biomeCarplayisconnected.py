__artifacts_v2__ = {
    "get_biomeCarplayisconnected": {
        "name": "Biome - Carplay",
        "description": "Parses carplay is connected entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on macOS "
                  "27.2.1 (26B131); no iOS copy of the class was read. Start Date, End Date and Creation "
                  "Date are fields 2, 3 and 8 (startDate, endDate and creationDate) and were reported "
                  "before as Time Start, Time End and Time Write. Stream Name is field 1.1 and was reported "
                  "before as Activity. Is Connected (as stored) is field 4.4 (the value's integerValue) of the _DKEvent.Carplay.IsConnected stream, and the header repeats that stream name. It does not say that 1 means connected. It was reported as Status in v2026.4.6; it is shown as stored and its meaning is not established. On the 21 iOS images tested (12 held written records of this stream), which include the sample_data keys, it held 0 on 89 and 1 on 68 of the 157 written rows. Identifier is field 5 and was reported before as Action GUID. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (12 held written records of this stream), which include the sample_data keys, it was set on each of the 157 written rows, with 6 distinct values, each a whole number of quarter hours within 14 hours of GMT."),
        "paths": ('*/Biome/streams/restricted/_DKEvent.Carplay.IsConnected/local/*'),
        "output_types": "standard",
        "artifact_icon": "car",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 116 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 36 rows",
            "iphone11_ios17": "iOS 17.3 | 34 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 8 rows",
            "abe_ios16": "iOS 16.5 | 116 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
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


@artifact_processor
def get_biomeCarplayisconnected(context):

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
                '4': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
        '5': {'type': 'str', 'name': ''},
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
                    logfunc(f'Biome Carplay: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                activity = (protostuff['1']['1'])
                
                # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                timestart = (webkit_timestampsconv(protostuff['2']) or None)
                timeend = (webkit_timestampsconv(protostuff['3']) or None)
                timewrite = (webkit_timestampsconv(protostuff['8']) or None)
                
                actionguid = (protostuff['5'])
                status = (protostuff['4']['4'])
                
                tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''
                data_list.append((ts, timestart, timeend, timewrite, tz_offset, record.state.name, activity, status, actionguid,
                                  filename,  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, None, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'),
                    ('Creation Date', 'datetime'), 'Time Zone Offset (seconds)', 'SEGB State', 'Stream Name', 'Is Connected (as stored)', 'Identifier', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
