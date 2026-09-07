__artifacts_v2__ = {
    "get_biomeDeviceMetadata": {
        "name": "Biome - Device Metadata",
        "description": "Parses OS build records from the Device.Metadata biome stream. Each record "
                       "captures the OS build at the time it was written, producing an iOS "
                       "version/update history that can span years.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Observed builds spanning iOS 16 through 18 in test extractions (e.g. 20B110, "
                 "21D50, 22H31).",
        "paths": ('*/streams/*/Device.Metadata/local/*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
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

# Pin flat fields so build strings are never eagerly decoded as nested protobuf.
TYPESS = {
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'str', 'name': ''},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


@artifact_processor
def get_biomeDeviceMetadata(context):

    data_list = []
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
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
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Device Metadata: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                os_build = _to_str(protostuff.get('2', b''))
                os_build_alt = _to_str(protostuff.get('4', b''))
                record_type = protostuff.get('3', '')

                data_list.append((ts, record.state.name, os_build, os_build_alt, record_type,
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'OS Build',
                    'OS Build (Field 4)', 'Type (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
