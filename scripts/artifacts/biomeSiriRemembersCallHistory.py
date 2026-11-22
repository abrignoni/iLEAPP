__artifacts_v2__ = {
    "get_biomeSiriRemembersCallHistory": {
        "name": "Biome - Siri Remembers Call History",
        "description": "Parses call intent records (timestamps, direction, contacts and handles, "
                       "group identifier and app intent interaction identifier) from the "
                       "Siri.Remembers.CallHistory biome stream. On the tested images, records were "
                       "present for com.apple.InCallService and for WhatsApp, Messenger, LINE and "
                       "imo.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMSiriCallHistory class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "Direction and call timestamps were compared with CallHistory.storedata "
                 "(ZORIGINATED, ZDATE) on iphone11_ios17: 5 of 5 records compared matched, and the "
                 "report for that image holds 22 rows. Direction is interaction.direction: 0 "
                 "Unknown, 1 Incoming, 2 Outgoing, 3 Bidirectional (0 was labelled Unspecified "
                 "before); the written records on the tested images held 1 or 2 only, matching the "
                 "Siri.Remembers.MessageHistory convention. App Intent Interaction ID is field 1.13 "
                 "(appIntentInteractionIdentifier), reported before as Call GUID; it held a "
                 "UUID-format string on every tested written record. Group Identifier is field 1.12 "
                 "(groupIdentifier), reported before as Conversation ID, where it showed the text "
                 "{} on 55 of 61 written rows because the field was empty; it is now blank there. "
                 "Group Name was empty on every tested record. Intent Class is field 1.2, which the "
                 "class names type. Each parameter holds a repeated list of entities and every "
                 "entity is reported; no tested Call record held more than one. Status and Status (raw) are field 1.5 (status) of BMSiriRemembersInteraction, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read, and were not reported before. Of the 61 written records, on the 9 of 21 tested images that held written records of this stream, 21 read 1 (Unspecified) and 40 read 4 (Success). On the 23 written records (15 distinct identifiers) whose App Intent Interaction ID equalled the identifier key of an App.Intent record's INInteraction plist on the same image, status 1 sat with intentHandlingStatus 0 (Unspecified) on 3 and status 4 with 3 (Success) on 20. Duration (Seconds) is field 1.9 (durationInSeconds), a double, and was not reported before. It was non-zero on 35 of the 61 written records, from 2 to 155. On the 23 joined records it equalled the App.Intent duration interval with the fraction dropped. 4 of them (2 distinct intervals, each recorded twice) had an interval above 0 and under one second and read 0, and 3 had an interval of 0. A 0 does not establish that a call did not connect. SEGB Timestamp is the record time in the SEGB file; the event time is the second column."),
        "paths": (
            '*/streams/*/Siri.Remembers.CallHistory/local/*',
            '*/streams/*/Siri.Remembers.CallHistory/remote/*',
        ),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 22 rows",
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
# interaction.status names, read from BiomeLibrary.framework on macOS 27.2.1 (26B131).
STATUSES = {0: 'Unknown', 1: 'Unspecified', 2: 'Ready', 3: 'InProgress', 4: 'Success',
            5: 'Failure', 6: 'DeferredToApplication', 7: 'UserConfirmationRequired'}


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


def _status(value):
    # Read schema-less: a pinned field with an unexpected wire type would discard the record.
    if type(value) is not int:
        return '', None
    return STATUSES.get(value, ''), value


def _duration(value):
    # durationInSeconds (field 9) is a double; schema-less decoding returns its 8 bytes as an int.
    if type(value) is not int:
        return None
    seconds = struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]
    return seconds if seconds == seconds and abs(seconds) != float('inf') else None


def _call_timestamp(value):
    # Field 8 holds the call date as a Unix epoch double stored in a fixed64.
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
    # Repeated field 2 items pair a parameter name (contacts, contactHandles,
    # speakableGroupName) with an entity.
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
def get_biomeSiriRemembersCallHistory(context):

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
                    logfunc(f'Siri Remembers Call History: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                metadata = protostuff.get('1', {})
                if not isinstance(metadata, dict):
                    continue

                call_ts = _call_timestamp(metadata.get('8'))
                direction = metadata.get('6')
                direction = DIRECTIONS.get(direction, str(direction) if direction is not None else '')
                status_name, status_raw = _status(metadata.get('5'))
                duration = _duration(metadata.get('9'))
                bundle_id = _to_str(metadata.get('4', b''))
                intent_class = _to_str(metadata.get('2', b''))
                conversation_id = _to_str(metadata.get('12', b''))
                call_guid = _to_str(metadata.get('13', b''))

                is_group = ''
                group_metadata = _to_str(metadata.get('11', b''))
                if group_metadata:
                    try:
                        is_group = str(json.loads(group_metadata).get('isGroup', ''))
                    except (json.JSONDecodeError, AttributeError, TypeError):
                        is_group = ''

                params = _participants(protostuff)

                data_list.append((ts, call_ts, duration, record.state.name, direction, status_name,
                                  status_raw, bundle_id,
                                  params.get('contacts', ''), params.get('contactHandles', ''),
                                  params.get('speakableGroupName', ''), is_group, conversation_id,
                                  call_guid, intent_class, origin, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, record.state.name, None, None, None, None, None,
                                  None, None, None, None, None, None, origin, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Call Timestamp', 'datetime'), 'Duration (Seconds)',
                    'SEGB State', 'Direction', 'Status', 'Status (raw)', 'Bundle ID', 'Contacts', 'Contact Handles', 'Group Name',
                    'Is Group', 'Group Identifier', ('App Intent Interaction ID', 'hash'), 'Intent Class', 'Sync Origin',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
