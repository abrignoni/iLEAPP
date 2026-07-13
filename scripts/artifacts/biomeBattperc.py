__artifacts_v2__ = {
    "get_biomeBattperc": {
        "name": "Biome - Battery Percentage",
        "description": "Parses battery percentage entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2025-10-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/_DKEvent.Device.BatteryPercentage/local/*'),
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
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv


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
                
                percent = (protostuff['4']['5'])
                actionguid = (protostuff['5'])
                
                data_list.append((ts, timestart, timeend, timewrite, record.state.name, activity, percent, actionguid,
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name, None, None, None, filename,
                                  record.data_start_offset))


    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), ('Time End', 'datetime'),
                    ('Time Write', 'datetime'), 'SEGB State', 'Activity', 'Battery Percentage', 'Action GUID',
                    'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'

