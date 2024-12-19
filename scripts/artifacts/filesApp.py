__artifacts_v2__ = {
    "iCloudSyncDeviceNames": {
        "name": "Files App - iCloud Sync Device Names",
        "description": "Device names that are able to sync to iCloud Drive",
        "author": "@JohannPLW",
        "creation_date": "2024-02-05",
        "last_update_date": "2024-12-13",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smartphone"
    },
    "iCloudApplicationList": {
        "name": "Files App - iCloud Application List",
        "description": "List of applications that sync data in iCloud",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2024-12-13",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package"
    },
    "iCloudDriveStoredFiles": {
        "name": "Files App - Files stored in iCloud Drive",
        "description": "Files stored in iCloud Drive with their metadata",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2024-12-17",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*'),
        "output_types": "standard",
        "artifact_icon": "cloud"
    },
    "iCloudDriveSharedFiles": {
        "name": "Files App - Shared files stored in iCloud Drive",
        "description": "Shared files stored in iCloud Drive with their metadata",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2024-12-18",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "share"
    },
    "iCloudDriveTaggedFiles": {
        "name": "Files App - Tagged files",
        "description": "Tagged files in iCloud Drive with their metadata",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2024-12-18",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag"
    },
    "iCloudDriveFavouriteFiles": {
        "name": "Files App - Favourite files",
        "description": "Favourite files in iCloud Drive with their metadata",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2024-12-18",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "star"
    },
    "FilesIosUpdates": {
        "name": "'Files App - Operating System Updates'",
        "description": "iOS Updates",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2024-12-18",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',),
        "output_types": "standard",
        "artifact_icon": "refresh-cw"
    }
}


import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, get_plist_content, convert_bytes_to_unit, convert_unix_ts_to_utc

def get_tree_structure(source_path):

    query = '''
    SELECT
        client_items.item_id,
        client_items.item_parent_id,
        client_items.item_filename
    FROM client_items
    WHERE client_items.item_type != 1
    '''

    db_records = get_sqlite_db_records(source_path, query)

    tree_structure_dict = {}
    tree_structure_paths = {}

    for record in db_records:
        ts_id, ts_parent_id, ts_filename = record
        tree_structure_dict[ts_id] = (ts_parent_id, ts_filename)

    for ts_key, ts_value in tree_structure_dict.items():
        ts_p_id, ts_path = ts_value
        while len(ts_p_id) == 16:
            ts_p_id, ts_name = tree_structure_dict[ts_p_id]
            ts_path = ts_name + "/" + ts_path
        tree_structure_paths[ts_key] = f"{ts_path}/"
    
    return tree_structure_paths

@artifact_processor
def iCloudSyncDeviceNames(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "server.db")
    data_list = []

    query = '''
    SELECT
        devices.key,
        devices.name
    FROM devices
    '''

    data_headers = ('Device Number', 'Device Name')

    data_list = get_sqlite_db_records(source_path, query)
    
    return data_headers, data_list, source_path

@artifact_processor
def iCloudApplicationList(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "client.db")
    data_list = []

    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) < version.parse('18'):
        query = '''
        SELECT 
            app_libraries.app_library_name,
            app_libraries.auto_client_item_count - app_libraries.auto_document_count,
            app_libraries.auto_document_count,
            app_libraries.auto_aggregate_size
        FROM app_libraries
        '''
        data_headers = ('Application Bundle ID', 'Number of folders', 'Number of files', ('Total size in bytes', 'bytes'))
    else:
        query = '''
        SELECT 
            app_libraries.app_library_name
        FROM app_libraries
        '''
        data_headers = ('Application Bundle ID', )

    data_list = get_sqlite_db_records(source_path, query)
    
    return data_headers, data_list, source_path

@artifact_processor
def iCloudDriveStoredFiles(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = '''ATTACH DATABASE "file:''' + server_db_path + '''?mode=ro" AS server '''
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_sharing_options AS 'Is Shared?',
        CASE client_items.item_user_visible
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Is Visible?',
        client_items.item_trash_put_back_path AS 'Recently Deleted'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
	LEFT JOIN server.devices ON client_items.version_device = server.devices.key
    '''

    data_headers = (
        ('Created', 'datetime'), 
        ('Modified', 'datetime'), 
        ('Last opened', 'datetime'), 
        'Application Bundle ID', 
        'Path', 
        'Filename', 
        'Hidden extension', 
        'Size in bytes', 
        'Size', 
        'From Device Name', 
        'Shared?', 
        'Visible?',
        'Recently Deleted')     

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    if db_records:
        parents = get_tree_structure(source_path)
    
    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, size_in_bytes, device, \
            sharing_options, visible, trash_back_path = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')
        
        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)
        
        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        shared = 'No' if sharing_options <= 4 else 'Yes'
        recently_deleted = 'Yes' if trash_back_path else 'No'
        
        data_list.append((cdate, mdate, lodate, app_id, path, filename, ext, size_in_bytes, 
                          size, device, shared, visible, recently_deleted))
            
    return data_headers, data_list, source_path

@artifact_processor
def iCloudDriveSharedFiles(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = '''ATTACH DATABASE "file:''' + server_db_path + '''?mode=ro" AS server '''
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_sharing_options AS 'Is Shared?',
        client_items.item_creator_id AS 'Creator ID?',
		server.users.user_plist,
        client_items.item_trash_put_back_path AS 'Recently Deleted'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
	LEFT JOIN server.devices ON client_items.version_device = server.devices.key
	LEFT JOiN server.users ON client_items.item_creator_id = server.users.user_key
	WHERE client_items.item_sharing_options > 4
    '''

    data_headers = (
        ('Created', 'datetime'), 
        ('Modified', 'datetime'), 
        ('Last opened', 'datetime'), 
        'Application Bundle ID', 
        'Path', 
        'Filename', 
        'Hidden extension', 
        'Size in bytes', 
        'Size', 
        'From Device Name', 
        'Shared by', 
        'Permissions',
        'Recently Deleted')     

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    if db_records:
        parents = get_tree_structure(source_path)
    
    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, size_in_bytes, device, \
            sharing_options, creator_id, user_plist, trash_back_path = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')
        
        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)
        
        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        if sharing_options == 8 or sharing_options == 12:
            sharing_permissions = "Anyone with the link can make changes"
        elif sharing_options == 24 or sharing_options == 28:
            sharing_permissions = "Anyone with the link can view only"
        elif sharing_options == 64 or sharing_options == 68:
            sharing_permissions = "Only invited people"
        else:
            sharing_permissions = ''

        user_fullName = ''
        if user_plist:
            deserialized_user_plist = get_plist_content(user_plist[3:])
            user = deserialized_user_plist.get('NS.nameComponentsPrivate')
            if user:
                user_givenName = user.get('NS.givenName', '')
                user_familyName = user.get('NS.familyName', '')
                user_fullName = f"{user_givenName + ' ' if user_givenName else ''}{user_familyName}"
        creator_name = user_fullName if user_fullName else 'an unknown user'
        shared_by = creator_name if creator_id else 'me'

        recently_deleted = 'Yes' if trash_back_path else 'No'
        
        data_list.append((cdate, mdate, lodate, app_id, path, filename, ext, size_in_bytes, 
                          size, device, shared_by, sharing_permissions, recently_deleted))
            
    return data_headers, data_list, source_path

@artifact_processor
def iCloudDriveTaggedFiles(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = '''ATTACH DATABASE "file:''' + server_db_path + '''?mode=ro" AS server '''
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.item_finder_tags AS 'Tags',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_trash_put_back_path AS 'Recently Deleted'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
	LEFT JOIN server.devices ON client_items.version_device = server.devices.key
	WHERE client_items.item_finder_tags IS NOT NULL
    '''

    data_headers = (
        ('Created', 'datetime'), 
        ('Modified', 'datetime'), 
        ('Last opened', 'datetime'), 
        'Application Bundle ID', 
        'Path', 
        'Filename', 
        'Hidden extension', 
        'Tags', 
        'Size in bytes', 
        'Size', 
        'From Device Name', 
        'Recently Deleted')     

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    if db_records:
        parents = get_tree_structure(source_path)
    
    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, tags, size_in_bytes, device, \
            trash_back_path = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')
        
        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)
        
        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        if tags:
            tags = ', '.join(tags.decode('utf-8').split())

        recently_deleted = 'Yes' if trash_back_path else 'No'
        
        data_list.append((cdate, mdate, lodate, app_id, path, filename, ext, tags, size_in_bytes, 
                          size, device, recently_deleted))
            
    return data_headers, data_list, source_path

@artifact_processor
def iCloudDriveFavouriteFiles(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = '''ATTACH DATABASE "file:''' + server_db_path + '''?mode=ro" AS server '''
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_trash_put_back_path AS 'Recently Deleted',
        client_items.item_favoriterank AS 'Favourite'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
	LEFT JOIN server.devices ON client_items.version_device = server.devices.key
	WHERE client_items.item_favoriterank != 0
    '''

    data_headers = (
        ('Created', 'datetime'), 
        ('Modified', 'datetime'), 
        ('Last opened', 'datetime'), 
        'Application Bundle ID', 
        'Path', 
        'Filename', 
        'Hidden extension', 
        'Size in bytes', 
        'Size', 
        'From Device Name', 
        'Recently Deleted')     

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    if db_records:
        parents = get_tree_structure(source_path)
    
    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, size_in_bytes, \
            device, trash_back_path, favourite = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')
        
        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)
        
        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        recently_deleted = 'Yes' if trash_back_path else 'No'
        
        data_list.append((cdate, mdate, lodate, app_id, path, filename, ext, size_in_bytes, 
                          size, device, recently_deleted))
            
    return data_headers, data_list, source_path

@artifact_processor
def FilesIosUpdates(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "client.db")
    data_list = []

    query = '''
    SELECT
        boot_history.date,
        boot_history.os
    FROM boot_history
    '''
    data_headers = (('Date and Time', 'datetime'), 'OS Build', 'OS Version')     

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        os_date, os_os  = record
        os_date = convert_unix_ts_to_utc(os_date)
        os_version = OS_build.get(os_os, '')

        data_list.append((os_date, os_os, os_version))

    
    return data_headers, data_list, source_path
