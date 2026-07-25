__artifacts_v2__ = {
    "get_biomeSafariNavigations": {
        "name": "Biome - Safari Navigations",
        "description": "Parses Safari navigation events from the Safari.Navigations biome stream: "
                       "host, full URL (observed on iOS 18+; earlier versions record the host only) "
                       "and country code. Complements App.WebUsage and _DKEvent.Safari.History, and "
                       "records were observed to remain after the matching History.db visits were "
                       "gone.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "The rounded timestamp is the record timestamp rounded up to the next 30 minute "
                 "boundary (observed consistently on iOS 17 and 18.7 samples).",
        "paths": ('*/streams/*/Safari.Navigations/local/*',),
        "output_types": "standard",
        "artifact_icon": "compass",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
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

# Pin flat fields so host/URL strings are never eagerly decoded as nested protobuf.
TYPESS = {
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'double', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'str', 'name': ''},
    '8': {'type': 'str', 'name': ''},
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


def _unix_double(value):
    # Unix epoch double stored in a fixed64.
    if isinstance(value, int) and value > 10 ** 15:
        value = struct.unpack('<d', struct.pack('<q', value))[0]
    if not isinstance(value, (int, float)) or not value:
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeSafariNavigations(context):

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
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Safari Navigations: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                rounded_ts = _unix_double(protostuff.get('2'))
                host = _to_str(protostuff.get('1', b''))
                url = _to_str(protostuff.get('8', b''))
                country = _to_str(protostuff.get('5', b''))

                data_list.append((ts, rounded_ts, record.state.name, host, url, country,
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Rounded Timestamp (30 min)', 'datetime'),
                    'SEGB State', 'Host', 'URL', 'Country', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
