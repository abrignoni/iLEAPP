__artifacts_v2__ = {
    'Ph11KwrdsCapsTitlesDescripsLikesBasicAsstDataPhDaPsql': {
        'name': 'Ph11-KwrdsCapsTitlesDescripsLikesBasicAsstData-PhDaPsql',
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
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-B-Interaction_Artifacts',
        'notes': '',
        'paths': ('*/PhotoData/Photos.sqlite*',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, get_file_path, open_sqlite_db_readonly, get_sqlite_db_records, logfunc

@artifact_processor
def Ph11KwrdsCapsTitlesDescripsLikesBasicAsstDataPhDaPsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for source_path in files_found:
        source_path = str(source_path)

        if source_path.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("13.7"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite iOS " + iosversion)
        return (), [], source_path
    if (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
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
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-EXIF-String-5',
                        ('zAsset-Modification Date-6', 'datetime'),
                        ('zAsset-Last Shared Date-7', 'datetime'),
                        ('zAsset-Trashed Date-8', 'datetime'),
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
                        ('zCldFeedEnt-Entry Date-23', 'datetime'),
                        'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-24',
                        'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-25',
                        'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-26',
                        'zCldFeedEnt-Entry Priority Number-27',
                        'zCldFeedEnt-Entry Type Number-28',
                        'zCldSharedComment-Cloud GUID-4TableStart-29',
                        ('zCldSharedComment-Date-30', 'datetime'),
                        ('zCldSharedComment-Comment Client Date-31', 'datetime'),
                        ('zAsset-Cloud Last Viewed Comment Date-32', 'datetime'),
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
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
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
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-EXIF-String-5',
                        ('zAsset-Modification Date-6', 'datetime'),
                        ('zAsset-Last Shared Date-7', 'datetime'),
                        ('zAsset-Trashed Date-8', 'datetime'),
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
                        ('zCldFeedEnt-Entry Date-28', 'datetime'),
                        'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-29',
                        'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-30',
                        'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-31',
                        'zCldFeedEnt-Entry Priority Number-32',
                        'zCldFeedEnt-Entry Type Number-33',
                        'zCldSharedComment-Cloud GUID-4TableStart-34',
                        ('zCldSharedComment-Date-35', 'datetime'),
                        ('zCldSharedComment-Comment Client Date-36', 'datetime'),
                        ('zAsset-Cloud Last Viewed Comment Date-37', 'datetime'),
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
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("17.6")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
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
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-EXIF-String-5',
                        ('zAsset-Modification Date-6', 'datetime'),
                        ('zAsset-Last Shared Date-7', 'datetime'),
                        ('zAsset-Trashed Date-8', 'datetime'),
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
                        ('zCldSharedComment-Date-37', 'datetime'),
                        ('zCldSharedComment-Comment Client Date-38', 'datetime'),
                        ('zAsset-Cloud Last Viewed Comment Date-39', 'datetime'),
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
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
	
    elif (version.parse(iosversion) >= version.parse("17.6")) & (version.parse(iosversion) < version.parse("18")):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
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
        z1KeyWrds.Z_41KEYWORDS AS 'z1KeyWrds-41Keywords = zKeywrd-zPK',
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
            LEFT JOIN ZKEYWORD zKeywrd ON z1KeyWrds.Z_41KEYWORDS = zKeywrd.Z_PK
            LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
            LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
        WHERE (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or (zCldSharedCommentLiked.ZISLIKE = 1)
        ORDER BY zAsset.ZDATECREATED        
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                row[73], row[74], row[75], row[76], row[77]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-EXIF-String-5',
                        ('zAsset-Modification Date-6', 'datetime'),
                        ('zAsset-Last Shared Date-7', 'datetime'),
                        ('zAsset-Trashed Date-8', 'datetime'),
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
                        ('zCldFeedEnt-Entry Date-30', 'datetime'),
                        'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-31',
                        'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-32',
                        'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-33',
                        'zCldFeedEnt-Entry Priority Number-34',
                        'zCldFeedEnt-Entry Type Number-35',
                        'zCldSharedComment-Cloud GUID-4TableStart-36',
                        ('zCldSharedComment-Date-37', 'datetime'),
                        ('zCldSharedComment-Comment Client Date-38', 'datetime'),
                        ('zAsset-Cloud Last Viewed Comment Date-39', 'datetime'),
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
                        'z1KeyWrds-41Keywords = zKeywrd-zPK-69',
                        'zKeywrd-zENT-70',
                        'zKeywrd-zOPT-71',
                        'zKeywrd-UUID-72',
                        'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK-73',
                        'zAsset-zPK-74',
                        'zAddAssetAttr-zPK-75',
                        'zAsset-UUID = store.cloudphotodb-76',
                        'zAddAssetAttr-Master Fingerprint-77')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path

    elif version.parse(iosversion) >= version.parse("18"):
        source_path = get_file_path(files_found,"Photos.sqlite")
        if source_path is None or not os.path.exists(source_path):
            logfunc(f"Photos.sqlite not found for iOS version {iosversion}")
            return (), [], source_path
        data_list = []

        query = '''
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
			WHEN 0 THEN '0-Not_Recently_Saved-0'
			WHEN 1 THEN '1-Recently_Saved-1'
			ELSE 'Unknown-New-Value!: ' || zAsset.ZISRECENTLYSAVED || ''
		END AS 'zAsset-Is_Recently_Saved',
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
        z1KeyWrds.Z_47KEYWORDS AS 'z1KeyWrds-47Keywords = zKeywrd-zPK',
        zKeywrd.Z_ENT AS 'zKeywrd-zENT',
        zKeywrd.Z_OPT AS 'zKeywrd-zOPT',       
        zKeywrd.ZUUID AS 'zKeywrd-UUID',
        z1KeyWrds.Z_1ASSETATTRIBUTES AS 'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK',
        zAsset.Z_PK AS 'zAsset-zPK',      
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
            LEFT JOIN Z_1KEYWORDS z1KeyWrds ON zAddAssetAttr.Z_PK = z1KeyWrds.Z_1ASSETATTRIBUTES
            LEFT JOIN ZKEYWORD zKeywrd ON z1KeyWrds.Z_47KEYWORDS = zKeywrd.Z_PK
            LEFT JOIN ZASSETDESCRIPTION zAssetDes ON zAssetDes.Z_PK = zAddAssetAttr.ZASSETDESCRIPTION
            LEFT JOIN ZCLOUDFEEDENTRY zCldFeedEnt ON zAsset.ZCLOUDFEEDASSETSENTRY = zCldFeedEnt.Z_PK
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedComment ON zAsset.Z_PK = zCldSharedComment.ZCOMMENTEDASSET
            LEFT JOIN ZCLOUDSHAREDCOMMENT zCldSharedCommentLiked ON zAsset.Z_PK = zCldSharedCommentLiked.ZLIKEDASSET
        WHERE (zAssetDes.ZLONGDESCRIPTION > 0) or (zAddAssetAttr.ZTITLE > 0) or (zAddAssetAttr.ZACCESSIBILITYDESCRIPTION > 0) or (zKeywrd.ZSHORTCUT > 0) or (zKeywrd.ZTITLE > 0) or (zCldSharedComment.ZCOMMENTTYPE > 0) or (zCldSharedComment.ZCOMMENTTEXT > 0) or (zCldSharedCommentLiked.ZISLIKE = 1)
        ORDER BY zAsset.ZDATECREATED       
        '''

        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                            row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                            row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                            row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                            row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                            row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                            row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                            row[73], row[74], row[75], row[76], row[77], row[78], row[79]))

        data_headers = (('zAsset-Date Created-0', 'datetime'),
                        ('zAsset- SortToken -CameraRoll-1', 'datetime'),
                        ('zAsset-Added Date-2', 'datetime'),
                        ('zCldMast-Creation Date-3', 'datetime'),
                        'zAddAssetAttr-Time Zone Name-4',
                        'zAddAssetAttr-EXIF-String-5',
                        ('zAsset-Modification Date-6', 'datetime'),
                        ('zAsset-Last Shared Date-7', 'datetime'),
                        ('zAsset-Trashed Date-8', 'datetime'),
                        'zAsset-Trashed by Participant= zShareParticipant_zPK-9',
                        'zAsset-Directory-Path-10',
                        'zAsset-Filename-11',
                        'zAddAssetAttr- Original Filename-12',
                        'zCldMast- Original Filename-13',
                        'zAddAssetAttr- Syndication Identifier-SWY-Files-14',
                        'zAddAssetAttr- Imported by Bundle Identifier-15',
                        'zAddAssetAttr- Imported By Display Name-16',
                        'zAsset-Is_Recently_Saved-17',
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
                        'zCldSharedComment-Type-29',
                        'zCldSharedComment-Comment Text-30',
                        ('zCldFeedEnt-Entry Date-31', 'datetime'),
                        'zCldFeedEnt-Album-GUID=zGenAlbum.zCloudGUID-4TableStart-32',
                        'zCldFeedEnt-Entry Invitation Record GUID-4TableStart-33',
                        'zCldFeedEnt-Entry Cloud Asset GUID-4TableStart-34',
                        'zCldFeedEnt-Entry Priority Number-35',
                        'zCldFeedEnt-Entry Type Number-36',
                        'zCldSharedComment-Cloud GUID-4TableStart-37',
                        ('zCldSharedComment-Date-38', 'datetime'),
                        ('zCldSharedComment-Comment Client Date-39', 'datetime'),
                        ('zAsset-Cloud Last Viewed Comment Date-40', 'datetime'),
                        'zCldSharedComment-Commenter Hashed Person ID-41',
                        'zCldSharedComment-Batch Comment-42',
                        'zCldSharedComment-Is a Caption-43',
                        'zAsset-Cloud Has Comments by Me-44',
                        'zCldSharedComment-Is My Comment-45',
                        'zCldSharedComment-Is Deletable-46',
                        'zAsset-Cloud Has Comments Conversation-47',
                        'zAsset-Cloud Has Unseen Comments-48',
                        'zCldSharedComment-Liked-49',
                        'zAddAssetAttr-Asset Description-50',
                        'zAsset-Cloud Feed Assets Entry= zCldFeedEnt.zPK-51',
                        'zAsset-FOK-Cloud Feed Asset Entry Key-52',
                        'zCldFeedEnt-zPK= zCldShared keys-53',
                        'zCldFeedEnt-zENT-54',
                        'zCldFeedEnt-zOPT-55',
                        'zCldFeedEnt-Album-GUID= zGenAlbum.zCloudGUID-56',
                        'zCldFeedEnt-Entry Invitation Record GUID-57',
                        'zCldFeedEnt-Entry Cloud Asset GUID-58',
                        'zCldSharedComment-zPK-59',
                        'zCldSharedComment-zENT-60',
                        'zCldSharedComment-zOPT-61',
                        'zCldSharedComment-Commented Asset Key= zAsset-zPK-62',
                        'zCldSharedComment-CldFeedCommentEntry= zCldFeedEnt.zPK-63',
                        'zCldSharedComment-FOK-Cld-Feed-Comment-Entry-Key-64',
                        'zCldSharedComment-Liked Asset Key= zAsset-zPK-65',
                        'zCldSharedComment-CldFeedLikeCommentEntry Key-66',
                        'zCldSharedComment-FOK-Cld-Feed-Like-Comment-Entry-Key-67',
                        'zCldSharedComment-Cloud GUID-68',
                        'zKeywrd-zPK-69',
                        'z1KeyWrds-47Keywords = zKeywrd-zPK-70',
                        'zKeywrd-zENT-71',
                        'zKeywrd-zOPT-72',
                        'zKeywrd-UUID-73',
                        'z1KeyWrds-1AssetAttributes = zAddAssetAttr-zPK-74',
                        'zAsset-zPK-75',
                        'zAddAssetAttr-zPK-76',
                        'zAsset-UUID = store.cloudphotodb-77',
                        'zAddAssetAttr-Original Stable Hash-78',
                        'zAddAssetAttr.Adjusted Stable Hash-79')
        data_list = get_sqlite_db_records(source_path, query)

        return data_headers, data_list, source_path
