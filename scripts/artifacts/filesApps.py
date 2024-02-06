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
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',
            ),
        "function": "get_filesApp"
    }
}


import nska_deserialize as nd

from scripts.builds_ids import OS_build
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_bytes_to_unit, convert_ts_int_to_timezone


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
    ts_data_dict = {}
    ts_paths = {}

    if ts_usageentries > 0:
        for ts_row in ts_all_rows:
            ts_id, ts_parent_id, ts_filename = ts_row
            ts_data_dict[ts_id] = (ts_parent_id, ts_filename)

        for ts_key, ts_value in ts_data_dict.items():
            ts_p_id, ts_path = ts_value
            while len(ts_p_id) == 16:
                ts_p_id, ts_name = ts_data_dict[ts_p_id]
                ts_path = ts_name + "/" + ts_path
            ts_paths[ts_key] = f"{ts_path}/"
    
    return ts_paths


def get_filesApps_server(file_found, report_folder):
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    # Devices able to sync
    cursor.execute('''
    SELECT
    devices.key,
    devices.name
    FROM devices
    ''')

    devices_all_rows = cursor.fetchall()
    devices_usageentries = len(devices_all_rows)
    devices_data_list = []
    devices_dict = {}

    if devices_usageentries > 0:
        for devices_row in devices_all_rows:
            device_key, device_name = devices_row

            devices_data_list.append((device_key, device_name))
            devices_dict[device_key] = device_name
            
        description = 'Device names that are able to sync to iCloud Drive.'
        report = ArtifactHtmlReport('iCloud Sync Device Names')
        report.start_artifact_report(report_folder, 'Files App - iCloud Sync Device Names', description)
        report.add_script()
        devices_data_headers = ('#', 'Device Name')     
        report.write_artifact_data_table(devices_data_headers, devices_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - iCloud Sync Device Names'
        tsv(report_folder, devices_data_headers, devices_data_list, tsvname)
    
    else:
        logfunc('No iCloud sync device names data available in Files App')
    
    # Users
    cursor.execute('''
    SELECT
    users.user_key,
    users.user_plist
    FROM users
    ''')

    users_all_rows = cursor.fetchall()
    users_usageentries = len(users_all_rows)
    users_data_dict = {}

    if users_usageentries > 0:
        for users_row in users_all_rows:
            user_key, user_plist = users_row

            user_fullName = ''
            if user_plist:
                deserialized_users_plist = nd.deserialize_plist_from_string(user_plist[3:])
                user_plist_dict = deserialized_users_plist
                user = user_plist_dict.get('NS.nameComponentsPrivate')
                if user:
                    user_givenName = user.get('NS.givenName', '')
                    user_familyName = user.get('NS.familyName', '')
                    user_fullName = f"{user_givenName + ' ' if user_givenName else ''}{user_familyName}"

            users_data_dict[user_key] = user_fullName

    db.close()
    return devices_dict, users_data_dict
    
    
def get_filesApp_client(file_found, ci_device_names, ci_users, timezone_offset, report_folder):
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
            
        description = '	List of applications that sync data in iCloud '
        report = ArtifactHtmlReport('iCloud Application List')
        report.start_artifact_report(report_folder, 'Files App - iCloud Application List', description)
        report.add_script()
        app_data_headers = ('Application Bundle ID', 'Number of folders', 'Number of files', 'Total size in bytes', 'Total size' )     
        report.write_artifact_data_table(app_data_headers, app_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - iCloud Application List'
        tsv(report_folder, app_data_headers, app_data_list, tsvname)
    
    else:
        logfunc('No App name data found in Files App')


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
    client_items.item_sharing_options AS 'Is Shared?',
    client_items.item_creator_id AS 'Creator ID?',
    CASE client_items.item_user_visible
    WHEN 0 THEN 'No'
    WHEN 1 THEN 'Yes'
    END AS 'Is Visible?',
    client_items.item_finder_tags AS 'Tags',
    client_items.item_favoriterank AS 'Favourite',
    client_items.item_trash_put_back_path AS 'Recently Deleted'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
    ''')
    
    ci_all_rows = cursor.fetchall()
    ci_usageentries = len(ci_all_rows)
    ci_data_list = []
    ci_tlactivity_list = []
    ci_tlactivity_deleted_list = []
    ci_sharing_list = []
    ci_tagged_list = []
    ci_favourite_list = []
    ci_deleted_list = []
        
    if ci_usageentries > 0:
        ci_parents = get_tree_structure(cursor)

        for ci_row in ci_all_rows:
            ci_app_id, ci_parent_id, ci_filename, ci_ext, ci_size_in_bytes, ci_cdate, \
                ci_mdate, ci_lodate, ci_device, ci_sharing_options, ci_creator_id, \
                ci_visible, ci_tags, ci_favourite, ci_deleted = ci_row
            
            ci_path = ''
            if len(ci_parent_id) == 16:
                ci_path = ci_parents.get(ci_parent_id, '')
            
            if not isinstance(ci_size_in_bytes, int):
                ci_path += f"{ci_filename}/"
                ci_filename = ""

            ci_size = ci_size_in_bytes
            if ci_size:
                ci_size = convert_bytes_to_unit(ci_size_in_bytes)
            
            ci_cdate = convert_ts_int_to_timezone(ci_cdate, timezone_offset) if ci_cdate and ci_cdate > 0 else ''

            ci_mdate = convert_ts_int_to_timezone(ci_mdate, timezone_offset) if ci_mdate and ci_mdate > 0 else ''

            ci_lodate = convert_ts_int_to_timezone(ci_lodate, timezone_offset) if ci_lodate and ci_lodate > 0 else ''

            ci_device = ci_device_names.get(ci_device, '')

            ci_shared = 'No' if ci_sharing_options <= 4 else 'Yes'
            
            if ci_deleted:
                ci_deleted_list.append((ci_app_id, ci_path, ci_deleted, ci_ext, ci_size_in_bytes, ci_size, 
                                 ci_cdate, ci_mdate, ci_lodate, ci_device, ci_shared, ci_visible))
                if ci_cdate:
                    ci_tlactivity_deleted_list.append((ci_cdate, ci_app_id, ci_path, ci_filename, ci_ext, 
                                                       ci_size_in_bytes, ci_size, ci_mdate, ci_lodate, ci_device, 
                                                       ci_shared, ci_visible))
            else:
                ci_data_list.append((ci_app_id, ci_path, ci_filename, ci_ext, ci_size_in_bytes, ci_size, 
                                 ci_cdate, ci_mdate, ci_lodate, ci_device, ci_shared, ci_visible))
                if ci_cdate:
                    ci_tlactivity_list.append((ci_cdate, ci_app_id, ci_path, ci_filename, ci_ext, ci_size_in_bytes, 
                                                ci_size, ci_mdate, ci_lodate, ci_device, ci_shared, ci_visible))
            
            if ci_sharing_options == 8 or ci_sharing_options == 12:
                ci_sharing_permissions = "Anyone with the link can make changes"
            elif ci_sharing_options == 24 or ci_sharing_options == 28:
                ci_sharing_permissions = "Anyone with the link can view only"
            elif ci_sharing_options == 64 or ci_sharing_options == 68:
                ci_sharing_permissions = "Only people invited"
            else:
                ci_sharing_permissions = ''
            
            if ci_sharing_permissions:
                ci_creator_name = ci_users.get(ci_creator_id, 'an unknown user')
                ci_sharing_type = f"Shared by {ci_creator_name if ci_creator_id else 'me'}"
                ci_sharing_list.append((ci_app_id, ci_path, ci_filename, ci_sharing_type, ci_sharing_permissions, \
                                        ci_ext, ci_size_in_bytes, ci_size, ci_cdate, ci_mdate, ci_lodate))
            
            if ci_tags:
                ci_tags = ', '.join(ci_tags.decode('utf-8').split())
                ci_tagged_list.append((ci_app_id, ci_path, ci_filename, ci_ext, ci_tags ,ci_size_in_bytes, ci_size, \
                                       ci_cdate, ci_mdate, ci_lodate))
            
            if ci_favourite:
                ci_favourite_list.append((ci_app_id, ci_path, ci_filename, ci_ext, ci_size_in_bytes, ci_size, \
                                       ci_cdate, ci_mdate, ci_lodate))
            
        description = '	Files stored in iCloud Drive with their metadata. '
        report = ArtifactHtmlReport('Files stored in iCloud Drive')
        report.start_artifact_report(report_folder, 'Files App - Files stored in iCloud Drive', description)
        report.add_script()
        ci_data_headers = ('Application Bundle ID', 'Path', 'Filename', 'Hidden extension', 'Size in bytes', 
                        'Size', 'Created', 'Modified', 'Last opened', 'From Device Name', 'Shared?', 'Visible?')     
        report.write_artifact_data_table(ci_data_headers, ci_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - Files stored in iCloud Drive'
        tsv(report_folder, ci_data_headers, ci_data_list, tsvname)
    

        ci_tlactivity_headers = ('Created', 'Application Bundle ID', 'Path', 'Filename', 'Hidden extension', 
                                 'Size in bytes', 'Size', 'Modified', 'Last opened', 'From Device Name', 
                                 'Shared?', 'Visible?')     
        tlactivity = 'Files App - Files stored in iCloud Drive'
        timeline(report_folder, tlactivity, ci_tlactivity_list, ci_tlactivity_headers)
    
        # Recently Deleted Items

        if ci_deleted_list:
            description = '	Recently deleted files stored in iCloud Drive with their metadata. '
            report = ArtifactHtmlReport('Recently deleted files stored in iCloud Drive')
            report.start_artifact_report(report_folder, 'Files App - Recently deleted files', description)
            report.add_script()
            ci_data_headers = ('Application Bundle ID', 'Path', 'Filename', 'Hidden extension', 'Size in bytes', 
                            'Size', 'Created', 'Modified', 'Last opened', 'From Device Name', 'Shared?', 'Visible?')     
            report.write_artifact_data_table(ci_data_headers, ci_deleted_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Files App - Recently deleted files'
            tsv(report_folder, ci_data_headers, ci_deleted_list, tsvname)
        
            tlactivity = 'Files App - Recently deleted files'
            timeline(report_folder, tlactivity, ci_deleted_list, ci_data_headers)
        
        else:
            logfunc('No recently deleted file data found in Files App')
    
        # Shared Items
            
        if ci_sharing_list:
            description = '	Shared files stored in iCloud Drive with their metadata. '
            report = ArtifactHtmlReport('Shared files stored in iCloud Drive')
            report.start_artifact_report(report_folder, 'Files App - Shared files', description)
            report.add_script()
            ci_sharing_data_headers = ('Application Bundle ID', 'Path', 'Filename', 'Sharing type', 'Permissions', 
                                    'Hidden extension', 'Size in bytes', 'Size', 'Created', 'Modified', 'Last opened',)     
            report.write_artifact_data_table(ci_sharing_data_headers, ci_sharing_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Files App - Shared files'
            tsv(report_folder, ci_sharing_data_headers, ci_sharing_list, tsvname)
        
        else:
            logfunc('No shared file data found in Files App')

        # Tagged Items
            
        if ci_tagged_list:
            description = '	Tagged files in iCloud Drive with their metadata. '
            report = ArtifactHtmlReport('Tagged files in iCloud Drive')
            report.start_artifact_report(report_folder, 'Files App - Tagged files', description)
            report.add_script()
            ci_tagged_data_headers = ('Application Bundle ID', 'Path', 'Filename', 'Hidden extension', 'Tags', \
                                    'Size in bytes', 'Size', 'Created', 'Modified', 'Last opened',)     
            report.write_artifact_data_table(ci_tagged_data_headers, ci_tagged_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Files App - Tagged files'
            tsv(report_folder, ci_tagged_data_headers, ci_tagged_list, tsvname)
        
        else:
            logfunc('No tagged file data found in Files App')

        # Favourite Items
            
        if ci_favourite_list:
            description = '	Favourite files in iCloud Drive with their metadata. '
            report = ArtifactHtmlReport('Favourite files in iCloud Drive')
            report.start_artifact_report(report_folder, 'Files App - Favourite files', description)
            report.add_script()
            ci_favourite_data_headers = ('Application Bundle ID', 'Path', 'Filename', 'Hidden extension', \
                                    'Size in bytes', 'Size', 'Created', 'Modified', 'Last opened',)     
            report.write_artifact_data_table(ci_favourite_data_headers, ci_favourite_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Files App - Favourite files'
            tsv(report_folder, ci_favourite_data_headers, ci_favourite_list, tsvname)
        
        else:
            logfunc('No tagged file data found in Files App')

    else:
        logfunc('No file data found in Files App')


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
        report.start_artifact_report(report_folder, 'Files App - OS Updates', description)
        report.add_script()
        os_data_headers = ('Date and Time', 'OS Build', 'OS Version')     
        report.write_artifact_data_table(os_data_headers, os_data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Files App - OS Updates'
        tsv(report_folder, os_data_headers, os_data_list, tsvname)

        tlactivity = 'Files App - OS Updates'
        timeline(report_folder, tlactivity, os_data_list, os_data_headers)

    else:
        logfunc('No OS update data found in Files App')

    db.close()


def get_filesApp(files_found, report_folder, seeker, wrap_text, timezone_offset):
    client_db = ''
    server_db = ''
    device_names = {}
    users = {}

    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('client.db'):
            client_db = file_found
        if file_found.endswith('server.db'):
            server_db = file_found
    
    if server_db:
        device_names, users = get_filesApps_server(server_db, report_folder)
    else:
        logfunc('No server database found in Files App')
    
    if client_db:
        get_filesApp_client(client_db, device_names, users, timezone_offset, report_folder)
    else:
        logfunc('No client database found in Files App')
