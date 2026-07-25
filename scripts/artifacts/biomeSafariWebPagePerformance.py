__artifacts_v2__ = {
    "get_biomeSafariWebPagePerformance": {
        "name": "Biome - Safari Web Page Performance",
        "description": "Parses Safari page load performance events from the "
                       "Safari.WebPagePerformance biome stream. Each record marks Safari web "
                       "activity in a rounded time bucket and complements Safari.Navigations "
                       "and App.WebUsage.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Like Safari.Navigations, the second timestamp is rounded up to the next 30 "
                 "minute boundary. Remaining fields are performance counters and are reported "
                 "raw as their units are not confirmed.",
        "paths": ('*/streams/*/Safari.WebPagePerformance/local/*',),
        "output_types": "standard",
        "artifact_icon": "compass",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
        },
    }
}


import os
import struct
from datetime import datetime, timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


def _unix_double(value):
    if isinstance(value, int) and value > 10 ** 15:
        value = struct.unpack('<d', struct.pack('<q', value))[0]
    if not isinstance(value, (int, float)) or not value:
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeSafariWebPagePerformance(context):

    data_list = []
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

        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Safari Web Page Performance: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                detail = protostuff.get('1', {})
                detail = _to_str(detail) if not isinstance(detail, (dict, list)) else str(detail)

                data_list.append((ts, _unix_double(protostuff.get('2')), record.state.name,
                                  detail, protostuff.get('3', ''), protostuff.get('4', ''),
                                  protostuff.get('5', ''), filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Rounded Timestamp (30 min)', 'datetime'),
                    'SEGB State', 'Detail (raw)', 'Field 3 (raw)', 'Field 4 (raw)',
                    'Field 5 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
