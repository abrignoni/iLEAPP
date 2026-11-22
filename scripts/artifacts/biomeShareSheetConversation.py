__artifacts_v2__ = {
    "get_biomeShareSheetConversation": {
        "name": "Biome - Share Sheet Conversation",
        "description": "Parses share sheet conversation records from the "
                       "MLSE.ShareSheet.ConversationUserInteraction biome stream: the bundle id, "
                       "the conversation identifier (service;-;handle form on the tested Messages "
                       "records, see notes) and the event type.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "On the tested images the conversation identifier had the service;-;handle "
                 "form on all 16 written records, so the handle is split out into its own column while the "
                 "full identifier is retained. Event Type is field 10 (eventType) of the "
                 "BMMLSEConversationUserInteraction class, read from BiomeLibrary.framework on "
                 "macOS 27.2.1 (26B131): 0 Unknown, 1 UserEnteredConversation, 2 "
                 "UserExitedConversation; it was reported raw as Field 10 before. Interaction "
                 "Timestamp is field 11 (timestamp), which the framework decodes as Unix seconds.",
        "paths": ('*/streams/*/MLSE.ShareSheet.ConversationUserInteraction/local/*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "hc_ios26": "26.5.2 | 12 rows (deleted only)",
            "hill_iphone15pro_ios26": "iOS 26 | 227 rows (4 written)",
            "wilkerson_iphone16_ios26": "iOS 26 | 394 rows (12 written)",
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

TYPESS = {'1': {'type': 'str', 'name': ''}, '2': {'type': 'str', 'name': ''},
          '10': {'type': 'int', 'name': ''}}


# eventType names, read from BiomeLibrary.framework BMMLSEConversationUserInteraction on
# macOS 27.2.1 (26B131).
EVENT_TYPES = {0: 'Unknown', 1: 'UserEnteredConversation', 2: 'UserExitedConversation'}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _handle(conversation_id):
    """Conversation ids use the service;-;handle form."""
    return conversation_id.rsplit(';-;', 1)[1] if ';-;' in conversation_id else ''


def _unix_double(value):
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeShareSheetConversation(context):

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
                    logfunc(f'Share Sheet Conversation: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                conversation = _to_str(protostuff.get('2', b''))

                data_list.append((ts, _unix_double(protostuff.get('11')), record.state.name,
                                  _to_str(protostuff.get('1', b'')), _handle(conversation),
                                  conversation, EVENT_TYPES.get(protostuff.get('10'), ''),
                                  protostuff.get('10', ''), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Interaction Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Contact Handle', 'Conversation ID',
                    'Event Type', 'Event Type (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
