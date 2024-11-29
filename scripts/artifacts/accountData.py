__artifacts_v2__ = {
    "accountData": {
        "name": "Account Data",
        "description": "Configured user accounts",
        "author": "@AlexisBrignoni",
        "version": "0.4.3",
        "date": "2020-04-30",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/mobile/Library/Accounts/Accounts3.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "user"
    }
}


from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def accountData(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_file = get_file_path(files_found, "Accounts.sqlite")
    data_list = []

    query = '''
    SELECT
        zdate,
        zaccounttypedescription,
        zusername,
        zaccountdescription,
        zaccount.zidentifier,
        zaccount.zowningbundleid
    FROM zaccount, zaccounttype 
    WHERE zaccounttype.z_pk=zaccount.zaccounttype
    '''

    data_headers = (
        ('Timestamp', 'datetime'), 
        'Account Desc.', 
        'Username', 
        'Description', 
        'Identifier', 
        'Bundle ID'
        )

    db_records = get_sqlite_db_records(db_file, query)
    
    for record in db_records:
        timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((timestamp, record[1], record[2], record[3], record[4], record[5]))                

    return data_headers, data_list, db_file
