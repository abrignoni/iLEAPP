__artifacts_v2__ = {
    "offerup_app_state": {
        "name": "OfferUp - Account and App State",
        "description": "Account identifier, device and advertising identifiers, app versions, "
                       "onboarding progress and push-permission state kept by the OfferUp app "
                       "(com.offerup.iphone.consumer) in its redux store, React Native storage, "
                       "preferences and Statsig store.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "OfferUp",
        "notes": "The Account ID is read from the name of a React Native storage key of the form "
                 "<number>:<NAME>:<hex>; it is the number in the key, and the file does not say "
                 "that the account was signed in at acquisition. The item userHasLoggedInAtLeastOnce "
                 "is the redux store key of that name; its meaning beyond the name is not "
                 "established. The hex part of the storage key is reported as the Storage key "
                 "suffix, and its meaning is not established; the key pattern matches any NAME, "
                 "so the suffix is not tied to one key. App version last run (core.currentVersion) "
                 "and App version previous (core.previousVersion) are the values of those redux "
                 "store keys. Device ID and Advertising ID are the values the app wrote "
                 "under those names. The Statsig and AppsFlyer values are read from keys "
                 "carrying those SDK names. No listings, chat messages or meet-up details were "
                 "found stored in the two research containers; whether the app stores them "
                 "under other conditions is not established. Origin names the store a "
                 "row came from, which is why there is no Source File column. "
                 "Evidence base: the layouts were read from 2 research containers. The installed app versions are 2026.3.0 and 2026.9.0, but the stores in them record 2026.2.0 and 2026.8.0 as the version last run (VersionOfLastRun, core.currentVersion), so the stores were last written by those two builds; the test fixtures are synthetic, rebuilt from those layouts with invented values. Other app builds are untested. No app binary was analysed; everything here comes from the data containers.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/mobile/Containers/Data/Application/*/Documents/mmkv/redux*",
            "*/mobile/Containers/Data/Application/*/Documents/mmkv/statsig*",
            "*/mobile/Containers/Data/Application/*/Library/Preferences/com.offerup.iphone.consumer.plist",
            "*/mobile/Containers/Data/Application/*/Library/Application Support/"
            "com.offerup.iphone.consumer/RCTAsyncLocalStorage_V1/manifest.json",
        ),
        "output_types": "standard",
        "artifact_icon": "user-circle",
    },
    "offerup_locations": {
        "name": "OfferUp - Search and Posting Locations",
        "description": "Locations the OfferUp app stored: the area the user searches in, the "
                       "rentals search area and the location chosen in the posting flow.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "OfferUp",
        "notes": "These are places the user (or the app, from the device location) chose as a "
                 "search or posting area, not a record of where the device was at any time. The "
                 "posting location row has a Used GPS column taken from the stored didUseGPS "
                 "flag; for the other rows the file does not say how the place was chosen. "
                 "Only the value current at acquisition is read. State is read from the state "
                 "key; when that key is absent or empty, the adminArea key is used. In the "
                 "research containers the rentals coordinates are stored as text and are "
                 "converted to numbers. Kind tells which store a row came "
                 "from: the search and rentals locations are read from the redux store, the posting "
                 "location from React Native storage, so there is no Source File column. "
                 "Evidence base: the layouts were read from 2 research containers. The installed app versions are 2026.3.0 and 2026.9.0, but the stores in them record 2026.2.0 and 2026.8.0 as the version last run (VersionOfLastRun, core.currentVersion), so the stores were last written by those two builds; the test fixtures are synthetic, rebuilt from those layouts with invented values. Other app builds are untested. No app binary was analysed; everything here comes from the data containers.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/mobile/Containers/Data/Application/*/Documents/mmkv/redux*",
            "*/mobile/Containers/Data/Application/*/Library/Application Support/"
            "com.offerup.iphone.consumer/RCTAsyncLocalStorage_V1/manifest.json",
        ),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "map-pin",
    },
    "offerup_recent_searches": {
        "name": "OfferUp - Recent Searches",
        "description": "Search suggestions the OfferUp app kept under its recent-searches keys "
                       "in React Native storage.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "OfferUp",
        "notes": "Position is the place of the entry in the stored list; whether the list is "
                 "newest first is not established and no time is stored per entry. The Type, "
                 "Sub Label and Preposition columns are reported as stored and their meaning "
                 "beyond the names is not established. A value too large for the manifest is "
                 "kept by React Native in a separate file named by the MD5 of the key; that "
                 "file is read when it is present in the extraction. An entry is a suggestion "
                 "the app held for the user, which is not proof that the user ran that search. "
                 "The rows come from the React Native storage of the container: the manifest, or "
                 "the overflow file for that key when the value is kept there. Both are listed "
                 "as the source, so there is no Source File column. "
                 "Evidence base: the layouts were read from 2 research containers. The installed app versions are 2026.3.0 and 2026.9.0, but the stores in them record 2026.2.0 and 2026.8.0 as the version last run (VersionOfLastRun, core.currentVersion), so the stores were last written by those two builds; the test fixtures are synthetic, rebuilt from those layouts with invented values. Other app builds are untested. No app binary was analysed; everything here comes from the data containers.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/"
            "com.offerup.iphone.consumer/RCTAsyncLocalStorage_V1/*",
        ),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "offerup_listing_affinity": {
        "name": "OfferUp - Listing Affinity",
        "description": "Listing and category identifiers the OfferUp app keeps in its "
                       "feedAffinity redux store.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "OfferUp",
        "notes": "Read from the feedAffinity store of the redux state. The store holds a list of "
                 "listing and category identifiers (listingAffinities) and a comma separated "
                 "list of category identifiers (LAST_VIEWED_CATEGORIES). The file does not say "
                 "whether a listing was viewed, saved or contacted. In the one research container "
                 "that has a feedAffinity store, each listingAffinities entry holds only "
                 "listingId and categoryId, with no listing title, price, seller or time. "
                 "Position is the place in the stored list. The rows come from the one "
                 "redux store file of the container, so there is no Source File column. The "
                 "feedAffinity store was present in the 2026.9.0 container and absent in the 2026.3.0 "
                 "one. "
                 "Evidence base: the layouts were read from 2 research containers. The installed app versions are 2026.3.0 and 2026.9.0, but the stores in them record 2026.2.0 and 2026.8.0 as the version last run (VersionOfLastRun, core.currentVersion), so the stores were last written by those two builds; the test fixtures are synthetic, rebuilt from those layouts with invented values. Other app builds are untested. No app binary was analysed; everything here comes from the data containers.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/mobile/Containers/Data/Application/*/Documents/mmkv/redux*",
        ),
        "output_types": "standard",
        "artifact_icon": "list-details",
    },
    "offerup_chat_drafts": {
        "name": "OfferUp - Chat Drafts",
        "description": "Draft chat message text the OfferUp app kept per conversation "
                       "(chat_draft_message in React Native storage).",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "OfferUp",
        "notes": "The key under chat_draft_message is reported as Conversation ID; that it "
                 "identifies a conversation is read from the name chat_draft_message and is not "
                 "established by the file. A draft is text typed and not sent at the time of the "
                 "last write; whether the app clears a draft after sending is not established, "
                 "so a row does not prove the message was never sent. Sent and received chat "
                 "messages were not found stored in either research container. The rows come from "
                 "the React Native storage of the container: the manifest, or the overflow file "
                 "(named by the MD5 of the key) when the value is kept there. Both are listed as "
                 "the source, so there is no Source File column. "
                 "Evidence base: the layouts were read from 2 research containers. The installed app versions are 2026.3.0 and 2026.9.0, but the stores in them record 2026.2.0 and 2026.8.0 as the version last run (VersionOfLastRun, core.currentVersion), so the stores were last written by those two builds; the test fixtures are synthetic, rebuilt from those layouts with invented values. Other app builds are untested. No app binary was analysed; everything here comes from the data containers.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Application Support/"
            "com.offerup.iphone.consumer/RCTAsyncLocalStorage_V1/*",
        ),
        "output_types": "standard",
        "artifact_icon": "message-2",
    },
    "offerup_activity": {
        "name": "OfferUp - Activity and Timing",
        "description": "Times read from the OfferUp app's stores: Statsig sessions, the "
                       "LAST_REGISTERED_AT time, prompt counters, the Ably heartbeat time and the "
                       "install timestamps.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "OfferUp",
        "notes": "Statsig sessions come from the session_id entries of the Statsig MMKV store. "
                 "MMKV is append-only between rewrites, so superseded entries of the same session "
                 "can be present and are read too; the latest Last Update per session is "
                 "reported. The meaning of a Statsig session beyond the key names is not "
                 "established. For prompt counters, Time is the value of the "
                 "last successful run key and Last Update that of the last attempt key; both "
                 "are stored as Unix milliseconds and shown as UTC. The meaning of the profile_location_after_filter and "
                 "LAST_ACCOUNT_PAGE_REFRESH timestamps is not established beyond the key name. "
                 "The realtime heartbeat is the value of the lastHeartbeatTime key in the "
                 "ablyState entry of the redux store. The install times are the values of the "
                 "AppsFlyerInstallTimestamp and com.facebook.sdk:FBSDKSettingsInstallTimestamp "
                 "preference keys; "
                 "how they relate to the App Store install time is not established. Event tells which store a row came from "
                 "(Statsig session: the Statsig store; Prompt exposure, Push permission prompt shown "
                 "and Realtime (Ably) heartbeat: the redux store; the install timestamps: the app "
                 "preferences; Registration time (LAST_REGISTERED_AT), Prompt counter and Stored "
                 "time: React Native storage), so there is no Source File column. "
                 "Evidence base: the layouts were read from 2 research containers. The installed app versions are 2026.3.0 and 2026.9.0, but the stores in them record 2026.2.0 and 2026.8.0 as the version last run (VersionOfLastRun, core.currentVersion), so the stores were last written by those two builds; the test fixtures are synthetic, rebuilt from those layouts with invented values. Other app builds are untested. No app binary was analysed; everything here comes from the data containers.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist",
            "*/mobile/Containers/Data/Application/*/Documents/mmkv/redux*",
            "*/mobile/Containers/Data/Application/*/Documents/mmkv/statsig*",
            "*/mobile/Containers/Data/Application/*/Library/Preferences/com.offerup.iphone.consumer.plist",
            "*/mobile/Containers/Data/Application/*/Library/Application Support/"
            "com.offerup.iphone.consumer/RCTAsyncLocalStorage_V1/manifest.json",
        ),
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "offerup_network_cache": {
        "name": "OfferUp - Cached Network Responses",
        "description": "NSURLCache entries of the OfferUp app for OfferUp and Ably realtime "
                       "hosts, with the HTTP status, MIME type and the top-level keys of a JSON "
                       "body.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "OfferUp",
        "notes": "Only entries whose host contains offerup or is an Ably host are listed; the "
                 "cache also holds advertising and analytics requests, which are left out. "
                 "Cached is the time_stamp column of the cache row, stored as text without a "
                 "time zone and read as UTC. A cached request records that the app made it, not "
                 "that the user saw the content. Body Keys lists the top-level JSON keys only. "
                 "The body is parsed for those keys and its text is not reported. HTTP Status and MIME Type "
                 "are a heuristic read of the archived response: the status is the first "
                 "integer between 100 and 599 and the MIME type the first type-shaped string "
                 "in it, or a content-type header entry when there is none. Where the payload is "
                 "kept in a separate file (isDataOnFS) the body is not read. The rows come from "
                 "the one Cache.db of the container, so there is no Source File column. "
                 "Evidence base: the layouts were read from 2 research containers. The installed app versions are 2026.3.0 and 2026.9.0, but the stores in them record 2026.2.0 and 2026.8.0 as the version last run (VersionOfLastRun, core.currentVersion), so the stores were last written by those two builds; the test fixtures are synthetic, rebuilt from those layouts with invented values. Other app builds are untested. No app binary was analysed; everything here comes from the data containers.",
        "paths": (
            "*/mobile/Containers/Data/Application/*/Library/Caches/com.offerup.iphone.consumer/Cache.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "world-www",
    },
}

import datetime
import hashlib
import json
import os
import re
from urllib.parse import urlsplit

from scripts.ilapfuncs import (
    artifact_processor,
    convert_plist_date_to_utc,
    convert_ts_human_to_utc,
    convert_unix_ts_to_utc,
    get_plist_content,
    get_plist_file_content,
    get_sqlite_db_records,
    logfunc,
)
from scripts.mmkv_parser import MMKVError, decode_value, read_dict, read_entries

BUNDLE_ID = 'com.offerup.iphone.consumer'
METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
CONTAINER_RE = re.compile(r'/Containers/Data/Application/([0-9A-Fa-f-]{36})/')
ACCOUNT_KEY_RE = re.compile(r'^(\d+):([A-Za-z_]+):([0-9A-Fa-f]+)$')
OFFERUP_HOST_RE = re.compile(r'offerup|(^|\.)ably(-realtime)?\.(io|com)(:\d+)?$', re.I)

RECENT_SEARCH_KEYS = (('ou-recent-searches', 'Recent search'),
                      ('recent_searches_rentals', 'Recent rentals search'))
RUNNER_KEYS = ('PUSH_NOTIFICATION_PERMISSIONS_RUNNER_KEY', 'SELLER_INSIGHTS_FEATURE_HIGHLIGHT',
               'BUSINESS_TOOLS', 'BLOCKED_PUSH_NOTIFICATIONS_DIALOG_REQUEST',
               'SEARCH_ALERTS_HIGHLIGHT_RUNNER_KEY')
MILLISECOND_TEXT_KEYS = ('LAST_ACCOUNT_PAGE_REFRESH', 'PREMIUM_TAKEOVER_ENGAGEMENT_INTERVAL_KEY',
                         'profile_location_after_filter')


# --------------------------------------------------------------------------------------
# file and container helpers
# --------------------------------------------------------------------------------------

def _norm(path):
    return str(path).replace('\\', '/')


def _container_of(path):
    match = CONTAINER_RE.search(_norm(path))
    return match.group(1).upper() if match else ''


def _offerup_containers(files_found):
    """UUIDs of the data containers that belong to OfferUp.

    A container counts when its metadata plist names the bundle id, or when one of its
    files lives under a path that carries the bundle id (preferences, storage folder,
    cache folder). The redux and Statsig MMKV stores sit in Documents/mmkv, a name other
    React Native apps use too, so they are read only from these containers.
    """
    found = set()
    for file_found in files_found:
        path = _norm(file_found)
        uuid = _container_of(path)
        if not uuid:
            continue
        if path.endswith('/' + METADATA_NAME):
            content = get_plist_file_content(str(file_found))
            if isinstance(content, dict) and content.get('MCMMetadataIdentifier') == BUNDLE_ID:
                found.add(uuid)
        elif BUNDLE_ID in path:
            found.add(uuid)
    return found


def _select(files_found, containers, tail_re):
    """Files of OfferUp containers whose normalised path matches tail_re."""
    selected = []
    for file_found in files_found:
        path = _norm(file_found)
        if _container_of(path) in containers and re.search(tail_re, path) and os.path.isfile(str(file_found)):
            selected.append(str(file_found))
    return selected


def _load_json(value):
    """Parse JSON text; anything else (or text that is not JSON) is returned unchanged."""
    if isinstance(value, (bytes, bytearray)):
        try:
            value = bytes(value).decode('utf-8')
        except UnicodeDecodeError:
            return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return value
    return value


def _redux_state(path):
    """The redux-persist stores of a redux MMKV file as {store: {field: value}}.

    redux-persist writes one MMKV key per store (persist:<store>) whose value is a JSON
    object, and each field of that object is itself a JSON encoded string.
    """
    try:
        raw = read_dict(path)
    except (MMKVError, OSError, ValueError) as err:
        logfunc(f'OfferUp: redux store not readable ({type(err).__name__})')
        return {}
    state = {}
    for key, value in raw.items():
        if not (isinstance(key, str) and key.startswith('persist:')):
            continue
        store = _load_json(value)
        if not isinstance(store, dict):
            continue
        state[key[len('persist:'):]] = {
            name: _load_json(field) for name, field in store.items() if name != '_persist'
        }
    return state


def _manifest(path):
    """React Native AsyncStorage manifest as {key: value}, or {} when unreadable."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            content = json.load(handle)
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    return content if isinstance(content, dict) else {}


def _async_value(manifest, key, storage_dir):
    """(value, overflow path) for key.

    The value is the manifest entry, or the content of the overflow file React Native
    names by MD5(key). The path is that overflow file when the value came from it, else ''.
    """
    if key not in manifest:
        return None, ''
    if manifest[key] is not None:
        return _load_json(manifest[key]), ''
    overflow = os.path.join(storage_dir, hashlib.md5(key.encode('utf-8')).hexdigest())
    try:
        with open(overflow, 'r', encoding='utf-8') as handle:
            return _load_json(handle.read()), overflow
    except (OSError, UnicodeDecodeError):
        return None, ''


def _storage_dir(manifest_path):
    return os.path.dirname(manifest_path)


def _yes_no(value):
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    return value


def _ms_time(value):
    """Unix milliseconds (number or digit string) as a UTC datetime, else ''."""
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    return convert_unix_ts_to_utc(number)


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return value if value not in (None, '') else ''


def _manifests(files_found, containers):
    return _select(files_found, containers, r'/RCTAsyncLocalStorage_V1/manifest\.json$')


def _redux_files(files_found, containers):
    return _select(files_found, containers, r'/Documents/mmkv/redux$')


def _statsig_files(files_found, containers):
    return _select(files_found, containers, r'/Documents/mmkv/statsig$')


def _prefs_files(files_found, containers):
    return _select(files_found, containers, r'/Library/Preferences/com\.offerup\.iphone\.consumer\.plist$')


# --------------------------------------------------------------------------------------
# artifacts
# --------------------------------------------------------------------------------------

@artifact_processor
def offerup_app_state(context):
    files_found = context.get_files_found()
    containers = _offerup_containers(files_found)
    headers = ('Item', 'Value', 'Origin')
    rows = []
    sources = set()

    def add(item, value, origin, path):
        if value is None or value == '':
            return
        rows.append((item, _yes_no(value), origin))
        sources.add(path)

    for path in _redux_files(files_found, containers):
        state = _redux_state(path)
        core = state.get('core', {})
        add('App version last run (core.currentVersion)', core.get('currentVersion'), 'Redux store', path)
        add('App version previous (core.previousVersion)', core.get('previousVersion'), 'Redux store', path)
        onboarding = state.get('onboarding', {})
        add('userHasLoggedInAtLeastOnce (meaning beyond the name not established)', onboarding.get('userHasLoggedInAtLeastOnce'), 'Redux store', path)
        steps = onboarding.get('steps')
        if isinstance(steps, dict):
            for name, step in steps.items():
                done = step.get('completed') if isinstance(step, dict) else step
                add(f'Onboarding step: {name}', done, 'Redux store', path)
        ads = state.get('ads', {})
        add('Do not sell my data', ads.get('doNotSellMyData'), 'Redux store', path)
        info = ads.get('advertisingInfo')
        if isinstance(info, dict):
            add('Advertising ID', info.get('advertisingId'), 'Redux store', path)
            add('Limit ad tracking', info.get('isLimitAdTrackingEnabled'), 'Redux store', path)
        root = state.get('root', {})
        instrumentation = root.get('instrumentation')
        if isinstance(instrumentation, dict):
            attributes = instrumentation.get('attributes')
            if isinstance(attributes, dict):
                add('Device ID (app instrumentation)', attributes.get('deviceId'), 'Redux store', path)
                add('Locale', attributes.get('locale'), 'Redux store', path)
                add('App user agent', attributes.get('deviceUserAgent'), 'Redux store', path)
            tags = instrumentation.get('tags')
            if isinstance(tags, dict):
                add('Premium user', tags.get('isPremiumUser'), 'Redux store', path)
                add('First open after install', tags.get('isFirstOpenAfterInstall'), 'Redux store', path)
                add('First open after update', tags.get('isFirstOpenAfterUpdate'), 'Redux store', path)
        shown = root.get('pushNotificationPermissions')
        if isinstance(shown, dict):
            add('Push permission prompt shown (times)', shown.get('numberOfTimesShown'), 'Redux store', path)
        theme = root.get('theme')
        if isinstance(theme, dict):
            add('Theme follows system', theme.get('isSystemPreference'), 'Redux store', path)
        posting = root.get('servicePosting')
        if isinstance(posting, dict):
            add('Service posting draft started', posting.get('hasDraftStarted'), 'Redux store', path)

    for path in _prefs_files(files_found, containers):
        prefs = get_plist_file_content(path)
        if not isinstance(prefs, dict):
            continue
        add('App version of last run', prefs.get('VersionOfLastRun'), 'Preferences', path)
        add('AppsFlyer user ID', prefs.get('AppsFlyerUserId'), 'Preferences', path)
        add('AppsFlyer launch counter', prefs.get('AppsFlyerRealLaunchCounter'), 'Preferences', path)
        add('AppsFlyer reinstall counter', prefs.get('AppsFlyerReInstallCounter'), 'Preferences', path)

    for path in _manifests(files_found, containers):
        manifest = _manifest(path)
        accounts = {}
        for key in manifest:
            match = ACCOUNT_KEY_RE.match(key)
            if match:
                accounts.setdefault(match.group(1), set()).add(match.group(3))
        for number in sorted(accounts):
            add('Account ID (from storage key name)', number, 'Async storage key', path)
            for suffix in sorted(accounts[number]):
                add('Storage key suffix (meaning not established)', suffix, 'Async storage key', path)
        status = _load_json(manifest.get('push_permission_status'))
        if isinstance(status, dict):
            add('Push permission status', status.get('status'), 'Async storage', path)
            settings = status.get('settings')
            if isinstance(settings, dict):
                for name, value in sorted(settings.items()):
                    add(f'Push permission setting: {name}', value, 'Async storage', path)

    for path in _statsig_files(files_found, containers):
        try:
            entries = read_entries(path)
        except (MMKVError, OSError, ValueError):
            continue
        stable = ''
        for key, container in entries:
            if isinstance(key, str) and key.startswith('statsig.stable_id.'):
                value = _load_json(decode_value(container))
                if isinstance(value, str):
                    stable = value
        add('Statsig stable ID', stable, 'Statsig store', path)

    if not rows:
        return headers, [], ''
    return headers, rows, '\n'.join(sorted(sources))


def _location_row(kind, location, gps):
    if not isinstance(location, dict):
        return None
    name = location.get('locationName', '')
    lat = _number(location.get('lat', location.get('latitude')))
    lon = _number(location.get('lon', location.get('longitude')))
    if name in ('', None) and lat in ('', None) and lon in ('', None):
        return None
    return (kind, name, location.get('city', ''), location.get('state') or location.get('adminArea', ''),
            location.get('zipcode', ''), lat, lon, _yes_no(gps) if gps is not None else '')


@artifact_processor
def offerup_locations(context):
    files_found = context.get_files_found()
    containers = _offerup_containers(files_found)
    headers = ('Kind', 'Place', 'City', 'State', 'Zip', ('Latitude', 'latitude'),
               ('Longitude', 'longitude'), 'Used GPS')
    rows = []
    sources = set()

    for path in _redux_files(files_found, containers):
        state = _redux_state(path)
        row = _location_row('Search location', state.get('search', {}).get('location'), None)
        if row:
            rows.append(row)
            sources.add(path)
        rentals = state.get('root', {}).get('rentals')
        if isinstance(rentals, dict):
            row = _location_row('Rentals search location', rentals.get('rentalsSearchLocation'), None)
            if row:
                rows.append(row)
                sources.add(path)

    for path in _manifests(files_found, containers):
        manifest = _manifest(path)
        flow = _load_json(manifest.get('ou_post_flow_preferences'))
        if isinstance(flow, dict):
            location = flow.get('location')
            gps = location.get('didUseGPS') if isinstance(location, dict) else None
            row = _location_row('Posting location', location, gps)
            if row:
                rows.append(row)
                sources.add(path)

    if not rows:
        return headers, [], ''
    return headers, rows, '\n'.join(sorted(sources))


@artifact_processor
def offerup_recent_searches(context):
    files_found = context.get_files_found()
    containers = _offerup_containers(files_found)
    headers = ('Kind', ('Position', 'number'), 'Label', 'Sub Label', 'Type', 'Preposition',
               'Action Path')
    rows = []
    sources = set()

    for path in _manifests(files_found, containers):
        manifest = _manifest(path)
        directory = _storage_dir(path)
        for key, kind in RECENT_SEARCH_KEYS:
            entries, overflow = _async_value(manifest, key, directory)
            if not isinstance(entries, list):
                continue
            for position, entry in enumerate(entries, start=1):
                if not isinstance(entry, dict):
                    continue
                rows.append((kind, position, entry.get('label', ''), entry.get('subLabel') or '',
                             entry.get('type', ''), entry.get('preposition') or '',
                             entry.get('actionPath', '')))
                sources.add(path)
                if overflow:
                    sources.add(overflow)

    if not rows:
        return headers, [], ''
    return headers, rows, '\n'.join(sorted(sources))


@artifact_processor
def offerup_listing_affinity(context):
    files_found = context.get_files_found()
    containers = _offerup_containers(files_found)
    headers = ('Kind', ('Position', 'number'), 'Listing ID', 'Category ID')
    rows = []
    sources = set()

    for path in _redux_files(files_found, containers):
        store = _redux_state(path).get('feedAffinity', {})
        listings = store.get('listingAffinities')
        if isinstance(listings, list):
            for position, entry in enumerate(listings, start=1):
                if isinstance(entry, dict):
                    rows.append(('Listing affinity', position, str(entry.get('listingId', '')),
                                 str(entry.get('categoryId', ''))))
                    sources.add(path)
        formatted = store.get('formattedAffinities')
        last = formatted.get('LAST_VIEWED_CATEGORIES') if isinstance(formatted, dict) else None
        if isinstance(last, str) and last:
            for position, category in enumerate(last.split(','), start=1):
                rows.append(('Last viewed category', position, '', category.strip()))
                sources.add(path)

    if not rows:
        return headers, [], ''
    return headers, rows, '\n'.join(sorted(sources))


@artifact_processor
def offerup_chat_drafts(context):
    files_found = context.get_files_found()
    containers = _offerup_containers(files_found)
    headers = ('Conversation ID', 'Draft', ('Length', 'number'))
    rows = []
    sources = set()

    for path in _manifests(files_found, containers):
        drafts, overflow = _async_value(_manifest(path), 'chat_draft_message', _storage_dir(path))
        if not isinstance(drafts, dict):
            continue
        for conversation, text in drafts.items():
            text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
            rows.append((str(conversation), text, len(text)))
            sources.add(path)
            if overflow:
                sources.add(overflow)

    if not rows:
        return headers, [], ''
    return headers, rows, '\n'.join(sorted(sources))


def _counter_row(event, last_success, last_attempt, runs, attempts):
    detail = f'run count {runs}' if runs not in (None, '') else ''
    if attempts not in (None, ''):
        detail += f'{"; " if detail else ""}attempted {attempts}'
    return (_ms_time(last_success), _ms_time(last_attempt), event, detail)


@artifact_processor
def offerup_activity(context):
    files_found = context.get_files_found()
    containers = _offerup_containers(files_found)
    headers = (('Time', 'datetime'), ('Last Update', 'datetime'), 'Event', 'Detail')
    rows = []
    sources = set()

    for path in _statsig_files(files_found, containers):
        try:
            entries = read_entries(path)
        except (MMKVError, OSError, ValueError):
            continue
        sessions = {}
        for key, container in entries:
            if not (isinstance(key, str) and key.startswith('statsig.session_id.')):
                continue
            value = _load_json(decode_value(container))
            if not isinstance(value, dict) or not value.get('sessionID'):
                continue
            start = value.get('startTime')
            update = value.get('lastUpdate')
            old = sessions.get(value['sessionID'])
            if old is None or (update or 0) >= (old[1] or 0):
                sessions[value['sessionID']] = (start, update)
        for session_id, (start, update) in sessions.items():
            rows.append((_ms_time(start), _ms_time(update), 'Statsig session', f'Session {session_id}'))
            sources.add(path)

    for path in _redux_files(files_found, containers):
        state = _redux_state(path)
        root = state.get('root', {})
        exposures = root.get('exposureTracking')
        if isinstance(exposures, dict) and isinstance(exposures.get('exposures'), dict):
            for name, item in exposures['exposures'].items():
                if isinstance(item, dict):
                    rows.append(_counter_row(f'Prompt exposure: {name}',
                                             item.get('lastSuccessfulExposureTimestamp'),
                                             item.get('lastAttemptedExposureTimestamp'),
                                             item.get('exposureCount'), item.get('attemptedExposureCount')))
                    sources.add(path)
        shown = root.get('pushNotificationPermissions')
        if isinstance(shown, dict) and shown.get('lastShown'):
            rows.append((_ms_time(shown.get('lastShown')), '', 'Push permission prompt shown',
                         f"shown {shown.get('numberOfTimesShown', '')} times"))
            sources.add(path)
        notifications = root.get('notifications')
        if isinstance(notifications, dict) and isinstance(notifications.get('ablyState'), dict):
            beat = notifications['ablyState'].get('lastHeartbeatTime')
            if beat:
                rows.append((_ms_time(beat), '', 'Realtime (Ably) heartbeat', 'lastHeartbeatTime'))
                sources.add(path)

    for path in _prefs_files(files_found, containers):
        prefs = get_plist_file_content(path)
        if not isinstance(prefs, dict):
            continue
        stamp = prefs.get('AppsFlyerInstallTimestamp')
        if stamp:
            try:
                stamp_time = convert_unix_ts_to_utc(int(float(stamp)))
            except (TypeError, ValueError, OverflowError):
                stamp_time = str(stamp)
            rows.append((stamp_time, '', 'AppsFlyer install timestamp',
                         'AppsFlyerInstallTimestamp'))
            sources.add(path)
        installed = prefs.get('com.facebook.sdk:FBSDKSettingsInstallTimestamp')
        if isinstance(installed, datetime.datetime):
            rows.append((convert_plist_date_to_utc(installed), '', 'Facebook SDK install timestamp',
                         'com.facebook.sdk:FBSDKSettingsInstallTimestamp'))
            sources.add(path)

    for path in _manifests(files_found, containers):
        manifest = _manifest(path)
        for key in manifest:
            match = ACCOUNT_KEY_RE.match(key)
            if match and match.group(2) == 'LAST_REGISTERED_AT':
                value = _load_json(manifest[key])
                rows.append((_ms_time(value), '', 'Registration time (LAST_REGISTERED_AT)',
                             'what was registered is not established'))
                sources.add(path)
        for key in RUNNER_KEYS:
            item = _load_json(manifest.get(key))
            if isinstance(item, dict):
                rows.append(_counter_row(f'Prompt counter: {key}',
                                         item.get('lastSuccessfulRunDate'), item.get('lastAttemptedRunDate'),
                                         item.get('runCount'), item.get('attemptedRunCount')))
                sources.add(path)
        for key in MILLISECOND_TEXT_KEYS:
            if manifest.get(key):
                rows.append((_ms_time(_load_json(manifest[key])), '', f'Stored time: {key}',
                             'meaning not established beyond the key name'))
                sources.add(path)

    rows = [row for row in rows if row[0] != '' or row[1] != '']
    if not rows:
        return headers, [], ''
    return headers, rows, '\n'.join(sorted(sources))


def _body_keys(body):
    """Top-level JSON keys of a cached body (set of keys over all objects), else ''."""
    if not body:
        return ''
    try:
        parsed = json.loads(body if isinstance(body, str) else bytes(body).decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return ''
    objects = parsed if isinstance(parsed, list) else [parsed]
    keys = []
    for item in objects:
        if isinstance(item, dict):
            for key in item:
                if key not in keys:
                    keys.append(key)
    return ', '.join(keys)


def _archived(blob):
    """The Array of an archived CFURLResponse, or []."""
    if not blob:
        return []
    content = get_plist_content(bytes(blob))
    array = content.get('Array') if isinstance(content, dict) else None
    return array if isinstance(array, list) else []


def _status_and_mime(array):
    status, mime = '', ''
    for item in array:
        if isinstance(item, int) and not isinstance(item, bool) and 100 <= item <= 599 and status == '':
            status = item
        elif isinstance(item, str) and item.count('/') == 1 and ' ' not in item and not item.startswith('http'):
            if not mime and not item.startswith('__'):
                mime = item
    if not mime:
        for item in array:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(key, str) and key.lower() == 'content-type' and isinstance(value, str):
                        mime = value.split(';')[0].strip()
    return status, mime


@artifact_processor
def offerup_network_cache(context):
    files_found = context.get_files_found()
    headers = (('Cached', 'datetime'), 'Host', 'URL', 'HTTP Status', 'MIME Type',
               ('Body Size', 'number'), 'Body In File', 'Body Keys')
    rows = []
    sources = set()

    for file_found in files_found:
        path = str(file_found)
        if not _norm(path).endswith('/Cache.db') or BUNDLE_ID not in _norm(path):
            continue
        query = ('SELECT r.request_key, r.time_stamp, b.response_object, d.isDataOnFS, d.receiver_data '
                 'FROM cfurl_cache_response r '
                 'LEFT JOIN cfurl_cache_blob_data b ON b.entry_ID = r.entry_ID '
                 'LEFT JOIN cfurl_cache_receiver_data d ON d.entry_ID = r.entry_ID')
        for url, stamp, response, on_disk, body in get_sqlite_db_records(path, query):
            host = urlsplit(url or '').netloc
            if not OFFERUP_HOST_RE.search(host):
                continue
            status, mime = _status_and_mime(_archived(response))
            cached = convert_ts_human_to_utc(stamp) if stamp else ''
            size = '' if on_disk else (len(body) if body is not None else '')
            keys = '' if on_disk else _body_keys(body)
            rows.append((cached, host, url, status, mime, size, 'Yes' if on_disk else 'No', keys))
            sources.add(path)

    if not rows:
        return headers, [], ''
    return headers, rows, '\n'.join(sorted(sources))
