__artifacts_v2__ = {
    "biomeSetsPhoneIndexedCalls": {
        "name": "Biome Sets - Phone Indexed Calls",
        "description": ("Entities stored under the com.apple.mobilephone source of the "
                        "App.Intents.IndexedEntity Biome set, with a column saying whether each one's "
                        "identifier matches a ZCALLRECORD.ZUNIQUE_ID in CallHistory.storedata."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "liblzfse",
        "category": "Biome",
        "notes": ("Reads Set.db of the App.Intents.IndexedEntity Biome set for com.apple.mobilephone. On "
                  "the tested store every content blob was one byte followed by an LZFSE stream, which is "
                  "decompressed with liblzfse and decoded as protobuf; a blob without the LZFSE marker is "
                  "decoded as plain protobuf. Field numbers come from the CascadeSets.framework classes "
                  "CCAppIntentsIndexedEntityContent, CCAppIntentsIndexedEntityMetaContent, "
                  "CCAppEntityDisplayRepresentation, CCSpotlightDefinedAttributes, "
                  "CCSpotlightDocumentAttributes and CCSpotlightMediaAttributes on macOS 27.2.1 (26B131): "
                  "planted values serialized with the classes' initializers gave contentCreationDate as "
                  "media field 2, lastUsedDate as 8, participants as 9 and the metacontent "
                  "sourceItemIdentifier as field 1, and the properties the classes decoded from the "
                  "tested records matched the type identifier (field 1), the displayRepresentation title "
                  "(field 2.1) and the document contentDescription (field 5.2.2). No iOS copy of the "
                  "classes was read. Entity Type is the type identifier as stored. Content Creation Date "
                  "is the media contentCreationDate, stored as seconds since 1970 (a planted date 1000 "
                  "seconds after 1970 serialized as 1000.0); the report shows it in whole seconds. On "
                  "every tested row with In Call History Yes it was within 1 second of that record's "
                  "ZDATE. lastUsedDate held the same value as contentCreationDate on every tested record "
                  "and is not shown. Title is the displayRepresentation title and Participants the media "
                  "participants. Call Type, Call Status, Localised Call Status, Provider, SIM and Callback "
                  "URL are the entity's own named properties (com_apple_mobilephone_callType and so on), "
                  "shown as stored; only string values with a single value are read, and "
                  "index_ranking_date, a numeric property, is not shown. Source Item Identifier is the "
                  "metacontent sourceItemIdentifier (field 1); the instanceIdentifier (field 6) held the "
                  "same value on every tested record. In Call History is Yes when the Source Item "
                  "Identifier equals, ignoring letter case, a ZCALLRECORD.ZUNIQUE_ID in "
                  "CallHistory.storedata, No when it does not, and Not checked when no "
                  "CallHistory.storedata with a ZCALLRECORD table was found (not exercised on the tested "
                  "data). No means no ZCALLRECORD row in that file has the identifier; it does not show "
                  "why. Written Date is metacontent_provenance.written_date, read as Unix microseconds by "
                  "magnitude (16-digit integers on the tested store), the same way biomeSetsStores reads "
                  "it; the unit was not sourced from Apple code. It was later than Content Creation Date "
                  "on every tested row and many rows shared one value: it is when the row was written to "
                  "the set, not when the call happened. Rows with a non-zero "
                  "metacontent_provenance.deleted_run_length are skipped; no tested entity was affected, "
                  "so this is not exercised. The set was absent from the tested iOS 26.5.2 image. Other "
                  "sources of the same set are not read by this artifact. Field mapped from a private "
                  "sample."),
        "paths": ('*/[Bb]iome/sets/Default/App.Intents.IndexedEntity/sourceIdentifier=com.apple.mobilephone/'
                  'Database/Set.db*',
                  '*/CallHistoryDB/CallHistory.storedata*'),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    }
}


import struct

import liblzfse
from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records,
                               does_table_exist_in_db, logfunc)

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
_LZFSE_ERRORS = (ValueError, getattr(liblzfse, 'error', ValueError))

# Field numbers read by serializing planted values with the CascadeSets.framework classes
# CCAppIntentsIndexedEntityContent, CCSpotlightDefinedAttributes and CCSpotlightMediaAttributes
# on macOS 27.2.1 (26B131), and by matching their decoded properties to the raw fields.
CONTENT_TYPES = {
    '1': {'type': 'str', 'name': ''},                       # typeIdentifier
    '2': {'type': 'message', 'name': '', 'message_typedef': {  # displayRepresentation
        '1': {'type': 'str', 'name': ''}}},                 # title
    '5': {'type': 'message', 'name': '', 'message_typedef': {  # definedAttributes
        '2': {'type': 'message', 'name': '', 'message_typedef': {   # document
            '2': {'type': 'str', 'name': ''}}},             # contentDescription
        '7': {'type': 'message', 'name': '', 'message_typedef': {   # media
            '2': {'type': 'double', 'name': ''},            # contentCreationDate
            '8': {'type': 'double', 'name': ''},            # lastUsedDate
            '9': {'type': 'str', 'name': ''}}}}},           # participants
    '6': {'type': 'message', 'name': '', 'message_typedef': {  # custom attributes
        '2': {'type': 'message', 'name': '', 'message_typedef': {
            '1': {'type': 'str', 'name': ''},
            '3': {'type': 'double', 'name': ''}}},
        '3': {'type': 'str', 'name': ''}}},
}
META_TYPES = {'1': {'type': 'str', 'name': ''}}              # sourceItemIdentifier

PROPERTIES = ('com_apple_mobilephone_callType', 'com_apple_mobilephone_callStatus',
              'com_apple_mobilephone_localisedCallStatus', 'com_apple_mobilephone_provider',
              'com_apple_mobilephone_SIM', 'com_apple_mobilephone_callbackURL')


def _list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None else str(value)


def _content_message(blob):
    """The entity protobuf. The tested store held it as one byte then an LZFSE stream ('bvx')."""
    data = bytes(blob)
    if len(data) > 4 and data[1:4] == b'bvx':
        data = liblzfse.decompress(data[1:])  # pylint: disable=c-extension-no-member
    message, _ = blackboxprotobuf.decode_message(data, CONTENT_TYPES)
    return message


def _call_history_ids(files_found):
    ids, found = set(), False
    for file_found in files_found:
        if not file_found.endswith('CallHistory.storedata'):
            continue
        if not does_table_exist_in_db(file_found, 'ZCALLRECORD'):
            continue
        found = True
        for record in get_sqlite_db_records(file_found, 'SELECT ZUNIQUE_ID FROM ZCALLRECORD'):
            if record[0]:
                ids.add(str(record[0]).upper())
    return ids if found else None


@artifact_processor
def biomeSetsPhoneIndexedCalls(context):
    files_found = [str(f) for f in context.get_files_found()]
    history = _call_history_ids(files_found)
    data_list = []
    source_paths = []
    for file_found in files_found:
        if not file_found.endswith('Set.db'):
            continue
        if not does_table_exist_in_db(file_found, 'metacontent_provenance'):
            logfunc(f'Phone Indexed Calls: no metacontent_provenance table in {file_found}')
            continue
        source_paths.append(file_found)
        query = '''
            SELECT p.written_date, m.metacontent, c.content
            FROM metacontent_provenance p
            JOIN metacontent m ON m.instance_hash = p.instance_hash
            LEFT JOIN content c ON c.content_hash = p.content_hash
            WHERE p.deleted_run_length = 0
        '''
        for written, meta_blob, content_blob in get_sqlite_db_records(file_found, query):
            try:
                meta, _ = blackboxprotobuf.decode_message(bytes(meta_blob), META_TYPES)
            except _DECODE_ERRORS as ex:
                logfunc(f'Phone Indexed Calls: could not decode a metacontent record in {file_found}: {ex}')
                continue
            source_item_id = _text(meta.get('1'))
            content = {}
            if content_blob is not None:
                try:
                    content = _content_message(content_blob)
                except _DECODE_ERRORS + _LZFSE_ERRORS as ex:
                    logfunc(f'Phone Indexed Calls: could not decode the content of {source_item_id} '
                            f'in {file_found}: {ex}')
            defined = content.get('5', {}) if isinstance(content.get('5'), dict) else {}
            media = defined.get('7', {}) if isinstance(defined.get('7'), dict) else {}
            document = defined.get('2', {}) if isinstance(defined.get('2'), dict) else {}
            title = content.get('2', {}).get('1') if isinstance(content.get('2'), dict) else None
            props = {}
            for item in _list(content.get('6')):
                if isinstance(item, dict) and isinstance(item.get('2'), dict):
                    props[_text(item.get('3'))] = item['2'].get('1')
            created = media.get('2')
            if history is None:
                in_history = 'Not checked (no CallHistory.storedata with ZCALLRECORD)'
            else:
                in_history = 'Yes' if source_item_id.upper() in history else 'No'
            data_list.append((
                convert_unix_ts_to_utc(created) if isinstance(created, float) else None,
                convert_unix_ts_to_utc(written) if written else None,
                _text(content.get('1')), _text(title),
                ', '.join(_text(p) for p in _list(media.get('9'))),
                _text(document.get('2')),
                *(_text(props.get(name)) for name in PROPERTIES),
                in_history, source_item_id))

    data_headers = (('Content Creation Date', 'datetime'), ('Written Date', 'datetime'), 'Entity Type',
                    'Title', 'Participants', 'Content Description', 'Call Type', 'Call Status',
                    'Localised Call Status', 'Provider', 'SIM', 'Callback URL', 'In Call History',
                    'Source Item Identifier')
    data_list.sort(key=lambda row: (row[0] is None, row[0] or row[1]))
    return data_headers, data_list, '\n'.join(source_paths)
