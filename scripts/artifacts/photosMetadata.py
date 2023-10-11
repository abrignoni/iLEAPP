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
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, generate_thumbnail, \
    open_sqlite_db_readonly


def get_photosMetadata(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
      file_found = str(file_found)
      
      if file_found.endswith('.sqlite'):
        break
      
    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) < version.parse("12"):
        logfunc("Unsupported version for Photos.sqlite metadata on iOS " + iOSversion)
    if (version.parse(iOSversion) >= version.parse("12")) & (version.parse(iOSversion) < version.parse("13")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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

        """)
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                postal_address = ''
                postal_address_subadminarea = ''
                postal_address_sublocality = ''

                if row[59] is not None:
                    pathto = os.path.join(report_folder, 'ReverseLocationData' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[59])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except (KeyError, ValueError, TypeError) as ex:
                            if str(ex).find("does not contain an '$archiver' key") >= 0:
                                logfunc('plist was Not an NSKeyedArchive ' + row[0])
                            else:
                                logfunc('Error reading exported bplist from Asset PK ' + row[0])
                            deserialized_plist = None

                htmlThumbTag = generate_thumbnail(row[13], row[8], seeker, report_folder)


                data_list.append((htmlThumbTag, row[0], row[0], postal_address, postal_address_subadminarea,
                                  postal_address_sublocality, row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
                                  row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                                  row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
                                  row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[42], row[43],
                                  row[44], row[45], row[46], row[47], row[48], row[49], row[50], row[51], row[52],
                                  row[53], row[54], row[55], row[56], row[57], row[58], row[59], row[60], row[61],
                                  row[62], row[63], row[64], row[65], row[66], row[67], row[68], row[69], row[70],
                                  row[71], row[72], row[73], row[74], row[75], row[76], row[77], row[78]))

                counter += 1

            description = ''
            report = ArtifactHtmlReport('Photos.sqlite')
            report.start_artifact_report(report_folder, 'Metadata', description)
            report.add_script()
            data_headers = (
                'Thumbnail', 'Timestamp', 'Date Created', 'Postal Address', 'Postal Subadmin Area',
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
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Thumbnail'])
            report.end_artifact_report()

            tsvname = 'Photos-sqlite Metadata'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Photos-sqlite Metadata'
            timeline(report_folder, tlactivity, data_list, data_headers)

            kmlactivity = 'Photos-sqlite Metadata'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Photos.sqlite metadata')

        db.close()
        return

    elif (version.parse(iOSversion) >= version.parse("13")) & (version.parse(iOSversion) < version.parse("14")):
        file_found = str(files_found[0])
        # os.chmod(file_found, 0o0777)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                postal_address = ''
                postal_address_subadminarea = ''
                postal_address_sublocality = ''

                if row[61] is not None:
                    pathto = os.path.join(report_folder, 'ReverseLocationData' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[61])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except:
                            logfunc('Error reading exported bplist from Asset PK' + row[0])
                            deserialized_plist = None

                htmlThumbTag = generate_thumbnail(row[14], row[9], seeker, report_folder)

                data_list.append((htmlThumbTag, row[0], row[0], postal_address, postal_address_subadminarea,
                                  postal_address_sublocality, row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
                                  row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                                  row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
                                  row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[42], row[43],
                                  row[44], row[45], row[46], row[47], row[48], row[49], row[50], row[51], row[52],
                                  row[53], row[54], row[55], row[56], row[57], row[58], row[59], row[60], row[61],
                                  row[62], row[63], row[64], row[65], row[66], row[67], row[68], row[69], row[70],
                                  row[71], row[72], row[73], row[74], row[75], row[76], row[77], row[78], row[79],
                                  row[80]))

                counter += 1

            description = ''
            report = ArtifactHtmlReport('Photos.sqlite')
            report.start_artifact_report(report_folder, 'Metadata', description)
            report.add_script()
            data_headers = (
                'Thumbnail', 'Timestamp', 'Date Created', 'Postal Address', 'Postal Subadmin Area',
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
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Thumbnail'])
            report.end_artifact_report()

            tsvname = 'Photos-sqlite Metadata'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Photos-sqlite Metadata'
            timeline(report_folder, tlactivity, data_list, data_headers)

            kmlactivity = 'Photos-sqlite Metadata'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Photos.sqlite metadata')

        db.close()
        return
    elif version.parse(iOSversion) >= version.parse("14"):
        file_found = str(files_found[0])
        # os.chmod(file_found, 0o0777)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
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
        """)
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                postal_address = ''
                postal_address_subadminarea = ''
                postal_address_sublocality = ''

                if row[61] is not None:
                    pathto = os.path.join(report_folder, 'ReverseLocationData' + str(counter) + '.bplist')
                    with open(pathto, 'ab') as wf:
                        wf.write(row[61])

                    with open(pathto, 'rb') as f:
                        try:
                            deserialized_plist = nd.deserialize_plist(f)
                            postal_address = deserialized_plist['postalAddress']['_formattedAddress']
                            postal_address_subadminarea = deserialized_plist['postalAddress']['_subAdministrativeArea']
                            postal_address_sublocality = deserialized_plist['postalAddress']['_subLocality']

                        except:
                            logfunc('Error reading exported bplist from Asset PK' + row[0])
                            deserialized_plist = None

                data_list.append((row[0], row[0], postal_address, postal_address_subadminarea,
                                  postal_address_sublocality, row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                  row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
                                  row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                                  row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
                                  row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[42], row[43],
                                  row[44], row[45], row[46], row[47], row[48], row[49], row[50], row[51], row[52],
                                  row[53], row[54], row[55], row[56], row[57], row[58], row[59], row[60], row[61],
                                  row[62], row[63], row[64], row[65], row[66], row[67], row[68], row[69], row[70],
                                  row[71], row[72], row[73], row[74], row[75], row[76], row[77], row[78], row[79],
                                  row[80], row[81]))

                counter += 1

            description = ''
            report = ArtifactHtmlReport('Photos.sqlite')
            report.start_artifact_report(report_folder, 'Metadata', description)
            report.add_script()
            data_headers = (
                'Timestamp', 'Date Created', 'Postal Address', 'Postal Subadmin Area', 'Postal Sublocality',
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
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Photos-sqlite Metadata'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Photos-sqlite Metadata'
            timeline(report_folder, tlactivity, data_list, data_headers)

            kmlactivity = 'Photos-sqlite Metadata'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)

        else:
            logfunc('No data available for Photos.sqlite metadata')

        db.close()
        return

__artifacts__ = {
    "photosMetadata": (
        "Photos",
        ('*/mobile/Media/PhotoData/Photos.sqlite*'),
        get_photosMetadata)
}