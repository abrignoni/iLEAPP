__artifacts_v2__ = {
    "get_biomeNowplaying": {
        "name": "Biome - Now Playing",
        "description": "Parses Now Playing entries from biomes",
        "author": "@JohnHyla, @mattiaepi (Mattia Epifani)",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Biome",
        "notes": "Records are read from both the local and remote subfolders; the Sync Origin column reports which one a record came from, with the remote folder's device identifier. Remote records were synced from another device on the same account and are not events of this device. Files under a tombstone folder are skipped. Remote Now Playing records carry the bundle id and "
                 "timestamps only: Output, Media Type, Title and Artist are not present in the synced copies "
                 "and are blank on those rows.",
        "paths": (
            '*/Biome/streams/public/NowPlaying/local/*',
            '*/streams/*/Media.NowPlaying/local/*',
            '*/streams/*/Media.NowPlaying/remote/*',
        ),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 234 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 68 rows",
            "magnet_ios16": "iOS 16.1.1 | 22 rows",
            "hc_ios18_7": "iOS 18.7.8 | 14 rows",
            "iphone11_ios17": "iOS 17.3 | 242 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 22 rows (20 remote)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 742 rows (108 remote)",
            "falken_ios26": "iOS 26.2.1 | 116 rows (102 remote)",
            "felix_ios17": "iOS 17.6.1 | 1986 rows (1976 remote)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 25 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 126 rows",
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
def get_biomeNowplaying(context):

    typess = {
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'int', 'name': ''},
        '5': {'type': 'str', 'name': ''},
        '6': {'type': 'int', 'name': ''},
        '8': {'type': 'str', 'name': ''},
        '9': {'type': 'int', 'name': ''},
        '10': {'type': 'str', 'name': ''},
        '13': {'type': 'int', 'name': ''},
        '14': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'int', 'name': ''},
                '2': {'type': 'int', 'name': ''},
                '3': {'type': 'str', 'name': ''}
            },
            'name': ''
        },
        '15': {'type': 'str', 'name': ''}
    }

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
                
                timestart = (webkit_timestampsconv(protostuff['2']))
                bundleid = (protostuff['15'])
                info = (protostuff.get('10',''))
                info2 = (protostuff.get('8',''))
                info3 = (protostuff.get('5',''))
                if (protostuff.get('14','')) != '':
                    if isinstance(protostuff['14'], dict):
                        output = protostuff['14']['3']
                    else:
                        output = (f"{protostuff['14'][0]['3']} <-> {protostuff['14'][1]['3']}")
                else:
                    output = ''
                data_list.append((ts, timestart, record.state.name, bundleid, output, info, info2, info3, origin,
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, origin,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Bundle ID', 'Output',
                    'Media Type', 'Title', 'Artist', 'Sync Origin', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
