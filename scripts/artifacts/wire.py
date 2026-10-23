__artifacts_v2__ = {
    "wireAccount": {
        "name": "Wire Secure Messenger Account",
        "description": "Wire users joined to the clients recorded for them (ZUSER LEFT JOIN ZUSERCLIENT), one row "
                       "per user and client, with handle, display name, phone and email as stored and each client's "
                       "ID, device class, label, model and activation, discovery and last active dates, and, where "
                       "the schema has them, the client's activation location as Latitude and Longitude. The query "
                       "is not limited to the account signed in on the device.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2024-01-21",
        "last_update_date": "2026-10-23",
        "requirements": "",
        "category": "Business",
        "notes": "Each result of ZUSER LEFT JOIN ZUSERCLIENT is reported without DISTINCT: a user with several "
                 "clients gives one row per client, and a user with no client gives one row with the client "
                 "columns blank. Clients with no matching ZUSER are not selected. Only the first "
                 "store.wiredatabase found is read. Client ID is ZUSERCLIENT.ZREMOTEIDENTIFIER. Handle is "
                 "ZUSER.ZHANDLE, the handle attribute of Wire's User entity, which Wire's header describes as "
                 "the \"@name\" handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Public/ZMUser.h#L55-L56). "
                 "ZMUser.m writes it from the handle field of the backend's user record "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L484-L487) and from search "
                 "results (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L562-L573), "
                 "and the app's settings let the account owner choose one, shown after an @ prefix and sent "
                 "to /self/handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios/Wire-iOS/Sources/UserInterface/Settings/ChangingDetails/ChangeHandleViewController.swift#L101, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios/Wire-iOS/Sources/UserInterface/Settings/ChangingDetails/ChangeHandleViewController.swift#L328-L329, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-sync-engine/Source/Synchronization/Strategies/UserProfileUpdateRequestStrategy.swift#L142-L145). "
                 "The handle is not Wire's user ID, which ZMUser.m sets from the id of the backend's user record "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L442-L472) and the model "
                 "stores as remoteIdentifier_data "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L381); "
                 "this artifact does not report ZUSER.ZREMOTEIDENTIFIER_DATA. "
                 "In the Wire code read, "
                 "Client ID, Device Class, Device Label, Device Model, Activation Date and Last Active Date are "
                 "written from the backend's record of the client (id, class, label, model, time and "
                 "last_active) (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/UserClient/UserClient.swift#L358-L379, "
                 "https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Repositories/UserClients/UserClientsLocalStore.swift#L124-L130). "
                 "The self client's label, model and device class are also set locally when that client is "
                 "created, with device class derived from the model name "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/UserClient/UserClient.swift#L140-L153). Discovery Date "
                 "is set to the current time when UserClient.swift creates a client record it did not already "
                 "have (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/UserClient/UserClient.swift#L202-L209); "
                 "UserClientsLocalStore.swift also sets it from a date its caller supplies, and that caller was "
                 "not read (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireDomain/Sources/WireDomain/Repositories/UserClients/UserClientsLocalStore.swift#L199-L204). "
                 "That code is newer than the Wire builds on the corpora below, and the older writer was not "
                 "read. Dates are Core Data timestamps converted to UTC. On every corpus below no row has both "
                 "Activation Date and Discovery Date, so Activation Date, which leads the table, is blank on the "
                 "rows that carry a Discovery Date (iphone11_ios17: filled on 5 of 13 rows). Discovery Date has "
                 "no value on any row of iphone12_ios18 and jess_ios15. Last Active Date is blank where the "
                 "schema has no ZLASTACTIVEDATE column (hickman_ios13, hickman_ios14, iphone11_ios17, "
                 "jess_ios15). Phone Number is blank where the schema has no ZPHONENUMBER column (hc_ios18_7, "
                 "iphone12_ios18) and held no value on any row of iphone11_ios17 and jess_ios15. On hickman_ios13 "
                 "the 12 rows are 12 clients of 2 users; on hickman_ios14 the 10 rows are 9 clients of 2 users "
                 "and 1 user with no client; no two rows are equal on any corpus below. Source ownership and "
                 "self-account identity are not established here. Original contribution credited to Elliot "
                 "Glendye.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*'),
        "output_types": "all",
        "artifact_icon": "user",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Wire • Secure Messenger 4.16.3 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 13 rows",
            "iphone12_ios18": "iOS 18.7 | Wire • Secure Messenger 4.10.0 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | Wire • Secure Messenger 3.54 | 12 rows",
            "hickman_ios14": "iOS 14.3 | Wire • Secure Messenger 3.73 | 10 rows",
            "jess_ios15": "iOS 15.0.2 | Wire • Secure Messenger 3.94 | 1 row",
        }
    },
    "wireMessages": {
        "name": "Wire Secure Messenger Messages",
        "description": "Wire messages, including the sender's handle and display name, and message type",
        "author": 'Elliot Glendye, @AlexisBrignoni, Codex',
        "creation_date": "2024-01-21",
        "last_update_date": '2026-10-23',
        "requirements": "",
        "category": "Business",
        "notes": "Rows with category 1 (undefined per the Wire source) are excluded; rows with "
                 "no stored category are retained. Handle and Display Name come from the ZUSER row that "
                 "ZMESSAGE.ZSENDER points to (LEFT JOIN), so they are blank when no such row exists. Handle "
                 "is ZUSER.ZHANDLE, the handle attribute of Wire's User entity, which Wire's header describes "
                 "as the \"@name\" handle "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Public/ZMUser.h#L55-L56). "
                 "ZMUser.m writes it from the handle field of the backend's user record "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L484-L487) and from search "
                 "results (https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L562-L573). "
                 "The handle is not Wire's user ID, which ZMUser.m sets from the id of the backend's user record "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/wire-ios-data-model/Source/Model/User/ZMUser.m#L442-L472) and the model "
                 "stores as remoteIdentifier_data "
                 "(https://github.com/wireapp/wire-ios/blob/851bba150924e03ab6256f81ee96596552f878ba/WireData/Sources/WireData/Schema/zmessaging.xcdatamodeld/zmessaging2.144.0.xcdatamodel/contents#L381); "
                 "this artifact does not report ZUSER.ZREMOTEIDENTIFIER_DATA. That code is newer than the Wire "
                 "builds on the corpora below. "
                 "Message is the ZNORMALIZEDTEXT column as stored. ZDURATION "
                 "is reported as stored; its unit is not sourced "
                 "here. Unrecognized category values (including bitmask combinations) are "
                 "reported as stored. Reference: Wire open source, wire-ios-data-model "
                 "MessageCategory (OptionSet raw values), "
                 "https://github.com/wireapp/wire-ios/blob/1d90c3e2c54b223a61fb766802cce112ed5afa0f/wire-ios-data-model/Source/Model/Message/ZMMessage%2BCategorization.swift#L255-L273",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Wire • Secure Messenger 4.16.3 | 19 rows",
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 50 rows",
            "iphone12_ios18": "iOS 18.7 | Wire • Secure Messenger 4.10.0 | 38 rows",
            "hickman_ios13": "iOS 13.3.1 | Wire • Secure Messenger 3.54 | 12 rows",
            "hickman_ios14": "iOS 14.3 | Wire • Secure Messenger 3.73 | 18 rows",
            "jess_ios15": "iOS 15.0.2 | Wire • Secure Messenger 3.94 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    does_column_exist_in_db,
    convert_cocoa_core_data_ts_to_utc
    )


def _optional_column(source_path, table, column):
    """The qualified column when the table has it, else NULL, for columns some Wire schemas lack."""
    if does_column_exist_in_db(source_path, table, column):
        return f'{table}.{column}'
    return 'NULL'


@artifact_processor
def wireAccount(context):
    files_found = context().get_files_found()
    source_path = get_file_path(files_found, "store.wiredatabase")
    data_list = []

    has_location_data = does_column_exist_in_db(
        source_path,
        'ZUSERCLIENT',
        'ZACTIVATIONLOCATIONLATITUDE'
        )

    # Newer Wire versions drop ZUSER.ZPHONENUMBER, so it is selected only when present.
    # The client columns are selected the same way, so a schema without one still reports the rest.
    columns = [
        'ZUSERCLIENT.ZACTIVATIONDATE',
        _optional_column(source_path, 'ZUSERCLIENT', 'ZDISCOVERYDATE'),
        _optional_column(source_path, 'ZUSERCLIENT', 'ZLASTACTIVEDATE'),
        'ZUSER.ZHANDLE',
        'ZUSER.ZNAME',
        _optional_column(source_path, 'ZUSER', 'ZPHONENUMBER'),
        'ZUSER.ZEMAILADDRESS',
        _optional_column(source_path, 'ZUSERCLIENT', 'ZREMOTEIDENTIFIER'),
        _optional_column(source_path, 'ZUSERCLIENT', 'ZDEVICECLASS'),
        _optional_column(source_path, 'ZUSERCLIENT', 'ZLABEL'),
        _optional_column(source_path, 'ZUSERCLIENT', 'ZMODEL'),
        ]
    data_headers = [
        ('Activation Date', 'datetime'),
        ('Discovery Date', 'datetime'),
        ('Last Active Date', 'datetime'),
        'Handle',
        'Display Name',
        ('Phone Number', 'phonenumber'),
        'Email Address',
        'Client ID',
        'Device Class',
        'Device Label',
        'Device Model',
        ]
    if has_location_data:
        columns.extend([
            'ZUSERCLIENT.ZACTIVATIONLOCATIONLATITUDE',
            'ZUSERCLIENT.ZACTIVATIONLOCATIONLONGITUDE',
            ])
        data_headers.extend(['Latitude', 'Longitude'])

    query = f'''
    SELECT
        {', '.join(columns)}
    FROM ZUSER
    LEFT JOIN ZUSERCLIENT ON ZUSER.Z_PK = ZUSERCLIENT.ZUSER;
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record[0]),
            convert_cocoa_core_data_ts_to_utc(record[1]),
            convert_cocoa_core_data_ts_to_utc(record[2]),
            *tuple(record)[3:]
            ))
    return tuple(data_headers), data_list, source_path


@artifact_processor
def wireMessages(context):
    files_found = context().get_files_found()
    source_path = get_file_path(files_found, "store.wiredatabase")
    data_list = []

    query = '''
    SELECT
        ZMESSAGE.ZSERVERTIMESTAMP AS 'Date / Time',
        ZUSER.ZHANDLE AS 'Handle',
        ZUSER.ZNAME AS 'Display Name',
        ZMESSAGE.ZNORMALIZEDTEXT AS 'Message',
        CASE ZMESSAGE.ZCACHEDCATEGORY
            WHEN 0 THEN 'None (uncategorized)'
            WHEN 2 THEN 'Text Message'
            WHEN 8 THEN 'Image Message'
            WHEN 256 THEN 'Location Message'
            WHEN 2048 THEN 'System Message'
            ELSE ZMESSAGE.ZCACHEDCATEGORY
        END AS 'Message Type',
        ZMESSAGE.ZDURATION AS 'ZDURATION (as stored)'
    FROM ZMESSAGE
    LEFT Join ZUSER On ZUSER.Z_PK = ZMESSAGE.ZSENDER
    WHERE ZMESSAGE.ZCACHEDCATEGORY != 1 OR ZMESSAGE.ZCACHEDCATEGORY IS NULL;
    '''
    data_headers = (
        ('Date / Time', 'datetime'),
        'Handle',
        'Display Name',
        'Message',
        'Message Type',
        'ZDURATION (as stored)')

    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
        date_time = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((
            date_time,
            record[1],
            record[2],
            record[3],
            record[4],
            record[5]
            ))

    return data_headers, data_list, source_path
