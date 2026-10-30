__artifacts_v2__ = {
    "homeKitHomes": {
        "name": "HomeKit Homes",
        "description": "Homes in the HomeKit store mobile/Library/homed/datastore.sqlite: name, owner user ID, the "
                       "location stored for the home and the dates its record carries",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "HomeKit",
        "notes": "Reads the record table of mobile/Library/homed/datastore.sqlite, with its -wal when the "
                 "extraction holds one (hc_ios26 and otto_ios17 held none, so the database file alone was read "
                 "there). Each record row's data blob (encoding 1 on every tested row) is an NSKeyedArchiver "
                 "archive of the model, read with nska_deserialize; fields are named after the keys of that "
                 "archive and reported as decoded, text unchanged and archived dates in UTC. Record Modified "
                 "and Record Created are RecordMtime and RecordCtime from the row's record blob, a keyed "
                 "archive whose top-level keys are those of a CloudKit CKRecord. Only the first "
                 "datastore.sqlite matched is read. One row per HMDHomeModel record. Creation Date, First "
                 "Accessory Added, Home Name, Owner User ID, Multi-User Enabled and Location Services Enabled "
                 "are its creationDate, firstHAPAccessoryAddedDate, name, ownerUserID, multiUserEnabled and "
                 "locationServicesEnabled fields, empty where the record has no such field. ownerName is not "
                 "reported: it held a UUID-shaped string, not a personal name, on every tested image. "
                 "Latitude, Longitude and Horizontal Accuracy (m) are the "
                 "kCLLocationCodingKeyCoordinateLatitude, kCLLocationCodingKeyCoordinateLongitude and "
                 "kCLLocationCodingKeyHorizontalAccuracy values of the CLLocation archived as homeLocation "
                 "inside the record's homeLocationData archive; CLLocation documents horizontalAccuracy in "
                 "metres, and the coding key is matched to that property by its name. How HomeKit sets that "
                 "location, and when, is not established here: its kCLLocationCodingKeyTimestamp held 0 on "
                 "both images that carried one, so it is not reported, and homeLocationNextUpdate is not "
                 "reported. On hickman_ios15 and iphone11_ios17 the location decoded; on hickman_ios13, "
                 "hickman_ios14 and abe_ios16 homeLocation was the archive's null object, so Latitude, "
                 "Longitude and Horizontal Accuracy (m) are empty there. Creation Date was filled only on "
                 "abe_ios16. The five images with rows held one home each; the other 19 tested images hold a "
                 "datastore.sqlite whose record table is empty.",
        "paths": ('*/mobile/Library/homed/datastore.sqlite*',),
        "output_types": "all",
        "artifact_icon": "home",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows (record table empty)",
            "belkactf6_tar": "iOS 16.3 | 0 rows (record table empty)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (record table empty)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (record table empty)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (record table empty)",
            "falken_ios26": "iOS 26.2.1 | 0 rows (record table empty)",
            "felix23_ios16": "iOS 16.5 | 0 rows (record table empty)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (record table empty)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (record table empty)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (record table empty)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (record table empty)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (record table empty)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (record table empty)",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows (record table empty)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (record table empty)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (record table empty)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (record table empty)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (record table empty)",
            "otto_ios17": "iOS 17.5.1 | 0 rows (record table empty)",
        },
    },
    "homeKitUsers": {
        "name": "HomeKit Users",
        "description": "Users of each home in the HomeKit store mobile/Library/homed/datastore.sqlite: user "
                       "ID, account handle, privilege and remote access",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "HomeKit",
        "notes": "Reads the record table of mobile/Library/homed/datastore.sqlite, with its -wal when the "
                 "extraction holds one (hc_ios26 and otto_ios17 held none, so the database file alone was read "
                 "there). Each record row's data blob (encoding 1 on every tested row) is an NSKeyedArchiver "
                 "archive of the model, read with nska_deserialize; fields are named after the keys of that "
                 "archive and reported as decoded, text unchanged and archived dates in UTC. Record Modified "
                 "and Record Created are RecordMtime and RecordCtime from the row's record blob, a keyed "
                 "archive whose top-level keys are those of a CloudKit CKRecord. Only the first "
                 "datastore.sqlite matched is read. One row per HMDUserModel record. Home Name is the name of "
                 "the home whose UUID is the user record's parent. User ID, Privilege (as stored) and Remote "
                 "Access Allowed are its userID, privilege and remoteAccessAllowed fields; no mapping of the "
                 "privilege number was sourced, and it held 3 on all 5 tested rows. Account Handle is the "
                 "prefixedURI inside the HMD.URI of its accountHandle archive, a mailto: URI on all 5 tested "
                 "rows. Remote Access Allowed held True on all 5 tested rows. Each of the five images with "
                 "rows held one user record.",
        "paths": ('*/mobile/Library/homed/datastore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows (record table empty)",
            "belkactf6_tar": "iOS 16.3 | 0 rows (record table empty)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (record table empty)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (record table empty)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (record table empty)",
            "falken_ios26": "iOS 26.2.1 | 0 rows (record table empty)",
            "felix23_ios16": "iOS 16.5 | 0 rows (record table empty)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (record table empty)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (record table empty)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (record table empty)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (record table empty)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (record table empty)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (record table empty)",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows (record table empty)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (record table empty)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (record table empty)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (record table empty)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (record table empty)",
            "otto_ios17": "iOS 17.5.1 | 0 rows (record table empty)",
        },
    },
    "homeKitAccessories": {
        "name": "HomeKit Accessories and Devices",
        "description": "Accessories and devices in the HomeKit store mobile/Library/homed/datastore.sqlite: "
                       "name, room, manufacturer, model, serial number, firmware and the Wi-Fi network "
                       "the store records for them",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "HomeKit",
        "notes": "Reads the record table of mobile/Library/homed/datastore.sqlite, with its -wal when the "
                 "extraction holds one (hc_ios26 and otto_ios17 held none, so the database file alone was read "
                 "there). Each record row's data blob (encoding 1 on every tested row) is an NSKeyedArchiver "
                 "archive of the model, read with nska_deserialize; fields are named after the keys of that "
                 "archive and reported as decoded, text unchanged and archived dates in UTC. Record Modified "
                 "and Record Created are RecordMtime and RecordCtime from the row's record blob, a keyed "
                 "archive whose top-level keys are those of a CloudKit CKRecord. Only the first "
                 "datastore.sqlite matched is read. One row per HMDDeviceModel record and per record whose "
                 "type ends in AccessoryModel or AccessorySensorModel. Type is the record type: on the tested "
                 "images HMDDeviceModel, HMDAppleMediaAccessoryModel, HMDAppleHomePodAccessoryModel and "
                 "HMDAppleMediaAccessorySensorModel; no tested image held a third-party accessory record, so "
                 "that path is not exercised. Name is the first of configuredName, name and providedName that "
                 "holds text; on every tested accessory row it came from providedName, as configuredName and "
                 "name were null or absent, so the first two choices are unexercised. Room is the name of the "
                 "HMDRoomModel record whose UUID is the accessory's roomUUID. Home Name is the name of the "
                 "home whose UUID is the record's parent. Manufacturer, Model, Serial Number and Firmware "
                 "Version are the manufacturer, model, serialNumber and firmwareVersion fields. Wi-Fi SSID and "
                 "Wi-Fi MAC Address are HMF.SSID and HMF.MACAddress from the record's wifiNetworkInfo archive, "
                 "the MAC written as six hex bytes. On the tested images every column was filled on the "
                 "HomePod and media accessory rows; on the sensor rows Room, Wi-Fi SSID and Wi-Fi MAC Address "
                 "were empty; on the HMDDeviceModel rows Home Name, Room, Manufacturer, Model, Serial Number, "
                 "Firmware Version, Wi-Fi SSID and Wi-Fi MAC Address are left empty: only a device's name is "
                 "read, and on the tested images device records carried none of those fields (their parent was "
                 "an HMDAccountModel record, not a home). Not reported from the same table: accessory setting, "
                 "setting group and setting constraint records (199 to 365 rows on the 4 images holding them); "
                 "the action sets, which on every tested image were the four of types HMActionSetTypeSleep, "
                 "HMActionSetTypeWakeUp, HMActionSetTypeHomeArrival and HMActionSetTypeHomeDeparture; and the "
                 "other record types, among them HMDResidentDeviceModel, HMDServiceTransaction, "
                 "HMDMediaDestinationModel, HMDApplicationDataModel, HMDHAPMetadataModel, "
                 "HMDSoftwareUpdateModel, device capability, home settings, network router, account handle and "
                 "cloud bookkeeping records. datastore3.sqlite and the other stores in the same folder "
                 "(core*.sqlite and eventstore*.sqlite in the iOS 16 and 17 path listings) are not read.",
        "paths": ('*/mobile/Library/homed/datastore.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "router",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows (record table empty)",
            "belkactf6_tar": "iOS 16.3 | 0 rows (record table empty)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (record table empty)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (record table empty)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (record table empty)",
            "falken_ios26": "iOS 26.2.1 | 0 rows (record table empty)",
            "felix23_ios16": "iOS 16.5 | 0 rows (record table empty)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (record table empty)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (record table empty)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (record table empty)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (record table empty)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (record table empty)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (record table empty)",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "hickman_ios15": "iOS 15.3.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (record table empty)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (record table empty)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (record table empty)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (record table empty)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (record table empty)",
            "otto_ios17": "iOS 17.5.1 | 0 rows (record table empty)",
        },
    },
}

import plistlib
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, does_table_exist_in_db, \
    get_file_path, get_sqlite_db_records, logfunc

_QUERY = 'SELECT type, uuid, parent_uuid, encoding, record, data FROM record ORDER BY rowid'
_DECODE_ERRORS = (nd.DeserializeError, plistlib.InvalidFileException, ValueError, TypeError, KeyError,
                  IndexError, AttributeError, OverflowError, RecursionError)


def _cocoa(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return convert_unix_ts_to_utc(value + 978307200)
    return ''


def _record_times(blob):
    """(RecordMtime, RecordCtime) from the record blob, the keyed archive of the row's CloudKit
    record, whose fields sit at the archive's $top level."""
    try:
        archive = plistlib.loads(bytes(blob))
        objects, top = archive['$objects'], archive['$top']
    except _DECODE_ERRORS:
        return '', ''

    def date(key):
        uid = top.get(key)
        if not isinstance(uid, plistlib.UID) or uid.data >= len(objects):
            return ''
        obj = objects[uid.data]
        return _cocoa(obj.get('NS.time')) if isinstance(obj, dict) else ''
    return date('RecordMtime'), date('RecordCtime')


def _archive(blob):
    """A keyed archive (bytes, or an NSData wrapper of them) deserialized, or None."""
    if isinstance(blob, dict) and 'NS.data' in blob:
        blob = blob['NS.data']
    if not isinstance(blob, (bytes, bytearray)) or not bytes(blob).startswith(b'bplist00'):
        return None
    try:
        return nd.deserialize_plist_from_string(bytes(blob))
    except _DECODE_ERRORS:
        return None


def _text(value):
    return value if isinstance(value, str) else ''


def _date(value):
    """An NSDate from the archive. ccl_bplist builds it as 2001-01-01 plus its seconds with no
    zone, so it is UTC and is marked as such."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return ''


def _stored(value):
    return '' if value is None or isinstance(value, (dict, list, bytes, bytearray)) else str(value)


def _records(context):
    """[(type, uuid, parent uuid, model dict, record modified, record created)] and the database path."""
    db_file = get_file_path(context.get_files_found(), 'datastore.sqlite')
    if not db_file or not does_table_exist_in_db(db_file, 'record'):
        return [], db_file or ''
    records = []
    skipped = 0
    for row in get_sqlite_db_records(db_file, _QUERY):
        model = _archive(row['data']) if row['encoding'] == 1 else None
        if not isinstance(model, dict):
            skipped += 1
            continue
        modified, created = _record_times(row['record']) if row['record'] else ('', '')
        records.append((row['type'] or '', row['uuid'] or '', row['parent_uuid'] or '', model,
                        modified, created))
    if skipped:
        logfunc(f'HomeKit: {skipped} record rows not read (data not a keyed archive, or encoding not 1)')
    return records, db_file


def _home_names(records):
    return {uuid: _text(model.get('name')) for kind, uuid, _p, model, _m, _c in records
            if kind == 'HMDHomeModel'}


@artifact_processor
def homeKitHomes(context):
    data_headers = (
        ('Record Modified', 'datetime'), ('Record Created', 'datetime'), ('Creation Date', 'datetime'),
        ('First Accessory Added', 'datetime'), 'Home Name',
        'Owner User ID', 'Latitude', 'Longitude', 'Horizontal Accuracy (m)',
        'Multi-User Enabled', 'Location Services Enabled', 'Home UUID')
    data_list = []
    records, db_file = _records(context)
    for kind, uuid, _parent, model, modified, created in records:
        if kind != 'HMDHomeModel':
            continue
        archived = _archive(model.get('homeLocationData'))
        location = archived.get('homeLocation') if isinstance(archived, dict) else None
        if not isinstance(location, dict):
            location = {}
        latitude = location.get('kCLLocationCodingKeyCoordinateLatitude')
        longitude = location.get('kCLLocationCodingKeyCoordinateLongitude')
        accuracy = location.get('kCLLocationCodingKeyHorizontalAccuracy')
        data_list.append((
            modified, created, _date(model.get('creationDate')),
            _date(model.get('firstHAPAccessoryAddedDate')), _text(model.get('name')),
            _text(model.get('ownerUserID')),
            latitude if isinstance(latitude, float) else '',
            longitude if isinstance(longitude, float) else '',
            accuracy if isinstance(accuracy, (int, float)) else '',
            _stored(model.get('multiUserEnabled')), _stored(model.get('locationServicesEnabled')), uuid))
    return data_headers, data_list, db_file


@artifact_processor
def homeKitUsers(context):
    data_headers = (
        ('Record Modified', 'datetime'), ('Record Created', 'datetime'), 'Home Name', 'User ID',
        'Account Handle', 'Privilege (as stored)', 'Remote Access Allowed', 'User UUID')
    data_list = []
    records, db_file = _records(context)
    homes = _home_names(records)
    for kind, uuid, parent, model, modified, created in records:
        if kind != 'HMDUserModel':
            continue
        handle = _archive(model.get('accountHandle')) or {}
        uri = handle.get('HMD.URI') if isinstance(handle, dict) else None
        data_list.append((
            modified, created, homes.get(parent, ''), _text(model.get('userID')),
            _text(uri.get('prefixedURI')) if isinstance(uri, dict) else '',
            _stored(model.get('privilege')), _stored(model.get('remoteAccessAllowed')), uuid))
    return data_headers, data_list, db_file


def _accessory_name(model):
    for key in ('configuredName', 'name', 'providedName'):
        if _text(model.get(key)):
            return model[key]
    return ''


@artifact_processor
def homeKitAccessories(context):
    data_headers = (
        ('Record Modified', 'datetime'), ('Record Created', 'datetime'), 'Type', 'Name', 'Home Name',
        'Room', 'Manufacturer', 'Model', 'Serial Number', 'Firmware Version', 'Wi-Fi SSID',
        'Wi-Fi MAC Address', 'UUID')
    data_list = []
    records, db_file = _records(context)
    homes = _home_names(records)
    rooms = {uuid: _text(model.get('name')) for kind, uuid, _p, model, _m, _c in records
             if kind == 'HMDRoomModel'}
    for kind, uuid, parent, model, modified, created in records:
        if kind == 'HMDDeviceModel':
            data_list.append((modified, created, kind, _text(model.get('name')), homes.get(parent, ''),
                              '', '', '', '', '', '', '', uuid))
            continue
        if not kind.endswith(('AccessoryModel', 'AccessorySensorModel')):
            continue
        wifi = _archive(model.get('wifiNetworkInfo')) or {}
        mac = wifi.get('HMF.MACAddress') if isinstance(wifi, dict) else None
        mac = mac.get('HMF.data') if isinstance(mac, dict) else None
        data_list.append((
            modified, created, kind, _accessory_name(model), homes.get(parent, ''),
            rooms.get(_text(model.get('roomUUID')), ''), _text(model.get('manufacturer')),
            _text(model.get('model')), _text(model.get('serialNumber')),
            _text(model.get('firmwareVersion')),
            _text(wifi.get('HMF.SSID')) if isinstance(wifi, dict) else '',
            ':'.join(f'{b:02x}' for b in mac) if isinstance(mac, (bytes, bytearray)) and len(mac) == 6 else '',
            uuid))
    return data_headers, data_list, db_file
