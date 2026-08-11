import glob
import os
import plistlib
import re

from scripts.filetype import guess_mime
from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc

__artifacts_v2__ = {
    "fsCachedData": {
        "name": "fsCachedData",
        "description": "Media and other files cached under fsCachedData",
        "author": "@abrignoni & @stark4n6",
        "creation_date": "2023-02-02",
        "last_update_date": "2026-07-29",
        "requirements": "none",
        "category": "Cache Data",
        "notes": "Source location in the extraction is provided for each item.",
        "paths": (
            '*/fsCachedData/**',
            '*/Shared/AppGroup/*/Library/Preferences/*.plist',
            '*/AppGroup/*/Library/Preferences/*.plist',
            '*/Containers/Data/Application/*/Library/Preferences/*.plist',
        ),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2746 rows",
            "dexter_ios18": "iOS 18.3.2 | 1708 rows",
            "felix_ios17": "iOS 17.6.1 | 872 rows",
            "fsfull002_ios17": "iOS 17.1 | 298 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2754 rows",
            "iphone11_ios17": "iOS 17.3 | 3900 rows",
            "iphone12_ios18": "iOS 18.7 | 915 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1101 rows",
            "otto_ios17": "iOS 17.5.1 | 3221 rows",
            "abe_ios16": "iOS 16.5 | 4937 rows",
            "felix23_ios16": "iOS 16.5 | 1056 rows",
            "hickman_ios13": "iOS 13.3.1 | 1056 rows",
            "hickman_ios14": "iOS 14.3 | 1991 rows",
            "jess_ios15": "iOS 15.0.2 | 1138 rows",
            "magnet_ios16": "iOS 16.1.1 | 1037 rows",
        }
    }
}

# System plist stems that should be ignored when looking for the main app bundle
IGNORED_SYSTEM_PLISTS = {
    'com.apple.peoplepicker',
    'com.apple.uikit',
    'com.apple.metal',
    'com.apple.mobilephone',
    'com.apple.security',
    'com.apple.locationd',
    'com.apple.webinspector',
    'com.apple.coremedia',
}


def get_application_bundle_name(file_found, app_plist_map):
    """Determine bundle name for Application container paths by inspecting Preferences plists."""
    match = re.search(r'[\/\\]Application[\/\\]([^\/\\]+)', file_found, re.I)
    if not match:
        return ''

    app_guid = match.group(1).upper()

    # 1. Look up in pre-indexed plist map
    if app_guid in app_plist_map:
        plist_paths = app_plist_map[app_guid]

        # Prioritize non-system reverse-domain plists
        candidates = []
        for plist_path in plist_paths:
            stem = os.path.splitext(os.path.basename(plist_path))[0]
            if stem.lower() in IGNORED_SYSTEM_PLISTS:
                continue

            # Check if plist contains internal bundle identifier keys
            try:
                with open(plist_path, 'rb') as f:
                    plist_data = plistlib.load(f)
                    if isinstance(plist_data, dict):
                        bundle_id = (
                            plist_data.get('CFBundleIdentifier')
                            or plist_data.get('MCMMetadataIdentifier')
                        )
                        if bundle_id:
                            return str(bundle_id)
            except (OSError, plistlib.InvalidFileException):
                pass

            candidates.append(stem)

        # Fallback to candidate stem matching com.* or org.*
        for stem in candidates:
            if stem.lower().startswith(('com.', 'org.', 'net.', 'io.')):
                return stem

        if candidates:
            return candidates[0]

    # 2. Filesystem Fallback
    match_root = re.search(r'^(.*?[\/\\]Application[\/\\][^\/\\]+)', file_found, re.I)
    if match_root:
        app_root = match_root.group(1)
        pref_dir = os.path.join(app_root, 'Library', 'Preferences')
        if os.path.isdir(pref_dir):
            for plist_file in glob.glob(os.path.join(pref_dir, '*.plist')):
                stem = os.path.splitext(os.path.basename(plist_file))[0]
                if stem.lower() in IGNORED_SYSTEM_PLISTS:
                    continue
                if stem.lower().startswith(('com.', 'org.', 'net.', 'io.')):
                    return stem

    return ''


def get_app_group_bundle_name(file_found, app_group_plist_map):
    """Extract bundle name from pre-indexed plist files or filesystem fallback for AppGroup."""
    match = re.search(r'[\/\\]AppGroup[\/\\]([^\/\\]+)', file_found, re.I)
    if not match:
        return ''

    app_group_guid = match.group(1).upper()

    # 1. Look up in pre-indexed plist map
    if app_group_guid in app_group_plist_map:
        plist_paths = app_group_plist_map[app_group_guid]
        for plist_path in plist_paths:
            stem = os.path.splitext(os.path.basename(plist_path))[0]
            if stem.lower().startswith(('group.', 'com.', 'org.')):
                return stem

        if plist_paths:
            return os.path.splitext(os.path.basename(plist_paths[0]))[0]

    # 2. Disk Fallback
    match_root = re.search(r'^(.*?[\/\\]AppGroup[\/\\][^\/\\]+)', file_found, re.I)
    if match_root:
        app_group_root = match_root.group(1)
        pref_dir = os.path.join(app_group_root, 'Library', 'Preferences')
        if os.path.isdir(pref_dir):
            for plist_file in glob.glob(os.path.join(pref_dir, '*.plist')):
                stem = os.path.splitext(os.path.basename(plist_file))[0]
                if stem.lower().startswith(('group.', 'com.', 'org.')):
                    return stem
                return stem

    return ''


def extract_bundle_name(file_path, app_group_plist_map, app_plist_map):
    """Determine the bundle name based on path structure."""
    # Pattern 1: AppGroup paths
    if re.search(r'[\/\\]AppGroup[\/\\]', file_path, re.I):
        return get_app_group_bundle_name(file_path, app_group_plist_map)

    # Pattern 2: Between Caches and nsurlcache
    match = re.search(r'[\/\\]Caches[\/\\](.*?)[\/\\]nsurlcache', file_path, re.I)
    if match:
        return match.group(1)

    # Pattern 3: Between Caches and fsCachedData
    match = re.search(r'[\/\\]Caches[\/\\](.*?)[\/\\]fsCachedData', file_path, re.I)
    if match:
        return match.group(1)

    # Pattern 4: Application container path fallback (e.g. Application Support/fsCachedData)
    if re.search(r'[\/\\]Containers[\/\\]Data[\/\\]Application[\/\\]', file_path, re.I):
        return get_application_bundle_name(file_path, app_plist_map)

    return ''


@artifact_processor
def fsCachedData(context):
    data_headers = (
        ('Timestamp Modified', 'datetime'),
        ('Media', 'media'),
        'Mime Type',
        'Filename',
        'Bundle Name',
        'Path')
    data_list = []

    # Pre-index plist maps by GUID
    app_group_plist_map = {}
    app_plist_map = {}

    files_found = [str(f) for f in context.get_files_found()]

    for file_found in files_found:
        if file_found.lower().endswith('.plist') and re.search(r'[\/\\]Library[\/\\]Preferences[\/\\]', file_found, re.I):
            # Index AppGroup plists
            ag_match = re.search(r'[\/\\]AppGroup[\/\\]([^\/\\]+)', file_found, re.I)
            if ag_match:
                guid = ag_match.group(1).upper()
                app_group_plist_map.setdefault(guid, []).append(file_found)
                continue

            # Index Application plists
            app_match = re.search(r'[\/\\]Application[\/\\]([^\/\\]+)', file_found, re.I)
            if app_match:
                guid = app_match.group(1).upper()
                app_plist_map.setdefault(guid, []).append(file_found)

    for file_found in files_found:
        if not os.path.isfile(file_found) or file_found.lower().endswith('.plist'):
            continue

        modified_time = convert_unix_ts_to_utc(os.path.getmtime(file_found))
        mime = guess_mime(file_found)
        media_ref = check_in_media(file_found)
        bundle_name = extract_bundle_name(file_found, app_group_plist_map, app_plist_map)

        data_list.append((
            modified_time,
            media_ref,
            mime,
            os.path.basename(file_found),
            bundle_name,
            context.get_relative_path(file_found)))

    return data_headers, data_list, ''
