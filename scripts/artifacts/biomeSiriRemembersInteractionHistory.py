__artifacts_v2__ = {
    "get_biomeSiriRemembersInteractionHistory": {
        "name": "Biome - Siri Remembers Interaction History",
        "description": "Parses app interaction intents from the "
                       "Siri.Remembers.InteractionHistory biome stream: note creation, calendar "
                       "event creation, alarm create and update, media playback and similar "
                       "donated intents, with the app that donated them.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Shares the intent record schema of the Siri.Remembers.MessageHistory and "
                 "Siri.Remembers.CallHistory streams. Intent classes observed include "
                 "INCreateNoteIntent, EKUICreateEventIntent, MTCreateAlarmIntent, "
                 "MTUpdateAlarmIntent and INPlayMediaIntent.",
        "paths": (
            '*/streams/*/Siri.Remembers.InteractionHistory/local/*',
            '*/streams/*/Siri.Remembers.InteractionHistory/remote/*',
        ),
        "output_types": "standard",
        "artifact_icon": "zap",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 27 rows",
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
    # Field 8 holds the intent date as a Unix epoch double stored in a fixed64.
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<q', value))[0] if value > 10 ** 15 else value
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _entity_display(entity):
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


def _parameters(protostuff):
    entities = protostuff.get('2', [])
    if isinstance(entities, dict):
        entities = [entities]
    parts = []
    for item in entities:
        if not isinstance(item, dict):
            continue
        param = _to_str(item.get('1', b''))
        entity = item.get('2', {})
        if not isinstance(entity, dict):
            continue
        display = _entity_display(entity)
        if display:
            parts.append(f'{param}: {display}' if param else display)
    return '; '.join(parts)


def _sync_origin(file_found):
    normalized = file_found.replace('\\', '/')
    if '/remote/' in normalized:
        trailer = normalized.split('/remote/', 1)[1]
        if '/' in trailer:
            return f"Remote ({trailer.split('/', 1)[0]})"
        return 'Remote'
    return 'Local'


@artifact_processor
def get_biomeSiriRemembersInteractionHistory(context):

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
        origin = _sync_origin(file_found)

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Siri Remembers Interaction History: could not decode record at '
                            f'offset {record.data_start_offset} in {filename}: {ex}')
                    continue

                metadata = protostuff.get('1', {})
                if not isinstance(metadata, dict):
                    continue

                data_list.append((ts, _intent_timestamp(metadata.get('8')), record.state.name,
                                  _to_str(metadata.get('4', b'')),
                                  _to_str(metadata.get('2', b'')),
                                  _to_str(metadata.get('3', b'')),
                                  _parameters(protostuff),
                                  _to_str(metadata.get('1', b'')),
                                  _to_str(metadata.get('13', b'')), origin, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, origin, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Intent Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Intent Class', 'Domain', 'Parameters',
                    'Intent UUID', 'Item GUID', 'Sync Origin', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
