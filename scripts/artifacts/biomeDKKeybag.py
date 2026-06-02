__artifacts_v2__ = {
    "get_biomeDKKeybag": {
        "name": "Biome - Keybag",
        "description": "Parses DKEvent Keybag IsLocked entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.1",
        "date": "2025-04-29",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/_DKEvent.Keybag.IsLocked/local/*'),
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
def get_biomeDKKeybag(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '4': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'bytes', 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}

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

                time2 = (webkit_timestampsconv(protostuff['2']))
                time2 = convert_utc_human_to_timezone(time2, timezone_offset)

                time3 = (webkit_timestampsconv(protostuff['3']))
                time3 = convert_utc_human_to_timezone(time3, timezone_offset)



                data_list.append((ts, time2, time3, '1 - Locked ' if protostuff['4']['4'] == 1 else '0 - Unlocked'))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Time', 'datetime'), ('End Time', 'datetime'), 'isLocked')

    return data_headers, data_list, report_file
