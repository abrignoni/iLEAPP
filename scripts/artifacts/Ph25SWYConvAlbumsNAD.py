# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.3
#
#   Description:
#   Parses Shared with You Conversation Album records found in the PhotoData/Photos.sqlite ZGENERICALBUM Table
#   and supports iOS 15-17. Parses Conversation Album records only no asset data being parsed.
#   This parser is based on research and SQLite Queries written by Scott Koenig
#   This is very large query and script, I recommend opening the TSV generated report with Zimmerman's Tools
#   https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search and filter the results.
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import glob
import os
import sys
import stat
import pathlib
import sqlite3
import nska_deserialize as nd
import scripts.artifacts.artGlobals
import shutil

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph25swyconvalbumnadphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) < version.parse("15"):
        logfunc("Unsupported version for PhotoData/Photos.sqlite Shared with You Conversation album records"
                " with no asset data from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First/CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_27ASSETS Albumsz27Assets ON Albumsz27Assets.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18]))

                counter += 1

            description = 'Parses Shared with You Conversation Album records found in the PhotoData/Photos.sqlite' \
                          ' ZGENERICALBUM Table and supports iOS 15. Parses Share with You Conversation Album' \
                          ' records only, no asset data being parsed.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph25.1-SWY Conversation Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('SWYConverszGenAlbum-Creation Date',
                            'SWYConverszGenAlbum-Start Date',
                            'SWYConverszGenAlbum-End Date',
                            'zAsset- Conversation= zGenAlbum_zPK',
                            'SWYConverszGenAlbum- Import Session ID-SWY',
                            'SWYzGenAlbum-Imported by Bundle Identifier',
                            'SWYConverszGenAlbum-Album Kind',
                            'SWYConverszGenAlbum-Cloud_Local_State',
                            'SWYConverszGenAlbum- Syndicate',
                            'SWYConverszGenAlbum-Sync Event Order Key',
                            'SWYConverszGenAlbum-Pinned',
                            'SWYConverszGenAlbum-Custom Sort Key',
                            'SWYConverszGenAlbum-Custom Sort Ascending',
                            'SWYConverszGenAlbum-Is Prototype',
                            'SWYConverszGenAlbum-Project Document Type',
                            'SWYConverszGenAlbum-Custom Query Type',
                            'SWYConverszGenAlbum-Trashed State',
                            'SWYConverszGenAlbum-Trash Date',
                            'SWYConverszGenAlbum-Cloud Delete State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph25.1-SWY Conversation Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph25.1-SWY Conversation Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite Shared with You Conversation Album Records'
                    ' with No Asset Data')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("16"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First/CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_28ASSETS Albumsz28Assets ON Albumsz28Assets.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19]))

                counter += 1

            description = 'Parses Shared with You Conversation Album records found in the PhotoData/Photos.sqlite' \
                          ' ZGENERICALBUM Table and supports iOS 16-17. Parses Share with You Conversation Album' \
                          ' records only, no asset data being parsed.'
            report = ArtifactHtmlReport('Photos.sqlite-GenAlbum_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph25.1-SWY Conversation Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('SWYConverszGenAlbum-Creation Date',
                            'SWYConverszGenAlbum-Start Date',
                            'SWYConverszGenAlbum-End Date',
                            'zAsset- Conversation= zGenAlbum_zPK',
                            'SWYConverszGenAlbum- Import Session ID-SWY',
                            'SWYzGenAlbum-Imported by Bundle Identifier',
                            'SWYConverszGenAlbum-Album Kind',
                            'SWYConverszGenAlbum-Cloud_Local_State',
                            'SWYConverszGenAlbum- Syndicate',
                            'SWYConverszGenAlbum-Sync Event Order Key',
                            'SWYConverszGenAlbum-Pinned',
                            'SWYConverszGenAlbum-Custom Sort Key',
                            'SWYConverszGenAlbum-Custom Sort Ascending',
                            'SWYConverszGenAlbum-Is Prototype',
                            'SWYConverszGenAlbum-Project Document Type',
                            'SWYConverszGenAlbum-Custom Query Type',
                            'SWYConverszGenAlbum-Trashed State',
                            'SWYConverszGenAlbum-Trash Date',
                            'SWYConverszGenAlbum-Cloud Delete State',
                            'SWYConverszGenAlbum-Privacy State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph25.1-SWY Conversation Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph25.1-SWY Conversation Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite Shared with You Conversation Album Records'
                    ' with No Asset Data')

        db.close()
        return


def get_ph25swyconvalbumnadsyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) < version.parse("15"):
        logfunc("Unsupported version for Syndication.photoslibrary/database/Photos.sqlite Shared with You Conversation"
                " album records with no asset data on iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First/CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_27ASSETS Albumsz27Assets ON Albumsz27Assets.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18]))

                counter += 1

            description = 'Parses Shared with You Conversation Album records found in the' \
                          ' Syndication.photoslibrary/database/Photos.sqlite ZGENERICALBUM Table and' \
                          ' supports iOS 15. Parses Share with You Conversation Album' \
                          ' records only, no asset data being parsed.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph25.2-SWY Conversation Records NAD-SyndPL', description)
            report.add_script()
            data_headers = ('SWYConverszGenAlbum-Creation Date',
                            'SWYConverszGenAlbum-Start Date',
                            'SWYConverszGenAlbum-End Date',
                            'zAsset- Conversation= zGenAlbum_zPK',
                            'SWYConverszGenAlbum- Import Session ID-SWY',
                            'SWYzGenAlbum-Imported by Bundle Identifier',
                            'SWYConverszGenAlbum-Album Kind',
                            'SWYConverszGenAlbum-Cloud_Local_State',
                            'SWYConverszGenAlbum- Syndicate',
                            'SWYConverszGenAlbum-Sync Event Order Key',
                            'SWYConverszGenAlbum-Pinned',
                            'SWYConverszGenAlbum-Custom Sort Key',
                            'SWYConverszGenAlbum-Custom Sort Ascending',
                            'SWYConverszGenAlbum-Is Prototype',
                            'SWYConverszGenAlbum-Project Document Type',
                            'SWYConverszGenAlbum-Custom Query Type',
                            'SWYConverszGenAlbum-Trashed State',
                            'SWYConverszGenAlbum-Trash Date',
                            'SWYConverszGenAlbum-Cloud Delete State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph25.2-SWY Conversation Records NAD-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph25.2-SWY Conversation Records NAD-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                    ' Shared with You Conversation Album Records with No Asset Data')

        db.close()
        return

    if version.parse(iosversion) >= version.parse("16"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(SWYConverszGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Creation Date',
        DateTime(SWYConverszGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Start Date',
        DateTime(SWYConverszGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-End Date',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID-SWY',
        SWYConverszGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'SWYzGenAlbum-Imported by Bundle Identifier',
        CASE SWYConverszGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZKIND || ''
        END AS 'SWYConverszGenAlbum-Album Kind',
        CASE SWYConverszGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud_Local_State',
        CASE SWYConverszGenAlbum.ZSYNDICATE
            WHEN 1 THEN '1-SWYConverszGenAlbum-Syndicate - SWY-SyncedFile-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZSYNDICATE || ''
        END AS 'SWYConverszGenAlbum- Syndicate',
        SWYConverszGenAlbum.ZSYNCEVENTORDERKEY AS 'SWYConverszGenAlbum-Sync Event Order Key',
        CASE SWYConverszGenAlbum.ZISPINNED
            WHEN 0 THEN 'SWYConverszGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPINNED || ''
        END AS 'SWYConverszGenAlbum-Pinned',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-SWYConverszGenAlbum-CusSrtAsc0=Sorted_Newest_First/CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-SWYConverszGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Key',
        CASE SWYConverszGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-SWYConverszGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-SWYConverszGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'SWYConverszGenAlbum-Custom Sort Ascending',
        CASE SWYConverszGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'SWYConverszGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'SWYConverszGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZISPROTOTYPE || ''
        END AS 'SWYConverszGenAlbum-Is Prototype',
        CASE SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'SWYConverszGenAlbum-Project Document Type',
        CASE SWYConverszGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'SWYConverszGenAlbum-Custom Query Type',
        CASE SWYConverszGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Not In Trash-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZTRASHEDSTATE || ''
        END AS 'SWYConverszGenAlbum-Trashed State',
        DateTime(SWYConverszGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'SWYConverszGenAlbum-Trash Date',
        CASE SWYConverszGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'SWYConverszGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'SWYConverszGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'SWYConverszGenAlbum-Cloud Delete State',
        CASE SWYConverszGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || SWYConverszGenAlbum.ZPRIVACYSTATE || ''
        END AS 'SWYConverszGenAlbum-Privacy State'
        FROM ZGENERICALBUM SWYConverszGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = SWYConverszGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZASSET zAsset ON zAsset.ZCONVERSATION = SWYConverszGenAlbum.Z_PK			
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN Z_28ASSETS Albumsz28Assets ON Albumsz28Assets.Z_28ALBUMS = SWYConverszGenAlbum.Z_PK	
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = SWYConverszGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON SWYConverszGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE SWYConverszGenAlbum.ZKIND = 1509
        ORDER BY SWYConverszGenAlbum.ZCREATIONDATE        
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19]))

                counter += 1

            description = 'Parses Shared with You Conversation Album records found in the' \
                          ' Syndication.photoslibrary/database/Photos.sqlite ZGENERICALBUM Table and' \
                          ' supports iOS 16-17. Parses Share with You Conversation Album' \
                          ' records only, no asset data being parsed.'
            report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
            report.start_artifact_report(report_folder, 'Ph25.2-SWY Conversation Records NAD-SyndPL', description)
            report.add_script()
            data_headers = ('SWYConverszGenAlbum-Creation Date',
                            'SWYConverszGenAlbum-Start Date',
                            'SWYConverszGenAlbum-End Date',
                            'zAsset- Conversation= zGenAlbum_zPK',
                            'SWYConverszGenAlbum- Import Session ID-SWY',
                            'SWYzGenAlbum-Imported by Bundle Identifier',
                            'SWYConverszGenAlbum-Album Kind',
                            'SWYConverszGenAlbum-Cloud_Local_State',
                            'SWYConverszGenAlbum- Syndicate',
                            'SWYConverszGenAlbum-Sync Event Order Key',
                            'SWYConverszGenAlbum-Pinned',
                            'SWYConverszGenAlbum-Custom Sort Key',
                            'SWYConverszGenAlbum-Custom Sort Ascending',
                            'SWYConverszGenAlbum-Is Prototype',
                            'SWYConverszGenAlbum-Project Document Type',
                            'SWYConverszGenAlbum-Custom Query Type',
                            'SWYConverszGenAlbum-Trashed State',
                            'SWYConverszGenAlbum-Trash Date',
                            'SWYConverszGenAlbum-Cloud Delete State',
                            'SWYConverszGenAlbum-Privacy State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph25.2-SWY Conversation Records NAD-SyndPL'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph25.2-SWY Conversation Records NAD-SyndPL'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                    ' Shared with You Conversation Album Records with No Asset Data')

        db.close()
        return


__artifacts_v2__ = {
    'Ph25-1-SWY Conversation Records with NAD-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 25.1 SWY Conversation Album Records with No Asset Data',
        'description': 'Parses Shared with You Conversation Album records found in the PhotoData/Photos.sqlite'
                       ' ZGENERICALBUM Table and supports iOS 15-17. Parses Share with You Conversation Album'
                       ' records only, no asset data being parsed.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.3',
        'date': '2024-04-13',
        'requirements': 'Acquisition that contains PhotoData/Photos.sqlite',
        'category': 'Photos.sqlite-GenAlbum_Records-NAD',
        'notes': '',
        'paths': ('*/mobile/Media/PhotoData/Photos.sqlite*'),
        'function': 'get_ph25swyconvalbumnadphdapsql'
    },
    'Ph25-2-SWY Conversation Records with NAD-SyndPL': {
        'name': 'SyndPL Photos.sqlite 25.2 SWY Conversation Records with No Asset Data',
        'description': 'Parses SWY Conversation Album Records found in the'
                       ' Syndication.photoslibrary/database/Photos.sqlite ZGENERICALBUM Table and supports iOS 15-17.'
                       ' Parses Share with You Conversation Album records only, no asset data being parsed.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.3',
        'date': '2024-04-13',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-Syndication_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*'),
        'function': 'get_ph25swyconvalbumnadsyndpl'
    }
}