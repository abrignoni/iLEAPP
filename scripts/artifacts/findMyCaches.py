__artifacts_v2__ = {
    "findMyDevicesCache": {
        "name": "Find My Devices Cache",
        "description": "Device records from the Find My Devices.data cache file, where that file is "
                       "plain JSON",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "One row per record in the Devices.data JSON list. The list held 3 records on abe_ios16, "
                 "1 on hc_ios17_2 and hexordia_ios1651, 3 on hickman_ios13 and hickman_ios14, 23 on "
                 "hickman_ios15 and 28 on iphone11_ios17, and it is not limited to the examined device: "
                 "thisDevice was True on exactly one record per image. A 13-digit timeStamp value is read "
                 "as Unix milliseconds and a 10-digit one as Unix seconds (convert_unix_ts_to_utc chooses "
                 "the unit by magnitude); what each time marks is not established. Location Timestamp, "
                 "Latitude, Longitude, Horizontal Accuracy, positionType, isOld and isInaccurate come from "
                 "the record's location dictionary, which was present on 6 of the 28 iphone11_ios17 "
                 "records and 1 of the 3 abe_ios16 records; the others leave those columns blank. The "
                 "Crowdsourced columns come from the crowdSourcedLocation dictionary and were blank on "
                 "every hickman_ios13 row. Address joins formattedAddressLines, or uses "
                 "mapItemFullAddress. lostModeEnabled held False on every row of every image run. Columns "
                 "marked (as stored) are the file's own values under the key named in the header; no "
                 "public source defining them was found, so what each means is not established. On "
                 "dexter_ios18 (iOS 18.3.2), felix_ios17 (iOS 17.6.1) and otto_ios17 (iOS 17.5.1) the "
                 "Devices, Owner, SafeLocations and FriendCacheData files are binary plists whose top "
                 "level holds an encryptedData and a signature key. They are logged and not read, and the "
                 "0 rows recorded for those images are not evidence that nothing was recorded. Not "
                 "reported: features, audioChannels, lowPowerMode (False on every row run), the capability "
                 "and state flags, deviceModel, deviceColor, prsId, deviceDiscoveryId, trackingInfo (null "
                 "on every row run), itemGroup, the per-record safeLocations list, and on iphone11_ios17 "
                 "pendingRemove and pendingRemoveUntilTS. Items.data is read by the Find My Items "
                 "artifacts in findMyItems.py.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Devices.data',),
        "output_types": "all",
        "artifact_icon": "smartphone",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 3 rows",
            "hc_ios17_2": "iOS 17.2.1 | 1 row",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "hickman_ios15": "iOS 15.3.1 | 23 rows",
            "iphone11_ios17": "iOS 17.3 | 28 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "findMyOwnerCache": {
        "name": "Find My Owner Cache",
        "description": "The account record in the Find My Owner.data cache file, where that file is "
                       "plain JSON",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "One row per Owner.data file; 1 row on each image whose file is JSON. The hickman_ios13 "
                 "(iOS 13.3.1) file holds neither a phoneNumber nor an identifier key, so Phone Number and "
                 "Identifier are empty there. The hickman_ios14 (iOS 14.3) file holds no phoneNumber key, "
                 "so Phone Number is empty there too. Columns marked (as stored) are the file's own values "
                 "under the key named in the header; no public source defining them was found, so what "
                 "each means is not established. On dexter_ios18 (iOS 18.3.2), felix_ios17 (iOS 17.6.1) "
                 "and otto_ios17 (iOS 17.5.1) the Devices, Owner, SafeLocations and FriendCacheData files "
                 "are binary plists whose top level holds an encryptedData and a signature key. They are "
                 "logged and not read, and the 0 rows recorded for those images are not evidence that "
                 "nothing was recorded.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/Owner.data',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "hc_ios17_2": "iOS 17.2.1 | 1 row",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
    },
    "findMyFamilyMembersCache": {
        "name": "Find My Family Members Cache",
        "description": "Member records in the Find My FamilyMembers.data cache file, where that file "
                       "is plain JSON",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "One row per record in the FamilyMembers.data JSON list, with the same keys as "
                 "Owner.data. Of the images run, the file was found only on hickman_ios15 and "
                 "iphone11_ios17, with 5 records each; Phone Number held no value, isHSA held True and "
                 "hasMembers held False on all 5 rows of both. A missing file is not evidence that no "
                 "family group existed. Columns marked (as stored) are the file's own values under the key "
                 "named in the header; no public source defining them was found, so what each means is not "
                 "established.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/FamilyMembers.data',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hickman_ios15": "iOS 15.3.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
        },
    },
    "findMySafeLocationsCache": {
        "name": "Find My Safe Locations Cache",
        "description": "Safe location records in the Find My SafeLocations.data cache file, where "
                       "that file is plain JSON",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "One row per record in the safeLocations list of SafeLocations.data. Mapped To IDs lists "
                 "the ids that safeLocationsMapping pairs with the record's identifier, and Mapped To the "
                 "name of the Devices.data record whose baUUID, or the Items.data record whose identifier, "
                 "equals that id; Devices.data and Items.data are read for those names but are not listed "
                 "as this artifact's source. Of the ids in safeLocationsMapping, 3 of 4 on abe_ios16, 9 of "
                 "12 on hickman_ios15 and 13 of 14 on iphone11_ios17 matched one of the two; an id that "
                 "matches neither is listed without a name. Location Timestamp held one value on all rows "
                 "of each image run, so it does not tell one location's time from another's. approvalState "
                 "held 1 on every iphone11_ios17 row. A 13-digit timeStamp value is read as Unix "
                 "milliseconds and a 10-digit one as Unix seconds (convert_unix_ts_to_utc chooses the unit "
                 "by magnitude); what each time marks is not established. Columns marked (as stored) are "
                 "the file's own values under the key named in the header; no public source defining them "
                 "was found, so what each means is not established. Not reported: the separationStates, "
                 "canBeLeashedByHost and separationSupported keys. On dexter_ios18 (iOS 18.3.2), "
                 "felix_ios17 (iOS 17.6.1) and otto_ios17 (iOS 17.5.1) the Devices, Owner, SafeLocations "
                 "and FriendCacheData files are binary plists whose top level holds an encryptedData and a "
                 "signature key. They are logged and not read, and the 0 rows recorded for those images "
                 "are not evidence that nothing was recorded.",
        "paths": ('*/Caches/com.apple.findmy.fmipcore/SafeLocations.data',
                  '*/Caches/com.apple.findmy.fmipcore/Devices.data',
                  '*/Caches/com.apple.findmy.fmipcore/Items.data'),
        "output_types": "all",
        "artifact_icon": "shield-check",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 6 rows",
            "hc_ios17_2": "iOS 17.2.1 | 1 row",
            "hexordia_ios1651": "iOS 16.5.1 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
        },
    },
    "findMyFriendsCache": {
        "name": "Find My Friends Cache",
        "description": "Records from the following and followers lists of the Find My fmfcore "
                       "FriendCacheData.data cache file, where that file is plain JSON",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "One row per record in the following, followers, pendingFollowers, futureFollowing and "
                 "futureFollowers lists of FriendCacheData.data; List names the list. Only following and "
                 "followers held records on the images run (2 rows on abe_ios16, hickman_ios15 and "
                 "iphone11_ios17). A create or update timestamp of 0 is left blank. A 13-digit "
                 "createTimestamp or updateTimestamp value is read as Unix milliseconds and a 10-digit one "
                 "as Unix seconds (convert_unix_ts_to_utc chooses the unit by magnitude); what each time "
                 "marks is not established. Not reported: the expires and invitationSentToHandle keys, "
                 "empty on every record run; myInfo, whose emails included the Owner.data Apple ID on "
                 "every image run; devices (an id, a name and autoMeCapable per entry); the config, "
                 "features and preferences dictionaries; the labels list (1 entry on abe_ios16, empty on "
                 "the others run) and the contacts dictionary (1 entry on abe_ios16, empty on the others "
                 "run). The locationAlerts lists were empty on every image run. Columns marked (as stored) "
                 "are the file's own values under the key named in the header; no public source defining "
                 "them was found, so what each means is not established. On dexter_ios18 (iOS 18.3.2), "
                 "felix_ios17 (iOS 17.6.1) and otto_ios17 (iOS 17.5.1) the Devices, Owner, SafeLocations "
                 "and FriendCacheData files are binary plists whose top level holds an encryptedData and a "
                 "signature key. They are logged and not read, and the 0 rows recorded for those images "
                 "are not evidence that nothing was recorded.",
        "paths": ('*/Caches/com.apple.findmy.fmfcore/FriendCacheData.data',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
        },
    },
    "findMyFriendsLabelledLocations": {
        "name": "Find My Friends Labelled Locations",
        "description": "The labelledLocations records in the Find My fmfcore FriendCacheData.data "
                       "cache file, where that file is plain JSON",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "One row per record in the labelledLocations list of FriendCacheData.data; 1 row on "
                 "abe_ios16 and none on the other images run. User ID held no value on that row. A "
                 "13-digit updateTs value is read as Unix milliseconds and a 10-digit one as Unix seconds "
                 "(convert_unix_ts_to_utc chooses the unit by magnitude); what each time marks is not "
                 "established. Columns marked (as stored) are the file's own values under the key named in "
                 "the header; no public source defining them was found, so what each means is not "
                 "established. On dexter_ios18 (iOS 18.3.2), felix_ios17 (iOS 17.6.1) and otto_ios17 (iOS "
                 "17.5.1) the Devices, Owner, SafeLocations and FriendCacheData files are binary plists "
                 "whose top level holds an encryptedData and a signature key. They are logged and not "
                 "read, and the 0 rows recorded for those images are not evidence that nothing was "
                 "recorded.",
        "paths": ('*/Caches/com.apple.findmy.fmfcore/FriendCacheData.data',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
        },
    },
    "findMySiriSyncDevices": {
        "name": "Find My Siri Sync Devices",
        "description": "The syncDevices list in com.apple.siri.findmy.syncdevicedata.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "One row per entry in value.syncDevices of com.apple.siri.findmy.syncdevicedata.json. "
                 "Eviction Time is the file's single evictionTime value, so it repeats on every row of a "
                 "file; it is a file-level value, not a per-device time, and is placed last for that "
                 "reason. evictionTime was a 10-digit value on every file run and is read as Unix seconds; "
                 "convert_unix_ts_to_utc chooses the unit by magnitude, so a 13-digit value would be read "
                 "as milliseconds. What the time marks is not established. On abe_ios16, hickman_ios15 and "
                 "iphone11_ios17 most names here also appear in Devices.data (3 of 4, 20 of 22 and 21 of "
                 "23 distinct names). It was the only one of these caches read on cookbook_ios1751, "
                 "dexter_ios18, felix_ios17, hc_ios18_7, hc_ios26, iphone12_ios18 and otto_ios17. "
                 "value.pushToken is not reported. Which process writes the file is not established.",
        "paths": ('*/Caches/com.apple.siri.findmy.syncdevicedata.json',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 4 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 8 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "hc_ios26": "iOS 26.5.2 | 2 rows",
            "hickman_ios15": "iOS 15.3.1 | 25 rows",
            "iphone11_ios17": "iOS 17.3 | 29 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
        },
    },
}

import json

from scripts.ilapfuncs import artifact_processor, logfunc, convert_unix_ts_to_utc


FRIEND_LISTS = ('following', 'followers', 'pendingFollowers', 'futureFollowing', 'futureFollowers')


def _load_json(file_found):
    """Return the parsed JSON of a cache file, or None where the file is not JSON.

    On three corpus images (iOS 17.5.1, 17.6.1 and 18.3.2) these cache files are binary plists holding
    an encryptedData and a signature key, which this module does not read; each is logged and skipped.
    """
    with open(file_found, 'rb') as f:
        raw = f.read()
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        kind = 'a binary plist' if raw[:8] == b'bplist00' else 'not JSON'
        logfunc(f'{file_found} is {kind}; not read')
        return None


def _files(context, name):
    return [str(f) for f in context.get_files_found() if str(f).endswith('/' + name) or str(f) == name]


def _ts(value):
    """Unix time to UTC; a 13-digit value is read as milliseconds. 0 and None stay blank."""
    if not value:
        return ''
    return convert_unix_ts_to_utc(value)


def _join(value):
    if isinstance(value, list):
        return ', '.join(str(v) for v in value)
    return '' if value is None else value


def _address(address):
    if not isinstance(address, dict):
        return ''
    lines = address.get('formattedAddressLines')
    if isinstance(lines, list) and lines:
        return ', '.join(str(x) for x in lines)
    return address.get('mapItemFullAddress') or ''


def _location_cols(loc):
    loc = loc if isinstance(loc, dict) else {}
    return (_ts(loc.get('timeStamp')), loc.get('latitude', ''), loc.get('longitude', ''),
            loc.get('horizontalAccuracy', ''), loc.get('positionType', ''), loc.get('isOld', ''),
            loc.get('isInaccurate', ''))


def _account_row(account):
    return (account.get('appleId', ''), account.get('firstName', ''), account.get('lastName', ''),
            _join(account.get('phoneNumber')), account.get('identifier', ''), account.get('isHSA', ''),
            account.get('hasMembers', ''))


@artifact_processor
def findMyDevicesCache(context):
    data_headers = (('Location Timestamp', 'datetime'), 'Name', 'Device Display Name',
                    'Model Display Name', 'Raw Device Model', 'Device Class', 'thisDevice (as stored)',
                    'Latitude', 'Longitude', 'Horizontal Accuracy', 'positionType (as stored)',
                    'isOld (as stored)', 'isInaccurate (as stored)', 'Address',
                    ('Crowdsourced Location Timestamp', 'datetime'), 'Crowdsourced Latitude',
                    'Crowdsourced Longitude', 'Battery Level', 'batteryStatus (as stored)',
                    'deviceStatus (as stored)',
                    'lostModeEnabled (as stored)', 'fmlyShare (as stored)', 'Device ID')
    data_list = []
    sources = []
    for file_found in _files(context, 'Devices.data'):
        devices = _load_json(file_found)
        if not isinstance(devices, list):
            continue
        sources.append(file_found)
        for dev in devices:
            if not isinstance(dev, dict):
                continue
            ts, lat, lon, acc, ptype, is_old, inacc = _location_cols(dev.get('location'))
            crowd = dev.get('crowdSourcedLocation') if isinstance(dev.get('crowdSourcedLocation'), dict) else {}
            data_list.append((
                ts, dev.get('name', ''), dev.get('deviceDisplayName', ''), dev.get('modelDisplayName', ''),
                dev.get('rawDeviceModel', ''), dev.get('deviceClass', ''), dev.get('thisDevice', ''),
                lat, lon, acc, ptype, is_old, inacc, _address(dev.get('address')),
                _ts(crowd.get('timeStamp')), crowd.get('latitude', ''), crowd.get('longitude', ''),
                dev.get('batteryLevel', ''), dev.get('batteryStatus', ''),
                dev.get('deviceStatus', ''), dev.get('lostModeEnabled', ''), dev.get('fmlyShare', ''),
                dev.get('id', '')))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyOwnerCache(context):
    data_headers = ('Apple ID', 'First Name', 'Last Name', 'Phone Number', 'Identifier',
                    'isHSA (as stored)', 'hasMembers (as stored)')
    data_list = []
    sources = []
    for file_found in _files(context, 'Owner.data'):
        owner = _load_json(file_found)
        if not isinstance(owner, dict):
            continue
        sources.append(file_found)
        data_list.append(_account_row(owner))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyFamilyMembersCache(context):
    data_headers = ('Apple ID', 'First Name', 'Last Name', 'Phone Number', 'Identifier',
                    'isHSA (as stored)', 'hasMembers (as stored)')
    data_list = []
    sources = []
    for file_found in _files(context, 'FamilyMembers.data'):
        members = _load_json(file_found)
        if not isinstance(members, list):
            continue
        sources.append(file_found)
        for member in members:
            if isinstance(member, dict):
                data_list.append(_account_row(member))
    return data_headers, data_list, '\n'.join(sources)


def _names_by_id(context):
    """Name of each device (Devices.data baUUID) and item (Items.data identifier) in the files found."""
    names = {}
    for file_found in _files(context, 'Devices.data'):
        for dev in _load_json(file_found) or []:
            if isinstance(dev, dict) and dev.get('baUUID'):
                names[dev['baUUID']] = dev.get('name', '')
    for file_found in _files(context, 'Items.data'):
        for item in _load_json(file_found) or []:
            if isinstance(item, dict) and item.get('identifier'):
                names[item['identifier']] = item.get('name', '')
    return names


@artifact_processor
def findMySafeLocationsCache(context):
    data_headers = (('Location Timestamp', 'datetime'), 'Name', 'Address', 'Latitude', 'Longitude',
                    'type (as stored)', 'approvalState (as stored)', 'Mapped To', 'Mapped To IDs',
                    'Identifier')
    data_list = []
    sources = []
    names = None
    for file_found in _files(context, 'SafeLocations.data'):
        safe = _load_json(file_found)
        if not isinstance(safe, dict):
            continue
        sources.append(file_found)
        if names is None:
            names = _names_by_id(context)
        mapped = {}
        mapping = safe.get('safeLocationsMapping')
        if isinstance(mapping, list):
            for owner_id, safe_ids in zip(mapping[0::2], mapping[1::2]):
                for safe_id in safe_ids if isinstance(safe_ids, list) else []:
                    mapped.setdefault(safe_id, []).append(owner_id)
        for loc in safe.get('safeLocations') or []:
            if not isinstance(loc, dict):
                continue
            ts, lat, lon, _acc, _ptype, _old, _inacc = _location_cols(loc.get('location'))
            owners = mapped.get(loc.get('identifier'), [])
            data_list.append((ts, loc.get('name') or '', _address(loc.get('address')), lat, lon,
                              loc.get('type', ''), loc.get('approvalState', ''),
                              ', '.join(names.get(o) or '' for o in owners if names.get(o)),
                              ', '.join(str(o) for o in owners), loc.get('identifier', '')))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyFriendsCache(context):
    data_headers = (('Create Timestamp', 'datetime'), ('Update Timestamp', 'datetime'), 'List',
                    'Invitation From Handles', 'Invitation Accepted Handles', 'optedNotToShare (as stored)', 'ID')
    data_list = []
    sources = []
    for file_found in _files(context, 'FriendCacheData.data'):
        cache = _load_json(file_found)
        if not isinstance(cache, dict):
            continue
        sources.append(file_found)
        for list_name in FRIEND_LISTS:
            for person in cache.get(list_name) or []:
                if not isinstance(person, dict):
                    continue
                from_handles = person.get('invitationFromHandles') or person.get('invitationFromHandle')
                data_list.append((_ts(person.get('createTimestamp')), _ts(person.get('updateTimestamp')),
                                  list_name, _join(from_handles), _join(person.get('invitationAcceptedHandles')),
                                  _join(person.get('optedNotToShare')), person.get('id', '')))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyFriendsLabelledLocations(context):
    data_headers = (('Update Timestamp', 'datetime'), 'Label', 'labelType (as stored)', 'Latitude',
                    'Longitude', 'User ID', 'ID')
    data_list = []
    sources = []
    for file_found in _files(context, 'FriendCacheData.data'):
        cache = _load_json(file_found)
        if not isinstance(cache, dict):
            continue
        sources.append(file_found)
        for loc in cache.get('labelledLocations') or []:
            if isinstance(loc, dict):
                data_list.append((_ts(loc.get('updateTs')), loc.get('label', ''), loc.get('labelType', ''),
                                  loc.get('latitude', ''), loc.get('longitude', ''), _join(loc.get('userId')),
                                  loc.get('id', '')))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMySiriSyncDevices(context):
    data_headers = ('Device Name', 'Owner First Name', 'Owner Last Name', ('Eviction Time', 'datetime'))
    data_list = []
    sources = []
    for file_found in _files(context, 'com.apple.siri.findmy.syncdevicedata.json'):
        doc = _load_json(file_found)
        if not isinstance(doc, dict):
            continue
        sources.append(file_found)
        value = doc.get('value') if isinstance(doc.get('value'), dict) else {}
        eviction = _ts(doc.get('evictionTime'))
        for dev in value.get('syncDevices') or []:
            if isinstance(dev, dict):
                data_list.append((dev.get('name', ''), dev.get('ownerFirstName', ''),
                                  dev.get('ownerLastName', ''), eviction))
    return data_headers, data_list, '\n'.join(sources)
