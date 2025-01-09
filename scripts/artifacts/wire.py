__artifacts_v2__ = {
    "wireAccount": {
        "name": "Wire Secure Messenger Account",
        "description": "Wire account details",
        "author": "Elliot Glendye",
        "creation_date": "2024-01-21",
        "last_update_date": "2025-01-03",
        "requirements": "",
        "category": "Business",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*'),
        "output_types": "all",
        "artifact_icon": "user"
    },
    "wireMessages": {
        "name": "Wire Secure Messenger Messages",
        "description": "Wire messages, including message sender, associated user identifiers and message type",
        "author": "Elliot Glendye",
        "creation_date": "2024-01-21",
        "last_update_date": "2025-01-03",
        "requirements": "",
        "category": "Business",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/AccountData/*/store/store.wiredatabase*'),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, does_column_exist_in_db, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def wireAccount(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "store.wiredatabase")
    data_list = []

    has_location_data = does_column_exist_in_db(source_path, 'ZUSER', 'ZUSERCLIENT.ZACTIVATIONLOCATIONLATITUDE')

    if has_location_data:
        query = '''
        SELECT
            DISTINCT ZUSER.ZHANDLE AS 'User ID',
            ZUSER.ZNAME AS 'Display Name',
            ZUSERCLIENT.ZACTIVATIONDATE AS 'Activation Date',
            ZUSER.ZPHONENUMBER AS 'Phone Number',
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
        query = '''
        SELECT
            DISTINCT ZUSER.ZHANDLE AS 'User ID',
            ZUSER.ZNAME AS 'Display Name',
            ZUSERCLIENT.ZACTIVATIONDATE AS 'Activation Date',
            ZUSER.ZPHONENUMBER AS 'Phone Number',
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
            data_list.append((record[0], record[1], activation_date, record[3], record[4], record[5], record[6]))
        else:
            data_list.append((record[0], record[1], activation_date, record[3], record[4]))
        
    return data_headers, data_list, source_path    
    
@artifact_processor
def wireMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "store.wiredatabase")
    data_list = []

    query = '''
    SELECT
        ZMESSAGE.ZSERVERTIMESTAMP AS 'Date / Time',
        ZUSER.ZHANDLE AS 'User ID',
        ZUSER.ZNAME AS 'Display Name',
        ZMESSAGE.ZNORMALIZEDTEXT AS 'Message',
        CASE ZMESSAGE.ZCACHEDCATEGORY
            WHEN 0 THEN 'Audio / Video Call'
            WHEN 2 THEN 'Text Message'
            WHEN 8 THEN 'Media Message'
            WHEN 256 THEN 'Location Message'
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
        data_list.append((date_time, record[1], record[2], record[3], record[4], record[5]))

    return data_headers, data_list, source_path