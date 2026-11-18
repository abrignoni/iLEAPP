__artifacts_v2__ = {
    "get_biomeSiriRemembersAssistantSuggestions": {
        "name": "Biome - Siri Remembers Assistant Suggestions",
        "description": "Parses suggestion events recorded in the "
                       "Siri.Remembers.AssistantSuggestions biome stream, with the suggestion names carried in each record, joined with '; '.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("The record has the interaction and entities fields that the Siri.Remembers AudioHistory, CallHistory, InteractionHistory and MessageHistory classes also have. "
                 "Field types are those of the BMSiriAssistantSuggestions class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Suggestions and Suggestion Types are the identifier and type of each "
                 "entity in entities[].entities[], a repeated list. Each non-empty identifier is reported, and each distinct type is reported once per record. The string fields are now pinned as strings so they are not decoded as nested messages. Before, the record "
                 "was decoded without a schema, and on the tested images 3 entities on 3 written "
                 "records of hill_iphone15pro_ios26 were left out of Suggestions (25 names "
                 "reported before, 28 now, over 13 written records). "
                 "Records are read from both the local and remote subfolders; the Sync Origin "
                 "column reports which one a record came from. On the tested images Sync Origin read Local on 12 of the 13 written records and Remote on 1 (felix_ios17). The local/remote naming is the "
                 "stream's own folder layout; cross-device sync semantics are not documented."),
        "paths": (
            '*/streams/*/Siri.Remembers.AssistantSuggestions/local/*',
            '*/streams/*/Siri.Remembers.AssistantSuggestions/remote/*',
        ),
        "output_types": "standard",
        "artifact_icon": "zap",
        "sample_data": {
            "felix_ios17": "1 row",
            "otto_ios17": "2 rows",
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


# Field types pinned from BMSiriAssistantSuggestions in BiomeLibrary.framework (macOS 27.2.1,
# 26B131) so that a string whose bytes happen to parse as protobuf stays a string.
# Unlisted fields decode schema-less.
_STR = {'type': 'bytes', 'name': ''}
TYPESS = {
    '1': {'type': 'message', 'name': '', 'message_typedef': {   # interaction
        '1': _STR, '2': _STR, '3': _STR, '4': _STR, '8': {'type': 'fixed64', 'name': ''},
        '11': _STR, '12': _STR, '13': _STR}},
    '2': {'type': 'message', 'name': '', 'message_typedef': {   # entities[]
        '1': _STR,
        '2': {'type': 'message', 'name': '', 'message_typedef': {   # entities[].entities[]
            '1': _STR, '2': _STR, '4': _STR, '5': _STR}}}},
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


def _intent_timestamp(value):
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _as_list(value):
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return value
    return []


def _suggestions(protostuff):
    """Suggestion names sit in entities[].entities[] (identifier and type); every inner
    entity of every parameter is kept."""
    names, kinds = [], []
    for slot in _as_list(protostuff.get('2')):
        if not isinstance(slot, dict):
            continue
        for entity in _as_list(slot.get('2')):
            if not isinstance(entity, dict):
                continue
            name = _to_str(entity.get('1'))
            kind = _to_str(entity.get('2'))
            if name:
                names.append(name)
            if kind and kind not in kinds:
                kinds.append(kind)
    return '; '.join(names), '; '.join(kinds)


def _sync_origin(file_found):
    normalized = file_found.replace('\\', '/')
    if '/remote/' in normalized:
        trailer = normalized.split('/remote/', 1)[1]
        if '/' in trailer:
            return f"Remote ({trailer.split('/', 1)[0]})"
        return 'Remote'
    return 'Local'


@artifact_processor
def get_biomeSiriRemembersAssistantSuggestions(context):

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
        origin = _sync_origin(context.get_relative_path(file_found))

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Siri Remembers Assistant Suggestions: could not decode record '
                            f'at offset {record.data_start_offset} in {filename}: {ex}')
                    continue

                metadata = protostuff.get('1', {})
                if not isinstance(metadata, dict):
                    continue
                names, kinds = _suggestions(protostuff)

                data_list.append((ts, _intent_timestamp(metadata.get('8')), record.state.name,
                                  names, kinds, _to_str(metadata.get('4')),
                                  _to_str(metadata.get('2')), _to_str(metadata.get('11')),
                                  _to_str(metadata.get('1')), origin, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, origin, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Suggestion Timestamp', 'datetime'),
                    'SEGB State', 'Suggestions', 'Suggestion Types', 'Bundle ID',
                    'Intent Class', 'Metadata', 'Event ID', 'Sync Origin', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
