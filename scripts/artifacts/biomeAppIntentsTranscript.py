__artifacts_v2__ = {
    "get_biomeAppIntentsTranscript": {
        "name": "Biome - App Intents Transcript",
        "description": "Parses records from the App.Intents.Transcript biome stream: a "
                       "bundle identifier, the action identifier, its parameter identifiers "
                       "and the display titles of the parameter values and of the predictions.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMAppIntentInvocation class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. Intent Class is the identifier of action (field 5), or of resolvedAction "
                 "(field 6) when the record holds no action. Before, a record with no field 5 was reported with Intent Class, Parameters, Entity Types, the titles and the URL blank: on the tested images 72 of the 479 "
                 "written records held field 6 only, and they now carry it. "
                 "A display title is a StaticDeferredLocalizedString with a key (field 1) and a "
                 "defaultValue (field 2). Parameter Display Titles is the defaultValue of "
                 "parameters[].value.displayRepresentation.title and Prediction Display Titles "
                 "is the defaultValue of predictions[].displayRepresentation.title. They were "
                 "reported before as Entity Titles and Phrase Template, read from the key. On "
                 "the tested images the key and defaultValue held the same text on each of the 312 parameter titles reported (572 counting action and resolvedAction together) and on 264 of 264 prediction titles, so the key is not reported. "
                 "Title Bundle URL is the bundleURL of the parameter title (field 4), reported before as App URL; on the tested images it was set on 288 of the 479 written rows, and each held a file URL. On the tested images 302 of the 479 written records embed an NSKeyedArchiver plist, which this artifact does not read. Intent Timestamp is executionDate (field 4), which the class reads as seconds since 1970-01-01 UTC."),
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


# Field types pinned from BMAppIntentInvocation in BiomeLibrary.framework (macOS 27.2.1, 26B131)
# along the paths read below, so that a string whose bytes happen to parse as protobuf stays a
# string. Unlisted fields decode schema-less.
_STR = {'type': 'bytes', 'name': ''}
_LOCALIZED = {'type': 'message', 'name': '', 'message_typedef': {   # StaticDeferredLocalizedString
    '1': _STR, '2': _STR, '3': _STR, '4': _STR}}                   # key, defaultValue, table, bundleURL
_DISPLAY = {'type': 'message', 'name': '', 'message_typedef': {     # DisplayRepresentation
    '1': _LOCALIZED, '2': _LOCALIZED}}                               # title, subtitle
_VALUE = {'type': 'message', 'name': '', 'message_typedef': {       # BMAppIntentInvocationValue
    '1': {'type': 'message', 'name': '', 'message_typedef': {       # valueType
        '3': {'type': 'message', 'name': '', 'message_typedef': {'1': _STR}}}},   # entity.identifier
    '2': _STR,                                                       # value (NSData)
    '3': _DISPLAY}}                                                  # displayRepresentation
_ACTION = {'type': 'message', 'name': '', 'message_typedef': {      # BMAppIntentInvocationAction
    '1': _STR,                                                       # identifier
    '7': {'type': 'message', 'name': '', 'message_typedef': {       # parameters[]
        '1': _STR, '2': _VALUE}}}}
TYPESS = {
    '1': _STR,                                                       # bundleID
    '5': _ACTION,                                                    # action
    '6': _ACTION,                                                    # resolvedAction
    '8': {'type': 'message', 'name': '', 'message_typedef': {       # predictions[]
        '1': _STR, '2': _DISPLAY}},
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
    """Pull parameter identifiers, entity type identifiers, and the defaultValue and
    bundleURL of each parameter value's displayRepresentation.title out of an action."""
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
                title = _to_str(inner.get('2', b''))   # defaultValue
                if title:
                    titles.append(title)
                url = _to_str(inner.get('4', b''))     # bundleURL
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
                    logfunc(f'App Intents Transcript: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                # action (field 5), or resolvedAction (field 6) when the record holds no action.
                intent = protostuff.get('5')
                if not isinstance(intent, dict):
                    intent = protostuff.get('6', {})
                if not isinstance(intent, dict):
                    intent = {}

                params, entity_types, titles, urls = _intent_details(intent)

                # predictions[].displayRepresentation.title.defaultValue (field 8.2.1.2).
                prediction_titles = []
                for prediction in _as_list(protostuff.get('8')):
                    if not isinstance(prediction, dict):
                        continue
                    display = prediction.get('2', {})
                    if isinstance(display, dict):
                        inner = display.get('1', {})
                        if isinstance(inner, dict):
                            title = _to_str(inner.get('2', b''))
                            if title:
                                prediction_titles.append(title)

                data_list.append((ts, _unix_double(protostuff.get('4')), record.state.name,
                                  _to_str(protostuff.get('1', b'')),
                                  _to_str(intent.get('1', b'')),
                                  '; '.join(params), '; '.join(entity_types),
                                  '; '.join(titles), '; '.join(prediction_titles),
                                  '; '.join(sorted(set(urls))),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Intent Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Intent Class', 'Parameters', 'Entity Types',
                    'Parameter Display Titles', 'Prediction Display Titles',
                    'Title Bundle URL', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
