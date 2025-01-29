__artifacts_v2__ = {
    'Ph2_1AssetBasicGenAlbumDataPhDaPsql': {
        'name': 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql',
        'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for basic asset and album data.'
                       ' The results may contain multiple records per ZASSET table Z_PK value and supports iOS 11-18.'
                       ' Use 2-Non-Shared-Album-2 in the search box to view Non-Shared Albums Assets.'
                       ' Use 1505-Shared-Album-1505 in the search box to view Shared Albums Assets.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 in the search box to view'
                       ' Shared with You Conversation Identifiers Assets.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-A-Asset_Basic_Data',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    },
    'Ph2_2AssetBasicConversationDataSyndPL': {
        'name': 'Ph2.2-Asset Basic Data & Convers Data-SyndPL',
        'description': 'Parses basic asset row data from -Syndication.photoslibrary-database-Photos.sqlite'
                       ' for basic asset and album data. The results may contain multiple records'
                       ' per ZASSET table Z_PK value and supports iOS 11-18.'
                       ' Use -Non-Shared-Album-2 in the search box to view Non-Shared Albums Assets.'
                       ' Use 1505-Shared-Album-1505 in the search box to view Shared Albums Assets.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 in the search box to view'
                       ' Shared with You Conversation Identifiers Assets.',
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
def Ph2_1AssetBasicGenAlbumDataPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("12")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',       
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',       
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_20ASSETS z20Assets ON z20Assets.Z_27ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z20Assets.Z_20ALBUMS
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
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        ('zAsset-Modification Date-5', 'datetime'),
                        ('zAsset-Last Shared Date-6', 'datetime'),
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-11',
                        ('zAsset-Trashed Date-12', 'datetime'),
                        'zAsset-Saved Asset Type-13',
                        'zAddAssetAttr- Creator Bundle ID-14',
                        'zAddAssetAttr-Imported by-15',
                        'zAsset-Visibility State-16',
                        'zAddAssetAttr-Camera Captured Device-17',
                        'zCldMast-Cloud Local State-18',
                        ('zCldMast-Import Date-19', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-20',
                        ('zAsset-Cloud Batch Publish Date-21', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-22', 'datetime'),
                        'zAsset-Cloud Download Requests-23',
                        'zAsset-Cloud Batch ID-24',
                        'zAsset-Latitude-25',
                        'zAsset-Longitude-26',
                        'zAddAssetAttr-Location Hash-27',
                        'zAddAssetAttr-Shifted Location Valid-28',
                        'zAddAssetAttr-Shifted Location Data-29',
                        'zAddAssetAttr-Reverse Location Is Valid-30',
                        'zAddAssetAttr-Reverse Location Data-31',
                        ('zGenAlbum-Start Date-32', 'datetime'),
                        ('zGenAlbum-End Date-33', 'datetime'),
                        'zGenAlbum-Album Kind-34',
                        'zGenAlbum-Title-User&System Applied-35',
                        'zGenAlbum- Import Session ID-36',
                        'zGenAlbum-Cached Photos Count-37',
                        'zGenAlbum-Cached Videos Count-38',
                        'zGenAlbum-Cached Count-39',
                        'zGenAlbum-Trashed State-40',
                        ('zGenAlbum-Trash Date-41', 'datetime'),
                        'zGenAlbum-UUID-42',
                        'zGenAlbum-Cloud GUID-43',
                        'zAsset-zPK-44',
                        'zAddAssetAttr-zPK-45',
                        'zAsset-UUID = store.cloudphotodb-46',
                        'zAddAssetAttr-Master Fingerprint-47')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("12")) & (version.parse(iosversion) < version.parse("13")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT 
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',       
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',       
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_23ASSETS z23Assets ON z23Assets.Z_30ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z23Assets.Z_23ALBUMS
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
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        ('zAsset-Modification Date-5', 'datetime'),
                        ('zAsset-Last Shared Date-6', 'datetime'),
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-11',
                        ('zAsset-Trashed Date-12', 'datetime'),
                        'zAsset-Saved Asset Type-13',
                        'zAddAssetAttr- Creator Bundle ID-14',
                        'zAddAssetAttr-Imported by-15',
                        'zAsset-Visibility State-16',
                        'zAddAssetAttr-Camera Captured Device-17',
                        'zCldMast-Cloud Local State-18',
                        ('zCldMast-Import Date-19', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-20',
                        ('zAsset-Cloud Batch Publish Date-21', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-22', 'datetime'),
                        'zAsset-Cloud Download Requests-23',
                        'zAsset-Cloud Batch ID-24',
                        'zAsset-Latitude-25',
                        'zAsset-Longitude-26',
                        'zAddAssetAttr-Location Hash-27',
                        'zAddAssetAttr-Shifted Location Valid-28',
                        'zAddAssetAttr-Shifted Location Data-29',
                        'zAddAssetAttr-Reverse Location Is Valid-30',
                        'zAddAssetAttr-Reverse Location Data-31',
                        ('zGenAlbum-Start Date-32', 'datetime'),
                        ('zGenAlbum-End Date-33', 'datetime'),
                        'zGenAlbum-Album Kind-34',
                        'zGenAlbum-Title-User&System Applied-35',
                        'zGenAlbum- Import Session ID-36',
                        'zGenAlbum-Cached Photos Count-37',
                        'zGenAlbum-Cached Videos Count-38',
                        'zGenAlbum-Cached Count-39',
                        'zGenAlbum-Trashed State-40',
                        ('zGenAlbum-Trash Date-41', 'datetime'),
                        'zGenAlbum-UUID-42',
                        'zGenAlbum-Cloud GUID-43',
                        'zAsset-zPK-44',
                        'zAddAssetAttr-zPK-45',
                        'zAsset-UUID = store.cloudphotodb-46',
                        'zAddAssetAttr-Master Fingerprint-47')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_34ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Saved Asset Type-15',
                        'zAddAssetAttr- Creator Bundle ID-16',
                        'zAddAssetAttr-Imported by-17',
                        'zCldMast-Imported By-18',
                        'zAsset-Visibility State-19',
                        'zExtAttr-Camera Make-20',
                        'zExtAttr-Camera Model-21',
                        'zExtAttr-Lens Model-22',
                        'zAddAssetAttr-Camera Captured Device-23',
                        'zAddAssetAttr-Share Type-24',
                        'zCldMast-Cloud Local State-25',
                        ('zCldMast-Import Date-26', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-27', 'datetime'),
                        'zAddAssetAttr-Import Session ID-28',
                        ('zAddAssetAttr-Alt Import Image Date-29', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-30',
                        ('zAsset-Cloud Batch Publish Date-31', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-32', 'datetime'),
                        'zAsset-Cloud Download Requests-33',
                        'zAsset-Cloud Batch ID-34',
                        'zAsset-Latitude-35',
                        'zExtAttr-Latitude-36',
                        'zAsset-Longitude-37',
                        'zExtAttr-Longitude-38',
                        'zAddAssetAttr-Location Hash-39',
                        'zAddAssetAttr-Shifted Location Valid-40',
                        'zAddAssetAttr-Shifted Location Data-41',
                        'zAddAssetAttr-Reverse Location Is Valid-42',
                        'zAddAssetAttr-Reverse Location Data-43',
                        'AAAzCldMastMedData-zOPT-44',
                        'zAddAssetAttr-Media Metadata Type-45',
                        'AAAzCldMastMedData-Data-46',
                        'CldMasterzCldMastMedData-zOPT-47',
                        'zCldMast-Media Metadata Type-48',
                        'CMzCldMastMedData-Data-49',
                        ('zGenAlbum-Start Date-50', 'datetime'),
                        ('zGenAlbum-End Date-51', 'datetime'),
                        'zGenAlbum-Album Kind-52',
                        'zGenAlbum-Title-User&System Applied-53',
                        'zGenAlbum- Import Session ID-54',
                        'zGenAlbum-Cached Photos Count-55',
                        'zGenAlbum-Cached Videos Count-56',
                        'zGenAlbum-Cached Count-57',
                        'zGenAlbum-Trashed State-58',
                        ('zGenAlbum-Trash Date-59', 'datetime'),
                        'zGenAlbum-UUID-60',
                        'zGenAlbum-Cloud GUID-61',
                        'zAsset-zPK-62',
                        'zAddAssetAttr-zPK-63',
                        'zAsset-UUID = store.cloudphotodb-64',
                        'zAddAssetAttr-Master Fingerprint-65')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',        
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Saved Asset Type-15',
                        'zAddAssetAttr-Creator Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zAddAssetAttr-Imported by-18',
                        'zCldMast-Imported by Bundle ID-19',
                        'zCldMast-Imported by Display Name-20',
                        'zCldMast-Imported By-21',
                        'zAsset-Visibility State-22',
                        'zExtAttr-Camera Make-23',
                        'zExtAttr-Camera Model-24',
                        'zExtAttr-Lens Model-25',
                        'zAsset-Derived Camera Capture Device-26',
                        'zAddAssetAttr-Camera Captured Device-27',
                        'zAddAssetAttr-Share Type-28',
                        'zCldMast-Cloud Local State-29',
                        ('zCldMast-Import Date-30', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-31', 'datetime'),
                        'zAddAssetAttr-Import Session ID-32',
                        ('zAddAssetAttr-Alt Import Image Date-33', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-34',
                        ('zAsset-Cloud Batch Publish Date-35', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-36', 'datetime'),
                        'zAsset-Cloud Download Requests-37',
                        'zAsset-Cloud Batch ID-38',
                        'zAsset-Latitude-39',
                        'zExtAttr-Latitude-40',
                        'zAsset-Longitude-41',
                        'zExtAttr-Longitude-42',
                        'zAddAssetAttr-GPS Horizontal Accuracy-43',
                        'zAddAssetAttr-Location Hash-44',
                        'zAddAssetAttr-Shifted Location Valid-45',
                        'zAddAssetAttr-Shifted Location Data-46',
                        'zAddAssetAttr-Reverse Location Is Valid-47',
                        'zAddAssetAttr-Reverse Location Data-48',
                        'AAAzCldMastMedData-zOPT-49',
                        'zAddAssetAttr-Media Metadata Type-50',
                        'AAAzCldMastMedData-Data-51',
                        'CldMasterzCldMastMedData-zOPT-52',
                        'zCldMast-Media Metadata Type-53',
                        'CMzCldMastMedData-Data-54',
                        ('zGenAlbum-Creation Date-55', 'datetime'),
                        ('zGenAlbum-Start Date-56', 'datetime'),
                        ('zGenAlbum-End Date-57', 'datetime'),
                        'zGenAlbum-Album Kind-58',
                        'zGenAlbum-Title-User&System Applied-59',
                        'zGenAlbum- Import Session ID-60',
                        'zGenAlbum-Creator Bundle Identifier-61',
                        'zGenAlbum-Cached Photos Count-62',
                        'zGenAlbum-Cached Videos Count-63',
                        'zGenAlbum-Cached Count-64',
                        'zGenAlbum-Trashed State-65',
                        ('zGenAlbum-Trash Date-66', 'datetime'),
                        'zGenAlbum-UUID-67',
                        'zGenAlbum-Cloud GUID-68',
                        'zAsset-zPK-69',
                        'zAddAssetAttr-zPK-70',
                        'zAsset-UUID = store.cloudphotodb-71',
                        'zAddAssetAttr-Master Fingerprint-72')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z27Assets.Z_27ALBUMS
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                        'zAsset- Conversation= zGenAlbum_zPK-14',
                        'SWYConverszGenAlbum- Import Session ID-15',
                        'zAsset-Syndication State-16',
                        ('zAsset-Trashed Date-17', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-18',
                        'zAsset-Saved Asset Type-19',
                        'zAddAssetAttr-Imported by Bundle ID-20',
                        'zAddAssetAttr-Imported By Display Name-21',
                        'zAddAssetAttr-Imported by-22',
                        'zCldMast-Imported by Bundle ID-23',
                        'zCldMast-Imported by Display Name-24',
                        'zCldMast-Imported By-25',
                        'zAsset-Visibility State-26',
                        'zExtAttr-Camera Make-27',
                        'zExtAttr-Camera Model-28',
                        'zExtAttr-Lens Model-29',
                        'zAsset-Derived Camera Capture Device-30',
                        'zAddAssetAttr-Camera Captured Device-31',
                        'zAddAssetAttr-Share Type-32',
                        'zCldMast-Cloud Local State-33',
                        ('zCldMast-Import Date-34', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-35', 'datetime'),
                        'zAddAssetAttr-Import Session ID-36',
                        ('zAddAssetAttr-Alt Import Image Date-37', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-38',
                        ('zAsset-Cloud Batch Publish Date-39', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-40', 'datetime'),
                        'zAsset-Cloud Download Requests-41',
                        'zAsset-Cloud Batch ID-42',
                        'zAsset-Latitude-43',
                        'zExtAttr-Latitude-44',
                        'zAsset-Longitude-45',
                        'zExtAttr-Longitude-46',
                        'zAddAssetAttr-GPS Horizontal Accuracy-47',
                        'zAddAssetAttr-Location Hash-48',
                        'zAddAssetAttr-Shifted Location Valid-49',
                        'zAddAssetAttr-Shifted Location Data-50',
                        'zAddAssetAttr-Reverse Location Is Valid-51',
                        'zAddAssetAttr-Reverse Location Data-52',
                        'AAAzCldMastMedData-zOPT-53',
                        'zAddAssetAttr-Media Metadata Type-54',
                        'AAAzCldMastMedData-Data-55',
                        'CldMasterzCldMastMedData-zOPT-56',
                        'zCldMast-Media Metadata Type-57',
                        'CMzCldMastMedData-Data-58',
                        'zAsset-Bundle Scope-59',
                        ('zGenAlbum-Creation Date-60', 'datetime'),
                        ('zGenAlbum-Start Date-61', 'datetime'),
                        ('zGenAlbum-End Date-62', 'datetime'),
                        'zGenAlbum-Album Kind-63',
                        'zGenAlbum-Title-User&System Applied-64',
                        'zGenAlbum- Import Session ID-65',
                        'zGenAlbum-Imported by Bundle Identifier-66',
                        'zGenAlbum-Cached Photos Count-67',
                        'zGenAlbum-Cached Videos Count-68',
                        'zGenAlbum-Cached Count-69',
                        'zGenAlbum-Trashed State-70',
                        ('zGenAlbum-Trash Date-71', 'datetime'),
                        'zGenAlbum-UUID-72',
                        'zGenAlbum-Cloud GUID-73',
                        'zAsset-zPK-74',
                        'zAddAssetAttr-zPK-75',
                        'zAsset-UUID = store.cloudphotodb-76',
                        'zAddAssetAttr-Master Fingerprint-77')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                        'zAsset- Conversation= zGenAlbum_zPK-14',
                        'SWYConverszGenAlbum- Import Session ID-15',
                        'zAsset-Syndication State-16',
                        ('zAsset-Trashed Date-17', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-18',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-19',
                        'zAsset-Saved Asset Type-20',
                        'zAddAssetAttr-Imported by Bundle ID-21',
                        'zAddAssetAttr-Imported By Display Name-22',
                        'zAddAssetAttr-Imported by-23',
                        'zCldMast-Imported by Bundle ID-24',
                        'zCldMast-Imported by Display Name-25',
                        'zCldMast-Imported By-26',
                        'zAsset-Visibility State-27',
                        'zExtAttr-Camera Make-28',
                        'zExtAttr-Camera Model-29',
                        'zExtAttr-Lens Model-30',
                        'zAsset-Derived Camera Capture Device-31',
                        'zAddAssetAttr-Camera Captured Device-32',
                        'zAddAssetAttr-Share Type-33',
                        'zCldMast-Cloud Local State-34',
                        ('zCldMast-Import Date-35', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-36', 'datetime'),
                        'zAddAssetAttr-Import Session ID-37',
                        ('zAddAssetAttr-Alt Import Image Date-38', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-39',
                        ('zAsset-Cloud Batch Publish Date-40', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-41', 'datetime'),
                        'zAsset-Cloud Download Requests-42',
                        'zAsset-Cloud Batch ID-43',
                        'zAsset-Latitude-44',
                        'zExtAttr-Latitude-45',
                        'zAsset-Longitude-46',
                        'zExtAttr-Longitude-47',
                        'zAddAssetAttr-GPS Horizontal Accuracy-48',
                        'zAddAssetAttr-Location Hash-49',
                        'zAddAssetAttr-Shifted Location Valid-50',
                        'zAddAssetAttr-Shifted Location Data-51',
                        'zAddAssetAttr-Reverse Location Is Valid-52',
                        'zAddAssetAttr-Reverse Location Data-53',
                        'AAAzCldMastMedData-zOPT-54',
                        'zAddAssetAttr-Media Metadata Type-55',
                        'AAAzCldMastMedData-Data-56',
                        'CldMasterzCldMastMedData-zOPT-57',
                        'zCldMast-Media Metadata Type-58',
                        'CMzCldMastMedData-Data-59',
                        'zAsset-Bundle Scope-60',
                        ('zGenAlbum-Creation Date-61', 'datetime'),
                        ('zGenAlbum-Start Date-62', 'datetime'),
                        ('zGenAlbum-End Date-63', 'datetime'),
                        'zGenAlbum-Album Kind-64',
                        'zGenAlbum-Title-User&System Applied-65',
                        'zGenAlbum- Import Session ID-66',
                        'zGenAlbum-Imported by Bundle Identifier-67',
                        'zGenAlbum-Cached Photos Count-68',
                        'zGenAlbum-Cached Videos Count-69',
                        'zGenAlbum-Cached Count-70',
                        'zGenAlbum-Trashed State-71',
                        ('zGenAlbum-Trash Date-72', 'datetime'),
                        'zGenAlbum-UUID-73',
                        'zGenAlbum-Cloud GUID-74',
                        'zAsset-Active Library Scope Participation State-75',
                        'zAsset-zPK-76',
                        'zAddAssetAttr-zPK-77',
                        'zAsset-UUID = store.cloudphotodb-78',
                        'zAddAssetAttr-Master Fingerprint-79')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("17")) & (version.parse(iosversion) < version.parse("17.6")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        ('zAddAssetAttr-Last Viewed Date-9', 'datetime'),
                        'zAsset-Directory-Path-10',
                        'zAsset-Filename-11',
                        'zAddAssetAttr- Original Filename-12',
                        'zCldMast- Original Filename-13',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                        'zAsset- Conversation= zGenAlbum_zPK-15',
                        'SWYConverszGenAlbum- Import Session ID-16',
                        'zAsset-Syndication State-17',
                        ('zAsset-Trashed Date-18', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-19',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-20',
                        'zAsset-Saved Asset Type-21',
                        'zAddAssetAttr-Imported by Bundle ID-22',
                        'zAddAssetAttr-Imported By Display Name-23',
                        'zAddAssetAttr-Imported by-24',
                        'zCldMast-Imported by Bundle ID-25',
                        'zCldMast-Imported by Display Name-26',
                        'zCldMast-Imported By-27',
                        'zAsset-Visibility State-28',
                        'zExtAttr-Camera Make-29',
                        'zExtAttr-Camera Model-30',
                        'zExtAttr-Lens Model-31',
                        'zAsset-Derived Camera Capture Device-32',
                        'zAddAssetAttr-Camera Captured Device-33',
                        'zAddAssetAttr-Share Type-34',
                        'zCldMast-Cloud Local State-35',
                        ('zCldMast-Import Date-36', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-37', 'datetime'),
                        'zAddAssetAttr-Import Session ID-38',
                        ('zAddAssetAttr-Alt Import Image Date-39', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-40',
                        ('zAsset-Cloud Batch Publish Date-41', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-42', 'datetime'),
                        'zAsset-Cloud Download Requests-43',
                        'zAsset-Cloud Batch ID-44',
                        'zAsset-Latitude-45',
                        'zExtAttr-Latitude-46',
                        'zAsset-Longitude-47',
                        'zExtAttr-Longitude-48',
                        'zAddAssetAttr-GPS Horizontal Accuracy-49',
                        'zAddAssetAttr-Location Hash-50',
                        'zAddAssetAttr-Shifted Location Valid-51',
                        'zAddAssetAttr-Shifted Location Data-52',
                        'zAddAssetAttr-Reverse Location Is Valid-53',
                        'zAddAssetAttr-Reverse Location Data-54',
                        'AAAzCldMastMedData-zOPT-55',
                        'zAddAssetAttr-Media Metadata Type-56',
                        'AAAzCldMastMedData-Data-57',
                        'CldMasterzCldMastMedData-zOPT-58',
                        'zCldMast-Media Metadata Type-59',
                        'CMzCldMastMedData-Data-60',
                        'zAsset-Bundle Scope-61',
                        ('zGenAlbum-Creation Date-62', 'datetime'),
                        ('zGenAlbum-Start Date-63', 'datetime'),
                        ('zGenAlbum-End Date-64', 'datetime'),
                        'zGenAlbum-Album Kind-65',
                        'zGenAlbum-Title-User&System Applied-66',
                        'zGenAlbum- Import Session ID-67',
                        'zGenAlbum-Imported by Bundle Identifier-68',
                        'zGenAlbum-Cached Photos Count-69',
                        'zGenAlbum-Cached Videos Count-70',
                        'zGenAlbum-Cached Count-71',
                        'zGenAlbum-Trashed State-72',
                        ('zGenAlbum-Trash Date-73', 'datetime'),
                        'zGenAlbum-UUID-74',
                        'zGenAlbum-Cloud GUID-75',
                        'zAsset-Active Library Scope Participation State-76',
                        'zAsset-zPK-77',
                        'zAddAssetAttr-zPK-78',
                        'zAsset-UUID = store.cloudphotodb-79',
                        'zAddAssetAttr-Master Fingerprint-80')
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
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_29ASSETS z29Assets ON z29Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z29Assets.Z_29ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        ('zAddAssetAttr-Last Viewed Date-9', 'datetime'),
                        'zAsset-Directory-Path-10',
                        'zAsset-Filename-11',
                        'zAddAssetAttr- Original Filename-12',
                        'zCldMast- Original Filename-13',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                        'zAsset- Conversation= zGenAlbum_zPK-15',
                        'SWYConverszGenAlbum- Import Session ID-16',
                        'zAsset-Syndication State-17',
                        ('zAsset-Trashed Date-18', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-19',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-20',
                        'zAsset-Saved Asset Type-21',
                        'zAddAssetAttr-Imported by Bundle ID-22',
                        'zAddAssetAttr-Imported By Display Name-23',
                        'zAddAssetAttr-Imported by-24',
                        'zCldMast-Imported by Bundle ID-25',
                        'zCldMast-Imported by Display Name-26',
                        'zCldMast-Imported By-27',
                        'zAsset-Visibility State-28',
                        'zExtAttr-Camera Make-29',
                        'zExtAttr-Camera Model-30',
                        'zExtAttr-Lens Model-31',
                        'zAsset-Derived Camera Capture Device-32',
                        'zAddAssetAttr-Camera Captured Device-33',
                        'zAddAssetAttr-Share Type-34',
                        'zCldMast-Cloud Local State-35',
                        ('zCldMast-Import Date-36', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-37', 'datetime'),
                        'zAddAssetAttr-Import Session ID-38',
                        ('zAddAssetAttr-Alt Import Image Date-39', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-40',
                        ('zAsset-Cloud Batch Publish Date-41', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-42', 'datetime'),
                        'zAsset-Cloud Download Requests-43',
                        'zAsset-Cloud Batch ID-44',
                        'zAsset-Latitude-45',
                        'zExtAttr-Latitude-46',
                        'zAsset-Longitude-47',
                        'zExtAttr-Longitude-48',
                        'zAddAssetAttr-GPS Horizontal Accuracy-49',
                        'zAddAssetAttr-Location Hash-50',
                        'zAddAssetAttr-Shifted Location Valid-51',
                        'zAddAssetAttr-Shifted Location Data-52',
                        'zAddAssetAttr-Reverse Location Is Valid-53',
                        'zAddAssetAttr-Reverse Location Data-54',
                        'AAAzCldMastMedData-zOPT-55',
                        'zAddAssetAttr-Media Metadata Type-56',
                        'AAAzCldMastMedData-Data-57',
                        'CldMasterzCldMastMedData-zOPT-58',
                        'zCldMast-Media Metadata Type-59',
                        'CMzCldMastMedData-Data-60',
                        'zAsset-Bundle Scope-61',
                        ('zGenAlbum-Creation Date-62', 'datetime'),
                        ('zGenAlbum-Start Date-63', 'datetime'),
                        ('zGenAlbum-End Date-64', 'datetime'),
                        'zGenAlbum-Album Kind-65',
                        'zGenAlbum-Title-User&System Applied-66',
                        'zGenAlbum- Import Session ID-67',
                        'zGenAlbum-Imported by Bundle Identifier-68',
                        'zGenAlbum-Cached Photos Count-69',
                        'zGenAlbum-Cached Videos Count-70',
                        'zGenAlbum-Cached Count-71',
                        'zGenAlbum-Trashed State-72',
                        ('zGenAlbum-Trash Date-73', 'datetime'),
                        'zGenAlbum-UUID-74',
                        'zGenAlbum-Cloud GUID-75',
                        'zAsset-Active Library Scope Participation State-76',
                        'zAsset-zPK-77',
                        'zAddAssetAttr-zPK-78',
                        'zAsset-UUID = store.cloudphotodb-79',
                        'zAddAssetAttr-Master Fingerprint-80')
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
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',        
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        CASE zAsset.ZISRECENTLYSAVED
            WHEN 0 THEN '0-Not_Recenlty_Saved_Still_Testing-0'
            WHEN 1 THEN '1-Recently_Saved_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZISRECENTLYSAVED || ''
        END AS 'zAsset-Is_Recently_Saved',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',
        zAsset.ZCAPTURESESSIONIDENTIFIER AS 'zAsset-Capture_Session_Identifier',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_30ASSETS z30Assets ON z30Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z30Assets.Z_30ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                row[82], row[83]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        ('zAddAssetAttr-Last Viewed Date-9', 'datetime'),
                        'zAsset-Directory-Path-10',
                        'zAsset-Filename-11',
                        'zAddAssetAttr- Original Filename-12',
                        'zCldMast- Original Filename-13',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                        'zAsset- Conversation= zGenAlbum_zPK-15',
                        'SWYConverszGenAlbum- Import Session ID-16',
                        'zAsset-Syndication State-17',
                        ('zAsset-Trashed Date-18', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-19',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-20',
                        'zAsset-Is_Recently_Saved-21',
                        'zAsset-Saved Asset Type-22',
                        'zAddAssetAttr-Imported by Bundle ID-23',
                        'zAddAssetAttr-Imported By Display Name-24',
                        'zAddAssetAttr-Imported by-25',
                        'zCldMast-Imported by Bundle ID-26',
                        'zCldMast-Imported by Display Name-27',
                        'zCldMast-Imported By-28',
                        'zAsset-Visibility State-29',
                        'zExtAttr-Camera Make-30',
                        'zExtAttr-Camera Model-31',
                        'zExtAttr-Lens Model-32',
                        'zAsset-Derived Camera Capture Device-33',
                        'zAddAssetAttr-Camera Captured Device-34',
                        'zAsset-Capture_Session_Identifier-35',
                        'zAddAssetAttr-Share Type-36',
                        'zCldMast-Cloud Local State-37',
                        ('zCldMast-Import Date-38', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-39', 'datetime'),
                        'zAddAssetAttr-Import Session ID-40',
                        ('zAddAssetAttr-Alt Import Image Date-41', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-42',
                        ('zAsset-Cloud Batch Publish Date-43', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-44', 'datetime'),
                        'zAsset-Cloud Download Requests-45',
                        'zAsset-Cloud Batch ID-46',
                        'zAsset-Latitude-47',
                        'zExtAttr-Latitude-48',
                        'zAsset-Longitude-49',
                        'zExtAttr-Longitude-50',
                        'zAddAssetAttr-GPS Horizontal Accuracy-51',
                        'zAddAssetAttr-Location Hash-52',
                        'zAddAssetAttr-Shifted Location Valid-53',
                        'zAddAssetAttr-Shifted Location Data-54',
                        'zAddAssetAttr-Reverse Location Is Valid-55',
                        'zAddAssetAttr-Reverse Location Data-56',
                        'AAAzCldMastMedData-zOPT-57',
                        'zAddAssetAttr-Media Metadata Type-58',
                        'AAAzCldMastMedData-Data-59',
                        'CldMasterzCldMastMedData-zOPT-60',
                        'zCldMast-Media Metadata Type-61',
                        'CMzCldMastMedData-Data-62',
                        'zAsset-Bundle Scope-63',
                        ('zGenAlbum-Creation Date-64', 'datetime'),
                        ('zGenAlbum-Start Date-65', 'datetime'),
                        ('zGenAlbum-End Date-66', 'datetime'),
                        'zGenAlbum-Album Kind-67',
                        'zGenAlbum-Title-User&System Applied-68',
                        'zGenAlbum- Import Session ID-69',
                        'zGenAlbum-Imported by Bundle Identifier-70',
                        'zGenAlbum-Cached Photos Count-71',
                        'zGenAlbum-Cached Videos Count-72',
                        'zGenAlbum-Cached Count-73',
                        'zGenAlbum-Trashed State-74',
                        ('zGenAlbum-Trash Date-75', 'datetime'),
                        'zGenAlbum-UUID-76',
                        'zGenAlbum-Cloud GUID-77',
                        'zAsset-Active Library Scope Participation State-78',
                        'zAsset-zPK-79',
                        'zAddAssetAttr-zPK-80',
                        'zAsset-UUID = store.cloudphotodb-81',
                        'zAddAssetAttr-Original Stable Hash-82',
                        'zAddAssetAttr.Adjusted Stable Hash-83')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph2_2AssetBasicConversationDataSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("12")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',       
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',       
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON
             zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_20ASSETS z20Assets ON z20Assets.Z_27ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z20Assets.Z_20ALBUMS
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
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        ('zAsset-Modification Date-5', 'datetime'),
                        ('zAsset-Last Shared Date-6', 'datetime'),
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-11',
                        ('zAsset-Trashed Date-12', 'datetime'),
                        'zAsset-Saved Asset Type-13',
                        'zAddAssetAttr- Creator Bundle ID-14',
                        'zAddAssetAttr-Imported by-15',
                        'zAsset-Visibility State-16',
                        'zAddAssetAttr-Camera Captured Device-17',
                        'zCldMast-Cloud Local State-18',
                        ('zCldMast-Import Date-19', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-20',
                        ('zAsset-Cloud Batch Publish Date-21', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-22', 'datetime'),
                        'zAsset-Cloud Download Requests-23',
                        'zAsset-Cloud Batch ID-24',
                        'zAsset-Latitude-25',
                        'zAsset-Longitude-26',
                        'zAddAssetAttr-Location Hash-27',
                        'zAddAssetAttr-Shifted Location Valid-28',
                        'zAddAssetAttr-Shifted Location Data-29',
                        'zAddAssetAttr-Reverse Location Is Valid-30',
                        'zAddAssetAttr-Reverse Location Data-31',
                        ('zGenAlbum-Start Date-32', 'datetime'),
                        ('zGenAlbum-End Date-33', 'datetime'),
                        'zGenAlbum-Album Kind-34',
                        'zGenAlbum-Title-User&System Applied-35',
                        'zGenAlbum- Import Session ID-36',
                        'zGenAlbum-Cached Photos Count-37',
                        'zGenAlbum-Cached Videos Count-38',
                        'zGenAlbum-Cached Count-39',
                        'zGenAlbum-Trashed State-40',
                        ('zGenAlbum-Trash Date-41', 'datetime'),
                        'zGenAlbum-UUID-42',
                        'zGenAlbum-Cloud GUID-43',
                        'zAsset-zPK-44',
                        'zAddAssetAttr-zPK-45',
                        'zAsset-UUID = store.cloudphotodb-46',
                        'zAddAssetAttr-Master Fingerprint-47')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("12")) & (version.parse(iosversion) < version.parse("13")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT 
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',       
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',       
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON
             zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_23ASSETS z23Assets ON z23Assets.Z_30ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z23Assets.Z_23ALBUMS
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
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        ('zAsset-Modification Date-5', 'datetime'),
                        ('zAsset-Last Shared Date-6', 'datetime'),
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-11',
                        ('zAsset-Trashed Date-12', 'datetime'),
                        'zAsset-Saved Asset Type-13',
                        'zAddAssetAttr- Creator Bundle ID-14',
                        'zAddAssetAttr-Imported by-15',
                        'zAsset-Visibility State-16',
                        'zAddAssetAttr-Camera Captured Device-17',
                        'zCldMast-Cloud Local State-18',
                        ('zCldMast-Import Date-19', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-20',
                        ('zAsset-Cloud Batch Publish Date-21', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-22', 'datetime'),
                        'zAsset-Cloud Download Requests-23',
                        'zAsset-Cloud Batch ID-24',
                        'zAsset-Latitude-25',
                        'zAsset-Longitude-26',
                        'zAddAssetAttr-Location Hash-27',
                        'zAddAssetAttr-Shifted Location Valid-28',
                        'zAddAssetAttr-Shifted Location Data-29',
                        'zAddAssetAttr-Reverse Location Is Valid-30',
                        'zAddAssetAttr-Reverse Location Data-31',
                        ('zGenAlbum-Start Date-32', 'datetime'),
                        ('zGenAlbum-End Date-33', 'datetime'),
                        'zGenAlbum-Album Kind-34',
                        'zGenAlbum-Title-User&System Applied-35',
                        'zGenAlbum- Import Session ID-36',
                        'zGenAlbum-Cached Photos Count-37',
                        'zGenAlbum-Cached Videos Count-38',
                        'zGenAlbum-Cached Count-39',
                        'zGenAlbum-Trashed State-40',
                        ('zGenAlbum-Trash Date-41', 'datetime'),
                        'zGenAlbum-UUID-42',
                        'zGenAlbum-Cloud GUID-43',
                        'zAsset-zPK-44',
                        'zAddAssetAttr-zPK-45',
                        'zAsset-UUID = store.cloudphotodb-46',
                        'zAddAssetAttr-Master Fingerprint-47')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON
             zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_34ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Saved Asset Type-15',
                        'zAddAssetAttr- Creator Bundle ID-16',
                        'zAddAssetAttr-Imported by-17',
                        'zCldMast-Imported By-18',
                        'zAsset-Visibility State-19',
                        'zExtAttr-Camera Make-20',
                        'zExtAttr-Camera Model-21',
                        'zExtAttr-Lens Model-22',
                        'zAddAssetAttr-Camera Captured Device-23',
                        'zAddAssetAttr-Share Type-24',
                        'zCldMast-Cloud Local State-25',
                        ('zCldMast-Import Date-26', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-27', 'datetime'),
                        'zAddAssetAttr-Import Session ID-28',
                        'zAddAssetAttr-Alt Import Image Date-29',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-30',
                        ('zAsset-Cloud Batch Publish Date-31', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-32', 'datetime'),
                        'zAsset-Cloud Download Requests-33',
                        'zAsset-Cloud Batch ID-34',
                        'zAsset-Latitude-35',
                        'zExtAttr-Latitude-36',
                        'zAsset-Longitude-37',
                        'zExtAttr-Longitude-38',
                        'zAddAssetAttr-Location Hash-39',
                        'zAddAssetAttr-Shifted Location Valid-40',
                        'zAddAssetAttr-Shifted Location Data-41',
                        'zAddAssetAttr-Reverse Location Is Valid-42',
                        'zAddAssetAttr-Reverse Location Data-43',
                        'AAAzCldMastMedData-zOPT-44',
                        'zAddAssetAttr-Media Metadata Type-45',
                        'AAAzCldMastMedData-Data-46',
                        'CldMasterzCldMastMedData-zOPT-47',
                        'zCldMast-Media Metadata Type-48',
                        'CMzCldMastMedData-Data-49',
                        ('zGenAlbum-Start Date-50', 'datetime'),
                        ('zGenAlbum-End Date-51', 'datetime'),
                        'zGenAlbum-Album Kind-52',
                        'zGenAlbum-Title-User&System Applied-53',
                        'zGenAlbum- Import Session ID-54',
                        'zGenAlbum-Cached Photos Count-55',
                        'zGenAlbum-Cached Videos Count-56',
                        'zGenAlbum-Cached Count-57',
                        'zGenAlbum-Trashed State-58',
                        ('zGenAlbum-Trash Date-59', 'datetime'),
                        'zGenAlbum-UUID-60',
                        'zGenAlbum-Cloud GUID-61',
                        'zAsset-zPK-62',
                        'zAddAssetAttr-zPK-63',
                        'zAsset-UUID = store.cloudphotodb-64',
                        'zAddAssetAttr-Master Fingerprint-65')
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',        
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON
             zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
        ORDER BY zAsset.ZDATECREATED
        '''
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        ('zAsset-Trashed Date-13', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-14',
                        'zAsset-Saved Asset Type-15',
                        'zAddAssetAttr-Creator Bundle ID-16',
                        'zAddAssetAttr-Imported By Display Name-17',
                        'zAddAssetAttr-Imported by-18',
                        'zCldMast-Imported by Bundle ID-19',
                        'zCldMast-Imported by Display Name-20',
                        'zCldMast-Imported By-21',
                        'zAsset-Visibility State-22',
                        'zExtAttr-Camera Make-23',
                        'zExtAttr-Camera Model-24',
                        'zExtAttr-Lens Model-25',
                        'zAsset-Derived Camera Capture Device-26',
                        'zAddAssetAttr-Camera Captured Device-27',
                        'zAddAssetAttr-Share Type-28',
                        'zCldMast-Cloud Local State-29',
                        ('zCldMast-Import Date-30', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-31', 'datetime'),
                        'zAddAssetAttr-Import Session ID-32',
                        ('zAddAssetAttr-Alt Import Image Date-33', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-34',
                        ('zAsset-Cloud Batch Publish Date-35', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-36', 'datetime'),
                        'zAsset-Cloud Download Requests-37',
                        'zAsset-Cloud Batch ID-38',
                        'zAsset-Latitude-39',
                        'zExtAttr-Latitude-40',
                        'zAsset-Longitude-41',
                        'zExtAttr-Longitude-42',
                        'zAddAssetAttr-GPS Horizontal Accuracy-43',
                        'zAddAssetAttr-Location Hash-44',
                        'zAddAssetAttr-Shifted Location Valid-45',
                        'zAddAssetAttr-Shifted Location Data-46',
                        'zAddAssetAttr-Reverse Location Is Valid-47',
                        'zAddAssetAttr-Reverse Location Data-48',
                        'AAAzCldMastMedData-zOPT-49',
                        'zAddAssetAttr-Media Metadata Type-50',
                        'AAAzCldMastMedData-Data-51',
                        'CldMasterzCldMastMedData-zOPT-52',
                        'zCldMast-Media Metadata Type-53',
                        'CMzCldMastMedData-Data-54',
                        ('zGenAlbum-Creation Date-55', 'datetime'),
                        ('zGenAlbum-Start Date-56', 'datetime'),
                        ('zGenAlbum-End Date-57', 'datetime'),
                        'zGenAlbum-Album Kind-58',
                        'zGenAlbum-Title-User&System Applied-59',
                        'zGenAlbum- Import Session ID-60',
                        'zGenAlbum-Creator Bundle Identifier-61',
                        'zGenAlbum-Cached Photos Count-62',
                        'zGenAlbum-Cached Videos Count-63',
                        'zGenAlbum-Cached Count-64',
                        'zGenAlbum-Trashed State-65',
                        ('zGenAlbum-Trash Date-66', 'datetime'),
                        'zGenAlbum-UUID-67',
                        'zGenAlbum-Cloud GUID-68',
                        'zAsset-zPK-69',
                        'zAddAssetAttr-zPK-70',
                        'zAsset-UUID = store.cloudphotodb-71',
                        'zAddAssetAttr-Master Fingerprint-72')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON
             zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z27Assets.Z_27ALBUMS
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                        'zAsset- Conversation= zGenAlbum_zPK-14',
                        'SWYConverszGenAlbum- Import Session ID-15',
                        'zAsset-Syndication State-16',
                        ('zAsset-Trashed Date-17', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-18',
                        'zAsset-Saved Asset Type-19',
                        'zAddAssetAttr-Imported by Bundle ID-20',
                        'zAddAssetAttr-Imported By Display Name-21',
                        'zAddAssetAttr-Imported by-22',
                        'zCldMast-Imported by Bundle ID-23',
                        'zCldMast-Imported by Display Name-24',
                        'zCldMast-Imported By-25',
                        'zAsset-Visibility State-26',
                        'zExtAttr-Camera Make-27',
                        'zExtAttr-Camera Model-28',
                        'zExtAttr-Lens Model-29',
                        'zAsset-Derived Camera Capture Device-30',
                        'zAddAssetAttr-Camera Captured Device-31',
                        'zAddAssetAttr-Share Type-32',
                        'zCldMast-Cloud Local State-33',
                        ('zCldMast-Import Date-34', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-35', 'datetime'),
                        'zAddAssetAttr-Import Session ID-36',
                        ('zAddAssetAttr-Alt Import Image Date-37', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-38',
                        ('zAsset-Cloud Batch Publish Date-39', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-40', 'datetime'),
                        'zAsset-Cloud Download Requests-41',
                        'zAsset-Cloud Batch ID-42',
                        'zAsset-Latitude-43',
                        'zExtAttr-Latitude-44',
                        'zAsset-Longitude-45',
                        'zExtAttr-Longitude-46',
                        'zAddAssetAttr-GPS Horizontal Accuracy-47',
                        'zAddAssetAttr-Location Hash-48',
                        'zAddAssetAttr-Shifted Location Valid-49',
                        'zAddAssetAttr-Shifted Location Data-50',
                        'zAddAssetAttr-Reverse Location Is Valid-51',
                        'zAddAssetAttr-Reverse Location Data-52',
                        'AAAzCldMastMedData-zOPT-53',
                        'zAddAssetAttr-Media Metadata Type-54',
                        'AAAzCldMastMedData-Data-55',
                        'CldMasterzCldMastMedData-zOPT-56',
                        'zCldMast-Media Metadata Type-57',
                        'CMzCldMastMedData-Data-58',
                        'zAsset-Bundle Scope-59',
                        ('zGenAlbum-Creation Date-60', 'datetime'),
                        ('zGenAlbum-Start Date-61', 'datetime'),
                        ('zGenAlbum-End Date-62', 'datetime'),
                        'zGenAlbum-Album Kind-63',
                        'zGenAlbum-Title-User&System Applied-64',
                        'zGenAlbum- Import Session ID-65',
                        'zGenAlbum-Imported by Bundle Identifier-66',
                        'zGenAlbum-Cached Photos Count-67',
                        'zGenAlbum-Cached Videos Count-68',
                        'zGenAlbum-Cached Count-69',
                        'zGenAlbum-Trashed State-70',
                        ('zGenAlbum-Trash Date-71', 'datetime'),
                        'zGenAlbum-UUID-72',
                        'zGenAlbum-Cloud GUID-73',
                        'zAsset-zPK-74',
                        'zAddAssetAttr-zPK-75',
                        'zAsset-UUID = store.cloudphotodb-76',
                        'zAddAssetAttr-Master Fingerprint-77')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'       
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON
             zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        'zAsset-Directory-Path-9',
                        'zAsset-Filename-10',
                        'zAddAssetAttr- Original Filename-11',
                        'zCldMast- Original Filename-12',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                        'zAsset- Conversation= zGenAlbum_zPK-14',
                        'SWYConverszGenAlbum- Import Session ID-15',
                        'zAsset-Syndication State-16',
                        ('zAsset-Trashed Date-17', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-18',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-19',
                        'zAsset-Saved Asset Type-20',
                        'zAddAssetAttr-Imported by Bundle ID-21',
                        'zAddAssetAttr-Imported By Display Name-22',
                        'zAddAssetAttr-Imported by-23',
                        'zCldMast-Imported by Bundle ID-24',
                        'zCldMast-Imported by Display Name-25',
                        'zCldMast-Imported By-26',
                        'zAsset-Visibility State-27',
                        'zExtAttr-Camera Make-28',
                        'zExtAttr-Camera Model-29',
                        'zExtAttr-Lens Model-30',
                        'zAsset-Derived Camera Capture Device-31',
                        'zAddAssetAttr-Camera Captured Device-32',
                        'zAddAssetAttr-Share Type-33',
                        'zCldMast-Cloud Local State-34',
                        ('zCldMast-Import Date-35', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-36', 'datetime'),
                        'zAddAssetAttr-Import Session ID-37',
                        ('zAddAssetAttr-Alt Import Image Date-38', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-39',
                        ('zAsset-Cloud Batch Publish Date-40', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-41', 'datetime'),
                        ('zAsset-Cloud Download Requests-42', 'datetime'),
                        'zAsset-Cloud Batch ID-43',
                        'zAsset-Latitude-44',
                        'zExtAttr-Latitude-45',
                        'zAsset-Longitude-46',
                        'zExtAttr-Longitude-47',
                        'zAddAssetAttr-GPS Horizontal Accuracy-48',
                        'zAddAssetAttr-Location Hash-49',
                        'zAddAssetAttr-Shifted Location Valid-50',
                        'zAddAssetAttr-Shifted Location Data-51',
                        'zAddAssetAttr-Reverse Location Is Valid-52',
                        'zAddAssetAttr-Reverse Location Data-53',
                        'AAAzCldMastMedData-zOPT-54',
                        'zAddAssetAttr-Media Metadata Type-55',
                        'AAAzCldMastMedData-Data-56',
                        'CldMasterzCldMastMedData-zOPT-57',
                        'zCldMast-Media Metadata Type-58',
                        'CMzCldMastMedData-Data-59',
                        'zAsset-Bundle Scope-60',
                        ('zGenAlbum-Creation Date-61', 'datetime'),
                        ('zGenAlbum-Start Date-62', 'datetime'),
                        ('zGenAlbum-End Date-63', 'datetime'),
                        'zGenAlbum-Album Kind-64',
                        'zGenAlbum-Title-User&System Applied-65',
                        'zGenAlbum- Import Session ID-66',
                        'zGenAlbum-Imported by Bundle Identifier-67',
                        'zGenAlbum-Cached Photos Count-68',
                        'zGenAlbum-Cached Videos Count-69',
                        'zGenAlbum-Cached Count-70',
                        'zGenAlbum-Trashed State-71',
                        ('zGenAlbum-Trash Date-72', 'datetime'),
                        'zGenAlbum-UUID-73',
                        'zGenAlbum-Cloud GUID-74',
                        'zAsset-Active Library Scope Participation State-75',
                        'zAsset-zPK-76',
                        'zAddAssetAttr-zPK-77',
                        'zAsset-UUID = store.cloudphotodb-78',
                        'zAddAssetAttr-Master Fingerprint-79')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("17")) & (version.parse(iosversion) < version.parse("17.6")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',  
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        ('zAddAssetAttr-Last Viewed Date-9', 'datetime'),
                        'zAsset-Directory-Path-10',
                        'zAsset-Filename-11',
                        'zAddAssetAttr- Original Filename-12',
                        'zCldMast- Original Filename-13',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                        'zAsset- Conversation= zGenAlbum_zPK-15',
                        'SWYConverszGenAlbum- Import Session ID-16',
                        'zAsset-Syndication State-17',
                        ('zAsset-Trashed Date-18', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-19',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-20',
                        'zAsset-Saved Asset Type-21',
                        'zAddAssetAttr-Imported by Bundle ID-22',
                        'zAddAssetAttr-Imported By Display Name-23',
                        'zAddAssetAttr-Imported by-24',
                        'zCldMast-Imported by Bundle ID-25',
                        'zCldMast-Imported by Display Name-26',
                        'zCldMast-Imported By-27',
                        'zAsset-Visibility State-28',
                        'zExtAttr-Camera Make-29',
                        'zExtAttr-Camera Model-30',
                        'zExtAttr-Lens Model-31',
                        'zAsset-Derived Camera Capture Device-32',
                        'zAddAssetAttr-Camera Captured Device-33',
                        'zAddAssetAttr-Share Type-34',
                        'zCldMast-Cloud Local State-35',
                        ('zCldMast-Import Date-36', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-37', 'datetime'),
                        'zAddAssetAttr-Import Session ID-38',
                        ('zAddAssetAttr-Alt Import Image Date-39', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-40',
                        ('zAsset-Cloud Batch Publish Date-41', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-42', 'datetime'),
                        'zAsset-Cloud Download Requests-43',
                        'zAsset-Cloud Batch ID-44',
                        'zAsset-Latitude-45',
                        'zExtAttr-Latitude-46',
                        'zAsset-Longitude-47',
                        'zExtAttr-Longitude-48',
                        'zAddAssetAttr-GPS Horizontal Accuracy-49',
                        'zAddAssetAttr-Location Hash-50',
                        'zAddAssetAttr-Shifted Location Valid-51',
                        'zAddAssetAttr-Shifted Location Data-52',
                        'zAddAssetAttr-Reverse Location Is Valid-53',
                        'zAddAssetAttr-Reverse Location Data-54',
                        'AAAzCldMastMedData-zOPT-55',
                        'zAddAssetAttr-Media Metadata Type-56',
                        'AAAzCldMastMedData-Data-57',
                        'CldMasterzCldMastMedData-zOPT-58',
                        'zCldMast-Media Metadata Type-59',
                        'CMzCldMastMedData-Data-60',
                        'zAsset-Bundle Scope-61',
                        ('zGenAlbum-Creation Date-62', 'datetime'),
                        ('zGenAlbum-Start Date-63', 'datetime'),
                        ('zGenAlbum-End Date-64', 'datetime'),
                        'zGenAlbum-Album Kind-65',
                        'zGenAlbum-Title-User&System Applied-66',
                        'zGenAlbum- Import Session ID-67',
                        'zGenAlbum-Imported by Bundle Identifier-68',
                        'zGenAlbum-Cached Photos Count-69',
                        'zGenAlbum-Cached Videos Count-70',
                        'zGenAlbum-Cached Count-71',
                        'zGenAlbum-Trashed State-72',
                        ('zGenAlbum-Trash Date-73', 'datetime'),
                        'zGenAlbum-UUID-74',
                        'zGenAlbum-Cloud GUID-75',
                        'zAsset-Active Library Scope Participation State-76',
                        'zAsset-zPK-77',
                        'zAddAssetAttr-zPK-78',
                        'zAsset-UUID = store.cloudphotodb-79',
                        'zAddAssetAttr-Master Fingerprint-80')
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
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',        
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'        
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_29ASSETS z29Assets ON z29Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z29Assets.Z_29ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        ('zAddAssetAttr-Last Viewed Date-9', 'datetime'),
                        'zAsset-Directory-Path-10',
                        'zAsset-Filename-11',
                        'zAddAssetAttr- Original Filename-12',
                        'zCldMast- Original Filename-13',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                        'zAsset- Conversation= zGenAlbum_zPK-15',
                        'SWYConverszGenAlbum- Import Session ID-16',
                        'zAsset-Syndication State-17',
                        ('zAsset-Trashed Date-18', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-19',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-20',
                        'zAsset-Saved Asset Type-21',
                        'zAddAssetAttr-Imported by Bundle ID-22',
                        'zAddAssetAttr-Imported By Display Name-23',
                        'zAddAssetAttr-Imported by-24',
                        'zCldMast-Imported by Bundle ID-25',
                        'zCldMast-Imported by Display Name-26',
                        'zCldMast-Imported By-27',
                        'zAsset-Visibility State-28',
                        'zExtAttr-Camera Make-29',
                        'zExtAttr-Camera Model-30',
                        'zExtAttr-Lens Model-31',
                        'zAsset-Derived Camera Capture Device-32',
                        'zAddAssetAttr-Camera Captured Device-33',
                        'zAddAssetAttr-Share Type-34',
                        'zCldMast-Cloud Local State-35',
                        ('zCldMast-Import Date-36', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-37', 'datetime'),
                        'zAddAssetAttr-Import Session ID-38',
                        ('zAddAssetAttr-Alt Import Image Date-39', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-40',
                        ('zAsset-Cloud Batch Publish Date-41', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-42', 'datetime'),
                        'zAsset-Cloud Download Requests-43',
                        'zAsset-Cloud Batch ID-44',
                        'zAsset-Latitude-45',
                        'zExtAttr-Latitude-46',
                        'zAsset-Longitude-47',
                        'zExtAttr-Longitude-48',
                        'zAddAssetAttr-GPS Horizontal Accuracy-49',
                        'zAddAssetAttr-Location Hash-50',
                        'zAddAssetAttr-Shifted Location Valid-51',
                        'zAddAssetAttr-Shifted Location Data-52',
                        'zAddAssetAttr-Reverse Location Is Valid-53',
                        'zAddAssetAttr-Reverse Location Data-54',
                        'AAAzCldMastMedData-zOPT-55',
                        'zAddAssetAttr-Media Metadata Type-56',
                        'AAAzCldMastMedData-Data-57',
                        'CldMasterzCldMastMedData-zOPT-58',
                        'zCldMast-Media Metadata Type-59',
                        'CMzCldMastMedData-Data-60',
                        'zAsset-Bundle Scope-61',
                        ('zGenAlbum-Creation Date-62', 'datetime'),
                        ('zGenAlbum-Start Date-63', 'datetime'),
                        ('zGenAlbum-End Date-64', 'datetime'),
                        'zGenAlbum-Album Kind-65',
                        'zGenAlbum-Title-User&System Applied-66',
                        'zGenAlbum- Import Session ID-67',
                        'zGenAlbum-Imported by Bundle Identifier-68',
                        'zGenAlbum-Cached Photos Count-69',
                        'zGenAlbum-Cached Videos Count-70',
                        'zGenAlbum-Cached Count-71',
                        'zGenAlbum-Trashed State-72',
                        ('zGenAlbum-Trash Date-73', 'datetime'),
                        'zGenAlbum-UUID-74',
                        'zGenAlbum-Cloud GUID-75',
                        'zAsset-Active Library Scope Participation State-76',
                        'zAsset-zPK-77',
                        'zAddAssetAttr-zPK-78',
                        'zAsset-UUID = store.cloudphotodb-79',
                        'zAddAssetAttr-Master Fingerprint-80')
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
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZTIMEZONEOFFSET AS 'zAddAssetAttr-Time Zone Offset',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',        
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        CASE zAsset.ZISRECENTLYSAVED
            WHEN 0 THEN '0-Not_Recenlty_Saved_Still_Testing-0'
            WHEN 1 THEN '1-Recently_Saved_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZISRECENTLYSAVED || ''
        END AS 'zAsset-Is_Recently_Saved',
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
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr-Imported by Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',   
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zCldMast.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zCldMast-Imported by Bundle ID',
        zCldMast.ZIMPORTEDBYDISPLAYNAME AS 'zCldMast-Imported by Display Name',
        CASE zCldMast.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZIMPORTEDBY || ''
        END AS 'zCldMast-Imported By',                      
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zExtAttr.ZLENSMODEL AS 'zExtAttr-Lens Model',
        CASE zAsset.ZDERIVEDCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZDERIVEDCAMERACAPTUREDEVICE || ''
        END AS 'zAsset-Derived Camera Capture Device',
        CASE zAddAssetAttr.ZCAMERACAPTUREDEVICE
            WHEN 0 THEN '0-Back-Camera-Other-0'
            WHEN 1 THEN '1-Front-Camera-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCAMERACAPTUREDEVICE || ''
        END AS 'zAddAssetAttr-Camera Captured Device',
        zAsset.ZCAPTURESESSIONIDENTIFIER AS 'zAsset-Capture_Session_Identifier',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zCldMast.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-Not Synced with Cloud-0'
            WHEN 1 THEN '1-Pending Upload-1'
            WHEN 2 THEN '2-StillTesting'
            WHEN 3 THEN '3-Synced with Cloud-3'
            ELSE 'Unknown-New-Value!: ' || zCldMast.ZCLOUDLOCALSTATE || ''
        END AS 'zCldMast-Cloud Local State',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        zAddAssetAttr.ZIMPORTSESSIONID AS 'zAddAssetAttr-Import Session ID',
        DateTime(zAddAssetAttr.ZALTERNATEIMPORTIMAGEDATE + 978307200, 'UNIXEPOCH')
         AS 'zAddAssetAttr-Alt Import Image Date',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        DateTime(zAsset.ZCLOUDBATCHPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Batch Publish Date',
        DateTime(zAsset.ZCLOUDSERVERPUBLISHDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Server Publish Date',
        zAsset.ZCLOUDDOWNLOADREQUESTS AS 'zAsset-Cloud Download Requests',
        zAsset.ZCLOUDBATCHID AS 'zAsset-Cloud Batch ID',
        CASE zAsset.ZLATITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLATITUDE
        END AS 'zAsset-Latitude',
        zExtAttr.ZLATITUDE AS 'zExtAttr-Latitude',
        CASE zAsset.ZLONGITUDE
            WHEN -180.0 THEN '-180.0'
            ELSE zAsset.ZLONGITUDE
        END AS 'zAsset-Longitude',
        zExtAttr.ZLONGITUDE AS 'zExtAttr-Longitude',
        CASE zAddAssetAttr.ZGPSHORIZONTALACCURACY
            WHEN -1.0 THEN '-1.0'
            ELSE zAddAssetAttr.ZGPSHORIZONTALACCURACY
        END AS 'zAddAssetAttr-GPS Horizontal Accuracy',
        zAddAssetAttr.ZLOCATIONHASH AS 'zAddAssetAttr-Location Hash',
        CASE zAddAssetAttr.ZSHIFTEDLOCATIONISVALID
            WHEN 0 THEN '0-Shifted Location Not Valid-0'
            WHEN 1 THEN '1-Shifted Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHIFTEDLOCATIONISVALID || ''
        END AS 'zAddAssetAttr-Shifted Location Valid',
        CASE
            WHEN zAddAssetAttr.ZSHIFTEDLOCATIONDATA > 0 THEN 'zAddAssetAttr-Shifted_Location_Data_has_Plist'
            ELSE 'zAddAssetArrt-Shifted_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Shifted Location Data',
        CASE zAddAssetAttr.ZREVERSELOCATIONDATAISVALID
            WHEN 0 THEN '0-Reverse Location Not Valid-0'
            WHEN 1 THEN '1-Reverse Location Valid-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZREVERSELOCATIONDATAISVALID || ''
        END AS 'zAddAssetAttr-Reverse Location Is Valid',		
        CASE
            WHEN zAddAssetAttr.ZREVERSELOCATIONDATA > 0 THEN 'zAddAssetAttr-Reverse_Location_Data_has_Plist'
            ELSE 'zAddAssetAttr-Reverse_Location_Data_Empty-NULL'
        END AS 'zAddAssetAttr-Reverse Location Data',
        CASE AAAzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Cloud-1'
            WHEN 2 THEN '2-StillTesting-This Device-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || AAAzCldMastMedData.Z_OPT || ''
        END AS 'AAAzCldMastMedData-zOPT',
        zAddAssetAttr.ZMEDIAMETADATATYPE AS 'zAddAssetAttr-Media Metadata Type',
        CASE
            WHEN AAAzCldMastMedData.ZDATA > 0 THEN 'AAAzCldMastMedData-Data_has_Plist'
            ELSE 'AAAzCldMastMedData-Data_Empty-NULL'
        END AS 'AAAzCldMastMedData-Data',
        CASE CMzCldMastMedData.Z_OPT
            WHEN 1 THEN '1-StillTesting-Has_CldMastAsset-1'
            WHEN 2 THEN '2-StillTesting-Local_Asset-2'
            WHEN 3 THEN '3-StillTesting-Muted-3'
            WHEN 4 THEN '4-StillTesting-Unknown-4'
            WHEN 5 THEN '5-StillTesting-Unknown-5'
            ELSE 'Unknown-New-Value!: ' || CMzCldMastMedData.Z_OPT || ''
        END AS 'CldMasterzCldMastMedData-zOPT',
        zCldMast.ZMEDIAMETADATATYPE AS 'zCldMast-Media Metadata Type',		
        CASE
            WHEN CMzCldMastMedData.ZDATA > 0 THEN 'CMzCldMastMedData-Data_has_Plist'
            ELSE 'CMzCldMastMedData-Data_Empty-NULL'
        END AS 'CMzCldMastMedData-Data',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'    
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_30ASSETS z30Assets ON z30Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z30Assets.Z_30ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA AAAzCldMastMedData ON
             AAAzCldMastMedData.Z_PK = zAddAssetAttr.ZMEDIAMETADATA
            LEFT JOIN ZCLOUDMASTERMEDIAMETADATA CMzCldMastMedData ON
             CMzCldMastMedData.Z_PK = zCldMast.ZMEDIAMETADATA
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                  row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                  row[82], row[83]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-Time Zone Offset-5',
                        'zAddAssetAttr-EXIF-String-6',
                        ('zAsset-Modification Date-7', 'datetime'),
                        ('zAsset-Last Shared Date-8', 'datetime'),
                        ('zAddAssetAttr-Last Viewed Date-9', 'datetime'),
                        'zAsset-Directory-Path-10',
                        'zAsset-Filename-11',
                        'zAddAssetAttr- Original Filename-12',
                        'zCldMast- Original Filename-13',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                        'zAsset- Conversation= zGenAlbum_zPK-15',
                        'SWYConverszGenAlbum- Import Session ID-16',
                        'zAsset-Syndication State-17',
                        ('zAsset-Trashed Date-18', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-19',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-20',
                        'zAsset-Is_Recently_Saved-21',
                        'zAsset-Saved Asset Type-22',
                        'zAddAssetAttr-Imported by Bundle ID-23',
                        'zAddAssetAttr-Imported By Display Name-24',
                        'zAddAssetAttr-Imported by-25',
                        'zCldMast-Imported by Bundle ID-26',
                        'zCldMast-Imported by Display Name-27',
                        'zCldMast-Imported By-28',
                        'zAsset-Visibility State-29',
                        'zExtAttr-Camera Make-30',
                        'zExtAttr-Camera Model-31',
                        'zExtAttr-Lens Model-32',
                        'zAsset-Derived Camera Capture Device-33',
                        'zAddAssetAttr-Camera Captured Device-34',
                        'zAsset-Capture_Session_Identifier-35',
                        'zAddAssetAttr-Share Type-36',
                        'zCldMast-Cloud Local State-37',
                        ('zCldMast-Import Date-38', 'datetime'),
                        ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-39', 'datetime'),
                        'zAddAssetAttr-Import Session ID-40',
                        ('zAddAssetAttr-Alt Import Image Date-41', 'datetime'),
                        'zCldMast-Import Session ID- AirDrop-StillTesting-42',
                        ('zAsset-Cloud Batch Publish Date-43', 'datetime'),
                        ('zAsset-Cloud Server Publish Date-44', 'datetime'),
                        'zAsset-Cloud Download Requests-45',
                        'zAsset-Cloud Batch ID-46',
                        'zAsset-Latitude-47',
                        'zExtAttr-Latitude-48',
                        'zAsset-Longitude-49',
                        'zExtAttr-Longitude-50',
                        'zAddAssetAttr-GPS Horizontal Accuracy-51',
                        'zAddAssetAttr-Location Hash-52',
                        'zAddAssetAttr-Shifted Location Valid-53',
                        'zAddAssetAttr-Shifted Location Data-54',
                        'zAddAssetAttr-Reverse Location Is Valid-55',
                        'zAddAssetAttr-Reverse Location Data-56',
                        'AAAzCldMastMedData-zOPT-57',
                        'zAddAssetAttr-Media Metadata Type-58',
                        'AAAzCldMastMedData-Data-59',
                        'CldMasterzCldMastMedData-zOPT-60',
                        'zCldMast-Media Metadata Type-61',
                        'CMzCldMastMedData-Data-62',
                        'zAsset-Bundle Scope-63',
                        ('zGenAlbum-Creation Date-64', 'datetime'),
                        ('zGenAlbum-Start Date-65', 'datetime'),
                        ('zGenAlbum-End Date-66', 'datetime'),
                        'zGenAlbum-Album Kind-67',
                        'zGenAlbum-Title-User&System Applied-68',
                        'zGenAlbum- Import Session ID-69',
                        'zGenAlbum-Imported by Bundle Identifier-70',
                        'zGenAlbum-Cached Photos Count-71',
                        'zGenAlbum-Cached Videos Count-72',
                        'zGenAlbum-Cached Count-73',
                        'zGenAlbum-Trashed State-74',
                        ('zGenAlbum-Trash Date-75', 'datetime'),
                        'zGenAlbum-UUID-76',
                        'zGenAlbum-Cloud GUID-77',
                        'zAsset-Active Library Scope Participation State-78',
                        'zAsset-zPK-79',
                        'zAddAssetAttr-zPK-80',
                        'zAsset-UUID = store.cloudphotodb-81',
                        'zAddAssetAttr-Original Stable Hash-82',
                        'zAddAssetAttr.Adjusted Stable Hash-83')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
