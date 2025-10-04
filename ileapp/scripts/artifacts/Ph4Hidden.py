__artifacts_v2__ = {
    'Ph4_1HiddenPhDaPsql': {
        'name': 'Ph4.1-Hidden-PhDaPsql',
        'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for hidden assets'
                       ' and supports iOS 11-18. The results for this script will contain'
                       ' one row per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "eye-off"
    },
    'Ph4_3HiddenGenPlayPsql': {
        'name': 'Ph4.3-Hidden-GenPlayPsql',
        'description': 'Parses basic asset row data from GenerativePlayground-Photos.sqlite for hidden assets'
                       ' and supports iOS 18. The results for this script will contain'
                       ' one row per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '1.0',
        'date': '2025-02-05',
        'requirements': 'Acquisition that contains GenerativePlayground-Photos.sqlite',
        'category': 'Photos.sqlite-P-GenerativePlayground_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Application/com.apple.GenerativePlayground/00000000-0000-0000-0000-000000000001.photoslibrary/database/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "eye-off"
	}
}

import os
from packaging import version
from ileapp.scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc, iOS

@artifact_processor
def Ph4_1HiddenPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
            return (), [], None
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZHIDDEN
            WHEN 0 THEN '0-Asset Not Hidden-0'
            WHEN 1 THEN '1-Asset Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
        END AS 'zAsset-Hidden',
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
        WHERE zAsset.ZHIDDEN = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
                        'zAsset-Hidden-1',
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
            return (), [], None
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZHIDDEN
            WHEN 0 THEN '0-Asset Not Hidden-0'
            WHEN 1 THEN '1-Asset Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
        END AS 'zAsset-Hidden',
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
        WHERE zAsset.ZHIDDEN = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
                        'zAsset-Hidden-1',
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

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], None
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZHIDDEN
            WHEN 0 THEN '0-Asset Not Hidden-0'
            WHEN 1 THEN '1-Asset Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
        END AS 'zAsset-Hidden',
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
        WHERE zAsset.ZHIDDEN = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11]))

        data_headers = (('zAsset-Modification Date-0', 'datetime'),
                        'zAsset-Hidden-1',
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
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], None
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZHIDDEN
            WHEN 0 THEN '0-Asset Not Hidden-0'
            WHEN 1 THEN '1-Asset Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
        END AS 'zAsset-Hidden',
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
        WHERE zAsset.ZHIDDEN = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12]))
                
        data_headers = (('zAsset-Modification Date-0', 'datetime'),
                        'zAsset-Hidden-1',
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
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

@artifact_processor
def Ph4_3HiddenGenPlayPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)
        
        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = iOS.get_version()
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for GenerativePlayground-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], None
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        CASE zAsset.ZHIDDEN
            WHEN 0 THEN '0-Asset Not Hidden-0'
            WHEN 1 THEN '1-Asset Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
        END AS 'zAsset-Hidden',
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
        WHERE zAsset.ZHIDDEN = 1
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12]))
                
        data_headers = (('zAsset-Modification Date-0', 'datetime'),
                        'zAsset-Hidden-1',
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
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path