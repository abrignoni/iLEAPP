# Photos.sqlite Migrations - UserEventAgent
# Author:  John Hyla
# Version: 1.0.0
#
#   Description:
#   Parses migration records found in the Photos.sqlite database. May assist in determining history of iOS versions history
#   Based on SQL Queries written by Scott Koenig https://theforensicscooter.com/
#   https://github.com/ScottKjr3347/iOS_Local_PL_Photos.sqlite_Queries/blob/main/iOS16/iOS16_LPL_Phsql_MigrationHistory.txt
#


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, generate_thumbnail, \
    open_sqlite_db_readonly


def get_photosMigration(files_found, report_folder, seeker, wrap_text):
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
          CASE zMigrationHistory.ZOSVERSION
            WHEN '15A372' THEN '15A372-11'
            WHEN '15A402' THEN '15A402-11.0.1'
            WHEN '15A403' THEN '15A403-11.0.1'
            WHEN '15A8391' THEN '15A8391-11.0.1'
            WHEN '15A421' THEN '15A421-11.0.2'
            WHEN '15A432' THEN '15A432-11.0.3'
            WHEN '15B93' THEN '15B93-11.1'
            WHEN '15B101' THEN '15B101-11.1'
            WHEN '15B150' THEN '15B150-11.1.1'
            WHEN '15B202' THEN '15B202-11.1.2'
            WHEN '15C114' THEN '15C114-11.2'
            WHEN '15C153' THEN '15C153-11.2.1'
            WHEN '15C202' THEN '15C202-11.2.2'
            WHEN '15D60' THEN '15D60-11.2.5'
            WHEN '15D100' THEN '15D100-11.2.6'
            WHEN '15E216' THEN '15E216-11.3'
            WHEN '15E218' THEN '15E218-11.3'
            WHEN '15E302' THEN '15E302-11.3.1'
            WHEN '15F79' THEN '15F79-11.4'
            WHEN '15G77' THEN '15G77-11.4.1'
            WHEN '16A366' THEN '16A366-12'
            WHEN '16A366' THEN '16A366-12'
            WHEN '16A366' THEN '16A366-12'
            WHEN '16A404' THEN '16A404-12.0.1'
            WHEN '16A405' THEN '16A405-12.0.1'
            WHEN '16B92' THEN '16B92-12.1'
            WHEN '16B93' THEN '16B93-12.1'
            WHEN '16B94' THEN '16B94-12.1'
            WHEN '16C50' THEN '16C50-12.1.1'
            WHEN '16C104' THEN '16C104-12.1.2'
            WHEN '16D39' THEN '16D39-12.1.3'
            WHEN '16D40' THEN '16D40-12.1.3'
            WHEN '16D57' THEN '16D57-12.1.4'
            WHEN '16E227' THEN '16E227-12.2'
            WHEN '16F156' THEN '16F156-12.3'
            WHEN '16F203' THEN '16F203-12.3.1'
            WHEN '16F8202' THEN '16F8202-12.3.1'
            WHEN '16F250' THEN '16F250-12.3.2'
            WHEN '16G77' THEN '16G77-12.4'
            WHEN '16G102' THEN '16G102-12.4.1'
            WHEN '16G114' THEN '16G114-12.4.2'
            WHEN '16G130' THEN '16G130-12.4.3'
            WHEN '16G140' THEN '16G140-12.4.4'
            WHEN '16G161' THEN '16G161-12.4.5'
            WHEN '16G183' THEN '16G183-12.4.6'
            WHEN '16G192' THEN '16G192-12.4.7'
            WHEN '16G201' THEN '16G201-12.4.8'
            WHEN '16H5' THEN '16H5-12.4.9'
            WHEN '16H20' THEN '16H20-12.5'
            WHEN '16H22' THEN '16H22-12.5.1'
            WHEN '16H30' THEN '16H30-12.5.2'
            WHEN '16H41' THEN '16H41-12.5.3'
            WHEN '16H50' THEN '16H50-12.5.4'
            WHEN '16H62' THEN '16H62-12.5.5'
            WHEN '16H71' THEN '16H71-12.5.6'
            WHEN '17A577' THEN '17A577-13'
            WHEN '17A844' THEN '17A844-13.1'
            WHEN '17A854' THEN '17A854-13.1.1'
            WHEN '17A860' THEN '17A860-13.1.2'
            WHEN '17A861' THEN '17A861-13.1.2'
            WHEN '17A878' THEN '17A878-13.1.3'
            WHEN '17B84' THEN '17B84-13.2'
            WHEN '17B90' THEN '17B90-13.2.1'
            WHEN '17B102' THEN '17B102-13.2.2'
            WHEN '17B111' THEN '17B111-13.2.3'
            WHEN '17C54' THEN '17C54-13.3'
            WHEN '17D50' THEN '17D50-13.3.1'
            WHEN '17E255' THEN '17E255-13.4'
            WHEN '17E8255' THEN '17E8255-13.4'
            WHEN '17E262' THEN '17E262-13.4.1'
            WHEN '17E8258' THEN '17E8258-13.4.1'
            WHEN '17F75' THEN '17F75-13.5'
            WHEN '17F80' THEN '17F80-13.5.1'
            WHEN '17G68' THEN '17G68-13.6'
            WHEN '17G80' THEN '17G80-13.6.1'
            WHEN '17H35' THEN '17H35-13.7'
            WHEN '18A373' THEN '18A373-14'
            WHEN '18A393' THEN '18A393-14.0.1'
            WHEN '18A8395' THEN '18A8395-14.1'
            WHEN '18B92' THEN '18B92-14.2'
            WHEN '18B111' THEN '18B111-14.2'
            WHEN '18B121' THEN '18B121-14.2.1'
            WHEN '18C66' THEN '18C66-14.3'
            WHEN '18D52' THEN '18D52-14.4'
            WHEN '18D61' THEN '18D61-14.4.1'
            WHEN '18D70' THEN '18D70-14.4.2'
            WHEN '18E199' THEN '18E199-14.5'
            WHEN '18E212' THEN '18E212-14.5.1'
            WHEN '18F72' THEN '18F72-14.6'
            WHEN '18G69' THEN '18G69-14.7'
            WHEN '18G70' THEN '18G70-14.7'
            WHEN '18G82' THEN '18G82-14.7.1'
            WHEN '18H17' THEN '18H17-14.8'
            WHEN '18H107' THEN '18H107-14.8.1'
            WHEN '19A346' THEN '19A346-15'
            WHEN '19A348' THEN '19A348-15.0.1'
            WHEN '19A404' THEN '19A404-15.0.2'
            WHEN '19B74' THEN '19B74-15.1'
            WHEN '19B75' THEN '19B75-15.1'
            WHEN '19B81' THEN '19B81-15.1.1'
            WHEN '19C56' THEN '19C56-15.2'
            WHEN '19C57' THEN '19C57-15.2'
            WHEN '19C63' THEN '19C63-15.2.1'
            WHEN '19D50' THEN '19D50-15.3'
            WHEN '19D52' THEN '19D52-15.3.1'
            WHEN '19E241' THEN '19E241-15.4'
            WHEN '19E258' THEN '19E258-15.4.1'
            WHEN '19F77' THEN '19F77-15.5'
            WHEN '19G71' THEN '19G71-15.6'
            WHEN '19G82' THEN '19G82-15.6.1'
            WHEN '19H12' THEN '19H12-15.7'
            WHEN '19H117' THEN '19H117-15.7.1'
            WHEN '20A362' THEN '20A362-16'
            WHEN '20A371' THEN '20A371-16.0.1'
            WHEN '20A380' THEN '20A380-16.0.2'
            WHEN '20A392' THEN '20A392-16.0.3'
            WHEN '20B82' THEN '20B82-16.1'
            WHEN '20B101' THEN '20B101-16.1.1'
            WHEN '20B110' THEN '20B110-16.1.2'
            WHEN '20C5032e' THEN '20C5032e-16.2 Beta 1'
            WHEN '20C65' THEN '20C65-16.2'
            WHEN '20D5024e' THEN '20D5024e-16.3 Beta'
            ELSE 'Unknown-New-Value!: ' || zMigrationHistory.ZOSVERSION || ''
          END AS 'zMigrationHistory-Build-and-Version',
          zMigrationHistory.ZORIGIN AS 'zMigrationHistory-Origin',
          zMigrationHistory.ZSTOREUUID AS 'zMigrationHistory-Store UUID',
          zMigrationHistory.ZGLOBALKEYVALUES AS 'zMigrationHistory-Global Key Values/HEX'
        FROM ZMIGRATIONHISTORY zMigrationHistory
        ORDER BY zMigrationHistory.ZMIGRATIONDATE

    """)
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    counter = 0
    if usageentries > 0:
        for row in all_rows:



            data_list.append((row[3], row[4], row[5], row[6], row[7], row[8], row[10], row[11], row[12]))

            counter += 1

        description = ''
        report = ArtifactHtmlReport('Photos.sqlite Migrations')
        report.start_artifact_report(report_folder, 'Migrations', description)
        report.add_script()
        data_headers = ('Date', 'Index', 'Type', 'Force Rebuild Reason', 'Source Model Version', 'Model Version', 'Build/iOS Version', 'Origin', 'Store UUID')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Photos-sqlite Migrations'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Photos-sqlite Migrations'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No data available for Photos.sqlite metadata')

    db.close()
    return



__artifacts__ = {
    "photosMigration": (
        "Photos",
        ('**/Photos.sqlite*'),
        get_photosMigration)
}