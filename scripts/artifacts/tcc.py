# pylint: disable=W0613
__artifacts_v2__ = {
    'tcc': {
        'name': 'Application Permissions',
        'description': 'Extract application permissions from TCC.db database',
        'author': '@AlexisBrignoni - @KevinPagano3 - @johannplw',
        'creation_date': '2020-12-15',
        'last_update_date': '2025-04-07',
        'requirements': 'none',
        'category': 'App Permissions',
        'notes': '',
        'paths': ('*/mobile/Library/TCC/TCC.db*','*/logs/Accessibility/TCC.db*'),
        'output_types': 'standard',
        'artifact_icon': 'key',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 46 rows',
            'dexter_ios18': 'iOS 18.3.2 | 141 rows',
            'felix_ios17': 'iOS 17.6.1 | 118 rows',
            'fsfull002_ios17': 'iOS 17.1 | 121 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 109 rows',
            'iphone11_ios17': 'iOS 17.3 | 289 rows',
            'iphone12_ios18': 'iOS 18.7 | 143 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 69 rows',
            'otto_ios17': 'iOS 17.5.1 | 185 rows',
            'abe_ios16': 'iOS 16.5 | 184 rows',
            'felix23_ios16': 'iOS 16.5 | 127 rows',
            'hickman_ios13': 'iOS 13.3.1 | 130 rows',
            'hickman_ios14': 'iOS 14.3 | 154 rows',
            'jess_ios15': 'iOS 15.0.2 | 76 rows',
            'magnet_ios16': 'iOS 16.1.1 | 66 rows',
        }
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, does_column_exist_in_db, \
    convert_unix_ts_to_utc


@artifact_processor
def tcc(context):
    source_path = get_file_path(context.get_files_found(), 'TCC.db')
    data_list = []

    last_modified_timestamp_exists = does_column_exist_in_db(
        source_path, 'access', 'last_modified')

    if does_column_exist_in_db(source_path, 'access', 'auth_value'):
        access = '''
        case auth_value
            when 0 then 'Not allowed'
            when 2 then 'Allowed'
            when 3 then 'Limited'
            else auth_value
        end as 'Access'
        '''
    else:
        access = '''
        case allowed
            when 0 then 'Not allowed'
            when 1 then 'Allowed'
            else allowed
        end as 'Access'
        '''

    prompt_count_exists = does_column_exist_in_db(
        source_path, 'access', 'prompt_count')

    query = f'''
    SELECT
        {'last_modified,' if last_modified_timestamp_exists else ''}
        client,
        service,
        {access}
        {',prompt_count' if prompt_count_exists else ''}
    FROM access
    ORDER BY client
    '''

    if last_modified_timestamp_exists:
        data_headers = (
            ('Last Modified Timestamp', 'datetime'),
            'Bundle ID',
            'Service',
            'Access')
    else:
        data_headers = ('Bundle ID', 'Service', 'Access', 'Prompt Count')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        if last_modified_timestamp_exists:
            last_modified_timestamp = convert_unix_ts_to_utc(
                record['last_modified'])
            data_list.append(
                (last_modified_timestamp, record[1],
                 record[2].replace('kTCCService', ''), record[3]))
        else:
            data_list.append((record[1], record[2].replace('kTCCService', ''),
                              record[3], record[4]))

    return data_headers, data_list, source_path
