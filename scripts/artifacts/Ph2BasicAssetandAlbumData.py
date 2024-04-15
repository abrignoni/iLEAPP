# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.3
#
#   Description:
#   Parses basic asset record data from Photos.sqlite to include associated album data and supports iOS 11-17.
#   The results could produce multiple records for a single asset.
#   Use '2-Non-Shared-Album-2' in the search box to view Assets in Non-Shared Albums.
#   Use '1505-Shared-Album-1505' in the search box to view Assets in Shared Albums.
#   Use '1509-SWY_Synced_Conversation_Media-1509' in the search box to view Shared with You Conversation Assets.
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


def get_ph2assetbasicandalbumdataphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('Photos.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) < version.parse("11"):
        logfunc("Unsupported version for PhotoData/Photos.sqlite basic asset and album data from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("12")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
         CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_20ASSETS z20Assets ON z20Assets.Z_27ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z20Assets.Z_20ALBUMS
        ORDER BY zAsset.ZDATECREATED        
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
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for' \
                          ' basic asset and album data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 11.' \
                          ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                          ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                          ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                          ' Shared with You Conversation Identifiers Assets.'
            report = ArtifactHtmlReport('Photos.sqlite-Asset_Basic_Data')
            report.start_artifact_report(report_folder, 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-zPK',
                            'zAsset-Directory/Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAddAssetAttr-Creator Bundle ID',
                            'zAsset-Visibility State',
                            'zAsset-Saved Asset Type',
                            'zAddAssetAttr-Imported by',
                            'zAsset- SortToken -CameraRoll',
                            'zAsset-Added Date',
                            'zCldMast-Creation Date',
                            'zAddAssetAttr-Time Zone Name',
                            'zAsset-Modification Date',
                            'zAsset-Last Shared Date',
                            'zCldMast-Import Date',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                            'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                            'zAsset-Trashed Date',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint',
                            'zGenAlbum-Start Date',
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

            tsvname = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite basic asset and album data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("12")) & (version.parse(iosversion) < version.parse("13")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT 
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',        
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_23ASSETS z23Assets ON z23Assets.Z_30ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z23Assets.Z_23ALBUMS
        ORDER BY zAsset.ZDATECREATED
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
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for' \
                          ' basic asset and album data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 12.' \
                          ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                          ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                          ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                          ' Shared with You Conversation Identifiers Assets.'
            report = ArtifactHtmlReport('Photos.sqlite-Asset_Basic_Data')
            report.start_artifact_report(report_folder, 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-zPK',
                            'zAsset-Directory/Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAddAssetAttr-Creator Bundle ID',
                            'zAsset-Visibility State',
                            'zAsset-Saved Asset Type',
                            'zAddAssetAttr-Imported by',
                            'zAddAssetAttr-Share Type',
                            'zAsset- SortToken -CameraRoll',
                            'zAsset-Added Date',
                            'zCldMast-Creation Date',
                            'zAddAssetAttr-Time Zone Name',
                            'zAsset-Modification Date',
                            'zAsset-Last Shared Date',
                            'zCldMast-Import Date',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                            'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                            'zAsset-Trashed Date',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint',
                            'zGenAlbum-Start Date',
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

            tsvname = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite basic asset and album data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'       
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_34ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
        ORDER BY zAsset.ZDATECREATED
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
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for' \
                          ' basic asset and album data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 13.' \
                          ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                          ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                          ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                          ' Shared with You Conversation Identifiers Assets.'
            report = ArtifactHtmlReport('Photos.sqlite-Asset_Basic_Data')
            report.start_artifact_report(report_folder, 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-zPK',
                            'zAsset-Directory/Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zExtAttr-Camera Make',
                            'zExtAttr-Camera Model',
                            'zAddAssetAttr-Creator Bundle ID',
                            'zAsset-Visibility State',
                            'zAsset-Saved Asset Type',
                            'zAddAssetAttr-Imported by',
                            'zAddAssetAttr-Share Type',
                            'zAsset- SortToken -CameraRoll',
                            'zAsset-Added Date',
                            'zCldMast-Creation Date',
                            'zAddAssetAttr-Time Zone Name',
                            'zAsset-Modification Date',
                            'zAsset-Last Shared Date',
                            'zCldMast-Import Date',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                            'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                            'zAsset-Trashed Date',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint',
                            'zGenAlbum-Start Date',
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

            tsvname = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite basic asset and album data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
        ORDER BY zAsset.ZDATECREATED
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
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for' \
                          ' basic asset and album data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 14.' \
                          ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                          ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                          ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                          ' Shared with You Conversation Identifiers Assets.'
            report = ArtifactHtmlReport('Photos.sqlite-Asset_Basic_Data')
            report.start_artifact_report(report_folder, 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-zPK',
                            'zAsset-Directory/Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zExtAttr-Camera Make',
                            'zExtAttr-Camera Model',
                            'zAddAssetAttr-Creator Bundle ID',
                            'zAddAssetAttr-Imported By Display Name',
                            'zAsset-Visibility State',
                            'zAsset-Saved Asset Type',
                            'zAddAssetAttr-Imported by',
                            'zAddAssetAttr-Share Type',
                            'zAsset- SortToken -CameraRoll',
                            'zAsset-Added Date',
                            'zCldMast-Creation Date',
                            'zAddAssetAttr-Time Zone Name',
                            'zAsset-Modification Date',
                            'zAsset-Last Shared Date',
                            'zCldMast-Import Date',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                            'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                            'zAsset-Trashed Date',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint',
                            'zGenAlbum-Creation Date',
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

            tsvname = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite basic asset and album data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',      
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z27Assets.Z_27ALBUMS
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
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
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for' \
                          ' basic asset and album data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 15.' \
                          ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                          ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                          ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                          ' Shared with You Conversation Identifiers Assets.'
            report = ArtifactHtmlReport('Photos.sqlite-Asset_Basic_Data')
            report.start_artifact_report(report_folder, 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-zPK',
                            'zAsset-Directory/Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files',
                            'zAsset- Conversation= zGenAlbum_zPK ',
                            'SWYConverszGenAlbum- Import Session ID',
                            'zAsset-Syndication State',
                            'zExtAttr-Camera Make',
                            'zExtAttr-Camera Model',
                            'zAsset-Bundle Scope',
                            'zAddAssetAttr.Imported by Bundle Identifier',
                            'zAddAssetAttr-Imported By Display Name',
                            'zAsset-Visibility State',
                            'zAsset-Saved Asset Type',
                            'zAddAssetAttr-Imported by',
                            'zAddAssetAttr-Share Type',
                            'zAsset- SortToken -CameraRoll',
                            'zAsset-Added Date',
                            'zCldMast-Creation Date',
                            'zAddAssetAttr-Time Zone Name',
                            'zAsset-Modification Date',
                            'zAsset-Last Shared Date',
                            'zCldMast-Import Date',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                            'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                            'zAsset-Trashed Date',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint',
                            'zGenAlbum-Creation Date',
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

            tsvname = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite basic asset and album data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',      
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
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
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for' \
                          ' basic asset and album data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 16.' \
                          ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                          ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                          ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                          ' Shared with You Conversation Identifiers Assets.'
            report = ArtifactHtmlReport('Photos.sqlite-Asset_Basic_Data')
            report.start_artifact_report(report_folder, 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-zPK',
                            'zAsset-Directory/Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files',
                            'zAsset- Conversation= zGenAlbum_zPK ',
                            'SWYConverszGenAlbum- Import Session ID',
                            'zAsset-Syndication State',
                            'zExtAttr-Camera Make',
                            'zExtAttr-Camera Model',
                            'zAsset-Bundle Scope',
                            'zAddAssetAttr.Imported by Bundle Identifier',
                            'zAddAssetAttr-Imported By Display Name',
                            'zAsset-Visibility State',
                            'zAsset-Saved Asset Type',
                            'zAddAssetAttr-Imported by',
                            'zAddAssetAttr-Share Type',
                            'zAsset-Active Library Scope Participation State',
                            'zAsset- SortToken -CameraRoll',
                            'zAsset-Added Date',
                            'zCldMast-Creation Date',
                            'zAddAssetAttr-Time Zone Name',
                            'zAsset-Modification Date',
                            'zAsset-Last Shared Date',
                            'zCldMast-Import Date',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                            'zAddAssetAttr-Last Viewed Date',
                            'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                            'zAsset-Trashed Date',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint',
                            'zGenAlbum-Creation Date',
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

            tsvname = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite basic asset and album data')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("17"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
        SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',      
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
        DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
         'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
        DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
        ORDER BY zAsset.ZDATECREATED
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
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData/Photos.sqlite for' \
                          ' basic asset and album data. The results may contain multiple records' \
                          ' per ZASSET table Z_PK value and supports iOS 17.' \
                          ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                          ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                          ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                          ' Shared with You Conversation Identifiers Assets.'
            report = ArtifactHtmlReport('Photos.sqlite-Asset_Basic_Data')
            report.start_artifact_report(report_folder, 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created',
                            'zAsset-zPK',
                            'zAsset-Directory/Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files',
                            'zAsset- Conversation= zGenAlbum_zPK ',
                            'SWYConverszGenAlbum- Import Session ID',
                            'zAsset-Syndication State',
                            'zExtAttr-Camera Make',
                            'zExtAttr-Camera Model',
                            'zAsset-Bundle Scope',
                            'zAddAssetAttr.Imported by Bundle Identifier',
                            'zAddAssetAttr-Imported By Display Name',
                            'zAsset-Visibility State',
                            'zAsset-Saved Asset Type',
                            'zAddAssetAttr-Imported by',
                            'zAddAssetAttr-Share Type',
                            'zAsset-Active Library Scope Participation State',
                            'zAsset- SortToken -CameraRoll',
                            'zAsset-Added Date',
                            'zCldMast-Creation Date',
                            'zAddAssetAttr-Time Zone Name',
                            'zAsset-Modification Date',
                            'zAsset-Last Shared Date',
                            'zCldMast-Import Date',
                            'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                            'zAddAssetAttr-Last Viewed Date',
                            'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                            'zAsset-Trashed Date',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint',
                            'zGenAlbum-Creation Date',
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

            tsvname = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph2.1-Asset Basic Data & GenAlbum Data-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData/Photos.sqlite basic asset and album data')

        db.close()
        return


def get_ph2asserbasicandconversdatasyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):
        for file_found in files_found:
            file_found = str(file_found)

            if file_found.endswith('.sqlite'):
                break

        if report_folder.endswith('/') or report_folder.endswith('\\'):
            report_folder = report_folder[:-1]
        iosversion = scripts.artifacts.artGlobals.versionf
        if version.parse(iosversion) < version.parse("11"):
            logfunc("Unsupported version for Syndication.photoslibrary/database/Photos.sqlite"
                    " basic asset and album data iOS " + iosversion)
        if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("12")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
            zAsset.Z_PK AS 'zAsset-zPK',
            zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
            CASE zAsset.ZVISIBILITYSTATE
                WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
                WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
            END AS 'zAsset-Visibility State',
            CASE zAsset.ZSAVEDASSETTYPE
                WHEN 0 THEN '0-Saved-via-other-source-0'
                WHEN 1 THEN '1-StillTesting-1'
                WHEN 2 THEN '2-StillTesting-2'
                WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
                WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
                WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
                WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
                WHEN 7 THEN '7-StillTesting-7'
                WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
                WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
            END AS 'zAsset-Saved Asset Type',
            CASE zAddAssetAttr.ZIMPORTEDBY
                WHEN 0 THEN '0-Cloud-Other-0'
                WHEN 1 THEN '1-Native-Back-Camera-1'
                WHEN 2 THEN '2-Native-Front-Camera-2'
                WHEN 3 THEN '3-Third-Party-App-3'
                WHEN 4 THEN '4-StillTesting-4'
                WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
                WHEN 6 THEN '6-Third-Party-App-6'
                WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
                WHEN 8 THEN '8-System-Package-App-8'
                WHEN 9 THEN '9-Native-App-9'
                WHEN 10 THEN '10-StillTesting-10'
                WHEN 11 THEN '11-StillTesting-11'
                WHEN 12 THEN '12-SWY_Syndication_PL-12'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
            END AS 'zAddAssetAttr-Imported by',
            DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
            DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
            DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
            zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
            DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
            DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
            DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
             CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
            zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
            zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
            FROM ZGENERICASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN Z_20ASSETS z20Assets ON z20Assets.Z_27ASSETS = zAsset.Z_PK
                LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z20Assets.Z_20ALBUMS
            ORDER BY zAsset.ZDATECREATED        
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
                                      row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary/database/Photos.sqlite' \
                              ' for basic asset and album data. The results may contain multiple records' \
                              ' per ZASSET table Z_PK value and supports iOS 11.' \
                              ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                              ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                              ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                              ' Shared with You Conversation Identifiers Assets.'
                report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph2.2-Asset Basic Data & Convers Data-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Date Created',
                                'zAsset-zPK',
                                'zAsset-Directory/Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zAddAssetAttr-Creator Bundle ID',
                                'zAsset-Visibility State',
                                'zAsset-Saved Asset Type',
                                'zAddAssetAttr-Imported by',
                                'zAsset- SortToken -CameraRoll',
                                'zAsset-Added Date',
                                'zCldMast-Creation Date',
                                'zAddAssetAttr-Time Zone Name',
                                'zAsset-Modification Date',
                                'zAsset-Last Shared Date',
                                'zCldMast-Import Date',
                                'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                                'zAsset-Trashed Date',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint',
                                'zGenAlbum-Start Date',
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

                tsvname = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                        ' basic asset and album data')

            db.close()
            return

        elif (version.parse(iosversion) >= version.parse("12")) & (version.parse(iosversion) < version.parse("13")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT 
            DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
            zAsset.Z_PK AS 'zAsset-zPK',
            zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',        
            CASE zAsset.ZVISIBILITYSTATE
                WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
                WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
            END AS 'zAsset-Visibility State',
            CASE zAsset.ZSAVEDASSETTYPE
                WHEN 0 THEN '0-Saved-via-other-source-0'
                WHEN 1 THEN '1-StillTesting-1'
                WHEN 2 THEN '2-StillTesting-2'
                WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
                WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
                WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
                WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
                WHEN 7 THEN '7-StillTesting-7'
                WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
                WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
            END AS 'zAsset-Saved Asset Type',
            CASE zAddAssetAttr.ZIMPORTEDBY
                WHEN 0 THEN '0-Cloud-Other-0'
                WHEN 1 THEN '1-Native-Back-Camera-1'
                WHEN 2 THEN '2-Native-Front-Camera-2'
                WHEN 3 THEN '3-Third-Party-App-3'
                WHEN 4 THEN '4-StillTesting-4'
                WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
                WHEN 6 THEN '6-Third-Party-App-6'
                WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
                WHEN 8 THEN '8-System-Package-App-8'
                WHEN 9 THEN '9-Native-App-9'
                WHEN 10 THEN '10-StillTesting-10'
                WHEN 11 THEN '11-StillTesting-11'
                WHEN 12 THEN '12-SWY_Syndication_PL-12'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
            END AS 'zAddAssetAttr-Imported by',
            CASE zAddAssetAttr.ZSHARETYPE
                WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
                WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
            END AS 'zAddAssetAttr-Share Type',
            DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
            DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
            DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
            zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
            DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
            DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
            DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
            FROM ZGENERICASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN Z_23ASSETS z23Assets ON z23Assets.Z_30ASSETS = zAsset.Z_PK
                LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z23Assets.Z_23ALBUMS
            ORDER BY zAsset.ZDATECREATED
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
                                      row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary/database/Photos.sqlite' \
                              ' for basic asset and album data. The results may contain multiple records' \
                              ' per ZASSET table Z_PK value and supports iOS 12.' \
                              ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                              ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                              ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                              ' Shared with You Conversation Identifiers Assets.'
                report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph2.2-Asset Basic Data & Convers Data-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Date Created',
                                'zAsset-zPK',
                                'zAsset-Directory/Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zAddAssetAttr-Creator Bundle ID',
                                'zAsset-Visibility State',
                                'zAsset-Saved Asset Type',
                                'zAddAssetAttr-Imported by',
                                'zAddAssetAttr-Share Type',
                                'zAsset- SortToken -CameraRoll',
                                'zAsset-Added Date',
                                'zCldMast-Creation Date',
                                'zAddAssetAttr-Time Zone Name',
                                'zAsset-Modification Date',
                                'zAsset-Last Shared Date',
                                'zCldMast-Import Date',
                                'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                                'zAsset-Trashed Date',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint',
                                'zGenAlbum-Start Date',
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

                tsvname = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                        ' basic asset and album data')

            db.close()
            return

        elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
            zAsset.Z_PK AS 'zAsset-zPK',
            zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
            zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
            zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
            CASE zAsset.ZVISIBILITYSTATE
                WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
                WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
            END AS 'zAsset-Visibility State',
            CASE zAsset.ZSAVEDASSETTYPE
                WHEN 0 THEN '0-Saved-via-other-source-0'
                WHEN 1 THEN '1-StillTesting-1'
                WHEN 2 THEN '2-StillTesting-2'
                WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
                WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
                WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
                WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
                WHEN 7 THEN '7-StillTesting-7'
                WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
                WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
            END AS 'zAsset-Saved Asset Type',
            CASE zAddAssetAttr.ZIMPORTEDBY
                WHEN 0 THEN '0-Cloud-Other-0'
                WHEN 1 THEN '1-Native-Back-Camera-1'
                WHEN 2 THEN '2-Native-Front-Camera-2'
                WHEN 3 THEN '3-Third-Party-App-3'
                WHEN 4 THEN '4-StillTesting-4'
                WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
                WHEN 6 THEN '6-Third-Party-App-6'
                WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
                WHEN 8 THEN '8-System-Package-App-8'
                WHEN 9 THEN '9-Native-App-9'
                WHEN 10 THEN '10-StillTesting-10'
                WHEN 11 THEN '11-StillTesting-11'
                WHEN 12 THEN '12-SWY_Syndication_PL-12'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
            END AS 'zAddAssetAttr-Imported by',
            CASE zAddAssetAttr.ZSHARETYPE
                WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
                WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
            END AS 'zAddAssetAttr-Share Type',
            DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
            DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
            DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
            zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
            DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
            DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
            DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
            zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
            zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'       
            FROM ZGENERICASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_34ASSETS = zAsset.Z_PK
                LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
            ORDER BY zAsset.ZDATECREATED
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
                                      row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                      row[37], row[38]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary/database/Photos.sqlite' \
                              ' for basic asset and album data. The results may contain multiple records' \
                              ' per ZASSET table Z_PK value and supports iOS 13.' \
                              ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                              ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                              ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                              ' Shared with You Conversation Identifiers Assets.'
                report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph2.2-Asset Basic Data & Convers Data-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Date Created',
                                'zAsset-zPK',
                                'zAsset-Directory/Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zExtAttr-Camera Make',
                                'zExtAttr-Camera Model',
                                'zAddAssetAttr-Creator Bundle ID',
                                'zAsset-Visibility State',
                                'zAsset-Saved Asset Type',
                                'zAddAssetAttr-Imported by',
                                'zAddAssetAttr-Share Type',
                                'zAsset- SortToken -CameraRoll',
                                'zAsset-Added Date',
                                'zCldMast-Creation Date',
                                'zAddAssetAttr-Time Zone Name',
                                'zAsset-Modification Date',
                                'zAsset-Last Shared Date',
                                'zCldMast-Import Date',
                                'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                                'zAsset-Trashed Date',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint',
                                'zGenAlbum-Start Date',
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

                tsvname = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                        ' basic asset and album data')

            db.close()
            return

        elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
            zAsset.Z_PK AS 'zAsset-zPK',
            zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
            zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
            zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr-Creator Bundle ID',
            zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
            CASE zAsset.ZVISIBILITYSTATE
                WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
                WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
            END AS 'zAsset-Visibility State',
            CASE zAsset.ZSAVEDASSETTYPE
                WHEN 0 THEN '0-Saved-via-other-source-0'
                WHEN 1 THEN '1-StillTesting-1'
                WHEN 2 THEN '2-StillTesting-2'
                WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
                WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
                WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
                WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
                WHEN 7 THEN '7-StillTesting-7'
                WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
                WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
            END AS 'zAsset-Saved Asset Type',
            CASE zAddAssetAttr.ZIMPORTEDBY
                WHEN 0 THEN '0-Cloud-Other-0'
                WHEN 1 THEN '1-Native-Back-Camera-1'
                WHEN 2 THEN '2-Native-Front-Camera-2'
                WHEN 3 THEN '3-Third-Party-App-3'
                WHEN 4 THEN '4-StillTesting-4'
                WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
                WHEN 6 THEN '6-Third-Party-App-6'
                WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
                WHEN 8 THEN '8-System-Package-App-8'
                WHEN 9 THEN '9-Native-App-9'
                WHEN 10 THEN '10-StillTesting-10'
                WHEN 11 THEN '11-StillTesting-11'
                WHEN 12 THEN '12-SWY_Syndication_PL-12'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
            END AS 'zAddAssetAttr-Imported by',
            CASE zAddAssetAttr.ZSHARETYPE
                WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
                WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
            END AS 'zAddAssetAttr-Share Type',
            DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
            DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
            DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
            zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
            DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
            DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
            DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
            zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
            zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
            FROM ZASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
                LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
            ORDER BY zAsset.ZDATECREATED
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
                                      row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                      row[37], row[38], row[39], row[40], row[41]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary/database/Photos.sqlite' \
                              ' for basic asset and album data. The results may contain multiple records' \
                              ' per ZASSET table Z_PK value and supports iOS 14.' \
                              ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                              ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                              ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                              ' Shared with You Conversation Identifiers Assets.'
                report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph2.2-Asset Basic Data & Convers Data-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Date Created',
                                'zAsset-zPK',
                                'zAsset-Directory/Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zExtAttr-Camera Make',
                                'zExtAttr-Camera Model',
                                'zAddAssetAttr-Creator Bundle ID',
                                'zAddAssetAttr-Imported By Display Name',
                                'zAsset-Visibility State',
                                'zAsset-Saved Asset Type',
                                'zAddAssetAttr-Imported by',
                                'zAddAssetAttr-Share Type',
                                'zAsset- SortToken -CameraRoll',
                                'zAsset-Added Date',
                                'zCldMast-Creation Date',
                                'zAddAssetAttr-Time Zone Name',
                                'zAsset-Modification Date',
                                'zAsset-Last Shared Date',
                                'zCldMast-Import Date',
                                'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                                'zAsset-Trashed Date',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint',
                                'zGenAlbum-Creation Date',
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

                tsvname = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                        ' basic asset and album data')

            db.close()
            return

        elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
            zAsset.Z_PK AS 'zAsset-zPK',
            zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
            zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
            SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
            CASE zAsset.ZSYNDICATIONSTATE
                WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
                WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
                WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
                WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
                WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
                WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
                WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
            END AS 'zAsset-Syndication State',      
            zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
            zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
            CASE zAsset.ZBUNDLESCOPE
                WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
                WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
                WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
                WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
            END AS 'zAsset-Bundle Scope',
            zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
            zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
            CASE zAsset.ZVISIBILITYSTATE
                WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
                WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
            END AS 'zAsset-Visibility State',
            CASE zAsset.ZSAVEDASSETTYPE
                WHEN 0 THEN '0-Saved-via-other-source-0'
                WHEN 1 THEN '1-StillTesting-1'
                WHEN 2 THEN '2-StillTesting-2'
                WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
                WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
                WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
                WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
                WHEN 7 THEN '7-StillTesting-7'
                WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
                WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
            END AS 'zAsset-Saved Asset Type',
            CASE zAddAssetAttr.ZIMPORTEDBY
                WHEN 0 THEN '0-Cloud-Other-0'
                WHEN 1 THEN '1-Native-Back-Camera-1'
                WHEN 2 THEN '2-Native-Front-Camera-2'
                WHEN 3 THEN '3-Third-Party-App-3'
                WHEN 4 THEN '4-StillTesting-4'
                WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
                WHEN 6 THEN '6-Third-Party-App-6'
                WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
                WHEN 8 THEN '8-System-Package-App-8'
                WHEN 9 THEN '9-Native-App-9'
                WHEN 10 THEN '10-StillTesting-10'
                WHEN 11 THEN '11-StillTesting-11'
                WHEN 12 THEN '12-SWY_Syndication_PL-12'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
            END AS 'zAddAssetAttr-Imported by',
            CASE zAddAssetAttr.ZSHARETYPE
                WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
                WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
            END AS 'zAddAssetAttr-Share Type',
            DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
            DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
            DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
            zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
            DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
            DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
            DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
            zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
            zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
            FROM ZASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
                LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z27Assets.Z_27ALBUMS
                LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
            ORDER BY zAsset.ZDATECREATED
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
                                      row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                      row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                      row[46]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary/database/Photos.sqlite' \
                              ' for basic asset and album data. The results may contain multiple records' \
                              ' per ZASSET table Z_PK value and supports iOS 15.' \
                              ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                              ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                              ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                              ' Shared with You Conversation Identifiers Assets.'
                report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph2.2-Asset Basic Data & Convers Data-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Date Created',
                                'zAsset-zPK',
                                'zAsset-Directory/Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zAddAssetAttr- Syndication Identifier-SWY-Files',
                                'zAsset- Conversation= zGenAlbum_zPK ',
                                'SWYConverszGenAlbum- Import Session ID',
                                'zAsset-Syndication State',
                                'zExtAttr-Camera Make',
                                'zExtAttr-Camera Model',
                                'zAsset-Bundle Scope',
                                'zAddAssetAttr.Imported by Bundle Identifier',
                                'zAddAssetAttr-Imported By Display Name',
                                'zAsset-Visibility State',
                                'zAsset-Saved Asset Type',
                                'zAddAssetAttr-Imported by',
                                'zAddAssetAttr-Share Type',
                                'zAsset- SortToken -CameraRoll',
                                'zAsset-Added Date',
                                'zCldMast-Creation Date',
                                'zAddAssetAttr-Time Zone Name',
                                'zAsset-Modification Date',
                                'zAsset-Last Shared Date',
                                'zCldMast-Import Date',
                                'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                                'zAsset-Trashed Date',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint',
                                'zGenAlbum-Creation Date',
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

                tsvname = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                        ' basic asset and album data')

            db.close()
            return

        elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
            zAsset.Z_PK AS 'zAsset-zPK',
            zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
            zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
            SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
            CASE zAsset.ZSYNDICATIONSTATE
                WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
                WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
                WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
                WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
                WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
                WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
                WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
            END AS 'zAsset-Syndication State',      
            zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
            zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
            CASE zAsset.ZBUNDLESCOPE
                WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
                WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
                WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
                WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
            END AS 'zAsset-Bundle Scope',            
            zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
            zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
            CASE zAsset.ZVISIBILITYSTATE
                WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
                WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
            END AS 'zAsset-Visibility State',
            CASE zAsset.ZSAVEDASSETTYPE
                WHEN 0 THEN '0-Saved-via-other-source-0'
                WHEN 1 THEN '1-StillTesting-1'
                WHEN 2 THEN '2-StillTesting-2'
                WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
                WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
                WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
                WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
                WHEN 7 THEN '7-StillTesting-7'
                WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
                WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
            END AS 'zAsset-Saved Asset Type',
            CASE zAddAssetAttr.ZIMPORTEDBY
                WHEN 0 THEN '0-Cloud-Other-0'
                WHEN 1 THEN '1-Native-Back-Camera-1'
                WHEN 2 THEN '2-Native-Front-Camera-2'
                WHEN 3 THEN '3-Third-Party-App-3'
                WHEN 4 THEN '4-StillTesting-4'
                WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
                WHEN 6 THEN '6-Third-Party-App-6'
                WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
                WHEN 8 THEN '8-System-Package-App-8'
                WHEN 9 THEN '9-Native-App-9'
                WHEN 10 THEN '10-StillTesting-10'
                WHEN 11 THEN '11-StillTesting-11'
                WHEN 12 THEN '12-SWY_Syndication_PL-12'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
            END AS 'zAddAssetAttr-Imported by',
            CASE zAddAssetAttr.ZSHARETYPE
                WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
                WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
            END AS 'zAddAssetAttr-Share Type',
            CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
                WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
                WHEN 1 THEN '1-Asset-In-Active-SPL-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
            END AS 'zAsset-Active Library Scope Participation State',
            DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
            DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
            DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
            zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
            DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
            DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
            DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
            DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
            zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
            zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
            FROM ZASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
                LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
                LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
            ORDER BY zAsset.ZDATECREATED
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
                                      row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                      row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                      row[46], row[47], row[48], row[49]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary/database/Photos.sqlite' \
                              ' for basic asset and album data. The results may contain multiple records' \
                              ' per ZASSET table Z_PK value and supports iOS 16.' \
                              ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                              ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                              ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                              ' Shared with You Conversation Identifiers Assets.'
                report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph2.2-Asset Basic Data & Convers Data-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Date Created',
                                'zAsset-zPK',
                                'zAsset-Directory/Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zAddAssetAttr- Syndication Identifier-SWY-Files',
                                'zAsset- Conversation= zGenAlbum_zPK ',
                                'SWYConverszGenAlbum- Import Session ID',
                                'zAsset-Syndication State',
                                'zExtAttr-Camera Make',
                                'zExtAttr-Camera Model',
                                'zAsset-Bundle Scope',
                                'zAddAssetAttr.Imported by Bundle Identifier',
                                'zAddAssetAttr-Imported By Display Name',
                                'zAsset-Visibility State',
                                'zAsset-Saved Asset Type',
                                'zAddAssetAttr-Imported by',
                                'zAddAssetAttr-Share Type',
                                'zAsset-Active Library Scope Participation State',
                                'zAsset- SortToken -CameraRoll',
                                'zAsset-Added Date',
                                'zCldMast-Creation Date',
                                'zAddAssetAttr-Time Zone Name',
                                'zAsset-Modification Date',
                                'zAsset-Last Shared Date',
                                'zCldMast-Import Date',
                                'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAddAssetAttr-Last Viewed Date',
                                'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                                'zAsset-Trashed Date',
                                'zAsset-Trashed by Participant= zShareParticipant_zPK',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint',
                                'zGenAlbum-Creation Date',
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

                tsvname = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                        ' basic asset and album data')

            db.close()
            return

        elif version.parse(iosversion) >= version.parse("17"):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
            zAsset.Z_PK AS 'zAsset-zPK',
            zAsset.ZDIRECTORY AS 'zAsset-Directory/Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
            zAsset.ZCONVERSATION AS 'zAsset- Conversation= zGenAlbum_zPK ',
            SWYConverszGenAlbum.ZIMPORTSESSIONID AS 'SWYConverszGenAlbum- Import Session ID',
            CASE zAsset.ZSYNDICATIONSTATE
                WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
                WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
                WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
                WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
                WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
                WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
                WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
            END AS 'zAsset-Syndication State',      
            zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
            zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
            CASE zAsset.ZBUNDLESCOPE
                WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
                WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
                WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
                WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
            END AS 'zAsset-Bundle Scope',
            zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr.Imported by Bundle Identifier',
            zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr-Imported By Display Name',
            CASE zAsset.ZVISIBILITYSTATE
                WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
                WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
            END AS 'zAsset-Visibility State',
            CASE zAsset.ZSAVEDASSETTYPE
                WHEN 0 THEN '0-Saved-via-other-source-0'
                WHEN 1 THEN '1-StillTesting-1'
                WHEN 2 THEN '2-StillTesting-2'
                WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
                WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
                WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
                WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
                WHEN 7 THEN '7-StillTesting-7'
                WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
                WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
            END AS 'zAsset-Saved Asset Type',
            CASE zAddAssetAttr.ZIMPORTEDBY
                WHEN 0 THEN '0-Cloud-Other-0'
                WHEN 1 THEN '1-Native-Back-Camera-1'
                WHEN 2 THEN '2-Native-Front-Camera-2'
                WHEN 3 THEN '3-Third-Party-App-3'
                WHEN 4 THEN '4-StillTesting-4'
                WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
                WHEN 6 THEN '6-Third-Party-App-6'
                WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
                WHEN 8 THEN '8-System-Package-App-8'
                WHEN 9 THEN '9-Native-App-9'
                WHEN 10 THEN '10-StillTesting-10'
                WHEN 11 THEN '11-StillTesting-11'
                WHEN 12 THEN '12-SWY_Syndication_PL-12'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
            END AS 'zAddAssetAttr-Imported by',
            CASE zAddAssetAttr.ZSHARETYPE
                WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
                WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
                ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
            END AS 'zAddAssetAttr-Share Type',
            CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
                WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
                WHEN 1 THEN '1-Asset-In-Active-SPL-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
            END AS 'zAsset-Active Library Scope Participation State',
            DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
            DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
            DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
            zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
            DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
            DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
            DateTime(zCldMast.ZIMPORTDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Import Date',
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
            DateTime(zAddAssetAttr.ZLASTVIEWEDDATE + 978307200, 'UNIXEPOCH') AS 'zAddAssetAttr-Last Viewed Date',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash/Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash/Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State/LocalAssetRecentlyDeleted',
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
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
            zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
            zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID'
            FROM ZASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
                LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK  
                LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN ZGENERICALBUM SWYConverszGenAlbum ON SWYConverszGenAlbum.Z_PK = zAsset.ZCONVERSATION
            ORDER BY zAsset.ZDATECREATED
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
                                      row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                      row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                      row[46], row[47], row[48], row[49]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary/database/Photos.sqlite' \
                              ' for basic asset and album data. The results may contain multiple records' \
                              ' per ZASSET table Z_PK value and supports iOS 17.' \
                              ' Use "2-Non-Shared-Album-2" in the search box to view Non-Shared Albums Assets.' \
                              ' Use "1505-Shared-Album-1505" in the search box to view Shared Albums Assets.' \
                              ' Use "1509-SWY_Synced_Conversation_Media-1509" in the search box to view' \
                              ' Shared with You Conversation Identifiers Assets.'
                report = ArtifactHtmlReport('Photos.sqlite-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph2.2-Asset Basic Data & Convers Data-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Date Created',
                                'zAsset-zPK',
                                'zAsset-Directory/Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zAddAssetAttr- Syndication Identifier-SWY-Files',
                                'zAsset- Conversation= zGenAlbum_zPK ',
                                'SWYConverszGenAlbum- Import Session ID',
                                'zAsset-Syndication State',
                                'zExtAttr-Camera Make',
                                'zExtAttr-Camera Model',
                                'zAsset-Bundle Scope',
                                'zAddAssetAttr.Imported by Bundle Identifier',
                                'zAddAssetAttr-Imported By Display Name',
                                'zAsset-Visibility State',
                                'zAsset-Saved Asset Type',
                                'zAddAssetAttr-Imported by',
                                'zAddAssetAttr-Share Type',
                                'zAsset-Active Library Scope Participation State',
                                'zAsset- SortToken -CameraRoll',
                                'zAsset-Added Date',
                                'zCldMast-Creation Date',
                                'zAddAssetAttr-Time Zone Name',
                                'zAsset-Modification Date',
                                'zAsset-Last Shared Date',
                                'zCldMast-Import Date',
                                'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAddAssetAttr-Last Viewed Date',
                                'zAsset-Trashed State/LocalAssetRecentlyDeleted',
                                'zAsset-Trashed Date',
                                'zAsset-Trashed by Participant= zShareParticipant_zPK',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint',
                                'zGenAlbum-Creation Date',
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

                tsvname = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph2.2-Asset Basic Data & Convers Data-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary/database/Photos.sqlite'
                        ' basic asset and album data')

            db.close()
            return

__artifacts_v2__ = {
    'Ph2-1-Asset Basic & GenAlbum Data-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 2.1 Asset Basic & Generic Album Data',
        'description': 'Parses basic asset record data from PhotoData/Photos.sqlite for basic asset and album data.'
                       ' The results may contain multiple records per ZASSET table Z_PK value and supports iOS 11-17.'
                       ' Use 2-Non-Shared-Album-2 in the search box to view Non-Shared Albums Assets.'
                       ' Use 1505-Shared-Album-1505 in the search box to view Shared Albums Assets.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 in the search box to view'
                       ' Shared with You Conversation Identifiers Assets.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.3',
        'date': '2024-04-13',
        'requirements': 'Acquisition that contains PhotoData/Photos.sqlite',
        'category': 'Photos.sqlite-Asset_Basic_Data',
        'notes': '',
        'paths': ('*/mobile/Media/PhotoData/Photos.sqlite'),
        'function': 'get_ph2assetbasicandalbumdataphdapsql'
    },
    'Ph2-2-Asset Basic & Conversation Data-SyndPL': {
        'name': 'SyndPL Photos.sqlite 2.2 Asset Basic and Conversation Data',
        'description': 'Parses basic asset record data from /Syndication.photoslibrary/database/Photos.sqlite'
                       ' for basic asset and album data. The results may contain multiple records'
                       ' per ZASSET table Z_PK value and supports iOS 11-17.'
                       ' Use -Non-Shared-Album-2 in the search box to view Non-Shared Albums Assets.'
                       ' Use 1505-Shared-Album-1505 in the search box to view Shared Albums Assets.'
                       ' Use 1509-SWY_Synced_Conversation_Media-1509 in the search box to view'
                       ' Shared with You Conversation Identifiers Assets.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.3',
        'date': '2024-04-13',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-Syndication_PL_Artifacts',
        'notes': '',
        'paths': ('*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite'),
        'function': 'get_ph2asserbasicandconversdatasyndpl'
    }
}