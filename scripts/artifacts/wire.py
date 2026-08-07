__artifacts_v2__ = {
    "wireAccount": {
        "name": "Wire Secure Messenger Account",
        "description": "Wire account details",
        "author": "Elliot Glendye",
        "creation_date": "2024-01-21",
        "last_update_date": "2025-11-12",
        "requirements": "",
        "category": "Business",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*'),
        "output_types": "all",
        "artifact_icon": "user",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | Wire • Secure Messenger 4.16.3 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Wire • Secure Messenger 3.111.9 | 8 rows",
            "iphone12_ios18": "iOS 18.7 | Wire • Secure Messenger 4.10.0 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | Wire • Secure Messenger 3.54 | 7 rows",
            "hickman_ios14": "iOS 14.3 | Wire • Secure Messenger 3.73 | 9 rows",
            "jess_ios15": "iOS 15.0.2 | Wire • Secure Messenger 3.94 | 1 row",
        }
    },
    "wireMessages": {
        "name": "Wire Secure Messenger Messages",
        "description": "Wire messages, including message sender, associated user identifiers and message type",
        "author": "Elliot Glendye",
        "creation_date": "2024-01-21",
        "last_update_date": "2026-07-31",
        "requirements": "",
        "category": "Business",
        "notes": "Rows with category 1 (undefined per the Wire source) are excluded. Unrecognized category values (including bitmask combinations) are reported as stored. Reference: Wire open source, wire-ios-data-model MessageCategory (OptionSet raw values), https://github.com/wireapp/wire-ios/blob/develop/wire-ios-data-model/Source/Model/Message/ZMMessage%2BCategorization.swift",
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
    phone_column = (
        'ZUSER.ZPHONENUMBER' if does_column_exist_in_db(source_path, 'ZUSER', 'ZPHONENUMBER')
        else 'NULL'
        )

    if has_location_data:
        query = f'''
        SELECT
            DISTINCT ZUSER.ZHANDLE AS 'User ID',
            ZUSER.ZNAME AS 'Display Name',
            ZUSERCLIENT.ZACTIVATIONDATE AS 'Activation Date',
            {phone_column} AS 'Phone Number',
            ZUSER.ZEMAILADDRESS AS 'Email Address',
            ZUSERCLIENT.ZACTIVATIONLOCATIONLATITUDE AS 'Activation Latitude',
            ZUSERCLIENT.ZACTIVATIONLOCATIONLONGITUDE AS 'Activation Longitude'
        FROM ZUSER
        LEFT JOIN ZUSERCLIENT ON ZUSER.Z_PK = ZUSERCLIENT.ZUSER;
        '''
        data_headers = (
            'User ID',
            'Display Name',
            ('Activation Date', 'datetime'),
            ('Phone Number', 'phonenumber'),
            'Email Address',
            'Latitude',
            'Longitude'
            )
    else:
        query = f'''
        SELECT
            DISTINCT ZUSER.ZHANDLE AS 'User ID',
            ZUSER.ZNAME AS 'Display Name',
            ZUSERCLIENT.ZACTIVATIONDATE AS 'Activation Date',
            {phone_column} AS 'Phone Number',
            ZUSER.ZEMAILADDRESS AS 'Email Address'
        FROM ZUSER
        LEFT JOIN ZUSERCLIENT ON ZUSER.Z_PK = ZUSERCLIENT.ZUSER;
        '''
        data_headers = (
            'User ID',
            'Display Name',
            ('Activation Date', 'datetime'),
            ('Phone Number', 'phonenumber'),
            'Email Address'
            )

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        activation_date = convert_cocoa_core_data_ts_to_utc(record[2])
        if has_location_data:
            data_list.append((
                record[0],
                record[1],
                activation_date,
                record[3],
                record[4],
                record[5],
                record[6]
                ))
        else:
            data_list.append((
                record[0],
                record[1],
                activation_date,
                record[3],
                record[4]
                ))
    return data_headers, data_list, source_path


@artifact_processor
def wireMessages(context):
    files_found = context().get_files_found()
    source_path = get_file_path(files_found, "store.wiredatabase")
    data_list = []

    query = '''
    SELECT
        ZMESSAGE.ZSERVERTIMESTAMP AS 'Date / Time',
        ZUSER.ZHANDLE AS 'User ID',
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
        ZMESSAGE.ZDURATION AS 'Call Duration (seconds)'
    FROM ZMESSAGE
    LEFT Join ZUSER On ZUSER.Z_PK = ZMESSAGE.ZSENDER
    WHERE ZMESSAGE.ZCACHEDCATEGORY != 1;
    '''
    data_headers = (
        ('Date / Time', 'datetime'),
        'User ID',
        'Display Name',
        'Message',
        'Message Type',
        'Call Duration (seconds)')

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
