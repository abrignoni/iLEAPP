__artifacts_v2__ = {
    "get_biomeShareSheetConversation": {
        "name": "Biome - Share Sheet Conversation",
        "description": "Parses share sheet conversation records from the "
                       "MLSE.ShareSheet.ConversationUserInteraction biome stream: the app "
                       "associated with the share and the conversation identifier, which "
                       "carries a contact handle for Messages shares.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The conversation identifier follows the service;-;handle form used elsewhere "
                 "in Messages data, so the handle is split out into its own column while the "
                 "full identifier is retained. Field 10 varied across the sample and is "
                 "reported raw.",
        "paths": ('*/streams/*/MLSE.ShareSheet.ConversationUserInteraction/local/*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "hc_ios26": "26.5.2 | 12 rows",
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
                    logfunc(f'Share Sheet Conversation: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                conversation = _to_str(protostuff.get('2', b''))

                data_list.append((ts, _unix_double(protostuff.get('11')), record.state.name,
                                  _to_str(protostuff.get('1', b'')), _handle(conversation),
                                  conversation, protostuff.get('10', ''), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Interaction Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Contact Handle', 'Conversation ID',
                    'Field 10 (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
