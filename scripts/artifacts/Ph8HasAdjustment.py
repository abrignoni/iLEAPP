# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 2.0
#
#   Description:
#   Parses basic asset record data from Photos.sqlite for adjusted assets and supports iOS 11-18.
#   The results for this script will contain one record per ZASSET table Z_PK value.
#   This parser is based on research and SQLite queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
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
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite adjusted assets from iOS " + iosversion)
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
        END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',       
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

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for adjusted assets' \
                          ' and supports iOS 11-13. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Ph8-Has Adjustment-PhDaPsq')
            report.start_artifact_report(report_folder, 'Ph8-Has Adjustment-PhDaPsql', description)
            report.add_script()
            data_headers = ('zUnmAdj-Adjustment Timestamp',
                            'zAsset-Has Adjustments-Camera-Effects-Filters',
                            'zAddAssetAttr-Editor Bundle ID',
                            'zUnmAdj-Editor Localized Name',
                            'zUnmAdj-Adjustment Format ID',
                            'zUnmAdj-Adjustment Render Types',
                            'zUnmAdj-Adjustment Format Version',
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

            tsvname = 'Ph8-Has Adjustment-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph8-Has Adjustment-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Adjusted Assets')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("18")):
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
        END AS 'zAsset-Has Adjustments-Camera-Effects-Filters',       
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
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',        
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint'        
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
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for adjusted assets' \
                          ' and supports iOS 14-17. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Ph8-Has Adjustment-PhDaPsq')
            report.start_artifact_report(report_folder, 'Ph8-Has Adjustment-PhDaPsql', description)
            report.add_script()
            data_headers = ('zUnmAdj-Adjustment Timestamp-0',
                            'zAsset-Has Adjustments-Camera-Effects-Filters-1',
                            'zAddAssetAttr-Editor Bundle ID-2',
                            'zUnmAdj-Editor Localized Name-3',
                            'zUnmAdj-Adjustment Format ID-4',
                            'zUnmAdj-Adjustment Render Types-5',
                            'zUnmAdj-Adjustment Format Version-6',
                            'zAsset-Directory-Path-7',
                            'zAsset-Filename-8',
                            'zAddAssetAttr- Original Filename-9',
                            'zCldMast- Original Filename-10',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-11',
                            'zAsset-zPK-12',
                            'zAddAssetAttr-zPK-13',
                            'zAsset-UUID = store.cloudphotodb-14',
                            'zAddAssetAttr-Master Fingerprint-15',
                            'zAddAssetAttr.Adjusted Fingerprint-16')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph8-Has Adjustment-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph8-Has Adjustment-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Adjusted Assets')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("18"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zUnmAdj.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zUnmAdj-Adjustment Timestamp',
        CASE zAsset.ZADJUSTMENTSSTATE
            WHEN 0 THEN '0-No-Adjustments-0'
            WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
            WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
        END AS 'zAsset-Adjustments_State/Camera-Effects-Filters-iOS18',
        DateTime(zCompSyncAttr.ZCLOUDCOMPUTESTATELASTUPDATEDDATE + 978307200, 'UNIXEPOCH') AS 'zCompSyncAttr-Cloud_Compute_State_Last_Updated_Date-iOS18',
        CASE zCompSyncAttr.ZLOCALANALYSISMAJORVERSION
            WHEN 1 THEN '1-Is_Local_Analysis_Major_Version-1'
            ELSE 'Unknown-New-Value!: ' || zCompSyncAttr.ZLOCALANALYSISMAJORVERSION || ''
        END AS 'zCompSyncAttr-Local_Analysis_Major_Version-iOS18',
        zAddAssetAttr.ZEDITORBUNDLEID AS 'zAddAssetAttr-Editor Bundle ID',
        zUnmAdj.ZEDITORLOCALIZEDNAME AS 'zUnmAdj-Editor Localized Name',
        zUnmAdj.ZADJUSTMENTFORMATIDENTIFIER AS 'zUnmAdj-Adjustment Format ID',
        CASE zUnmAdj.ZADJUSTMENTRENDERTYPES
            WHEN 0 THEN '0-Standard or Portrait with errors-0'
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
        CASE zAsset.ZISDETECTEDSCREENSHOT
            WHEN 0 THEN '0-Not_Detected_Screenshot iOS18_Still_Testing-0'
            WHEN 1 THEN '1-Detected_Screenshot iOS18_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZISDETECTEDSCREENSHOT || ''
        END AS 'zAsset-Is_Detected_Screenshot-iOS18',
        CASE zAsset.ZISRECENTLYSAVED
            WHEN 0 THEN '0-Not_Recently_Saved iOS18_Still_Testing-0'
            WHEN 1 THEN '1-Recently_Saved iOS18_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZISRECENTLYSAVED || ''
        END AS 'zAsset-Is_Recently_Saved-iOS18',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zCompSyncAttr.ZLOCALANALYSISSTAGE AS 'zCompSyncAttr-Local_Analysis_Stage-iOS18',
        zCompSyncAttr.ZCLOUDCOMPUTESTATEVERSION AS 'zCompSyncAttr-Cloud_Compute_State_Version-iOS18',     
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZCOMPUTESYNCATTRIBUTES AS 'zAsset-Compute_Sync_Attributes= zCompSyncAttr-zPK-iOS18',
        zCompSyncAttr.Z_PK AS 'zCompSyncAttr-zPK= zAsset-zCompSyncAttr-iOS18',
        zCompSyncAttr.ZASSET AS 'zCompSyncAttr-zAsset= zAsset-zPK-iOS18',
        zCompSyncAttr.Z_ENT AS 'zCompSyncAttr-zENT-iOS18',
        zCompSyncAttr.Z_OPT AS 'zCompSyncAttr-zOPT-iOS18',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash-iOS18',
        zUnmAdj.ZOTHERADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Other Adjustments Fingerprint',
        zUnmAdj.ZSIMILARTOORIGINALADJUSTMENTSFINGERPRINT AS 'zUnmAdj-Similar to Orig Adjustments Fingerprint',
        zCompSyncAttr.ZCLOUDCOMPUTESTATEADJUSTMENTFINGERPRINT AS 'zCompSyncAttr-Cloud_Compute_State_Adjustment_Fingerprint-iOS18',
        CASE zExtAttr.ZGENERATIVEAITYPE 
            WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
            ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
        END AS 'zExtAttr-Generative_AI_Type-iOS18'  
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZUNMANAGEDADJUSTMENT zUnmAdj ON zAddAssetAttr.ZUNMANAGEDADJUSTMENT = zUnmAdj.Z_PK
            LEFT JOIN ZCOMPUTESYNCATTRIBUTES zCompSyncAttr ON zCompSyncAttr.Z_PK = zAsset.ZCOMPUTESYNCATTRIBUTES
        WHERE zAsset.ZADJUSTMENTSSTATE > 0
        ORDER BY zUnmAdj.ZADJUSTMENTTIMESTAMP
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for adjusted assets' \
                          ' and supports iOS 18. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Ph8-Has Adjustment-PhDaPsq')
            report.start_artifact_report(report_folder, 'Ph8-Has Adjustment-PhDaPsql', description)
            report.add_script()
            data_headers = ('zUnmAdj-Adjustment Timestamp-0',
                            'zAsset-Adjustments_State/Camera-Effects-Filters-iOS18-1',
                            'zCompSyncAttr-Cloud_Compute_State_Last_Updated_Date-iOS18-2',
                            'zCompSyncAttr-Local_Analysis_Major_Version-iOS18-3',
                            'zAddAssetAttr-Editor Bundle ID-4',
                            'zUnmAdj-Editor Localized Name-5',
                            'zUnmAdj-Adjustment Format ID-6',
                            'zUnmAdj-Adjustment Render Types-7',
                            'zUnmAdj-Adjustment Format Version-8',
                            'zAsset-Is_Detected_Screenshot-iOS18-9',
                            'zAsset-Is_Recently_Saved-iOS18-10',
                            'zAsset-Directory-Path-11',
                            'zAsset-Filename-12',
                            'zAddAssetAttr- Original Filename-13',
                            'zCldMast- Original Filename-14',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-15',
                            'zCompSyncAttr-Local_Analysis_Stage-iOS18-16',
                            'zCompSyncAttr-Cloud_Compute_State_Version-iOS18-17',
                            'zAsset-zPK-18',
                            'zAddAssetAttr-zPK-19',
                            'zAsset-Compute_Sync_Attributes= zCompSyncAttr-zPK-iOS18-20',
                            'zCompSyncAttr-zPK= zAsset-zCompSyncAttr-iOS18-21',
                            'zCompSyncAttr-zAsset= zAsset-zPK-iOS18-22',
                            'zCompSyncAttr-zENT-iOS18-23',
                            'zCompSyncAttr-zOPT-iOS18-24',
                            'zAsset-UUID = store.cloudphotodb-25',
                            'zAddAssetAttr-Original Stable Hash-iOS18-26',
                            'zAddAssetAttr.Adjusted Stable Hash-iOS18-27',
                            'zUnmAdj-Other Adjustments Fingerprint-28',
                            'zUnmAdj-Similar to Orig Adjustments Fingerprint-29',
                            'zCompSyncAttr-Cloud_Compute_State_Adjustment_Fingerprint-iOS18-30',
                            'zExtAttr-Generative_AI_Type-iOS18-31')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph8-Has Adjustment-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph8-Has Adjustment-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Adjusted Assets')

        db.close()
        return


__artifacts_v2__ = {
    'Ph8-Has Adjustment-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite Ph8 Adjusted Assets',
        'description': 'Parses basic asset record data from PhotoData-Photos.sqlite for adjusted assets'
                       ' and supports iOS 11-18. The results for this script will contain'
                       ' one record per ZASSET table Z_PK value.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '2.0',
        'date': '2024-06-14',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': '*/PhotoData/Photos.sqlite*',
        'function': 'get_ph8hasadjustmentphdapsql'
    }
}
