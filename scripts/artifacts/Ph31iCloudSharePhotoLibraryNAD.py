__artifacts_v2__ = {
    'Ph31iCloudSPLwithParticipantswithNADPhDaPsql': {
        'name': 'Ph31-iCloud SPL with Participants NAD-PhDaPsql',
        'description': 'Parses iCloud Shared Photo Library records and invites from the PhotoData-Photos.sqlite'
                       ' ZSHARE Table and supports iOS 14-18. Parses iCloud SPL and Participant information'
                       ' records only no asset data being parsed.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-F-Cloud_Shared_Methods',
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
def Ph31iCloudSPLwithParticipantswithNADPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("13.7"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        CASE zShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            WHEN 3 THEN '3-SPL-Actively-Sharing-3'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
        END AS 'zShare-Status',
        CASE zShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            WHEN 5 THEN '5-SPL-Active-Participant-5'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
        END AS 'zShare-Scope Type',
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        CASE zShare.ZLOCALPUBLISHSTATE
            WHEN 2 THEN '2-Published-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
        END AS 'zShare-Local Publish State',
        CASE zShare.ZPUBLICPERMISSION
            WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
            WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
        END AS 'zShare-Public Permission',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_This_User-0'
            WHEN 1 THEN '1-Participant-Is_This_User-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE zSharePartic.ZPERMISSION
            WHEN 3 THEN '3-Participant-has-Full-Permissions-3'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
        END AS 'zSharePartic-Premission',
        CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
            WHEN 0 THEN '0-DoNotNotify-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
        END AS 'zShare-Should Notify On Upload Completion',
        CASE zShare.ZSHOULDIGNOREBUDGETS
            WHEN 1 THEN '1-StillTesting-CMM-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
        END AS 'zShare-Should Ignore Budgets',
        CASE zShare.ZTRASHEDSTATE
            WHEN 0 THEN '0-Not_in_Trash-0'
            WHEN 1 THEN '1-In_Trash-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
        END AS 'zShare-Trashed State',
        CASE zShare.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-Not Deleted-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
        END AS 'zShare-Cloud Delete State',
        CASE zShare.Z_ENT
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-64'
            ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
        END AS 'zShare-zENT'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE IN (4, 5)
        ORDER BY zShare.ZCREATIONDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25]))

        data_headers = ('zShare-Creation Date-0',
                        'zShare-Start Date-1',
                        'zShare-End Date-2',
                        'zShare-Expiry Date-3',
                        'zShare-UUID-4',
                        'zShare-Originating Scope ID-5',
                        'zShare-Status-6',
                        'zShare-Scope Type-7',
                        'zShare-Scope ID-8',
                        'zShare-Title-SPL-9',
                        'zShare-Share URL-10',
                        'zShare-Local Publish State-11',
                        'zShare-Public Permission-12',
                        'zSharePartic-Acceptance Status-13',
                        'zSharePartic-User ID-14',
                        'zSharePartic-zPK-15',
                        'zSharePartic-Email Address-16',
                        'zSharePartic-Phone Number-17',
                        'zSharePartic-Is Current User-18',
                        'zSharePartic-Role-19',
                        'zSharePartic-Premission-20',
                        'zShare-Should Notify On Upload Completion-21',
                        'zShare-Should Ignore Budgets-22',
                        'zShare-Trashed State-23',
                        'zShare-Cloud Delete State-24',
                        'zShare-zENT-25')
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
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        CASE zSharePartic.Z54_SHARE
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-64'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.Z54_SHARE || ''
        END AS 'zSharePartic-z54SHARE',
        CASE zShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            WHEN 3 THEN '3-SPL-Actively-Sharing-3'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
        END AS 'zShare-Status',
        CASE zShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            WHEN 5 THEN '5-SPL-Active-Participant-5'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
        END AS 'zShare-Scope Type',
        zShare.ZCLOUDPHOTOCOUNT AS 'zShare-Cloud Photo Count',
        zShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare',
        zShare.ZCLOUDVIDEOCOUNT AS 'zShare-Cloud Video Count',
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        CASE zShare.ZLOCALPUBLISHSTATE
            WHEN 2 THEN '2-Published-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
        END AS 'zShare-Local Publish State',
        CASE zShare.ZPUBLICPERMISSION
            WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
            WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
        END AS 'zShare-Public Permission',
        CASE zShare.ZCLOUDLOCALSTATE
            WHEN 1 THEN '1-LocalandCloud-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDLOCALSTATE || ''
        END AS 'zShare-Cloud Local State',
        CASE zShare.ZSCOPESYNCINGSTATE
            WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPESYNCINGSTATE || ''
        END AS 'zShare-Scope Syncing State',
        CASE zShare.ZAUTOSHAREPOLICY
            WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZAUTOSHAREPOLICY || ''
        END AS 'zShare-Auto Share Policy',  
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',  
        zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
        zSharePartic.ZUUID AS 'zSharePartic-UUID',  
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_This_User-0'
            WHEN 1 THEN '1-Participant-Is_This_User-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE zSharePartic.ZPERMISSION
            WHEN 3 THEN '3-Participant-has-Full-Permissions-3'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
        END AS 'zSharePartic-Premission',
        CASE zShare.ZPARTICIPANTCLOUDUPDATESTATE
            WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
        END AS 'zShare-Participant Cloud Update State', 
        CASE zSharePartic.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZEXITSTATE || ''
        END AS 'zSharePartic-Exit State',
        CASE zShare.ZPREVIEWSTATE
            WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPREVIEWSTATE || ''
        END AS 'zShare-Preview State',
        CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
            WHEN 0 THEN '0-DoNotNotify-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
        END AS 'zShare-Should Notify On Upload Completion',
        CASE zShare.ZSHOULDIGNOREBUDGETS
            WHEN 1 THEN '1-StillTesting-CMM-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
        END AS 'zShare-Should Ignore Budgets',
        CASE zShare.ZEXITSOURCE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSOURCE || ''
        END AS 'zShare-Exit Source',
        CASE zShare.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSTATE || ''
        END AS 'zShare-Exit State',
        CASE zShare.ZEXITTYPE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITTYPE || ''
        END AS 'zShare-Exit Type',
        CASE zShare.ZTRASHEDSTATE
            WHEN 0 THEN '0-Not_in_Trash-0'
            WHEN 1 THEN '1-In_Trash-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
        END AS 'zShare-Trashed State',
        CASE zShare.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-Not Deleted-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
        END AS 'zShare-Cloud Delete State',
        DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
        'zShare-LastParticipant Asset Trash Notification Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS
        'zShare-Last Participant Asset Trash Notification View Date',
        CASE zShare.Z_ENT
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-64'
            ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
        END AS 'zShare-zENT'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE IN (4, 5)
        ORDER BY zShare.ZCREATIONDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43]))

        data_headers = ('zShare-Creation Date-0',
                        'zShare-Start Date-1',
                        'zShare-End Date-2',
                        'zShare-Expiry Date-3',
                        'zShare-UUID-4',
                        'zShare-Originating Scope ID-5',
                        'zSharePartic-z54SHARE-6',
                        'zShare-Status-7',
                        'zShare-Scope Type-8',
                        'zShare-Cloud Photo Count-9',
                        'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-10',
                        'zShare-Cloud Video Count-11',
                        'zShare-Scope ID-12',
                        'zShare-Title-SPL-13',
                        'zShare-Share URL-14',
                        'zShare-Local Publish State-15',
                        'zShare-Public Permission-16',
                        'zShare-Cloud Local State-17',
                        'zShare-Scope Syncing State-18',
                        'zShare-Auto Share Policy-19',
                        'zSharePartic-Acceptance Status-20',
                        'zSharePartic-User ID-21',
                        'zSharePartic-zPK-22',
                        'zSharePartic-Email Address-23',
                        'zSharePartic-Phone Number-24',
                        'zSharePartic-Participant ID-25',
                        'zSharePartic-UUID-26',
                        'zSharePartic-Is Current User-27',
                        'zSharePartic-Role-28',
                        'zSharePartic-Premission-29',
                        'zShare-Participant Cloud Update State-30',
                        'zSharePartic-Exit State-31',
                        'zShare-Preview State-32',
                        'zShare-Should Notify On Upload Completion-33',
                        'zShare-Should Ignore Budgets-34',
                        'zShare-Exit Source-35',
                        'zShare-Exit State-36',
                        'zShare-Exit Type-37',
                        'zShare-Trashed State-38',
                        'zShare-Cloud Delete State-39',
                        'zShare-Trashed Date-40',
                        'zShare-LastParticipant Asset Trash Notification Date-41',
                        'zShare-Last Participant Asset Trash Notification View Date-42',
                        'zShare-zENT-43')
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
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        CASE zSharePartic.Z55_SHARE
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-64'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.Z55_SHARE || ''
        END AS 'zSharePartic-z55SHARE',
        CASE zShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            WHEN 3 THEN '3-SPL-Actively-Sharing-3'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
        END AS 'zShare-Status',
        CASE zShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            WHEN 5 THEN '5-SPL-Active-Participant-5'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
        END AS 'zShare-Scope Type',
        zShare.ZCLOUDPHOTOCOUNT AS 'zShare-Cloud Photo Count',
        zShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare',
        zShare.ZCLOUDVIDEOCOUNT AS 'zShare-Cloud Video Count',
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        CASE zShare.ZLOCALPUBLISHSTATE
            WHEN 2 THEN '2-Published-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
        END AS 'zShare-Local Publish State',
        CASE zShare.ZPUBLICPERMISSION
            WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
            WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
        END AS 'zShare-Public Permission',
        CASE zShare.ZCLOUDLOCALSTATE
            WHEN 1 THEN '1-LocalandCloud-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDLOCALSTATE || ''
        END AS 'zShare-Cloud Local State',
        CASE zShare.ZSCOPESYNCINGSTATE
            WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPESYNCINGSTATE || ''
        END AS 'zShare-Scope Syncing State',
        CASE zShare.ZAUTOSHAREPOLICY
            WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZAUTOSHAREPOLICY || ''
        END AS 'zShare-Auto Share Policy',  
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',  
        zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
        zSharePartic.ZUUID AS 'zSharePartic-UUID',  
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_This_User-0'
            WHEN 1 THEN '1-Participant-Is_This_User-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE zSharePartic.ZPERMISSION
            WHEN 3 THEN '3-Participant-has-Full-Permissions-3'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
        END AS 'zSharePartic-Premission',
        CASE zShare.ZPARTICIPANTCLOUDUPDATESTATE
            WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
        END AS 'zShare-Participant Cloud Update State', 
        CASE zSharePartic.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZEXITSTATE || ''
        END AS 'zSharePartic-Exit State',
        CASE zShare.ZPREVIEWSTATE
            WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPREVIEWSTATE || ''
        END AS 'zShare-Preview State',
        CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
            WHEN 0 THEN '0-DoNotNotify-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
        END AS 'zShare-Should Notify On Upload Completion',
        CASE zShare.ZSHOULDIGNOREBUDGETS
            WHEN 1 THEN '1-StillTesting-CMM-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
        END AS 'zShare-Should Ignore Budgets',
        CASE zShare.ZEXITSOURCE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSOURCE || ''
        END AS 'zShare-Exit Source',
        CASE zShare.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSTATE || ''
        END AS 'zShare-Exit State',
        CASE zShare.ZEXITTYPE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITTYPE || ''
        END AS 'zShare-Exit Type',
        CASE zShare.ZTRASHEDSTATE
            WHEN 0 THEN '0-Not_in_Trash-0'
            WHEN 1 THEN '1-In_Trash-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
        END AS 'zShare-Trashed State',
        CASE zShare.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-Not Deleted-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
        END AS 'zShare-Cloud Delete State',
        DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
        'zShare-LastParticipant Asset Trash Notification Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS
        'zShare-Last Participant Asset Trash Notification View Date',
        CASE zShare.Z_ENT
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-64'
            ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
        END AS 'zShare-zENT'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE IN (4, 5)
        ORDER BY zShare.ZCREATIONDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43]))

        data_headers = ('zShare-Creation Date-0',
                        'zShare-Start Date-1',
                        'zShare-End Date-2',
                        'zShare-Expiry Date-3',
                        'zShare-UUID-4',
                        'zShare-Originating Scope ID-5',
                        'zSharePartic-z55SHARE-6',
                        'zShare-Status-7',
                        'zShare-Scope Type-8',
                        'zShare-Cloud Photo Count-9',
                        'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-10',
                        'zShare-Cloud Video Count-11',
                        'zShare-Scope ID-12',
                        'zShare-Title-SPL-13',
                        'zShare-Share URL-14',
                        'zShare-Local Publish State-15',
                        'zShare-Public Permission-16',
                        'zShare-Cloud Local State-17',
                        'zShare-Scope Syncing State-18',
                        'zShare-Auto Share Policy-19',
                        'zSharePartic-Acceptance Status-20',
                        'zSharePartic-User ID-21',
                        'zSharePartic-zPK-22',
                        'zSharePartic-Email Address-23',
                        'zSharePartic-Phone Number-24',
                        'zSharePartic-Participant ID-25',
                        'zSharePartic-UUID-26',
                        'zSharePartic-Is Current User-27',
                        'zSharePartic-Role-28',
                        'zSharePartic-Premission-29',
                        'zShare-Participant Cloud Update State-30',
                        'zSharePartic-Exit State-31',
                        'zShare-Preview State-32',
                        'zShare-Should Notify On Upload Completion-33',
                        'zShare-Should Ignore Budgets-34',
                        'zShare-Exit Source-35',
                        'zShare-Exit State-36',
                        'zShare-Exit Type-37',
                        'zShare-Trashed State-38',
                        'zShare-Cloud Delete State-39',
                        'zShare-Trashed Date-40',
                        'zShare-LastParticipant Asset Trash Notification Date-41',
                        'zShare-Last Participant Asset Trash Notification View Date-42',
                        'zShare-zENT-43')
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
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        CASE zSharePartic.Z61_SHARE
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-64'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.Z61_SHARE || ''
        END AS 'zSharePartic-z61SHARE',
        CASE zShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            WHEN 3 THEN '3-SPL-Actively-Sharing-3'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
        END AS 'zShare-Status',
        CASE zShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            WHEN 5 THEN '5-SPL-Active-Participant-5'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
        END AS 'zShare-Scope Type',
        zShare.ZCLOUDPHOTOCOUNT AS 'zShare-Cloud Photo Count',
        zShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare',
        zShare.ZCLOUDVIDEOCOUNT AS 'zShare-Cloud Video Count',
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        CASE zShare.ZLOCALPUBLISHSTATE
            WHEN 2 THEN '2-Published-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
        END AS 'zShare-Local Publish State',
        CASE zShare.ZPUBLICPERMISSION
            WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
            WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
        END AS 'zShare-Public Permission',
        CASE zShare.ZCLOUDLOCALSTATE
            WHEN 1 THEN '1-LocalandCloud-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDLOCALSTATE || ''
        END AS 'zShare-Cloud Local State',
        CASE zShare.ZSCOPESYNCINGSTATE
            WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPESYNCINGSTATE || ''
        END AS 'zShare-Scope Syncing State',
        CASE zShare.ZAUTOSHAREPOLICY
            WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZAUTOSHAREPOLICY || ''
        END AS 'zShare-Auto Share Policy',  
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',  
        zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
        zSharePartic.ZUUID AS 'zSharePartic-UUID',  
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_This_User-0'
            WHEN 1 THEN '1-Participant-Is_This_User-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE zSharePartic.ZPERMISSION
            WHEN 3 THEN '3-Participant-has-Full-Permissions-3'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
        END AS 'zSharePartic-Premission',
        CASE zShare.ZPARTICIPANTCLOUDUPDATESTATE
            WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
        END AS 'zShare-Participant Cloud Update State', 
        CASE zSharePartic.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZEXITSTATE || ''
        END AS 'zSharePartic-Exit State',
        CASE zShare.ZPREVIEWSTATE
            WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPREVIEWSTATE || ''
        END AS 'zShare-Preview State',
        CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
            WHEN 0 THEN '0-DoNotNotify-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
        END AS 'zShare-Should Notify On Upload Completion',
        CASE zShare.ZSHOULDIGNOREBUDGETS
            WHEN 1 THEN '1-StillTesting-CMM-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
        END AS 'zShare-Should Ignore Budgets',
        CASE zShare.ZEXITSOURCE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSOURCE || ''
        END AS 'zShare-Exit Source',
        CASE zShare.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSTATE || ''
        END AS 'zShare-Exit State',
        CASE zShare.ZEXITTYPE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITTYPE || ''
        END AS 'zShare-Exit Type',
        CASE zShare.ZTRASHEDSTATE
            WHEN 0 THEN '0-Not_in_Trash-0'
            WHEN 1 THEN '1-In_Trash-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
        END AS 'zShare-Trashed State',
        CASE zShare.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-Not Deleted-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
        END AS 'zShare-Cloud Delete State',
        DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
        'zShare-LastParticipant Asset Trash Notification Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS
        'zShare-Last Participant Asset Trash Notification View Date',
        CASE zShare.Z_ENT
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-64'
            ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
        END AS 'zShare-zENT'
        FROM ZSHARE zShare
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zShare.ZSCOPETYPE IN (4, 5)
        ORDER BY zShare.ZCREATIONDATE
        '''
        
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                              row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                              row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                              row[37], row[38], row[39], row[40], row[41], row[42], row[43]))

        data_headers = ('zShare-Creation Date-0',
                        'zShare-Start Date-1',
                        'zShare-End Date-2',
                        'zShare-Expiry Date-3',
                        'zShare-UUID-4',
                        'zShare-Originating Scope ID-5',
                        'zSharePartic-z61SHARE-6',
                        'zShare-Status-7',
                        'zShare-Scope Type-8',
                        'zShare-Cloud Photo Count-9',
                        'zShare-CountOfAssets AddedByCamera Smart Sharing-HomeShare-10',
                        'zShare-Cloud Video Count-11',
                        'zShare-Scope ID-12',
                        'zShare-Title-SPL-13',
                        'zShare-Share URL-14',
                        'zShare-Local Publish State-15',
                        'zShare-Public Permission-16',
                        'zShare-Cloud Local State-17',
                        'zShare-Scope Syncing State-18',
                        'zShare-Auto Share Policy-19',
                        'zSharePartic-Acceptance Status-20',
                        'zSharePartic-User ID-21',
                        'zSharePartic-zPK-22',
                        'zSharePartic-Email Address-23',
                        'zSharePartic-Phone Number-24',
                        'zSharePartic-Participant ID-25',
                        'zSharePartic-UUID-26',
                        'zSharePartic-Is Current User-27',
                        'zSharePartic-Role-28',
                        'zSharePartic-Premission-29',
                        'zShare-Participant Cloud Update State-30',
                        'zSharePartic-Exit State-31',
                        'zShare-Preview State-32',
                        'zShare-Should Notify On Upload Completion-33',
                        'zShare-Should Ignore Budgets-34',
                        'zShare-Exit Source-35',
                        'zShare-Exit State-36',
                        'zShare-Exit Type-37',
                        'zShare-Trashed State-38',
                        'zShare-Cloud Delete State-39',
                        'zShare-Trashed Date-40',
                        'zShare-LastParticipant Asset Trash Notification Date-41',
                        'zShare-Last Participant Asset Trash Notification View Date-42',
                        'zShare-zENT-43')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
