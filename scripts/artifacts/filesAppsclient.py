__artifacts_v2__ = {
    "filesappsclient": {
        "name": "Files App Client",
        "description": "Items stored in iCloud Drive.",
        "author": "@AlexisBrignoni",
        "version": "0.1",
        "date": "2023-01-01",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',),
        "function": "get_filesAppsclient"
    }
}


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_filesAppsclient(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('client.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(item_birthtime, 'unixepoch'),
    item_filename,
    datetime(version_mtime, 'unixepoch')
    FROM
    client_items
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    if usageentries > 0:
        for row in all_rows:
            birthtime = convert_ts_human_to_utc(row[0])
            birthtime = convert_utc_human_to_timezone(birthtime, timezone_offset)
            
            versionmtime = convert_ts_human_to_utc(row[2])
            versionmtime = convert_utc_human_to_timezone(versionmtime, timezone_offset)
            
            data_list.append((birthtime, row[1], versionmtime))
            
        description = '	Items stored in iCloud Drive with metadata about files. '
        report = ArtifactHtmlReport('Files App - iCloud Client Items')
        report.start_artifact_report(report_folder, 'Files App - iCloud Client Items', description)
        report.add_script()
        data_headers = ('Birthtime', 'Filename', 'Version Modified Time' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - iCloud Client Items'
        tsv(report_folder, data_headers, data_list, tsvname)
    
        tlactivity = 'Files App - iCloud Client Items'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Files App - iCloud Client Items data available')

