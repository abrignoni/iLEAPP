__artifacts_v2__ = {
    "get_biomeAirpMode": {
        "name": "Biome DKEvent Airplane Mode",
        "description": "Parses airplane mode entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2020-04-30",
        "requirements": "none",
        "category": "Biome Airplane Mode",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/_DKEvent.System.AirplaneMode/local/*'),
        "output_types": "standard"
    }
}

import os
import blackboxprotobuf
from datetime import *
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_ts_human_to_timezone_offset

@artifact_processor
def get_biomeAirpMode(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'bytes', 'message_typedef': {'8': {'type': 'fixed64', 'name': ''}}, 'name': ''}}, 'name': ''}, '5': {'type': 'bytes', 'name': ''}, '8': {'type': 'fixed64', 'name': ''}, '10': {'type': 'int', 'name': ''}}

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
            offset = record.data_start_offset
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
                timestart = (webkit_timestampsconv(protostuff['2']))
                timeend = (webkit_timestampsconv(protostuff['3']))
                #timeend = convert_ts_int_to_utc(timeend)
                event = protostuff['1']['1']
                guid = protostuff['5'].decode()

                data_list.append((ts, timestart, timeend, record.state.name, event, guid, filename, offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, record.state.name, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), ('Timestamp2', 'datetime'), 'SEGB State'
                    , 'Event', 'GUID', 'Filename', 'Offset')

    return data_headers, data_list, report_file


