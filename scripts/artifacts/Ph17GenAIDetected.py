__artifacts_v2__ = {
    'Ph17_1GenAIDetectedPhDaPsql': {
        'name': 'Ph17.1-Gen_AI_Detected-PhDaPsql',
        'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for assets'
                       ' with Gen AI Type >0 and supports iOS 18. The results for this script'
					   ' will contain one row per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '1.0',
        'date': '2025-02-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
		"artifact_icon": "edit"
    },
    'Ph17_2GenAIDetectedSyndPL': {
        'name': 'Ph17.2-Gen_AI_Detected-SyndPL',
        'description': 'Parses basic asset row data from Syndication.photoslibrary-database-Photos.sqlite for assets'
                       ' with Gen AI Type >0 and supports iOS 18. The results for this script'
					   ' will contain one row per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '1.0',
        'date': '2025-02-05',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-S-Syndication_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
		"artifact_icon": "edit"	
    },
    'Ph17_3GenAIDetectedGenPlayPsql': {
        'name': 'Ph17.3-Gen_AI_Detected-GenPlayPsql',
        'description': 'Parses basic asset row data from GenPlay-Photos.sqlite for assets'
                       ' with Gen AI Type >0 and supports iOS 18. The results for this script'
					   ' will contain one row per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '1.0',
        'date': '2025-02-05',
        'requirements': 'Acquisition that contains Library GenPlay Photos.sqlite',
        'category': 'Photos.sqlite-P-GenerativePlayground_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Application/com.apple.GenerativePlayground/00000000-0000-0000-0000-000000000001.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
		"artifact_icon": "edit"
    }	
}

import os
from packaging import version
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc, iOS

@artifact_processor
def Ph17_1GenAIDetectedPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
    if version.parse(iosversion) >= version.parse("18"):
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
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZISRECENTLYSAVED
            WHEN 0 THEN '0-Not_Recently_Saved_Still_Testing-0'
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
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',       
        zAsset.Z_PK AS 'zAsset-zPK',      
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash',
		CASE zExtAttr.ZGENERATIVEAITYPE
			WHEN 0 THEN '0-Gen_AI_Type_Not_Detected-0'
			WHEN 1 THEN '1-GenPlayground_or_3rdPrty_GenAI-1'
			WHEN 2 THEN '2-CleanUp-SafetyFilter-2'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit'		
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
		WHERE zExtAttr.ZGENERATIVEAITYPE > 0
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30]))

        data_headers = (
            ('zAsset-Date Created-0', 'datetime'),
            ('zAsset- SortToken -CameraRoll-1', 'datetime'),
            ('zAsset-Added Date-2', 'datetime'),
            ('zCldMast-Creation Date-3', 'datetime'),
            'zAddAssetAttr-Time Zone Name-4',
            'zAddAssetAttr-EXIF-String-5',
            ('zAsset-Modification Date-6', 'datetime'),
            ('zAsset-Last Shared Date-7', 'datetime'),
            ('zAsset-Trashed Date-8', 'datetime'),
            'zAsset-Trashed by Participant= zShareParticipant_zPK-9',
            'zAsset-Directory-Path-10',
            'zAsset-Filename-11',
            'zAddAssetAttr- Original Filename-12',
            'zCldMast- Original Filename-13',
            'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
            'zAddAssetAttr- Imported by Bundle Identifier-15',
            'zAddAssetAttr- Imported By Display Name-16',
            'zAsset-Is_Recently_Saved-17',
            'zAsset-Saved Asset Type-18',
            'zAsset-Syndication State-19',
            'zAsset-Bundle Scope-20',
            'zAddAssetAttr-Share Type-21',
            'zAsset-Active Library Scope Participation State-22',
            'zAsset-Visibility State-23',
            'zAsset-zPK-24',
            'zAddAssetAttr-zPK-25',
            'zAsset-UUID = store.cloudphotodb-26',
            'zAddAssetAttr-Original Stable Hash-27',
            'zAddAssetAttr.Adjusted Stable Hash-28',
			'zExtAttr-Generative_AI_Type-29',
			'zExtAttr-Credit-30')

        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    return (), [], source_path

@artifact_processor
def Ph17_2GenAIDetectedSyndPL(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for Syndication.photoslibrary iOS " + iosversion)
        return (), [], source_path
    if version.parse(iosversion) >= version.parse("18"):
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
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
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
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',       
        zAsset.Z_PK AS 'zAsset-zPK',      
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash',
		CASE zExtAttr.ZGENERATIVEAITYPE
			WHEN 0 THEN '0-Gen_AI_Type_Not_Detected-0'
			WHEN 1 THEN '1-GenPlayground_or_3rdPrty_GenAI-1'
			WHEN 2 THEN '2-CleanUp-SafetyFilter-2'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit'		
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
		WHERE zExtAttr.ZGENERATIVEAITYPE > 0
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30]))

        data_headers = (
            ('zAsset-Date Created-0', 'datetime'),
            ('zAsset- SortToken -CameraRoll-1', 'datetime'),
            ('zAsset-Added Date-2', 'datetime'),
            ('zCldMast-Creation Date-3', 'datetime'),
            'zAddAssetAttr-Time Zone Name-4',
            'zAddAssetAttr-EXIF-String-5',
            ('zAsset-Modification Date-6', 'datetime'),
            ('zAsset-Last Shared Date-7', 'datetime'),
            ('zAsset-Trashed Date-8', 'datetime'),
            'zAsset-Trashed by Participant= zShareParticipant_zPK-9',
            'zAsset-Directory-Path-10',
            'zAsset-Filename-11',
            'zAddAssetAttr- Original Filename-12',
            'zCldMast- Original Filename-13',
            'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
            'zAddAssetAttr- Imported by Bundle Identifier-15',
            'zAddAssetAttr- Imported By Display Name-16',
            'zAsset-Is_Recently_Saved-17',
            'zAsset-Saved Asset Type-18',
            'zAsset-Syndication State-19',
            'zAsset-Bundle Scope-20',
            'zAddAssetAttr-Share Type-21',
            'zAsset-Active Library Scope Participation State-22',
            'zAsset-Visibility State-23',
            'zAsset-zPK-24',
            'zAddAssetAttr-zPK-25',
            'zAsset-UUID = store.cloudphotodb-26',
            'zAddAssetAttr-Original Stable Hash-27',
            'zAddAssetAttr.Adjusted Stable Hash-28',
			'zExtAttr-Generative_AI_Type-29',
			'zExtAttr-Credit-30')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    return (), [], source_path

@artifact_processor
def Ph17_3GenAIDetectedGenPlayPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZISRECENTLYSAVED
            WHEN 0 THEN '0-Not_Recently_Saved_Still_Testing-0'
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
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',       
        zAsset.Z_PK AS 'zAsset-zPK',      
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash',
		CASE zExtAttr.ZGENERATIVEAITYPE
			WHEN 0 THEN '0-Gen_AI_Type_Not_Detected-0'
			WHEN 1 THEN '1-GenPlayground_or_3rdPrty_GenAI-1'
			WHEN 2 THEN '2-CleanUp-SafetyFilter-2'
			ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
		END AS 'zExtAttr-Generative_AI_Type',
		zExtAttr.ZCREDIT AS 'zExtAttr-Credit'		
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
			LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
		WHERE zExtAttr.ZGENERATIVEAITYPE > 0
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30]))

        data_headers = (
            ('zAsset-Date Created-0', 'datetime'),
            ('zAsset- SortToken -CameraRoll-1', 'datetime'),
            ('zAsset-Added Date-2', 'datetime'),
            ('zCldMast-Creation Date-3', 'datetime'),
            'zAddAssetAttr-Time Zone Name-4',
            'zAddAssetAttr-EXIF-String-5',
            ('zAsset-Modification Date-6', 'datetime'),
            ('zAsset-Last Shared Date-7', 'datetime'),
            ('zAsset-Trashed Date-8', 'datetime'),
            'zAsset-Trashed by Participant= zShareParticipant_zPK-9',
            'zAsset-Directory-Path-10',
            'zAsset-Filename-11',
            'zAddAssetAttr- Original Filename-12',
            'zCldMast- Original Filename-13',
            'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
            'zAddAssetAttr- Imported by Bundle Identifier-15',
            'zAddAssetAttr- Imported By Display Name-16',
            'zAsset-Is_Recently_Saved-17',
            'zAsset-Saved Asset Type-18',
            'zAsset-Syndication State-19',
            'zAsset-Bundle Scope-20',
            'zAddAssetAttr-Share Type-21',
            'zAsset-Active Library Scope Participation State-22',
            'zAsset-Visibility State-23',
            'zAsset-zPK-24',
            'zAddAssetAttr-zPK-25',
            'zAsset-UUID = store.cloudphotodb-26',
            'zAddAssetAttr-Original Stable Hash-27',
			'zAddAssetAttr.Adjusted Stable Hash-28',
			'zExtAttr-Generative_AI_Type-29',
			'zExtAttr-Credit-30')

        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path