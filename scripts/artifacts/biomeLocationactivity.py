__artifacts_v2__ = {
    "get_biomeLocationactivity": {
        "name": "Biome - Location Activity",
        "description": "Parses location activity entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/biome/streams/restricted/_DKEvent.App.LocationActivity/local/*'),
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
            "iphone12_ios18": "iOS 18.7 | 92 rows",
            "abe_ios16": "iOS 16.5 | 73 rows",
            "felix23_ios16": "iOS 16.5 | 44 rows",
            "magnet_ios16": "iOS 16.1.1 | 8 rows",
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
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, get_plist_content, logfunc


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
                '1': {'type': 'message', 'message_typedef': {}, 'name': ''},
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

                    activity = (protostuff['1']['1'])
                    timestart = (webkit_timestampsconv(protostuff['2']))
                    timeend = (webkit_timestampsconv(protostuff['3']))

                    bundle = (protostuff['4']['3'])
                    actionguid = (protostuff['5'])
                    data0 = (protostuff['6']['1'])
                    bundle2 = (protostuff['6']['2'])

                    if (protostuff['7'][2]['2'].get('3','')) != '':
                        data1 = (protostuff['7'][2]['2']['3'].decode())
                    else:
                        data1 = ''
                    if (protostuff['7'][3]['2'].get('3','')) != '':
                        data2 = (protostuff['7'][3]['2'].get('3',''))
                    else:
                        data2 = ''
                    if (protostuff['7'][4]['2'].get('3','')) != '':
                        data3 = (protostuff['7'][4]['2']['3'].decode())
                    else:
                        data3 = ''

                    data4 = (protostuff['7'][10]['2'].get('6',''))
                    if isinstance(data4, bytes):
                        #deserialized_plist = nd.deserialize_plist_from_string(data4)
                        deserialized_plist = get_plist_content(data4)
                        if not deserialized_plist or not isinstance(deserialized_plist, dict):
                            data4 = None
                        else:
                            data4 = (deserialized_plist.get('NS.relative'))

                    data5 = (protostuff['7'][13]['2'].get('6',''))
                    if isinstance(data5, bytes):
                        #deserialized_plist = nd.deserialize_plist_from_string(data5)
                        deserialized_plist = get_plist_content(data5)
                        if not deserialized_plist or not isinstance(deserialized_plist, dict):
                            data5 = None
                        else:
                            data5 = (deserialized_plist)

                    data6 = (protostuff['7'][16]['2'].get('6',''))
                    if isinstance(data6, bytes):
                        #deserialized_plist = nd.deserialize_plist_from_string(data6)
                        deserialized_plist = get_plist_content(data6)
                        if not deserialized_plist or not isinstance(deserialized_plist, dict):
                            data6 = None
                        else:
                            data6 = (deserialized_plist.get('NS.relative'))

                    timewrite = (webkit_timestampsconv(protostuff['8']))
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeLocationactivity record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

                data_list.append((ts, timestart, timeend, timewrite, record.state.name, activity, bundle, bundle2,
                                  data0, data1, data2, data3, data4, data5, data6, actionguid, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name, None, None, None, None, None, None, None,
                                  None, None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), ('Time End', 'datetime'),
                    ('Time Write', 'datetime'), 'SEGB State', 'Activity', 'Bundle ID','Bundle ID 2', 'Data 0', 'Data 1',
                    'Data 2', 'Data 3', 'Data 4', 'Data 5', 'Data 6', 'Action GUID', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
