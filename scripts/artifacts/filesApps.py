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


from datetime import datetime
from scripts.builds_ids import OS_build
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_int_to_timezone, convert_ts_human_to_utc, convert_utc_human_to_timezone, convert_bytes_to_unit


def get_tree_structure(cursor):
    cursor.execute('''
    SELECT
    client_items.item_id,
    client_items.item_parent_id,
    client_items.item_filename
    FROM client_items
    WHERE client_items.item_type != 1
    ''')

    ts_all_rows = cursor.fetchall()
    ts_usageentries = len(ts_all_rows)
    ts_data_list = {}
    ts_paths = {}

    if ts_usageentries > 0:
        for ts_row in ts_all_rows:
            ts_id, ts_parent_id, ts_filename = ts_row
            ts_data_list[ts_id] = (ts_parent_id, ts_filename)

        for ts_key, ts_value in ts_data_list.items():
            ts_p_id, ts_path = ts_value
            while len(ts_p_id) == 16:
                ts_p_id, ts_name = ts_data_list[ts_p_id]
                ts_path = ts_name + "/" + ts_path
            ts_paths[ts_key] = f"{ts_path}/"
    
    return ts_paths


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
        data_headers = ('Application Bundle ID', 'Number of folders', 'Number of files', 'Total size in bytes', 'Total size' )     
        report.write_artifact_data_table(data_headers, app_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - iCloud Application List'
        tsv(report_folder, data_headers, app_data_list, tsvname)
    
    else:
        logfunc('No Application found in Files App')


    # Client Items
    cursor.execute('''
    SELECT
    app_libraries.app_library_name AS 'App Bundle ID',
    client_items.item_parent_id AS 'Parent ID',
    client_items.item_filename AS 'Filename',
    CASE client_items.item_hidden_ext
    WHEN 0 THEN 'No'
    WHEN 1 THEN 'Yes'
    END AS 'Hidden Extension',
    client_items.version_size AS 'Size',
    client_items.item_birthtime AS 'Created',
    client_items.version_mtime AS 'Modified',
    client_items.item_lastusedtime AS 'Last opened',
    client_items.version_device AS 'From Device',
    CASE
    WHEN client_items.item_sharing_options<=4 THEN 'No'
    ELSE 'Yes'
    END AS 'Is Shared?',
    item_recursive_properties.shared_by_me_count AS 'Shared by me',
    item_recursive_properties.shared_to_me_count AS 'Shared with me',
    CASE client_items.item_user_visible
    WHEN 0 THEN 'No'
    WHEN 1 THEN 'Yes'
    END AS 'Is Visible?'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
    LEFT JOIN item_recursive_properties ON client_items.rowid = item_recursive_properties.item_rowid
    ''')
    
    ci_all_rows = cursor.fetchall()
    ci_usageentries = len(ci_all_rows)
    ci_data_list = []
    shared_data_list = []
    
    
    if ci_usageentries > 0:
        ci_parents = get_tree_structure(cursor)

        for ci_row in ci_all_rows:
            ci_app_id, ci_parent_id, ci_filename, ci_ext, ci_size_in_bytes, ci_cdate, \
                ci_mdate, ci_lodate, ci_device, ci_shared, ci_shared_by_me, ci_shared_to_me, \
                ci_visible = ci_row
            
            ci_path = ''
            if len(ci_parent_id) == 16:
                ci_path = ci_parents.get(ci_parent_id, '')
            
            if not isinstance(ci_size_in_bytes, int):
                ci_path += f"{ci_filename}/"
                ci_filename = ""

            ci_size = ci_size_in_bytes
            if ci_size:
                ci_size = convert_bytes_to_unit(ci_size_in_bytes)
            
            ci_cdate = convert_ts_int_to_timezone(ci_cdate, timezone_offset) if ci_cdate else ''

            ci_mdate = convert_ts_int_to_timezone(ci_mdate, timezone_offset) if ci_mdate else ''

            ci_lodate = convert_ts_int_to_timezone(ci_lodate, timezone_offset) if ci_lodate else ''
            
            ci_data_list.append((ci_app_id, ci_path, ci_filename, ci_ext, ci_size_in_bytes, ci_size, 
                                 ci_cdate, ci_mdate, ci_lodate, ci_device, ci_shared, ci_visible))
            
        description = '	Files stored in iCloud Drive with their metadata. '
        report = ArtifactHtmlReport('Files App - Files stored in iCloud')
        report.start_artifact_report(report_folder, 'Files App - Files stored in iCloud', description)
        report.add_script()
        data_headers = ('Application Bundle ID', 'Path', 'Filename', 'Hidden extension', 'Size in bytes', 
                        'Size', 'Created', 'Modified', 'Last opened', 'Device', 'Shared?', 'Visible?')     
        report.write_artifact_data_table(data_headers, ci_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - Files stored in iCloud'
        tsv(report_folder, data_headers, ci_data_list, tsvname)
    
        tlactivity = 'Files App - Files stored in iCloud'
        timeline(report_folder, tlactivity, ci_data_list, data_headers)
    
    else:
        logfunc('No file found in Files App')


    # iOS Updated
    cursor.execute('''
    SELECT
    boot_history.date,
    boot_history.os
    FROM boot_history
    ''')
    
    os_all_rows = cursor.fetchall()
    os_usageentries = len(os_all_rows)
    os_data_list = []

    if os_usageentries > 0:
        for os_row in os_all_rows:
            os_date, os_os  = os_row

            os_date = convert_ts_int_to_timezone(os_date, timezone_offset) if os_date else ''

            os_version = OS_build.get(os_os, '')

            os_data_list.append((os_date, os_os, os_version))
            
        description = '	Operating System Updates '
        report = ArtifactHtmlReport('Files App - Operating System Updates')
        report.start_artifact_report(report_folder, 'Files App - Operating System Updates', description)
        report.add_script()
        data_headers = ('Date and Time', 'OS Build', 'OS Version')     
        report.write_artifact_data_table(data_headers, os_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - Operating System Updates'
        tsv(report_folder, data_headers, os_data_list, tsvname)

        tlactivity = 'Files App - Operating System Updates'
        timeline(report_folder, tlactivity, ci_data_list, data_headers)

    
    else:
        logfunc('No Operating System Update found in Files App')


def get_filesApp(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('client.db'):
            get_filesApp_client(file_found, timezone_offset, report_folder)
