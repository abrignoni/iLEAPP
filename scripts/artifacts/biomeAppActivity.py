__artifacts_v2__ = {
    "get_biomeAppActivity": {
        "name": "Biome - App Activity",
        "description": "Parses NSUserActivity records from the App.Activity biome stream: bundle id, "
                       "activity type, linked item URI and an activity payload that can embed content "
                       "such as note titles or map activity details.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "The expiration timestamp was observed to be exactly 30 days after the record "
                 "timestamp. Payload strings are URL-decoded for display. Reference: Mattia "
                 "Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
        "paths": ('*/streams/*/App.Activity/local/*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 1528 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
        },
    }
}


import os
import struct
from datetime import datetime, timezone
from urllib.parse import unquote

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# Pin flat fields so payload/URI strings are never eagerly decoded as nested protobuf.
TYPESS = {
    '1': {'type': 'str', 'name': ''},
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '8': {'type': 'str', 'name': ''},
    '10': {'type': 'str', 'name': ''},
    '14': {'type': 'str', 'name': ''},
    '15': {'type': 'str', 'name': ''},
    '16': {'type': 'str', 'name': ''},
    '17': {'type': 'str', 'name': ''},
    '18': {'type': 'str', 'name': ''},
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
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<q', value))[0] if value > 10 ** 15 else value
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeAppActivity(context):

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
                    logfunc(f'App Activity: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                expiration = _unix_double(protostuff.get('5'))
                bundle_id = _to_str(protostuff.get('1', b''))
                activity_type = _to_str(protostuff.get('2', b''))
                status_raw = protostuff.get('3', '')
                activity_uuid = _to_str(protostuff.get('8', b''))
                item_uri = _to_str(protostuff.get('10', b''))
                payload = unquote(_to_str(protostuff.get('14', b'')))
                session_uuid = _to_str(protostuff.get('15', b''))
                source = _to_str(protostuff.get('16', b''))

                data_list.append((ts, expiration, record.state.name, bundle_id, activity_type,
                                  payload, item_uri, activity_uuid, session_uuid, source,
                                  status_raw, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Expiration Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Activity Type', 'Payload', 'Item URI',
                    'Activity UUID', 'Session UUID', 'Source', 'Status (raw)', 'Filename',
                    'Offset')

    return data_headers, data_list, 'see Filename for more info'
