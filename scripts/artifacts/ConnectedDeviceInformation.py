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
        "artifact_icon": "smartphone"
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
        "artifact_icon": "smartphone"
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
        "artifact_icon": "smartphone"
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
        device_model = context.get_device_model(record[2])
        os_version = context.get_os_version(record[4], record[2])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], device_model,
             record[3], record[4], os_version))

    return data_headers, data_list, source_path


import sqlite3 # <--- PENTING: Tambahkan ini di bagian paling atas file jika belum ada

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
    LEFT OUTER JOIN data_provenances ON objects.provenance 
        = data_provenances.ROWID
    WHERE data_provenances.origin_product_type != "iPhone0,0" AND 
        data_provenances.origin_product_type != "UnknownDevice"
    AND objects.creation_date > 0
    GROUP BY origin_product_type, origin_build
    HAVING MIN(objects.creation_date) != MAX(objects.creation_date)
    ORDER BY creation_date;
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'),
        'Origin Product Type', 'Device Model', 'Source ID', 'Origin Build',
        'OS Version')

    # --- BAGIAN PERBAIKAN (BUG FIX) ---
    try:
        # Coba buka database dan jalankan query
        db_records = get_sqlite_db_records(source_path, query)
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        # Jika gagal (file corrupt/bukan DB), catat error dan kembalikan data kosong
        # logfunc adalah fungsi bawaan iLEAPP untuk logging, atau gunakan print biasa
        print(f" [!] Error: Gagal membaca database {source_path}. Kemungkinan file rusak atau bukan SQLite. Detail: {e}")
        return data_headers, [], source_path 
    # ----------------------------------

    # Jika berhasil (masuk blok ini), proses datanya
    if db_records:
        for record in db_records:
            start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
            end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
            device_model = context.get_device_model(record[2])
            os_version = context.get_os_version(record[4], record[2])
            data_list.append(
                (start_timestamp, end_timestamp, record[2], device_model,
                 record[3], record[4], os_version))

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
            device_model = context.get_device_model(record[1])
            data_list.append(
                (mod_timestamp, record[1], device_model, record[2]))

    return data_headers, data_list, source_path
