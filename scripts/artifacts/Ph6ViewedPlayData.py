#   Photos.sqlite
#   Author:  Scott Koenig, assisted by past contributors
#   Version: 1.2
#
#   Description:
#   Parses basic asset record data from Photos.sqlite for assets with last viewed timestamp and other view and play data
#   from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE and ZPLAYCOUNT fields and iOS version support varies
#   but last viewed date is supported in iOS 16-17.
#   The results for this script will contain one record per ZASSET table Z_PK value.
#   This parser is based on research and SQLite queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph6viewplaydataphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotosData-Photos.sqlite assets with view and"
                " play data from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("13")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for assets with' \
                          ' view and played data in versions 11-12. If the iOS version is greater than iOS 16' \
                          ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field' \
                          ' will be included. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph6-Viewed and Played Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Modification Date',
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
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph6-Viewed and Played Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph6-Viewed and Played Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite asset viewed and played data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for assets with' \
                          ' view and played data in versions 13. If the iOS version is greater than iOS 16' \
                          ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field' \
                          ' will be included. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph6-Viewed and Played Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Modification Date',
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
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph6-Viewed and Played Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph6-Viewed and Played Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite asset viewed and played data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for assets with' \
                          ' view and played data in versions 14. If the iOS version is greater than iOS 16' \
                          ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field' \
                          ' will be included. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph6-Viewed and Played Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Modification Date',
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
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph6-Viewed and Played Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph6-Viewed and Played Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite asset viewed and played data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for assets with' \
                          ' view and played data in versions 15. If the iOS version is greater than iOS 16' \
                          ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field' \
                          ' will be included. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph6-Viewed and Played Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Modification Date',
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
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph6-Viewed and Played Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph6-Viewed and Played Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite asset viewed and played data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) <= version.parse("16.5.1")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for assets with' \
                          ' view and played data in versions 16-17. If the iOS version is greater than iOS 16' \
                          ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field' \
                          ' will be included. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph6-Viewed and Played Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Modification Date',
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
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph6-Viewed and Played Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph6-Viewed and Played Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite asset viewed and played data')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("16.6"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for assets with' \
                          ' view and played data in versions 16-17. If the iOS version is greater than iOS 16' \
                          ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field' \
                          ' will be included. The results for this script will contain' \
                          ' one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph6-Viewed and Played Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAddAssetAttr-Last Viewed Date',
                            'zAsset-Modification Date',
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
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph6-Viewed and Played Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph6-Viewed and Played Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite asset viewed and played data')

        db.close()
        return


__artifacts_v2__ = {
    'Ph6-View and Play Data-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 6 assets with viewed and played data',
        'description': 'Parses basic asset record data from PhotoData-Photos.sqlite for assets with'
                       ' view and played data in versions 11-17. If the iOS version is greater than iOS 16'
                       ' last viewed date from ZADDITTIONALASSETATTRIBUTES table ZLASTVIEWEDDATE field'
                       ' will be included. The results for this script will contain'
                       ' one record per ZASSET table Z_PK value.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.2',
        'date': '2024-04-06',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
        'function': 'get_ph6viewplaydataphdapsql'
    }
}
