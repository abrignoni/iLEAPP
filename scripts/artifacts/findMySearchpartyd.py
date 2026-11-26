__artifacts_v2__ = {
    "findMyBeaconEstimatedLocations": {
        "name": "Find My Beacon Estimated Locations",
        "description": "Location records from the encrypted BeaconEstimatedLocation records of searchpartyd, "
                       "with the beacon's name",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per BeaconEstimatedLocation record in com.apple.icloud.searchpartyd. Each .record file is a "
                 "binary plist list of a 16 byte nonce, a 16 byte tag and the AES-256-GCM ciphertext. It is decrypted "
                 "with the BeaconStore / BeaconStoreKey keychain item from the keychain carried by the extraction or "
                 "supplied with --keychain, and read only when the GCM tag verifies. The item's access group was "
                 "com.apple.icloud.searchpartyd on dexter_ios18, hill_iphone15pro_ios26 and wilkerson_iphone16_ios26 "
                 "and searchpartyd-baa-fmna-group on abe_ios16, felix23_ios16, adams_iphone12mini, iphone11_ios17, "
                 "felix_ios17 and otto_ios17. The key was the item's data on dexter_ios18, felix_ios17, otto_ios17, "
                 "hill_iphone15pro_ios26 and wilkerson_iphone16_ios26, and its gena attribute on abe_ios16, "
                 "felix23_ios16, adams_iphone12mini and iphone11_ios17, where the item holds no data. The layout was "
                 "published in denysvitali/searchparty-keys "
                 "(https://github.com/denysvitali/searchparty-keys/blob/b1b4b13c09c46d61b3cf22e66a2fb54e20e3c8c6/decrypt.go#L12-L33)"
                 " and joshuahickman1/Lost_Apples "
                 "(https://github.com/joshuahickman1/Lost_Apples/blob/9ec8597a4164bd63fa757fe2463597a393934e03/src/owned_beacons_parser.py#L99-L117)."
                 " A record file that cannot be opened is logged and skipped, and the others are still read. Without a"
                 " usable key a record is logged and gives no row, which is not evidence that nothing was recorded: "
                 "records were present and not read on cookbook_ios1751, hexordia_ios1651, iphone12_ios18, "
                 "iphone14plus_ios18, iphone14plus_ios18_mvs2025 and jess_ios15, where iLEAPP finds no keychain in the"
                 " extraction, and on falken_ios26, fsfull002_ios17 and hc_ios17_2, whose keychain-backup.plist "
                 "entries hold only encrypted data and a persistent reference. They carry no service, account or "
                 "access group, so no BeaconStore item could be identified. Records are joined only within one "
                 "searchpartyd folder. Timestamp and Scan Date are the record's timestamp and scanDate dates, in UTC; "
                 "what each marks is not established. Over the 190 rows of the nine images read they were equal on "
                 "145, Timestamp was earlier on 30, and Scan Date held the text $null, shown as no value, on 15. "
                 "locationSource (as stored) held seven distinct integers (1, 2, 3, 4, 7, 8 and 15) and Horizontal "
                 "Accuracy is horizontalAccuracy as stored; the meaning of the first and the unit of the second are "
                 "not established. Beacon Record names the record type whose identifier equals the record's "
                 "associatedBeacon: OwnedBeacons on 171 rows and SharedBeacons on 19, all 19 on iphone11_ios17. Beacon"
                 " Name is the name in the BeaconNamingRecord whose associatedBeacon matches, and is empty on those 19"
                 " rows, which have none. Where several naming records match, their distinct names are joined with a "
                 "comma; no image read had more than one. The record identifier and cloudKitMetadata are not reported."
                 " SafeLocations records are not read; Find My Safe Locations Cache reads the SafeLocations.data cache"
                 " file. The other record types in the folder (among them WildModeAssociationRecord, KeySyncRecord, "
                 "KeyAlignmentRecords, OwnedDeviceKeyRecord and the SecureLocation records), its databases and "
                 "CachedUnifiedBeacons.data are not read.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconEstimatedLocation/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconNamingRecord/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/OwnedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/SharedBeacons/*.record',
        ),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 32 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 50 rows",
            "iphone11_ios17": "iOS 17.3 | 50 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 24 rows",
            "dexter_ios18": "iOS 18.3.2 | 18 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1 row",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 15 rows",
        },
    },
    "findMyOwnedBeacons": {
        "name": "Find My Owned Beacons",
        "description": "Beacon records from the encrypted OwnedBeacons records of searchpartyd, with the name "
                       "from the matching BeaconNamingRecord",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per OwnedBeacons record in com.apple.icloud.searchpartyd, decrypted as described in Find My "
                 "Beacon Estimated Locations, where the images whose records could not be read are listed. Model "
                 "(model as stored) held a string shaped like a device model identifier on 31 of the 37 rows read "
                 "(iPhone, iPad, Mac and Watch forms among them) and an empty string on 6. What the field identifies "
                 "is not established. Pairing Date is pairingDate in UTC; what it marks is not established. Name is "
                 "the name in the BeaconNamingRecord whose associatedBeacon equals the identifier, empty on the 6 of "
                 "37 rows with none. BeaconNamingRecord files for 6 beacons that match neither an OwnedBeacons nor a "
                 "SharedBeacons identifier (2 on abe_ios16, 4 on iphone11_ios17) are not reported. Latest Estimated "
                 "Location Timestamp is the latest Timestamp among the beacon's BeaconEstimatedLocation records and "
                 "Estimated Location Records is their count; 20 of 37 rows had none. Leash Records counts the "
                 "LeashRecords whose associatedBeacons list the identifier (1 on 23 rows, 0 on 14); what a leash "
                 "record represents is not established. batteryLevel (as stored) held 0 on 33 rows and 1 on 4, "
                 "productId (as stored) -1 on 31 and vendorId (as stored) -1 on 31; their meanings are not "
                 "established. Not reported: isZeus (False on all 37 records), cloudKitMetadata, groupIdentifier "
                 "(present on 2 records), the naming record's emoji (on 6 of 37) and roleId, and the key material "
                 "(privateKey, publicKey and sharedSecret on all 37, secureLocationsSharedSecret on 29, "
                 "secondarySharedSecret on 6).",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/OwnedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconNamingRecord/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/LeashRecords/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconEstimatedLocation/*.record',
        ),
        "output_types": "standard",
        "artifact_icon": "tag",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 9 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 7 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1 row",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 2 rows",
        },
    },
    "findMySharedBeacons": {
        "name": "Find My Shared Beacons",
        "description": "Beacon records from the encrypted SharedBeacons records of searchpartyd, with the "
                       "owner handle and share date",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "One row per SharedBeacons record in com.apple.icloud.searchpartyd, decrypted as described in Find My"
                 " Beacon Estimated Locations. Of the images whose records could be read, only iphone11_ios17 held "
                 "SharedBeacons records, so every count here is from that image. Share Date is shareDate in UTC; what "
                 "it marks is not established. Owner Handle is the destination string of the ownerHandle dictionary, "
                 "present on all 14 rows; the dictionary's type integer (0 on all 14) is not reported. Owner Beacon "
                 "Identifier is ownerBeaconIdentifier from the record's name dictionary, present on 7 rows; on the "
                 "other 7 name held an empty string, and no record held a text name. shareType (as stored) held 1 on 7"
                 " rows and 4 on 7; its meaning is not established. Model held an empty string on 4 rows. Latest "
                 "Estimated Location Timestamp and Estimated Location Records come from the BeaconEstimatedLocation "
                 "records whose associatedBeacon equals the identifier: 19 records for 3 of the 14 beacons. Not "
                 "reported: accepted (True on all 14), role (-1 on all 14), groupIdentifier ($null on all 14), "
                 "correlationIdentifier, shareIdentifier, advertisedIndex, cloudKitMetadata and the name dictionary's "
                 "version.",
        "paths": (
            '*/mobile/Library/com.apple.icloud.searchpartyd/SharedBeacons/*.record',
            '*/mobile/Library/com.apple.icloud.searchpartyd/BeaconEstimatedLocation/*.record',
        ),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 14 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 0 rows",
        },
    },
}

import plistlib
from datetime import timezone
from pathlib import PurePath
from xml.parsers.expat import ExpatError

from Crypto.Cipher import AES

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.ios_keychain import active_keychain_path, load_keychain_entries

STORE_DIR = 'com.apple.icloud.searchpartyd'
# The item's access group was com.apple.icloud.searchpartyd on the three iOS 18 and 26 images read
# and searchpartyd-baa-fmna-group on the six iOS 16 and 17 images read; the lookup matches a
# substring of both.
ACCESS_GROUP = 'searchpartyd'
KEY_SERVICE = 'BeaconStore'
KEY_ACCOUNT = 'BeaconStoreKey'
KEY_LENGTH = 32
NONCE_LENGTH = 16
TAG_LENGTH = 16
# Some keys hold this text in place of a value. It is read as no value.
NULL_TEXT = '$null'

_PLIST_ERRORS = (plistlib.InvalidFileException, ValueError, TypeError, IndexError, KeyError,
                 OverflowError, RecursionError, ExpatError)

_key_cache = {}


def _loads_plist(raw):
    try:
        return plistlib.loads(raw)
    except _PLIST_ERRORS:
        return None


def _field_text(entry, field):
    value = entry.get(field)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'ignore').rstrip('\x00')
    return str(value) if value is not None else ''


def _beacon_store_keys():
    """Every 32 byte BeaconStore key candidate the keychain in use holds, or None without one.

    The key was the item's data (v_Data) on some images run. On others the item held no data
    and the key was its 32 byte gena attribute, so both are candidates; the GCM tag decides
    which, if either, is the key.
    """
    keychain = active_keychain_path()
    if not keychain:
        return None
    if keychain not in _key_cache:
        keys = []
        for entry in load_keychain_entries(keychain):
            if (ACCESS_GROUP not in _field_text(entry, 'agrp').lower()
                    or _field_text(entry, 'svce') != KEY_SERVICE
                    or _field_text(entry, 'acct') != KEY_ACCOUNT):
                continue
            for field in ('v_Data', 'gena'):
                value = entry.get(field)
                if isinstance(value, (bytes, bytearray)) and len(value) == KEY_LENGTH \
                        and bytes(value) not in keys:
                    keys.append(bytes(value))
        _key_cache[keychain] = keys
    return _key_cache[keychain]


def read_searchpartyd_record(file_found):
    """Open one searchpartyd .record file, or return None (logged) where it cannot be read.

    The file is a binary plist holding a list of three byte strings: a 16 byte nonce, a 16 byte
    tag and the AES-256-GCM ciphertext. The key is the BeaconStore / BeaconStoreKey keychain item.
    The plaintext is a binary plist dictionary.
    """
    try:
        with open(file_found, 'rb') as record_file:
            outer = _loads_plist(record_file.read())
    except OSError as error:
        logfunc(f'{file_found}: could not read record: {error}')
        return None
    if (not isinstance(outer, list) or len(outer) != 3 or not all(isinstance(x, bytes) for x in outer)
            or len(outer[0]) != NONCE_LENGTH or len(outer[1]) != TAG_LENGTH):
        logfunc(f'{file_found} is not a nonce, tag and ciphertext list; not read')
        return None
    keys = _beacon_store_keys()
    if keys is None:
        logfunc(f'{file_found} is encrypted and no keychain is available; not read. '
                'Supply the extraction\'s keychain with --keychain.')
        return None
    if not keys:
        logfunc(f'{file_found} is encrypted and no readable BeaconStore key was found in the keychain in use; not read')
        return None
    nonce, tag, ciphertext = outer
    for key in keys:
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        try:
            plain = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            continue
        document = _loads_plist(plain)
        if not isinstance(document, dict):
            logfunc(f'{file_found}: decrypted content is not a plist dictionary; not read')
            return None
        return document
    logfunc(f'{file_found}: the authentication tag did not verify with the BeaconStore key; not read')
    return None


def _store_root(file_found):
    """The searchpartyd folder a record belongs to, so records join only within one store."""
    parts = PurePath(file_found).parts
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] == STORE_DIR:
            return PurePath(*parts[:index + 1])
    return None


def _record_type(file_found, root):
    return PurePath(file_found).relative_to(root).parts[0]


def _read_store(files_found):
    """Decrypted records grouped by store folder and record type, with the files that opened."""
    stores = {}
    for file_found in sorted(str(path) for path in files_found):
        if not file_found.endswith('.record'):
            continue
        root = _store_root(file_found)
        if root is None:
            continue
        record = read_searchpartyd_record(file_found)
        if record is None:
            continue
        stores.setdefault(root, {}).setdefault(_record_type(file_found, root), []).append(
            (file_found, record))
    return stores


def _value(value):
    return '' if value is None or value == NULL_TEXT else value


def _date(value):
    if hasattr(value, 'replace') and hasattr(value, 'year'):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    return ''


def _text(value):
    return value if isinstance(value, str) and value != NULL_TEXT else ''


def _names(records):
    names = {}
    for _file_found, record in records.get('BeaconNamingRecord', []):
        beacon = _text(record.get('associatedBeacon')).upper()
        name = _text(record.get('name'))
        if beacon and name:
            names.setdefault(beacon, []).append(name)
    return {beacon: ', '.join(dict.fromkeys(found)) for beacon, found in names.items()}


def _identifiers(records, record_type):
    return {_text(record.get('identifier')).upper() for _file_found, record in records.get(record_type, [])}


def _estimates(records):
    """The timestamps of the BeaconEstimatedLocation records, keyed by beacon identifier."""
    estimated = {}
    for _file_found, record in records.get('BeaconEstimatedLocation', []):
        estimated.setdefault(_text(record.get('associatedBeacon')).upper(), []).append(
            _date(record.get('timestamp')))
    return estimated


def _estimate_columns(estimated, identifier):
    times = [time for time in estimated.get(identifier.upper(), []) if time]
    return (max(times) if times else ''), len(estimated.get(identifier.upper(), []))


@artifact_processor
def findMyBeaconEstimatedLocations(context):
    data_headers = (('Timestamp', 'datetime'), ('Scan Date', 'datetime'), ('Latitude', 'latitude'),
                    ('Longitude', 'longitude'), 'Horizontal Accuracy', 'locationSource (as stored)',
                    'Beacon Name', 'Beacon Record', 'Beacon Identifier')
    data_list = []
    sources = []
    for _root, records in _read_store(context.get_files_found()).items():
        names = _names(records)
        owned = _identifiers(records, 'OwnedBeacons')
        shared = _identifiers(records, 'SharedBeacons')
        for file_found, record in records.get('BeaconEstimatedLocation', []):
            beacon = _text(record.get('associatedBeacon'))
            kind = 'OwnedBeacons' if beacon.upper() in owned else \
                'SharedBeacons' if beacon.upper() in shared else ''
            sources.append(file_found)
            data_list.append((_date(record.get('timestamp')), _date(record.get('scanDate')),
                              _value(record.get('latitude')), _value(record.get('longitude')),
                              _value(record.get('horizontalAccuracy')), _value(record.get('locationSource')),
                              names.get(beacon.upper(), ''), kind, beacon))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMyOwnedBeacons(context):
    data_headers = (('Pairing Date', 'datetime'), ('Latest Estimated Location Timestamp', 'datetime'), 'Name',
                    'Model', 'System Version', 'batteryLevel (as stored)', 'productId (as stored)',
                    'vendorId (as stored)', 'Estimated Location Records', 'Leash Records', 'Identifier',
                    'Stable Identifier')
    data_list = []
    sources = []
    for _root, records in _read_store(context.get_files_found()).items():
        names = _names(records)
        estimated = _estimates(records)
        leashes = {}
        for _file_found, record in records.get('LeashRecords', []):
            for beacon in record.get('associatedBeacons') or []:
                if isinstance(beacon, str):
                    leashes[beacon.upper()] = leashes.get(beacon.upper(), 0) + 1
        for file_found, record in records.get('OwnedBeacons', []):
            sources.append(file_found)
            identifier = _text(record.get('identifier'))
            newest, count = _estimate_columns(estimated, identifier)
            stable = record.get('stableIdentifier')
            stable = ', '.join(s for s in stable if isinstance(s, str)) if isinstance(stable, list) \
                else _text(stable)
            data_list.append((_date(record.get('pairingDate')), newest, names.get(identifier.upper(), ''),
                              _text(record.get('model')), _text(record.get('systemVersion')),
                              _value(record.get('batteryLevel')), _value(record.get('productId')),
                              _value(record.get('vendorId')), count, leashes.get(identifier.upper(), 0),
                              identifier, stable))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def findMySharedBeacons(context):
    data_headers = (('Share Date', 'datetime'), ('Latest Estimated Location Timestamp', 'datetime'), 'Owner Handle',
                    'Model', 'System Version', 'shareType (as stored)',
                    'productId (as stored)', 'vendorId (as stored)',
                    'Estimated Location Records', 'Identifier', 'Owner Beacon Identifier')
    data_list = []
    sources = []
    for _root, records in _read_store(context.get_files_found()).items():
        estimated = _estimates(records)
        for file_found, record in records.get('SharedBeacons', []):
            sources.append(file_found)
            identifier = _text(record.get('identifier'))
            newest, count = _estimate_columns(estimated, identifier)
            handle = record.get('ownerHandle') if isinstance(record.get('ownerHandle'), dict) else {}
            name = record.get('name')
            owner_beacon = _text(name.get('ownerBeaconIdentifier')) if isinstance(name, dict) else ''
            data_list.append((_date(record.get('shareDate')), newest, _text(handle.get('destination')),
                              _text(record.get('model')),
                              _text(record.get('systemVersion')), _value(record.get('shareType')),
                              _value(record.get('productId')),
                              _value(record.get('vendorId')), count, identifier, owner_beacon))
    return data_headers, data_list, '\n'.join(sources)
