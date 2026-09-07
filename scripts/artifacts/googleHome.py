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
                 "location. Concierge Owner Email was empty in the tested sample; the column is "
                 "kept because the store defines it. The "
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
                 "that join table is reported with an empty Room; 12 of the 14 devices on the "
                 "tested sample had a row in that table. Link Timestamp is "
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
                 "name. These are the rooms recorded for this home, which is distinct from the "
                 "ZSPACETYPE table itself: that table lists room types rather than rooms and is "
                 "not reported. The same applies to ZDEVICETYPE and ZTRAIT, which list types "
                 "rather than rows tied to this home. Structure ID holds one value on every row "
                 "in the tested sample because that "
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
                 "strings the app stores for the automation rather than its full definition, and "
                 "no table in the tested store records an automation having run, so a row is "
                 "evidence that an "
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
        "name": "Google Cast Framework - Devices",
        "description": "Cast receivers recorded in the Google Cast SDK's CastFrameworkDB.sqlite "
                       "inside an app's container, with the app that owns the container, the "
                       "receiver's friendly name and model where the store holds them, IP address "
                       "and port, and the last accessed and last discovered times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from ZGCKDBDEVICEINFO in every Library/Caches/CastFrameworkDB.sqlite the "
                 "extraction holds. The file is written by Google's Cast SDK, which many apps "
                 "embed, so a store sits in the container of whichever app embeds it: Container "
                 "App is the bundle id from that container's metadata plist, and on the 12 tested "
                 "images holding the store the containers belonged to YouTube, Spotify, Netflix, "
                 "Google Photos, Google Home, Disney+, ESPN, CNN, Facebook, NHL, MSNBC and "
                 "Twitch; the Google Home app itself was on one of them. A row records that the "
                 "SDK inside that app knew of a receiver; it does not establish that the user "
                 "cast to it, and no table in the tested stores records playback. Friendly Name "
                 "and Model "
                 "Name are the receiver's own strings as stored, present on 9 of the 31 device "
                 "rows across the tested images. A device is reached from ZGCKDBDEVICEINFO "
                 "through ZGCKDBLOCALCONNECTIONINFO (ZGCKDBDISCOVERYINFO.ZDEVICEINFO was null on "
                 "every row), each device owning up to two discovery records that reference it "
                 "through ZLOCALCONNECTIONINFO or ZLOCALCONNECTIONINFO1; both are followed, the "
                 "newest discovery time is reported and Discovery Records gives how many were "
                 "found. A device with no local connection record, 22 of the 31 rows, has blank "
                 "IP Address, Port, Service Instance Name and Last Discovered Time and a Device "
                 "Version and Capabilities of 0, which is why Last Accessed Time, present on "
                 "every row, leads the table. All timestamps in this store are Core Data seconds "
                 "since 2001-01-01. IP Address was a private network address on every row that "
                 "carried one, so it places the receiver on its own network rather than on the "
                 "internet. Older SDK stores lack the ZDEVICECONFIGCHANGETIMESTAMP and "
                 "ZINTERNALSTATUS columns (the iOS 12 to 16 images); they are read as empty "
                 "rather than failing the query, which until this change returned no device on 11 "
                 "of the 12 images. Last Published Time and Device Config Change Time were empty "
                 "on all 31 rows and Internal Status on all but 2; the columns are kept because "
                 "the store defines them. Endpoint Device ID held the literal guestModeDeviceID "
                 "on 21 of the 31 rows. The ZMANUFACTURER column was empty on every row of every "
                 "tested image and is not reported. The relay access token this store also holds "
                 "is deliberately not reported.",
        "paths": ('*/Library/Caches/CastFrameworkDB.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "cast",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 3 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 2 rows",
            "belkactf6": "iOS 16.3 | 1 row",
            "ctf2020_ios12": "iOS 12.4 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 7 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 5 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no CastFrameworkDB.sqlite in the extraction)",
        },
    },
    "googleCastNetwork": {
        "name": "Google Cast Framework - Networks",
        "description": "Networks recorded in the Google Cast SDK's CastFrameworkDB.sqlite inside "
                       "an app's container, with the app that owns the container and the last "
                       "connected and last query times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Google Home",
        "notes": "Read from ZGCKDBNETWORKINFO in every Library/Caches/CastFrameworkDB.sqlite the "
                 "extraction holds. The file is written by Google's Cast SDK, which many apps "
                 "embed, so Container App names the app whose container the store sits in, from "
                 "that container's metadata plist; the apps seen on the 12 tested images are "
                 "listed in the Devices artifact's notes. Network ID is the value the SDK stored "
                 "to identify the network: an IPv4 address on 34 of the 38 tested rows and an "
                 "IPv6 address on the other 4, never a network name, so it is reported as stored "
                 "and must not be read as an SSID. Timestamps are Core Data seconds since "
                 "2001-01-01. Type and Analytics Enabled are reported as stored. Last Query Time "
                 "was empty on all 38 tested rows; the column is kept because the store defines "
                 "it.",
        "paths": ('*/Library/Caches/CastFrameworkDB.sqlite*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/mobile/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava", "timeline"],
        "artifact_icon": "wifi",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 5 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 1 row",
            "belkactf6": "iOS 16.3 | 1 row",
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 9 rows",
            "hickman_ios15": "iOS 15.3.1 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows (no CastFrameworkDB.sqlite in the extraction)",
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
    null_absent_columns,
    open_sqlite_db_readonly,
)

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'


def _container_apps(files_found):
    """Map a container directory to the bundle id its metadata plist records.

    Built from this artifact's own matched files, so it does not depend on the order
    artifacts run in."""
    apps = {}
    for found in files_found:
        found = str(found)
        if os.path.basename(found) != _METADATA_NAME:
            continue
        try:
            with open(found, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Google Cast: could not read a container metadata plist: {error}')
            continue
        bundle_id = plist.get('MCMMetadataIdentifier')
        if bundle_id:
            apps[os.path.dirname(found).replace('\\', '/')] = bundle_id
    return apps


def _container_app(store, apps):
    """Bundle id of the app owning <container>/Library/Caches/CastFrameworkDB.sqlite, or ''."""
    container = os.path.dirname(os.path.dirname(os.path.dirname(str(store)))).replace('\\', '/')
    return apps.get(container, '')

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
        ('Last Accessed Time', 'datetime'),
        ('Last Discovered Time', 'datetime'),
        ('Last Published Time', 'datetime'),
        ('Device Config Change Time', 'datetime'),
        'Container App',
        'Friendly Name',
        'Model Name',
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
        I.ZFRIENDLYNAME,
        I.ZMODELNAME,
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
    ORDER BY I.ZLASTACCESSEDTIME
    '''
    files_found = context.get_files_found()
    apps = _container_apps(files_found)
    for database in _cast_stores(files_found):
        rows = 0
        # older Cast SDK stores lack ZDEVICECONFIGCHANGETIMESTAMP and ZINTERNALSTATUS; read them as NULL
        for record in get_sqlite_db_records(database, null_absent_columns(database, query)):
            rows += 1
            data_list.append((
                _core_data_to_utc(record[1]),
                _core_data_to_utc(record[0]),
                _core_data_to_utc(record[2]),
                _core_data_to_utc(record[3]),
                _container_app(database, apps),
                record[4], record[5],
                record[6], record[7], record[8], record[9], record[10], record[11],
                record[12], record[13], record[14],
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
        'Container App',
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
    files_found = context.get_files_found()
    apps = _container_apps(files_found)
    for database in _cast_stores(files_found):
        rows = 0
        for record in get_sqlite_db_records(database, query):
            rows += 1
            data_list.append((
                _core_data_to_utc(record[0]),
                _core_data_to_utc(record[1]),
                _container_app(database, apps),
                record[2], record[3],
                bool(record[4]) if record[4] is not None else '',
                context.get_relative_path(database),
            ))
        if rows:
            source_files.append(database)

    return data_headers, data_list, '\n'.join(source_files)
