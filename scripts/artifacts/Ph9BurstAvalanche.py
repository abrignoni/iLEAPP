# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.2
#
#   Description:
#   Parses basic asset record data from Photos.sqlite for burst avalanche assets and supports iOS 11-17.
#   The results for this script will contain one record per ZASSET table Z_PK value.
#   This parser is based on research and SQLite queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
from datetime import datetime
import pytz
import json
import shutil
import base64
from PIL import Image
from pillow_heif import register_heif_opener
import glob
import sys
import stat
from pathlib import Path
import sqlite3
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph9burstavalanchephdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite burst avalanche assets from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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
        WHERE zAsset.ZAVALANCHEPICKTYPE > 0
        ORDER BY zAsset.ZDATECREATED    
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for burst avalanche assets' \
                          ' and supports iOS 11-13. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-Other_Artifacts')
            report.start_artifact_report(report_folder, 'Ph9-Burst Avalanche-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-Avalanche_Pick_Type-BurstAsset',
                            'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
                            'zAsset-Visibility State',
                            'zAsset-Directory-Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAsset-zPK',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph9-Burst Avalanche-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph9-Burst Avalanche-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Burst Avalanche Assets')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("14"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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
        WHERE zAsset.ZAVALANCHEPICKTYPE > 0
        ORDER BY zAsset.ZDATECREATED    
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for burst avalanche assets' \
                          ' and supports iOS 14-17. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-Other_Artifacts')
            report.start_artifact_report(report_folder, 'Ph9-Burst Avalanche-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-Avalanche_Pick_Type-BurstAsset',
                            'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
                            'zAsset-Visibility State',
                            'zAsset-Directory-Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAsset-zPK',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph9-Burst Avalanche-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph9-Burst Avalanche-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Burst Avalanche Assets')

        db.close()
        return


__artifacts_v2__ = {
    'Ph9-Burst Avalanche-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 9 Burst Avalanche Assets',
        'description': 'Parses basic asset record data from PhotoData-Photos.sqlite for burst avalanche assets'
                       ' and supports iOS 11-17. The results for this script will contain'
                       ' one record per ZASSET table Z_PK value.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.2',
        'date': '2024-04-07',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-Other_Artifacts',
        'notes': '',
        'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
        'function': 'get_ph9burstavalanchephdapsql'
    }
}
