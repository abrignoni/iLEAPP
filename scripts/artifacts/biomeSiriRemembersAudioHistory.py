__artifacts_v2__ = {
    "get_biomeSiriRemembersAudioHistory": {
        "name": "Biome - Siri Remembers Audio History",
        "description": "Parses media playback intents from the Siri.Remembers.AudioHistory "
                       "biome stream: the app that played the media, the title, artist and "
                       "media type of what was played, and the item entity's identifier. "
                       "Music and podcast playback were both observed on the tested images.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMSiriAudioHistory class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "Shares the interaction and entities record shape of the MessageHistory, "
                 "CallHistory, InteractionHistory and AssistantSuggestions streams. The media "
                 "details come from a JSON attribute on the item entity. Title and media type were "
                 "present on every tested written record; Artist was present on 74 of 111. Item ID "
                 "is the identifier of the items entity (type MediaItem). Group Identifier is field "
                 "1.12 (groupIdentifier), reported before as Media ID; what it identifies is not "
                 "established. Both are shown as decoded text. Playback Timestamp is field 1.8, "
                 "which the class names startDate, and Intent UUID is field 1.1, which the class "
                 "names identifier. Intent Class is field 1.2, which the class names type. Records "
                 "are read from both the local and remote subfolders; the Sync Origin column "
                 "reports which one a record came from. The local and remote names are the "
                 "stream's own folder layout; what they mean for cross-device sync is not "
                 "established here. Status and Status (raw) are field 1.5 (status) of BMSiriRemembersInteraction, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read, and were not reported before. Of the 111 written records, on the 3 of 21 tested images that held written records of this stream, 92 read 1 (Unspecified) and 19 read 4 (Success). On the 15 written records whose field 1.13 (appIntentInteractionIdentifier, not shown by this artifact) equalled the identifier key of an App.Intent record's INInteraction plist on the same image, status 1 sat with intentHandlingStatus 0 (Unspecified) on 12 and status 4 with 3 (Success) on 3. Donated by Siri is field 1.7 (isDonatedBySiri), not reported before; it read True on 10 of the 111 written records and False on 101. SEGB Timestamp is the record time in the SEGB file; the event time is the second column."),
        "paths": (
            '*/streams/*/Siri.Remembers.AudioHistory/local/*',
            '*/streams/*/Siri.Remembers.AudioHistory/remote/*',
        ),
        "output_types": "standard",
        "artifact_icon": "headphones",
        "sample_data": {
            "dexter_ios18": "73 rows",
            "otto_ios17": "1 row",
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

# interaction.status names, read from BiomeLibrary.framework on macOS 27.2.1 (26B131).
STATUSES = {0: 'Unknown', 1: 'Unspecified', 2: 'Ready', 3: 'InProgress', 4: 'Success',
            5: 'Failure', 6: 'DeferredToApplication', 7: 'UserConfirmationRequired'}


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


def _donated_by_siri(value):
    # isDonatedBySiri (field 1.7), a Boolean stored as a varint.
    if type(value) is not int:
        return ''
    return {0: 'False', 1: 'True'}.get(value, str(value))


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


def _media_details(protostuff):
    """Media metadata rides as a JSON attribute on the item entity."""
    titles, artists, kinds, item_ids = [], [], [], []
    for slot in _as_list(protostuff.get('2')):
        if not isinstance(slot, dict):
            continue
        for entity in _as_list(slot.get('2')):
            if not isinstance(entity, dict):
                continue
            item_id = _to_str(entity.get('1'))
            if item_id:
                item_ids.append(item_id)
            try:
                attrs = json.loads(_to_str(entity.get('4')) or '{}')
            except (json.JSONDecodeError, TypeError):
                continue
            if not isinstance(attrs, dict):
                continue
            title = attrs.get('title') or attrs.get('mediaName')
            if title:
                titles.append(str(title))
            if attrs.get('artist'):
                artists.append(str(attrs['artist']))
            if attrs.get('mediaType'):
                kinds.append(str(attrs['mediaType']))
    return ('; '.join(titles), '; '.join(artists), '; '.join(kinds), '; '.join(item_ids))


def _sync_origin(file_found):
    normalized = file_found.replace('\\', '/')
    if '/remote/' in normalized:
        trailer = normalized.split('/remote/', 1)[1]
        if '/' in trailer:
            return f"Remote ({trailer.split('/', 1)[0]})"
        return 'Remote'
    return 'Local'


@artifact_processor
def get_biomeSiriRemembersAudioHistory(context):

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
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Siri Remembers Audio History: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                metadata = protostuff.get('1', {})
                if not isinstance(metadata, dict):
                    continue
                title, artist, media_type, item_ids = _media_details(protostuff)
                status_name, status_raw = _status(metadata.get('5'))

                data_list.append((ts, _intent_timestamp(metadata.get('8')), record.state.name,
                                  status_name, status_raw,
                                  _donated_by_siri(metadata.get('7')), title, artist, media_type,
                                  _to_str(metadata.get('4')), _to_str(metadata.get('12')),
                                  item_ids, _to_str(metadata.get('2')),
                                  _to_str(metadata.get('1')), origin, filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, None, None, None, None, None, origin, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Playback Timestamp', 'datetime'),
                    'SEGB State', 'Status', 'Status (raw)', 'Donated by Siri', 'Title', 'Artist', 'Media Type', 'Bundle ID', 'Group Identifier',
                    'Item ID', 'Intent Class', 'Intent UUID', 'Sync Origin', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
