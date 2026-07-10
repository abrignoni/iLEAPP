"""
This module extracts and processes historical information about connected
devices from the `healthdb_secure.sqlite` database, and consolidates device
connection history.
It also extracts current connected device information from 'healthdb.sqlite'.
"""

__artifacts_v2__ = {
    "connected_device_info_device_history": {
        "name": "Connected Device Information - Connected Device and \
OS History",
        "description": "Connected Devices",
        "author": "@SQLMcGee",
        'creation_date': '2025-01-30',
        'last_update_date': '2025-09-29',
        "requirements": "none",
        "category": "Device Information",
        "notes": "Queries from research conducted by Metadata Forensics, LLC \
Apple product identification, common name, OS, and timeframe of use",
        "paths": ('*Health/healthdb_secure.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | 13 rows",
            "fsfull002_ios17": "iOS 17.1 | 8 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 15 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 5 rows",
        }
    },
    "connected_device_info_consolidated_connected_device_history": {
        "name": "Connected Device Information - Consolidated Connected Device \
History",
        "description": "Connected Devices",
        "author": "@SQLMcGee",
        'creation_date': '2025-01-30',
        'last_update_date': '2025-09-29',
        "requirements": "none",
        "category": "Device Information",
        "notes": "Queries from research conducted by Metadata Forensics, LLC \
Apple product grouped for starting and ending timeframe of use",
        "paths": ('*Health/healthdb_secure.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
        }
    },
    "connected_device_information_current_device_info": {
        "name": "Connected Device Information - Current Device Information",
        "description": "Connected Devices",
        "author": "@SQLMcGee",
        'creation_date': '2025-01-30',
        'last_update_date': '2025-09-29',
        "requirements": "none",
        "category": "Device Information",
        "notes": "Queries from reserach conducted by Metadata Forensics, LLC \
Current Apple Device and OS Information",
        "paths": ('*Health/healthdb.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 1 row",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, does_table_exist_in_db, \
    convert_cocoa_core_data_ts_to_utc


@artifact_processor
def connected_device_info_device_history(context):
    """
    Extracts and processes historical information about connected devices from
    the `healthdb_secure.sqlite` database.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        MIN(objects.creation_date),
        MAX(objects.creation_date),
        data_provenances.origin_product_type,
        source_id,
        data_provenances.origin_build
    FROM objects
    LEFT OUTER JOIN data_provenances ON objects.provenance ''' +\
        '''= data_provenances.ROWID
    WHERE data_provenances.origin_product_type != "iPhone0,0" AND ''' +\
        '''data_provenances.origin_product_type != "UnknownDevice"
    AND objects.creation_date > 0
    GROUP BY origin_product_type, origin_build
    HAVING MIN(objects.creation_date) != MAX(objects.creation_date)
    ORDER BY creation_date;
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'),
        'Origin Product Type', 'Device Model', 'Source ID', 'Origin Build',
        'OS Version')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        device_model = context.lookup_metadata('apple_device_id_to_model', record[2])
        os_version = context.get_apple_os_version(record[4], record[2])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], device_model,
             record[3], record[4], os_version))

    return data_headers, data_list, source_path


@artifact_processor
def connected_device_info_consolidated_connected_device_history(context):
    """
    Extracts and consolidates device connection history from
    'healthdb_secure.sqlite'.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        MIN(objects.creation_date),
        MAX(objects.creation_date),
        data_provenances.origin_product_type
    FROM objects
    LEFT OUTER JOIN data_provenances ON objects.provenance = ''' +\
        '''data_provenances.ROWID
    WHERE data_provenances.origin_product_type != "UnknownDevice" and ''' +\
        '''data_provenances.origin_product_type != "iPhone0,0" AND ''' +\
        '''objects.creation_date > 1
    GROUP BY data_provenances.origin_product_type
    ORDER BY creation_date;
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'),
        'Origin Product Type', 'Device Model')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        device_model = context.lookup_metadata('apple_device_id_to_model', record[2])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], device_model))

    return data_headers, data_list, source_path


@artifact_processor
def connected_device_information_current_device_info(context):
    """
    Extracts current connected device information from 'healthdb.sqlite'.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'healthdb.sqlite')
    data_list = []

    query = '''
    SELECT
        device_context.date_modified,
        device_context.product_type_name,
        device_context.currentOS_name || " " || ''' +\
            '''device_context.currentOS_version As "OS Version"
    From device_context;
    '''

    data_headers = (
        ('Modified Time', 'datetime'), 'Origin Product Type', 'Device Model',
        'OS Version')

    if does_table_exist_in_db(source_path, 'device_context'):
        db_records = get_sqlite_db_records(source_path, query)
        for record in db_records:
            mod_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
            device_model = context.lookup_metadata('apple_device_id_to_model', record[1])
            data_list.append(
                (mod_timestamp, record[1], device_model, record[2]))

    return data_headers, data_list, source_path
