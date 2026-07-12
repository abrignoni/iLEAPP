__artifacts_v2__ = {
    "get_biomeDKKeybag": {
        "name": "Biome - Keybag",
        "description": "Parses DKEvent Keybag IsLocked entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2025-04-29",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/_DKEvent.Keybag.IsLocked/local/*'),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | 58 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 138 rows",
            "iphone11_ios17": "iOS 17.3 | 82 rows",
            "iphone12_ios18": "iOS 18.7 | 115 rows",
            "iphone14plus_ios18": "iOS 18.0 | 28 rows",
            "otto_ios17": "iOS 17.5.1 | 62 rows",
            "dexter_ios18": "iOS 18.3.2 | 382 rows",
            "abe_ios16": "iOS 16.5 | 942 rows",
            "felix23_ios16": "iOS 16.5 | 8 rows",
            "magnet_ios16": "iOS 16.1.1 | 66 rows",
        }
    }
}


import os
import struct
from datetime import timezone
import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, logfunc


@artifact_processor
def get_biomeDKKeybag(context):

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
        '5': {'type': 'bytes', 'name': ''},
        '8': {'type': 'double', 'name': ''},
        '10': {'type': 'int', 'name': ''}
    }

    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                    time2 = (webkit_timestampsconv(protostuff['2']))
                    time3 = (webkit_timestampsconv(protostuff['3']))

                    data_list.append((ts, time2, time3, '1 - Locked ' if protostuff['4']['4'] == 1 else '0 - Unlocked', filename))
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeDKKeybag record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Time', 'datetime'), ('End Time', 'datetime'), 'isLocked', 'Filename')

    return data_headers, data_list, 'see Filename for more info'
