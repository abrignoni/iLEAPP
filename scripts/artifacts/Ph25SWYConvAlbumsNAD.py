__artifacts_v2__ = {
    'Ph25_1SWYConversationRecordswithNADPhDaPsql': {
        'name': 'Ph25.1-SWY Conversation Records NAD-PhDaPsql',
        'description': 'Parses Shared with You Conversation Album records found in the PhotoData-Photos.sqlite'
                       ' ZGENERICALBUM Table and supports iOS 15-18. Parses Share with You Conversation Album'
                       ' records only, no asset data being parsed.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-D-Generic_Album_Records-NAD',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    },
    'Ph25_2SWYConversationRecordswithNADSyndPL': {
        'name': 'Ph25.2-SWY Conversation Records NAD-SyndPL',
        'description': 'Parses SWY Conversation Album Records found in the'
                       ' Syndication.photoslibrary-database-Photos.sqlite ZGENERICALBUM Table and supports iOS 15-18.'
                       ' Parses Share with You Conversation Album records only, no asset data being parsed.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '4.0',
        'date': '2024-12-31',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-S-Syndication_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import glob
import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc

@artifact_processor
def Ph25_1SWYConversationRecordswithNADPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("14.8.1"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_27ASSETS Albumsz27Assets ON Albumsz27Assets.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18]))

        data_headers = (('SWYConverszGenAlbum-Creation Date', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date', 'datetime'),
                        ('SWYConverszGenAlbum-End Date', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK',
                        'SWYConverszGenAlbum- Import Session ID-SWY',
                        'SWYzGenAlbum-Imported by Bundle Identifier',
                        'SWYConverszGenAlbum-Album Kind',
                        'SWYConverszGenAlbum-Cloud_Local_State',
                        'SWYConverszGenAlbum- Syndicate',
                        'SWYConverszGenAlbum-Sync Event Order Key',
                        'SWYConverszGenAlbum-Pinned',
                        'SWYConverszGenAlbum-Custom Sort Key',
                        'SWYConverszGenAlbum-Custom Sort Ascending',
                        'SWYConverszGenAlbum-Is Prototype',
                        'SWYConverszGenAlbum-Project Document Type',
                        'SWYConverszGenAlbum-Custom Query Type',
                        'SWYConverszGenAlbum-Trashed State',
                        ('SWYConverszGenAlbum-Trash Date', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17.6")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_28ASSETS Albumsz28Assets ON Albumsz28Assets.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19]))

        data_headers = (('SWYConverszGenAlbum-Creation Date-0', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-2', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-3',
                        'SWYConverszGenAlbum- Import Session ID-SWY-4',
                        'SWYzGenAlbum-Imported by Bundle Identifier-5',
                        'SWYConverszGenAlbum-Album Kind-6',
                        'SWYConverszGenAlbum-Cloud_Local_State-7',
                        'SWYConverszGenAlbum- Syndicate-8',
                        'SWYConverszGenAlbum-Sync Event Order Key-9',
                        'SWYConverszGenAlbum-Pinned-10',
                        'SWYConverszGenAlbum-Custom Sort Key-11',
                        'SWYConverszGenAlbum-Custom Sort Ascending-12',
                        'SWYConverszGenAlbum-Is Prototype-13',
                        'SWYConverszGenAlbum-Project Document Type-14',
                        'SWYConverszGenAlbum-Custom Query Type-15',
                        'SWYConverszGenAlbum-Trashed State-16',
                        ('SWYConverszGenAlbum-Trash Date-17', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-18',
                        'SWYConverszGenAlbum-Privacy State-19')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
	
    elif (version.parse(iosversion) >= version.parse("17.6")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_29ASSETS z29Assets ON z29Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_29ASSETS Albumsz29Assets ON Albumsz29Assets.Z_29ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_28ALBUMLISTS z28AlbumLists ON z28AlbumLists.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z28AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19]))

        data_headers = (('SWYConverszGenAlbum-Creation Date-0', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-2', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-3',
                        'SWYConverszGenAlbum- Import Session ID-SWY-4',
                        'SWYzGenAlbum-Imported by Bundle Identifier-5',
                        'SWYConverszGenAlbum-Album Kind-6',
                        'SWYConverszGenAlbum-Cloud_Local_State-7',
                        'SWYConverszGenAlbum- Syndicate-8',
                        'SWYConverszGenAlbum-Sync Event Order Key-9',
                        'SWYConverszGenAlbum-Pinned-10',
                        'SWYConverszGenAlbum-Custom Sort Key-11',
                        'SWYConverszGenAlbum-Custom Sort Ascending-12',
                        'SWYConverszGenAlbum-Is Prototype-13',
                        'SWYConverszGenAlbum-Project Document Type-14',
                        'SWYConverszGenAlbum-Custom Query Type-15',
                        'SWYConverszGenAlbum-Trashed State-16',
                        ('SWYConverszGenAlbum-Trash Date-17', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-18',
                        'SWYConverszGenAlbum-Privacy State-19')
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
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_30ASSETS z30Assets ON z30Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_30ASSETS Albumsz30Assets ON Albumsz30Assets.Z_30ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_29ALBUMLISTS z29AlbumLists ON z29AlbumLists.Z_29ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z29AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19]))

        data_headers = (('SWYConverszGenAlbum-Creation Date-0', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-2', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-3',
                        'SWYConverszGenAlbum- Import Session ID-SWY-4',
                        'SWYzGenAlbum-Imported by Bundle Identifier-5',
                        'SWYConverszGenAlbum-Album Kind-6',
                        'SWYConverszGenAlbum-Cloud_Local_State-7',
                        'SWYConverszGenAlbum- Syndicate-8',
                        'SWYConverszGenAlbum-Sync Event Order Key-9',
                        'SWYConverszGenAlbum-Pinned-10',
                        'SWYConverszGenAlbum-Custom Sort Key-11',
                        'SWYConverszGenAlbum-Custom Sort Ascending-12',
                        'SWYConverszGenAlbum-Is Prototype-13',
                        'SWYConverszGenAlbum-Project Document Type-14',
                        'SWYConverszGenAlbum-Custom Query Type-15',
                        'SWYConverszGenAlbum-Trashed State-16',
                        ('SWYConverszGenAlbum-Trash Date-17', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-18',
                        'SWYConverszGenAlbum-Privacy State-19')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph25_2SWYConversationRecordswithNADSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("14.8.1"):
        logfunc("Unsupported version for Syndication.photoslibrary iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_27ASSETS Albumsz27Assets ON Albumsz27Assets.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18]))

        data_headers = (('SWYConverszGenAlbum-Creation Date', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date', 'datetime'),
                        ('SWYConverszGenAlbum-End Date', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK',
                        'SWYConverszGenAlbum- Import Session ID-SWY',
                        'SWYzGenAlbum-Imported by Bundle Identifier',
                        'SWYConverszGenAlbum-Album Kind',
                        'SWYConverszGenAlbum-Cloud_Local_State',
                        'SWYConverszGenAlbum- Syndicate',
                        'SWYConverszGenAlbum-Sync Event Order Key',
                        'SWYConverszGenAlbum-Pinned',
                        'SWYConverszGenAlbum-Custom Sort Key',
                        'SWYConverszGenAlbum-Custom Sort Ascending',
                        'SWYConverszGenAlbum-Is Prototype',
                        'SWYConverszGenAlbum-Project Document Type',
                        'SWYConverszGenAlbum-Custom Query Type',
                        'SWYConverszGenAlbum-Trashed State',
                        ('SWYConverszGenAlbum-Trash Date', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17.6")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_28ASSETS Albumsz28Assets ON Albumsz28Assets.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19]))

        data_headers = (('SWYConverszGenAlbum-Creation Date-0', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-2', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-3',
                        'SWYConverszGenAlbum- Import Session ID-SWY-4',
                        'SWYzGenAlbum-Imported by Bundle Identifier-5',
                        'SWYConverszGenAlbum-Album Kind-6',
                        'SWYConverszGenAlbum-Cloud_Local_State-7',
                        'SWYConverszGenAlbum- Syndicate-8',
                        'SWYConverszGenAlbum-Sync Event Order Key-9',
                        'SWYConverszGenAlbum-Pinned-10',
                        'SWYConverszGenAlbum-Custom Sort Key-11',
                        'SWYConverszGenAlbum-Custom Sort Ascending-12',
                        'SWYConverszGenAlbum-Is Prototype-13',
                        'SWYConverszGenAlbum-Project Document Type-14',
                        'SWYConverszGenAlbum-Custom Query Type-15',
                        'SWYConverszGenAlbum-Trashed State-16',
                        ('SWYConverszGenAlbum-Trash Date-17', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-18',
                        'SWYConverszGenAlbum-Privacy State-19')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
	
    elif (version.parse(iosversion) >= version.parse("17.6")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_29ASSETS z29Assets ON z29Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_29ASSETS Albumsz29Assets ON Albumsz29Assets.Z_29ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_28ALBUMLISTS z28AlbumLists ON z28AlbumLists.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z28AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19]))

        data_headers = (('SWYConverszGenAlbum-Creation Date-0', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-2', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-3',
                        'SWYConverszGenAlbum- Import Session ID-SWY-4',
                        'SWYzGenAlbum-Imported by Bundle Identifier-5',
                        'SWYConverszGenAlbum-Album Kind-6',
                        'SWYConverszGenAlbum-Cloud_Local_State-7',
                        'SWYConverszGenAlbum- Syndicate-8',
                        'SWYConverszGenAlbum-Sync Event Order Key-9',
                        'SWYConverszGenAlbum-Pinned-10',
                        'SWYConverszGenAlbum-Custom Sort Key-11',
                        'SWYConverszGenAlbum-Custom Sort Ascending-12',
                        'SWYConverszGenAlbum-Is Prototype-13',
                        'SWYConverszGenAlbum-Project Document Type-14',
                        'SWYConverszGenAlbum-Custom Query Type-15',
                        'SWYConverszGenAlbum-Trashed State-16',
                        ('SWYConverszGenAlbum-Trash Date-17', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-18',
                        'SWYConverszGenAlbum-Privacy State-19')
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
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_30ASSETS z30Assets ON z30Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_30ASSETS Albumsz30Assets ON Albumsz30Assets.Z_30ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_29ALBUMLISTS z29AlbumLists ON z29AlbumLists.Z_29ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z29AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19]))

        data_headers = (('SWYConverszGenAlbum-Creation Date-0', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-2', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-3',
                        'SWYConverszGenAlbum- Import Session ID-SWY-4',
                        'SWYzGenAlbum-Imported by Bundle Identifier-5',
                        'SWYConverszGenAlbum-Album Kind-6',
                        'SWYConverszGenAlbum-Cloud_Local_State-7',
                        'SWYConverszGenAlbum- Syndicate-8',
                        'SWYConverszGenAlbum-Sync Event Order Key-9',
                        'SWYConverszGenAlbum-Pinned-10',
                        'SWYConverszGenAlbum-Custom Sort Key-11',
                        'SWYConverszGenAlbum-Custom Sort Ascending-12',
                        'SWYConverszGenAlbum-Is Prototype-13',
                        'SWYConverszGenAlbum-Project Document Type-14',
                        'SWYConverszGenAlbum-Custom Query Type-15',
                        'SWYConverszGenAlbum-Trashed State-16',
                        ('SWYConverszGenAlbum-Trash Date-17', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-18',
                        'SWYConverszGenAlbum-Privacy State-19')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path



