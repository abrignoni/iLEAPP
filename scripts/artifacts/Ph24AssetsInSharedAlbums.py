__artifacts_v2__ = {
    'Ph24AssetinSharedAlbumsInvitesPhDaPsql': {
        'name': 'Ph24-Assets in Shared Albums & Invites-PhDaPsql',
        'description': 'Parses Assets in Shared Albums found in PhotoData-Photos.sqlite and supports iOS 18.'
                       ' Parses limited asset data with full non-shared album data.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-E-Asset_In_Albums',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc

@artifact_processor
def Ph24AssetinSharedAlbumsInvitesPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZCLOUDMETADATA AS 'zGenAlbum-Cloud Metadata-HEX NSKeyed Plist',        
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',  
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_20ASSETS z20Assets ON z20Assets.Z_27ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z20Assets.Z_20ALBUMS
            LEFT JOIN Z_19ALBUMLISTS z19AlbumLists ON z19AlbumLists.Z_19ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z19AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Creator Bundle ID-6',
                        'zAsset-Visibility State-7',
                        'zAsset-Saved Asset Type-8',
                        ('zAsset- SortToken -CameraRoll-9', 'datetime'),
                        ('zAsset-Added Date-10', 'datetime'),
                        ('zCldMast-Creation Date-11', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-12',
                        'zAddAssetAttr-EXIF-String-13',
                        ('zAsset-Modification Date-14', 'datetime'),
                        ('zAsset-Last Shared Date-15', 'datetime'),
                        ('zAsset-Trashed Date-16', 'datetime'),
                        'zAddAssetAttr-zPK-17',
                        'zAsset-UUID = store.cloudphotodb-18',
                        'zAddAssetAttr-Master Fingerprint-19',
                        ('zGenAlbum-Cloud Creation Date-20', 'datetime'),
                        ( 'zGenAlbum-Start Date-21', 'datetime'),
                        ('zGenAlbum-End Date-22', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-23', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-24',
                        'zGenAlbum-UUID-25',
                        'zGenAlbum-Cloud GUID-26',
                        'zGenAlbum-Cloud Metadata-HEX NSKeyed Plist-27',
                        'zGenAlbum-Pending Items Count-28',
                        'zGenAlbum-Pending Items Type-29',
                        'zGenAlbum- Cached Photos Count-30',
                        'zGenAlbum- Cached Videos Count-31',
                        'zGenAlbum- Cached Count-32',
                        'zGenAlbum-Has Unseen Content-33',
                        'zGenAlbum-Unseen Asset Count-34',
                        'zGenAlbum-zENT- Entity-35',
                        'zGenAlbum-Album Kind-36',
                        'zGenAlbum-Cloud_Local_State-37',
                        'zGenAlbum-Sync Event Order Key-38',
                        'zGenAlbum-is Owned-39',
                        'zGenAlbum-Cloud Relationship State-40',
                        'zGenAlbum-Cloud Relationship State Local-41',
                        'zGenAlbum-Cloud Owner Mail Key-42',
                        'zGenAlbum-Cloud Owner First Name-43',
                        'zGenAlbum-Cloud Owner Last Name-44',
                        'zGenAlbum-Cloud Owner Full Name-45',
                        'zGenAlbum-Cloud Person ID-46',
                        'zGenAlbum-Cloud Owner Hashed Person ID-47',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-48',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-49',
                        'zGenAlbum-Cloud Album Sub Type-50',
                        ('zGenAlbum-Cloud Contribution Date-51', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-52', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-53',
                        'zGenAlbum-Pinned-54',
                        'zGenAlbum-Custom Sort Key-55',
                        'zGenAlbum-Custom Sort Ascending-56',
                        'zGenAlbum-Custom Query Type-57',
                        'zGenAlbum-Trashed State-58',
                        ('zGenAlbum-Trash Date-59', 'datetime'),
                        'zGenAlbum-Cloud Owner Whitelisted-60',
                        'zGenAlbum-Cloud Local Public URL Enabled-61',
                        'zGenAlbum-Cloud Public URL Enabled-62',
                        'zGenAlbum-Public URL-63',
                        'zGenAlbum-Key Asset Face Thumb Index-64',
                        'zGenAlbum-Custom Query Parameters-65',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-66',
                        'zCldShareAlbumInvRec-Invitation State Local-67',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-68',
                        ('zCldShareAlbumInvRec-Subscription Date-69', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-70',
                        'zCldShareAlbumInvRec-Invitee Last Name-71',
                        'zCldShareAlbumInvRec-Invitee Full Name-72',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-73',
                        'zCldShareAlbumInvRec-Invitee Email Key-74',
                        'zCldShareAlbumInvRec-Album GUID-75',
                        'zCldShareAlbumInvRec-Cloud GUID-76',
                        'zAlbumList-Needs Reordering Number-77')
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',  
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',              
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',      
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',  
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_23ASSETS z23Assets ON z23Assets.Z_30ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z23Assets.Z_23ALBUMS
            LEFT JOIN Z_22ALBUMLISTS z22AlbumLists ON z22AlbumLists.Z_22ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z22AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Creator Bundle ID-6',
                        'zAsset-Visibility State-7',
                        'zAsset-Saved Asset Type-8',
                        ('zAsset- SortToken -CameraRoll-9', 'datetime'),
                        ('zAsset-Added Date-10', 'datetime'),
                        ('zCldMast-Creation Date-11', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-12',
                        'zAddAssetAttr-EXIF-String-13',
                        ('zAsset-Modification Date-14', 'datetime'),
                        ('zAsset-Last Shared Date-15', 'datetime'),
                        ('zAsset-Trashed Date-16', 'datetime'),
                        'zAddAssetAttr-zPK-17',
                        'zAsset-UUID = store.cloudphotodb-18',
                        'zAddAssetAttr-Master Fingerprint-19',
                        ('zGenAlbum-Cloud Creation Date-20', 'datetime'),
                        ('zGenAlbum-Start Date-21', 'datetime'),
                        ('zGenAlbum-End Date-22', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-23', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-24',
                        'zGenAlbum-UUID-25',
                        'zGenAlbum-Cloud GUID-26',
                        'zGenAlbum-Pending Items Count-27',
                        'zGenAlbum-Pending Items Type-28',
                        'zGenAlbum- Cached Photos Count-29',
                        'zGenAlbum- Cached Videos Count-30',
                        'zGenAlbum- Cached Count-31',
                        'zGenAlbum-Has Unseen Content-32',
                        'zGenAlbum-Unseen Asset Count-33',
                        'zGenAlbum-zENT- Entity-34',
                        'zGenAlbum-Album Kind-35',
                        'zGenAlbum-Cloud_Local_State-36',
                        'zGenAlbum-Sync Event Order Key-37',
                        'zGenAlbum-is Owned-38',
                        'zGenAlbum-Cloud Relationship State-39',
                        'zGenAlbum-Cloud Relationship State Local-40',
                        'zGenAlbum-Cloud Owner Mail Key-41',
                        'zGenAlbum-Cloud Owner First Name-42',
                        'zGenAlbum-Cloud Owner Last Name-43',
                        'zGenAlbum-Cloud Owner Full Name-44',
                        'zGenAlbum-Cloud Person ID-45',
                        'zGenAlbum-Cloud Owner Hashed Person ID-46',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-47',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-48',
                        'zGenAlbum-Cloud Album Sub Type-49',
                        ('zGenAlbum-Cloud Contribution Date-50', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-51', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-52',
                        'zGenAlbum-Pinned-53',
                        'zGenAlbum-Custom Sort Key-54',
                        'zGenAlbum-Custom Sort Ascending-55',
                        'zGenAlbum-Custom Query Type-56',
                        'zGenAlbum-Trashed State-57',
                        ('zGenAlbum-Trash Date-58', 'datetime'),
                        'zGenAlbum-Cloud Delete State-59',
                        'zGenAlbum-Cloud Owner Whitelisted-60',
                        'zGenAlbum-Cloud Local Public URL Enabled-61',
                        'zGenAlbum-Cloud Public URL Enabled-62',
                        'zGenAlbum-Public URL-63',
                        'zGenAlbum-Key Asset Face Thumb Index-64',
                        'zGenAlbum-Custom Query Parameters-65',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-66',
                        'zCldShareAlbumInvRec-Invitation State Local-67',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-68',
                        ('zCldShareAlbumInvRec-Subscription Date-69', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-70',
                        'zCldShareAlbumInvRec-Invitee Last Name-71',
                        'zCldShareAlbumInvRec-Invitee Full Name-72',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-73',
                        'zCldShareAlbumInvRec-Invitee Email Key-74',
                        'zCldShareAlbumInvRec-Album GUID-75',
                        'zCldShareAlbumInvRec-Cloud GUID-76',
                        'zAlbumList-Needs Reordering Number-77')
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',   
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',        
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_34ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Creator Bundle ID-6',
                        'zAsset-Visibility State-7',
                        'zAsset-Saved Asset Type-8',
                        ('zAsset- SortToken -CameraRoll-9', 'datetime'),
                        ('zAsset-Added Date-10', 'datetime'),
                        ('zCldMast-Creation Date-11', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-12',
                        'zAddAssetAttr-EXIF-String-13',
                        ('zAsset-Modification Date-14', 'datetime'),
                        ('zAsset-Last Shared Date-15', 'datetime'),
                        ('zAsset-Trashed Date-16', 'datetime'),
                        'zAddAssetAttr-zPK-17',
                        'zAsset-UUID = store.cloudphotodb-18',
                        'zAddAssetAttr-Master Fingerprint-19',
                        ('zGenAlbum-Cloud Creation Date-20', 'datetime'),
                        ('zGenAlbum-Creation Date-21', 'datetime'),
                        ('zGenAlbum-Start Date-22', 'datetime'),
                        ('zGenAlbum-End Date-23', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-24', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-25',
                        'zGenAlbum-UUID-26',
                        'zGenAlbum-Cloud GUID-27',
                        'zGenAlbum-Pending Items Count-28',
                        'zGenAlbum-Pending Items Type-29',
                        'zGenAlbum- Cached Photos Count-30',
                        'zGenAlbum- Cached Videos Count-31',
                        'zGenAlbum- Cached Count-32',
                        'zGenAlbum-Has Unseen Content-33',
                        'zGenAlbum-Unseen Asset Count-34',
                        'zGenAlbum-zENT- Entity-35',
                        'zGenAlbum-Album Kind-36',
                        'zGenAlbum-Cloud_Local_State-37',
                        'zGenAlbum-Sync Event Order Key-38',
                        'zGenAlbum-is Owned-39',
                        'zGenAlbum-Cloud Relationship State-40',
                        'zGenAlbum-Cloud Relationship State Local-41',
                        'zGenAlbum-Cloud Owner Mail Key-42',
                        'zGenAlbum-Cloud Owner First Name-43',
                        'zGenAlbum-Cloud Owner Last Name-44',
                        'zGenAlbum-Cloud Owner Full Name-45',
                        'zGenAlbum-Cloud Person ID-46',
                        'zGenAlbum-Cloud Owner Hashed Person ID-47',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-48',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-49',
                        'zGenAlbum-Cloud Album Sub Type-50',
                        ('zGenAlbum-Cloud Contribution Date-51', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-52', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-53',
                        'zGenAlbum-Pinned-54',
                        'zGenAlbum-Custom Sort Key-55',
                        'zGenAlbum-Custom Sort Ascending-56',
                        'zGenAlbum-Project Document Type-57',
                        'zGenAlbum-Custom Query Type-58',
                        'zGenAlbum-Trashed State-59',
                        ('zGenAlbum-Trash Date-60', 'datetime'),
                        'zGenAlbum-Cloud Delete State-61',
                        'zGenAlbum-Cloud Owner Whitelisted-62',
                        'zGenAlbum-Cloud Local Public URL Enabled-63',
                        'zGenAlbum-Cloud Public URL Enabled-64',
                        'zGenAlbum-Public URL-65',
                        'zGenAlbum-Key Asset Face Thumb Index-66',
                        'zGenAlbum-Project Text Extension ID-67',
                        'zGenAlbum-User Query Data-68',
                        'zGenAlbum-Custom Query Parameters-69',
                        'zGenAlbum-Project Data-70',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-71',
                        'zCldShareAlbumInvRec-Invitation State Local-72',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-73',
                        ('zCldShareAlbumInvRec-Subscription Date-74', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-75',
                        'zCldShareAlbumInvRec-Invitee Last Name-76',
                        'zCldShareAlbumInvRec-Invitee Full Name-77',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-78',
                        'zCldShareAlbumInvRec-Invitee Email Key-79',
                        'zCldShareAlbumInvRec-Album GUID-80',
                        'zCldShareAlbumInvRec-Cloud GUID-81',
                        'zGenAlbum-Project Render UUID-82',
                        'zAlbumList-Needs Reordering Number-83')
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',              
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle ID',     
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                              row[82], row[83], row[84], row[85], row[86], row[87]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Creator Bundle ID-6',
                        'zAddAssetAttr-Imported By Display Name-7',
                        'zAsset-Visibility State-8',
                        'zAsset-Saved Asset Type-9',
                        'zAddAssetAttr-Share Type-10',
                        ('zAsset- SortToken -CameraRoll-11', 'datetime'),
                        ('zAsset-Added Date-12', 'datetime'),
                        ('zCldMast-Creation Date-13', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-14',
                        'zAddAssetAttr-EXIF-String-15',
                        ('zAsset-Modification Date-16', 'datetime'),
                        ('zAsset-Last Shared Date-17', 'datetime'),
                        ('zAsset-Trashed Date-18', 'datetime'),
                        'zAddAssetAttr-zPK-19',
                        'zAsset-UUID = store.cloudphotodb-20',
                        'zAddAssetAttr-Master Fingerprint-21',
                        ('zGenAlbum-Cloud Creation Date-22', 'datetime'),
                        ('zGenAlbum-Creation Date-23', 'datetime'),
                        ('zGenAlbum-Start Date-24', 'datetime'),
                        ('zGenAlbum-End Date-25', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-26', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-27',
                        'zGenAlbum-UUID-28',
                        'zGenAlbum-Cloud GUID-29',
                        'zGenAlbum-Creator Bundle ID-30',
                        'zGenAlbum-Pending Items Count-31',
                        'zGenAlbum-Pending Items Type-32',
                        'zGenAlbum- Cached Photos Count-33',
                        'zGenAlbum- Cached Videos Count-34',
                        'zGenAlbum- Cached Count-35',
                        'zGenAlbum-Has Unseen Content-36',
                        'zGenAlbum-Unseen Asset Count-37',
                        'zGenAlbum-zENT- Entity-38',
                        'zGenAlbum-Album Kind-39',
                        'zGenAlbum-Cloud_Local_State-40',
                        'zGenAlbum-Sync Event Order Key-41',
                        'zGenAlbum-is Owned-42',
                        'zGenAlbum-Cloud Relationship State-43',
                        'zGenAlbum-Cloud Relationship State Local-44',
                        'zGenAlbum-Cloud Owner Mail Key-45',
                        'zGenAlbum-Cloud Owner Frist Name-46',
                        'zGenAlbum-Cloud Owner Last Name-47',
                        'zGenAlbum-Cloud Owner Full Name-48',
                        'zGenAlbum-Cloud Person ID-49',
                        'zGenAlbum-Cloud Owner Hashed Person ID-50',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-51',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-52',
                        'zGenAlbum-Cloud Album Sub Type-53',
                        ('zGenAlbum-Cloud Contribution Date-54', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-55', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-56',
                        'zGenAlbum-Pinned-57',
                        'zGenAlbum-Custom Sort Key-58',
                        'zGenAlbum-Custom Sort Ascending-59',
                        'zGenAlbum-Is Prototype-60',
                        'zGenAlbum-Project Document Type-61',
                        'zGenAlbum-Custom Query Type-62',
                        'zGenAlbum-Trashed State-63',
                        ('zGenAlbum-Trash Date-64', 'datetime'),
                        'zGenAlbum-Cloud Delete State-65',
                        'zGenAlbum-Cloud Owner Whitelisted-66',
                        'zGenAlbum-Cloud Local Public URL Enabled-67',
                        'zGenAlbum-Cloud Public URL Enabled-68',
                        'zGenAlbum-Public URL-69',
                        'zGenAlbum-Key Asset Face Thumb Index-70',
                        'zGenAlbum-Project Text Extension ID-71',
                        'zGenAlbum-User Query Data-72',
                        'zGenAlbum-Custom Query Parameters-73',
                        'zGenAlbum-Project Data-74',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-75',
                        'zCldShareAlbumInvRec-Invitation State Local-76',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-77',
                        ('zCldShareAlbumInvRec-Subscription Date-78', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-79',
                        'zCldShareAlbumInvRec-Invitee Last Name-80',
                        'zCldShareAlbumInvRec-Invitee Full Name-81',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-82',
                        'zCldShareAlbumInvRec-Invitee Email Key-83',
                        'zCldShareAlbumInvRec-Album GUID-84',
                        'zCldShareAlbumInvRec-Cloud GUID-85',
                        'zGenAlbum-Project Render UUID-86',
                        'zAlbumList-Needs Reordering Number-87')
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',            
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',               
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z27Assets.Z_27ALBUMS
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                        'zAsset-Syndication State-7',
                        'zAsset-Bundle Scope-8',
                        'zAddAssetAttr- Imported by Bundle Identifier-9',
                        'zAddAssetAttr-Imported By Display Name-10',
                        'zAsset-Visibility State-11',
                        'zAsset-Saved Asset Type-12',
                        'zAddAssetAttr-Share Type-13',
                        ('zAsset- SortToken -CameraRoll-14', 'datetime'),
                        ('zAsset-Added Date-15', 'datetime'),
                        ('zCldMast-Creation Date-16', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-17',
                        'zAddAssetAttr-EXIF-String-18',
                        ('zAsset-Modification Date-19', 'datetime'),
                        ('zAsset-Last Shared Date-20', 'datetime'),
                        ('zAsset-Trashed Date-21', 'datetime'),
                        'zAddAssetAttr-zPK-22',
                        'zAsset-UUID = store.cloudphotodb-23',
                        'zAddAssetAttr-Master Fingerprint-24',
                        ('zGenAlbum-Cloud Creation Date-25', 'datetime'),
                        ('zGenAlbum-Creation Date-26', 'datetime'),
                        ('zGenAlbum-Start Date-27', 'datetime'),
                        ('zGenAlbum-End Date-28', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-29', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-30',
                        'zGenAlbum-UUID-31',
                        'zGenAlbum-Cloud GUID-32',
                        'zGenAlbum-Imported by Bundle Identifier-33',
                        'zGenAlbum-Pending Items Count-34',
                        'zGenAlbum-Pending Items Type-35',
                        'zGenAlbum- Cached Photos Count-36',
                        'zGenAlbum- Cached Videos Count-37',
                        'zGenAlbum- Cached Count-38',
                        'zGenAlbum-Has Unseen Content-39',
                        'zGenAlbum-Unseen Asset Count-40',
                        'zGenAlbum-zENT- Entity-41',
                        'zGenAlbum-Album Kind-42',
                        'zGenAlbum-Cloud_Local_State-43',
                        'zGenAlbum-Sync Event Order Key-44',
                        'zGenAlbum-is Owned-45',
                        'zGenAlbum-Cloud Relationship State-46',
                        'zGenAlbum-Cloud Relationship State Local-47',
                        'zGenAlbum-Cloud Owner Mail Key-48',
                        'zGenAlbum-Cloud Owner Frist Name-49',
                        'zGenAlbum-Cloud Owner Last Name-50',
                        'zGenAlbum-Cloud Owner Full Name-51',
                        'zGenAlbum-Cloud Person ID-52',
                        'zGenAlbum-Cloud Owner Hashed Person ID-53',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-54',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-55',
                        'zGenAlbum-Cloud Album Sub Type-56',
                        ('zGenAlbum-Cloud Contribution Date-57', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-58', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-59',
                        'zGenAlbum-Pinned-60',
                        'zGenAlbum-Custom Sort Key-61',
                        'zGenAlbum-Custom Sort Ascending-62',
                        'zGenAlbum-Is Prototype-63',
                        'zGenAlbum-Project Document Type-64',
                        'zGenAlbum-Custom Query Type-65',
                        'zGenAlbum-Trashed State-66',
                        ('zGenAlbum-Trash Date-67', 'datetime'),
                        'zGenAlbum-Cloud Delete State-68',
                        'zGenAlbum-Cloud Owner Whitelisted-69',
                        'zGenAlbum-Cloud Local Public URL Enabled-70',
                        'zGenAlbum-Cloud Public URL Enabled-71',
                        'zGenAlbum-Public URL-72',
                        'zGenAlbum-Key Asset Face Thumb Index-73',
                        'zGenAlbum-Project Text Extension ID-74',
                        'zGenAlbum-User Query Data-75',
                        'zGenAlbum-Custom Query Parameters-76',
                        'zGenAlbum-Project Data-77',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-78',
                        'zCldShareAlbumInvRec-Invitation State Local-79',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-80',
                        ('zCldShareAlbumInvRec-Subscription Date-81', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-82',
                        'zCldShareAlbumInvRec-Invitee Last Name-83',
                        'zCldShareAlbumInvRec-Invitee Full Name-84',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-85',
                        'zCldShareAlbumInvRec-Invitee Email Key-86',
                        'zCldShareAlbumInvRec-Album GUID-87',
                        'zCldShareAlbumInvRec-Cloud GUID-88',
                        'zGenAlbum-Project Render UUID-89',
                        'zAlbumList-Needs Reordering Number-90')
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',             
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',        
        CASE zGenAlbum.ZSEARCHINDEXREBUILDSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
        END AS 'zGenAlbum-Search Index Rebuild State',        
        CASE zGenAlbum.ZDUPLICATETYPE
            WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
            WHEN 1 THEN 'Duplicate Asset_Pending-Merge-1'
            WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZDUPLICATETYPE || ''
        END AS 'zGenAlbum-Duplicate Type',        
        CASE zGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPRIVACYSTATE || ''
        END AS 'zGenAlbum-Privacy State',        
        zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                        'zAsset-Syndication State-7',
                        'zAsset-Bundle Scope-8',
                        'zAddAssetAttr.Imported by Bundle Identifier-9',
                        'zAddAssetAttr-Imported By Display Name-10',
                        'zAsset-Visibility State-11',
                        'zAsset-Saved Asset Type-12',
                        'zAddAssetAttr-Share Type-13',
                        'zAsset-Active Library Scope Participation State-14',
                        ('zAsset- SortToken -CameraRoll-15', 'datetime'),
                        ('zAsset-Added Date-16', 'datetime'),
                        ('zCldMast-Creation Date-17', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-18',
                        'zAddAssetAttr-EXIF-String-19',
                        ('zAsset-Modification Date-20', 'datetime'),
                        ('zAsset-Last Shared Date-21', 'datetime'),
                        ('zAsset-Trashed Date-22', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-23',
                        'zAddAssetAttr-zPK-24',
                        'zAsset-UUID = store.cloudphotodb-25',
                        'zAddAssetAttr-Master Fingerprint-26',
                        ('zGenAlbum-Cloud Creation Date-27', 'datetime'),
                        ('zGenAlbum-Creation Date-28', 'datetime'),
                        ('zGenAlbum-Start Date-29', 'datetime'),
                        ('zGenAlbum-End Date-30', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-31', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-32',
                        'zGenAlbum-UUID-33',
                        'zGenAlbum-Cloud GUID-34',
                        'zGenAlbum-Imported by Bundle Identifier-35',
                        'zGenAlbum-Pending Items Count-36',
                        'zGenAlbum-Pending Items Type-37',
                        'zGenAlbum- Cached Photos Count-38',
                        'zGenAlbum- Cached Videos Count-39',
                        'zGenAlbum- Cached Count-40',
                        'zGenAlbum-Has Unseen Content-41',
                        'zGenAlbum-Unseen Asset Count-42',
                        'zGenAlbum-zENT- Entity-43',
                        'zGenAlbum-Album Kind-44',
                        'zGenAlbum-Cloud_Local_State-45',
                        'zGenAlbum-Sync Event Order Key-46',
                        'zGenAlbum-is Owned-47',
                        'zGenAlbum-Cloud Relationship State-48',
                        'zGenAlbum-Cloud Relationship State Local-49',
                        'zGenAlbum-Cloud Owner Mail Key-50',
                        'zGenAlbum-Cloud Owner First Name-51',
                        'zGenAlbum-Cloud Owner Last Name-52',
                        'zGenAlbum-Cloud Owner Full Name-53',
                        'zGenAlbum-Cloud Person ID-54',
                        'zGenAlbum-Cloud Owner Hashed Person ID-55',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-56',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-57',
                        'zGenAlbum-Cloud Album Sub Type-58',
                        ('zGenAlbum-Cloud Contribution Date-59', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-60', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-61',
                        'zGenAlbum-Pinned-62',
                        'zGenAlbum-Custom Sort Key-63',
                        'zGenAlbum-Custom Sort Ascending-64',
                        'zGenAlbum-Is Prototype-65',
                        'zGenAlbum-Project Document Type-66',
                        'zGenAlbum-Custom Query Type-67',
                        'zGenAlbum-Trashed State-68',
                        ('zGenAlbum-Trash Date-69', 'datetime'),
                        'zGenAlbum-Cloud Delete State-70',
                        'zGenAlbum-Cloud Owner Whitelisted-71',
                        'zGenAlbum-Cloud Local Public URL Enabled-72',
                        'zGenAlbum-Cloud Public URL Enabled-73',
                        'zGenAlbum-Public URL-74',
                        'zGenAlbum-Key Asset Face Thumb Index-75',
                        'zGenAlbum-Project Text Extension ID-76',
                        'zGenAlbum-User Query Data-77',
                        'zGenAlbum-Custom Query Parameters-78',
                        'zGenAlbum-Project Data-79',
                        'zGenAlbum-Search Index Rebuild State-80',
                        'zGenAlbum-Duplicate Type-81',
                        'zGenAlbum-Privacy State-82',
                        'zCldShareAlbumInvRec-zUUID-83',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-84',
                        'zCldShareAlbumInvRec-Invitation State Local-85',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-86',
                        ('zCldShareAlbumInvRec-Subscription Date-87', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-88',
                        'zCldShareAlbumInvRec-Invitee Last Name-89',
                        'zCldShareAlbumInvRec-Invitee Full Name-90',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-91',
                        'zCldShareAlbumInvRec-Invitee Email Key-92',
                        'zCldShareAlbumInvRec-Album GUID-93',
                        'zCldShareAlbumInvRec-Cloud GUID-94',
                        'zGenAlbum-Project Render UUID-95',
                        'zAlbumList-Needs Reordering Number-96')
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',             
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',        
        CASE zGenAlbum.ZSEARCHINDEXREBUILDSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
        END AS 'zGenAlbum-Search Index Rebuild State',        
        CASE zGenAlbum.ZDUPLICATETYPE
            WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
            WHEN 1 THEN 'Duplicate Asset_Pending-Merge-1'
            WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZDUPLICATETYPE || ''
        END AS 'zGenAlbum-Duplicate Type',        
        CASE zGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPRIVACYSTATE || ''
        END AS 'zGenAlbum-Privacy State',        
        zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_29ASSETS z29Assets ON z29Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z29Assets.Z_29ALBUMS
            LEFT JOIN Z_28ALBUMLISTS z28AlbumLists ON z28AlbumLists.Z_28ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z28AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                        'zAsset-Syndication State-7',
                        'zAsset-Bundle Scope-8',
                        'zAddAssetAttr.Imported by Bundle Identifier-9',
                        'zAddAssetAttr-Imported By Display Name-10',
                        'zAsset-Visibility State-11',
                        'zAsset-Saved Asset Type-12',
                        'zAddAssetAttr-Share Type-13',
                        'zAsset-Active Library Scope Participation State-14',
                        ('zAsset- SortToken -CameraRoll-15', 'datetime'),
                        ('zAsset-Added Date-16', 'datetime'),
                        ('zCldMast-Creation Date-17', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-18',
                        'zAddAssetAttr-EXIF-String-19',
                        ('zAsset-Modification Date-20', 'datetime'),
                        ('zAsset-Last Shared Date-21', 'datetime'),
                        ('zAsset-Trashed Date-22', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-23',
                        'zAddAssetAttr-zPK-24',
                        'zAsset-UUID = store.cloudphotodb-25',
                        'zAddAssetAttr-Master Fingerprint-26',
                        ('zGenAlbum-Cloud Creation Date-27', 'datetime'),
                        ('zGenAlbum-Creation Date-28', 'datetime'),
                        ('zGenAlbum-Start Date-29', 'datetime'),
                        ('zGenAlbum-End Date-30', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-31', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-32',
                        'zGenAlbum-UUID-33',
                        'zGenAlbum-Cloud GUID-34',
                        'zGenAlbum-Imported by Bundle Identifier-35',
                        'zGenAlbum-Pending Items Count-36',
                        'zGenAlbum-Pending Items Type-37',
                        'zGenAlbum- Cached Photos Count-38',
                        'zGenAlbum- Cached Videos Count-39',
                        'zGenAlbum- Cached Count-40',
                        'zGenAlbum-Has Unseen Content-41',
                        'zGenAlbum-Unseen Asset Count-42',
                        'zGenAlbum-zENT- Entity-43',
                        'zGenAlbum-Album Kind-44',
                        'zGenAlbum-Cloud_Local_State-45',
                        'zGenAlbum-Sync Event Order Key-46',
                        'zGenAlbum-is Owned-47',
                        'zGenAlbum-Cloud Relationship State-48',
                        'zGenAlbum-Cloud Relationship State Local-49',
                        'zGenAlbum-Cloud Owner Mail Key-50',
                        'zGenAlbum-Cloud Owner First Name-51',
                        'zGenAlbum-Cloud Owner Last Name-52',
                        'zGenAlbum-Cloud Owner Full Name-53',
                        'zGenAlbum-Cloud Person ID-54',
                        'zGenAlbum-Cloud Owner Hashed Person ID-55',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-56',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-57',
                        'zGenAlbum-Cloud Album Sub Type-58',
                        ('zGenAlbum-Cloud Contribution Date-59', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-60', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-61',
                        'zGenAlbum-Pinned-62',
                        'zGenAlbum-Custom Sort Key-63',
                        'zGenAlbum-Custom Sort Ascending-64',
                        'zGenAlbum-Is Prototype-65',
                        'zGenAlbum-Project Document Type-66',
                        'zGenAlbum-Custom Query Type-67',
                        'zGenAlbum-Trashed State-68',
                        ('zGenAlbum-Trash Date-69', 'datetime'),
                        'zGenAlbum-Cloud Delete State-70',
                        'zGenAlbum-Cloud Owner Whitelisted-71',
                        'zGenAlbum-Cloud Local Public URL Enabled-72',
                        'zGenAlbum-Cloud Public URL Enabled-73',
                        'zGenAlbum-Public URL-74',
                        'zGenAlbum-Key Asset Face Thumb Index-75',
                        'zGenAlbum-Project Text Extension ID-76',
                        'zGenAlbum-User Query Data-77',
                        'zGenAlbum-Custom Query Parameters-78',
                        'zGenAlbum-Project Data-79',
                        'zGenAlbum-Search Index Rebuild State-80',
                        'zGenAlbum-Duplicate Type-81',
                        'zGenAlbum-Privacy State-82',
                        'zCldShareAlbumInvRec-zUUID-83',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-84',
                        'zCldShareAlbumInvRec-Invitation State Local-85',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-86',
                        ('zCldShareAlbumInvRec-Subscription Date-87', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-88',
                        'zCldShareAlbumInvRec-Invitee Last Name-89',
                        'zCldShareAlbumInvRec-Invitee Full Name-90',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-91',
                        'zCldShareAlbumInvRec-Invitee Email Key-92',
                        'zCldShareAlbumInvRec-Album GUID-93',
                        'zCldShareAlbumInvRec-Cloud GUID-94',
                        'zGenAlbum-Project Render UUID-95',
                        'zAlbumList-Needs Reordering Number-96')
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
        DateTime(zGenAlbum.ZCLOUDCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Creation Date',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',             
        DateTime(zGenAlbum.ZCLOUDSUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Cloud Subscription Date',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',             
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISOWNED
            WHEN 0 THEN 'zGenAlbum-Not Owned by Device Apple Acnt-0'
            WHEN 1 THEN 'zGenAlbum-Owned by Device Apple Acnt-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISOWNED || ''
        END AS 'zGenAlbum-is Owned',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATE
            WHEN 0 THEN 'zGenAlbum-Cloud Album Owned by Device Apple Acnt-0'
            WHEN 2 THEN 'zGenAlbum-Cloud Album Not Owned by Device Apple Acnt-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATE || ''
        END AS 'zGenAlbum-Cloud Relationship State',        
        CASE zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL
            WHEN 0 THEN 'zGenAlbum-Shared Album Accessible Local Device-0'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDRELATIONSHIPSTATELOCAL || ''
        END AS 'zGenAlbum-Cloud Relationship State Local',        
        zGenAlbum.ZCLOUDOWNEREMAILKEY AS 'zGenAlbum-Cloud Owner Mail Key',        
        zGenAlbum.ZCLOUDOWNERFIRSTNAME AS 'zGenAlbum-Cloud Owner Frist Name',        
        zGenAlbum.ZCLOUDOWNERLASTNAME AS 'zGenAlbum-Cloud Owner Last Name',        
        zGenAlbum.ZCLOUDOWNERFULLNAME AS 'zGenAlbum-Cloud Owner Full Name',
        zGenAlbum.ZCLOUDPERSONID AS 'zGenAlbum-Cloud Person ID',        
        zGenAlbum.ZCLOUDOWNERHASHEDPERSONID AS 'zGenAlbum-Cloud Owner Hashed Person ID',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum-Local Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Local Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLEDLOCAL || ''
        END AS 'zGenAlbum-Local Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Single Contributor Enabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Multi-Contributors Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDMULTIPLECONTRIBUTORSENABLED || ''
        END AS 'zGenAlbum-Cloud Multi-Contributors Enabled',        
        CASE zGenAlbum.ZCLOUDALBUMSUBTYPE
            WHEN 0 THEN 'zGenAlbum Multi-Contributor-0'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDALBUMSUBTYPE || ''
        END AS 'zGenAlbum-Cloud Album Sub Type',        
        DateTime(zGenAlbum.ZCLOUDLASTCONTRIBUTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Contribution Date',        
        DateTime(zGenAlbum.ZCLOUDLASTINTERESTINGCHANGEDATE + 978307200, 'UNIXEPOCH') AS
         'zGenAlbum-Cloud Last Interesting Change Date',        
        CASE zGenAlbum.ZCLOUDNOTIFICATIONSENABLED
            WHEN 0 THEN 'zGenAlbum-Cloud Notifications Disabled-0'
            WHEN 1 THEN 'zGenAlbum-Cloud Notifications Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDNOTIFICATIONSENABLED || ''
        END AS 'zGenAlbum-Cloud Notification Enabled',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZCLOUDOWNERISWHITELISTED
            WHEN 0 THEN 'zGenAlbum Cloud Owner Not Whitelisted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Owner Whitelisted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDOWNERISWHITELISTED || ''
        END AS 'zGenAlbum-Cloud Owner Whitelisted',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL
            WHEN 0 THEN 'zGenAlbum Cloud Local Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Local has Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLEDLOCAL || ''
        END AS 'zGenAlbum-Cloud Local Public URL Enabled',        
        CASE zGenAlbum.ZCLOUDPUBLICURLENABLED
            WHEN 0 THEN 'zGenAlbum Cloud Public URL Disabled-0'
            WHEN 1 THEN 'zGenAlbum Cloud Public URL Enabled-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDPUBLICURLENABLED || ''
        END AS 'zGenAlbum-Cloud Public URL Enabled',
        zGenAlbum.ZPUBLICURL AS 'zGenAlbum-Public URL',        
        zGenAlbum.ZKEYASSETFACETHUMBNAILINDEX AS 'zGenAlbum-Key Asset Face Thumb Index',        
        zGenAlbum.ZPROJECTEXTENSIONIDENTIFIER AS 'zGenAlbum-Project Text Extension ID',        
        zGenAlbum.ZUSERQUERYDATA AS 'zGenAlbum-User Query Data',        
        zGenAlbum.ZCUSTOMQUERYPARAMETERS AS 'zGenAlbum-Custom Query Parameters',        
        zGenAlbum.ZPROJECTDATA AS 'zGenAlbum-Project Data',        
        CASE zGenAlbum.ZSEARCHINDEXREBUILDSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
        END AS 'zGenAlbum-Search Index Rebuild State',        
        CASE zGenAlbum.ZDUPLICATETYPE
            WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
            WHEN 1 THEN 'Duplicate Asset_Pending-Merge-1'
            WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZDUPLICATETYPE || ''
        END AS 'zGenAlbum-Duplicate Type',        
        CASE zGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPRIVACYSTATE || ''
        END AS 'zGenAlbum-Privacy State',        
        zCldShareAlbumInvRec.ZUUID AS 'zCldShareAlbumInvRec-zUUID',
        CASE zCldShareAlbumInvRec.ZISMINE
            WHEN 0 THEN 'Not My Invitation-0'
            WHEN 1 THEN 'My Invitation-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZISMINE || ''
        END AS 'zCldShareAlbumInvRec-Is My Invitation to Shared Album',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL
            WHEN 0 THEN '0-StillTesting-0'
            WHEN 1 THEN '1-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATELOCAL || ''
        END AS 'zCldShareAlbumInvRec-Invitation State Local',
        CASE zCldShareAlbumInvRec.ZINVITATIONSTATE
            WHEN 1 THEN 'Shared Album Invitation Pending-1'
            WHEN 2 THEN 'Shared Album Invitation Accepted-2'
            WHEN 3 THEN 'Shared Album Invitation Declined-3'
            WHEN 4 THEN '4-StillTesting'
            WHEN 5 THEN '5-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldShareAlbumInvRec.ZINVITATIONSTATE || ''
        END AS 'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status',
        DateTime(zCldShareAlbumInvRec.ZINVITEESUBSCRIPTIONDATE + 978307200, 'UNIXEPOCH') AS
         'zCldShareAlbumInvRec-Subscription Date',
        zCldShareAlbumInvRec.ZINVITEEFIRSTNAME AS 'zCldShareAlbumInvRec-Invitee First Name',
        zCldShareAlbumInvRec.ZINVITEELASTNAME AS 'zCldShareAlbumInvRec-Invitee Last Name',
        zCldShareAlbumInvRec.ZINVITEEFULLNAME AS 'zCldShareAlbumInvRec-Invitee Full Name',
        zCldShareAlbumInvRec.ZINVITEEHASHEDPERSONID AS 'zCldShareAlbumInvRec-Invitee Hashed Person ID',
        zCldShareAlbumInvRec.ZINVITEEEMAILKEY AS 'zCldShareAlbumInvRec-Invitee Email Key',    
        zCldShareAlbumInvRec.ZALBUMGUID AS 'zCldShareAlbumInvRec-Album GUID',
        zCldShareAlbumInvRec.ZCLOUDGUID AS 'zCldShareAlbumInvRec-Cloud GUID',
        zGenAlbum.ZPROJECTRENDERUUID AS 'zGenAlbum-Project Render UUID',        
        CASE zAlbumList.ZNEEDSREORDERINGNUMBER
            WHEN 1 THEN '1-Yes-1'
            ELSE 'Unknown-New-Value!: ' || zAlbumList.ZNEEDSREORDERINGNUMBER || ''
        END AS 'zAlbumList-Needs Reordering Number'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_30ASSETS z30Assets ON z30Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z30Assets.Z_30ALBUMS
            LEFT JOIN Z_29ALBUMLISTS z29AlbumLists ON z29AlbumLists.Z_29ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z29AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON
             zGenAlbum.Z_PK = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
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
                              row[82], row[83], row[84], row[85], row[86], row[87], row[88], row[89], row[90],
                              row[91], row[92], row[93], row[94], row[95], row[96], row[97]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-zPK-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                        'zAsset-Syndication State-7',
                        'zAsset-Bundle Scope-8',
                        'zAddAssetAttr.Imported by Bundle Identifier-9',
                        'zAddAssetAttr-Imported By Display Name-10',
                        'zAsset-Visibility State-11',
                        'zAsset-Saved Asset Type-12',
                        'zAddAssetAttr-Share Type-13',
                        'zAsset-Active Library Scope Participation State-14',
                        ('zAsset- SortToken -CameraRoll-15', 'datetime'),
                        ('zAsset-Added Date-16', 'datetime'),
                        ('zCldMast-Creation Date-17', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-18',
                        'zAddAssetAttr-EXIF-String-19',
                        ('zAsset-Modification Date-20', 'datetime'),
                        ('zAsset-Last Shared Date-21', 'datetime'),
                        ('zAsset-Trashed Date-22', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-23',
                        'zAddAssetAttr-zPK-24',
                        'zAsset-UUID = store.cloudphotodb-25',
                        'zAddAssetAttr-Original Stable Hash-26',
                        'zAddAssetAttr.Adjusted Stable Hash-27',
                        ('zGenAlbum-Cloud Creation Date-28', 'datetime'),
                        ('zGenAlbum-Creation Date-29', 'datetime'),
                        ('zGenAlbum-Start Date-30', 'datetime'),
                        ('zGenAlbum-End Date-31', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-32', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-33',
                        'zGenAlbum-UUID-34',
                        'zGenAlbum-Cloud GUID-35',
                        'zGenAlbum-Imported by Bundle Identifier-36',
                        'zGenAlbum-Pending Items Count-37',
                        'zGenAlbum-Pending Items Type-38',
                        'zGenAlbum- Cached Photos Count-39',
                        'zGenAlbum- Cached Videos Count-40',
                        'zGenAlbum- Cached Count-41',
                        'zGenAlbum-Has Unseen Content-42',
                        'zGenAlbum-Unseen Asset Count-43',
                        'zGenAlbum-zENT- Entity-44',
                        'zGenAlbum-Album Kind-45',
                        'zGenAlbum-Cloud_Local_State-46',
                        'zGenAlbum-Sync Event Order Key-47',
                        'zGenAlbum-is Owned-48',
                        'zGenAlbum-Cloud Relationship State-49',
                        'zGenAlbum-Cloud Relationship State Local-50',
                        'zGenAlbum-Cloud Owner Mail Key-51',
                        'zGenAlbum-Cloud Owner First Name-52',
                        'zGenAlbum-Cloud Owner Last Name-53',
                        'zGenAlbum-Cloud Owner Full Name-54',
                        'zGenAlbum-Cloud Person ID-55',
                        'zGenAlbum-Cloud Owner Hashed Person ID-56',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-57',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-58',
                        'zGenAlbum-Cloud Album Sub Type-59',
                        ('zGenAlbum-Cloud Contribution Date-60', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-61', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-62',
                        'zGenAlbum-Pinned-63',
                        'zGenAlbum-Custom Sort Key-64',
                        'zGenAlbum-Custom Sort Ascending-65',
                        'zGenAlbum-Is Prototype-66',
                        'zGenAlbum-Project Document Type-67',
                        'zGenAlbum-Custom Query Type-68',
                        'zGenAlbum-Trashed State-69',
                        ('zGenAlbum-Trash Date-70', 'datetime'),
                        'zGenAlbum-Cloud Delete State-71',
                        'zGenAlbum-Cloud Owner Whitelisted-72',
                        'zGenAlbum-Cloud Local Public URL Enabled-73',
                        'zGenAlbum-Cloud Public URL Enabled-74',
                        'zGenAlbum-Public URL-75',
                        'zGenAlbum-Key Asset Face Thumb Index-76',
                        'zGenAlbum-Project Text Extension ID-77',
                        'zGenAlbum-User Query Data-78',
                        'zGenAlbum-Custom Query Parameters-79',
                        'zGenAlbum-Project Data-80',
                        'zGenAlbum-Search Index Rebuild State-81',
                        'zGenAlbum-Duplicate Type-82',
                        'zGenAlbum-Privacy State-83',
                        'zCldShareAlbumInvRec-zUUID-84',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-85',
                        'zCldShareAlbumInvRec-Invitation State Local-86',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-87',
                        ('zCldShareAlbumInvRec-Subscription Date-88', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-89',
                        'zCldShareAlbumInvRec-Invitee Last Name-90',
                        'zCldShareAlbumInvRec-Invitee Full Name-91',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-92',
                        'zCldShareAlbumInvRec-Invitee Email Key-93',
                        'zCldShareAlbumInvRec-Album GUID-94',
                        'zCldShareAlbumInvRec-Cloud GUID-95',
                        'zGenAlbum-Project Render UUID-96',
                        'zAlbumList-Needs Reordering Number-97')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
