__artifacts_v2__ = {
    "managedSettings": {
        "name": "ManagedSettings - Settings",
        "description": "Setting keys and values held by the ManagedSettings stores in a sysdiagnose (logs/ManagedSettings): install, web content, shield, Siri and intelligence, user safety and similar keys, as stored",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-20",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A sysdiagnose carries a copy of the ManagedSettings stores under logs/ManagedSettings/User and "
                 "logs/ManagedSettings/System. The folder and key names point to the Screen Time and Family "
                 "Controls settings stores; what the file does on the device, and what writes it, is not "
                 "established by the file. A row is one top-level key of one property list: a store file "
                 "(<store identifier>.plist, kept in a folder named for the client that owns it), a "
                 "clientEffectiveSettings.plist or the EffectiveSettings.plist of the scope. A file with no "
                 "setting key gives one row that says so. Store Name is the StoreName value of a store "
                 "file; Store Active and Sync To Watch are the two values of its Properties entry; Format "
                 "Version is its version value, all as stored. The store names are not the same in every "
                 "version: the iOS 27.0 (24A437) sysdiagnose tested holds the stores ContentAndPrivacy, "
                 "Restrictions, UserSafety, defaultGroup, downtime, scheduleDowntime, bedtime and Default under "
                 "com.apple.ScreenTimeSettings, com.apple.ScreenTimeSettings.TimeAllowances, "
                 "com.apple.UserSafety, com.apple.Preferences and FamilyControlsAgent, and the iOS 26.6 "
                 "(23G71) one holds Default, SafariStore, UserSafetyStore, UserSafety and DeviceActivityStore "
                 "under com.apple.ScreenTime, com.apple.UserSafety, com.apple.Preferences, com.apple.momentsd "
                 "and FamilyControlsAgent. Other versions are not checked, and a key not listed here is "
                 "reported with its key and value as stored. Setting is a label written from the key "
                 "name; the file does not describe the keys and the meaning of a number stored for a key "
                 "(for example the webContent.blockedByFilter policy value or the appStore.maximumRating "
                 "value) is not established. Group is taken from the part of the key before the first dot. "
                 "The group 'User safety' follows the key prefix userSafety; the file does not say whether "
                 "it corresponds to a named feature such as Communication Safety. Value is the stored value "
                 "written as text: true and false for booleans, lists as bracketed text, and a dictionary "
                 "as key: value pairs. Items is the number of list entries in the value (for a dictionary, the "
                 "entries of its lists). A list of shielded apps is given by bundle identifier and a list of "
                 "categories by category identifier, as stored; the file does not name the categories. The "
                 "token encoding and decoding keys are not copied, only their size. A value of false for a "
                 "key that begins with deny means the store holds the value false; a key that is absent is "
                 "not reported, because an absent key is not evidence that a setting was off. A store file "
                 "in the archive is a snapshot of the stores when the sysdiagnose was taken and carries no "
                 "time, so no row says when a setting was set or changed. The .tokenized.plist copies kept "
                 "beside the store files are not read. An empty result is not evidence that no restriction "
                 "is or was set. Observed on one iOS 27.0 (24A437) sysdiagnose: 73 rows from 13 property "
                 "lists (9 store files, 3 clientEffectiveSettings files and the EffectiveSettings file), and "
                 "on one iOS 26.6 (23G71) sysdiagnose: 21 rows from 12 property lists (7 store files, 4 "
                 "clientEffectiveSettings files and the EffectiveSettings file). Neither sysdiagnose is "
                 "shareable as it is; the test cases hold a copy of each with the identifying values replaced "
                 "(case_ios27_sanitized, case_ios26_sanitized) and a generated synthetic copy of each shape.",
        "paths": (
            '*/logs/ManagedSettings/*.plist',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile-cog",
        "sample_data": {
            "case_ios27_sanitized": "iOS 27.0 (24A437) | 73 rows; real structure, identifiers replaced",
            "case_ios26_sanitized": "iOS 26.6 (23G71) | 21 rows; real structure, identifiers replaced",
        }
    },
    "managedSettingsStores": {
        "name": "ManagedSettings - Store Directory",
        "description": "Clients and stores listed in the ManagedSettings SettingRecords files of a sysdiagnose (logs/ManagedSettings), with the data version",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-20",
        "last_update_date": "2026-10-20",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "A row is one store entry of one client record in a SettingRecords.plist (User or System "
                 "scope), or one DataVersion.plist. Client is the client container identifier of the record, "
                 "Store Name the key of the store entry and Store Identifier the identifier stored for it. "
                 "Store Active and Sync To Watch are the stored values of the entry. Store File In Archive "
                 "says whether a store file named with that identifier was read in the same run; it is "
                 "'no' when the sysdiagnose does not hold it. Team Identifier, Internal Client, Record "
                 "Identifier, Container Path and Record Version are copied as stored; what they mean for "
                 "the device is not established. A record with no store entry gives one row with the "
                 "store columns blank. Data Version is the version number stored in DataVersion.plist. A "
                 "listed store is not proof that anything is restricted: the settings themselves are in "
                 "'ManagedSettings - Settings'. The files carry no time, so no row says when a store was "
                 "created or changed. An empty result is not evidence that no store exists. Observed on one "
                 "iOS 27.0 (24A437) sysdiagnose: 11 rows (9 store entries, 2 data versions), and on one iOS "
                 "26.6 (23G71) sysdiagnose: 9 rows (7 store entries, 2 data versions); other versions are "
                 "not checked.",
        "paths": (
            '*/logs/ManagedSettings/*.plist',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "building-warehouse",
        "sample_data": {
            "case_ios27_sanitized": "iOS 27.0 (24A437) | 11 rows; real structure, identifiers replaced",
            "case_ios26_sanitized": "iOS 26.6 (23G71) | 9 rows; real structure, identifiers replaced",
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
    'shield.applicationCategories': 'Shielded apps and app categories',
    'shield.webDomainCategories': 'Shielded web domains and web categories',
    'screenTime.categoryShieldPolicies': 'Category shield policies',
    'siri.denySiri': 'Deny Siri',
    'siri.denySiri3489': 'Deny Siri (second key, denySiri3489)',
    'siri.forceSiriReduceSensitiveContent': 'Force Siri to reduce sensitive content',
    'intelligence.denyExternalIntelligenceIntegrations': 'Deny external intelligence integrations',
    'intelligence.denyGenmoji': 'Deny Genmoji',
    'intelligence.denyImagePlayground': 'Deny Image Playground',
    'intelligence.denyImageWand': 'Deny Image Wand',
    'intelligence.denyPhotorealisticImageGeneration': 'Deny photorealistic image generation',
    'userSafety.scanningPolicy': 'User safety scanning policy (services and applications on or off)',
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
    'appStore': 'App installation',
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
    if name.endswith('.tokenized'):
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


def read_files(context):
    '''Yield dicts for every readable ManagedSettings plist: scope, client, name, kind, source, obj.'''
    for stream, source in get_sysdiagnose_files(context.get_files_found(), _PLIST_NAME, text_mode=False):
        inner = source.split(' >> ')[-1]
        match = _PLIST_PATH.search(inner)
        if not match:
            continue
        scope, client, name = match.group(1), match.group(2) or '', match.group(3)
        kind = classify(name, client)
        if kind is None:
            continue
        yield {'scope': scope, 'client': client, 'name': name, 'kind': kind, 'source': source,
               'obj': load_plist(stream.read())}


def _sorted(files):
    return sorted(files, key=lambda item: (item['scope'], item['client'], item['kind'], item['name'], item['source']))


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
    head = (info['scope'], info['client'], info['kind'], info['name'], store_name)
    tail = (active, sync, version)
    if obj is None or not isinstance(obj, dict):
        return [head + ('', _UNREADABLE, '', '', '') + tail + ('The file could not be read.',)]
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
    stems = {(item['scope'], item['name']) for item in files if item['kind'] == KIND_STORE}
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
                          'yes' if (scope, identifier) in stems else 'no') + common[1:] + ('', ''),
                         info['source']))
    else:
        rows.append(((scope, 'Store entry', common[0], '', '', '', '', '', '') + common[1:]
                     + ('', 'The record has no store entry.'), info['source']))
    return rows


@artifact_processor
def managedSettings(context):
    ''' See artifact description '''
    data_headers = (
        'Scope', 'Client Folder', 'File Kind', 'File Name', 'Store Name', 'Group', 'Setting', 'Key (as stored)',
        'Value (as stored)', 'Items', 'Store Active', 'Sync To Watch', 'Format Version', 'Notes', 'Source File')
    data_list, sources = [], []
    for info in _sorted(f for f in read_files(context) if f['kind'] in (KIND_STORE, KIND_CLIENT, KIND_EFFECTIVE)):
        sources.append(info['source'])
        relative = context.get_relative_path(info['source'])
        for row in setting_rows(info):
            data_list.append(row + (relative,))
    return data_headers, data_list, '\n'.join(sorted(set(sources)))


@artifact_processor
def managedSettingsStores(context):
    ''' See artifact description '''
    data_headers = (
        'Scope', 'Row Kind', 'Client', 'Store Name', 'Store Identifier', 'Store Version', 'Store Active',
        'Sync To Watch', 'Store File In Archive', 'Team Identifier', 'Internal Client', 'Record Identifier',
        'Container Path (as stored)', 'Record Version', 'Data Version', 'Notes', 'Source File')
    files = _sorted(f for f in read_files(context) if f['kind'] in (KIND_STORE, KIND_RECORDS, KIND_VERSION))
    data_list, sources = [], set()
    for row, source in store_rows(files):
        sources.add(source)
        data_list.append(row + (context.get_relative_path(source),))
    return data_headers, data_list, '\n'.join(sorted(sources))
