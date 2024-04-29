# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.0
#
#   Description:
#   Parses iCloud Shared Link records and related assets from the PhotoData-Photos.sqlite ZSHARE Table
#   and supports iOS 14-17.
#   This parser is based on research and SQLite Queries written by Scott Koenig
#   This is very large query and script, I recommend opening the TSV generated report with Zimmerman's Tools
#   https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search and filter the results.
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


def get_ph35icldsharedLinkassetsphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("13.7"):
        logfunc("Unsupported version for iCloud Shared Link Assets from PhotoData-Photos.sqlite from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
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
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        CASE zShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
        END AS 'zShare-Status',
        CASE zShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
        END AS 'zShare-Scope Type',
        zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
        zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',  
        zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
        zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
        zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
        zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        CASE zShare.ZLOCALPUBLISHSTATE
            WHEN 2 THEN '2-Published-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
        END AS 'zShare-Local Publish State',
        CASE zShare.ZPUBLICPERMISSION
            WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
            WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
        END AS 'zShare-Public Permission',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE zSharePartic.ZPERMISSION
            WHEN 3 THEN '3-Participant-has-Full-Premissions-3'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
        END AS 'zSharePartic-Premission',
        CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
            WHEN 0 THEN '0-DoNotNotify-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
        END AS 'zShare-Should Notify On Upload Completion',
        CASE zShare.ZSHOULDIGNOREBUDGETS
            WHEN 1 THEN '1-StillTesting-CMM-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
        END AS 'zShare-Should Ignor Budgets',
        CASE zShare.ZTRASHEDSTATE
            WHEN 0 THEN '0-Not_in_Trash-0'
            WHEN 1 THEN '1-In_Trash-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
        END AS 'zShare-Trashed State',
        CASE zShare.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-Not Deleted-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
        END AS 'zShare-Cloud Delete State',
        CASE zShare.Z_ENT
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
        END AS 'zShare-zENT'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zAsset.ZSAVEDASSETTYPE = 8
        ORDER BY zShare.ZCREATIONDATE        
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
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53]))

                counter += 1

            description = 'Parses iCloud Shared Link records and related assets from the' \
                          ' PhotoData-Photos.sqlite ZSHARE Table and supports iOS 14-15.'
            report = ArtifactHtmlReport('Photos.sqlite-iCloud_Shared_Methods')
            report.start_artifact_report(report_folder, 'Ph35-iCld Shared Link Assets-PhDaPsql', description)
            report.add_script()
            data_headers = ('zShare-Creation Date-0',
                            'zShare-Start Date-1',
                            'zShare-End Date-2',
                            'zShare-Expiry Date-3',
                            'zAsset-Date Created-4',
                            'zAsset-zPK-5',
                            'zAsset-Directory-Path-6',
                            'zAsset-Filename-7',
                            'zAddAssetAttr- Original Filename-8',
                            'zCldMast- Original Filename-9',
                            'zAddAssetAttr- Creator Bundle ID-10',
                            'zAddAssetAttr-Imported By Display Name-11',
                            'zAsset-Visibility State-12',
                            'zAsset-Saved Asset Type-13',
                            'zAddAssetAttr-Share Type-14',
                            'zAsset- SortToken -CameraRoll-15',
                            'zAsset-Added Date-16',
                            'zCldMast-Creation Date-17',
                            'zAddAssetAttr-Time Zone Name-18',
                            'zAddAssetAttr-EXIF-String-19',
                            'zAsset-Modification Date-20',
                            'zAsset-Last Shared Date-21',
                            'zAsset-Trashed Date-22',
                            'zAddAssetAttr-zPK-23',
                            'zAsset-UUID = store.cloudphotodb-24',
                            'zAddAssetAttr-Master Fingerprint-25',
                            'zShare-UUID-26',
                            'zShare-Originating Scope ID-27',
                            'zShare-Status-28',
                            'zShare-Scope Type-29',
                            'zShare-Asset Count-CMM-30',
                            'zShare-Force Sync Attempted-CMM-31',
                            'zShare-Photos Count-CMM-32',
                            'zShare-Uploaded Photos Count-CMM-33',
                            'zShare-Videos Count-CMM-34',
                            'zShare-Uploaded Videos Count-CMM-35',
                            'zShare-Scope ID-36',
                            'zShare-Title-SPL-37',
                            'zShare-Share URL-38',
                            'zShare-Local Publish State-39',
                            'zShare-Public Permission-40',
                            'zSharePartic-Acceptance Status-41',
                            'zSharePartic-User ID-42',
                            'zSharePartic-zPK-43',
                            'zSharePartic-Email Address-44',
                            'zSharePartic-Phone Number-45',
                            'zSharePartic-Is Current User-46',
                            'zSharePartic-Role-47',
                            'zSharePartic-Premission-48',
                            'zShare-Should Notify On Upload Completion-49',
                            'zShare-Should Ignor Budgets-50',
                            'zShare-Trashed State-51',
                            'zShare-Cloud Delete State-52',
                            'zShare-zENT-53')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph35-iCld Shared Link Assets-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph35-iCld Shared Link Assets-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No iCloud Shared Link Assets found in PhotoData-Photos.sqlite ZSHARE table')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
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
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
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
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',       
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        CASE zShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
        END AS 'zShare-Status',
        CASE zShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
        END AS 'zShare-Scope Type',
        zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
        zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',  
        zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
        zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
        zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
        zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        CASE zShare.ZLOCALPUBLISHSTATE
            WHEN 2 THEN '2-Published-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
        END AS 'zShare-Local Publish State',
        CASE zShare.ZPUBLICPERMISSION
            WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
            WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
        END AS 'zShare-Public Permission',
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE zSharePartic.ZPERMISSION
            WHEN 3 THEN '3-Participant-has-Full-Premissions-3'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
        END AS 'zSharePartic-Premission',
        CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
            WHEN 0 THEN '0-DoNotNotify-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
        END AS 'zShare-Should Notify On Upload Completion',
        CASE zShare.ZSHOULDIGNOREBUDGETS
            WHEN 1 THEN '1-StillTesting-CMM-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
        END AS 'zShare-Should Ignor Budgets',
        CASE zShare.ZTRASHEDSTATE
            WHEN 0 THEN '0-Not_in_Trash-0'
            WHEN 1 THEN '1-In_Trash-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
        END AS 'zShare-Trashed State',
        CASE zShare.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-Not Deleted-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
        END AS 'zShare-Cloud Delete State',
        CASE zShare.Z_ENT
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
        END AS 'zShare-zENT'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zAsset.ZSAVEDASSETTYPE = 8
        ORDER BY zShare.ZCREATIONDATE
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
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56]))

                counter += 1

            description = 'Parses iCloud Shared Link records and related assets from the' \
                          ' PhotoData-Photos.sqlite ZSHARE Table and supports iOS 14-15.'
            report = ArtifactHtmlReport('Photos.sqlite-iCloud_Shared_Methods')
            report.start_artifact_report(report_folder, 'Ph35-iCld Shared Link Assets-PhDaPsql', description)
            report.add_script()
            data_headers = ('zShare-Creation Date-0',
                            'zShare-Start Date-1',
                            'zShare-End Date-2',
                            'zShare-Expiry Date-3',
                            'zAsset-Date Created-4',
                            'zAsset-zPK-5',
                            'zAsset-Directory-Path-6',
                            'zAsset-Filename-7',
                            'zAddAssetAttr- Original Filename-8',
                            'zCldMast- Original Filename-9',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-10',
                            'zAsset-Syndication State-11',
                            'zAsset-Bundle Scope-12',
                            'zAddAssetAttr- Imported by Bundle Identifier-13',
                            'zAddAssetAttr-Imported By Display Name-14',
                            'zAsset-Visibility State-15',
                            'zAsset-Saved Asset Type-16',
                            'zAddAssetAttr-Share Type-17',
                            'zAsset- SortToken -CameraRoll-18',
                            'zAsset-Added Date-19',
                            'zCldMast-Creation Date-20',
                            'zAddAssetAttr-Time Zone Name-21',
                            'zAddAssetAttr-EXIF-String-22',
                            'zAsset-Modification Date-23',
                            'zAsset-Last Shared Date-24',
                            'zAsset-Trashed Date-25',
                            'zAddAssetAttr-zPK-26',
                            'zAsset-UUID = store.cloudphotodb-27',
                            'zAddAssetAttr-Master Fingerprint-28',
                            'zShare-UUID-29',
                            'zShare-Originating Scope ID-30',
                            'zShare-Status-31',
                            'zShare-Scope Type-32',
                            'zShare-Asset Count-CMM-33',
                            'zShare-Force Sync Attempted-CMM-34',
                            'zShare-Photos Count-CMM-35',
                            'zShare-Uploaded Photos Count-CMM-36',
                            'zShare-Videos Count-CMM-37',
                            'zShare-Uploaded Videos Count-CMM-38',
                            'zShare-Scope ID-39',
                            'zShare-Title-SPL-40',
                            'zShare-Share URL-41',
                            'zShare-Local Publish State-42',
                            'zShare-Public Permission-43',
                            'zSharePartic-Acceptance Status-44',
                            'zSharePartic-User ID-45',
                            'zSharePartic-zPK-46',
                            'zSharePartic-Email Address-47',
                            'zSharePartic-Phone Number-48',
                            'zSharePartic-Is Current User-49',
                            'zSharePartic-Role-50',
                            'zSharePartic-Premission-51',
                            'zShare-Should Notify On Upload Completion-52',
                            'zShare-Should Ignor Budgets-53',
                            'zShare-Trashed State-54',
                            'zShare-Cloud Delete State-55',
                            'zShare-zENT-56')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph35-iCld Shared Link Assets-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph35-iCld Shared Link Assets-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No iCloud Shared Link Assets found in PhotoData-Photos.sqlite ZSHARE table')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("16"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Creation Date',
        DateTime(zShare.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Start Date',
        DateTime(zShare.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-End Date',
        DateTime(zShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Expiry Date',
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
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
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
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
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        zShare.ZUUID AS 'zShare-UUID',
        zShare.ZORIGINATINGSCOPEIDENTIFIER AS 'zShare-Originating Scope ID',
        CASE zSharePartic.Z54_SHARE
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.Z54_SHARE || ''
        END AS 'zSharePartic-z54SHARE',       
        CASE zShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSTATUS || ''
        END AS 'zShare-Status',
        CASE zShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPETYPE || ''
        END AS 'zShare-Scope Type',
        zShare.ZASSETCOUNT AS 'zShare-Asset Count-CMM',
        zShare.ZFORCESYNCATTEMPTED AS 'zShare-Force Sync Attempted-CMM',  
        zShare.ZPHOTOSCOUNT AS 'zShare-Photos Count-CMM',
        zShare.ZUPLOADEDPHOTOSCOUNT AS 'zShare-Uploaded Photos Count-CMM',
        zShare.ZVIDEOSCOUNT AS 'zShare-Videos Count-CMM',
        zShare.ZUPLOADEDVIDEOSCOUNT AS 'zShare-Uploaded Videos Count-CMM',  
        zShare.ZSCOPEIDENTIFIER AS 'zShare-Scope ID',
        zShare.ZTITLE AS 'zShare-Title-SPL',
        zShare.ZSHAREURL AS 'zShare-Share URL',
        CASE zShare.ZLOCALPUBLISHSTATE
            WHEN 2 THEN '2-Published-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZLOCALPUBLISHSTATE || ''
        END AS 'zShare-Local Publish State',
        CASE zShare.ZPUBLICPERMISSION
            WHEN 1 THEN '1-Public_Premission_Denied-Private-1'
            WHEN 2 THEN '2-Public_Premission_Granted-Public-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPUBLICPERMISSION || ''
        END AS 'zShare-Public Permission',
        CASE zShare.ZCLOUDLOCALSTATE
            WHEN 1 THEN '1-LocalandCloud-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDLOCALSTATE || ''
        END AS 'zShare-Cloud Local State',
        CASE zShare.ZSCOPESYNCINGSTATE
            WHEN 1 THEN '1-ScopeAllowedToSync-SPL-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSCOPESYNCINGSTATE || ''
        END AS 'zShare-Scope Syncing State',
        CASE zShare.ZAUTOSHAREPOLICY
            WHEN 0 THEN '0-AutoShare-OFF_SPL_Test_NotAllAtSetup-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZAUTOSHAREPOLICY || ''
        END AS 'zShare-Auto Share Policy',  
        CASE zSharePartic.ZACCEPTANCESTATUS
            WHEN 1 THEN '1-Invite-Pending_or_Declined-1'
            WHEN 2 THEN '2-Invite-Accepted-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZACCEPTANCESTATUS || ''
        END AS 'zSharePartic-Acceptance Status',
        zSharePartic.ZUSERIDENTIFIER AS 'zSharePartic-User ID',
        zSharePartic.Z_PK AS 'zSharePartic-zPK',
        zSharePartic.ZEMAILADDRESS AS 'zSharePartic-Email Address',
        zSharePartic.ZPHONENUMBER AS 'zSharePartic-Phone Number',
        zSharePartic.ZPARTICIPANTID AS 'zSharePartic-Participant ID',
        zSharePartic.ZUUID AS 'zSharePartic-UUID',  
        CASE zSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_CurrentUser-0'
            WHEN 1 THEN '1-Participant-Is_CurrentUser-1'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZISCURRENTUSER || ''
        END AS 'zSharePartic-Is Current User',
        CASE zSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZROLE || ''
        END AS 'zSharePartic-Role',
        CASE zSharePartic.ZPERMISSION
            WHEN 3 THEN '3-Participant-has-Full-Premissions-3'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZPERMISSION || ''
        END AS 'zSharePartic-Premission',
        CASE zShare.ZPARTICIPANTCLOUDUPDATESTATE
            WHEN 2 THEN '2-ParticipantAllowedToUpdate_SPL_StillTesting-2'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPARTICIPANTCLOUDUPDATESTATE || ''
        END AS 'zShare-Participant Cloud Update State', 
        CASE zSharePartic.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zSharePartic.ZEXITSTATE || ''
        END AS 'zSharePartic-Exit State',
        CASE zShare.ZPREVIEWSTATE
            WHEN 0 THEN '0-NotInPreviewState-StillTesting-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZPREVIEWSTATE || ''
        END AS 'zShare-Preview State',
        CASE zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION
            WHEN 0 THEN '0-DoNotNotify-SPL-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDNOTIFYONUPLOADCOMPLETION || ''
        END AS 'zShare-Should Notify On Upload Completion',
        CASE zShare.ZSHOULDIGNOREBUDGETS
            WHEN 1 THEN '1-StillTesting-CMM-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZSHOULDIGNOREBUDGETS || ''
        END AS 'zShare-Should Ignor Budgets',
        CASE zShare.ZEXITSOURCE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSOURCE || ''
        END AS 'zShare-Exit Source',
        CASE zShare.ZEXITSTATE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITSTATE || ''
        END AS 'zShare-Exit State',
        CASE zShare.ZEXITTYPE
            WHEN 0 THEN '0-NA_SPL_StillTesting'
            ELSE 'Unknown-New-Value!: ' || zShare.ZEXITTYPE || ''
        END AS 'zShare-Exit Type',
        CASE zShare.ZTRASHEDSTATE
            WHEN 0 THEN '0-Not_in_Trash-0'
            WHEN 1 THEN '1-In_Trash-1'
            ELSE 'Unknown-New-Value!: ' || zShare.ZTRASHEDSTATE || ''
        END AS 'zShare-Trashed State',
        CASE zShare.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-Not Deleted-0'
            ELSE 'Unknown-New-Value!: ' || zShare.ZCLOUDDELETESTATE || ''
        END AS 'zShare-Cloud Delete State',
        DateTime(zShare.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zShare-Trashed Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-LastParticipant Asset Trash Notification Date',
        DateTime(zShare.ZLASTPARTICIPANTASSETTRASHNOTIFICATIONVIEWEDDATE + 978307200, 'UNIXEPOCH') AS
         'zShare-Last Participant Asset Trash Notification View Date',
        CASE zShare.Z_ENT
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            ELSE 'Unknown-New-Value!: ' || zShare.Z_ENT || ''
        END AS 'zShare-zENT'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE zShare ON zShare.Z_PK = zAsset.ZMOMENTSHARE
            LEFT JOIN ZSHAREPARTICIPANT zSharePartic ON zSharePartic.ZSHARE = zShare.Z_PK
        WHERE zAsset.ZSAVEDASSETTYPE = 8
        ORDER BY zShare.ZCREATIONDATE
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
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                  row[73]))

                counter += 1

            description = 'Parses iCloud Shared Link records and related assets from the' \
                          ' PhotoData-Photos.sqlite ZSHARE Table and supports iOS 16-17.'
            report = ArtifactHtmlReport('Photos.sqlite-iCloud_Shared_Methods')
            report.start_artifact_report(report_folder, 'Ph35-iCld Shared Link Assets-PhDaPsql', description)
            report.add_script()
            data_headers = ('zShare-Creation Date-0',
                            'zShare-Start Date-1',
                            'zShare-End Date-2',
                            'zShare-Expiry Date-3',
                            'zAsset-Date Created-4',
                            'zAsset-zPK-5',
                            'zAsset-Directory-Path-6',
                            'zAsset-Filename-7',
                            'zAddAssetAttr- Original Filename-8',
                            'zCldMast- Original Filename-9',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-10',
                            'zAsset-Syndication State-11',
                            'zAsset-Bundle Scope-12',
                            'zAddAssetAttr.Imported by Bundle Identifier-13',
                            'zAddAssetAttr-Imported By Display Name-14',
                            'zAsset-Visibility State-15',
                            'zAsset-Saved Asset Type-16',
                            'zAddAssetAttr-Share Type-17',
                            'zAsset-Active Library Scope Participation State-18',
                            'zAsset- SortToken -CameraRoll-19',
                            'zAsset-Added Date-20',
                            'zCldMast-Creation Date-21',
                            'zAddAssetAttr-Time Zone Name-22',
                            'zAddAssetAttr-EXIF-String-23',
                            'zAsset-Modification Date-24',
                            'zAsset-Last Shared Date-25',
                            'zAsset-Trashed Date-26',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-27',
                            'zAddAssetAttr-zPK-28',
                            'zAsset-UUID = store.cloudphotodb-29',
                            'zAddAssetAttr-Master Fingerprint-30',
                            'zShare-UUID-31',
                            'zShare-Originating Scope ID-32',
                            'zSharePartic-z54SHARE-33',
                            'zShare-Status-34',
                            'zShare-Scope Type-35',
                            'zShare-Asset Count-CMM-36',
                            'zShare-Force Sync Attempted-CMM-37',
                            'zShare-Photos Count-CMM-38',
                            'zShare-Uploaded Photos Count-CMM-39',
                            'zShare-Videos Count-CMM-40',
                            'zShare-Uploaded Videos Count-CMM-41',
                            'zShare-Scope ID-42',
                            'zShare-Title-SPL-43',
                            'zShare-Share URL-44',
                            'zShare-Local Publish State-45',
                            'zShare-Public Permission-46',
                            'zShare-Cloud Local State-47',
                            'zShare-Scope Syncing State-48',
                            'zShare-Auto Share Policy-49',
                            'zSharePartic-Acceptance Status-50',
                            'zSharePartic-User ID-51',
                            'zSharePartic-zPK-52',
                            'zSharePartic-Email Address-53',
                            'zSharePartic-Phone Number-54',
                            'zSharePartic-Participant ID-55',
                            'zSharePartic-UUID-56',
                            'zSharePartic-Is Current User-57',
                            'zSharePartic-Role-58',
                            'zSharePartic-Premission-59',
                            'zShare-Participant Cloud Update State-60',
                            'zSharePartic-Exit State-61',
                            'zShare-Preview State-62',
                            'zShare-Should Notify On Upload Completion-63',
                            'zShare-Should Ignor Budgets-64',
                            'zShare-Exit Source-65',
                            'zShare-Exit State-66',
                            'zShare-Exit Type-67',
                            'zShare-Trashed State-68',
                            'zShare-Cloud Delete State-69',
                            'zShare-Trashed Date-70',
                            'zShare-LastParticipant Asset Trash Notification Date-71',
                            'zShare-Last Participant Asset Trash Notification View Date-72',
                            'zShare-zENT-73')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph35-iCld Shared Link Assets-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph35-iCld Shared Link Assets-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No iCloud Shared Link Assets found in PhotoData-Photos.sqlite ZSHARE table')

        db.close()
        return


__artifacts_v2__ = {
    'Ph35-iCloud Shared Link Assets-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 35 iCld Shared Link Assets',
        'description': 'Parses iCloud Shared Link records and related assets from the'
                       ' PhotoData-Photos.sqlite ZSHARE Table and supports iOS 14-17.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-04-13',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-iCloud_Shared_Methods',
        'notes': '',
        'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
        'function': 'get_ph35icldsharedLinkassetsphdapsql'
    }
}
