__artifacts_v2__ = {
    "get_photosMigration": {
        "name": "Migrations",
        "description": "Parses migration records from photos.sqlite database",
        "author": "@JohnHyla",
        "version": "1.0.1",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Photos",
        "notes": "Parses migration records found in the Photos.sqlite database. May assist in determining history of "
                 "iOS versions history Based on SQL Queries written by Scott Koenig https://theforensicscooter.com/",
        "paths": ('*/PhotoData/Photos.sqlite*'),
        "output_types": "standard"
    }
}

from scripts.ilapfuncs import convert_ts_human_to_utc, convert_utc_human_to_timezone, open_sqlite_db_readonly, artifact_processor
from scripts.builds_ids import OS_build

@artifact_processor
def get_photosMigration(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute("""
        SELECT zMigrationHistory.Z_PK AS 'zMigrationHistory-zPK',
          zMigrationHistory.Z_ENT AS 'zMigrationHistory-zENT',
          zMigrationHistory.Z_OPT AS 'zMigrationHistory-zOPT',
          DateTime(zMigrationHistory.ZMIGRATIONDATE + 978307200, 'UNIXEPOCH') AS 'zMigrationHistory-Migration Date',
          zMigrationHistory.ZINDEX AS 'zMigrationHistory-Index',
          CASE zMigrationHistory.ZMIGRATIONTYPE
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-iOS Update-2'
            WHEN 3 THEN '3-iOS History Start/Factory Reset-3'
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
    """)

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        ios_version = row[9] + ' - ' + OS_build[row[9]]
        timestamp = convert_ts_human_to_utc(row[3])
        timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)

        data_list.append((timestamp, row[4], row[5], row[6], row[7], row[8], ios_version, row[10], row[11]))

    db.close()

    data_headers = (('Timestamp', 'datetime'), 'Migration Index', 'Type', 'Force Rebuild Reason', 'Source Model Version',
                    'Model Version', 'Build/iOS Version', 'Origin', 'Store UUID')

    return data_headers, data_list, file_found
