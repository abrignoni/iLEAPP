__artifacts_v2__ = {
    "get_biomeSiriRemembersMessageHistory": {
        "name": "Biome - Siri Remembers Message History",
        "description": "Parses message intent records (timestamps, participants, group identifier "
                       "and app intent interaction identifier) from the Siri.Remembers.MessageHistory "
                       "biome stream. On the tested images the stream held records for Messages and "
                       "for 17 third party apps. The parser reads no message body field.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMSiriMessageHistory class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "Direction is interaction.direction: 0 Unknown, 1 Incoming, 2 Outgoing, 3 "
                 "Bidirectional (0 was labelled Unspecified before); the written records on the "
                 "tested images held 1 or 2 only. This is inverted from the siriremembers.sqlite3 "
                 "convention. Intent Class is field 1.2, which the class names type; it held an "
                 "IN...Intent class name on every tested written record. Group Identifier is field "
                 "1.12 (groupIdentifier), reported before as Chat ID, and App Intent Interaction ID "
                 "is field 1.13 (appIntentInteractionIdentifier), reported before as Message GUID. "
                 "Each parameter in field 2 holds a repeated list of entities, and every entity is "
                 "now reported: on the tested images 30 written records held a parameter with two "
                 "or three entities, whose extra recipients were left out before. Field types are "
                 "now pinned from the class, so a string is never printed as a decoded message: "
                 "Group Identifier showed the text {} on 4,530 written rows and decoded-message "
                 "text on 132 before. On the tested images no parameter or field key named a "
                 "message body. SEGB Timestamp is the record time in the SEGB file; the event time is the second column."),
        "paths": (
            '*/streams/*/Siri.Remembers.MessageHistory/local/*',
            '*/streams/*/Siri.Remembers.MessageHistory/remote/*',
        ),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 14 rows",
            "iphone11_ios17": "iOS 17.3 | 560 rows",
        },
    }
}


import json
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

# interaction.direction names, read from BiomeLibrary.framework on macOS 27.2.1 (26B131).
DIRECTIONS = {0: 'Unknown', 1: 'Incoming', 2: 'Outgoing', 3: 'Bidirectional'}


# Field types pinned from BiomeLibrary.framework (macOS 27.2.1, 26B131) so that a string
# whose bytes happen to parse as protobuf stays a string. Unlisted fields decode schema-less.
_STR = {'type': 'bytes', 'name': ''}
TYPESS = {
    '1': {'type': 'message', 'name': '', 'message_typedef': {   # interaction
        '1': _STR, '2': _STR, '3': _STR, '4': _STR, '6': {'type': 'int', 'name': ''},
        '8': {'type': 'fixed64', 'name': ''}, '11': _STR, '12': _STR, '13': _STR}},
    '2': {'type': 'message', 'name': '', 'message_typedef': {   # entities[]
        '1': _STR,
        '2': {'type': 'message', 'name': '', 'message_typedef': {   # entities[].entities[]
            '1': _STR, '2': _STR, '4': _STR}}}},
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


def _message_timestamp(value):
    # Field 8 holds the message date as a Unix epoch double stored in a fixed64.
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<q', value))[0] if value > 10 ** 15 else value
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _entity_display(entity):
    # Entity value plus display name from its JSON attributes, when available.
    value = _to_str(entity.get('1', b''))
    name = ''
    attrs = _to_str(entity.get('4', b''))
    if attrs:
        try:
            name = json.loads(attrs).get('name', '')
        except (json.JSONDecodeError, AttributeError, TypeError):
            name = ''
    if name and name != value:
        return f'{value} ({name})' if value else name
    return value


def _participants(protostuff):
    # Repeated field 2 items pair a parameter name (sender, senderHandle, recipients,
    # recipientHandles, speakableGroupName, sentMessages) with an entity.
    params = {}
    entities = protostuff.get('2', [])
    if isinstance(entities, dict):
        entities = [entities]
    for item in entities:
        if not isinstance(item, dict):
            continue
        param = _to_str(item.get('1', b''))
        inner = item.get('2', [])
        # entities[].entities[] is repeated in BMSiriRemembersEntities; keep every entry.
        for entity in inner if isinstance(inner, list) else [inner]:
            if not isinstance(entity, dict):
                continue
            display = _entity_display(entity)
            if display:
                params.setdefault(param, []).append(display)
    return {key: '; '.join(values) for key, values in params.items()}


def _sync_origin(file_found):
    normalized = file_found.replace('\\', '/')
    if '/remote/' in normalized:
        trailer = normalized.split('/remote/', 1)[1]
        if '/' in trailer:
            return f"Remote ({trailer.split('/', 1)[0]})"
        return 'Remote'
    return 'Local'


@artifact_processor
def get_biomeSiriRemembersMessageHistory(context):

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
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Siri Remembers Message History: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                metadata = protostuff.get('1', {})
                if not isinstance(metadata, dict):
                    continue

                message_ts = _message_timestamp(metadata.get('8'))
                direction = metadata.get('6')
                direction = DIRECTIONS.get(direction, str(direction) if direction is not None else '')
                bundle_id = _to_str(metadata.get('4', b''))
                intent_class = _to_str(metadata.get('2', b''))
                chat_id = _to_str(metadata.get('12', b''))
                message_guid = _to_str(metadata.get('13', b''))

                is_group = ''
                group_metadata = _to_str(metadata.get('11', b''))
                if group_metadata:
                    try:
                        is_group = str(json.loads(group_metadata).get('isGroup', ''))
                    except (json.JSONDecodeError, AttributeError, TypeError):
                        is_group = ''

                params = _participants(protostuff)

                data_list.append((ts, message_ts, record.state.name, direction, bundle_id,
                                  params.get('sender', ''), params.get('senderHandle', ''),
                                  params.get('recipients', ''), params.get('recipientHandles', ''),
                                  params.get('speakableGroupName', ''), is_group, chat_id,
                                  message_guid, intent_class, origin, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None,
                                  None, None, None, None, None, origin, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Message Timestamp', 'datetime'), 'SEGB State',
                    'Direction', 'Bundle ID', 'Sender', 'Sender Handle', 'Recipients',
                    'Recipient Handles', 'Group Name', 'Is Group', 'Group Identifier', 'App Intent Interaction ID',
                    'Intent Class', 'Sync Origin', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
