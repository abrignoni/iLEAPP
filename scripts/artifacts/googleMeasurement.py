__artifacts_v2__ = {
    "google_measurement_store": {
        "name": "Google Measurement - App Analytics Store",
        "description": "Event counters, user properties and session values the Google Measurement "
                       "(Firebase Analytics) SDK kept inside an app's data container, with the app's "
                       "bundle identifier as a column.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-07",
        "last_update_date": "2026-11-07",
        "requirements": "none",
        "category": "Firebase Analytics",
        "notes": (
            "Reads the events and user_attributes tables of Library/Application Support/Google/Measurement/"
            "google-app-measurement.sql and selected keys of com.google.gmp.measurement.plist in the same "
            "folder, in the data container of any app that carries them. App Bundle ID is the identifier in the "
            "container's metadata plist or, in an iTunes backup, the name of the AppDomain folder; it is blank "
            "for a container that has neither. Record Type tells which file a row came from (Event and User "
            "Property rows are from the database, Measurement plist rows from the plist), so there is no "
            "Source File column. Event rows: Name is events.name as stored, Count is lifetime_count and "
            "Time is last_fire_timestamp, left blank when that is zero; one row per event name, not per "
            "occurrence. User Property rows: Name, Value and Origin as stored, Time is "
            "set_timestamp; Value is shown as stored except bytes, which are shown as hex. Times in the database are read as Unix seconds, "
            "and a value of 100000000000 or more is read as milliseconds. Measurement plist rows: first_open_timestamp_ms and "
            "last_uploaded_event_millis are read as Unix milliseconds, last_engagement_end, "
            "last_successful_upload and last_failed_upload as Unix seconds (a zero leaves Time blank and "
            "the stored value is shown in Value), "
            "session_number, app_version, os_version and app_instance_id as stored. Names that start "
            "with an underscore are written by the SDK, not the app (Firebase does not accept app-chosen "
            "event names that start with an underscore) and this module does not expand them; "
            "other names are chosen by the app, and an event name does not by itself show that the user "
            "did what the name suggests. os_version is the value last written by the SDK, not necessarily "
            "the OS now installed. Not read: the tables of google-app-measurement.sql other than events and "
            "user_attributes (for example raw_events, queue and event_filters) and "
            "google_experimentation_database.sql. Only Containers/Data/Application is searched; app "
            "extension containers and app group containers are not. "
            "Evidence base: the author's own testing. The layout and these cross-checks were read in 2 "
            "research containers of one app: the Time of event '_f' equalled first_open_timestamp_ms to the "
            "second; the user property '_fot' was a whole number of hours in milliseconds; and '_sno' "
            "equalled session_number. The "
            "same store was seen in the container of at least one other app but was not read there. Other "
            "apps, SDK versions and app layouts are untested, and the fixtures are synthetic."
        ),
        "paths": (
            '*/Containers/Data/Application/*/Library/Application Support/Google/Measurement/google-app-measurement.sql*',
            '*/Containers/Data/Application/*/Library/Application Support/Google/Measurement/com.google.gmp.measurement.plist',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "chart-line",
    }
}

import datetime
import json
import os
import plistlib
import re
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               logfunc)

_METADATA = '.com.apple.mobile_container_manager.metadata.plist'
_CONTAINER_RX = re.compile(r'^(.*?/Containers/Data/Application/([^/]+))/', re.I)
_UUID_RX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
_STORE_DB = '/Google/Measurement/google-app-measurement.sql'
_STORE_PLIST = '/Google/Measurement/com.google.gmp.measurement.plist'
_UTC = datetime.timezone.utc

_MEASUREMENT_PREFIX = '/google/measurement/'
# (key, kind): kind is how the value is read.
_MEASUREMENT_KEYS = (
    ('first_open_timestamp_ms', 'ms'), ('last_uploaded_event_millis', 'ms'),
    ('last_engagement_end', 's'), ('last_successful_upload', 's'), ('last_failed_upload', 's'),
    ('session_number', 'n'), ('app_version', 'text'), ('os_version', 'text'), ('app_instance_id', 'text'),
)


def _norm(path):
    return str(path).replace('\\', '/')


def _container_bundles(files):
    """Map container prefix to the bundle id in its metadata plist."""
    bundles = {}
    for path in files:
        norm = _norm(path)
        if not norm.endswith('/' + _METADATA):
            continue
        match = _CONTAINER_RX.match(norm)
        if not match or norm.rsplit('/', 1)[0] != match.group(1):
            continue
        try:
            with open(path, 'rb') as handle:
                data = plistlib.load(handle)
        except (OSError, ValueError, TypeError, OverflowError, ExpatError, plistlib.InvalidFileException):
            logfunc(f'Google Measurement: unreadable container metadata; folder={match.group(2)}')
            continue
        identifier = data.get('MCMMetadataIdentifier') if isinstance(data, dict) else None
        if isinstance(identifier, str):
            bundles[match.group(1)] = identifier
    return bundles


def _app_of(match, bundles):
    """The bundle id of a container: from its metadata plist, else from a folder named by the id."""
    known = bundles.get(match.group(1))
    if known:
        return known
    folder = match.group(2)
    return '' if _UUID_RX.match(folder) else folder


def _epoch(value, unit='auto'):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value == 0 or value != value:
        return ''
    if unit == 'auto':
        unit = 'ms' if abs(value) >= 100_000_000_000 else 's'
    try:
        return datetime.datetime.fromtimestamp(value / (1000 if unit == 'ms' else 1), _UTC)
    except (ValueError, OverflowError, OSError):
        return ''


def _show(value):
    if isinstance(value, bytes):
        return value.hex() if len(value) <= 64 else value[:64].hex() + '...'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    return value


def _load_plist(path, label):
    try:
        with open(path, 'rb') as handle:
            data = plistlib.load(handle)
    except (OSError, ValueError, TypeError, OverflowError, ExpatError, plistlib.InvalidFileException):
        logfunc(f'Google Measurement: unreadable plist; {label}')
        return {}
    return data if isinstance(data, dict) else {}


def _database_rows(path, app, label):
    rows = []
    if does_table_exist_in_db(path, 'events'):
        for name, count, last_fire in get_sqlite_db_records(
                path, 'SELECT name, lifetime_count, last_fire_timestamp FROM events ORDER BY name'):
            rows.append((_epoch(last_fire), app, 'Event', name, '', count, ''))
    else:
        logfunc(f'Google Measurement: no events table; {label}')
    if does_table_exist_in_db(path, 'user_attributes'):
        for name, stamp, value, origin in get_sqlite_db_records(
                path, 'SELECT name, set_timestamp, value, origin FROM user_attributes ORDER BY name'):
            rows.append((_epoch(stamp), app, 'User Property', name, _show(value), '', origin))
    else:
        logfunc(f'Google Measurement: no user_attributes table; {label}')
    return rows


def _plist_rows(path, app, label):
    rows = []
    plist = _load_plist(path, label)
    for key, kind in _MEASUREMENT_KEYS:
        if _MEASUREMENT_PREFIX + key not in plist:
            continue
        value = plist[_MEASUREMENT_PREFIX + key]
        if kind in ('ms', 's'):
            when = _epoch(value, kind)
            rows.append((when, app, 'Measurement plist', key, value if when == '' else '', '', ''))
        else:
            rows.append(('', app, 'Measurement plist', key, _show(value), '', ''))
    return rows


@artifact_processor
def google_measurement_store(context):
    data_headers = (('Time', 'datetime'), 'App Bundle ID', 'Record Type', 'Name', 'Value', ('Count', 'number'),
                    'Origin')
    files = sorted({str(path) for path in context.get_files_found()})
    bundles = _container_bundles(files)
    rows = []
    sources = []
    for path in files:
        norm = _norm(path)
        is_database = norm.endswith(_STORE_DB)
        if not (is_database or norm.endswith(_STORE_PLIST)):
            continue
        match = _CONTAINER_RX.match(norm)
        if not match:
            continue
        app = _app_of(match, bundles)
        label = f'file={context.get_relative_path(path)}'
        sources.append(path)
        if is_database:
            rows.extend(_database_rows(os.path.abspath(path), app, label))
        else:
            rows.extend(_plist_rows(path, app, label))
    return data_headers, rows, '\n'.join(sources)
