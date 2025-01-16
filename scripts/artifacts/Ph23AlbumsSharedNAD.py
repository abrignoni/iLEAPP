__artifacts_v2__ = {
    'Ph23SharedAlbumRecordsInviteswithNADPhDaPsql': {
        'name': 'Ph23-Shared Album Records & Invites NAD-PhDaPsql',
        'description': 'Parses Shared Album records found in the PhotoData-Photos.sqlite ZGENERICALBUM Table'
                       ' and supports iOS 11-18. Parses Shared Album records only, no asset data being parsed.'
                       ' This parser will contain shared albums, share album invites, and invite status data.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-D-Generic_Album_Records-NAD',
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
def Ph23SharedAlbumRecordsInviteswithNADPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_19ALBUMLISTS z19AlbumLists ON z19AlbumLists.Z_19ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z19AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZSTARTDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Start Date-1', 'datetime'),
                        ('zGenAlbum-End Date-2', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-3', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-4',
                        'zGenAlbum-UUID-5',
                        'zGenAlbum-Cloud GUID-6',
                        'zGenAlbum-Cloud Metadata-HEX NSKeyed Plist-7',
                        'zGenAlbum-Pending Items Count-8',
                        'zGenAlbum-Pending Items Type-9',
                        'zGenAlbum- Cached Photos Count-10',
                        'zGenAlbum- Cached Videos Count-11',
                        'zGenAlbum- Cached Count-12',
                        'zGenAlbum-Has Unseen Content-13',
                        'zGenAlbum-Unseen Asset Count-14',
                        'zGenAlbum-zENT- Entity-15',
                        'zGenAlbum-Album Kind-16',
                        'zGenAlbum-Cloud_Local_State-17',
                        'zGenAlbum-Sync Event Order Key-18',
                        'zGenAlbum-is Owned-19',
                        'zGenAlbum-Cloud Relationship State-20',
                        'zGenAlbum-Cloud Relationship State Local-21',
                        'zGenAlbum-Cloud Owner Mail Key-22',
                        'zGenAlbum-Cloud Owner Frist Name-23',
                        'zGenAlbum-Cloud Owner Last Name-24',
                        'zGenAlbum-Cloud Owner Full Name-25',
                        'zGenAlbum-Cloud Person ID-26',
                        'zGenAlbum-Cloud Owner Hashed Person ID-27',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-28',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-29',
                        'zGenAlbum-Cloud Album Sub Type-30',
                        ('zGenAlbum-Cloud Contribution Date-31', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-32', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-33',
                        'zGenAlbum-Pinned-34',
                        'zGenAlbum-Custom Sort Key-35',
                        'zGenAlbum-Custom Sort Ascending-36',
                        'zGenAlbum-Custom Query Type-37',
                        'zGenAlbum-Trashed State-38',
                        ('zGenAlbum-Trash Date-39', 'datetime'),
                        'zGenAlbum-Cloud Owner Whitelisted-40',
                        'zGenAlbum-Cloud Local Public URL Enabled-41',
                        'zGenAlbum-Cloud Public URL Enabled-42',
                        'zGenAlbum-Public URL-43',
                        'zGenAlbum-Key Asset Face Thumb Index-44',
                        'zGenAlbum-Custom Query Parameters-45',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-46',
                        'zCldShareAlbumInvRec-Invitation State Local-47',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-48',
                        ('zCldShareAlbumInvRec-Subscription Date-49', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-50',
                        'zCldShareAlbumInvRec-Invitee Last Name-51',
                        'zCldShareAlbumInvRec-Invitee Full Name-52',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-53',
                        'zCldShareAlbumInvRec-Invitee Email Key-54',
                        'zCldShareAlbumInvRec-Album GUID-55',
                        'zCldShareAlbumInvRec-Cloud GUID-56',
                        'zAlbumList-Needs Reordering Number-57')
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_22ALBUMLISTS z22AlbumLists ON z22AlbumLists.Z_22ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z22AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZSTARTDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Start Date-1', 'datetime'),
                        ('zGenAlbum-End Date-2', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-3', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-4',
                        'zGenAlbum-UUID-5',
                        'zGenAlbum-Cloud GUID-6',
                        'zGenAlbum-Pending Items Count-7',
                        'zGenAlbum-Pending Items Type-8',
                        'zGenAlbum- Cached Photos Count-9',
                        'zGenAlbum- Cached Videos Count-10',
                        'zGenAlbum- Cached Count-11',
                        'zGenAlbum-Has Unseen Content-12',
                        'zGenAlbum-Unseen Asset Count-13',
                        'zGenAlbum-zENT- Entity-14',
                        'zGenAlbum-Album Kind-15',
                        'zGenAlbum-Cloud_Local_State-16',
                        'zGenAlbum-Sync Event Order Key-17',
                        'zGenAlbum-is Owned-18',
                        'zGenAlbum-Cloud Relationship State-19',
                        'zGenAlbum-Cloud Relationship State Local-20',
                        'zGenAlbum-Cloud Owner Mail Key-21',
                        'zGenAlbum-Cloud Owner First Name-22',
                        'zGenAlbum-Cloud Owner Last Name-23',
                        'zGenAlbum-Cloud Owner Full Name-24',
                        'zGenAlbum-Cloud Person ID-25',
                        'zGenAlbum-Cloud Owner Hashed Person ID-26',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-27',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-28',
                        'zGenAlbum-Cloud Album Sub Type-29',
                        ('zGenAlbum-Cloud Contribution Date-30', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-31', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-32',
                        'zGenAlbum-Pinned-33',
                        'zGenAlbum-Custom Sort Key-34',
                        'zGenAlbum-Custom Sort Ascending-35',
                        'zGenAlbum-Custom Query Type-36',
                        'zGenAlbum-Trashed State-37',
                        ('zGenAlbum-Trash Date-38', 'datetime'),
                        'zGenAlbum-Cloud Delete State-39',
                        'zGenAlbum-Cloud Owner Whitelisted-40',
                        'zGenAlbum-Cloud Local Public URL Enabled-41',
                        'zGenAlbum-Cloud Public URL Enabled-42',
                        'zGenAlbum-Public URL-43',
                        'zGenAlbum-Key Asset Face Thumb Index-44',
                        'zGenAlbum-Custom Query Parameters-45',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-46',
                        'zCldShareAlbumInvRec-Invitation State Local-47',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-48',
                        ('zCldShareAlbumInvRec-Subscription Date-49', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-50',
                        'zCldShareAlbumInvRec-Invitee Last Name-51',
                        'zCldShareAlbumInvRec-Invitee Full Name-52',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-53',
                        'zCldShareAlbumInvRec-Invitee Email Key-54',
                        'zCldShareAlbumInvRec-Album GUID-55',
                        'zCldShareAlbumInvRec-Cloud GUID-56',
                        'zAlbumList-Needs Reordering Number-57')
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                              row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                              row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Creation Date-1', 'datetime'),
                        ('zGenAlbum-Start Date-2', 'datetime'),
                        ('zGenAlbum-End Date-3', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-5',
                        'zGenAlbum-UUID-6',
                        'zGenAlbum-Cloud GUID-7',
                        'zGenAlbum-Pending Items Count-8',
                        'zGenAlbum-Pending Items Type-9',
                        'zGenAlbum- Cached Photos Count-10',
                        'zGenAlbum- Cached Videos Count-11',
                        'zGenAlbum- Cached Count-12',
                        'zGenAlbum-Has Unseen Content-13',
                        'zGenAlbum-Unseen Asset Count-14',
                        'zGenAlbum-zENT- Entity-15',
                        'zGenAlbum-Album Kind-16',
                        'zGenAlbum-Cloud_Local_State-17',
                        'zGenAlbum-Sync Event Order Key-18',
                        'zGenAlbum-is Owned-19',
                        'zGenAlbum-Cloud Relationship State-20',
                        'zGenAlbum-Cloud Relationship State Local-21',
                        'zGenAlbum-Cloud Owner Mail Key-22',
                        'zGenAlbum-Cloud Owner Frist Name-23',
                        'zGenAlbum-Cloud Owner Last Name-24',
                        'zGenAlbum-Cloud Owner Full Name-25',
                        'zGenAlbum-Cloud Person ID-26',
                        'zGenAlbum-Cloud Owner Hashed Person ID-27',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-28',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-29',
                        'zGenAlbum-Cloud Album Sub Type-30',
                        ('zGenAlbum-Cloud Contribution Date-31', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-32', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-33',
                        'zGenAlbum-Pinned-34',
                        'zGenAlbum-Custom Sort Key-35',
                        'zGenAlbum-Custom Sort Ascending-36',
                        'zGenAlbum-Project Document Type-37',
                        'zGenAlbum-Custom Query Type-38',
                        'zGenAlbum-Trashed State-39',
                        ('zGenAlbum-Trash Date-40', 'datetime'),
                        'zGenAlbum-Cloud Delete State-41',
                        'zGenAlbum-Cloud Owner Whitelisted-42',
                        'zGenAlbum-Cloud Local Public URL Enabled-43',
                        'zGenAlbum-Cloud Public URL Enabled-44',
                        'zGenAlbum-Public URL-45',
                        'zGenAlbum-Key Asset Face Thumb Index-46',
                        'zGenAlbum-Project Text Extension ID-47',
                        'zGenAlbum-User Query Data-48',
                        'zGenAlbum-Custom Query Parameters-49',
                        'zGenAlbum-Project Data-50',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-51',
                        'zCldShareAlbumInvRec-Invitation State Local-52',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-53',
                        ('zCldShareAlbumInvRec-Subscription Date-54', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-55',
                        'zCldShareAlbumInvRec-Invitee Last Name-56',
                        'zCldShareAlbumInvRec-Invitee Full Name-57',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-58',
                        'zCldShareAlbumInvRec-Invitee Email Key-59',
                        'zCldShareAlbumInvRec-Album GUID-60',
                        'zCldShareAlbumInvRec-Cloud GUID-61',
                        'zGenAlbum-Project Render UUID-62',
                        'zAlbumList-Needs Reordering Number-63')
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
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

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Creation Date-1', 'datetime'),
                        ('zGenAlbum-Start Date-2', 'datetime'),
                        ('zGenAlbum-End Date-3', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-5',
                        'zGenAlbum-UUID-6',
                        'zGenAlbum-Cloud GUID-7',
                        'zGenAlbum-Creator Bundle ID-8',
                        'zGenAlbum-Pending Items Count-9',
                        'zGenAlbum-Pending Items Type-10',
                        'zGenAlbum- Cached Photos Count-11',
                        'zGenAlbum- Cached Videos Count-12',
                        'zGenAlbum- Cached Count-13',
                        'zGenAlbum-Has Unseen Content-14',
                        'zGenAlbum-Unseen Asset Count-15',
                        'zGenAlbum-zENT- Entity-16',
                        'zGenAlbum-Album Kind-17',
                        'zGenAlbum-Cloud_Local_State-18',
                        'zGenAlbum-Sync Event Order Key-19',
                        'zGenAlbum-is Owned-20',
                        'zGenAlbum-Cloud Relationship State-21',
                        'zGenAlbum-Cloud Relationship State Local-22',
                        'zGenAlbum-Cloud Owner Mail Key-23',
                        'zGenAlbum-Cloud Owner Frist Name-24',
                        'zGenAlbum-Cloud Owner Last Name-25',
                        'zGenAlbum-Cloud Owner Full Name-26',
                        'zGenAlbum-Cloud Person ID-27',
                        'zGenAlbum-Cloud Owner Hashed Person ID-28',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-29',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-30',
                        'zGenAlbum-Cloud Album Sub Type-31',
                        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-34',
                        'zGenAlbum-Pinned-35',
                        'zGenAlbum-Custom Sort Key-36',
                        'zGenAlbum-Custom Sort Ascending-37',
                        'zGenAlbum-Is Prototype-38',
                        'zGenAlbum-Project Document Type-39',
                        'zGenAlbum-Custom Query Type-40',
                        'zGenAlbum-Trashed State-41',
                        ('zGenAlbum-Trash Date-42', 'datetime'),
                        'zGenAlbum-Cloud Delete State-43',
                        'zGenAlbum-Cloud Owner Whitelisted-44',
                        'zGenAlbum-Cloud Local Public URL Enabled-45',
                        'zGenAlbum-Cloud Public URL Enabled-46',
                        'zGenAlbum-Public URL-47',
                        'zGenAlbum-Key Asset Face Thumb Index-48',
                        'zGenAlbum-Project Text Extension ID-49',
                        'zGenAlbum-User Query Data-50',
                        'zGenAlbum-Custom Query Parameters-51',
                        'zGenAlbum-Project Data-52',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-53',
                        'zCldShareAlbumInvRec-Invitation State Local-54',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-55',
                        ('zCldShareAlbumInvRec-Subscription Date-56', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-57',
                        'zCldShareAlbumInvRec-Invitee Last Name-58',
                        'zCldShareAlbumInvRec-Invitee Full Name-59',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-60',
                        'zCldShareAlbumInvRec-Invitee Email Key-61',
                        'zCldShareAlbumInvRec-Album GUID-62',
                        'zCldShareAlbumInvRec-Cloud GUID-63',
                        'zGenAlbum-Project Render UUID-64',
                        'zAlbumList-Needs Reordering Number-65')
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
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

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Creation Date-1', 'datetime'),
                        ('zGenAlbum-Start Date-2', 'datetime'),
                        ('zGenAlbum-End Date-3', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-5',
                        'zGenAlbum-UUID-6',
                        'zGenAlbum-Cloud GUID-7',
                        'zGenAlbum-Imported by Bundle Identifier-8',
                        'zGenAlbum-Pending Items Count-9',
                        'zGenAlbum-Pending Items Type-10',
                        'zGenAlbum- Cached Photos Count-11',
                        'zGenAlbum- Cached Videos Count-12',
                        'zGenAlbum- Cached Count-13',
                        'zGenAlbum-Has Unseen Content-14',
                        'zGenAlbum-Unseen Asset Count-15',
                        'zGenAlbum-zENT- Entity-16',
                        'zGenAlbum-Album Kind-17',
                        'zGenAlbum-Cloud_Local_State-18',
                        'zGenAlbum-Sync Event Order Key-19',
                        'zGenAlbum-is Owned-20',
                        'zGenAlbum-Cloud Relationship State-21',
                        'zGenAlbum-Cloud Relationship State Local-22',
                        'zGenAlbum-Cloud Owner Mail Key-23',
                        'zGenAlbum-Cloud Owner Frist Name-24',
                        'zGenAlbum-Cloud Owner Last Name-25',
                        'zGenAlbum-Cloud Owner Full Name-26',
                        'zGenAlbum-Cloud Person ID-27',
                        'zGenAlbum-Cloud Owner Hashed Person ID-28',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-29',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-30',
                        'zGenAlbum-Cloud Album Sub Type-31',
                        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-34',
                        'zGenAlbum-Pinned-35',
                        'zGenAlbum-Custom Sort Key-36',
                        'zGenAlbum-Custom Sort Ascending-37',
                        'zGenAlbum-Is Prototype-38',
                        'zGenAlbum-Project Document Type-39',
                        'zGenAlbum-Custom Query Type-40',
                        'zGenAlbum-Trashed State-41',
                        ('zGenAlbum-Trash Date-42', 'datetime'),
                        'zGenAlbum-Cloud Delete State-43',
                        'zGenAlbum-Cloud Owner Whitelisted-44',
                        'zGenAlbum-Cloud Local Public URL Enabled-45',
                        'zGenAlbum-Cloud Public URL Enabled-46',
                        'zGenAlbum-Public URL-47',
                        'zGenAlbum-Key Asset Face Thumb Index-48',
                        'zGenAlbum-Project Text Extension ID-49',
                        'zGenAlbum-User Query Data-50',
                        'zGenAlbum-Custom Query Parameters-51',
                        'zGenAlbum-Project Data-52',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-53',
                        'zCldShareAlbumInvRec-Invitation State Local-54',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-55',
                        ('zCldShareAlbumInvRec-Subscription Date-56', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-57',
                        'zCldShareAlbumInvRec-Invitee Last Name-58',
                        'zCldShareAlbumInvRec-Invitee Full Name-59',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-60',
                        'zCldShareAlbumInvRec-Invitee Email Key-61',
                        'zCldShareAlbumInvRec-Album GUID-62',
                        'zCldShareAlbumInvRec-Cloud GUID-63',
                        'zGenAlbum-Project Render UUID-64',
                        'zAlbumList-Needs Reordering Number-65')
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
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
                              row[64], row[65], row[66], row[67], row[68], row[69]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Creation Date-1', 'datetime'),
                        ('zGenAlbum-Start Date-2', 'datetime'),
                        ('zGenAlbum-End Date-3', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-5',
                        'zGenAlbum-UUID-6',
                        'zGenAlbum-Cloud GUID-7',
                        'zGenAlbum-Imported by Bundle Identifier-8',
                        'zGenAlbum-Pending Items Count-9',
                        'zGenAlbum-Pending Items Type-10',
                        'zGenAlbum- Cached Photos Count-11',
                        'zGenAlbum- Cached Videos Count-12',
                        'zGenAlbum- Cached Count-13',
                        'zGenAlbum-Has Unseen Content-14',
                        'zGenAlbum-Unseen Asset Count-15',
                        'zGenAlbum-zENT- Entity-16',
                        'zGenAlbum-Album Kind-17',
                        'zGenAlbum-Cloud_Local_State-18',
                        'zGenAlbum-Sync Event Order Key-19',
                        'zGenAlbum-is Owned-20',
                        'zGenAlbum-Cloud Relationship State-21',
                        'zGenAlbum-Cloud Relationship State Local-22',
                        'zGenAlbum-Cloud Owner Mail Key-23',
                        'zGenAlbum-Cloud Owner First Name-24',
                        'zGenAlbum-Cloud Owner Last Name-25',
                        'zGenAlbum-Cloud Owner Full Name-26',
                        'zGenAlbum-Cloud Person ID-27',
                        'zGenAlbum-Cloud Owner Hashed Person ID-28',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-29',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-30',
                        'zGenAlbum-Cloud Album Sub Type-31',
                        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-34',
                        'zGenAlbum-Pinned-35',
                        'zGenAlbum-Custom Sort Key-36',
                        'zGenAlbum-Custom Sort Ascending-37',
                        'zGenAlbum-Is Prototype-38',
                        'zGenAlbum-Project Document Type-39',
                        'zGenAlbum-Custom Query Type-40',
                        'zGenAlbum-Trashed State-41',
                        ('zGenAlbum-Trash Date-42', 'datetime'),
                        'zGenAlbum-Cloud Delete State-43',
                        'zGenAlbum-Cloud Owner Whitelisted-44',
                        'zGenAlbum-Cloud Local Public URL Enabled-45',
                        'zGenAlbum-Cloud Public URL Enabled-46',
                        'zGenAlbum-Public URL-47',
                        'zGenAlbum-Key Asset Face Thumb Index-48',
                        'zGenAlbum-Project Text Extension ID-49',
                        'zGenAlbum-User Query Data-50',
                        'zGenAlbum-Custom Query Parameters-51',
                        'zGenAlbum-Project Data-52',
                        'zGenAlbum-Search Index Rebuild State-53',
                        'zGenAlbum-Duplicate Type-54',
                        'zGenAlbum-Privacy State-55',
                        'zCldShareAlbumInvRec-zUUID-56',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-57',
                        'zCldShareAlbumInvRec-Invitation State Local-58',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-59',
                        ('zCldShareAlbumInvRec-Subscription Date-60', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-61',
                        'zCldShareAlbumInvRec-Invitee Last Name-62',
                        'zCldShareAlbumInvRec-Invitee Full Name-63',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-64',
                        'zCldShareAlbumInvRec-Invitee Email Key-65',
                        'zCldShareAlbumInvRec-Album GUID-66',
                        'zCldShareAlbumInvRec-Cloud GUID-67',
                        'zGenAlbum-Project Render UUID-68',
                        'zAlbumList-Needs Reordering Number-69')
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_28ALBUMLISTS z28AlbumLists ON z28AlbumLists.Z_28ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z28AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
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
                              row[64], row[65], row[66], row[67], row[68], row[69]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Creation Date-1', 'datetime'),
                        ('zGenAlbum-Start Date-2', 'datetime'),
                        ('zGenAlbum-End Date-3', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-5',
                        'zGenAlbum-UUID-6',
                        'zGenAlbum-Cloud GUID-7',
                        'zGenAlbum-Imported by Bundle Identifier-8',
                        'zGenAlbum-Pending Items Count-9',
                        'zGenAlbum-Pending Items Type-10',
                        'zGenAlbum- Cached Photos Count-11',
                        'zGenAlbum- Cached Videos Count-12',
                        'zGenAlbum- Cached Count-13',
                        'zGenAlbum-Has Unseen Content-14',
                        'zGenAlbum-Unseen Asset Count-15',
                        'zGenAlbum-zENT- Entity-16',
                        'zGenAlbum-Album Kind-17',
                        'zGenAlbum-Cloud_Local_State-18',
                        'zGenAlbum-Sync Event Order Key-19',
                        'zGenAlbum-is Owned-20',
                        'zGenAlbum-Cloud Relationship State-21',
                        'zGenAlbum-Cloud Relationship State Local-22',
                        'zGenAlbum-Cloud Owner Mail Key-23',
                        'zGenAlbum-Cloud Owner First Name-24',
                        'zGenAlbum-Cloud Owner Last Name-25',
                        'zGenAlbum-Cloud Owner Full Name-26',
                        'zGenAlbum-Cloud Person ID-27',
                        'zGenAlbum-Cloud Owner Hashed Person ID-28',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-29',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-30',
                        'zGenAlbum-Cloud Album Sub Type-31',
                        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-34',
                        'zGenAlbum-Pinned-35',
                        'zGenAlbum-Custom Sort Key-36',
                        'zGenAlbum-Custom Sort Ascending-37',
                        'zGenAlbum-Is Prototype-38',
                        'zGenAlbum-Project Document Type-39',
                        'zGenAlbum-Custom Query Type-40',
                        'zGenAlbum-Trashed State-41',
                        ('zGenAlbum-Trash Date-42', 'datetime'),
                        'zGenAlbum-Cloud Delete State-43',
                        'zGenAlbum-Cloud Owner Whitelisted-44',
                        'zGenAlbum-Cloud Local Public URL Enabled-45',
                        'zGenAlbum-Cloud Public URL Enabled-46',
                        'zGenAlbum-Public URL-47',
                        'zGenAlbum-Key Asset Face Thumb Index-48',
                        'zGenAlbum-Project Text Extension ID-49',
                        'zGenAlbum-User Query Data-50',
                        'zGenAlbum-Custom Query Parameters-51',
                        'zGenAlbum-Project Data-52',
                        'zGenAlbum-Search Index Rebuild State-53',
                        'zGenAlbum-Duplicate Type-54',
                        'zGenAlbum-Privacy State-55',
                        'zCldShareAlbumInvRec-zUUID-56',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-57',
                        'zCldShareAlbumInvRec-Invitation State Local-58',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-59',
                        ('zCldShareAlbumInvRec-Subscription Date-60', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-61',
                        'zCldShareAlbumInvRec-Invitee Last Name-62',
                        'zCldShareAlbumInvRec-Invitee Full Name-63',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-64',
                        'zCldShareAlbumInvRec-Invitee Email Key-65',
                        'zCldShareAlbumInvRec-Album GUID-66',
                        'zCldShareAlbumInvRec-Cloud GUID-67',
                        'zGenAlbum-Project Render UUID-68',
                        'zAlbumList-Needs Reordering Number-69')
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
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_29ALBUMLISTS z29AlbumLists ON z29AlbumLists.Z_29ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z29AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 1505
        ORDER BY zGenAlbum.ZCREATIONDATE
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
                              row[64], row[65], row[66], row[67], row[68], row[69]))

        data_headers = (('zGenAlbum-Cloud Creation Date-0', 'datetime'),
                        ('zGenAlbum-Creation Date-1', 'datetime'),
                        ('zGenAlbum-Start Date-2', 'datetime'),
                        ('zGenAlbum-End Date-3', 'datetime'),
                        ('zGenAlbum-Cloud Subscription Date-4', 'datetime'),
                        'zGenAlbum- Title-User&System Applied-5',
                        'zGenAlbum-UUID-6',
                        'zGenAlbum-Cloud GUID-7',
                        'zGenAlbum-Imported by Bundle Identifier-8',
                        'zGenAlbum-Pending Items Count-9',
                        'zGenAlbum-Pending Items Type-10',
                        'zGenAlbum- Cached Photos Count-11',
                        'zGenAlbum- Cached Videos Count-12',
                        'zGenAlbum- Cached Count-13',
                        'zGenAlbum-Has Unseen Content-14',
                        'zGenAlbum-Unseen Asset Count-15',
                        'zGenAlbum-zENT- Entity-16',
                        'zGenAlbum-Album Kind-17',
                        'zGenAlbum-Cloud_Local_State-18',
                        'zGenAlbum-Sync Event Order Key-19',
                        'zGenAlbum-is Owned-20',
                        'zGenAlbum-Cloud Relationship State-21',
                        'zGenAlbum-Cloud Relationship State Local-22',
                        'zGenAlbum-Cloud Owner Mail Key-23',
                        'zGenAlbum-Cloud Owner First Name-24',
                        'zGenAlbum-Cloud Owner Last Name-25',
                        'zGenAlbum-Cloud Owner Full Name-26',
                        'zGenAlbum-Cloud Person ID-27',
                        'zGenAlbum-Cloud Owner Hashed Person ID-28',
                        'zGenAlbum-Local Cloud Multi-Contributors Enabled-29',
                        'zGenAlbum-Cloud Multi-Contributors Enabled-30',
                        'zGenAlbum-Cloud Album Sub Type-31',
                        ('zGenAlbum-Cloud Contribution Date-32', 'datetime'),
                        ('zGenAlbum-Cloud Last Interesting Change Date-33', 'datetime'),
                        'zGenAlbum-Cloud Notification Enabled-34',
                        'zGenAlbum-Pinned-35',
                        'zGenAlbum-Custom Sort Key-36',
                        'zGenAlbum-Custom Sort Ascending-37',
                        'zGenAlbum-Is Prototype-38',
                        'zGenAlbum-Project Document Type-39',
                        'zGenAlbum-Custom Query Type-40',
                        'zGenAlbum-Trashed State-41',
                        ('zGenAlbum-Trash Date-42', 'datetime'),
                        'zGenAlbum-Cloud Delete State-43',
                        'zGenAlbum-Cloud Owner Whitelisted-44',
                        'zGenAlbum-Cloud Local Public URL Enabled-45',
                        'zGenAlbum-Cloud Public URL Enabled-46',
                        'zGenAlbum-Public URL-47',
                        'zGenAlbum-Key Asset Face Thumb Index-48',
                        'zGenAlbum-Project Text Extension ID-49',
                        'zGenAlbum-User Query Data-50',
                        'zGenAlbum-Custom Query Parameters-51',
                        'zGenAlbum-Project Data-52',
                        'zGenAlbum-Search Index Rebuild State-53',
                        'zGenAlbum-Duplicate Type-54',
                        'zGenAlbum-Privacy State-55',
                        'zCldShareAlbumInvRec-zUUID-56',
                        'zCldShareAlbumInvRec-Is My Invitation to Shared Album-57',
                        'zCldShareAlbumInvRec-Invitation State Local-58',
                        'zCldShareAlbumInvRec-Invitation State-Shared Album Invite Status-59',
                        ('zCldShareAlbumInvRec-Subscription Date-60', 'datetime'),
                        'zCldShareAlbumInvRec-Invitee First Name-61',
                        'zCldShareAlbumInvRec-Invitee Last Name-62',
                        'zCldShareAlbumInvRec-Invitee Full Name-63',
                        'zCldShareAlbumInvRec-Invitee Hashed Person ID-64',
                        'zCldShareAlbumInvRec-Invitee Email Key-65',
                        'zCldShareAlbumInvRec-Album GUID-66',
                        'zCldShareAlbumInvRec-Cloud GUID-67',
                        'zGenAlbum-Project Render UUID-68',
                        'zAlbumList-Needs Reordering Number-69')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
