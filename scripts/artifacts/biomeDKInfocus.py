__artifacts_v2__ = {
    "get_biomeDKInfocus": {
        "name": "Biome DKEvent In Focus",
        "description": "Parses DKEvent InFocus Events from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome In Focus",
        "notes": "",
        "paths": ('*/biome/streams/restricted/_DKEvent.App.InFocus/local/*'),
        "output_types": "standard"
    }
}


import os
import struct
import blackboxprotobuf
from io import BytesIO
from ccl_segb import read_segb_file
from ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_utc_human_to_timezone


@artifact_processor
def get_biomeDKInfocus(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    typess = {
        '1': {'type': 'message', 'message_typedef': {
            '1': {'type': 'str', 'name': ''},
            '2': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': ''},
                '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''},
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'double', 'name': ''},
        '4': {'type': 'message', 'message_typedef': {
            '1': {'type': 'message', 'message_typedef': {
                '1': {'type': 'int', 'name': ''},
                '2': {'type': 'int', 'name': ''}}, 'name': ''},
            '3': {'type': 'str', 'name': ''}}, 'name': ''},
        '5': {'type': 'str', 'name': ''},
        '7': {'type': 'message', 'message_typedef': {
            '1': {'type': 'message', 'message_typedef': {}, 'name': ''},
            '2': {'type': 'message', 'message_typedef': {
                '1': {'type': 'message', 'message_typedef': {
                    '1': {'type': 'int', 'name': ''},
                    '2': {'type': 'int', 'name': ''}}, 'name': ''},
                '3': {'type': 'str', 'name': ''}}, 'name': ''},
            '3': {'type': 'int', 'name': ''}}, 'name': ''},
        '8': {'type': 'double', 'name': ''},
        '10': {'type': 'int', 'name': ''}}

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
                bundleid = (protostuff['4']['3'])
                if protostuff.get('7', '') != '':
                    if isinstance(protostuff['7'], list):
                        transition = (protostuff['7'][0]['2']['3'])
                    else:
                        transition = (protostuff['7']['2']['3'])
                else:
                    transition = ''

                data_list.append((timestart, timeend, timewrite, activity, bundleid, transition, actionguid))

    data_headers = (('Time Start', 'datetime'), ('Time End', 'datetime'), ('Time Write', 'datetime'),'Activity',
                    'Bundle ID', 'Transition', 'Action GUID')

    return data_headers, data_list, file_found