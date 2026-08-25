__artifacts_v2__ = {
    "get_biomePhotosSearchInsights": {
        "name": "Biome - Photos Search Insights",
        "description": "Parses Photos search terms from the "
                       "AeroML.Insights.PhotosSearchInsights biome stream, along with the "
                       "language and region the search was made in. The search term is text "
                       "entered in the Photos app search.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Remaining fields were constant across the sample and are reported raw.",
        "paths": ('*/streams/*/AeroML.Insights.PhotosSearchInsights/local/*',),
        "output_types": "standard",
        "artifact_icon": "search",
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

TYPESS = {
    '1': {'type': 'int', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '9': {'type': 'str', 'name': ''},
    '22': {'type': 'str', 'name': ''},
    '23': {'type': 'str', 'name': ''},
    '24': {'type': 'str', 'name': ''},
    '25': {'type': 'int', 'name': ''},
    '26': {'type': 'int', 'name': ''},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


@artifact_processor
def get_biomePhotosSearchInsights(context):

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
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Photos Search Insights: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('9', b'')),
                                  _to_str(protostuff.get('22', b'')),
                                  _to_str(protostuff.get('23', b'')),
                                  _to_str(protostuff.get('24', b'')),
                                  protostuff.get('1', ''), protostuff.get('5', ''),
                                  protostuff.get('25', ''), protostuff.get('26', ''),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Search Term', 'Language',
                    'Region', 'Schema Version', 'Field 1 (raw)', 'Field 5 (raw)',
                    'Field 25 (raw)', 'Field 26 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
