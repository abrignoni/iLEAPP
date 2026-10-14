__artifacts_v2__ = {
'Ph003_1TrashedRecentlyDeletedPhDaPsql': {
'name': 'Ph003.1-Trashed Recently Deleted-PhDaPsql',
'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for trashed-recently deleted assets.'
' The results list assets whose ZTRASHEDSTATE is 1, on iOS 11 through 26. The results contain one'
' row per asset.'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'creation_date': '2026-05-28',
'last_update_date': '2026-10-10',
'version': '6.0',
'date': '2026-05-26',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'On iOS 16 and later the SPLzSharePartic columns are read from the ZSHAREPARTICIPANT row whose'
" Z_PK equals the asset's ZTRASHEDBYPARTICIPANT value. The Core Data model stored in the tested"
' databases (Z_MODELCACHE on abe_ios16, otto_ios17, dexter_ios18 and falken_ios26) defines'
' trashedByParticipant as a to-one relationship from Asset to ShareParticipant. The value names a'
' share participant record. Who operated the device is not recorded. On dexter_ios18'
' ZTRASHEDBYPARTICIPANT was filled on 2 of 3 rows and both resolved to a participant row. On'
' abe_ios16 (538 rows), otto_ios17 (2 rows) and iphone12_ios18 (5 rows) it was blank on every row.'
" Value labels in this report are the module author's working interpretations from testing. The"
' module cites no source for them. Each label carries the stored value. Labels marked STILLTESTING'
' are unconfirmed. The Syndication State labels for values 2, 8 and 10 are interpretations with no'
' cited source. The store records the state value. It does not record who changed it.',
'paths': ('*/PhotoData/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "trash",
'sample_data': {
'ctf2020_ios12': 'iOS 12.4 | 0 rows',
'dexter_ios18': 'iOS 18.3.2 | 3 rows',
'felix_ios17': 'iOS 17.6.1 | 0 rows',
'fsfull002_ios17': 'iOS 17.1 | 0 rows',
'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 0 rows',
'iphone12_ios18': 'iOS 18.7 | 5 rows',
'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
'otto_ios17': 'iOS 17.5.1 | 2 rows',
'abe_ios16': 'iOS 16.5 | 538 rows',
'felix23_ios16': 'iOS 16.5 | 0 rows',
'hickman_ios13': 'iOS 13.3.1 | 5 rows',
'hickman_ios14': 'iOS 14.3 | 3 rows',
'jess_ios15': 'iOS 15.0.2 | 0 rows',
'magnet_ios16': 'iOS 16.1.1 | 0 rows',
}
},
'Ph003_2RemovedfromCameraRollSyndPL': {
'name': 'Ph003.2-Removed from Camera Roll-SyndPL',
'description': 'Parses basic asset row data from Syndication.photoslibrary-database-Photos.sqlite for'
' Syndication library assets whose ZSYNDICATIONSTATE is 8 or 10, on iOS 15 through 26. No corpus'
" in sample_data produced a row, so this artifact's output is unexercised. The results contain one"
' row per asset.'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'creation_date': '2026-05-28',
'last_update_date': '2026-10-10',
'version': '6.0',
'date': '2026-05-26',
'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'On dexter_ios18, iphone12_ios18, hc_ios18_7 and iphone14plus_ios18 the Syndication library held'
' no asset in state 8 or 10 (34, 2, 0 and 0 assets), so the filter returns no row there. The'
" Syndication State labels are the module author's interpretation from testing. The module cites"
' no source for them. The store records the state value. It does not record who changed it. Labels'
' marked STILLTESTING are unconfirmed. On iOS 16 and later the SPLzSharePartic columns are read'
" from the ZSHAREPARTICIPANT row whose Z_PK equals the asset's ZTRASHEDBYPARTICIPANT value. The"
' Core Data model stored in the tested databases (Z_MODELCACHE on abe_ios16, otto_ios17,'
' dexter_ios18 and falken_ios26) defines trashedByParticipant as a to-one relationship from Asset'
' to ShareParticipant. The value names a share participant record. Who operated the device is not'
' recorded.',
'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "trash",
'sample_data': {
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
'felix_ios17': 'iOS 17.6.1 | 0 rows',
'fsfull002_ios17': 'iOS 17.1 | 0 rows',
'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 0 rows',
'iphone12_ios18': 'iOS 18.7 | 0 rows',
'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
'otto_ios17': 'iOS 17.5.1 | 0 rows',
'abe_ios16': 'iOS 16.5 | 0 rows',
'felix23_ios16': 'iOS 16.5 | 0 rows',
'jess_ios15': 'iOS 15.0.2 | 0 rows',
'magnet_ios16': 'iOS 16.1.1 | 0 rows',
}
},
'Ph003_3TrashedRecentlyDeletedGenPlayPsql': {
'name': 'Ph003.3-Trashed Recently Deleted-GenPlayPsql',
'description': 'Parses basic asset row data from GenPlay-Photos.sqlite for trashed-recently deleted assets on'
' iOS 18 through 26. Lists assets whose ZTRASHEDSTATE is 1. The results contain one row per asset.'
' The only corpus in sample_data is at 0 rows.'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'creation_date': '2026-05-28',
'last_update_date': '2026-10-10',
'version': '2.0',
'date': '2026-05-26',
'requirements': 'Acquisition that contains GenPlay-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'The SPLzSharePartic columns are read from the ZSHAREPARTICIPANT row whose Z_PK equals the'
" asset's ZTRASHEDBYPARTICIPANT value. The Core Data model stored in the tested PhotoData"
' databases (Z_MODELCACHE on abe_ios16, otto_ios17, dexter_ios18 and falken_ios26) defines'
' trashedByParticipant as a to-one relationship from Asset to ShareParticipant. The value names a'
' share participant record. Who operated the device is not recorded. Value labels in this report'
" are the module author's working interpretations from testing. The module cites no source for"
' them. Each label carries the stored value. Labels marked STILLTESTING are unconfirmed. The'
' Syndication State labels for values 2, 8 and 10 are interpretations with no cited source. The'
' store records the state value. It does not record who changed it.',
'paths': ('*/mobile/Library/Photos/Libraries/Application/com.apple.GenerativePlayground/00000000-0000-0000-0000-000000000001.photoslibrary/database/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "trash",
'sample_data': {
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
}
}
}

import os
from packaging import version
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, null_absent_columns, logfunc, iOS

@artifact_processor
def Ph003_1TrashedRecentlyDeletedPhDaPsql(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()
    source_path = ''
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
    if not iosversion:
        logfunc("No iOS version had been read when this artifact ran, Photos.sqlite was not queried")
        return (), [], source_path
    if (version.parse(iosversion) <= version.parse("10.3.4")) or (version.parse(iosversion) >= version.parse("27")):
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
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE      
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID-6',
        'zAsset-zPK-7',
        'zAddAssetAttr-zPK-8',
        'zAsset-UUID-9',
        'zAddAssetAttr-Master Fingerprint-10')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID-6',
        'zAsset-zPK-7',
        'zAddAssetAttr-zPK-8',
        'zAsset-UUID-9',
        'zAddAssetAttr-Master Fingerprint-10')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_Link_Removed-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Saved_SWY_Synd_Asset_Removed_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',      
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12]))

        data_headers = (('zAsset-Trashed Date-0', 'datetime'),
        'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID-6',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
        'zAsset-Syndication State-8',
        'zAsset-zPK-9',
        'zAddAssetAttr-zPK-10',
        'zAsset-UUID-11',
        'zAddAssetAttr-Master Fingerprint-12')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_Link_Removed-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Saved_SWY_Synd_Asset_Removed_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAsset.ZTRASHEDBYPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE, zAsset.rowid, zAddAssetAttr.rowid, zCldMast.rowid, SPLzShare.rowid, SPLzSharePartic.rowid
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zCldMast-Import Session ID-10',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
        'zAsset-Syndication State-12',
        'zAsset-zPK-13',
        'zAddAssetAttr-zPK-14',
        'zAsset-UUID-15',
        'zAddAssetAttr-Master Fingerprint-16')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("27")):
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
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_Link_Removed-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Saved_SWY_Synd_Asset_Removed_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAsset.ZTRASHEDBYPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zCldMast-Import Session ID-10',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
        'zAsset-Syndication State-12',
        'zAsset-zPK-13',
        'zAddAssetAttr-zPK-14',
        'zAsset-UUID-15',
        'zAddAssetAttr-Original Stable Hash-16',
        'zAddAssetAttr.Adjusted Stable Hash-17')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

@artifact_processor
def Ph003_2RemovedfromCameraRollSyndPL(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()
    source_path = ''
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
    if not iosversion:
        logfunc("No iOS version had been read when this artifact ran, Photos.sqlite was not queried")
        return (), [], source_path
    if (version.parse(iosversion) <= version.parse("14.8.1")) or (version.parse(iosversion) >= version.parse("27")):
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
            WHEN 2 THEN '2-SyndPs-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_Link_Removed-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Saved_SWY_Synd_Asset_Removed_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',               
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',           
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZSYNDICATIONSTATE IN (8, 10)
        ORDER BY zAddAssetAttr.ZLASTUPLOADATTEMPTDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13]))

        data_headers = (('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-0', 'datetime'),
        'zAsset-Syndication State-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID-6',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
        ('zAsset-Trashed Date-8', 'datetime'),
        'zAsset-Trashed State-LocalAssetRecentlyDeleted-9',
        'zAsset-zPK-10',
        'zAddAssetAttr-zPK-11',
        'zAsset-UUID-12',
        'zAddAssetAttr-Master Fingerprint-13')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
            WHEN 2 THEN '2-SyndPs-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_Link_Removed-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Saved_SWY_Synd_Asset_Removed_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',
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
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAsset.ZTRASHEDBYPARTICIPANT
        WHERE zAsset.ZSYNDICATIONSTATE IN (8, 10)
        ORDER BY zAddAssetAttr.ZLASTUPLOADATTEMPTDATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

        data_headers = (('zAddAssetAttr-Last Upload Attempt Date-SWY_Files-0', 'datetime'),
        'zAsset-Syndication State-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID-6',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
        ('zAsset-Trashed Date-8', 'datetime'),
        'zAsset-Trashed State-LocalAssetRecentlyDeleted-9',
        'zAsset-Trashed by Participant= zShareParticipant_zPK-10',
        'SPLzSharePartic-zPK= TrashedByParticipant-11',
        'SPLzSharePartic-Email Address-12',
        'SPLzSharePartic-Phone Number-13',
        'zAsset-zPK-14',
        'zAddAssetAttr-zPK-15',
        'zAsset-UUID-16',
        'zAddAssetAttr-Master Fingerprint-17')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("27")):
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
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_Link_Removed-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Saved_SWY_Synd_Asset_Removed_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAsset.ZTRASHEDBYPARTICIPANT
        WHERE zAsset.ZSYNDICATIONSTATE IN (8, 10)
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zCldMast-Import Session ID-10',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
        'zAsset-Syndication State-12',
        'zAsset-zPK-13',
        'zAddAssetAttr-zPK-14',
        'zAsset-UUID-15',
        'zAddAssetAttr-Original Stable Hash-16',
        'zAddAssetAttr.Adjusted Stable Hash-17')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

@artifact_processor
def Ph003_3TrashedRecentlyDeletedGenPlayPsql(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()
    source_path = ''
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
    if not iosversion:
        logfunc("No iOS version had been read when this artifact ran, Photos.sqlite was not queried")
        return (), [], source_path
    if (version.parse(iosversion) <= version.parse("10.3.4")) or (version.parse(iosversion) >= version.parse("27")):
        logfunc("Unsupported version for GenPlay-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("27")):
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
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_Link_Removed-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Saved_SWY_Synd_Asset_Removed_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAsset.ZTRASHEDBYPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zCldMast-Import Session ID-10',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
        'zAsset-Syndication State-12',
        'zAsset-zPK-13',
        'zAddAssetAttr-zPK-14',
        'zAsset-UUID-15',
        'zAddAssetAttr-Original Stable Hash-16',
        'zAddAssetAttr.Adjusted Stable Hash-17')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path