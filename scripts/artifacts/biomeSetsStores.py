__artifacts_v2__ = {
    "biomeSetsInstalledApps": {
        "name": "Biome Sets - Installed Apps",
        "description": "Installed application records (bundle ID and display name) from the App.InstalledApp "
                       "Biome Set.db store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Modified timestamps come from the store's instance table.",
        "paths": ('*/Biome/sets/Default/App.InstalledApp/Database/Set.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 95 rows",
            "hc_ios18_7": "iOS 18.7.8 | 76 rows",
            "iphone12_ios18": "iOS 18.7 | 91 rows",
        },
    },
    "biomeSetsContacts": {
        "name": "Biome Sets - Contacts",
        "description": "Contact name records from the Contacts.Contact Biome Set.db store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Unmapped protobuf fields are preserved in the Other Fields column.",
        "paths": ('*/Biome/sets/Default/Contacts.Contact/Database/Set.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
        },
    },
    "biomeSetsFindMyDevices": {
        "name": "Biome Sets - FindMy Devices",
        "description": "FindMy device records (device name and owner name) from the FindMy.Device Biome "
                       "Set.db store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go.",
        "paths": ('*/Biome/sets/Default/FindMy.Device/Database/Set.db*',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
        },
    },
    "biomeSetsSignificantLocations": {
        "name": "Biome Sets - Significant Locations",
        "description": "Significant location records (label, street, locality, city, country) from the "
                       "Location.SignificantLocation Biome Set.db store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go.",
        "paths": ('*/Biome/sets/Default/Location.SignificantLocation/Database/Set.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 74 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
        },
    },
    "biomeSetsShortcutPhrases": {
        "name": "Biome Sets - App Shortcut Phrases",
        "description": "Per-application Siri/Shortcuts phrases from the App.Shortcut.Phrase Biome Set.db stores "
                       "(one store per source application).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Documents which intent phrases installed apps registered with the system.",
        "paths": ('*/Biome/sets/Default/App.Shortcut.Phrase/*/Database/Set.db*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 675 rows",
            "hc_ios18_7": "iOS 18.7.8 | 393 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
        },
    },
    "biomeSetsShortcutEntities": {
        "name": "Biome Sets - App Shortcut Entities",
        "description": "Per-application entity records exposed to Siri/Shortcuts from the App.Shortcut.Entity "
                       "Biome Set.db stores (can include user content names such as note titles and board names).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go.",
        "paths": ('*/Biome/sets/Default/App.Shortcut.Entity/*/Database/Set.db*',),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 32 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
        },
    },
}

import re
import struct

import blackboxprotobuf
from google.protobuf.message import DecodeError

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db,
                               convert_unix_ts_to_utc, logfunc)

SOURCE_APP_RE = re.compile(r'sourceIdentifier=([^/\\]+)')


def _set_records(file_found):
    """Yields (modified_utc, protobuf_dict) for every content record of a
    Set.db store. Records that fail protobuf decoding are logged and skipped."""
    if not does_table_exist_in_db(file_found, 'content'):
        logfunc(f'No content table in {file_found} (unsupported Set.db layout?)')
        return
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
            SELECT i.modified, c.content
            FROM content c
            JOIN provenance p ON p.content_hash = c.content_hash
            JOIN instance i ON i.provenance_row_id = p.provenance_row_id
        ''')
        rows = cursor.fetchall()
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(f'Unable to query Set.db {file_found}: {ex}')
        rows = []
    db.close()

    for modified, blob in rows:
        try:
            message, _ = blackboxprotobuf.decode_message(blob)
        except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
            logfunc(f'Skipping Set.db record in {file_found} due to protobuf decode error: {ex}')
            continue
        # instance.modified is Unix epoch microseconds
        yield convert_unix_ts_to_utc(modified), message


def _text(message, key):
    """Returns the protobuf field as text ('' when absent)."""
    value = message.get(key, '')
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if isinstance(value, list):
        return ', '.join(_text({'x': item}, 'x') for item in value)
    if isinstance(value, dict):
        return str(value)
    return str(value) if value != '' else ''


def _nested(message, key):
    value = message.get(key, {})
    return value if isinstance(value, dict) else {}


def _leftover(message, known_keys):
    """Returns unmapped fields as readable text so no data is dropped."""
    rest = {}
    for key in message:
        if key in known_keys:
            continue
        rest[key] = _text(message, key)
    return str(rest) if rest else ''


def _source_app(file_found):
    match = SOURCE_APP_RE.search(file_found)
    return match.group(1) if match else ''


@artifact_processor
def biomeSetsInstalledApps(context):
    data_headers = (('Modified', 'datetime'), 'Bundle ID', 'App Name', 'Other Fields')
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('Set.db'):
            continue
        source_path = file_found
        for modified, message in _set_records(file_found):
            data_list.append((modified, _text(message, '1'), _text(message, '3'),
                              _leftover(message, ('1', '3'))))
    return data_headers, data_list, source_path


@artifact_processor
def biomeSetsContacts(context):
    data_headers = (('Modified', 'datetime'), 'Given Name', 'Family Name', 'Other Fields')
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('Set.db'):
            continue
        source_path = file_found
        for modified, message in _set_records(file_found):
            data_list.append((modified, _text(message, '1'), _text(message, '3'),
                              _leftover(message, ('1', '3'))))
    return data_headers, data_list, source_path


@artifact_processor
def biomeSetsFindMyDevices(context):
    data_headers = (('Modified', 'datetime'), 'Device Name', 'Owner Given Name', 'Owner Family Name',
                    'Other Fields')
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('Set.db'):
            continue
        source_path = file_found
        for modified, message in _set_records(file_found):
            owner = _nested(message, '2')
            data_list.append((modified, _text(message, '1'), _text(owner, '1'), _text(owner, '2'),
                              _leftover(message, ('1', '2'))))
    return data_headers, data_list, source_path


@artifact_processor
def biomeSetsSignificantLocations(context):
    data_headers = (('Modified', 'datetime'), 'Label', 'Street', 'Area', 'City', 'Country', 'Other Fields')
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('Set.db'):
            continue
        source_path = file_found
        for modified, message in _set_records(file_found):
            address = _nested(message, '3')
            data_list.append((modified, _text(message, '1'), _text(address, '1'), _text(address, '2'),
                              _text(address, '3'), _text(address, '4'), _leftover(message, ('1', '2', '3'))))
    return data_headers, data_list, source_path


@artifact_processor
def biomeSetsShortcutPhrases(context):
    data_headers = (('Modified', 'datetime'), 'Source App', 'Phrase', 'Phrase Template', 'Intent URL',
                    'Source File')
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('Set.db'):
            continue
        source_app = _source_app(file_found)
        for modified, message in _set_records(file_found):
            data_list.append((modified, source_app, _text(message, '1'), _text(message, '2'),
                              _text(message, '4'), context.get_relative_path(file_found)))
    return data_headers, data_list, 'see Source File for more info'


@artifact_processor
def biomeSetsShortcutEntities(context):
    data_headers = (('Modified', 'datetime'), 'Source App', 'Entity Name', 'Entity Identifier', 'Entity Type',
                    'Query Provider', 'Source File')
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('Set.db'):
            continue
        source_app = _source_app(file_found)
        for modified, message in _set_records(file_found):
            data_list.append((modified, source_app, _text(message, '1'), _text(message, '2'),
                              _text(message, '3'), _text(message, '4'),
                              context.get_relative_path(file_found)))
    return data_headers, data_list, 'see Source File for more info'
