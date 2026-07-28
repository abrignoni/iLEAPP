__artifacts_v2__ = {
    "get_biomeClockAlarm": {
        "name": "Biome - Clock Alarm",
        "description": "Parses alarm state changes from the Clock.Alarm biome stream, including "
                       "the alarm identifier, which can be correlated with the Clock app alarm "
                       "list and with the _DKEvent.Clock.Alarm stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Raw state values observed: 0, 1, 2 and 4. Apple describes this stream as "
                 "capturing alarm states such as firing and snoozed; exact value semantics are "
                 "not confirmed, so the raw value is reported.",
        "paths": ('*/streams/*/Clock.Alarm/local/*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 27 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
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

TYPESS = {
    '1': {'type': 'int', 'name': ''},
    '2': {'type': 'int', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'int', 'name': ''},
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
def get_biomeClockAlarm(context):

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
                    logfunc(f'Clock Alarm: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                data_list.append((ts, record.state.name, _to_str(protostuff.get('3', b'')),
                                  protostuff.get('2', ''), protostuff.get('1', ''),
                                  protostuff.get('4', ''), filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Alarm ID', 'State (raw)',
                    'Field 1 (raw)', 'Field 4 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
