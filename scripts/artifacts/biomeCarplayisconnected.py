__artifacts_v2__ = {
    "get_biomeCarplayisconnected": {
        "name": "Biome Carplay Is Connected",
        "description": "Parses carplay is connected entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Carplay",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/_DKEvent.Carplay.IsConnected/local/*'),
        "output_types": "standard"
    }
}


import os
import blackboxprotobuf
from ccl_segb import read_segb_file
from ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_utc_human_to_timezone


@artifact_processor
def get_biomeCarplayisconnected(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '4': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}
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
                
                timewrite = (webkit_timestampsconv(protostuff['8']))
                timewrite = convert_utc_human_to_timezone(timewrite, timezone_offset)
                
                actionguid = (protostuff['5'])
                status = (protostuff['4']['4'])
                
                data_list.append((timestart, timeend, timewrite, activity, status, actionguid, filename,
                                  record.data_start_offset))

    data_headers = (('Time Start', 'datetime'), ('Time End', 'datetime'), ('Time Write', 'datetime'), 'Activity',
                    'Status','Action GUID', 'Filename', 'Offset')

    return data_headers, data_list, file_found
