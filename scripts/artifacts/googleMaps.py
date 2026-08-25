"""
Parses Apple iOS Google Maps application artifacts.

Paths and fields in this module were derived from an iOS Data container whose
.com.apple.mobile_container_manager.metadata.plist records
MCMMetadataIdentifier = com.google.Maps.

The On Device Location History stores (odlh-storage.db) carry the same table and
column names as the Android copy that ALEAPP's googleOdlh module reads, so the
queries here are the iOS counterpart of that module rather than a new derivation.
On Android the store sits under com.google.android.gms; on iOS it sits inside the
Google Maps Data container.
"""

import os
import plistlib
import re
import sqlite3
from datetime import datetime, timezone, timedelta

from scripts.ilapfuncs import (
    artifact_processor, get_sqlite_db_records, convert_unix_ts_to_utc,
    convert_cocoa_core_data_ts_to_utc, logfunc
)
from scripts import blackboxprotobuf

UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

__artifacts_v2__ = {
    "googleMapsSemanticSegments": {
        "name": "Google Maps - Semantic Location Segments",
        "description": (
            "Time-bounded segments stored by Google's On Device Location History "
            "(odlh-storage.db, semantic_segment_table). For segments whose "
            "semantic_segment protobuf embeds a coordinate pair the latitude and "
            "longitude are decoded; the segment type is reported as stored."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Maps",
        "notes": (
            "Coordinates are stored as E7 fixed-point integers inside the protobuf at "
            "field path 3 > 1 > 4 > 5, the same position ALEAPP's googleOdlh module reads "
            "on Android. Decoding was measured across the tested images rather than assumed: "
            "on otto_ios17 all 242 segment_type 1 rows yielded a coordinate pair and every "
            "value fell inside valid latitude and longitude bounds, while the 215 "
            "segment_type 2 and 276 segment_type 3 rows carry no coordinate at that path "
            "and are reported with empty latitude and longitude. "
            "segment_type is an undocumented integer and is reported as stored; no "
            "mapping from the value to a name was found in the evidence. "
            "start_timestamp_seconds and end_timestamp_seconds are Unix seconds; "
            "timestamp_millis is Unix milliseconds and is converted at this call site "
            "rather than inferred from magnitude. obfuscated_gaia_id identifies the "
            "Google account the segment belongs to. The SemanticLocation folder is a Google library "
            "location rather than an app-specific one, so the owning app is resolved per "
            "container from its own .com.apple.mobile_container_manager.metadata.plist and "
            "reported in Container App. Across the 19 scannable registered iOS images every "
            "container matching this pattern resolved to com.google.Maps or its "
            "HomeTrafficWidgetExtension, so no foreign attribution was observed; the column is "
            "present so a container belonging to another app is visible rather than silently "
            "reported as Google Maps."),
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/SemanticLocation/odlh-storage.db*',
            '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | com.google.Maps | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | com.google.Maps | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | com.google.Maps | 4 rows",
            "hc_ios18_7": "iOS 18.7 | com.google.Maps | 0 rows",
            "hc_ios26": "iOS 26.5.2 | com.google.Maps | 0 rows",
            "iphone11_ios17": "iOS 17.3 | com.google.Maps | 17 rows",
            "iphone12_ios18": "iOS 18.7 | com.google.Maps | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | com.google.Maps | 0 rows",
            "otto_ios17": "iOS 17.5.1 | com.google.Maps | 733 rows",
        },
    },
    "googleMapsEditedSegments": {
        "name": "Google Maps - Edited Location Segments",
        "description": (
            "Entries in the edited_segment_table of Google's On Device Location History "
            "(odlh-storage.db): segment time ranges with the block range they belong to "
            "and whether the edit was uploaded."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Maps",
        "notes": (
            "Same table and columns as the Android copy read by ALEAPP's googleOdlh "
            "module. All four timestamp columns are Unix seconds. segment_type and "
            "is_edit_uploaded are reported as stored. The table was present and empty "
            "in the tested image, so this reader is code-present and exercised only "
            "against the empty case; the column list comes from the CREATE TABLE "
            "statement in the evidence. The SemanticLocation folder is a Google library "
            "location rather than an app-specific one, so the owning app is resolved per "
            "container from its own .com.apple.mobile_container_manager.metadata.plist and "
            "reported in Container App. Across the 19 scannable registered iOS images every "
            "container matching this pattern resolved to com.google.Maps or its "
            "HomeTrafficWidgetExtension, so no foreign attribution was observed; the column is "
            "present so a container belonging to another app is visible rather than silently "
            "reported as Google Maps."),
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/SemanticLocation/odlh-storage.db*',
            '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "edit",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | com.google.Maps | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | com.google.Maps | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | com.google.Maps | 0 rows",
            "hc_ios18_7": "iOS 18.7 | com.google.Maps | 0 rows",
            "hc_ios26": "iOS 26.5.2 | com.google.Maps | 0 rows",
            "iphone11_ios17": "iOS 17.3 | com.google.Maps | 0 rows",
            "iphone12_ios18": "iOS 18.7 | com.google.Maps | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | com.google.Maps | 0 rows",
            "otto_ios17": "iOS 17.5.1 | com.google.Maps | 0 rows",
        },
    },
    "googleMapsPlaceIndex": {
        "name": "Google Maps - Place Index Cells",
        "description": (
            "Rows of the on-device place index (place-index.db, l1_table). Each row "
            "records an S2 geographic cell identifier, the time the entry was inserted, "
            "and a protobuf payload describing places within that cell."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Maps",
        "notes": (
            "s2_cell_id is reported as stored. The value is an S2 cell identifier, which "
            "encodes a geographic cell, but this module does not convert it to latitude "
            "and longitude and no coordinate pair was found inside the payload, so no "
            "position is asserted. time_inserted is Unix milliseconds, converted at this "
            "call site. Payload Bytes reports the size of the s2_cell_with_places blob so "
            "an examiner can see which cells carry more than a stub; the payload itself is "
            "not decoded. Presence of a cell records that the index held it, which is not "
            "by itself evidence the device was inside that cell. The SemanticLocation folder is a Google library "
            "location rather than an app-specific one, so the owning app is resolved per "
            "container from its own .com.apple.mobile_container_manager.metadata.plist and "
            "reported in Container App. Across the 19 scannable registered iOS images every "
            "container matching this pattern resolved to com.google.Maps or its "
            "HomeTrafficWidgetExtension, so no foreign attribution was observed; the column is "
            "present so a container belonging to another app is visible rather than silently "
            "reported as Google Maps."),
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/SemanticLocation/place-index.db*',
            '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "map",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | com.google.Maps | 30770 rows",
            "cookbook_ios1751": "iOS 17.5.1 | com.google.Maps | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | com.google.Maps | 103 rows",
            "hc_ios18_7": "iOS 18.7 | com.google.Maps | 0 rows",
            "hc_ios26": "iOS 26.5.2 | com.google.Maps | 0 rows",
            "iphone11_ios17": "iOS 17.3 | com.google.Maps | 2814 rows",
            "iphone12_ios18": "iOS 18.7 | com.google.Maps | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | com.google.Maps | 41 rows",
            "otto_ios17": "iOS 17.5.1 | com.google.Maps | 15532 rows",
        },
    },
    "googleMapsCachedObjects": {
        "name": "Google Maps - Cached Objects",
        "description": (
            "Entries in the app's Core Data object cache (GMSCacheStorage-Objects, "
            "Objects.sqlite, ZGMSCACHEDOBJECT): the cache key, its type and version, and "
            "when the entry was last updated."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Google Maps",
        "notes": (
            "ZUPDATEDDATE is a Core Data timestamp counted from the 2001 Cocoa epoch. The "
            "unit was established by decoding stored values against both candidate epochs "
            "and keeping the only reading that falls inside the tested image's lifetime; "
            "read as Unix seconds the same values land in 1994. ZTYPE is an undocumented "
            "integer and is reported as stored. In the tested images most entries are HTTP "
            "cache keys and bundled icon or texture asset names; a small number of ZTYPE 6 "
            "entries carry named corpora. Entry names are cache keys written by the app, "
            "not necessarily places the user visited or searched. The WAL sidecar is "
            "load-bearing for this store and the path pattern picks it up: across the nine "
            "tested images the committed file alone reads short on six of them, and on one "
            "it reads zero rows against 44 with the WAL applied. GMSCacheStorage is written by the Google Maps SDK, which "
            "other apps can embed, so the owning app is resolved per container from its own "
            ".com.apple.mobile_container_manager.metadata.plist and reported in Container App. "
            "Across the 19 scannable registered iOS images every container matching this pattern "
            "resolved to com.google.Maps or its HomeTrafficWidgetExtension; the column is present "
            "so a container belonging to another app is visible rather than silently reported as "
            "Google Maps."),
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Application Support/GMSCacheStorage-Objects/Objects.sqlite*',
            '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | com.google.Maps | 625 rows",
            "cookbook_ios1751": "iOS 17.5.1 | com.google.Maps | 141 rows",
            "dexter_ios18": "iOS 18.3.2 | com.google.Maps | 152 rows",
            "hc_ios18_7": "iOS 18.7 | com.google.Maps | 172 rows",
            "hc_ios26": "iOS 26.5.2 | com.google.Maps | 0 rows",
            "iphone11_ios17": "iOS 17.3 | com.google.Maps | 238 rows",
            "iphone12_ios18": "iOS 18.7 | com.google.Maps | 44 rows",
            "magnet_ios16": "iOS 16.1.1 | com.google.Maps | 142 rows",
            "otto_ios17": "iOS 17.5.1 | com.google.Maps | 517 rows",
        },
    },
}


CONTAINER_RE = re.compile(r'/Containers/Data/Application/([^/]+)/', re.I)


def _container_owners(context):
    """Map container directory name to the bundle id its own metadata plist records.

    The container directory is a UUID, so the owning app is only knowable from
    .com.apple.mobile_container_manager.metadata.plist inside that container. That file
    is declared in this artifact's own paths so it is staged regardless of the order
    artifacts run in; a filesystem sibling check would depend on run order because the
    seeker copies matches into a shared staging folder.
    """
    owners = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            continue
        try:
            with open(file_found, 'rb') as handle:
                parsed = plistlib.load(handle)
        except (plistlib.InvalidFileException, ValueError, OSError):
            continue
        identifier = parsed.get('MCMMetadataIdentifier')
        if identifier:
            owners[os.path.basename(os.path.dirname(file_found))] = identifier
    return owners


def _container_app(path, owners):
    """Bundle id of the container the file sits in, or '' when it cannot be resolved."""
    match = CONTAINER_RE.search(str(path).replace('\\', '/'))
    if not match:
        return ''
    return owners.get(match.group(1), '')


def _db_files(context, name):
    """Database files matching the file name, without -wal/-shm/-journal sidecars."""
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) == name:
            result.append(file_found)
    return result


def _unix_ms_to_utc(value):
    """Unix milliseconds. Converted here because the column's unit is known, rather
    than handing the value to a converter that infers the unit from magnitude."""
    if not isinstance(value, int) or value == 0:
        return ''
    return UNIX_EPOCH + timedelta(milliseconds=value)


def _pb_get(node, *path):
    """Defensively walk a blackboxprotobuf dict."""
    current = node
    for key in path:
        if isinstance(current, list):
            current = current[0] if current else None
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _e7_to_degrees(value, limit):
    """E7 fixed-point coordinate stored as an unsigned varint; negative values wrap."""
    if not isinstance(value, int):
        return ''
    if value > 2**31:
        value -= 2**32
    degrees = value / 1e7
    if abs(degrees) > limit:
        return ''
    return degrees


def _segment_coordinates(blob):
    """Latitude and longitude of the place coordinate a semantic_segment protobuf
    embeds, if any. Returns empty strings when the field path is absent."""
    if not blob:
        return '', ''
    try:
        info, _ = blackboxprotobuf.decode_message(blob)
    except Exception:  # pylint: disable=broad-exception-caught
        return '', ''
    point = _pb_get(info, '3', '1', '4', '5')
    if not isinstance(point, dict):
        return '', ''
    latitude = _e7_to_degrees(point.get('1'), 90)
    longitude = _e7_to_degrees(point.get('2'), 180)
    if latitude == '' or longitude == '':
        return '', ''
    return latitude, longitude


@artifact_processor
def googleMapsSemanticSegments(context):
    data_list = []
    source_path = ''
    owners = _container_owners(context)

    for file_found in _db_files(context, 'odlh-storage.db'):
        try:
            db_records = get_sqlite_db_records(file_found, '''
                SELECT start_timestamp_seconds, end_timestamp_seconds, timestamp_millis,
                       segment_type, semantic_segment, shown_in_timeline, is_finalized,
                       hierarchy_level, segment_id, obfuscated_gaia_id
                FROM semantic_segment_table
                ORDER BY start_timestamp_seconds DESC
            ''')
        except sqlite3.Error as ex:
            logfunc(f'Unable to read semantic_segment_table in {file_found}: {ex}')
            continue

        for record in db_records:
            source_path = file_found
            latitude, longitude = _segment_coordinates(record[4])
            data_list.append((
                convert_unix_ts_to_utc(record[0]),
                convert_unix_ts_to_utc(record[1]),
                _unix_ms_to_utc(record[2]),
                record[3],
                latitude,
                longitude,
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                _container_app(file_found, owners),
            ))

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        ('Record Written', 'datetime'),
        'Segment Type (as stored)',
        'Latitude',
        'Longitude',
        'Shown In Timeline',
        'Is Finalized',
        'Hierarchy Level',
        'Segment ID',
        'Obfuscated GAIA ID',
        'Container App',
    )
    return data_headers, data_list, source_path


@artifact_processor
def googleMapsEditedSegments(context):
    data_list = []
    source_path = ''
    owners = _container_owners(context)

    for file_found in _db_files(context, 'odlh-storage.db'):
        try:
            db_records = get_sqlite_db_records(file_found, '''
                SELECT start_timestamp_seconds, end_timestamp_seconds,
                       block_start_timestamp_seconds, block_end_timestamp_seconds,
                       segment_type, is_edit_uploaded, hierarchy_level,
                       segment_id, obfuscated_gaia_id
                FROM edited_segment_table
                ORDER BY start_timestamp_seconds DESC
            ''')
        except sqlite3.Error as ex:
            logfunc(f'Unable to read edited_segment_table in {file_found}: {ex}')
            continue

        for record in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(record[0]),
                convert_unix_ts_to_utc(record[1]),
                convert_unix_ts_to_utc(record[2]),
                convert_unix_ts_to_utc(record[3]),
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                _container_app(file_found, owners),
            ))

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        ('Block Start Time', 'datetime'),
        ('Block End Time', 'datetime'),
        'Segment Type (as stored)',
        'Is Edit Uploaded',
        'Hierarchy Level',
        'Segment ID',
        'Obfuscated GAIA ID',
        'Container App',
    )
    return data_headers, data_list, source_path


@artifact_processor
def googleMapsPlaceIndex(context):
    data_list = []
    source_path = ''
    owners = _container_owners(context)

    for file_found in _db_files(context, 'place-index.db'):
        try:
            db_records = get_sqlite_db_records(file_found, '''
                SELECT time_inserted, s2_cell_id, length(s2_cell_with_places)
                FROM l1_table
                ORDER BY time_inserted DESC
            ''')
        except sqlite3.Error as ex:
            logfunc(f'Unable to read l1_table in {file_found}: {ex}')
            continue

        for record in db_records:
            source_path = file_found
            data_list.append((
                _unix_ms_to_utc(record[0]),
                record[1],
                record[2],
                _container_app(file_found, owners),
            ))

    data_headers = (
        ('Time Inserted', 'datetime'),
        'S2 Cell ID (as stored)',
        'Payload Bytes',
        'Container App',
    )
    return data_headers, data_list, source_path


@artifact_processor
def googleMapsCachedObjects(context):
    data_list = []
    source_path = ''
    owners = _container_owners(context)

    for file_found in _db_files(context, 'Objects.sqlite'):
        try:
            db_records = get_sqlite_db_records(file_found, '''
                SELECT ZUPDATEDDATE, ZNAME, ZTYPE, ZVERSION
                FROM ZGMSCACHEDOBJECT
                ORDER BY ZUPDATEDDATE DESC
            ''')
        except sqlite3.Error as ex:
            logfunc(f'Unable to read ZGMSCACHEDOBJECT in {file_found}: {ex}')
            continue

        for record in db_records:
            source_path = file_found
            data_list.append((
                convert_cocoa_core_data_ts_to_utc(record[0]),
                record[1],
                record[2],
                record[3],
                _container_app(file_found, owners),
            ))

    data_headers = (
        ('Updated', 'datetime'),
        'Entry Name',
        'Type (as stored)',
        'Version',
        'Container App',
    )
    return data_headers, data_list, source_path
