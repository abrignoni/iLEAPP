__artifacts_v2__ = {
    "get_biomeDevTimeZone": {
        "name": "Biome - Device TimeZone",
        "description": "Parses the device time zone from biomes",
        "author": "Cynthia van Dorp",
        "creation_date": "2026-07-09",
        "last_update_date": "2026-07-09",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/biome/streams/restricted/Device.TimeZone/local/*'),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    }
}

import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_plist_content


@artifact_processor
def get_biomeDevTimeZone(context):
    typess = {'1': {'type': 'fixed64', 'name': ''}, '2': {'type': 'str', 'name': ''}}
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
                print("File found: ", file_found)
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                tz = protostuff['2']

                data_list.append((ts, tz, filename))

    data_headers = (('SEGB Timestamp', 'datetime'), 'Timezone', 'Filename')

    return data_headers, data_list, 'see Filename for more info'
