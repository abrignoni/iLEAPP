__artifacts_v2__ = {
    "citizenColdLaunchLocations": {
        "name": "Citizen - Cold Launch Locations",
        "description": "Locations Citizen (com.sp0n.vigilante) stored under com.citizen.location.coldLaunchLocations "
                       "in its preferences.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("The key holds a JSON list in Library/Preferences/com.sp0n.vigilante.plist. Stored At is storedAt "
                  "and Location Timestamp is location.timestamp, both read as seconds since 2001-01-01 UTC: on the "
                  "tested image that reading put the latest storedAt at the same second as the newest request in "
                  "the app's Cache.db. The other columns are the location's coordinate.latitude, "
                  "coordinate.longitude, horizontalAccuracy, altitude, verticalAccuracy, speed, speedAccuracy, "
                  "course and courseAccuracy as stored. On the tested image speed, speedAccuracy, course and "
                  "courseAccuracy held one value on both rows."),
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.sp0n.vigilante.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Citizen 0.1315.0 | 2 rows",
        }
    },
    "citizenIncidentHistory": {
        "name": "Citizen - Viewed and Seen Incidents",
        "description": "Incident ids Citizen stored under com.citizen.recently_viewed_incidents and "
                       "com.citizen.recently_seen_incidents in its preferences.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("Both keys hold a JSON list in Library/Preferences/com.sp0n.vigilante.plist. List is the key the "
                  "row came from. Time is viewedAt or seenAt, read as seconds since 2001-01-01 UTC, the same "
                  "reading as Citizen - Cold Launch Locations. Incident ID is id or incidentId as stored. Title is "
                  "taken from a cached map incidents response with the same incident id, and is blank when the "
                  "app's Cache.db holds none."),
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.sp0n.vigilante.plist',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/Cache.db*',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/fsCachedData/*'),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Citizen 0.1315.0 | 8 rows",
        }
    },
    "citizenCachedRequests": {
        "name": "Citizen - Cached API Requests",
        "description": "Requests to Citizen's API (data.sp0n.io) held in the app's URL cache, with the location, map "
                       "area and search parameters they carried.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("One row per cfurl_cache_response row of Library/Caches/com.sp0n.vigilante/Cache.db whose request "
                  "URL is on data.sp0n.io. Cached At is the row's time_stamp, stored as UTC text. Latitude and "
                  "Longitude are the request's lat and long parameters; the four map bound columns are "
                  "lowerLatitude, lowerLongitude, upperLatitude and upperLongitude; Search Query is q. Other "
                  "parameters are listed in Other Parameters. The cache holds only requests the app chose to "
                  "cache and keeps one row per request URL, so this is not a full history of the app's "
                  "requests."),
        "paths": ('*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/Cache.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Citizen 0.1315.0 | 133 rows",
        }
    },
    "citizenAccount": {
        "name": "Citizen - Account",
        "description": "The Citizen user record from a cached /v1/user/<id> response in the app's URL cache.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("One row per cached response of data.sp0n.io/v1/user/<id>. Column names are the response's keys "
                  "as stored; plus.active, protect.active and protect.status are taken from the nested objects. "
                  "Cached At is the cache row's time_stamp (UTC). No meaning is assigned to the keys. On the "
                  "tested image firstName and lastName had no value on the 1 row."),
        "paths": ('*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/Cache.db*',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/fsCachedData/*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Citizen 0.1315.0 | 1 row",
        }
    },
    "citizenMapIncidents": {
        "name": "Citizen - Cached Map Incidents",
        "description": "Incidents listed in cached /v3/homescreen/mapIncidents responses in the app's URL cache.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("One row per incident per cached response of data.sp0n.io/v3/homescreen/mapIncidents. List is the "
                  "response key the incident was under (incidents or inactiveIncidents). The other columns are the "
                  "incident's keys as stored; createdAt and updatedAt are shown as stored text. Cached At is the "
                  "cache row's time_stamp (UTC). An incident listed in several cached responses appears once per "
                  "response. On the tested image isAreaAlert and isGoodNews held one value on all 699 rows."),
        "paths": ('*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/Cache.db*',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/fsCachedData/*'),
        "output_types": "standard",
        "artifact_icon": "alert-triangle",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Citizen 0.1315.0 | 699 rows",
        }
    },
    "citizenNotificationImages": {
        "name": "Citizen - Notification Images",
        "description": "Images held in the URL cache of Citizen's notification service extension.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("One row per cfurl_cache_response row of Library/Caches/com.sp0n.vigilante.notificationServices/"
                  "Cache.db in the com.sp0n.vigilante.notificationServices extension container. Cached At is the "
                  "row's time_stamp (UTC). Image is the cached body, read from the database or from fsCachedData, "
                  "and attached only when it starts with a JPEG, PNG, GIF or WebP signature. That the extension "
                  "fetched an image does not show the notification was displayed or opened."),
        "paths": ('*/Containers/Data/PluginKitPlugin/*/Library/Caches/com.sp0n.vigilante.notificationServices/Cache.db*',
                  '*/Containers/Data/PluginKitPlugin/*/Library/Caches/com.sp0n.vigilante.notificationServices/'
                  'fsCachedData/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Citizen 0.1315.0 | 32 rows",
        }
    },
}

import datetime
import json
import os
import plistlib
import sqlite3
import urllib.parse

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media, logfunc,
                               open_sqlite_db_readonly)

_COCOA_EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
_API_HOST = 'data.sp0n.io'
_IMAGE_SIGNATURES = (b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n', b'GIF87a', b'GIF89a')


def _cocoa(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return _COCOA_EPOCH + datetime.timedelta(seconds=value)
        except OverflowError:
            return None
    return None


def _blank(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'True' if value else 'False'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


# --- preferences ------------------------------------------------------------------------------------

def _preferences(context):
    for file_found in context.get_files_found():
        path = str(file_found)
        if path.endswith('com.sp0n.vigilante.plist'):
            try:
                with open(path, 'rb') as handle:
                    return plistlib.load(handle), path
            except (OSError, plistlib.InvalidFileException, ValueError) as ex:
                logfunc(f'Citizen: could not read {path}: {ex}')
    return {}, ''


def _json_list(prefs, key):
    raw = prefs.get(key)
    if isinstance(raw, bytes):
        try:
            raw = json.loads(raw)
        except ValueError:
            return []
    return raw if isinstance(raw, list) else []


# --- URL cache --------------------------------------------------------------------------------------

def _cache_rows(context, folder):
    """[(time_stamp, url, body bytes or None, source db)] from the Cache.db in Library/Caches/<folder>/."""
    files = [str(f) for f in context.get_files_found()]
    rows = []
    for db_path in files:
        normalised = db_path.replace('\\', '/')
        if not normalised.endswith(f'/Library/Caches/{folder}/Cache.db'):
            continue
        cache_dir = os.path.dirname(db_path)
        on_disk = {os.path.basename(f): f for f in files
                   if os.path.dirname(f).replace('\\', '/') == cache_dir.replace('\\', '/') + '/fsCachedData'}
        try:
            db = open_sqlite_db_readonly(db_path)
            records = db.execute('''
                SELECT r.time_stamp, r.request_key, d.isDataOnFS, d.receiver_data
                FROM cfurl_cache_response r
                LEFT JOIN cfurl_cache_receiver_data d ON r.entry_ID = d.entry_ID
                ORDER BY r.time_stamp, r.entry_ID''').fetchall()
            db.close()
        except sqlite3.Error as ex:
            logfunc(f'Citizen: could not read {db_path}: {ex}')
            continue
        for time_stamp, url, on_fs, data in records:
            body = None
            if on_fs and data is not None:
                name = data.decode('utf-8', 'replace') if isinstance(data, bytes) else str(data)
                path = on_disk.get(name)
                if path:
                    try:
                        with open(path, 'rb') as handle:
                            body = handle.read()
                    except OSError:
                        body = None
                rows.append((_cache_time(time_stamp), url or '', body, db_path, path or ''))
            else:
                rows.append((_cache_time(time_stamp), url or '', data if isinstance(data, bytes) else None,
                             db_path, ''))
    return rows


def _cache_time(value):
    if not value:
        return None
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def _json_body(body):
    if not body:
        return None
    try:
        return json.loads(body)
    except ValueError:
        return None


def _map_incident_titles(rows):
    titles = {}
    for _, url, body, _, _ in rows:
        if '/homescreen/mapIncidents' in urllib.parse.urlparse(url).path:
            data = _json_body(body)
            if isinstance(data, dict):
                for key in ('incidents', 'inactiveIncidents'):
                    for incident in data.get(key) or []:
                        if isinstance(incident, dict) and incident.get('incidentId'):
                            titles[incident['incidentId']] = incident.get('title') or ''
    return titles


# --- artifacts --------------------------------------------------------------------------------------

@artifact_processor
def citizenColdLaunchLocations(context):
    prefs, source = _preferences(context)
    data_list = []
    for entry in _json_list(prefs, 'com.citizen.location.coldLaunchLocations'):
        if not isinstance(entry, dict):
            continue
        location = entry.get('location') if isinstance(entry.get('location'), dict) else {}
        coordinate = location.get('coordinate') if isinstance(location.get('coordinate'), dict) else {}
        data_list.append((
            _cocoa(entry.get('storedAt')), _cocoa(location.get('timestamp')),
            _blank(coordinate.get('latitude')), _blank(coordinate.get('longitude')),
            _blank(location.get('horizontalAccuracy')), _blank(location.get('altitude')),
            _blank(location.get('verticalAccuracy')), _blank(location.get('speed')),
            _blank(location.get('speedAccuracy')), _blank(location.get('course')),
            _blank(location.get('courseAccuracy'))))
    data_headers = (('Stored At', 'datetime'), ('Location Timestamp', 'datetime'), 'Latitude', 'Longitude',
                    'Horizontal Accuracy', 'Altitude', 'Vertical Accuracy', 'Speed', 'Speed Accuracy', 'Course',
                    'Course Accuracy')
    return data_headers, data_list, source


@artifact_processor
def citizenIncidentHistory(context):
    prefs, source = _preferences(context)
    titles = _map_incident_titles(_cache_rows(context, 'com.sp0n.vigilante'))
    data_list = []
    for key, time_key, id_key in (('com.citizen.recently_viewed_incidents', 'viewedAt', 'id'),
                                  ('com.citizen.recently_seen_incidents', 'seenAt', 'incidentId')):
        for entry in _json_list(prefs, key):
            if not isinstance(entry, dict):
                continue
            incident_id = entry.get(id_key) or ''
            data_list.append((_cocoa(entry.get(time_key)), key, incident_id, titles.get(incident_id, '')))
    data_list.sort(key=lambda row: row[0] or _COCOA_EPOCH, reverse=True)
    data_headers = (('Time', 'datetime'), 'List', 'Incident ID', 'Title')
    return data_headers, data_list, source


@artifact_processor
def citizenCachedRequests(context):
    data_list = []
    sources = set()
    for cached_at, url, _, db_path, _ in _cache_rows(context, 'com.sp0n.vigilante'):
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc != _API_HOST:
            continue
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        first = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        used = ('lat', 'long', 'lowerLatitude', 'lowerLongitude', 'upperLatitude', 'upperLongitude', 'q')
        other = {k: v for k, v in first.items() if k not in used}
        data_list.append((
            cached_at, parsed.path, first.get('lat', ''), first.get('long', ''), first.get('lowerLatitude', ''),
            first.get('lowerLongitude', ''), first.get('upperLatitude', ''), first.get('upperLongitude', ''),
            first.get('q', ''), json.dumps(other, ensure_ascii=False) if other else '', url))
        sources.add(db_path)
    data_headers = (('Cached At', 'datetime'), 'Endpoint', 'Latitude', 'Longitude', 'Lower Latitude',
                    'Lower Longitude', 'Upper Latitude', 'Upper Longitude', 'Search Query', 'Other Parameters',
                    'URL')
    return data_headers, data_list, '\n'.join(sorted(sources))


_ACCOUNT_KEYS = ('id', 'email', 'phone', 'createdAt', 'firstName', 'lastName', 'languageCode', 'private',
                 'avatarURL', 'avatarThumbURL', 'eligibleForReferralRewards')


@artifact_processor
def citizenAccount(context):
    data_list = []
    sources = set()
    for cached_at, url, body, db_path, file_path in _cache_rows(context, 'com.sp0n.vigilante'):
        parsed = urllib.parse.urlparse(url)
        parts = parsed.path.strip('/').split('/')
        if parsed.netloc != _API_HOST or len(parts) != 3 or parts[:2] != ['v1', 'user']:
            continue
        data = _json_body(body)
        if not isinstance(data, dict):
            continue
        plus = data.get('plus') if isinstance(data.get('plus'), dict) else {}
        protect = data.get('protect') if isinstance(data.get('protect'), dict) else {}
        data_list.append((cached_at,) + tuple(_blank(data.get(k)) for k in _ACCOUNT_KEYS) + (
            _blank(plus.get('active')), _blank(protect.get('active')), _blank(protect.get('status'))))
        sources.add(file_path or db_path)
    data_headers = (('Cached At', 'datetime'),) + _ACCOUNT_KEYS + ('plus.active', 'protect.active',
                                                                   'protect.status')
    return data_headers, data_list, '\n'.join(sorted(sources))


_INCIDENT_KEYS = ('incidentId', 'title', 'latitude', 'longitude', 'createdAt', 'updatedAt', 'category',
                  'severity', 'level', 'isAreaAlert', 'isGoodNews', 'viewCount', 'shareCount', 'commentCount')


@artifact_processor
def citizenMapIncidents(context):
    data_list = []
    sources = set()
    for cached_at, url, body, db_path, file_path in _cache_rows(context, 'com.sp0n.vigilante'):
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc != _API_HOST or '/homescreen/mapIncidents' not in parsed.path:
            continue
        data = _json_body(body)
        if not isinstance(data, dict):
            continue
        for list_key in ('incidents', 'inactiveIncidents'):
            for incident in data.get(list_key) or []:
                if isinstance(incident, dict):
                    data_list.append((cached_at, list_key) + tuple(_blank(incident.get(k)) for k in _INCIDENT_KEYS))
        sources.add(file_path or db_path)
    data_headers = (('Cached At', 'datetime'), 'List') + _INCIDENT_KEYS
    return data_headers, data_list, '\n'.join(sorted(sources))


@artifact_processor
def citizenNotificationImages(context):
    data_list = []
    sources = set()
    for cached_at, url, body, db_path, file_path in _cache_rows(context, 'com.sp0n.vigilante.notificationServices'):
        image = ''
        if body and (body.startswith(_IMAGE_SIGNATURES) or (body[:4] == b'RIFF' and body[8:12] == b'WEBP')):
            name = os.path.basename(urllib.parse.urlparse(url).path) or 'image'
            if file_path:
                image = check_in_media(file_path, name)
            else:
                image = check_in_embedded_media(db_path, body, name) or ''
        data_list.append((cached_at, image, url, len(body) if body else ''))
        sources.add(db_path)
    data_headers = (('Cached At', 'datetime'), ('Image', 'media'), 'URL', 'Size (bytes)')
    return data_headers, data_list, '\n'.join(sorted(sources))
