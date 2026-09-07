__artifacts_v2__ = {
    "get_biomeAppIntentsTranscript": {
        "name": "Biome - App Intents Transcript",
        "description": "Parses donated App Intents from the App.Intents.Transcript biome "
                       "stream: the donating app, the intent class, the intent parameter and "
                       "the human readable entity title associated with the intent (for "
                       "example a Settings destination or a Focus filter target).",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Each record also embeds an NSKeyedArchiver plist holding the full entity "
                 "payload; that blob is not currently parsed.",
        "paths": ('*/streams/*/App.Intents.Transcript/local/*',),
        "output_types": "standard",
        "artifact_icon": "bolt",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 41 rows",
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


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _unix_double(value):
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<q', value))[0] if value > 10 ** 15 else value
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


def _intent_details(intent):
    """Pull parameter names, entity types and display titles out of an intent message."""
    params, entity_types, titles, urls = [], [], [], []
    for slot in _as_list(intent.get('7')):
        if not isinstance(slot, dict):
            continue
        name = _to_str(slot.get('1', b''))
        if name:
            params.append(name)
        payload = slot.get('2', {})
        if not isinstance(payload, dict):
            continue
        descriptor = payload.get('1', {})
        if isinstance(descriptor, dict):
            type_info = descriptor.get('3', {})
            if isinstance(type_info, dict):
                entity_type = _to_str(type_info.get('1', b''))
                if entity_type:
                    entity_types.append(entity_type)
        display = payload.get('3', {})
        if isinstance(display, dict):
            inner = display.get('1', {})
            if isinstance(inner, dict):
                title = _to_str(inner.get('1', b''))
                if title:
                    titles.append(title)
                url = _to_str(inner.get('4', b''))
                if url:
                    urls.append(url)
    return params, entity_types, titles, urls


@artifact_processor
def get_biomeAppIntentsTranscript(context):

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
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'App Intents Transcript: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                intent = protostuff.get('5', {})
                if not isinstance(intent, dict):
                    intent = protostuff.get('6', {})
                if not isinstance(intent, dict):
                    intent = {}

                params, entity_types, titles, urls = _intent_details(intent)

                # Field 8 carries the phrase template shown for the intent.
                template = ''
                phrase = protostuff.get('8', {})
                if isinstance(phrase, dict):
                    display = phrase.get('2', {})
                    if isinstance(display, dict):
                        inner = display.get('1', {})
                        if isinstance(inner, dict):
                            template = _to_str(inner.get('1', b''))

                data_list.append((ts, _unix_double(protostuff.get('4')), record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  _to_str(intent.get('1', b'')),
                                  '; '.join(params), '; '.join(entity_types),
                                  '; '.join(titles), template, '; '.join(sorted(set(urls))),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Intent Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Intent Class', 'Parameters', 'Entity Types',
                    'Entity Titles', 'Phrase Template', 'App URL', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
