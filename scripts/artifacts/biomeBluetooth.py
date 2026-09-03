__artifacts_v2__ = {
    "get_biomeBluetooth": {
        "name": "Biome - Bluetooth",
        "description": "Parses Bluetooth device entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Biome",
        "notes": "Use caution when interpreting this artifact. Lists of Bluetooth devices have been "
                 "observed sharing a single SEGB timestamp, so the presence of a device in this "
                 "stream does not establish that the device was connected to the iOS device at "
                 "that time. Reference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple "
                 "Biome', https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html\n"
                 "Records are read from both the local and remote subfolders; the Sync Origin column reports which one a record came from, with the remote folder's device identifier. Remote records were synced from another device on the same account and are not events of this device. Files under a tombstone folder are skipped.",
        "paths": ('*/Biome/streams/restricted/Device.Wireless.Bluetooth/local/*',
                  '*/Biome/streams/restricted/Device.Wireless.Bluetooth/remote/*'),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 87 rows (14 remote)",
            "felix_ios17": "iOS 17.6.1 | 420 rows (420 remote)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 22 rows",
            "abe_ios16": "iOS 16.5 | 84 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
        }
    }
}


import os
from scripts import blackboxprotobuf
from datetime import timezone
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor


def _sync_origin(file_found):
    """Local for the device's own stream, Remote (<device id>) for a copy synced from another
    device on the same account; the id is the folder name Biome keeps under remote/."""
    normalized = file_found.replace('\\', '/')
    if '/remote/' in normalized:
        trailer = normalized.split('/remote/', 1)[1]
        if '/' in trailer:
            return f"Remote ({trailer.split('/', 1)[0]})"
        return 'Remote'
    return 'Local'


@artifact_processor
def get_biomeBluetooth(context):

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

        origin = _sync_origin(file_found)
        source_dirs.add(os.path.dirname(file_found))
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
                data_list.append((ts, record.state.name, mac, desc, origin, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, origin, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'MAC', 'Name', 'Sync Origin', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
