__artifacts_v2__ = {
    "get_biomeLocationactivity": {
        "name": "Biome Location Activity",
        "description": "Parses location activity entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Location Activity",
        "notes": "",
        "paths": ('*/biome/streams/restricted/_DKEvent.App.LocationActivity/local/*'),
        "output_types": "standard"
    }
}


import os
import nska_deserialize as nd
import blackboxprotobuf
from ccl_segb import read_segb_file
from ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_utc_human_to_timezone


@artifact_processor
def get_biomeLocationactivity(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '6': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'str', 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '6': {'type': 'int', 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '5': {'type': 'fixed64', 'name': ''}, '4': {'type': 'int', 'name': ''}, '6': {'type': 'bytes', 'name': ''}, '7': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                pass
        else:
            continue

        for record in read_segb_file(file_found):
            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
                
                activity = (protostuff['1']['1'])
                timestart = (webkit_timestampsconv(protostuff['2']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)
                
                timeend = (webkit_timestampsconv(protostuff['3']))
                timeend = convert_utc_human_to_timezone(timeend, timezone_offset)
                
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
                    deserialized_plist = nd.deserialize_plist_from_string(data4)
                    data4 = (deserialized_plist['NS.relative'])
                    
                data5 = (protostuff['7'][13]['2'].get('6',''))
                if isinstance(data5, bytes):
                    deserialized_plist = nd.deserialize_plist_from_string(data5)
                    data5 = (deserialized_plist)
                    
                data6 = (protostuff['7'][16]['2'].get('6',''))
                if isinstance(data6, bytes):
                    deserialized_plist = nd.deserialize_plist_from_string(data6)
                    data6 = (deserialized_plist['NS.relative'])
                    
                timewrite = (webkit_timestampsconv(protostuff['8']))
                timewrite = convert_utc_human_to_timezone(timewrite, timezone_offset)
                
                data_list.append((timestart, timeend, timewrite, activity, bundle, bundle2, data0, data1, data2, data3,
                                  data4, data5, data6, actionguid, filename, record.data_start_offset))

    data_headers = (('Time Start', 'datetime'), ('Time End', 'datetime'), ('Time Write', 'datetime'), 'Activity',
                    'Bundle ID','Bundle ID 2', 'Data 0', 'Data 1', 'Data 2', 'Data 3', 'Data 4', 'Data 5', 'Data 6',
                    'Action GUID', 'Filename', 'Offset')

    return data_headers, data_list, file_found
