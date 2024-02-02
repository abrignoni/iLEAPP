__artifacts_v2__ = {
    "filesapp": {
        "name": "Files App",
        "description": "Items stored in iCloud Drive.",
        "author": "@AlexisBrignoni - @JohannPLW",
        "version": "0.2",
        "date": "2024-01-27",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',),
        "function": "get_filesApp"
    }
}


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, convert_bytes_to_unit


def get_filesApp_client(file_found, timezone_offset, report_folder):
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    # Applications
    cursor.execute('''
    SELECT 
    app_libraries.app_library_name AS 'App Bundle ID',
    app_libraries.auto_client_item_count - app_libraries.auto_document_count AS 'Number of folders',
    app_libraries.auto_document_count AS 'Number of files',
    app_libraries.auto_aggregate_size AS 'Total size'
    FROM app_libraries
    ''')
    
    app_all_rows = cursor.fetchall()
    app_usageentries = len(app_all_rows)
    app_data_list = []

    if app_usageentries > 0:
        for app_row in app_all_rows:
            app_id, app_folders, app_files, app_size_in_bytes = app_row
            app_size = app_size_in_bytes
            if app_size:
                app_size = convert_bytes_to_unit(app_size_in_bytes)

            app_data_list.append((app_id, app_folders, app_files, app_size_in_bytes, app_size))
            
        description = '	List of applications that synchronize data in iCloud '
        report = ArtifactHtmlReport('Files App - iCloud Application List')
        report.start_artifact_report(report_folder, 'Files App - iCloud Application List', description)
        report.add_script()
        data_headers = ('Application Bundle ID', 'Number of folders', 'Number of files', 'Size in bytes', 'Total size' )     
        report.write_artifact_data_table(data_headers, app_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - iCloud Application List'
        tsv(report_folder, data_headers, app_data_list, tsvname)
    
    else:
        logfunc('No Application in Files App data available')


def get_filesApp(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('client.db'):
            get_filesApp_client(file_found, timezone_offset, report_folder)
