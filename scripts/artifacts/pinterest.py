__artifacts_v2__ = {
    "pinterestAccount": {
        "name": "Pinterest - Account",
        "description": "Parses the signed in account record stored by the Pinterest iOS app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Read from the activeUser file in the app's Documents directory, an "
                 "NSKeyedArchiver archive of the account record as the API returned it. The "
                 "app writes the same record twice, once as activeUser and once as "
                 "activeUser followed by the account id; the two were byte identical in both "
                 "tested samples, so rows are keyed on the account id and the duplicate is "
                 "reported once with both file names in Source File. Account Created and Last "
                 "Board Created are RFC 2822 strings carrying their own UTC offset, so they "
                 "are converted from that offset rather than from an assumed zone; neither "
                 "landed on midnight in the tested samples, so they are instants and not "
                 "calendar dates. The counts are the values the record carries, not a count "
                 "of anything parsed from this extraction. The record's key set differs "
                 "between app versions, so every column is read by key with an empty value "
                 "when the key is absent, and absence of a key is not evidence the setting "
                 "was off. Field mapping was done against private samples; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/mobile/Containers/Data/Application/*/Documents/activeUser*',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/pinterest.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "pinterestMessages": {
        "name": "Pinterest - Messages",
        "description": "Parses cached direct message conversations of the Pinterest iOS app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Read from the app's PINRemoteModelCache, where each file is an "
                 "NSKeyedArchiver archive of one cached API response and the file name is the "
                 "percent encoded request path. Files whose decoded path begins with "
                 "conversations/ hold PIMessage objects and are parsed here. This is a "
                 "response cache, not a message store: it holds what the app last fetched for "
                 "the conversations it opened, so it is neither the complete message history "
                 "nor evidence that other conversations do not exist.\n"
                 "The cache key of the response parsed from the tested sample carries the "
                 "request parameter hide_sys_msg true, so system messages were excluded by "
                 "the server before the response was cached and none appear here. A file whose "
                 "key does not carry that parameter is parsed the same way and its system "
                 "messages, if any, would be reported.\n"
                 "Direction is derived by comparing the message sender id against the signed "
                 "in account id read from the activeUser file, so it is reported only when "
                 "that file is present in the extraction. Every message in the tested "
                 "sample's cached response was from the other participant, so the sent side "
                 "of that comparison is code present and unexercised. Sent At is the message "
                 "created_at, "
                 "an NSDate in Cocoa epoch seconds. Read At is the conversation's read_times "
                 "entry for the signed in account, also an NSDate.\n"
                 "Message Type, Event Type, Message Context and Deleted By are integers the "
                 "record carries. No source that names their values was found: both samples "
                 "are data containers holding no application binary, so the Swift reflection "
                 "metadata that would carry the case names is not present, and the app is not "
                 "open source. They are reported as stored and the mapping is not recoverable "
                 "from these samples. All four were zero on every message of the tested "
                 "sample.\n"
                 "Two of the four cached messages carried no text and a pin object instead; "
                 "those are shared pins rather than empty messages, and the pin's own title, "
                 "description, link and image are reported on that row. A row with neither "
                 "text nor a pin was not observed. Shared pin images are linked by recorded "
                 "identity: the file name in the app's PINRemoteImage cache is the percent "
                 "encoded image URL, so a cached file is matched by decoding its name and "
                 "comparing it to the pin's own image URL, with no size or time correlation. "
                 "The largest rendition present on disk is rendered; a pin whose renditions "
                 "were never downloaded is reported with an empty media cell, which does not "
                 "establish that the image was never on the device. Both shared pins of the "
                 "tested sample had one rendition cached and two not, so the rendered path "
                 "and the partly absent path were both exercised, but a pin with nothing on "
                 "disk was not observed. Field mapping was done against private samples; no "
                 "sample data is recorded for them.",
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteModelCache/*',
            '*/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*',
            '*/mobile/Containers/Data/Application/*/Documents/activeUser*',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/pinterest.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "From Me",
                "directionSentValue": 1,
                "timeColumn": "Sent At",
                "senderColumn": "Sender",
                "mediaColumn": "Shared Pin Image",
            }
        }
    },
    "pinterestCachedModelRequests": {
        "name": "Pinterest - Cached Model Requests",
        "description": "Inventories the cached API responses held by the Pinterest iOS app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "One row per file in the app's PINRemoteModelCache. The file name is the "
                 "percent encoded path and query of the API request whose response it holds, "
                 "so the decoded name states what the app asked the server for; any nineteen "
                 "digit run inside it is reported separately as a referenced identifier, "
                 "because on the tested sample those matched the signed in account id and a "
                 "conversation id, but what a given identifier points at is not established "
                 "here. Model Count is the number of objects in the cached response and Model "
                 "Class is the archived class name of the first of them, both read from the "
                 "archive. A cached response with zero models is reported as such: it records "
                 "that the app made the request and the server returned nothing, which is not "
                 "the same as the app never making it.\n"
                 "Created and Modified are the file system dates the extraction recorded for "
                 "the cache file, not times the app wrote into the record. This library keys "
                 "its cache entries on the request path, so an entry is overwritten in place "
                 "when the same request is repeated and these dates describe the most recent "
                 "fetch only. Field mapping was done against private samples; no sample data "
                 "is recorded for them.",
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteModelCache/*',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/pinterest.plist',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/com.pinterest.applicationhealthmonitor.plist',
            '*/mobile/Containers/Data/Application/*/Documents/activeUser*',
        ),
        "output_types": "standard",
        "artifact_icon": "database"
    },
    "pinterestCachedImages": {
        "name": "Pinterest - Cached Images",
        "description": "Parses and renders the PINRemoteImage disk cache of the Pinterest iOS app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Each file in this cache is named for the URL it was fetched from, percent "
                 "encoded, so the source URL is recovered by decoding the file name rather "
                 "than by correlating anything. Every file name in both tested samples "
                 "decoded to a URL, 253 of 253.\n"
                 "PINRemoteImage is Pinterest's own open source image library and other "
                 "applications embed it, so this cache directory carries the "
                 "com.pinterest.PINDiskCache prefix inside those applications' containers "
                 "too. Rows are therefore restricted to files sitting under a container that "
                 "also holds a file only the Pinterest application writes, and cache files "
                 "found under any other container are skipped with a log line rather than "
                 "reported here. If no such container is identified, no rows are produced and "
                 "that is logged; it is not evidence the cache was empty.\n"
                 "Types are taken from the leading bytes of each file, not from the URL, "
                 "because the cache stores jpeg, png and webp alike under a name that carries "
                 "no extension. Raster images are checked in and rendered. Anything whose "
                 "leading bytes are not a recognised raster image is reported with its type "
                 "and not rendered; every file of both tested samples was a raster image, so "
                 "that path is code present and unexercised. Field mapping was done against "
                 "private samples; no sample data is recorded for them.",
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/pinterest.plist',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/com.pinterest.applicationhealthmonitor.plist',
            '*/mobile/Containers/Data/Application/*/Documents/activeUser*',
        ),
        "output_types": "standard",
        "artifact_icon": "photo"
    },
    "pinterestSearchAutocompleteCache": {
        "name": "Pinterest - Search Autocomplete Cache",
        "description": "Parses the downloaded search autocomplete cache of the Pinterest iOS app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "This store holds suggestions the app downloaded, not terms the user "
                 "searched for, and the suggestion text is therefore not reported. A list of "
                 "server supplied phrases printed beside a Pinterest account reads as a search "
                 "history and is not one. The suggestions remain in the evidence file, where a "
                 "keyword search of this database will surface them; a hit on one of those "
                 "strings is not evidence that the account holder entered it.\n"
                 "What establishes that, on both tested samples: the app's own preference "
                 "kPinterestAutocompleteQueryCacheCurrentKey archives a "
                 "PINSearchAutocompleteCacheMetadata object holding the content delivery "
                 "URLs the corpus was fetched from on a Pinterest host, a version string "
                 "naming a country and gender audience segment with a dated build, a download "
                 "date and the local file prefix naming the database; the table's rows ran on "
                 "a contiguous span of docids from one to the row count with no gaps, which is "
                 "one bulk insert; every query value was distinct, which is a dictionary and "
                 "not a history; the table declares a score column, which a user does not "
                 "supply; and score decreased monotonically with the docid across every row of "
                 "all three databases, so each was written once in server rank order. One "
                 "sample also retained the raw downloaded partition files in the Documents "
                 "directory as tab separated query and score pairs in that same descending "
                 "order.\n"
                 "Row Count is counted from the database. Downloaded and Last Checked come "
                 "from that preference, as an NSDate in Cocoa epoch seconds and a plist date "
                 "respectively. The Local File Prefix the preference records is the current "
                 "cache; a database whose prefix does not match it is a superseded download "
                 "still on disk and is reported with Current reading No. One tested sample "
                 "named a prefix that was not present in the extraction at all, so the "
                 "preference row is reported even when its database is absent.\n"
                 "No store holding terms entered by the user was found in either tested "
                 "sample. Field mapping was done against private samples; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/mobile/Containers/Data/Application/*/Documents/*ap.db',
            '*/mobile/Containers/Data/Application/*/Library/Preferences/pinterest.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "pinterestAppState": {
        "name": "Pinterest - App State",
        "description": "Parses the application state preferences of the Pinterest iOS app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "One row per preference key, with the value as stored. The app's preference "
                 "file also holds the state of several embedded third party kits, so only "
                 "keys whose names carry one of the application's own prefixes are reported "
                 "and the rest are left out; the prefix list is matched rather than a fixed "
                 "key list, so keys added by a later app version still appear. What the "
                 "application does with each preference is not established here, so no "
                 "meaning is asserted beyond the key name the application itself uses.\n"
                 "A value that the plist stored as a date is converted; every other value is "
                 "reported as text in the form it was stored, and a value that is a nested "
                 "archive or binary payload is reported by its type and length rather than "
                 "decoded. The keys ending last_selected_date carry a tab number whose "
                 "meaning is not established, so the key name is reported as stored. Absence "
                 "of a key is not evidence a setting was off; the app writes many of these "
                 "only once the state they describe changes. Field mapping was done against "
                 "private samples; no sample data is recorded for them.",
        "paths": (
            '*/mobile/Containers/Data/Application/*/Library/Preferences/pinterest.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "settings"
    },
}

import os
import plistlib
import re
import sqlite3
import urllib.parse
import xml.parsers.expat
from email.utils import parsedate_to_datetime
from plistlib import UID

from scripts.ilapfuncs import artifact_processor, check_in_media, \
    convert_cocoa_core_data_ts_to_utc, convert_plist_date_to_utc, \
    get_plist_content, logfunc

# Files only the Pinterest application writes. Its bundle identifier is the bare
# word "pinterest", read from MCMMetadataIdentifier in the container metadata of
# both tested samples, so its preference file is named for that and not for a
# reverse DNS identifier.
CONTAINER_MARKERS = (
    'Library/Preferences/pinterest.plist',
    'Library/Preferences/com.pinterest.applicationhealthmonitor.plist',
    'Documents/activeUser',
)

# The cache directories carry Pinterest's open source library name, so they appear
# inside other applications' containers as well.
IMAGE_CACHE_DIR = 'com.pinterest.PINDiskCache.PINRemoteImageManagerCache'
MODEL_CACHE_DIR = 'com.pinterest.PINDiskCache.PINRemoteModelCache'

# Preference key prefixes the application uses for its own state. Everything else
# in the file belongs to an embedded third party kit.
APP_STATE_PREFIXES = (
    'kPinterest', 'kPIN', 'kPI', 'kUserDefault', 'com.pinterest.', 'tab_',
    'external_share_sources', 'has_shown_location_prompt', 'closeupVisualSearch',
    'kAppDidRequestTracking', 'kSafariKeychainStopAsking', 'kPLRemap',
    'SavedComplianceManagerRequirements', 'kLastShareSheetOpen',
)

# The preference holding the autocomplete cache metadata, and the keys of the
# object it archives.
AUTOCOMPLETE_CURRENT_KEY = 'kPinterestAutocompleteQueryCacheCurrentKey'
AUTOCOMPLETE_LAST_CHECK_KEY = 'kPinterestAutocompleteQueryCacheLastCheckKey'
AUTOCOMPLETE_FIELDS = {
    'prefix': 'kAutocompleteCacheCodingLocalFilePrefixKey',
    'version': 'kAutocompleteCacheCodingVersionKey',
    'downloaded': 'kAutocompleteCacheCodingDownloadDateKey',
    'urls': 'kAutocompleteCacheCodingPartitionURLsKey',
    'state': 'kAutocompleteCacheCodingStateKey',
}

# Leading bytes of the image types this cache was observed to hold.
IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'JPEG', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'png'),
    (b'GIF87a', 'GIF', 'gif'),
    (b'GIF89a', 'GIF', 'gif'),
)

# A Pinterest object id, as it appears inside a cache request path.
OBJECT_ID = re.compile(r'\d{16,20}')


def _unarchive(raw):
    '''The object graph of an NSKeyedArchiver archive of plain Foundation types.

    The app archives its API models as NSDictionary graphs, so only the container
    classes and NSDate, NSURL and NSNull are resolved. Anything else is returned
    as its own dictionary carrying the archived class name, so an unhandled class
    is visible rather than silently dropped.
    '''
    try:
        plist = plistlib.loads(raw) if isinstance(raw, bytes) else raw
    except (ValueError, TypeError, AttributeError, xml.parsers.expat.ExpatError):
        return None
    if not isinstance(plist, dict) or '$objects' not in plist or '$top' not in plist:
        return None
    objects = plist['$objects']

    def resolve(ref, depth=0):
        if not isinstance(ref, UID):
            return ref
        if depth > 80:
            return None
        try:
            value = objects[ref.data]
        except IndexError:
            return None
        if isinstance(value, dict) and '$class' in value:
            class_ref = value['$class']
            if not isinstance(class_ref, UID) or class_ref.data >= len(objects):
                return None
            name = objects[class_ref.data].get('$classname')
            if name in ('NSDictionary', 'NSMutableDictionary'):
                keys = [resolve(k, depth + 1) for k in value.get('NS.keys', [])]
                values = [resolve(v, depth + 1) for v in value.get('NS.objects', [])]
                return dict(zip(keys, values))
            if name in ('NSArray', 'NSMutableArray', 'NSSet', 'NSMutableSet'):
                return [resolve(v, depth + 1) for v in value.get('NS.objects', [])]
            if name == 'NSNull':
                return None
            if name == 'NSDate':
                return convert_cocoa_core_data_ts_to_utc(value.get('NS.time'))
            if name in ('NSString', 'NSMutableString'):
                return value.get('NS.string')
            if name in ('NSData', 'NSMutableData'):
                return value.get('NS.data')
            if name == 'NSURL':
                relative = resolve(value.get('NS.relative'), depth + 1)
                base = resolve(value.get('NS.base'), depth + 1)
                if isinstance(base, str) and isinstance(relative, str):
                    return base.rstrip('/') + '/' + relative.lstrip('/')
                return relative
            resolved = {k: resolve(v, depth + 1) for k, v in value.items() if k != '$class'}
            resolved['__class__'] = name
            return resolved
        # UID 0 is the archive's null placeholder.
        return None if value == '$null' else value

    return resolve(plist['$top'].get('root'))


def _paths(files_found):
    '''The matched paths as strings, in a stable order.'''
    return sorted(str(path) for path in files_found)


def _containers(files_found):
    '''Container directories holding a file only the Pinterest app writes.'''
    roots = set()
    for path in _paths(files_found):
        normalized = path.replace('\\', '/')
        for marker in CONTAINER_MARKERS:
            index = normalized.rfind('/' + marker)
            if index > 0:
                roots.add(normalized[:index])
                break
    return roots


def _container_of(path, roots):
    '''The Pinterest container a path sits under, or '' when it is outside them.

    The longest match wins, so a container nested inside another cannot be
    attributed to the outer one.
    '''
    normalized = path.replace('\\', '/')
    matches = [root for root in roots if normalized.startswith(root + '/')]
    return max(matches, key=len) if matches else ''


def _in_container(path, roots):
    '''Whether a path sits under one of the identified Pinterest containers.'''
    return bool(_container_of(path, roots))


def _source_label(path, roots):
    '''A source name that stays unambiguous when several containers are present.

    An extraction can hold more than one application container, so the bare file
    name would not say which one a row came from.
    '''
    root = _container_of(path, roots)
    if not root:
        return os.path.basename(path)
    return os.path.basename(root) + '/' + path.replace('\\', '/')[len(root) + 1:]


def _cache_files(files_found, directory, roots):
    '''Cache files under directory that sit inside a Pinterest container.

    Files matched in another application's container are skipped and counted, so
    a run that reports nothing says why rather than reporting a bare zero.
    '''
    candidates = [path for path in _paths(files_found)
                  if '/' + directory + '/' in path.replace('\\', '/')
                  and os.path.isfile(path)]
    if not candidates:
        return []
    if not roots:
        logfunc(f'Pinterest: {len(candidates)} {directory} file(s) were found but no '
                f'Pinterest container was identified, so none are reported. This cache '
                f'directory is named for a shared library and is not evidence of Pinterest.')
        return []
    kept = [path for path in candidates if _in_container(path, roots)]
    skipped = len(candidates) - len(kept)
    if skipped:
        logfunc(f'Pinterest: skipped {skipped} {directory} file(s) found outside a '
                f'Pinterest container; this cache directory is named for a shared library.')
    return kept


def _decoded_name(path):
    '''The cache file name decoded from its percent encoded form.'''
    return urllib.parse.unquote(os.path.basename(path))


def _image_type(path):
    '''(label, extension) for a cached file, from its leading bytes.'''
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError:
        return '', ''
    for magic, label, extension in IMAGE_MAGIC:
        if head.startswith(magic):
            return label, extension
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'WEBP', 'webp'
    return '', ''


def _account_records(files_found, roots=(), container=None):
    '''{account id: (record, [file names])} from the activeUser files matched.

    The app writes the record twice under two names. They were byte identical in
    both tested samples, so the id keys the row and both names are reported. When
    container is given, only that container's files are read, so an extraction
    holding more than one container does not merge their accounts.
    '''
    accounts = {}
    for path in _paths(files_found):
        name = os.path.basename(path)
        if not name.startswith('activeUser') or not os.path.isfile(path):
            continue
        if container is not None and _container_of(path, roots) != container:
            continue
        try:
            with open(path, 'rb') as handle:
                record = _unarchive(handle.read())
        except OSError:
            continue
        if not isinstance(record, dict):
            continue
        account_id = record.get('id') or name
        existing = accounts.setdefault(account_id, (record, []))
        existing[1].append(_source_label(path, roots) if roots else name)
        if len(record) > len(existing[0]):
            accounts[account_id] = (record, existing[1])
    return accounts


def _rfc2822(value):
    '''An RFC 2822 date string as a UTC datetime, using the offset it carries.'''
    if not value or not isinstance(value, str):
        return ''
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return value


def _text(value):
    '''A preference value as report text, leaving the stored form intact.'''
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, bytes):
        return f'<{len(value)} bytes>'
    if isinstance(value, (list, tuple)):
        return ', '.join(_text(item) for item in value)
    if isinstance(value, dict):
        return f'<dictionary, {len(value)} keys>'
    return str(value)


def _read_preferences(path):
    '''The app's own preference file as a dictionary, or {}.'''
    try:
        with open(path, 'rb') as handle:
            content = get_plist_content(handle.read())
    except OSError:
        return {}
    return content if isinstance(content, dict) else {}


def _preferences_by_container(files_found, roots):
    '''{container: (path, content)} for every preference file matched.

    Keyed on the container rather than taking the first match, because these
    preferences describe one installation and an extraction can carry several.
    '''
    found = {}
    for path in _paths(files_found):
        if os.path.basename(path) != 'pinterest.plist' or not os.path.isfile(path):
            continue
        found[_container_of(path, roots)] = (path, _read_preferences(path))
    return found


def _autocomplete_metadata(preferences):
    '''The archived autocomplete cache metadata as a plain dictionary.'''
    blob = preferences.get(AUTOCOMPLETE_CURRENT_KEY)
    if not isinstance(blob, bytes):
        return {}
    archived = _unarchive(blob)
    return archived if isinstance(archived, dict) else {}


@artifact_processor
def pinterestAccount(context):
    files_found = context.get_files_found()
    data_headers = (
        ('Account Created', 'datetime'), ('Last Board Created', 'datetime'),
        'Username', 'Full Name', 'Email', 'First Name', 'Last Name', 'Account ID',
        'About', 'Location', 'Country', 'Locale', 'Gender', 'Age In Years',
        'Private Profile', 'Excluded From Search', 'Email Confirmed',
        'Followers', 'Following', 'Boards', 'Secret Boards', 'Archived Boards',
        'Pins', 'Video Pins', 'Story Pins', 'Saved Pins', 'Profile Views',
        'Connected To Facebook', 'Connected To Instagram', 'Connected To Twitter',
        'Connected To YouTube', 'Connected To Etsy', 'Profile Image URL',
        'Account Type', 'Source File')
    data_list = []
    source_path = ''

    roots = _containers(files_found)
    for account_id, (record, names) in sorted(_account_records(files_found, roots).items()):
        source_path = source_path or 'activeUser'
        data_list.append((
            _rfc2822(record.get('created_at')),
            _rfc2822(record.get('last_board_created_at')),
            _text(record.get('username')),
            _text(record.get('full_name')),
            _text(record.get('email')),
            _text(record.get('first_name')),
            _text(record.get('last_name')),
            _text(account_id),
            _text(record.get('about')),
            _text(record.get('location')),
            _text(record.get('country')),
            _text(record.get('locale')),
            _text(record.get('gender')),
            _text(record.get('age_in_years')),
            _text(record.get('is_private_profile')),
            _text(record.get('exclude_from_search')),
            _text(record.get('has_confirmed_email')),
            _text(record.get('follower_count')),
            _text(record.get('following_count')),
            _text(record.get('board_count')),
            _text(record.get('secret_board_count')),
            _text(record.get('archived_board_count')),
            _text(record.get('pin_count')),
            _text(record.get('video_pin_count')),
            _text(record.get('story_pin_count')),
            _text(record.get('quick_saves_pin_count')),
            _text(record.get('profile_views')),
            _text(record.get('connected_to_facebook')),
            _text(record.get('connected_to_instagram')),
            _text(record.get('connected_to_twitter')),
            _text(record.get('connected_to_youtube')),
            _text(record.get('connected_to_etsy')),
            _text(record.get('image_large_url')),
            _text(record.get('type')),
            ', '.join(sorted(set(names))),
        ))

    return data_headers, data_list, source_path


def _image_index(files_found, roots):
    '''{decoded URL: path} for the cached images of the Pinterest container.'''
    index = {}
    for path in _cache_files(files_found, IMAGE_CACHE_DIR, roots):
        index.setdefault(_decoded_name(path), path)
    return index


def _pin_image(pin, index):
    '''(media ref, URL, rendition) for the largest cached rendition of a pin.'''
    images = pin.get('images') if isinstance(pin, dict) else None
    if not isinstance(images, dict):
        return None, '', ''
    best = (None, '', '')
    best_width = -1
    for rendition, details in images.items():
        url = details.get('url') if isinstance(details, dict) else None
        if not isinstance(url, str):
            continue
        digits = re.match(r'(\d+)', str(rendition))
        width = int(digits.group(1)) if digits else 0
        path = index.get(url)
        if path and width > best_width:
            extension = _image_type(path)[1]
            best = (check_in_media(path, os.path.basename(path),
                                   force_extension=extension or None), url, str(rendition))
            best_width = width
    if best[0] is None:
        # Nothing on disk: report the largest rendition the record names.
        for rendition, details in sorted(images.items()):
            url = details.get('url') if isinstance(details, dict) else None
            if isinstance(url, str):
                return None, url, str(rendition)
    return best


@artifact_processor
def pinterestMessages(context):
    files_found = context.get_files_found()
    data_headers = (
        ('Sent At', 'datetime'), ('Read At', 'datetime'), ('Pin Created', 'datetime'),
        'From Me', 'Sender', 'Conversation', 'Message', ('Shared Pin Image', 'media'),
        'Sender Username', 'Sender ID', 'Participants', 'Pin Title',
        'Pin Description', 'Pin Link', 'Pin Domain', 'Pin Is Video', 'Pin ID',
        'Pin Image URL', 'Pin Image Rendition', 'Message Type (as stored)',
        'Event Type (as stored)', 'Message Context (as stored)',
        'Deleted By (as stored)', 'Message ID', 'Conversation ID', 'Cached Request',
        'Source File')
    data_list = []
    source_path = ''

    roots = _containers(files_found)
    index = _image_index(files_found, roots)
    # The signed in account decides direction, so it is read from the container the
    # cached response belongs to rather than from any container in the extraction.
    accounts_by_container = {}

    for path in _cache_files(files_found, MODEL_CACHE_DIR, roots):
        request = _decoded_name(path)
        if not request.startswith('conversations/'):
            continue
        container = _container_of(path, roots)
        if container not in accounts_by_container:
            accounts_by_container[container] = set(
                _account_records(files_found, roots, container))
        account_ids = accounts_by_container[container]
        try:
            with open(path, 'rb') as handle:
                cached = _unarchive(handle.read())
        except OSError:
            continue
        models = cached.get('models') if isinstance(cached, dict) else None
        if not isinstance(models, list):
            continue
        source_path = source_path or path

        for message in models:
            if not isinstance(message, dict):
                continue
            sender = message.get('sender') if isinstance(message.get('sender'), dict) else {}
            conversation = message.get('conversation') \
                if isinstance(message.get('conversation'), dict) else {}
            sender_id = sender.get('id')
            # Direction is only derivable when the signed in account is known.
            from_me = ''
            if account_ids and sender_id:
                from_me = 1 if str(sender_id) in {str(i) for i in account_ids} else 0

            read_times = conversation.get('read_times')
            read_at = ''
            if isinstance(read_times, dict):
                for candidate in account_ids:
                    if str(candidate) in read_times:
                        read_at = read_times[str(candidate)]
                        break

            participants = []
            for user in conversation.get('users') or []:
                if isinstance(user, dict):
                    participants.append(_text(user.get('username') or user.get('id')))

            pin = message.get('pin') if isinstance(message.get('pin'), dict) else {}
            media, image_url, rendition = _pin_image(pin, index) if pin else (None, '', '')

            data_list.append((
                message.get('created_at') or '',
                read_at or '',
                pin.get('created_at') or '',
                from_me,
                _text(sender.get('full_name') or sender.get('username')),
                _text(conversation.get('name')),
                _text(message.get('text')),
                media,
                _text(sender.get('username')),
                _text(sender_id),
                ', '.join(participants),
                _text(pin.get('title') or pin.get('grid_title')),
                _text(pin.get('description')),
                _text(pin.get('link')),
                _text(pin.get('domain')),
                _text(pin.get('is_video')) if pin else '',
                _text(pin.get('id')),
                image_url,
                rendition,
                _text(message.get('message_type')),
                _text(message.get('event_type')),
                _text(message.get('message_context')),
                _text(message.get('deleted_by')),
                _text(message.get('id')),
                _text(conversation.get('id')),
                request,
                _source_label(path, roots),
            ))

    return data_headers, data_list, source_path


@artifact_processor
def pinterestCachedModelRequests(context):
    files_found = context.get_files_found()
    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), 'Cached Request',
        'Model Count', 'Model Class', 'Referenced Identifiers', 'File Size (bytes)',
        'Source File')
    data_list = []
    source_path = ''

    seeker = context.get_seeker()
    roots = _containers(files_found)

    for path in _cache_files(files_found, MODEL_CACHE_DIR, roots):
        try:
            with open(path, 'rb') as handle:
                cached = _unarchive(handle.read())
        except OSError:
            continue
        source_path = source_path or os.path.dirname(path)
        models = cached.get('models') if isinstance(cached, dict) else None
        model_class = ''
        if isinstance(models, list) and models and isinstance(models[0], dict):
            model_class = models[0].get('__class__', '')
        request = _decoded_name(path)
        file_info = seeker.file_infos.get(path) if seeker else None
        data_list.append((
            file_info.creation_date if file_info else '',
            file_info.modification_date if file_info else '',
            request,
            len(models) if isinstance(models, list) else '',
            model_class,
            ', '.join(sorted(set(OBJECT_ID.findall(request)))),
            os.path.getsize(path),
            _source_label(path, roots),
        ))

    return data_headers, data_list, source_path


@artifact_processor
def pinterestCachedImages(context):
    files_found = context.get_files_found()
    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), ('Image', 'media'),
        'Source URL', 'Host', 'Image Type', 'File Size (bytes)', 'Source File')
    data_list = []
    source_path = ''

    seeker = context.get_seeker()
    roots = _containers(files_found)

    for path in _cache_files(files_found, IMAGE_CACHE_DIR, roots):
        source_path = source_path or os.path.dirname(path)
        url = _decoded_name(path)
        label, extension = _image_type(path)
        media = check_in_media(path, os.path.basename(path),
                               force_extension=extension or None) if label else None
        file_info = seeker.file_infos.get(path) if seeker else None
        data_list.append((
            file_info.creation_date if file_info else '',
            file_info.modification_date if file_info else '',
            media,
            url,
            urllib.parse.urlparse(url).netloc,
            label or 'Not a recognised raster image',
            os.path.getsize(path),
            _source_label(path, roots),
        ))

    return data_headers, data_list, source_path


def _autocomplete_rows(path):
    '''(row count, docid gaps, distinct queries) of an autocomplete database.'''
    try:
        db = sqlite3.connect(f'file:{path}?immutable=1', uri=True)
    except sqlite3.Error:
        return '', '', ''
    try:
        cursor = db.cursor()
        # The query lives in the FTS content table, which carries the docid.
        cursor.execute("SELECT count(*), count(DISTINCT c0query), min(docid), max(docid) "
                       "FROM search_queries_content")
        total, distinct, low, high = cursor.fetchone()
        gaps = '' if total in (0, None) else (high - low + 1) - total
        return total, gaps, distinct
    except sqlite3.Error as error:
        logfunc(f'Pinterest: could not read {os.path.basename(path)}: {error}')
        return '', '', ''
    finally:
        db.close()


@artifact_processor
def pinterestSearchAutocompleteCache(context):
    files_found = context.get_files_found()
    data_headers = (
        ('Downloaded', 'datetime'), ('Last Checked', 'datetime'), 'Current',
        'Cache Version (audience segment)', 'Row Count', 'Distinct Queries',
        'Docid Gaps', 'Local File Prefix', 'Partition URLs', 'Cache State (as stored)',
        'File Size (bytes)', 'Source File')
    data_list = []
    source_path = ''

    roots = _containers(files_found)
    preferences_by_container = _preferences_by_container(files_found, roots)

    # The metadata of each installation, keyed on the container it describes.
    metadata_by_container = {}
    for container, (preferences_path, preferences) in preferences_by_container.items():
        metadata = _autocomplete_metadata(preferences)
        last_checked = preferences.get(AUTOCOMPLETE_LAST_CHECK_KEY)
        urls = metadata.get(AUTOCOMPLETE_FIELDS['urls']) or []
        metadata_by_container[container] = {
            'path': preferences_path,
            'prefix': metadata.get(AUTOCOMPLETE_FIELDS['prefix']) or '',
            'version': metadata.get(AUTOCOMPLETE_FIELDS['version']) or '',
            'downloaded': metadata.get(AUTOCOMPLETE_FIELDS['downloaded']) or '',
            'state': metadata.get(AUTOCOMPLETE_FIELDS['state']),
            'urls': ', '.join(url for url in urls if isinstance(url, str)),
            'last_checked': convert_plist_date_to_utc(last_checked) if last_checked else '',
            'seen': set(),
        }

    for path in _paths(files_found):
        name = os.path.basename(path)
        if not name.endswith('ap.db') or not os.path.isfile(path):
            continue
        if roots and not _in_container(path, roots):
            continue
        container = _container_of(path, roots)
        metadata = metadata_by_container.get(container, {})
        prefix = name[:-len('ap.db')]
        if metadata:
            metadata['seen'].add(prefix)
        total, gaps, distinct = _autocomplete_rows(path)
        is_current = 'Yes' if prefix and prefix == metadata.get('prefix') else 'No'
        current = is_current == 'Yes'
        source_path = source_path or path
        data_list.append((
            metadata.get('downloaded', '') if current else '',
            metadata.get('last_checked', '') if current else '',
            is_current,
            _text(metadata.get('version')) if current else '',
            total,
            distinct,
            gaps,
            prefix,
            metadata.get('urls', '') if current else '',
            _text(metadata.get('state')) if current else '',
            os.path.getsize(path),
            _source_label(path, roots),
        ))

    # A preference naming a cache whose database did not come across is still a
    # record of the fetch, so it is reported with the database columns empty.
    for container, metadata in sorted(metadata_by_container.items()):
        prefix = metadata['prefix']
        if not prefix or prefix in metadata['seen']:
            continue
        source_path = source_path or metadata['path']
        data_list.append((
            metadata['downloaded'], metadata['last_checked'], 'Yes',
            _text(metadata['version']), '', '', '', prefix, metadata['urls'],
            _text(metadata['state']), '',
            _source_label(metadata['path'], roots) + ' (database not in extraction)',
        ))

    return data_headers, data_list, source_path


@artifact_processor
def pinterestAppState(context):
    files_found = context.get_files_found()
    data_headers = (('Date Value', 'datetime'), 'Key', 'Value', 'Value Type', 'Source File')
    data_list = []
    source_path = ''

    roots = _containers(files_found)
    for preferences_path, preferences in sorted(
            _preferences_by_container(files_found, roots).values()):
        source_path = source_path or preferences_path
        label = _source_label(preferences_path, roots)
        for key in sorted(preferences):
            if not key.startswith(APP_STATE_PREFIXES):
                continue
            value = preferences[key]
            date_value = ''
            text = ''
            # A plist date is a datetime; a bool is not, and must not be read as one.
            if hasattr(value, 'year') and hasattr(value, 'hour') and not isinstance(value, bool):
                date_value = convert_plist_date_to_utc(value)
            else:
                text = _text(value)
            data_list.append((date_value, key, text, type(value).__name__, label))

    return data_headers, data_list, source_path
