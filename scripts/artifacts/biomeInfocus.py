__artifacts_v2__ = {
    "get_biomeInfocus": {
        "name": "Biome - In Focus",
        "description": "Parses InFocus Events from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The Foreground/Background labels for values 1 and 0 are an interpretation of the App.InFocus stream name; other values are reported as stored.",
        "paths": ('*/[Bb]iome/streams/restricted/App.InFocus/local/*',),
        "output_types": "standard",
        "artifact_icon": "focus-2",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 2439 rows",
            "felix_ios17": "iOS 17.6.1 | 516 rows",
            "fsfull002_ios17": "iOS 17.1 | 559 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4031 rows",
            "iphone11_ios17": "iOS 17.3 | 4943 rows",
            "iphone12_ios18": "iOS 18.7 | 1868 rows",
            "iphone14plus_ios18": "iOS 18.0 | 262 rows",
            "otto_ios17": "iOS 17.5.1 | 825 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}


import os
from datetime import timezone
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv


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

                data_list.append((ts, timestart, record.state.name, bundleid, foreground, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, filename, record.data_start_offset))

    data_headers = (('Timestamp', 'datetime'), ('Start Time', 'datetime'), 'SEGB State', 'Bundle ID', 'Action', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))

