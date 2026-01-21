__artifacts_v2__ = {
    'tileAppNetDb': {
        'name': 'Tile App Account Information',
        'description': '',
        'author': '@AlexisBrignoni',
        'creation_date': '2020-09-03',
        'last_update_date': '2025-04-05',
        'requirements': 'none',
        'category': 'Tile App',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*', ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc


@artifact_processor
def tileAppNetDb(context):
    files_found = context.get_files_found()
    source_path = get_file_path(
        files_found, 'com.thetileapp.tile-TileNetworkDB.sqlite')
    data_list = []

    query = '''
    SELECT
        ZREGISTRATION_TIMESTAMP, 
        ZEMAIL,
        ZFULL_NAME,
        ZMOBILE_PHONE
    FROM ZTILENTITY_USER
    '''

    data_headers = (
        ('Registration Timestamp', 'datetime'),
        'Email',
        'Full Name',
        ('Mobile Phone Number', 'phonenumber'))

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        registration_timestamp = convert_cocoa_core_data_ts_to_utc(
            record['ZREGISTRATION_TIMESTAMP'])
        data_list.append(
            (registration_timestamp, record[1], record[2], record[3]))

    return data_headers, data_list, source_path
