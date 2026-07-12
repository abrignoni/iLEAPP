__artifacts_v2__ = {
    "get_biomeDKInfocus": {
        "name": "Biome - In Focus DKEvent",
        "description": "Parses DKEvent InFocus Events from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/biome/streams/restricted/_DKEvent.App.InFocus/local/*'),
        "output_types": "standard",
        "artifact_icon": "focus-2",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | 261 rows",
            "fsfull002_ios17": "iOS 17.1 | 290 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2024 rows",
            "iphone11_ios17": "iOS 17.3 | 2476 rows",
            "iphone12_ios18": "iOS 18.7 | 936 rows",
            "iphone14plus_ios18": "iOS 18.0 | 132 rows",
            "otto_ios17": "iOS 17.5.1 | 1758 rows",
            "dexter_ios18": "iOS 18.3.2 | 3838 rows",
            "abe_ios16": "iOS 16.5 | 2938 rows",
            "felix23_ios16": "iOS 16.5 | 753 rows",
            "magnet_ios16": "iOS 16.1.1 | 333 rows",
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
def get_biomeDKInfocus(context):
    
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
                    timewrite = (webkit_timestampsconv(protostuff['8']))

                    actionguid = (protostuff['5'])
                    bundleid = (protostuff['4']['3'])
                    if protostuff.get('7', '') != '':
                        if isinstance(protostuff['7'], list):
                            transition = (protostuff['7'][0]['2']['3'])
                        else:
                            transition = (protostuff['7']['2']['3'])
                    else:
                        transition = ''
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeDKInfocus record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

                data_list.append((ts, timestart, timeend, timewrite, record.state.name, activity, bundleid, transition,
                                  actionguid, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), ('Time End', 'datetime'),
                    ('Time Write', 'datetime'), 'SEGB State', 'Activity', 'Bundle ID', 'Transition', 'Action GUID',
                    'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
