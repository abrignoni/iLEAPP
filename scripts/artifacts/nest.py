__artifacts_v2__ = {
    "nestStructure": {
        "name": "Nest - Structure",
        "description": "The Nest home recorded in the app's transport store, with its name, "
                       "postal address, coordinates, time zone and the away state, away "
                       "timestamp and away setter as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Nest",
        "notes": "Read from the ZNLTRANSPORTOBJECT row whose ZOBJECT_KEY begins 'structure.'. "
                 "ZOBJECTVALUE is an NSKeyedArchiver archive of a binary plist and is resolved by "
                 "walking $objects from the $top root. Two epochs appear in the same file and are "
                 "handled separately: ZOBJECT_TIMESTAMP is Unix milliseconds and the away_timestamp "
                 "and manual_away_timestamp fields are Unix seconds. Both readings are corroborated "
                 "against each other on the tested sample, where the row's millisecond "
                 "ZOBJECT_TIMESTAMP and its seconds away_timestamp resolve to the same instant. 'Away' "
                 "is the state the store held when the app last wrote the object, not a history of "
                 "arrivals and departures, and the store keeps no prior values. Away Setter is "
                 "reported as stored; no mapping from that integer to a person or a cause was sourced. "
                 "Coordinates are the location recorded for the structure and are not evidence of a "
                 "person's location. The app's data container was present on 1 of the 26 registered "
                 "iOS corpora swept for it, so every count recorded here comes from that one "
                 "extraction and no field has been seen to vary across devices or app versions. A "
                 "second extraction carrying this app would close that gap.",
        "paths": ('*/Documents/Nest.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "home",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
    "nestGeofence": {
        "name": "Nest - Geofence and Presence",
        "description": "Geofences defined for the Nest structure and the presence value the "
                       "app last evaluated, with its evaluation timestamp.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Nest",
        "notes": "Read from the ZNLTRANSPORTOBJECT row whose ZOBJECT_KEY begins 'geofence_info.'. Each "
                 "fence contributes one row carrying its identifier, centre coordinates, radius and "
                 "direction as stored. Presence and Raw Presence are the values the app recorded for "
                 "the combined_presence object and are reported as stored; no mapping of those strings "
                 "was sourced. The presence evaluation timestamp is Unix milliseconds. A geofence is a "
                 "boundary the account configured, so its coordinates describe the fence and not a "
                 "person's position, and a presence value is the app's own evaluation rather than an "
                 "observed location. The device_events list was present and empty on the tested "
                 "sample, so no per-device crossing events are reported. Direction is stored as a list "
                 "of values and is reported as the list, joined; no mapping of those values was "
                 "sourced. On the tested sample the fence carried a radius of 200 and an identifier "
                 "but its latitude and longitude were both 0.0, read identically from the transport "
                 "object and from the ZCDGEOFENCE table, so the store recorded no usable coordinate "
                 "for the fence and no KML placemark results from it. The structure's own coordinates "
                 "are reported by the Nest - Structure artifact and are populated. The app's data "
                 "container was present on 1 of the 26 registered iOS corpora swept for it, so every "
                 "count recorded here comes from that one extraction and no field has been seen to "
                 "vary across devices or app versions. A second extraction carrying this app would "
                 "close that gap.",
        "paths": ('*/Documents/Nest.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
    "nestCameras": {
        "name": "Nest - Cameras",
        "description": "Nest and Dropcam cameras recorded by the app, with serial number, MAC "
                       "and IP address, model, activation time and the last connect and "
                       "disconnect times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Nest",
        "notes": "Read from the ZNLTRANSPORTOBJECT rows whose ZOBJECT_KEY begins 'quartz.', whose "
                 "ZOBJECTVALUE is an NSKeyedArchiver archive. activation_time, last_connect_time and "
                 "last_disconnect_time are Unix milliseconds. IP Address is the address the camera "
                 "last reported to the service and is a private network address in the tested sample, "
                 "so it locates the camera on its own network and not on the internet. Streaming "
                 "State, Camera Type and Last Disconnect Reason are reported as stored. Public Share "
                 "Enabled records whether the camera had public sharing turned on. No video, snapshot "
                 "or event clip is stored locally by this database, so none is recovered here; the "
                 "snapshot and stream host fields are service addresses only. The transport camera "
                 "object carries no camera name field, so no name column is reported here; the name is "
                 "recorded in Dropcam.sqlite and appears in the Nest - Dropcam Cameras artifact. "
                 "Cameras recorded in Dropcam.sqlite are reported separately by the Nest - Dropcam "
                 "Cameras artifact, because that store records a different set of fields and merging "
                 "the two would put values of different meaning in one column. The app's data "
                 "container was present on 1 of the 26 registered iOS corpora swept for it, so every "
                 "count recorded here comes from that one extraction and no field has been seen to "
                 "vary across devices or app versions. A second extraction carrying this app would "
                 "close that gap.",
        "paths": ('*/Documents/Nest.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "device-cctv",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
    "nestDropcamCameras": {
        "name": "Nest - Dropcam Cameras",
        "description": "Cameras recorded in the app's Dropcam store, with serial number, the "
                       "last local IP address seen, software version and the recording and "
                       "streaming settings held for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Nest",
        "notes": "Read from ZCAMERA in Dropcam.sqlite, joined to ZCAMERASETTINGS on the camera's "
                 "primary key. ZLASTCONNECTEDTIME is Core Data seconds since 2001-01-01, a different "
                 "epoch from the Unix milliseconds used by the transport store in Nest.sqlite. Last "
                 "Local IP is the address the camera last reported and is a private network address in "
                 "the tested sample. Audio Recording Enabled and Streaming Enabled are the stored "
                 "settings and record configuration rather than whether recording occurred. Camera "
                 "Type and Share Mode are reported as stored. This store holds no video, snapshot or "
                 "event history, so none is recovered. Software Version was empty on the camera in the "
                 "tested sample; the column is kept because the store defines it and a device on "
                 "another extraction may carry it. The app's data container was present on 1 of the 26 "
                 "registered iOS corpora swept for it, so every count recorded here comes from that "
                 "one extraction and no field has been seen to vary across devices or app versions. A "
                 "second extraction carrying this app would close that gap.",
        "paths": ('*/Documents/Dropcam.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "device-cctv",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
    "nestProtect": {
        "name": "Nest - Protect Devices",
        "description": "Nest Protect smoke and carbon monoxide alarms recorded by the app, "
                       "with battery and alarm status, self-test component results and the "
                       "auto-away state as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Nest",
        "notes": "Read from the ZNLTRANSPORTOBJECT rows whose ZOBJECT_KEY begins 'topaz.', whose "
                 "ZOBJECTVALUE is an NSKeyedArchiver archive. The sibling 'delayed_topaz.' row was "
                 "examined and is deliberately not reported: it resolves to a single entry keyed by "
                 "the same device identifier rather than to the device's own fields, so reporting it "
                 "would emit a second, blank row for a device already listed. "
                 "device_born_on_date_utc_secs and replace_by_date_utc_secs are Unix seconds, as their "
                 "field names record. Smoke Status, CO Status, Heat Status, Battery Health State and "
                 "Hushed State are reported as stored; no mapping from those integers to a condition "
                 "was sourced, so a non-zero value must not be read as an alarm without one. The "
                 "component test columns are the device's own self-test results. Auto Away and Home "
                 "Away Input are the values the device reported and are one input to the structure's "
                 "away state rather than a record of occupancy. This artifact reports device state at "
                 "the time the app last wrote the object; the store holds no alarm or event history. "
                 "The app's data container was present on 1 of the 26 registered iOS corpora swept for "
                 "it, so every count recorded here comes from that one extraction and no field has "
                 "been seen to vary across devices or app versions. A second extraction carrying this "
                 "app would close that gap.",
        "paths": ('*/Documents/Nest.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "alarm-smoke",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
    "nestAccount": {
        "name": "Nest - Account",
        "description": "The Nest account signed in to the app, with the email address, name "
                       "and the structures it belongs to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Nest",
        "notes": "Read from the ZNLTRANSPORTOBJECT row whose ZOBJECT_KEY begins 'user.', whose "
                 "ZOBJECTVALUE is an NSKeyedArchiver archive. The email and name are the values the "
                 "service returned for the signed-in account. Structure Count is the number of entries "
                 "in the account's structures list. Merged With GAIA records whether the account had "
                 "been migrated to a Google account, as stored. Short Name was empty on the account in "
                 "the tested sample; the column is kept because the object defines the field and "
                 "another account may carry it. The app's data container was present on 1 of the 26 "
                 "registered iOS corpora swept for it, so every count recorded here comes from that "
                 "one extraction and no field has been seen to vary across devices or app versions. A "
                 "second extraction carrying this app would close that gap.",
        "paths": ('*/Documents/Nest.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "user",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
    "nestLockUserCredentials": {
        "name": "Nest - Lock User Credentials",
        "description": "User identifiers that have a lock PIN credential provisioned in the "
                       "app's store, with the enabled flag and the stored credential length.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Nest",
        "notes": "Read from ZPCDUSERPINCODESSETTINGSTRAITUSERPINCODE, with the per-user schedule count "
                 "taken from ZPCDBASICUSERSCHEDULESSETTINGSTRAITBASICUSERSCHEDULE on the user "
                 "identifier. The PIN itself is NOT recovered and this artifact does not attempt to. "
                 "On the tested sample the ZPINCODE column holds a 41 byte blob whose bytes are not "
                 "ASCII digits and whose measured entropy is about 5.0 bits per byte, which is not "
                 "consistent with a stored 4 to 8 digit PIN in the clear. The column is therefore "
                 "reported only as present or absent with its length, and no meaning is asserted for "
                 "its contents. What the row does establish is that a credential was provisioned for "
                 "that user identifier. Credential Enabled is reported as stored and was null on three "
                 "of the four rows in the tested sample, so an empty value means the flag was not set "
                 "rather than that the credential was disabled. Schedule Count is a count of schedule "
                 "rows carrying the same user identifier; the schedule rows themselves record a start "
                 "time and, on the tested sample, no end time. The app's data container was present on "
                 "1 of the 26 registered iOS corpora swept for it, so every count recorded here comes "
                 "from that one extraction and no field has been seen to vary across devices or app "
                 "versions. A second extraction carrying this app would close that gap.",
        "paths": ('*/Documents/Nest.sqlite*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "key",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 4 rows",
        },
    },
}

import os
import plistlib
import sqlite3
from datetime import datetime, timedelta, timezone
from plistlib import UID

from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    logfunc,
    open_sqlite_db_readonly,
)

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)
_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)

# Every table in both stores was empty in the main database file on the tested sample and
# populated only in the write-ahead log, so the sidecars are load-bearing and the paths
# patterns must keep their trailing wildcard.
_NEST_MARKER_TABLE = 'ZNLTRANSPORTOBJECT'
_DROPCAM_MARKER_TABLE = 'ZCAMERA'


def _ms_to_utc(value):
    """Unix milliseconds to an aware UTC datetime, or '' when absent or unreadable."""
    if value in (None, '', 0):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(milliseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _sec_to_utc(value):
    """Unix seconds to an aware UTC datetime, or '' when absent or unreadable."""
    if value in (None, '', 0):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(seconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _core_data_to_utc(value):
    """Core Data seconds since 2001-01-01 to an aware UTC datetime, or ''."""
    if value in (None, '', 0):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _unarchive(blob):
    """Resolve an NSKeyedArchiver archive into plain Python objects.

    The transport store keeps each object as a binary plist written by NSKeyedArchiver, so
    the payload is a flat $objects table addressed by UID references from $top. Returns None
    when the blob is absent or is not such an archive, and the caller logs the skip.
    """
    if not blob:
        return None
    try:
        archive = plistlib.loads(bytes(blob))
    except (plistlib.InvalidFileException, ValueError, TypeError):
        return None
    if not isinstance(archive, dict) or '$objects' not in archive:
        return None
    objects = archive['$objects']

    def resolve(node, depth=0):
        if depth > 24:
            return None
        if isinstance(node, UID):
            index = node.data
            return resolve(objects[index], depth + 1) if index < len(objects) else None
        if isinstance(node, dict):
            if 'NS.keys' in node and 'NS.objects' in node:
                return {
                    str(resolve(key, depth + 1)): resolve(value, depth + 1)
                    for key, value in zip(node['NS.keys'], node['NS.objects'])
                }
            if 'NS.objects' in node:
                return [resolve(item, depth + 1) for item in node['NS.objects']]
            if 'NS.string' in node:
                return resolve(node['NS.string'], depth + 1)
            return {
                key: resolve(value, depth + 1)
                for key, value in node.items() if key != '$class'
            }
        if isinstance(node, str) and node == '$null':
            return None
        return node

    top = archive.get('$top') or {}
    root = top.get('root')
    if root is None and top:
        root = next(iter(top.values()))
    return resolve(root)


def _has_table(database, table):
    """True when the store carries the named table, so a same-named file fails closed."""
    try:
        connection = open_sqlite_db_readonly(database)
    except sqlite3.Error:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def _stores(files_found, basename, marker_table):
    """The main database files matching basename, sidecars and lookalikes excluded."""
    stores = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != basename:
            continue
        if not _has_table(file_found, marker_table):
            logfunc(f'Nest: {basename} without a {marker_table} table, skipped: {file_found}')
            continue
        stores.append(file_found)
    return stores


def _transport_objects(database, prefixes):
    """Yield (key, ZOBJECT_TIMESTAMP, resolved value) for transport rows matching a prefix."""
    query = '''
    SELECT ZOBJECT_KEY, ZOBJECT_TIMESTAMP, ZOBJECTVALUE
    FROM ZNLTRANSPORTOBJECT
    ORDER BY ZOBJECT_KEY
    '''
    for record in get_sqlite_db_records(database, query):
        key = record[0] or ''
        if not key.startswith(prefixes):
            continue
        value = _unarchive(record[2])
        if not isinstance(value, dict):
            logfunc(f'Nest: transport object {key} did not resolve to an archived dictionary')
            continue
        yield key, record[1], value


def _text(value):
    """A displayable value.

    A list is rendered as its own comma joined members rather than as its length, so a
    column labelled 'as stored' always shows what the store holds. Use _count for the
    columns that are deliberately counts.
    """
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    if isinstance(value, dict):
        logfunc(f'Nest: expected a scalar and found a dictionary of {len(value)} keys')
        return ''
    return value


def _count(value):
    """The number of members of a list, for the columns that are counts."""
    if isinstance(value, (list, dict)):
        return len(value)
    return '' if value is None else value


@artifact_processor
def nestStructure(context):
    data_headers = (
        ('Object Timestamp', 'datetime'),
        ('Away Timestamp', 'datetime'),
        ('Manual Away Timestamp', 'datetime'),
        'Structure Name',
        'Away',
        'Away Setter (as stored)',
        'Vacation Mode',
        'Address',
        'Postal Code',
        'Country Code',
        'Latitude',
        'Longitude',
        'Time Zone',
        'Member Count',
        'Structure ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _stores(context.get_files_found(), 'Nest.sqlite', _NEST_MARKER_TABLE):
        rows = 0
        for key, timestamp, value in _transport_objects(database, ('structure.',)):
            rows += 1
            address = value.get('address_lines')
            data_list.append((
                _ms_to_utc(timestamp),
                _sec_to_utc(value.get('away_timestamp')),
                _sec_to_utc(value.get('manual_away_timestamp')),
                _text(value.get('name')),
                _text(value.get('away')),
                _text(value.get('away_setter')),
                _text(value.get('vacation_mode')),
                ', '.join(str(line) for line in address) if isinstance(address, list) else '',
                _text(value.get('postal_code')),
                _text(value.get('country_code')),
                _text(value.get('latitude')),
                _text(value.get('longitude')),
                _text(value.get('time_zone')),
                _count(value.get('members')),
                key.split('.', 1)[1] if '.' in key else key,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def nestGeofence(context):
    data_headers = (
        ('Presence Evaluation Timestamp', 'datetime'),
        ('Object Timestamp', 'datetime'),
        'Fence ID',
        'Latitude',
        'Longitude',
        'Radius',
        'Direction (as stored)',
        'Presence (as stored)',
        'Raw Presence (as stored)',
        'Structure ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _stores(context.get_files_found(), 'Nest.sqlite', _NEST_MARKER_TABLE):
        rows = 0
        for key, timestamp, value in _transport_objects(database, ('geofence_info.',)):
            presence = value.get('combined_presence')
            presence = presence if isinstance(presence, dict) else {}
            fences = value.get('fences')
            fences = fences if isinstance(fences, list) else []
            structure_id = key.split('.', 1)[1] if '.' in key else key
            for fence in fences:
                if not isinstance(fence, dict):
                    continue
                rows += 1
                data_list.append((
                    _ms_to_utc(presence.get('presence_evaluation_timestamp')),
                    _ms_to_utc(timestamp),
                    _text(fence.get('fence_id')),
                    _text(fence.get('latitude')),
                    _text(fence.get('longitude')),
                    _text(fence.get('radius')),
                    _text(fence.get('direction')),
                    _text(presence.get('presence')),
                    _text(presence.get('raw_presence')),
                    structure_id,
                    context.get_relative_path(database),
                ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def nestCameras(context):
    data_headers = (
        ('Last Connect Time', 'datetime'),
        ('Last Disconnect Time', 'datetime'),
        ('Activation Time', 'datetime'),
        'Serial Number',
        'MAC Address',
        'IP Address',
        'Model',
        'Camera Type (as stored)',
        'Streaming State (as stored)',
        'Last Disconnect Reason (as stored)',
        'Audio Input Enabled',
        'Preview Streaming Enabled',
        'Public Share Enabled',
        'Where ID',
        'Structure ID',
        'Camera ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _stores(context.get_files_found(), 'Nest.sqlite', _NEST_MARKER_TABLE):
        rows = 0
        for key, _timestamp, value in _transport_objects(database, ('quartz.',)):
            rows += 1
            data_list.append((
                _ms_to_utc(value.get('last_connect_time')),
                _ms_to_utc(value.get('last_disconnect_time')),
                _ms_to_utc(value.get('activation_time')),
                _text(value.get('serial_number')),
                _text(value.get('mac_address')),
                _text(value.get('ip_address')),
                _text(value.get('model')),
                _text(value.get('camera_type')),
                _text(value.get('streaming_state')),
                _text(value.get('last_disconnect_reason')),
                _text(value.get('audio_input_enabled')),
                _text(value.get('preview_streaming_enabled')),
                _text(value.get('public_share_enabled')),
                _text(value.get('where_id')),
                _text(value.get('structure_id')),
                key.split('.', 1)[1] if '.' in key else key,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def nestDropcamCameras(context):
    data_headers = (
        ('Last Connected Time', 'datetime'),
        'Camera Name',
        'Serial Number',
        'Last Local IP',
        'Software Version',
        'Camera Type (as stored)',
        'Share Mode (as stored)',
        'Is Online',
        'Is Streaming',
        'Is Public',
        'Audio Recording Enabled',
        'Streaming Enabled',
        'Where Name',
        'Time Zone',
        'Structure ID',
        'Camera ID',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT
        C.ZLASTCONNECTEDTIME,
        C.ZNAME,
        C.ZSERIALNUMBER,
        C.ZLASTLOCALIP,
        C.ZCOMBINEDSOFTWAREVERSION,
        C.ZCAMERATYPE,
        C.ZSHAREMODE,
        C.ZISONLINE,
        C.ZISSTREAMING,
        C.ZISPUBLIC,
        S.ZAUDIORECORDINGENABLED,
        S.ZSTREAMINGENABLED,
        C.ZWHERENAME,
        C.ZTIMEZONE,
        C.ZNESTSTRUCTUREID,
        C.ZCAMERAID
    FROM ZCAMERA AS C
    LEFT JOIN ZCAMERASETTINGS AS S ON S.ZCAMERA = C.Z_PK
    '''

    for database in _stores(context.get_files_found(), 'Dropcam.sqlite', _DROPCAM_MARKER_TABLE):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                _core_data_to_utc(record[0]),
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                record[10],
                record[11],
                record[12],
                record[13],
                record[14],
                record[15],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def nestProtect(context):
    data_headers = (
        ('Object Timestamp', 'datetime'),
        ('Born On Date', 'datetime'),
        ('Replace By Date', 'datetime'),
        'Device ID',
        'Battery Level',
        'Battery Health State (as stored)',
        'Smoke Status (as stored)',
        'CO Status (as stored)',
        'Heat Status (as stored)',
        'Hushed State (as stored)',
        'Auto Away (as stored)',
        'Home Away Input (as stored)',
        'Device Locale',
        'Smoke Test Passed',
        'CO Test Passed',
        'Heat Test Passed',
        'Buzzer Test Passed',
        'Speaker Test Passed',
        'Wifi Test Passed',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _stores(context.get_files_found(), 'Nest.sqlite', _NEST_MARKER_TABLE):
        rows = 0
        for key, timestamp, value in _transport_objects(database, ('topaz.',)):
            rows += 1
            data_list.append((
                _ms_to_utc(timestamp),
                _sec_to_utc(value.get('device_born_on_date_utc_secs')),
                _sec_to_utc(value.get('replace_by_date_utc_secs')),
                key.split('.', 1)[1] if '.' in key else key,
                _text(value.get('battery_level')),
                _text(value.get('battery_health_state')),
                _text(value.get('smoke_status')),
                _text(value.get('co_status')),
                _text(value.get('heat_status')),
                _text(value.get('hushed_state')),
                _text(value.get('auto_away')),
                _text(value.get('home_away_input')),
                _text(value.get('device_locale')),
                _text(value.get('component_smoke_test_passed')),
                _text(value.get('component_co_test_passed')),
                _text(value.get('component_heat_test_passed')),
                _text(value.get('component_buzzer_test_passed')),
                _text(value.get('component_speaker_test_passed')),
                _text(value.get('component_wifi_test_passed')),
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def nestAccount(context):
    data_headers = (
        ('Object Timestamp', 'datetime'),
        'Email',
        'Name',
        'Short Name',
        'Merged With GAIA',
        'Merged With GAIA At',
        'Structure Count',
        'Jasper Version',
        'User ID',
        'Source File',
    )
    data_list = []
    source_files = []

    for database in _stores(context.get_files_found(), 'Nest.sqlite', _NEST_MARKER_TABLE):
        rows = 0
        for key, timestamp, value in _transport_objects(database, ('user.',)):
            rows += 1
            data_list.append((
                _ms_to_utc(timestamp),
                _text(value.get('email')),
                _text(value.get('name')),
                _text(value.get('short_name')),
                _text(value.get('is_merged_with_gaia')),
                _text(value.get('merged_with_gaia_at')),
                _count(value.get('structures')),
                _text(value.get('jasper_version')),
                key.split('.', 1)[1] if '.' in key else key,
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def nestLockUserCredentials(context):
    data_headers = (
        'User ID',
        'Credential Present',
        'Credential Length (bytes)',
        'Credential Enabled (as stored)',
        'Schedule Count',
        'Source File',
    )
    data_list = []
    source_files = []

    pincode_query = '''
    SELECT ZUSERID, ZPINCODE, ZPINCODECREDENTIALENABLED
    FROM ZPCDUSERPINCODESSETTINGSTRAITUSERPINCODE
    ORDER BY ZUSERID
    '''
    schedule_query = '''
    SELECT ZUSERID, COUNT(*)
    FROM ZPCDBASICUSERSCHEDULESSETTINGSTRAITBASICUSERSCHEDULE
    GROUP BY ZUSERID
    '''

    for database in _stores(context.get_files_found(), 'Nest.sqlite', _NEST_MARKER_TABLE):
        schedules = {}
        for record in get_sqlite_db_records(database, schedule_query):
            schedules[record[0]] = record[1]
        rows = 0
        for record in get_sqlite_db_records(database, pincode_query):
            rows += 1
            credential = record[1]
            length = len(bytes(credential)) if credential is not None else 0
            data_list.append((
                record[0],
                bool(length),
                length,
                '' if record[2] is None else record[2],
                schedules.get(record[0], 0),
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)
