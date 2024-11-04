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
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_biomeBluetooth(files_found, report_folder, seeker, wrap_text, timezone_offset):

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
                protostuff, _ = blackboxprotobuf.decode_message(record.data)
                
                mac = protostuff['1'].decode()
                if isinstance(protostuff['2'], dict):
                    desc = protostuff['2']
                else:
                    desc = protostuff['2'].decode()
                data_list.append((ts, record.state.name, mac, desc, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'MAC', 'Name', 'Filename', 'Offset')

    return data_headers, data_list, report_file
