__artifacts_v2__ = {
    "get_biomeHardware": {
        "name": "Biome - Hardware Reliability",
        "description": "Parses hardware reliability entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/OSAnalytics.Hardware.Reliability/local/*'),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 783 rows",
            "felix_ios17": "iOS 17.6.1 | 110 rows",
            "fsfull002_ios17": "iOS 17.1 | 345 rows",
            "hc_ios18_7": "iOS 18.7.8 | 485 rows",
            "iphone11_ios17": "iOS 17.3 | 1106 rows",
            "iphone12_ios18": "iOS 18.7 | 370 rows",
            "iphone14plus_ios18": "iOS 18.0 | 28 rows",
            "otto_ios17": "iOS 17.5.1 | 2789 rows",
            "abe_ios16": "iOS 16.5 | 4493 rows",
            "felix23_ios16": "iOS 16.5 | 1279 rows",
            "magnet_ios16": "iOS 16.1.1 | 236 rows",
        }
    }
}


import os
import struct
from datetime import timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_biomeHardware(context):

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
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                    hardware = (protostuff['1'])
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeHardware record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

                data_list.append((ts, record.state.name, hardware, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, filename, record.data_start_offset))

    data_headers = (('SEGB Record Time', 'datetime'), 'SEGB State', 'Hardware', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
