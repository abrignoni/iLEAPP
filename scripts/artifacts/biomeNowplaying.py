__artifacts_v2__ = {
    "get_biomeNowplaying": {
        "name": "Biome Now Playing",
        "description": "Parses Now Playing entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Now Playing",
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
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, convert_utc_human_to_timezone


@artifact_processor
def get_biomeNowplaying(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'2': {'type': 'double', 'name': ''}, '3': {'type': 'int', 'name': ''}, '5': {'type': 'str', 'name': ''}, '6': {'type': 'int', 'name': ''}, '8': {'type': 'str', 'name': ''}, '9': {'type': 'int', 'name': ''}, '10': {'type': 'str', 'name': ''}, '13': {'type': 'int', 'name': ''}, '14': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'str', 'name': ''}}, 'name': ''}, '15': {'type': 'str', 'name': ''}}

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
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)
                
                timestart = (webkit_timestampsconv(protostuff['2']))
                timestart = convert_utc_human_to_timezone(timestart, timezone_offset)
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

    return data_headers, data_list, report_file
