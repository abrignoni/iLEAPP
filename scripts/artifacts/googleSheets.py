__artifacts_v2__ = {
    "google_sheets_documents": {
        "name": "Google Sheets - Documents",
        "description": "Spreadsheets the Google Sheets app has opened and kept an offline copy of, "
                       "with the stored title, MIME type, revision, sync timestamps and the cached "
                       "thumbnail where one is present",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Sheets",
        "notes": "One row per row of cross_document_metadata in Documents/<account id>/localStore/shared/documentMetadata.db, joined by document id to the per-document store at localStore/documents/<document id>/<document id>.db. A container can hold more than one account directory, and the same Drive document can appear under each of them, so the join is keyed on the container, the account directory and the document id together and each account's copy is reported as its own row. Rows for the same document under different accounts carry that account's own sync timestamps, revision and ownership; the title is expected to agree between them, because it is one document seen from two accounts. Title, MIME type, revision and ownership come from that store's document_properties table, which is an entity-attribute-value table whose type column selects the encoding of the value blob: in the tested container every type 0 value decoded as UTF-8 text (230 of 230), every type 1 value as an 8-byte little-endian IEEE 754 double (186 of 186) and every type 2 value as JSON (60 of 60). Timestamps are converted by the unit the column name or the store states rather than inferred: last_server_updated_timestamp_milliseconds and the document_properties doubles are Unix milliseconds, drive_last_server_udated_timestamp (spelled that way in the schema) and last_sync_finish_timestamp are Unix seconds. Those two units were checked against each other: cross_document_metadata.last_sync_finish_timestamp in seconds and the per-document lastSyncedTimestamp in milliseconds are held in different stores and rendered the same instant on all 12 documents, so only Last Synced is reported here. Has Pending Changes, Needs Snapshot and All Pending Commands Persisted read the same value on every row of the tested container, which bounds what they demonstrate rather than showing they are the same field. Offline Content Parts and Offline Content Bytes count the rows and total the payload of the document_commands table of that document's own store, which holds the offline copy: cell text, formulas and formatting as JSON arrays of command code and payload. The command codes are undocumented, no value list ships in the container and the sample holds no application binary, so the payload is located and measured here rather than decoded, and an examiner reading it goes to the source database named per row. The highest revision in that table equalled the rev property on all 12 documents tested, so only the property is reported. Owned by Account comes from the document_properties isOwner value, which stores the text true when set and an empty value when not, with the row written either way, so an empty value is reported as No and only a missing property is left blank; on the tested container the two documents storing it empty are the two the Drive item cache in the same container independently records with is_owner 0. Document Type is reported as stored; no value list ships in the container. The Thumbnail column shows the PNG under Documents/drivekit/users/<account id>/thumbnails/<document id>/, which is named <document id>-<milliseconds> and is matched only when those milliseconds equal the row's last_server_updated_timestamp_milliseconds, so the link is the one the store records rather than a nearest match. The main database files carry their content in the WAL sidecar; documentMetadata.db read without it returned no rows at all in the tested container, so the sidecars must travel with the evidence. Files are accepted only from a container that also holds Library/Preferences/com.google.Sheets.plist, because Google Docs and Google Slides ship the same localStore layout and would otherwise be reported here. Validated against a single device, so nothing here is corroborated across devices; a second extraction would establish whether the property names, the type encodings and the thumbnail naming hold across app versions. Reference: Park, Park, Kim, Kang, Kim, 'A comprehensive artifact analysis of Google applications on Android and iOS platforms', Forensic Science International: Digital Investigation. A file is attributed to this app only when its container also holds Library/Preferences/com.google.Sheets.plist, which is declared in this artifact's own paths; the check fails closed, so a collection that captured the stores but not that preferences file reports nothing here, and the skip line in the run log is what distinguishes that from an app whose feature was never used.",
        "paths": ('*/Library/Preferences/com.google.Sheets.plist',
                  '*/Documents/*/localStore/shared/documentMetadata.db*',
                  '*/Documents/*/localStore/documents/*/*.db*',
                  '*/Documents/drivekit/users/*/thumbnails/*/*'),
        "output_types": "standard",
        "artifact_icon": 'grid',
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
        }
    },
    "google_sheets_tabs": {
        "name": "Google Sheets - Sheet Tabs",
        "description": "The individual sheet tabs of each spreadsheet held offline by the Google "
                       "Sheets app, with the stored tab name, tab id and grid size",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Sheets",
        "notes": "One row per sheet tab declared in the top part of the document_commands table of each localStore/documents/<document id>/<document id>.db. Each serialized_commands value is a JSON array of two-element [integer, payload] entries; the integers are undocumented and are reported as stored in the Command Code column rather than named. The payload is written two ways in real data, a positional array whose index is the field number and an object whose keys are those numbers as strings; both are read, and a reader that accepted only the array form reported no tabs at all for a document written the other way while every other artifact reported that same document. A tab is read only from an entry whose payload matches the fixed shape [null, index, n, tab id, {...}, rows, columns], and only that shape is used. The reading is checked against identity the store records elsewhere: the tab id carried in the payload has to equal the chunk<tab id> value of a part_id row in the same database. In the tested container that held for 21 of 21 tabs, and for 12 of 12 documents the set of declared tab ids equalled the set of chunk part ids exactly, with no tab declared that had no chunk and no chunk that had no tab. The Active When Last Viewed column is set from the settingsForSheet:<document id> entry of Library/Preferences/com.google.Sheets.plist, whose recorded tab ids were a subset of the declared tab ids on both documents that carried the preference; it is left empty for documents with no such entry, which is not evidence the tab was not viewed. Row and column counts are the grid extent the store records, not a count of populated cells. Files are accepted only from a container that also holds Library/Preferences/com.google.Sheets.plist. Validated against a single device, so the shape check is not corroborated across devices or app versions. A file is attributed to this app only when its container also holds Library/Preferences/com.google.Sheets.plist, which is declared in this artifact's own paths; the check fails closed, so a collection that captured the stores but not that preferences file reports nothing here, and the skip line in the run log is what distinguishes that from an app whose feature was never used.",
        "paths": ('*/Library/Preferences/com.google.Sheets.plist',
                  '*/Documents/*/localStore/documents/*/*.db*'),
        "output_types": "standard",
        "artifact_icon": 'table',
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
        }
    },
    "google_sheets_templates": {
        "name": "Google Sheets - Template Gallery",
        "description": "One row per account summarising the spreadsheet template gallery the app "
                       "downloaded and cached, with the count and the newest publication date",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Sheets",
        "notes": "One row per templateMetadata.db under Documents/<account id>/localStore/shared/. These are templates the app fetched to populate its gallery, not documents the user created: every row in the tested container carried a thumbnailUrl on a Google host, a server-side category number and a locale, and the locale read en on all 25 rows while the device and the account were set to Italian. They are summarised rather than listed, because a downloaded catalogue enumerated beside an account reads as something the user chose. The underlying store still holds each template's id, title, category, style, branded author and URL, and the cached PNG for each sits under fileStore/globalFiles/templates/thumbnail/ named by the template id, matching 25 of 25 rows with no file left over in the tested container. Newest Template Last Modified is the most recent of a column that mixes units: 23 of the 25 values were Unix milliseconds and 2 were Unix microseconds, and the microsecond reading is the only one of the two in representable range for those 2, so the unit is taken from the magnitude here rather than assumed. Every one of the 25 values fell on exactly 00:00:00 UTC, so the value encodes a calendar date and is also given as a plain date that no later timezone conversion can move. Categories and document types are reported as stored; no value list ships in the container. templateMetadata.db read without its WAL sidecar returned no rows at all. Validated against a single device plus one corpus image. A file is attributed to this app only when its container also holds Library/Preferences/com.google.Sheets.plist, which is declared in this artifact's own paths; the check fails closed, so a collection that captured the stores but not that preferences file reports nothing here, and the skip line in the run log is what distinguishes that from an app whose feature was never used.",
        "paths": ('*/Library/Preferences/com.google.Sheets.plist',
                  '*/Documents/*/localStore/shared/templateMetadata.db*'),
        "output_types": "standard",
        "artifact_icon": 'layout-grid',
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
        }
    },
    "google_sheets_accounts": {
        "name": "Google Sheets - Accounts and App State",
        "description": "Google accounts known to the Google Sheets app and the app state recorded "
                       "beside them, including the signed in account, app version and first launch",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Sheets",
        "notes": "One row per account id found in Library/Preferences/com.google.Sheets.plist. Account ids are read from the preference keys that carry one, and the account named by signed_in_user_id is marked in the Signed In column; the file records account ids only, so no address or display name is available from it. The per-account sync timestamps come from the NSKeyedArchiver archive stored under userid:<account id>, whose date values are Cocoa timestamps counted in seconds from 2001-01-01 UTC as plistlib returns them. Three of those sync fields fell inside the same second in the tested container and so render identically at this resolution; they are separate stored fields and are kept separate. Storage Locale is the value the app recorded for its own messaging cache, not a device setting. Version fields are reported from the two keys that carry one, which held different values in the tested container, so both are shown rather than one being chosen. Absence of a key is reported as empty and is not evidence a feature was unused. Validated against a single device, so the key set is not corroborated across app versions. A file is attributed to this app only when its container also holds Library/Preferences/com.google.Sheets.plist, which is declared in this artifact's own paths; the check fails closed, so a collection that captured the stores but not that preferences file reports nothing here, and the skip line in the run log is what distinguishes that from an app whose feature was never used.",
        "paths": ('*/Library/Preferences/com.google.Sheets.plist',),
        "output_types": "standard",
        "artifact_icon": 'user-circle',
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
        }
    },
    "google_sheets_document_view_state": {
        "name": "Google Sheets - Document View State",
        "description": "The tab, scroll position and zoom the Google Sheets app recorded for each "
                       "spreadsheet it has open state for",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Sheets",
        "notes": "One row per sheet tab recorded under a settingsForSheet:<document id> key of Library/Preferences/com.google.Sheets.plist. The value is an NSKeyedArchiver archive holding kActiveSheetId and a map of tab id to scroll offset and zoom scale; those key names are the app's own and the values are reported as stored. The offsets are the numbers the app recorded, in its own units, and are not converted to a cell reference. In the tested container only 2 of the 12 documents carried this preference, and for both the recorded tab ids were a subset of the tabs declared in that document's own store, so the key is a partial record of documents opened rather than a complete one; absence of a document here is not evidence it was never opened. Validated against a single device. A file is attributed to this app only when its container also holds Library/Preferences/com.google.Sheets.plist, which is declared in this artifact's own paths; the check fails closed, so a collection that captured the stores but not that preferences file reports nothing here, and the skip line in the run log is what distinguishes that from an app whose feature was never used.",
        "paths": ('*/Library/Preferences/com.google.Sheets.plist',),
        "output_types": "standard",
        "artifact_icon": 'eye',
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
        }
    },
    "google_sheets_synced_settings": {
        "name": "Google Sheets - Synced Settings",
        "description": "One row per account recording how many editor settings and fonts the app "
                       "synced, and which setting groups the store holds",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Sheets",
        "notes": "One row per applicationMetadata.db under Documents/<account id>/localStore/shared/, counting the rows of its sync_objects and font_metadata tables and listing the second element of each stored key path. The individual settings are summarised rather than listed: they carry no timestamp, so they cannot be placed in time, and a value that arrived from the server is indistinguishable here from one the user changed, so a row would not be evidence the user set that option. The store still holds every key path and its value and sync state for an examiner who needs them. Key paths are stored as JSON arrays and the group names are reported as stored; they carry a docs- prefix in the Google Sheets container as well, which names the shared editors namespace and not the Google Docs app. Validated against a single device plus one corpus image. A file is attributed to this app only when its container also holds Library/Preferences/com.google.Sheets.plist, which is declared in this artifact's own paths; the check fails closed, so a collection that captured the stores but not that preferences file reports nothing here, and the skip line in the run log is what distinguishes that from an app whose feature was never used.",
        "paths": ('*/Library/Preferences/com.google.Sheets.plist',
                  '*/Documents/*/localStore/shared/applicationMetadata.db*'),
        "output_types": "standard",
        "artifact_icon": 'settings',
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
        }
    },
}

import datetime
import json
import os
import plistlib
import re
import struct

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_sqlite_db_records,
    logfunc,
    null_absent_columns,
)

# The preferences file is the container marker: Google Docs and Google Slides ship the same
# localStore layout, so a file is attributed to Sheets only when it sits under a container
# that also holds this file.
_PREFS_NAME = 'com.google.Sheets.plist'
_PREFS_TAIL = re.compile(r'[/\\]Library[/\\]Preferences[/\\]' + re.escape(_PREFS_NAME) + r'$')

_ACCOUNT_DIR_RE = re.compile(r'[/\\]Documents[/\\]([^/\\]+)[/\\]localStore[/\\]')
_DRIVEKIT_ACCOUNT_RE = re.compile(r'[/\\]drivekit[/\\]users[/\\]([^/\\]+)[/\\]')
_DOC_DB_RE = re.compile(
    r'[/\\]localStore[/\\]documents[/\\]([^/\\]+)[/\\]([^/\\]+)\.db$')
_THUMB_RE = re.compile(
    r'[/\\]drivekit[/\\]users[/\\][^/\\]+[/\\]thumbnails[/\\]([^/\\]+)[/\\]([^/\\]+)$')
_TEMPLATE_THUMB_RE = re.compile(
    r'[/\\]fileStore[/\\]globalFiles[/\\]templates[/\\]thumbnail[/\\]([^/\\]+)$')

# document_properties, template_metadata_properties and their siblings are all
# entity-attribute-value tables sharing one encoding tag. Each name below was confirmed
# against every value of that type in the tested container.
_EAV_TEXT = 0
_EAV_DOUBLE = 1
_EAV_JSON = 2


def _container_roots(files_found):
    '''Container directories that hold the app's own preferences file.

    Anchoring on the container rather than on the store's path is what keeps a sibling
    editor's identically shaped localStore out of this module. The preferences file is
    declared in every artifact's paths, so it arrives through files_found and this needs
    no filesystem probing, which would depend on which artifact ran first.
    '''
    roots = []
    for path in files_found:
        path = str(path)
        match = _PREFS_TAIL.search(path)
        if match:
            roots.append(path[:match.start()])
    # Longest first, so a nested container cannot be attributed to an outer one.
    return sorted(set(roots), key=len, reverse=True)


def _in_container(path, roots):
    return _root_for(path, roots) is not None


def _root_for(path, roots):
    '''The container this path sits under, or None.

    roots is ordered longest first, so a container nested inside another is preferred over
    the outer one. The answer is part of every store key: two containers can hold the same
    account and the same document id.
    '''
    path = str(path)
    for root in roots:
        if path == root or path.startswith(root + os.sep) or path.startswith(root + '/'):
            return root
    return None


def _scoped(files_found, roots, predicate):
    '''Files matching predicate that sit under one of the app's own containers.'''
    kept, dropped = [], 0
    for path in files_found:
        path = str(path)
        if not predicate(path):
            continue
        if _in_container(path, roots):
            kept.append(path)
        else:
            dropped += 1
    if dropped:
        # Say what was excluded, so a reduced count cannot be mistaken for an empty store.
        logfunc(f'Google Sheets: skipped {dropped} file(s) outside a container holding '
                f'{_PREFS_NAME}')
    return kept


def _prefs_files(files_found):
    return [str(f) for f in files_found if _PREFS_TAIL.search(str(f))]


def _doc_dbs(files_found, roots):
    return _scoped(files_found, roots, lambda p: bool(_DOC_DB_RE.search(p)))


def _shared_db(files_found, roots, name):
    return _scoped(
        files_found, roots,
        lambda p: p.replace('\\', '/').endswith(f'/localStore/shared/{name}'))


def _account_from_path(path, pattern=_ACCOUNT_DIR_RE):
    match = pattern.search(str(path))
    return match.group(1) if match else ''


def _text(value):
    if isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', 'replace')
    return '' if value is None else str(value)


def _eav_value(value_type, blob):
    '''Decode one entity-attribute-value payload by the encoding tag stored beside it.'''
    blob = blob if isinstance(blob, (bytes, bytearray)) else (
        b'' if blob is None else str(blob).encode('utf-8', 'replace'))
    if value_type == _EAV_DOUBLE and len(blob) == 8:
        return struct.unpack('<d', bytes(blob))[0]
    if value_type in (_EAV_TEXT, _EAV_JSON):
        return blob.decode('utf-8', 'replace')
    # Any other tag, or a double of the wrong width, is returned as stored rather than
    # dropped, so an unexpected encoding shows up in the report instead of vanishing.
    return blob.decode('utf-8', 'replace') if blob else ''


def _eav_map(db_path, table):
    '''Read one properties table into {record_id: {name: value}}.'''
    out = {}
    query = f'SELECT record_id, name, type, value FROM {table}'
    for record in get_sqlite_db_records(db_path, query):
        out.setdefault(record[0], {})[_text(record[1])] = _eav_value(record[2], record[3])
    return out


def _from_unix(value, divisor):
    '''Render a Unix timestamp whose unit the caller already knows.

    The unit is passed in rather than inferred from magnitude, because two columns of
    cross_document_metadata hold the same instant in different units and a shared guesser
    cannot be told which is which.
    '''
    if value in (None, '', 0, 0.0):
        return ''
    try:
        seconds = float(value) / divisor
    except (TypeError, ValueError):
        return ''
    try:
        return (datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S')
    except (OverflowError, OSError, ValueError):
        return ''


def _from_unix_ms(value):
    return _from_unix(value, 1000.0)


def _from_unix_s(value):
    return _from_unix(value, 1.0)


def _cocoa(value):
    '''Render a Cocoa timestamp (seconds from 2001-01-01 UTC), as plistlib returns them.'''
    if value in (None, '', 0, 0.0):
        return ''
    try:
        return (datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(seconds=float(value))).strftime('%Y-%m-%d %H:%M:%S')
    except (OverflowError, OSError, ValueError, TypeError):
        return ''


def _yes_no(value):
    '''Render a stored flag, keeping absence empty rather than turning it into a No.'''
    if value is None or value == '':
        return ''
    if isinstance(value, str):
        return 'Yes' if value.strip().lower() == 'true' else 'No'
    return 'Yes' if value else 'No'


def _stored_flag(properties, name):
    """Render a document_properties flag, keeping absent and false apart.

    These flags store the text true when set and an empty value when not, and the row is
    written either way, so a missing key and an empty value mean different things. Reading
    an empty value as unknown would hide a negative finding: on the tested container the
    two documents whose isOwner was stored empty are the two the account does not own,
    which the Drive item cache in the same container independently records as is_owner 0.
    """
    if name not in properties:
        return ''
    value = properties[name]
    if isinstance(value, str):
        return 'Yes' if value.strip().lower() == 'true' else 'No'
    return _yes_no(value)


def _number(value):
    '''Render a stored double without a trailing .0 when it is a whole number.'''
    if value in (None, ''):
        return ''
    try:
        number = float(value)
    except (TypeError, ValueError):
        return _text(value)
    return str(int(number)) if number.is_integer() else str(number)


def _load_prefs(path):
    try:
        with open(path, 'rb') as handle:
            return plistlib.load(handle)
    except (OSError, plistlib.InvalidFileException, ValueError) as error:
        logfunc(f'Google Sheets: could not read {os.path.basename(path)}: {error}')
        return {}


def _unarchive(blob):
    '''Resolve an NSKeyedArchiver archive to plain Python containers.'''
    try:
        archive = plistlib.loads(bytes(blob))
    except (plistlib.InvalidFileException, ValueError, TypeError):
        return None
    objects = archive.get('$objects')
    if not isinstance(objects, list):
        return archive

    def resolve(node, depth=0):
        if depth > 12:
            return None
        if isinstance(node, plistlib.UID):
            index = node.data
            if 0 <= index < len(objects):
                return resolve(objects[index], depth + 1)
            return None
        if isinstance(node, dict):
            if 'NS.keys' in node and 'NS.objects' in node:
                return {resolve(k, depth + 1): resolve(v, depth + 1)
                        for k, v in zip(node['NS.keys'], node['NS.objects'])}
            if 'NS.objects' in node:
                return [resolve(v, depth + 1) for v in node['NS.objects']]
            if 'NS.time' in node:
                return node['NS.time']
            return {k: resolve(v, depth + 1) for k, v in node.items() if k != '$class'}
        if isinstance(node, str) and node == '$null':
            return None
        return node

    top = archive.get('$top')
    if isinstance(top, dict) and 'root' in top:
        return resolve(top['root'])
    return resolve(top)


# The tab declaration inside a `top` part. The command code is undocumented, so a payload
# is read only when it matches this exact shape and the id it carries is one the same
# database records as a chunk part.
_TAB_INDEX_INDEX = 1
_TAB_ID_INDEX = 3
_TAB_DETAIL_INDEX = 4
_TAB_ROWS_INDEX = 5
_TAB_COLS_INDEX = 6
_TAB_NAME_INDEX = 3


def _iter_commands(serialized):
    try:
        entries = json.loads(serialized)
    except (TypeError, ValueError):
        return
    if not isinstance(entries, list):
        return
    for entry in entries:
        if isinstance(entry, list) and len(entry) == 2 and isinstance(entry[0], int):
            yield entry[0], entry[1]


def _payload_field(payload, number):
    """One numbered field of a command payload, whichever way it was written.

    These payloads carry the same fields in two spellings: a positional array, where the
    field number is the index, and an object whose keys are those numbers as strings. Both
    appear in real data, chosen per message by the producer, so a reader that tests for a
    list silently returns nothing for every document written the other way.
    """
    if isinstance(payload, list):
        return payload[number] if 0 <= number < len(payload) else None
    if isinstance(payload, dict):
        return payload.get(str(number))
    return None


def _tab_from_payload(payload):
    '''A (tab id, name, rows, columns, index) tuple, or None when the shape does not match.'''
    if not isinstance(payload, (list, dict)):
        return None
    tab_id = _payload_field(payload, _TAB_ID_INDEX)
    detail = _payload_field(payload, _TAB_DETAIL_INDEX)
    rows = _payload_field(payload, _TAB_ROWS_INDEX)
    columns = _payload_field(payload, _TAB_COLS_INDEX)
    if not (isinstance(tab_id, str) and tab_id and isinstance(detail, dict)
            and isinstance(rows, int) and isinstance(columns, int)):
        return None
    inner = detail.get('1')
    if not (isinstance(inner, list) and inner):
        return None
    name = _payload_field(inner[0], _TAB_NAME_INDEX)
    if not isinstance(name, str):
        return None
    index = _payload_field(payload, _TAB_INDEX_INDEX)
    return tab_id, name, rows, columns, index if isinstance(index, int) else ''


def _document_rows(db_path):
    '''The document_properties of a per-document store, keyed by property name.'''
    records = _eav_map(db_path, 'document_properties')
    merged = {}
    for properties in records.values():
        merged.update(properties)
    return merged


@artifact_processor
def google_sheets_documents(context):
    files_found = context.get_files_found()
    roots = _container_roots(files_found)
    data_list = []
    sources = []

    # Both maps are keyed on the full identity of the store: the container, the account
    # directory it sits in, and the document id. A container can hold more than one account
    # directory, and the same Drive document can appear under each of them, so a key of the
    # document id alone keeps only the last copy read and reports its title, MIME type,
    # revision and ownership against every account's row.
    doc_dbs = {}
    for path in _doc_dbs(files_found, roots):
        match = _DOC_DB_RE.search(path)
        if match and match.group(1) == match.group(2):
            doc_dbs[(_root_for(path, roots), _account_from_path(path),
                     match.group(1))] = path

    thumbs = {}
    for path in _scoped(files_found, roots, lambda p: bool(_THUMB_RE.search(p))):
        match = _THUMB_RE.search(path)
        key = (_root_for(path, roots),
               _account_from_path(path, _DRIVEKIT_ACCOUNT_RE), match.group(1))
        thumbs.setdefault(key, []).append((match.group(2), path))

    query = '''
    SELECT document_id, document_type, last_server_updated_timestamp_milliseconds,
           drive_last_server_udated_timestamp, last_sync_finish_timestamp,
           has_pending_changes, is_fast_track, needs_snapshot, sync_failures,
           all_pending_commands_persisted, jobset, resource_key
    FROM cross_document_metadata
    '''
    for db_path in _shared_db(files_found, roots, 'documentMetadata.db'):
        account = _account_from_path(db_path)
        container = _root_for(db_path, roots)
        sources.append(db_path)
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            document_id = _text(record[0])
            properties = {}
            doc_db = doc_dbs.get((container, account, document_id))
            if doc_db:
                properties = _document_rows(doc_db)
                if doc_db not in sources:
                    sources.append(doc_db)

            server_ms = record[2]
            thumbnail = ''
            for name, path in thumbs.get((container, account, document_id), []):
                suffix = name.rsplit('-', 1)[-1]
                # Match only on the milliseconds the metadata row itself records.
                if server_ms is not None and suffix.isdigit() and int(suffix) == int(server_ms):
                    thumbnail = check_in_media(path, name)
                    if path not in sources:
                        sources.append(path)
                    break

            parts = payload_bytes = ''
            if doc_db:
                counted = list(get_sqlite_db_records(
                    doc_db, 'SELECT COUNT(*), SUM(LENGTH(serialized_commands)) '
                            'FROM document_commands'))
                if counted:
                    parts = _number(counted[0][0])
                    payload_bytes = _number(counted[0][1])

            data_list.append((
                _from_unix_ms(server_ms),
                _from_unix_ms(properties.get('lastSyncedTimestamp')),
                _from_unix_ms(properties.get('lastServerSnapshotTimestamp')),
                _from_unix_ms(properties.get('lastColdStartedTimestamp')),
                _from_unix_ms(properties.get('lastWarmStartedTimestamp')),
                _text(properties.get('title', '')),
                document_id,
                _text(record[1]),
                _text(properties.get('mimeType', '')),
                _number(properties.get('rev')),
                parts,
                payload_bytes,
                _stored_flag(properties, 'isOwner'),
                _yes_no(record[5]),
                _yes_no(record[7]),
                _number(record[8]),
                _yes_no(record[6]),
                _yes_no(record[9]),
                _text(record[10]),
                _text(record[11]),
                account,
                thumbnail,
                db_path,
            ))

    data_headers = (
        ('Last Modified on Server', 'datetime'),
        ('Last Synced', 'datetime'),
        ('Last Server Snapshot', 'datetime'),
        ('Last Cold Started', 'datetime'),
        ('Last Warm Started', 'datetime'),
        'Title',
        'Document ID',
        'Document Type (as stored)',
        'MIME Type',
        'Revision',
        'Offline Content Parts',
        'Offline Content Bytes',
        'Owned by Account',
        'Has Pending Changes',
        'Needs Snapshot',
        'Sync Failures',
        'Is Fast Track',
        'All Pending Commands Persisted',
        'Jobset',
        'Resource Key',
        'Account',
        ('Thumbnail', 'media'),
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def google_sheets_tabs(context):
    files_found = context.get_files_found()
    roots = _container_roots(files_found)
    data_list = []
    sources = []

    # Which tab each document had active, from the app's own preferences.
    active_tabs = {}
    for prefs_path in _prefs_files(files_found):
        for key, value in _load_prefs(prefs_path).items():
            if not key.startswith('settingsForSheet:'):
                continue
            settings = _unarchive(value)
            if isinstance(settings, dict):
                active_tabs[key.split(':', 1)[1]] = _text(settings.get('kActiveSheetId', ''))

    for db_path in _doc_dbs(files_found, roots):
        match = _DOC_DB_RE.search(db_path)
        if not match or match.group(1) != match.group(2):
            continue
        document_id = match.group(1)
        account = _account_from_path(db_path)
        properties = _document_rows(db_path)
        title = _text(properties.get('title', ''))

        # The tab ids this database records as content parts. A declared tab is reported
        # only when its id appears here, so the reading rests on recorded identity.
        chunk_ids = set()
        for record in get_sqlite_db_records(
                db_path, "SELECT DISTINCT part_id FROM document_commands "
                         "WHERE part_id LIKE 'chunk%'"):
            chunk_ids.add(_text(record[0])[len('chunk'):])

        seen = set()
        rows_for_db = []
        for record in get_sqlite_db_records(
                db_path, "SELECT part_id, revision, chunk_index, serialized_commands "
                         "FROM document_commands WHERE part_id = 'top' "
                         "ORDER BY revision, chunk_index"):
            for code, payload in _iter_commands(record[3]):
                tab = _tab_from_payload(payload)
                if not tab:
                    continue
                tab_id, name, grid_rows, grid_columns, index = tab
                if tab_id not in chunk_ids or tab_id in seen:
                    continue
                seen.add(tab_id)
                active = active_tabs.get(document_id)
                rows_for_db.append((
                    title,
                    document_id,
                    _number(index),
                    name,
                    tab_id,
                    _number(grid_rows),
                    _number(grid_columns),
                    ('Yes' if active == tab_id else 'No') if active else '',
                    code,
                    account,
                    db_path,
                ))
        if rows_for_db:
            data_list.extend(rows_for_db)
            sources.append(db_path)

    data_headers = (
        'Document Title',
        'Document ID',
        'Tab Index',
        'Tab Name',
        'Tab ID',
        'Grid Rows',
        'Grid Columns',
        'Active When Last Viewed',
        'Command Code (as stored)',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def google_sheets_templates(context):
    files_found = context.get_files_found()
    roots = _container_roots(files_found)
    data_list = []
    sources = []

    for db_path in _shared_db(files_found, roots, 'templateMetadata.db'):
        account = _account_from_path(db_path)
        properties = _eav_map(db_path, 'template_metadata_properties')
        rows = list(get_sqlite_db_records(
            db_path, 'SELECT record_id, template_id FROM template_metadata'))
        if not rows:
            continue
        sources.append(db_path)
        newest = None
        categories, locales, types = set(), set(), set()
        for record in rows:
            fields = properties.get(record[0], {})
            stored = fields.get('lastModifiedTimestamp')
            # One column, two units. The microsecond reading is the only one in
            # representable range for the larger values, so magnitude decides here.
            if isinstance(stored, float):
                seconds = stored / (1_000_000.0 if abs(stored) >= 10 ** 13 else 1000.0)
                newest = seconds if newest is None else max(newest, seconds)
            for value, bucket in ((fields.get('category'), categories),
                                  (fields.get('locale'), locales),
                                  (fields.get('documentType'), types)):
                rendered = _number(value) if isinstance(value, float) else _text(value)
                if rendered:
                    bucket.add(rendered)
        when = _from_unix(newest * 1000.0, 1000.0) if newest is not None else ''
        data_list.append((
            when,
            when.split(' ')[0] if when else '',
            _number(len(rows)),
            ', '.join(sorted(categories)),
            ', '.join(sorted(types)),
            ', '.join(sorted(locales)),
            account,
            db_path,
        ))

    data_headers = (
        ('Newest Template Last Modified', 'datetime'),
        ('Newest Template Date', 'date'),
        'Templates Cached',
        'Categories (as stored)',
        'Document Types (as stored)',
        'Locales',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


_ACCOUNT_KEY_RES = (
    re.compile(r'^userid:(\d+)$'),
    re.compile(r'^GNPRepresentativeTargetIDKey-(\d+)$'),
    re.compile(r'^GNPRenderContextStorage-\w+-(\d+)-\w+$'),
)


@artifact_processor
def google_sheets_accounts(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for prefs_path in _prefs_files(files_found):
        prefs = _load_prefs(prefs_path)
        if not prefs:
            continue
        sources.append(prefs_path)
        signed_in = _text(prefs.get('signed_in_user_id', ''))

        accounts = set()
        for key in prefs:
            for pattern in _ACCOUNT_KEY_RES:
                match = pattern.match(key)
                if match:
                    accounts.add(match.group(1))
        for key, value in prefs.items():
            if key.startswith('shared_container_folder_to_id_') and isinstance(value, str):
                accounts.add(value)
        if signed_in:
            accounts.add(signed_in)
        mdm = prefs.get('MDMACMStorage')
        if isinstance(mdm, dict):
            accounts.update(str(k) for k in mdm)

        cache = prefs.get('GRWMessagingCacheUserDefaultsKey')
        cache = cache if isinstance(cache, dict) else {}

        for account in sorted(accounts):
            state = _unarchive(prefs.get(f'userid:{account}', b'')) or {}
            state = state if isinstance(state, dict) else {}
            data_list.append((
                _cocoa(state.get('lastAutoSyncRunWithSyncHints')),
                _cocoa(state.get('offlineLastBackgroundFetchServerChanges')),
                _cocoa(state.get('offlineLastBackgroundFetchLocalChanges')),
                _cocoa(state.get('offlineMetadataLastUpdated')),
                _cocoa(state.get('lastSyncObjectsSync')),
                _cocoa(state.get('lastTemplatesSync')),
                _text(prefs.get('ASWUniversalMetricsFirstLaunchDateKey', '')),
                account,
                'Yes' if account == signed_in else 'No',
                _text(prefs.get('kSignalCrashStateTrackerVersion', '')),
                _text((prefs.get('kGMResourceLastApplicationVersionKey') or {}).get(
                    'filetypes.json', '')) if isinstance(
                        prefs.get('kGMResourceLastApplicationVersionKey'), dict) else '',
                _text(prefs.get('com.google.sso.GeneratedDeviceIdentifier', '')),
                _text(cache.get('GRWCacheLastSyncLocale', '')),
                _number(prefs.get('numberOfEditorAppsInstalled')),
                _yes_no(state.get('isAutoSyncingDisabled')),
                _yes_no(state.get('areTemplatesAvailable')),
                _yes_no(state.get('createSheetsDisabled')),
                _yes_no(state.get('createDocsDisabled')),
                _yes_no(state.get('createSlidesDisabled')),
                prefs_path,
            ))

    data_headers = (
        ('Last Auto Sync Run', 'datetime'),
        ('Last Background Fetch of Server Changes', 'datetime'),
        ('Last Background Fetch of Local Changes', 'datetime'),
        ('Offline Metadata Last Updated', 'datetime'),
        ('Last Settings Sync', 'datetime'),
        ('Last Templates Sync', 'datetime'),
        ('App First Launch', 'datetime'),
        'Account ID',
        'Signed In',
        'App Version (crash state)',
        'App Version (resources)',
        'Generated Device Identifier',
        'Messaging Cache Locale',
        'Editor Apps Installed',
        'Auto Syncing Disabled',
        'Templates Available',
        'Create Sheets Disabled',
        'Create Docs Disabled',
        'Create Slides Disabled',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def google_sheets_document_view_state(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for prefs_path in _prefs_files(files_found):
        prefs = _load_prefs(prefs_path)
        added = False
        for key, value in prefs.items():
            if not key.startswith('settingsForSheet:'):
                continue
            document_id = key.split(':', 1)[1]
            settings = _unarchive(value)
            if not isinstance(settings, dict):
                continue
            active = _text(settings.get('kActiveSheetId', ''))
            tabs = settings.get('kSheetManagerSettingsKey')
            tabs = tabs if isinstance(tabs, dict) else {}
            for tab_id, state in sorted(tabs.items()):
                state = state if isinstance(state, dict) else {}
                data_list.append((
                    document_id,
                    _text(tab_id),
                    'Yes' if _text(tab_id) == active else 'No',
                    _number(state.get('kScrollOffsetXKey')),
                    _number(state.get('kScrollOffsetYKey')),
                    _number(state.get('kZoomScaleKey')),
                    key,
                    prefs_path,
                ))
                added = True
        if added:
            sources.append(prefs_path)

    data_headers = (
        'Document ID',
        'Tab ID',
        'Active Tab',
        'Scroll Offset X (as stored)',
        'Scroll Offset Y (as stored)',
        'Zoom Scale (as stored)',
        'Preference Key',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def google_sheets_synced_settings(context):
    files_found = context.get_files_found()
    roots = _container_roots(files_found)
    data_list = []
    sources = []

    for db_path in _shared_db(files_found, roots, 'applicationMetadata.db'):
        account = _account_from_path(db_path)
        rows = list(get_sqlite_db_records(db_path, 'SELECT key_path FROM sync_objects'))
        if not rows:
            continue
        sources.append(db_path)
        groups = set()
        for record in rows:
            try:
                parts = json.loads(_text(record[0]))
            except (TypeError, ValueError):
                continue
            if isinstance(parts, list) and len(parts) > 1:
                groups.add(str(parts[1]))
        fonts = list(get_sqlite_db_records(db_path, 'SELECT COUNT(*) FROM font_metadata'))
        data_list.append((
            _number(len(rows)),
            ', '.join(sorted(groups)),
            _number(fonts[0][0]) if fonts else '',
            account,
            db_path,
        ))

    data_headers = (
        'Settings Synced',
        'Setting Groups (as stored)',
        'Fonts Cached',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
