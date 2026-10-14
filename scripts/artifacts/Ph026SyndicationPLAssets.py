__artifacts_v2__ = {
'Ph026_1SyndicationIDAssetsPhDaPsql': {
'name': 'Ph026.1-Syndication ID Assets-PhDaPsql',
'description': 'Assets with a stored Syndication Identifier in PhotoData/Photos.sqlite, with linked conversation album data when present. Queries cover iOS 15 through 26. Enum fields report their raw stored values without assigning user-action meanings.',
'author': '@AlexisBrignoni, Codex',
'creation_date': '2026-05-28',
'version': '6.0',
'date': '2026-05-27',
'last_update_date': '2026-10-10',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'Original parser and Photos.sqlite research: Scott Koenig, https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/. Raw enum projections preserve stored NULL and unknown values; per-value interpretations are not emitted.',
'paths': ('*/PhotoData/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "refresh",
'sample_data': {
'ctf2020_ios12': 'iOS 12.4 | 0 rows',
'dexter_ios18': 'iOS 18.3.2 | 3 rows',
'felix_ios17': 'iOS 17.6.1 | 0 rows',
'fsfull002_ios17': 'iOS 17.1 | 0 rows',
'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 3 rows',
'iphone12_ios18': 'iOS 18.7 | 0 rows',
'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
'otto_ios17': 'iOS 17.5.1 | 1 row',
'abe_ios16': 'iOS 16.5 | 7 rows',
'felix23_ios16': 'iOS 16.5 | 0 rows',
'hickman_ios13': 'iOS 13.3.1 | 0 rows',
'hickman_ios14': 'iOS 14.3 | 0 rows',
'jess_ios15': 'iOS 15.0.2 | 0 rows',
'magnet_ios16': 'iOS 16.1.1 | 0 rows',
}
},
'Ph026_2SyndicationPLAssetsSyndPL': {
'name': 'Ph026.2-Syndication PL Assets-SyndPL',
'description': 'Assets with a stored Syndication Identifier in Syndication.photoslibrary/database/Photos.sqlite, with linked conversation album data when present. Queries cover iOS 15 through 26. Enum fields report their raw stored values without assigning user-action meanings.',
'author': '@AlexisBrignoni, Codex',
'creation_date': '2026-05-28',
'version': '6.0',
'date': '2026-05-27',
'last_update_date': '2026-10-10',
'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
'category': 'Photos.sqlite',
'notes': 'Original parser and Photos.sqlite research: Scott Koenig, https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/. Raw enum projections preserve stored NULL and unknown values; per-value interpretations are not emitted.',
'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "message",
'sample_data': {
'dexter_ios18': 'iOS 18.3.2 | 34 rows',
'felix_ios17': 'iOS 17.6.1 | 9 rows',
'fsfull002_ios17': 'iOS 17.1 | 25 rows',
'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 16 rows',
'iphone12_ios18': 'iOS 18.7 | 2 rows',
'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
'otto_ios17': 'iOS 17.5.1 | 40 rows',
'abe_ios16': 'iOS 16.5 | 39 rows',
'felix23_ios16': 'iOS 16.5 | 9 rows',
'jess_ios15': 'iOS 15.0.2 | 0 rows',
'magnet_ios16': 'iOS 16.1.1 | 0 rows',
}
}
}

import os
from packaging import version
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, null_absent_columns, logfunc, iOS

@artifact_processor
def Ph026_1SyndicationIDAssetsPhDaPsql(context):
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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value'
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

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr- Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-31',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-32',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-33',
        'SWYConverszGenAlbum-Sync Event Order Key-34',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-35',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-36',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-37',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-38',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-39',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-40',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-41',
        ('SWYConverszGenAlbum-Trash Date-42', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-43')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED, zAsset.rowid, zAddAssetAttr.rowid, zExtAttr.rowid, SWYConverszGenAlbum.rowid, z27AlbumLists.rowid, zAlbumList.rowid, zCldMast.rowid
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-33',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-34',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-35',
        'SWYConverszGenAlbum-Sync Event Order Key-36',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-37',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-39',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-40',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-43',
        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-45',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-46')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
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

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-33',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-34',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-35',
        'SWYConverszGenAlbum-Sync Event Order Key-36',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-37',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-39',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-40',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-43',
        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-45',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-46')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("26")):
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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
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

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-34',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-35',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-36',
        'SWYConverszGenAlbum-Sync Event Order Key-37',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-39',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-40',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-43',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-44',
        ('SWYConverszGenAlbum-Trash Date-45', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-46',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-47')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("26")) & (version.parse(iosversion) < version.parse("27")):
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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_32ALBUMLISTS z32AlbumLists ON z32AlbumLists.Z_32ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z32AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-34',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-35',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-36',
        'SWYConverszGenAlbum-Sync Event Order Key-37',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-39',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-40',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-43',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-44',
        ('SWYConverszGenAlbum-Trash Date-45', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-46',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-47')
        data_list = list(get_sqlite_db_records(source_path, null_absent_columns(source_path, query)))

        return data_headers, data_list, source_path

@artifact_processor
def Ph026_2SyndicationPLAssetsSyndPL(context):
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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value'
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

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr- Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-31',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-32',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-33',
        'SWYConverszGenAlbum-Sync Event Order Key-34',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-35',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-36',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-37',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-38',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-39',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-40',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-41',
        ('SWYConverszGenAlbum-Trash Date-42', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-43')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED, zAsset.rowid, zAddAssetAttr.rowid, zExtAttr.rowid, SWYConverszGenAlbum.rowid, z27AlbumLists.rowid, zAlbumList.rowid, zCldMast.rowid
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-33',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-34',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-35',
        'SWYConverszGenAlbum-Sync Event Order Key-36',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-37',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-39',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-40',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-43',
        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-45',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-46')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
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

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-33',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-34',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-35',
        'SWYConverszGenAlbum-Sync Event Order Key-36',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-37',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-39',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-40',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-43',
        ('SWYConverszGenAlbum-Trash Date-44', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-45',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-46')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("26")):
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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
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

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-34',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-35',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-36',
        'SWYConverszGenAlbum-Sync Event Order Key-37',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-39',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-40',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-43',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-44',
        ('SWYConverszGenAlbum-Trash Date-45', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-46',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-47')
# data_list = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("26")) & (version.parse(iosversion) < version.parse("27")):
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
        zAsset.ZSYNDICATIONSTATE AS 'zAsset-ZSYNDICATIONSTATE Raw Value',
        zAsset.ZBUNDLESCOPE AS 'zAsset-ZBUNDLESCOPE Raw Value',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        zAsset.ZVISIBILITYSTATE AS 'zAsset-ZVISIBILITYSTATE Raw Value',
        zAsset.ZSAVEDASSETTYPE AS 'zAsset-ZSAVEDASSETTYPE Raw Value',
        zAddAssetAttr.ZSHARETYPE AS 'zAddAssetAttr-ZSHARETYPE Raw Value',
        zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE AS 'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value',
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
        SWYConverszGenAlbum.ZKIND AS 'SWYConverszGenAlbum-ZKIND Raw Value',
        SWYConverszGenAlbum.ZCLOUDLOCALSTATE AS 'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value',
        SWYConverszGenAlbum.ZSYNDICATE AS 'SWYConverszGenAlbum-ZSYNDICATE Raw Value',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        SWYConverszGenAlbum.ZISPINNED AS 'SWYConverszGenAlbum-ZISPINNED Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTKEY AS 'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value',
        SWYConverszGenAlbum.ZCUSTOMSORTASCENDING AS 'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value',
        SWYConverszGenAlbum.ZISPROTOTYPE AS 'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value',
        SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE AS 'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value',
        SWYConverszGenAlbum.ZCUSTOMQUERYTYPE AS 'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value',
        SWYConverszGenAlbum.ZTRASHEDSTATE AS 'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        SWYConverszGenAlbum.ZCLOUDDELETESTATE AS 'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value',
        SWYConverszGenAlbum.ZPRIVACYSTATE AS 'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION			
            LEFT JOIN Z_32ALBUMLISTS z32AlbumLists ON z32AlbumLists.Z_32ALBUMS = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z32AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAddAssetAttr.ZSYNDICATIONIDENTIFIER IS NOT NULL
        ORDER BY zAsset.ZDATECREATED
        '''

        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))
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
        'zAsset-ZSYNDICATIONSTATE Raw Value-13',
        'zAsset-ZBUNDLESCOPE Raw Value-14',
        'zAddAssetAttr.Imported by Bundle Identifier-15',
        'zAddAssetAttr-Imported By Display Name-16',
        'zAsset-ZVISIBILITYSTATE Raw Value-17',
        'zAsset-ZSAVEDASSETTYPE Raw Value-18',
        'zAddAssetAttr-ZSHARETYPE Raw Value-19',
        'zAsset-ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE Raw Value-20',
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
        'SWYConverszGenAlbum-ZKIND Raw Value-34',
        'SWYConverszGenAlbum-ZCLOUDLOCALSTATE Raw Value-35',
        'SWYConverszGenAlbum-ZSYNDICATE Raw Value-36',
        'SWYConverszGenAlbum-Sync Event Order Key-37',
        'SWYConverszGenAlbum-ZISPINNED Raw Value-38',
        'SWYConverszGenAlbum-ZCUSTOMSORTKEY Raw Value-39',
        'SWYConverszGenAlbum-ZCUSTOMSORTASCENDING Raw Value-40',
        'SWYConverszGenAlbum-ZISPROTOTYPE Raw Value-41',
        'SWYConverszGenAlbum-ZPROJECTDOCUMENTTYPE Raw Value-42',
        'SWYConverszGenAlbum-ZCUSTOMQUERYTYPE Raw Value-43',
        'SWYConverszGenAlbum-ZTRASHEDSTATE Raw Value-44',
        ('SWYConverszGenAlbum-Trash Date-45', 'datetime'),
        'SWYConverszGenAlbum-ZCLOUDDELETESTATE Raw Value-46',
        'SWYConverszGenAlbum-ZPRIVACYSTATE Raw Value-47')
        data_list = list(get_sqlite_db_records(source_path, null_absent_columns(source_path, query)))

        return data_headers, data_list, source_path
