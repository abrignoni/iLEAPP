# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 2.0
#
#   Description:
#   Parses basic asset record data from PhotoData-Photos.sqlite for recently deleted-trashed assets
#   and supports iOS 11-18. SyndPL Parser parses basic asset record data from
#   Syndication.photoslibrary-database-Photos.sqlite for indicators of assets removed from the camera roll
#   and supports iOS 15-18. The results for these scripts will contain one record per ZASSET table Z_PK value.
#   This parser is based on research and SQLite queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph3trashedphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite recently deleted or"
                " trashed assets from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE      
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' trashed-recently deleted assets and supports iOS 11-13.' \
                          ' The results for this script will contain one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph3.1-Trashed Recently Deleted-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Trashed Date',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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

            tsvname = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Trashed Recently Deleted Assets')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' trashed-recently deleted assets and supports iOS 14.' \
                          ' The results for this script will contain one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph3.1-Trashed Recently Deleted-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Trashed Date',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted',
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

            tsvname = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Trashed Recently Deleted Assets')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
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

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' trashed-recently deleted assets and supports iOS 15.' \
                          ' The results for this script will contain one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph3.1-Trashed Recently Deleted-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Trashed Date',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted',
                            'zAsset-Directory-Path',
                            'zAsset-Filename',
                            'zAddAssetAttr- Original Filename',
                            'zCldMast- Original Filename',
                            'zCldMast-Import Session ID- AirDrop-StillTesting',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files',
                            'zAsset-Syndication State',
                            'zAsset-zPK',
                            'zAddAssetAttr-zPK',
                            'zAsset-UUID = store.cloudphotodb',
                            'zAddAssetAttr-Master Fingerprint')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Trashed Recently Deleted Assets')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("18")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
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

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' trashed-recently deleted assets and supports iOS 16-17.' \
                          ' The results for this script will contain one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph3.1-Trashed Recently Deleted-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Trashed Date-0',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-2',
                            'SPLzSharePartic-zPK= TrashedByParticipant-3',
                            'SPLzSharePartic-Email Address-4',
                            'SPLzSharePartic-Phone Number-5',
                            'zAsset-Directory-Path-6',
                            'zAsset-Filename-7',
                            'zAddAssetAttr- Original Filename-8',
                            'zCldMast- Original Filename-9',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-10',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                            'zAsset-Syndication State-12',
                            'zAsset-zPK-13',
                            'zAddAssetAttr-zPK-14',
                            'zAsset-UUID = store.cloudphotodb-15',
                            'zAddAssetAttr-Master Fingerprint-16')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Trashed Recently Deleted Assets')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("18"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash-iOS18'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
            LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
            LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZTRASHEDSTATE = 1
        ORDER BY zAsset.ZTRASHEDSTATE
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

                counter += 1

            description = 'Parses basic asset record data from PhotoData-Photos.sqlite for' \
                          ' trashed-recently deleted assets and supports iOS 18.' \
                          ' The results for this script will contain one record per ZASSET table Z_PK value.'
            report = ArtifactHtmlReport('Photos.sqlite-B-Interaction_Artifacts')
            report.start_artifact_report(report_folder, 'Ph3.1-Trashed Recently Deleted-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Trashed Date-0',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-2',
                            'SPLzSharePartic-zPK= TrashedByParticipant-3',
                            'SPLzSharePartic-Email Address-4',
                            'SPLzSharePartic-Phone Number-5',
                            'zAsset-Directory-Path-6',
                            'zAsset-Filename-7',
                            'zAddAssetAttr- Original Filename-8',
                            'zCldMast- Original Filename-9',
                            'zCldMast-Import Session ID- AirDrop-StillTesting-10',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                            'zAsset-Syndication State-12',
                            'zAsset-zPK-13',
                            'zAddAssetAttr-zPK-14',
                            'zAsset-UUID = store.cloudphotodb-15',
                            'zAddAssetAttr-Original Stable Hash-iOS18-16',
                            'zAddAssetAttr.Adjusted Stable Hash-iOS18-17')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph3.1-Trashed Recently Deleted-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available for PhotoData-Photos.sqlite Trashed Recently Deleted Assets')

        db.close()
        return


def get_ph3removedfromcamerarollsyndpl(files_found, report_folder, seeker, wrap_text, timezone_offset):
        for file_found in files_found:
            file_found = str(file_found)

            if file_found.endswith('.sqlite'):
                break

        if report_folder.endswith('/') or report_folder.endswith('\\'):
            report_folder = report_folder[:-1]
        iosversion = scripts.artifacts.artGlobals.versionf
        if version.parse(iosversion) <= version.parse("14.8.1"):
            logfunc("Unsupported version for Syndication.photoslibrary-database-Photos.sqlite"
                    " Syndication PL assets removed from camera roll iOS " + iosversion)
        if (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
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
            zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',               
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',           
            zAsset.Z_PK AS 'zAsset-zPK',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
            FROM ZASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            WHERE zAsset.ZSYNDICATIONSTATE IN (8, 10)
            ORDER BY zAddAssetAttr.ZLASTUPLOADATTEMPTDATE
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

                description = 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite' \
                              ' for syndication PL asserts remvoed from camera roll and supports iOS 15.' \
                              ' These assets may have been displayed in the camera roll, then deleted from' \
                              ' the camera roll view. The results for this script will contain one record per asset.'
                report = ArtifactHtmlReport('Photos.sqlite-S-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph3.2-Removed from camera roll-SyndPL', description)
                report.add_script()
                data_headers = ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAsset-Syndication State',
                                'zAsset-Directory-Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zAddAssetAttr- Syndication Identifier-SWY-Files',
                                'zAsset-Trashed Date',
                                'zAsset-Trashed State-LocalAssetRecentlyDeleted',
                                'zAsset-zPK',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = 'Ph3.2-Removed from camera roll-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph3.2-Removed from camera roll-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary-database-Photos.sqlite'
                        ' possible deleted or removed from camera roll SyndPL assets')

            db.close()
            return

        elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("18")):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAddAssetAttr.ZLASTUPLOADATTEMPTDATE + 978307200, 'UNIXEPOCH') AS
             'zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
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
            zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
            zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',            
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
            zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
            SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
            SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
            SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',            
            zAsset.Z_PK AS 'zAsset-zPK',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
            FROM ZASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
                LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
                LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
            WHERE zAsset.ZSYNDICATIONSTATE IN (8, 10)
            ORDER BY zAddAssetAttr.ZLASTUPLOADATTEMPTDATE
            """)

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []
            counter = 0
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite' \
                              ' for syndication PL asserts removed from camera roll and supports iOS 16-17.' \
                              ' These assets may have been displayed in the camera roll, then deleted from' \
                              ' the camera roll view. The results for this script will contain one record per asset.'
                report = ArtifactHtmlReport('Photos.sqlite-S-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph3.2-Removed from camera roll-SyndPL', description)
                report.add_script()
                data_headers = ('zAddAssetAttr-Last Upload Attempt Date-SWY_Files',
                                'zAsset-Syndication State',
                                'zAsset-Directory-Path',
                                'zAsset-Filename',
                                'zAddAssetAttr- Original Filename',
                                'zCldMast- Original Filename',
                                'zCldMast-Import Session ID- AirDrop-StillTesting',
                                'zAddAssetAttr- Syndication Identifier-SWY-Files',
                                'zAsset-Trashed Date',
                                'zAsset-Trashed State-LocalAssetRecentlyDeleted',
                                'zAsset-Trashed by Participant= zShareParticipant_zPK',
                                'SPLzSharePartic-zPK= TrashedByParticipant',
                                'SPLzSharePartic-Email Address',
                                'SPLzSharePartic-Phone Number',
                                'zAsset-zPK',
                                'zAddAssetAttr-zPK',
                                'zAsset-UUID = store.cloudphotodb',
                                'zAddAssetAttr-Master Fingerprint')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = 'Ph3.2-Removed from camera roll-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph3.2-Removed from camera roll-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary-database-Photos.sqlite'
                        ' possible deleted or removed from camera roll SyndPL assets')

            db.close()
            return

        elif version.parse(iosversion) >= version.parse("18"):
            file_found = str(files_found[0])
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            SELECT
            DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
            CASE zAsset.ZTRASHEDSTATE
                WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
                WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
                ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
            END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
            zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
            SPLzSharePartic.Z_PK AS 'SPLzSharePartic-zPK= TrashedByParticipant',
            SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
            SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',
            zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
            zAsset.ZFILENAME AS 'zAsset-Filename',
            zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
            zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
            zCldMast.ZIMPORTSESSIONID AS 'zCldMast-Import Session ID- AirDrop-StillTesting',
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
            zAsset.Z_PK AS 'zAsset-zPK',
            zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
            zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
            zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18',
            zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash-iOS18'
            FROM ZASSET zAsset
                LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
                LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
                LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
                LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
                LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
            WHERE zAsset.ZTRASHEDSTATE = 1
            ORDER BY zAsset.ZTRASHEDSTATE
            """)

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []
            counter = 0
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

                    counter += 1

                description = 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite' \
                              ' for syndication PL asserts removed from camera roll and supports iOS 18.' \
                              ' These assets may have been displayed in the camera roll, then deleted from' \
                              ' the camera roll view. The results for this script will contain one record per asset.'
                report = ArtifactHtmlReport('Photos.sqlite-S-Syndication_PL_Artifacts')
                report.start_artifact_report(report_folder, 'Ph3.2-Removed from camera roll-SyndPL', description)
                report.add_script()
                data_headers = ('zAsset-Trashed Date-0',
                                'zAsset-Trashed State-LocalAssetRecentlyDeleted-1',
                                'zAsset-Trashed by Participant= zShareParticipant_zPK-2',
                                'SPLzSharePartic-zPK= TrashedByParticipant-3',
                                'SPLzSharePartic-Email Address-4',
                                'SPLzSharePartic-Phone Number-5',
                                'zAsset-Directory-Path-6',
                                'zAsset-Filename-7',
                                'zAddAssetAttr- Original Filename-8',
                                'zCldMast- Original Filename-9',
                                'zCldMast-Import Session ID- AirDrop-StillTesting-10',
                                'zAddAssetAttr- Syndication Identifier-SWY-Files-11',
                                'zAsset-Syndication State-12',
                                'zAsset-zPK-13',
                                'zAddAssetAttr-zPK-14',
                                'zAsset-UUID = store.cloudphotodb-15',
                                'zAddAssetAttr-Original Stable Hash-iOS18-16',
                                'zAddAssetAttr.Adjusted Stable Hash-iOS18-17')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

                tsvname = 'Ph3.2-Removed from camera roll-SyndPL'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Ph3.2-Removed from camera roll-SyndPL'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No data available for Syndication.photoslibrary-database-Photos.sqlite'
                        ' possible deleted or removed from camera roll SyndPL assets')

            db.close()
            return


__artifacts_v2__ = {
    'Ph3-1-Recently Deleted Trashed-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 3.1 Trashed Recently Deleted',
        'description': 'Parses basic asset record data from PhotoData-Photos.sqlite for trashed-recently deleted'
                       ' assets and supports iOS 11-17. The results for this script will contain one record'
                       ' per ZASSET table Z_PK value.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '2.0',
        'date': '2024-06-12',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': '*/PhotoData/Photos.sqlite*',
        'function': 'get_ph3trashedphdapsql'
    },
    'Ph3-2-Removed from Camera Roll-SyndPL': {
        'name': 'SyndPL Photos.sqlite 3.2 Removed from camera roll',
        'description': 'Parses basic asset record data from Syndication.photoslibrary-database-Photos.sqlite'
                       ' for syndication PL asserts remvoed from camera roll and supports iOS 15-17.'
                       ' These assets may have been displayed in the camera roll, then deleted from'
                       ' the camera roll view. The results for this script will contain one record per asset.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '2.0',
        'date': '2024-06-12',
        'requirements': 'Acquisition that contains Syndication Photo Library Photos.sqlite',
        'category': 'Photos.sqlite-S-Syndication_PL_Artifacts',
        'notes': '',
        'paths': '*/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite*',
        'function': 'get_ph3removedfromcamerarollsyndpl'
    }
}
