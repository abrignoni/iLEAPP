__artifacts_v2__ = {
    "webkit_website_data_origins": {
        "name": "WebKit - Website Data Origins",
        "description": "Web origins recorded in WebKit website data stores in app containers, with the kinds of stored "
                       "data found for each, the container's identifier and the file's modified time as the extraction "
                       "recorded it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Browsers",
        "notes": "Lists the origins in WebKit website data stores inside app data containers, app extension "
                 "containers and other paths. Three locations are read. In two of them (iOS 16.1.1 to 26.5.2 on the "
                 "tested images) each origin has a folder two levels under WebsiteData/Default, or under "
                 "WebsiteDataStore/<identifier>/Origins, both levels named with a hash, holding a file named origin; "
                 "the WebsiteDataStore location held 102 origins, all on dexter_ios18. That file is decoded as "
                 "WebKit writes it: writeOriginToFile in Source/WebCore/storage/StorageUtilities.cpp encodes a "
                 "ClientOrigin with WTF::Persistence::Encoder, which "
                 "Source/WebCore/platform/WebCorePersistentCoders.cpp writes as the top origin then the client "
                 "origin, each a protocol and host string and an optional port (WebKit/WebKit at commit c3a7f3c0). "
                 "Each origin file must decode to its last byte or it is logged and skipped; all 623 on the tested "
                 "images decoded, and no origin on them carried a port. Only an origin file directly inside the "
                 "hashed folder makes a row; the copy CacheStorage keeps in its own folder does not. Top Origin is "
                 "the top origin and Origin the client origin. Top Origin and Origin were the same on 438 of the 623 "
                 "rows; on iphone14plus_ios18 Top Origin and Origin are identical on all 9 rows. An origin stored "
                 "with an empty protocol and host is shown as :// (3 cells); what it stands for is not established. "
                 "In the third, older location (iOS 12.4 to 15.3.1 on the tested images) LocalStorage files are "
                 "named after the origin, in WebsiteData/LocalStorage or directly in WebsiteData, and IndexedDB "
                 "databases sit in folders named after it, under WebsiteData/IndexedDB or directly under "
                 "WebsiteData. The name is in the protocol_host_port form that "
                 "SecurityOriginData::fromDatabaseIdentifier in Source/WebCore/page/SecurityOriginData.cpp parses, "
                 "and it is split at the first and last underscore as that function does, with port 0 shown as no "
                 "port. The module also percent-decodes the host. No name on the tested images held an escape or a "
                 "port other than 0. That form names one origin, so Top Origin has no value on any row of "
                 "ctf2020_ios12, hickman_ios13, hickman_ios14, hickman_ios15 and jess_ios15. Origin Read From says "
                 "which way each row was read, and it held one value on all rows of each newer-layout image, since "
                 "no image produced rows from both. On a newer-layout row Data Kinds names LocalStorage when "
                 "LocalStorage/localstorage.sqlite3, IndexedDB when an IndexedDB.sqlite3 and CacheStorage when "
                 "CacheStorage/origin was found for that origin; on iphone14plus_ios18 Data Kinds held one value, "
                 "LocalStorage, on all rows. An empty Data Kinds on a newer-layout row means none of those was "
                 "found: of the 160 such folders under WebsiteData/Default on 18 images, 131 held only the origin "
                 "file, 16 a CacheStorage folder without its own origin file, 8 ServiceWorkers and 5 a LocalStorage "
                 "folder without localstorage.sqlite3, and of the 70 under WebsiteDataStore on dexter_ios18, 52 held "
                 "only the origin file, 17 ServiceWorkers and 1 CacheStorage. Their contents are not read. On an "
                 "older-layout row Data Kinds names the store the name was read from, and an origin with both gets "
                 "two rows. Bundle ID is MCMMetadataIdentifier from the container's metadata plist. Store is "
                 "SafariViewService for a store under SystemData/com.apple.SafariViewService in an app container (31 "
                 "rows on 9 images, 7 of them older-layout files directly in WebsiteData), App data store for "
                 "WebsiteDataStore, App for the rest of an app container, App extension for a PluginKitPlugin "
                 "container, and Other elsewhere; Store held one value on all rows of 12 images. One Other row, on "
                 "hc_ios26, is under mobile/Library/WebKit/com.apple.purplebuddy and has no Bundle ID. Modified is "
                 "the modified time the extraction recorded for the origin file, the .localstorage file, or the "
                 "first IndexedDB.sqlite3 in path order for an older-layout origin. What moment it marks is not "
                 "established, so rows are not written to the timeline. A row records that WebKit kept this file for "
                 "the origin in that store. It does not establish that a person opened the site, and whether "
                 "clearing website data removes the folder was not tested. Cookies, caches and the contents of "
                 "LocalStorage and IndexedDB are not read here.",
        "paths": (
            '*/WebsiteData/Default/*/*/origin',
            '*/WebsiteData/Default/*/*/LocalStorage/localstorage.sqlite3',
            '*/WebsiteData/Default/*/*/IndexedDB/*/IndexedDB.sqlite3',
            '*/WebsiteDataStore/*/Origins/*/*/origin',
            '*/WebsiteDataStore/*/Origins/*/*/LocalStorage/localstorage.sqlite3',
            '*/WebsiteDataStore/*/Origins/*/*/IndexedDB/*/IndexedDB.sqlite3',
            '*/WebsiteData/*.localstorage',
            '*/WebsiteData/*/IndexedDB.sqlite3',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 75 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 12 rows",
            "belkactf6_tar": "iOS 16.3 | 15 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 35 rows",
            "ctf2020_ios12": "iOS 12.4 | 61 rows",
            "dexter_ios18": "iOS 18.3.2 | 138 rows",
            "falken_ios26": "iOS 26.2.1 | 42 rows",
            "felix23_ios16": "iOS 16.5 | 9 rows",
            "felix_ios17": "iOS 17.6.1 | 25 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios17_2": "iOS 17.2.1 | 32 rows",
            "hc_ios18_7": "iOS 18.7.8 | 34 rows",
            "hc_ios26": "iOS 26.5.2 | 34 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 28 rows",
            "hickman_ios13": "iOS 13.3.1 | 22 rows",
            "hickman_ios14": "iOS 14.3 | 18 rows",
            "hickman_ios15": "iOS 15.3.1 | 32 rows",
            "iphone11_ios17": "iOS 17.3 | 52 rows",
            "iphone12_ios18": "iOS 18.7 | 23 rows",
            "iphone14plus_ios18": "iOS 18.0 | 9 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 13 rows",
            "jess_ios15": "iOS 15.0.2 | 13 rows",
            "magnet_ios16": "iOS 16.1.1 | 14 rows",
            "otto_ios17": "iOS 17.5.1 | 29 rows",
        },
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe",
    },
}

import re
import struct
from urllib.parse import unquote

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, convert_unix_ts_to_utc, logfunc

_CONTAINER = re.compile(r'/Containers/Data/(Application|PluginKitPlugin)/([^/]+)/')
_OLD_IDB = re.compile(r'/WebsiteData/(?:IndexedDB/(?:v\d+/)?)?([^/]+)/[^/]+/IndexedDB\.sqlite3$')
_NULL = 0xFFFFFFFF
_NEW_ROOT = r'/(?:WebsiteData/Default|WebsiteDataStore/[^/]+/Origins)/[^/]+/[^/]+'
_ORIGIN_FILE = re.compile(_NEW_ROOT + r'/origin$')
_IN_FOLDER = re.compile(r'^(.*' + _NEW_ROOT + r')/(.+)$')
_KINDS = ((re.compile(r'^LocalStorage/localstorage\.sqlite3$'), 'LocalStorage'),
          (re.compile(r'^IndexedDB/.+/IndexedDB\.sqlite3$'), 'IndexedDB'),
          (re.compile(r'^CacheStorage/origin$'), 'CacheStorage'))


def _read_string(blob, offset):
    """WTF::Persistence String: uint32 length (0xFFFFFFFF for null), uint8 is8Bit, then the characters."""
    (length,) = struct.unpack_from('<I', blob, offset)
    offset += 4
    if length == _NULL:
        return None, offset
    is_8bit = blob[offset]
    offset += 1
    if is_8bit not in (0, 1):
        raise ValueError('is8Bit is not a bool')
    size = length if is_8bit else 2 * length
    if offset + size > len(blob):
        raise ValueError('string runs past the end')
    text = blob[offset:offset + size].decode('latin-1' if is_8bit else 'utf-16-le')
    return text, offset + size


def _read_origin(blob, offset):
    """SecurityOriginData: protocol, host, optional<uint16> port."""
    protocol, offset = _read_string(blob, offset)
    host, offset = _read_string(blob, offset)
    has_port = blob[offset]
    offset += 1
    if has_port not in (0, 1):
        raise ValueError('port flag is not a bool')
    port = None
    if has_port:
        (port,) = struct.unpack_from('<H', blob, offset)
        offset += 2
    return (protocol, host, port), offset


def decode_origin_file(blob):
    """(top origin, frame origin) from a WebsiteData origin file, or None when the bytes do not decode exactly."""
    try:
        top, offset = _read_origin(blob, 0)
        frame, offset = _read_origin(blob, offset)
    except (struct.error, IndexError, ValueError, UnicodeDecodeError):
        return None
    if offset != len(blob):
        return None
    return top, frame


def parse_database_identifier(identifier):
    """protocol_host_port, split as SecurityOriginData::fromDatabaseIdentifier does; None when it does not parse."""
    first, last = identifier.find('_'), identifier.rfind('_')
    if first < 0 or first == last:
        return None
    port_text = identifier[last + 1:]
    if port_text and not port_text.isdigit():
        return None
    port = int(port_text) if port_text else None
    return identifier[:first], unquote(identifier[first + 1:last]), (port or None)


def _text(origin):
    if not origin:
        return ''
    protocol, host, port = origin
    text = f'{protocol or ""}://{host or ""}'
    return f'{text}:{port}' if port is not None else text


def _modified(seeker, path):
    infos = getattr(seeker, 'file_infos', None) or {}
    info = infos.get(path)
    times = getattr(info, 'times', None)
    return convert_unix_ts_to_utc(getattr(times, 'modified', None)) if times else ''


@artifact_processor
def webkit_website_data_origins(context):
    real = {str(f).replace('\\', '/'): str(f) for f in context.get_files_found()}
    files = list(real)
    seeker = context.get_seeker()
    bundles = {}
    for path in files:
        if path.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            plist = get_plist_file_content(real[path])
            if isinstance(plist, dict) and plist.get('MCMMetadataIdentifier'):
                bundles[path.rsplit('/', 2)[-2]] = plist['MCMMetadataIdentifier']

    kinds = {}
    for path in files:
        inside = _IN_FOLDER.match(path)
        if inside:
            for pattern, kind in _KINDS:
                if pattern.match(inside.group(2)):
                    kinds.setdefault(inside.group(1), set()).add(kind)

    def place(path):
        match = _CONTAINER.search(path)
        if not match:
            return '', 'Other'
        bundle = bundles.get(match.group(2), '')
        if '/com.apple.SafariViewService/' in path:
            return bundle, 'SafariViewService'
        if '/WebsiteDataStore/' in path:
            return bundle, 'App data store'
        return bundle, 'App' if match.group(1) == 'Application' else 'App extension'

    data_list = []
    sources = []
    old_idb_seen = set()
    for path in sorted(files):
        if _ORIGIN_FILE.search(path):
            try:
                with open(real[path], 'rb') as handle:
                    decoded = decode_origin_file(handle.read())
            except OSError as error:
                logfunc(f'WebKit origins: could not read {path}: {error}')
                continue
            if decoded is None:
                logfunc(f'WebKit origins: origin file did not decode: {path}')
                continue
            top, frame = decoded
            folder = path.rsplit('/', 1)[0]
            bundle, store = place(path)
            data_list.append((_modified(seeker, real[path]), bundle, store, _text(top), _text(frame),
                              ', '.join(sorted(kinds.get(folder, ()))), 'origin file'))
            sources.append(real[path])
        elif path.endswith('.localstorage') and '/WebsiteData/' in path and not _IN_FOLDER.match(path):
            parsed = parse_database_identifier(path.rsplit('/', 1)[-1][:-len('.localstorage')])
            if parsed is None:
                continue
            bundle, store = place(path)
            data_list.append((_modified(seeker, real[path]), bundle, store, '', _text(parsed), 'LocalStorage',
                              'file name'))
            sources.append(real[path])
        elif path.endswith('/IndexedDB.sqlite3') and not _IN_FOLDER.match(path):
            match = _OLD_IDB.search(path)
            if not match or parse_database_identifier(match.group(1)) is None:
                continue
            key = path[:match.start(1)] + match.group(1)
            if key in old_idb_seen:
                continue
            old_idb_seen.add(key)
            bundle, store = place(path)
            data_list.append((_modified(seeker, real[path]), bundle, store, '',
                              _text(parse_database_identifier(match.group(1))), 'IndexedDB', 'folder name'))
            sources.append(real[path])

    data_headers = (
        ('Modified', 'datetime'), 'Bundle ID', 'Store', 'Top Origin', 'Origin', 'Data Kinds', 'Origin Read From',
    )
    return data_headers, data_list, '\n'.join(sources)
