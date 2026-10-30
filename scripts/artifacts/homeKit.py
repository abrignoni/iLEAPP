__artifacts_v2__ = {
    "homeKitHomes": {
        "name": "HomeKit Homes",
        "description": "Homes in the HomeKit stores mobile/Library/homed/datastore.sqlite and core.sqlite: name, owner user ID, the "
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
                 "archive and reported as decoded, text unchanged and archived dates in UTC. Record Modified and "
                 "Record Created are RecordMtime and RecordCtime from the row's record blob, a keyed archive whose"
                 " top-level keys (RecordType, RecordID, RecordMtime, RecordCtime, ETag and others) are named like"
                 " CloudKit CKRecord properties; that encoding was not sourced. Only the first datastore.sqlite "
                 "matched is read. One row per HMDHomeModel record. Creation Date, First Accessory Added, Home "
                 "Name, Owner User ID, Multi-User Enabled and Location Services Enabled are its creationDate, "
                 "firstHAPAccessoryAddedDate, name, ownerUserID, multiUserEnabled and locationServicesEnabled "
                 "fields, empty where the record has no such field. ownerName is not reported: it held a UUID-"
                 "shaped string, not a personal name, on the five images whose datastore.sqlite held a home. "
                 "Latitude, Longitude and Horizontal Accuracy (m) are the kCLLocationCodingKeyCoordinateLatitude, "
                 "kCLLocationCodingKeyCoordinateLongitude and kCLLocationCodingKeyHorizontalAccuracy values of the"
                 " CLLocation archived as homeLocation inside the record's homeLocationData archive; CLLocation "
                 "documents horizontalAccuracy in metres, and the coding key is matched to that property by its "
                 "name. How HomeKit sets that location, and when, is not established here: its "
                 "kCLLocationCodingKeyTimestamp held 0 on both images that carried one, so it is not reported, and"
                 " homeLocationNextUpdate is not reported. On hickman_ios15 and iphone11_ios17 the location "
                 "decoded; on hickman_ios13, hickman_ios14 and abe_ios16 homeLocation was the archive's null "
                 "object, so Latitude, Longitude and Horizontal Accuracy (m) are empty there. Creation Date was "
                 "filled only on abe_ios16. Also reads the ZMKFHOME table of the Core Data store core.sqlite in "
                 "the same folder, with its -wal, and adds a row for each home whose UUID (ZMODELID) no "
                 "datastore.sqlite record carries; Store names the file a row came from. Such a row has Home Name "
                 "from ZNAME and Owner User ID from the ZUSERID of the ZMKFUSER row that ZOWNER points to, and its"
                 " other columns are left empty: ZMKFHOME holds no record blob, and its ZCREATIONDATE, "
                 "ZFIRSTHAPACCESSORYADDEDDATE, ZLOCATION, ZMULTIUSERENABLED and ZLOCATIONSERVICESENABLED columns "
                 "are not read here (on adams_iphone12mini they held no value or 0). On abe_ios16 and "
                 "iphone11_ios17 both stores held the same home, with equal UUID and name; there the core ZUSERID "
                 "was the datastore ownerUserID with a mailto: prefix. On adams_iphone12mini (iOS 17.1.1) "
                 "datastore.sqlite held no records and core.sqlite held one home, the only row taken from "
                 "core.sqlite in the 24 tested images; why that image held the home only there is not established."
                 " Six images had a home row; on the other 18 datastore.sqlite held no records and core.sqlite, on"
                 " the 15 of them that had one, held no home. Record Modified and Record Created have no value on "
                 "rows from core.sqlite, which holds no record blob, and Store held one value on every row of each"
                 " tested image. core-cloudkit.sqlite is not read: on the three images holding a home it carried, "
                 "beside a copy of that home, a second home absent from datastore.sqlite and core.sqlite whose "
                 "name, rooms, scenes, accessories and user handles were mostly strings mixing letters and "
                 "punctuation, unlike the matching home, and what that record is has not been established. Also "
                 "not read from the same folder: datastore3.sqlite (mostly cloud zone state and setting records, "
                 "with a few IDS activity, access control and user data records), core-local.sqlite (a local "
                 "settings row, with bulletin registration and Aliro version rows on some images), core-cloudkit-"
                 "shared.sqlite (CloudKit mirroring bookkeeping only on the tested images), eventstore-*.sqlite "
                 "(no rows in any table on the tested images) and homeeventsd/homeevents.sqlite (Core Data "
                 "bookkeeping rows only).",
        "paths": ('*/mobile/Library/homed/datastore.sqlite*', '*/mobile/Library/homed/core.sqlite*'),
        "output_types": "all",
        "artifact_icon": "home",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 1 row (core.sqlite)",
            "belkactf6_tar": "iOS 16.3 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "falken_ios26": "iOS 26.2.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "felix23_ios16": "iOS 16.5 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "otto_ios17": "iOS 17.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
        },
    },
    "homeKitUsers": {
        "name": "HomeKit Users",
        "description": "Users of each home in the HomeKit stores mobile/Library/homed/datastore.sqlite and core.sqlite: user "
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
                 "archive and reported as decoded, text unchanged and archived dates in UTC. Record Modified and "
                 "Record Created are RecordMtime and RecordCtime from the row's record blob, a keyed archive whose"
                 " top-level keys (RecordType, RecordID, RecordMtime, RecordCtime, ETag and others) are named like"
                 " CloudKit CKRecord properties; that encoding was not sourced. Only the first datastore.sqlite "
                 "matched is read. One row per HMDUserModel record. Home Name is the name of the home whose UUID "
                 "is the user record's parent. User ID, Privilege (as stored) and Remote Access Allowed are its "
                 "userID, privilege and remoteAccessAllowed fields; no mapping of the privilege number was "
                 "sourced, and it held 3 on all 6 tested rows. Account Handle is the prefixedURI inside the "
                 "HMD.URI of its accountHandle archive, a mailto: URI on all 6 tested rows. Remote Access Allowed "
                 "held True on the 5 datastore.sqlite rows. Also reads the ZMKFUSER table of the Core Data store "
                 "core.sqlite in the same folder, with its -wal, and adds a row for each user whose UUID "
                 "(ZMODELID) no datastore.sqlite record carries; Store names the file a row came from. Such a row "
                 "has Home Name from the ZMKFHOME row that ZHOME (or ZOWNEDHOME) points to, User ID from ZUSERID, "
                 "Account Handle from the ZACCOUNTHANDLE archive read as above, and Privilege (as stored) and "
                 "Remote Access Allowed from ZPRIVILEGE and ZREMOTEACCESSALLOWED as stored. On abe_ios16 and "
                 "iphone11_ios17 both stores held the same user, with equal UUID, home, handle and privilege; "
                 "there ZUSERID was the datastore userID with a mailto: prefix, and ZREMOTEACCESSALLOWED held 1 "
                 "where datastore.sqlite held True. The only row taken from core.sqlite in the 24 tested images "
                 "was on adams_iphone12mini, whose datastore.sqlite held no records. Each of the six images with "
                 "rows held one user. Record Modified and Record Created have no value on rows from core.sqlite, "
                 "which holds no record blob, and Store held one value on every row of each tested image. core-"
                 "cloudkit.sqlite is not read: on the three images holding a home it carried, beside a copy of "
                 "that home, a second home absent from datastore.sqlite and core.sqlite whose name, rooms, scenes,"
                 " accessories and user handles were mostly strings mixing letters and punctuation, unlike the "
                 "matching home, and what that record is has not been established. Also not read from the same "
                 "folder: datastore3.sqlite (mostly cloud zone state and setting records, with a few IDS activity,"
                 " access control and user data records), core-local.sqlite (a local settings row, with bulletin "
                 "registration and Aliro version rows on some images), core-cloudkit-shared.sqlite (CloudKit "
                 "mirroring bookkeeping only on the tested images), eventstore-*.sqlite (no rows in any table on "
                 "the tested images) and homeeventsd/homeevents.sqlite (Core Data bookkeeping rows only).",
        "paths": ('*/mobile/Library/homed/datastore.sqlite*', '*/mobile/Library/homed/core.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 1 row (core.sqlite)",
            "belkactf6_tar": "iOS 16.3 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "falken_ios26": "iOS 26.2.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "felix23_ios16": "iOS 16.5 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "otto_ios17": "iOS 17.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
        },
    },
    "homeKitAccessories": {
        "name": "HomeKit Accessories and Devices",
        "description": "Accessories and devices in the HomeKit stores mobile/Library/homed/datastore.sqlite and core.sqlite: "
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
                 "archive and reported as decoded, text unchanged and archived dates in UTC. Record Modified and "
                 "Record Created are RecordMtime and RecordCtime from the row's record blob, a keyed archive whose"
                 " top-level keys (RecordType, RecordID, RecordMtime, RecordCtime, ETag and others) are named like"
                 " CloudKit CKRecord properties; that encoding was not sourced. Only the first datastore.sqlite "
                 "matched is read. One row per HMDDeviceModel record and per record whose type ends in "
                 "AccessoryModel or AccessorySensorModel. Type is the record type: on the tested images "
                 "HMDDeviceModel, HMDAppleMediaAccessoryModel, HMDAppleHomePodAccessoryModel and "
                 "HMDAppleMediaAccessorySensorModel; no tested image held a third-party accessory record, so that "
                 "path is not exercised. Name is the first of configuredName, name and providedName that holds "
                 "text; on every tested accessory row it came from providedName, as configuredName and name were "
                 "null or absent, so the first two choices are unexercised. Room is the name of the HMDRoomModel "
                 "record whose UUID is the accessory's roomUUID. Home Name is the name of the home whose UUID is "
                 "the record's parent. Manufacturer, Model, Serial Number and Firmware Version are the "
                 "manufacturer, model, serialNumber and firmwareVersion fields. Wi-Fi SSID and Wi-Fi MAC Address "
                 "are HMF.SSID and HMF.MACAddress from the record's wifiNetworkInfo archive, the MAC written as "
                 "six hex bytes. On the tested images every column was filled on the HomePod and media accessory "
                 "rows; on the sensor rows Room, Wi-Fi SSID and Wi-Fi MAC Address were empty; on the "
                 "HMDDeviceModel rows Home Name, Room, Manufacturer, Model, Serial Number, Firmware Version, Wi-Fi"
                 " SSID and Wi-Fi MAC Address are left empty: only a device's name is read, and on the tested "
                 "images device records carried none of those fields (their parent was an HMDAccountModel record, "
                 "not a home). Not reported from the same table: accessory setting, setting group and setting "
                 "constraint records (199 to 365 rows on the 4 images holding them); the action sets, which on "
                 "every tested image were the four of types HMActionSetTypeSleep, HMActionSetTypeWakeUp, "
                 "HMActionSetTypeHomeArrival and HMActionSetTypeHomeDeparture; and the other record types, among "
                 "them HMDResidentDeviceModel, HMDServiceTransaction, HMDMediaDestinationModel, "
                 "HMDApplicationDataModel, HMDHAPMetadataModel, HMDSoftwareUpdateModel, device capability, home "
                 "settings, network router, account handle and cloud bookkeeping records. Also reads the "
                 "ZMKFACCESSORY table of the Core Data store core.sqlite in the same folder, with its -wal, and "
                 "adds a row for each accessory whose UUID (ZMODELID) no datastore.sqlite record carries; Store "
                 "names the file a row came from. Such a row has Type from the store's own entity name for the row"
                 " (Z_PRIMARYKEY), Name from ZCONFIGUREDNAME or else ZPROVIDEDNAME, Home Name and Room from the "
                 "ZMKFHOME and ZMKFROOM rows that ZHOME and ZROOM point to, and Manufacturer, Model, Serial Number"
                 " and Firmware Version from ZMANUFACTURER, ZMODEL, ZSERIALNUMBER and ZFIRMWAREVERSION; the record"
                 " times and Wi-Fi columns are empty. No accessory in the 24 tested images was held only in "
                 "core.sqlite, so no row in those runs came from it. On iphone11_ios17 its four accessories had "
                 "the UUIDs of datastore.sqlite records, and read from core.sqlite alone (test case "
                 "hickman_ios17_core) they gave the same Name, Home Name, Room, Manufacturer, Model, Serial Number"
                 " and Firmware Version as those records, with Type MKFHAPAccessory or MKFAppleMediaAccessory. "
                 "Record Modified and Record Created have no value on rows from core.sqlite, which holds no record"
                 " blob, and Store held one value on every row of each tested image. core-cloudkit.sqlite is not "
                 "read: on the three images holding a home it carried, beside a copy of that home, a second home "
                 "absent from datastore.sqlite and core.sqlite whose name, rooms, scenes, accessories and user "
                 "handles were mostly strings mixing letters and punctuation, unlike the matching home, and what "
                 "that record is has not been established. Also not read from the same folder: datastore3.sqlite "
                 "(mostly cloud zone state and setting records, with a few IDS activity, access control and user "
                 "data records), core-local.sqlite (a local settings row, with bulletin registration and Aliro "
                 "version rows on some images), core-cloudkit-shared.sqlite (CloudKit mirroring bookkeeping only "
                 "on the tested images), eventstore-*.sqlite (no rows in any table on the tested images) and "
                 "homeeventsd/homeevents.sqlite (Core Data bookkeeping rows only).",
        "paths": ('*/mobile/Library/homed/datastore.sqlite*', '*/mobile/Library/homed/core.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "router",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1 row",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows (no datastore.sqlite records, no accessory in core.sqlite)",
            "belkactf6_tar": "iOS 16.3 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "ctf2020_ios12": "iOS 12.4 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "falken_ios26": "iOS 26.2.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "felix23_ios16": "iOS 16.5 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "felix_ios17": "iOS 17.6.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "fsfull002_ios17": "iOS 17.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "hickman_ios15": "iOS 15.3.1 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
            "jess_ios15": "iOS 15.0.2 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (no datastore.sqlite records, no core.sqlite)",
            "otto_ios17": "iOS 17.5.1 | 0 rows (no datastore.sqlite records, none in core.sqlite)",
        },
    },
}

import plistlib
import uuid as uuid_module
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


def _uuid(value):
    if isinstance(value, (bytes, bytearray)) and len(value) == 16:
        return str(uuid_module.UUID(bytes=bytes(value))).upper()
    return ''


def _core_table(core_file, table):
    if not core_file or not does_table_exist_in_db(core_file, table):
        return []
    return [dict(zip(row.keys(), row)) for row in get_sqlite_db_records(core_file, f'SELECT * FROM {table}')]


def _core(context):
    """Homes, users, rooms and accessories of the Core Data store core.sqlite, as row dicts keyed
    by Z_PK, with each accessory's entity name from Z_PRIMARYKEY, and the store path."""
    core_file = get_file_path(context.get_files_found(), 'core.sqlite') or ''
    store = {name: {row['Z_PK']: row for row in _core_table(core_file, table)}
             for name, table in (('homes', 'ZMKFHOME'), ('users', 'ZMKFUSER'), ('rooms', 'ZMKFROOM'),
                                 ('accessories', 'ZMKFACCESSORY'))}
    store['entities'] = {row['Z_ENT']: row['Z_NAME'] for row in _core_table(core_file, 'Z_PRIMARYKEY')}
    return store, core_file


def _source(*paths):
    return '\n'.join(path for path in paths if path)


def _core_home_names(core):
    return {pk: _text(row.get('ZNAME')) for pk, row in core['homes'].items()}


@artifact_processor
def homeKitHomes(context):
    data_headers = (
        ('Record Modified', 'datetime'), ('Record Created', 'datetime'), ('Creation Date', 'datetime'),
        ('First Accessory Added', 'datetime'), 'Home Name',
        'Owner User ID', 'Latitude', 'Longitude', 'Horizontal Accuracy (m)',
        'Multi-User Enabled', 'Location Services Enabled', 'Home UUID', 'Store')
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
            _stored(model.get('multiUserEnabled')), _stored(model.get('locationServicesEnabled')), uuid,
            'datastore.sqlite'))
    seen = {row[11] for row in data_list}
    core, core_file = _core(context)
    for row in core['homes'].values():
        uuid = _uuid(row.get('ZMODELID'))
        if not uuid or uuid in seen:
            continue
        owner = core['users'].get(row.get('ZOWNER'), {})
        data_list.append(('', '', '', '', _text(row.get('ZNAME')), _text(owner.get('ZUSERID')),
                          '', '', '', '', '', uuid, 'core.sqlite'))
    return data_headers, data_list, _source(db_file, core_file)


def _account_handle(blob):
    handle = _archive(blob) or {}
    uri = handle.get('HMD.URI') if isinstance(handle, dict) else None
    return _text(uri.get('prefixedURI')) if isinstance(uri, dict) else ''


@artifact_processor
def homeKitUsers(context):
    data_headers = (
        ('Record Modified', 'datetime'), ('Record Created', 'datetime'), 'Home Name', 'User ID',
        'Account Handle', 'Privilege (as stored)', 'Remote Access Allowed', 'User UUID', 'Store')
    data_list = []
    records, db_file = _records(context)
    homes = _home_names(records)
    for kind, uuid, parent, model, modified, created in records:
        if kind != 'HMDUserModel':
            continue
        data_list.append((
            modified, created, homes.get(parent, ''), _text(model.get('userID')),
            _account_handle(model.get('accountHandle')),
            _stored(model.get('privilege')), _stored(model.get('remoteAccessAllowed')), uuid,
            'datastore.sqlite'))
    seen = {row[7] for row in data_list}
    core, core_file = _core(context)
    core_homes = _core_home_names(core)
    for row in core['users'].values():
        uuid = _uuid(row.get('ZMODELID'))
        if not uuid or uuid in seen:
            continue
        data_list.append((
            '', '', core_homes.get(row.get('ZHOME') or row.get('ZOWNEDHOME'), ''), _text(row.get('ZUSERID')),
            _account_handle(row.get('ZACCOUNTHANDLE')), _stored(row.get('ZPRIVILEGE')),
            _stored(row.get('ZREMOTEACCESSALLOWED')), uuid, 'core.sqlite'))
    return data_headers, data_list, _source(db_file, core_file)


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
        'Wi-Fi MAC Address', 'UUID', 'Store')
    data_list = []
    records, db_file = _records(context)
    homes = _home_names(records)
    rooms = {uuid: _text(model.get('name')) for kind, uuid, _p, model, _m, _c in records
             if kind == 'HMDRoomModel'}
    for kind, uuid, parent, model, modified, created in records:
        if kind == 'HMDDeviceModel':
            data_list.append((modified, created, kind, _text(model.get('name')), homes.get(parent, ''),
                              '', '', '', '', '', '', '', uuid, 'datastore.sqlite'))
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
            uuid, 'datastore.sqlite'))
    seen = {row[12] for row in data_list}
    core, core_file = _core(context)
    core_homes = _core_home_names(core)
    for row in core['accessories'].values():
        uuid = _uuid(row.get('ZMODELID'))
        if not uuid or uuid in seen:
            continue
        room = core['rooms'].get(row.get('ZROOM'), {})
        data_list.append((
            '', '', core['entities'].get(row.get('Z_ENT'), ''),
            _text(row.get('ZCONFIGUREDNAME')) or _text(row.get('ZPROVIDEDNAME')),
            core_homes.get(row.get('ZHOME'), ''), _text(room.get('ZNAME')), _text(row.get('ZMANUFACTURER')),
            _text(row.get('ZMODEL')), _text(row.get('ZSERIALNUMBER')), _text(row.get('ZFIRMWAREVERSION')),
            '', '', uuid, 'core.sqlite'))
    return data_headers, data_list, _source(db_file, core_file)
