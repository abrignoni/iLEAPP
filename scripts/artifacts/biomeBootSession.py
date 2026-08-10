__artifacts_v2__ = {
    "get_biomeBootSession": {
        "name": "Biome - Boot Session",
        "description": "Parses boot session records from the Device.BootSession biome stream. "
                       "Each boot closes the previous session identifier and opens a new one, "
                       "so the stream reconstructs when the device started and stopped running "
                       "and, where a close and the following open are separated in time, a "
                       "gap consistent with the device being powered off.",
        "author": "@abrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "Session state 1 is the opening of a session and 0 its close, established by "
                 "the record pattern across four test images: a close and an open share a "
                 "timestamp at a reboot, and each session identifier appears exactly twice, "
                 "once opened and once closed. A close with no open at the same instant marks "
                 "a shutdown, and the gap to the next open is consistent with the device "
                 "being powered off during that period. "
                 "Sort by timestamp and pair on Session ID to measure uptime.",
        "paths": ('*/streams/*/Device.BootSession/local/*',),
        "output_types": "standard",
        "artifact_icon": "power",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 43 rows",
            "hc_ios18_7": "iOS 18.7.8 | 134 rows",
            "iphone12_ios18": "iOS 18.7 | 13 rows",
            "iphone14plus_ios18": "iOS 18.0 | 11 rows",
        },
    }
}


import os
import struct
import uuid
from datetime import timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

TYPESS = {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''}}

SESSION_STATE = {0: 'Session End', 1: 'Session Start'}


def _session_id(value):
    """Field 1 is a raw 16 byte UUID."""
    if isinstance(value, bytes) and len(value) == 16:
        try:
            return str(uuid.UUID(bytes=value))
        except ValueError:
            return value.hex()
    if isinstance(value, bytes):
        return value.hex()
    return '' if value is None else str(value)


@artifact_processor
def get_biomeBootSession(context):

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
                    logfunc(f'Boot Session: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                raw_state = protostuff.get('2', '')
                data_list.append((ts, record.state.name, SESSION_STATE.get(raw_state, ''),
                                  raw_state, _session_id(protostuff.get('1')), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Session State',
                    'Session State (raw)', 'Session ID', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
