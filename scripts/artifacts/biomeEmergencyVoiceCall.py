__artifacts_v2__ = {
    "get_biomeEmergencyVoiceCall": {
        "name": "Biome - Emergency Voice Call",
        "description": "Parses emergency voice calls from the "
                       "CommCenter.Call.EmergencyVoiceCall biome stream: the emergency number "
                       "that was dialled and the mobile country and network codes of the "
                       "serving network at the time of the call.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field mapped from a small private sample, so read the columns with that in "
                 "mind. Field 1 is the dialled number and is unambiguous in an emergency call "
                 "stream. Fields 2 and 3 are short numeric strings in the positions and value "
                 "ranges of a mobile country code and mobile network code, which is the "
                 "reading given here but is inferred from shape rather than confirmed. Field 7 "
                 "is a small integer that varies per call and is consistent with a duration in "
                 "seconds; it is labelled as such but marked unconfirmed. Fields 4, 5 and 6 "
                 "were constant across the sample and are reported raw. Corroborate against "
                 "CallHistory.storedata where the call still exists there.",
        "paths": ('*/streams/*/CommCenter.Call.EmergencyVoiceCall/local/*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
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
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '6': {'type': 'int', 'name': ''},
    '7': {'type': 'int', 'name': ''},
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
def get_biomeEmergencyVoiceCall(context):

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
                    logfunc(f'Emergency Voice Call: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  _to_str(protostuff.get('2', b'')),
                                  _to_str(protostuff.get('3', b'')),
                                  protostuff.get('7', ''),
                                  protostuff.get('4', ''), protostuff.get('5', ''),
                                  protostuff.get('6', ''), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Emergency Number',
                    'Mobile Country Code', 'Mobile Network Code',
                    'Duration Seconds (unconfirmed)', 'Field 4 (raw)', 'Field 5 (raw)',
                    'Field 6 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
