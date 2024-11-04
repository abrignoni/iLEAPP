__artifacts_v2__ = {
    "get_biomeNotificationsPub": {
        "name": "Biome Notifications Pub",
        "description": "Parses notifications entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Notifications",
        "notes": "",
        "paths": ('*/Biome/streams/public/Notification/local/*'),
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
def get_biomeNotificationsPub(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'str', 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'int', 'name': ''}, '4': {'type': 'str', 'name': ''}, '5': {'type': 'str', 'name': ''}, '8': {'type': 'str', 'name': ''}, '9': {'type': 'str', 'name': ''}, '11': {'type': 'int', 'name': ''}, '12': {'type': 'str', 'name': ''}, '14': {'type': 'str', 'name': ''}, '16': {'type': 'int', 'name': ''}}

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
                
                timestart = (webkit_timestampsconv(protostuff['2']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)
                bundleid = (protostuff['14'])
                data1 = (protostuff.get('8',''))
                data2 = (protostuff.get('9',''))
                data3 = (protostuff.get('12',''))
                data4 = (protostuff.get('15',''))
                data5 = (protostuff.get('5',''))
                if data4 != '':
                    data4 = data4.decode()
                data = (protostuff.get('1',''))
                
                data_list.append((ts, timestart, record.state.name, bundleid, data1, data2, data3, data4, data5, data,
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Bundle ID', 'Field 1',
                    'Field 2','Field 3','Field 4','Field 5','Field 6', 'Filename', 'Offset')

    return data_headers, data_list, report_file

