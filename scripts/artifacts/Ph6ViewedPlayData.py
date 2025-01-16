__artifacts_v2__ = {
    'Ph6ViewandPlayDataPhDaPsql': {
        'name': 'Ph6-View and Play Data-PhDaPsql',
        'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for assets with'
                       ' view and played data in versions 11-18. If the iOS version is greater than iOS 16.5'
                       ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field'
                       ' will be included. The results for this script will contain'
                       ' one row per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
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
def Ph6ViewandPlayDataPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotosData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("13")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
        zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
        zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
        zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',        
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
        WHERE (zAddAssetAttr.ZPENDINGVIEWCOUNT > 0) OR (zAddAssetAttr.ZVIEWCOUNT > 0)
         OR (zAddAssetAttr.ZPENDINGPLAYCOUNT > 0) OR (zAddAssetAttr.ZPLAYCOUNT > 0)
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13]))

        data_headers = (('zAsset-Modification Date', 'datetime'),
                        'zAddAssetAttr- Pending View Count',
                        'zAddAssetAttr- View Count',
                        'zAddAssetAttr- Pending Play Count',
                        'zAddAssetAttr- Play Count',
                        'zAsset-Directory-Path',
                        'zAsset-Filename',
                        'zAddAssetAttr- Original Filename',
                        'zCldMast- Original Filename',
                        'zCldMast-Import Session ID- AirDrop-StillTesting',
                        'zAsset-zPK',
                        'zAddAssetAttr-zPK',
                        'zAsset-UUID = store.cloudphotodb',
                        'zAddAssetAttr-Master Fingerprint')
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
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zAsset-Analysis State Modification Date',
        zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
        zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
        zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
        zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',        
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
        WHERE (zAddAssetAttr.ZPENDINGVIEWCOUNT > 0) OR (zAddAssetAttr.ZVIEWCOUNT > 0)
         OR (zAddAssetAttr.ZPENDINGPLAYCOUNT > 0) OR (zAddAssetAttr.ZPLAYCOUNT > 0)
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14]))

        data_headers = (('zAsset-Modification Date', 'datetime'),
                        'zAsset-Analysis State Modification Date',
                        'zAddAssetAttr- Pending View Count',
                        'zAddAssetAttr- View Count',
                        'zAddAssetAttr- Pending Play Count',
                        'zAddAssetAttr- Play Count',
                        'zAsset-Directory-Path',
                        'zAsset-Filename',
                        'zAddAssetAttr- Original Filename',
                        'zCldMast- Original Filename',
                        'zCldMast-Import Session ID- AirDrop-StillTesting',
                        'zAsset-zPK',
                        'zAddAssetAttr-zPK',
                        'zAsset-UUID = store.cloudphotodb',
                        'zAddAssetAttr-Master Fingerprint')
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
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zAsset-Analysis State Modification Date',
        zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
        zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
        zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
        zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',        
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
        WHERE (zAddAssetAttr.ZPENDINGVIEWCOUNT > 0) OR (zAddAssetAttr.ZVIEWCOUNT > 0)
         OR (zAddAssetAttr.ZPENDINGPLAYCOUNT > 0) OR (zAddAssetAttr.ZPLAYCOUNT > 0)
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14]))

        data_headers = (('zAsset-Modification Date', 'datetime'),
                        'zAsset-Analysis State Modification Date',
                        'zAddAssetAttr- Pending View Count',
                        'zAddAssetAttr- View Count',
                        'zAddAssetAttr- Pending Play Count',
                        'zAddAssetAttr- Play Count',
                        'zAsset-Directory-Path',
                        'zAsset-Filename',
                        'zAddAssetAttr- Original Filename',
                        'zCldMast- Original Filename',
                        'zCldMast-Import Session ID- AirDrop-StillTesting',
                        'zAsset-zPK',
                        'zAddAssetAttr-zPK',
                        'zAsset-UUID = store.cloudphotodb',
                        'zAddAssetAttr-Master Fingerprint')
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
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zAsset-Analysis State Modification Date',
        zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
        zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
        zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
        zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',        
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
        WHERE (zAddAssetAttr.ZPENDINGVIEWCOUNT > 0) OR (zAddAssetAttr.ZVIEWCOUNT > 0)
         OR (zAddAssetAttr.ZPENDINGPLAYCOUNT > 0) OR (zAddAssetAttr.ZPLAYCOUNT > 0)
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15]))

        data_headers = (('zAsset-Modification Date', 'datetime'),
                        'zAsset-Analysis State Modification Date',
                        'zAddAssetAttr- Pending View Count',
                        'zAddAssetAttr- View Count',
                        'zAddAssetAttr- Pending Play Count',
                        'zAddAssetAttr- Play Count',
                        'zAsset-Directory-Path',
                        'zAsset-Filename',
                        'zAddAssetAttr- Original Filename',
                        'zCldMast- Original Filename',
                        'zCldMast-Import Session ID- AirDrop-StillTesting',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files',
                        'zAsset-zPK',
                        'zAddAssetAttr-zPK',
                        'zAsset-UUID = store.cloudphotodb',
                        'zAddAssetAttr-Master Fingerprint')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) <= version.parse("16.5.1")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',        
        DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zAsset-Analysis State Modification Date',
        zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
        zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
        zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
        zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',        
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
        WHERE (zAddAssetAttr.ZLASTVIEWEDDATE > 0) OR (zAddAssetAttr.ZPENDINGVIEWCOUNT > 0)
         OR (zAddAssetAttr.ZVIEWCOUNT > 0) OR (zAddAssetAttr.ZPENDINGPLAYCOUNT > 0) OR (zAddAssetAttr.ZPLAYCOUNT > 0)
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15]))

        data_headers = (('zAsset-Modification Date', 'datetime'),
                        'zAsset-Analysis State Modification Date',
                        'zAddAssetAttr- Pending View Count',
                        'zAddAssetAttr- View Count',
                        'zAddAssetAttr- Pending Play Count',
                        'zAddAssetAttr- Play Count',
                        'zAsset-Directory-Path',
                        'zAsset-Filename',
                        'zAddAssetAttr- Original Filename',
                        'zCldMast- Original Filename',
                        'zCldMast-Import Session ID- AirDrop-StillTesting',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files',
                        'zAsset-zPK',
                        'zAddAssetAttr-zPK',
                        'zAsset-UUID = store.cloudphotodb',
                        'zAddAssetAttr-Master Fingerprint')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16.6")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',        
        DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zAsset-Analysis State Modification Date',
        zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
        zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
        zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
        zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',        
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
        WHERE (zAddAssetAttr.ZLASTVIEWEDDATE > 0) OR (zAddAssetAttr.ZPENDINGVIEWCOUNT > 0)
         OR (zAddAssetAttr.ZVIEWCOUNT > 0) OR (zAddAssetAttr.ZPENDINGPLAYCOUNT > 0) OR (zAddAssetAttr.ZPLAYCOUNT > 0)
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16]))

        data_headers = (('zAddAssetAttr-Last Viewed Date-0', 'datetime'),
                        'zAsset-Modification Date-1',
                        ('zAsset-Analysis State Modification Date-2', 'datetime'),
                        'zAddAssetAttr- Pending View Count-3',
                        'zAddAssetAttr- View Count-4',
                        'zAddAssetAttr- Pending Play Count-5',
                        'zAddAssetAttr- Play Count-6',
                        'zAsset-Directory-Path-7',
                        'zAsset-Filename-8',
                        'zAddAssetAttr- Original Filename-9',
                        'zCldMast- Original Filename-10',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-11',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-12',
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
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',        
        DateTime(zAsset.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zAsset-Analysis State Modification Date',
        zAddAssetAttr.ZPENDINGVIEWCOUNT AS 'zAddAssetAttr- Pending View Count',
        zAddAssetAttr.ZVIEWCOUNT AS 'zAddAssetAttr- View Count',
        zAddAssetAttr.ZPENDINGPLAYCOUNT AS 'zAddAssetAttr- Pending Play Count',
        zAddAssetAttr.ZPLAYCOUNT AS 'zAddAssetAttr- Play Count',
        CASE zAddAssetAttr.ZVIEWPRESENTATION
            WHEN 0 THEN '0-Obs in iOS 18 still testing-0'
            WHEN 1 THEN '1-Obs in iOS 18 still testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZVIEWPRESENTATION || ''
        END AS 'zAddAssetAttr.View_Presentation',
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
        WHERE (zAddAssetAttr.ZLASTVIEWEDDATE > 0) OR (zAddAssetAttr.ZPENDINGVIEWCOUNT > 0)
         OR (zAddAssetAttr.ZVIEWCOUNT > 0) OR (zAddAssetAttr.ZPENDINGPLAYCOUNT > 0) OR (zAddAssetAttr.ZPLAYCOUNT > 0)
        ORDER BY zAsset.ZMODIFICATIONDATE
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18]))

        data_headers = (('zAddAssetAttr-Last Viewed Date-0', 'datetime'),
                        'zAsset-Modification Date-1',
                        ('zAsset-Analysis State Modification Date-2', 'datetime'),
                        'zAddAssetAttr- Pending View Count-3',
                        'zAddAssetAttr- View Count-4',
                        'zAddAssetAttr- Pending Play Count-5',
                        'zAddAssetAttr- Play Count-6',
                        'zAddAssetAttr.View_Presentation-7',
                        'zAsset-Directory-Path-8',
                        'zAsset-Filename-9',
                        'zAddAssetAttr- Original Filename-10',
                        'zCldMast- Original Filename-11',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-12',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                        'zAsset-zPK-14',
                        'zAddAssetAttr-zPK-15',
                        'zAsset-UUID = store.cloudphotodb-16',
                        'zAddAssetAttr-Original Stable Hash-17',
                        'zAddAssetAttr.Adjusted Stable Hash-18')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
