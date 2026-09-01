__artifacts_v2__ = {
    "googleHomeStructure": {
        "name": "Google Home - Structure",
        "description": "The home recorded in the Google Home app's home graph, with its name, "
                       "postal address, coordinates, time zone and the owner email addresses "
                       "the store holds.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from ZSTRUCTURE in the home graph store, whose file name is prefixed with the "
                 "Google account identifier it belongs to, so one file is reported per signed-in "
                 "account. Address is taken from the ZADDRESS column, an NSKeyedArchiver binary plist "
                 "resolved by walking $objects from the $top root, and its addressAsSingleLine value "
                 "is reported. The latitude and longitude inside that archive matched the ZLATITUDE "
                 "and ZLONGITUDE columns exactly on the tested sample, which is two independent "
                 "readings of the same coordinate. Version Timestamp is Unix milliseconds, a different "
                 "epoch from the Core Data seconds used elsewhere in the same store. Coordinates "
                 "describe the home the account configured and are not evidence of a person's "
                 "location. Concierge Owner Email was empty in the tested sample, where that "
                 "subscription was not held; the column is kept because the store defines it. The "
                 "app's data container was present on 1 of the 26 registered iOS corpora swept for it, "
                 "so every count recorded here comes from that one extraction.",
        "paths": ('*/Documents/*_HomeGraphModel*',),
        "output_types": ["html", "tsv", "lava", "timeline", "kml"],
        "artifact_icon": "home",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
    "googleHomeDevices": {
        "name": "Google Home - Devices",
        "description": "Devices in the home graph, with the display name, manufacturer, model, "
                       "software version, assigned room and the timestamp the device was "
                       "linked.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from ZDEVICE, with the device type resolved through ZDEVICETYPE and the "
                 "assigned room through the Z_3SPACES join table to ZSPACE. A device with no row in "
                 "that join table is reported with an empty Room, which is how an unassigned device "
                 "appears; 12 of the 14 devices were assigned on the tested sample. Link Timestamp is "
                 "Core Data seconds since 2001-01-01. Display Name, User Defined Name and Agent "
                 "Defined Name are reported separately because the store holds all three and they need "
                 "not agree. SSID Suffix is the value the store holds for the device and is reported "
                 "as stored. The device's local authorization token is deliberately not reported. The "
                 "app's data container was present on 1 of the 26 registered iOS corpora swept for it, "
                 "so every count recorded here comes from that one extraction.",
        "paths": ('*/Documents/*_HomeGraphModel*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "device-desktop",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 14 rows",
        },
    },
    "googleHomeRooms": {
        "name": "Google Home - Rooms",
        "description": "Rooms defined in the home graph, with the room type recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from ZSPACE, with the room type resolved through ZSPACETYPE to its localized "
                 "name. These are the rooms the account created in this home, which is distinct from "
                 "the ZSPACETYPE table itself: that table is the catalogue of room types the app ships "
                 "and is the same on every device, so it is deliberately not reported. The same "
                 "applies to ZDEVICETYPE and ZTRAIT, which are shipped catalogues rather than user "
                 "data. Structure ID holds one value on every row in the tested sample because that "
                 "account had a single home, and it is kept so an account with more than one home "
                 "shows which home each room belongs to. The app's data container was present on 1 of "
                 "the 26 registered iOS corpora swept for it, so every count recorded here comes from "
                 "that one extraction.",
        "paths": ('*/Documents/*_HomeGraphModel*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "door",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 7 rows",
        },
    },
    "googleHomeAutomations": {
        "name": "Google Home - Automations",
        "description": "Automations configured for the home, with the name, what starts them, "
                       "what they do and whether they are enabled.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from ZAUTOMATION. Starter Description and Action Description are the summary "
                 "strings the app stores for the automation rather than its full definition, and the "
                 "store holds no record of an automation having run, so a row is evidence that an "
                 "automation was configured and not that it fired. Automation Type, Starter Type and "
                 "Automation Source are reported as stored; no mapping from those integers to a name "
                 "was sourced. Enabled, Valid and Executable were true and Scripted was false on every "
                 "automation in the tested sample. Those columns are uniform here rather than "
                 "unpopulated, and they are kept because a disabled or invalid automation is exactly "
                 "what an examiner would want to see distinguished. The app's data container was "
                 "present on 1 of the 26 registered iOS corpora swept for it, so every count recorded "
                 "here comes from that one extraction.",
        "paths": ('*/Documents/*_HomeGraphModel*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "automation",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 5 rows",
        },
    },
    "googleCastDevices": {
        "name": "Google Home - Cast Devices",
        "description": "Cast devices the app discovered on the local network, with the IP "
                       "address, port and the last discovered, accessed and published times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from CastFrameworkDB.sqlite, one row per device in ZGCKDBDEVICEINFO. "
                 "ZGCKDBDISCOVERYINFO.ZDEVICEINFO is null on every row, so the device is reached "
                 "through ZGCKDBLOCALCONNECTIONINFO instead, and each device owns two discovery "
                 "records that reference it through either ZLOCALCONNECTIONINFO or "
                 "ZLOCALCONNECTIONINFO1; both are followed, the newest discovery time is reported and "
                 "Discovery Records gives how many were found. All timestamps in this store are Core "
                 "Data seconds since 2001-01-01. IP Address is a private network address in the tested "
                 "sample, so it places the device on its own network rather than on the internet. "
                 "Discovery is the app observing a device on the network it was joined to, which is "
                 "not the same as the user casting to it, and the store holds no playback history. The "
                 "relay access token this store also holds is deliberately not reported. Last "
                 "Published Time and Device Config Change Time were empty on both devices in the "
                 "tested sample; the columns are kept because the store defines them and another "
                 "device may carry them. The app's data container was present on 1 of the 26 "
                 "registered iOS corpora swept for it, so every count recorded here comes from that "
                 "one extraction.",
        "paths": ('*/Library/Caches/CastFrameworkDB.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "cast",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
        },
    },
    "googleCastNetwork": {
        "name": "Google Home - Cast Network",
        "description": "Networks the cast framework recorded, with the last connected and last "
                       "query times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from ZGCKDBNETWORKINFO in CastFrameworkDB.sqlite. Network ID is the value the "
                 "framework stored to identify the network and on the tested sample it is an IPv4 "
                 "address rather than a network name, so it is reported as stored and must not be read "
                 "as an SSID. Timestamps are Core Data seconds since 2001-01-01. Type and Analytics "
                 "Enabled are reported as stored. Last Query Time was empty on the single network row "
                 "in the tested sample; the column is kept because the store defines it. The app's "
                 "data container was present on 1 of the 26 registered iOS corpora swept for it, so "
                 "every count recorded here comes from that one extraction.",
        "paths": ('*/Library/Caches/CastFrameworkDB.sqlite*',),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "wifi",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
        },
    },
}

import os
import plistlib
import sqlite3
from datetime import datetime, timedelta, timezone
from plistlib import UID

from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    logfunc,
    open_sqlite_db_readonly,
)

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)
_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)


def _core_data_to_utc(value):
    """Core Data seconds since 2001-01-01 to an aware UTC datetime, or ''."""
    if value in (None, '', 0):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _ms_to_utc(value):
    """Unix milliseconds to an aware UTC datetime, or ''."""
    if value in (None, '', 0):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(milliseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _unarchive(blob):
    """Resolve an NSKeyedArchiver archive into plain Python objects, or None."""
    if not blob:
        return None
    try:
        archive = plistlib.loads(bytes(blob))
    except (plistlib.InvalidFileException, ValueError, TypeError):
        return None
    if not isinstance(archive, dict) or '$objects' not in archive:
        return None
    objects = archive['$objects']

    def resolve(node, depth=0):
        if depth > 24:
            return None
        if isinstance(node, UID):
            index = node.data
            return resolve(objects[index], depth + 1) if index < len(objects) else None
        if isinstance(node, dict):
            if 'NS.keys' in node and 'NS.objects' in node:
                return {
                    str(resolve(key, depth + 1)): resolve(value, depth + 1)
                    for key, value in zip(node['NS.keys'], node['NS.objects'])
                }
            if 'NS.objects' in node:
                return [resolve(item, depth + 1) for item in node['NS.objects']]
            if 'NS.string' in node:
                return resolve(node['NS.string'], depth + 1)
            return {
                key: resolve(value, depth + 1)
                for key, value in node.items() if key != '$class'
            }
        if isinstance(node, str) and node == '$null':
            return None
        return node

    top = archive.get('$top') or {}
    root = top.get('root')
    if root is None and top:
        root = next(iter(top.values()))
    return resolve(root)


def _has_table(database, table):
    """True when the store carries the named table, so a same-named file fails closed."""
    try:
        connection = open_sqlite_db_readonly(database)
    except sqlite3.Error:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def _stores(files_found, suffix, marker_table):
    """Main database files whose name ends with suffix, sidecars and lookalikes excluded."""
    stores = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if not os.path.basename(file_found).endswith(suffix):
            continue
        if not _has_table(file_found, marker_table):
            logfunc(f'Google Home: {os.path.basename(file_found)} carries no '
                    f'{marker_table} table, skipped')
            continue
        stores.append(file_found)
    return stores


def _home_graph_stores(files_found):
    return _stores(files_found, '_HomeGraphModel', 'ZDEVICE')


def _cast_stores(files_found):
    return _stores(files_found, 'CastFrameworkDB.sqlite', 'ZGCKDBDEVICEINFO')


@artifact_processor
def googleHomeStructure(context):
    data_headers = (
        ('Version Timestamp', 'datetime'),
        'Structure Name',
        'Address',
        'Location',
        'Latitude',
        'Longitude',
        'Time Zone',
        'Nest Structure Owner Email',
        'Concierge Owner Email',
        'Linked With Nest Structure',
        'Structure ID',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT ZVERSIONTIMESTAMP, ZDISPLAYNAME, ZADDRESS, ZLOCATION, ZLATITUDE, ZLONGITUDE,
           ZTIMEZONE, ZNESTSTRUCTUREOWNEREMAIL, ZCONCIERGEOWNEREMAIL,
           ZISLINKEDWITHNESTSTRUCTURE, ZIDENTIFICATION
    FROM ZSTRUCTURE
    '''
    for database in _home_graph_stores(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            address = _unarchive(record[2])
            single_line = ''
            if isinstance(address, dict):
                single_line = address.get('addressAsSingleLine') or ''
            data_list.append((
                _ms_to_utc(record[0]),
                record[1],
                single_line,
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                bool(record[9]) if record[9] is not None else '',
                record[10],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googleHomeDevices(context):
    data_headers = (
        ('Link Timestamp', 'datetime'),
        'Display Name',
        'User Defined Name',
        'Agent Defined Name',
        'Room',
        'Device Type',
        'Manufacturer',
        'Model',
        'Software Version',
        'SSID Suffix (as stored)',
        'Notifications Enabled By User',
        'Is Matter Hub',
        'Agent Device ID',
        'Device ID',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT D.ZLINKTIMESTAMP, D.ZDISPLAYNAME, D.ZUSERDEFINEDNAME, D.ZAGENTDEFINEDNAME,
           S.ZDISPLAYNAME, T.ZLOCALIZEDNAME, D.ZMANUFACTURER, D.ZMODEL, D.ZSOFTWAREVERSION,
           D.ZSSIDSUFFIX, D.ZNOTIFICATIONENABLEDBYUSER, D.ZISMATTERHUB, D.ZAGENTDEVICEID,
           D.ZHGSID
    FROM ZDEVICE AS D
    LEFT JOIN ZDEVICETYPE AS T ON T.Z_PK = D.ZDEVICETYPE
    LEFT JOIN Z_3SPACES AS J ON J.Z_3DEVICES1 = D.Z_PK
    LEFT JOIN ZSPACE AS S ON S.Z_PK = J.Z_9SPACES
    ORDER BY D.ZLINKTIMESTAMP
    '''
    for database in _home_graph_stores(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                _core_data_to_utc(record[0]),
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                bool(record[10]) if record[10] is not None else '',
                bool(record[11]) if record[11] is not None else '',
                record[12],
                record[13],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googleHomeRooms(context):
    data_headers = (
        'Room Name',
        'Room Type',
        'Room ID',
        'Structure ID',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT S.ZDISPLAYNAME, T.ZLOCALIZEDNAME, S.ZIDENTIFICATION, R.ZIDENTIFICATION
    FROM ZSPACE AS S
    LEFT JOIN ZSPACETYPE AS T ON T.Z_PK = S.ZSPACETYPE
    LEFT JOIN ZSTRUCTURE AS R ON R.Z_PK = S.ZSTRUCTURE
    ORDER BY S.ZDISPLAYNAME
    '''
    for database in _home_graph_stores(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                record[0], record[1], record[2], record[3],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googleHomeAutomations(context):
    data_headers = (
        'Automation Name',
        'Starter Description',
        'Action Description',
        'Enabled',
        'Valid',
        'Executable',
        'Scripted',
        'Automation Type (as stored)',
        'Starter Type (as stored)',
        'Automation Source (as stored)',
        'Automation ID',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT ZDISPLAYNAME, ZSTARTERDESCRIPTION, ZACTIONDESCRIPTION, ZENABLED, ZVALID,
           ZEXECUTABLE, ZSCRIPTED, ZAUTOMATIONTYPE, ZSTARTERTYPE, ZAUTOMATIONSOURCE,
           ZIDENTIFICATION
    FROM ZAUTOMATION
    ORDER BY ZPOSITION
    '''
    for database in _home_graph_stores(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                record[0], record[1], record[2],
                bool(record[3]) if record[3] is not None else '',
                bool(record[4]) if record[4] is not None else '',
                bool(record[5]) if record[5] is not None else '',
                bool(record[6]) if record[6] is not None else '',
                record[7], record[8], record[9], record[10],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googleCastDevices(context):
    data_headers = (
        ('Last Discovered Time', 'datetime'),
        ('Last Accessed Time', 'datetime'),
        ('Last Published Time', 'datetime'),
        ('Device Config Change Time', 'datetime'),
        'Service Instance Name',
        'IP Address',
        'Port',
        'Device Version',
        'Capabilities (as stored)',
        'Status (as stored)',
        'Internal Status (as stored)',
        'Endpoint Device ID',
        'Discovery Records',
        'Source File',
    )
    data_list = []
    source_files = []

    # A device is reached from ZGCKDBDEVICEINFO through ZGCKDBLOCALCONNECTIONINFO.
    # ZGCKDBDISCOVERYINFO.ZDEVICEINFO is null on every row, and each device instead owns two
    # discovery records that point back through either ZLOCALCONNECTIONINFO or
    # ZLOCALCONNECTIONINFO1, so both columns are followed and the newest time is reported.
    query = '''
    SELECT
        (SELECT MAX(D.ZLASTDISCOVEREDTIME) FROM ZGCKDBDISCOVERYINFO AS D
          WHERE D.ZLOCALCONNECTIONINFO = LC.Z_PK OR D.ZLOCALCONNECTIONINFO1 = LC.Z_PK),
        I.ZLASTACCESSEDTIME,
        I.ZLASTPUBLISHEDTIME,
        I.ZDEVICECONFIGCHANGETIMESTAMP,
        (SELECT D.ZSERVICEINSTANCENAME FROM ZGCKDBDISCOVERYINFO AS D
          WHERE (D.ZLOCALCONNECTIONINFO = LC.Z_PK OR D.ZLOCALCONNECTIONINFO1 = LC.Z_PK)
            AND D.ZSERVICEINSTANCENAME IS NOT NULL LIMIT 1),
        NA.ZIPADDRESS,
        LC.ZPORT,
        I.ZDEVICEVERSION,
        I.ZCAPABILITIES,
        I.ZSTATUS,
        I.ZINTERNALSTATUS,
        I.ZENDPOINTDEVICEID,
        (SELECT COUNT(*) FROM ZGCKDBDISCOVERYINFO AS D
          WHERE D.ZLOCALCONNECTIONINFO = LC.Z_PK OR D.ZLOCALCONNECTIONINFO1 = LC.Z_PK)
    FROM ZGCKDBDEVICEINFO AS I
    LEFT JOIN ZGCKDBLOCALCONNECTIONINFO AS LC ON LC.ZDEVICEINFO = I.Z_PK
    LEFT JOIN ZGCKDBNETWORKADDRESS AS NA ON NA.ZLOCALCONNECTIONINFO = LC.Z_PK
    ORDER BY 1
    '''
    for database in _cast_stores(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                _core_data_to_utc(record[0]),
                _core_data_to_utc(record[1]),
                _core_data_to_utc(record[2]),
                _core_data_to_utc(record[3]),
                record[4], record[5], record[6], record[7], record[8], record[9],
                record[10], record[11], record[12],
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def googleCastNetwork(context):
    data_headers = (
        ('Last Connected Time', 'datetime'),
        ('Last Query Time', 'datetime'),
        'Network ID (as stored)',
        'Type (as stored)',
        'Analytics Enabled',
        'Source File',
    )
    data_list = []
    source_files = []

    query = '''
    SELECT ZLASTCONNECTEDTIME, ZLASTQUERYTIME, ZNETWORKID, ZTYPE, ZANALYTICSENABLED
    FROM ZGCKDBNETWORKINFO
    ORDER BY ZLASTCONNECTEDTIME
    '''
    for database in _cast_stores(context.get_files_found()):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                _core_data_to_utc(record[0]),
                _core_data_to_utc(record[1]),
                record[2], record[3],
                bool(record[4]) if record[4] is not None else '',
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)
