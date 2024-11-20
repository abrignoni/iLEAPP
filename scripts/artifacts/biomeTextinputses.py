__artifacts_v2__ = {
    "get_biomeTextinputses": {
        "name": "Biome Text Input Session",
        "description": "Parses Text Input Session entries from biomes",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Text Input Session",
        "notes": "",
        "paths":
            ('*/Biome/streams/public/TextInputSession/local/*',
             '*/Biome/streams/restricted/Text.InputSession/local/*'),
        "output_types": "standard"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, convert_utc_human_to_timezone, convert_ts_int_to_timezone, webkit_timestampsconv


@artifact_processor
def get_biomeTextinputses(files_found, report_folder, seeker, wrap_text, timezone_offset):

    typess = {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'str', 'name': ''}, '4': {'type': 'int', 'name': ''}}

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

                duration = protostuff['1']
                # Records in "restricted" folder seem to have time in Unix time, whereas public was cocoa time
                if 'restricted' in file_found:
                    timestart = (convert_ts_int_to_timezone(protostuff['2'], timezone_offset))
                else:
                    timestart = (webkit_timestampsconv(protostuff['2']))
                    timestart = convert_utc_human_to_timezone(timestart, timezone_offset)

                bundleid = (protostuff.get('3',''))
                
                data_list.append((ts, timestart, record.state.name, bundleid, duration, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Time Start', 'datetime'), 'SEGB State', 'Bundle ID', 'Duration',
                    'Filename', 'Offset')

    return data_headers, data_list, report_file
