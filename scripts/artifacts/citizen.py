__artifacts_v2__ = {
    "citizenColdLaunchLocations": {
        "name": "Citizen - Cold Launch Locations",
        "description": "Locations Citizen (com.sp0n.vigilante) stored under com.citizen.location.coldLaunchLocations "
                       "in its preferences.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("The key holds a JSON list in Library/Preferences/com.sp0n.vigilante.plist. Stored At is storedAt "
                  "and Location Timestamp is location.timestamp, both read as seconds since 2001-01-01 UTC: on one tested image that reading put a storedAt value within a second of a cached request time in the app's Cache.db. The other columns are the location's coordinate.latitude, "
                  "coordinate.longitude, horizontalAccuracy, altitude, verticalAccuracy, speed, speedAccuracy, "
                  "course and courseAccuracy as stored. On one tested image speed, speedAccuracy, course and courseAccuracy held one value on every row. Speed Accuracy and Course Accuracy each held one value across every location in the acquisitions tested."),
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.sp0n.vigilante.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Citizen 0.1296.0 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | Citizen 0.1301.0 | 2 rows",
        }
    },
    "citizenIncidentHistory": {
        "name": "Citizen - Viewed and Seen Incidents",
        "description": "Incident ids Citizen stored under com.citizen.recently_viewed_incidents and "
                       "com.citizen.recently_seen_incidents in its preferences.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("Both keys hold a JSON list in Library/Preferences/com.sp0n.vigilante.plist. List is the key the "
                  "row came from. Time is viewedAt or seenAt, read as seconds since 2001-01-01 UTC, the same "
                  "reading as Citizen - Cold Launch Locations. Incident ID is id or incidentId as stored. Title is "
                  "taken from the same container's cached map responses for that incident ID. Conflicting cached "
                  "titles leave Title blank. A cached title can postdate the preference entry. Title is blank when the "
                  "app's Cache.db holds none."),
        "paths": ('*/Containers/Data/Application/*/Library/Preferences/com.sp0n.vigilante.plist',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/Cache.db*',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/fsCachedData/*'),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Citizen 0.1296.0 | 6 rows",
            "hc_ios26": "iOS 26.5.2 | Citizen 0.1301.0 | 8 rows",
        }
    },
    "citizenCachedRequests": {
        "name": "Citizen - Cached API Requests",
        "description": "Requests to Citizen's API (data.sp0n.io) held in the app's URL cache, with the location, map "
                       "area and search parameters they carried.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
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
            "hc_ios18_7": "iOS 18.7.8 | Citizen 0.1296.0 | 210 rows",
            "hc_ios26": "iOS 26.5.2 | Citizen 0.1301.0 | 24 rows",
        }
    },
    "citizenAccount": {
        "name": "Citizen - Cached User Profiles",
        "description": "User profiles returned by a cached /v1/user/<id> response in the app's URL cache.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("One row per cached profile with an id from data.sp0n.io/v1/user/<id>. Column names are the response's keys "
                  "as stored. A cached profile alone does not identify the signed-in user. Requested User ID is the "
                  "ID in the URL and matched id on each tested profile. plus.active, protect.active and protect.status are taken from the nested objects. "
                  "Cached At is the cache row's time_stamp (UTC). No meaning is assigned to the keys. On one tested image firstName and lastName had no value. Across the acquisitions tested the same profile was cached: id, username, Requested User ID, email, phone, createdAt, languageCode, "
                  "private, avatarURL, avatarThumbURL, eligibleForReferralRewards, plus.active, protect.active "
                  "and protect.status each held one value. Other Profile Fields also held one value across those profiles and preserves additional response "
                  "properties as JSON. Cache Entry ID identifies the response within its Cache.db."),
        "paths": ('*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/Cache.db*',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/fsCachedData/*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Citizen 0.1296.0 | 1 row",
            "hc_ios26": "iOS 26.5.2 | Citizen 0.1301.0 | 1 row",
        }
    },
    "citizenMapIncidents": {
        "name": "Citizen - Cached Map Incidents",
        "description": "Incidents listed in cached /v3/homescreen/mapIncidents responses in the app's URL cache.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Citizen",
        "notes": ("One row per incident per cached response of data.sp0n.io/v3/homescreen/mapIncidents. List is the "
                  "response key the incident was under (incidents or inactiveIncidents). The other columns are the "
                  "incident's keys as stored; createdAt and updatedAt are shown as stored text. Cached At is the "
                  "cache row's time_stamp (UTC). An incident listed in several cached responses appears once per "
                  "response. Cache Entry ID identifies that response within its Cache.db. Other Incident Fields "
                  "preserves additional properties as JSON. On one tested image isAreaAlert and isGoodNews held one value on every row."),
        "paths": ('*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/Cache.db*',
                  '*/Containers/Data/Application/*/Library/Caches/com.sp0n.vigilante/fsCachedData/*'),
        "output_types": "standard",
        "artifact_icon": "alert-triangle",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Citizen 0.1296.0 | 159 rows",
            "hc_ios26": "iOS 26.5.2 | Citizen 0.1301.0 | 179 rows",
        }
    },
    "citizenNotificationImages": {
        "name": "Citizen - Notification Images",
        "description": "Images held in the URL cache of Citizen's notification service extension.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
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
            "hc_ios18_7": "iOS 18.7.8 | Citizen 0.1296.0 | 8 rows",
            "hc_ios26": "iOS 26.5.2 | Citizen 0.1301.0 | 8 rows",
        }
    },
}

import datetime
import json
import os
import plistlib
import sqlite3
import urllib.parse
from collections import defaultdict
from contextlib import closing
from pathlib import PurePosixPath

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media, logfunc,
                               open_sqlite_db_readonly)

_COCOA_EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
_API_HOST = 'data.sp0n.io'
_IMAGE_SIGNATURES = (b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n', b'GIF87a', b'GIF89a')


def _cocoa(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return _COCOA_EPOCH + datetime.timedelta(seconds=value)
        except (OverflowError, ValueError):
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
    for path in dict.fromkeys(map(str, context.get_files_found())):
        if os.path.basename(path) == 'com.sp0n.vigilante.plist':
            try:
                with open(path, 'rb') as handle:
                    prefs = plistlib.load(handle)
                if isinstance(prefs, dict):
                    yield prefs, path
            except (OSError, plistlib.InvalidFileException, ValueError) as ex:
                logfunc(f'Citizen: could not read {path}: {ex}')


def _json_list(prefs, key):
    raw = prefs.get(key)
    if isinstance(raw, (bytes, str)):
        try:
            raw = json.loads(raw)
        except ValueError:
            return []
    return raw if isinstance(raw, list) else []


# --- URL cache --------------------------------------------------------------------------------------

def _url_parts(url):
    if not isinstance(url, str):
        return None
    try:
        return urllib.parse.urlsplit(url)
    except ValueError:
        return None


def _cache_rows(context, folder, *, endpoint=None, metadata_only=False):
    """Stream rows. Load body files only for the endpoint that consumes them."""
    files = dict.fromkeys(map(str, context.get_files_found()))
    cache_files = {(os.path.dirname(path), os.path.basename(path)): path for path in files
                   if os.path.basename(os.path.dirname(path)) == 'fsCachedData'}
    if metadata_only:
        query = 'SELECT entry_ID, time_stamp, request_key, NULL, NULL FROM cfurl_cache_response'
    else:
        query = ('SELECT r.entry_ID, r.time_stamp, r.request_key, d.isDataOnFS, d.receiver_data '
                 'FROM cfurl_cache_response r LEFT JOIN cfurl_cache_receiver_data d USING (entry_ID)')
    for db_path in files:
        if not db_path.replace('\\', '/').endswith(f'/Library/Caches/{folder}/Cache.db'):
            continue
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            with closing(db):
                for entry_id, ts, url, on_fs, data in db.execute(query + ' ORDER BY time_stamp, entry_ID'):
                    parsed = _url_parts(url)
                    if folder == 'com.sp0n.vigilante':
                        if not parsed or parsed.scheme not in ('http', 'https') or parsed.hostname != _API_HOST:
                            continue
                        path = parsed.path.rstrip('/')
                        if endpoint == 'map' and path != '/v3/homescreen/mapIncidents':
                            continue
                        if endpoint == 'user' and not (path.startswith('/v1/user/') and path.count('/') == 3):
                            continue
                    body_path = ''
                    body = data if isinstance(data, bytes) else None
                    if on_fs:
                        name = data.decode('utf-8', 'replace') if isinstance(data, bytes) else data
                        body_path = cache_files.get((os.path.join(os.path.dirname(db_path), 'fsCachedData'), name), '')
                        body = None
                        if body_path:
                            try:
                                with open(body_path, 'rb') as handle:
                                    body = handle.read()
                            except OSError as error:
                                logfunc(f'Citizen: could not read cached body: {error}')
                    yield _cache_time(ts), url or '', parsed, entry_id, body, db_path, body_path
        except sqlite3.Error as error:
            logfunc(f'Citizen: could not read {db_path}: {error}')


def _cache_time(value):
    if not value:
        return None
    try:
        timestamp = datetime.datetime.fromisoformat(str(value))
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=datetime.timezone.utc)
        return timestamp.astimezone(datetime.timezone.utc)
    except ValueError:
        return None


def _json_body(body):
    if not body:
        return None
    try:
        return json.loads(body)
    except ValueError:
        return None


def _map_rows(context):
    for ts, _, _, entry, body, db, external in _cache_rows(context, 'com.sp0n.vigilante', endpoint='map'):
        data = _json_body(body)
        if isinstance(data, dict):
            for key in ('incidents', 'inactiveIncidents'):
                incidents = data.get(key)
                if isinstance(incidents, list):
                    for incident in incidents:
                        if isinstance(incident, dict):
                            yield ts, entry, key, incident, db, external


def _result(context, headers, sourced_rows, supporting=()):
    sources = {path for path, _ in sourced_rows}
    if len(sources) > 1:
        headers = (*headers, 'Source File')
        rows = [(*row, context.get_relative_path(path)) for path, row in sourced_rows]
    else:
        rows = [row for _, row in sourced_rows]
    return headers, rows, '\n'.join(sorted(sources.union(supporting)))


# --- artifacts --------------------------------------------------------------------------------------

@artifact_processor
def citizenColdLaunchLocations(context):
    data_list = []
    for prefs, source in _preferences(context):
        for entry in _json_list(prefs, 'com.citizen.location.coldLaunchLocations'):
            if not isinstance(entry, dict):
                continue
            location = entry.get('location') if isinstance(entry.get('location'), dict) else {}
            coordinate = location.get('coordinate') if isinstance(location.get('coordinate'), dict) else {}
            data_list.append((source, (
                _cocoa(entry.get('storedAt')), _cocoa(location.get('timestamp')),
                _blank(coordinate.get('latitude')), _blank(coordinate.get('longitude')),
                _blank(location.get('horizontalAccuracy')), _blank(location.get('altitude')),
                _blank(location.get('verticalAccuracy')), _blank(location.get('speed')),
                _blank(location.get('speedAccuracy')), _blank(location.get('course')),
                _blank(location.get('courseAccuracy')))))
    data_headers = (('Stored At', 'datetime'), ('Location Timestamp', 'datetime'), 'Latitude', 'Longitude',
                    'Horizontal Accuracy', 'Altitude', 'Vertical Accuracy', 'Speed', 'Speed Accuracy', 'Course',
                    'Course Accuracy')
    return _result(context, data_headers, data_list)


@artifact_processor
def citizenIncidentHistory(context):
    titles = defaultdict(set)
    title_sources = defaultdict(set)
    for _, _, _, incident, db, external in _map_rows(context):
        iid, title = incident.get('incidentId'), incident.get('title')
        if isinstance(iid, str) and isinstance(title, str) and title:
            # Cache.db is under Library/Caches/<bundle>/. The plist is under Library/Preferences/.
            library = PurePosixPath(context.get_relative_path(db).replace('\\', '/')).parents[2]
            titles[library, iid].add(title)
            title_sources[library, iid].add(db)
            if external:
                title_sources[library, iid].add(external)
    data_list = []
    supporting = set()
    for prefs, source in _preferences(context):
        library = PurePosixPath(context.get_relative_path(source).replace('\\', '/')).parents[1]
        for key, time_key, id_key in (('com.citizen.recently_viewed_incidents', 'viewedAt', 'id'),
                                      ('com.citizen.recently_seen_incidents', 'seenAt', 'incidentId')):
            for entry in _json_list(prefs, key):
                if not isinstance(entry, dict):
                    continue
                iid = _blank(entry.get(id_key))
                matches = titles.get((library, iid), set())
                title = next(iter(matches)) if len(matches) == 1 else ''
                if title:
                    supporting.update(title_sources[library, iid])
                data_list.append((source, (_cocoa(entry.get(time_key)), key, iid, title)))
    data_list.sort(key=lambda item: item[1][0] or _COCOA_EPOCH, reverse=True)
    data_headers = (('Time', 'datetime'), 'List', 'Incident ID', 'Title')
    return _result(context, data_headers, data_list, supporting)


@artifact_processor
def citizenCachedRequests(context):
    data_list = []
    for cached_at, url, parsed, entry, _, db_path, _ in _cache_rows(context, 'com.sp0n.vigilante', metadata_only=True):
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        first = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        used = ('lat', 'long', 'lowerLatitude', 'lowerLongitude', 'upperLatitude', 'upperLongitude', 'q')
        other = {k: v for k, v in first.items() if k not in used}
        data_list.append((db_path, (cached_at, parsed.path, *(_blank(first.get(k)) for k in used),
                                    json.dumps(other, ensure_ascii=False) if other else '', url, entry)))
    data_headers = (('Cached At', 'datetime'), 'Endpoint', 'Latitude', 'Longitude', 'Lower Latitude',
                    'Lower Longitude', 'Upper Latitude', 'Upper Longitude', 'Search Query', 'Other Parameters',
                    'URL', 'Cache Entry ID')
    return _result(context, data_headers, data_list)


_ACCOUNT_KEYS = ('id', 'username', 'email', 'phone', 'createdAt', 'firstName', 'lastName', 'languageCode', 'private',
                 'avatarURL', 'avatarThumbURL', 'eligibleForReferralRewards')


@artifact_processor
def citizenAccount(context):
    data_list = []
    supporting = set()
    for cached_at, _, parsed, entry, body, db_path, external in _cache_rows(context, 'com.sp0n.vigilante', endpoint='user'):
        data = _json_body(body)
        if not isinstance(data, dict) or type(data.get('id')) not in (str, int) or data['id'] == '':
            continue
        plus = data.get('plus') if isinstance(data.get('plus'), dict) else {}
        protect = data.get('protect') if isinstance(data.get('protect'), dict) else {}
        extra = {k: v for k, v in data.items() if k not in _ACCOUNT_KEYS}
        for key, shown in (('plus', ('active',)), ('protect', ('active', 'status'))):
            if isinstance(extra.get(key), dict):
                remainder = {k: v for k, v in extra[key].items() if k not in shown}
                if remainder:
                    extra[key] = remainder
                else:
                    del extra[key]
        requested = urllib.parse.unquote(parsed.path.rstrip('/').rsplit('/', 1)[-1])
        data_list.append((db_path, (cached_at,) + tuple(_blank(data.get(k)) for k in _ACCOUNT_KEYS) + (
            _blank(plus.get('active')), _blank(protect.get('active')), _blank(protect.get('status')), requested, entry, _blank(extra) if extra else '')))
        if external:
            supporting.add(external)
    data_headers = (('Cached At', 'datetime'),) + _ACCOUNT_KEYS + ('plus.active', 'protect.active', 'protect.status',
                                                                  'Requested User ID', 'Cache Entry ID', 'Other Profile Fields')
    return _result(context, data_headers, data_list, supporting)


_INCIDENT_KEYS = ('incidentId', 'title', 'latitude', 'longitude', 'createdAt', 'updatedAt', 'category',
                  'severity', 'level', 'isAreaAlert', 'isGoodNews', 'viewCount', 'shareCount', 'commentCount')


@artifact_processor
def citizenMapIncidents(context):
    data_list = []
    supporting = set()
    for cached_at, entry, list_key, incident, db, external in _map_rows(context):
        extra = {k: v for k, v in incident.items() if k not in _INCIDENT_KEYS}
        values = tuple(_blank(incident.get(k)) for k in _INCIDENT_KEYS)
        data_list.append((db, (cached_at, list_key, *values, entry, _blank(extra) if extra else '')))
        if external:
            supporting.add(external)
    data_headers = (('Cached At', 'datetime'), 'List') + _INCIDENT_KEYS + ('Cache Entry ID', 'Other Incident Fields')
    return _result(context, data_headers, data_list, supporting)


@artifact_processor
def citizenNotificationImages(context):
    data_list = []
    supporting = set()
    for cached_at, url, parsed, entry, body, db_path, file_path in _cache_rows(context, 'com.sp0n.vigilante.notificationServices'):
        image = ''
        if body and (body.startswith(_IMAGE_SIGNATURES) or (body[:4] == b'RIFF' and body[8:12] == b'WEBP')):
            name = os.path.basename(parsed.path if parsed else '') or 'image'
            if file_path:
                image = check_in_media(file_path, name)
            else:
                image = check_in_embedded_media(db_path, body, name) or ''
        data_list.append((db_path, (cached_at, image, url, len(body) if body is not None else '', entry)))
        if file_path:
            supporting.add(file_path)
    data_headers = (('Cached At', 'datetime'), ('Image', 'media'), 'URL', 'Size (bytes)', 'Cache Entry ID')
    return _result(context, data_headers, data_list, supporting)
