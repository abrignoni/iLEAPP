""" appInventory.py - extraction, app and file inventory for coverage analysis

This module writes three machine-readable tables into the LAVA SQLite output
(_lava_artifacts.db) so downstream tooling (e.g. batch-leapp) can determine,
per extraction, which installed apps exist, which files belong to each app
container, and which extraction/device the data came from. Combined with the
_artifact_search_patterns / _file_path_list / _artifact_pattern_to_file
registry tables the framework already writes, this makes it possible to diff
"apps installed" against "apps parsed by the tooling".

Notes:
- appFileInventory lists EVERY file in the extraction (not only app container
  files) so unparsed non-app data can be measured too. It is lava_only to
  keep the HTML report usable.
- Modified Time values are stored as text, not LAVA datetime: zip archives
  record zone-less DOS timestamps, so coercing them to UTC would be wrong.
  Tar, directory and iTunes sources are recorded in UTC.
"""

__artifacts_v2__ = {
    "extractionInfo": {
        "name": "Extraction Info",
        "description": "Identifiers for this extraction and parse run: LEAPP version, "
                       "input path, extraction type, iOS version and device identifiers "
                       "when available. Written to the LAVA database so batch tooling "
                       "can tell which device/extraction the data came from.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-08",
        "last_update_date": "2026-07-08",
        "requirements": "none",
        "category": "App Inventory",
        "notes": "",
        "paths": None,
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "id",
    },
    "installedAppInventory": {
        "name": "Installed App Inventory",
        "description": "Canonical installed application inventory: one row per app "
                       "container (bundle, data, shared group, plugin) with its bundle ID, "
                       "container path and UUID. Sources: applicationState.db and "
                       ".com.apple.mobile_container_manager.metadata.plist files.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-08",
        "last_update_date": "2026-07-08",
        "requirements": "none",
        "category": "App Inventory",
        "notes": "",
        "paths": (
            '*/mobile/Library/FrontBoard/applicationState.db*',
            '*/[Cc]ontainers/Bundle/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
    },
    "appFileInventory": {
        "name": "App File Inventory",
        "description": "Complete file listing of the extraction with each file mapped to "
                       "the app container (bundle ID) it belongs to, when applicable. "
                       "Supports coverage analysis of which apps/files the tooling parsed. "
                       "LAVA only due to size.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-08",
        "last_update_date": "2026-07-08",
        "requirements": "none",
        "category": "App Inventory",
        "notes": "Modified Time is text as recorded in the source (zip timestamps are "
                 "zone-less; tar/directory/iTunes timestamps are UTC).",
        "paths": None,
        "output_types": "lava_only",
        "artifact_icon": "files",
    },
}

import io
import os
import plistlib
import re
import sys
from datetime import datetime, timezone

import biplist
import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, \
    logfunc, open_sqlite_db_readonly
from scripts.version_info import leapp_name, leapp_version


# Container metadata plists searched to map container UUIDs to bundle IDs.
# Bundle containers live under lowercase '/private/var/containers/' on device;
# the [Cc] class covers both just in case.
_CONTAINER_METADATA_PATTERNS = (
    ('*/[Cc]ontainers/Bundle/Application/*/.com.apple.mobile_container_manager.metadata.plist', 'bundle'),
    ('*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist', 'data'),
    ('*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist', 'group'),
    ('*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist', 'plugin'),
)

_CONTAINER_SEGMENTS = (
    ('containers/bundle/application/', 'bundle'),
    ('containers/data/application/', 'data'),
    ('containers/shared/appgroup/', 'group'),
    ('containers/data/pluginkitplugin/', 'plugin'),
)

_GUID_RE = re.compile(
    r'containers/(Bundle/Application|Data/Application|Shared/AppGroup|Data/PluginKitPlugin)'
    r'/([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})(?=/|$)',
    re.IGNORECASE)

_GUID_SEGMENT_TYPE = {
    'bundle/application': 'bundle',
    'data/application': 'data',
    'shared/appgroup': 'group',
    'data/pluginkitplugin': 'plugin',
}

# iTunes backup domain prefixes mapped to container types.
_ITUNES_DOMAIN_PREFIXES = (
    ('AppDomainGroup-', 'group'),
    ('AppDomainPlugin-', 'plugin'),
    ('AppDomain-', 'data'),
)

_APPSTATE_QUERY = '''SELECT application_identifier_tab.application_identifier,
                    key_tab.key,
                    kvs.value
             FROM kvs LEFT JOIN application_identifier_tab
             ON application_identifier_tab.id = kvs.application_identifier
             LEFT JOIN key_tab ON kvs.key = key_tab.id
             WHERE key_tab.key = 'compatibilityInfo'
          '''


def _seeker_kind(seeker):
    '''Human-readable extraction type from the seeker class name.'''
    kind = type(seeker).__name__
    return {
        'FileSeekerDir': 'directory',
        'FileSeekerItunes': 'itunes backup',
        'FileSeekerTar': 'tar',
        'FileSeekerZip': 'zip',
        'FileSeekerFile': 'single file',
    }.get(kind, kind)


def _input_path(seeker):
    '''Best-effort path of the extraction input for this seeker.'''
    zip_file = getattr(seeker, 'zip_file', None)
    if zip_file is not None:
        return getattr(zip_file, 'filename', '') or ''
    tar_file = getattr(seeker, 'tar_file', None)
    if tar_file is not None:
        return getattr(tar_file, 'name', '') or ''
    return getattr(seeker, 'directory', '') or ''


def _parse_blob(appid, blob):
    '''Deserialize a compatibilityInfo blob (based on applicationStateDB.py).'''
    if blob is None:
        return None
    plist_file_object = io.BytesIO(blob)
    if blob.find(b'NSKeyedArchiver') == -1:
        if sys.version_info >= (3, 9):
            plist = plistlib.load(plist_file_object)
        else:
            plist = biplist.readPlist(plist_file_object)
    else:
        try:
            plist = nd.deserialize_plist(plist_file_object)
        except (nd.DeserializeError, nd.biplist.NotBinaryPlistException,
                nd.biplist.InvalidPlistException, nd.plistlib.InvalidFileException,
                nd.ccl_bplist.BplistError, ValueError, TypeError, OSError, OverflowError) as ex:
            logfunc(f'WARNING: Failed to read compatibilityInfo blob for {appid}: {ex}')
            return None
    return plist if isinstance(plist, dict) else None


def _parse_application_state(db_path):
    '''Yield (bundle_id, bundle_path, sandbox_path) from applicationState.db.'''
    results = []
    try:
        db = open_sqlite_db_readonly(db_path)
        cursor = db.cursor()
        cursor.execute(_APPSTATE_QUERY)
        all_rows = cursor.fetchall()
        db.close()
    except Exception as ex:  # pylint: disable=broad-except
        logfunc(f'WARNING: could not query {db_path}: {ex}')
        return results
    for appid, _key, value in all_rows:
        compat_info = _parse_blob(appid, value)
        if compat_info is None:
            continue
        results.append((compat_info.get('bundleIdentifier', ''),
                        compat_info.get('bundlePath', ''),
                        compat_info.get('sandboxPath', '')))
    return results


def _read_container_metadata(plist_path):
    '''Return (identifier, container_uuid) from a container metadata plist.'''
    identifier = ''
    try:
        with open(plist_path, 'rb') as fp:
            pl = plistlib.load(fp)
        identifier = pl.get('MCMMetadataIdentifier', '')
    except Exception as ex:  # pylint: disable=broad-except
        logfunc(f'WARNING: could not read {plist_path}: {ex}')
    uuid = os.path.basename(os.path.dirname(plist_path))
    return identifier, uuid


def _container_type_from_path(path):
    '''Container type based on the path of a container metadata plist.'''
    normalized = path.replace('\\', '/').lower()
    for segment, ctype in _CONTAINER_SEGMENTS:
        if segment in normalized:
            return ctype
    return ''


def _guids_from_device_path(device_path):
    '''Yield (uuid, container_type) for container GUIDs found in a device path.'''
    for match in _GUID_RE.finditer(device_path.replace('\\', '/')):
        yield match.group(2).upper(), _GUID_SEGMENT_TYPE.get(match.group(1).lower(), '')


def _build_guid_map(seeker):
    '''Map container UUID (uppercased) -> bundle/group identifier.

    Built from the container metadata plists and, as a fallback, from the
    bundle/sandbox paths recorded in applicationState.db.
    '''
    guid_map = {}
    for pattern, _ctype in _CONTAINER_METADATA_PATTERNS:
        for found in seeker.search(pattern):
            identifier, uuid = _read_container_metadata(str(found))
            if identifier and uuid:
                guid_map.setdefault(uuid.upper(), identifier)
    appstate = seeker.search('*/mobile/Library/FrontBoard/applicationState.db',
                             return_on_first_hit=True)
    if appstate:
        for bundle_id, bundle_path, sandbox_path in _parse_application_state(str(appstate)):
            if not bundle_id:
                continue
            for device_path in (bundle_path, sandbox_path):
                if not device_path:
                    continue
                for uuid, _ctype in _guids_from_device_path(device_path):
                    guid_map.setdefault(uuid, bundle_id)
    return guid_map


def _format_utc(epoch):
    '''Epoch seconds -> "YYYY-MM-DD HH:MM:SS" UTC text, or empty string.'''
    if not epoch:
        return ''
    try:
        return datetime.fromtimestamp(epoch, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    except (OverflowError, OSError, ValueError):
        return ''


def _iter_extraction_files(seeker):
    '''Yield (path, size, modified_time_text) for every file in the extraction.

    Reads the seeker's existing listings (zip/tar central directory, directory
    walk, iTunes manifest) without extracting or copying anything.
    '''
    zip_file = getattr(seeker, 'zip_file', None)
    if zip_file is not None:
        for info in zip_file.infolist():
            if info.is_dir() or info.filename.startswith('__MACOSX'):
                continue
            d = info.date_time
            mtime = f'{d[0]:04d}-{d[1]:02d}-{d[2]:02d} {d[3]:02d}:{d[4]:02d}:{d[5]:02d}'
            yield info.filename, info.file_size, mtime
        return
    tar_file = getattr(seeker, 'tar_file', None)
    if tar_file is not None:
        for member in tar_file.getmembers():
            if not member.isfile():
                continue
            yield member.name, member.size, _format_utc(member.mtime)
        return
    all_files = getattr(seeker, '_all_files', None)
    if isinstance(all_files, dict):
        # iTunes backup: relative "Domain/path" keys; sizes are not in the listing.
        for path in all_files:
            yield path, '', ''
        return
    if isinstance(all_files, list):
        directory = getattr(seeker, 'directory', '')
        for item in all_files:
            try:
                if os.path.isdir(item):
                    continue
                stat = os.stat(item)
                size, mtime = stat.st_size, _format_utc(stat.st_mtime)
            except OSError:
                size, mtime = '', ''
            rel = item.replace(directory, '', 1) if directory else item
            yield rel, size, mtime


def _map_path_to_app(path, guid_map):
    '''Return (bundle_id, container_type, container_uuid) for an extraction path.'''
    normalized = path.replace('\\', '/')
    match = _GUID_RE.search(normalized)
    if match:
        uuid = match.group(2).upper()
        ctype = _GUID_SEGMENT_TYPE.get(match.group(1).lower(), '')
        return guid_map.get(uuid, ''), ctype, uuid
    first_segment = normalized.lstrip('/').split('/', 1)[0]
    for prefix, ctype in _ITUNES_DOMAIN_PREFIXES:
        if first_segment.startswith(prefix):
            return first_segment[len(prefix):], ctype, ''
    return '', '', ''


@artifact_processor
def extractionInfo(context):
    '''One row per identifier describing this extraction and parse run.'''
    seeker = context.get_seeker()
    out_params = context.get_output_params()
    data_list = []

    def add(prop, value, source=''):
        if value is not None and value != '':
            data_list.append((prop, str(value), source))

    input_path = _input_path(seeker)
    add('LEAPP Name', leapp_name)
    add('LEAPP Version', leapp_version)
    add('Extraction Type', _seeker_kind(seeker))
    add('Input Path', input_path)
    add('Input Name', os.path.basename(input_path) if input_path else '')
    add('Report Folder', os.path.basename(out_params.output_folder_base))
    add('iOS Version', context.get_installed_os_version() or '')

    data_ark = seeker.search('*/root/Library/Lockdown/data_ark.plist',
                             return_on_first_hit=True)
    if data_ark:
        pl = get_plist_file_content(str(data_ark))
        if isinstance(pl, dict):
            for key, label in (('-DeviceName', 'Device Name'),
                               ('-TimeZone', 'Time Zone')):
                add(label, pl.get(key, ''), 'data_ark.plist')

    # iTunes backups: Info.plist sits at the backup root, outside the manifest.
    directory = getattr(seeker, 'directory', '')
    info_plist = os.path.join(directory, 'Info.plist') if directory else ''
    if _seeker_kind(seeker) == 'itunes backup' and os.path.isfile(info_plist):
        pl = get_plist_file_content(info_plist)
        if isinstance(pl, dict):
            for key in ('Device Name', 'Product Type', 'Product Version',
                        'Build Version', 'Serial Number', 'Unique Identifier',
                        'IMEI', 'Phone Number', 'Last Backup Date'):
                add(key, pl.get(key, ''), 'Info.plist')

    data_headers = ('Property', 'Value', 'Source')
    return data_headers, data_list, input_path


@artifact_processor
def installedAppInventory(context):
    '''One row per app container with its bundle ID, path and UUID.'''
    files_found = context.get_files_found()
    rows = {}

    def add(bundle_id, ctype, container_path, uuid, source):
        if not container_path and not bundle_id:
            return
        key = (bundle_id, ctype, uuid.upper() if uuid else container_path)
        if key not in rows:
            rows[key] = (bundle_id, ctype, container_path, uuid.upper() if uuid else '', source)

    appstate_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            identifier, uuid = _read_container_metadata(file_found)
            container_dir = os.path.dirname(context.get_relative_path(file_found))
            add(identifier, _container_type_from_path(file_found), container_dir,
                uuid, '.com.apple.mobile_container_manager.metadata.plist')
        elif file_found.endswith('applicationState.db'):
            appstate_path = file_found
            for bundle_id, bundle_path, sandbox_path in _parse_application_state(file_found):
                for device_path, default_type in ((bundle_path, 'bundle'),
                                                  (sandbox_path, 'data')):
                    if not device_path:
                        continue
                    guids = list(_guids_from_device_path(device_path))
                    uuid = guids[0][0] if guids else ''
                    ctype = guids[0][1] if guids else default_type
                    add(bundle_id, ctype, device_path, uuid, 'applicationState.db')

    data_list = sorted(rows.values())
    logfunc(f'Installed App Inventory: {len(data_list)} container(s) recorded')
    data_headers = ('Bundle ID', 'Container Type', 'Container Path',
                    'Container UUID', 'Data Source')
    source_path = appstate_path or get_file_path(
        files_found, '.com.apple.mobile_container_manager.metadata.plist') or ''
    return data_headers, data_list, source_path


@artifact_processor
def appFileInventory(context):
    '''Every file in the extraction, mapped to its app container when possible.'''
    seeker = context.get_seeker()
    guid_map = _build_guid_map(seeker)

    data_list = []
    mapped = 0
    for path, size, mtime in _iter_extraction_files(seeker):
        bundle_id, ctype, uuid = _map_path_to_app(path, guid_map)
        if bundle_id:
            mapped += 1
        data_list.append((bundle_id, ctype, uuid, path, size, mtime))

    logfunc(f'App File Inventory: {len(data_list)} file(s) listed, '
            f'{mapped} mapped to {len(guid_map)} known container(s)')
    data_headers = ('Bundle ID', 'Container Type', 'Container UUID',
                    'File Path', 'File Size', 'Modified Time')
    return data_headers, data_list, _input_path(seeker)
