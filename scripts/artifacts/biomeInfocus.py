__artifacts_v2__ = {
    "get_biomeInfocus": {
        "name": "Biome - In Focus",
        "description": "Parses InFocus Events from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Biome",
        "notes": "The Foreground/Background labels for values 1 and 0 are an interpretation of the App.InFocus stream name; other values are reported as stored. Records are read from both the local and remote subfolders; the Sync Origin column reports which one a record came from, with the remote folder's device identifier. Remote records were synced from another device on the same account and are not events of this device. Files under a tombstone folder are skipped.",
        "paths": ('*/[Bb]iome/streams/restricted/App.InFocus/local/*',
                  '*/[Bb]iome/streams/restricted/App.InFocus/remote/*'),
        "output_types": "standard",
        "artifact_icon": "focus-2",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 3895 rows (1456 remote)",
            "felix_ios17": "iOS 17.6.1 | 20368 rows (19852 remote)",
            "fsfull002_ios17": "iOS 17.1 | 680 rows (121 remote)",
            "hc_ios18_7": "iOS 18.7.8 | 4031 rows",
            "iphone11_ios17": "iOS 17.3 | 4943 rows",
            "iphone12_ios18": "iOS 18.7 | 2073 rows (205 remote)",
            "iphone14plus_ios18": "iOS 18.0 | 909 rows (647 remote)",
            "otto_ios17": "iOS 17.5.1 | 1139 rows (314 remote)",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2357 rows (1490 remote)",
            "cookbook_ios1751": "iOS 17.5.1 | 947 rows (240 remote)",
            "falken_ios26": "iOS 26.2.1 | 2374 rows (730 remote)",
            "hc_ios26": "iOS 26.5.2 | 545 rows (230 remote)",
        }
    }
}


import os
from datetime import timezone
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv


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
def get_biomeInfocus(context):

    typess = {'10': {'name': '', 'type': 'str'}, '2': {'name': '', 'type': 'int'}, '3': {'name': '', 'type': 'int'},
              '4': {'name': '', 'type': 'double'}, '6': {'name': '', 'type': 'str'}, '9': {'name': '', 'type': 'str'}}

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
                protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                bundleid = (protostuff['6'])
                timestart = (webkit_timestampsconv(protostuff['4']))
                state = protostuff['3']
                foreground = {1: 'Foreground', 0: 'Background'}.get(state, str(state))

                data_list.append((ts, timestart, record.state.name, bundleid, foreground, origin, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, origin, filename, record.data_start_offset))

    data_headers = (('Timestamp', 'datetime'), ('Start Time', 'datetime'), 'SEGB State', 'Bundle ID', 'Action', 'Sync Origin', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))

