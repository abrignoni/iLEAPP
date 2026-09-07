__artifacts_v2__ = {
    "get_biomeSiriUI": {
        "name": "Biome - Siri UI",
        "description": "Parses Siri interface sessions from the Siri.UI biome stream. In test "
                       "data records paired: one carrying state 1 with no dismissal reason, "
                       "followed by one carrying state 0 and a dismissal reason (e.g. "
                       "HardwareButton), consistent with the Siri interface appearing and "
                       "being dismissed.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Dismissal reasons observed: HardwareButton, Punchout, Timeout and "
                 "TapOutsideOfContent. The two records of a pair share a session identifier, "
                 "so sort by timestamp and group on it to measure how long the interface was "
                 "up. Field 5 is 1 on the appearing record and 0 on the dismissing one. The "
                 "presentation field carried a single constant value in the sample and is "
                 "reported raw.",
        "paths": ('*/streams/*/Siri.UI/local/*',),
        "output_types": "standard",
        "artifact_icon": "mic",
        "sample_data": {
            "dexter_ios18": "11 rows",
            "felix_ios17": "6 rows",
            "hc_ios26": "26.5.2 | 2 rows",
            "iphone11_ios17": "30 rows",
            "otto_ios17": "111 rows",
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

SESSION_STATE = {0: 'Dismissed', 1: 'Presented'}


def _to_str(value):
    """Absent submessages decode as an empty dict, which is not a value."""
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


@artifact_processor
def get_biomeSiriUI(context):

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
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Siri UI: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                raw_state = protostuff.get('5', '')

                data_list.append((ts, record.state.name,
                                  SESSION_STATE.get(raw_state, ''), raw_state,
                                  _to_str(protostuff.get('4')),
                                  _to_str(protostuff.get('2')),
                                  _to_str(protostuff.get('7')),
                                  _to_str(protostuff.get('3')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Interface State',
                    'State (raw)', 'Dismissal Reason', 'Session ID', 'Related ID',
                    'Presentation (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
