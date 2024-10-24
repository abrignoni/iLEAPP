__artifacts_v2__ = {
    "get_biomeAppinstall": {
        "name": "Biome App Install",
        "description": "Parses airplane mode entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome App Install",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/_DKEvent.App.Install/local/*', '*/Biome/streams/restricted/App.Install/local/*'),
        "output_types": "standard"
    }
}

import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_utc_human_to_timezone

@artifact_processor
def get_biomeAppinstall(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '4': {'type': 'int', 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}

    data_list = []
    report_file = 'Unknown'
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                report_file = os.path.dirname(file_found)
        else:
            continue
    
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:

                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
            
                activity = (protostuff['1']['1'])
                timestart = (webkit_timestampsconv(protostuff['2']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)
                
                
                timeend = (webkit_timestampsconv(protostuff['3']))
                timeend = convert_utc_human_to_timezone(timeend, timezone_offset)
                
                bundleid = (protostuff['4']['3'])
                actionguid = (protostuff['5'])
                appinfo1 = appinfo2 = ''
                if protostuff.get('7', '') != '':
                    if isinstance(protostuff['7'], list):
                        if len(protostuff['7']) < 3:
                            appinfo1 = (protostuff['7'][0]['2'].get('3', ''))
                        else:
                            appinfo1 = (protostuff['7'][0]['2'].get('3', ''))
                            bundleinfo = (protostuff['7'][1]['2'].get('3', ''))
                            appinfo2 = (protostuff['7'][2]['2'].get('3', ''))
                    else:
                        bundleinfo = ''
                else:
                    bundleinfo = ''
                
                timewrite = (webkit_timestampsconv(protostuff['8']))
                timewrite = convert_utc_human_to_timezone(timewrite, timezone_offset)
                
                data_list.append((ts, timestart, timeend, timewrite, record.state.name, activity, bundleid, bundleinfo,
                                  appinfo1, appinfo2, actionguid, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name, None, None, None, None, None, None, filename,
                                  record.data_start_offset))


    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), ('Time End', 'datetime'), ('Time Write', 'datetime'), 'SEGB State', 'Activity', 'Bundle ID', 'Bundle Info', 'App Info', 'App Info2', 'Action GUID', 'Filename', 'Offset')

    return data_headers, data_list, report_file


