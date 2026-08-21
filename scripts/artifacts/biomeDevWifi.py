__artifacts_v2__ = {
    "get_biomeDevWifi": {
        "name": "Biome - WiFi Devices",
        "description": "Parses (device) WiFi connection entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/Device.Wireless.WiFi/local/*'),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 432 rows",
            "felix_ios17": "iOS 17.6.1 | 612 rows",
            "fsfull002_ios17": "iOS 17.1 | 228 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1164 rows",
            "iphone11_ios17": "iOS 17.3 | 1287 rows",
            "iphone14plus_ios18": "iOS 18.0 | 16 rows",
            "otto_ios17": "iOS 17.5.1 | 87 rows",
            "abe_ios16": "iOS 16.5 | 2350 rows",
            "felix23_ios16": "iOS 16.5 | 1706 rows",
            "magnet_ios16": "iOS 16.1.1 | 762 rows",
        }
    }
}


import os
import struct
from scripts import blackboxprotobuf
from datetime import timezone
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_biomeDevWifi(context):
    typess = {'1': {'type': 'str', 'name': 'SSID'}, '2': {'type': 'int', 'name': 'Connect'}}

    data_list = []
    source_dirs = set()
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

        stale_slots = 0
        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                    ssid = protostuff['SSID']
                    status = 'Connected' if protostuff['Connect'] == 1 else 'Disconnected'
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    # A SEGB v2 file can reuse its data area, leaving slots whose trailer still reads
                    # Written while the data itself has been overwritten; a failed CRC identifies
                    # those. Their decode was never going to succeed, so they are counted and
                    # reported once per file - one line per record buried the genuine failures.
                    # The CRC only decides how a failure is reported: every record is still decoded,
                    # so a CRC-failed slot that does parse is kept exactly as before.
                    if record.crc_passed is False:
                        stale_slots += 1
                    else:
                        logfunc(f"Skipping biomeDevWifi record due to protobuf decode error: {ex} | "
                                f"File: {context.get_relative_path(file_found)} | "
                                f"Offset: {record.data_start_offset}")
                    continue
                data_list.append((ts, record.state.name, ssid, status, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, filename, record.data_start_offset))

        if stale_slots:
            logfunc(f"biomeDevWifi: skipped {stale_slots} record(s) with a failed CRC (overwritten "
                    f"data area) in {context.get_relative_path(file_found)}")

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'SSID', 'Status', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))

