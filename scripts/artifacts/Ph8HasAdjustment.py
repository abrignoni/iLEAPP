# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.2
#
#   Description:
#   Parses basic asset record data from Photos.sqlite for adjusted assets and supports iOS 11-17.
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
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, \
    open_sqlite_db_readonly


def get_ph8hasadjustmentphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) < version.parse("11"):
        logfunc("Unsupported version for PhotoData/Photos.sqlite adjusted assets from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zUnmAdj.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zUnmAdj-Adjustment Timestamp',
        CASE zAsset.ZHASADJUSTMENTS
            WHEN 0 THEN '0-No-Adjustments-0'
            WHEN 1 THEN '1-Yes-Adjustments-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
        END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',       
        zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
        zUnmAdj.ZEDITORLOCALIZEDNAME AS 'zUnmAdj-Editor Localized Name',
        zUnmAdj.ZADJUSTMENTFORMATIDENTIFIER AS 'zUnmAdj-Adjustment Format ID',
        CASE zUnmAdj.ZADJUSTMENTRENDERTYPES
            WHEN 0 THEN '0-Standard or Portrait with erros-0'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-Portrait-2'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTRENDERTYPES || ''
        END AS 'zUnmAdj-Adjustment Render Types',
        CASE zUnmAdj.ZADJUSTMENTFORMATVERSION
            WHEN 1.0 THEN '1.0-Markup-1.0'
            WHEN 1.1 THEN '1.1-Slow-Mo-1.1'
            WHEN 1.2 THEN '1.2-StillTesting'
            WHEN 1.3 THEN '1.3-StillTesting'
            WHEN 1.4 THEN '1.4-Filter-1.4'
            WHEN 1.5 THEN '1.5-Adjust-1.5'
            WHEN 1.6 THEN '1.6-Video-Trim-1.6'
            WHEN 1.7 THEN '1.7-StillTesting'
            WHEN 1.8 THEN '1.8-StillTesting'
            WHEN 1.9 THEN '1.9-StillTesting'
            WHEN 2.0 THEN '2.0-ScreenshotServices-2.0'
            ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTFORMATVERSION || ''
        END AS 'zUnmAdj-Adjustment Format Version',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
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
            LEFT JOIN ZUNMANAGEDADJUSTMENT zUnmAdj ON zAddAssetAttr.ZUNMANAGEDADJUSTMENT = zUnmAdj.Z_PK
        WHERE zAsset.ZHASADJUSTMENTS = 1
        ORDER BY zUnmAdj.ZADJUSTMENTTIMESTAMP
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for adjusted assets' \
                          ' and supports iOS 11-13. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph8-Has Adjustment-PhDaPsql', description)
            report.add_script()
            data_headers = ('zUnmAdj-Adjustment Timestamp',
                            'zAsset-Has Adjustments/Camera-Effects-Filters',
                            'zAddAssetAttr-Editor Bundle ID',
                            'zUnmAdj-Editor Localized Name',
                            'zUnmAdj-Adjustment Format ID',
                            'zUnmAdj-Adjustment Render Types',
                            'zUnmAdj-Adjustment Format Version',
                            'zAsset-Directory/Path',
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

            tsvname = 'Ph8-Has Adjustment-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph8-Has Adjustment-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite Adjusted Assets')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("14"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zUnmAdj.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zUnmAdj-Adjustment Timestamp',
        CASE zAsset.ZHASADJUSTMENTS
            WHEN 0 THEN '0-No-Adjustments-0'
            WHEN 1 THEN '1-Yes-Adjustments-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHASADJUSTMENTS || ''
        END AS 'zAsset-Has Adjustments/Camera-Effects-Filters',       
        zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
        zUnmAdj.ZEDITORLOCALIZEDNAME AS 'zUnmAdj-Editor Localized Name',
        zUnmAdj.ZADJUSTMENTFORMATIDENTIFIER AS 'zUnmAdj-Adjustment Format ID',
        CASE zUnmAdj.ZADJUSTMENTRENDERTYPES
            WHEN 0 THEN '0-Standard or Portrait with erros-0'
            WHEN 1 THEN '1-StillTesting'
            WHEN 2 THEN '2-Portrait-2'
            WHEN 3 THEN '3-StillTesting'
            WHEN 4 THEN '4-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTRENDERTYPES || ''
        END AS 'zUnmAdj-Adjustment Render Types',
        CASE zUnmAdj.ZADJUSTMENTFORMATVERSION
            WHEN 1.0 THEN '1.0-Markup-1.0'
            WHEN 1.1 THEN '1.1-Slow-Mo-1.1'
            WHEN 1.2 THEN '1.2-StillTesting'
            WHEN 1.3 THEN '1.3-StillTesting'
            WHEN 1.4 THEN '1.4-Filter-1.4'
            WHEN 1.5 THEN '1.5-Adjust-1.5'
            WHEN 1.6 THEN '1.6-Video-Trim-1.6'
            WHEN 1.7 THEN '1.7-StillTesting'
            WHEN 1.8 THEN '1.8-StillTesting'
            WHEN 1.9 THEN '1.9-StillTesting'
            WHEN 2.0 THEN '2.0-ScreenshotServices-2.0'
            ELSE 'Unknown-New-Value!: ' || zUnmAdj.ZADJUSTMENTFORMATVERSION || ''
        END AS 'zUnmAdj-Adjustment Format Version',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
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
            LEFT JOIN ZUNMANAGEDADJUSTMENT zUnmAdj ON zAddAssetAttr.ZUNMANAGEDADJUSTMENT = zUnmAdj.Z_PK
        WHERE zAsset.ZHASADJUSTMENTS = 1
        ORDER BY zUnmAdj.ZADJUSTMENTTIMESTAMP
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for adjusted assets' \
                          ' and supports iOS 14-17. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph8-Has Adjustment-PhDaPsql', description)
            report.add_script()
            data_headers = ('zUnmAdj-Adjustment Timestamp',
                            'zAsset-Has Adjustments/Camera-Effects-Filters',
                            'zAddAssetAttr-Editor Bundle ID',
                            'zUnmAdj-Editor Localized Name',
                            'zUnmAdj-Adjustment Format ID',
                            'zUnmAdj-Adjustment Render Types',
                            'zUnmAdj-Adjustment Format Version',
                            'zAsset-Directory/Path',
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

            tsvname = 'Ph8-Has Adjustment-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph8-Has Adjustment-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite Adjusted Assets')

        db.close()
        return


__artifacts_v2__ = {
    'Ph8-Has Adjustment-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 8 Adjusted Assets',
        'description': 'Parses basic asset record data from PhotoData/Photos.sqlite for adjusted assets'
                       ' and supports iOS 11-17. The results for this script will contain'
                       ' one record per ZASSET table Z_PK value.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.2',
        'date': '2024-04-07',
        'requirements': 'Acquisition that contains PhotoData/Photos.sqlite',
        'category': 'Photos.sqlite-Interaction_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Media/PhotoData/Photos.sqlite*'),
        'function': 'get_ph8hasadjustmentphdapsql'
    }
}