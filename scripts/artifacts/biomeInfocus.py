__artifacts_v2__ = {
    "get_biomeInfocus": {
        "name": "Biome In Focus",
        "description": "Parses InFocus Events from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome In Focus",
        "notes": "",
        "paths": ('*/biome/streams/restricted/App.InFocus/local/*'),
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
def get_biomeInfocus(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'10': {'name': '', 'type': 'str'}, '2': {'name': '', 'type': 'int'}, '3': {'name': '', 'type': 'int'},
              '4': {'name': '', 'type': 'double'}, '6': {'name': '', 'type': 'str'}, '9': {'name': '', 'type': 'str'}}

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

                bundleid = (protostuff['6'])
                timestart = (webkit_timestampsconv(protostuff['4']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)
                foreground = ('Foreground' if protostuff['3'] == 1 else 'Background')

                data_list.append((timestart, bundleid, foreground, filename))

    data_headers = (('Timestamp', 'datetime'), 'Bundle ID', 'Action', 'Filename')

    return data_headers, data_list, file_found

