__artifacts_v2__ = {
    "craigslist_recent_searches": {
        "name": "Craigslist - Recent Searches",
        "description": "Entries of recentSearches in the React Native AsyncStorage value persist:search of the "
                       "Craigslist app (org.craigslist.CraigslistMobile): search text, category, filters and the "
                       "search area stored with each entry.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Each entry timestamp is read as Unix milliseconds and shown in UTC. The value is stored by "
                 "the app as one JSON object, kept "
                 "in a file named with the MD5 of the key when it is large and inline in manifest.json when it "
                 "is small, and both forms are read. Filters are listed as key=value from humanReadableParams, with the query entry left out. Radius is shown "
                 "as stored: its unit is not established here. The search area is the area saved with the "
                 "search, not a device location. The longest list seen in the research containers held 24 entries; "
                 "whether the app caps it at that number is not established, so absence of a search does not show that it was not made. "
                 "The rows come from the AsyncStorage storage of the container: manifest.json, or the MD5-named file for a value kept there. The source path line lists each file read, so there is no Source File column. Evidence base: the author's own testing on 3 research containers (installed app versions 1.27.0, 1.27.0 and 1.29.1) and on synthetic fixtures; what is said here about what was seen rests on those three containers, and other app versions are untested.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "craigslist_visited_postings": {
        "name": "Craigslist - Viewed Postings",
        "description": "Posting ids and times in visitedPostings of the persist:search value, with the title and "
                       "category when a detail response for the same posting id is stored inside Cache.db "
                       "(responses kept in fsCachedData files are not read).",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Times are Unix milliseconds shown in UTC. The map is read as the app's own record of when a "
                 "posting id was opened. No vendor documentation of it was found. Of 28 viewed ids that also had a "
                 "cached detail request across the three research containers, 14 had a Cache.db time within 60 seconds of "
                 "the viewed time, 8 a later cache time and 6 an earlier one, so the viewed time is not a "
                 "cache time. The map held 1, 85 and 178 ids in the three containers. Title and category are "
                 "filled only when a detail response for the id is stored inside Cache.db; a detail response kept in an "
                 "fsCachedData file is not read, so for that posting id Cache Time, Cached Title and Cached Category stay blank. Cache Time is the cfurl_cache_response time_stamp (UTC) of one cached detail response for the id; when several are cached, which one is shown is not controlled. Blanks do not mean the "
                 "posting had no title. Entries in postingsNotFound and postingViewTelemetrySent are not "
                 "exported: the first was empty and the second held at most one id with an integer whose "
                 "meaning was not established. The rows come from the AsyncStorage storage of the container (manifest.json, or the MD5-named file for a value kept there), and the cache columns from Cache.db. The source path line lists each file read, so there is no Source File column. Evidence base: the author's own testing on 3 research containers (installed app versions 1.27.0, 1.27.0 and 1.29.1) and on synthetic fixtures; what is said here about what was seen rests on those three containers, and other app versions are untested.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/'
                  'org.craigslist.CraigslistMobile/Cache.db*',),
        "output_types": "standard",
        "artifact_icon": "eye",
    },
    "craigslist_saved_items": {
        "name": "Craigslist - Favorites, Hidden and Saved Searches",
        "description": "Entries in user.savedSearches of the persist:root value: favorite postings, hidden "
                       "postings and saved searches, with the sync state held in favoriteLookup and hiddenLookup.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Favorites were seen as one entry in one of the three research containers and none in the others, so "
                 "the favorite fields (posting id, title, posted date in Unix seconds, location description) are "
                 "read as stored from a single observed entry. The hidden and saved-search lists were empty in "
                 "all three containers, so "
                 "their field names are not established: those rows carry the entry in "
                 "Stored Entry and use the favorite field names only if the entry has them. Sync State is the "
                 "lookup value as stored (unsynched was the only value observed). Posted is the posting's own date; the entry fields read here hold no save time. "
                 "Stored Entry is the entry re-serialised as compact JSON (filled for hidden and saved-search rows, empty for favorites); an entry that is not a JSON object is wrapped under the key value. A favorite is a "
                 "bookmark kept in the app; it does not show that the posting was contacted or answered. The rows come from the AsyncStorage storage of the container: manifest.json, or the MD5-named file for a value kept there. The source path line lists each file read, so there is no Source File column. Evidence base: the author's own testing on 3 research containers (installed app versions 1.27.0, 1.27.0 and 1.29.1) and on synthetic fixtures; what is said here about what was seen rests on those three containers, and other app versions are untested.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',),
        "output_types": "standard",
        "artifact_icon": "star",
    },
    "craigslist_account_state": {
        "name": "Craigslist - Account and App State",
        "description": "Sign-in state, stored login, home area, permission states, app/config version and the "
                       "deviceUID value from the preferences plist, read from persist:root, the preferences plist and "
                       "manifest.json.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "The login value is exported as stored; it was empty and isLoggedIn false in all three "
                 "research containers, so how it is filled after sign-in was not observed. Access, push and cookie tokens "
                 "are NOT exported: only whether a value is present is shown. Device UID is the identifier "
                 "stored in the preferences plist under deviceUID; its use by the vendor is not established "
                 "here. Permission values are shown as the strings the app stored; the set of possible values is not established here. Times are Unix milliseconds or seconds as noted in the Item "
                 "name and shown in UTC. Home Area is the area saved in the app, not a device location. "
                 "The Device UID row is read from the preferences plist and every other row from the "
                 "AsyncStorage storage (manifest.json, or the MD5-named file for a value kept there). The source path line lists each file read, so there is no Source File column. Evidence base: the author's own testing on 3 research containers (installed app versions 1.27.0, 1.27.0 and 1.29.1) and on synthetic fixtures; what is said here about what was seen rests on those three containers, and other app versions are untested.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/*',
                  '*/mobile/Containers/Data/Application/*/Library/Preferences/'
                  'org.craigslist.CraigslistMobile.plist',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "user",
    },
    "craigslist_startup_log": {
        "name": "Craigslist - Startup Log",
        "description": "Entries of the startupLog key in the AsyncStorage manifest.json: log time, event and "
                       "detail, with the detail text trimmed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Times in the app's ISO format are parsed and shown as UTC datetimes; a value in another shape is passed on unparsed. The log held one start sequence (init, onboarding, tab, "
                 "startup complete) in each of the three research containers, so it is read as a short log of "
                 "the most recent start(s); it is not evidence of every launch. The rows come from the startupLog value in manifest.json; a value kept in an MD5-named file is not read by this artifact. The source path line lists each manifest read, so there is no Source File column. Evidence base: the author's own testing on 3 research containers (installed app versions 1.27.0, 1.27.0 and 1.29.1) and on synthetic fixtures; what is said here about what was seen rests on those three containers, and other app versions are untested.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/'
                  'org.craigslist.CraigslistMobile/RCTAsyncLocalStorage_V1/manifest.json',),
        "output_types": "standard",
        "artifact_icon": "player-play",
    },
    "craigslist_cached_searches": {
        "name": "Craigslist - Cached Search Requests",
        "description": "Search-related requests held in the app's URL cache (Cache.db): search results, search "
                       "suggestions and category counts, with the query text and the area parameters in the "
                       "request.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Cache Time is the cfurl_cache_response time_stamp (UTC). In our testing, suggestion requests were "
                 "seen while text was being entered, so a query on a suggestion row can be a partial entry. Entries exist only "
                 "while the system cache keeps them. Search Distance is shown as a number when it parses as one (unit not "
                 "established); latitude and longitude are the values sent in the request. Response Stored "
                 "says whether the body is in the database or in an fsCachedData file, which is not read here. The rows come from the Cache.db of the container, so there is no Source File column; the source path line of the artifact lists the Cache.db or Cache.db files read. Evidence base: the author's own testing on 3 research containers (installed app versions 1.27.0, 1.27.0 and 1.29.1) and on synthetic fixtures; what is said here about what was seen rests on those three containers, and other app versions are untested.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/'
                  'org.craigslist.CraigslistMobile/Cache.db*',),
        "output_types": "standard",
        "artifact_icon": "world-search",
    },
    "craigslist_cached_postings": {
        "name": "Craigslist - Cached Posting Details",
        "description": "Posting detail responses held in the app's URL cache (Cache.db): title, category, price "
                       "string, posted and updated dates, location fields and the posting URL.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Craigslist",
        "notes": "Cache Time is the cfurl_cache_response time_stamp (UTC). Posted and Updated are Unix seconds "
                 "shown in UTC. Record Created is read as Unix seconds and shown in UTC; its meaning was not "
                 "established. Location fields are the posting's published location; Location Type is shown as stored. Only responses stored inside the database are read; responses kept in "
                 "fsCachedData files are counted in the log but not parsed. A cached posting shows what the "
                 "app downloaded for that id, not that the user contacted the poster. The rows come from the Cache.db of the container, so there is no Source File column; the source path line of the artifact lists the Cache.db or Cache.db files read. Evidence base: the author's own testing on 3 research containers (installed app versions 1.27.0, 1.27.0 and 1.29.1) and on synthetic fixtures; what is said here about what was seen rests on those three containers, and other app versions are untested.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Caches/'
                  'org.craigslist.CraigslistMobile/Cache.db*',),
        "output_types": "standard",
        "artifact_icon": "file-description",
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
    """AsyncStorage stores found, as a list of (manifest_path, {key: parsed value}, {key: value file read}).

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
        value_files = {}
        for key, inline in entries.items():
            value = inline
            if value is None:
                hashed = os.path.join(folder, hashlib.md5(key.encode('utf-8')).hexdigest())
                value = _read_text(hashed) if os.path.isfile(hashed) else None
                if value is not None:
                    value_files[key] = hashed
            store[key] = value
        stores.append((manifest, store, value_files))
    return stores


def _store_sources(manifest, value_files, *keys):
    """The manifest plus the MD5-named value file of each key that was read from one."""
    return [manifest] + [value_files[k] for k in keys if k in value_files]


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
    """{posting id: (cache time, item, Cache.db path)} over every Cache.db found; the last matching row read wins."""
    found = {}
    for db_path in _cache_dbs(context):
        for _eid, stamp, url, on_disk, body in _cache_rows(db_path):
            match = _RX_DETAIL.match(urlparse(url or '').path)
            if not match or on_disk:
                continue
            item = _detail_item(body)
            if item is not None:
                found[match.group(4)] = (_cache_time(stamp), item, db_path)
    return found


@artifact_processor
def craigslist_recent_searches(context):
    headers = (('Search Time', 'datetime'), 'Search Text', 'Category Abbreviation', 'Category Labels',
               'Filters', 'City', 'Region', 'Postal Code', 'Country', ('Latitude', 'latitude'),
               ('Longitude', 'longitude'), 'Radius (as stored)', 'Area ID', 'Subarea ID', 'Area Site')
    data_list = []
    sources = []
    for manifest, store, value_files in _async_stores(context):
        entries = _list(_state(store, 'persist:search').get('recentSearches'))
        if entries:
            sources.extend(_store_sources(manifest, value_files, 'persist:search'))
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
                location.get('areaId'), location.get('subareaId'), location.get('url')))
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_visited_postings(context):
    headers = (('Viewed Time', 'datetime'), ('Cache Time', 'datetime'), 'Posting ID', 'Cached Title',
               'Cached Category')
    details = _cached_details(context)
    data_list = []
    sources = []
    for manifest, store, value_files in _async_stores(context):
        visited = _dict(_state(store, 'persist:search').get('visitedPostings'))
        if visited:
            sources.extend(_store_sources(manifest, value_files, 'persist:search'))
        for posting_id, when in visited.items():
            cache_time, item, db_path = details.get(str(posting_id), (None, {}, None))
            if db_path and db_path not in sources:
                sources.append(db_path)
            data_list.append((_ts(when, 'ms'), cache_time, str(posting_id), item.get('title'),
                              item.get('category')))
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_saved_items(context):
    headers = (('Posted', 'datetime'), 'List', 'Posting ID', 'Posting UUID', 'Title', 'Category Abbreviation',
               'Category ID', 'Remuneration (as stored)', 'Location Description', 'Area Host',
               'Subarea Abbreviation', ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Sync State',
               'Stored Entry')
    lists = (('favorites', 'Favorite', 'favoriteLookup'), ('hidden', 'Hidden', 'hiddenLookup'),
             ('searches', 'Saved search', None))
    data_list = []
    sources = []
    for manifest, store, value_files in _async_stores(context):
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
                    json.dumps(entry, ensure_ascii=False, separators=(',', ':')) if key != 'favorites' else ''))
        if used:
            sources.extend(_store_sources(manifest, value_files, 'persist:root'))
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_account_state(context):
    headers = (('Time', 'datetime'), 'Item', 'Value')
    data_list = []
    sources = []

    def add(rows, item, value, when=None):
        if value is None or value == '':
            value = ''
        rows.append((when, item, _text(value)))

    for manifest, store, value_files in _async_stores(context):
        root = _state(store, 'persist:root')
        user = _dict(root.get('user'))
        config = _dict(root.get('config'))
        tokens = _dict(root.get('tokens'))
        before = len(data_list)
        if root:
            add(data_list, 'Is Logged In', user.get('isLoggedIn'))
            add(data_list, 'Login (as stored)', user.get('login'))
            home = _dict(user.get('location'))
            for name, key in (('Home Area City', 'city'), ('Home Area Region', 'region'),
                              ('Home Area Postal Code', 'postal'), ('Home Area Country', 'country'),
                              ('Home Area Latitude', 'lat'), ('Home Area Longitude', 'lon'),
                              ('Home Area Radius (as stored)', 'radius'), ('Home Area ID', 'areaId'),
                              ('Home Subarea ID', 'subareaId'), ('Home Area Site', 'url')):
                if key in home:
                    add(data_list, name, home.get(key))
            for name, key in (('Email App Setting', 'emailAppToUse'), ('Color Scheme Override', 'colorSchemeOverride'),
                              ('Push Token Sent State (as stored)', 'pushTokenSent')):
                if key in user:
                    add(data_list, name, user.get(key))
            for key, value in _dict(root.get('permissions')).items():
                add(data_list, f'Permission: {key}', value)
            for name, key in (('Access Token Present', 'accessToken'), ('Browser Cookie Token Present', 'browserCookie'),
                              ('Push Token Present', 'pushToken')):
                if key in tokens:
                    add(data_list, name, 'Yes' if tokens.get(key) else 'No')
            if config.get('appVersion') is not None:
                add(data_list, 'Config App Version', config.get('appVersion'))
            if config.get('configTs') is not None:
                add(data_list, 'Config Timestamp (Unix seconds)', config.get('configTs'),
                    _ts(config.get('configTs'), 's'))
            rating = _dict(user.get('ratingStatus'))
            for name, key in (('Last Day Used (Unix ms)', 'lastDayIUsedTheApp'),
                              ('Rating Startup Prompt Shown (Unix ms)', 'gotStartupPrompt'),
                              ('Rating Delete Prompt Shown (Unix ms)', 'gotDeletePrompt')):
                value = rating.get(key)
                if value:
                    add(data_list, name, value, _ts(value, 'ms'))
            if 'daysInARow' in rating:
                add(data_list, 'Days In A Row (as stored)', rating.get('daysInARow'))
        if len(data_list) > before:
            sources.extend(_store_sources(manifest, value_files, 'persist:root'))
    for found in context.get_files_found():
        found = str(found)
        if os.path.basename(found) == f'{BUNDLE}.plist' and os.path.isfile(found):
            plist = get_plist_file_content(found)
            if isinstance(plist, dict) and plist.get('deviceUID') is not None:
                add(data_list, 'Device UID (as stored)', plist.get('deviceUID'))
                sources.append(found)
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_startup_log(context):
    headers = (('Log Time', 'datetime'), 'Event', 'Detail')
    data_list = []
    sources = []
    for manifest, store, value_files in _async_stores(context):
        raw = store.get('startupLog')
        if not isinstance(raw, str):
            continue
        sources.extend(_store_sources(manifest, value_files, 'startupLog'))
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
            data_list.append((when, parts[1] if len(parts) > 1 else '', '\t'.join(parts[2:]).strip()))
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
    headers = (('Cache Time', 'datetime'), 'Request Type', 'Search Text', 'Category', 'Search Distance',
               'Area ID', ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Start Index', 'Batch Size',
               'Response Stored', 'Request URL')
    data_list = []
    sources = []
    for db_path in _cache_dbs(context):
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
                'fsCachedData file' if on_disk else 'Database', url))
            used = True
        if used:
            sources.append(db_path)
    return headers, data_list, _paths(context, *sources) if sources else ''


@artifact_processor
def craigslist_cached_postings(context):
    headers = (('Cache Time', 'datetime'), 'Posting ID', 'Title', 'Category', 'Category Abbreviation',
               'Price', ('Posted', 'datetime'), ('Updated', 'datetime'),
               ('Record Created', 'datetime'), 'Location Description', 'Location Area',
               'Neighborhood', 'Location Type', ('Latitude', 'latitude'), ('Longitude', 'longitude'),
               'Image Count', 'Has Contact Info', 'Posting URL', 'Body')
    data_list = []
    sources = []
    on_disk_count = 0
    for db_path in _cache_dbs(context):
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
                item.get('url'), item.get('body')))
            used = True
        if used:
            sources.append(db_path)
    if on_disk_count:
        logfunc(f'Craigslist: {on_disk_count} cached posting response(s) are kept in fsCachedData files and were not parsed')
    return headers, data_list, _paths(context, *sources) if sources else ''
