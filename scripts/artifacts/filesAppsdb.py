__artifacts_v2__ = {
    "filesappsdb": {
        "name": "Files App Db",
        "description": "Items stored in iCloud Drive.",
        "author": "@AlexisBrignoni",
        "version": "0.1",
        "date": "2023-01-01",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',),
        "function": "get_filesAppsdb"
    }
}


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_filesAppsdb(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('server.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT * 
    FROM
    DEVICES
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    if usageentries > 0:

        for row in all_rows:
            data_list.append((row[1],))
            
        description = 'Device names that are able to sync to iCloud Drive.'
        report = ArtifactHtmlReport('Files App - iCloud Sync Names')
        report.start_artifact_report(report_folder, 'Files App - iCloud Sync Names', description)
        report.add_script()
        data_headers = ('Name', )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - iCloud Sync Names'
        tsv(report_folder, data_headers, data_list, tsvname)
    
    else:
        logfunc('No Files App - iCloud Sync Names data available')
    
    
    cursor.execute('''
    SELECT
    datetime(item_birthtime, 'unixepoch'),
    item_filename,
    datetime(version_mtime, 'unixepoch')
    FROM
    server_items
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    if usageentries > 0:
        for row in all_rows:
            birthtime = convert_ts_human_to_utc(row[0])
            birthtime = convert_utc_human_to_timezone(birthtime,timezone_offset)

            versionmtime = convert_ts_human_to_utc(row[2])
            versionmtime = convert_utc_human_to_timezone(versionmtime,timezone_offset)

            data_list.append((birthtime, row[1], versionmtime))
            
        description = ''
        report = ArtifactHtmlReport('Files App - iCloud Server Items')
        report.start_artifact_report(report_folder, 'Files App - iCloud Server Items', description)
        report.add_script()
        data_headers = ('Birthtime', 'Filename', 'Version Modified Time' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - iCloud Server Items'
        tsv(report_folder, data_headers, data_list, tsvname)
    
        tlactivity = 'Files App - iCloud Server Items'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Files App - iCloud Server Items data available')
    
