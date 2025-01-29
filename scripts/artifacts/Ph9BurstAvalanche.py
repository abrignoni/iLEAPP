__artifacts_v2__ = {
    'Ph9BurstAvalanchePhDaPsql': {
        'name': 'Ph9-Burst Avalanche-PhDaPsql',
        'description': 'Parses basic asset row data from PhotoData-Photos.sqlite for burst avalanche assets'
                       ' and supports iOS 11-17. The results for this script will contain'
                       ' one row per ZASSET table Z_PK value.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-C-Other_Artifacts',
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
def Ph9BurstAvalanchePhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',      
        CASE zAsset.ZAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
        END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
        CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
        END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
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
       WHERE (zAsset.ZAVALANCHEPICKTYPE > 0) OR
          (zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE > 0)
        ORDER BY zAsset.ZDATECREATED    
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-Avalanche_Pick_Type-BurstAsset-1',
                        'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-2',
                        'zAsset-Visibility State-3',
                        'zAsset-Directory-Path-4',
                        'zAsset-Filename-5',
                        'zAddAssetAttr- Original Filename-6',
                        'zCldMast- Original Filename-7',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-8',
                        'zAsset-zPK-9',
                        'zAddAssetAttr-zPK-10',
                        'zAsset-UUID = store.cloudphotodb-11',
                        'zAddAssetAttr-Master Fingerprint-12')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',      
        CASE zAsset.ZAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
        END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
        CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
        END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
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
        WHERE (zAsset.ZAVALANCHEPICKTYPE > 0) OR
          (zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE > 0)
        ORDER BY zAsset.ZDATECREATED    
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-Avalanche_Pick_Type-BurstAsset-1',
                        'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-2',
                        'zAsset-Visibility State-3',
                        'zAsset-Directory-Path-4',
                        'zAsset-Filename-5',
                        'zAddAssetAttr- Original Filename-6',
                        'zCldMast- Original Filename-7',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-8',
                        'zAsset-zPK-9',
                        'zAddAssetAttr-zPK-10',
                        'zAsset-UUID = store.cloudphotodb-11',
                        'zAddAssetAttr-Master Fingerprint-12')
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
        CASE zAsset.ZAVALANCHEKIND
            WHEN 0 THEN '0-No_Avalanche_Still_Testing-0'
            WHEN 1 THEN '1-Is_Avalanche_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEKIND || ''
        END AS 'zAsset-Avalanche_Kind',
        CASE zAsset.ZAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
        END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
        CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
        END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE (zAsset.ZAVALANCHEPICKTYPE > 0) OR
          (zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE > 0)
        ORDER BY zAsset.ZDATECREATED    
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                              row[10], row[11], row[12], row[13], row[14]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        'zAsset-Avalanche_Kind-1',
                        'zAsset-Avalanche_Pick_Type-BurstAsset-2',
                        'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-3',
                        'zAsset-Visibility State-4',
                        'zAsset-Directory-Path-5',
                        'zAsset-Filename-6',
                        'zAddAssetAttr- Original Filename-7',
                        'zCldMast- Original Filename-8',
                        'zCldMast-Import Session ID- AirDrop-StillTesting-9',
                        'zAsset-zPK-10',
                        'zAddAssetAttr-zPK-11',
                        'zAsset-UUID = store.cloudphotodb-12',
                        'zAddAssetAttr-Original Stable Hash-13',
                        'zAddAssetAttr.Adjusted Stable Hash-14')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
