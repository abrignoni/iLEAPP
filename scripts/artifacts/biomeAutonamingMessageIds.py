__artifacts_v2__ = {
    "get_biomeAutonamingMessageIds": {
        "name": "Biome - Autonaming Message IDs",
        "description": "Parses message references (message identifier, domain and conversation "
                       "identifiers and message date) from the Autonaming.Messages.MessageIds "
                       "biome stream. The purpose of the stream is not established.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names are those of the BMAutonamingMessageIds class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Message ID is field 6 (messageId). It was reported before as Message GUID, "
                 "filled from field 4 (spotlightId) first. Domain ID is field 3 (domainId) and "
                 "Conversation ID is field 7 (conversationId); both were reported before as one "
                 "Chat ID column, filled from field 3 first. On the tested images (9 images, 327 "
                 "written rows) spotlightId and messageId held the same value on every row, so "
                 "Message ID matches the old Message GUID, and Domain ID and Conversation ID "
                 "differ on 20 rows. Is Deletion is field 8 (isDeletion), True for 1 and False "
                 "for 0; it was not reported before. On the tested images it held True on "
                 "72 of the 327 written rows and False on 255. What a deletion record marks is not "
                 "established.",
        "paths": ('*/streams/*/Autonaming.Messages.MessageIds/local/*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 54 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
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

# Pin flat fields so identifier strings are never eagerly decoded as nested protobuf.
# BMAutonamingMessageIds fields, read from BiomeLibrary.framework on macOS 27.2.1 (26B131):
# 2 bundleId, 3 domainId, 4 spotlightId, 6 messageId, 7 conversationId, 8 isDeletion,
# 10 messageTimestamp.
TYPESS = {
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'str', 'name': ''},
    '6': {'type': 'str', 'name': ''},
    '7': {'type': 'str', 'name': ''},
    '8': {'type': 'int', 'name': ''},
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
def get_biomeAutonamingMessageIds(context):

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
                    logfunc(f'Autonaming Message IDs: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                message_ts = _unix_double(protostuff.get('10'))
                bundle_id = _to_str(protostuff.get('2', b''))
                domain_id = _to_str(protostuff.get('3', b''))
                conversation_id = _to_str(protostuff.get('7', b''))
                message_id = _to_str(protostuff.get('6', b''))
                is_deletion = {1: 'True', 0: 'False'}.get(protostuff.get('8'), '')

                data_list.append((ts, message_ts, record.state.name, bundle_id, domain_id,
                                  conversation_id, message_id, is_deletion, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Message Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Domain ID', 'Conversation ID', 'Message ID',
                    'Is Deletion', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
