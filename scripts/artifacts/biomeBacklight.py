__artifacts_v2__ = {
    "get_biomeBacklight": {
        "name": "Biome Backlight",
        "description": "Parses backlight entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Backlight",
        "notes": "",
        "paths": ('*/Biome/streams/public/Backlight/local/*'),
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
def get_biomeBacklight(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'double', 'name': ''}, '2': {'type': 'int', 'name': ''}}

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

                timestart = (webkit_timestampsconv(protostuff['1']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)
                state = (protostuff['2'])

                data_list.append((timestart, state, filename, record.data_start_offset))

    data_headers = (('Timestamp', 'datetime'), 'State', 'Filename', 'Offset')

    return data_headers, data_list, file_found
