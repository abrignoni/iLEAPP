__artifacts_v2__ = {
    "ornet_browser_tabs": {
        "name": "OrNET Browser - Open Tabs",
        "description": "URLs of the tabs that were open in OrNET Browser, from the archived open "
                       "and private tab lists in the app preferences",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "OrNET Browser",
        "notes": "The open_tabs and privateTabs preference values are NSKeyedArchiver plists holding "
                 "NSURL objects; each is decoded to its URL. Private tab URLs come from the "
                 "privateTabs value and are labelled as such. The app with bundle id "
                 "ch.b-eng.tor names itself OrNET Browser in its bundle's Info.plist, read from "
                 "the tested image; iLEAPP releases up to v2026.3.0 labelled these artifacts "
                 "Onion Browser, which is a different app.",
        "paths": ('*/Library/Preferences/ch.b-eng.tor.plist',),
        "output_types": "standard",
        "artifact_icon": "layers",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | OrNET Browser | 2 rows",
        },
    },
    "ornet_browser_settings": {
        "name": "OrNET Browser - Settings",
        "description": "Connection, privacy and clean-up settings from OrNET Browser, including the "
                       "Tor connection mode and any custom bridge the user configured",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "OrNET Browser",
        "notes": "Values are read directly from the app preferences plist. Each configured custom "
                 "bridge is reported on its own row; a bridge line contains the transport, the "
                 "relay address and its fingerprint as the user entered them. The app with "
                 "bundle id ch.b-eng.tor names itself OrNET Browser in its bundle's Info.plist, "
                 "read from the tested image; iLEAPP releases up to v2026.3.0 labelled these "
                 "artifacts Onion Browser, which is a different app.",
        "paths": ('*/Library/Preferences/ch.b-eng.tor.plist',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | OrNET Browser | 21 rows",
        },
    },
    "ornet_browser_bookmarks": {
        "name": "OrNET Browser - Bookmarks",
        "description": "Bookmarks saved in OrNET Browser, with the page title, the URL and the site "
                       "icon",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "OrNET Browser",
        "notes": "Read from the class_BookmarkItem table of the app's Realm store "
                 "(Documents/default.realm) using the vendored realm_parser. The stored icon is a "
                 "base64 PNG and is checked in. The app with bundle id ch.b-eng.tor names "
                 "itself OrNET Browser in its bundle's Info.plist, read from the tested image; "
                 "iLEAPP releases up to v2026.3.0 labelled these artifacts Onion Browser, which "
                 "is a different app.",
        "paths": ('*/Documents/default.realm*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | OrNET Browser | 1 row",
        },
    },
    "ornet_browser_favourites": {
        "name": "OrNET Browser - Favourites",
        "description": "Favourite sites shown on the OrNET Browser start page, with the title, the "
                       "URL and the site icon",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "OrNET Browser",
        "notes": "Read from the class_FavouriteModel table of the app's Realm store. The app ships "
                 "with preset favourites, so a row does not on its own show the user added it. "
                 "The app with bundle id ch.b-eng.tor names itself OrNET Browser in its "
                 "bundle's Info.plist, read from the tested image; iLEAPP releases up to "
                 "v2026.3.0 labelled these artifacts Onion Browser, which is a different app.",
        "paths": ('*/Documents/default.realm*',),
        "output_types": "standard",
        "artifact_icon": "star",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | OrNET Browser | 7 rows",
        },
    },
    "ornet_browser_history": {
        "name": "OrNET Browser - Browsing History",
        "description": "Pages recorded in OrNET Browser browsing history, with the title, the URL, "
                       "the site icon and the date and time shown to the user",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "OrNET Browser",
        "notes": "Read from the class_BrowsingHistoryItem table of the app's Realm store. The date "
                 "and time are the display strings the app stored, in device local time. The "
                 "app with bundle id ch.b-eng.tor names itself OrNET Browser in its bundle's "
                 "Info.plist, read from the tested image; iLEAPP releases up to v2026.3.0 "
                 "labelled these artifacts Onion Browser, which is a different app.",
        "paths": ('*/Documents/default.realm*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | OrNET Browser | 1 row",
        },
    },
}

import base64
import binascii
import plistlib

import nska_deserialize

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    convert_plist_date_to_utc,
    get_file_path,
)
from scripts.realm_parser import parse_realm_file, realm_rows

# Preference keys reported by the settings artifact, in the order shown, with readable labels.
_SETTINGS = [
    ('browser_connection_mode', 'Connection Mode'),
    ('kSelectedVPNAddress', 'Selected VPN Address'),
    ('kSelectedVPNCity', 'Selected VPN City'),
    ('lastSelectedServer', 'Last Selected Server'),
    ('kIsSearchHistory', 'Search History Enabled'),
    ('isCookiesEnabled', 'Cookies Enabled'),
    ('isPersistentCookiesSelected', 'Persistent Cookies'),
    ('is_JavaScript_On', 'JavaScript Enabled'),
    ('isFingerprintingEnabled', 'Fingerprinting Protection Off'),
    ('isWebGLEnabled', 'WebGL Enabled'),
    ('isDeleteBrowsingHistorySelected', 'Delete Browsing History On Exit'),
    ('isDeleteCacheSelected', 'Delete Cache On Exit'),
    ('isDeleteCookiesSelected', 'Delete Cookies On Exit'),
    ('isDeleteSuggestionSelected', 'Delete Suggestions On Exit'),
    ('isPrivacyBlurOn', 'Privacy Blur On'),
    ('isBottomSearchBar', 'Bottom Search Bar'),
    ('PremiumUser', 'Premium User'),
    ('activatedSubscription', 'Activated Subscription'),
]


def _load_plist(path):
    try:
        with open(path, 'rb') as handle:
            return plistlib.load(handle)
    except (OSError, plistlib.InvalidFileException, ValueError):
        return {}


def _decode_tab_urls(value):
    urls = []
    if not isinstance(value, (bytes, bytearray)):
        return urls
    try:
        import io
        objects = nska_deserialize.deserialize_plist(io.BytesIO(value))
    except Exception:  # pylint: disable=broad-except
        return urls
    if not isinstance(objects, list):
        objects = [objects]
    for obj in objects:
        if isinstance(obj, dict):
            url = obj.get('NS.relative') or obj.get('NS.base')
            if url:
                urls.append(url)
        elif isinstance(obj, str):
            urls.append(obj)
    return urls


@artifact_processor
def ornet_browser_tabs(context):
    source_path = get_file_path(context.get_files_found(), 'ch.b-eng.tor.plist')
    plist = _load_plist(source_path)
    data_list = []

    for url in _decode_tab_urls(plist.get('open_tabs')):
        data_list.append(('Open', url))
    for url in _decode_tab_urls(plist.get('privateTabs')):
        data_list.append(('Private', url))

    data_headers = (
        'Tab Type',
        'URL',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ornet_browser_settings(context):
    source_path = get_file_path(context.get_files_found(), 'ch.b-eng.tor.plist')
    plist = _load_plist(source_path)
    data_list = []

    last_active = plist.get('lastActiveTime')
    if last_active is not None:
        try:
            last_active = convert_plist_date_to_utc(last_active)
        except (TypeError, ValueError):
            pass
        data_list.append(('Last Active Time', last_active))

    for key, label in _SETTINGS:
        if key in plist:
            value = plist[key]
            if isinstance(value, bool):
                value = 'Yes' if value else 'No'
            data_list.append((label, value))

    bridges = plist.get('customBridges')
    if isinstance(bridges, list):
        for bridge in bridges:
            data_list.append(('Custom Bridge', bridge))

    data_headers = (
        'Setting',
        'Value',
    )
    return data_headers, data_list, source_path


def _is_ornet_realm(path):
    """The default.realm glob is shared by several apps, so confirm this Realm
    carries OrNET Browser classes before reporting rows."""
    tables = parse_realm_file(path).get("active", {})
    return any(name in tables for name in
               ('class_BookmarkItem', 'class_FavouriteModel', 'class_BrowsingHistoryItem'))


def _ornet_realm_path(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('default.realm') and _is_ornet_realm(file_found):
            return file_found
    return ''


def _check_in_icon(source_path, icon, name):
    """OrNET Browser stores site icons as base64 PNG; decode and check in."""
    if not icon or not isinstance(icon, str):
        return ''
    try:
        raw = base64.b64decode(icon)
    except (binascii.Error, ValueError):
        return ''
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        return ''
    return check_in_embedded_media(source_path, raw, name,
                                   force_type='image/png', force_extension='png') or ''


@artifact_processor
def ornet_browser_bookmarks(context):
    source_path = _ornet_realm_path(context.get_files_found())
    data_list = []

    for index, row in enumerate(realm_rows(source_path, 'class_BookmarkItem')):
        icon = _check_in_icon(source_path, row.get('icon'), f'ornet_bookmark_{index}.png')
        data_list.append((row.get('title'), row.get('url'), icon))

    data_headers = (
        'Title',
        'URL',
        ('Icon', 'media'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def ornet_browser_favourites(context):
    source_path = _ornet_realm_path(context.get_files_found())
    data_list = []

    for index, row in enumerate(realm_rows(source_path, 'class_FavouriteModel')):
        icon = _check_in_icon(source_path, row.get('icon'), f'ornet_favourite_{index}.png')
        data_list.append((row.get('title'), row.get('url'), icon))

    data_headers = (
        'Title',
        'URL',
        ('Icon', 'media'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def ornet_browser_history(context):
    source_path = _ornet_realm_path(context.get_files_found())
    data_list = []

    for index, row in enumerate(realm_rows(source_path, 'class_BrowsingHistoryItem')):
        icon = _check_in_icon(source_path, row.get('icon'), f'ornet_history_{index}.png')
        data_list.append((
            row.get('date'),
            row.get('time'),
            row.get('title'),
            row.get('url'),
            icon,
        ))

    data_headers = (
        'Date (device local)',
        'Time (device local)',
        'Title',
        'URL',
        ('Icon', 'media'),
    )
    return data_headers, data_list, source_path
