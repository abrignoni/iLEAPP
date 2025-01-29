__artifacts_v2__ = {
    'Ph26_1SyndicationIDAssetsPhDaPsql': {
        'name': 'Ph26.1-Syndication ID Assets-PhDaPsql',
        'description': 'Parses Syndication ID and Syndication Photos Library assets which includes'
                       ' Shared with You Conversation assets from PhotoData-Photos.sqlite and'
                       ' Syndication.photoslibrary-database-Photos.sqlite'
                       ' and supports iOS 15-18. Parses assets that have a ZADDITIONALASSETATTRIBUTES'
                       ' ZSYNDICATIONIDENTIFIER value. ZASSET ZSAVEDASSETTYPE and ZASSET ZSYNDICATIONSTATE fields'
                       ' can be used to filter those results: ZADDITIONALASSETATTRIBUTES ZSYNDICATIONIDENTIFIER:'
                       ' 0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0 1-SyndPs-Sent-SWY_Synd_Asset-1'
                       ' 2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
                       ' 8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
                       ' 9-SyndPs-STILLTESTING_Sent_SWY-9'
                       ' 10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
                       ' ZASSET ZSAVEDASSETTYPE: 12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-C-Other_Artifacts',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    },
    'Ph26_2SyndicationPLAssetsSyndPL': {
        'name': 'Ph26.2-Syndication PL Assets-SyndPL',
        'description': 'Parses Syndication ID and Syndication Photos Library assets which includes'
                       ' Shared with You Conversation assets from PhotoData-Photos.sqlite and'
                       ' Syndication.photoslibrary-database-Photos.sqlite'
                       ' and supports iOS 15-18. Parses assets that have a ZADDITIONALASSETATTRIBUTES'
                       ' ZSYNDICATIONIDENTIFIER value. ZASSET ZSAVEDASSETTYPE and ZASSET ZSYNDICATIONSTATE fields'
                       ' can be used to filter those results: ZADDITIONALASSETATTRIBUTES ZSYNDICATIONIDENTIFIER:'
                       ' 0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0 1-SyndPs-Sent-SWY_Synd_Asset-1'
                       ' 2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
                       ' 8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
                       ' 9-SyndPs-STILLTESTING_Sent_SWY-9'
                       ' 10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
                       ' ZASSET ZSAVEDASSETTYPE: 12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12',
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

import glob
import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc

@artifact_processor
def Ph26_1SyndicationIDAssetsPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("14.8.1"):
        logfunc("Unsupported version from PhotoData-Photos.sqlite for iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',		
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',       
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr- Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        ('zAsset- SortToken -CameraRoll-20', 'datetime'),
                        ('zAsset-Added Date-21', 'datetime'),
                        ('zCldMast-Creation Date-22', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-23',
                        'zAddAssetAttr-EXIF-String-24',
                        ('zAsset-Modification Date-25', 'datetime'),
                        ('zAsset-Last Shared Date-26', 'datetime'),
                        ('zAsset-Trashed Date-27', 'datetime'),
                        'zAddAssetAttr-zPK-28',
                        'zAsset-UUID = store.cloudphotodb-29',
                        'zAddAssetAttr-Master Fingerprint-30',
                        'SWYConverszGenAlbum-Album Kind-31',
                        'SWYConverszGenAlbum-Cloud_Local_State-32',
                        'SWYConverszGenAlbum- Syndicate-33',
                        'SWYConverszGenAlbum-Sync Event Order Key-34',
                        'SWYConverszGenAlbum-Pinned-35',
                        'SWYConverszGenAlbum-Custom Sort Key-36',
                        'SWYConverszGenAlbum-Custom Sort Ascending-37',
                        'SWYConverszGenAlbum-Is Prototype-38',
                        'SWYConverszGenAlbum-Project Document Type-39',
                        'SWYConverszGenAlbum-Custom Query Type-40',
                        'SWYConverszGenAlbum-Trashed State-41',
                        ('SWYConverszGenAlbum-Trash Date-42', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-43')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr.Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        'zAsset-Active Library Scope Participation State-20',
                        ('zAsset- SortToken -CameraRoll-21', 'datetime'),
                        ('zAsset-Added Date-22', 'datetime'),
                        ('zCldMast-Creation Date-23', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-24',
                        'zAddAssetAttr-EXIF-String-25',
                        ('zAsset-Modification Date-26', 'datetime'),
                        ('zAsset-Last Shared Date-27', 'datetime'),
                        ('zAsset-Trashed Date-28', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-29',
                        'zAddAssetAttr-zPK-30',
                        'zAsset-UUID = store.cloudphotodb-31',
                        'zAddAssetAttr-Master Fingerprint-32',
                        'SWYConverszGenAlbum-Album Kind-33',
                        'SWYConverszGenAlbum-Cloud_Local_State-34',
                        'SWYConverszGenAlbum- Syndicate-35',
                        'SWYConverszGenAlbum-Sync Event Order Key-36',
                        'SWYConverszGenAlbum-Pinned-37',
                        'SWYConverszGenAlbum-Custom Sort Key-38',
                        'SWYConverszGenAlbum-Custom Sort Ascending-39',
                        'SWYConverszGenAlbum-Is Prototype-40',
                        'SWYConverszGenAlbum-Project Document Type-41',
                        'SWYConverszGenAlbum-Custom Query Type-42',
                        'SWYConverszGenAlbum-Trashed State-43',
                        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-45',
                        'SWYConverszGenAlbum-Privacy State-46')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_28ALBUMLISTS z28AlbumLists ON z28AlbumLists.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z28AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr.Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        'zAsset-Active Library Scope Participation State-20',
                        ('zAsset- SortToken -CameraRoll-21', 'datetime'),
                        ('zAsset-Added Date-22', 'datetime'),
                        ('zCldMast-Creation Date-23', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-24',
                        'zAddAssetAttr-EXIF-String-25',
                        ('zAsset-Modification Date-26', 'datetime'),
                        ('zAsset-Last Shared Date-27', 'datetime'),
                        ('zAsset-Trashed Date-28', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-29',
                        'zAddAssetAttr-zPK-30',
                        'zAsset-UUID = store.cloudphotodb-31',
                        'zAddAssetAttr-Master Fingerprint-32',
                        'SWYConverszGenAlbum-Album Kind-33',
                        'SWYConverszGenAlbum-Cloud_Local_State-34',
                        'SWYConverszGenAlbum- Syndicate-35',
                        'SWYConverszGenAlbum-Sync Event Order Key-36',
                        'SWYConverszGenAlbum-Pinned-37',
                        'SWYConverszGenAlbum-Custom Sort Key-38',
                        'SWYConverszGenAlbum-Custom Sort Ascending-39',
                        'SWYConverszGenAlbum-Is Prototype-40',
                        'SWYConverszGenAlbum-Project Document Type-41',
                        'SWYConverszGenAlbum-Custom Query Type-42',
                        'SWYConverszGenAlbum-Trashed State-43',
                        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-45',
                        'SWYConverszGenAlbum-Privacy State-46')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash',        
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_29ALBUMLISTS z29AlbumLists ON z29AlbumLists.Z_29ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z29AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr.Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        'zAsset-Active Library Scope Participation State-20',
                        ('zAsset- SortToken -CameraRoll-21', 'datetime'),
                        ('zAsset-Added Date-22', 'datetime'),
                        ('zCldMast-Creation Date-23', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-24',
                        'zAddAssetAttr-EXIF-String-25',
                        ('zAsset-Modification Date-26', 'datetime'),
                        ('zAsset-Last Shared Date-27', 'datetime'),
                        ('zAsset-Trashed Date-28', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-29',
                        'zAddAssetAttr-zPK-30',
                        'zAsset-UUID = store.cloudphotodb-31',
                        'zAddAssetAttr-Original Stable Hash-32',
                        'zAddAssetAttr.Adjusted Stable Hash-33',
                        'SWYConverszGenAlbum-Album Kind-34',
                        'SWYConverszGenAlbum-Cloud_Local_State-35',
                        'SWYConverszGenAlbum- Syndicate-36',
                        'SWYConverszGenAlbum-Sync Event Order Key-37',
                        'SWYConverszGenAlbum-Pinned-38',
                        'SWYConverszGenAlbum-Custom Sort Key-39',
                        'SWYConverszGenAlbum-Custom Sort Ascending-40',
                        'SWYConverszGenAlbum-Is Prototype-41',
                        'SWYConverszGenAlbum-Project Document Type-42',
                        'SWYConverszGenAlbum-Custom Query Type-43',
                        'SWYConverszGenAlbum-Trashed State-44',
                        ('SWYConverszGenAlbum-Trash Date-45', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-46',
                        'SWYConverszGenAlbum-Privacy State-47')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph26_2SyndicationPLAssetsSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("14.8.1"):
        logfunc("Unsupported version from Syndication.photoslibrary for iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',		
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',       
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr- Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        ('zAsset- SortToken -CameraRoll-20', 'datetime'),
                        ('zAsset-Added Date-21', 'datetime'),
                        ('zCldMast-Creation Date-22', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-23',
                        'zAddAssetAttr-EXIF-String-24',
                        ('zAsset-Modification Date-25', 'datetime'),
                        ('zAsset-Last Shared Date-26', 'datetime'),
                        ('zAsset-Trashed Date-27', 'datetime'),
                        'zAddAssetAttr-zPK-28',
                        'zAsset-UUID = store.cloudphotodb-29',
                        'zAddAssetAttr-Master Fingerprint-30',
                        'SWYConverszGenAlbum-Album Kind-31',
                        'SWYConverszGenAlbum-Cloud_Local_State-32',
                        'SWYConverszGenAlbum- Syndicate-33',
                        'SWYConverszGenAlbum-Sync Event Order Key-34',
                        'SWYConverszGenAlbum-Pinned-35',
                        'SWYConverszGenAlbum-Custom Sort Key-36',
                        'SWYConverszGenAlbum-Custom Sort Ascending-37',
                        'SWYConverszGenAlbum-Is Prototype-38',
                        'SWYConverszGenAlbum-Project Document Type-39',
                        'SWYConverszGenAlbum-Custom Query Type-40',
                        'SWYConverszGenAlbum-Trashed State-41',
                        ('SWYConverszGenAlbum-Trash Date-42', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-43')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr.Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        'zAsset-Active Library Scope Participation State-20',
                        ('zAsset- SortToken -CameraRoll-21', 'datetime'),
                        ('zAsset-Added Date-22', 'datetime'),
                        ('zCldMast-Creation Date-23', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-24',
                        'zAddAssetAttr-EXIF-String-25',
                        ('zAsset-Modification Date-26', 'datetime'),
                        ('zAsset-Last Shared Date-27', 'datetime'),
                        ('zAsset-Trashed Date-28', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-29',
                        'zAddAssetAttr-zPK-30',
                        'zAsset-UUID = store.cloudphotodb-31',
                        'zAddAssetAttr-Master Fingerprint-32',
                        'SWYConverszGenAlbum-Album Kind-33',
                        'SWYConverszGenAlbum-Cloud_Local_State-34',
                        'SWYConverszGenAlbum- Syndicate-35',
                        'SWYConverszGenAlbum-Sync Event Order Key-36',
                        'SWYConverszGenAlbum-Pinned-37',
                        'SWYConverszGenAlbum-Custom Sort Key-38',
                        'SWYConverszGenAlbum-Custom Sort Ascending-39',
                        'SWYConverszGenAlbum-Is Prototype-40',
                        'SWYConverszGenAlbum-Project Document Type-41',
                        'SWYConverszGenAlbum-Custom Query Type-42',
                        'SWYConverszGenAlbum-Trashed State-43',
                        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-45',
                        'SWYConverszGenAlbum-Privacy State-46')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_28ALBUMLISTS z28AlbumLists ON z28AlbumLists.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z28AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr.Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        'zAsset-Active Library Scope Participation State-20',
                        ('zAsset- SortToken -CameraRoll-21', 'datetime'),
                        ('zAsset-Added Date-22', 'datetime'),
                        ('zCldMast-Creation Date-23', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-24',
                        'zAddAssetAttr-EXIF-String-25',
                        ('zAsset-Modification Date-26', 'datetime'),
                        ('zAsset-Last Shared Date-27', 'datetime'),
                        ('zAsset-Trashed Date-28', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-29',
                        'zAddAssetAttr-zPK-30',
                        'zAsset-UUID = store.cloudphotodb-31',
                        'zAddAssetAttr-Master Fingerprint-32',
                        'SWYConverszGenAlbum-Album Kind-33',
                        'SWYConverszGenAlbum-Cloud_Local_State-34',
                        'SWYConverszGenAlbum- Syndicate-35',
                        'SWYConverszGenAlbum-Sync Event Order Key-36',
                        'SWYConverszGenAlbum-Pinned-37',
                        'SWYConverszGenAlbum-Custom Sort Key-38',
                        'SWYConverszGenAlbum-Custom Sort Ascending-39',
                        'SWYConverszGenAlbum-Is Prototype-40',
                        'SWYConverszGenAlbum-Project Document Type-41',
                        'SWYConverszGenAlbum-Custom Query Type-42',
                        'SWYConverszGenAlbum-Trashed State-43',
                        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-45',
                        'SWYConverszGenAlbum-Privacy State-46')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash',        
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
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_29ALBUMLISTS z29AlbumLists ON z29AlbumLists.Z_29ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z29AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('SWYConverszGenAlbum-Creation Date-1', 'datetime'),
                        ('SWYConverszGenAlbum-Start Date-2', 'datetime'),
                        ('SWYConverszGenAlbum-End Date-3', 'datetime'),
                        'zAsset- Conversation= zGenAlbum_zPK-4',
                        'SWYConverszGenAlbum- Import Session ID-SWY-5',
                        'SWYzGenAlbum-Imported by Bundle Identifier-6',
                        'zAsset-zPK-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
                        'zAsset-Syndication State-13',
                        'zAsset-Bundle Scope-14',
                        'zAddAssetAttr.Imported by Bundle Identifier-15',
                        'zAddAssetAttr-Imported By Display Name-16',
                        'zAsset-Visibility State-17',
                        'zAsset-Saved Asset Type-18',
                        'zAddAssetAttr-Share Type-19',
                        'zAsset-Active Library Scope Participation State-20',
                        ('zAsset- SortToken -CameraRoll-21', 'datetime'),
                        ('zAsset-Added Date-22', 'datetime'),
                        ('zCldMast-Creation Date-23', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-24',
                        'zAddAssetAttr-EXIF-String-25',
                        ('zAsset-Modification Date-26', 'datetime'),
                        ('zAsset-Last Shared Date-27', 'datetime'),
                        ('zAsset-Trashed Date-28', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-29',
                        'zAddAssetAttr-zPK-30',
                        'zAsset-UUID = store.cloudphotodb-31',
                        'zAddAssetAttr-Original Stable Hash-32',
                        'zAddAssetAttr.Adjusted Stable Hash-33',
                        'SWYConverszGenAlbum-Album Kind-34',
                        'SWYConverszGenAlbum-Cloud_Local_State-35',
                        'SWYConverszGenAlbum- Syndicate-36',
                        'SWYConverszGenAlbum-Sync Event Order Key-37',
                        'SWYConverszGenAlbum-Pinned-38',
                        'SWYConverszGenAlbum-Custom Sort Key-39',
                        'SWYConverszGenAlbum-Custom Sort Ascending-40',
                        'SWYConverszGenAlbum-Is Prototype-41',
                        'SWYConverszGenAlbum-Project Document Type-42',
                        'SWYConverszGenAlbum-Custom Query Type-43',
                        'SWYConverszGenAlbum-Trashed State-44',
                        ('SWYConverszGenAlbum-Trash Date-45', 'datetime'),
                        'SWYConverszGenAlbum-Cloud Delete State-46',
                        'SWYConverszGenAlbum-Privacy State-47')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
