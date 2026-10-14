__artifacts_v2__ = {
    "onion_browser_bookmarks": {
        "name": "Onion Browser - Bookmarks",
        "description": "Bookmarks held in Onion Browser's bookmark store, including the defaults "
                       "the app seeds on first run, with the page name, the URL and the stored "
                       "site icon",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Onion Browser",
        "notes": "Read from any Documents/bookmarks.plist whose root holds a bookmarks list, the "
                 "layout Onion Browser (com.miketigas.OnionBrowser) writes. The app is not "
                 "confirmed by bundle id; check the Source Path column. The file holds a version "
                 "number and a bookmarks list whose entries carry name, url and an icon value "
                 "naming a PNG stored beside the plist. The app seeds a set of default bookmarks "
                 "on first run, so a row does not on its own show the user added it. Reference: "
                 "Bookmark.swift in the app's published source, "
                 "github.com/OnionBrowser/OnionBrowser/blob/9a17dd4f2ee61697a8c65af5b09380b3d32646a8/OnionBrowser/Bookmarks/Bookmark.swift. "
                 "The sibling host_settings.plist is not parsed.",
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
        "notes": "Read from any Documents/hsts_cache.plist in the extraction, the file Onion "
                 "Browser (com.miketigas.OnionBrowser) writes. The app is not confirmed by "
                 "bundle id; check the Source Path column. An entry without the Preloaded flag "
                 "is written when the app receives a Strict-Transport-Security header in an "
                 "HTTPS response from that host; its expiration comes from the header's "
                 "max-age and is not a visit timestamp, and the app's source at the commit "
                 "cited below parses the header for the host of each HTTPS response it handles "
                 "(Psiphon/JAHPAuthenticatingHTTPProtocol.m at the same commit), so the entry "
                 "shows the browser received a response from the host, not that the user "
                 "opened it as a page. Older app versions also persisted the bundled preload "
                 "list into this file, flagged preloaded, with a synthetic expiration one year "
                 "from when the app loaded the cache; the store on hickman_ios13 (iOS 13.3.1) "
                 "gave 67,303 rows of which 9 were not flagged preloaded. The source at the "
                 "cited commit writes received entries and, when it removes a host that is in "
                 "the bundled preload list, an entry with ignore set and no expiration. This "
                 "artifact reports only entries that carry an expiration. References in the "
                 "app's published source: "
                 "github.com/OnionBrowser/OnionBrowser/blob/9a17dd4f2ee61697a8c65af5b09380b3d32646a8/OnionBrowser/HstsCache.swift "
                 "(parseHstsHeader and persist) and "
                 "github.com/OnionBrowser/OnionBrowser/blob/fc5622891d7e88e4b16884873efc5469296d466c/Endless/HSTSCache.m "
                 "(tag v2.7.3: +retrieve mixes the bundled preload list into the dictionary "
                 "with the one-year expiration and the preloaded key, and writeToFile writes "
                 "the whole dictionary; from tag v2.7.4 writeToFile leaves preloaded entries "
                 "out) with the key names in Endless/HSTSCache.h. An expiration is the time "
                 "the header was received plus its max-age, or a synthetic date for a "
                 "preloaded entry, so it is not the time of an event, and this artifact writes "
                 "no timeline entries.",
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
