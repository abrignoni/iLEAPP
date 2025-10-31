__artifacts_v2__ = {
    "get_biomeNowplaying": {
        "name": "Biome - Now Playing",
        "description": "Parses Now Playing entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2025-10-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/public/NowPlaying/local/*'),
        "output_types": "standard"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv


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
                data_list.append((ts, timestart, record.state.name, bundleid, output, info, info2, info3, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Bundle ID', 'Output',
                    'Media Type', 'Title', 'Artist', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
