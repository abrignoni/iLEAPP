__artifacts_v2__ = {
    "get_biomeBluetooth": {
        "name": "Biome Bluetooth",
        "description": "Parses bluetooth connection entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Bluetooth",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/Device.Wireless.Bluetooth/local/*'),
        "output_types": "standard"
    }
}


import os
import blackboxprotobuf
from datetime import *
from ccl_segb import read_segb_file
from ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_biomeBluetooth(files_found, report_folder, seeker, wrap_text, timezone_offset):

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
                protostuff, _ = blackboxprotobuf.decode_message(record.data)

                ts = record.timestamp1
                ts = ts.replace(tzinfo=timezone.utc)
                
                mac = protostuff['1'].decode()
                if isinstance(protostuff['2'], dict):
                    desc = protostuff['2']
                else:
                    desc = protostuff['2'].decode()
                data_list.append((ts, mac, desc, filename, record.data_start_offset))

    data_headers = (('Timestamp', 'datetime'), 'MAC', 'Name', 'Filename', 'Offset')

    return data_headers, data_list, file_found
