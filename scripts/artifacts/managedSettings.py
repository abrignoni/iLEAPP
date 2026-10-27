__artifacts_v2__ = {
    "managedSettings": {
        "name": "ManagedSettings - Settings",
        "description": "Setting keys and values held by the ManagedSettings stores of a sysdiagnose (logs/ManagedSettings) or of a full file system extraction (com.apple.ManagedSettings): install, web content, shield, Siri and intelligence, user safety and similar keys, written as text",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A sysdiagnose holds copies of the ManagedSettings stores under logs/ManagedSettings/User and "
                 "logs/ManagedSettings/System. A full file system extraction holds the live stores in a different layout, "
                 "under /private/var/mobile/Library/com.apple.ManagedSettings and in a com.apple.ManagedSettings.system "
                 "folder of a shared system group container; both are read, and Source File tells the two layouts apart. "
                 "The folder and key names point to the Screen Time and Family Controls settings stores; what the file "
                 "does on the device, and what writes it, is not established by the file. A row is one top-level key of "
                 "one property list: a store file, a clientEffectiveSettings.plist or the EffectiveSettings.plist of the "
                 "scope. In a sysdiagnose a store file is <store identifier>.plist in a folder named for the client of its"
                 " record; in the live layout it is Records/<record identifier>/<store identifier>/detokenized.plist and "
                 "the client effective settings are Records/<record identifier>/clientEffectiveSettings.plist. A file with"
                 " no setting key gives one row that says so. On magnet_ios16 (iOS 16.1.1 full file system) "
                 "SettingRecords.plist sat at the top of com.apple.ManagedSettings, not under Records, and that location "
                 "is read too. Scope is the User or System folder of a sysdiagnose; in the live layout it follows the "
                 "folder, User for com.apple.ManagedSettings and System for com.apple.ManagedSettings.system. On hc_ios26 "
                 "the live SettingRecords.plist of each of those folders was byte-identical to the User and System one of "
                 "the same device's later sysdiagnose, hc_ios26_sysdiag. Scope held User on every row of the four iOS 26 "
                 "corpus images in sample_data, because no System folder held a setting file. The same key and value can "
                 "appear in a store file, in its client's clientEffectiveSettings.plist and in the "
                 "EffectiveSettings.plist: on all four iOS 26 corpus images safari.denyPrivateBrowsing appears in all "
                 "three, so the rows are not a count of settings. Client is the client folder name in a sysdiagnose. In "
                 "the live layout the folders are named by identifier, so Client is the containerIdentifier of the record "
                 "in the SettingRecords.plist of the same folder, and the row's Notes say so. Store Name is the StoreName "
                 "value of a sysdiagnose store file; Store Active and Sync To Watch are the active and syncToWatch values "
                 "of its Properties entry, and any other Properties key is named in Notes. A live detokenized.plist holds "
                 "the setting keys and version of a store without StoreName or Properties: on hc_ios26 each held the keys "
                 "of the hc_ios26_sysdiag store file with the same store identifier minus those two. For a live store file"
                 " Store Name, Store Active and Sync To Watch are therefore the key, active and syncToWatch of its store "
                 "entry in SettingRecords.plist. On ai16_ios26_sysdiag and hc_ios26_sysdiag, for all 8 store entries, the "
                 "client folder name equalled the record's containerIdentifier and the StoreName, active and syncToWatch "
                 "of the store file equalled the store entry; every live record and store folder on hc_ios26 and "
                 "falken_ios26 was listed in its SettingRecords.plist. A live record folder not listed there keeps its "
                 "record identifier as Client; a store folder not listed for its record keeps its Client and gets blank "
                 "store columns; the Notes say which. File Name is the file name without .plist. File Version is the "
                 "version value of the file, as stored. On the four iOS 26 corpus images File Version held 3 on every row,"
                 " while the store entry for the same store in SettingRecords.plist held version 2, so the two are "
                 "different values. The store names are not the same on every device. The iOS 27.0 (24A437) sysdiagnose "
                 "read holds the stores ContentAndPrivacy, Restrictions, UserSafety, defaultGroup, downtime, "
                 "scheduleDowntime, bedtime and Default under com.apple.ScreenTimeSettings, "
                 "com.apple.ScreenTimeSettings.TimeAllowances, com.apple.UserSafety, com.apple.Preferences and "
                 "FamilyControlsAgent, and a second iOS 26.6 (23G71) sysdiagnose, not in the corpus, holds Default, "
                 "SafariStore, UserSafetyStore, UserSafety and DeviceActivityStore under com.apple.ScreenTime, "
                 "com.apple.UserSafety, com.apple.Preferences, com.apple.momentsd and FamilyControlsAgent. On "
                 "ai16_ios26_sysdiag (iOS 26.5.2) the stores were SafariStore, UserSafetyStore, DeviceActivityStore and "
                 "two named UserSafety, under com.apple.ScreenTime, com.apple.momentsd, com.apple.Preferences and "
                 "com.apple.UserSafety; on hc_ios26_sysdiag (iOS 26.6), hc_ios26 (iOS 26.5.2) and falken_ios26 (iOS "
                 "26.2.1) they were SafariStore and two named UserSafety, under com.apple.ScreenTime, "
                 "com.apple.Preferences and com.apple.UserSafety. On those four images the only keys were "
                 "safari.denyHistoryClearing and safari.denyPrivateBrowsing (false wherever they appeared), "
                 "userSafety.allowedClients, userSafety.scanningPolicy and, on ai16_ios26_sysdiag, "
                 "deviceActivity.allowedClients; no app installation, web content or shield key was present. The iOS "
                 "13.3.1, 14.3 and 17.3 sysdiagnoses in sample_data hold no logs/ManagedSettings folder. A key not listed "
                 "here is reported with its key and its value written as text. Setting is a label written from the key "
                 "name; the file does not describe the keys and the meaning of a number stored for a key (for example the "
                 "webContent.blockedByFilter policy value or the appStore.maximumRating value) is not established. Group "
                 "is taken from the part of the key before the first dot and is a label for that part. The group 'User "
                 "safety' follows the key prefix userSafety; the file does not say whether it corresponds to a named "
                 "feature such as Communication Safety. Value is the stored value written as text: true and false for "
                 "booleans, lists as bracketed text, and a dictionary as key: value pairs with its keys sorted. A list "
                 "entry that is a one-entry dictionary is written as its value, a key and value pair as key=value, an "
                 "empty dictionary as (empty), and a binary value by its byte size only. Items is the number of list "
                 "entries in the value (for a dictionary, the entries of the lists directly under it). A list of shielded "
                 "apps is given by bundle identifier and a list of categories by category identifier, as stored; the file "
                 "does not name the categories. The token encoding key is given by its byte size and the token decoding "
                 "keys by their count; neither is copied. A value of false for a key that begins with deny means the store"
                 " holds the value false; a key that is absent is not reported, because an absent key is not evidence that"
                 " a setting was off. A store file carries no time of its own and the artifact reads no file system time, "
                 "so no row says when a setting was set or changed; the name of a sysdiagnose archive carries the date it "
                 "was taken. Not read: any .tokenized.plist copy beside a sysdiagnose store file, present on the iOS 27.0 "
                 "sysdiagnose read and absent on the iOS 26 ones, and the tokenized.plist beside every live "
                 "detokenized.plist, which the paths do not match; the managed_settings_diagnostic_tool_stdout.txt beside "
                 "the sysdiagnose property lists, which was empty on both iOS 26 sysdiagnoses in sample_data. An empty "
                 "result is not evidence that no restriction is or was set. Observed on the iOS 27.0 (24A437) sysdiagnose "
                 "read: 73 rows from 13 property lists (9 store files, 3 clientEffectiveSettings files and the "
                 "EffectiveSettings file), and on the second iOS 26.6 (23G71) one: 21 rows from 12 property lists (7 store"
                 " files, 4 clientEffectiveSettings files and the EffectiveSettings file). On hc_ios26 and falken_ios26: "
                 "10 rows each from 6 live property lists (3 store files, 2 clientEffectiveSettings files and the "
                 "EffectiveSettings file), the same clients, stores and keys as hc_ios26_sysdiag. On magnet_ios16 and "
                 "iphone14plus_ios18_mvs2025 (iOS 18.0 full file system) the only live setting file was an "
                 "EffectiveSettings.plist with no setting key and a File Version of 2, which gave one row each. Neither of"
                 " the two sysdiagnoses outside the corpus is shareable as it is; the test cases hold a copy of each with "
                 "the identifying values replaced (case_ios27_sanitized, case_ios26_sanitized) and a generated synthetic "
                 "copy of each shape, and the unit tests build a synthetic live layout of the same stores.",
        "paths": (
            '*/logs/ManagedSettings/*.plist',
            '*/sysdiagnose_*.tar.gz',
            '*/com.apple.ManagedSettings/DataVersion.plist',
            '*/com.apple.ManagedSettings/EffectiveSettings.plist',
            '*/com.apple.ManagedSettings/SettingRecords.plist',
            '*/com.apple.ManagedSettings/Records/SettingRecords.plist',
            '*/com.apple.ManagedSettings/Records/*/clientEffectiveSettings.plist',
            '*/com.apple.ManagedSettings/Records/*/*/detokenized.plist',
            '*/com.apple.ManagedSettings.system/DataVersion.plist',
            '*/com.apple.ManagedSettings.system/EffectiveSettings.plist',
            '*/com.apple.ManagedSettings.system/SettingRecords.plist',
            '*/com.apple.ManagedSettings.system/Records/SettingRecords.plist',
            '*/com.apple.ManagedSettings.system/Records/*/clientEffectiveSettings.plist',
            '*/com.apple.ManagedSettings.system/Records/*/*/detokenized.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile-cog",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 0 rows; no logs/ManagedSettings folder",
            "hickman_ios14_sysdiag": "iOS 14.3 | 0 rows; no logs/ManagedSettings folder",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows; no logs/ManagedSettings folder",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 16 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 10 rows",
            "hc_ios26": "iOS 26.5.2 full file system | 10 rows",
            "falken_ios26": "iOS 26.2.1 full file system | 10 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 full file system | 1 row",
            "magnet_ios16": "iOS 16.1.1 full file system | 1 row",
        }
    },
    "managedSettingsStores": {
        "name": "ManagedSettings - Store Directory",
        "description": "Clients and stores listed in the ManagedSettings SettingRecords files of a sysdiagnose (logs/ManagedSettings) or of a full file system extraction (com.apple.ManagedSettings), with the data version",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A row is one store entry of one client record in a SettingRecords.plist (User or System scope), or one "
                 "DataVersion.plist. A sysdiagnose holds them under logs/ManagedSettings/User and "
                 "logs/ManagedSettings/System; a full file system extraction holds the live ones as "
                 "Records/SettingRecords.plist and DataVersion.plist in "
                 "/private/var/mobile/Library/com.apple.ManagedSettings (User; at the top of that folder on magnet_ios16) "
                 "and in a com.apple.ManagedSettings.system folder of a shared system group container (System). Scope "
                 "follows the folder, and Source File tells the two layouts apart. Client is the client container "
                 "identifier of the record, Store Name the key of the store entry and Store Identifier the identifier "
                 "stored for it. Store Active and Sync To Watch are the stored values of the entry. Store File Found says "
                 "whether a store file for that identifier was found in this run in the same sysdiagnose or the same live "
                 "folder (<identifier>.plist in a sysdiagnose, Records/<record identifier>/<identifier>/detokenized.plist "
                 "in the live layout); it is 'no' when the input does not hold one. Team Identifier, Internal Client, "
                 "Record Identifier and Record Version are the stored values written as text (true and false for a "
                 "boolean), Container Path is the relative value of the record's containerPath entry, and Store Entry "
                 "Version is the version of the store entry (2 on all four iOS 26 corpus images, against 3 in the store "
                 "files); what they mean for the device is not established. A record with no store entry gives one row "
                 "with the store columns blank, and a SettingRecords.plist that holds an empty list gives no row: the "
                 "System one was an empty list on ai16_ios26_sysdiag, hc_ios26_sysdiag and hc_ios26. Data Version is the "
                 "version number stored in DataVersion.plist, as stored: on hc_ios26 the live files held 7 and "
                 "hc_ios26_sysdiag, taken later on the same device, held 8. A listed store is not proof that anything is "
                 "restricted: the settings themselves are in 'ManagedSettings - Settings'. The files carry no time and the"
                 " artifact reads no file system time, so no row says when a store was created or changed. An empty result"
                 " is not evidence that no store exists. Observed on the iOS 27.0 (24A437) sysdiagnose read: 11 rows (9 "
                 "store entries, 2 data versions), and on the second iOS 26.6 (23G71) one: 9 rows (7 store entries, 2 data"
                 " versions). On ai16_ios26_sysdiag (iOS 26.5.2): 7 rows (5 store entries, 2 data versions); on "
                 "hc_ios26_sysdiag (iOS 26.6) and hc_ios26 (iOS 26.5.2 full file system): 5 rows each (3 store entries, 2 "
                 "data versions); on falken_ios26 (iOS 26.2.1 full file system): 4 rows (3 store entries, 1 data version),"
                 " because that extraction holds no com.apple.ManagedSettings.system folder, so Scope held User on every "
                 "row there. Every listed store file was found on all four. Notes had no value on any row of the four. On "
                 "iphone14plus_ios18_mvs2025 (iOS 18.0 full file system): 2 rows, one data version and one UserSafety "
                 "store entry under com.apple.Preferences whose record folder in Records was empty, so Store File Found is"
                 " no. On magnet_ios16 (iOS 16.1.1 full file system) SettingRecords.plist sat at the top of "
                 "com.apple.ManagedSettings and held an empty list, and there was no DataVersion.plist, so it gave no row."
                 " The iOS 13.3.1, 14.3 and 17.3 sysdiagnoses in sample_data hold no logs/ManagedSettings folder. Not "
                 "read: the managed_settings_diagnostic_tool_stdout.txt beside the sysdiagnose property lists, which was "
                 "empty on both iOS 26 sysdiagnoses in sample_data.",
        "paths": (
            '*/logs/ManagedSettings/*.plist',
            '*/sysdiagnose_*.tar.gz',
            '*/com.apple.ManagedSettings/DataVersion.plist',
            '*/com.apple.ManagedSettings/EffectiveSettings.plist',
            '*/com.apple.ManagedSettings/SettingRecords.plist',
            '*/com.apple.ManagedSettings/Records/SettingRecords.plist',
            '*/com.apple.ManagedSettings/Records/*/clientEffectiveSettings.plist',
            '*/com.apple.ManagedSettings/Records/*/*/detokenized.plist',
            '*/com.apple.ManagedSettings.system/DataVersion.plist',
            '*/com.apple.ManagedSettings.system/EffectiveSettings.plist',
            '*/com.apple.ManagedSettings.system/SettingRecords.plist',
            '*/com.apple.ManagedSettings.system/Records/SettingRecords.plist',
            '*/com.apple.ManagedSettings.system/Records/*/clientEffectiveSettings.plist',
            '*/com.apple.ManagedSettings.system/Records/*/*/detokenized.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "building-warehouse",
        "sample_data": {
            "hickman_ios13_sysdiag": "iOS 13.3.1 | 0 rows; no logs/ManagedSettings folder",
            "hickman_ios14_sysdiag": "iOS 14.3 | 0 rows; no logs/ManagedSettings folder",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 0 rows; no logs/ManagedSettings folder",
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 7 rows",
            "hc_ios26_sysdiag": "iOS 26.6 | 5 rows",
            "hc_ios26": "iOS 26.5.2 full file system | 5 rows",
            "falken_ios26": "iOS 26.2.1 full file system | 4 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 full file system | 2 rows",
            "magnet_ios16": "iOS 16.1.1 full file system | 0 rows; SettingRecords.plist an empty list, no DataVersion.plist",
        }
    }
}

import plistlib
import re
from datetime import date, datetime
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

_PLIST_NAME = re.compile(r'\.plist$')
_PLIST_PATH = re.compile(
    r'(?:^|[/\\])logs[/\\]ManagedSettings[/\\](User|System)[/\\](?:(.+)[/\\])?([^/\\]+)\.plist$')
_UUID = r'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}'
# The live stores of a full file system extraction; tokenized.plist never matches.
_LIVE_PATH = re.compile(
    r'(?:^|[/\\])com\.apple\.ManagedSettings(\.system)?[/\\]'
    r'(?:(DataVersion|EffectiveSettings|SettingRecords)|Records[/\\](?:(SettingRecords)|(' + _UUID + r')[/\\]'
    r'(?:(clientEffectiveSettings)|(' + _UUID + r')[/\\](detokenized))))\.plist$')
LAYOUT_SYSDIAGNOSE = 'sysdiagnose'
LAYOUT_LIVE = 'live'
_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, ValueError, OverflowError, TypeError)

KIND_STORE = 'Store file'
KIND_CLIENT = 'Client effective settings'
KIND_EFFECTIVE = 'Effective settings'
KIND_RECORDS = 'Setting records'
KIND_VERSION = 'Data version'

# Setting label (written from the key name; the file does not describe the keys) by key.
SETTING_LABELS = {
    'appStore.denyAppStoreAppInstallation': 'Deny App Store app installation',
    'appStore.denyMarketplaceAppInstallation': 'Deny marketplace app installation',
    'appStore.denyWebDistributionAppInstallation': 'Deny web distribution app installation',
    'appStore.maximumRating': 'Maximum app rating (number as stored)',
    'webContent.blockedByFilter': 'Web content filter policy',
    'webContent.limitWebProxies': 'Limit web proxies',
    'webContent.overridePolicy': 'Web content override policy',
    'shield.applicationCategories': 'Shielded application categories',
    'shield.webDomainCategories': 'Shielded web domain categories',
    'screenTime.categoryShieldPolicies': 'Category shield policies',
    'siri.denySiri': 'Deny Siri',
    'siri.denySiri3489': 'Deny Siri (second key, denySiri3489)',
    'siri.forceSiriReduceSensitiveContent': 'Force Siri to reduce sensitive content',
    'intelligence.denyExternalIntelligenceIntegrations': 'Deny external intelligence integrations',
    'intelligence.denyGenmoji': 'Deny Genmoji',
    'intelligence.denyImagePlayground': 'Deny Image Playground',
    'intelligence.denyImageWand': 'Deny Image Wand',
    'intelligence.denyPhotorealisticImageGeneration': 'Deny photorealistic image generation',
    'userSafety.scanningPolicy': 'User safety scanning policy',
    'userSafety.allowedClients': 'User safety allowed clients',
    'deviceActivity.shareAcrossDevices': 'Share device activity across devices',
    'deviceActivity.allowedClients': 'Device activity allowed clients',
    'eyeRelief.forceScreenDistanceOn': 'Force screen distance on',
    'safari.denyHistoryClearing': 'Deny Safari history clearing',
    'safari.denyPrivateBrowsing': 'Deny Safari private browsing',
    'managedSettings.tokenEncodingKey': 'Token encoding key (not copied)',
    'managedSettings.tokenDecodingKeys': 'Token decoding keys (not copied)',
}

# Group by the part of the key before the first dot.
GROUP_LABELS = {
    'appStore': 'App Store',
    'webContent': 'Web content',
    'shield': 'Shield',
    'screenTime': 'Shield',
    'siri': 'Siri and intelligence',
    'intelligence': 'Siri and intelligence',
    'userSafety': 'User safety',
    'deviceActivity': 'Device activity',
    'eyeRelief': 'Screen distance',
    'safari': 'Safari',
    'managedSettings': 'Store keys',
}

_SECRET_KEYS = ('managedSettings.tokenEncodingKey', 'managedSettings.tokenDecodingKeys')
_STORE_PROPERTIES = ('StoreName', 'Properties', 'version')
_NO_SETTINGS = '(no setting key in this file)'
_UNREADABLE = '(file could not be read as a property list)'


def _scalar(value):
    '''One value as text: booleans as true/false, bytes by size only, dates as ISO text.'''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (bytes, bytearray)):
        return f'<{len(value)} bytes, not copied>'
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _item(value):
    '''A list item as text; the single-field dictionaries the stores use are written as their value.'''
    if isinstance(value, dict):
        if set(value) == {'key', 'value'} and isinstance(value['key'], dict) and len(value['key']) == 1:
            return f"{_scalar(next(iter(value['key'].values())))}={_scalar(value['value'])}"
        if len(value) == 1:
            return _scalar(next(iter(value.values())))
        return _compact(value)
    return _scalar(value)


def _compact(value):
    '''Value as stored, written as text.'''
    if isinstance(value, dict):
        if not value:
            return '(empty)'
        return '; '.join(f'{key}: {_compact(item)}' for key, item in sorted(value.items(), key=lambda pair: str(pair[0])))
    if isinstance(value, list):
        return '[' + ', '.join(_item(item) for item in value) + ']'
    return _scalar(value)


def value_text(key, value):
    '''Value as text; key material is reported by size only.'''
    if key in _SECRET_KEYS:
        if isinstance(value, list):
            return f'[{len(value)} item(s), not copied]'
        return _scalar(value)
    return _compact(value)


def item_count(value):
    '''Number of list entries in a value (a dictionary counts the entries of its lists), else None.'''
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        counts = [len(item) for item in value.values() if isinstance(item, list)]
        return sum(counts) if counts else None
    return None


def classify(name, client):
    '''File kind of a plist in logs/ManagedSettings/<scope>, or None when it is not read.'''
    if name == 'tokenized' or name.endswith('.tokenized'):
        return None
    if name == 'DataVersion':
        return KIND_VERSION
    if name == 'SettingRecords':
        return KIND_RECORDS
    if name == 'EffectiveSettings' and not client:
        return KIND_EFFECTIVE
    if name == 'clientEffectiveSettings':
        return KIND_CLIENT
    if client:
        return KIND_STORE
    return None


def load_plist(data):
    '''Parsed property list, or None when it cannot be read.'''
    try:
        return plistlib.loads(data)
    except _PLIST_ERRORS as ex:
        logfunc(f'ManagedSettings: property list not readable: {ex}')
        return None


def _live_info(relative):
    '''Kind and identifiers of a live store file from its path, or None when it is not read.'''
    match = _LIVE_PATH.search(relative)
    if not match:
        return None
    system, top, records, record, client_file, store, _ = match.groups()
    scope = 'System' if system else 'User'
    root = relative[:match.start()] + '/com.apple.ManagedSettings' + (system or '')
    if top:
        kind = {'DataVersion': KIND_VERSION, 'EffectiveSettings': KIND_EFFECTIVE}.get(top, KIND_RECORDS)
        name = top
    elif records:
        kind, name = KIND_RECORDS, records
    elif client_file:
        kind, name = KIND_CLIENT, client_file
    else:
        kind, name = KIND_STORE, 'detokenized'
    return {'scope': scope, 'name': name, 'kind': kind, 'root': root,
            'record': (record or '').upper(), 'store_id': (store or '').upper()}


def read_files(context):
    '''Yield dicts for every readable ManagedSettings plist: scope, client, name, kind, source, obj,
    layout, root (the folder the file's SettingRecords.plist sits in), record and store_id.'''
    for stream, source in get_sysdiagnose_files(context.get_files_found(), _PLIST_NAME, text_mode=False):
        inner = source.split(' >> ')[-1]
        match = _PLIST_PATH.search(inner)
        if match:
            scope, client, name = match.group(1), match.group(2) or '', match.group(3)
            kind = classify(name, client)
            if kind is None:
                continue
            outer = source.split(' >> ')[0] if ' >> ' in source else ''
            yield {'scope': scope, 'client': client, 'name': name, 'kind': kind, 'source': source,
                   'layout': LAYOUT_SYSDIAGNOSE, 'root': (outer, inner[:match.start(1)]), 'record': '',
                   'store_id': name.upper() if kind == KIND_STORE else '', 'obj': load_plist(stream.read())}
            continue
        if ' >> ' in source:
            continue
        info = _live_info(context.get_relative_path(source))
        if info is None:
            continue
        info.update({'client': '', 'source': source, 'layout': LAYOUT_LIVE, 'obj': load_plist(stream.read())})
        yield info


def resolve_live(files):
    '''Name the client and store of each live record and store file from the SettingRecords.plist
    in the same folder; a folder whose record is not listed there keeps its identifier.'''
    clients, entries = {}, {}
    for info in files:
        if info['layout'] != LAYOUT_LIVE or info['kind'] != KIND_RECORDS or not isinstance(info['obj'], list):
            continue
        for record in info['obj']:
            if not isinstance(record, dict) or not isinstance(record.get('recordIdentifier'), str):
                continue
            record_id = record['recordIdentifier'].upper()
            client = record.get('client') if isinstance(record.get('client'), dict) else {}
            clients[(info['root'], record_id)] = _scalar(client.get('containerIdentifier', ''))
            directory = record.get('storeDirectory')
            for store_name, entry in (directory.items() if isinstance(directory, dict) else ()):
                if isinstance(entry, dict) and isinstance(entry.get('identifier'), str):
                    entries[(info['root'], record_id, entry['identifier'].upper())] = (str(store_name), entry)
    for info in files:
        if info['layout'] != LAYOUT_LIVE or info['kind'] not in (KIND_CLIENT, KIND_STORE):
            continue
        key = (info['root'], info['record'])
        info['client'] = clients.get(key, info['record'])
        info['resolved'] = key in clients
        if info['kind'] == KIND_STORE:
            info['entry'] = entries.get(key + (info['store_id'],))
    return files


def _sorted(files):
    files = resolve_live(list(files))
    return sorted(files, key=lambda item: (item['layout'] != LAYOUT_SYSDIAGNOSE, item['scope'], item['client'],
                                           item['kind'], item['name'], item['source']))


def _live_note(info, from_entry=False):
    '''Where the Client and store columns of a live record or store file came from.'''
    if info.get('layout') != LAYOUT_LIVE or info['kind'] not in (KIND_CLIENT, KIND_STORE):
        return ''
    if not info.get('resolved'):
        return ('The record identifier of this folder is not listed in the SettingRecords.plist beside it; '
                'Client is the folder name.')
    if info['kind'] == KIND_STORE and info.get('entry') is None:
        return ('The store identifier of this folder is not listed for its record in SettingRecords.plist; '
                'the store columns are blank.')
    if info['kind'] == KIND_STORE and from_entry:
        return ('Client, Store Name, Store Active and Sync To Watch are from the SettingRecords.plist entry '
                'for this record and store.')
    return 'Client is from the SettingRecords.plist entry for this record.'


def setting_rows(info):
    '''Rows (without the source) for one store, client effective or effective settings file.'''
    obj = info['obj']
    store_name = active = sync = version = ''
    notes = ''
    items = []
    if isinstance(obj, dict):
        store_name = _scalar(obj['StoreName']) if 'StoreName' in obj else ''
        properties = obj.get('Properties')
        if isinstance(properties, dict):
            active = _scalar(properties['active']) if 'active' in properties else ''
            sync = _scalar(properties['syncToWatch']) if 'syncToWatch' in properties else ''
            extra = sorted(str(key) for key in properties if key not in ('active', 'syncToWatch'))
            if extra:
                notes = 'Other Properties keys as stored: ' + ', '.join(extra)
        version = _scalar(obj['version']) if 'version' in obj else ''
        items = sorted((key for key in obj if key not in _STORE_PROPERTIES), key=str)
    from_entry = info.get('entry') is not None and not store_name
    if from_entry:
        store_name, entry = info['entry']
        active = _scalar(entry['active']) if 'active' in entry else ''
        sync = _scalar(entry['syncToWatch']) if 'syncToWatch' in entry else ''
    live_note = _live_note(info, from_entry)
    if live_note:
        notes = f'{notes} {live_note}'.strip()
    head = (info['scope'], info['client'], info['kind'], info['name'], store_name)
    tail = (active, sync, version)
    if obj is None or not isinstance(obj, dict):
        return [head + ('', _UNREADABLE, '', '', '') + tail + (f'The file could not be read. {live_note}'.strip(),)]
    if not items:
        return [head + ('', _NO_SETTINGS, '', '', '') + tail + (notes,)]
    rows = []
    for key in items:
        value = obj[key]
        label = SETTING_LABELS.get(key, '')
        group = GROUP_LABELS.get(str(key).split('.', 1)[0], 'Other')
        rows.append(head + (group, label or 'Setting not described by this parser', str(key),
                            value_text(key, value), item_count(value)) + tail + (notes,))
    return rows


def store_rows(files):
    '''Rows (without the source) for the SettingRecords and DataVersion files, with source per row.'''
    stems = {(item['root'], item['scope'], item['store_id']) for item in files if item['kind'] == KIND_STORE}
    out = []
    for info in files:
        obj = info['obj']
        if info['kind'] == KIND_VERSION:
            version = obj.get('version') if isinstance(obj, dict) else None
            note = '' if version is not None else 'The file could not be read or has no version value.'
            out.append(((info['scope'], KIND_VERSION, '', '', '', '', '', '', '', '', '', '', '', '', version, note),
                        info['source']))
        elif info['kind'] == KIND_RECORDS:
            if not isinstance(obj, list):
                out.append(((info['scope'], KIND_RECORDS, '', '', '', '', '', '', '', '', '', '', '', '', '',
                             'The file could not be read as a list of records.'), info['source']))
                continue
            for record in obj:
                out.extend(_record_rows(info, record, stems))
    return out


def _record_rows(info, record, stems):
    scope = info['scope']
    if not isinstance(record, dict):
        return [((scope, KIND_RECORDS, '', '', '', '', '', '', '', '', '', '', '', '', '',
                  'A record that is not a dictionary was skipped.'), info['source'])]
    client = record.get('client') if isinstance(record.get('client'), dict) else {}
    path = record.get('containerPath')
    path_text = _scalar(path.get('relative')) if isinstance(path, dict) and 'relative' in path else ''
    common = (_scalar(client.get('containerIdentifier', '')), _scalar(client.get('teamIdentifier', '')),
              _scalar(client['isInternal']) if 'isInternal' in client else '',
              _scalar(record.get('recordIdentifier', '')), path_text,
              _scalar(record['version']) if 'version' in record else '')
    directory = record.get('storeDirectory')
    rows = []
    if isinstance(directory, dict) and directory:
        for store_name in sorted(directory, key=str):
            entry = directory[store_name]
            entry = entry if isinstance(entry, dict) else {}
            identifier = _scalar(entry.get('identifier', ''))
            rows.append(((scope, 'Store entry', common[0], str(store_name), identifier,
                          _scalar(entry['version']) if 'version' in entry else '',
                          _scalar(entry['active']) if 'active' in entry else '',
                          _scalar(entry['syncToWatch']) if 'syncToWatch' in entry else '',
                          'yes' if (info['root'], scope, identifier.upper()) in stems else 'no')
                         + common[1:] + ('', ''),
                         info['source']))
    else:
        rows.append(((scope, 'Store entry', common[0], '', '', '', '', '', '') + common[1:]
                     + ('', 'The record has no store entry.'), info['source']))
    return rows


@artifact_processor
def managedSettings(context):
    ''' See artifact description '''
    data_headers = (
        'Scope', 'Client', 'File Kind', 'File Name', 'Store Name', 'Group', 'Setting', 'Key (as stored)',
        'Value (text)', 'Items', 'Store Active', 'Sync To Watch', 'File Version (as stored)', 'Notes', 'Source File')
    data_list, sources = [], []
    files = [f for f in _sorted(read_files(context)) if f['kind'] in (KIND_STORE, KIND_CLIENT, KIND_EFFECTIVE)]
    for info in files:
        sources.append(info['source'])
        relative = context.get_relative_path(info['source'])
        for row in setting_rows(info):
            data_list.append(row + (relative,))
    return data_headers, data_list, '\n'.join(sorted(set(sources)))


@artifact_processor
def managedSettingsStores(context):
    ''' See artifact description '''
    data_headers = (
        'Scope', 'Row Kind', 'Client', 'Store Name', 'Store Identifier', 'Store Entry Version', 'Store Active',
        'Sync To Watch', 'Store File Found', 'Team Identifier', 'Internal Client', 'Record Identifier',
        'Container Path (relative, as stored)', 'Record Version', 'Data Version', 'Notes', 'Source File')
    files = [f for f in _sorted(read_files(context)) if f['kind'] in (KIND_STORE, KIND_RECORDS, KIND_VERSION)]
    data_list, sources = [], set()
    for row, source in store_rows(files):
        sources.add(source)
        data_list.append(row + (context.get_relative_path(source),))
    return data_headers, data_list, '\n'.join(sorted(sources))
