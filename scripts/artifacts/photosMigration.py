""" See notes below """

__artifacts_v2__ = {
    "photos_migration": {
        "name": "Migrations",
        "description": "Parses migration records from photos.sqlite database",
        "author": "@JohnHyla",
        'creation_date': '2023-08-01',
        'last_update_date': '2025-10-07',
        "requirements": "none",
        "category": "OS Updates",
        "notes": "Parses migration records found in the Photos.sqlite database. May assist in determining history of "
                 "iOS versions history Based on SQL Queries written by Scott Koenig https://theforensicscooter.com/",
        "paths": ('*/PhotoData/Photos.sqlite*',),
        "output_types": "standard",
        'artifact_icon': "chevrons-up"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc


@artifact_processor
def photos_migration(context):
    """ See artifact description """
    data_source = get_file_path(context.get_files_found(), "Photos.sqlite")
    data_list = []

    query = """
        SELECT zMigrationHistory.Z_PK AS 'zMigrationHistory-zPK',
          zMigrationHistory.Z_ENT AS 'zMigrationHistory-zENT',
          zMigrationHistory.Z_OPT AS 'zMigrationHistory-zOPT',
          zMigrationHistory.ZMIGRATIONDATE,
          zMigrationHistory.ZINDEX AS 'zMigrationHistory-Index',
          CASE zMigrationHistory.ZMIGRATIONTYPE
            WHEN 0 THEN '0 - StillTesting'
            WHEN 1 THEN '1 - StillTesting'
            WHEN 2 THEN '2 - OS Update'
            WHEN 3 THEN '3 - OS History Start/Factory Reset'
            ELSE 'Unknown-New-Value!: ' || zMigrationHistory.ZMIGRATIONTYPE || ''
          END AS 'zMigrationHistory-Migration Type',
          zMigrationHistory.ZFORCEREBUILDREASON AS 'zMigrationHistory-Force Rebuild Reason',
          zMigrationHistory.ZSOURCEMODELVERSION AS 'zMigrationHistory-Source Model Version',
          zMigrationHistory.ZMODELVERSION AS 'zMigrationHistory-Model Version',
          zMigrationHistory.ZOSVERSION AS 'zMigrationHistory-OSVersion-BuildfromDB',
          zMigrationHistory.ZORIGIN AS 'zMigrationHistory-Origin',
          zMigrationHistory.ZSTOREUUID AS 'zMigrationHistory-Store UUID',
          zMigrationHistory.ZGLOBALKEYVALUES AS 'zMigrationHistory-Global Key Values/HEX'
        FROM ZMIGRATIONHISTORY zMigrationHistory
        ORDER BY zMigrationHistory.ZMIGRATIONDATE
    """

    data_headers = (
        ('Timestamp', 'datetime'), 'Migration Index', 'Type', 'Force Rebuild Reason',
        'Source Model Version', 'Model Version', 'OS Build', 'OS Version', 'Origin',
        'Store UUID')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        os_version = context.get_os_version(record[9])
        timestamp = convert_cocoa_core_data_ts_to_utc(record[3])

        data_list.append((timestamp, record[4], record[5], record[6], record[7],
                          record[8], record[9], os_version, record[10], record[11]))

    return data_headers, data_list, data_source
