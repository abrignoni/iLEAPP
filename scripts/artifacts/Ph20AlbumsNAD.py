__artifacts_v2__ = {
    'Ph20_1AlbumRecordswithNADPhDaPsql': {
        'name': 'Ph20.1-Album Records NAD-PhDaPsql',
        'description': 'Parses Basic Album records found in the PhotoData-Photos.sqlite ZGENERICALBUM Table'
                       ' and supports iOS 11-18. Parses Album records only no asset data being parsed.'
                       ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.'
                       ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You Conversation Identifiers.'
                       ' Please see the album type specific scripts to view more data for each album type.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-D-Generic_Album_Records-NAD',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    },
    'Ph20_2AlbumRecordswithNADSyndPL': {
        'name': 'Ph20.2-Album Records NAD-SyndPL',
        'description': 'Parses Basic Album records found in the Syndication.photoslibrary-database-Photos.sqlite'
                       ' ZGENERICALBUM Table and supports iOS 11-18. Parses Album records only no asset data'
                       ' being parsed. Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.'
                       ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You Conversation Identifiers.'
                       ' Please see the album type specific scripts to view more data for each album type.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-S-Syndication_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc

@artifact_processor
def Ph20_1AlbumRecordswithNADPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('-') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT 
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZSTARTDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11]))

        data_headers = (('zGenAlbum-Start Date', 'datetime'),
                        ('zGenAlbum-End Date', 'datetime'),
                        'zGenAlbum-Album Kind',
                        'zGenAlbum-Title',
                        'zGenAlbum-Import Session ID',
                        'zGenAlbum-Cached Photos Count',
                        'zGenAlbum-Cached Videos Count',
                        'zGenAlbum-Cached Count',
                        'zGenAlbum-Trashed State',
                        ('zGenAlbum-Trash Date', 'datetime'),
                        'zGenAlbum-UUID',
                        'zGenAlbum-Cloud GUID')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle Identifier',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11], row[12], row[13]))

        data_headers = (('zGenAlbum-Creation Date', 'datetime'),
                        ('zGenAlbum-Start Date', 'datetime'),
                        ('zGenAlbum-End Date', 'datetime'),
                        'zGenAlbum-Album Kind',
                        'zGenAlbum-Title',
                        'zGenAlbum-Import Session ID',
                        'zGenAlbum-Creator Bundle Identifier',
                        'zGenAlbum-Cached Photos Count',
                        'zGenAlbum-Cached Videos Count',
                        'zGenAlbum-Cached Count',
                        'zGenAlbum-Trashed State',
                        ('zGenAlbum-Trash Date', 'datetime'),
                        'zGenAlbum-UUID',
                        'zGenAlbum-Cloud GUID')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11], row[12], row[13]))

        data_headers = (('zGenAlbum-Creation Date', 'datetime'),
                        ('zGenAlbum-Start Date', 'datetime'),
                        ('zGenAlbum-End Date', 'datetime'),
                        'zGenAlbum-Album Kind',
                        'zGenAlbum-Title',
                        'zGenAlbum-Import Session ID',
                        'zGenAlbum-Imported by Bundle Identifier',
                        'zGenAlbum-Cached Photos Count',
                        'zGenAlbum-Cached Videos Count',
                        'zGenAlbum-Cached Count',
                        'zGenAlbum-Trashed State',
                        ('zGenAlbum-Trash Date', 'datetime'),
                        'zGenAlbum-UUID',
                        'zGenAlbum-Cloud GUID')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11], row[12], row[13]))

        data_headers = (('zGenAlbum-Creation Date-0', 'datetime'),
                        ('zGenAlbum-Start Date-1', 'datetime'),
                        ('zGenAlbum-End Date-2', 'datetime'),
                        'zGenAlbum-Album Kind-3',
                        'zGenAlbum-Title-4',
                        'zGenAlbum-Import Session ID-5',
                        'zGenAlbum-Imported by Bundle Identifier-6',
                        'zGenAlbum-Cached Photos Count-7',
                        'zGenAlbum-Cached Videos Count-8',
                        'zGenAlbum-Cached Count-9',
                        'zGenAlbum-Trashed State-10',
                        ('zGenAlbum-Trash Date-11', 'datetime'),
                        'zGenAlbum-UUID-12',
                        'zGenAlbum-Cloud GUID-13')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph20_2AlbumRecordswithNADSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for Syndication.photoslibrary iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT 
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZSTARTDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11]))

        data_headers = (('zGenAlbum-Start Date', 'datetime'),
                        ('zGenAlbum-End Date', 'datetime'),
                        'zGenAlbum-Album Kind',
                        'zGenAlbum-Title',
                        'zGenAlbum-Import Session ID',
                        'zGenAlbum-Cached Photos Count',
                        'zGenAlbum-Cached Videos Count',
                        'zGenAlbum-Cached Count',
                        'zGenAlbum-Trashed State',
                        ('zGenAlbum-Trash Date', 'datetime'),
                        'zGenAlbum-UUID',
                        'zGenAlbum-Cloud GUID')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle Identifier',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11], row[12], row[13]))

        data_headers = (('zGenAlbum-Creation Date', 'datetime'),
                        ('zGenAlbum-Start Date', 'datetime'),
                        ('zGenAlbum-End Date', 'datetime'),
                        'zGenAlbum-Album Kind',
                        'zGenAlbum-Title',
                        'zGenAlbum-Import Session ID',
                        'zGenAlbum-Creator Bundle Identifier',
                        'zGenAlbum-Cached Photos Count',
                        'zGenAlbum-Cached Videos Count',
                        'zGenAlbum-Cached Count',
                        'zGenAlbum-Trashed State',
                        ('zGenAlbum-Trash Date', 'datetime'),
                        'zGenAlbum-UUID',
                        'zGenAlbum-Cloud GUID')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11], row[12], row[13]))

        data_headers = (('zGenAlbum-Creation Date', 'datetime'),
                        ('zGenAlbum-Start Date', 'datetime'),
                        ('zGenAlbum-End Date', 'datetime'),
                        'zGenAlbum-Album Kind',
                        'zGenAlbum-Title',
                        'zGenAlbum-Import Session ID',
                        'zGenAlbum-Imported by Bundle Identifier',
                        'zGenAlbum-Cached Photos Count',
                        'zGenAlbum-Cached Videos Count',
                        'zGenAlbum-Cached Count',
                        'zGenAlbum-Trashed State',
                        ('zGenAlbum-Trash Date', 'datetime'),
                        'zGenAlbum-UUID',
                        'zGenAlbum-Cloud GUID')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title-User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], row[10], row[11], row[12], row[13]))

        data_headers = (('zGenAlbum-Creation Date-0', 'datetime'),
                        ('zGenAlbum-Start Date-1', 'datetime'),
                        ('zGenAlbum-End Date-2', 'datetime'),
                        'zGenAlbum-Album Kind-3',
                        'zGenAlbum-Title-4',
                        'zGenAlbum-Import Session ID-5',
                        'zGenAlbum-Imported by Bundle Identifier-6',
                        'zGenAlbum-Cached Photos Count-7',
                        'zGenAlbum-Cached Videos Count-8',
                        'zGenAlbum-Cached Count-9',
                        'zGenAlbum-Trashed State-10',
                        ('zGenAlbum-Trash Date-11', 'datetime'),
                        'zGenAlbum-UUID-12',
                        'zGenAlbum-Cloud GUID-13')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
