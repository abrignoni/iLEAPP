__artifacts_v2__ = {
    "craigslist_recent_searches": {
        "name": "Craigslist - Recent Searches",
        "description": "Entries of recentSearches in the React Native AsyncStorage value persist:search of the "
                       "Craigslist app (org.craigslist.CraigslistMobile): search text, category, filters and the "
                       "search area stored with each entry.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Each entry timestamp is read as Unix milliseconds and shown in UTC. Read on three real "
                 "containers (installed app versions 1.27.0 and 1.29.1, see sample_data); the value is stored by "
                 "the app as one JSON object, kept "
                 "in a file named with the MD5 of the key when it is large and inline in manifest.json when it "
                 "is small, and both forms are read. Filters are listed as name=value as stored. Radius is shown "
                 "as stored: its unit is not established here. The search area is the area saved with the "
                 "search, not a device location. The list is a capped recent list (24 entries in the tested "
                 "samples), so absence of a search does not show that it was not made.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "local_ffs_a": "iOS FFS | 24 rows, ms timestamps, 1-2 filters per entry",
            "local_ffs_b": "iOS FFS | 24 rows",
            "local_ffs_c": "iOS FFS | recentSearches present and empty, 0 rows",
            "synthetic": "admin/test/cases: case_synthetic, 3 rows incl. an entry with no location",
        }
    },
    "craigslist_visited_postings": {
        "name": "Craigslist - Viewed Postings",
        "description": "Posting ids and times in visitedPostings of the persist:search value, with the title and "
                       "category when the same posting id is present in the app's URL cache (Cache.db).",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Times are Unix milliseconds shown in UTC. The map is read as the app's own record of when a "
                 "posting id was opened; the vendor does not document it. Of 28 viewed ids that also had a "
                 "cached detail request on three real containers, 14 had a Cache.db time within 60 seconds of "
                 "the viewed time, 8 a later cache time and 6 an earlier one, so the viewed time is not a "
                 "cache time. The map held 1, 85 and 178 ids on the three containers. Title and category are "
                 "filled only when a cached detail response for the id survives; blanks do not mean the "
                 "posting had no title. Entries in postingsNotFound and postingViewTelemetrySent are not "
                 "exported: the first was empty and the second held at most one id with an integer whose "
                 "meaning was not established.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/'
                  'org.craigslist.CraigslistMobile/Cache.db*',),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "local_ffs_a": "iOS FFS | 85 rows",
            "local_ffs_b": "iOS FFS | 178 rows",
            "local_ffs_c": "iOS FFS | 1 row",
            "synthetic": "admin/test/cases: case_synthetic, 3 rows, 2 with a cached title",
        }
    },
    "craigslist_saved_items": {
        "name": "Craigslist - Favorites, Hidden and Saved Searches",
        "description": "Entries in user.savedSearches of the persist:root value: favorite postings, hidden "
                       "postings and saved searches, with the sync state held in favoriteLookup and hiddenLookup.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Favorites were observed with one entry on one of three tested images and none on the others; the "
                 "favorite fields (posting id, title, posted date in Unix seconds, location description) are "
                 "read as stored. The hidden and saved-search lists were empty on every tested image, so "
                 "their field names are not established: those rows carry the entry as stored JSON in "
                 "Stored Entry and use the favorite field names only if the entry has them. Sync State is the "
                 "lookup value as stored (unsynched was the only value observed). A favorite is a "
                 "bookmark kept in the app; it does not show that the posting was contacted or answered.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',),
        "output_types": "standard",
        "artifact_icon": "star",
        "sample_data": {
            "local_ffs_a": "iOS FFS | 1 favorite, hidden and saved searches empty",
            "local_ffs_b": "iOS FFS | all lists empty, 0 rows",
            "local_ffs_c": "iOS FFS | all lists empty, 0 rows",
            "synthetic": "admin/test/cases: case_synthetic, 3 rows (favorite, hidden, saved search)",
        }
    },
    "craigslist_account_state": {
        "name": "Craigslist - Account and App State",
        "description": "Sign-in state, stored login, home area, permission states, app/config version and the "
                       "app's install identifier, read from persist:root, the preferences plist and "
                       "manifest.json.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "The login value is exported as stored; it was empty and isLoggedIn false on every tested "
                 "image, so how it is filled after sign-in was not observed. Access, push and cookie tokens "
                 "are NOT exported: only whether a value is present is shown. Device UID is the identifier "
                 "stored in the preferences plist under deviceUID; its use by the vendor is not established "
                 "here. Permission values are the strings the app stored (granted, denied, blocked, "
                 "undetermined, unavailable). Times are Unix milliseconds or seconds as noted in the Item "
                 "name and shown in UTC. Home Area is the area saved in the app, not a device location.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',
                  '*/mobile/Containers/Data/Application/*/Library/Preferences/'
                  'org.craigslist.CraigslistMobile.plist',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "user",
        "sample_data": {
            "local_ffs_a": "iOS FFS | signed out, 32 rows",
            "local_ffs_b": "iOS FFS | signed out, 32 rows",
            "local_ffs_c": "iOS FFS | signed out, 32 rows, extra token and permission keys present",
            "synthetic": "admin/test/cases: case_synthetic, signed in with a stored login",
        }
    },
    "craigslist_startup_log": {
        "name": "Craigslist - Startup Log",
        "description": "Entries of the startupLog key in the AsyncStorage manifest.json: ISO time, event and "
                       "detail, tab separated as stored.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Times are ISO 8601 UTC as stored. The log held one start sequence (init, onboarding, tab, "
                 "startup complete) on each tested image, so it is read as a short log of the most recent "
                 "start(s); it is not evidence of every launch.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/manifest.json',),
        "output_types": "standard",
        "artifact_icon": "player-play",
        "sample_data": {
            "local_ffs_a": "iOS FFS | 5 rows",
            "local_ffs_b": "iOS FFS | 5 rows",
            "local_ffs_c": "iOS FFS | 5 rows",
            "synthetic": "admin/test/cases: case_synthetic, 5 rows",
        }
    },
    "craigslist_cached_searches": {
        "name": "Craigslist - Cached Search Requests",
        "description": "Search-related requests held in the app's URL cache (Cache.db): search results, search "
                       "suggestions and category counts, with the query text and the area parameters in the "
                       "request.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Cache Time is the cfurl_cache_response time_stamp (UTC). Suggestion requests are sent while "
                 "text is entered, so a query on a suggestion row can be a partial entry. Entries exist only "
                 "while the system cache keeps them. Search Distance is shown as stored (unit not "
                 "established); latitude and longitude are the values sent in the request. Response Stored "
                 "says whether the body is in the database or in an fsCachedData file, which is not read here.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/'
                  'org.craigslist.CraigslistMobile/Cache.db*',),
        "output_types": "standard",
        "artifact_icon": "world-search",
        "sample_data": {
            "local_ffs_a": "iOS FFS | 35 rows",
            "local_ffs_b": "iOS FFS | 3 rows",
            "local_ffs_c": "iOS FFS | 17 rows",
            "synthetic": "admin/test/cases: case_synthetic, 4 rows",
        }
    },
    "craigslist_cached_postings": {
        "name": "Craigslist - Cached Posting Details",
        "description": "Posting detail responses held in the app's URL cache (Cache.db): title, category, price "
                       "string, posted and updated dates, location fields and the posting URL.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Cache Time is the cfurl_cache_response time_stamp (UTC). Posted and Updated are Unix seconds "
                 "shown in UTC. Record Created (as stored) is a Unix-seconds field whose meaning was not "
                 "established. Location fields are the posting's published location, which can be an "
                 "approximate area. Only responses stored inside the database are read; responses kept in "
                 "fsCachedData files are counted in the log but not parsed. A cached posting shows what the "
                 "app downloaded for that id, not that the user contacted the poster.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/'
                  'org.craigslist.CraigslistMobile/Cache.db*',),
        "output_types": "standard",
        "artifact_icon": "file-description",
        "sample_data": {
            "local_ffs_a": "iOS FFS | 49 rows, 7 bodies kept in fsCachedData and not parsed",
            "local_ffs_b": "iOS FFS | 31 rows, 1 body in fsCachedData",
            "local_ffs_c": "iOS FFS | 14 rows",
            "synthetic": "admin/test/cases: case_synthetic, 3 rows incl. one body kept on disk",
        }
    },
}

import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, unquote, urlparse

from scripts.ilapfuncs import (
    artifact_processor, get_plist_file_content, get_sqlite_db_records, logfunc,
)

BUNDLE = 'org.craigslist.CraigslistMobile'
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ASYNC_DIR = 'RCTAsyncLocalStorage_V1'
_RX_DETAIL = re.compile(r'^/v\d+/postings/([^/]+)/([^/]+)/([^/]+)/(\d+)/?$')
_RX_SEARCH = re.compile(r'^/v\d+/postings/([^/]+)/search/?$')
_RX_SUGGEST = re.compile(r'^/v\d+/suggest/search/?$')
_RX_COUNT = re.compile(r'^/v\d+/categories/count/?$')


def _ts(value, unit):
    """A UTC datetime from a number of seconds or milliseconds, or None when it is not usable."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return _EPOCH + timedelta(milliseconds=value) if unit == 'ms' else _EPOCH + timedelta(seconds=value)
    except (OverflowError, ValueError, OSError):
        return None


def _as_json(value):
    """A stored value as a Python object: an already-decoded value, or the JSON text of one."""
    if isinstance(value, str):
        text = value.strip()
        if text[:1] in ('{', '['):
            try:
                return json.loads(text)
            except ValueError:
                return None
        return None
    return value


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _text(value):
    """A cell value: scalars as they are, containers as compact JSON."""
    if value is None or isinstance(value, (str, int, float)):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _read_text(path):
    try:
        with open(path, 'rb') as handle:
            return handle.read().decode('utf-8', errors='replace')
    except OSError as err:
        logfunc(f'Craigslist: cannot read {os.path.basename(path)}: {err}')
        return None


def _async_stores(context):
    """AsyncStorage stores found, as a list of (manifest_path, {key: parsed value}).

    React Native keeps a small value inline in manifest.json and a large one in a file named with the
    lowercase MD5 hex of its key; a null manifest value points at that file. Both are read.
    """
    folders = {}
    for found in context.get_files_found():
        found = str(found)
        if os.path.isfile(found) and os.path.basename(os.path.dirname(found)) == _ASYNC_DIR:
            folders.setdefault(os.path.dirname(found), []).append(found)
    stores = []
    for folder in sorted(folders):
        manifest = os.path.join(folder, 'manifest.json')
        raw = _read_text(manifest) if os.path.isfile(manifest) else None
        if raw is None:
            continue
        try:
            entries = json.loads(raw)
        except ValueError:
            logfunc('Craigslist: manifest.json is not valid JSON')
            continue
        if not isinstance(entries, dict):
            continue
        store = {}
        for key, inline in entries.items():
            value = inline
            if value is None:
                hashed = os.path.join(folder, hashlib.md5(key.encode('utf-8')).hexdigest())
                value = _read_text(hashed) if os.path.isfile(hashed) else None
            store[key] = value
        stores.append((manifest, store))
    return stores


def _state(store, key):
    """The decoded persisted state under a key, as a dict (empty when missing or unreadable)."""
    return _dict(_as_json(store.get(key)))


def _paths(context, *parts):
    return '\n'.join(context.get_relative_path(p) for p in parts)


def _cache_dbs(context):
    return [str(f) for f in context.get_files_found()
            if os.path.basename(str(f)) == 'Cache.db' and os.path.isfile(str(f))]


def _cache_rows(db_path):
    """Rows of (entry_ID, time_stamp, request_key, isDataOnFS, receiver_data) or [] when the tables are missing."""
    query = '''
        SELECT r.entry_ID, r.time_stamp, r.request_key, d.isDataOnFS, d.receiver_data
        FROM cfurl_cache_response r
        LEFT JOIN cfurl_cache_receiver_data d ON d.entry_ID = r.entry_ID
    '''
    try:
        # absolute, because the SQLite URI helper mishandles a relative path on Windows
        records = get_sqlite_db_records(os.path.abspath(db_path), query)
        return [tuple(r) for r in records]
    except sqlite3.DatabaseError as err:
        logfunc(f'Craigslist Cache.db: {err}')
        return []


def _cache_time(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value).split('.')[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return value


def _detail_item(body):
    """The first item of a posting detail response, or None."""
    if body is None:
        return None
    if isinstance(body, memoryview):
        body = bytes(body)
    try:
        parsed = json.loads(body)
    except (ValueError, TypeError):
        return None
    items = _list(_dict(_dict(parsed).get('data')).get('items'))
    return items[0] if items and isinstance(items[0], dict) else None


def _cached_details(context):
    """{posting id: (cache time, item)} over every Cache.db found, newest entry wins."""
    found = {}
    for db_path in _cache_dbs(context):
        for _eid, stamp, url, on_disk, body in _cache_rows(db_path):
            match = _RX_DETAIL.match(urlparse(url or '').path)
            if not match or on_disk:
                continue
            item = _detail_item(body)
            if item is not None:
                found[match.group(4)] = (_cache_time(stamp), item)
    return found


@artifact_processor
def craigslist_recent_searches(context):
    headers = (('Search Time', 'datetime'), 'Search Text', 'Category Abbreviation', 'Category Labels',
               'Filters', 'City', 'Region', 'Postal Code', 'Country', ('Latitude', 'latitude'),
               ('Longitude', 'longitude'), 'Radius (as stored)', 'Area ID', 'Subarea ID', 'Area Site',
               'Source File')
    data_list = []
    sources = []
    for manifest, store in _async_stores(context):
        relative = context.get_relative_path(manifest)
        entries = _list(_state(store, 'persist:search').get('recentSearches'))
        if entries:
            sources.append(manifest)
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            location = _dict(entry.get('location'))
            labels = entry.get('categoryLabels')
            filters = []
            for item in _list(entry.get('humanReadableParams')):
                item = _dict(item)
                if item.get('key') != 'query':
                    filters.append(f"{item.get('key')}={item.get('value')}")
            data_list.append((
                _ts(entry.get('timestamp'), 'ms'), _dict(entry.get('params')).get('query'),
                entry.get('catabbr'), ' > '.join(map(str, labels)) if isinstance(labels, list) else _text(labels),
                '; '.join(filters), location.get('city'), location.get('region'), location.get('postal'),
                location.get('country'), location.get('lat'), location.get('lon'), location.get('radius'),
                location.get('areaId'), location.get('subareaId'), location.get('url'), relative))
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_visited_postings(context):
    headers = (('Viewed Time', 'datetime'), 'Posting ID', 'Cached Title', 'Cached Category',
               ('Cache Time', 'datetime'), 'Source File')
    details = _cached_details(context)
    data_list = []
    sources = []
    for manifest, store in _async_stores(context):
        relative = context.get_relative_path(manifest)
        visited = _dict(_state(store, 'persist:search').get('visitedPostings'))
        if visited:
            sources.append(manifest)
        for posting_id, when in visited.items():
            cache_time, item = details.get(str(posting_id), (None, {}))
            data_list.append((_ts(when, 'ms'), str(posting_id), item.get('title'), item.get('category'),
                              cache_time, relative))
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_saved_items(context):
    headers = (('Posted', 'datetime'), 'List', 'Posting ID', 'Posting UUID', 'Title', 'Category Abbreviation',
               'Category ID', 'Remuneration (as stored)', 'Location Description', 'Area Host',
               'Subarea Abbreviation', ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Sync State',
               'Stored Entry', 'Source File')
    lists = (('favorites', 'Favorite', 'favoriteLookup'), ('hidden', 'Hidden', 'hiddenLookup'),
             ('searches', 'Saved search', None))
    data_list = []
    sources = []
    for manifest, store in _async_stores(context):
        relative = context.get_relative_path(manifest)
        saved = _dict(_dict(_state(store, 'persist:root').get('user')).get('savedSearches'))
        used = False
        for key, label, lookup_key in lists:
            lookup = _dict(saved.get(lookup_key)) if lookup_key else {}
            for entry in _list(saved.get(key)):
                used = True
                entry = _dict(entry) if isinstance(entry, dict) else {'value': entry}
                location = _dict(entry.get('location'))
                posting_id = entry.get('postingId')
                data_list.append((
                    _ts(entry.get('postedDate'), 's'), label, posting_id, entry.get('postingUuid'),
                    entry.get('title'), entry.get('categoryAbbr'), entry.get('categoryId'),
                    entry.get('remuneration'), location.get('description'), location.get('hostname'),
                    location.get('subareaAbbr'), location.get('lat'), location.get('lon'),
                    _text(lookup.get(str(posting_id))) if posting_id is not None else None,
                    json.dumps(entry, ensure_ascii=False, separators=(',', ':')) if key != 'favorites' else '',
                    relative))
        if used:
            sources.append(manifest)
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_account_state(context):
    headers = (('Time', 'datetime'), 'Item', 'Value', 'Source File')
    data_list = []
    sources = []

    def add(rows, item, value, when=None, relative=''):
        if value is None or value == '':
            value = ''
        rows.append((when, item, _text(value), relative))

    for manifest, store in _async_stores(context):
        relative = context.get_relative_path(manifest)
        root = _state(store, 'persist:root')
        user = _dict(root.get('user'))
        config = _dict(root.get('config'))
        tokens = _dict(root.get('tokens'))
        before = len(data_list)
        if root:
            add(data_list, 'Is Logged In', user.get('isLoggedIn'), relative=relative)
            add(data_list, 'Login (as stored)', user.get('login'), relative=relative)
            home = _dict(user.get('location'))
            for name, key in (('Home Area City', 'city'), ('Home Area Region', 'region'),
                              ('Home Area Postal Code', 'postal'), ('Home Area Country', 'country'),
                              ('Home Area Latitude', 'lat'), ('Home Area Longitude', 'lon'),
                              ('Home Area Radius (as stored)', 'radius'), ('Home Area ID', 'areaId'),
                              ('Home Subarea ID', 'subareaId'), ('Home Area Site', 'url')):
                if key in home:
                    add(data_list, name, home.get(key), relative=relative)
            for name, key in (('Email App Setting', 'emailAppToUse'), ('Color Scheme Override', 'colorSchemeOverride'),
                              ('Push Token Sent (as stored)', 'pushTokenSent')):
                if key in user:
                    add(data_list, name, user.get(key), relative=relative)
            for key, value in _dict(root.get('permissions')).items():
                add(data_list, f'Permission: {key}', value, relative=relative)
            for name, key in (('Access Token Present', 'accessToken'), ('Browser Cookie Token Present', 'browserCookie'),
                              ('Push Token Present', 'pushToken')):
                if key in tokens:
                    add(data_list, name, 'Yes' if tokens.get(key) else 'No', relative=relative)
            if config.get('appVersion') is not None:
                add(data_list, 'Config App Version', config.get('appVersion'), relative=relative)
            if config.get('configTs') is not None:
                add(data_list, 'Config Timestamp (Unix seconds)', config.get('configTs'),
                    _ts(config.get('configTs'), 's'), relative)
            rating = _dict(user.get('ratingStatus'))
            for name, key in (('Last Day Used (Unix ms)', 'lastDayIUsedTheApp'),
                              ('Rating Startup Prompt Shown (Unix ms)', 'gotStartupPrompt'),
                              ('Rating Delete Prompt Shown (Unix ms)', 'gotDeletePrompt')):
                value = rating.get(key)
                if value:
                    add(data_list, name, value, _ts(value, 'ms'), relative)
            if 'daysInARow' in rating:
                add(data_list, 'Days In A Row (as stored)', rating.get('daysInARow'), relative=relative)
        if len(data_list) > before:
            sources.append(manifest)
    for found in context.get_files_found():
        found = str(found)
        if os.path.basename(found) == f'{BUNDLE}.plist' and os.path.isfile(found):
            plist = get_plist_file_content(found)
            if isinstance(plist, dict) and plist.get('deviceUID') is not None:
                add(data_list, 'Device UID (as stored)', plist.get('deviceUID'),
                    relative=context.get_relative_path(found))
                sources.append(found)
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_startup_log(context):
    headers = (('Log Time', 'datetime'), 'Event', 'Detail', 'Source File')
    data_list = []
    sources = []
    for manifest, store in _async_stores(context):
        raw = store.get('startupLog')
        if not isinstance(raw, str):
            continue
        relative = context.get_relative_path(manifest)
        sources.append(manifest)
        for line in raw.split('\n'):
            line = line[1:] if line.startswith(',') else line
            if not line.strip():
                continue
            parts = line.split('\t')
            when = None
            try:
                when = datetime.strptime(parts[0], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            except ValueError:
                when = parts[0]
            data_list.append((when, parts[1] if len(parts) > 1 else '', '\t'.join(parts[2:]).strip(), relative))
    return headers, data_list, _paths(context, *sources) if sources else ''


def _first(params, name):
    values = params.get(name)
    return unquote(values[0]) if values else None


def _number(text):
    try:
        return float(text) if text is not None else None
    except ValueError:
        return text


@artifact_processor
def craigslist_cached_searches(context):
    headers = (('Cache Time', 'datetime'), 'Request Type', 'Search Text', 'Category', 'Search Distance (as stored)',
               'Area ID', ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Start Index', 'Batch Size',
               'Response Stored', 'Request URL', 'Source File')
    data_list = []
    sources = []
    for db_path in _cache_dbs(context):
        relative = context.get_relative_path(db_path)
        used = False
        for _eid, stamp, url, on_disk, _body in _cache_rows(db_path):
            parsed = urlparse(url or '')
            path = parsed.path
            if _RX_SEARCH.match(path):
                kind, category = 'Search results', _RX_SEARCH.match(path).group(1)
            elif _RX_SUGGEST.match(path):
                kind, category = 'Search suggestions', None
            elif _RX_COUNT.match(path):
                kind, category = 'Category counts', None
            else:
                continue
            params = parse_qs(parsed.query)
            data_list.append((
                _cache_time(stamp), kind, _first(params, 'query'), category or _first(params, 'catabbr'),
                _number(_first(params, 'search_distance')),
                _first(params, 'area_id') or _first(params, 'areaId'),
                _number(_first(params, 'lat')), _number(_first(params, 'lon')),
                _first(params, 'startIndex'), _first(params, 'batchSize'),
                'fsCachedData file' if on_disk else 'Database', url, relative))
            used = True
        if used:
            sources.append(db_path)
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_cached_postings(context):
    headers = (('Cache Time', 'datetime'), 'Posting ID', 'Title', 'Category', 'Category Abbreviation',
               'Price', ('Posted', 'datetime'), ('Updated', 'datetime'),
               ('Record Created (as stored)', 'datetime'), 'Location Description', 'Location Area',
               'Neighborhood', 'Location Type', ('Latitude', 'latitude'), ('Longitude', 'longitude'),
               'Image Count', 'Has Contact Info', 'Posting URL', 'Body', 'Source File')
    data_list = []
    sources = []
    on_disk_count = 0
    for db_path in _cache_dbs(context):
        relative = context.get_relative_path(db_path)
        used = False
        for _eid, stamp, url, on_disk, body in _cache_rows(db_path):
            if not _RX_DETAIL.match(urlparse(url or '').path):
                continue
            if on_disk:
                on_disk_count += 1
                continue
            item = _detail_item(body)
            if item is None:
                continue
            location = _dict(item.get('location'))
            images = item.get('images')
            data_list.append((
                _cache_time(stamp), str(item.get('postingId', _RX_DETAIL.match(urlparse(url).path).group(4))),
                item.get('title'), item.get('category'), item.get('categoryAbbr'),
                item.get('priceString'), _ts(item.get('postedDate'), 's'), _ts(item.get('updatedDate'), 's'),
                _ts(item.get('recordCreated'), 's'), location.get('description'), location.get('area'),
                location.get('neighborhood'), location.get('type'), location.get('lat'), location.get('lon'),
                len(images) if isinstance(images, list) else None, item.get('hasContactInfo'),
                item.get('url'), item.get('body'), relative))
            used = True
        if used:
            sources.append(db_path)
    if on_disk_count:
        logfunc(f'Craigslist: {on_disk_count} cached posting response(s) are kept in fsCachedData files and were not parsed')
    return headers, data_list, _paths(context, *sources) if sources else ''
