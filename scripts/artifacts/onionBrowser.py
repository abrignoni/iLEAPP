__artifacts_v2__ = {
    "onion_browser_bookmarks": {
        "name": "Onion Browser - Bookmarks",
        "description": "Bookmarks saved in Onion Browser, with the page name, the URL and the "
                       "stored site icon",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Onion Browser",
        "notes": "Read from Documents/bookmarks.plist of the Onion Browser app "
                 "(com.miketigas.OnionBrowser). The file holds a version number and a bookmarks "
                 "list whose entries carry name, url and an icon value naming a PNG stored "
                 "beside the plist. The app seeds a set of default bookmarks on first run, so a "
                 "row does not on its own show the user added it. Reference: Bookmark.swift in "
                 "the app's published source, github.com/OnionBrowser/OnionBrowser/blob/"
                 "9a17dd4f2ee61697a8c65af5b09380b3d32646a8/OnionBrowser/Bookmarks/Bookmark.swift. "
                 "The sibling host_settings.plist is not parsed: OrNET Browser, a different app, "
                 "writes a file of the same name and layout.",
        "paths": ('*/Documents/bookmarks.plist',
                  '*/Documents/????????-????-????-????-????????????'),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "hickman_ios13": "iOS 13.3.1 | 10 rows",
            "hickman_ios14": "iOS 14.3 | 9 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows, the seeded default set",
            "felix_ios17": "iOS 17.6.1 | 10 rows, the seeded default set",
        },
    },
    "onion_browser_hsts": {
        "name": "Onion Browser - HSTS Cache",
        "description": "Hosts recorded in Onion Browser's HSTS cache, each with the expiration "
                       "of its strict-transport-security entry",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Onion Browser",
        "notes": "Read from Documents/hsts_cache.plist of the Onion Browser app "
                 "(com.miketigas.OnionBrowser). An entry without the Preloaded flag is written "
                 "when the app receives a Strict-Transport-Security header in an HTTPS response "
                 "from that host; its expiration comes from the header's max-age and is not a "
                 "visit timestamp, and such hosts include content-delivery and analytics "
                 "servers, so the entry shows the browser received a response from the host, "
                 "not that the user opened it as a page. Older app versions also persisted the "
                 "bundled preload list into this file, flagged preloaded, with a synthetic "
                 "expiration one year from when the app loaded the cache; an iOS 13-era store "
                 "held 67,303 entries of which 9 were unflagged. Current versions write only "
                 "received entries. References in the app's published source: "
                 "github.com/OnionBrowser/OnionBrowser/blob/"
                 "9a17dd4f2ee61697a8c65af5b09380b3d32646a8/OnionBrowser/HstsCache.swift "
                 "(parseHstsHeader and persist) and blob/v2.7.4 Endless/HSTSCache.m "
                 "(dictFromSharedHSTSCache mixing in the preload list) with the key names in "
                 "Endless/HSTSCache.h. Expirations are future-dated by design, so this "
                 "artifact writes no timeline entries.",
        "paths": ('*/Documents/hsts_cache.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield-lock",
        "sample_data": {
            "hickman_ios13": "iOS 13.3.1 | 67,303 rows, 9 not flagged preloaded",
            "hickman_ios14": "iOS 14.3 | 67,304 rows, 12 not flagged preloaded",
            "felix23_ios16": "iOS 16.5 | 4 rows, none preloaded",
            "felix_ios17": "iOS 17.6.1 | 4 rows, none preloaded",
        },
    },
}

import os
import plistlib

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_plist_date_to_utc,
)


def _load_plist(path):
    try:
        with open(path, 'rb') as handle:
            return plistlib.load(handle)
    except (OSError, plistlib.InvalidFileException, ValueError):
        return {}


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


@artifact_processor
def onion_browser_bookmarks(context):
    files_found = [str(f) for f in context.get_files_found()]
    data_list = []
    source_paths = set()

    # Icon files sit beside the plist, named by a bare UUID.
    icons_by_dir = {}
    for found in files_found:
        if not found.endswith('bookmarks.plist'):
            icons_by_dir.setdefault(os.path.dirname(found), {})[
                os.path.basename(found)] = found

    for found in files_found:
        if not found.endswith('bookmarks.plist'):
            continue
        plist = _load_plist(found)
        # Other apps could carry a Documents/bookmarks.plist; only the
        # version-plus-bookmarks layout of this app is reported.
        if not isinstance(plist, dict) or not isinstance(plist.get('bookmarks'), list):
            continue
        source_paths.add(found)
        icons = icons_by_dir.get(os.path.dirname(found), {})
        for entry in plist['bookmarks']:
            if not isinstance(entry, dict):
                continue
            media_ref = ''
            icon_name = entry.get('icon')
            icon_path = icons.get(icon_name) if isinstance(icon_name, str) else None
            if icon_path:
                extension = None
                try:
                    with open(icon_path, 'rb') as handle:
                        magic = handle.read(8)
                    if magic.startswith(b'\x89PNG'):
                        extension = 'png'
                    elif magic.startswith(b'\xff\xd8'):
                        extension = 'jpg'
                except OSError:
                    pass
                media_ref = check_in_media(icon_path, entry.get('name', ''),
                                           force_extension=extension) or ''
            data_list.append((
                entry.get('name'),
                entry.get('url'),
                media_ref,
                context.get_relative_path(found),
            ))

    data_headers = (
        'Name',
        'URL',
        ('Icon', 'media'),
        'Source Path',
    )
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def onion_browser_hsts(context):
    data_list = []
    source_paths = set()

    for found in context.get_files_found():
        found = str(found)
        if not found.endswith('hsts_cache.plist'):
            continue
        plist = _load_plist(found)
        if not isinstance(plist, dict):
            continue
        source_paths.add(found)
        for host, entry in sorted(plist.items(),
                                  key=lambda kv: bool(kv[1].get('preloaded'))
                                  if isinstance(kv[1], dict) else True):
            if not isinstance(entry, dict) or 'expiration' not in entry:
                continue
            expiration = entry.get('expiration')
            try:
                expiration = convert_plist_date_to_utc(expiration)
            except (TypeError, ValueError):
                pass
            data_list.append((
                expiration,
                host,
                _yes_no(entry.get('allowSubdomains')),
                _yes_no(entry.get('preloaded')),
                context.get_relative_path(found),
            ))

    data_headers = (
        ('Expiration', 'datetime'),
        'Host',
        'Allow Subdomains',
        'Preloaded',
        'Source Path',
    )
    return data_headers, data_list, '\n'.join(sorted(source_paths))
