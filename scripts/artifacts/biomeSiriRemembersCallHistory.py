__artifacts_v2__ = {
    "get_biomeSiriRemembersCallHistory": {
        "name": "Biome - Siri Remembers Call History",
        "description": "Parses call records (timestamps, direction, contacts and handles, conversation "
                       "identifiers) from the Siri.Remembers.CallHistory biome stream. Covers cellular "
                       "and third party VoIP calls (WhatsApp, Messenger, LINE, imo and others observed).",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Direction and call timestamps validated against CallHistory.storedata (ZORIGINATED, "
                 "ZDATE) from the same iOS 17 test extraction (5/5 matches). In this stream direction "
                 "1 = Incoming and 2 = Outgoing, matching the Siri.Remembers.MessageHistory convention.",
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

DIRECTIONS = {0: 'Unspecified', 1: 'Incoming', 2: 'Outgoing'}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


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
        entity = item.get('2', {})
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
        origin = _sync_origin(file_found)

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
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

                data_list.append((ts, call_ts, record.state.name, direction, bundle_id,
                                  params.get('contacts', ''), params.get('contactHandles', ''),
                                  params.get('speakableGroupName', ''), is_group, conversation_id,
                                  call_guid, intent_class, origin, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None, None,
                                  None, None, None, origin, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Call Timestamp', 'datetime'), 'SEGB State',
                    'Direction', 'Bundle ID', 'Contacts', 'Contact Handles', 'Group Name',
                    'Is Group', 'Conversation ID', 'Call GUID', 'Intent Class', 'Sync Origin',
                    'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
