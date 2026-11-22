__artifacts_v2__ = {
    "get_biomeDevTimeZone": {
        "name": "Biome - Device TimeZone",
        "description": "Parses historical device time zone records from the Device.TimeZone biome "
                       "stream",
        "author": "Cynthia van Dorp, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-09",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names are those of the BMDeviceTimeZone class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Seconds From GMT is field 1, a double the framework names secondsFromGMT; "
                 "it was not reported before. On the tested images (16 images, 386 rows) every "
                 "value was a whole number of seconds, a multiple of 900 and within 14 hours of "
                 "GMT. Seconds From GMT held one value on every row of cookbook_ios1751 (11 rows) "
                 "and hc_ios17_2 (4 rows), and two to seven values on the other images.",
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
import struct
from datetime import timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


@artifact_processor
def get_biomeDevTimeZone(context):
    typess = {'1': {'type': 'double', 'name': ''}, '2': {'type': 'str', 'name': ''}}
    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Device TimeZone: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                tz = protostuff.get('2')
                if tz is None:
                    logfunc(f"Biome - Device TimeZone: record without timezone field in {filename}, skipped")
                    continue

                offset = protostuff.get('1')
                if isinstance(offset, float) and offset.is_integer():
                    offset = int(offset)

                data_list.append((ts, tz, offset, filename))

    data_headers = (('SEGB Timestamp', 'datetime'), 'Timezone', 'Seconds From GMT', 'Filename')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
