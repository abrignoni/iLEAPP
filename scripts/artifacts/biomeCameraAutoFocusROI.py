__artifacts_v2__ = {
    "get_biomeCameraAutoFocusROI": {
        "name": "Biome - Camera Auto Focus ROI",
        "description": "Parses camera autofocus region of interest events from the "
                       "CameraCapture.AutoFocusROI biome stream. Each record marks camera "
                       "use and which camera port was in use.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Only the camera port (for example PortTypeBack) is self describing. The "
                 "remaining fields are capture parameters whose units the sample data does not "
                 "confirm, so they are reported raw; field 8 is a 32 bit float and is also "
                 "shown decoded.",
        "paths": ('*/streams/*/CameraCapture.AutoFocusROI/local/*',),
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "dexter_ios18": "313 rows",
            "hc_ios18_7": "12 rows",
            "iphone12_ios18": "146 rows",
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
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'int', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '6': {'type': 'int', 'name': ''},
    '7': {'type': 'int', 'name': ''},
    '9': {'type': 'int', 'name': ''},
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


def _float32(value):
    if not isinstance(value, int):
        return ''
    try:
        return round(struct.unpack('<f', struct.pack('<I', value & 0xFFFFFFFF))[0], 3)
    except struct.error:
        return ''


@artifact_processor
def get_biomeCameraAutoFocusROI(context):

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
                    logfunc(f'Camera Auto Focus ROI: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  _float32(protostuff.get('8')),
                                  protostuff.get('2', ''), protostuff.get('3', ''),
                                  protostuff.get('4', ''), protostuff.get('5', ''),
                                  protostuff.get('6', ''), protostuff.get('7', ''),
                                  protostuff.get('9', ''), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Camera Port',
                    'Field 8 (float)', 'Field 2 (raw)', 'Field 3 (raw)', 'Field 4 (raw)',
                    'Field 5 (raw)', 'Field 6 (raw)', 'Field 7 (raw)', 'Field 9 (raw)',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
