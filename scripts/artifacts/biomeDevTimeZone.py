__artifacts_v2__ = {
    "get_biomeDevTimeZone": {
        "name": "Biome - Device TimeZone",
        "description": "Parses historical device time zone changes from the Device.TimeZone biome "
                       "stream",
        "author": "Cynthia van Dorp, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-09",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/Device.TimeZone/local/*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 30 rows",
            "iphone11_ios17": "iOS 17.3 | 27 rows",
        },
    }
}

import os
from datetime import timezone
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc


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
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                tz = protostuff.get('2')
                if tz is None:
                    logfunc(f"Biome - Device TimeZone: record without timezone field in {filename}, skipped")
                    continue

                data_list.append((ts, tz, filename))

    data_headers = (('SEGB Timestamp', 'datetime'), 'Timezone', 'Filename')

    return data_headers, data_list, 'see Filename for more info'
