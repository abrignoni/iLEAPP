__artifacts_v2__ = {
    "get_biomeHardware": {
        "name": "Biome - Hardware Reliability",
        "description": "Parses hardware reliability entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2025-03-05",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/OSAnalytics.Hardware.Reliability/local/*'),
        "output_types": "standard"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor
from scripts.context import Context


@artifact_processor
def get_biomeHardware(context:Context):

    typess = {'1': {'type': 'str', 'name': ''}}

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
                
                #pp = pprint.PrettyPrinter(indent=4)
                #pp.pprint(protostuff)
                #print(types)
                
                hardware = (protostuff['1'])
                
                data_list.append((ts, record.state.name, hardware, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, filename, record.data_start_offset))

    data_headers = (('SEGB Record Time', 'datetime'), 'SEGB State', 'Hardware', 'Filename', 'Offset')

    return data_headers, data_list, ''
