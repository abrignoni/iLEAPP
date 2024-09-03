#   Photos.sqlite
#   Author:  Scott Koenig
#   Version: 1.0
#
#   Description:
#   Parses basic asset record data from */PhotoData/Photos.sqlite for assets that have Keywords, Captions, Titles,
#   Descriptions, Captions and Likes. (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0)
#   or (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0)
#   or (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0)
#   or (zCldSharedCommentLiked.ZISLIKE = 1)
#   I recommend opening the TSV generated report with Zimmerman's Tools
#   https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search and filter the results.
#   This parser is based on research and SQLite Queries written by Scott Koenig
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph11kwrdscapstitlesdescripsbasicassetdataphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite basic asset data from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
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
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        zAssetDes.ZLONGDESCRIPTION AS 'zAssetDes-Long Description',
        zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
        zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
        zKeywrd.ZSHORTCUT AS 'zKeywrd-Shortcut',
        zKeywrd.ZTITLE AS 'zKeywrd-Title',
        zCldSharedComment.ZCOMMENTTYPE AS 'zCldSharedComment-Type',
        zCldSharedComment.ZCOMMENTTEXT AS 'zCldSharedComment-Comment Text',
        DateTime(zCldFeedEnt.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS 'zCldFeedEnt-Entry Date',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID-4TableStart',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart',
        CASE zCldFeedEnt.ZENTRYPRIORITYNUMBER
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYPRIORITYNUMBER || ''
        END AS 'zCldFeedEnt-Entry Priority Number',
        CASE zCldFeedEnt.ZENTRYTYPENUMBER
            WHEN 1 THEN 'Is My Shared Asset-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-StillTesting-3'
            WHEN 4 THEN 'Not My Shared Asset-4'
            WHEN 5 THEN 'Asset in Album with Invite Record-5'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYTYPENUMBER || ''
        END AS 'zCldFeedEnt-Entry Type Number',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID-4TableStart',
        DateTime(zCldSharedComment.ZCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Date',
        DateTime(zCldSharedComment.ZCOMMENTCLIENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Comment Client Date',
        DateTime(zAsset.ZCLOUDLASTVIEWEDCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Last Viewed Comment Date',		
        zCldSharedComment.ZCOMMENTERHASHEDPERSONID AS 'zCldSharedComment-Commenter Hashed Person ID',
        CASE zCldSharedComment.ZISBATCHCOMMENT
            WHEN 0 THEN 'Not Batch Comment-0'
            WHEN 1 THEN 'Batch Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISBATCHCOMMENT || ''
        END AS 'zCldSharedComment-Batch Comment',
        CASE zCldSharedComment.ZISCAPTION
            WHEN 0 THEN 'Not a Caption-0'
            WHEN 1 THEN 'Caption-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISCAPTION || ''
        END AS 'zCldSharedComment-Is a Caption',
        CASE zAsset.ZCLOUDHASCOMMENTSBYME
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Asset-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSBYME || ''
        END AS 'zAsset-Cloud Has Comments by Me',
        CASE zCldSharedComment.ZISMYCOMMENT
            WHEN 0 THEN 'Not My Comment-0'
            WHEN 1 THEN 'My Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISMYCOMMENT || ''
        END AS 'zCldSharedComment-Is My Comment',
        CASE zCldSharedComment.ZISDELETABLE
            WHEN 0 THEN 'Not Deletable-0'
            WHEN 1 THEN 'Deletable-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISDELETABLE || ''
        END AS 'zCldSharedComment-Is Deletable',
        CASE zAsset.ZCLOUDHASCOMMENTSCONVERSATION
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Conversation-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSCONVERSATION || ''
        END AS 'zAsset-Cloud Has Comments Conversation',
        CASE zAsset.ZCLOUDHASUNSEENCOMMENTS
            WHEN 0 THEN 'zAsset No Unseen Comments-0'
            WHEN 1 THEN 'zAsset Unseen Comments-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASUNSEENCOMMENTS || ''
        END AS 'zAsset-Cloud Has Unseen Comments',
        CASE zCldSharedCommentLiked.ZISLIKE
            WHEN 0 THEN 'Asset Not Liked-0'
            WHEN 1 THEN 'Asset Liked-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedCommentLiked.ZISLIKE || ''
        END AS 'zCldSharedComment-Liked',       
        zAddAssetAttr.ZASSETDESCRIPTION AS 'zAddAssetAttr-Asset Description',
        zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
        zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
        zCldFeedEnt.Z_PK AS 'zCldFeedEnt-zPK= zCldShared keys',
        zCldFeedEnt.Z_ENT AS 'zCldFeedEnt-zENT',
        zCldFeedEnt.Z_OPT AS 'zCldFeedEnt-zOPT',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID',
        zCldSharedComment.Z_PK AS 'zCldSharedComment-zPK',
        zCldSharedComment.Z_ENT AS 'zCldSharedComment-zENT',
        zCldSharedComment.Z_OPT AS 'zCldSharedComment-zOPT',
        zCldSharedComment.ZCOMMENTEDASSET AS 'zCldSharedComment-Commented Asset Key= zAsset-zPK',
        zCldSharedComment.ZCLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK',
        zCldSharedComment.Z_FOK_CLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key',
        zCldSharedCommentLiked.ZLIKEDASSET AS 'zCldSharedComment-Liked Asset Key= zAsset-zPK',
        zCldSharedCommentLiked.ZCLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-CldFeedLikeCommentEntry Key',
        zCldSharedCommentLiked.Z_FOK_CLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID',       
        zKeywrd.Z_PK AS 'zKeywrd-zPK',
        z1KeyWrds.Z_36KEYWORDS AS 'z1KeyWrds-36Keywords = zKeywrd-zPK',
        zKeywrd.Z_ENT AS 'zKeywrd-zENT',
        zKeywrd.Z_OPT AS 'zKeywrd-zOPT',       
        zKeywrd.ZUUID AS 'zKeywrd-UUID',       
        zAsset.Z_PK AS 'zAsset-zPK',
        z1KeyWrds.Z_1ASSETATTRIBUTES AS 'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_1KEYWORDS z1KeyWrds ON zAddAssetAttr.Z_PK = z1KeyWrds.Z_1ASSETATTRIBUTES
            LEFT JOIN ZKEYWORD zKeywrd ON z1KeyWrds.Z_36KEYWORDS = zKeywrd.Z_PK
            LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
            LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
        WHERE (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or (zCldSharedCommentLiked.ZISLIKE = 1)
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
                                    row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                    row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                    row[64], row[65], row[66], row[67], row[68], row[69], row[70]))

                counter += 1

            description = ('Parses basic asset record data from iOS14 *PhotoData-Photos.sqlite for assets that have'
                           ' Keywords, Captions, Titles, Descriptions, Captions and Likes.'
                           ' (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or'
                           ' (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or'
                           ' (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or'
                           ' (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or'
                           ' (zCldSharedCommentLiked.ZISLIKE = 1). I recommend opening the TSV generated report'
                           ' with Zimmermans Tools https://ericzimmerman.github.io/#!index.md TimelineExplorer to view,'
                           ' search and filter the results. This parser is based on research and SQLite Queries'
                           ' written by Scott Koenig https://theforensicscooter.com/')
            report = ArtifactHtmlReport('Ph11 Keywords Captions Titles Descriptions Likes and Basic Asset Datas')
            report.start_artifact_report(report_folder, 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-EXIF-String-5',
                            'zAsset-Modification Date-6',
                            'zAsset-Last Shared Date-7',
                            'zAsset-Trashed Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAddAssetAttr- Creator Bundle ID-13',
                            'zAsset-Saved Asset Type-14',
                            'zAsset-Visibility State-15',
                            'zAssetDes-Long Description-16',
                            'zAddAssetAttr-Title-Comments via Cloud Website-17',
                            'zAddAssetAttr-Accessibility Description-18',
                            'zKeywrd-Shortcut-19',
                            'zKeywrd-Title-20',
                            'zCldSharedComment-Type-21',
                            'zCldSharedComment-Comment Text-22',
                            'zCldFeedEnt-Entry Date-23',
                            'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-24',
                            'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-25',
                            'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-26',
                            'zCldFeedEnt-Entry Priority Number-27',
                            'zCldFeedEnt-Entry Type Number-28',
                            'zCldSharedComment-Cloud GUID-4TableStart-29',
                            'zCldSharedComment-Date-30',
                            'zCldSharedComment-Comment Client Date-31',
                            'zAsset-Cloud Last Viewed Comment Date-32',
                            'zCldSharedComment-Commenter Hashed Person ID-33',
                            'zCldSharedComment-Batch Comment-34',
                            'zCldSharedComment-Is a Caption-35',
                            'zAsset-Cloud Has Comments by Me-36',
                            'zCldSharedComment-Is My Comment-37',
                            'zCldSharedComment-Is Deletable-38',
                            'zAsset-Cloud Has Comments Conversation-39',
                            'zAsset-Cloud Has Unseen Comments-40',
                            'zCldSharedComment-Liked-41',
                            'zAddAssetAttr-Asset Description-42',
                            'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-43',
                            'zAsset-FOK-Cloud Feed Asset Entry Key-44',
                            'zCldFeedEnt-zPK= zCldShared keys-45',
                            'zCldFeedEnt-zENT-46',
                            'zCldFeedEnt-zOPT-47',
                            'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-48',
                            'zCldFeedEnt-Entry Invitation Record GUID-49',
                            'zCldFeedEnt-Entry Cloud Asset GUID-50',
                            'zCldSharedComment-zPK-51',
                            'zCldSharedComment-zENT-52',
                            'zCldSharedComment-zOPT-53',
                            'zCldSharedComment-Commented Asset Key= zAsset-zPK-54',
                            'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-55',
                            'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-56',
                            'zCldSharedComment-Liked Asset Key= zAsset-zPK-57',
                            'zCldSharedComment-CldFeedLikeCommentEntry Key-58',
                            'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-59',
                            'zCldSharedComment-Cloud GUID-60',
                            'zKeywrd-zPK-61',
                            'z1KeyWrds-36Keywords = zKeywrd-zPK-62',
                            'zKeywrd-zENT-63',
                            'zKeywrd-zOPT-64',
                            'zKeywrd-UUID-65',
                            'zAsset-zPK-66',
                            'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK-67',
                            'zAddAssetAttr-zPK-68',
                            'zAsset-UUID = store.cloudphotodb-69',
                            'zAddAssetAttr-Master Fingerprint-70')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc('No data available for iOS 14 Photos.sqlite Keywords Captions Titles Descriptions Basic Asst Data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files', 
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
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
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',       
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',	
        zAssetDes.ZLONGDESCRIPTION AS 'zAssetDes-Long Description',
        zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
        zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
        zKeywrd.ZSHORTCUT AS 'zKeywrd-Shortcut',
        zKeywrd.ZTITLE AS 'zKeywrd-Title',
        zCldSharedComment.ZCOMMENTTYPE AS 'zCldSharedComment-Type',
        zCldSharedComment.ZCOMMENTTEXT AS 'zCldSharedComment-Comment Text',
        DateTime(zCldFeedEnt.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS 'zCldFeedEnt-Entry Date',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID-4TableStart',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart',
        CASE zCldFeedEnt.ZENTRYPRIORITYNUMBER
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYPRIORITYNUMBER || ''
        END AS 'zCldFeedEnt-Entry Priority Number',
        CASE zCldFeedEnt.ZENTRYTYPENUMBER
            WHEN 1 THEN 'Is My Shared Asset-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-StillTesting-3'
            WHEN 4 THEN 'Not My Shared Asset-4'
            WHEN 5 THEN 'Asset in Album with Invite Record-5'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYTYPENUMBER || ''
        END AS 'zCldFeedEnt-Entry Type Number',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID-4TableStart',
        DateTime(zCldSharedComment.ZCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Date',
        DateTime(zCldSharedComment.ZCOMMENTCLIENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Comment Client Date',
        DateTime(zAsset.ZCLOUDLASTVIEWEDCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Last Viewed Comment Date',		
        zCldSharedComment.ZCOMMENTERHASHEDPERSONID AS 'zCldSharedComment-Commenter Hashed Person ID',
        CASE zCldSharedComment.ZISBATCHCOMMENT
            WHEN 0 THEN 'Not Batch Comment-0'
            WHEN 1 THEN 'Batch Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISBATCHCOMMENT || ''
        END AS 'zCldSharedComment-Batch Comment',
        CASE zCldSharedComment.ZISCAPTION
            WHEN 0 THEN 'Not a Caption-0'
            WHEN 1 THEN 'Caption-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISCAPTION || ''
        END AS 'zCldSharedComment-Is a Caption',
        CASE zAsset.ZCLOUDHASCOMMENTSBYME
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Asset-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSBYME || ''
        END AS 'zAsset-Cloud Has Comments by Me',
        CASE zCldSharedComment.ZISMYCOMMENT
            WHEN 0 THEN 'Not My Comment-0'
            WHEN 1 THEN 'My Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISMYCOMMENT || ''
        END AS 'zCldSharedComment-Is My Comment',
        CASE zCldSharedComment.ZISDELETABLE
            WHEN 0 THEN 'Not Deletable-0'
            WHEN 1 THEN 'Deletable-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISDELETABLE || ''
        END AS 'zCldSharedComment-Is Deletable',
        CASE zAsset.ZCLOUDHASCOMMENTSCONVERSATION
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Conversation-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSCONVERSATION || ''
        END AS 'zAsset-Cloud Has Comments Conversation',
        CASE zAsset.ZCLOUDHASUNSEENCOMMENTS
            WHEN 0 THEN 'zAsset No Unseen Comments-0'
            WHEN 1 THEN 'zAsset Unseen Comments-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASUNSEENCOMMENTS || ''
        END AS 'zAsset-Cloud Has Unseen Comments',
        CASE zCldSharedCommentLiked.ZISLIKE
            WHEN 0 THEN 'Asset Not Liked-0'
            WHEN 1 THEN 'Asset Liked-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedCommentLiked.ZISLIKE || ''
        END AS 'zCldSharedComment-Liked',       
        zAddAssetAttr.ZASSETDESCRIPTION AS 'zAddAssetAttr-Asset Description',
        zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
        zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
        zCldFeedEnt.Z_PK AS 'zCldFeedEnt-zPK= zCldShared keys',
        zCldFeedEnt.Z_ENT AS 'zCldFeedEnt-zENT',
        zCldFeedEnt.Z_OPT AS 'zCldFeedEnt-zOPT',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID',
        zCldSharedComment.Z_PK AS 'zCldSharedComment-zPK',
        zCldSharedComment.Z_ENT AS 'zCldSharedComment-zENT',
        zCldSharedComment.Z_OPT AS 'zCldSharedComment-zOPT',
        zCldSharedComment.ZCOMMENTEDASSET AS 'zCldSharedComment-Commented Asset Key= zAsset-zPK',
        zCldSharedComment.ZCLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK',
        zCldSharedComment.Z_FOK_CLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key',
        zCldSharedCommentLiked.ZLIKEDASSET AS 'zCldSharedComment-Liked Asset Key= zAsset-zPK',
        zCldSharedCommentLiked.ZCLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-CldFeedLikeCommentEntry Key',
        zCldSharedCommentLiked.Z_FOK_CLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID',       
        zKeywrd.Z_PK AS 'zKeywrd-zPK',
        z1KeyWrds.Z_38KEYWORDS AS 'z1KeyWrds-38Keywords = zKeywrd-zPK',
        zKeywrd.Z_ENT AS 'zKeywrd-zENT',
        zKeywrd.Z_OPT AS 'zKeywrd-zOPT',       
        zKeywrd.ZUUID AS 'zKeywrd-UUID',       
        z1KeyWrds.Z_1ASSETATTRIBUTES AS 'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_1KEYWORDS z1KeyWrds ON zAddAssetAttr.Z_PK = z1KeyWrds.Z_1ASSETATTRIBUTES
            LEFT JOIN ZKEYWORD zKeywrd ON z1KeyWrds.Z_38KEYWORDS = zKeywrd.Z_PK
            LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
            LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
        WHERE (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or (zCldSharedCommentLiked.ZISLIKE = 1)
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
                                    row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                    row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                    row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                    row[73], row[74], row[75]))

                counter += 1

            description = ('Parses basic asset record data from iOS15 *PhotoData-Photos.sqlite for assets that have'
                            ' Keywords, Captions, Titles, Descriptions, Captions and Likes.'
                            ' (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or'
                            ' (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or'
                            ' (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or'
                            ' (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or'
                            ' (zCldSharedCommentLiked.ZISLIKE = 1). I recommend opening the TSV generated report'
                            ' with Zimmermans Tools https://ericzimmerman.github.io/#!index.md TimelineExplorer to view,'
                            ' search and filter the results. This parser is based on research and SQLite Queries'
                            ' written by Scott Koenig https://theforensicscooter.com/')
            report = ArtifactHtmlReport('Ph11 Keywords Captions Titles Descriptions Likes and Basic Asset Data')
            report.start_artifact_report(report_folder, 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-EXIF-String-5',
                            'zAsset-Modification Date-6',
                            'zAsset-Last Shared Date-7',
                            'zAsset-Trashed Date-8',
                            'zAsset-Directory-Path-9',
                            'zAsset-Filename-10',
                            'zAddAssetAttr- Original Filename-11',
                            'zCldMast- Original Filename-12',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-13',
                            'zAddAssetAttr- Imported by Bundle Identifier-14',
                            'zAddAssetAttr- Imported By Display Name-15',
                            'zAsset-Saved Asset Type-16',
                            'zAsset-Syndication State-17',
                            'zAsset-Bundle Scope-18',
                            'zAddAssetAttr-Share Type-19',
                            'zAsset-Visibility State-20',
                            'zAssetDes-Long Description-21',
                            'zAddAssetAttr-Title-Comments via Cloud Website-22',
                            'zAddAssetAttr-Accessibility Description-23',
                            'zKeywrd-Shortcut-24',
                            'zKeywrd-Title-25',
                            'zCldSharedComment-Type-26',
                            'zCldSharedComment-Comment Text-27',
                            'zCldFeedEnt-Entry Date-28',
                            'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-29',
                            'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-30',
                            'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-31',
                            'zCldFeedEnt-Entry Priority Number-32',
                            'zCldFeedEnt-Entry Type Number-33',
                            'zCldSharedComment-Cloud GUID-4TableStart-34',
                            'zCldSharedComment-Date-35',
                            'zCldSharedComment-Comment Client Date-36',
                            'zAsset-Cloud Last Viewed Comment Date-37',
                            'zCldSharedComment-Commenter Hashed Person ID-38',
                            'zCldSharedComment-Batch Comment-39',
                            'zCldSharedComment-Is a Caption-40',
                            'zAsset-Cloud Has Comments by Me-41',
                            'zCldSharedComment-Is My Comment-42',
                            'zCldSharedComment-Is Deletable-43',
                            'zAsset-Cloud Has Comments Conversation-44',
                            'zAsset-Cloud Has Unseen Comments-45',
                            'zCldSharedComment-Liked-46',
                            'zAddAssetAttr-Asset Description-47',
                            'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-48',
                            'zAsset-FOK-Cloud Feed Asset Entry Key-49',
                            'zCldFeedEnt-zPK= zCldShared keys-50',
                            'zCldFeedEnt-zENT-51',
                            'zCldFeedEnt-zOPT-52',
                            'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-53',
                            'zCldFeedEnt-Entry Invitation Record GUID-54',
                            'zCldFeedEnt-Entry Cloud Asset GUID-55',
                            'zCldSharedComment-zPK-56',
                            'zCldSharedComment-zENT-57',
                            'zCldSharedComment-zOPT-58',
                            'zCldSharedComment-Commented Asset Key= zAsset-zPK-59',
                            'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-60',
                            'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-61',
                            'zCldSharedComment-Liked Asset Key= zAsset-zPK-62',
                            'zCldSharedComment-CldFeedLikeCommentEntry Key-63',
                            'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-64',
                            'zCldSharedComment-Cloud GUID-65',
                            'zKeywrd-zPK-66',
                            'z1KeyWrds-38Keywords = zKeywrd-zPK-67',
                            'zKeywrd-zENT-68',
                            'zKeywrd-zOPT-69',
                            'zKeywrd-UUID-70',
                            'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK-71',
                            'zAsset-zPK-72',
                            'zAddAssetAttr-zPK-73',
                            'zAsset-UUID = store.cloudphotodb-74',
                            'zAddAssetAttr-Master Fingerprint-75')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc('No data available for iOS15 Photos.sqlite Keywords Captions Titles Descriptions Basic Asst Data')

        db.close()
        return

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("18")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
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
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',	
        zAssetDes.ZLONGDESCRIPTION AS 'zAssetDes-Long Description',
        zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
        zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
        zKeywrd.ZSHORTCUT AS 'zKeywrd-Shortcut',
        zKeywrd.ZTITLE AS 'zKeywrd-Title',
        zCldSharedComment.ZCOMMENTTYPE AS 'zCldSharedComment-Type',
        zCldSharedComment.ZCOMMENTTEXT AS 'zCldSharedComment-Comment Text',
        DateTime(zCldFeedEnt.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS 'zCldFeedEnt-Entry Date',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID-4TableStart',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart',
        CASE zCldFeedEnt.ZENTRYPRIORITYNUMBER
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYPRIORITYNUMBER || ''
        END AS 'zCldFeedEnt-Entry Priority Number',
        CASE zCldFeedEnt.ZENTRYTYPENUMBER
            WHEN 1 THEN 'Is My Shared Asset-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-StillTesting-3'
            WHEN 4 THEN 'Not My Shared Asset-4'
            WHEN 5 THEN 'Asset in Album with Invite Record-5'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYTYPENUMBER || ''
        END AS 'zCldFeedEnt-Entry Type Number',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID-4TableStart',
        DateTime(zCldSharedComment.ZCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Date',
        DateTime(zCldSharedComment.ZCOMMENTCLIENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Comment Client Date',
        DateTime(zAsset.ZCLOUDLASTVIEWEDCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Last Viewed Comment Date',		
        zCldSharedComment.ZCOMMENTERHASHEDPERSONID AS 'zCldSharedComment-Commenter Hashed Person ID',
        CASE zCldSharedComment.ZISBATCHCOMMENT
            WHEN 0 THEN 'Not Batch Comment-0'
            WHEN 1 THEN 'Batch Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISBATCHCOMMENT || ''
        END AS 'zCldSharedComment-Batch Comment',
        CASE zCldSharedComment.ZISCAPTION
            WHEN 0 THEN 'Not a Caption-0'
            WHEN 1 THEN 'Caption-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISCAPTION || ''
        END AS 'zCldSharedComment-Is a Caption',
        CASE zAsset.ZCLOUDHASCOMMENTSBYME
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Asset-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSBYME || ''
        END AS 'zAsset-Cloud Has Comments by Me',
        CASE zCldSharedComment.ZISMYCOMMENT
            WHEN 0 THEN 'Not My Comment-0'
            WHEN 1 THEN 'My Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISMYCOMMENT || ''
        END AS 'zCldSharedComment-Is My Comment',
        CASE zCldSharedComment.ZISDELETABLE
            WHEN 0 THEN 'Not Deletable-0'
            WHEN 1 THEN 'Deletable-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISDELETABLE || ''
        END AS 'zCldSharedComment-Is Deletable',
        CASE zAsset.ZCLOUDHASCOMMENTSCONVERSATION
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Conversation-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSCONVERSATION || ''
        END AS 'zAsset-Cloud Has Comments Conversation',
        CASE zAsset.ZCLOUDHASUNSEENCOMMENTS
            WHEN 0 THEN 'zAsset No Unseen Comments-0'
            WHEN 1 THEN 'zAsset Unseen Comments-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASUNSEENCOMMENTS || ''
        END AS 'zAsset-Cloud Has Unseen Comments',
        CASE zCldSharedCommentLiked.ZISLIKE
            WHEN 0 THEN 'Asset Not Liked-0'
            WHEN 1 THEN 'Asset Liked-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedCommentLiked.ZISLIKE || ''
        END AS 'zCldSharedComment-Liked',       
        zAddAssetAttr.ZASSETDESCRIPTION AS 'zAddAssetAttr-Asset Description',
        zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
        zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
        zCldFeedEnt.Z_PK AS 'zCldFeedEnt-zPK= zCldShared keys',
        zCldFeedEnt.Z_ENT AS 'zCldFeedEnt-zENT',
        zCldFeedEnt.Z_OPT AS 'zCldFeedEnt-zOPT',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID',
        zCldSharedComment.Z_PK AS 'zCldSharedComment-zPK',
        zCldSharedComment.Z_ENT AS 'zCldSharedComment-zENT',
        zCldSharedComment.Z_OPT AS 'zCldSharedComment-zOPT',
        zCldSharedComment.ZCOMMENTEDASSET AS 'zCldSharedComment-Commented Asset Key= zAsset-zPK',
        zCldSharedComment.ZCLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK',
        zCldSharedComment.Z_FOK_CLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key',
        zCldSharedCommentLiked.ZLIKEDASSET AS 'zCldSharedComment-Liked Asset Key= zAsset-zPK',
        zCldSharedCommentLiked.ZCLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-CldFeedLikeCommentEntry Key',
        zCldSharedCommentLiked.Z_FOK_CLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID',       
        zKeywrd.Z_PK AS 'zKeywrd-zPK',
        z1KeyWrds.Z_40KEYWORDS AS 'z1KeyWrds-40Keywords = zKeywrd-zPK',
        zKeywrd.Z_ENT AS 'zKeywrd-zENT',
        zKeywrd.Z_OPT AS 'zKeywrd-zOPT',       
        zKeywrd.ZUUID AS 'zKeywrd-UUID',
        z1KeyWrds.Z_1ASSETATTRIBUTES AS 'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK',
        zAsset.Z_PK AS 'zAsset-zPK',      
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_1KEYWORDS z1KeyWrds ON zAddAssetAttr.Z_PK = z1KeyWrds.Z_1ASSETATTRIBUTES
            LEFT JOIN ZKEYWORD zKeywrd ON z1KeyWrds.Z_40KEYWORDS = zKeywrd.Z_PK
            LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
            LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
        WHERE (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or (zCldSharedCommentLiked.ZISLIKE = 1)
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
                                    row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                    row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                    row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                    row[73], row[74], row[75], row[76], row[77]))

                counter += 1

            description = ('Parses basic asset record data from iOS16-17 *PhotoData-Photos.sqlite for assets that have'
                           ' Keywords, Captions, Titles, Descriptions, Captions and Likes.'
                           ' (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or'
                           ' (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or'
                           ' (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or'
                           ' (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or'
                           ' (zCldSharedCommentLiked.ZISLIKE = 1). I recommend opening the TSV generated report'
                           ' with Zimmermans Tools https://ericzimmerman.github.io/#!index.md TimelineExplorer to view,'
                           ' search and filter the results. This parser is based on research and SQLite Queries'
                           ' written by Scott Koenig https://theforensicscooter.com/')
            report = ArtifactHtmlReport('Ph11 Keywords Captions Titles Descriptions Likes and Basic Asset Data')
            report.start_artifact_report(report_folder, 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-EXIF-String-5',
                            'zAsset-Modification Date-6',
                            'zAsset-Last Shared Date-7',
                            'zAsset-Trashed Date-8',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-9',
                            'zAsset-Directory-Path-10',
                            'zAsset-Filename-11',
                            'zAddAssetAttr- Original Filename-12',
                            'zCldMast- Original Filename-13',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                            'zAddAssetAttr- Imported by Bundle Identifier-15',
                            'zAddAssetAttr- Imported By Display Name-16',
                            'zAsset-Saved Asset Type-17',
                            'zAsset-Syndication State-18',
                            'zAsset-Bundle Scope-19',
                            'zAddAssetAttr-Share Type-20',
                            'zAsset-Active Library Scope Participation State-21',
                            'zAsset-Visibility State-22',
                            'zAssetDes-Long Description-23',
                            'zAddAssetAttr-Title-Comments via Cloud Website-24',
                            'zAddAssetAttr-Accessibility Description-25',
                            'zKeywrd-Shortcut-26',
                            'zKeywrd-Title-27',
                            'zCldSharedComment-Type-28',
                            'zCldSharedComment-Comment Text-29',
                            'zCldFeedEnt-Entry Date-30',
                            'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-31',
                            'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-32',
                            'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-33',
                            'zCldFeedEnt-Entry Priority Number-34',
                            'zCldFeedEnt-Entry Type Number-35',
                            'zCldSharedComment-Cloud GUID-4TableStart-36',
                            'zCldSharedComment-Date-37',
                            'zCldSharedComment-Comment Client Date-38',
                            'zAsset-Cloud Last Viewed Comment Date-39',
                            'zCldSharedComment-Commenter Hashed Person ID-40',
                            'zCldSharedComment-Batch Comment-41',
                            'zCldSharedComment-Is a Caption-42',
                            'zAsset-Cloud Has Comments by Me-43',
                            'zCldSharedComment-Is My Comment-44',
                            'zCldSharedComment-Is Deletable-45',
                            'zAsset-Cloud Has Comments Conversation-46',
                            'zAsset-Cloud Has Unseen Comments-47',
                            'zCldSharedComment-Liked-48',
                            'zAddAssetAttr-Asset Description-49',
                            'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-50',
                            'zAsset-FOK-Cloud Feed Asset Entry Key-51',
                            'zCldFeedEnt-zPK= zCldShared keys-52',
                            'zCldFeedEnt-zENT-53',
                            'zCldFeedEnt-zOPT-54',
                            'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-55',
                            'zCldFeedEnt-Entry Invitation Record GUID-56',
                            'zCldFeedEnt-Entry Cloud Asset GUID-57',
                            'zCldSharedComment-zPK-58',
                            'zCldSharedComment-zENT-59',
                            'zCldSharedComment-zOPT-60',
                            'zCldSharedComment-Commented Asset Key= zAsset-zPK-61',
                            'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-62',
                            'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-63',
                            'zCldSharedComment-Liked Asset Key= zAsset-zPK-64',
                            'zCldSharedComment-CldFeedLikeCommentEntry Key-65',
                            'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-66',
                            'zCldSharedComment-Cloud GUID-67',
                            'zKeywrd-zPK-68',
                            'z1KeyWrds-40Keywords = zKeywrd-zPK-69',
                            'zKeywrd-zENT-70',
                            'zKeywrd-zOPT-71',
                            'zKeywrd-UUID-72',
                            'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK-73',
                            'zAsset-zPK-74',
                            'zAddAssetAttr-zPK-75',
                            'zAsset-UUID = store.cloudphotodb-76',
                            'zAddAssetAttr-Master Fingerprint-77')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc('No data available for iOS16-17 Photos.sqlite Keywords Captions Titles Descriptions Basic Asst Data')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("18"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZISRECENTLYSAVED
            WHEN 0 THEN '0-Not_Recently_Saved iOS18_Still_Testing-0'
            WHEN 1 THEN '1-Recently_Saved iOS18_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZISRECENTLYSAVED || ''
        END AS 'zAsset-Is_Recently_Saved-iOS18',
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
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',       
        zAssetDes.ZLONGDESCRIPTION AS 'zAssetDes-Long Description',
        zAddAssetAttr.ZTITLE AS 'zAddAssetAttr-Title-Comments via Cloud Website',
        zAddAssetAttr.ZACCESSIBILITYDESCRIPTION AS 'zAddAssetAttr-Accessibility Description',
        zKeywrd.ZSHORTCUT AS 'zKeywrd-Shortcut',
        zKeywrd.ZTITLE AS 'zKeywrd-Title',
        zGeneratedAsstDescrip.ZANALYSISVERSION AS 'zGeneratedAsstDescrip-Analysis_Version',
        zGeneratedAsstDescrip.ZANALYSISSOURCETYPE AS 'zGeneratedAsstDescrip-Analysis_Source_Type',
        DateTime(zGeneratedAsstDescrip.ZANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH') AS 'zGeneratedAsstDescrip-Analysis_Timestamp',
        zGeneratedAsstDescrip.ZDESCRIPTIONTEXT AS 'zGeneratedAsstDescrip-Description-Text',
        zCldSharedComment.ZCOMMENTTYPE AS 'zCldSharedComment-Type',
        zCldSharedComment.ZCOMMENTTEXT AS 'zCldSharedComment-Comment Text',       
        DateTime(zCldFeedEnt.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS 'zCldFeedEnt-Entry Date',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID-4TableStart',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart',
        CASE zCldFeedEnt.ZENTRYPRIORITYNUMBER
            WHEN 0 THEN '0-StillTesting'
            WHEN 1 THEN '1-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYPRIORITYNUMBER || ''
        END AS 'zCldFeedEnt-Entry Priority Number',
        CASE zCldFeedEnt.ZENTRYTYPENUMBER
            WHEN 1 THEN 'Is My Shared Asset-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-StillTesting-3'
            WHEN 4 THEN 'Not My Shared Asset-4'
            WHEN 5 THEN 'Asset in Album with Invite Record-5'
            ELSE 'Unknown-New-Value!: ' || zCldFeedEnt.ZENTRYTYPENUMBER || ''
        END AS 'zCldFeedEnt-Entry Type Number',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID-4TableStart',
        DateTime(zCldSharedComment.ZCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Date',
        DateTime(zCldSharedComment.ZCOMMENTCLIENTDATE + 978307200, 'UNIXEPOCH') AS 'zCldSharedComment-Comment Client Date',
        DateTime(zAsset.ZCLOUDLASTVIEWEDCOMMENTDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Cloud Last Viewed Comment Date',		
        zCldSharedComment.ZCOMMENTERHASHEDPERSONID AS 'zCldSharedComment-Commenter Hashed Person ID',
        CASE zCldSharedComment.ZISBATCHCOMMENT
            WHEN 0 THEN 'Not Batch Comment-0'
            WHEN 1 THEN 'Batch Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISBATCHCOMMENT || ''
        END AS 'zCldSharedComment-Batch Comment',
        CASE zCldSharedComment.ZISCAPTION
            WHEN 0 THEN 'Not a Caption-0'
            WHEN 1 THEN 'Caption-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISCAPTION || ''
        END AS 'zCldSharedComment-Is a Caption',
        CASE zAsset.ZCLOUDHASCOMMENTSBYME
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Asset-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSBYME || ''
        END AS 'zAsset-Cloud Has Comments by Me',
        CASE zCldSharedComment.ZISMYCOMMENT
            WHEN 0 THEN 'Not My Comment-0'
            WHEN 1 THEN 'My Comment-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISMYCOMMENT || ''
        END AS 'zCldSharedComment-Is My Comment',
        CASE zCldSharedComment.ZISDELETABLE
            WHEN 0 THEN 'Not Deletable-0'
            WHEN 1 THEN 'Deletable-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedComment.ZISDELETABLE || ''
        END AS 'zCldSharedComment-Is Deletable',
        CASE zAsset.ZCLOUDHASCOMMENTSCONVERSATION
            WHEN 1 THEN 'Device Apple Acnt Commented-Liked Conversation-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASCOMMENTSCONVERSATION || ''
        END AS 'zAsset-Cloud Has Comments Conversation',
        CASE zAsset.ZCLOUDHASUNSEENCOMMENTS
            WHEN 0 THEN 'zAsset No Unseen Comments-0'
            WHEN 1 THEN 'zAsset Unseen Comments-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZCLOUDHASUNSEENCOMMENTS || ''
        END AS 'zAsset-Cloud Has Unseen Comments',
        CASE zCldSharedCommentLiked.ZISLIKE
            WHEN 0 THEN 'Asset Not Liked-0'
            WHEN 1 THEN 'Asset Liked-1'
            ELSE 'Unknown-New-Value!: ' || zCldSharedCommentLiked.ZISLIKE || ''
        END AS 'zCldSharedComment-Liked',       
        zAddAssetAttr.ZASSETDESCRIPTION AS 'zAddAssetAttr-Asset Description',
        zAsset.ZCLOUDFEEDASSETSENTRY AS 'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK',
        zAsset.Z_FOK_CLOUDFEEDASSETSENTRY AS 'zAsset-FOK-Cloud Feed Asset Entry Key',
        zCldFeedEnt.Z_PK AS 'zCldFeedEnt-zPK= zCldShared keys',
        zCldFeedEnt.Z_ENT AS 'zCldFeedEnt-zENT',
        zCldFeedEnt.Z_OPT AS 'zCldFeedEnt-zOPT',
        zCldFeedEnt.ZENTRYALBUMGUID AS 'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID',
        zCldFeedEnt.ZENTRYINVITATIONRECORDGUID AS 'zCldFeedEnt-Entry Invitation Record GUID',
        zCldFeedEnt.ZENTRYCLOUDASSETGUID AS 'zCldFeedEnt-Entry Cloud Asset GUID',
        zCldSharedComment.Z_PK AS 'zCldSharedComment-zPK',
        zCldSharedComment.Z_ENT AS 'zCldSharedComment-zENT',
        zCldSharedComment.Z_OPT AS 'zCldSharedComment-zOPT',
        zCldSharedComment.ZCOMMENTEDASSET AS 'zCldSharedComment-Commented Asset Key= zAsset-zPK',
        zCldSharedComment.ZCLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK',
        zCldSharedComment.Z_FOK_CLOUDFEEDCOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key',
        zCldSharedCommentLiked.ZLIKEDASSET AS 'zCldSharedComment-Liked Asset Key= zAsset-zPK',
        zCldSharedCommentLiked.ZCLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-CldFeedLikeCommentEntry Key',
        zCldSharedCommentLiked.Z_FOK_CLOUDFEEDLIKECOMMENTENTRY AS 'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key',
        zCldSharedComment.ZCLOUDGUID AS 'zCldSharedComment-Cloud GUID',       
        zKeywrd.Z_PK AS 'zKeywrd-zPK',
        z1KeyWrds.Z_48KEYWORDS AS 'z1KeyWrds-48Keywords = zKeywrd-zPK',
        zKeywrd.Z_ENT AS 'zKeywrd-zENT',
        zKeywrd.Z_OPT AS 'zKeywrd-zOPT',       
        zKeywrd.ZUUID AS 'zKeywrd-UUID',
        z1KeyWrds.Z_1ASSETATTRIBUTES AS 'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK',
        zGeneratedAsstDescrip.ZASSET AS 'zGeneratedAsstDescrip-zAsset= zAsset-zPK',
        zAsset.ZGENERATEDASSETDESCRIPTION AS 'zAsset-Generated Asset Description= zGeneratedAsstDescrip-zPK', 
        zGeneratedAsstDescrip.Z_PK AS 'zGeneratedAsstDescrip-zPK = zAsset-Generated Asset Description',
        zGeneratedAsstDescrip.Z_ENT AS 'zGeneratedAsstDescrip-zENT',
        zGeneratedAsstDescrip.Z_OPT AS 'zGeneratedAsstDescrip-zOPT',
        zAsset.Z_PK AS 'zAsset-zPK',      
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash-iOS18'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_1KEYWORDS z1KeyWrds ON zAddAssetAttr.Z_PK = z1KeyWrds.Z_1ASSETATTRIBUTES
            LEFT JOIN ZKEYWORD zKeywrd ON z1KeyWrds.Z_48KEYWORDS = zKeywrd.Z_PK
            LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
            LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
            LEFT JOIN ZGENERATEDASSETDESCRIPTION zGeneratedAsstDescrip ON zAsset.ZGENERATEDASSETDESCRIPTION = zGeneratedAsstDescrip.Z_PK
        WHERE (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or (zCldSharedCommentLiked.ZISLIKE = 1) or (zGeneratedAsstDescrip.ZDESCRIPTIONTEXT > 0)
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
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77], row[78], row[79], row[80], row[81],
                                row[82], row[83], row[84], row[85], row[86], row[87], row[88]))

                counter += 1

            description = ('Parses basic asset record data from iOS18 *PhotoData-Photos.sqlite for assets that have'
                           ' Keywords, Captions, Titles, Descriptions, Captions and Likes.'
                           ' (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or'
                           ' (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or'
                           ' (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or'
                           ' (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or'
                           ' (zCldSharedCommentLiked.ZISLIKE = 1). I recommend opening the TSV generated report'
                           ' with Zimmermans Tools https://ericzimmerman.github.io/#!index.md TimelineExplorer to view,'
                           ' search and filter the results. This parser is based on research and SQLite Queries'
                           ' written by Scott Koenig https://theforensicscooter.com/')
            report = ArtifactHtmlReport('Ph11 Keywords Captions Titles Descriptions Likes and Basic Asset Data')
            report.start_artifact_report(report_folder, 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset- SortToken -CameraRoll-1',
                            'zAsset-Added Date-2',
                            'zCldMast-Creation Date-3',
                            'zAddAssetAttr-Time Zone Name-4',
                            'zAddAssetAttr-EXIF-String-5',
                            'zAsset-Modification Date-6',
                            'zAsset-Last Shared Date-7',
                            'zAsset-Trashed Date-8',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-9',
                            'zAsset-Directory-Path-10',
                            'zAsset-Filename-11',
                            'zAddAssetAttr- Original Filename-12',
                            'zCldMast- Original Filename-13',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                            'zAddAssetAttr- Imported by Bundle Identifier-15',
                            'zAddAssetAttr- Imported By Display Name-16',
                            'zAsset-Is_Recently_Saved-iOS18-17',
                            'zAsset-Saved Asset Type-18',
                            'zAsset-Syndication State-19',
                            'zAsset-Bundle Scope-20',
                            'zAddAssetAttr-Share Type-21',
                            'zAsset-Active Library Scope Participation State-22',
                            'zAsset-Visibility State-23',
                            'zAssetDes-Long Description-24',
                            'zAddAssetAttr-Title-Comments via Cloud Website-25',
                            'zAddAssetAttr-Accessibility Description-26',
                            'zKeywrd-Shortcut-27',
                            'zKeywrd-Title-28',
                            'zGeneratedAsstDescrip-Analysis_Version-29',
                            'zGeneratedAsstDescrip-Analysis_Source_Type-30',
                            'zGeneratedAsstDescrip-Analysis_Timestamp-31',
                            'zGeneratedAsstDescrip-Description-Text-32',
                            'zCldSharedComment-Type-33',
                            'zCldSharedComment-Comment Text-34',
                            'zCldFeedEnt-Entry Date-35',
                            'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-36',
                            'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-37',
                            'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-38',
                            'zCldFeedEnt-Entry Priority Number-39',
                            'zCldFeedEnt-Entry Type Number-40',
                            'zCldSharedComment-Cloud GUID-4TableStart-41',
                            'zCldSharedComment-Date-42',
                            'zCldSharedComment-Comment Client Date-43',
                            'zAsset-Cloud Last Viewed Comment Date-44',
                            'zCldSharedComment-Commenter Hashed Person ID-45',
                            'zCldSharedComment-Batch Comment-46',
                            'zCldSharedComment-Is a Caption-47',
                            'zAsset-Cloud Has Comments by Me-48',
                            'zCldSharedComment-Is My Comment-49',
                            'zCldSharedComment-Is Deletable-50',
                            'zAsset-Cloud Has Comments Conversation-51',
                            'zAsset-Cloud Has Unseen Comments-52',
                            'zCldSharedComment-Liked-53',
                            'zAddAssetAttr-Asset Description-54',
                            'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-55',
                            'zAsset-FOK-Cloud Feed Asset Entry Key-56',
                            'zCldFeedEnt-zPK= zCldShared keys-57',
                            'zCldFeedEnt-zENT-58',
                            'zCldFeedEnt-zOPT-59',
                            'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-60',
                            'zCldFeedEnt-Entry Invitation Record GUID-61',
                            'zCldFeedEnt-Entry Cloud Asset GUID-62',
                            'zCldSharedComment-zPK-63',
                            'zCldSharedComment-zENT-64',
                            'zCldSharedComment-zOPT-65',
                            'zCldSharedComment-Commented Asset Key= zAsset-zPK-66',
                            'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-67',
                            'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-68',
                            'zCldSharedComment-Liked Asset Key= zAsset-zPK-69',
                            'zCldSharedComment-CldFeedLikeCommentEntry Key-70',
                            'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-71',
                            'zCldSharedComment-Cloud GUID-72',
                            'zKeywrd-zPK-73',
                            'z1KeyWrds-48Keywords = zKeywrd-zPK-74',
                            'zKeywrd-zENT-75',
                            'zKeywrd-zOPT-76',
                            'zKeywrd-UUID-77',
                            'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK-78',
                            'zGeneratedAsstDescrip-zAsset= zAsset-zPK-79',
                            'zAsset-Generated Asset Description= zGeneratedAsstDescrip-zPK-80',
                            'zGeneratedAsstDescrip-zPK = zAsset-Generated Asset Description-81',
                            'zGeneratedAsstDescrip-zENT-82',
                            'zGeneratedAsstDescrip-zOPT-83',
                            'zAsset-zPK-84',
                            'zAddAssetAttr-zPK-85',
                            'zAsset-UUID = store.cloudphotodb-86',
                            'zAddAssetAttr-Original Stable Hash-iOS18-87',
                            'zAddAssetAttr.Adjusted Stable Hash-iOS18-88')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc('No data available for iOS 18 Photos.sqlite basic asset data one record per zAsset-zPK')

        db.close()
        return


__artifacts_v2__ = {
    'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite Ph11 Keywords Captions Titles Descriptions Likes and Basic Asset Data',
        'description': 'Parses basic asset record data from iOS18 *PhotoData-Photos.sqlite for assets that have'
                       ' Keywords, Captions, Titles, Descriptions, Captions and Likes.'
                       ' (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or'
                       ' (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or'
                       ' (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or'
                       ' (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or'
                       ' (zCldSharedCommentLiked.ZISLIKE = 1). I recommend opening the TSV generated report'
                       ' with Zimmermans Tools https://ericzimmerman.github.io/#!index.md TimelineExplorer to view,'
                       ' search and filter the results. This parser is based on research and SQLite Queries'
                       ' written by Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-20',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': '*/PhotoData/Photos.sqlite*',
        'function': 'get_ph11kwrdscapstitlesdescripsbasicassetdataphdapsql'
    }
}
