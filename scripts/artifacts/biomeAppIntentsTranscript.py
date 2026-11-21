__artifacts_v2__ = {
    "get_biomeAppIntentsTranscript": {
        "name": "Biome - App Intents Transcript",
        "description": "Parses records from the App.Intents.Transcript biome stream: a "
                       "bundle identifier, the action identifier, its parameter identifiers "
                       "and the display titles of the parameter values and of the predictions.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-20",
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
                 "Title Bundle URL is the bundleURL of the parameter title (field 4), reported before as App URL; on the tested images it was set on 288 of the 479 written rows, and each held a file URL. Source and Source (raw) are field 2 (source), not reported before: of the 479 written records, on the 12 of 21 tested images that held written records of this stream, 267 read 1 (App), 209 read 0 (Unknown) and 3 read 4 (Shortcuts). Parameter Values is parameters[].value.value (field 5.7.2.2, or 6.7.2.2 when the row reads resolvedAction, NSData), not reported before. It is decoded as a keyed archive and shows a scalar value, or the scalar and URL properties of an entity. List and nested properties and empty values are left out. settingsHostApplicationBundleIdentifier is left out too: it held one value on the 264 tested entities. On the tested images it was filled on 302 of the 479 written rows: 264 with a SettingsNavigationLocationEntity and 38 with scalar values. Across those 264 entities navigationLink held 45 distinct values, while Parameter Display Titles held one and the same text. A value that is not a binary plist is left out (14 of the 349 parameter values on the reported action). A parameter value is what the record holds and does not establish that the action completed. Intent Timestamp is executionDate (field 4), which the class reads as seconds since 1970-01-01 UTC."),
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
from datetime import date, datetime, timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, get_plist_content, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# BMAppIntentInvocation.source names, read from BiomeLibrary.framework on macOS 27.2.1 (26B131).
SOURCES = {0: 'Unknown', 1: 'App', 2: 'CLI', 3: 'Siri', 4: 'Shortcuts', 5: 'Testing',
           6: 'ActionButton', 7: 'Spotlight', 8: 'ControlCenter'}

# A property holding the same value on each tested entity, left out of Parameter Values.
_SKIPPED_ENTITY_PROPERTIES = {'settingsHostApplicationBundleIdentifier'}

_CONTROL_MAP = str.maketrans({'\t': '\\t', '\r': '\\r', '\n': '\\n', '\x00': ''})


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


def _readable(value):
    """Text for a scalar or an NSURL; empty for anything else."""
    if isinstance(value, dict):
        value = value.get('NS.relative')
        return value.translate(_CONTROL_MAP) if isinstance(value, str) else ''
    if isinstance(value, (bool, int, float, datetime, date)):
        return str(value)
    return value.translate(_CONTROL_MAP) if isinstance(value, str) else ''


def _parameter_value(raw):
    """Decode parameters[].value.value (NSData): a keyed archive of a scalar or an LNEntity."""
    if not isinstance(raw, bytes) or not raw.startswith(b'bplist'):
        return ''
    decoded = get_plist_content(raw)
    if not isinstance(decoded, dict):
        return ''
    if 'root' in decoded:
        return _readable(decoded['root'])
    parts = []
    for prop in _as_list(decoded.get('properties')):
        if not isinstance(prop, dict):
            continue
        name = prop.get('identifier')
        holder = prop.get('value')
        if not isinstance(name, str) or name in _SKIPPED_ENTITY_PROPERTIES:
            continue
        text = _readable(holder.get('value')) if isinstance(holder, dict) else ''
        if text:
            parts.append(f'{name}={text}')
    return ', '.join(parts)


def _intent_details(intent):
    """Pull parameter identifiers, entity type identifiers, and the defaultValue and
    bundleURL of each parameter value's displayRepresentation.title out of an action."""
    params, entity_types, titles, urls, values = [], [], [], [], []
    for slot in _as_list(intent.get('7')):
        if not isinstance(slot, dict):
            continue
        name = _to_str(slot.get('1', b''))
        if name:
            params.append(name)
        payload = slot.get('2', {})
        if not isinstance(payload, dict):
            continue
        text = _parameter_value(payload.get('2'))
        if text:
            values.append(f'{name}: {text}' if name else text)
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
    return params, entity_types, titles, urls, values


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

                params, entity_types, titles, urls, values = _intent_details(intent)
                source = protostuff.get('2')
                source_raw = source if type(source) is int else None
                source_name = SOURCES.get(source_raw, '') if source_raw is not None else ''

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
                                  source_name, source_raw,
                                  _to_str(protostuff.get('1', b'')),
                                  _to_str(intent.get('1', b'')),
                                  '; '.join(params), '; '.join(values), '; '.join(entity_types),
                                  '; '.join(titles), '; '.join(prediction_titles),
                                  '; '.join(sorted(set(urls))),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, None,
                                  None, None, None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Intent Timestamp', 'datetime'),
                    'SEGB State', 'Source', 'Source (raw)', 'Bundle ID', 'Intent Class',
                    'Parameters', 'Parameter Values', 'Entity Types',
                    'Parameter Display Titles', 'Prediction Display Titles',
                    'Title Bundle URL', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
