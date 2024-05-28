# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.2
#
#   Description:
#   Parses Non-Shared Album records found in the PhotoData-Photos.sqlite ZGENERICALBUM Table and supports iOS 11-17.
#   Parses Non-Shared Album records only no asset data being parsed. This parser will contain parent albums and
#   folders, and associated album data.
#   This parser is based on research and SQLite Queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph21nonsharedalbumsphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite Non-Shared Album records with"
                " no asset data from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("12")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_19ALBUMLISTS z19AlbumLists ON z19AlbumLists.Z_19ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z19AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zGenAlbum.ZSTARTDATE
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

            description = 'Parses Non-Shared Album records found in the PhotoData-Photos.sqlite from' \
                          ' ZGENERICALBUM Table and supports iOS 11. Parses Non-Shared Album records only' \
                          ' no asset data is being parsed in this parser. This parser will contain parent albums,' \
                          ' folders, and associated album data. '
            report = ArtifactHtmlReport('Photos.sqlite-D-Generic_Album_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph21-Non-Shared Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'ParentzGenAlbum-UUID',
                            'ParentzGenAlbum-Cloud GUID',
                            'ParentzGenAlbum- Title',
                            'zGenAlbum- Title-User&System Applied',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID',
                            'ParentzGenAlbum-Pending Items Count',
                            'ParentzGenAlbum-Pending Items Type',
                            'ParentzGenAlbum-Kind',
                            'ParentzGenAlbum-Cloud-Local-State',
                            'ParentzGenAlbum-Sync Event Order Key',
                            'ParentzGenAlbum-Pinned',
                            'ParentzGenAlbum-Custom Sort Key',
                            'ParentzGenAlbum-Custom Sort Ascending',
                            'ParentzGenAlbum-Custom Query Type',
                            'ParentzGenAlbum-Trashed State',
                            'ParentzGenAlbum-Trash Date',
                            'zGenAlbum-Pending Items Count',
                            'zGenAlbum-Pending Items Type',
                            'zGenAlbum- Cached Photos Count',
                            'zGenAlbum- Cached Videos Count',
                            'zGenAlbum- Cached Count',
                            'zGenAlbum-Has Unseen Content',
                            'zGenAlbum-Unseen Asset Count',
                            'zGenAlbum-zENT- Entity',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Cloud_Local_State',
                            'zGenAlbum-Sync Event Order Key',
                            'zGenAlbum-Pinned',
                            'zGenAlbum-Custom Sort Key',
                            'zGenAlbum-Custom Sort Ascending',
                            'zGenAlbum-Custom Query Type',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Non-Shared Album Records with No Asset Data')

            db.close()
        return

    elif (version.parse(iosversion) >= version.parse("12")) & (version.parse(iosversion) < version.parse("13")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_22ALBUMLISTS z22AlbumLists ON z22AlbumLists.Z_22ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z22AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zGenAlbum.ZSTARTDATE
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
                                  row[37]))

                counter += 1

            description = 'Parses Non-Shared Album records found in the PhotoData-Photos.sqlite from' \
                          ' ZGENERICALBUM Table and supports iOS 12. Parses Non-Shared Album records only' \
                          ' no asset data is being parsed in this parser. This parser will contain parent albums,' \
                          ' folders, and associated album data. '
            report = ArtifactHtmlReport('Photos.sqlite-D-Generic_Album_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph21-Non-Shared Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'ParentzGenAlbum-UUID',
                            'ParentzGenAlbum-Cloud GUID',
                            'ParentzGenAlbum- Title',
                            'zGenAlbum- Title-User&System Applied',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID',
                            'ParentzGenAlbum-Pending Items Count',
                            'ParentzGenAlbum-Pending Items Type',
                            'ParentzGenAlbum-Kind',
                            'ParentzGenAlbum-Cloud-Local-State',
                            'ParentzGenAlbum-Sync Event Order Key',
                            'ParentzGenAlbum-Pinned',
                            'ParentzGenAlbum-Custom Sort Key',
                            'ParentzGenAlbum-Custom Sort Ascending',
                            'ParentzGenAlbum-Custom Query Type',
                            'ParentzGenAlbum-Trashed State',
                            'ParentzGenAlbum-Trash Date',
                            'ParentzGenAlbum-Cloud Delete State',
                            'zGenAlbum-Pending Items Count',
                            'zGenAlbum-Pending Items Type',
                            'zGenAlbum- Cached Photos Count',
                            'zGenAlbum- Cached Videos Count',
                            'zGenAlbum- Cached Count',
                            'zGenAlbum-Has Unseen Content',
                            'zGenAlbum-Unseen Asset Count',
                            'zGenAlbum-zENT- Entity',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Cloud_Local_State',
                            'zGenAlbum-Sync Event Order Key',
                            'zGenAlbum-Pinned',
                            'zGenAlbum-Custom Sort Key',
                            'zGenAlbum-Custom Sort Ascending',
                            'zGenAlbum-Custom Query Type',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-Cloud Delete State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Non-Shared Album Records with No Asset Data')

            db.close()
        return

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zGenAlbum.ZCREATIONDATE
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
                                  row[37], row[38], row[39], row[40]))

                counter += 1

            description = 'Parses Non-Shared Album records found in the PhotoData-Photos.sqlite from' \
                          ' ZGENERICALBUM Table and supports iOS 13. Parses Non-Shared Album records only' \
                          ' no asset data is being parsed in this parser. This parser will contain parent albums,' \
                          ' folders, and associated album data. '
            report = ArtifactHtmlReport('Photos.sqlite-D-Generic_Album_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph21-Non-Shared Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'ParentzGenAlbum-UUID',
                            'ParentzGenAlbum-Cloud GUID',
                            'ParentzGenAlbum- Title',
                            'zGenAlbum- Title-User&System Applied',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID',
                            'ParentzGenAlbum-Pending Items Count',
                            'ParentzGenAlbum-Pending Items Type',
                            'ParentzGenAlbum-Kind',
                            'ParentzGenAlbum-Cloud-Local-State',
                            'ParentzGenAlbum-Sync Event Order Key',
                            'ParentzGenAlbum-Pinned',
                            'ParentzGenAlbum-Custom Sort Key',
                            'ParentzGenAlbum-Custom Sort Ascending',
                            'ParentzGenAlbum-Project Document Type',
                            'ParentzGenAlbum-Custom Query Type',
                            'ParentzGenAlbum-Trashed State',
                            'ParentzGenAlbum-Trash Date',
                            'ParentzGenAlbum-Cloud Delete State',
                            'zGenAlbum-Pending Items Count',
                            'zGenAlbum-Pending Items Type',
                            'zGenAlbum- Cached Photos Count',
                            'zGenAlbum- Cached Videos Count',
                            'zGenAlbum- Cached Count',
                            'zGenAlbum-Has Unseen Content',
                            'zGenAlbum-Unseen Asset Count',
                            'zGenAlbum-zENT- Entity',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Cloud_Local_State',
                            'zGenAlbum-Sync Event Order Key',
                            'zGenAlbum-Pinned',
                            'zGenAlbum-Custom Sort Key',
                            'zGenAlbum-Custom Sort Ascending',
                            'zGenAlbum-Project Document Type',
                            'zGenAlbum-Custom Query Type',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-Cloud Delete State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Non-Shared Album Records with No Asset Data')

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
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle Id',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
            WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
        END AS 'ParentzGenAlbum-Is Prototype',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zGenAlbum.ZCREATIONDATE
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
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44]))

                counter += 1

            description = 'Parses Non-Shared Album records found in the PhotoData-Photos.sqlite from' \
                          ' ZGENERICALBUM Table and supports iOS 14. Parses Non-Shared Album records only' \
                          ' no asset data is being parsed in this parser. This parser will contain parent albums,' \
                          ' folders, and associated album data. '
            report = ArtifactHtmlReport('Photos.sqlite-D-Generic_Album_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph21-Non-Shared Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'ParentzGenAlbum-UUID',
                            'ParentzGenAlbum-Cloud GUID',
                            'ParentzGenAlbum- Title',
                            'zGenAlbum- Title-User&System Applied',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID',
                            'zGenAlbum-Creator Bundle Id',
                            'ParentzGenAlbum-Creation Date',
                            'ParentzGenAlbum-Pending Items Count',
                            'ParentzGenAlbum-Pending Items Type',
                            'ParentzGenAlbum-Kind',
                            'ParentzGenAlbum-Cloud-Local-State',
                            'ParentzGenAlbum-Sync Event Order Key',
                            'ParentzGenAlbum-Pinned',
                            'ParentzGenAlbum-Custom Sort Key',
                            'ParentzGenAlbum-Custom Sort Ascending',
                            'ParentzGenAlbum-Is Prototype',
                            'ParentzGenAlbum-Project Document Type',
                            'ParentzGenAlbum-Custom Query Type',
                            'ParentzGenAlbum-Trashed State',
                            'ParentzGenAlbum-Trash Date',
                            'ParentzGenAlbum-Cloud Delete State',
                            'zGenAlbum-Pending Items Count',
                            'zGenAlbum-Pending Items Type',
                            'zGenAlbum- Cached Photos Count',
                            'zGenAlbum- Cached Videos Count',
                            'zGenAlbum- Cached Count',
                            'zGenAlbum-Has Unseen Content',
                            'zGenAlbum-Unseen Asset Count',
                            'zGenAlbum-zENT- Entity',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Cloud_Local_State',
                            'zGenAlbum-Sync Event Order Key',
                            'zGenAlbum-Pinned',
                            'zGenAlbum-Custom Sort Key',
                            'zGenAlbum-Custom Sort Ascending',
                            'zGenAlbum-Is Prototype',
                            'zGenAlbum-Project Document Type',
                            'zGenAlbum-Custom Query Type',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-Cloud Delete State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Non-Shared Album Records with No Asset Data')

            db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
            WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
        END AS 'ParentzGenAlbum-Is Prototype',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zGenAlbum.ZCREATIONDATE
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
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44]))

                counter += 1

            description = 'Parses Non-Shared Album records found in the PhotoData-Photos.sqlite from' \
                          ' ZGENERICALBUM Table and supports iOS 15. Parses Non-Shared Album records only' \
                          ' no asset data is being parsed in this parser. This parser will contain parent albums,' \
                          ' folders, and associated album data. '
            report = ArtifactHtmlReport('Photos.sqlite-D-Generic_Album_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph21-Non-Shared Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'ParentzGenAlbum-UUID',
                            'ParentzGenAlbum-Cloud GUID',
                            'ParentzGenAlbum- Title',
                            'zGenAlbum- Title-User&System Applied',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID',
                            'zGenAlbum-Imported by Bundle Identifier',
                            'ParentzGenAlbum-Creation Date',
                            'ParentzGenAlbum-Pending Items Count',
                            'ParentzGenAlbum-Pending Items Type',
                            'ParentzGenAlbum-Kind',
                            'ParentzGenAlbum-Cloud-Local-State',
                            'ParentzGenAlbum-Sync Event Order Key',
                            'ParentzGenAlbum-Pinned',
                            'ParentzGenAlbum-Custom Sort Key',
                            'ParentzGenAlbum-Custom Sort Ascending',
                            'ParentzGenAlbum-Is Prototype',
                            'ParentzGenAlbum-Project Document Type',
                            'ParentzGenAlbum-Custom Query Type',
                            'ParentzGenAlbum-Trashed State',
                            'ParentzGenAlbum-Trash Date',
                            'ParentzGenAlbum-Cloud Delete State',
                            'zGenAlbum-Pending Items Count',
                            'zGenAlbum-Pending Items Type',
                            'zGenAlbum- Cached Photos Count',
                            'zGenAlbum- Cached Videos Count',
                            'zGenAlbum- Cached Count',
                            'zGenAlbum-Has Unseen Content',
                            'zGenAlbum-Unseen Asset Count',
                            'zGenAlbum-zENT- Entity',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Cloud_Local_State',
                            'zGenAlbum-Sync Event Order Key',
                            'zGenAlbum-Pinned',
                            'zGenAlbum-Custom Sort Key',
                            'zGenAlbum-Custom Sort Ascending',
                            'zGenAlbum-Is Prototype',
                            'zGenAlbum-Project Document Type',
                            'zGenAlbum-Custom Query Type',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-Cloud Delete State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Non-Shared Album Records with No Asset Data')

            db.close()
        return

    elif version.parse(iosversion) >= version.parse("16"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
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
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
            WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
        END AS 'ParentzGenAlbum-Is Prototype',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
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
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZSEARCHINDEXREBUILDSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
        END AS 'zGenAlbum-Search Index Rebuild State',        
        CASE zGenAlbum.ZDUPLICATETYPE
            WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
            WHEN 1 THEN 'Duplicate Asset_Pending-Merge-1'
            WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZDUPLICATETYPE || ''
        END AS 'zGenAlbum-Duplicate Type',        
        CASE zGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPRIVACYSTATE || ''
        END AS 'zGenAlbum-Privacy State'
        FROM ZGENERICALBUM zGenAlbum
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZCLOUDSHAREDALBUMINVITATIONRECORD zCldShareAlbumInvRec ON zGenAlbum.Z_PK
             = zCldShareAlbumInvRec.ZALBUM
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zGenAlbum.ZCREATIONDATE
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
                                  row[46], row[47]))

                counter += 1

            description = 'Parses Non-Shared Album records found in the PhotoData-Photos.sqlite from' \
                          ' ZGENERICALBUM Table and supports iOS 16-17. Parses Non-Shared Album records only' \
                          ' no asset data is being parsed in this parser. This parser will contain parent albums,' \
                          ' folders, and associated album data. '
            report = ArtifactHtmlReport('Photos.sqlite-D-Generic_Album_Records-NAD')
            report.start_artifact_report(report_folder, 'Ph21-Non-Shared Album Records NAD-PhDaPsql', description)
            report.add_script()
            data_headers = ('zGenAlbum-Creation Date',
                            'zGenAlbum-Start Date',
                            'zGenAlbum-End Date',
                            'ParentzGenAlbum-UUID',
                            'ParentzGenAlbum-Cloud GUID',
                            'ParentzGenAlbum- Title',
                            'zGenAlbum- Title-User&System Applied',
                            'zGenAlbum-UUID',
                            'zGenAlbum-Cloud GUID',
                            'zGenAlbum-Imported by Bundle Identifier',
                            'ParentzGenAlbum-Creation Date',
                            'ParentzGenAlbum-Pending Items Count',
                            'ParentzGenAlbum-Pending Items Type',
                            'ParentzGenAlbum-Kind',
                            'ParentzGenAlbum-Cloud-Local-State',
                            'ParentzGenAlbum-Sync Event Order Key',
                            'ParentzGenAlbum-Pinned',
                            'ParentzGenAlbum-Custom Sort Key',
                            'ParentzGenAlbum-Custom Sort Ascending',
                            'ParentzGenAlbum-Is Prototype',
                            'ParentzGenAlbum-Project Document Type',
                            'ParentzGenAlbum-Custom Query Type',
                            'ParentzGenAlbum-Trashed State',
                            'ParentzGenAlbum-Trash Date',
                            'ParentzGenAlbum-Cloud Delete State',
                            'zGenAlbum-Pending Items Count',
                            'zGenAlbum-Pending Items Type',
                            'zGenAlbum- Cached Photos Count',
                            'zGenAlbum- Cached Videos Count',
                            'zGenAlbum- Cached Count',
                            'zGenAlbum-Has Unseen Content',
                            'zGenAlbum-Unseen Asset Count',
                            'zGenAlbum-zENT- Entity',
                            'zGenAlbum-Album Kind',
                            'zGenAlbum-Cloud_Local_State',
                            'zGenAlbum-Sync Event Order Key',
                            'zGenAlbum-Pinned',
                            'zGenAlbum-Custom Sort Key',
                            'zGenAlbum-Custom Sort Ascending',
                            'zGenAlbum-Is Prototype',
                            'zGenAlbum-Project Document Type',
                            'zGenAlbum-Custom Query Type',
                            'zGenAlbum-Trashed State',
                            'zGenAlbum-Trash Date',
                            'zGenAlbum-Cloud Delete State',
                            'zGenAlbum-Search Index Rebuild State',
                            'zGenAlbum-Duplicate Type',
                            'zGenAlbum-Privacy State')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph21-Non-Shared Album Records NAD-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Non-Shared Album Records with No Asset Data')

        db.close()
        return


__artifacts_v2__ = {
    'Ph21-Non-Shared Album Records with NAD-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 21 Non-Shared Album Records with No Asset Data',
        'description': 'Parses Non-Shared Album records found in the PhotoData-Photos.sqlite ZGENERICALBUM Table'
                       ' and supports iOS 11-17. Parses Non-Shared Album records only, no asset data being parsed.'
                       ' This parser will contain parent albums and folders, and associated album data.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.2',
        'date': '2024-04-09',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-D-Generic_Album_Records-NAD',
        'notes': '',
        'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
        'function': 'get_ph21nonsharedalbumsphdapsql'
    }
}
