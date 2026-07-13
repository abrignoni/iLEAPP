__artifacts_v2__ = {
'Ph007_1FavoritePhDaPsql': {
'name': 'Ph007.1-Favorite-PhDaPsql',
'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for favorite assets'
' and supports iOS. The results for this script will contain'
' one row per ZASSET table Z_PK value.'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'version': '6.0',
'date': '2026-05-26',
'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
'category': 'Photos.sqlite-Assets-Favorite-PhotoData-Psql',
'notes': '',
'paths': ('*/PhotoData/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "heart",
'sample_data': {
'ctf2020_ios12': 'iOS 12.4 | 0 rows',
'dexter_ios18': 'iOS 18.3.2 | 3 rows',
'felix_ios17': 'iOS 17.6.1 | 0 rows',
'fsfull002_ios17': 'iOS 17.1 | 0 rows',
'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
'iphone11_ios17': 'iOS 17.3 | 0 rows',
'iphone12_ios18': 'iOS 18.7 | 3076 rows',
'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
'otto_ios17': 'iOS 17.5.1 | 2 rows',
'abe_ios16': 'iOS 16.5 | 4 rows',
'felix23_ios16': 'iOS 16.5 | 0 rows',
'hickman_ios13': 'iOS 13.3.1 | 0 rows',
'hickman_ios14': 'iOS 14.3 | 0 rows',
'jess_ios15': 'iOS 15.0.2 | 0 rows',
'magnet_ios16': 'iOS 16.1.1 | 0 rows',
}
},
'Ph007_3FavoriteGenPlayPsql': {
'name': 'Ph007.3-Favorite-GenPlayPsql',
'description': 'Parses basic asset row data from GenPlay-Photos.sqlite for favorite assets'
' and supports iOS. The results for this script will contain'
' one row per ZASSET table Z_PK value.'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'version': '2.0',
'date': '2026-05-26',
'requirements': 'Acquisition that contains Library GenPlay Photos.sqlite',
'category': 'Photos.sqlite-Assets-Favorite-GenPlaygrndPL-Psql',
'notes': '',
'paths': ('*/mobile/Library/Photos/Libraries/Application/com.apple.GenerativePlayground/00000000-0000-0000-0000-000000000001.photoslibrary/database/Photos.sqlite*',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "heart",
'sample_data': {
'dexter_ios18': 'iOS 18.3.2 | 0 rows',
}
}
}

import os
from packaging import version
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, logfunc, iOS

@artifact_processor
def Ph007_1FavoritePhDaPsql(context):
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
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZFAVORITE
            WHEN 0 THEN '0-Asset Not Favorite-0'
            WHEN 1 THEN '1-Asset Favorite-1'
        END AS 'zAsset-Favorite',
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
        WHERE zAsset.ZFAVORITE = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
        'zAsset-Favorite-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
        'zAsset-zPK-7',
        'zAddAssetAttr-zPK-8',
        'zAsset-UUID = store.cloudphotodb-9',
        'zAddAssetAttr-Master Fingerprint-10')
# data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZFAVORITE
            WHEN 0 THEN '0-Asset Not Favorite-0'
            WHEN 1 THEN '1-Asset Favorite-1'
        END AS 'zAsset-Favorite',
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
        WHERE zAsset.ZFAVORITE = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
        'zAsset-Favorite-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
        'zAsset-zPK-7',
        'zAddAssetAttr-zPK-8',
        'zAsset-UUID = store.cloudphotodb-9',
        'zAddAssetAttr-Master Fingerprint-10')
# data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZFAVORITE
            WHEN 0 THEN '0-Asset Not Favorite-0'
            WHEN 1 THEN '1-Asset Favorite-1'
        END AS 'zAsset-Favorite',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZFAVORITE = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
        'zAsset-Favorite-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
        'zAsset-zPK-8',
        'zAddAssetAttr-zPK-9',
        'zAsset-UUID = store.cloudphotodb-10',
        'zAddAssetAttr-Master Fingerprint-11')
# data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("18")) & (version.parse(iosversion) < version.parse("27")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZFAVORITE
            WHEN 0 THEN '0-Asset Not Favorite-0'
            WHEN 1 THEN '1-Asset Favorite-1'
        END AS 'zAsset-Favorite',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZFAVORITE = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
        'zAsset-Favorite-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
        'zAsset-zPK-8',
        'zAddAssetAttr-zPK-9',
        'zAsset-UUID = store.cloudphotodb-10',
        'zAddAssetAttr-Original Stable Hash-11',
        'zAddAssetAttr.Adjusted Stable Hash-12')
# data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph007_3FavoriteGenPlayPsql(context):
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
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZFAVORITE
            WHEN 0 THEN '0-Asset Not Favorite-0'
            WHEN 1 THEN '1-Asset Favorite-1'
        END AS 'zAsset-Favorite',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZFAVORITE = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
            row[10], row[11], row[12]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
        'zAsset-Favorite-1',
        'zAsset-Directory-Path-2',
        'zAsset-Filename-3',
        'zAddAssetAttr- Original Filename-4',
        'zCldMast- Original Filename-5',
        'zCldMast-Import Session ID- AirDrop-StillTesting-6',
        'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
        'zAsset-zPK-8',
        'zAddAssetAttr-zPK-9',
        'zAsset-UUID = store.cloudphotodb-10',
        'zAddAssetAttr-Original Stable Hash-11',
        'zAddAssetAttr.Adjusted Stable Hash-12')
# data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path