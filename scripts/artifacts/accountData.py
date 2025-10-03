__artifacts_v2__ = {
    'accountData': {
        'name': 'Account Data',
        'description': 'Configured user accounts',
        'author': '@AlexisBrignoni',
        'creation_date': '2020-04-30',
        "last_update_date": "2025-10-03",
        'requirements': 'none',
        'category': 'Accounts',
        'notes': '',
        'paths': ('*/mobile/Library/Accounts/Accounts3.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def accountData(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Accounts3.sqlite')
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

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        timestamp = convert_cocoa_core_data_ts_to_utc(record['zdate'])
        data_list.append(
            (timestamp, record[1], record[2], record[3], record[4], record[5]))

    return data_headers, data_list, source_path
