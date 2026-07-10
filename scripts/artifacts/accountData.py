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
        'artifact_icon': 'user',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 14 rows',
            'dexter_ios18': 'iOS 18.3.2 | 20 rows',
            'felix_ios17': 'iOS 17.6.1 | 17 rows',
            'fsfull002_ios17': 'iOS 17.1 | 15 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 15 rows',
            'iphone11_ios17': 'iOS 17.3 | 19 rows',
            'iphone12_ios18': 'iOS 18.7 | 16 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 16 rows',
            'otto_ios17': 'iOS 17.5.1 | 19 rows',
        }
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
