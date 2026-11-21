__artifacts_v2__ = {
    "get_biomeAppActivity": {
        "name": "Biome - App Activity",
        "description": "Parses app activity records (BMAppActivity) from the App.Activity biome stream: "
                       "bundle id, activity type, item identifiers and related content URL, and an "
                       "activity payload string whose content depends on the app.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "On the tested images the expiration timestamp was 30 days after the SEGB "
                 "timestamp, to within about 7 minutes, on all 1,748 written rows that carried "
                 "one. "
                 "Payload strings are URL-decoded for display. Field names are those of the "
                 "BMAppActivity class, read from BiomeLibrary.framework on macOS 27.2.1 "
                 "(26B131); no iOS copy of the class was read. Columns reported before as "
                 "Activity UUID, Item URI, Session UUID and Status (raw) are now Item "
                 "Identifier, Item Related Unique Identifier, User Activity UUID and Beginning "
                 "Of Activity. Item Related Content URL (field 9) is new and is reported as "
                 "stored. Payload is the field the framework names userActivityRequiredString, "
                 "and Source is sourceID. Beginning Of Activity shows True for 1 and False for "
                 "0; on the tested images it was True on 1,113, False on 635 and absent on 96 "
                 "of the 1,844 written rows, and Item Related Content URL was set on 711 of "
                 "them. Reference: Mattia "
                 "Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html . Content Description is field 4 (contentDescription) of the BMAppActivity class in BiomeLibrary.framework, macOS 27.2.1 (26B131); no iOS copy was read. It was not reported before. On the 21 iOS images tested (9 held written records of this stream) it was non-empty on 183 of 1,844 written rows, on 8 images, with 69 distinct values.",
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
    '4': {'type': 'bytes', 'name': ''},
    '8': {'type': 'str', 'name': ''},
    '9': {'type': 'str', 'name': ''},
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


def _bool(value):
    if value == 1:
        return 'True'
    if value == 0:
        return 'False'
    return ''


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
                beginning = _bool(protostuff.get('3'))
                content_description = _to_str(protostuff.get('4', b''))
                item_identifier = _to_str(protostuff.get('8', b''))
                content_url = _to_str(protostuff.get('9', b''))
                related_unique_id = _to_str(protostuff.get('10', b''))
                payload = unquote(_to_str(protostuff.get('14', b'')))
                activity_uuid = _to_str(protostuff.get('15', b''))
                source = _to_str(protostuff.get('16', b''))

                data_list.append((ts, expiration, record.state.name, bundle_id, activity_type,
                                  content_description,
                                  payload, content_url, related_unique_id, item_identifier,
                                  activity_uuid, source, beginning, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None, None,
                                  None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Expiration Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Activity Type', 'Content Description', 'Payload',
                    'Item Related Content URL', 'Item Related Unique Identifier',
                    'Item Identifier', 'User Activity UUID', 'Source', 'Beginning Of Activity',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
