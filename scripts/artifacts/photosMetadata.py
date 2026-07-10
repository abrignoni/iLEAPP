__artifacts_v2__ = {
    "photosMetadata": {
        "name": "Photos.sqlite Metadata",
        "description": "Comprehensive asset metadata from Photos.sqlite (per iOS version): "
                       "timestamps, location/reverse-geocode, faces, moments, fingerprints and more.",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Photos",
        "notes": "Schema varies by iOS version; the matching query is selected automatically. "
                 "Reverse-location bplists are written to the report folder.",
        "paths": ('*/mobile/Media/PhotoData/Photos.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 381 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        }
    }
}

import os
import sqlite3

import nska_deserialize as nd
from packaging import version

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, get_sqlite_db_records,
                               iOS, logfunc, thumbnail_root)

_QUERY_IOS12 = """
        SELECT
        DateTime( ZGENERICASSET.ZDATECREATED + 978307200, 'UNIXEPOCH' ) AS 'DateCreated',
                        ZGENERICASSET.Z_PK AS 'GenericAsset_zpk',
                        ZGENERICASSET.ZADDITIONALATTRIBUTES AS 'AddAttributes_Key',
                        ZDETECTEDFACE.ZASSET AS 'DetectedFaceAsset',
                CASE
                                ZGENERICASSET.ZKIND
                                WHEN 0 THEN
                                'Photo'
                                WHEN 1 THEN
                                'Video'
                        END AS 'Kind',
        ZADDITIONALASSETATTRIBUTES.ZEXIFTIMESTAMPSTRING AS 'EXIFtimestamp',
        DateTime( ZADDITIONALASSETATTRIBUTES.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH' ) AS 'SceneAnalysisTimeStamp',
                        DateTime( ZGENERICASSET.ZADDEDDATE + 978307200, 'UNIXEPOCH' ) AS 'AddDate',
                        ZGENERICASSET.ZFILENAME AS 'FileName',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALFILENAME AS 'OriginalFilename',
         ZGENERICALBUM.ZTITLE AS 'AlbumTitle',
                        ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID AS 'CreatorBundleID',
                        ZADDITIONALASSETATTRIBUTES.ZEDITORBUNDLEID AS 'EditorBundleID',
                        ZGENERICASSET.ZDIRECTORY AS 'Directory',
                        ZGENERICASSET.ZUNIFORMTYPEIDENTIFIER AS 'UniformID',
                CASE
                                ZGENERICASSET.ZSAVEDASSETTYPE
                                WHEN 0 THEN
                                'Saved from other source'
                                WHEN 2 THEN
                                'Photo Streams Data'
                                WHEN 3 THEN
                                'Made/saved with this device'
                                WHEN 4 THEN
                                'Default row'
                                WHEN 7 THEN
                                'Deleted' ELSE ZGENERICASSET.ZSAVEDASSETTYPE
                        END AS 'SavedAssetType',
                CASE
                          WHEN ZGENERICASSET.ZFACEAREAPOINTS > 0 THEN 'Yes'
                          ELSE 'NA'
                        END AS 'FaceDetectedinPhoto',
                        ZPERSON.ZDISPLAYNAME AS 'DisplayName',
                        ZPERSON.ZFULLNAME AS 'FullName',
                        ZPERSON.ZFACECOUNT AS 'FaceCount',
                        ZDETECTEDFACE.ZPERSON AS 'Person',
                        ZPERSON.ZCONTACTMATCHINGDICTIONARY AS 'ContactBlob',
                        ZPERSON.ZPERSONUUID as 'PersonUUID',
                        ZDETECTEDFACE.ZQUALITYMEASURE AS 'DetectedFaceQuality',
                CASE
                                ZDETECTEDFACE.ZAGETYPE
                                WHEN 1 THEN
                                'Baby/Toddler'
                                WHEN 2 THEN
                                'Baby/Toddler'
                                WHEN 3 THEN
                                'Child/YoungAdult'
                                WHEN 4 THEN
                                'YoungAdult/Adult'
                                WHEN 5 THEN
                                'Adult'
                                ELSE ZDETECTEDFACE.ZAGETYPE
                        END AS 'AgeTypeEstimate',
                CASE
                                ZDETECTEDFACE.ZGENDERTYPE
                                WHEN 1 THEN
                                'Male'
                                WHEN 2 THEN
                                'Female'
                                ELSE ZDETECTEDFACE.ZGENDERTYPE
                        END AS 'Gender',
                CASE
                          ZDETECTEDFACE.ZGLASSESTYPE
                          WHEN 3 THEN
                          'None'
                          WHEN 2 THEN
                          'Sun'
                          WHEN 1 THEN
                          'Eye'
                          ELSE ZDETECTEDFACE.ZGLASSESTYPE
                        END AS 'GlassesType',
                CASE
                          ZDETECTEDFACE.ZFACIALHAIRTYPE
                          WHEN 1 THEN
                          'None'
                          WHEN 2 THEN
                          'Beard/Mustache'
                          WHEN 3 THEN
                          'Goatee'
                          WHEN 5 THEN
                          'Stubble'
                          ELSE ZDETECTEDFACE.ZFACIALHAIRTYPE
                        END AS 'FacialHairType',
                CASE
                          ZDETECTEDFACE.ZBALDTYPE
                          WHEN 2 THEN
                          'Bald'
                          WHEN 3 THEN
                          'NotBald'
                          ELSE ZDETECTEDFACE.ZBALDTYPE
                        END AS 'Baldness',
                        ZGENERICASSET.ZORIGINALCOLORSPACE AS 'ColorSpace',
                        ZGENERICASSET.Zduration AS 'Duration',
                        ZGENERICASSET.Zvideocpdurationvalue AS 'VideoDuration',
               CASE
                                ZGENERICASSET.ZCOMPLETE
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Complete',
                CASE
                                ZGENERICASSET.ZVISIBILITYSTATE
                                WHEN 0 THEN
                                'Visible'
                                WHEN 1 THEN
                                'Photo Streams Data'
                                WHEN 2 THEN
                                'Burst' ELSE ZVISIBILITYSTATE
                        END AS 'VisibilityState',
                CASE
                                ZGENERICASSET.ZFAVORITE
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Favorite',
                CASE
                                ZGENERICASSET.zhidden
                                WHEN 0 THEN
                                'Not_Hidden'
                                WHEN 1 THEN
                                'File_Hidden' ELSE ZGENERICASSET.zhidden
                        END AS 'Hidden_File',
                CASE
                                ZGENERICASSET.ZTRASHEDSTATE
                                WHEN 1 THEN
                                'In_Trash'
                                WHEN 0 THEN
                                'Not_In_Trash' ELSE ZGENERICASSET.ZTRASHEDSTATE
                        END AS 'TrashState',
                        DateTime( ZGENERICASSET.ZTRASHEDDATE + 978307200, 'UNIXEPOCH' ) AS 'FileTrashDate',
                        ZADDITIONALASSETATTRIBUTES.ZVIEWCOUNT AS 'ViewCount',
                        ZADDITIONALASSETATTRIBUTES.ZPLAYCOUNT AS 'PlayCount',
                        ZADDITIONALASSETATTRIBUTES.ZSHARECOUNT AS 'ShareCount',
                        DateTime( ZGENERICASSET.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH' ) AS 'LastSharedDate',
                        DateTime( ZGENERICASSET.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'FileModificationDate',
                CASE
                                ZGENERICASSET.ZHASADJUSTMENTS
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Has_Adjustments',
                        DateTime( ZGENERICASSET.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH' ) AS 'AdjustmentsTimeStamp',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALFILESIZE AS 'OriginalFileSize',
                        ZGENERICASSET.ZHEIGHT AS 'File_Height',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALHEIGHT AS 'OrgFileHeight',
                        ZGENERICASSET.ZWIDTH AS 'File_Width',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALWIDTH AS 'OrgFileWidth',
                CASE
                                ZGENERICASSET.ZORIENTATION
                                WHEN 1 THEN
                                'Horizontal (left)'
                                WHEN 3 THEN
                                'Horizontal (right)'
                                WHEN 6 THEN
                                'Vertical (up)'
                                WHEN 8 THEN
                                'Vertical (down)' ELSE ZORIENTATION
                        END AS 'Orientation',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZORIGINALORIENTATION
                                WHEN 1 THEN
                                'Horizontal (left)'
                                WHEN 3 THEN
                                'Horizontal (right)'
                                WHEN 6 THEN
                                'Vertical (up)'
                                WHEN 8 THEN
                                'Vertical (down)' ELSE ZORIENTATION
                        END AS 'Org_Orientation',
                        ZADDITIONALASSETATTRIBUTES.ZTIMEZONENAME AS 'TimeZoneName',
                        ZADDITIONALASSETATTRIBUTES.ZTIMEZONEOFFSET AS 'TimeZoneOffset',
                        ZGENERICASSET.ZLOCATIONDATA AS 'FileLocationData',
                CASE
                                ZGENERICASSET.ZLATITUDE
                                WHEN - 180.0 THEN
                                '' ELSE ZGENERICASSET.ZLATITUDE
                        END AS 'Latitude',
                CASE
                                ZGENERICASSET.ZLONGITUDE
                                WHEN - 180.0 THEN
                                '' ELSE ZGENERICASSET.ZLONGITUDE
                        END AS 'Longitude',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZSHIFTEDLOCATIONISVALID
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'ShiftedLocationValid',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZREVERSELOCATIONDATAISVALID
                                WHEN 0 THEN
                                'No_Check_SceneAnalysis'
                                WHEN 1 THEN
                                'Yes_Check_SceneAnalysis'
                        END AS 'ReverseLocationDataIsValid',
                        ZADDITIONALASSETATTRIBUTES.ZREVERSELOCATIONDATA AS 'OrgFileReverseLocationData',
                        ZGENERICASSET.Zthumbnailindex AS 'ThumbnailIndex',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILWIDTH AS 'EmbeddedThumbnailWidth',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILHEIGHT AS 'EmbeddedThumbnailHeight',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILOFFSET AS 'EmbeddedThumbnailOffset',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILLENGTH AS 'EmbeddedThumbnailLenght',
                        ZGENERICASSET.ZMOMENT AS 'MomentPK',
                        DateTime( ZMOMENT.ZSTARTDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentStartDate',
                        DateTime( ZMOMENT.Zrepresentativedate + 978307200, 'UNIXEPOCH' ) AS 'MomentRepresentativeDate',
                        DateTime( ZMOMENT.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentModificationDate',
                        DateTime( ZMOMENT.ZENDDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentEndDate',
                        ZMOMENT.ZTITLE AS 'MomentTitle',
                CASE
                                ZMOMENT.Zapproximatelatitude
                                WHEN - 180.0 THEN
                                '' ELSE ZMOMENT.Zapproximatelatitude
                        END AS 'MomentApproxLatitude',
                CASE
                                ZMOMENT.Zapproximatelongitude
                                WHEN - 180.0 THEN
                                '' ELSE ZMOMENT.Zapproximatelongitude
                        END AS 'MomentApproxLongitude',
                        ZGENERICASSET.ZUUID AS 'UUID',
                        ZGENERICASSET.ZMEDIAGROUPUUID AS 'MediaGroupUUID',
                        ZGENERICASSET.ZCLOUDASSETGUID AS 'CloudAssetGUID',
                        ZADDITIONALASSETATTRIBUTES.ZPUBLICGLOBALUUID AS 'PublicGlobalUUID',
                        ZADDITIONALASSETATTRIBUTES.ZMASTERFINGERPRINT AS 'MasterFingerprint',
                        ZADDITIONALASSETATTRIBUTES.ZADJUSTEDFINGERPRINT AS 'AdjustedFingerprint'
                FROM
                        ZGENERICASSET
                        JOIN Z_PRIMARYKEY ON ZGENERICASSET.z_ent = Z_PRIMARYKEY.z_ent
                        LEFT JOIN ZMOMENT ON ZGENERICASSET.ZMOMENT = ZMOMENT.Z_PK
                        JOIN ZADDITIONALASSETATTRIBUTES ON ZGENERICASSET.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK
                        LEFT JOIN ZDETECTEDFACE ON ZADDITIONALASSETATTRIBUTES.ZASSET = ZDETECTEDFACE.ZASSET
                        LEFT JOIN ZPERSON ON ZPERSON.Z_PK = ZDETECTEDFACE.ZPERSON
        LEFT JOIN Z_23ASSETS ON ZGENERICASSET.Z_PK = Z_23ASSETS.Z_30ASSETS
        LEFT JOIN ZGENERICALBUM ON ZGENERICALBUM.Z_PK = Z_23ASSETS.Z_23ALBUMS

"""

_QUERY_IOS13 = """
        SELECT
        DateTime( ZGENERICASSET.ZDATECREATED + 978307200, 'UNIXEPOCH' ) AS 'DateCreated',
                        ZGENERICASSET.Z_PK AS 'GenericAsset_zpk',
                        ZGENERICASSET.ZADDITIONALATTRIBUTES AS 'AddAttributes_Key',
                        ZDETECTEDFACE.ZASSET AS 'DetectedFaceAsset',
                CASE
                                ZGENERICASSET.ZKIND
                                WHEN 0 THEN
                                'Photo'
                                WHEN 1 THEN
                                'Video'
                        END AS 'Kind',
        ZADDITIONALASSETATTRIBUTES.ZEXIFTIMESTAMPSTRING AS 'EXIFtimestamp',
        DateTime( ZADDITIONALASSETATTRIBUTES.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH' ) AS 'SceneAnalysisTimeStamp',
                        DateTime( ZGENERICASSET.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'AnalysisStateModificationDate',
                        DateTime( ZGENERICASSET.ZADDEDDATE + 978307200, 'UNIXEPOCH' ) AS 'AddDate',
                        ZGENERICASSET.ZFILENAME AS 'FileName',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALFILENAME AS 'OriginalFilename',
        ZGENERICALBUM.ZTITLE AS 'AlbumTitle',
                        ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID AS 'CreatorBundleID',
                        ZADDITIONALASSETATTRIBUTES.ZEDITORBUNDLEID AS 'EditorBundleID',
                        ZGENERICASSET.ZDIRECTORY AS 'Directory',
                        ZGENERICASSET.ZUNIFORMTYPEIDENTIFIER AS 'UniformID',
                CASE
                                ZGENERICASSET.ZSAVEDASSETTYPE
                                WHEN 0 THEN
                                'Saved from other source'
                                WHEN 2 THEN
                                'Photo Streams Data'
                                WHEN 3 THEN
                                'Made/saved with this device'
                                WHEN 4 THEN
                                'Default row'
                                WHEN 7 THEN
                                'Deleted' ELSE ZGENERICASSET.ZSAVEDASSETTYPE
                        END AS 'SavedAssetType',
                CASE
                          WHEN ZGENERICASSET.ZFACEAREAPOINTS > 0 THEN 'Yes'
                          ELSE 'NA'
                        END AS 'FaceDetectedinPhoto',
                        ZPERSON.ZDISPLAYNAME AS 'DisplayName',
                        ZPERSON.ZFULLNAME AS 'FullName',
                        ZPERSON.ZFACECOUNT AS 'FaceCount',
                        ZDETECTEDFACE.ZPERSON AS 'Person',
                        ZPERSON.ZCONTACTMATCHINGDICTIONARY AS 'ContactBlob',
                        ZPERSON.ZPERSONUUID as 'PersonUUID',
                        ZDETECTEDFACE.ZQUALITYMEASURE AS 'DetectedFaceQuality',
                CASE
                                ZDETECTEDFACE.ZAGETYPE
                                WHEN 1 THEN
                                'Baby/Toddler'
                                WHEN 2 THEN
                                'Baby/Toddler'
                                WHEN 3 THEN
                                'Child/YoungAdult'
                                WHEN 4 THEN
                                'YoungAdult/Adult'
                                WHEN 5 THEN
                                'Adult'
                                ELSE ZDETECTEDFACE.ZAGETYPE
                        END AS 'AgeTypeEstimate',
                CASE
                                ZDETECTEDFACE.ZGENDERTYPE
                                WHEN 1 THEN
                                'Male'
                                WHEN 2 THEN
                                'Female'
                                ELSE ZDETECTEDFACE.ZGENDERTYPE
                        END AS 'Gender',
                CASE
                          ZDETECTEDFACE.ZGLASSESTYPE
                          WHEN 3 THEN
                          'None'
                          WHEN 2 THEN
                          'Sun'
                          WHEN 1 THEN
                          'Eye'
                          ELSE ZDETECTEDFACE.ZGLASSESTYPE
                        END AS 'GlassesType',
                CASE
                          ZDETECTEDFACE.ZFACIALHAIRTYPE
                          WHEN 1 THEN
                          'None'
                          WHEN 2 THEN
                          'Beard/Mustache'
                          WHEN 3 THEN
                          'Goatee'
                          WHEN 5 THEN
                          'Stubble'
                          ELSE ZDETECTEDFACE.ZFACIALHAIRTYPE
                        END AS 'FacialHairType',
                CASE
                          ZDETECTEDFACE.ZBALDTYPE
                          WHEN 2 THEN
                          'Bald'
                          WHEN 3 THEN
                          'NotBald'
                          ELSE ZDETECTEDFACE.ZBALDTYPE
                        END AS 'Baldness',
                        ZGENERICASSET.ZORIGINALCOLORSPACE AS 'ColorSpace',
                        ZGENERICASSET.Zduration AS 'Duration',
                        ZGENERICASSET.Zvideocpdurationvalue AS 'VideoDuration',
                CASE
                                ZGENERICASSET.ZCOMPLETE
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Complete',
                CASE
                                ZGENERICASSET.ZVISIBILITYSTATE
                                WHEN 0 THEN
                                'Visible'
                                WHEN 1 THEN
                                'Photo Streams Data'
                                WHEN 2 THEN
                                'Burst' ELSE ZVISIBILITYSTATE
                        END AS 'VisibilityState',
                CASE
                                ZGENERICASSET.ZFAVORITE
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Favorite',
                CASE
                                ZGENERICASSET.zhidden
                                WHEN 0 THEN
                                'Not_Hidden'
                                WHEN 1 THEN
                                'File_Hidden' ELSE ZGENERICASSET.zhidden
                        END AS 'Hidden_File',
                CASE
                                ZGENERICASSET.ZTRASHEDSTATE
                                WHEN 1 THEN
                                'In_Trash'
                                WHEN 0 THEN
                                'Not_In_Trash' ELSE ZGENERICASSET.ZTRASHEDSTATE
                        END AS 'TrashState',
                        DateTime( ZGENERICASSET.ZTRASHEDDATE + 978307200, 'UNIXEPOCH' ) AS 'FileTrashDate',
                        ZADDITIONALASSETATTRIBUTES.ZVIEWCOUNT AS 'ViewCount',
                        ZADDITIONALASSETATTRIBUTES.ZPLAYCOUNT AS 'PlayCount',
                        ZADDITIONALASSETATTRIBUTES.ZSHARECOUNT AS 'ShareCount',
                        DateTime( ZGENERICASSET.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH' ) AS 'LastSharedDate',
                        DateTime( ZGENERICASSET.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'FileModificationDate',
                CASE
                                ZGENERICASSET.ZHASADJUSTMENTS
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Has_Adjustments',
                        DateTime( ZGENERICASSET.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH' ) AS 'AdjustmentsTimeStamp',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALFILESIZE AS 'OriginalFileSize',
                        ZGENERICASSET.ZHEIGHT AS 'File_Height',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALHEIGHT AS 'OrgFileHeight',
                        ZGENERICASSET.ZWIDTH AS 'File_Width',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALWIDTH AS 'OrgFileWidth',
                CASE
                                ZGENERICASSET.ZORIENTATION
                                WHEN 1 THEN
                                'Horizontal (left)'
                                WHEN 3 THEN
                                'Horizontal (right)'
                                WHEN 6 THEN
                                'Vertical (up)'
                                WHEN 8 THEN
                                'Vertical (down)' ELSE ZORIENTATION
                        END AS 'Orientation',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZORIGINALORIENTATION
                                WHEN 1 THEN
                                'Horizontal (left)'
                                WHEN 3 THEN
                                'Horizontal (right)'
                                WHEN 6 THEN
                                'Vertical (up)'
                                WHEN 8 THEN
                                'Vertical (down)' ELSE ZORIENTATION
                        END AS 'Org_Orientation',
                        ZADDITIONALASSETATTRIBUTES.ZTIMEZONENAME AS 'TimeZoneName',
                        ZADDITIONALASSETATTRIBUTES.ZTIMEZONEOFFSET AS 'TimeZoneOffset',
                        ZADDITIONALASSETATTRIBUTES.ZINFERREDTIMEZONEOFFSET AS 'InferredTimeZoneOffset',
                        ZGENERICASSET.ZLOCATIONDATA AS 'FileLocationData',
                CASE
                                ZGENERICASSET.ZLATITUDE
                                WHEN - 180.0 THEN
                                '' ELSE ZGENERICASSET.ZLATITUDE
                        END AS 'Latitude',
                CASE
                                ZGENERICASSET.ZLONGITUDE
                                WHEN - 180.0 THEN
                                '' ELSE ZGENERICASSET.ZLONGITUDE
                        END AS 'Longitude',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZSHIFTEDLOCATIONISVALID
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'ShiftedLocationValid',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZREVERSELOCATIONDATAISVALID
                                WHEN 0 THEN
                                'No_Check_SceneAnalysis'
                                WHEN 1 THEN
                                'Yes_Check_SceneAnalysis'
                        END AS 'ReverseLocationDataIsValid',
                        ZADDITIONALASSETATTRIBUTES.ZREVERSELOCATIONDATA AS 'OrgFileReverseLocationData',
                        ZGENERICASSET.Zthumbnailindex AS 'ThumbnailIndex',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILWIDTH AS 'EmbeddedThumbnailWidth',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILHEIGHT AS 'EmbeddedThumbnailHeight',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILOFFSET AS 'EmbeddedThumbnailOffset',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILLENGTH AS 'EmbeddedThumbnailLenght',
                        ZGENERICASSET.ZMOMENT AS 'MomentPK',
                        DateTime( ZMOMENT.ZSTARTDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentStartDate',
                        DateTime( ZMOMENT.Zrepresentativedate + 978307200, 'UNIXEPOCH' ) AS 'MomentRepresentativeDate',
                        DateTime( ZMOMENT.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentModificationDate',
                        DateTime( ZMOMENT.ZENDDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentEndDate',
                        ZMOMENT.ZTITLE AS 'MomentTitle',
                CASE
                                ZMOMENT.Zapproximatelatitude
                                WHEN - 180.0 THEN
                                '' ELSE ZMOMENT.Zapproximatelatitude
                        END AS 'MomentApproxLatitude',
                CASE
                                ZMOMENT.Zapproximatelongitude
                                WHEN - 180.0 THEN
                                '' ELSE ZMOMENT.Zapproximatelongitude
                        END AS 'MomentApproxLongitude',
                        ZGENERICASSET.ZUUID AS 'UUID',
                        ZGENERICASSET.ZMEDIAGROUPUUID AS 'MediaGroupUUID',
                        ZGENERICASSET.ZCLOUDASSETGUID AS 'CloudAssetGUID',
                        ZADDITIONALASSETATTRIBUTES.ZPUBLICGLOBALUUID AS 'PublicGlobalUUID',
                        ZADDITIONALASSETATTRIBUTES.ZMASTERFINGERPRINT AS 'MasterFingerprint',
                        ZADDITIONALASSETATTRIBUTES.ZADJUSTEDFINGERPRINT AS 'AdjustedFingerprint'
                FROM
                        ZGENERICASSET
                        JOIN Z_PRIMARYKEY ON ZGENERICASSET.z_ent = Z_PRIMARYKEY.z_ent
                        LEFT JOIN ZMOMENT ON ZGENERICASSET.ZMOMENT = ZMOMENT.Z_PK
                        JOIN ZADDITIONALASSETATTRIBUTES ON ZGENERICASSET.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK
                        LEFT JOIN ZDETECTEDFACE ON ZADDITIONALASSETATTRIBUTES.ZASSET = ZDETECTEDFACE.ZASSET
                        LEFT JOIN ZPERSON ON ZPERSON.Z_PK = ZDETECTEDFACE.ZPERSON
        LEFT JOIN Z_26ASSETS ON ZGENERICASSET.Z_PK = Z_26ASSETS.Z_34ASSETS
        LEFT JOIN ZGENERICALBUM ON ZGENERICALBUM.Z_PK = Z_26ASSETS.Z_26ALBUMS
"""

_QUERY_IOS14 = """
        SELECT

                        DateTime( ZASSET.ZDATECREATED + 978307200, 'UNIXEPOCH' ) AS 'DateCreated',
                        ZASSET.Z_PK AS 'Asset_zpk',
                        ZASSET.ZADDITIONALATTRIBUTES AS 'AddAttributes_Key',
                        ZDETECTEDFACE.ZASSET AS 'DetectedFaceAsset',
                CASE
                                ZASSET.ZKIND
                                WHEN 0 THEN
                                'Photo'
                                WHEN 1 THEN
                                'Video'
                        END AS 'Kind',

        ZADDITIONALASSETATTRIBUTES.ZEXIFTIMESTAMPSTRING AS 'EXIFtimestamp',
        DateTime( ZADDITIONALASSETATTRIBUTES.ZSCENEANALYSISTIMESTAMP + 978307200, 'UNIXEPOCH' ) AS 'SceneAnalysisTimeStamp',
                        DateTime( ZASSET.ZANALYSISSTATEMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'AnalysisStateModificationDate',
                        DateTime( ZASSET.ZADDEDDATE + 978307200, 'UNIXEPOCH' ) AS 'AddDate',
                        ZASSET.ZFILENAME AS 'FileName',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALFILENAME AS 'OriginalFilename',
        ZGENERICALBUM.ZTITLE AS 'AlbumTitle',
                        ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID AS 'CreatorBundleID',
                        ZADDITIONALASSETATTRIBUTES.ZEDITORBUNDLEID AS 'EditorBundleID',
                        ZASSET.ZDIRECTORY AS 'Directory',
                        ZASSET.ZUNIFORMTYPEIDENTIFIER AS 'UniformID',
                CASE
                                ZASSET.ZSAVEDASSETTYPE
                                WHEN 0 THEN
                                'Saved from other source'
                                WHEN 2 THEN
                                'Photo Streams Data'
                                WHEN 3 THEN
                                'Made/saved with this device'
                                WHEN 4 THEN
                                'Default row'
                                WHEN 7 THEN
                                'Deleted' ELSE ZASSET.ZSAVEDASSETTYPE
                        END AS 'SavedAssetType',
                CASE
                          WHEN ZASSET.ZFACEAREAPOINTS > 0 THEN 'Yes'
                          ELSE 'NA'
                        END AS 'FaceDetectedinPhoto',
                        ZPERSON.ZDISPLAYNAME AS 'DisplayName',
                        ZPERSON.ZFULLNAME AS 'FullName',
                        ZPERSON.ZFACECOUNT AS 'FaceCount',
                        ZDETECTEDFACE.ZPERSON AS 'Person',
                        ZPERSON.ZCONTACTMATCHINGDICTIONARY AS 'ContactBlob',
                        ZPERSON.ZPERSONUUID as 'PersonUUID',
                        ZDETECTEDFACE.ZQUALITYMEASURE AS 'DetectedFaceQuality',
                CASE
                                ZDETECTEDFACE.ZAGETYPE
                                WHEN 1 THEN
                                'Baby/Toddler'
                                WHEN 2 THEN
                                'Baby/Toddler'
                                WHEN 3 THEN
                                'Child/YoungAdult'
                                WHEN 4 THEN
                                'YoungAdult/Adult'
                                WHEN 5 THEN
                                'Adult'
                                ELSE ZDETECTEDFACE.ZAGETYPE
                        END AS 'AgeTypeEstimate',
                CASE
                                ZDETECTEDFACE.ZGENDERTYPE
                                WHEN 1 THEN
                                'Male'
                                WHEN 2 THEN
                                'Female'
                                ELSE ZDETECTEDFACE.ZGENDERTYPE
                        END AS 'Gender',
                CASE
                          ZDETECTEDFACE.ZGLASSESTYPE
                          WHEN 3 THEN
                          'None'
                          WHEN 2 THEN
                          'Sun'
                          WHEN 1 THEN
                          'Eye'
                          ELSE ZDETECTEDFACE.ZGLASSESTYPE
                        END AS 'GlassesType',
                CASE
                          ZDETECTEDFACE.ZFACIALHAIRTYPE
                          WHEN 1 THEN
                          'None'
                          WHEN 2 THEN
                          'Beard/Mustache'
                          WHEN 3 THEN
                          'Goatee'
                          WHEN 5 THEN
                          'Stubble'
                          ELSE ZDETECTEDFACE.ZFACIALHAIRTYPE
                        END AS 'FacialHairType',
                CASE
                          ZDETECTEDFACE.ZBALDTYPE
                          WHEN 2 THEN
                          'Bald'
                          WHEN 3 THEN
                          'NotBald'
                          ELSE ZDETECTEDFACE.ZBALDTYPE
                        END AS 'Baldness',
                        ZASSET.ZORIGINALCOLORSPACE AS 'ColorSpace',
                        ZASSET.Zduration AS 'Duration',
                        ZASSET.Zvideocpdurationvalue AS 'VideoDuration',
                CASE
                                ZASSET.ZCOMPLETE
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Complete',
                CASE
                                ZASSET.ZVISIBILITYSTATE
                                WHEN 0 THEN
                                'Visible'
                                WHEN 1 THEN
                                'Photo Streams Data'
                                WHEN 2 THEN
                                'Burst' ELSE ZVISIBILITYSTATE
                        END AS 'VisibilityState',
                CASE
                                ZASSET.ZFAVORITE
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Favorite',
                CASE
                                ZASSET.zhidden
                                WHEN 0 THEN
                                'Not_Hidden'
                                WHEN 1 THEN
                                'File_Hidden' ELSE ZASSET.zhidden
                        END AS 'Hidden_File',
                CASE
                                ZASSET.ZTRASHEDSTATE
                                WHEN 1 THEN
                                'In_Trash'
                                WHEN 0 THEN
                                'Not_In_Trash' ELSE ZASSET.ZTRASHEDSTATE
                        END AS 'TrashState',
                        DateTime( ZASSET.ZTRASHEDDATE + 978307200, 'UNIXEPOCH' ) AS 'FileTrashDate',
                        ZADDITIONALASSETATTRIBUTES.ZVIEWCOUNT AS 'ViewCount',
                        ZADDITIONALASSETATTRIBUTES.ZPLAYCOUNT AS 'PlayCount',
                        ZADDITIONALASSETATTRIBUTES.ZSHARECOUNT AS 'ShareCount',
                        DateTime( ZASSET.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH' ) AS 'LastSharedDate',
                        DateTime( ZASSET.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'FileModificationDate',
                CASE
                                ZASSET.ZHASADJUSTMENTS
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'Has_Adjustments',
                        DateTime( ZASSET.ZADJUSTMENTTIMESTAMP + 978307200, 'UNIXEPOCH' ) AS 'AdjustmentsTimeStamp',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALFILESIZE AS 'OriginalFileSize',
                        ZASSET.ZHEIGHT AS 'File_Height',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALHEIGHT AS 'OrgFileHeight',
                        ZASSET.ZWIDTH AS 'File_Width',
                        ZADDITIONALASSETATTRIBUTES.ZORIGINALWIDTH AS 'OrgFileWidth',
                CASE
                                ZASSET.ZORIENTATION
                                WHEN 1 THEN
                                'Horizontal (left)'
                                WHEN 3 THEN
                                'Horizontal (right)'
                                WHEN 6 THEN
                                'Vertical (up)'
                                WHEN 8 THEN
                                'Vertical (down)' ELSE ZORIENTATION
                        END AS 'Orientation',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZORIGINALORIENTATION
                                WHEN 1 THEN
                                'Horizontal (left)'
                                WHEN 3 THEN
                                'Horizontal (right)'
                                WHEN 6 THEN
                                'Vertical (up)'
                                WHEN 8 THEN
                                'Vertical (down)' ELSE ZORIENTATION
                        END AS 'Org_Orientation',
                        ZADDITIONALASSETATTRIBUTES.ZTIMEZONENAME AS 'TimeZoneName',
                        ZADDITIONALASSETATTRIBUTES.ZTIMEZONEOFFSET AS 'TimeZoneOffset',
                        ZADDITIONALASSETATTRIBUTES.ZINFERREDTIMEZONEOFFSET AS 'InferredTimeZoneOffset',
                        ZASSET.ZLOCATIONDATA AS 'FileLocationData',
                CASE
                                ZASSET.ZLATITUDE
                                WHEN - 180.0 THEN
                                '' ELSE ZASSET.ZLATITUDE
                        END AS 'Latitude',
                CASE
                                ZASSET.ZLONGITUDE
                                WHEN - 180.0 THEN
                                '' ELSE ZASSET.ZLONGITUDE
                        END AS 'Longitude',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZSHIFTEDLOCATIONISVALID
                                WHEN 0 THEN
                                'No'
                                WHEN 1 THEN
                                'Yes'
                        END AS 'ShiftedLocationValid',
                CASE
                                ZADDITIONALASSETATTRIBUTES.ZREVERSELOCATIONDATAISVALID
                                WHEN 0 THEN
                                'No_Check_SceneAnalysis'
                                WHEN 1 THEN
                                'Yes_Check_SceneAnalysis'
                        END AS 'ReverseLocationDataIsValid',
                        ZADDITIONALASSETATTRIBUTES.ZREVERSELOCATIONDATA AS 'OrgFileReverseLocationData',
                        ZASSET.Zthumbnailindex AS 'ThumbnailIndex',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILWIDTH AS 'EmbeddedThumbnailWidth',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILHEIGHT AS 'EmbeddedThumbnailHeight',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILOFFSET AS 'EmbeddedThumbnailOffset',
                        ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILLENGTH AS 'EmbeddedThumbnailLenght',
                        ZASSET.ZMOMENT AS 'MomentPK',
        ZMOMENT.ZTITLE AS 'MomentTitle',
                        DateTime( ZMOMENT.ZSTARTDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentStartDate',
                        DateTime( ZMOMENT.Zrepresentativedate + 978307200, 'UNIXEPOCH' ) AS 'MomentRepresentativeDate',
                        DateTime( ZMOMENT.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentModificationDate',
                        DateTime( ZMOMENT.ZENDDATE + 978307200, 'UNIXEPOCH' ) AS 'MomentEndDate',
                CASE
                                ZMOMENT.ZTRASHEDSTATE
                                WHEN 1 THEN
                                'In_Trash'
                                WHEN 0 THEN
                                'Not_In_Trash' ELSE ZMOMENT.ZTRASHEDSTATE
                        END AS 'MomentTrashState',
                CASE
                                ZMOMENT.Zapproximatelatitude
                                WHEN - 180.0 THEN
                                '' ELSE ZMOMENT.Zapproximatelatitude
                        END AS 'MomentApproxLatitude',
                CASE
                                ZMOMENT.Zapproximatelongitude
                                WHEN - 180.0 THEN
                                '' ELSE ZMOMENT.Zapproximatelongitude
                        END AS 'MomentApproxLongitude',
                        ZASSET.ZUUID AS 'UUID',
                        ZASSET.ZMEDIAGROUPUUID AS 'MediaGroupUUID',
                        ZASSET.ZCLOUDASSETGUID AS 'CloudAssetGUID',
                        ZADDITIONALASSETATTRIBUTES.ZPUBLICGLOBALUUID AS 'PublicGlobalUUID',
                        ZADDITIONALASSETATTRIBUTES.ZMASTERFINGERPRINT AS 'MasterFingerprint',
                        ZADDITIONALASSETATTRIBUTES.ZADJUSTEDFINGERPRINT AS 'AdjustedFingerprint'
                FROM
                        ZASSET
                        LEFT JOIN ZMOMENT ON ZASSET.ZMOMENT = ZMOMENT.Z_PK
        JOIN ZADDITIONALASSETATTRIBUTES ON ZASSET.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK
                        LEFT JOIN ZDETECTEDFACE ON ZADDITIONALASSETATTRIBUTES.ZASSET = ZDETECTEDFACE.ZASSET
                        LEFT JOIN ZPERSON ON ZPERSON.Z_PK = ZDETECTEDFACE.ZPERSON
        LEFT JOIN Z_26ASSETS ON ZASSET.Z_PK = Z_26ASSETS.Z_3ASSETS
        LEFT JOIN ZGENERICALBUM ON ZGENERICALBUM.Z_PK = Z_26ASSETS.Z_26ALBUMS
"""

_HEADERS_IOS12 = (
    ('Thumbnail', 'media'), ('Timestamp', 'datetime'), ('Date Created', 'datetime'), 'Postal Address', 'Postal Subadmin Area',
    'Postal Sublocality',
    'Generic Asset ZPK', 'Add Attributes Key', 'Detected Face Asset', 'Kind', 'EXIF Timestamp',
    'Scene Analysis Timestamp', 'Add Date', 'Filename', 'Original Filename', 'Album Title',
    'Creator Bundle ID',
    'Editor Bundle ID', 'Directory', 'Uniform ID', 'Saved Asset Type', 'Face Detected in Photo',
    'Display Name',
    'Full Name', 'Face Count', 'Person', 'Contact Blob', 'Person UUID', 'Detected Face Quality',
    'Age Type Estimate', 'Gender', 'Glasses Type', 'Facial Hair Type', 'Baldness', 'Color Space',
    'Duration',
    'Video Duration', 'Complete', 'Visibility State', 'Favorite', 'Hidden File?', 'Trash State',
    'File Trash Date', 'View Count', 'Play Count', 'Share Count', 'Last Shared Date',
    'File Modification Date',
    'Has Adjustments?', 'Adjustment Timestamp', 'Original File Size', 'File Height', 'Org File Height',
    'File Width', 'Org File Width', 'Orientation', 'Org Orientation', 'Timezone Name', 'Timezone Offset',
    'File Location Data', 'Latitude', 'Longitude', 'Shifted Location Valid',
    'Reverse Location Data is Valid',
    'Org File Reverse Location Data', 'Thumbnail Index', 'Embedded Thumbnail Width',
    'Embedded Thumbnail Height', 'Embedded Thumbnail Offset', 'Embedded Thumbnail Length', 'Moment PK',
    'Moment Start Date', 'Moment Representative Date', 'Moment Modification Date', 'Moment End Date',
    'Moment Title', 'Moment Approx Latitude', 'Moment Approx Longitude', 'UUID', 'Media Group UUID',
    'Cloud Assets GUID', 'Public Global UUID', 'Master Fingerprint', 'Adjusted Fingerprint')

_HEADERS_IOS13 = (
    ('Thumbnail', 'media'), ('Timestamp', 'datetime'), ('Date Created', 'datetime'), 'Postal Address', 'Postal Subadmin Area',
    'Postal Sublocality',
    'Generic Asset ZPK', 'Add Attributes Key', 'Detected Face Asset', 'Kind', 'EXIF Timestamp',
    'Scene Analysis Timestamp', 'Analysis State Modified Date', 'Add Date', 'Filename', 'Original Filename',
    'Album Title', 'Creator Bundle ID', 'Editor Bundle ID', 'Directory', 'Uniform ID', 'Saved Asset Type',
    'Face Detected in Photo', 'Display Name', 'Full Name', 'Face Count', 'Person', 'Contact Blob',
    'Person UUID', 'Detected Face Quality', 'Age Type Estimate', 'Gender', 'Glasses Type',
    'Facial Hair Type',
    'Baldness', 'Color Space', 'Duration', 'Video Duration', 'Complete', 'Visibility State', 'Favorite',
    'Hidden File?', 'Trash State', 'File Trash Date', 'View Count', 'Play Count', 'Share Count',
    'Last Shared Date', 'File Modification Date', 'Has Adjustments?', 'Adjustment Timestamp',
    'Original File Size', 'File Height', 'Org File Height', 'File Width', 'Org File Width', 'Orientation',
    'Org Orientation', 'Timezone Name', 'Timezone Offset', 'Infered Timezone Offset', 'File Location Data',
    'Latitude', 'Longitude', 'Shifted Location Valid', 'Reverse Location Data is Valid',
    'Org File Reverse Location Data', 'Thumbnail Index', 'Embedded Thumbnail Width',
    'Embedded Thumbnail Height', 'Embedded Thumbnail Offset', 'Embedded Thumbnail Lenght', 'Moment PK',
    'Moment Start Date', 'Moment Representative Date', 'Moment Modification Date', 'Moment End Date',
    'Moment Title', 'Moment Approx Latitude', 'Moment Approx Longitude', 'UUID', 'Media Group UUID',
    'Cloud Assest GUID', 'Public Global UUID', 'Master Fingetprint', 'Adjusted Fingerprint')

_HEADERS_IOS14 = (
    ('Timestamp', 'datetime'), ('Date Created', 'datetime'), 'Postal Address', 'Postal Subadmin Area', 'Postal Sublocality',
    'Asset ZPK',
    'Add Attributes Key', 'Detected Face Asset', 'Kind', 'EXIF Timestamp', 'Scene Analysis Timestamp',
    'Analysis State Modified Date', 'Add Date', 'Filename', 'Original Filename', 'Album Title',
    'Creator Bundle ID', 'Editor Bundle ID', 'Directory', 'Uniform ID', 'Saved Asset Type',
    'Face Detected in Photo', 'Display Name', 'Full Name', 'Face Count', 'Person', 'Contact Blob',
    'Person UUID', 'Detected Face Quality', 'Age Type Estimate', 'Gender', 'Glasses Type',
    'Facial Hair Type',
    'Baldness', 'Color Space', 'Duration', 'Video Duration', 'Complete', 'Visibility State', 'Favorite',
    'Hidden File?', 'Trash State', 'File Trash Date', 'View Count', 'Play Count', 'Share Count',
    'Last Shared Date', 'File Modification Date', 'Has Adjustments?', 'Adjustment Timestamp',
    'Original File Size', 'File Height', 'Org File Height', 'File Width', 'Org File Width', 'Orientation',
    'Org Orientation', 'Timezone Name', 'Timezone Offset', 'Infered Timezone Offset', 'File Location Data',
    'Latitude', 'Longitude', 'Shifted Location Valid', 'Reverse Location Data is Valid',
    'Org File Reverse Location Data', 'Thumbnail Index', 'Embedded Thumbnail Width',
    'Embedded Thumbnail Height', 'Embedded Thumbnail Offset', 'Embedded Thumbnail Lenght', 'Moment PK',
    'Moment Title', 'Moment Start Date', 'Moment Representative Date', 'Moment Modification Date',
    'Moment End Date', 'Moment Trash State', 'Moment Approx Latitude', 'Moment Approx Longitude', 'UUID',
    'Media Group UUID', 'Cloud Assest GUID', 'Public Global UUID', 'Master Fingetprint',
    'Adjusted Fingerprint')


def _postal(blob, report_folder, counter):
    """Write a reverse-location bplist and return (formatted, subadmin, sublocality)."""
    if blob is None:
        return '', '', ''
    pathto = os.path.join(report_folder, 'ReverseLocationData' + str(counter) + '.bplist')
    try:
        with open(pathto, 'wb') as wf:
            wf.write(blob)
        with open(pathto, 'rb') as f:
            dp = nd.deserialize_plist(f)
        addr = dp['postalAddress']
        return (addr.get('_formattedAddress', ''), addr.get('_subAdministrativeArea', ''),
                addr.get('_subLocality', ''))
    except (KeyError, ValueError, TypeError, OSError, nd.DeserializeError):
        return '', '', ''


def _thumbnail_ref(directory, filename, seeker, source_file):
    """Find the cached Photos thumbnail JPG and check it in as embedded media."""
    found = seeker.search(thumbnail_root + directory + '/' + filename + '/**.JPG', return_on_first_hit=True)
    if not found:
        return None
    try:
        with open(found, 'rb') as f:
            return check_in_embedded_media(source_file, f.read(), os.path.basename(str(found)))
    except OSError:
        return None


@artifact_processor
def photosMetadata(context):
    source_file = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.sqlite'):
            source_file = file_found
            break

    data_list = []
    if not source_file:
        return _HEADERS_IOS14, data_list, ''

    seeker = context.get_seeker()
    report_folder = context.get_report_folder()
    ios_version = iOS.get_version()

    if version.parse(ios_version) >= version.parse("14"):
        headers, query, postal_idx, thumb_idx = _HEADERS_IOS14, _QUERY_IOS14, 61, None
    elif version.parse(ios_version) >= version.parse("13"):
        headers, query, postal_idx, thumb_idx = _HEADERS_IOS13, _QUERY_IOS13, 61, (14, 9)
    elif version.parse(ios_version) >= version.parse("12"):
        headers, query, postal_idx, thumb_idx = _HEADERS_IOS12, _QUERY_IOS12, 59, (13, 8)
    else:
        logfunc(f"Unsupported iOS version for Photos.sqlite metadata: {ios_version}")
        return _HEADERS_IOS14, data_list, context.get_relative_path(source_file)

    try:
        rows = get_sqlite_db_records(source_file, query)
    except sqlite3.Error as ex:
        logfunc(f'Error processing Photos.sqlite metadata: {ex}')
        return headers, data_list, context.get_relative_path(source_file)

    for counter, record in enumerate(rows):
        row = tuple(record)
        postal = _postal(row[postal_idx], report_folder, counter)
        prefix = (row[0], row[0]) + postal + row[1:]
        if thumb_idx is not None:
            thumb = _thumbnail_ref(row[thumb_idx[0]], row[thumb_idx[1]], seeker, source_file)
            data_list.append((thumb,) + prefix)
        else:
            data_list.append(prefix)

    return headers, data_list, context.get_relative_path(source_file)
