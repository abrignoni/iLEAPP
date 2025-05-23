__artifacts_v2__ = {
    'Ph3_1TrashedRecentlyDeletedPhDaPsql': {
        'name': 'Ph3.1-Trashed Recently Deleted-PhDaPsql',
        'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for trashed-recently deleted'
                       ' assets and supports iOS 11-18. The results for this script will contain one row'
                       ' per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "trash-2"
    },
    'Ph3_2RemovedfromCameraRollSyndPL': {
        'name': 'Ph3.2-Removed from Camera Roll-SyndPL',
        'description': 'Parses basic asset row data from Syndication.photoslibrary-database-Photos.sqlite'
                       ' for syndication PL asserts remvoed from camera roll and supports iOS 15-18.'
                       ' These assets may have been displayed in the camera roll, then deleted from'
                       ' the camera roll view. The results for this script will contain one row per asset.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-S-Syndication_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "delete"
    },
    'Ph3_3TrashedRecentlyDeletedGenPlayPsql': {
        'name': 'Ph3.3-Trashed Recently Deleted-GenPlayPsql',
        'description': 'Parses basic asset row data from GenPlay-Photos.sqlite for trashed-recently deleted'
                       ' assets and supports iOS 18. The results for this script will contain one row'
                       ' per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '1.0',
        'date': '2025-02-05',
        'requirements': 'Acquisition that contains GenPlay-Photos.sqlite',
        'category': 'Photos.sqlite-P-GenerativePlayground_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Application/com.apple.GenerativePlayground/00000000-0000-0000-0000-000000000001.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "trash-2"
	}
}

import os
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc, iOS

@artifact_processor
def Ph3_1TrashedRecentlyDeletedPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)
        
        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE      
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
                        'zAsset-zPK-7',
                        'zAddAssetAttr-zPK-8',
                        'zAsset-UUID = store.cloudphotodb-9',
                        'zAddAssetAttr-Master Fingerprint-10')
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
                        'zAsset-zPK-7',
                        'zAddAssetAttr-zPK-8',
                        'zAsset-UUID = store.cloudphotodb-9',
                        'zAddAssetAttr-Master Fingerprint-10')
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
                        'zAsset-Syndication State-8',
                        'zAsset-zPK-9',
                        'zAddAssetAttr-zPK-10',
                        'zAsset-UUID = store.cloudphotodb-11',
                        'zAddAssetAttr-Master Fingerprint-12')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-2',
                        'SPLzSharePartic-zPK= TrashedByParticipant-3',
                        'SPLzSharePartic-Email Address-4',
                        'SPLzSharePartic-Phone Number-5',
                        'zAsset-Directory-Path-6',
                        'zAsset-Filename-7',
                        'zAddAssetAttr- Original Filename-8',
                        'zCldMast- Original Filename-9',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset-Syndication State-12',
                        'zAsset-zPK-13',
                        'zAddAssetAttr-zPK-14',
                        'zAsset-UUID = store.cloudphotodb-15',
                        'zAddAssetAttr-Master Fingerprint-16')
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-2',
                        'SPLzSharePartic-zPK= TrashedByParticipant-3',
                        'SPLzSharePartic-Email Address-4',
                        'SPLzSharePartic-Phone Number-5',
                        'zAsset-Directory-Path-6',
                        'zAsset-Filename-7',
                        'zAddAssetAttr- Original Filename-8',
                        'zCldMast- Original Filename-9',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset-Syndication State-12',
                        'zAsset-zPK-13',
                        'zAddAssetAttr-zPK-14',
                        'zAsset-UUID = store.cloudphotodb-15',
                        'zAddAssetAttr-Original Stable Hash-16',
                        'zAddAssetAttr.Adjusted Stable Hash-17')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph3_2RemovedfromCameraRollSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
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
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
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
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',               
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',           
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZSYNDICATIONSTATE IN (8, 10)
        ORDER BY zAddAssetAttr.ZLASTUPLOADATTEMPTDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13]))

        data_headers = (('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-0', 'datetime'),
                        'zAsset-Syndication State-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
                        ('zAsset-Trashed Date-8', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-9',
                        'zAsset-zPK-10',
                        'zAddAssetAttr-zPK-11',
                        'zAsset-UUID = store.cloudphotodb-12',
                        'zAddAssetAttr-Master Fingerprint-13')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
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
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',            
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',            
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZSYNDICATIONSTATE IN (8, 10)
        ORDER BY zAddAssetAttr.ZLASTUPLOADATTEMPTDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

        data_headers = (('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-0', 'datetime'),
                        'zAsset-Syndication State-1',
                        'zAsset-Directory-Path-2',
                        'zAsset-Filename-3',
                        'zAddAssetAttr- Original Filename-4',
                        'zCldMast- Original Filename-5',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
                        ('zAsset-Trashed Date-8', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-9',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-10',
                        'SPLzSharePartic-zPK= TrashedByParticipant-11',
                        'SPLzSharePartic-Email Address-12',
                        'SPLzSharePartic-Phone Number-13',
                        'zAsset-zPK-14',
                        'zAddAssetAttr-zPK-15',
                        'zAsset-UUID = store.cloudphotodb-16',
                        'zAddAssetAttr-Master Fingerprint-17')
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
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-2',
                        'SPLzSharePartic-zPK= TrashedByParticipant-3',
                        'SPLzSharePartic-Email Address-4',
                        'SPLzSharePartic-Phone Number-5',
                        'zAsset-Directory-Path-6',
                        'zAsset-Filename-7',
                        'zAddAssetAttr- Original Filename-8',
                        'zCldMast- Original Filename-9',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset-Syndication State-12',
                        'zAsset-zPK-13',
                        'zAddAssetAttr-zPK-14',
                        'zAsset-UUID = store.cloudphotodb-15',
                        'zAddAssetAttr-Original Stable Hash-16',
                        'zAddAssetAttr.Adjusted Stable Hash-17')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph3_3TrashedRecentlyDeletedGenPlayPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)
        
        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for GenPlay-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
                        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-2',
                        'SPLzSharePartic-zPK= TrashedByParticipant-3',
                        'SPLzSharePartic-Email Address-4',
                        'SPLzSharePartic-Phone Number-5',
                        'zAsset-Directory-Path-6',
                        'zAsset-Filename-7',
                        'zAddAssetAttr- Original Filename-8',
                        'zCldMast- Original Filename-9',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-10',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                        'zAsset-Syndication State-12',
                        'zAsset-zPK-13',
                        'zAddAssetAttr-zPK-14',
                        'zAsset-UUID = store.cloudphotodb-15',
                        'zAddAssetAttr-Original Stable Hash-16',
                        'zAddAssetAttr.Adjusted Stable Hash-17')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path