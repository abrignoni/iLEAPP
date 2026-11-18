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
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names are those of the BMSiriUI class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Columns reported before as Session ID, Related ID and Presentation "
                 "(raw) are now UUID, Turn ID and View Mode. The two records of a pair share a "
                 "UUID, so records can be grouped on it: on the tested images the 80 written "
                 "records formed 40 UUID pairs, each with one record at field 5 = 1 and one at "
                 "0. The time between the two records of a pair is the time between their SEGB "
                 "record timestamps, and that it equals the time the interface was shown was "
                 "not tested. The framework names field 5 starting, a boolean. On the tested "
                 "images it was 1 on the record with no dismissal reason and 0 on the record "
                 "that carries one; the Interface State labels Presented and Dismissed follow "
                 "that observation. On the tested images all 40 Dismissed records carried a "
                 "dismissal reason, with seven distinct values, among them HardwareButton, "
                 "Timeout and TapOutsideOfContent. View Mode is a string in the framework and is reported "
                 "as stored; on the tested images it was set on the 40 Presented records and "
                 "empty on the 40 Dismissed records. On the tested images Turn ID was set on 55 "
                 "of the 80 written records. The framework sessionID field was not present on any written record "
                 "on the tested images and is not reported. The framework absoluteTimestamp "
                 "field (field 6, present on all 80 written records on the tested images) and "
                 "carplayPPID field (field 8, present on 6) are also not reported.",
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

# Pin the string fields so a short string is never decoded as a nested message.
TYPESS = {
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'str', 'name': ''},
    '7': {'type': 'str', 'name': ''},
    '8': {'type': 'str', 'name': ''},
}


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
            if 'tombstone' in context.get_relative_path(file_found):
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
                    'State (raw)', 'Dismissal Reason', 'UUID', 'Turn ID',
                    'View Mode', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
