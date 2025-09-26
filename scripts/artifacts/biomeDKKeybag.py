__artifacts_v2__ = {
    "get_biomeDKKeybag": {
        "name": "Biome Keybag",
        "description": "Parses DKEvent Keybag IsLocked entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2025-04-29",
        "last_update_date": "2025-05-06",
        "requirements": "none",
        "category": "Biome Keybag",
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
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv
from scripts.context import Context


@artifact_processor
def get_biomeDKKeybag(context:Context):

    typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'str', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '4': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'bytes', 'name': ''}, '8': {'type': 'double', 'name': ''}, '10': {'type': 'int', 'name': ''}}

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
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)

                time2 = (webkit_timestampsconv(protostuff['2']))

                time3 = (webkit_timestampsconv(protostuff['3']))



                data_list.append((ts, time2, time3, '1 - Locked ' if protostuff['4']['4'] == 1 else '0 - Unlocked'), filename)

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Time', 'datetime'), ('End Time', 'datetime'), 'isLocked', 'Filename')

    return data_headers, data_list, ''
