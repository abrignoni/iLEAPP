__artifacts_v2__ = {
    "get_biomeFrontBoardDisplayElement": {
        "name": "Biome - FrontBoard Display Element",
        "description": "Parses app scene display events from the FrontBoard.DisplayElement "
                       "biome stream: which app scene was recorded against which display and "
                       "when. This is a high volume stream that may assist in reconstructing "
                       "app display activity; whether a record corresponds to on-screen "
                       "presentation is not established.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "In sample data, records with an empty bundle id corresponded to system or "
                 "home screen scenes. Numeric state fields are reported raw as their semantics "
                 "are not confirmed.",
        "paths": ('*/streams/*/FrontBoard.DisplayElement/local/*',),
        "output_types": "standard",
        "artifact_icon": "layers",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 7762 rows",
            "iphone11_ios17": "iOS 17.3 | 5234 rows",
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

TYPESS = {
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '6': {'type': 'int', 'name': ''},
    '7': {'type': 'int', 'name': ''},
    '8': {'type': 'int', 'name': ''},
    '10': {'type': 'int', 'name': ''},
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
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<q', value))[0] if value > 10 ** 15 else value
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeFrontBoardDisplayElement(context):

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
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'FrontBoard Display Element: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                display = protostuff.get('9', {})
                if not isinstance(display, dict):
                    display = {}

                data_list.append((ts, _unix_double(protostuff.get('1')), record.state.name,
                                  _to_str(protostuff.get('3', b'')),
                                  _to_str(protostuff.get('2', b'')),
                                  _to_str(display.get('2', b'')),
                                  _to_str(display.get('3', b'')),
                                  protostuff.get('4', ''), protostuff.get('5', ''),
                                  protostuff.get('6', ''), protostuff.get('7', ''),
                                  protostuff.get('8', ''), protostuff.get('10', ''),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Event Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Scene ID', 'Display Type', 'Display Role',
                    'Field 4 (raw)', 'Field 5 (raw)', 'Field 6 (raw)', 'Field 7 (raw)',
                    'Field 8 (raw)', 'Field 10 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
