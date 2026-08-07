__artifacts_v2__ = {
    "get_biomeShareSheetFeedback": {
        "name": "Biome - Share Sheet Feedback",
        "description": "Parses share sheet activity from the ShareSheet.Feedback biome stream: "
                       "the app the content was shared from, the activity recorded as chosen "
                       "(for example copy to pasteboard, save photo, open in Safari) and the "
                       "list of share targets that were offered.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Biome",
        "notes": "In tested data the candidate list contained bundle IDs of apps installed on "
                 "the device; if that holds generally, entries can indicate an app's past "
                 "presence. Field 4 holds an NSKeyedArchiver plist that is not currently "
                 "parsed.",
        "paths": ('*/streams/*/ShareSheet.Feedback/local/*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 17 rows",
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
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'bytes', 'name': ''},
    '5': {'type': 'str', 'name': ''},
    '11': {'type': 'str', 'name': ''},
    '15': {'type': 'str', 'name': ''},
    '16': {'type': 'str', 'name': ''},
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
def get_biomeShareSheetFeedback(context):

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
                    logfunc(f'Share Sheet Feedback: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                candidates = _to_str(protostuff.get('11', b'')).replace(',', ', ')

                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('15', b'')),
                                  _to_str(protostuff.get('16', b'')),
                                  _to_str(protostuff.get('2', b'')),
                                  candidates,
                                  _to_str(protostuff.get('5', b'')),
                                  _to_str(protostuff.get('3', b'')),
                                  protostuff.get('17', ''), protostuff.get('20', ''),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Source App',
                    'Chosen Activity', 'Activity Type', 'Offered Candidates', 'Event UUID',
                    'Session ID', 'Field 17 (raw)', 'Field 20 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
