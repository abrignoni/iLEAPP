__artifacts_v2__ = {
    "get_biomeSafari": {
        "name": "Biome Safari",
        "description": "Parses safari entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Safari",
        "notes": "",
        "paths": ('*/biome/streams/restricted/_DKEvent.Safari.History/local/*'),
        "output_types": "standard"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from ccl_segb import read_segb_file
from ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_utc_human_to_timezone


@artifact_processor
def get_biomeSafari(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '5': {'type': 'str', 'name': ''}, '6': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'str', 'name': ''}, '3': {'type': 'str', 'name': ''}, '4': {'type': 'str', 'name': ''}, '6': {'type': 'int', 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''}, '8': {'type': 'fixed64', 'name': ''}, '10': {'type': 'int', 'name': ''}}

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
                ts1 = record.timestamp1
                ts1 = ts1.replace(tzinfo=timezone.utc)

                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
                activity = (protostuff['1']['1'])
                timestart = (webkit_timestampsconv(protostuff['2']))
                url = (protostuff['4']['3'])
                guid = (protostuff['5'])
                detail1 = (protostuff['6']['1'])
                detail2 = (protostuff['6']['2'])
                detail3 = (protostuff['6']['4'])
                title = (protostuff['7']['2']['3'])

                data_list.append((ts1, timestart, activity, title, url, detail1, detail2, detail3, guid, filename,
                                  record.data_start_offset))

        data_headers = (('Timestamp SEGB', 'datetime'), ('Timestamp', 'datetime'), 'Activity', 'Title', 'URL', 'Detail',
                        'Detail 2', 'Detail 3', 'GUID', "Filename", "Offset")

        return data_headers, data_list, file_found