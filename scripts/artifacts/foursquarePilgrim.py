__artifacts_v2__ = {
    "foursquare_pilgrim_visits": {
        "name": "Foursquare Pilgrim - Location Visits",
        "description": "Visits recorded in the Foursquare Pilgrim SDK store, with the "
                       "arrival and departure fix of each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per row of PilgrimLocationVisit in Library/pilgrim-database.sqlite. "
                 "Arrival and Departure are stored as JSON holding a single location fix each: "
                 "latitude, longitude, altitude, speed, heading, floor, horizontal and vertical "
                 "accuracy, and a Unix timestamp in seconds. The reported coordinates are the "
                 "arrival fix, and the departure fix is carried in its own columns, so a row "
                 "that moved between the two is visible. Dwell is the difference between the two "
                 "timestamps and is computed here, not stored. Every one of the 755 rows across "
                 "the three tested stores carried both an arrival and a departure and no "
                 "departure preceded its arrival. Stop Detection Algorithm is reported as "
                 "stored; the tested stores hold clientEma and clientEmaMallMode and nothing "
                 "available defines either. Nothing in a row records that a person entered it, "
                 "so a row is not a check-in and does not establish that anyone used the app at "
                 "that moment. Arrival Floor (as stored) held no value on any row of either "
                 "tested image and is kept because the store declares the field. Pilgrim is a "
                 "licensable SDK, so Container App names the app whose data container held the "
                 "store, read from that container's own metadata plist, and no row is attributed "
                 "to Foursquare by assumption. On the iOS 17.5.1 image two containers each held "
                 "a store and their visit sets overlap without matching: 60 of the rows agree on "
                 "arrival time, coordinates and departure time while 107 appear only in one and "
                 "104 only in the other, so the stores are reported separately and are not "
                 "merged. The database names a job PruneLocationVisitsJob; the window a store "
                 "covers is not established, and an absent visit is not evidence that none "
                 "occurred.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/pilgrim-database.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Swarm 6.12.20, Pilgrim SDK 4.0.1 | 424 rows",
            "otto_ios17": "iOS 17.5.1 | Swarm 6.12.32 and Foursquare 11.23.33, Pilgrim SDK 4.0.4 | 331 rows",
        },
    },
    "foursquare_pilgrim_movement": {
        "name": "Foursquare Pilgrim - Movement Log",
        "description": "Location fixes the Foursquare Pilgrim SDK wrote to its own debug log, "
                       "with the movement state on the rows that carry one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per row of PilgrimDebugLog whose data field carries a coordinate pair. "
                 "The SDK writes that field as a Swift description rather than as JSON, so the "
                 "coordinates, accuracy, speed, course, movement state and the app's own "
                 "rendering of the local time are read out of it by pattern and any part that "
                 "does not match is left blank. Rows without a coordinate are not reported, which "
                 "excludes the SDK's request and response logging; those rows carry request "
                 "headers including an API key, and nothing in them is reported here. Timestamp "
                 "is the row's own timestamp column, stored as text with no zone marker. It is "
                 "UTC on one of the tested images, measured rather than assumed: 359 rows there "
                 "also carry the app's rendering of the same moment in a named local zone, and "
                 "converting that rendering to UTC agreed with the column to within a minute "
                 "on 357 of them. The two that did not are rows whose own event text records an "
                 "old fix being logged, one of them stating that a very old location was "
                 "ignored, so the gap there is the age of the fix rather than a zone difference. "
                 "The other two stores carry no such rendering, so the same reading is applied "
                 "to them without that corroboration. Local Time and Local Time Zone are the "
                 "app's own text where it is present, reported as stored. Speed State is "
                 "reported as stored; the tested stores hold stopped, moving, honing and "
                 "unknown, and nothing available defines them. Speed State (as stored) and "
                 "Current Speed (as stored) are blank on the rows that record a monitored region "
                 "rather than a fix, since those rows carry no movement state. Type (as stored) "
                 "held the single value 2 on every reported row of both tested images, so only "
                 "one of the log's types carries a coordinate, which is why this artifact "
                 "reports far fewer rows than the table holds; Level (as stored) varies. "
                 "Container App held one value on the iOS 16.5 image, where a single app "
                 "embedded the SDK, and two on the iOS 17.5.1 image. The database names a job "
                 "PurgeOldLogsJob; the window a store covers is not established.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/pilgrim-database.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "navigation",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Swarm 6.12.20, Pilgrim SDK 4.0.1 | 379 rows",
            "otto_ios17": "iOS 17.5.1 | Swarm 6.12.32 and Foursquare 11.23.33, Pilgrim SDK 4.0.4 | 92 rows",
        },
    },
    "foursquare_pilgrim_resolved_visits": {
        "name": "Foursquare Pilgrim - Resolved Visits",
        "description": "Visits the Foursquare Pilgrim SDK resolved to a named place or to a "
                       "location type, with the venue record where one was attached.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per row of PilgrimLastVisit and PilgrimBackFillVisit, which share a "
                 "schema and are told apart by the Source Table column. Departure Time was blank on every "
                 "row of both tested images: the embedded visit carries an arrival and a null "
                 "departure, and the reason is not established here. Venue "
                 "Name, Venue ID, Venue Categories and Venue Address were each blank on the iOS "
                 "16.5 image, whose row resolved to a location type with no venue attached, and "
                 "carry values on the iOS 17.5.1 image. Region Latitude and Region Longitude "
                 "were each blank on the iOS 17.5.1 image, whose rows recorded no region. PilgrimLastVisit held "
                 "exactly one row in each tested store and PilgrimBackFillVisit was empty in all "
                 "three, so the backfill half is code present and was not exercised. The venue "
                 "field is JSON and carries the place's name, identifier, category names and a "
                 "nested address with its own coordinates; where it is absent the row still "
                 "records a location type. Location Type and Confidence are reported as stored; "
                 "the tested rows hold home and venue, and high and med, and nothing available "
                 "defines the full set. The row also embeds a copy of the visit in the same form "
                 "the Location Visits artifact reads, so Arrival and Departure here come from "
                 "that copy. On the one store whose row recorded region coordinates, those "
                 "coordinates equalled one of the rows in PilgrimRegion, and that row carried the "
                 "highest probability of the four; that is a single observation and no mapping "
                 "between the two tables is asserted from it.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/pilgrim-database.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Swarm 6.12.20, Pilgrim SDK 4.0.1 | 1 row",
            "otto_ios17": "iOS 17.5.1 | Swarm 6.12.32 and Foursquare 11.23.33, Pilgrim SDK 4.0.4 | 2 rows",
        },
    },
    "foursquare_pilgrim_regions": {
        "name": "Foursquare Pilgrim - Regions",
        "description": "Regions the Foursquare Pilgrim SDK held for the device, from its region "
                       "table and its monitored stop region.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per row of PilgrimRegion and of PilgrimStopRegion, told apart by the "
                 "Source Table column. PilgrimRegion rows carry a centre coordinate and a "
                 "probability; PilgrimStopRegion rows carry a centre, a radius and an identifier "
                 "and there was one in each tested store. Probability, Type and Secondary Type "
                 "are reported as stored: the tested rows hold type 1 with secondary type 0 or 2, "
                 "and nothing available defines either number, so no meaning is given to them "
                 "here. The database names a job HomeWorkJob, which is "
                 "recorded here only as an observation about the store and is not evidence that "
                 "any particular row is a home or a work location.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/pilgrim-database.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "target",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Swarm 6.12.20, Pilgrim SDK 4.0.1 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | Swarm 6.12.32 and Foursquare 11.23.33, Pilgrim SDK 4.0.4 | 11 rows",
        },
    },
    "foursquare_pilgrim_trail": {
        "name": "Foursquare Pilgrim - Location Trail",
        "description": "Rows of the Foursquare Pilgrim SDK location trail table, unpopulated on "
                       "the two tested images.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per row of PilgrimLocationTrail, whose columns the store itself declares "
                 "as latitude, longitude, altitude, horizontal accuracy, timestamp, speed, "
                 "heading, a used flag and two authorisation strings. Timestamp there is a "
                 "number rather than the text used elsewhere in the same database and is read as "
                 "Unix seconds, which is the form the visit rows use. This table was empty in all "
                 "three tested stores, so the reader is code present and unexercised and the "
                 "timestamp reading is taken from the sibling tables rather than observed here. "
                 "The database contains a job named TrailPruningJob, and an empty table is not "
                 "evidence "
                 "that the device did not move.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/pilgrim-database.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "activity",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Swarm 6.12.20, Pilgrim SDK 4.0.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Swarm 6.12.32 and Foursquare 11.23.33, Pilgrim SDK 4.0.4 | 0 rows",
        },
    },
    "foursquare_pilgrim_system_visits": {
        "name": "Foursquare Pilgrim - System Visits",
        "description": "Rows of the Foursquare Pilgrim SDK system visit table, unpopulated on the "
                       "two tested images.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Locations",
        "notes": "One row per row of PilgrimCLVisit, whose columns the store declares as an "
                 "arrival date, a departure date, a latitude, a longitude, a horizontal accuracy "
                 "and a visit identifier. The table name and those columns match the shape of "
                 "the operating system's CLVisit object, which is not sourced here; the rows are "
                 "a "
                 "different source from the SDK's own stop detection in the Location Visits "
                 "artifact, so the two can disagree and neither confirms the other. This table "
                 "was empty in all three tested stores, so the reader is code present and "
                 "unexercised, and its dates are read as the same text form the sibling tables "
                 "in this database use rather than from observation here.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/pilgrim-database.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Swarm 6.12.20, Pilgrim SDK 4.0.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | Swarm 6.12.32 and Foursquare 11.23.33, Pilgrim SDK 4.0.4 | 0 rows",
        },
    },
}

import json
import os
import plistlib
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               logfunc)

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_STORE_NAME = 'pilgrim-database.sqlite'
_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)

# The SDK writes PilgrimDebugLog.data as a Swift description rather than as JSON.
_COORDS = re.compile(r'<([+-]?\d+\.\d+),\s*([+-]?\d+\.\d+)>')
_ACCURACY = re.compile(r'\+/-\s*([\d.]+)m')
_SPEED_COURSE = re.compile(r'\(speed\s+([-\d.]+)\s+mps\s*/\s*course\s+([-\d.]+)\)')
_LOCAL_TIME = re.compile(r'@\s*(\d+/\d+/\d+,\s*[\d:]+\s*[AP]M)\s+([A-Za-z][A-Za-z ]+?)(?:,|\]|$)')
_SPEED_STATE = re.compile(r'"speedState":\s*(\w+)')
_CURRENT_SPEED = re.compile(r'"currentSpeed":\s*([-\d.]+)')
_RADIUS = re.compile(r'radius:\s*([\d.]+)m')


def _stores(files_found):
    '''Every Pilgrim database among the matched files, directories skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if os.path.basename(path) == _STORE_NAME and path not in seen:
            seen.append(path)
    return seen


def _container_apps(files_found):
    '''{container directory: bundle id} from each container's own metadata plist.'''
    apps = {}
    for found in files_found:
        path = str(found)
        if os.path.basename(path) != _METADATA_NAME or os.path.isdir(path):
            continue
        try:
            with open(path, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Foursquare Pilgrim: could not read a container metadata plist: {error}')
            continue
        bundle_id = plist.get('MCMMetadataIdentifier')
        if bundle_id:
            apps[os.path.dirname(path).replace('\\', '/')] = bundle_id
    return apps


def _container_app(store, apps):
    '''Bundle id of the app whose container holds <container>/Library/pilgrim-database.sqlite.'''
    container = os.path.dirname(os.path.dirname(str(store))).replace('\\', '/')
    return apps.get(container, '')


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        logfunc(f'Foursquare Pilgrim: {table} is not in this pilgrim-database.sqlite')
        return []
    statement = f'SELECT {columns} FROM {table}'
    try:
        return list(get_sqlite_db_records(path, statement))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Foursquare Pilgrim: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _unix_to_utc(value):
    '''Unix seconds, whole or fractional, to an aware UTC datetime, or ''.'''
    if value in (None, ''):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _stored_datetime(value):
    '''A stored 'YYYY-MM-DD HH:MM:SS' string as an aware UTC datetime, or the value as text.'''
    if value in (None, ''):
        return ''
    try:
        return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return _text(value)


def _fix(blob):
    '''The location fix a visit stores as JSON, as a dict, or {} when it cannot be read.'''
    if not blob:
        return {}
    try:
        value = json.loads(blob)
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _dwell_minutes(arrival, departure):
    '''Minutes between two fix timestamps, rounded to one decimal, or ''.'''
    start, end = arrival.get('timestamp'), departure.get('timestamp')
    if start in (None, '') or end in (None, ''):
        return ''
    try:
        return round((float(end) - float(start)) / 60, 1)
    except (TypeError, ValueError):
        return ''


def _first(pattern, text, group=1):
    '''The first capture of a pattern in a string, or ''.'''
    match = pattern.search(text)
    return match.group(group) if match else ''


@artifact_processor
def foursquare_pilgrim_visits(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _stores(files_found)
    apps = _container_apps(files_found)

    for source_path in sources:
        app = _container_app(source_path, apps)
        for row_id, arrival, departure, algorithm in _rows(
                source_path, 'PilgrimLocationVisit',
                'id, arrival, departure, stopDetectionAlgorithm'):
            start, end = _fix(arrival), _fix(departure)
            data_list.append((
                _unix_to_utc(start.get('timestamp')), _unix_to_utc(end.get('timestamp')),
                _dwell_minutes(start, end),
                _text(start.get('latitude')), _text(start.get('longitude')),
                _text(start.get('altitude')), _text(start.get('horizontalAccuracy')),
                _text(start.get('verticalAccuracy')), _text(start.get('speed')),
                _text(start.get('heading')), _text(start.get('floor')),
                _text(end.get('latitude')), _text(end.get('longitude')),
                _text(end.get('horizontalAccuracy')),
                _text(algorithm), app, _text(row_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Arrival Time', 'datetime'), ('Departure Time', 'datetime'), 'Dwell (minutes)',
        'Latitude', 'Longitude', 'Arrival Altitude', 'Arrival Horizontal Accuracy',
        'Arrival Vertical Accuracy', 'Arrival Speed (as stored)', 'Arrival Heading (as stored)',
        'Arrival Floor (as stored)', 'Departure Latitude', 'Departure Longitude',
        'Departure Horizontal Accuracy', 'Stop Detection Algorithm (as stored)',
        'Container App', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def foursquare_pilgrim_movement(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _stores(files_found)
    apps = _container_apps(files_found)

    for source_path in sources:
        app = _container_app(source_path, apps)
        for stamp, level, kind, data, description in _rows(
                source_path, 'PilgrimDebugLog',
                'timestamp, level, type, data, eventDescription'):
            text = '' if data is None else str(data)
            coords = _COORDS.search(text)
            if not coords:
                continue
            speed_course = _SPEED_COURSE.search(text)
            data_list.append((
                _stored_datetime(stamp), coords.group(1), coords.group(2),
                _first(_ACCURACY, text), speed_course.group(1) if speed_course else '',
                speed_course.group(2) if speed_course else '',
                _first(_SPEED_STATE, text), _first(_CURRENT_SPEED, text),
                _first(_RADIUS, text), _text(description),
                _first(_LOCAL_TIME, text), _first(_LOCAL_TIME, text, 2),
                _text(level), _text(kind), app,
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Horizontal Accuracy',
        'Speed (as stored)', 'Course (as stored)', 'Speed State (as stored)',
        'Current Speed (as stored)', 'Region Radius (as stored)', 'Event',
        'Local Time (as stored)', 'Local Time Zone (as stored)', 'Level (as stored)',
        'Type (as stored)', 'Container App',
    )
    return data_headers, data_list, '\n'.join(sources)


def _venue_fields(blob):
    '''(name, id, categories, latitude, longitude, address) out of a stored venue record.'''
    if not blob:
        return ('', '', '', '', '', '')
    try:
        venue = json.loads(blob)
    except (TypeError, ValueError):
        return ('', '', '', '', '', '')
    if not isinstance(venue, dict):
        return ('', '', '', '', '', '')
    location = venue.get('location')
    if isinstance(location, str):
        try:
            location = json.loads(location)
        except (TypeError, ValueError):
            location = {}
    if not isinstance(location, dict):
        location = {}
    categories = venue.get('categories')
    names = []
    if isinstance(categories, list):
        for entry in categories:
            if isinstance(entry, str):
                try:
                    entry = json.loads(entry)
                except (TypeError, ValueError):
                    continue
            if isinstance(entry, dict) and entry.get('name'):
                names.append(str(entry['name']))
    address = ', '.join(str(location[key]) for key in
                        ('address', 'city', 'state', 'postalCode', 'country') if location.get(key))
    return (_text(venue.get('name')), _text(venue.get('id')), '; '.join(names),
            _text(location.get('latitude')), _text(location.get('longitude')), address)


@artifact_processor
def foursquare_pilgrim_resolved_visits(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _stores(files_found)
    apps = _container_apps(files_found)

    for source_path in sources:
        app = _container_app(source_path, apps)
        for table in ('PilgrimLastVisit', 'PilgrimBackFillVisit'):
            for (row_id, location_type, confidence, venue, other_venues, visit_id,
                 matched_trigger, location_visit, region_lat, region_lng) in _rows(
                    source_path, table,
                    'id, locationTypeString, confidenceString, venue, otherPossibleVenues, '
                    'pilgrimVisitId, matchedTrigger, locationVisit, regionLat, regionLng'):
                visit = _fix(location_visit)
                start, end = _fix(visit.get('arrival')), _fix(visit.get('departure'))
                name, venue_id, categories, lat, lng, address = _venue_fields(venue)
                data_list.append((
                    _unix_to_utc(start.get('timestamp')), _unix_to_utc(end.get('timestamp')),
                    _text(location_type), _text(confidence), name, venue_id, categories,
                    address, lat or _text(start.get('latitude')),
                    lng or _text(start.get('longitude')),
                    _text(region_lat), _text(region_lng), _text(other_venues),
                    _text(matched_trigger), _text(visit_id), table, app, _text(row_id),
                ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Arrival Time', 'datetime'), ('Departure Time', 'datetime'),
        'Location Type (as stored)', 'Confidence (as stored)', 'Venue Name', 'Venue ID',
        'Venue Categories', 'Venue Address', 'Latitude', 'Longitude', 'Region Latitude',
        'Region Longitude', 'Other Possible Venues (as stored)', 'Matched Trigger (as stored)',
        'Visit ID', 'Source Table', 'Container App', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def foursquare_pilgrim_regions(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _stores(files_found)
    apps = _container_apps(files_found)

    for source_path in sources:
        app = _container_app(source_path, apps)
        for row_id, probability, lat, lng, kind, secondary in _rows(
                source_path, 'PilgrimRegion',
                'id, probability, centerLatitude, centerLongitude, type, secondaryType'):
            data_list.append((_text(lat), _text(lng), _text(probability), '', _text(kind),
                              _text(secondary), '', 'PilgrimRegion', app, _text(row_id)))
        for row_id, lat, lng, radius, identifier in _rows(
                source_path, 'PilgrimStopRegion', 'id, lat, lng, radius, identifier'):
            data_list.append((_text(lat), _text(lng), '', _text(radius), '', '',
                              _text(identifier), 'PilgrimStopRegion', app, _text(row_id)))

    data_headers = (
        'Latitude', 'Longitude', 'Probability (as stored)', 'Radius (as stored)',
        'Type (as stored)', 'Secondary Type (as stored)', 'Identifier', 'Source Table',
        'Container App', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def foursquare_pilgrim_trail(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _stores(files_found)
    apps = _container_apps(files_found)

    for source_path in sources:
        app = _container_app(source_path, apps)
        for (row_id, stamp, lat, lng, altitude, accuracy, speed, heading, used,
             location_auth, accuracy_auth) in _rows(
                source_path, 'PilgrimLocationTrail',
                'id, timestamp, latitude, longitude, altitude, horizontalAccuracy, speed, '
                'heading, used, locationAuth, locationAccAuth'):
            data_list.append((
                _unix_to_utc(stamp), _text(lat), _text(lng), _text(altitude), _text(accuracy),
                _text(speed), _text(heading), _text(used), _text(location_auth),
                _text(accuracy_auth), app, _text(row_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Altitude',
        'Horizontal Accuracy', 'Speed (as stored)', 'Heading (as stored)', 'Used (as stored)',
        'Location Authorization (as stored)', 'Accuracy Authorization (as stored)',
        'Container App', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def foursquare_pilgrim_system_visits(context):
    data_list = []
    files_found = context.get_files_found()
    sources = _stores(files_found)
    apps = _container_apps(files_found)

    for source_path in sources:
        app = _container_app(source_path, apps)
        for row_id, arrival, departure, lat, lng, accuracy, visit_id in _rows(
                source_path, 'PilgrimCLVisit',
                'id, arrivalDate, departureDate, latitude, longitude, hacc, visitId'):
            data_list.append((
                _stored_datetime(arrival), _stored_datetime(departure), _text(lat), _text(lng),
                _text(accuracy), _text(visit_id), app, _text(row_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Arrival Time', 'datetime'), ('Departure Time', 'datetime'), 'Latitude', 'Longitude',
        'Horizontal Accuracy', 'Visit ID', 'Container App', 'Row ID',
    )
    return data_headers, data_list, '\n'.join(sources)
