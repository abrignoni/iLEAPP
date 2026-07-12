__artifacts_v2__ = {
    "get_biomeCarplayisconnected": {
        "name": "Biome - Carplay",
        "description": "Parses carplay is connected entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2025-10-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
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
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv


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
                protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                activity = (protostuff['1']['1'])
                
                timestart = (webkit_timestampsconv(protostuff['2']))
                timeend = (webkit_timestampsconv(protostuff['3']))
                timewrite = (webkit_timestampsconv(protostuff['8']))
                
                actionguid = (protostuff['5'])
                status = (protostuff['4']['4'])
                
                data_list.append((ts, timestart, timeend, timewrite, record.state.name, activity, status, actionguid,
                                  filename,  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), ('Time End', 'datetime'),
                    ('Time Write', 'datetime'), 'Activity', 'Status', 'Action GUID', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
