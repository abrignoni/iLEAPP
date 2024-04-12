# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.2
#
#   Description:
#   Parses Basic Album records found in the PhotoData/Photos.sqlite ZGENERICALBUM Table and supports iOS 11-17.
#   Parses Album records only no asset data being parsed.
#   Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.
#   Use 1505-Shared-Album-1505 in the search to view Shared Albums.
#   Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You Conversation Identifiers.
#   Please see the album type specific scripts to view more data for each album type.
#   This parser is based on research and SQLite Queries written by Scott Koenig
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


def get_ph20albumrecordsnadphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('Photos.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) < version.parse("11"):
        logfunc("Unsupported version for PhotoData/Photos.sqlite album records with no asset data on iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT 
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title/User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZSTARTDATE
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11]))

                counter += 1

            description = 'Parses Basic Album records found in the PhotoData/Photos.sqlite ZGENERICALBUM Table' \
                          ' and supports iOS 11-17. Parses Album records only no asset data being parsed.' \
                          ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.' \
                          ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.' \
                          ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You' \
                          ' Conversation Identifiers. Please see the album type specific scripts to view more data' \
                          ' for each album type.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph20-Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Title',
                            'zGenAlbum-Import Session ID',
                            'zGenAlbum-Cached Photos Count',
                            'zGenAlbum-Cached Videos Count',
                            'zGenAlbum-Cached Count',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph20-Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph20-Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite Album Records with No Asset Data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title/User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle Identifier',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11], row[12], row[13]))

                counter += 1

            description = 'Parses Basic Album records found in the PhotoData/Photos.sqlite ZGENERICALBUM Table' \
                          ' and supports iOS 11-17. Parses Album records only no asset data being parsed.' \
                          ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.' \
                          ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.' \
                          ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You' \
                          ' Conversation Identifiers. Please see the album type specific scripts to view more data' \
                          ' for each album type.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph20-Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Title',
                            'zGenAlbum-Import Session ID',
                            'zGenAlbum-Creator Bundle Identifier',
                            'zGenAlbum-Cached Photos Count',
                            'zGenAlbum-Cached Videos Count',
                            'zGenAlbum-Cached Count',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph20-Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph20-Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite Album Records No Asset Data')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("15"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title/User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        """)
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11], row[12], row[13]))

                counter += 1

            description = 'Parses Basic Album records found in the PhotoData/Photos.sqlite ZGENERICALBUM Table' \
                          ' and supports iOS 11-17. Parses Album records only no asset data being parsed.' \
                          ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.' \
                          ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.' \
                          ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You' \
                          ' Conversation Identifiers. Please see the album type specific scripts to view more data' \
                          ' for each album type.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph20-Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Title',
                            'zGenAlbum-Import Session ID',
                            'zGenAlbum-Imported by Bundle Identifier',
                            'zGenAlbum-Cached Photos Count',
                            'zGenAlbum-Cached Videos Count',
                            'zGenAlbum-Cached Count',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph20-Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph20-Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite Album Records with No Asset Data')

        db.close()
        return


def get_ph20albumrecrodsnadsyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) < version.parse("11"):
        logfunc("Unsupported version for Syndication.photoslibrary/database/Photos.sqlite"
                " album records with no asset data on iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT 
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title/User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZSTARTDATE
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11]))

                counter += 1

            description = 'Parses Basic Album records found in the Syndication.photoslibrary/database/Photos.sqlite' \
                          ' ZGENERICALBUM Table and supports iOS 11-17.' \
                          ' Parses Album records only no asset data being parsed.' \
                          ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.' \
                          ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.' \
                          ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You' \
                          ' Conversation Identifiers. Please see the album type specific scripts to view more data' \
                          ' for each album type.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph20-Album Records NAD-SyndPL', description)
            report.add_script()
            data_headers = ('zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Title',
                            'zGenAlbum-Import Session ID',
                            'zGenAlbum-Cached Photos Count',
                            'zGenAlbum-Cached Videos Count',
                            'zGenAlbum-Cached Count',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph20-Album Records NAD-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph20-Album Records NAD-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                    ' Album Records with No Asset Data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title/User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle Identifier',        
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11], row[12], row[13]))

                counter += 1

            description = 'Parses Basic Album records found in the Syndication.photoslibrary/database/Photos.sqlite' \
                          ' ZGENERICALBUM Table and supports iOS 11-17.' \
                          ' Parses Album records only no asset data being parsed.' \
                          ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.' \
                          ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.' \
                          ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You' \
                          ' Conversation Identifiers. Please see the album type specific scripts to view more data' \
                          ' for each album type.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph20-Album Records NAD-SyndPL', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Title',
                            'zGenAlbum-Import Session ID',
                            'zGenAlbum-Creator Bundle Identifier',
                            'zGenAlbum-Cached Photos Count',
                            'zGenAlbum-Cached Videos Count',
                            'zGenAlbum-Cached Count',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph20-Album Records NAD-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph20-Album Records NAD-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                    ' Album Records No Asset Data')

        db.close()
        return
    elif version.parse(iosversion) >= version.parse("15"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',
        zGenAlbum.ZTITLE AS 'zGenAlbum-Title/User&System Applied',
        zGenAlbum.ZIMPORTSESSIONID AS 'zGenAlbum- Import Session ID',
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum-Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum-Cached Videos Count',
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum-Cached Count',
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID-4TableStart',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID-4TableStart'
        FROM ZGENERICALBUM zGenAlbum
        ORDER BY zGenAlbum.ZCREATIONDATE
        """)
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11], row[12], row[13]))

                counter += 1

            description = 'Parses Basic Album records found in the Syndication.photoslibrary/database/Photos.sqlite' \
                          ' ZGENERICALBUM Table and supports iOS 11-17.' \
                          ' Parses Album records only no asset data being parsed.' \
                          ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.' \
                          ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.' \
                          ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You' \
                          ' Conversation Identifiers. Please see the album type specific scripts to view more data' \
                          ' for each album type.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph20-Album Records NAD-SyndPL', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Title',
                            'zGenAlbum-Import Session ID',
                            'zGenAlbum-Imported by Bundle Identifier',
                            'zGenAlbum-Cached Photos Count',
                            'zGenAlbum-Cached Videos Count',
                            'zGenAlbum-Cached Count',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph20-Album Records NAD-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph20-Album Records NAD-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                    ' Album Records with No Asset Data')

        db.close()
        return


__artifacts_v2__ = {
    'Album Records with No Asset Data-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 20 Album Records with No Asset Data',
        'description': 'Parses Basic Album records found in the PhotoData/Photos.sqlite ZGENERICALBUM Table'
                       ' and supports iOS 11-17. Parses Album records only no asset data being parsed.'
                       ' Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.'
                       ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You Conversation Identifiers.'
                       ' Please see the album type specific scripts to view more data for each album type.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.2',
        'date': '2024-04-07',
        'requirements': 'Acquisition that contains PhotoData/Photos.sqlite',
        'category': 'Photos.sqlite-GenAlbum_Records-NAD',
        'notes': '',
        'paths': ('*/mobile/Media/PhotoData/Photos.sqlite'),
        'function': 'get_ph20albumrecordsnadphdapsql'
    },
    'Album Records with No Asset Data-SyndPL': {
        'name': 'SyndPL Photos.sqlite 20 Album Records with No Asset Data',
        'description': 'Parses Basic Album records found in the Syndication.photoslibrary/database/Photos.sqlite'
                       ' ZGENERICALBUM Table and supports iOS 11-17. Parses Album records only no asset data'
                       ' being parsed. Use 2-Non-Shared-Album-2 in the search to view Non-Shared Albums.'
                       ' Use 1505-Shared-Album-1505 in the search to view Shared Albums.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 to view Shared with You Conversation Identifiers.'
                       ' Please see the album type specific scripts to view more data for each album type.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.2',
        'date': '2024-04-07',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-GenAlbum_Records-NAD',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite'),
        'function': 'get_ph20albumrecrodsnadsyndpl'
    }
}