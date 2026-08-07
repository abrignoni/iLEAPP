__artifacts_v2__ = {
    "onion_browser_tabs": {
        "name": "Onion Browser - Open Tabs",
        "description": "URLs of the tabs that were open in Onion Browser, from the archived open "
                       "and private tab lists in the app preferences",
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Onion Browser",
        "notes": "The open_tabs and privateTabs preference values are NSKeyedArchiver plists holding "
                 "NSURL objects; each is decoded to its URL. Private tab URLs come from the "
                 "privateTabs value and are labelled as such.",
        "paths": ('*/Library/Preferences/ch.b-eng.tor.plist',),
        "output_types": "standard",
        "artifact_icon": "layers",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | Onion Browser | 2 rows",
        },
    },
    "onion_browser_settings": {
        "name": "Onion Browser - Settings",
        "description": "Connection, privacy and clean-up settings from Onion Browser, including the "
                       "Tor connection mode and any custom bridge the user configured",
        "author": "",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Onion Browser",
        "notes": "Values are read directly from the app preferences plist. Each configured custom "
                 "bridge is reported on its own row; a bridge line contains the transport, the "
                 "relay address and its fingerprint as the user entered them.",
        "paths": ('*/Library/Preferences/ch.b-eng.tor.plist',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | Onion Browser | settings reported",
        },
    },
}

import plistlib

import nska_deserialize

from scripts.ilapfuncs import artifact_processor, convert_plist_date_to_utc, get_file_path

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
def onion_browser_tabs(context):
    source_path = get_file_path(context.get_files_found(), 'ch.b-eng.tor.plist')
    plist = _load_plist(source_path)
    data_list = []

    for url in _decode_tab_urls(plist.get('open_tabs')):
        data_list.append(('Open', url))
    for url in _decode_tab_urls(plist.get('privateTabs')):
        data_list.append(('Private', url))

    data_headers = (
        'Tab Type',
        ('URL', 'url'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def onion_browser_settings(context):
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
